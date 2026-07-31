"""
Goal Relevance Signal Implementation.

Measures alignment of input with current agent goals.
Supports goal hierarchy (primary, secondary, tertiary goals).
"""

import re
from typing import Optional, List
from enum import Enum
import numpy as np

from attention.core.interfaces import AttentionContext, AttentionResult
from attention.core.types import SignalName
from attention.signals.base import BaseSignal


class GoalPriority(str, Enum):
    """Goal priority levels."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"


class GoalRelevanceSignal(BaseSignal):
    """
    Goal relevance attention signal.
    
    Computes how relevant the input is to the agent's current goals.
    Uses semantic similarity to goal statements and pattern matching
    for goal-related keywords.
    
    Supports goal hierarchy with different weights for different priority levels.
    """
    
    def __init__(
        self,
        weight: float = 0.12,
        enabled: bool = True,
        primary_goal_weight: float = 1.0,
        secondary_goal_weight: float = 0.7,
        tertiary_goal_weight: float = 0.4,
        embedding_model: Optional[str] = None,
    ):
        """
        Initialize the goal relevance signal.
        
        Args:
            weight: Signal weight in aggregation (default: 0.12)
            enabled: Whether signal is enabled
            primary_goal_weight: Weight for primary goals
            secondary_goal_weight: Weight for secondary goals
            tertiary_goal_weight: Weight for tertiary goals
            embedding_model: Name of embedding model to use
        """
        super().__init__(weight, enabled)
        self.primary_goal_weight = primary_goal_weight
        self.secondary_goal_weight = secondary_goal_weight
        self.tertiary_goal_weight = tertiary_goal_weight
        self.embedding_model = embedding_model or "all-MiniLM-L6-v2"
        self._encoder = None
    
    @property
    def signal_name(self) -> str:
        """Return the signal name."""
        return SignalName.GOAL_RELEVANCE.value
    
    def _get_encoder(self):
        """Lazy-load the embedding encoder."""
        if self._encoder is None:
            from sentence_transformers import SentenceTransformer
            self._encoder = SentenceTransformer(self.embedding_model)
        return self._encoder
    
    async def _compute_score(self, context: AttentionContext) -> float:
        """
        Compute goal relevance score.
        
        Computes relevance by:
        1. Semantic similarity to current goal
        2. Pattern matching for goal-related keywords
        3. Goal hierarchy weighting
        
        Args:
            context: The attention context
            
        Returns:
            Goal relevance score between 0.0 and 1.0
        """
        current_goal = context.current_goal
        if not current_goal:
            # No current goal → neutral relevance
            return 0.5
        
        # Get goal hierarchy from metadata
        goals = context.metadata.get("goals", {})
        primary_goals = goals.get("primary", [])
        secondary_goals = goals.get("secondary", [])
        tertiary_goals = goals.get("tertiary", [])
        
        # Compute semantic similarity
        encoder = self._get_encoder()
        input_embedding = encoder.encode(
            context.input_text,
            normalize_embeddings=True,
        )
        
        # Similarity to current goal
        goal_embedding = encoder.encode(current_goal, normalize_embeddings=True)
        similarity = float(np.dot(input_embedding, goal_embedding))
        
        # Weight by goal priority
        goal_priority = context.metadata.get("goal_priority", GoalPriority.PRIMARY)
        if goal_priority == GoalPriority.PRIMARY:
            weighted_similarity = similarity * self.primary_goal_weight
        elif goal_priority == GoalPriority.SECONDARY:
            weighted_similarity = similarity * self.secondary_goal_weight
        else:
            weighted_similarity = similarity * self.tertiary_goal_weight
        
        # Pattern matching for goal-related keywords
        goal_keywords = context.metadata.get("goal_keywords", [])
        pattern_score = self._compute_pattern_score(context.input_text, goal_keywords)
        
        # Combine semantic and pattern scores
        final_score = (weighted_similarity * 0.7) + (pattern_score * 0.3)
        
        return self._clamp_score(final_score)
    
    def _compute_pattern_score(self, text: str, keywords: List[str]) -> float:
        """
        Compute pattern matching score for goal keywords.
        
        Args:
            text: Input text
            keywords: Goal-related keywords
            
        Returns:
            Pattern score between 0.0 and 1.0
        """
        if not keywords:
            return 0.0
        
        text_lower = text.lower()
        matches = sum(1 for kw in keywords if kw.lower() in text_lower)
        return self._normalize_score(matches, 0, len(keywords))
    
    def _generate_explanation(self, score: float, context: AttentionContext) -> str:
        """Generate explanation for the goal relevance score."""
        current_goal = context.current_goal or "no current goal"
        
        if score >= 0.8:
            return f"Input is highly relevant to current goal '{current_goal}' (score: {score:.2f})."
        elif score >= 0.5:
            return f"Input is moderately relevant to current goal '{current_goal}' (score: {score:.2f})."
        elif score >= 0.3:
            return f"Input has low relevance to current goal '{current_goal}' (score: {score:.2f})."
        else:
            return f"Input is not relevant to current goal '{current_goal}' (score: {score:.2f})."
    
    def _build_metadata(self, score: float, context: AttentionContext) -> dict:
        """Build metadata with goal-specific information."""
        metadata = super()._build_metadata(score, context)
        metadata.update({
            "current_goal": context.current_goal,
            "goal_priority": context.metadata.get("goal_priority", GoalPriority.PRIMARY),
            "primary_goal_weight": self.primary_goal_weight,
            "secondary_goal_weight": self.secondary_goal_weight,
            "tertiary_goal_weight": self.tertiary_goal_weight,
        })
        return metadata
