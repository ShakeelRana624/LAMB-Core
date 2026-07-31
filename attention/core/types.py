"""Type definitions and enums for the Attention Engine."""

from enum import Enum
from typing import Literal

# Signal names as enum for type safety
class SignalName(str, Enum):
    """All available attention signal names."""
    NOVELTY = "novelty"
    GOAL_RELEVANCE = "goal_relevance"
    URGENCY = "urgency"
    REWARD = "reward"
    RISK = "risk"
    EMOTION = "emotion"
    CURIOSITY = "curiosity"
    SURPRISE = "surprise"
    CONFIDENCE = "confidence"
    FUTURE_UTILITY = "future_utility"
    SOCIAL_IMPORTANCE = "social_importance"
    REPETITION = "repetition"
    CURRENT_TASK_MATCH = "current_task_match"


# Aggregation strategies
AggregationStrategy = Literal[
    "weighted_sum",
    "geometric_mean",
    "maximum",
    "minimum",
    "harmonic_mean",
    "custom_ml",
]
