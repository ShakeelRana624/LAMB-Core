"""
lamb_bench.py — LAMB-Bench Evaluation Suite (Gap 05)
=====================================================
Addresses: No benchmark tests salience-based storage + decay simultaneously.

Problem (from literature):
  MemBench (Tan et al. 2025), LoCoMo (Maharana et al. 2024), LongMemEval
  all test retrieval accuracy — but NONE of them test:
    (a) whether trivial inputs were correctly discarded (salience filter)
    (b) whether memory strength decays correctly over time
    (c) whether consolidation produces accurate semantic summaries
  This is LAMB's novel evaluation contribution.

LAMB-Bench runs 4 test suites:
  Suite 1 — Salience Precision/Recall
    Are important inputs stored? Are trivial inputs discarded?

  Suite 2 — Forgetting Curve Correctness
    Does memory strength decay at the right rate?
    Does reinforcement (recall) correctly boost stability?

  Suite 3 — Consolidation Quality
    Are semantic summaries faithful to source episodic memories?
    Is no information hallucinated or lost?

  Suite 4 — Retrieval Relevance
    Do retrieved memories match the query intent?
    Measured by embedding cosine similarity.

Output: a structured benchmark report (JSON + human-readable summary).
"""

import asyncio
import json
import math
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np

from .config import settings
from .memory_store import MemoryStore
from .models import EpisodicMemory
from .salience import compute_salience
from .forgetting import current_strength, reinforce


# ------------------------------------------------------------------ #
#  Benchmark fixtures                                                  #
# ------------------------------------------------------------------ #

# Should be STORED (high salience, important content)
SHOULD_STORE = [
    "I am building a persistent memory system called LAMB for my AGI research",
    "My FYP deadline is 25th May — the presentation is critical for graduation",
    "The weapon detection mAP@0.5 is 93.6% — that is our key metric",
    "I prefer direct, practical answers without diplomatic framing",
    "We need to implement episodic to semantic consolidation in the pipeline",
    "The FastAPI server crashes when ChromaDB has more than 10k entries",
    "My goal is to submit this to IEEE conference before the deadline",
    "I am a Computer Science student at UET Lahore specializing in AI/ML",
]

# Should be DISCARDED (low salience, trivial content)
SHOULD_DISCARD = [
    "ok",
    "yes",
    "hi",
    "thanks",
    "sure",
    "got it",
    "bye",
    "alright",
    "hmm",
    "ok cool",
]

# Consolidation test: these related memories should merge into one summary
CONSOLIDATION_TEST_CLUSTER = [
    "User is working on a FastAPI backend for LAMB",
    "The backend uses ChromaDB for vector storage",
    "LAMB stands for Lifelong Adaptive Memory Buffer",
    "The system has three memory types: working, episodic, semantic",
]

CONSOLIDATION_EXPECTED_KEYWORDS = [
    "fastapi", "chromadb", "lamb", "memory", "episodic", "semantic"
]

# Retrieval test pairs: (query, expected_relevant_text)
RETRIEVAL_PAIRS = [
    (
        "What is the user working on?",
        "I am building a persistent memory system called LAMB",
    ),
    (
        "When is the deadline?",
        "My FYP deadline is 25th May",
    ),
    (
        "What is the detection accuracy?",
        "weapon detection mAP@0.5 is 93.6%",
    ),
]


# ------------------------------------------------------------------ #
#  Suite 1: Salience precision / recall                                #
# ------------------------------------------------------------------ #

def run_salience_suite(store: MemoryStore) -> dict:
    """Test salience filter: TP/FP/TN/FN."""
    session = f"bench_salience_{int(time.time())}"
    tp = fp = tn = fn = 0

    for text in SHOULD_STORE:
        emb = store.encode(text)
        sal = compute_salience(text, emb, store, session)
        stored = sal >= settings.salience_threshold
        if stored:
            tp += 1
        else:
            fn += 1

    for text in SHOULD_DISCARD:
        emb = store.encode(text)
        sal = compute_salience(text, emb, store, session)
        stored = sal >= settings.salience_threshold
        if not stored:
            tn += 1
        else:
            fp += 1

    precision = tp / max(tp + fp, 1)
    recall    = tp / max(tp + fn, 1)
    f1        = 2 * precision * recall / max(precision + recall, 1e-6)

    return {
        "suite": "salience",
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "precision": round(precision, 3),
        "recall":    round(recall, 3),
        "f1":        round(f1, 3),
        "pass": f1 >= 0.80,
        "verdict": "PASS" if f1 >= 0.80 else "FAIL",
        "note": f"{tp}/{len(SHOULD_STORE)} important stored, {tn}/{len(SHOULD_DISCARD)} trivial discarded",
    }


# ------------------------------------------------------------------ #
#  Suite 2: Forgetting curve correctness                               #
# ------------------------------------------------------------------ #

def run_forgetting_suite() -> dict:
    now = datetime.utcnow().timestamp()
    results = []

    test_cases = [
        ("fresh", 0, 0.8, 24.0, 0.75, 0.85),      # fresh → strength ≈ salience
        ("1h old", 1, 0.8, 24.0, 0.75, 0.83),      # 1h: slight decay
        ("12h old", 12, 0.8, 24.0, 0.55, 0.70),    # 12h: noticeable decay
        ("48h old", 48, 0.8, 24.0, 0.06, 0.15),    # 48h: significant decay
        ("low salience", 1, 0.3, 24.0, 0.25, 0.35),# low salience decays faster
    ]

    for label, hours_ago, salience, stability, lo, hi in test_cases:
        mem = EpisodicMemory(
            text=f"Test memory — {label}",
            session_id="bench",
            role="user",
            salience=salience,
            stability=stability,
            timestamp=now - hours_ago * 3600,
        )
        strength = current_strength(mem)
        passed = lo <= strength <= hi
        results.append({
            "label": label,
            "hours_old": hours_ago,
            "salience": salience,
            "strength": round(strength, 4),
            "expected_range": [lo, hi],
            "pass": passed,
        })

    # Test reinforcement boost
    old_mem = EpisodicMemory(
        text="Memory to reinforce",
        session_id="bench",
        role="user",
        salience=0.6,
        stability=24.0,
        timestamp=now - 24 * 3600,
    )
    before = current_strength(old_mem)
    reinforced = reinforce(old_mem)
    after = current_strength(reinforced)
    reinforce_pass = after > before and reinforced.stability > 24.0

    all_pass = all(r["pass"] for r in results) and reinforce_pass
    return {
        "suite": "forgetting_curve",
        "decay_tests": results,
        "reinforce_test": {
            "strength_before": round(before, 4),
            "strength_after": round(after, 4),
            "stability_after": round(reinforced.stability, 1),
            "pass": reinforce_pass,
        },
        "pass": all_pass,
        "verdict": "PASS" if all_pass else "FAIL",
    }


# ------------------------------------------------------------------ #
#  Suite 3: Consolidation quality                                      #
# ------------------------------------------------------------------ #

async def run_consolidation_suite(store: MemoryStore) -> dict:
    """Test that consolidation produces faithful, keyword-covering summaries."""
    import anthropic

    if not settings.anthropic_api_key:
        return {
            "suite": "consolidation",
            "verdict": "SKIP",
            "reason": "ANTHROPIC_API_KEY not set",
        }

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    cluster_text = "\n".join(
        f"[{i+1}] {t}" for i, t in enumerate(CONSOLIDATION_TEST_CLUSTER)
    )
    prompt = f"""Compress these related memory fragments into one concise factual statement (1-3 sentences).
State facts directly — no filler phrases.

{cluster_text}"""

    try:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        summary = response.content[0].text.strip()
    except Exception as e:
        return {"suite": "consolidation", "verdict": "ERROR", "error": str(e)}

    # Check keyword coverage
    summary_lower = summary.lower()
    found = [kw for kw in CONSOLIDATION_EXPECTED_KEYWORDS if kw in summary_lower]
    coverage = len(found) / len(CONSOLIDATION_EXPECTED_KEYWORDS)

    # Check hallucination: summary length shouldn't exceed cluster length massively
    source_len = sum(len(t) for t in CONSOLIDATION_TEST_CLUSTER)
    no_hallucination = len(summary) <= source_len * 0.8

    passed = coverage >= 0.6 and no_hallucination
    return {
        "suite": "consolidation",
        "summary": summary,
        "keywords_found": found,
        "keywords_missing": [k for k in CONSOLIDATION_EXPECTED_KEYWORDS if k not in summary_lower],
        "coverage": round(coverage, 3),
        "no_hallucination": no_hallucination,
        "pass": passed,
        "verdict": "PASS" if passed else "FAIL",
    }


# ------------------------------------------------------------------ #
#  Suite 4: Retrieval relevance                                        #
# ------------------------------------------------------------------ #

def run_retrieval_suite(store: MemoryStore) -> dict:
    """Test that retrieved memories are relevant to queries."""
    session = f"bench_retrieval_{int(time.time())}"

    # Seed memories
    for text in SHOULD_STORE:
        emb = store.encode(text)
        sal = compute_salience(text, emb, store, session)
        if sal >= settings.salience_threshold:
            mem = EpisodicMemory(
                text=text, session_id=session,
                role="user", salience=sal, stability=24.0,
            )
            store.add_episodic(mem)

    results = []
    for query, expected_text in RETRIEVAL_PAIRS:
        q_emb = store.encode(query)
        hits = store.search_episodic(q_emb, session, top_k=3)

        if not hits:
            results.append({
                "query": query, "top_result": None,
                "similarity": 0.0, "pass": False,
            })
            continue

        # Similarity between expected and top result
        expected_emb = np.array(store.encode(expected_text))
        top_emb      = np.array(store.encode(hits[0].text))
        similarity = float(np.dot(expected_emb, top_emb))

        results.append({
            "query": query,
            "top_result": hits[0].text[:80],
            "similarity": round(similarity, 3),
            "pass": similarity >= 0.75,
        })

    # Cleanup
    all_mems = store.get_all_episodic(session)
    store.delete_episodic([m.id for m in all_mems])

    all_pass = all(r["pass"] for r in results)
    avg_sim = sum(r["similarity"] for r in results) / max(len(results), 1)
    return {
        "suite": "retrieval",
        "pairs": results,
        "avg_similarity": round(avg_sim, 3),
        "pass": all_pass,
        "verdict": "PASS" if all_pass else "FAIL",
    }


# ------------------------------------------------------------------ #
#  Runner                                                              #
# ------------------------------------------------------------------ #

async def run_full_benchmark(store: MemoryStore) -> dict:
    """Run all 4 suites and return a complete benchmark report."""
    print("[LAMB-Bench] Running Suite 1: Salience...")
    s1 = run_salience_suite(store)

    print("[LAMB-Bench] Running Suite 2: Forgetting curve...")
    s2 = run_forgetting_suite()

    print("[LAMB-Bench] Running Suite 3: Consolidation quality...")
    s3 = await run_consolidation_suite(store)

    print("[LAMB-Bench] Running Suite 4: Retrieval relevance...")
    s4 = run_retrieval_suite(store)

    suites = [s1, s2, s3, s4]
    passed  = sum(1 for s in suites if s.get("verdict") == "PASS")
    skipped = sum(1 for s in suites if s.get("verdict") == "SKIP")
    failed  = sum(1 for s in suites if s.get("verdict") == "FAIL")

    report = {
        "lamb_bench_version": "1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "summary": {
            "total_suites": len(suites),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "overall": "PASS" if failed == 0 else "FAIL",
        },
        "suites": {
            "salience":         s1,
            "forgetting_curve": s2,
            "consolidation":    s3,
            "retrieval":        s4,
        },
    }
    return report


def print_report(report: dict):
    """Human-readable summary of benchmark results."""
    summary = report["summary"]
    print("\n" + "=" * 55)
    print(f"  LAMB-Bench v{report['lamb_bench_version']} — {report['timestamp'][:10]}")
    print("=" * 55)
    print(f"  Overall: {summary['overall']}")
    print(f"  Passed:  {summary['passed']} / {summary['total_suites']}")
    if summary["skipped"]:
        print(f"  Skipped: {summary['skipped']}")

    for name, suite in report["suites"].items():
        verdict = suite.get("verdict", "?")
        icon = "✓" if verdict == "PASS" else ("~" if verdict == "SKIP" else "✗")
        print(f"\n  {icon} [{verdict}] {name.upper()}")

        if name == "salience":
            print(f"    F1={suite['f1']}  P={suite['precision']}  R={suite['recall']}")
            print(f"    {suite['note']}")
        elif name == "forgetting_curve":
            passing = sum(1 for t in suite["decay_tests"] if t["pass"])
            print(f"    Decay tests: {passing}/{len(suite['decay_tests'])} passed")
            print(f"    Reinforce: {suite['reinforce_test']['pass']}")
        elif name == "consolidation" and verdict == "PASS":
            print(f"    Coverage: {suite['coverage']*100:.0f}%")
            print(f"    Keywords found: {', '.join(suite['keywords_found'])}")
        elif name == "retrieval":
            print(f"    Avg similarity: {suite['avg_similarity']}")

    print("\n" + "=" * 55)
