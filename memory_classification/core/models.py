"""
Pydantic models for the Memory Classification Engine.

This module defines the data models used throughout the classification system,
ensuring type safety, validation, and serialization.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import uuid4
from enum import Enum

from pydantic import BaseModel, Field, validator

from memory_classification.core.types import MemoryType, ClassificationMethod, StoragePolicy
from memory_classification.core.exceptions import ValidationError


class MemoryInputModel(BaseModel):
    """
    Pydantic model for memory input.
    
    This model validates and structures memory input data before classification.
    """
    
    content: str = Field(..., min_length=1, description="The memory content to classify")
    session_id: str = Field(..., min_length=1, description="Session identifier")
    agent_id: str = Field(..., min_length=1, description="Agent identifier")
    tenant_id: str = Field(..., min_length=1, description="Tenant identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: float = Field(default_factory=lambda: datetime.utcnow().timestamp(), description="Timestamp")
    
    @validator('content')
    def content_not_empty(cls, v):
        """Validate that content is not empty or whitespace."""
        if not v.strip():
            raise ValueError("Content cannot be empty or whitespace")
        return v
    
    @validator('session_id', 'agent_id', 'tenant_id')
    def id_not_empty(cls, v):
        """Validate that IDs are not empty."""
        if not v.strip():
            raise ValueError("ID cannot be empty")
        return v
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class ClassificationResultModel(BaseModel):
    """
    Pydantic model for classification result.
    
    This model structures the output of memory classification with validation.
    """
    
    memory_types: List[MemoryType] = Field(default_factory=list, description="Classified memory types")
    confidence_scores: Dict[MemoryType, float] = Field(default_factory=dict, description="Confidence scores per type")
    reasoning: Dict[MemoryType, str] = Field(default_factory=dict, description="Reasoning per type")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    computation_time_ms: float = Field(default=0.0, ge=0.0, description="Computation time in milliseconds")
    classifier_method: ClassificationMethod = Field(default=ClassificationMethod.RULE_BASED, description="Classification method used")
    
    @validator('confidence_scores')
    def confidence_scores_valid(cls, v, values):
        """Validate that confidence scores are between 0 and 1."""
        for memory_type, score in v.items():
            if not 0.0 <= score <= 1.0:
                raise ValueError(f"Confidence score for {memory_type} must be between 0.0 and 1.0")
        return v
    
    @validator('memory_types')
    def memory_types_in_confidence_scores(cls, v, values):
        """Validate that all memory types have confidence scores."""
        if 'confidence_scores' in values:
            confidence_scores = values['confidence_scores']
            for memory_type in v:
                if memory_type not in confidence_scores:
                    raise ValueError(f"Memory type {memory_type} missing from confidence scores")
        return v
    
    def get_highest_confidence_type(self) -> Optional[MemoryType]:
        """Return the memory type with highest confidence score."""
        if not self.confidence_scores:
            return None
        return max(self.confidence_scores.items(), key=lambda x: x[1])[0]
    
    def get_confidence_for_type(self, memory_type: MemoryType) -> float:
        """Return confidence score for a specific memory type."""
        return self.confidence_scores.get(memory_type, 0.0)
    
    def get_reasoning_for_type(self, memory_type: MemoryType) -> str:
        """Return reasoning for a specific memory type."""
        return self.reasoning.get(memory_type, "")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class UniversalMemoryObject(BaseModel):
    """
    Universal Memory Object - the canonical representation of a classified memory.
    
    This object serves as the universal format for all memories in the system,
    enabling consistent storage, retrieval, and processing across different
    memory types and storage backends.
    """
    
    # Core identification
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique memory identifier")
    content: str = Field(..., min_length=1, description="Memory content")
    
    # Classification results
    memory_types: List[MemoryType] = Field(default_factory=list, description="Classified memory types")
    confidence_scores: Dict[MemoryType, float] = Field(default_factory=dict, description="Confidence scores per type")
    reasoning: Dict[MemoryType, str] = Field(default_factory=dict, description="Reasoning per type")
    
    # Context information
    tenant_id: str = Field(..., min_length=1, description="Tenant identifier")
    session_id: str = Field(..., min_length=1, description="Session identifier")
    agent_id: str = Field(..., min_length=1, description="Agent identifier")
    
    # Metadata and indexing
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    tags: List[str] = Field(default_factory=list, description="Tags for indexing")
    
    # Temporal information
    timestamp: float = Field(default_factory=lambda: datetime.utcnow().timestamp(), description="Creation timestamp")
    last_accessed: float = Field(default_factory=lambda: datetime.utcnow().timestamp(), description="Last access timestamp")
    
    # Attention information (optional)
    attention_vector: Optional[Dict[str, Any]] = Field(default=None, description="Attention vector from Attention Engine")
    
    # Storage information
    storage_policy: StoragePolicy = Field(default=StoragePolicy.STANDARD, description="Storage policy")
    storage_locations: List[str] = Field(default_factory=list, description="Storage locations where memory is stored")
    
    # Classification metadata
    classifier_method: ClassificationMethod = Field(default=ClassificationMethod.RULE_BASED, description="Classification method used")
    classification_metadata: Dict[str, Any] = Field(default_factory=dict, description="Classification-specific metadata")
    
    @validator('content')
    def content_not_empty(cls, v):
        """Validate that content is not empty or whitespace."""
        if not v.strip():
            raise ValueError("Content cannot be empty or whitespace")
        return v
    
    @validator('confidence_scores')
    def confidence_scores_valid(cls, v):
        """Validate that confidence scores are between 0 and 1."""
        for memory_type, score in v.items():
            if not 0.0 <= score <= 1.0:
                raise ValueError(f"Confidence score for {memory_type} must be between 0.0 and 1.0")
        return v
    
    @validator('memory_types')
    def memory_types_in_confidence_scores(cls, v, values):
        """Validate that all memory types have confidence scores."""
        if 'confidence_scores' in values:
            confidence_scores = values['confidence_scores']
            for memory_type in v:
                if memory_type not in confidence_scores:
                    raise ValueError(f"Memory type {memory_type} missing from confidence scores")
        return v
    
    def has_memory_type(self, memory_type: MemoryType) -> bool:
        """Check if memory has a specific type."""
        return memory_type in self.memory_types
    
    def get_confidence_for_type(self, memory_type: MemoryType) -> float:
        """Return confidence score for a specific memory type."""
        return self.confidence_scores.get(memory_type, 0.0)
    
    def get_reasoning_for_type(self, memory_type: MemoryType) -> str:
        """Return reasoning for a specific memory type."""
        return self.reasoning.get(memory_type, "")
    
    def get_highest_confidence_type(self) -> Optional[MemoryType]:
        """Return the memory type with highest confidence score."""
        if not self.confidence_scores:
            return None
        return max(self.confidence_scores.items(), key=lambda x: x[1])[0]
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the memory."""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the memory."""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def update_last_accessed(self) -> None:
        """Update the last accessed timestamp."""
        self.last_accessed = datetime.utcnow().timestamp()
    
    def to_storage_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "content": self.content,
            "memory_types": [mt.value for mt in self.memory_types],
            "confidence_scores": {mt.value: score for mt, score in self.confidence_scores.items()},
            "reasoning": {mt.value: reason for mt, reason in self.reasoning.items()},
            "tenant_id": self.tenant_id,
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "metadata": self.metadata,
            "tags": self.tags,
            "timestamp": self.timestamp,
            "last_accessed": self.last_accessed,
            "attention_vector": self.attention_vector,
            "storage_policy": self.storage_policy.value,
            "storage_locations": self.storage_locations,
            "classifier_method": self.classifier_method.value,
            "classification_metadata": self.classification_metadata,
        }
    
    @classmethod
    def from_storage_dict(cls, data: Dict[str, Any]) -> "UniversalMemoryObject":
        """Create instance from storage dictionary."""
        # Convert enum values back to enums
        memory_types = [MemoryType(mt) for mt in data.get("memory_types", [])]
        confidence_scores = {
            MemoryType(mt): score 
            for mt, score in data.get("confidence_scores", {}).items()
        }
        reasoning = {
            MemoryType(mt): reason 
            for mt, reason in data.get("reasoning", {}).items()
        }
        storage_policy = StoragePolicy(data.get("storage_policy", "standard"))
        classifier_method = ClassificationMethod(data.get("classifier_method", "rule_based"))
        
        return cls(
            id=data.get("id"),
            content=data.get("content"),
            memory_types=memory_types,
            confidence_scores=confidence_scores,
            reasoning=reasoning,
            tenant_id=data.get("tenant_id"),
            session_id=data.get("session_id"),
            agent_id=data.get("agent_id"),
            metadata=data.get("metadata", {}),
            tags=data.get("tags", []),
            timestamp=data.get("timestamp"),
            last_accessed=data.get("last_accessed"),
            attention_vector=data.get("attention_vector"),
            storage_policy=storage_policy,
            storage_locations=data.get("storage_locations", []),
            classifier_method=classifier_method,
            classification_metadata=data.get("classification_metadata", {}),
        )
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = False
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class ClassifierConfig(BaseModel):
    """
    Configuration for a specific classifier.
    
    This model defines the configuration parameters for individual
    memory type classifiers.
    """
    
    enabled: bool = Field(default=True, description="Whether the classifier is enabled")
    weight: float = Field(default=1.0, ge=0.0, le=10.0, description="Classifier weight in aggregation")
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")
    method: ClassificationMethod = Field(default=ClassificationMethod.RULE_BASED, description="Classification method")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Classifier-specific parameters")
    
    @validator('weight')
    def weight_valid(cls, v):
        """Validate weight is non-negative."""
        if v < 0:
            raise ValueError("Weight must be non-negative")
        return v
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class ClassificationConfig(BaseModel):
    """
    Global configuration for the Memory Classification Engine.
    
    This model defines the overall configuration parameters for the
    classification system.
    """
    
    # Feature flags
    enable_caching: bool = Field(default=True, description="Enable result caching")
    enable_telemetry: bool = Field(default=True, description="Enable OpenTelemetry tracing")
    enable_logging: bool = Field(default=True, description="Enable structured logging")
    
    # Performance parameters
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Global confidence threshold")
    max_concurrent_classifications: int = Field(default=100, ge=1, description="Maximum concurrent classifications")
    batch_size: int = Field(default=50, ge=1, description="Default batch size for batch classification")
    
    # Classifier configurations
    classifier_configs: Dict[MemoryType, ClassifierConfig] = Field(
        default_factory=dict,
        description="Per-classifier configurations"
    )
    
    # Storage parameters
    enable_deduplication: bool = Field(default=True, description="Enable memory deduplication")
    deduplication_similarity_threshold: float = Field(default=0.95, ge=0.0, le=1.0, description="Similarity threshold for deduplication")
    
    # Multi-tenant parameters
    enable_multi_tenancy: bool = Field(default=True, description="Enable multi-tenancy support")
    tenant_isolation_level: str = Field(default="strict", description="Tenant isolation level")
    
    @validator('confidence_threshold')
    def confidence_threshold_valid(cls, v):
        """Validate confidence threshold is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")
        return v
    
    @validator('deduplication_similarity_threshold')
    def deduplication_threshold_valid(cls, v):
        """Validate deduplication threshold is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Deduplication similarity threshold must be between 0.0 and 1.0")
        return v
    
    def get_classifier_config(self, memory_type: MemoryType) -> ClassifierConfig:
        """Get configuration for a specific classifier."""
        return self.classifier_configs.get(memory_type, ClassifierConfig())
    
    def set_classifier_config(self, memory_type: MemoryType, config: ClassifierConfig) -> None:
        """Set configuration for a specific classifier."""
        self.classifier_configs[memory_type] = config
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class StorageLocation(BaseModel):
    """
    Model representing a storage location.
    
    This model describes where a memory is stored, including the
    backend type, location identifier, and access parameters.
    """
    
    backend_type: str = Field(..., description="Type of storage backend")
    location_id: str = Field(..., description="Location identifier")
    access_parameters: Dict[str, Any] = Field(default_factory=dict, description="Access parameters")
    created_at: float = Field(default_factory=lambda: datetime.utcnow().timestamp(), description="Creation timestamp")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class TypeDefinition(BaseModel):
    """
    Definition of a memory type.
    
    This model defines the schema, validation rules, and storage policy
    for a specific memory type.
    """
    
    memory_type: MemoryType = Field(..., description="The memory type")
    schema_definition: Dict[str, Any] = Field(default_factory=dict, description="Schema definition")
    validation_rules: List[str] = Field(default_factory=list, description="Validation rule names")
    storage_policy: StoragePolicy = Field(default=StoragePolicy.STANDARD, description="Storage policy")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
