"""
forgetting.py
Implements the Ebbinghaus forgetting curve for memory decay.

Memory strength at time t (hours after last recall):

    strength(t) = e^(-t / stability)

- stability  : how long the memory "lasts" (in hours). Starts at base_stability.
               Each time a memory is recalled, stability *= reinforcement_boost.
               This models spaced repetition — recalled memories stick longer.

- strength   : 1.0 = fresh, 0.0 = completely forgotten.
               Memories below strength_threshold are candidates for pruning.

Usage:
    score = current_strength(memory)        # check if alive
    memory = reinforce(memory)              # boost after recall
    dead_ids = get_decayed_ids(memories)   # find memories to prune
"""
import math
from datetime import datetime
from typing import Optional

from .config import settings
from .models import EpisodicMemory


STRENGTH_PRUNE_THRESHOLD = 0.10   # below 10% strength → prune candidate


def current_strength(memory: EpisodicMemory) -> float:
    """
    Compute current memory strength [0, 1] using the forgetting curve.

    strength = salience_weight * e^(-hours_elapsed / stability)

    Salience acts as initial encoding strength — high salience memories
    decay more slowly in absolute terms (they start higher).
    """
    now = datetime.utcnow().timestamp()
    reference_time = memory.last_recalled or memory.timestamp
    hours_elapsed = (now - reference_time) / 3600.0

    base_strength = memory.salience   # initial encoding strength
    decay = math.exp(-hours_elapsed / max(memory.stability, 0.1))
    return float(max(base_strength * decay, 0.0))


def reinforce(memory: EpisodicMemory) -> EpisodicMemory:
    """
    Called when a memory is retrieved — boosts its stability (spaced repetition).
    Also updates last_recalled timestamp and increments recall_count.
    """
    now = datetime.utcnow().timestamp()
    memory.stability *= settings.reinforcement_boost
    memory.recall_count += 1
    memory.last_recalled = now
    return memory


def get_decayed_ids(memories: list[EpisodicMemory]) -> list[str]:
    """
    Returns IDs of memories whose strength has fallen below the prune threshold.
    These are candidates for deletion or archival.
    """
    return [
        m.id
        for m in memories
        if current_strength(m) < STRENGTH_PRUNE_THRESHOLD
        and not m.consolidated   # don't prune if already in semantic
    ]


def rank_by_strength(memories: list[EpisodicMemory]) -> list[EpisodicMemory]:
    """Sort memories by current strength descending."""
    return sorted(memories, key=current_strength, reverse=True)


def compute_composite_score(
    memory: EpisodicMemory,
    relevance_score: float,
    recency_weight: float = 0.2,
    strength_weight: float = 0.3,
    relevance_weight: float = 0.5,
) -> float:
    """
    Composite retrieval score combining:
      - semantic relevance (cosine similarity from ChromaDB search)
      - memory strength (forgetting curve)
      - recency (how fresh is this memory?)

    Used to rank memories for context injection.
    """
    now = datetime.utcnow().timestamp()
    hours_since = (now - memory.timestamp) / 3600.0
    # Recency score: exponential decay over 72 hours
    recency = math.exp(-hours_since / 72.0)

    strength = current_strength(memory)

    return (
        relevance_weight * relevance_score
        + strength_weight * strength
        + recency_weight * recency
    )
