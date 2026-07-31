"""
Base classifier implementation.

This module provides the base class for all memory classifiers,
implementing common functionality and utility methods.
"""

import re
import time
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from memory_classification.core.types import MemoryType, ClassificationMethod
from memory_classification.core.interfaces import MemoryClassifier, MemoryInput, ClassificationResult


class BaseClassifier(MemoryClassifier, ABC):
    """
    Base class for rule-based memory classifiers.
    
    This class provides common functionality for all classifiers,
    including pattern matching, score normalization, and explanation generation.
    """
    
    def __init__(
        self,
        memory_type: MemoryType,
        confidence_threshold: float = 0.5,
        enabled: bool = True,
    ):
        """
        Initialize the base classifier.
        
        Args:
            memory_type: The memory type this classifier handles
            confidence_threshold: Minimum confidence threshold
            enabled: Whether this classifier is enabled
        """
        super().__init__(memory_type, confidence_threshold, enabled)
        self._pattern_cache = {}
    
    async def classify(self, memory_input: MemoryInput) -> ClassificationResult:
        """
        Classify a memory input.
        
        Args:
            memory_input: The memory input to classify
            
        Returns:
            Classification result
        """
        start_time = time.perf_counter()
        
        try:
            # Compute score
            score = await self._compute_score(memory_input)
            
            # Normalize score
            normalized_score = self._normalize_score(score)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(normalized_score, memory_input)
            
            # Extract attributes
            attributes = self._extract_attributes(memory_input)
            
            # Determine if classification passes threshold
            memory_types = [self.memory_type] if normalized_score >= self.confidence_threshold else []
            confidence_scores = {self.memory_type: normalized_score}
            reasoning_dict = {self.memory_type: reasoning}
            
            computation_time_ms = (time.perf_counter() - start_time) * 1000
            
            return ClassificationResult(
                memory_types=memory_types,
                confidence_scores=confidence_scores,
                reasoning=reasoning_dict,
                metadata=attributes,
                computation_time_ms=computation_time_ms,
                classifier_method=ClassificationMethod.RULE_BASED,
            )
            
        except Exception as e:
            raise Exception(f"Classification failed: {str(e)}")
    
    @abstractmethod
    async def _compute_score(self, memory_input: MemoryInput) -> float:
        """
        Compute the raw classification score.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Raw score (will be normalized)
        """
        pass
    
    @abstractmethod
    def _generate_reasoning(self, score: float, memory_input: MemoryInput) -> str:
        """
        Generate human-readable reasoning for the classification.
        
        Args:
            score: The normalized score
            memory_input: The memory input
            
        Returns:
            Reasoning string
        """
        pass
    
    def _extract_attributes(self, memory_input: MemoryInput) -> Dict[str, Any]:
        """
        Extract attributes from the memory input.
        
        Args:
            memory_input: The memory input
            
        Returns:
            Dictionary of extracted attributes
        """
        return {}
    
    def get_supported_types(self) -> List[MemoryType]:
        """Return the list of memory types this classifier handles."""
        return [self.memory_type]
    
    def _normalize_score(self, score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """
        Normalize a score to [0.0, 1.0].
        
        Args:
            score: Raw score
            min_val: Minimum expected value
            max_val: Maximum expected value
            
        Returns:
            Normalized score
        """
        if max_val == min_val:
            return 0.0
        normalized = (score - min_val) / (max_val - min_val)
        return max(0.0, min(1.0, normalized))
    
    def _clamp_score(self, score: float) -> float:
        """
        Clamp a score to [0.0, 1.0].
        
        Args:
            score: Score to clamp
            
        Returns:
            Clamped score
        """
        return max(0.0, min(1.0, score))
    
    def _match_pattern(self, text: str, pattern: str, flags: int = re.IGNORECASE) -> bool:
        """
        Check if a pattern matches in text.
        
        Args:
            text: Text to search
            pattern: Regex pattern
            flags: Regex flags
            
        Returns:
            True if pattern matches, False otherwise
        """
        compiled = self._compile_pattern(pattern, flags)
        return bool(compiled.search(text))
    
    def _count_pattern_matches(self, text: str, pattern: str, flags: int = re.IGNORECASE) -> int:
        """
        Count pattern matches in text.
        
        Args:
            text: Text to search
            pattern: Regex pattern
            flags: Regex flags
            
        Returns:
            Number of matches
        """
        compiled = self._compile_pattern(pattern, flags)
        return len(compiled.findall(text))
    
    def _compile_pattern(self, pattern: str, flags: int = re.IGNORECASE) -> re.Pattern:
        """
        Compile a regex pattern with caching.
        
        Args:
            pattern: Regex pattern
            flags: Regex flags
            
        Returns:
            Compiled pattern
        """
        cache_key = (pattern, flags)
        if cache_key not in self._pattern_cache:
            self._pattern_cache[cache_key] = re.compile(pattern, flags)
        return self._pattern_cache[cache_key]
    
    def _extract_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """
        Extract keywords present in text.
        
        Args:
            text: Text to search
            keywords: List of keywords to extract
            
        Returns:
            List of found keywords
        """
        text_lower = text.lower()
        found = []
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found.append(keyword)
        return found
    
    def _compute_word_overlap(self, text1: str, text2: str) -> float:
        """
        Compute word overlap between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Overlap score (0.0 to 1.0)
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
