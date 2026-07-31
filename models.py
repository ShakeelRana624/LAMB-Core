from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class MemoryInput(BaseModel):
    """Raw input to store as a memory."""
    text: str
    session_id: str = "default"
    role: str = "user"                      # user | assistant
    metadata: dict = Field(default_factory=dict)


class EpisodicMemory(BaseModel):
    """A single stored episode — raw event with decay tracking."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    session_id: str
    role: str
    timestamp: float = Field(default_factory=lambda: datetime.utcnow().timestamp())
    salience: float = 0.0
    stability: float = 24.0                 # hours before 50% decay
    recall_count: int = 0
    last_recalled: Optional[float] = None
    consolidated: bool = False              # has this been merged into semantic?
    metadata: dict = Field(default_factory=dict)


class SemanticMemory(BaseModel):
    """Compressed long-term knowledge — distilled from episodic clusters."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str                               # LLM-generated summary
    source_ids: list[str] = Field(default_factory=list)  # episodic IDs this came from
    session_id: str
    created_at: float = Field(default_factory=lambda: datetime.utcnow().timestamp())
    importance: float = 0.5                 # 0-1, higher = keep longer
    metadata: dict = Field(default_factory=dict)


class ChatMessage(BaseModel):
    role: str   # user | assistant | system
    content: str


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    system_prompt: str = "You are a helpful AI assistant with persistent memory."


class ChatResponse(BaseModel):
    reply: str
    memories_used: list[str]               # what memories were injected
    context_tokens_estimate: int


class MemoryStats(BaseModel):
    session_id: str
    episodic_count: int
    semantic_count: int
    consolidated_count: int
    avg_salience: float
    oldest_memory_hours: float


class RecallRequest(BaseModel):
    query: str
    session_id: str = "default"
    top_k: int = 5
