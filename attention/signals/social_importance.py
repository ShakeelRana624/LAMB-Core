"""
Social Importance Signal Implementation.

Detects socially relevant information using entity recognition
and social relationship indicators.
"""

import re
from typing import List, Optional

from attention.core.interfaces import AttentionContext, AttentionResult
from attention.core.types import SignalName
from attention.signals.base import BaseSignal


class SocialImportanceSignal(BaseSignal):
    """
    Social importance attention signal.
    
    Detects social relevance through:
    1. Entity recognition (people, organizations)
    2. Social relationship indicators
    3. Group context analysis
    
    High social importance indicates information relevant to social relationships.
    """
    
    # Entity patterns (people, organizations)
    ENTITY_PATTERNS = [
        r"\b(Mr|Mrs|Ms|Dr|Prof)\.?\s+[A-Z][a-z]+",
        r"\b([A-Z][a-z]+)\s+(said|told|asked|mentioned)\b",
        r"\b(team|group|organization|company|department)\b",
    ]
    
    # Social relationship patterns
    RELATIONSHIP_PATTERNS = [
        r"\b(friend|family|colleague|partner|boss)\b",
        r"\b(meeting|call|conversation|discussion)\b",
        r"\b(together|with|collaborate|coordinate)\b",
    ]
    
    # Group context patterns
    GROUP_PATTERNS = [
        r"\b(we|us|our|everyone|all of us)\b",
        r"\b(team|group|collective|joint)\b",
    ]
    
    def __init__(
        self,
        weight: float = 0.05,
        enabled: bool = True,
        enable_entity_recognition: bool = True,
    ):
        """
        Initialize the social importance signal.
        
        Args:
            weight: Signal weight in aggregation (default: 0.05)
            enabled: Whether signal is enabled
            enable_entity_recognition: Whether to perform entity recognition
        """
        super().__init__(weight, enabled)
        self.enable_entity_recognition = enable_entity_recognition
    
    @property
    def signal_name(self) -> str:
        """Return the signal name."""
        return SignalName.SOCIAL_IMPORTANCE.value
    
    async def _compute_score(self, context: AttentionContext) -> float:
        """
        Compute social importance score.
        
        Social importance is computed by:
        1. Entity recognition
        2. Social relationship detection
        3. Group context analysis
        
        Args:
            context: The attention context
            
        Returns:
            Social importance score between 0.0 and 1.0
        """
        text = context.input_text.lower()
        
        # Entity recognition
        entity_score = self._compute_entity_score(text)
        
        # Social relationship detection
        relationship_score = self._compute_relationship_score(text)
        
        # Group context analysis
        group_score = self._compute_group_score(text)
        
        # Social context from context object
        context_score = self._compute_context_score(context)
        
        # Combine scores
        final_score = (
            (entity_score * 0.3) +
            (relationship_score * 0.3) +
            (group_score * 0.2) +
            (context_score * 0.2)
        )
        
        return self._clamp_score(final_score)
    
    def _compute_entity_score(self, text: str) -> float:
        """Compute entity recognition score."""
        entity_matches = 0
        for pattern in self.ENTITY_PATTERNS:
            entity_matches += super()._count_pattern_matches(text, pattern)
        return self._normalize_score(entity_matches, 0, 2)
    
    def _compute_relationship_score(self, text: str) -> float:
        """Compute social relationship score."""
        relationship_matches = 0
        for pattern in self.RELATIONSHIP_PATTERNS:
            relationship_matches += super()._count_pattern_matches(text, pattern)
        return self._normalize_score(relationship_matches, 0, 2)
    
    def _compute_group_score(self, text: str) -> float:
        """Compute group context score."""
        group_matches = 0
        for pattern in self.GROUP_PATTERNS:
            group_matches += super()._count_pattern_matches(text, pattern)
        return self._normalize_score(group_matches, 0, 2)
    
    def _compute_context_score(self, context: AttentionContext) -> float:
        """Compute social context score from context object."""
        if not context.social_context:
            return 0.0
        
        # Consider group size
        if context.social_context.group_size:
            if context.social_context.group_size > 5:
                return 0.8
            elif context.social_context.group_size > 2:
                return 0.6
            else:
                return 0.4
        
        # Consider social importance from context
        if context.social_context.social_importance:
            return context.social_context.social_importance
        
        return 0.0
    
    def _generate_explanation(self, score: float, context: AttentionContext) -> str:
        """Generate explanation for the social importance score."""
        text = context.input_text.lower()
        
        if score >= 0.8:
            return f"Input has high social importance (score: {score:.2f}), contains entities or social references."
        elif score >= 0.5:
            return f"Input has moderate social importance (score: {score:.2f}), some social elements."
        elif score >= 0.3:
            return f"Input has low social importance (score: {score:.2f}), minimal social context."
        else:
            return f"Input has no social importance (score: {score:.2f}), no social indicators."
    
    def _build_metadata(self, score: float, context: AttentionContext) -> dict:
        """Build metadata with social importance-specific information."""
        metadata = super()._build_metadata(score, context)
        text = context.input_text.lower()
        
        metadata.update({
            "entity_matches": self._count_pattern_matches(text, self.ENTITY_PATTERNS),
            "relationship_matches": self._count_pattern_matches(text, self.RELATIONSHIP_PATTERNS),
            "group_matches": self._count_pattern_matches(text, self.GROUP_PATTERNS),
            "enable_entity_recognition": self.enable_entity_recognition,
            "group_size": context.social_context.group_size if context.social_context else None,
            "social_importance": context.social_context.social_importance if context.social_context else None,
        })
        return metadata
