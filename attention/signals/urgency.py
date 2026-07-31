"""
Urgency Signal Implementation.

Detects time-sensitive information using pattern matching
and temporal expression extraction.
"""

import re
from typing import List, Dict, Any
from datetime import datetime, timedelta

from attention.core.interfaces import AttentionContext, AttentionResult
from attention.core.types import SignalName
from attention.signals.base import BaseSignal


class UrgencySignal(BaseSignal):
    """
    Urgency attention signal.
    
    Detects time-sensitive information through:
    1. Pattern matching for urgency keywords
    2. Temporal expression extraction (dates, times, deadlines)
    3. Time proximity calculation
    
    High urgency indicates information that requires immediate attention.
    """
    
    # Urgency patterns
    HIGH_URGENCY_PATTERNS = [
        r"\b(urgent|asap|immediately|right now|emergency|critical|deadline)\b",
        r"\b(today|tonight|this morning|this afternoon)\b",
        r"\b(in \d+ (minutes|hours))\b",
        r"\b(by (today|tomorrow|tonight))\b",
    ]
    
    MEDIUM_URGENCY_PATTERNS = [
        r"\b(soon|shortly|quickly|promptly)\b",
        r"\b(this week|this month)\b",
        r"\b(within \d+ (days|weeks))\b",
    ]
    
    LOW_URGENCY_PATTERNS = [
        r"\b(eventually|later|someday|in the future)\b",
        r"\b(next (month|year|quarter))\b",
    ]
    
    def __init__(
        self,
        weight: float = 0.10,
        enabled: bool = True,
        enable_temporal_extraction: bool = True,
    ):
        """
        Initialize the urgency signal.
        
        Args:
            weight: Signal weight in aggregation (default: 0.10)
            enabled: Whether signal is enabled
            enable_temporal_extraction: Whether to extract temporal expressions
        """
        super().__init__(weight, enabled)
        self.enable_temporal_extraction = enable_temporal_extraction
    
    @property
    def signal_name(self) -> str:
        """Return the signal name."""
        return SignalName.URGENCY.value
    
    async def _compute_score(self, context: AttentionContext) -> float:
        """
        Compute urgency score.
        
        Urgency is computed by:
        1. Pattern matching for urgency keywords
        2. Temporal expression extraction
        3. Time proximity calculation
        
        Args:
            context: The attention context
            
        Returns:
            Urgency score between 0.0 and 1.0
        """
        text = context.input_text.lower()
        
        # Pattern matching
        high_urgency_count = self._count_pattern_matches(text, self.HIGH_URGENCY_PATTERNS)
        medium_urgency_count = self._count_pattern_matches(text, self.MEDIUM_URGENCY_PATTERNS)
        low_urgency_count = self._count_pattern_matches(text, self.LOW_URGENCY_PATTERNS)
        
        # Base score from patterns
        pattern_score = (
            (high_urgency_count * 1.0) +
            (medium_urgency_count * 0.6) +
            (low_urgency_count * 0.3)
        ) / max(1, high_urgency_count + medium_urgency_count + low_urgency_count)
        
        # Temporal extraction if enabled
        temporal_score = 0.0
        if self.enable_temporal_extraction:
            temporal_score = self._compute_temporal_urgency(text, context)
        
        # Combine scores
        final_score = (pattern_score * 0.7) + (temporal_score * 0.3)
        
        return self._clamp_score(final_score)
    
    def _count_pattern_matches(self, text: str, patterns: List[str]) -> int:
        """Count matches for a list of patterns."""
        count = 0
        for pattern in patterns:
            count += super()._count_pattern_matches(text, pattern)
        return count
    
    def _compute_temporal_urgency(self, text: str, context: AttentionContext) -> float:
        """
        Compute urgency based on temporal expressions.
        
        Args:
            text: Input text
            context: Attention context with temporal information
            
        Returns:
            Temporal urgency score
        """
        if not context.temporal_context:
            return 0.0
        
        current_time = context.temporal_context.current_time
        
        # Extract temporal expressions (simplified)
        # In production, use a proper temporal expression parser
        if "today" in text or "tonight" in text:
            return 1.0
        elif "tomorrow" in text:
            return 0.8
        elif "this week" in text:
            return 0.6
        elif "next week" in text:
            return 0.4
        elif "this month" in text:
            return 0.3
        elif "next month" in text:
            return 0.2
        
        return 0.0
    
    def _generate_explanation(self, score: float, context: AttentionContext) -> str:
        """Generate explanation for the urgency score."""
        text = context.input_text.lower()
        
        if score >= 0.8:
            return f"Input has high urgency (score: {score:.2f}), contains immediate action indicators."
        elif score >= 0.5:
            return f"Input has moderate urgency (score: {score:.2f}), contains time-sensitive information."
        elif score >= 0.3:
            return f"Input has low urgency (score: {score:.2f}), some temporal references present."
        else:
            return f"Input has no urgency (score: {score:.2f}), no time-sensitive indicators detected."
    
    def _build_metadata(self, score: float, context: AttentionContext) -> dict:
        """Build metadata with urgency-specific information."""
        metadata = super()._build_metadata(score, context)
        text = context.input_text.lower()
        
        metadata.update({
            "high_urgency_matches": self._count_pattern_matches(text, self.HIGH_URGENCY_PATTERNS),
            "medium_urgency_matches": self._count_pattern_matches(text, self.MEDIUM_URGENCY_PATTERNS),
            "low_urgency_matches": self._count_pattern_matches(text, self.LOW_URGENCY_PATTERNS),
            "enable_temporal_extraction": self.enable_temporal_extraction,
        })
        return metadata
