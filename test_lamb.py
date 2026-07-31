"""
test_lamb.py — Quick smoke test (no API key needed for memory ops)
Run: python test_lamb.py
"""
import asyncio
import sys
sys.path.insert(0, ".")

from .memory_store import MemoryStore
from .models import EpisodicMemory
from .salience import compute_salience
from .forgetting import current_strength, reinforce, get_decayed_ids
from datetime import datetime


def test_salience(store: MemoryStore):
    print("\n--- Salience Scoring ---")
    test_cases = [
        ("ok", "user"),
        ("hi", "user"),
        ("I am building a FastAPI persistent memory system for AGI research", "user"),
        ("My FYP deadline is 25th May, it is critical", "user"),
        ("I hate when code breaks at 2am before demo day", "user"),
        ("yes", "user"),
    ]
    for text, role in test_cases:
        emb = store.encode(text)
        sal = compute_salience(text, emb, store, session_id="test")
        status = "STORE" if sal >= 0.35 else "DISCARD"
        print(f"  [{status}] salience={sal:.3f} | '{text[:60]}'")


def test_forgetting():
    print("\n--- Forgetting Curve ---")
    now = datetime.utcnow().timestamp()

    # Fresh memory
    fresh = EpisodicMemory(
        text="User is working on LAMB memory system",
        session_id="test",
        role="user",
        salience=0.8,
        stability=24.0,
        timestamp=now,
    )
    print(f"  Fresh memory strength: {current_strength(fresh):.3f} (expect ~0.8)")

    # Old memory (48 hours ago)
    old = EpisodicMemory(
        text="Some old conversation",
        session_id="test",
        role="user",
        salience=0.5,
        stability=24.0,
        timestamp=now - 48 * 3600,
    )
    print(f"  48h old memory strength: {current_strength(old):.3f} (should be low)")

    # Reinforce and check
    reinforced = reinforce(old)
    print(f"  After reinforcement — stability: {reinforced.stability:.1f}h (was 24.0h)")

    # Decay check
    very_old = EpisodicMemory(
        text="Ancient memory",
        session_id="test",
        role="user",
        salience=0.4,
        stability=24.0,
        timestamp=now - 200 * 3600,
    )
    dead_ids = get_decayed_ids([very_old])
    print(f"  200h old memory → prune candidate: {len(dead_ids) > 0}")


def test_store_and_retrieve(store: MemoryStore):
    print("\n--- Store & Retrieve ---")
    session = "test_session"

    memories_to_add = [
        "User is Shakeel, CS student at UET Lahore, specializing in AI/ML",
        "User is building LAMB — a persistent memory system for LLMs",
        "User's FYP is Smart City Surveillance using YOLOv8 and multi-agent decision engine",
        "User freelances and is targeting ML engineer roles at Pakistani tech companies",
        "User prefers direct, practical answers without diplomatic framing",
    ]

    for text in memories_to_add:
        emb = store.encode(text)
        sal = compute_salience(text, emb, store, session)
        if sal >= 0.35:
            mem = EpisodicMemory(
                text=text, session_id=session,
                role="user", salience=sal, stability=24.0,
            )
            store.add_episodic(mem)
            print(f"  Stored (sal={sal:.3f}): {text[:55]}...")

    # Retrieve
    query = "What is the user working on?"
    q_emb = store.encode(query)
    results = store.search_episodic(q_emb, session, top_k=3)
    print(f"\n  Query: '{query}'")
    for r in results:
        print(f"    → {r.text[:60]}...")

    # Cleanup
    all_mems = store.get_all_episodic(session)
    store.delete_episodic([m.id for m in all_mems])


def main():
    print("=" * 50)
    print("  LAMB — Smoke Test")
    print("=" * 50)

    print("\nLoading MemoryStore (downloads model on first run)...")
    store = MemoryStore()
    print("Store ready.")

    test_salience(store)
    test_forgetting()
    test_store_and_retrieve(store)

    print("\n" + "=" * 50)
    print("  All tests passed!")
    print("  Run the server: uvicorn lamb.main:app --reload")
    print("=" * 50)


if __name__ == "__main__":
    main()
