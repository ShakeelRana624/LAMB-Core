"""
Core interfaces for the Memory Classification Engine.

This module defines the fundamental interfaces that all classifiers
and related components must implement, ensuring consistency and
enabling extensibility.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from memory_classification.core.types import MemoryType, ClassificationMethod


@dataclass
class MemoryInput:
    """
    Input data for memory classification.
    
    This class encapsulates all information needed to classify a memory,
    including the content, context, and metadata.
    """
    
    content: str
    session_id: str
    agent_id: str
    tenant_id: str
    metadata: Dict[str, Any] = None
    timestamp: Optional[float] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().timestamp()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "content": self.content,
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "tenant_id": self.tenant_id,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


@dataclass
class ClassificationResult:
    """
    Result of memory classification.
    
    This class contains the classification output including assigned
    memory types, confidence scores, reasoning, and metadata.
    """
    
    memory_types: List[MemoryType]
    confidence_scores: Dict[MemoryType, float]
    reasoning: Dict[MemoryType, str]
    metadata: Dict[str, Any] = None
    computation_time_ms: float = 0.0
    classifier_method: ClassificationMethod = ClassificationMethod.RULE_BASED
    
    def __post_init__(self):
        """Initialize default values and validate."""
        if self.metadata is None:
            self.metadata = {}
        
        # Ensure all memory types have confidence scores
        for memory_type in self.memory_types:
            if memory_type not in self.confidence_scores:
                self.confidence_scores[memory_type] = 0.0
        
        # Ensure all memory types have reasoning
        for memory_type in self.memory_types:
            if memory_type not in self.reasoning:
                self.reasoning[memory_type] = ""
    
    def get_highest_confidence_type(self) -> Optional[MemoryType]:
        """Return the memory type with highest confidence score."""
        if not self.confidence_scores:
            return None
        return max(self.confidence_scores.items(), key=lambda x: x[1])[0]
    
    def get_confidence_for_type(self, memory_type: MemoryType) -> float:
        """Return confidence score for a specific memory type."""
        return self.confidence_scores.get(memory_type, 0.0)
    
    def get_reasoning_for_type(self, memory_type: MemoryType) -> str:
        """Return reasoning for a specific memory type."""
        return self.reasoning.get(memory_type, "")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "memory_types": [mt.value for mt in self.memory_types],
            "confidence_scores": {mt.value: score for mt, score in self.confidence_scores.items()},
            "reasoning": {mt.value: reason for mt, reason in self.reasoning.items()},
            "metadata": self.metadata,
            "computation_time_ms": self.computation_time_ms,
            "classifier_method": self.classifier_method.value,
        }


class MemoryClassifier(ABC):
    """
    Abstract base class for memory classifiers.
    
    All memory classifiers must implement this interface to ensure
    consistency and enable the classification engine to manage them.
    """
    
    def __init__(
        self,
        memory_type: MemoryType,
        confidence_threshold: float = 0.5,
        enabled: bool = True,
    ):
        """
        Initialize the memory classifier.
        
        Args:
            memory_type: The memory type this classifier handles
            confidence_threshold: Minimum confidence threshold for classification
            enabled: Whether this classifier is enabled
        """
        self.memory_type = memory_type
        self.confidence_threshold = confidence_threshold
        self.enabled = enabled
    
    @abstractmethod
    async def classify(self, memory_input: MemoryInput) -> ClassificationResult:
        """
        Classify a memory input into memory types.
        
        This method must be implemented by all classifiers to perform
        the actual classification logic.
        
        Args:
            memory_input: The memory input to classify
            
        Returns:
            ClassificationResult with memory types, confidence scores, and reasoning
            
        Raises:
            ClassificationFailedError: If classification fails
        """
        pass
    
    @abstractmethod
    def get_supported_types(self) -> List[MemoryType]:
        """
        Return the list of memory types this classifier can handle.
        
        Returns:
            List of supported memory types
        """
        pass
    
    def get_confidence_threshold(self) -> float:
        """Return the confidence threshold for this classifier."""
        return self.confidence_threshold
    
    def set_confidence_threshold(self, threshold: float) -> None:
        """
        Set the confidence threshold for this classifier.
        
        Args:
            threshold: New confidence threshold (0.0 to 1.0)
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")
        self.confidence_threshold = threshold
    
    def is_enabled(self) -> bool:
        """Return whether this classifier is enabled."""
        return self.enabled
    
    def enable(self) -> None:
        """Enable this classifier."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable this classifier."""
        self.enabled = False
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Return metadata about this classifier.
        
        Returns:
            Dictionary with classifier metadata
        """
        return {
            "memory_type": self.memory_type.value,
            "confidence_threshold": self.confidence_threshold,
            "enabled": self.enabled,
            "classifier_type": self.__class__.__name__,
        }


class StorageBackend(ABC):
    """
    Abstract base class for storage backends.
    
    Storage backends handle the actual persistence of classified memories
    to various storage systems (databases, file systems, etc.).
    """
    
    @abstractmethod
    async def store(self, memory_object: Dict[str, Any]) -> str:
        """
        Store a memory object.
        
        Args:
            memory_object: The memory object to store
            
        Returns:
            The ID of the stored memory
            
        Raises:
            StorageError: If storage fails
        """
        pass
    
    @abstractmethod
    async def retrieve(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a memory object by ID.
        
        Args:
            memory_id: The ID of the memory to retrieve
            
        Returns:
            The memory object if found, None otherwise
            
        Raises:
            StorageError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def exists(self, memory_id: str) -> bool:
        """
        Check if a memory exists.
        
        Args:
            memory_id: The ID of the memory to check
            
        Returns:
            True if the memory exists, False otherwise
            
        Raises:
            StorageError: If check fails
        """
        pass
    
    @abstractmethod
    async def delete(self, memory_id: str) -> bool:
        """
        Delete a memory by ID.
        
        Args:
            memory_id: The ID of the memory to delete
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            StorageError: If deletion fails
        """
        pass


class DeduplicationStrategy(ABC):
    """
    Abstract base class for deduplication strategies.
    
    Deduplication strategies determine whether a memory is a duplicate
    of an existing memory to prevent redundant storage.
    """
    
    @abstractmethod
    async def is_duplicate(
        self,
        memory_object: Dict[str, Any],
        existing_memories: List[Dict[str, Any]],
    ) -> bool:
        """
        Check if a memory is a duplicate of existing memories.
        
        Args:
            memory_object: The memory object to check
            existing_memories: List of existing memories to compare against
            
        Returns:
            True if the memory is a duplicate, False otherwise
        """
        pass
    
    @abstractmethod
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
        pass


class ValidationRule(ABC):
    """
    Abstract base class for validation rules.
    
    Validation rules check whether memory inputs or classification results
    meet specific criteria.
    """
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate data against this rule.
        
        Args:
            data: The data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    def get_rule_name(self) -> str:
        """
        Return the name of this validation rule.
        
        Returns:
            The rule name
        """
        pass
