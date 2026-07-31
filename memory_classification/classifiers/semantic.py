"""
Semantic Memory classifier implementation.

This module implements the classifier for SemanticMemory, which detects
general knowledge, facts, concepts, and declarative information.
"""

import re
from typing import Dict, Any

from memory_classification.core.types import MemoryType
from memory_classification.core.interfaces import MemoryInput
from memory_classification.classifiers.base import BaseClassifier


class SemanticClassifier(BaseClassifier):
    """
    Classifier for Semantic Memory.
    
    Detects semantic-related information including:
    - General knowledge and facts
    - Concepts and definitions
    - Declarative information
    - Knowledge domains
    """
    
    # Semantic patterns
    SEMANTIC_PATTERNS = [
        r"\b(is|are|was|were|means|definition)\b",
        r"\b(fact|truth|knowledge|information)\b",
        r"\b(concept|idea|theory|principle)\b",
        r"\b(definition|meaning|explanation)\b",
        r"\b(basically|essentially|fundamentally)\b",
        r"\b(important to note|key point|main idea)\b",
    ]
    
    # Knowledge domain patterns
    DOMAIN_PATTERNS = [
        r"\b(science|math|history|geography|literature)\b",
        r"\b(technology|programming|engineering)\b",
        r"\b(business|economics|finance)\b",
        r"\b(art|music|culture)\b",
    ]
    
    def __init__(
        self,
        confidence_threshold: float = 0.5,
        enabled: bool = True,
    ):
        """Initialize the semantic classifier."""
        super().__init__(MemoryType.SEMANTIC_MEMORY, confidence_threshold, enabled)
    
    async def _compute_score(self, memory_input: MemoryInput) -> float:
        """
        Compute semantic score based on pattern matching.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Raw semantic score
        """
        text = memory_input.content.lower()
        
        # Pattern matching for semantic indicators
        semantic_matches = 0
        for pattern in self.SEMANTIC_PATTERNS:
            semantic_matches += self._count_pattern_matches(text, pattern)
        
        # Pattern matching for domain indicators
        domain_matches = 0
        for pattern in self.DOMAIN_PATTERNS:
            domain_matches += self._count_pattern_matches(text, pattern)
        
        # Combine scores
        semantic_score = self._normalize_score(semantic_matches, 0, 4)
        domain_score = self._normalize_score(domain_matches, 0, 2)
        
        final_score = (semantic_score * 0.8) + (domain_score * 0.2)
        
        return final_score
    
    def _generate_reasoning(self, score: float, memory_input: MemoryInput) -> str:
        """
        Generate reasoning for the semantic classification.
        
        Args:
            score: The normalized score
            memory_input: The memory input
            
        Returns:
            Reasoning string
        """
        text = memory_input.content.lower()
        
        if score >= 0.8:
            return f"High confidence semantic information (score: {score:.2f}), contains explicit semantic statements"
        elif score >= 0.5:
            return f"Moderate confidence semantic information (score: {score:.2f}), contains some semantic indicators"
        else:
            return f"Low confidence semantic information (score: {score:.2f}), minimal semantic indicators"
    
    def _extract_attributes(self, memory_input: MemoryInput) -> Dict[str, Any]:
        """
        Extract semantic attributes from the memory input.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Dictionary of extracted attributes
        """
        text = memory_input.content
        attributes = {}
        
        # Extract knowledge domain
        for domain in ["science", "math", "history", "technology", "business", "art"]:
            if self._match_pattern(text.lower(), rf"\b{domain}\b"):
                attributes["knowledge_domain"] = domain
                break
        
        # Extract fact type
        if self._match_pattern(text.lower(), r"\b(definition|means|is)\b"):
            attributes["fact_type"] = "definition"
        elif self._match_pattern(text.lower(), r"\b(concept|idea|theory)\b"):
            attributes["fact_type"] = "concept"
        else:
            attributes["fact_type"] = "general"
        
        return attributes
