"""
memory_store.py
ChromaDB wrapper managing two collections:
  - episodic_memories : raw events with decay metadata
  - semantic_memories : consolidated long-term summaries
"""
import json
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from typing import Optional
from datetime import datetime

from .config import settings
from .models import EpisodicMemory, SemanticMemory


class MemoryStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.encoder = SentenceTransformer(settings.embedding_model)

        # Two separate collections
        self.episodic = self.client.get_or_create_collection(
            name="episodic_memories",
            metadata={"hnsw:space": "cosine"},
        )
        self.semantic = self.client.get_or_create_collection(
            name="semantic_memories",
            metadata={"hnsw:space": "cosine"},
        )

    # ------------------------------------------------------------------ #
    #  Encoding                                                            #
    # ------------------------------------------------------------------ #

    def encode(self, text: str) -> list[float]:
        return self.encoder.encode(text, normalize_embeddings=True).tolist()

    def encode_batch(self, texts: list[str]) -> list[list[float]]:
        return self.encoder.encode(texts, normalize_embeddings=True).tolist()

    # ------------------------------------------------------------------ #
    #  Episodic CRUD                                                       #
    # ------------------------------------------------------------------ #

    def add_episodic(self, memory: EpisodicMemory) -> None:
        embedding = self.encode(memory.text)
        self.episodic.add(
            ids=[memory.id],
            embeddings=[embedding],
            documents=[memory.text],
            metadatas=[{
                "session_id": memory.session_id,
                "role": memory.role,
                "timestamp": memory.timestamp,
                "salience": memory.salience,
                "stability": memory.stability,
                "recall_count": memory.recall_count,
                "last_recalled": memory.last_recalled or 0.0,
                "consolidated": int(memory.consolidated),
                "metadata_json": json.dumps(memory.metadata),
            }],
        )

    def get_episodic(self, memory_id: str) -> Optional[EpisodicMemory]:
        result = self.episodic.get(ids=[memory_id], include=["documents", "metadatas"])
        if not result["ids"]:
            return None
        return self._row_to_episodic(
            memory_id, result["documents"][0], result["metadatas"][0]
        )

    def update_episodic_meta(self, memory_id: str, updates: dict) -> None:
        """Update only metadata fields (e.g. recall_count, stability)."""
        self.episodic.update(ids=[memory_id], metadatas=[updates])

    def search_episodic(
        self,
        query_embedding: list[float],
        session_id: str,
        top_k: int = 5,
        exclude_consolidated: bool = False,
    ) -> list[EpisodicMemory]:
        where: dict = {"session_id": session_id}
        if exclude_consolidated:
            where["consolidated"] = 0

        results = self.episodic.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self._count_episodic(session_id)),
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        memories = []
        for i, mid in enumerate(results["ids"][0]):
            mem = self._row_to_episodic(
                mid, results["documents"][0][i], results["metadatas"][0][i]
            )
            memories.append(mem)
        return memories

    def get_all_episodic(self, session_id: str, only_unconsolidated: bool = False) -> list[EpisodicMemory]:
        where: dict = {"session_id": session_id}
        if only_unconsolidated:
            where["consolidated"] = 0

        results = self.episodic.get(
            where=where,
            include=["documents", "metadatas"],
        )
        memories = []
        for i, mid in enumerate(results["ids"]):
            mem = self._row_to_episodic(
                mid, results["documents"][i], results["metadatas"][i]
            )
            memories.append(mem)
        return sorted(memories, key=lambda m: m.timestamp)

    def mark_consolidated(self, ids: list[str]) -> None:
        for mid in ids:
            self.episodic.update(ids=[mid], metadatas=[{"consolidated": 1}])

    def delete_episodic(self, ids: list[str]) -> None:
        self.episodic.delete(ids=ids)

    def _count_episodic(self, session_id: str) -> int:
        result = self.episodic.get(where={"session_id": session_id}, include=[])
        return len(result["ids"])

    # ------------------------------------------------------------------ #
    #  Semantic CRUD                                                        #
    # ------------------------------------------------------------------ #

    def add_semantic(self, memory: SemanticMemory) -> None:
        embedding = self.encode(memory.text)
        self.semantic.add(
            ids=[memory.id],
            embeddings=[embedding],
            documents=[memory.text],
            metadatas=[{
                "session_id": memory.session_id,
                "source_ids": json.dumps(memory.source_ids),
                "created_at": memory.created_at,
                "importance": memory.importance,
                "metadata_json": json.dumps(memory.metadata),
            }],
        )

    def search_semantic(
        self,
        query_embedding: list[float],
        session_id: str,
        top_k: int = 3,
    ) -> list[SemanticMemory]:
        count = self._count_semantic(session_id)
        if count == 0:
            return []
        results = self.semantic.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, count),
            where={"session_id": session_id},
            include=["documents", "metadatas"],
        )
        memories = []
        for i, mid in enumerate(results["ids"][0]):
            mem = self._row_to_semantic(
                mid, results["documents"][0][i], results["metadatas"][0][i]
            )
            memories.append(mem)
        return memories

    def get_all_semantic(self, session_id: str) -> list[SemanticMemory]:
        results = self.semantic.get(
            where={"session_id": session_id},
            include=["documents", "metadatas"],
        )
        return [
            self._row_to_semantic(mid, doc, meta)
            for mid, doc, meta in zip(
                results["ids"], results["documents"], results["metadatas"]
            )
        ]

    def _count_semantic(self, session_id: str) -> int:
        result = self.semantic.get(where={"session_id": session_id}, include=[])
        return len(result["ids"])

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _row_to_episodic(self, mid: str, doc: str, meta: dict) -> EpisodicMemory:
        return EpisodicMemory(
            id=mid,
            text=doc,
            session_id=meta["session_id"],
            role=meta["role"],
            timestamp=meta["timestamp"],
            salience=meta.get("salience", 0.0),
            stability=meta.get("stability", 24.0),
            recall_count=meta.get("recall_count", 0),
            last_recalled=meta.get("last_recalled") or None,
            consolidated=bool(meta.get("consolidated", 0)),
            metadata=json.loads(meta.get("metadata_json", "{}")),
        )

    def _row_to_semantic(self, mid: str, doc: str, meta: dict) -> SemanticMemory:
        return SemanticMemory(
            id=mid,
            text=doc,
            session_id=meta["session_id"],
            source_ids=json.loads(meta.get("source_ids", "[]")),
            created_at=meta.get("created_at", datetime.utcnow().timestamp()),
            importance=meta.get("importance", 0.5),
            metadata=json.loads(meta.get("metadata_json", "{}")),
        )
