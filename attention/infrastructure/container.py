"""
Dependency Injection Container for the Attention Engine.

This module provides a simple DI container for managing
dependencies and enabling testability.
"""

from typing import TypeVar, Type, Callable, Dict, Any, Optional
from functools import lru_cache

T = TypeVar("T")


class DIContainer:
    """
    Simple dependency injection container.
    
    Supports:
    - Transient dependencies (new instance each time)
    - Singleton dependencies (shared instance)
    - Factory functions
    """
    
    def __init__(self):
        """Initialize the DI container."""
        self._factories: Dict[Type, Callable[..., T]] = {}
        self._singletons: Dict[Type, T] = {}
    
    def register(
        self,
        interface: Type[T],
        factory: Callable[..., T],
        singleton: bool = False,
    ) -> None:
        """
        Register a dependency factory.
        
        Args:
            interface: Interface or class to register
            factory: Factory function to create instances
            singleton: Whether to register as singleton
        """
        if singleton:
            self._singletons[interface] = factory()
        else:
            self._factories[interface] = factory
    
    def register_singleton(self, interface: Type[T], instance: T) -> None:
        """
        Register a singleton instance.
        
        Args:
            interface: Interface or class to register
            instance: Instance to register
        """
        self._singletons[interface] = instance
    
    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve a dependency.
        
        Args:
            interface: Interface or class to resolve
            
        Returns:
            Instance of the requested type
            
        Raises:
            KeyError: If dependency not registered
        """
        # Check singletons first
        if interface in self._singletons:
            return self._singletons[interface]
        
        # Check factories
        if interface in self._factories:
            return self._factories[interface]()
        
        raise KeyError(f"Dependency {interface} not registered")
    
    def has(self, interface: Type[T]) -> bool:
        """
        Check if a dependency is registered.
        
        Args:
            interface: Interface or class to check
            
        Returns:
            True if registered
        """
        return interface in self._singletons or interface in self._factories
    
    def clear(self) -> None:
        """Clear all registered dependencies."""
        self._factories.clear()
        self._singletons.clear()


# Global container instance
_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
    """
    Get the global DI container.
    
    Returns:
        DIContainer instance
    """
    global _container
    if _container is None:
        _container = DIContainer()
    return _container
