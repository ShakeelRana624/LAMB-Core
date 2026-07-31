"""
Core interfaces for the Attention Engine.

This module defines the abstract base classes and protocols that all
attention signals must implement, ensuring pluggability and testability.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from attention.core.types import SignalName


class TemporalContext:
    """Temporal context for attention computation."""
    
    def __init__(
        self,
        current_time: Optional[datetime] = None,
        time_of_day: Optional[str] = None,
        day_of_week: Optional[str] = None,
        season: Optional[str] = None,
        timezone: Optional[str] = None,
    ):
        self.current_time = current_time or datetime.utcnow()
        self.time_of_day = time_of_day
        self.day_of_week = day_of_week
        self.season = season
        self.timezone = timezone


class SocialContext:
    """Social context for attention computation."""
    
    def __init__(
        self,
        participants: Optional[list[str]] = None,
        relationship_type: Optional[str] = None,
        group_size: Optional[int] = None,
        social_importance: Optional[float] = None,
    ):
        self.participants = participants or []
        self.relationship_type = relationship_type
        self.group_size = group_size
        self.social_importance = social_importance


@dataclass
class AttentionContext:
    """
    Context provided to all attention signals.
    
    This dataclass encapsulates all contextual information needed
    for attention signal computation, following the dependency
    injection principle.
    """
    input_text: str
    session_id: str
    agent_id: str
    current_goal: Optional[str] = None
    current_task: Optional[str] = None
    temporal_context: Optional[TemporalContext] = None
    social_context: Optional[SocialContext] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate context after initialization."""
        if not self.input_text or not self.input_text.strip():
            raise ValueError("input_text cannot be empty")
        if not self.session_id or not self.session_id.strip():
            raise ValueError("session_id cannot be empty")
        if not self.agent_id or not self.agent_id.strip():
            raise ValueError("agent_id cannot be empty")


@dataclass
class AttentionResult:
    """
    Result from a single attention signal computation.
    
    Encapsulates the normalized score, explanation, and metadata
    for a single attention signal, providing transparency and
    debuggability.
    """
    score: float  # Normalized 0.0 - 1.0
    explanation: str
    signal_name: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    computation_time_ms: float = 0.0
    
    def __post_init__(self):
        """Validate result after initialization."""
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"score must be between 0.0 and 1.0, got {self.score}")
        if not self.explanation or not self.explanation.strip():
            raise ValueError("explanation cannot be empty")
        if self.computation_time_ms < 0:
            raise ValueError("computation_time_ms cannot be negative")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "score": self.score,
            "explanation": self.explanation,
            "signal_name": self.signal_name,
            "metadata": self.metadata,
            "computation_time_ms": self.computation_time_ms,
        }


class AttentionSignal(ABC):
    """
    Abstract base class for all attention signals.
    
    This interface ensures all attention signals are:
    - Pluggable: Can be swapped without changing the engine
    - Testable: Can be mocked for unit testing
    - Observable: Provide computation time and explanations
    - Configurable: Support external configuration
    
    Implementation must follow the Single Responsibility Principle:
    each signal computes ONE aspect of attention.
    """
    
    def __init__(self, weight: float = 1.0, enabled: bool = True):
        """
        Initialize the attention signal.
        
        Args:
            weight: Configured weight for this signal (0.0 - 1.0)
            enabled: Whether this signal is enabled
        """
        if not 0.0 <= weight <= 1.0:
            raise ValueError(f"weight must be between 0.0 and 1.0, got {weight}")
        self._weight = weight
        self._enabled = enabled
    
    @abstractmethod
    async def compute(self, context: AttentionContext) -> AttentionResult:
        """
        Compute the attention signal score.
        
        This method must be implemented by all concrete signals.
        It should:
        - Return a normalized score between 0.0 and 1.0
        - Provide a human-readable explanation
        - Include relevant metadata for debugging
        - Track computation time
        
        Args:
            context: The attention context containing input and metadata
            
        Returns:
            AttentionResult with score, explanation, and metadata
            
        Raises:
            SignalComputationError: If computation fails
        """
        pass
    
    def get_weight(self) -> float:
        """Return the configured weight for this signal."""
        return self._weight
    
    def set_weight(self, weight: float) -> None:
        """Update the weight for this signal."""
        if not 0.0 <= weight <= 1.0:
            raise ValueError(f"weight must be between 0.0 and 1.0, got {weight}")
        self._weight = weight
    
    def is_enabled(self) -> bool:
        """Return whether this signal is enabled."""
        return self._enabled
    
    def enable(self) -> None:
        """Enable this signal."""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable this signal."""
        self._enabled = False
    
    @property
    @abstractmethod
    def signal_name(self) -> str:
        """
        Return the unique name of this signal.
        
        This must match one of the SignalName enum values.
        """
        pass
    
    async def compute_with_timing(self, context: AttentionContext) -> AttentionResult:
        """
        Compute the signal with automatic timing.
        
        This is a convenience method that wraps compute() with
        timing instrumentation. Subclasses should override compute()
        directly, not this method.
        
        Args:
            context: The attention context
            
        Returns:
            AttentionResult with computation time populated
        """
        import time
        start_time = time.perf_counter()
        
        try:
            result = await self.compute(context)
        except Exception as e:
            from attention.core.exceptions import SignalComputationError
            raise SignalComputationError(self.signal_name, str(e))
        
        end_time = time.perf_counter()
        result.computation_time_ms = (end_time - start_time) * 1000
        result.signal_name = self.signal_name
        
        return result
