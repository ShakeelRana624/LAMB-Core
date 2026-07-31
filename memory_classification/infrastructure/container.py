"""
Dependency Injection container for the Memory Classification Engine.

This module provides a simple DI container for managing dependencies
within the classification system, enabling testability and loose coupling.
"""

from typing import Dict, Any, Callable, Optional, TypeVar, Type

T = TypeVar('T')


class DIContainer:
    """
    Simple dependency injection container.
    
    Supports singleton and factory registrations for managing
    dependencies in the classification system.
    """
    
    def __init__(self):
        """Initialize the DI container."""
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._types: Dict[str, Type] = {}
    
    def register_singleton(
        self,
        name: str,
        instance: Any,
    ) -> None:
        """
        Register a singleton instance.
        
        Args:
            name: Name of the dependency
            instance: Instance to register
        """
        self._singletons[name] = instance
    
    def register_factory(
        self,
        name: str,
        factory: Callable,
    ) -> None:
        """
        Register a factory function.
        
        Args:
            name: Name of the dependency
            factory: Factory function to create instances
        """
        self._factories[name] = factory
    
    def register_type(
        self,
        name: str,
        type_: Type[T],
    ) -> None:
        """
        Register a type for instantiation.
        
        Args:
            name: Name of the dependency
            type_: Type to register
        """
        self._types[name] = type_
    
    def get(self, name: str) -> Any:
        """
        Get a dependency by name.
        
        Args:
            name: Name of the dependency
            
        Returns:
            The dependency instance
            
        Raises:
            KeyError: If dependency not found
        """
        # Check singletons first
        if name in self._singletons:
            return self._singletons[name]
        
        # Check factories
        if name in self._factories:
            return self._factories[name]()
        
        # Check types
        if name in self._types:
            return self._types[name]()
        
        raise KeyError(f"Dependency '{name}' not found in container")
    
    def get_or_default(self, name: str, default: Any = None) -> Any:
        """
        Get a dependency by name with default fallback.
        
        Args:
            name: Name of the dependency
            default: Default value if not found
            
        Returns:
            The dependency instance or default
        """
        try:
            return self.get(name)
        except KeyError:
            return default
    
    def has(self, name: str) -> bool:
        """
        Check if a dependency is registered.
        
        Args:
            name: Name of the dependency
            
        Returns:
            True if registered, False otherwise
        """
        return name in self._singletons or name in self._factories or name in self._types
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a dependency.
        
        Args:
            name: Name of the dependency
            
        Returns:
            True if unregistered, False if not found
        """
        removed = False
        
        if name in self._singletons:
            del self._singletons[name]
            removed = True
        
        if name in self._factories:
            del self._factories[name]
            removed = True
        
        if name in self._types:
            del self._types[name]
            removed = True
        
        return removed
    
    def clear(self) -> None:
        """Clear all registered dependencies."""
        self._singletons.clear()
        self._factories.clear()
        self._types.clear()
    
    def get_all_names(self) -> list:
        """
        Get all registered dependency names.
        
        Returns:
            List of dependency names
        """
        return list(set(self._singletons.keys()) | set(self._factories.keys()) | set(self._types.keys()))


# Global container instance
_global_container: Optional[DIContainer] = None


def get_global_container() -> DIContainer:
    """
    Get the global DI container instance.
    
    Returns:
        The global container instance
    """
    global _global_container
    if _global_container is None:
        _global_container = DIContainer()
    return _global_container


def reset_global_container() -> None:
    """Reset the global container instance (mainly for testing)."""
    global _global_container
    _global_container = None
