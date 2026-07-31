"""Attention signal implementations."""

from attention.signals.base import BaseSignal
from attention.signals.novelty import NoveltySignal
from attention.signals.goal_relevance import GoalRelevanceSignal
from attention.signals.urgency import UrgencySignal
from attention.signals.reward import RewardSignal
from attention.signals.risk import RiskSignal
from attention.signals.emotion import EmotionSignal
from attention.signals.curiosity import CuriositySignal
from attention.signals.surprise import SurpriseSignal
from attention.signals.confidence import ConfidenceSignal
from attention.signals.future_utility import FutureUtilitySignal
from attention.signals.social_importance import SocialImportanceSignal
from attention.signals.repetition import RepetitionSignal
from attention.signals.current_task_match import CurrentTaskMatchSignal

__all__ = [
    "BaseSignal",
    "NoveltySignal",
    "GoalRelevanceSignal",
    "UrgencySignal",
    "RewardSignal",
    "RiskSignal",
    "EmotionSignal",
    "CuriositySignal",
    "SurpriseSignal",
    "ConfidenceSignal",
    "FutureUtilitySignal",
    "SocialImportanceSignal",
    "RepetitionSignal",
    "CurrentTaskMatchSignal",
]
