"""
retrieval.py
Smart retrieval: given a user query, assembles the best possible context
from working memory + episodic + semantic memories.

Retrieval order (priority):
  1. Working memory — last K turns (always included, no search needed)
  2. Semantic memory — top-K relevant long-term facts
  3. Episodic memory — top-K relevant raw episodes, ranked by composite score

Composite score = relevance * 0.5 + strength * 0.3 + recency * 0.2

After retrieval, memories that are accessed have their stability reinforced.
"""
from collections import deque
from typing import Optional
from datetime import datetime

from .config import settings
from .models import EpisodicMemory, SemanticMemory
from .memory_store import MemoryStore
from .forgetting import compute_composite_score, reinforce


# In-memory working memory buffer per session
# { session_id: deque of (role, text) tuples }
_working_memory: dict[str, deque] = {}


def push_working_memory(session_id: str, role: str, text: str) -> None:
    """Add a turn to working memory (sliding window)."""
    if session_id not in _working_memory:
        _working_memory[session_id] = deque(maxlen=settings.working_memory_turns * 2)
    _working_memory[session_id].append((role, text))


def get_working_memory(session_id: str) -> list[tuple[str, str]]:
    """Get all turns in current working memory."""
    return list(_working_memory.get(session_id, []))


def retrieve_context(
    query: str,
    session_id: str,
    store: MemoryStore,
) -> tuple[str, list[str]]:
    """
    Build a memory-enriched context string for the LLM.

    Returns:
        context_block (str)  : formatted string to prepend to system prompt
        used_memory_ids (list): IDs of episodic memories accessed (for stats)
    """
    query_embedding = store.encode(query)
    used_ids = []

    # --- Semantic memories (long-term facts) ---
    semantic_hits = store.search_semantic(
        query_embedding=query_embedding,
        session_id=session_id,
        top_k=settings.semantic_top_k,
    )

    # --- Episodic memories ---
    episodic_hits = store.search_episodic(
        query_embedding=query_embedding,
        session_id=session_id,
        top_k=settings.episodic_top_k * 2,   # fetch more, then re-rank
    )

    # Re-rank episodic by composite score (relevance + strength + recency)
    scored_episodic = _score_episodic(episodic_hits, query_embedding, store)
    top_episodic = scored_episodic[: settings.episodic_top_k]

    # Reinforce retrieved episodic memories (spaced repetition)
    for mem in top_episodic:
        reinforced = reinforce(mem)
        store.update_episodic_meta(mem.id, {
            "recall_count": reinforced.recall_count,
            "stability": reinforced.stability,
            "last_recalled": reinforced.last_recalled,
        })
        used_ids.append(mem.id)

    # --- Assemble context block ---
    context_parts = []

    if semantic_hits:
        facts = "\n".join(f"• {m.text}" for m in semantic_hits)
        context_parts.append(f"[Long-term knowledge about this user]\n{facts}")

    if top_episodic:
        episodes = "\n".join(
            f"• ({m.role}) {m.text}"
            for m in top_episodic
        )
        context_parts.append(f"[Relevant past episodes]\n{episodes}")

    working = get_working_memory(session_id)
    if working:
        turns = "\n".join(f"{role}: {text}" for role, text in working[-6:])
        context_parts.append(f"[Current conversation]\n{turns}")

    context_block = "\n\n".join(context_parts)
    return context_block, used_ids


def _score_episodic(
    memories: list[EpisodicMemory],
    query_embedding: list[float],
    store: MemoryStore,
) -> list[EpisodicMemory]:
    """Re-rank by composite score."""
    if not memories:
        return []

    import numpy as np
    q = np.array(query_embedding)
    embeddings = store.encode_batch([m.text for m in memories])

    scored = []
    for mem, emb in zip(memories, embeddings):
        relevance = float(np.dot(q, np.array(emb)))   # cosine similarity
        composite = compute_composite_score(mem, relevance)
        scored.append((composite, mem))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [mem for _, mem in scored]


def build_system_prompt(base_prompt: str, context_block: str) -> str:
    """Inject memory context into the system prompt."""
    if not context_block.strip():
        return base_prompt

    return f"""{base_prompt}

---
MEMORY CONTEXT (use this to personalize your response):
{context_block}
---
Use the above memory context naturally. Do not explicitly say "according to my memory" — just respond as if you know the user."""
