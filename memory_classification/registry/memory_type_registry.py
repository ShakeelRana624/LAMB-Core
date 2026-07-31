"""
Memory Type Registry implementation.

This module implements the registry pattern for managing memory type definitions,
their schemas, validation rules, and storage policies.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from memory_classification.core.types import MemoryType, StoragePolicy
from memory_classification.core.models import TypeDefinition
from memory_classification.core.exceptions import (
    RegistryError,
    InvalidMemoryTypeError,
)


class MemoryTypeRegistry:
    """
    Registry for managing memory type definitions.
    
    This registry maintains the definitions for all memory types, including
    their schemas, validation rules, and storage policies. It provides a
    centralized location for memory type metadata.
    """
    
    def __init__(self):
        """Initialize the memory type registry."""
        self._type_definitions: Dict[MemoryType, TypeDefinition] = {}
        self._initialize_default_types()
    
    def _initialize_default_types(self) -> None:
        """Initialize default memory type definitions."""
        # Identity Memory
        self.register_type(
            TypeDefinition(
                memory_type=MemoryType.IDENTITY_MEMORY,
                schema_definition={
                    "fields": {
                        "name": {"type": "string", "required": False},
                        "age": {"type": "integer", "required": False},
                        "location": {"type": "string", "required": False},
                        "personal_attributes": {"type": "object", "required": False},
                    }
                },
                validation_rules=["content_not_empty", "max_length_10000"],
                storage_policy=StoragePolicy.LONG_TERM,
                metadata={
                    "description": "Personal identity information",
                    "retention_days": 3650,
                    "access_frequency": "low",
                },
            )
        )
        
        # Goal Memory
        self.register_type(
            TypeDefinition(
                memory_type=MemoryType.GOAL_MEMORY,
                schema_definition={
                    "fields": {
                        "goal_text": {"type": "string", "required": False},
                        "priority": {"type": "string", "required": False},
                        "deadline": {"type": "datetime", "required": False},
                        "status": {"type": "string", "required": False},
                    }
                },
                validation_rules=["content_not_empty", "max_length_10000"],
                storage_policy=StoragePolicy.LONG_TERM,
                metadata={
                    "description": "Goals and objectives",
                    "retention_days": 1825,
                    "access_frequency": "medium",
                },
            )
        )
        
        # Preference Memory
        self.register_type(
            TypeDefinition(
                memory_type=MemoryType.PREFERENCE_MEMORY,
                schema_definition={
                    "fields": {
                        "preference_type": {"type": "string", "required": False},
                        "preference_value": {"type": "string", "required": False},
                        "context": {"type": "string", "required": False},
                    }
                },
                validation_rules=["content_not_empty", "max_length_5000"],
                storage_policy=StoragePolicy.LONG_TERM,
                metadata={
                    "description": "User preferences and choices",
                    "retention_days": 3650,
                    "access_frequency": "medium",
                },
            )
        )
        
        # Relationship Memory
        self.register_type(
            TypeDefinition(
                memory_type=MemoryType.RELATIONSHIP_MEMORY,
                schema_definition={
                    "fields": {
                        "relationship_type": {"type": "string", "required": False},
                        "related_entities": {"type": "array", "required": False},
                        "relationship_strength": {"type": "float", "required": False},
                    }
                },
                validation_rules=["content_not_empty", "max_length_10000"],
                storage_policy=StoragePolicy.LONG_TERM,
                metadata={
                    "description": "Social relationships",
                    "retention_days": 3650,
                    "access_frequency": "medium",
                },
            )
        )
        
        # Project Memory
        self.register_type(
            TypeDefinition(
                memory_type=MemoryType.PROJECT_MEMORY,
                schema_definition={
                    "fields": {
                        "project_name": {"type": "string", "required": False},
                        "project_status": {"type": "string", "required": False},
                        "project_deadline": {"type": "datetime", "required": False},
                        "team_members": {"type": "array", "required": False},
                    }
                },
                validation_rules=["content_not_empty", "max_length_10000"],
                storage_policy=StoragePolicy.STANDARD,
                metadata={
                    "description": "Project-related information",
                    "retention_days": 1095,
                    "access_frequency": "high",
                },
            )
        )
        
        # Skill Memory
        self.register_type(
            TypeDefinition(
                memory_type=MemoryType.SKILL_MEMORY,
                schema_definition={
                    "fields": {
                        "skill_name": {"type": "string", "required": False},
                        "skill_level": {"type": "string", "required": False},
                        "learning_progress": {"type": "float", "required": False},
                    }
                },
                validation_rules=["content_not_empty", "max_length_5000"],
                storage_policy=StoragePolicy.LONG_TERM,
                metadata={
                    "description": "Skills and abilities",
                    "retention_days": 3650,
                    "access_frequency": "medium",
                },
            )
        )
        
        # Procedural Memory
        self.register_type(
            TypeDefinition(
                memory_type=MemoryType.PROCEDURAL_MEMORY,
                schema_definition={
                    "fields": {
                        "procedure_name": {"type": "string", "required": False},
                        "steps": {"type": "array", "required": False},
                        "complexity": {"type": "string", "required": False},
                    }
                },
                validation_rules=["content_not_empty", "max_length_20000"],
                storage_policy=StoragePolicy.LONG_TERM,
                metadata={
                    "description": "Procedural knowledge and how-to",
                    "retention_days": 3650,
                    "access_frequency": "medium",
                },
            )
        )
        
        # Task Memory
        self.register_type(
            TypeDefinition(
                memory_type=MemoryType.TASK_MEMORY,
                schema_definition={
                    "fields": {
                        "task_description": {"type": "string", "required": False},
                        "task_status": {"type": "string", "required": False},
                        "task_priority": {"type": "string", "required": False},
                        "due_date": {"type": "datetime", "required": False},
                    }
                },
                validation_rules=["content_not_empty", "max_length_5000"],
                storage_policy=StoragePolicy.SHORT_TERM,
                metadata={
                    "description": "Task-related information",
                    "retention_days": 365,
                    "access_frequency": "high",
                },
            )
        )
        
        # Episodic Memory
        self.register_type(
            TypeDefinition(
                memory_type=MemoryType.EPISODIC_MEMORY,
                schema_definition={
                    "fields": {
                        "event_time": {"type": "datetime", "required": False},
                        "event_location": {"type": "string", "required": False},
                        "participants": {"type": "array", "required": False},
                        "emotional_context": {"type": "string", "required": False},
                    }
                },
                validation_rules=["content_not_empty", "max_length_15000"],
                storage_policy=StoragePolicy.STANDARD,
                metadata={
                    "description": "Specific events and experiences",
                    "retention_days": 1825,
                    "access_frequency": "medium",
                },
            )
        )
        
        # Semantic Memory
        self.register_type(
            TypeDefinition(
                memory_type=MemoryType.SEMANTIC_MEMORY,
                schema_definition={
                    "fields": {
                        "knowledge_domain": {"type": "string", "required": False},
                        "fact_type": {"type": "string", "required": False},
                        "confidence": {"type": "float", "required": False},
                    }
                },
                validation_rules=["content_not_empty", "max_length_10000"],
                storage_policy=StoragePolicy.LONG_TERM,
                metadata={
                    "description": "General knowledge and facts",
                    "retention_days": 3650,
                    "access_frequency": "high",
                },
            )
        )
        
        # Emotional Memory
        self.register_type(
            TypeDefinition(
                memory_type=MemoryType.EMOTIONAL_MEMORY,
                schema_definition={
                    "fields": {
                        "emotion_type": {"type": "string", "required": False},
                        "emotion_intensity": {"type": "float", "required": False},
                        "emotion_trigger": {"type": "string", "required": False},
                    }
                },
                validation_rules=["content_not_empty", "max_length_5000"],
                storage_policy=StoragePolicy.STANDARD,
                metadata={
                    "description": "Emotional experiences",
                    "retention_days": 1095,
                    "access_frequency": "medium",
                },
            )
        )
        
        # Temporal Memory
        self.register_type(
            TypeDefinition(
                memory_type=MemoryType.TEMPORAL_MEMORY,
                schema_definition={
                    "fields": {
                        "time_reference": {"type": "datetime", "required": False},
                        "temporal_type": {"type": "string", "required": False},
                        "duration": {"type": "string", "required": False},
                    }
                },
                validation_rules=["content_not_empty", "max_length_5000"],
                storage_policy=StoragePolicy.SHORT_TERM,
                metadata={
                    "description": "Time-related information",
                    "retention_days": 365,
                    "access_frequency": "high",
                },
            )
        )
    
    def register_type(self, type_definition: TypeDefinition) -> None:
        """
        Register a memory type definition.
        
        Args:
            type_definition: The type definition to register
            
        Raises:
            RegistryError: If registration fails
        """
        try:
            memory_type = type_definition.memory_type
            self._type_definitions[memory_type] = type_definition
        except Exception as e:
            raise RegistryError(
                f"Failed to register memory type: {type_definition.memory_type}",
                registry_name="MemoryTypeRegistry",
                details={"error": str(e)}
            )
    
    def get_type(self, memory_type: MemoryType) -> Optional[TypeDefinition]:
        """
        Get a memory type definition.
        
        Args:
            memory_type: The memory type to retrieve
            
        Returns:
            The type definition if found, None otherwise
        """
        return self._type_definitions.get(memory_type)
    
    def get_all_types(self) -> List[MemoryType]:
        """
        Get all registered memory types.
        
        Returns:
            List of all registered memory types
        """
        return list(self._type_definitions.keys())
    
    def validate_type(self, memory_type: MemoryType) -> bool:
        """
        Validate that a memory type is registered.
        
        Args:
            memory_type: The memory type to validate
            
        Returns:
            True if the type is registered, False otherwise
        """
        return memory_type in self._type_definitions
    
    def get_storage_policy(self, memory_type: MemoryType) -> StoragePolicy:
        """
        Get the storage policy for a memory type.
        
        Args:
            memory_type: The memory type
            
        Returns:
            The storage policy for the memory type
            
        Raises:
            InvalidMemoryTypeError: If the memory type is not registered
        """
        type_definition = self.get_type(memory_type)
        if type_definition is None:
            raise InvalidMemoryTypeError(
                memory_type.value,
                valid_types=[mt.value for mt in self.get_all_types()]
            )
        return type_definition.storage_policy
    
    def get_schema(self, memory_type: MemoryType) -> Dict:
        """
        Get the schema definition for a memory type.
        
        Args:
            memory_type: The memory type
            
        Returns:
            The schema definition
            
        Raises:
            InvalidMemoryTypeError: If the memory type is not registered
        """
        type_definition = self.get_type(memory_type)
        if type_definition is None:
            raise InvalidMemoryTypeError(
                memory_type.value,
                valid_types=[mt.value for mt in self.get_all_types()]
            )
        return type_definition.schema_definition
    
    def get_validation_rules(self, memory_type: MemoryType) -> List[str]:
        """
        Get the validation rules for a memory type.
        
        Args:
            memory_type: The memory type
            
        Returns:
            List of validation rule names
            
        Raises:
            InvalidMemoryTypeError: If the memory type is not registered
        """
        type_definition = self.get_type(memory_type)
        if type_definition is None:
            raise InvalidMemoryTypeError(
                memory_type.value,
                valid_types=[mt.value for mt in self.get_all_types()]
            )
        return type_definition.validation_rules
    
    def get_metadata(self, memory_type: MemoryType) -> Dict[str, Any]:
        """
        Get the metadata for a memory type.
        
        Args:
            memory_type: The memory type
            
        Returns:
            The metadata dictionary
            
        Raises:
            InvalidMemoryTypeError: If the memory type is not registered
        """
        type_definition = self.get_type(memory_type)
        if type_definition is None:
            raise InvalidMemoryTypeError(
                memory_type.value,
                valid_types=[mt.value for mt in self.get_all_types()]
            )
        return type_definition.metadata
    
    def unregister_type(self, memory_type: MemoryType) -> bool:
        """
        Unregister a memory type.
        
        Args:
            memory_type: The memory type to unregister
            
        Returns:
            True if unregistered, False if not found
        """
        if memory_type in self._type_definitions:
            del self._type_definitions[memory_type]
            return True
        return False
    
    def get_registry_info(self) -> Dict[str, Any]:
        """
        Get information about the registry.
        
        Returns:
            Dictionary with registry information
        """
        return {
            "total_types": len(self._type_definitions),
            "types": [mt.value for mt in self.get_all_types()],
            "storage_policies": {
                mt.value: self.get_storage_policy(mt).value
                for mt in self.get_all_types()
            },
        }


# Global registry instance
_global_registry: Optional[MemoryTypeRegistry] = None


def get_global_registry() -> MemoryTypeRegistry:
    """
    Get the global memory type registry instance.
    
    Returns:
        The global registry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = MemoryTypeRegistry()
    return _global_registry


def reset_global_registry() -> None:
    """Reset the global registry instance (mainly for testing)."""
    global _global_registry
    _global_registry = None
