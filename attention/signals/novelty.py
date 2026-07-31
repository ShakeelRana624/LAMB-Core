"""
Novelty Signal Implementation.

Measures how different the input is from recent memories using
semantic similarity. Higher novelty indicates more unique information
that deserves attention.
"""

import numpy as np
from typing import Optional, List

from attention.core.interfaces import AttentionContext, AttentionResult
from attention.core.types import SignalName
from attention.signals.base import BaseSignal


class NoveltySignal(BaseSignal):
    """
    Novelty attention signal.
    
    Computes novelty by measuring semantic distance from recent memories.
    Uses cosine similarity between input embedding and recent memory embeddings.
    
    Novelty = 1 - max_similarity (higher = more novel)
    """
    
    def __init__(
        self,
        weight: float = 0.15,
        enabled: bool = True,
        recent_memory_count: int = 10,
        embedding_model: Optional[str] = None,
    ):
        """
        Initialize the novelty signal.
        
        Args:
            weight: Signal weight in aggregation (default: 0.15)
            enabled: Whether signal is enabled
            recent_memory_count: Number of recent memories to compare against
            embedding_model: Name of embedding model to use
        """
        super().__init__(weight, enabled)
        self.recent_memory_count = recent_memory_count
        self.embedding_model = embedding_model or "all-MiniLM-L6-v2"
        self._encoder = None
    
    @property
    def signal_name(self) -> str:
        """Return the signal name."""
        return SignalName.NOVELTY.value
    
    def _get_encoder(self):
        """Lazy-load the embedding encoder."""
        if self._encoder is None:
            from sentence_transformers import SentenceTransformer
            self._encoder = SentenceTransformer(self.embedding_model)
        return self._encoder
    
    async def _compute_score(self, context: AttentionContext) -> float:
        """
        Compute novelty score.
        
        Novelty is computed as 1 - max_similarity to recent memories.
        If no recent memories exist, novelty is maximum (1.0).
        
        Args:
            context: The attention context
            
        Returns:
            Novelty score between 0.0 and 1.0
        """
        # Get recent memories from metadata or context
        recent_memories = context.metadata.get("recent_memories", [])
        
        if not recent_memories:
            # No recent memories → maximum novelty
            return 1.0
        
        # Encode input
        encoder = self._get_encoder()
        input_embedding = encoder.encode(
            context.input_text,
            normalize_embeddings=True,
        )
        
        # Encode recent memories
        recent_texts = [mem.get("text", "") for mem in recent_memories[:self.recent_memory_count]]
        if not recent_texts:
            return 1.0
        
        recent_embeddings = encoder.encode(
            recent_texts,
            normalize_embeddings=True,
        )
        
        # Compute similarities
        similarities = np.dot(
            np.array(input_embedding),
            np.array(recent_embeddings).T,
        )
        
        # Novelty = 1 - max_similarity
        max_similarity = float(np.max(similarities))
        novelty = 1.0 - max_similarity
        
        return self._clamp_score(novelty)
    
    def _generate_explanation(self, score: float, context: AttentionContext) -> str:
        """
        Generate explanation for the novelty score.
        
        Args:
            score: The computed novelty score
            context: The attention context
            
        Returns:
            Human-readable explanation
        """
        if score >= 0.8:
            return f"Input is highly novel (score: {score:.2f}), significantly different from recent memories."
        elif score >= 0.5:
            return f"Input is moderately novel (score: {score:.2f}), somewhat different from recent context."
        elif score >= 0.3:
            return f"Input has low novelty (score: {score:.2f}), similar to recent memories."
        else:
            return f"Input is not novel (score: {score:.2f}), very similar to recent context."
    
    def _build_metadata(self, score: float, context: AttentionContext) -> dict:
        """Build metadata with novelty-specific information."""
        metadata = super()._build_metadata(score, context)
        metadata.update({
            "recent_memory_count": self.recent_memory_count,
            "embedding_model": self.embedding_model,
        })
        return metadata
