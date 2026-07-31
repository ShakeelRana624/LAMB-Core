"""
Confidence Signal Implementation.

Measures certainty level of information using hedge word detection
and certainty language analysis.
"""

import re
from typing import List

from attention.core.interfaces import AttentionContext, AttentionResult
from attention.core.types import SignalName
from attention.signals.base import BaseSignal


class ConfidenceSignal(BaseSignal):
    """
    Confidence attention signal.
    
    Measures certainty through:
    1. Hedge word detection
    2. Certainty language analysis
    3. Uncertainty indicator detection
    
    High confidence indicates certain, reliable information.
    Low confidence indicates uncertain information that may need verification.
    """
    
    # Hedge words (indicate low confidence)
    HEDGE_PATTERNS = [
        r"\b(maybe|perhaps|possibly|probably|likely)\b",
        r"\b(might|could|would|should)\b",
        r"\b(seems|appears|looks like)\b",
        r"\b(roughly|approximately|about|around)\b",
        r"\b(kind of|sort of|a bit)\b",
        r"\b(I think|I believe|I guess)\b",
    ]
    
    # Certainty words (indicate high confidence)
    CERTAINTY_PATTERNS = [
        r"\b(definitely|certainly|surely|absolutely)\b",
        r"\b(exactly|precisely|clearly)\b",
        r"\b(without doubt|no doubt)\b",
        r"\b(I know|I'm sure|I'm certain)\b",
        r"\b(undoubtedly|unquestionably)\b",
    ]
    
    # Uncertainty words
    UNCERTAINTY_PATTERNS = [
        r"\b(unsure|uncertain|unclear)\b",
        r"\b(don't know|not sure)\b",
        r"\b(confused|puzzled)\b",
        r"\b(hard to say|difficult to tell)\b",
    ]
    
    def __init__(
        self,
        weight: float = 0.04,
        enabled: bool = True,
    ):
        """
        Initialize the confidence signal.
        
        Args:
            weight: Signal weight in aggregation (default: 0.04)
            enabled: Whether signal is enabled
        """
        super().__init__(weight, enabled)
    
    @property
    def signal_name(self) -> str:
        """Return the signal name."""
        return SignalName.CONFIDENCE.value
    
    async def _compute_score(self, context: AttentionContext) -> float:
        """
        Compute confidence score.
        
        Confidence is computed by:
        1. Hedge word detection (lowers score)
        2. Certainty word detection (raises score)
        3. Uncertainty word detection (lowers score)
        
        Args:
            context: The attention context
            
        Returns:
            Confidence score between 0.0 (low confidence) and 1.0 (high confidence)
        """
        text = context.input_text.lower()
        
        # Hedge word detection (lowers confidence)
        hedge_score = self._compute_hedge_score(text)
        
        # Certainty word detection (raises confidence)
        certainty_score = self._compute_certainty_score(text)
        
        # Uncertainty word detection (lowers confidence)
        uncertainty_score = self._compute_uncertainty_score(text)
        
        # Base confidence (neutral)
        base_confidence = 0.5
        
        # Adjust based on detected patterns
        final_score = base_confidence
        final_score += (certainty_score * 0.5)  # Certainty raises score
        final_score -= (hedge_score * 0.3)  # Hedges lower score
        final_score -= (uncertainty_score * 0.2)  # Uncertainty lowers score
        
        return self._clamp_score(final_score)
    
    def _compute_hedge_score(self, text: str) -> float:
        """Compute hedge word score."""
        hedge_matches = 0
        for pattern in self.HEDGE_PATTERNS:
            hedge_matches += super()._count_pattern_matches(text, pattern)
        return self._normalize_score(hedge_matches, 0, 3)
    
    def _compute_certainty_score(self, text: str) -> float:
        """Compute certainty word score."""
        certainty_matches = 0
        for pattern in self.CERTAINTY_PATTERNS:
            certainty_matches += super()._count_pattern_matches(text, pattern)
        return self._normalize_score(certainty_matches, 0, 2)
    
    def _compute_uncertainty_score(self, text: str) -> float:
        """Compute uncertainty word score."""
        uncertainty_matches = 0
        for pattern in self.UNCERTAINTY_PATTERNS:
            uncertainty_matches += super()._count_pattern_matches(text, pattern)
        return self._normalize_score(uncertainty_matches, 0, 2)
    
    def _generate_explanation(self, score: float, context: AttentionContext) -> str:
        """Generate explanation for the confidence score."""
        text = context.input_text.lower()
        
        if score >= 0.8:
            return f"Input has high confidence (score: {score:.2f}), contains certainty indicators."
        elif score >= 0.5:
            return f"Input has moderate confidence (score: {score:.2f}), some certainty language."
        elif score >= 0.3:
            return f"Input has low confidence (score: {score:.2f}), contains hedge words or uncertainty."
        else:
            return f"Input has very low confidence (score: {score:.2f}), highly uncertain language."
    
    def _build_metadata(self, score: float, context: AttentionContext) -> dict:
        """Build metadata with confidence-specific information."""
        metadata = super()._build_metadata(score, context)
        text = context.input_text.lower()
        
        metadata.update({
            "hedge_matches": self._count_pattern_matches(text, self.HEDGE_PATTERNS),
            "certainty_matches": self._count_pattern_matches(text, self.CERTAINTY_PATTERNS),
            "uncertainty_matches": self._count_pattern_matches(text, self.UNCERTAINTY_PATTERNS),
        })
        return metadata
