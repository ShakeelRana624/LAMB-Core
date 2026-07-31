"""
Repetition Signal Implementation.

Detects recurring information using frequency analysis
and reinforcement pattern detection.
"""

import re
from typing import List, Dict
from collections import Counter

from attention.core.interfaces import AttentionContext, AttentionResult
from attention.core.types import SignalName
from attention.signals.base import BaseSignal


class RepetitionSignal(BaseSignal):
    """
    Repetition attention signal.
    
    Detects recurring information through:
    1. Frequency analysis across session
    2. Reinforcement pattern detection
    3. Topic recurrence analysis
    
    High repetition indicates information that appears frequently,
    suggesting importance or reinforcement.
    """
    
    # Reinforcement patterns
    REINFORCEMENT_PATTERNS = [
        r"\b(again|repeat|once more)\b",
        r"\b(still|yet|already)\b",
        r"\b(remind|remember|recall)\b",
    ]
    
    def __init__(
        self,
        weight: float = 0.06,
        enabled: bool = True,
        frequency_window: int = 20,
    ):
        """
        Initialize the repetition signal.
        
        Args:
            weight: Signal weight in aggregation (default: 0.06)
            enabled: Whether signal is enabled
            frequency_window: Number of recent inputs to analyze
        """
        super().__init__(weight, enabled)
        self.frequency_window = frequency_window
    
    @property
    def signal_name(self) -> str:
        """Return the signal name."""
        return SignalName.REPETITION.value
    
    async def _compute_score(self, context: AttentionContext) -> float:
        """
        Compute repetition score.
        
        Repetition is computed by:
        1. Frequency analysis across session
        2. Reinforcement pattern detection
        3. Topic recurrence analysis
        
        Args:
            context: The attention context
            
        Returns:
            Repetition score between 0.0 and 1.0
        """
        text = context.input_text.lower()
        
        # Frequency analysis
        frequency_score = self._compute_frequency_score(context)
        
        # Reinforcement pattern detection
        reinforcement_score = self._compute_reinforcement_score(text)
        
        # Topic recurrence
        topic_score = self._compute_topic_score(context)
        
        # Combine scores
        final_score = (
            (frequency_score * 0.5) +
            (reinforcement_score * 0.3) +
            (topic_score * 0.2)
        )
        
        return self._clamp_score(final_score)
    
    def _compute_frequency_score(self, context: AttentionContext) -> float:
        """
        Compute frequency score from recent inputs.
        
        Args:
            context: Attention context
            
        Returns:
            Frequency score
        """
        # Get recent inputs from metadata
        recent_inputs = context.metadata.get("recent_inputs", [])
        
        if not recent_inputs:
            return 0.0
        
        # Count occurrences of similar content
        current_text = context.input_text.lower()
        similar_count = 0
        
        for inp in recent_inputs[:self.frequency_window]:
            inp_text = inp.get("text", "").lower()
            # Simple similarity check (in production, use semantic similarity)
            if current_text in inp_text or inp_text in current_text:
                similar_count += 1
        
        # Normalize score
        return self._normalize_score(similar_count, 0, 5)
    
    def _compute_reinforcement_score(self, text: str) -> float:
        """Compute reinforcement pattern score."""
        reinforcement_matches = 0
        for pattern in self.REINFORCEMENT_PATTERNS:
            reinforcement_matches += super()._count_pattern_matches(text, pattern)
        return self._normalize_score(reinforcement_matches, 0, 2)
    
    def _compute_topic_score(self, context: AttentionContext) -> float:
        """
        Compute topic recurrence score.
        
        Args:
            context: Attention context
            
        Returns:
            Topic score
        """
        # Get topic history from metadata
        topic_history = context.metadata.get("topic_history", [])
        
        if not topic_history:
            return 0.0
        
        # Check if current topic appears in history
        current_topic = context.metadata.get("current_topic")
        if not current_topic:
            return 0.0
        
        topic_count = topic_history.count(current_topic)
        return self._normalize_score(topic_count, 0, 5)
    
    def _generate_explanation(self, score: float, context: AttentionContext) -> str:
        """Generate explanation for the repetition score."""
        text = context.input_text.lower()
        
        if score >= 0.8:
            return f"Input has high repetition (score: {score:.2f}), appears frequently in recent context."
        elif score >= 0.5:
            return f"Input has moderate repetition (score: {score:.2f}), some recurrence detected."
        elif score >= 0.3:
            return f"Input has low repetition (score: {score:.2f}), minimal recurrence."
        else:
            return f"Input has no repetition (score: {score:.2f}), first occurrence or unique."
    
    def _build_metadata(self, score: float, context: AttentionContext) -> dict:
        """Build metadata with repetition-specific information."""
        metadata = super()._build_metadata(score, context)
        text = context.input_text.lower()
        
        metadata.update({
            "reinforcement_matches": self._count_pattern_matches(text, self.REINFORCEMENT_PATTERNS),
            "frequency_window": self.frequency_window,
            "recent_inputs_count": len(context.metadata.get("recent_inputs", [])),
        })
        return metadata
