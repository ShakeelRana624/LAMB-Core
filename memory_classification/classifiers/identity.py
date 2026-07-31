"""
Identity Memory classifier implementation.

This module implements the classifier for IdentityMemory, which detects
personal identity information such as name, age, location, and personal attributes.
"""

import re
from typing import Dict, Any

from memory_classification.core.types import MemoryType
from memory_classification.core.interfaces import MemoryInput
from memory_classification.classifiers.base import BaseClassifier


class IdentityClassifier(BaseClassifier):
    """
    Classifier for Identity Memory.
    
    Detects personal identity information including:
    - Personal names
    - Age and personal attributes
    - Location information
    - Self-referential statements
    """
    
    # Identity patterns
    IDENTITY_PATTERNS = [
        r"\b(my name is|i am|i'm|i am called|call me)\b",
        r"\b(i live in|i am from|i'm from|i reside in)\b",
        r"\b(i am \d+ years old|i'm \d+ years old|age \d+)\b",
        r"\b(my age is|my birthday is|born in)\b",
        r"\b(i am a|i'm a|i work as|i work at)\b",
        r"\b(my address is|i live at)\b",
        r"\b(my phone is|my email is|my number is)\b",
    ]
    
    # Personal attribute patterns
    ATTRIBUTE_PATTERNS = [
        r"\b(tall|short|thin|heavy|athletic)\b",
        r"\b(hair|eyes|skin)\b",
        r"\b(gender|sex|male|female|non-binary)\b",
    ]
    
    def __init__(
        self,
        confidence_threshold: float = 0.5,
        enabled: bool = True,
    ):
        """Initialize the identity classifier."""
        super().__init__(MemoryType.IDENTITY_MEMORY, confidence_threshold, enabled)
    
    async def _compute_score(self, memory_input: MemoryInput) -> float:
        """
        Compute identity score based on pattern matching.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Raw identity score
        """
        text = memory_input.content.lower()
        
        # Pattern matching for identity indicators
        identity_matches = 0
        for pattern in self.IDENTITY_PATTERNS:
            identity_matches += self._count_pattern_matches(text, pattern)
        
        # Pattern matching for personal attributes
        attribute_matches = 0
        for pattern in self.ATTRIBUTE_PATTERNS:
            attribute_matches += self._count_pattern_matches(text, pattern)
        
        # Combine scores
        identity_score = self._normalize_score(identity_matches, 0, 3)
        attribute_score = self._normalize_score(attribute_matches, 0, 2)
        
        final_score = (identity_score * 0.7) + (attribute_score * 0.3)
        
        return final_score
    
    def _generate_reasoning(self, score: float, memory_input: MemoryInput) -> str:
        """
        Generate reasoning for the identity classification.
        
        Args:
            score: The normalized score
            memory_input: The memory input
            
        Returns:
            Reasoning string
        """
        text = memory_input.content.lower()
        
        if score >= 0.8:
            return f"High confidence identity information (score: {score:.2f}), contains explicit identity statements"
        elif score >= 0.5:
            return f"Moderate confidence identity information (score: {score:.2f}), contains some identity indicators"
        else:
            return f"Low confidence identity information (score: {score:.2f}), minimal identity indicators"
    
    def _extract_attributes(self, memory_input: MemoryInput) -> Dict[str, Any]:
        """
        Extract identity attributes from the memory input.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Dictionary of extracted attributes
        """
        text = memory_input.content
        attributes = {}
        
        # Extract name patterns
        name_match = re.search(r"(?:my name is|i am|i'm)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text, re.IGNORECASE)
        if name_match:
            attributes["name"] = name_match.group(1)
        
        # Extract age patterns
        age_match = re.search(r"(?:age|i am|i'm)\s+(\d+)\s*(?:years old)?", text, re.IGNORECASE)
        if age_match:
            attributes["age"] = int(age_match.group(1))
        
        # Extract location patterns
        location_match = re.search(r"(?:i live in|i'm from|i am from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text, re.IGNORECASE)
        if location_match:
            attributes["location"] = location_match.group(1)
        
        return attributes
