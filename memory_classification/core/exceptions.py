"""
Custom exceptions for the Memory Classification Engine.

This module defines specific exceptions for classification-related errors
to enable precise error handling and debugging.
"""


class ClassificationError(Exception):
    """
    Base exception for all classification-related errors.
    
    All specific classification exceptions inherit from this base class
    to enable catch-all error handling when needed.
    """
    
    def __init__(self, message: str, details: dict = None):
        """
        Initialize classification error.
        
        Args:
            message: Error message
            details: Additional error details for debugging
        """
        super().__init__(message)
        self.details = details or {}
    
    def __str__(self) -> str:
        """Return string representation."""
        if self.details:
            return f"{super().__str__()} | Details: {self.details}"
        return super().__str__()


class ClassifierNotFoundError(ClassificationError):
    """
    Exception raised when a requested classifier is not found.
    
    This occurs when attempting to use a memory type classifier
    that has not been registered or is disabled.
    """
    
    def __init__(self, memory_type: str, details: dict = None):
        """
        Initialize classifier not found error.
        
        Args:
            memory_type: The memory type for which classifier was not found
            details: Additional error details
        """
        message = f"Classifier not found for memory type: {memory_type}"
        super().__init__(message, details)
        self.memory_type = memory_type


class ClassificationFailedError(ClassificationError):
    """
    Exception raised when classification fails.
    
    This occurs when the classification process encounters an error
    during execution, such as invalid input or processing failure.
    """
    
    def __init__(self, message: str, memory_input: dict = None, details: dict = None):
        """
        Initialize classification failed error.
        
        Args:
            message: Error message
            memory_input: The memory input that caused the failure
            details: Additional error details
        """
        super().__init__(message, details)
        self.memory_input = memory_input


class InvalidMemoryTypeError(ClassificationError):
    """
    Exception raised when an invalid memory type is provided.
    
    This occurs when using a memory type that is not defined in the
    MemoryType enum or is not supported by the system.
    """
    
    def __init__(self, memory_type: str, valid_types: list = None, details: dict = None):
        """
        Initialize invalid memory type error.
        
        Args:
            memory_type: The invalid memory type
            valid_types: List of valid memory types
            details: Additional error details
        """
        message = f"Invalid memory type: {memory_type}"
        if valid_types:
            message += f". Valid types: {', '.join(valid_types)}"
        super().__init__(message, details)
        self.memory_type = memory_type
        self.valid_types = valid_types


class ConfigurationError(ClassificationError):
    """
    Exception raised when configuration is invalid.
    
    This occurs when the classification configuration contains
    invalid values, missing required fields, or incompatible settings.
    """
    
    def __init__(self, message: str, config_key: str = None, details: dict = None):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            config_key: The configuration key that caused the error
            details: Additional error details
        """
        super().__init__(message, details)
        self.config_key = config_key


class StorageError(ClassificationError):
    """
    Exception raised when storage operations fail.
    
    This occurs when routing or storing classified memories fails,
    such as storage backend unavailability or capacity issues.
    """
    
    def __init__(self, message: str, storage_location: str = None, details: dict = None):
        """
        Initialize storage error.
        
        Args:
            message: Error message
            storage_location: The storage location that failed
            details: Additional error details
        """
        super().__init__(message, details)
        self.storage_location = storage_location


class RegistryError(ClassificationError):
    """
    Exception raised when registry operations fail.
    
    This occurs when registering or retrieving items from the
    memory type or classifier registries fails.
    """
    
    def __init__(self, message: str, registry_name: str = None, details: dict = None):
        """
        Initialize registry error.
        
        Args:
            message: Error message
            registry_name: The registry that caused the error
            details: Additional error details
        """
        super().__init__(message, details)
        self.registry_name = registry_name


class ValidationError(ClassificationError):
    """
    Exception raised when validation fails.
    
    This occurs when memory input or classification results fail
    validation checks.
    """
    
    def __init__(self, message: str, validation_errors: list = None, details: dict = None):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            validation_errors: List of specific validation errors
            details: Additional error details
        """
        super().__init__(message, details)
        self.validation_errors = validation_errors or []


class DuplicateMemoryError(ClassificationError):
    """
    Exception raised when a duplicate memory is detected.
    
    This occurs when attempting to store a memory that already exists
    in the storage system.
    """
    
    def __init__(self, message: str, memory_id: str = None, details: dict = None):
        """
        Initialize duplicate memory error.
        
        Args:
            message: Error message
            memory_id: The ID of the duplicate memory
            details: Additional error details
        """
        super().__init__(message, details)
        self.memory_id = memory_id
