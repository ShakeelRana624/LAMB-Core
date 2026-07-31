"""
Emotional Memory classifier implementation.

This module implements the classifier for EmotionalMemory, which detects
emotional experiences, mood states, and affective reactions.
"""

import re
from typing import Dict, Any

from memory_classification.core.types import MemoryType
from memory_classification.core.interfaces import MemoryInput
from memory_classification.classifiers.base import BaseClassifier


class EmotionalClassifier(BaseClassifier):
    """
    Classifier for Emotional Memory.
    
    Detects emotional-related information including:
    - Emotional experiences
    - Mood states
    - Affective reactions
    - Emotional triggers
    """
    
    # Emotional patterns
    EMOTIONAL_PATTERNS = [
        r"\b(feel|feeling|felt|emotion)\b",
        r"\b(happy|sad|angry|excited|anxious)\b",
        r"\b(love|hate|fear|joy|surprise)\b",
        r"\b(mood|emotional|affect)\b",
        r"\b(experience|reaction|response)\b",
    ]
    
    # Emotion type patterns
    POSITIVE_EMOTIONS = [
        r"\b(happy|joy|excited|pleased|delighted)\b",
        r"\b(love|like|enjoy|appreciate)\b",
    ]
    
    NEGATIVE_EMOTIONS = [
        r"\b(sad|angry|fear|hate|anxious)\b",
        r"\b(upset|frustrated|worried|scared)\b",
    ]
    
    def __init__(
        self,
        confidence_threshold: float = 0.5,
        enabled: bool = True,
    ):
        """Initialize the emotional classifier."""
        super().__init__(MemoryType.EMOTIONAL_MEMORY, confidence_threshold, enabled)
    
    async def _compute_score(self, memory_input: MemoryInput) -> float:
        """
        Compute emotional score based on pattern matching.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Raw emotional score
        """
        text = memory_input.content.lower()
        
        # Pattern matching for emotional indicators
        emotional_matches = 0
        for pattern in self.EMOTIONAL_PATTERNS:
            emotional_matches += self._count_pattern_matches(text, pattern)
        
        # Normalize score
        emotional_score = self._normalize_score(emotional_matches, 0, 3)
        
        return emotional_score
    
    def _generate_reasoning(self, score: float, memory_input: MemoryInput) -> str:
        """
        Generate reasoning for the emotional classification.
        
        Args:
            score: The normalized score
            memory_input: The memory input
            
        Returns:
            Reasoning string
        """
        text = memory_input.content.lower()
        
        if score >= 0.8:
            return f"High confidence emotional information (score: {score:.2f}), contains explicit emotional statements"
        elif score >= 0.5:
            return f"Moderate confidence emotional information (score: {score:.2f}), contains some emotional indicators"
        else:
            return f"Low confidence emotional information (score: {score:.2f}), minimal emotional indicators"
    
    def _extract_attributes(self, memory_input: MemoryInput) -> Dict[str, Any]:
        """
        Extract emotional attributes from the memory input.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Dictionary of extracted attributes
        """
        text = memory_input.content
        text_lower = text.lower()
        attributes = {}
        
        # Determine emotion type
        if any(self._match_pattern(text_lower, pattern) for pattern in self.POSITIVE_EMOTIONS):
            attributes["emotion_type"] = "positive"
        elif any(self._match_pattern(text_lower, pattern) for pattern in self.NEGATIVE_EMOTIONS):
            attributes["emotion_type"] = "negative"
        else:
            attributes["emotion_type"] = "neutral"
        
        # Extract emotion intensity
        if self._match_pattern(text_lower, r"\b(very|extremely|intensely)\b"):
            attributes["emotion_intensity"] = "high"
        elif self._match_pattern(text_lower, r"\b(somewhat|moderately)\b"):
            attributes["emotion_intensity"] = "medium"
        else:
            attributes["emotion_intensity"] = "low"
        
        # Extract emotion trigger
        trigger_match = re.search(r"(?:because|due to|when)\s+(.+?)(?:\.|$)", text, re.IGNORECASE)
        if trigger_match:
            attributes["emotion_trigger"] = trigger_match.group(1).strip()
        
        return attributes
