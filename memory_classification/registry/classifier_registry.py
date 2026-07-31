"""
Classifier Registry implementation.

This module implements the registry pattern for managing classifier instances,
allowing dynamic registration, retrieval, and management of memory classifiers.
"""

from typing import Dict, List, Optional

from memory_classification.core.types import MemoryType
from memory_classification.core.interfaces import MemoryClassifier
from memory_classification.core.exceptions import (
    RegistryError,
    ClassifierNotFoundError,
)


class ClassifierRegistry:
    """
    Registry for managing classifier instances.
    
    This registry maintains the mapping between memory types and their
    corresponding classifier instances, enabling dynamic classifier
    management and lookup.
    """
    
    def __init__(self):
        """Initialize the classifier registry."""
        self._classifiers: Dict[MemoryType, MemoryClassifier] = {}
    
    def register_classifier(self, classifier: MemoryClassifier) -> None:
        """
        Register a classifier instance.
        
        Args:
            classifier: The classifier instance to register
            
        Raises:
            RegistryError: If registration fails
        """
        try:
            memory_type = classifier.memory_type
            self._classifiers[memory_type] = classifier
        except Exception as e:
            raise RegistryError(
                f"Failed to register classifier for memory type: {classifier.memory_type}",
                registry_name="ClassifierRegistry",
                details={"error": str(e)}
            )
    
    def get_classifier(self, memory_type: MemoryType) -> Optional[MemoryClassifier]:
        """
        Get a classifier instance for a memory type.
        
        Args:
            memory_type: The memory type
            
        Returns:
            The classifier instance if found, None otherwise
        """
        return self._classifiers.get(memory_type)
    
    def get_all_classifiers(self) -> List[MemoryClassifier]:
        """
        Get all registered classifier instances.
        
        Returns:
            List of all registered classifiers
        """
        return list(self._classifiers.values())
    
    def get_enabled_classifiers(self) -> List[MemoryClassifier]:
        """
        Get all enabled classifier instances.
        
        Returns:
            List of enabled classifiers
        """
        return [
            classifier for classifier in self._classifiers.values()
            if classifier.is_enabled()
        ]
    
    def get_disabled_classifiers(self) -> List[MemoryClassifier]:
        """
        Get all disabled classifier instances.
        
        Returns:
            List of disabled classifiers
        """
        return [
            classifier for classifier in self._classifiers.values()
            if not classifier.is_enabled()
        ]
    
    def unregister_classifier(self, memory_type: MemoryType) -> bool:
        """
        Unregister a classifier for a memory type.
        
        Args:
            memory_type: The memory type
            
        Returns:
            True if unregistered, False if not found
        """
        if memory_type in self._classifiers:
            del self._classifiers[memory_type]
            return True
        return False
    
    def enable_classifier(self, memory_type: MemoryType) -> bool:
        """
        Enable a classifier for a memory type.
        
        Args:
            memory_type: The memory type
            
        Returns:
            True if enabled, False if classifier not found
            
        Raises:
            ClassifierNotFoundError: If classifier not found
        """
        classifier = self.get_classifier(memory_type)
        if classifier is None:
            raise ClassifierNotFoundError(memory_type.value)
        classifier.enable()
        return True
    
    def disable_classifier(self, memory_type: MemoryType) -> bool:
        """
        Disable a classifier for a memory type.
        
        Args:
            memory_type: The memory type
            
        Returns:
            True if disabled, False if classifier not found
            
        Raises:
            ClassifierNotFoundError: If classifier not found
        """
        classifier = self.get_classifier(memory_type)
        if classifier is None:
            raise ClassifierNotFoundError(memory_type.value)
        classifier.disable()
        return True
    
    def has_classifier(self, memory_type: MemoryType) -> bool:
        """
        Check if a classifier is registered for a memory type.
        
        Args:
            memory_type: The memory type
            
        Returns:
            True if classifier is registered, False otherwise
        """
        return memory_type in self._classifiers
    
    def get_supported_memory_types(self) -> List[MemoryType]:
        """
        Get all memory types that have registered classifiers.
        
        Returns:
            List of memory types with registered classifiers
        """
        return list(self._classifiers.keys())
    
    def get_registry_info(self) -> Dict[str, any]:
        """
        Get information about the registry.
        
        Returns:
            Dictionary with registry information
        """
        return {
            "total_classifiers": len(self._classifiers),
            "enabled_count": len(self.get_enabled_classifiers()),
            "disabled_count": len(self.get_disabled_classifiers()),
            "memory_types": [mt.value for mt in self.get_supported_memory_types()],
            "classifier_metadata": {
                mt.value: classifier.get_metadata()
                for mt, classifier in self._classifiers.items()
            },
        }
    
    def clear(self) -> None:
        """Clear all registered classifiers."""
        self._classifiers.clear()


# Global registry instance
_global_classifier_registry: Optional[ClassifierRegistry] = None


def get_global_classifier_registry() -> ClassifierRegistry:
    """
    Get the global classifier registry instance.
    
    Returns:
        The global classifier registry instance
    """
    global _global_classifier_registry
    if _global_classifier_registry is None:
        _global_classifier_registry = ClassifierRegistry()
    return _global_classifier_registry


def reset_global_classifier_registry() -> None:
    """Reset the global classifier registry instance (mainly for testing)."""
    global _global_classifier_registry
    _global_classifier_registry = None
