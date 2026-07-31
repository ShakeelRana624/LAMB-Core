"""
Base signal implementation with common functionality.

This module provides a concrete base class that implements
common functionality for all attention signals, reducing
code duplication and ensuring consistency.
"""

import re
from typing import Dict, Any, Optional
from abc import abstractmethod

from attention.core.interfaces import AttentionSignal, AttentionContext, AttentionResult


class BaseSignal(AttentionSignal):
    """
    Base implementation for attention signals.
    
    Provides common functionality including:
    - Pattern matching utilities
    - Score normalization
    - Explanation generation
    - Metadata handling
    
    Concrete signals should inherit from this class and
    implement the _compute_score method.
    """
    
    def __init__(self, weight: float = 1.0, enabled: bool = True):
        """Initialize the base signal."""
        super().__init__(weight, enabled)
        self._pattern_cache: Dict[str, re.Pattern] = {}
    
    @abstractmethod
    async def _compute_score(self, context: AttentionContext) -> float:
        """
        Compute the raw score for this signal.
        
        This method should be implemented by concrete signals.
        It should return a score between 0.0 and 1.0.
        
        Args:
            context: The attention context
            
        Returns:
            Raw score between 0.0 and 1.0
        """
        pass
    
    @abstractmethod
    def _generate_explanation(self, score: float, context: AttentionContext) -> str:
        """
        Generate a human-readable explanation for the score.
        
        Args:
            score: The computed score
            context: The attention context
            
        Returns:
            Human-readable explanation
        """
        pass
    
    async def compute(self, context: AttentionContext) -> AttentionResult:
        """
        Compute the attention signal score.
        
        This method orchestrates the computation by:
        1. Calling _compute_score for the raw score
        2. Generating an explanation
        3. Building metadata
        4. Returning the complete result
        
        Args:
            context: The attention context
            
        Returns:
            Complete AttentionResult
        """
        score = await self._compute_score(context)
        explanation = self._generate_explanation(score, context)
        metadata = self._build_metadata(score, context)
        
        return AttentionResult(
            score=score,
            explanation=explanation,
            signal_name=self.signal_name,
            metadata=metadata,
        )
    
    def _build_metadata(self, score: float, context: AttentionContext) -> Dict[str, Any]:
        """
        Build metadata for the attention result.
        
        Args:
            score: The computed score
            context: The attention context
            
        Returns:
            Metadata dictionary
        """
        return {
            "signal_name": self.signal_name,
            "weight": self._weight,
            "input_length": len(context.input_text),
            "session_id": context.session_id,
            "agent_id": context.agent_id,
        }
    
    def _compile_pattern(self, pattern: str, flags: int = re.IGNORECASE) -> re.Pattern:
        """
        Compile a regex pattern with caching.
        
        Args:
            pattern: The regex pattern string
            flags: Regex flags
            
        Returns:
            Compiled regex pattern
        """
        if pattern not in self._pattern_cache:
            self._pattern_cache[pattern] = re.compile(pattern, flags)
        return self._pattern_cache[pattern]
    
    def _match_pattern(self, text: str, pattern: str, flags: int = re.IGNORECASE) -> bool:
        """
        Check if text matches a pattern.
        
        Args:
            text: Text to check
            pattern: Regex pattern
            flags: Regex flags
            
        Returns:
            True if pattern matches
        """
        compiled = self._compile_pattern(pattern, flags)
        return bool(compiled.search(text))
    
    def _count_pattern_matches(self, text: str, pattern: str, flags: int = re.IGNORECASE) -> int:
        """
        Count pattern matches in text.
        
        Args:
            text: Text to search
            pattern: Regex pattern (string or list of patterns)
            flags: Regex flags
            
        Returns:
            Number of matches
        """
        if isinstance(pattern, list):
            # Handle list of patterns
            total_matches = 0
            for p in pattern:
                compiled = self._compile_pattern(p, flags)
                total_matches += len(compiled.findall(text))
            return total_matches
        else:
            # Handle single pattern
            compiled = self._compile_pattern(pattern, flags)
            return len(compiled.findall(text))
    
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
        Clamp score to [0.0, 1.0].
        
        Args:
            score: Score to clamp
            
        Returns:
            Clamped score
        """
        return max(0.0, min(1.0, score))
