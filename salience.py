"""
salience.py
Computes a salience score [0, 1] for each incoming memory.

salience = α·novelty + β·emotion_weight + γ·frequency_bonus

- novelty     : how different is this from recent memories? (cosine distance)
- emotion     : presence of emotionally/informationally significant keywords
- frequency   : slight boost for topics already seen (reinforcement signal)

If salience < threshold → memory is discarded (not stored).
"""
import re
import numpy as np
from typing import Optional

from .config import settings
from .memory_store import MemoryStore

# Keywords that raise emotional/informational weight
HIGH_SALIENCE_PATTERNS = [
    r"\b(important|critical|urgent|remember|never forget|always|never)\b",
    r"\b(deadline|meeting|appointment|interview|exam|submission)\b",
    r"\b(hate|love|angry|excited|scared|worried|happy|frustrated)\b",
    r"\b(project|task|goal|plan|strategy|idea|problem|solution)\b",
    r"\b(name|called|known as|my|I am|I'm|we are|our)\b",
    r"\b(error|bug|fail|crash|broke|fix|solved|works)\b",
]

LOW_SALIENCE_PATTERNS = [
    r"^(ok|okay|sure|yes|no|thanks|thank you|got it|alright)\.?$",
    r"^(hi|hello|hey|bye|goodbye|see you)[\s!]*$",
    r"^.{1,10}$",    # very short responses
]


def compute_salience(
    text: str,
    query_embedding: list[float],
    store: MemoryStore,
    session_id: str,
) -> float:
    """
    Returns salience score [0, 1].
    """
    # 1. Novelty — how far is this from existing recent memories?
    novelty = _compute_novelty(query_embedding, store, session_id)

    # 2. Emotional / informational weight
    emotion = _compute_emotion_weight(text)

    # 3. Frequency bonus (soft reinforcement)
    frequency = _compute_frequency_bonus(text, query_embedding, store, session_id)

    # Weighted sum
    salience = (
        settings.novelty_weight * novelty
        + settings.emotion_weight * emotion
        + settings.frequency_weight * frequency
    )

    # Hard override: boring single-word acks → always discard
    if _is_trivial(text):
        return 0.0

    return float(np.clip(salience, 0.0, 1.0))


def _compute_novelty(
    embedding: list[float],
    store: MemoryStore,
    session_id: str,
) -> float:
    """
    Cosine distance from the nearest recent episodic memory.
    High novelty = very different from what's already stored.
    """
    try:
        recent = store.search_episodic(
            query_embedding=embedding,
            session_id=session_id,
            top_k=3,
        )
        if not recent:
            return 1.0   # nothing stored yet → maximum novelty

        # Nearest neighbour similarity (ChromaDB returns cosine distance)
        # We get them via search — the first result is closest
        # Re-encode recent texts and compute similarity manually
        recent_embeddings = store.encode_batch([m.text for m in recent])
        q = np.array(embedding)
        similarities = [
            float(np.dot(q, np.array(e)))
            for e in recent_embeddings
        ]
        max_similarity = max(similarities)
        # novelty = 1 - similarity (more different → more novel)
        return 1.0 - max_similarity

    except Exception:
        return 0.5   # safe fallback


def _compute_emotion_weight(text: str) -> float:
    """
    Pattern-based emotional/informational significance.
    Returns 0.0 – 1.0.
    """
    text_lower = text.lower()
    hits = sum(
        1
        for pattern in HIGH_SALIENCE_PATTERNS
        if re.search(pattern, text_lower)
    )
    # Normalise: 3+ hits → max score
    return min(hits / 3.0, 1.0)


def _compute_frequency_bonus(
    text: str,
    embedding: list[float],
    store: MemoryStore,
    session_id: str,
) -> float:
    """
    If similar content has been mentioned before → slight reinforcement boost.
    This captures recurring themes the user cares about.
    """
    try:
        similar = store.search_episodic(
            query_embedding=embedding,
            session_id=session_id,
            top_k=5,
        )
        if not similar:
            return 0.0

        # Count how many have high similarity
        q = np.array(embedding)
        similar_embeddings = store.encode_batch([m.text for m in similar])
        high_sim_count = sum(
            1
            for e in similar_embeddings
            if np.dot(q, np.array(e)) > 0.80
        )
        # More occurrences → stronger reinforcement (capped)
        return min(high_sim_count / 4.0, 1.0)

    except Exception:
        return 0.0


def _is_trivial(text: str) -> bool:
    """Returns True if the text is too trivial to store."""
    text_stripped = text.strip().lower()
    return any(
        re.match(pattern, text_stripped)
        for pattern in LOW_SALIENCE_PATTERNS
    )
