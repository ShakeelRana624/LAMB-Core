"""
Current Task Match Signal Implementation.

Measures alignment with active task using task similarity
and subtask hierarchy support.
"""

import re
from typing import List, Optional
import numpy as np

from attention.core.interfaces import AttentionContext, AttentionResult
from attention.core.types import SignalName
from attention.signals.base import BaseSignal


class CurrentTaskMatchSignal(BaseSignal):
    """
    Current task match attention signal.
    
    Measures alignment with active task through:
    1. Task similarity calculation
    2. Subtask hierarchy support
    3. Task-relevant keyword detection
    
    High task match indicates information relevant to current work.
    """
    
    # Task-related patterns
    TASK_PATTERNS = [
        r"\b(task|job|work|assignment)\b",
        r"\b(current|active|ongoing)\b",
        r"\b(progress|status|update)\b",
    ]
    
    def __init__(
        self,
        weight: float = 0.09,
        enabled: bool = True,
        embedding_model: Optional[str] = None,
    ):
        """
        Initialize the current task match signal.
        
        Args:
            weight: Signal weight in aggregation (default: 0.09)
            enabled: Whether signal is enabled
            embedding_model: Name of embedding model to use
        """
        super().__init__(weight, enabled)
        self.embedding_model = embedding_model or "all-MiniLM-L6-v2"
        self._encoder = None
    
    @property
    def signal_name(self) -> str:
        """Return the signal name."""
        return SignalName.CURRENT_TASK_MATCH.value
    
    def _get_encoder(self):
        """Lazy-load the embedding encoder."""
        if self._encoder is None:
            from sentence_transformers import SentenceTransformer
            self._encoder = SentenceTransformer(self.embedding_model)
        return self._encoder
    
    async def _compute_score(self, context: AttentionContext) -> float:
        """
        Compute current task match score.
        
        Task match is computed by:
        1. Task similarity calculation
        2. Subtask hierarchy support
        3. Task-relevant keyword detection
        
        Args:
            context: The attention context
            
        Returns:
            Task match score between 0.0 and 1.0
        """
        current_task = context.current_task
        if not current_task:
            # No current task → neutral match
            return 0.5
        
        # Semantic similarity to current task
        semantic_score = self._compute_semantic_similarity(context.input_text, current_task)
        
        # Subtask hierarchy weighting
        hierarchy_score = self._compute_hierarchy_score(context)
        
        # Task-relevant keyword detection
        keyword_score = self._compute_keyword_score(context)
        
        # Combine scores
        final_score = (
            (semantic_score * 0.5) +
            (hierarchy_score * 0.3) +
            (keyword_score * 0.2)
        )
        
        return self._clamp_score(final_score)
    
    def _compute_semantic_similarity(self, input_text: str, task: str) -> float:
        """
        Compute semantic similarity between input and task.
        
        Args:
            input_text: Input text
            task: Current task description
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        try:
            encoder = self._get_encoder()
            input_embedding = encoder.encode(input_text, normalize_embeddings=True)
            task_embedding = encoder.encode(task, normalize_embeddings=True)
            
            similarity = float(np.dot(input_embedding, task_embedding))
            return self._clamp_score(similarity)
        except Exception:
            return 0.5
    
    def _compute_hierarchy_score(self, context: AttentionContext) -> float:
        """
        Compute hierarchy score based on task hierarchy.
        
        Args:
            context: Attention context
            
        Returns:
            Hierarchy score
        """
        # Get task hierarchy from metadata
        task_hierarchy = context.metadata.get("task_hierarchy", {})
        current_task_level = context.metadata.get("task_level", "primary")
        
        # Primary tasks have higher weight
        if current_task_level == "primary":
            return 1.0
        elif current_task_level == "secondary":
            return 0.7
        elif current_task_level == "tertiary":
            return 0.4
        else:
            return 0.5
    
    def _compute_keyword_score(self, context: AttentionContext) -> float:
        """
        Compute task-relevant keyword score.
        
        Args:
            context: Attention context
            
        Returns:
            Keyword score
        """
        text = context.input_text.lower()
        
        # Get task keywords from metadata
        task_keywords = context.metadata.get("task_keywords", [])
        
        if not task_keywords:
            # Use pattern matching as fallback
            task_matches = 0
            for pattern in self.TASK_PATTERNS:
                task_matches += super()._count_pattern_matches(text, pattern)
            return self._normalize_score(task_matches, 0, 2)
        
        # Match against task keywords
        keyword_matches = sum(1 for kw in task_keywords if kw.lower() in text)
        return self._normalize_score(keyword_matches, 0, len(task_keywords))
    
    def _generate_explanation(self, score: float, context: AttentionContext) -> str:
        """Generate explanation for the task match score."""
        current_task = context.current_task or "no current task"
        
        if score >= 0.8:
            return f"Input highly matches current task '{current_task}' (score: {score:.2f})."
        elif score >= 0.5:
            return f"Input moderately matches current task '{current_task}' (score: {score:.2f})."
        elif score >= 0.3:
            return f"Input has low match with current task '{current_task}' (score: {score:.2f})."
        else:
            return f"Input does not match current task '{current_task}' (score: {score:.2f})."
    
    def _build_metadata(self, score: float, context: AttentionContext) -> dict:
        """Build metadata with task-specific information."""
        metadata = super()._build_metadata(score, context)
        text = context.input_text.lower()
        
        metadata.update({
            "current_task": context.current_task,
            "task_level": context.metadata.get("task_level", "primary"),
            "embedding_model": self.embedding_model,
            "task_keywords": context.metadata.get("task_keywords", []),
        })
        return metadata
