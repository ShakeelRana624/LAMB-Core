"""
Type definitions and enums for the Memory Classification Engine.

This module defines the core types used throughout the classification system.
"""

from enum import Enum


class MemoryType(str, Enum):
    """
    Enumeration of all cognitive memory types.
    
    Each memory type represents a distinct category of cognitive memory
    based on neuroscience and cognitive psychology research.
    """
    
    # Identity-related memories
    IDENTITY_MEMORY = "identity_memory"
    
    # Goal-related memories
    GOAL_MEMORY = "goal_memory"
    
    # Preference-related memories
    PREFERENCE_MEMORY = "preference_memory"
    
    # Relationship-related memories
    RELATIONSHIP_MEMORY = "relationship_memory"
    
    # Project-related memories
    PROJECT_MEMORY = "project_memory"
    
    # Skill-related memories
    SKILL_MEMORY = "skill_memory"
    
    # Procedural memories (how-to knowledge)
    PROCEDURAL_MEMORY = "procedural_memory"
    
    # Task-related memories
    TASK_MEMORY = "task_memory"
    
    # Episodic memories (specific events)
    EPISODIC_MEMORY = "episodic_memory"
    
    # Semantic memories (general knowledge)
    SEMANTIC_MEMORY = "semantic_memory"
    
    # Emotional memories
    EMOTIONAL_MEMORY = "emotional_memory"
    
    # Temporal memories (time-related)
    TEMPORAL_MEMORY = "temporal_memory"
    
    def __str__(self) -> str:
        """Return string representation."""
        return self.value
    
    @classmethod
    def get_all_types(cls) -> list["MemoryType"]:
        """Return all memory types."""
        return list(cls)
    
    @classmethod
    def get_core_types(cls) -> list["MemoryType"]:
        """Return core memory types (most commonly used)."""
        return [
            cls.EPISODIC_MEMORY,
            cls.SEMANTIC_MEMORY,
            cls.GOAL_MEMORY,
            cls.TASK_MEMORY,
        ]
    
    @classmethod
    def get_secondary_types(cls) -> list["MemoryType"]:
        """Return secondary memory types."""
        return [
            cls.IDENTITY_MEMORY,
            cls.PREFERENCE_MEMORY,
            cls.RELATIONSHIP_MEMORY,
            cls.PROJECT_MEMORY,
            cls.SKILL_MEMORY,
        ]
    
    @classmethod
    def get_specialized_types(cls) -> list["MemoryType"]:
        """Return specialized memory types."""
        return [
            cls.PROCEDURAL_MEMORY,
            cls.EMOTIONAL_MEMORY,
            cls.TEMPORAL_MEMORY,
        ]


class ClassificationMethod(str, Enum):
    """
    Enumeration of classification methods.
    
    Different methods can be used for classification, from simple
    rule-based approaches to complex ML models.
    """
    
    RULE_BASED = "rule_based"
    EMBEDDING_BASED = "embedding_based"
    LLM_BASED = "llm_based"
    ML_BASED = "ml_based"
    HYBRID = "hybrid"
    
    def __str__(self) -> str:
        """Return string representation."""
        return self.value


class StoragePolicy(str, Enum):
    """
    Enumeration of storage policies for memory types.
    
    Different memory types may require different storage strategies
    based on access patterns, retention requirements, and importance.
    """
    
    # Standard storage with default retention
    STANDARD = "standard"
    
    # Long-term storage with extended retention
    LONG_TERM = "long_term"
    
    # Short-term storage with automatic expiration
    SHORT_TERM = "short_term"
    
    # Hot storage for frequently accessed memories
    HOT = "hot"
    
    # Cold storage for archival purposes
    COLD = "cold"
    
    # No storage (transient only)
    TRANSIENT = "transient"
    
    def __str__(self) -> str:
        """Return string representation."""
        return self.value
