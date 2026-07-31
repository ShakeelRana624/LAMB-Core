"""
Goal Memory classifier implementation.

This module implements the classifier for GoalMemory, which detects
goals, objectives, targets, and desired outcomes.
"""

import re
from typing import Dict, Any

from memory_classification.core.types import MemoryType
from memory_classification.core.interfaces import MemoryInput
from memory_classification.classifiers.base import BaseClassifier


class GoalClassifier(BaseClassifier):
    """
    Classifier for Goal Memory.
    
    Detects goal-related information including:
    - Goals and objectives
    - Targets and milestones
    - Desired outcomes
    - Achievement criteria
    """
    
    # Goal patterns
    GOAL_PATTERNS = [
        r"\b(goal|objective|target|aim|purpose|mission)\b",
        r"\b(want to|need to|plan to|intend to|going to)\b",
        r"\b(achieve|accomplish|reach|attain|complete)\b",
        r"\b(success|successful|succeed)\b",
        r"\b(by (?:the end of|next (?:week|month|year))|deadline|due date)\b",
        r"\b(milestone|checkpoint|deliverable)\b",
    ]
    
    # Priority patterns
    PRIORITY_PATTERNS = [
        r"\b(high priority|urgent|important|critical)\b",
        r"\b(low priority|optional|nice to have)\b",
        r"\b(medium priority|normal)\b",
    ]
    
    def __init__(
        self,
        confidence_threshold: float = 0.5,
        enabled: bool = True,
    ):
        """Initialize the goal classifier."""
        super().__init__(MemoryType.GOAL_MEMORY, confidence_threshold, enabled)
    
    async def _compute_score(self, memory_input: MemoryInput) -> float:
        """
        Compute goal score based on pattern matching.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Raw goal score
        """
        text = memory_input.content.lower()
        
        # Pattern matching for goal indicators
        goal_matches = 0
        for pattern in self.GOAL_PATTERNS:
            goal_matches += self._count_pattern_matches(text, pattern)
        
        # Pattern matching for priority indicators
        priority_matches = 0
        for pattern in self.PRIORITY_PATTERNS:
            priority_matches += self._count_pattern_matches(text, pattern)
        
        # Combine scores
        goal_score = self._normalize_score(goal_matches, 0, 4)
        priority_score = self._normalize_score(priority_matches, 0, 2)
        
        final_score = (goal_score * 0.8) + (priority_score * 0.2)
        
        return final_score
    
    def _generate_reasoning(self, score: float, memory_input: MemoryInput) -> str:
        """
        Generate reasoning for the goal classification.
        
        Args:
            score: The normalized score
            memory_input: The memory input
            
        Returns:
            Reasoning string
        """
        text = memory_input.content.lower()
        
        if score >= 0.8:
            return f"High confidence goal information (score: {score:.2f}), contains explicit goal statements"
        elif score >= 0.5:
            return f"Moderate confidence goal information (score: {score:.2f}), contains some goal indicators"
        else:
            return f"Low confidence goal information (score: {score:.2f}), minimal goal indicators"
    
    def _extract_attributes(self, memory_input: MemoryInput) -> Dict[str, Any]:
        """
        Extract goal attributes from the memory input.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Dictionary of extracted attributes
        """
        text = memory_input.content
        attributes = {}
        
        # Extract goal text
        goal_match = re.search(r"(?:goal|objective|target|aim)\s+(?:is|:)?\s*(.+?)(?:\.|$)", text, re.IGNORECASE)
        if goal_match:
            attributes["goal_text"] = goal_match.group(1).strip()
        
        # Extract priority
        if self._match_pattern(text.lower(), r"\b(high priority|urgent|critical)\b"):
            attributes["priority"] = "high"
        elif self._match_pattern(text.lower(), r"\b(low priority|optional)\b"):
            attributes["priority"] = "low"
        else:
            attributes["priority"] = "medium"
        
        # Extract deadline
        deadline_match = re.search(r"(?:by|deadline|due)\s+(.+?)(?:\.|$)", text, re.IGNORECASE)
        if deadline_match:
            attributes["deadline"] = deadline_match.group(1).strip()
        
        return attributes
