"""
main.py — LAMB FastAPI Application
Lifelong Adaptive Memory Buffer

Endpoints:
  POST /remember          Store a new memory
  POST /recall            Search memories for a query
  POST /chat              Full chat with memory injection
  POST /consolidate       Manually trigger consolidation
  GET  /stats/{session}   Memory stats for a session
  DELETE /session/{id}    Clear all memories for a session
"""
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

import anthropic
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .models import (
    MemoryInput, EpisodicMemory,
    ChatRequest, ChatResponse,
    MemoryStats, RecallRequest,
)
from .memory_store import MemoryStore
from .salience import compute_salience
from .forgetting import current_strength, get_decayed_ids
from .consolidation import should_consolidate, run_consolidation
from .retrieval import (
    retrieve_context, push_working_memory,
    build_system_prompt, get_working_memory,
)
from .replay import ReplayBuffer
from .lamb_bench import run_full_benchmark, print_report


# ------------------------------------------------------------------ #
#  App init                                                            #
# ------------------------------------------------------------------ #

store: MemoryStore = None
replay: ReplayBuffer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global store, replay
    print("[LAMB] Loading embedding model & connecting to ChromaDB...")
    store = MemoryStore()
    replay = ReplayBuffer()
    print("[LAMB] Ready.")
    yield
    print("[LAMB] Shutting down.")


app = FastAPI(
    title="LAMB — Lifelong Adaptive Memory Buffer",
    description="Persistent memory layer for LLMs: salience scoring, forgetting curve, consolidation.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------ #
#  POST /remember                                                      #
# ------------------------------------------------------------------ #

@app.post("/remember", summary="Store a memory")
async def remember(
    payload: MemoryInput,
    background_tasks: BackgroundTasks,
):
    """
    Store text as an episodic memory after salience filtering.
    Returns whether the memory was accepted or discarded.
    """
    embedding = store.encode(payload.text)

    salience = compute_salience(
        text=payload.text,
        query_embedding=embedding,
        store=store,
        session_id=payload.session_id,
    )

    if salience < settings.salience_threshold:
        return {
            "stored": False,
            "reason": "below salience threshold",
            "salience": round(salience, 3),
        }

    memory = EpisodicMemory(
        text=payload.text,
        session_id=payload.session_id,
        role=payload.role,
        salience=salience,
        stability=settings.base_stability,
        metadata=payload.metadata,
    )
    store.add_episodic(memory)
    replay.add(memory, task_tag=payload.metadata.get("task", "general"))

    # Also push to working memory
    push_working_memory(payload.session_id, payload.role, payload.text)

    # Trigger consolidation in background if threshold reached
    if should_consolidate(store, payload.session_id):
        background_tasks.add_task(_consolidate_bg, payload.session_id)

    return {
        "stored": True,
        "memory_id": memory.id,
        "salience": round(salience, 3),
    }


async def _consolidate_bg(session_id: str):
    n = await run_consolidation(store, session_id)
    if n:
        print(f"[LAMB] Consolidated {n} semantic memories for session '{session_id}'")


# ------------------------------------------------------------------ #
#  POST /recall                                                        #
# ------------------------------------------------------------------ #

@app.post("/recall", summary="Search memories")
async def recall(payload: RecallRequest):
    """
    Semantic search across episodic + semantic memories.
    Returns ranked results with strength scores.
    """
    embedding = store.encode(payload.query)

    episodic = store.search_episodic(
        query_embedding=embedding,
        session_id=payload.session_id,
        top_k=payload.top_k,
    )
    semantic = store.search_semantic(
        query_embedding=embedding,
        session_id=payload.session_id,
        top_k=3,
    )

    return {
        "episodic": [
            {
                "id": m.id,
                "text": m.text,
                "role": m.role,
                "salience": round(m.salience, 3),
                "strength": round(current_strength(m), 3),
                "recall_count": m.recall_count,
                "age_hours": round(
                    (datetime.utcnow().timestamp() - m.timestamp) / 3600, 1
                ),
            }
            for m in episodic
        ],
        "semantic": [
            {
                "id": m.id,
                "text": m.text,
                "importance": round(m.importance, 3),
                "source_count": len(m.source_ids),
            }
            for m in semantic
        ],
    }


# ------------------------------------------------------------------ #
#  POST /chat                                                          #
# ------------------------------------------------------------------ #

@app.post("/chat", response_model=ChatResponse, summary="Chat with memory")
async def chat(payload: ChatRequest):
    """
    Full chat endpoint — injects relevant memories into context,
    calls Claude, stores the exchange, triggers consolidation if needed.
    """
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=500,
            detail="ANTHROPIC_API_KEY not set in .env",
        )

    # 1. Retrieve relevant memories
    context_block, used_ids = retrieve_context(
        query=payload.message,
        session_id=payload.session_id,
        store=store,
    )

    # 2. Build memory-aware system prompt
    system = build_system_prompt(payload.system_prompt, context_block)

    # 3. Get working memory as message history
    working = get_working_memory(payload.session_id)
    history = [
        {"role": role, "content": text}
        for role, text in working[:-1]   # exclude current message (not yet stored)
        if role in ("user", "assistant")
    ]
    history.append({"role": "user", "content": payload.message})

    # 4. Call Claude
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=system,
        messages=history,
    )
    reply = response.content[0].text

    # 5. Store user turn + assistant reply
    for role, text in [("user", payload.message), ("assistant", reply)]:
        emb = store.encode(text)
        sal = compute_salience(text, emb, store, payload.session_id)
        if sal >= settings.salience_threshold:
            mem = EpisodicMemory(
                text=text,
                session_id=payload.session_id,
                role=role,
                salience=sal,
                stability=settings.base_stability,
            )
            store.add_episodic(mem)
        push_working_memory(payload.session_id, role, text)

    # 6. Background consolidation if needed
    if should_consolidate(store, payload.session_id):
        asyncio.create_task(_consolidate_bg(payload.session_id))

    # Rough token estimate
    token_estimate = len((system + payload.message).split()) * 1.3

    return ChatResponse(
        reply=reply,
        memories_used=[m["text"] if isinstance(m, dict) else m for m in
                       [{"text": uid} for uid in used_ids]],
        context_tokens_estimate=int(token_estimate),
    )


# ------------------------------------------------------------------ #
#  POST /consolidate                                                   #
# ------------------------------------------------------------------ #

@app.post("/consolidate/{session_id}", summary="Manual consolidation")
async def consolidate(session_id: str):
    """Force consolidation for a session."""
    n = await run_consolidation(store, session_id)
    return {"semantic_memories_created": n, "session_id": session_id}


# ------------------------------------------------------------------ #
#  GET /stats                                                          #
# ------------------------------------------------------------------ #

@app.get("/stats/{session_id}", response_model=MemoryStats, summary="Memory stats")
async def stats(session_id: str):
    """Return memory statistics for a session."""
    all_episodic = store.get_all_episodic(session_id)
    all_semantic = store.get_all_semantic(session_id)

    consolidated_count = sum(1 for m in all_episodic if m.consolidated)
    avg_salience = (
        sum(m.salience for m in all_episodic) / len(all_episodic)
        if all_episodic else 0.0
    )
    now = datetime.utcnow().timestamp()
    oldest_hours = (
        (now - min(m.timestamp for m in all_episodic)) / 3600
        if all_episodic else 0.0
    )

    return MemoryStats(
        session_id=session_id,
        episodic_count=len(all_episodic),
        semantic_count=len(all_semantic),
        consolidated_count=consolidated_count,
        avg_salience=round(avg_salience, 3),
        oldest_memory_hours=round(oldest_hours, 1),
    )


# ------------------------------------------------------------------ #
#  POST /prune                                                         #
# ------------------------------------------------------------------ #

@app.post("/prune/{session_id}", summary="Prune decayed memories")
async def prune(session_id: str):
    """Delete episodic memories whose strength has decayed below threshold."""
    all_episodic = store.get_all_episodic(session_id)
    dead_ids = get_decayed_ids(all_episodic)
    if dead_ids:
        store.delete_episodic(dead_ids)
    return {"pruned": len(dead_ids), "remaining": len(all_episodic) - len(dead_ids)}


# ------------------------------------------------------------------ #
#  DELETE /session                                                     #
# ------------------------------------------------------------------ #

@app.delete("/session/{session_id}", summary="Clear session memories")
async def clear_session(session_id: str):
    """Delete all episodic and semantic memories for a session."""
    episodic = store.get_all_episodic(session_id)
    semantic = store.get_all_semantic(session_id)
    store.delete_episodic([m.id for m in episodic])
    # Semantic collection doesn't have bulk delete — remove one by one
    store.semantic.delete(ids=[m.id for m in semantic])
    return {
        "cleared": True,
        "episodic_deleted": len(episodic),
        "semantic_deleted": len(semantic),
    }


# ------------------------------------------------------------------ #
#  GET /replay/stats                                                   #
# ------------------------------------------------------------------ #

@app.get("/replay/stats", summary="Replay buffer stats")
async def replay_stats():
    """Stats for the catastrophic forgetting replay buffer."""
    return replay.stats()


@app.post("/replay/export", summary="Export replay buffer as JSONL")
async def replay_export(
    path: str = "./replay_training_data.jsonl",
    task_tag: Optional[str] = None,
):
    """Export replay buffer as JSONL for LoRA fine-tuning."""
    n = replay.export_jsonl(path=path, task_tag=task_tag)
    return {"exported_pairs": n, "path": path}


@app.post("/replay/record-perf", summary="Record performance snapshot")
async def record_performance(
    task_tag: str, metric_name: str, value: float
):
    """Record a performance metric for forgetting detection."""
    replay.record_performance(task_tag, metric_name, value)
    return {"recorded": True}


@app.get("/replay/detect-forgetting", summary="Detect catastrophic forgetting")
async def detect_forgetting(
    task_tag: str, metric_name: str, current_value: float
):
    """Compare current metric against baseline — detect forgetting."""
    return replay.detect_forgetting(task_tag, metric_name, current_value)


# ------------------------------------------------------------------ #
#  POST /benchmark                                                     #
# ------------------------------------------------------------------ #

@app.post("/benchmark", summary="Run LAMB-Bench evaluation suite")
async def benchmark():
    """
    Run all 4 LAMB-Bench suites:
    salience precision/recall, forgetting curve, consolidation quality, retrieval relevance.
    This is LAMB's novel contribution — no existing benchmark tests salience + decay together.
    """
    report = await run_full_benchmark(store)
    print_report(report)
    return report


# ------------------------------------------------------------------ #
#  GET /health                                                         #
# ------------------------------------------------------------------ #

@app.get("/health")
async def health():
    return {"status": "ok", "system": "LAMB v1.0"}
