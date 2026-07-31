"""
Preference Memory classifier implementation.

This module implements the classifier for PreferenceMemory, which detects
user preferences, likes, dislikes, and personal choices.
"""

import re
from typing import Dict, Any

from memory_classification.core.types import MemoryType
from memory_classification.core.interfaces import MemoryInput
from memory_classification.classifiers.base import BaseClassifier


class PreferenceClassifier(BaseClassifier):
    """
    Classifier for Preference Memory.
    
    Detects preference-related information including:
    - Likes and dislikes
    - Personal preferences
    - Choices and decisions
    - Personal tastes
    """
    
    # Preference patterns
    PREFERENCE_PATTERNS = [
        r"\b(i like|i love|i enjoy|i prefer)\b",
        r"\b(i dislike|i hate|i can't stand)\b",
        r"\b(my favorite|favourite)\b",
        r"\b(prefer|rather)\b",
        r"\b(choice|choose|chose)\b",
        r"\b(taste|style)\b",
    ]
    
    # Like patterns
    LIKE_PATTERNS = [
        r"\b(like|love|enjoy|prefer|favorite)\b",
    ]
    
    # Dislike patterns
    DISLIKE_PATTERNS = [
        r"\b(dislike|hate|can't stand|avoid)\b",
    ]
    
    def __init__(
        self,
        confidence_threshold: float = 0.5,
        enabled: bool = True,
    ):
        """Initialize the preference classifier."""
        super().__init__(MemoryType.PREFERENCE_MEMORY, confidence_threshold, enabled)
    
    async def _compute_score(self, memory_input: MemoryInput) -> float:
        """
        Compute preference score based on pattern matching.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Raw preference score
        """
        text = memory_input.content.lower()
        
        # Pattern matching for preference indicators
        preference_matches = 0
        for pattern in self.PREFERENCE_PATTERNS:
            preference_matches += self._count_pattern_matches(text, pattern)
        
        # Normalize score
        preference_score = self._normalize_score(preference_matches, 0, 3)
        
        return preference_score
    
    def _generate_reasoning(self, score: float, memory_input: MemoryInput) -> str:
        """
        Generate reasoning for the preference classification.
        
        Args:
            score: The normalized score
            memory_input: The memory input
            
        Returns:
            Reasoning string
        """
        text = memory_input.content.lower()
        
        if score >= 0.8:
            return f"High confidence preference information (score: {score:.2f}), contains explicit preference statements"
        elif score >= 0.5:
            return f"Moderate confidence preference information (score: {score:.2f}), contains some preference indicators"
        else:
            return f"Low confidence preference information (score: {score:.2f}), minimal preference indicators"
    
    def _extract_attributes(self, memory_input: MemoryInput) -> Dict[str, Any]:
        """
        Extract preference attributes from the memory input.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Dictionary of extracted attributes
        """
        text = memory_input.content
        attributes = {}
        
        # Determine sentiment
        text_lower = text.lower()
        if any(self._match_pattern(text_lower, pattern) for pattern in self.LIKE_PATTERNS):
            attributes["sentiment"] = "positive"
        elif any(self._match_pattern(text_lower, pattern) for pattern in self.DISLIKE_PATTERNS):
            attributes["sentiment"] = "negative"
        else:
            attributes["sentiment"] = "neutral"
        
        # Extract preference type
        pref_match = re.search(r"(?:i (?:like|love|prefer|enjoy))\s+(.+?)(?:\.|$)", text, re.IGNORECASE)
        if pref_match:
            attributes["preference_value"] = pref_match.group(1).strip()
        
        return attributes
