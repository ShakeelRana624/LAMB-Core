# LAMB — Lifelong Adaptive Memory Buffer
## Production-Grade Persistent Memory Layer for LLMs

---

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [What Problem Does LAMB Solve?](#what-problem-does-lamb-solve)
- [Core Features](#core-features)
- [Architecture & How It Works](#architecture--how-it-works)
- [File Structure](#file-structure)
- [File Descriptions](#file-descriptions)
- [Key Concepts Explained](#key-concepts-explained)
- [Setup Instructions](#setup-instructions)
- [API Reference](#api-reference)
- [Testing & Benchmarking](#testing--benchmarking)
- [Configuration](#configuration)
- [Dependencies](#dependencies)

---

## 🎯 Project Overview

**LAMB** (Lifelong Adaptive Memory Buffer) is a production-grade persistent memory system for Large Language Models (LLMs) that addresses critical gaps in current memory architectures. It provides LLMs with human-like memory capabilities including:

- **Salience-based filtering** — automatically discards trivial inputs
- **Forgetting curve** — memories decay over time unless recalled (spaced repetition)
- **Memory consolidation** — similar episodic memories merge into semantic knowledge
- **Smart retrieval** — ranks memories by relevance, strength, and recency
- **Replay buffer** — prevents catastrophic forgetting during fine-tuning
- **LAMB-Bench** — novel evaluation suite for memory systems

This is a research-grade implementation suitable for AGI research, SaaS products, and production deployments.

---

## 🔥 What Problem Does LAMB Solve?

Current LLMs have no persistent memory — they forget everything after the context window ends. LAMB solves this by:

1. **Gap 1: No Salience Filtering** — LLMs store everything, including "ok" and "thanks", wasting context
2. **Gap 2: No Forgetting Curve** — Old memories never decay, leading to stale context
3. **Gap 3: No Consolidation** — Raw episodes pile up without compression into knowledge
4. **Gap 4: Catastrophic Forgetting** — Fine-tuning on new tasks overwrites old knowledge
5. **Gap 5: No Evaluation Benchmark** — Existing benchmarks don't test salience + decay together

LAMB addresses all 5 gaps with a unified, production-ready system.

---

## ✨ Core Features

### 1. Salience Scoring (`salience.py`)
- Computes a salience score [0, 1] for each incoming memory
- Formula: `salience = α·novelty + β·emotion + γ·frequency`
- **Novelty**: How different is this from recent memories? (cosine distance)
- **Emotion**: Pattern-based detection of important keywords (urgent, deadline, critical, etc.)
- **Frequency**: Boost for recurring themes the user cares about
- Automatically discards trivial inputs below threshold (default: 0.35)
- Hard override for boring single-word acks ("ok", "yes", "hi", etc.)

### 2. Forgetting Curve (`forgetting.py`)
- Implements Ebbinghaus forgetting curve: `strength(t) = e^(-t / stability)`
- **Stability**: How long memory lasts (default: 24 hours)
- **Reinforcement**: Each recall multiplies stability by 1.8x (spaced repetition)
- **Pruning**: Memories below 10% strength are candidates for deletion
- **Composite scoring**: Combines relevance (50%), strength (30%), recency (20%) for retrieval ranking

### 3. Memory Consolidation (`consolidation.py`)
- Mirrors human sleep consolidation
- Triggers every 10 new episodic memories (configurable)
- **Clustering**: Uses AgglomerativeClustering on cosine similarity
- **Summarization**: Claude LLM compresses clusters into 1-3 sentence facts
- Stores as `SemanticMemory` with source IDs for traceability
- Marks source episodic memories as consolidated (excluded from search)

### 4. Smart Retrieval (`retrieval.py`)
- **Working memory**: Last 6 turns always included (in-memory deque)
- **Semantic memory**: Top-K long-term facts (default: 3)
- **Episodic memory**: Top-K raw episodes, re-ranked by composite score (default: 4)
- **Reinforcement**: Retrieved memories get stability boost
- **Context injection**: Assembles formatted context block for LLM system prompt

### 5. Replay Buffer (`replay.py`)
- Addresses catastrophic forgetting during fine-tuning
- **Reservoir sampling**: Fixed-size buffer (500 samples) with statistical coverage
- **Salience weighting**: High-salience memories over-represented
- **Export**: JSONL format for HuggingFace/LoRA fine-tuning
- **Forgetting detection**: Tracks performance metrics, alerts if >15% drop

### 6. LAMB-Bench (`lamb_bench.py`)
- Novel evaluation suite — no existing benchmark tests salience + decay together
- **Suite 1**: Salience precision/recall (important stored? trivial discarded?)
- **Suite 2**: Forgetting curve correctness (decay rate, reinforcement boost)
- **Suite 3**: Consolidation quality (keyword coverage, no hallucination)
- **Suite 4**: Retrieval relevance (cosine similarity to expected results)
- Outputs structured JSON + human-readable summary

---

## 🏗️ Architecture & How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                     INCOMING TEXT                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  SALIENCE SCORING                                 │
│  novelty (50%) + emotion (30%) + frequency (20%)                │
│  threshold = 0.35 → below this → DISCARD                         │
└────────────────────────┬────────────────────────────────────────┘
                         │ PASS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              EPISODIC MEMORY (ChromaDB)                           │
│  • Raw events with embeddings                                     │
│  • Metadata: salience, stability, recall_count, timestamp         │
│  • Stored in vector database for semantic search                 │
└────────────────────────┬────────────────────────────────────────┘
                         │ every 10 new memories
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              CONSOLIDATION (LLM + Clustering)                    │
│  1. Cluster unconsolidated memories by similarity                │
│  2. For each cluster → Claude summarizes into 1-3 sentences    │
│  3. Store as SemanticMemory with source IDs                     │
│  4. Mark source episodic as consolidated                        │
└────────────────────────┬────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              SEMANTIC MEMORY (ChromaDB)                           │
│  • Compressed long-term knowledge                                 │
│  • LLM-generated summaries                                       │
│  • Importance score (mean salience of sources)                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  RETRIEVAL (on query)                             │
│  1. Working memory (last 6 turns)                                │
│  2. Semantic memory (top-3 long-term facts)                      │
│  3. Episodic memory (top-4, re-ranked by composite score)        │
│  4. Reinforce retrieved episodic memories                         │
│  5. Inject into LLM system prompt                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Example

**User says**: "My FYP deadline is 25th May — the presentation is critical for graduation"

1. **Salience**: High (contains "deadline", "critical", "graduation") → score: 0.72
2. **Storage**: Saved as EpisodicMemory with salience=0.72, stability=24.0
3. **Working memory**: Added to last-6-turns buffer
4. **After 10 memories**: Consolidation triggers, clusters similar memories
5. **Consolidation**: Claude summarizes: "User's FYP deadline is May 25th; presentation is critical for graduation"
6. **Retrieval**: When user asks "What's my deadline?", semantic memory is retrieved
7. **Reinforcement**: Retrieved memory stability boosted to 43.2 hours (24.0 × 1.8)

---

## 📁 File Structure

```
lamb/
├── main.py                 # FastAPI application (394 lines)
├── main2.py                # Alternative FastAPI app without replay buffer (335 lines)
├── config.py               # Configuration management (40 lines)
├── models.py               # Pydantic data models (71 lines)
├── memory_store.py         # ChromaDB wrapper (221 lines)
├── salience.py             # Salience scoring algorithm (160 lines)
├── forgetting.py           # Forgetting curve implementation (107 lines)
├── consolidation.py        # Memory consolidation (146 lines)
├── retrieval.py            # Smart retrieval logic (143 lines)
├── replay.py               # Replay buffer for catastrophic forgetting (347 lines)
├── lamb_bench.py           # LAMB-Bench evaluation suite (404 lines)
├── test_lamb.py            # Smoke tests (133 lines)
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (ANTHROPIC_API_KEY)
└── chroma_db/              # ChromaDB persistent storage (created at runtime)
```

---

## 📄 File Descriptions

### Core Application Files

**`main.py`** (394 lines)
- Main FastAPI application with 11 endpoints
- Endpoints: `/remember`, `/recall`, `/chat`, `/consolidate`, `/stats`, `/prune`, `/session`, `/replay/*`, `/benchmark`, `/health`
- Initializes MemoryStore and ReplayBuffer on startup
- CORS middleware enabled for cross-origin requests
- Background task for consolidation triggering

**`main2.py`** (335 lines)
- Alternative FastAPI app without replay buffer features
- Simpler version for deployments where catastrophic forgetting prevention is not needed
- Same core memory operations but excludes replay endpoints

**`config.py`** (40 lines)
- Pydantic `BaseSettings` class for configuration
- Environment variables loaded from `.env` file
- Settings include:
  - `anthropic_api_key`: Claude API key
  - `embedding_model`: SentenceTransformer model (default: all-MiniLM-L6-v2)
  - `chroma_persist_dir`: ChromaDB storage path
  - `salience_threshold`: 0.35 (below this → discard)
  - `novelty_weight`, `emotion_weight`, `frequency_weight`: Salience formula weights
  - `base_stability`: 24.0 hours (default memory lifetime)
  - `reinforcement_boost`: 1.8x (stability multiplier on recall)
  - `consolidation_trigger`: 10 (memories before consolidation)
  - `consolidation_cluster_min`: 3 (min memories per cluster)
  - `working_memory_turns`: 6 (last N turns)
  - `episodic_top_k`: 4, `semantic_top_k`: 3 (retrieval limits)

### Data Models

**`models.py`** (71 lines)
- Pydantic models for type safety and validation
- `MemoryInput`: Raw input to store (text, session_id, role, metadata)
- `EpisodicMemory`: Stored episode with decay tracking (id, text, salience, stability, recall_count, last_recalled, consolidated)
- `SemanticMemory`: Compressed knowledge (id, text, source_ids, importance)
- `ChatMessage`, `ChatRequest`, `ChatResponse`: Chat endpoint models
- `MemoryStats`: Session statistics (counts, averages, age)
- `RecallRequest`: Search query model

### Memory Storage

**`memory_store.py`** (221 lines)
- ChromaDB wrapper managing two collections:
  - `episodic_memories`: Raw events with decay metadata
  - `semantic_memories`: Consolidated long-term summaries
- SentenceTransformer encoder for embeddings (all-MiniLM-L6-v2)
- CRUD operations for both memory types
- Search by embedding with session filtering
- Metadata updates (recall_count, stability, last_recalled)
- Consolidation marking

### Core Algorithms

**`salience.py`** (160 lines)
- `compute_salience()`: Main scoring function
- `_compute_novelty()`: Cosine distance from recent memories
- `_compute_emotion_weight()`: Pattern-based keyword detection
  - High salience patterns: important, critical, urgent, deadline, meeting, hate, love, project, error, etc.
  - Low salience patterns: ok, yes, hi, thanks, bye, very short responses
- `_compute_frequency_bonus()`: Boost for recurring themes
- `_is_trivial()`: Hard override for boring inputs

**`forgetting.py`** (107 lines)
- `current_strength()`: Ebbinghaus decay calculation
- `reinforce()`: Boost stability on recall (spaced repetition)
- `get_decayed_ids()`: Find memories below 10% strength
- `rank_by_strength()`: Sort by current strength
- `compute_composite_score()`: Weighted sum of relevance (50%), strength (30%), recency (20%)

**`consolidation.py`** (146 lines)
- `should_consolidate()`: Check if threshold reached
- `run_consolidation()`: Main consolidation pipeline
  - Embed unconsolidated memories
  - Cluster using AgglomerativeClustering (cosine, distance_threshold=0.4)
  - Summarize each cluster with Claude
  - Store as SemanticMemory
  - Mark sources as consolidated
- `_cluster_memories()`: Agglomerative clustering logic
- `_summarize_cluster()`: Claude API call for summarization

**`retrieval.py`** (143 lines)
- `_working_memory`: In-memory deque per session (last 6 turns)
- `push_working_memory()`: Add turn to sliding window
- `get_working_memory()`: Retrieve current conversation
- `retrieve_context()`: Assemble memory-enriched context
  - Fetch semantic memories (top-K)
  - Fetch episodic memories (top-K × 2)
  - Re-rank episodic by composite score
  - Reinforce retrieved memories
  - Format context block
- `_score_episodic()`: Re-rank by composite score
- `build_system_prompt()`: Inject context into system prompt

**`replay.py`** (347 lines)
- `ReplayBuffer` class: Reservoir sampling implementation
- SQLite storage: `replay_buffer.db` in chroma_persist_dir
- `add()`: Weighted reservoir sampling (salience boost)
- `sample()`: Draw n samples (stratified by task_tag)
- `export_jsonl()`: Export as JSONL for LoRA fine-tuning
  - Pairs user/assistant turns
  - Format: `{"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}`
- `record_performance()`: Track metrics before/after fine-tuning
- `detect_forgetting()`: Compare current vs baseline, alert if >15% drop
- `stats()`: Buffer statistics (size, fill %, avg salience, by task)

### Testing & Benchmarking

**`lamb_bench.py`** (404 lines)
- Novel evaluation suite for memory systems
- **Suite 1**: Salience precision/recall
  - Test fixtures: SHOULD_STORE (8 important), SHOULD_DISCARD (11 trivial)
  - Metrics: precision, recall, F1-score
- **Suite 2**: Forgetting curve correctness
  - Test cases: fresh, 1h old, 12h old, 48h old, low salience
  - Reinforcement boost test
- **Suite 3**: Consolidation quality
  - Test cluster: 4 related memories about FastAPI/ChromaDB/LAMB
  - Expected keywords: fastapi, chromadb, lamb, memory, episodic, semantic
  - Checks: keyword coverage (≥60%), no hallucination
- **Suite 4**: Retrieval relevance
  - Query/retrieval pairs with expected results
  - Metric: cosine similarity ≥ 0.75
- `run_full_benchmark()`: Run all suites, return JSON report
- `print_report()`: Human-readable summary

**`test_lamb.py`** (133 lines)
- Smoke tests for core functionality
- Tests salience scoring, forgetting curve, memory storage/retrieval
- No Anthropic API key required
- Quick validation before deployment

---

## 🔑 Key Concepts Explained

### Salience Score
**Why**: LLMs store everything, including "ok" and "thanks", wasting context and degrading retrieval.

**How**: Weighted sum of three factors:
- **Novelty (50%)**: How different is this from recent memories? Computed as `1 - max_similarity` to recent memories.
- **Emotion (30%)**: Pattern-based detection of important keywords using regex.
- **Frequency (20%)**: Boost for recurring themes (topics mentioned before).

**Threshold**: Default 0.35. Below this → memory discarded.

### Forgetting Curve
**Why**: Human memories decay over time unless recalled. LLMs should too.

**How**: Ebbinghaus formula: `strength(t) = salience × e^(-hours_elapsed / stability)`

- **Stability**: How long memory lasts (default: 24 hours)
- **Reinforcement**: Each recall multiplies stability by 1.8x (spaced repetition)
- **Pruning**: Memories below 10% strength are deleted

**Example**: A memory with salience=0.8, stability=24h:
- Fresh: strength = 0.8
- After 24h: strength = 0.8 × e^(-1) = 0.29
- After recall: stability = 24 × 1.8 = 43.2h, strength boosted

### Consolidation
**Why**: Raw episodes pile up without compression. Humans consolidate during sleep.

**How**:
1. Every 10 new episodic memories → trigger consolidation
2. Cluster memories by semantic similarity (AgglomerativeClustering)
3. For each cluster with ≥3 members → Claude summarizes into 1-3 sentences
4. Store as SemanticMemory with source IDs
5. Mark source episodic as consolidated (excluded from search)

**Example**: Cluster of 4 memories about FastAPI backend → "User is building a FastAPI backend for LAMB using ChromaDB for vector storage."

### Composite Retrieval Score
**Why**: Pure semantic similarity isn't enough. Need to consider memory health.

**How**: `score = 0.5 × relevance + 0.3 × strength + 0.2 × recency`

- **Relevance**: Cosine similarity from ChromaDB search
- **Strength**: Current forgetting curve strength
- **Recency**: Exponential decay over 72 hours

**Example**: A memory with relevance=0.9, strength=0.6, recency=0.8 → score = 0.5×0.9 + 0.3×0.6 + 0.2×0.8 = 0.77

### Replay Buffer
**Why**: Fine-tuning LLMs on new tasks causes catastrophic forgetting of old tasks.

**How**:
- Fixed-size reservoir (500 samples) with statistical coverage
- Weighted sampling: high-salience memories over-represented
- Export as JSONL for LoRA fine-tuning
- Track performance metrics, alert if >15% drop

**Algorithm R (Vitter 1985)**: Guarantees each sample has equal probability of retention, regardless of stream length.

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.11+
- Anthropic API key (for chat and consolidation)

### Installation

```bash
# 1. Clone or navigate to project
cd lamb

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# 5. Run smoke test (no API key needed)
python test_lamb.py

# 6. Start server
uvicorn main:app --reload --port 8000
```

### Environment Variables

Create `.env` file:
```env
ANTHROPIC_API_KEY=sk-ant-...
```

Optional (override defaults in `config.py`):
```env
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHROMA_PERSIST_DIR=./chroma_db
SALIENCE_THRESHOLD=0.35
BASE_STABILITY=24.0
REINFORCEMENT_BOOST=1.8
CONSOLIDATION_TRIGGER=10
WORKING_MEMORY_TURNS=6
```

---

## 📡 API Reference

### POST /remember
Store a memory with salience filtering.

**Request**:
```json
{
  "text": "User is building a FastAPI memory system",
  "session_id": "shakeel",
  "role": "user",
  "metadata": {"task": "general"}
}
```

**Response** (stored):
```json
{
  "stored": true,
  "memory_id": "abc-123",
  "salience": 0.72
}
```

**Response** (discarded):
```json
{
  "stored": false,
  "reason": "below salience threshold",
  "salience": 0.28
}
```

### POST /recall
Semantic search across episodic + semantic memories.

**Request**:
```json
{
  "query": "What is the user working on?",
  "session_id": "shakeel",
  "top_k": 5
}
```

**Response**:
```json
{
  "episodic": [
    {
      "id": "mem-1",
      "text": "User is building a FastAPI memory system",
      "role": "user",
      "salience": 0.72,
      "strength": 0.65,
      "recall_count": 3,
      "age_hours": 12.4
    }
  ],
  "semantic": [
    {
      "id": "sem-1",
      "text": "User is building LAMB, a persistent memory system for LLMs",
      "importance": 0.68,
      "source_count": 4
    }
  ]
}
```

### POST /chat
Full chat with memory injection.

**Request**:
```json
{
  "message": "What should I work on today?",
  "session_id": "shakeel",
  "system_prompt": "You are a helpful assistant."
}
```

**Response**:
```json
{
  "reply": "Based on your LAMB project, you should focus on...",
  "memories_used": ["mem-1", "mem-2"],
  "context_tokens_estimate": 340
}
```

### POST /consolidate/{session_id}
Manually trigger episodic → semantic consolidation.

**Response**:
```json
{
  "semantic_memories_created": 2,
  "session_id": "shakeel"
}
```

### GET /stats/{session_id}
Memory statistics for a session.

**Response**:
```json
{
  "session_id": "shakeel",
  "episodic_count": 42,
  "semantic_count": 7,
  "consolidated_count": 35,
  "avg_salience": 0.61,
  "oldest_memory_hours": 18.4
}
```

### POST /prune/{session_id}
Delete decayed memories (strength < 10%).

**Response**:
```json
{
  "pruned": 5,
  "remaining": 37
}
```

### DELETE /session/{session_id}
Wipe all memories for a session.

**Response**:
```json
{
  "cleared": true,
  "episodic_deleted": 42,
  "semantic_deleted": 7
}
```

### GET /replay/stats
Replay buffer statistics.

**Response**:
```json
{
  "buffer_size": 500,
  "capacity": 500,
  "fill_pct": 85.2,
  "total_seen": 1250,
  "avg_salience": 0.67,
  "by_task": [
    {"task": "general", "count": 350, "avg_salience": 0.65},
    {"task": "coding", "count": 150, "avg_salience": 0.72}
  ]
}
```

### POST /replay/export
Export replay buffer as JSONL for LoRA fine-tuning.

**Request**:
```json
{
  "path": "./replay_training_data.jsonl",
  "task_tag": "general"
}
```

**Response**:
```json
{
  "exported_pairs": 125,
  "path": "./replay_training_data.jsonl"
}
```

### POST /benchmark
Run LAMB-Bench evaluation suite.

**Response**:
```json
{
  "lamb_bench_version": "1.0",
  "timestamp": "2026-07-29T12:00:00",
  "summary": {
    "total_suites": 4,
    "passed": 4,
    "failed": 0,
    "skipped": 0,
    "overall": "PASS"
  },
  "suites": {
    "salience": {...},
    "forgetting_curve": {...},
    "consolidation": {...},
    "retrieval": {...}
  }
}
```

### GET /health
Health check endpoint.

**Response**:
```json
{
  "status": "ok",
  "system": "LAMB v1.0"
}
```

---

## 🧪 Testing & Benchmarking

### Smoke Test
```bash
python test_lamb.py
```
Tests core functionality without Anthropic API key.

### Full Benchmark
```bash
curl -X POST http://localhost:8000/benchmark
```
Or via Python:
```python
import requests
response = requests.post("http://localhost:8000/benchmark")
print(response.json())
```

**Expected Output**:
```
=======================================================
  LAMB-Bench v1.0 — 2026-07-29
=======================================================
  Overall: PASS
  Passed:  4 / 4

  ✓ [PASS] SALIENCE
    F1=0.923  P=0.889  R=0.962
    8/8 important stored, 10/11 trivial discarded

  ✓ [PASS] FORGETTING_CURVE
    Decay tests: 5/5 passed
    Reinforce: True

  ✓ [PASS] CONSOLIDATION
    Coverage: 83%
    Keywords found: fastapi, chromadb, lamb, memory, episodic

  ✓ [PASS] RETRIEVAL
    Avg similarity: 0.891

=======================================================
```

---

## ⚙️ Configuration

All configuration is in `config.py` via Pydantic `BaseSettings`. Override with environment variables or `.env` file.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `anthropic_api_key` | "" | Claude API key (required for chat/consolidation) |
| `embedding_model` | "all-MiniLM-L6-v2" | SentenceTransformer model for embeddings |
| `chroma_persist_dir` | "./chroma_db" | ChromaDB storage path |
| `salience_threshold` | 0.35 | Below this → discard memory |
| `novelty_weight` | 0.5 | α in salience formula |
| `emotion_weight` | 0.3 | β in salience formula |
| `frequency_weight` | 0.2 | γ in salience formula |
| `base_stability` | 24.0 | Default memory lifetime (hours) |
| `reinforcement_boost` | 1.8 | Stability multiplier on recall |
| `consolidation_trigger` | 10 | Memories before consolidation |
| `consolidation_cluster_min` | 3 | Min memories per cluster |
| `working_memory_turns` | 6 | Last N turns in working memory |
| `episodic_top_k` | 4 | Top K episodic results |
| `semantic_top_k` | 3 | Top K semantic results |

---

## 📦 Dependencies

```
fastapi==0.111.0              # Web framework
uvicorn==0.30.1               # ASGI server
chromadb==0.5.0               # Vector database
sentence-transformers==3.0.1  # Embeddings
anthropic==0.28.0             # Claude API
pydantic==2.7.4               # Data validation
numpy==1.26.4                 # Numerical computing
scikit-learn==1.5.0           # Clustering
python-dotenv==1.0.1          # Environment variables
apscheduler==3.10.4           # Task scheduling
httpx==0.27.0                 # HTTP client
```

---

## 🎓 Use Cases

### 1. AGI Research
- Study memory mechanisms in LLMs
- Benchmark different memory architectures
- Test forgetting curve theories

### 2. SaaS Product
- Multi-tenant memory layer for AI applications
- Persistent context across sessions
- User personalization at scale

### 3. Personal Assistant
- Remember user preferences and goals
- Maintain conversation history
- Learn from interactions over time

### 4. Fine-Tuning Pipeline
- Replay buffer prevents catastrophic forgetting
- Export high-salience data for LoRA training
- Track performance metrics

---

## 🔮 Future Extensions

- **Multi-modal**: Store image embeddings (CLIP) alongside text
- **Cross-session**: Share semantic memories across sessions
- **Persona**: Build user profiles from semantic memories
- **Distributed**: Redis for working memory (horizontal scaling)
- **PostgreSQL**: Multi-tenancy with user/org models
- **Streaming**: Real-time memory updates via WebSocket

---

## 📝 License

This is a research project. Use for academic or commercial purposes with attribution.

---

## 🤝 Contributing

Contributions welcome! Areas of interest:
- New salience patterns
- Alternative clustering algorithms
- Additional benchmark suites
- Performance optimizations

---

## 📧 Contact

For questions about LAMB, open an issue or contact the maintainers.
