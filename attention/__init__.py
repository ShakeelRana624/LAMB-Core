"""
LAMB Attention Engine
=====================

A neuroscience-inspired attention subsystem for the LAMB Cognitive Operating System.
Computes multi-dimensional attention signals before memory storage.
"""

from attention.core.interfaces import (
    AttentionSignal,
    AttentionResult,
    AttentionContext,
)
from attention.core.models import (
    AttentionVector,
    AttentionConfig,
    SignalConfig,
)
from attention.aggregation.aggregator import AttentionAggregator

__version__ = "1.0.0"
__all__ = [
    "AttentionSignal",
    "AttentionResult",
    "AttentionContext",
    "AttentionVector",
    "AttentionConfig",
    "SignalConfig",
    "AttentionAggregator",
]
