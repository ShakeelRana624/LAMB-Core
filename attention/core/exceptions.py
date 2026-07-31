"""Custom exceptions for the Attention Engine."""


class AttentionEngineError(Exception):
    """Base exception for all Attention Engine errors."""
    pass


class SignalComputationError(AttentionEngineError):
    """Raised when a signal computation fails."""
    
    def __init__(self, signal_name: str, reason: str):
        self.signal_name = signal_name
        self.reason = reason
        super().__init__(f"Signal '{signal_name}' computation failed: {reason}")


class AggregationError(AttentionEngineError):
    """Raised when aggregation fails."""
    
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Aggregation failed: {reason}")


class ConfigurationError(AttentionEngineError):
    """Raised when configuration is invalid."""
    
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Configuration error: {reason}")


class SignalNotFoundError(AttentionEngineError):
    """Raised when a requested signal is not found."""
    
    def __init__(self, signal_name: str):
        self.signal_name = signal_name
        super().__init__(f"Signal '{signal_name}' not found in registry")
