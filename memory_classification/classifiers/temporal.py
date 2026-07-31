"""
Temporal Memory classifier implementation.

This module implements the classifier for TemporalMemory, which detects
time-related information, schedules, deadlines, and temporal patterns.
"""

import re
from typing import Dict, Any

from memory_classification.core.types import MemoryType
from memory_classification.core.interfaces import MemoryInput
from memory_classification.classifiers.base import BaseClassifier


class TemporalClassifier(BaseClassifier):
    """
    Classifier for Temporal Memory.
    
    Detects temporal-related information including:
    - Time-related information
    - Schedules and deadlines
    - Temporal patterns
    - Duration and timing
    """
    
    # Temporal patterns
    TEMPORAL_PATTERNS = [
        r"\b(yesterday|today|tomorrow|now|soon|later)\b",
        r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
        r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\b",
        r"\b(morning|afternoon|evening|night|noon)\b",
        r"\b(deadline|due|schedule|appointment)\b",
        r"\b(\d+:\d+|\d+ (?:am|pm))\b",
        r"\b(next (?:week|month|year))\b",
    ]
    
    # Duration patterns
    DURATION_PATTERNS = [
        r"\b(\d+)\s+(?:hours|days|weeks|months|years)\b",
        r"\b(for \d+|in \d+)\b",
    ]
    
    def __init__(
        self,
        confidence_threshold: float = 0.5,
        enabled: bool = True,
    ):
        """Initialize the temporal classifier."""
        super().__init__(MemoryType.TEMPORAL_MEMORY, confidence_threshold, enabled)
    
    async def _compute_score(self, memory_input: MemoryInput) -> float:
        """
        Compute temporal score based on pattern matching.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Raw temporal score
        """
        text = memory_input.content.lower()
        
        # Pattern matching for temporal indicators
        temporal_matches = 0
        for pattern in self.TEMPORAL_PATTERNS:
            temporal_matches += self._count_pattern_matches(text, pattern)
        
        # Pattern matching for duration indicators
        duration_matches = 0
        for pattern in self.DURATION_PATTERNS:
            duration_matches += self._count_pattern_matches(text, pattern)
        
        # Combine scores
        temporal_score = self._normalize_score(temporal_matches, 0, 5)
        duration_score = self._normalize_score(duration_matches, 0, 2)
        
        final_score = (temporal_score * 0.8) + (duration_score * 0.2)
        
        return final_score
    
    def _generate_reasoning(self, score: float, memory_input: MemoryInput) -> str:
        """
        Generate reasoning for the temporal classification.
        
        Args:
            score: The normalized score
            memory_input: The memory input
            
        Returns:
            Reasoning string
        """
        text = memory_input.content.lower()
        
        if score >= 0.8:
            return f"High confidence temporal information (score: {score:.2f}), contains explicit temporal statements"
        elif score >= 0.5:
            return f"Moderate confidence temporal information (score: {score:.2f}), contains some temporal indicators"
        else:
            return f"Low confidence temporal information (score: {score:.2f}), minimal temporal indicators"
    
    def _extract_attributes(self, memory_input: MemoryInput) -> Dict[str, Any]:
        """
        Extract temporal attributes from the memory input.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Dictionary of extracted attributes
        """
        text = memory_input.content
        attributes = {}
        
        # Extract time reference
        time_match = re.search(r"\b(\d+:\d+|\d+ (?:am|pm)|morning|afternoon|evening|night)\b", text, re.IGNORECASE)
        if time_match:
            attributes["time_reference"] = time_match.group(0).strip()
        
        # Extract date reference
        date_match = re.search(r"\b(yesterday|today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", text, re.IGNORECASE)
        if date_match:
            attributes["date_reference"] = date_match.group(0).strip()
        
        # determine temporal type
        if self._match_pattern(text.lower(), r"\b(deadline|due)\b"):
            attributes["temporal_type"] = "deadline"
        elif self._match_pattern(text.lower(), r"\b(schedule|appointment)\b"):
            attributes["temporal_type"] = "scheduled"
        else:
            attributes["temporal_type"] = "reference"
        
        # Extract duration
        duration_match = re.search(r"(\d+)\s+(?:hours|days|weeks|months|years)", text, re.IGNORECASE)
        if duration_match:
            attributes["duration"] = duration_match.group(0).strip()
        
        return attributes
