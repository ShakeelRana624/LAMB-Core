"""
Pydantic models for the Attention Engine.

This module defines the data models used throughout the Attention Engine,
ensuring type safety, validation, and serialization capabilities.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional
from datetime import datetime

from attention.core.types import SignalName, AggregationStrategy


class SignalConfig(BaseModel):
    """
    Configuration for a single attention signal.
    
    Each signal can be independently configured with:
    - enabled: Whether the signal participates in aggregation
    - weight: Relative importance in aggregation (0.0 - 1.0)
    - threshold: Minimum score to consider signal active (0.0 - 1.0)
    - parameters: Signal-specific parameters
    """
    enabled: bool = True
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    threshold: float = Field(default=0.0, ge=0.0, le=1.0)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('weight')
    def validate_weight(cls, v):
        """Ensure weight is within valid range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"weight must be between 0.0 and 1.0, got {v}")
        return v
    
    @validator('threshold')
    def validate_threshold(cls, v):
        """Ensure threshold is within valid range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"threshold must be between 0.0 and 1.0, got {v}")
        return v
    
    class Config:
        """Pydantic configuration."""
        extra = "forbid"  # Disallow extra fields


class AttentionConfig(BaseModel):
    """
    Global attention engine configuration.
    
    This model contains all configuration for the Attention Engine,
    including signal-specific configs and global settings.
    """
    # Signal configurations
    signals: Dict[str, SignalConfig] = Field(default_factory=dict)
    
    # Aggregation settings
    aggregation_strategy: AggregationStrategy = "weighted_sum"
    storage_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Performance settings
    enable_caching: bool = True
    cache_ttl_seconds: int = Field(default=300, ge=0)
    parallel_execution: bool = True
    max_concurrent_signals: int = Field(default=13, ge=1)
    
    # Observability settings
    enable_telemetry: bool = True
    enable_logging: bool = True
    log_level: str = Field(default="INFO")
    log_computation_times: bool = True
    
    # Feature flags
    enable_ml_signals: bool = False
    enable_external_services: bool = False
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Ensure log level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}, got {v}")
        return v.upper()
    
    @validator('storage_threshold')
    def validate_storage_threshold(cls, v):
        """Ensure storage threshold is within valid range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"storage_threshold must be between 0.0 and 1.0, got {v}")
        return v
    
    def get_signal_config(self, signal_name: str) -> SignalConfig:
        """
        Get configuration for a specific signal.
        
        Args:
            signal_name: Name of the signal
            
        Returns:
            SignalConfig for the signal, or default if not found
        """
        return self.signals.get(signal_name, SignalConfig())
    
    def set_signal_config(self, signal_name: str, config: SignalConfig) -> None:
        """
        Set configuration for a specific signal.
        
        Args:
            signal_name: Name of the signal
            config: Configuration to set
        """
        self.signals[signal_name] = config
    
    def get_enabled_signals(self) -> list[str]:
        """
        Get list of enabled signal names.
        
        Returns:
            List of signal names that are enabled
        """
        return [
            name for name, config in self.signals.items()
            if config.enabled
        ]
    
    class Config:
        """Pydantic configuration."""
        extra = "forbid"  # Disallow extra fields


class AttentionVector(BaseModel):
    """
    Complete attention vector containing all signal results.
    
    This model encapsulates the results from all attention signals,
    the aggregated score, and the storage decision.
    """
    # Individual signal results
    novelty: Optional[float] = None
    goal_relevance: Optional[float] = None
    urgency: Optional[float] = None
    reward: Optional[float] = None
    risk: Optional[float] = None
    emotion: Optional[float] = None
    curiosity: Optional[float] = None
    surprise: Optional[float] = None
    confidence: Optional[float] = None
    future_utility: Optional[float] = None
    social_importance: Optional[float] = None
    repetition: Optional[float] = None
    current_task_match: Optional[float] = None
    
    # Detailed results (for debugging/analysis)
    signal_results: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Aggregated results
    aggregated_score: float = Field(default=0.0, ge=0.0, le=1.0)
    should_store: bool = False
    
    # Metadata
    computation_time_ms: float = Field(default=0.0, ge=0.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: str = ""
    agent_id: str = ""
    
    @validator('aggregated_score')
    def validate_aggregated_score(cls, v):
        """Ensure aggregated score is within valid range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"aggregated_score must be between 0.0 and 1.0, got {v}")
        return v
    
    def set_signal_result(self, signal_name: str, result: Dict[str, Any]) -> None:
        """
        Set the result for a specific signal.
        
        Args:
            signal_name: Name of the signal
            result: Result dictionary with score, explanation, etc.
        """
        self.signal_results[signal_name] = result
        # Also set the direct field if it exists
        if hasattr(self, signal_name):
            setattr(self, signal_name, result.get("score"))
    
    def get_signal_score(self, signal_name: str) -> Optional[float]:
        """
        Get the score for a specific signal.
        
        Args:
            signal_name: Name of the signal
            
        Returns:
            Signal score, or None if not computed
        """
        result = self.signal_results.get(signal_name)
        return result.get("score") if result else None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization.
        
        Returns:
            Dictionary representation of the attention vector
        """
        return {
            "signals": {
                name: self.get_signal_score(name)
                for name in SignalName
            },
            "signal_results": self.signal_results,
            "aggregated_score": self.aggregated_score,
            "should_store": self.should_store,
            "computation_time_ms": self.computation_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
            "agent_id": self.agent_id,
        }
    
    class Config:
        """Pydantic configuration."""
        extra = "forbid"  # Disallow extra fields
        use_enum_values = True  # Use enum values instead of objects
