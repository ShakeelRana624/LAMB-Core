"""
consolidation.py
Periodic consolidation: episodic memories → semantic summaries.

How it works:
  1. Take all unconsolidated episodic memories for a session.
  2. Cluster them by semantic similarity (cosine + simple agglomerative grouping).
  3. For each cluster with >= min_cluster_size members → call LLM to summarize.
  4. Store summary as a SemanticMemory.
  5. Mark source episodic memories as consolidated (they won't be returned in search).

This mirrors how human sleep consolidation works — related short-term
memories are merged into stable long-term knowledge.
"""
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from datetime import datetime
import anthropic

from .config import settings
from .models import EpisodicMemory, SemanticMemory
from .memory_store import MemoryStore


def should_consolidate(store: MemoryStore, session_id: str) -> bool:
    """Check if we've accumulated enough unconsolidated memories."""
    unconsolidated = store.get_all_episodic(
        session_id=session_id, only_unconsolidated=True
    )
    return len(unconsolidated) >= settings.consolidation_trigger


async def run_consolidation(store: MemoryStore, session_id: str) -> int:
    """
    Main consolidation pipeline.
    Returns number of semantic memories created.
    """
    unconsolidated = store.get_all_episodic(
        session_id=session_id, only_unconsolidated=True
    )
    if len(unconsolidated) < settings.consolidation_cluster_min:
        return 0

    # Step 1: Embed all unconsolidated memories
    texts = [m.text for m in unconsolidated]
    embeddings = np.array(store.encode_batch(texts))

    # Step 2: Cluster by semantic similarity
    clusters = _cluster_memories(unconsolidated, embeddings)

    # Step 3: Summarize each valid cluster
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    semantic_memories_created = 0

    for cluster_memories in clusters:
        if len(cluster_memories) < settings.consolidation_cluster_min:
            continue   # too small to summarize, skip

        summary = await _summarize_cluster(client, cluster_memories)
        if not summary:
            continue

        # Importance = mean salience of source memories
        importance = float(np.mean([m.salience for m in cluster_memories]))

        sem_mem = SemanticMemory(
            text=summary,
            source_ids=[m.id for m in cluster_memories],
            session_id=session_id,
            created_at=datetime.utcnow().timestamp(),
            importance=importance,
        )
        store.add_semantic(sem_mem)
        store.mark_consolidated([m.id for m in cluster_memories])
        semantic_memories_created += 1

    return semantic_memories_created


def _cluster_memories(
    memories: list[EpisodicMemory],
    embeddings: np.ndarray,
) -> list[list[EpisodicMemory]]:
    """
    Agglomerative clustering on cosine similarity.
    distance_threshold=0.4 means clusters are reasonably tight.
    """
    n = len(memories)
    if n < 2:
        return [memories]

    try:
        clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=0.4,
            metric="cosine",
            linkage="average",
        )
        labels = clustering.fit_predict(embeddings)
    except Exception:
        # Fallback: all in one cluster
        return [memories]

    # Group memories by cluster label
    cluster_dict: dict[int, list[EpisodicMemory]] = {}
    for mem, label in zip(memories, labels):
        cluster_dict.setdefault(label, []).append(mem)

    return list(cluster_dict.values())


async def _summarize_cluster(
    client: anthropic.AsyncAnthropic,
    memories: list[EpisodicMemory],
) -> str | None:
    """
    Use Claude to compress a cluster of related episodic memories
    into a single semantic summary.
    """
    memory_texts = "\n".join(
        f"[{i+1}] ({m.role}) {m.text}"
        for i, m in enumerate(memories)
    )

    prompt = f"""You are a memory consolidation system. The following are related conversation fragments:

{memory_texts}

Compress these into a single concise factual statement (1-3 sentences) that captures the key information.
Focus on facts, preferences, goals, and important context.
Do NOT include filler phrases like "The user said" — just state the facts directly.
Example good output: "User is building a FastAPI + ChromaDB persistent memory system called LAMB for their AI research."
"""
    try:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"[LAMB] Consolidation LLM error: {e}")
        # Fallback: simple concatenation truncated
        combined = " | ".join(m.text for m in memories)
        return combined[:300] if combined else None
