"""
Curiosity Signal Implementation.

Detects information gaps, questions, and learning opportunities
using pattern matching and uncertainty analysis.
"""

import re
from typing import List

from attention.core.interfaces import AttentionContext, AttentionResult
from attention.core.types import SignalName
from attention.signals.base import BaseSignal


class CuriositySignal(BaseSignal):
    """
    Curiosity attention signal.
    
    Detects learning opportunities through:
    1. Question detection
    2. Uncertainty indicators
    3. Information gap detection
    
    High curiosity indicates information that fills knowledge gaps.
    """
    
    # Question patterns
    QUESTION_PATTERNS = [
        r"\?",  # Question mark
        r"\b(what|why|how|when|where|who|which)\b",  # Wh-words
        r"\b(can|could|would|should|will)\b",  # Modal verbs for questions
    ]
    
    # Uncertainty patterns
    UNCERTAINTY_PATTERNS = [
        r"\b(wonder|curious|unsure|uncertain)\b",
        r"\b(don't know|not sure|confused|puzzled)\b",
        r"\b(interested in|want to learn|need to understand)\b",
    ]
    
    # Information gap patterns
    GAP_PATTERNS = [
        r"\b(learn|understand|figure out|find out)\b",
        r"\b(explain|clarify|elaborate)\b",
        r"\b(missing|need|lack)\b",
    ]
    
    def __init__(
        self,
        weight: float = 0.05,
        enabled: bool = True,
    ):
        """
        Initialize the curiosity signal.
        
        Args:
            weight: Signal weight in aggregation (default: 0.05)
            enabled: Whether signal is enabled
        """
        super().__init__(weight, enabled)
    
    @property
    def signal_name(self) -> str:
        """Return the signal name."""
        return SignalName.CURIOSITY.value
    
    async def _compute_score(self, context: AttentionContext) -> float:
        """
        Compute curiosity score.
        
        Curiosity is computed by:
        1. Question detection
        2. Uncertainty indicators
        3. Information gap detection
        
        Args:
            context: The attention context
            
        Returns:
            Curiosity score between 0.0 and 1.0
        """
        text = context.input_text.lower()
        
        # Question detection
        question_score = self._compute_question_score(text)
        
        # Uncertainty detection
        uncertainty_score = self._compute_uncertainty_score(text)
        
        # Information gap detection
        gap_score = self._compute_gap_score(text)
        
        # Combine scores
        final_score = (
            (question_score * 0.5) +
            (uncertainty_score * 0.3) +
            (gap_score * 0.2)
        )
        
        return self._clamp_score(final_score)
    
    def _compute_question_score(self, text: str) -> float:
        """Compute question detection score."""
        question_matches = 0
        for pattern in self.QUESTION_PATTERNS:
            question_matches += super()._count_pattern_matches(text, pattern)
        return self._normalize_score(question_matches, 0, 2)
    
    def _compute_uncertainty_score(self, text: str) -> float:
        """Compute uncertainty detection score."""
        uncertainty_matches = 0
        for pattern in self.UNCERTAINTY_PATTERNS:
            uncertainty_matches += super()._count_pattern_matches(text, pattern)
        return self._normalize_score(uncertainty_matches, 0, 2)
    
    def _compute_gap_score(self, text: str) -> float:
        """Compute information gap detection score."""
        gap_matches = 0
        for pattern in self.GAP_PATTERNS:
            gap_matches += super()._count_pattern_matches(text, pattern)
        return self._normalize_score(gap_matches, 0, 2)
    
    def _generate_explanation(self, score: float, context: AttentionContext) -> str:
        """Generate explanation for the curiosity score."""
        text = context.input_text.lower()
        
        if score >= 0.8:
            return f"Input indicates high curiosity (score: {score:.2f}), contains questions or information gaps."
        elif score >= 0.5:
            return f"Input indicates moderate curiosity (score: {score:.2f}), some uncertainty detected."
        elif score >= 0.3:
            return f"Input indicates low curiosity (score: {score:.2f}), minimal question indicators."
        else:
            return f"Input indicates no curiosity (score: {score:.2f}), no questions or gaps detected."
    
    def _build_metadata(self, score: float, context: AttentionContext) -> dict:
        """Build metadata with curiosity-specific information."""
        metadata = super()._build_metadata(score, context)
        text = context.input_text.lower()
        
        metadata.update({
            "question_matches": self._count_pattern_matches(text, self.QUESTION_PATTERNS),
            "uncertainty_matches": self._count_pattern_matches(text, self.UNCERTAINTY_PATTERNS),
            "gap_matches": self._count_pattern_matches(text, self.GAP_PATTERNS),
        })
        return metadata
