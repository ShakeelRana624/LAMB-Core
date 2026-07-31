"""
Reward Signal Implementation.

Detects positive outcomes, achievements, and beneficial information
using pattern matching and sentiment analysis.
"""

import re
from typing import List

from attention.core.interfaces import AttentionContext, AttentionResult
from attention.core.types import SignalName
from attention.signals.base import BaseSignal


class RewardSignal(BaseSignal):
    """
    Reward attention signal.
    
    Detects positive outcomes and achievements through:
    1. Pattern matching for success indicators
    2. Sentiment analysis for positive sentiment
    3. Achievement detection
    
    High reward indicates beneficial information worth remembering.
    """
    
    # Reward patterns
    REWARD_PATTERNS = [
        r"\b(success|successful|achieved|accomplished|completed|finished)\b",
        r"\b(won|victory|passed|approved|accepted)\b",
        r"\b(great|excellent|perfect|amazing|wonderful|outstanding)\b",
        r"\b(progress|improvement|breakthrough|milestone)\b",
        r"\b(solved|fixed|resolved|worked)\b",
        r"\b(goal|target|objective met|reached)\b",
    ]
    
    POSITIVE_SENTIMENT_PATTERNS = [
        r"\b(happy|excited|pleased|satisfied|delighted|thrilled)\b",
        r"\b(love|enjoy|appreciate|grateful)\b",
        r"\b(confident|optimistic|hopeful)\b",
    ]
    
    def __init__(
        self,
        weight: float = 0.08,
        enabled: bool = True,
        enable_sentiment_analysis: bool = True,
    ):
        """
        Initialize the reward signal.
        
        Args:
            weight: Signal weight in aggregation (default: 0.08)
            enabled: Whether signal is enabled
            enable_sentiment_analysis: Whether to perform sentiment analysis
        """
        super().__init__(weight, enabled)
        self.enable_sentiment_analysis = enable_sentiment_analysis
    
    @property
    def signal_name(self) -> str:
        """Return the signal name."""
        return SignalName.REWARD.value
    
    async def _compute_score(self, context: AttentionContext) -> float:
        """
        Compute reward score.
        
        Reward is computed by:
        1. Pattern matching for reward indicators
        2. Sentiment analysis for positive sentiment
        3. Achievement detection
        
        Args:
            context: The attention context
            
        Returns:
            Reward score between 0.0 and 1.0
        """
        text = context.input_text.lower()
        
        # Pattern matching for reward indicators
        reward_matches = 0
        for pattern in self.REWARD_PATTERNS:
            reward_matches += super()._count_pattern_matches(text, pattern)
        pattern_score = self._normalize_score(reward_matches, 0, 3)
        
        # Sentiment analysis if enabled
        sentiment_score = 0.0
        if self.enable_sentiment_analysis:
            sentiment_score = self._compute_sentiment_score(text)
        
        # Achievement detection from metadata
        achievement_score = self._compute_achievement_score(context)
        
        # Combine scores
        final_score = (
            (pattern_score * 0.5) +
            (sentiment_score * 0.3) +
            (achievement_score * 0.2)
        )
        
        return self._clamp_score(final_score)
    
    def _compute_sentiment_score(self, text: str) -> float:
        """
        Compute sentiment score using pattern matching.
        
        Args:
            text: Input text
            
        Returns:
            Sentiment score between 0.0 and 1.0
        """
        positive_matches = self._count_pattern_matches(text, self.POSITIVE_SENTIMENT_PATTERNS)
        return self._normalize_score(positive_matches, 0, 2)
    
    def _compute_achievement_score(self, context: AttentionContext) -> float:
        """
        Compute achievement score from context metadata.
        
        Args:
            context: Attention context
            
        Returns:
            Achievement score between 0.0 and 1.0
        """
        # Check for achievement markers in metadata
        is_achievement = context.metadata.get("is_achievement", False)
        achievement_type = context.metadata.get("achievement_type")
        
        if is_achievement:
            if achievement_type == "major":
                return 1.0
            elif achievement_type == "minor":
                return 0.7
            else:
                return 0.5
        
        return 0.0
    
    def _generate_explanation(self, score: float, context: AttentionContext) -> str:
        """Generate explanation for the reward score."""
        text = context.input_text.lower()
        
        if score >= 0.8:
            return f"Input indicates high reward (score: {score:.2f}), contains success or achievement indicators."
        elif score >= 0.5:
            return f"Input indicates moderate reward (score: {score:.2f}), some positive elements detected."
        elif score >= 0.3:
            return f"Input indicates low reward (score: {score:.2f}), minimal positive indicators."
        else:
            return f"Input indicates no reward (score: {score:.2f}), no positive or achievement indicators."
    
    def _build_metadata(self, score: float, context: AttentionContext) -> dict:
        """Build metadata with reward-specific information."""
        metadata = super()._build_metadata(score, context)
        text = context.input_text.lower()
        
        metadata.update({
            "reward_matches": self._count_pattern_matches(text, self.REWARD_PATTERNS),
            "positive_sentiment_matches": self._count_pattern_matches(text, self.POSITIVE_SENTIMENT_PATTERNS),
            "is_achievement": context.metadata.get("is_achievement", False),
            "achievement_type": context.metadata.get("achievement_type"),
            "enable_sentiment_analysis": self.enable_sentiment_analysis,
        })
        return metadata
