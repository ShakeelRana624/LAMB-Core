"""Core interfaces and models for the Attention Engine."""

from attention.core.interfaces import (
    AttentionSignal,
    AttentionResult,
    AttentionContext,
    TemporalContext,
    SocialContext,
)
from attention.core.models import (
    AttentionVector,
    AttentionConfig,
    SignalConfig,
)
from attention.core.exceptions import (
    AttentionEngineError,
    SignalComputationError,
    AggregationError,
)
from attention.core.types import (
    SignalName,
    AggregationStrategy,
)
from attention.core.engine import AttentionEngine

__all__ = [
    "AttentionSignal",
    "AttentionResult",
    "AttentionContext",
    "TemporalContext",
    "SocialContext",
    "AttentionVector",
    "AttentionConfig",
    "SignalConfig",
    "AttentionEngineError",
    "SignalComputationError",
    "AggregationError",
    "SignalName",
    "AggregationStrategy",
    "AttentionEngine",
]
