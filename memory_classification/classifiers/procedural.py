"""
Procedural Memory classifier implementation.

This module implements the classifier for ProceduralMemory, which detects
procedural knowledge, how-to information, and step-by-step processes.
"""

import re
from typing import Dict, Any

from memory_classification.core.types import MemoryType
from memory_classification.core.interfaces import MemoryInput
from memory_classification.classifiers.base import BaseClassifier


class ProceduralClassifier(BaseClassifier):
    """
    Classifier for Procedural Memory.
    
    Detects procedural-related information including:
    - How-to procedures
    - Step-by-step processes
    - Methodologies and workflows
    - Instructions and guidelines
    """
    
    # Procedural patterns
    PROCEDURAL_PATTERNS = [
        r"\b(how to|how do i|how can i)\b",
        r"\b(step|steps|procedure|process)\b",
        r"\b(first|second|third|finally|lastly)\b",
        r"\b(instruction|guide|tutorial|manual)\b",
        r"\b(method|methodology|approach)\b",
        r"\b(workflow|pipeline|sequence)\b",
        r"\b(\d+\.|\d+\))\b",  # Numbered steps
    ]
    
    # Action patterns
    ACTION_PATTERNS = [
        r"\b(do|make|create|build|implement)\b",
        r"\b(use|apply|execute|perform)\b",
        r"\b(follow|adhere to|comply with)\b",
    ]
    
    def __init__(
        self,
        confidence_threshold: float = 0.5,
        enabled: bool = True,
    ):
        """Initialize the procedural classifier."""
        super().__init__(MemoryType.PROCEDURAL_MEMORY, confidence_threshold, enabled)
    
    async def _compute_score(self, memory_input: MemoryInput) -> float:
        """
        Compute procedural score based on pattern matching.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Raw procedural score
        """
        text = memory_input.content.lower()
        
        # Pattern matching for procedural indicators
        procedural_matches = 0
        for pattern in self.PROCEDURAL_PATTERNS:
            procedural_matches += self._count_pattern_matches(text, pattern)
        
        # Pattern matching for action indicators
        action_matches = 0
        for pattern in self.ACTION_PATTERNS:
            action_matches += self._count_pattern_matches(text, pattern)
        
        # Combine scores
        procedural_score = self._normalize_score(procedural_matches, 0, 5)
        action_score = self._normalize_score(action_matches, 0, 3)
        
        final_score = (procedural_score * 0.7) + (action_score * 0.3)
        
        return final_score
    
    def _generate_reasoning(self, score: float, memory_input: MemoryInput) -> str:
        """
        Generate reasoning for the procedural classification.
        
        Args:
            score: The normalized score
            memory_input: The memory input
            
        Returns:
            Reasoning string
        """
        text = memory_input.content.lower()
        
        if score >= 0.8:
            return f"High confidence procedural information (score: {score:.2f}), contains explicit procedural statements"
        elif score >= 0.5:
            return f"Moderate confidence procedural information (score: {score:.2f}), contains some procedural indicators"
        else:
            return f"Low confidence procedural information (score: {score:.2f}), minimal procedural indicators"
    
    def _extract_attributes(self, memory_input: MemoryInput) -> Dict[str, Any]:
        """
        Extract procedural attributes from the memory input.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Dictionary of extracted attributes
        """
        text = memory_input.content
        attributes = {}
        
        # Extract procedure name
        proc_match = re.search(r"(?:how to|procedure|process)\s+(.+?)(?:\.|$)", text, re.IGNORECASE)
        if proc_match:
            attributes["procedure_name"] = proc_match.group(1).strip()
        
        # Count steps
        step_count = len(re.findall(r"\b(step|first|second|third|finally|\d+\.|\d+\))\b", text, re.IGNORECASE))
        attributes["estimated_steps"] = step_count
        
        # Determine complexity
        if step_count >= 5:
            attributes["complexity"] = "high"
        elif step_count >= 3:
            attributes["complexity"] = "medium"
        else:
            attributes["complexity"] = "low"
        
        return attributes
