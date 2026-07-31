"""
Memory Router implementation.

This module implements the Memory Router that routes classified memories
to appropriate storage locations without duplication, handling multi-label
classification and storage policy enforcement.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib

from memory_classification.core.types import MemoryType, StoragePolicy
from memory_classification.core.models import UniversalMemoryObject, StorageLocation
from memory_classification.core.interfaces import StorageBackend, DeduplicationStrategy
from memory_classification.core.exceptions import (
    StorageError,
    DuplicateMemoryError,
    InvalidMemoryTypeError,
)
from memory_classification.registry.memory_type_registry import get_global_registry


class ContentHashDeduplicationStrategy(DeduplicationStrategy):
    """
    Deduplication strategy based on content hashing.
    
    This strategy uses content hashing to detect duplicate memories,
    ensuring that identical content is not stored multiple times.
    """
    
    def __init__(self, hash_algorithm: str = "sha256"):
        """
        Initialize the content hash deduplication strategy.
        
        Args:
            hash_algorithm: Hash algorithm to use (default: sha256)
        """
        self.hash_algorithm = hash_algorithm
    
    def _compute_content_hash(self, content: str) -> str:
        """
        Compute hash of content.
        
        Args:
            content: The content to hash
            
        Returns:
            The content hash
        """
        hash_obj = hashlib.new(self.hash_algorithm)
        hash_obj.update(content.encode('utf-8'))
        return hash_obj.hexdigest()
    
    async def is_duplicate(
        self,
        memory_object: Dict[str, Any],
        existing_memories: List[Dict[str, Any]],
    ) -> bool:
        """
        Check if a memory is a duplicate based on content hash.
        
        Args:
            memory_object: The memory object to check
            existing_memories: List of existing memories to compare against
            
        Returns:
            True if the memory is a duplicate, False otherwise
        """
        content_hash = self._compute_content_hash(memory_object.get("content", ""))
        
        for existing_memory in existing_memories:
            existing_hash = self._compute_content_hash(existing_memory.get("content", ""))
            if content_hash == existing_hash:
                return True
        
        return False
    
    async def find_duplicate_id(
        self,
        memory_object: Dict[str, Any],
        existing_memories: List[Dict[str, Any]],
    ) -> Optional[str]:
        """
        Find the ID of a duplicate memory if one exists.
        
        Args:
            memory_object: The memory object to check
            existing_memories: List of existing memories to compare against
            
        Returns:
            The ID of the duplicate memory if found, None otherwise
        """
        content_hash = self._compute_content_hash(memory_object.get("content", ""))
        
        for existing_memory in existing_memories:
            existing_hash = self._compute_content_hash(existing_memory.get("content", ""))
            if content_hash == existing_hash:
                return existing_memory.get("id")
        
        return None


class MemoryRouter:
    """
    Router for classified memories.
    
    This router handles the routing of classified memories to appropriate
    storage locations based on their memory types and storage policies.
    It implements deduplication to prevent redundant storage.
    """
    
    def __init__(
        self,
        storage_backends: Dict[StoragePolicy, StorageBackend] = None,
        deduplication_strategy: DeduplicationStrategy = None,
        enable_deduplication: bool = True,
    ):
        """
        Initialize the memory router.
        
        Args:
            storage_backends: Mapping of storage policies to storage backends
            deduplication_strategy: Strategy for deduplication
            enable_deduplication: Whether to enable deduplication
        """
        self.storage_backends = storage_backends or {}
        self.deduplication_strategy = deduplication_strategy or ContentHashDeduplicationStrategy()
        self.enable_deduplication = enable_deduplication
        self.memory_type_registry = get_global_registry()
        self._routing_stats = {
            "total_routed": 0,
            "duplicates_prevented": 0,
            "routing_errors": 0,
        }
    
    def register_storage_backend(
        self,
        storage_policy: StoragePolicy,
        storage_backend: StorageBackend,
    ) -> None:
        """
        Register a storage backend for a storage policy.
        
        Args:
            storage_policy: The storage policy
            storage_backend: The storage backend instance
        """
        self.storage_backends[storage_policy] = storage_backend
    
    def get_storage_backend(self, storage_policy: StoragePolicy) -> Optional[StorageBackend]:
        """
        Get the storage backend for a storage policy.
        
        Args:
            storage_policy: The storage policy
            
        Returns:
            The storage backend if found, None otherwise
        """
        return self.storage_backends.get(storage_policy)
    
    async def route(
        self,
        memory_object: UniversalMemoryObject,
        existing_memories: List[Dict[str, Any]] = None,
    ) -> List[StorageLocation]:
        """
        Route a memory object to appropriate storage locations.
        
        This method determines the storage locations based on the memory's
        types and their storage policies, checks for duplicates, and stores
        the memory in the appropriate backends.
        
        Args:
            memory_object: The memory object to route
            existing_memories: List of existing memories for deduplication
            
        Returns:
            List of storage locations where the memory was stored
            
        Raises:
            StorageError: If routing or storage fails
            DuplicateMemoryError: If a duplicate is detected and deduplication is enabled
        """
        if existing_memories is None:
            existing_memories = []
        
        # Check for duplicates if deduplication is enabled
        if self.enable_deduplication:
            memory_dict = memory_object.to_storage_dict()
            if await self.deduplication_strategy.is_duplicate(memory_dict, existing_memories):
                duplicate_id = await self.deduplication_strategy.find_duplicate_id(
                    memory_dict, existing_memories
                )
                self._routing_stats["duplicates_prevented"] += 1
                raise DuplicateMemoryError(
                    f"Duplicate memory detected",
                    memory_id=duplicate_id,
                    details={"original_id": memory_object.id}
                )
        
        # Determine storage locations based on memory types
        storage_locations = []
        storage_policies = self._determine_storage_policies(memory_object.memory_types)
        
        # Store in each required storage backend
        for storage_policy in storage_policies:
            storage_backend = self.get_storage_backend(storage_policy)
            if storage_backend is None:
                # Log warning but continue with other backends
                continue
            
            try:
                memory_dict = memory_object.to_storage_dict()
                stored_id = await storage_backend.store(memory_dict)
                
                storage_location = StorageLocation(
                    backend_type=type(storage_backend).__name__,
                    location_id=stored_id,
                    access_parameters={"storage_policy": storage_policy.value},
                )
                storage_locations.append(storage_location)
                
                # Update memory object with storage location
                if storage_location.location_id not in memory_object.storage_locations:
                    memory_object.storage_locations.append(storage_location.location_id)
                
            except Exception as e:
                self._routing_stats["routing_errors"] += 1
                raise StorageError(
                    f"Failed to store memory in backend for policy {storage_policy.value}",
                    storage_location=storage_policy.value,
                    details={"error": str(e)}
                )
        
        self._routing_stats["total_routed"] += 1
        return storage_locations
    
    def _determine_storage_policies(self, memory_types: List[MemoryType]) -> List[StoragePolicy]:
        """
        Determine storage policies for memory types.
        
        Args:
            memory_types: List of memory types
            
        Returns:
            List of unique storage policies
        """
        storage_policies = set()
        
        for memory_type in memory_types:
            try:
                policy = self.memory_type_registry.get_storage_policy(memory_type)
                storage_policies.add(policy)
            except InvalidMemoryTypeError:
                # Use default policy if type not found
                storage_policies.add(StoragePolicy.STANDARD)
        
        return list(storage_policies)
    
    async def check_duplicate(
        self,
        memory_object: UniversalMemoryObject,
        existing_memories: List[Dict[str, Any]],
    ) -> bool:
        """
        Check if a memory is a duplicate.
        
        Args:
            memory_object: The memory object to check
            existing_memories: List of existing memories to compare against
            
        Returns:
            True if the memory is a duplicate, False otherwise
        """
        memory_dict = memory_object.to_storage_dict()
        return await self.deduplication_strategy.is_duplicate(memory_dict, existing_memories)
    
    async def find_duplicate(
        self,
        memory_object: UniversalMemoryObject,
        existing_memories: List[Dict[str, Any]],
    ) -> Optional[str]:
        """
        Find the ID of a duplicate memory if one exists.
        
        Args:
            memory_object: The memory object to check
            existing_memories: List of existing memories to compare against
            
        Returns:
            The ID of the duplicate memory if found, None otherwise
        """
        memory_dict = memory_object.to_storage_dict()
        return await self.deduplication_strategy.find_duplicate_id(memory_dict, existing_memories)
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """
        Get routing statistics.
        
        Returns:
            Dictionary with routing statistics
        """
        return self._routing_stats.copy()
    
    def reset_statistics(self) -> None:
        """Reset routing statistics."""
        self._routing_stats = {
            "total_routed": 0,
            "duplicates_prevented": 0,
            "routing_errors": 0,
        }
