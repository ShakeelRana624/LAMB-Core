"""
Task Memory classifier implementation.

This module implements the classifier for TaskMemory, which detects
tasks, to-dos, action items, and task-related information.
"""

import re
from typing import Dict, Any

from memory_classification.core.types import MemoryType
from memory_classification.core.interfaces import MemoryInput
from memory_classification.classifiers.base import BaseClassifier


class TaskClassifier(BaseClassifier):
    """
    Classifier for Task Memory.
    
    Detects task-related information including:
    - Tasks and to-dos
    - Action items
    - Task status and progress
    - Task priorities and deadlines
    """
    
    # Task patterns
    TASK_PATTERNS = [
        r"\b(task|todo|to-do|action item)\b",
        r"\b(need to|have to|must)\b",
        r"\b(complete|finish|done)\b",
        r"\b(pending|in progress|started)\b",
        r"\b(priority|urgent|important)\b",
        r"\b(deadline|due date|due by)\b",
    ]
    
    # Status patterns
    STATUS_PATTERNS = [
        r"\b(pending|not started|todo)\b",
        r"\b(in progress|working on|started)\b",
        r"\b(completed|finished|done)\b",
        r"\b(blocked|stuck|on hold)\b",
    ]
    
    def __init__(
        self,
        confidence_threshold: float = 0.5,
        enabled: bool = True,
    ):
        """Initialize the task classifier."""
        super().__init__(MemoryType.TASK_MEMORY, confidence_threshold, enabled)
    
    async def _compute_score(self, memory_input: MemoryInput) -> float:
        """
        Compute task score based on pattern matching.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Raw task score
        """
        text = memory_input.content.lower()
        
        # Pattern matching for task indicators
        task_matches = 0
        for pattern in self.TASK_PATTERNS:
            task_matches += self._count_pattern_matches(text, pattern)
        
        # Pattern matching for status indicators
        status_matches = 0
        for pattern in self.STATUS_PATTERNS:
            status_matches += self._count_pattern_matches(text, pattern)
        
        # Combine scores
        task_score = self._normalize_score(task_matches, 0, 4)
        status_score = self._normalize_score(status_matches, 0, 2)
        
        final_score = (task_score * 0.8) + (status_score * 0.2)
        
        return final_score
    
    def _generate_reasoning(self, score: float, memory_input: MemoryInput) -> str:
        """
        Generate reasoning for the task classification.
        
        Args:
            score: The normalized score
            memory_input: The memory input
            
        Returns:
            Reasoning string
        """
        text = memory_input.content.lower()
        
        if score >= 0.8:
            return f"High confidence task information (score: {score:.2f}), contains explicit task statements"
        elif score >= 0.5:
            return f"Moderate confidence task information (score: {score:.2f}), contains some task indicators"
        else:
            return f"Low confidence task information (score: {score:.2f}), minimal task indicators"
    
    def _extract_attributes(self, memory_input: MemoryInput) -> Dict[str, Any]:
        """
        Extract task attributes from the memory input.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Dictionary of extracted attributes
        """
        text = memory_input.content
        attributes = {}
        
        # Extract task description
        task_match = re.search(r"(?:task|todo|need to)\s+(.+?)(?:\.|$)", text, re.IGNORECASE)
        if task_match:
            attributes["task_description"] = task_match.group(1).strip()
        
        # Extract status
        if self._match_pattern(text.lower(), r"\b(pending|not started|todo)\b"):
            attributes["task_status"] = "pending"
        elif self._match_pattern(text.lower(), r"\b(in progress|working on)\b"):
            attributes["task_status"] = "in_progress"
        elif self._match_pattern(text.lower(), r"\b(completed|finished|done)\b"):
            attributes["task_status"] = "completed"
        else:
            attributes["task_status"] = "unknown"
        
        # Extract priority
        if self._match_pattern(text.lower(), r"\b(urgent|critical|high priority)\b"):
            attributes["task_priority"] = "high"
        elif self._match_pattern(text.lower(), r"\b(low priority|optional)\b"):
            attributes["task_priority"] = "low"
        else:
            attributes["task_priority"] = "medium"
        
        # Extract due date
        due_match = re.search(r"(?:due|deadline)\s+(.+?)(?:\.|$)", text, re.IGNORECASE)
        if due_match:
            attributes["due_date"] = due_match.group(1).strip()
        
        return attributes
