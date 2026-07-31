"""
Relationship Memory classifier implementation.

This module implements the classifier for RelationshipMemory, which detects
social relationships, interpersonal connections, and group memberships.
"""

import re
from typing import Dict, Any, List

from memory_classification.core.types import MemoryType
from memory_classification.core.interfaces import MemoryInput
from memory_classification.classifiers.base import BaseClassifier


class RelationshipClassifier(BaseClassifier):
    """
    Classifier for Relationship Memory.
    
    Detects relationship-related information including:
    - Social relationships
    - Interpersonal connections
    - Group memberships
    - Relationship dynamics
    """
    
    # Relationship patterns
    RELATIONSHIP_PATTERNS = [
        r"\b(friend|family|colleague|coworker|partner|spouse)\b",
        r"\b(mother|father|sister|brother|parent|child|son|daughter)\b",
        r"\b(team|group|organization|company|department)\b",
        r"\b(relationship|connection|associate|acquaintance)\b",
        r"\b(my (?:friend|family|colleague))\b",
    ]
    
    # Entity patterns
    ENTITY_PATTERNS = [
        r"\b([A-Z][a-z]+)\s+(?:is|was|are|were)\b",
        r"\b(with|from|at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b",
    ]
    
    def __init__(
        self,
        confidence_threshold: float = 0.5,
        enabled: bool = True,
    ):
        """Initialize the relationship classifier."""
        super().__init__(MemoryType.RELATIONSHIP_MEMORY, confidence_threshold, enabled)
    
    async def _compute_score(self, memory_input: MemoryInput) -> float:
        """
        Compute relationship score based on pattern matching.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Raw relationship score
        """
        text = memory_input.content.lower()
        
        # Pattern matching for relationship indicators
        relationship_matches = 0
        for pattern in self.RELATIONSHIP_PATTERNS:
            relationship_matches += self._count_pattern_matches(text, pattern)
        
        # Pattern matching for entity mentions
        entity_matches = 0
        for pattern in self.ENTITY_PATTERNS:
            entity_matches += self._count_pattern_matches(text, pattern)
        
        # Combine scores
        relationship_score = self._normalize_score(relationship_matches, 0, 3)
        entity_score = self._normalize_score(entity_matches, 0, 2)
        
        final_score = (relationship_score * 0.7) + (entity_score * 0.3)
        
        return final_score
    
    def _generate_reasoning(self, score: float, memory_input: MemoryInput) -> str:
        """
        Generate reasoning for the relationship classification.
        
        Args:
            score: The normalized score
            memory_input: The memory input
            
        Returns:
            Reasoning string
        """
        text = memory_input.content.lower()
        
        if score >= 0.8:
            return f"High confidence relationship information (score: {score:.2f}), contains explicit relationship statements"
        elif score >= 0.5:
            return f"Moderate confidence relationship information (score: {score:.2f}), contains some relationship indicators"
        else:
            return f"Low confidence relationship information (score: {score:.2f}), minimal relationship indicators"
    
    def _extract_attributes(self, memory_input: MemoryInput) -> Dict[str, Any]:
        """
        Extract relationship attributes from the memory input.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Dictionary of extracted attributes
        """
        text = memory_input.content
        attributes = {}
        
        # Extract relationship type
        if self._match_pattern(text.lower(), r"\b(friend|friends)\b"):
            attributes["relationship_type"] = "friendship"
        elif self._match_pattern(text.lower(), r"\b(family|mother|father|sister|brother)\b"):
            attributes["relationship_type"] = "family"
        elif self._match_pattern(text.lower(), r"\b(colleague|coworker|team)\b"):
            attributes["relationship_type"] = "professional"
        elif self._match_pattern(text.lower(), r"\b(partner|spouse)\b"):
            attributes["relationship_type"] = "romantic"
        
        # Extract related entities
        entities = []
        entity_matches = re.findall(r"\b([A-Z][a-z]+)\b", text)
        if entity_matches:
            attributes["related_entities"] = list(set(entity_matches))
        
        return attributes
