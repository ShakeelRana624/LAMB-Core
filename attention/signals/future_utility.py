"""
Future Utility Signal Implementation.

Predicts future usefulness of information using pattern matching
for planning language and future event references.
"""

import re
from typing import List

from attention.core.interfaces import AttentionContext, AttentionResult
from attention.core.types import SignalName
from attention.signals.base import BaseSignal


class FutureUtilitySignal(BaseSignal):
    """
    Future utility attention signal.
    
    Predicts future usefulness through:
    1. Pattern matching for planning language
    2. Future event reference detection
    3. Long-term relevance indicators
    
    High future utility indicates information that will be useful later.
    """
    
    # Planning patterns
    PLANNING_PATTERNS = [
        r"\b(plan|planning|schedule|agenda)\b",
        r"\b(will|going to|intend to)\b",
        r"\bnext (week|month|year|quarter)\b",
        r"\bin the (future|long term)\b",
        r"\b(goal|objective|target|milestone)\b",
    ]
    
    # Future reference patterns
    FUTURE_PATTERNS = [
        r"\b(remember|keep in mind|don't forget)\b",
        r"\b(for later|save|store)\b",
        r"\b(important|crucial|essential|key)\b",
        r"\b(reference|refer back to)\b",
    ]
    
    # Long-term relevance patterns
    LONGTERM_PATTERNS = [
        r"\b(permanent|ongoing|continuing)\b",
        r"\b(always|never|forever)\b",
        r"\b(foundation|basis|core)\b",
        r"\b(principle|rule|guideline)\b",
    ]
    
    def __init__(
        self,
        weight: float = 0.08,
        enabled: bool = True,
    ):
        """
        Initialize the future utility signal.
        
        Args:
            weight: Signal weight in aggregation (default: 0.08)
            enabled: Whether signal is enabled
        """
        super().__init__(weight, enabled)
    
    @property
    def signal_name(self) -> str:
        """Return the signal name."""
        return SignalName.FUTURE_UTILITY.value
    
    async def _compute_score(self, context: AttentionContext) -> float:
        """
        Compute future utility score.
        
        Future utility is computed by:
        1. Planning language detection
        2. Future reference detection
        3. Long-term relevance detection
        
        Args:
            context: The attention context
            
        Returns:
            Future utility score between 0.0 and 1.0
        """
        text = context.input_text.lower()
        
        # Planning language detection
        planning_score = self._compute_planning_score(text)
        
        # Future reference detection
        future_score = self._compute_future_score(text)
        
        # Long-term relevance detection
        longterm_score = self._compute_longterm_score(text)
        
        # Combine scores
        final_score = (
            (planning_score * 0.4) +
            (future_score * 0.4) +
            (longterm_score * 0.2)
        )
        
        return self._clamp_score(final_score)
    
    def _compute_planning_score(self, text: str) -> float:
        """Compute planning language score."""
        planning_matches = 0
        for pattern in self.PLANNING_PATTERNS:
            planning_matches += super()._count_pattern_matches(text, pattern)
        return self._normalize_score(planning_matches, 0, 3)
    
    def _compute_future_score(self, text: str) -> float:
        """Compute future reference score."""
        future_matches = 0
        for pattern in self.FUTURE_PATTERNS:
            future_matches += super()._count_pattern_matches(text, pattern)
        return self._normalize_score(future_matches, 0, 3)
    
    def _compute_longterm_score(self, text: str) -> float:
        """Compute long-term relevance score."""
        longterm_matches = 0
        for pattern in self.LONGTERM_PATTERNS:
            longterm_matches += super()._count_pattern_matches(text, pattern)
        return self._normalize_score(longterm_matches, 0, 2)
    
    def _generate_explanation(self, score: float, context: AttentionContext) -> str:
        """Generate explanation for the future utility score."""
        text = context.input_text.lower()
        
        if score >= 0.8:
            return f"Input has high future utility (score: {score:.2f}), contains planning or future reference indicators."
        elif score >= 0.5:
            return f"Input has moderate future utility (score: {score:.2f}), some future-oriented language."
        elif score >= 0.3:
            return f"Input has low future utility (score: {score:.2f}), minimal future relevance."
        else:
            return f"Input has no future utility (score: {score:.2f}), no planning or future indicators."
    
    def _build_metadata(self, score: float, context: AttentionContext) -> dict:
        """Build metadata with future utility-specific information."""
        metadata = super()._build_metadata(score, context)
        text = context.input_text.lower()
        
        metadata.update({
            "planning_matches": self._count_pattern_matches(text, self.PLANNING_PATTERNS),
            "future_matches": self._count_pattern_matches(text, self.FUTURE_PATTERNS),
            "longterm_matches": self._count_pattern_matches(text, self.LONGTERM_PATTERNS),
        })
        return metadata
