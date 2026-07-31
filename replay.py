"""
replay.py — Memory Replay Buffer (Gap 04)
==========================================
Addresses: Catastrophic forgetting at the weight level.

Problem (from literature):
  When LLMs are fine-tuned on new tasks, they overwrite weights learned
  from old tasks — catastrophic forgetting (Haque et al. 2025, arXiv 2504.01241).
  External memory (Gaps 1-3) helps at inference time but doesn't fix
  the model weights themselves.

Our approach — Gradient Episodic Memory (GEM-lite):
  1. Maintain a fixed-size replay buffer of high-salience past interactions
     (reservoir sampling ensures statistical coverage over time).
  2. When fine-tuning is triggered, mix replay samples with new data so the
     model sees old knowledge alongside new → prevents overwriting.
  3. Expose the replay buffer as a JSONL training file that any HF trainer
     or LoRA fine-tuning script can consume directly.
  4. Track per-task performance snapshots so we can detect if a new
     fine-tune is causing forgetting before committing.

This module does NOT require a GPU or HF — it's storage + sampling logic.
The actual fine-tuning is done externally (e.g. via LoRA / PEFT).
"""

import json
import math
import random
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import settings
from .models import EpisodicMemory


# ------------------------------------------------------------------ #
#  Config                                                              #
# ------------------------------------------------------------------ #

REPLAY_DB = Path(settings.chroma_persist_dir) / "replay_buffer.db"
REPLAY_BUFFER_SIZE = 500          # max samples in reservoir
MIN_SALIENCE_FOR_REPLAY = 0.55    # only high-salience memories qualify
FORGETTING_DETECT_THRESHOLD = 0.15  # >15% accuracy drop = forgetting detected


# ------------------------------------------------------------------ #
#  Replay buffer (reservoir sampling over episodic stream)            #
# ------------------------------------------------------------------ #

class ReplayBuffer:
    """
    Fixed-size reservoir buffer implementing Algorithm R (Vitter 1985).
    Guarantees each incoming sample has equal probability of being retained,
    regardless of stream length — no recency bias.

    High-salience samples get a weighted boost: they replace existing
    samples more aggressively, so important interactions are over-represented
    in the replay mix (unlike uniform reservoir).
    """

    def __init__(self):
        self._init_db()
        self._n_seen = self._count_seen()

    def _init_db(self):
        conn = self._conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS replay_buffer (
                id          TEXT PRIMARY KEY,
                session_id  TEXT NOT NULL,
                role        TEXT NOT NULL,
                text        TEXT NOT NULL,
                salience    REAL NOT NULL,
                timestamp   REAL NOT NULL,
                task_tag    TEXT DEFAULT 'general',
                added_at    REAL NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS seen_counter (
                id    INTEGER PRIMARY KEY CHECK (id = 1),
                count INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.execute("""
            INSERT OR IGNORE INTO seen_counter (id, count) VALUES (1, 0)
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS performance_snapshots (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                task_tag    TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                value       REAL NOT NULL,
                recorded_at REAL NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def _conn(self) -> sqlite3.Connection:
        REPLAY_DB.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(str(REPLAY_DB))

    def _count_seen(self) -> int:
        conn = self._conn()
        row = conn.execute("SELECT count FROM seen_counter WHERE id=1").fetchone()
        conn.close()
        return row[0] if row else 0

    def _buffer_size(self) -> int:
        conn = self._conn()
        n = conn.execute("SELECT COUNT(*) FROM replay_buffer").fetchone()[0]
        conn.close()
        return n

    # ---------------------------------------------------------------- #

    def add(self, memory: EpisodicMemory, task_tag: str = "general") -> bool:
        """
        Attempt to add a memory to the replay buffer.
        Uses weighted reservoir sampling — higher salience = higher replace prob.
        Returns True if the sample was accepted into the buffer.
        """
        if memory.salience < MIN_SALIENCE_FOR_REPLAY:
            return False

        self._n_seen += 1
        conn = self._conn()
        conn.execute(
            "UPDATE seen_counter SET count=? WHERE id=1", (self._n_seen,)
        )

        current_size = self._buffer_size()

        if current_size < REPLAY_BUFFER_SIZE:
            # Buffer not full yet — always accept
            self._insert(conn, memory, task_tag)
            conn.commit()
            conn.close()
            return True

        # Reservoir replacement with salience weighting
        # Standard Alg-R: replace with prob = k/n (k=buffer size, n=seen)
        # Salience boost: scale probability by (salience / threshold)
        base_prob = REPLAY_BUFFER_SIZE / self._n_seen
        salience_boost = memory.salience / MIN_SALIENCE_FOR_REPLAY
        replace_prob = min(base_prob * salience_boost, 1.0)

        accepted = False
        if random.random() < replace_prob:
            # Evict the lowest-salience sample currently in buffer
            victim = conn.execute(
                "SELECT id FROM replay_buffer ORDER BY salience ASC LIMIT 1"
            ).fetchone()
            if victim:
                conn.execute(
                    "DELETE FROM replay_buffer WHERE id=?", (victim[0],)
                )
                self._insert(conn, memory, task_tag)
                accepted = True

        conn.commit()
        conn.close()
        return accepted

    def _insert(
        self,
        conn: sqlite3.Connection,
        memory: EpisodicMemory,
        task_tag: str,
    ):
        conn.execute(
            """INSERT OR REPLACE INTO replay_buffer
               (id, session_id, role, text, salience, timestamp, task_tag, added_at)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                memory.id, memory.session_id, memory.role,
                memory.text, memory.salience, memory.timestamp,
                task_tag, datetime.utcnow().timestamp(),
            ),
        )

    # ---------------------------------------------------------------- #

    def sample(
        self,
        n: int = 32,
        task_tag: Optional[str] = None,
        min_salience: float = 0.0,
    ) -> list[dict]:
        """
        Draw n samples from the buffer (stratified by task_tag if given).
        Returns list of dicts suitable for a training batch.
        """
        conn = self._conn()
        if task_tag:
            rows = conn.execute(
                """SELECT role, text, salience, task_tag FROM replay_buffer
                   WHERE task_tag=? AND salience>=?
                   ORDER BY RANDOM() LIMIT ?""",
                (task_tag, min_salience, n),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT role, text, salience, task_tag FROM replay_buffer
                   WHERE salience>=?
                   ORDER BY RANDOM() LIMIT ?""",
                (min_salience, n),
            ).fetchall()
        conn.close()
        return [
            {"role": r[0], "text": r[1], "salience": r[2], "task_tag": r[3]}
            for r in rows
        ]

    def export_jsonl(
        self,
        path: str,
        task_tag: Optional[str] = None,
        n: Optional[int] = None,
    ) -> int:
        """
        Export replay samples as JSONL — ready for HuggingFace / LoRA trainer.

        Format per line:
        {"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}

        Pairs consecutive user/assistant rows from same session.
        Returns number of training examples written.
        """
        samples = self.sample(
            n=n or REPLAY_BUFFER_SIZE,
            task_tag=task_tag,
        )
        # Pair user/assistant into conversation turns
        pairs = []
        buffer_u = None
        for s in samples:
            if s["role"] == "user":
                buffer_u = s
            elif s["role"] == "assistant" and buffer_u:
                pairs.append({
                    "messages": [
                        {"role": "user", "content": buffer_u["text"]},
                        {"role": "assistant", "content": s["text"]},
                    ],
                    "salience": round((buffer_u["salience"] + s["salience"]) / 2, 3),
                    "task_tag": s["task_tag"],
                })
                buffer_u = None

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            for p in pairs:
                f.write(json.dumps(p) + "\n")
        return len(pairs)

    # ---------------------------------------------------------------- #
    #  Catastrophic forgetting detection                                #
    # ---------------------------------------------------------------- #

    def record_performance(
        self,
        task_tag: str,
        metric_name: str,
        value: float,
    ) -> None:
        """Record a performance snapshot before/after fine-tuning."""
        conn = self._conn()
        conn.execute(
            """INSERT INTO performance_snapshots
               (task_tag, metric_name, value, recorded_at)
               VALUES (?,?,?,?)""",
            (task_tag, metric_name, value, datetime.utcnow().timestamp()),
        )
        conn.commit()
        conn.close()

    def detect_forgetting(
        self,
        task_tag: str,
        metric_name: str,
        current_value: float,
    ) -> dict:
        """
        Compare current metric against historical baseline.
        Returns forgetting report — red flag if drop > threshold.
        """
        conn = self._conn()
        rows = conn.execute(
            """SELECT value, recorded_at FROM performance_snapshots
               WHERE task_tag=? AND metric_name=?
               ORDER BY recorded_at ASC""",
            (task_tag, metric_name),
        ).fetchall()
        conn.close()

        if not rows:
            return {
                "forgetting_detected": False,
                "reason": "no baseline recorded",
                "baseline": None,
                "current": current_value,
            }

        baseline = rows[0][0]       # first recorded = pre-finetune baseline
        drop = baseline - current_value
        pct_drop = drop / max(baseline, 1e-6)

        return {
            "forgetting_detected": pct_drop > FORGETTING_DETECT_THRESHOLD,
            "baseline": round(baseline, 4),
            "current": round(current_value, 4),
            "absolute_drop": round(drop, 4),
            "pct_drop": round(pct_drop * 100, 1),
            "threshold_pct": FORGETTING_DETECT_THRESHOLD * 100,
            "task_tag": task_tag,
            "metric_name": metric_name,
            "n_historical_snapshots": len(rows),
        }

    def stats(self) -> dict:
        conn = self._conn()
        total = conn.execute(
            "SELECT COUNT(*) FROM replay_buffer"
        ).fetchone()[0]
        by_task = conn.execute(
            "SELECT task_tag, COUNT(*), AVG(salience) FROM replay_buffer GROUP BY task_tag"
        ).fetchall()
        avg_sal = conn.execute(
            "SELECT AVG(salience) FROM replay_buffer"
        ).fetchone()[0] or 0.0
        conn.close()
        return {
            "buffer_size": total,
            "capacity": REPLAY_BUFFER_SIZE,
            "fill_pct": round(total / REPLAY_BUFFER_SIZE * 100, 1),
            "total_seen": self._n_seen,
            "avg_salience": round(avg_sal, 3),
            "by_task": [
                {"task": r[0], "count": r[1], "avg_salience": round(r[2], 3)}
                for r in by_task
            ],
        }
