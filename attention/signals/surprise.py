"""
Surprise Signal Implementation.

Detects unexpected information using Bayesian surprise calculation
and deviation from expected patterns.
"""

import re
from typing import List, Optional
import numpy as np

from attention.core.interfaces import AttentionContext, AttentionResult
from attention.core.types import SignalName
from attention.signals.base import BaseSignal


class SurpriseSignal(BaseSignal):
    """
    Surprise attention signal.
    
    Detects unexpected information through:
    1. Bayesian surprise calculation
    2. Deviation from expected patterns
    3. Unexpected event detection
    
    High surprise indicates information that deviates from expectations.
    """
    
    # Surprise patterns
    SURPRISE_PATTERNS = [
        r"\b(unexpected|surprising|shocking|sudden)\b",
        r"\b(wow|whoa|unbelievable|incredible)\b",
        r"\b(didn't expect|never thought|hard to believe)\b",
    ]
    
    def __init__(
        self,
        weight: float = 0.06,
        enabled: bool = True,
        enable_bayesian_surprise: bool = True,
        history_window: int = 10,
    ):
        """
        Initialize the surprise signal.
        
        Args:
            weight: Signal weight in aggregation (default: 0.06)
            enabled: Whether signal is enabled
            enable_bayesian_surprise: Whether to compute Bayesian surprise
            history_window: Number of recent inputs to consider
        """
        super().__init__(weight, enabled)
        self.enable_bayesian_surprise = enable_bayesian_surprise
        self.history_window = history_window
    
    @property
    def signal_name(self) -> str:
        """Return the signal name."""
        return SignalName.SURPRISE.value
    
    async def _compute_score(self, context: AttentionContext) -> float:
        """
        Compute surprise score.
        
        Surprise is computed by:
        1. Pattern matching for surprise indicators
        2. Bayesian surprise calculation
        3. Deviation from expected patterns
        
        Args:
            context: The attention context
            
        Returns:
            Surprise score between 0.0 and 1.0
        """
        text = context.input_text.lower()
        
        # Pattern matching
        pattern_score = self._compute_pattern_score(text)
        
        # Bayesian surprise if enabled
        bayesian_score = 0.0
        if self.enable_bayesian_surprise:
            bayesian_score = self._compute_bayesian_surprise(context)
        
        # Deviation from expected patterns
        deviation_score = self._compute_deviation_score(context)
        
        # Combine scores
        final_score = (
            (pattern_score * 0.4) +
            (bayesian_score * 0.4) +
            (deviation_score * 0.2)
        )
        
        return self._clamp_score(final_score)
    
    def _compute_pattern_score(self, text: str) -> float:
        """Compute pattern matching score."""
        surprise_matches = 0
        for pattern in self.SURPRISE_PATTERNS:
            surprise_matches += super()._count_pattern_matches(text, pattern)
        return self._normalize_score(surprise_matches, 0, 2)
    
    def _compute_bayesian_surprise(self, context: AttentionContext) -> float:
        """
        Compute Bayesian surprise.
        
        Bayesian surprise measures how much an observation
        changes the posterior distribution.
        
        Args:
            context: Attention context
            
        Returns:
            Bayesian surprise score
        """
        # Get recent inputs from metadata
        recent_inputs = context.metadata.get("recent_inputs", [])
        
        if not recent_inputs or len(recent_inputs) < 2:
            return 0.0
        
        # Simplified Bayesian surprise: KL divergence approximation
        # In production, use proper Bayesian surprise calculation
        try:
            # Get embeddings
            from sentence_transformers import SentenceTransformer
            encoder = SentenceTransformer("all-MiniLM-L6-v2")
            
            input_embedding = encoder.encode(context.input_text, normalize_embeddings=True)
            recent_embeddings = encoder.encode(
                [inp.get("text", "") for inp in recent_inputs[:self.history_window]],
                normalize_embeddings=True,
            )
            
            # Compute similarity distribution
            similarities = np.dot(input_embedding, np.array(recent_embeddings).T)
            mean_similarity = np.mean(similarities)
            
            # Surprise = 1 - mean similarity
            surprise = 1.0 - mean_similarity
            
            return self._clamp_score(surprise)
        except Exception:
            return 0.0
    
    def _compute_deviation_score(self, context: AttentionContext) -> float:
        """
        Compute deviation from expected patterns.
        
        Args:
            context: Attention context
            
        Returns:
            Deviation score
        """
        # Check for deviation markers in metadata
        is_unexpected = context.metadata.get("is_unexpected", False)
        deviation_level = context.metadata.get("deviation_level")
        
        if is_unexpected:
            if deviation_level == "high":
                return 1.0
            elif deviation_level == "medium":
                return 0.7
            elif deviation_level == "low":
                return 0.4
            else:
                return 0.5
        
        return 0.0
    
    def _generate_explanation(self, score: float, context: AttentionContext) -> str:
        """Generate explanation for the surprise score."""
        text = context.input_text.lower()
        
        if score >= 0.8:
            return f"Input is highly surprising (score: {score:.2f}), significantly deviates from expectations."
        elif score >= 0.5:
            return f"Input is moderately surprising (score: {score:.2f}), some unexpected elements."
        elif score >= 0.3:
            return f"Input has low surprise (score: {score:.2f}), minor deviation from expected."
        else:
            return f"Input is not surprising (score: {score:.2f}), aligns with expectations."
    
    def _build_metadata(self, score: float, context: AttentionContext) -> dict:
        """Build metadata with surprise-specific information."""
        metadata = super()._build_metadata(score, context)
        text = context.input_text.lower()
        
        metadata.update({
            "surprise_matches": self._count_pattern_matches(text, self.SURPRISE_PATTERNS),
            "enable_bayesian_surprise": self.enable_bayesian_surprise,
            "history_window": self.history_window,
            "is_unexpected": context.metadata.get("is_unexpected", False),
            "deviation_level": context.metadata.get("deviation_level"),
        })
        return metadata
