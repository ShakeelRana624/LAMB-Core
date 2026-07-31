from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str = ""

    # Embedding model (runs locally, no API key needed)
    embedding_model: str = "all-MiniLM-L6-v2"

    # ChromaDB
    chroma_persist_dir: str = "./chroma_db"

    # Salience thresholds
    salience_threshold: float = 0.35       # below this → discard memory
    novelty_weight: float = 0.5            # α
    emotion_weight: float = 0.3            # β
    frequency_weight: float = 0.2          # γ

    # Forgetting curve
    base_stability: float = 24.0           # hours — default memory lifetime
    reinforcement_boost: float = 1.8       # multiply stability on each recall

    # Consolidation
    consolidation_trigger: int = 10        # consolidate every N new episodic memories
    consolidation_cluster_min: int = 3     # min memories per cluster to summarize

    # Retrieval
    working_memory_turns: int = 6          # always include last N turns
    episodic_top_k: int = 4               # top K episodic results
    semantic_top_k: int = 3               # top K semantic results

    class Config:
        env_file = ".env"


settings = Settings()
BASE_DIR = Path(__file__).parent.parent
