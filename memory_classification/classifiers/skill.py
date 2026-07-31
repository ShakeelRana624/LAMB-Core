"""
Skill Memory classifier implementation.

This module implements the classifier for SkillMemory, which detects
skills, abilities, competencies, and learning progress.
"""

import re
from typing import Dict, Any

from memory_classification.core.types import MemoryType
from memory_classification.core.interfaces import MemoryInput
from memory_classification.classifiers.base import BaseClassifier


class SkillClassifier(BaseClassifier):
    """
    Classifier for Skill Memory.
    
    Detects skill-related information including:
    - Skills and abilities
    - Competencies and expertise
    - Learning progress
    - Skill levels
    """
    
    # Skill patterns
    SKILL_PATTERNS = [
        r"\b(skill|ability|competency|expertise|talent)\b",
        r"\b(can|able to|capable of)\b",
        r"\b(learn|learning|learned|studied)\b",
        r"\b(know|knowledge|experienced in)\b",
        r"\b(master|mastered|proficient)\b",
        r"\b(practice|practicing)\b",
    ]
    
    # Level patterns
    LEVEL_PATTERNS = [
        r"\b(beginner|novice|starter)\b",
        r"\b(intermediate|moderate)\b",
        r"\b(advanced|expert|master)\b",
        r"\b(proficient|skilled)\b",
    ]
    
    def __init__(
        self,
        confidence_threshold: float = 0.5,
        enabled: bool = True,
    ):
        """Initialize the skill classifier."""
        super().__init__(MemoryType.SKILL_MEMORY, confidence_threshold, enabled)
    
    async def _compute_score(self, memory_input: MemoryInput) -> float:
        """
        Compute skill score based on pattern matching.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Raw skill score
        """
        text = memory_input.content.lower()
        
        # Pattern matching for skill indicators
        skill_matches = 0
        for pattern in self.SKILL_PATTERNS:
            skill_matches += self._count_pattern_matches(text, pattern)
        
        # Pattern matching for level indicators
        level_matches = 0
        for pattern in self.LEVEL_PATTERNS:
            level_matches += self._count_pattern_matches(text, pattern)
        
        # Combine scores
        skill_score = self._normalize_score(skill_matches, 0, 4)
        level_score = self._normalize_score(level_matches, 0, 2)
        
        final_score = (skill_score * 0.8) + (level_score * 0.2)
        
        return final_score
    
    def _generate_reasoning(self, score: float, memory_input: MemoryInput) -> str:
        """
        Generate reasoning for the skill classification.
        
        Args:
            score: The normalized score
            memory_input: The memory input
            
        Returns:
            Reasoning string
        """
        text = memory_input.content.lower()
        
        if score >= 0.8:
            return f"High confidence skill information (score: {score:.2f}), contains explicit skill statements"
        elif score >= 0.5:
            return f"Moderate confidence skill information (score: {score:.2f}), contains some skill indicators"
        else:
            return f"Low confidence skill information (score: {score:.2f}), minimal skill indicators"
    
    def _extract_attributes(self, memory_input: MemoryInput) -> Dict[str, Any]:
        """
        Extract skill attributes from the memory input.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Dictionary of extracted attributes
        """
        text = memory_input.content
        attributes = {}
        
        # Extract skill name
        skill_match = re.search(r"(?:skill|ability)\s+(?:in|of)?\s*([a-zA-Z0-9\s]+?)(?:\.|$)", text, re.IGNORECASE)
        if skill_match:
            attributes["skill_name"] = skill_match.group(1).strip()
        
        # Extract skill level
        if self._match_pattern(text.lower(), r"\b(beginner|novice)\b"):
            attributes["skill_level"] = "beginner"
        elif self._match_pattern(text.lower(), r"\b(intermediate)\b"):
            attributes["skill_level"] = "intermediate"
        elif self._match_pattern(text.lower(), r"\b(advanced|expert|master)\b"):
            attributes["skill_level"] = "advanced"
        else:
            attributes["skill_level"] = "unknown"
        
        return attributes
