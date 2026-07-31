"""
Project Memory classifier implementation.

This module implements the classifier for ProjectMemory, which detects
project information, work assignments, and collaborative efforts.
"""

import re
from typing import Dict, Any

from memory_classification.core.types import MemoryType
from memory_classification.core.interfaces import MemoryInput
from memory_classification.classifiers.base import BaseClassifier


class ProjectClassifier(BaseClassifier):
    """
    Classifier for Project Memory.
    
    Detects project-related information including:
    - Project names and descriptions
    - Project status and progress
    - Team members and collaborators
    - Project deadlines and milestones
    """
    
    # Project patterns
    PROJECT_PATTERNS = [
        r"\b(project|initiative|program|campaign)\b",
        r"\b(working on|collaborating on|part of)\b",
        r"\b(team|squad|group|department)\b",
        r"\b(milestone|deliverable|deadline|timeline)\b",
        r"\b(status|progress|phase|stage)\b",
        r"\b(complete|completed|finished|done)\b",
    ]
    
    # Status patterns
    STATUS_PATTERNS = [
        r"\b(in progress|ongoing|active|started)\b",
        r"\b(completed|finished|done|closed)\b",
        r"\b(on hold|paused|delayed)\b",
        r"\b(planned|scheduled|upcoming)\b",
    ]
    
    def __init__(
        self,
        confidence_threshold: float = 0.5,
        enabled: bool = True,
    ):
        """Initialize the project classifier."""
        super().__init__(MemoryType.PROJECT_MEMORY, confidence_threshold, enabled)
    
    async def _compute_score(self, memory_input: MemoryInput) -> float:
        """
        Compute project score based on pattern matching.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Raw project score
        """
        text = memory_input.content.lower()
        
        # Pattern matching for project indicators
        project_matches = 0
        for pattern in self.PROJECT_PATTERNS:
            project_matches += self._count_pattern_matches(text, pattern)
        
        # Pattern matching for status indicators
        status_matches = 0
        for pattern in self.STATUS_PATTERNS:
            status_matches += self._count_pattern_matches(text, pattern)
        
        # Combine scores
        project_score = self._normalize_score(project_matches, 0, 4)
        status_score = self._normalize_score(status_matches, 0, 2)
        
        final_score = (project_score * 0.8) + (status_score * 0.2)
        
        return final_score
    
    def _generate_reasoning(self, score: float, memory_input: MemoryInput) -> str:
        """
        Generate reasoning for the project classification.
        
        Args:
            score: The normalized score
            memory_input: The memory input
            
        Returns:
            Reasoning string
        """
        text = memory_input.content.lower()
        
        if score >= 0.8:
            return f"High confidence project information (score: {score:.2f}), contains explicit project statements"
        elif score >= 0.5:
            return f"Moderate confidence project information (score: {score:.2f}), contains some project indicators"
        else:
            return f"Low confidence project information (score: {score:.2f}), minimal project indicators"
    
    def _extract_attributes(self, memory_input: MemoryInput) -> Dict[str, Any]:
        """
        Extract project attributes from the memory input.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Dictionary of extracted attributes
        """
        text = memory_input.content
        attributes = {}
        
        # Extract project name
        project_match = re.search(r"(?:project|initiative)\s+(?:named|called)?\s*([A-Z][a-zA-Z0-9\s]+?)(?:\.|$)", text, re.IGNORECASE)
        if project_match:
            attributes["project_name"] = project_match.group(1).strip()
        
        # Extract status
        if self._match_pattern(text.lower(), r"\b(in progress|ongoing|active)\b"):
            attributes["project_status"] = "in_progress"
        elif self._match_pattern(text.lower(), r"\b(completed|finished|done)\b"):
            attributes["project_status"] = "completed"
        elif self._match_pattern(text.lower(), r"\b(on hold|paused)\b"):
            attributes["project_status"] = "on_hold"
        else:
            attributes["project_status"] = "unknown"
        
        # Extract deadline
        deadline_match = re.search(r"(?:deadline|due)\s+(.+?)(?:\.|$)", text, re.IGNORECASE)
        if deadline_match:
            attributes["project_deadline"] = deadline_match.group(1).strip()
        
        return attributes
