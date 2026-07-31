"""
Episodic Memory classifier implementation.

This module implements the classifier for EpisodicMemory, which detects
specific events, experiences, and time-bound occurrences.
"""

import re
from typing import Dict, Any

from memory_classification.core.types import MemoryType
from memory_classification.core.interfaces import MemoryInput
from memory_classification.classifiers.base import BaseClassifier


class EpisodicClassifier(BaseClassifier):
    """
    Classifier for Episodic Memory.
    
    Detects episodic-related information including:
    - Specific events and experiences
    - Time-bound occurrences
    - Contextual situations
    - Event participants and locations
    """
    
    # Episodic patterns
    EPISODIC_PATTERNS = [
        r"\b(yesterday|today|tomorrow|last (?:week|month|year))\b",
        r"\b(happened|occurred|took place|experienced)\b",
        r"\b(event|occasion|incident|situation)\b",
        r"\b(when|where|who|what)\b",
        r"\b(during|while|at the time)\b",
        r"\b(remember|recall|memory)\b",
    ]
    
    # Temporal patterns
    TEMPORAL_PATTERNS = [
        r"\b(on (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday))\b",
        r"\b(in (?:the morning|afternoon|evening|night))\b",
        r"\b(at \d+ (?:am|pm))\b",
        r"\b(on (?:january|february|march|april|may|june|july|august|september|october|november|december))\b",
    ]
    
    def __init__(
        self,
        confidence_threshold: float = 0.5,
        enabled: bool = True,
    ):
        """Initialize the episodic classifier."""
        super().__init__(MemoryType.EPISODIC_MEMORY, confidence_threshold, enabled)
    
    async def _compute_score(self, memory_input: MemoryInput) -> float:
        """
        Compute episodic score based on pattern matching.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Raw episodic score
        """
        text = memory_input.content.lower()
        
        # Pattern matching for episodic indicators
        episodic_matches = 0
        for pattern in self.EPISODIC_PATTERNS:
            episodic_matches += self._count_pattern_matches(text, pattern)
        
        # Pattern matching for temporal indicators
        temporal_matches = 0
        for pattern in self.TEMPORAL_PATTERNS:
            temporal_matches += self._count_pattern_matches(text, pattern)
        
        # Combine scores
        episodic_score = self._normalize_score(episodic_matches, 0, 4)
        temporal_score = self._normalize_score(temporal_matches, 0, 3)
        
        final_score = (episodic_score * 0.7) + (temporal_score * 0.3)
        
        return final_score
    
    def _generate_reasoning(self, score: float, memory_input: MemoryInput) -> str:
        """
        Generate reasoning for the episodic classification.
        
        Args:
            score: The normalized score
            memory_input: The memory input
            
        Returns:
            Reasoning string
        """
        text = memory_input.content.lower()
        
        if score >= 0.8:
            return f"High confidence episodic information (score: {score:.2f}), contains explicit episodic statements"
        elif score >= 0.5:
            return f"Moderate confidence episodic information (score: {score:.2f}), contains some episodic indicators"
        else:
            return f"Low confidence episodic information (score: {score:.2f}), minimal episodic indicators"
    
    def _extract_attributes(self, memory_input: MemoryInput) -> Dict[str, Any]:
        """
        Extract episodic attributes from the memory input.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Dictionary of extracted attributes
        """
        text = memory_input.content
        attributes = {}
        
        # Extract event time
        time_match = re.search(r"(?:yesterday|today|tomorrow|on \w+|at \d+ (?:am|pm))", text, re.IGNORECASE)
        if time_match:
            attributes["event_time"] = time_match.group(0).strip()
        
        # Extract location
        location_match = re.search(r"(?:at|in|on)\s+([A-Z][a-zA-Z0-9\s]+?)(?:\.|,|$)", text)
        if location_match:
            attributes["event_location"] = location_match.group(1).strip()
        
        # Extract participants (capitalized words)
        participants = re.findall(r"\b([A-Z][a-z]+)\b", text)
        if participants:
            attributes["participants"] = list(set(participants))
        
        return attributes
