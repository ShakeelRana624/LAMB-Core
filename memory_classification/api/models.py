"""
API request/response models for the Memory Classification Engine.

This module defines Pydantic models for API requests and responses,
ensuring type safety and validation for the REST API.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from memory_classification.core.types import MemoryType, ClassificationMethod, StoragePolicy
from memory_classification.core.models import (
    MemoryInputModel,
    ClassificationResultModel,
    UniversalMemoryObject,
    ClassifierConfig,
    ClassificationConfig,
)


class ClassificationRequest(BaseModel):
    """Request model for memory classification."""
    
    content: str = Field(..., min_length=1, description="Memory content to classify")
    session_id: str = Field(..., min_length=1, description="Session identifier")
    agent_id: str = Field(..., min_length=1, description="Agent identifier")
    tenant_id: str = Field(..., min_length=1, description="Tenant identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    enable_routing: bool = Field(default=False, description="Whether to route to storage")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class BatchClassificationRequest(BaseModel):
    """Request model for batch memory classification."""
    
    memories: List[ClassificationRequest] = Field(..., min_length=1, description="Memories to classify")
    enable_routing: bool = Field(default=False, description="Whether to route to storage")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class ClassificationResponse(BaseModel):
    """Response model for memory classification."""
    
    success: bool = Field(..., description="Whether classification was successful")
    memory_object: Optional[UniversalMemoryObject] = Field(None, description="Classified memory object")
    error: Optional[str] = Field(None, description="Error message if failed")
    computation_time_ms: float = Field(..., description="Computation time in milliseconds")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class BatchClassificationResponse(BaseModel):
    """Response model for batch memory classification."""
    
    success: bool = Field(..., description="Whether batch classification was successful")
    results: List[ClassificationResponse] = Field(..., description="Individual classification results")
    total_count: int = Field(..., description="Total number of memories processed")
    successful_count: int = Field(..., description="Number of successful classifications")
    failed_count: int = Field(..., description="Number of failed classifications")
    total_computation_time_ms: float = Field(..., description="Total computation time")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class ConfigUpdateRequest(BaseModel):
    """Request model for configuration updates."""
    
    enable_caching: Optional[bool] = Field(None, description="Enable result caching")
    enable_telemetry: Optional[bool] = Field(None, description="Enable OpenTelemetry tracing")
    enable_logging: Optional[bool] = Field(None, description="Enable structured logging")
    confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Global confidence threshold")
    max_concurrent_classifications: Optional[int] = Field(None, ge=1, description="Maximum concurrent classifications")
    batch_size: Optional[int] = Field(None, ge=1, description="Default batch size")
    enable_deduplication: Optional[bool] = Field(None, description="Enable memory deduplication")
    deduplication_similarity_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Deduplication similarity threshold")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class ClassifierConfigUpdateRequest(BaseModel):
    """Request model for classifier-specific configuration updates."""
    
    memory_type: MemoryType = Field(..., description="Memory type to configure")
    enabled: Optional[bool] = Field(None, description="Whether the classifier is enabled")
    weight: Optional[float] = Field(None, ge=0.0, le=10.0, description="Classifier weight")
    confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Classifier confidence threshold")
    method: Optional[ClassificationMethod] = Field(None, description="Classification method")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Classifier-specific parameters")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class HealthResponse(BaseModel):
    """Response model for health check."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    components: Dict[str, str] = Field(..., description="Component status")
    
    class Config:
        """Pydantic configuration."""


class StatisticsResponse(BaseModel):
    """Response model for classification statistics."""
    
    total_classifications: int = Field(..., description="Total classifications performed")
    successful_classifications: int = Field(..., description="Successful classifications")
    failed_classifications: int = Field(..., description="Failed classifications")
    success_rate: float = Field(..., description="Success rate (0.0 to 1.0)")
    average_computation_time_ms: float = Field(..., description="Average computation time in milliseconds")
    classifier_usage: Dict[str, int] = Field(..., description="Classifier usage counts")
    classifier_registry_info: Dict[str, Any] = Field(..., description="Classifier registry information")
    
    class Config:
        """Pydantic configuration."""


class MemoryTypeResponse(BaseModel):
    """Response model for memory type information."""
    
    memory_type: MemoryType = Field(..., description="Memory type")
    enabled: bool = Field(..., description="Whether classifier is enabled")
    confidence_threshold: float = Field(..., description="Confidence threshold")
    method: ClassificationMethod = Field(..., description="Classification method")
    weight: float = Field(..., description="Classifier weight")
    parameters: Dict[str, Any] = Field(..., description="Classifier parameters")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class RegistryInfoResponse(BaseModel):
    """Response model for registry information."""
    
    total_types: int = Field(..., description="Total registered memory types")
    types: List[str] = Field(..., description="List of memory types")
    storage_policies: Dict[str, str] = Field(..., description="Storage policies per type")
    
    class Config:
        """Pydantic configuration."""


class ErrorResponse(BaseModel):
    """Response model for errors."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional error details")
    
    class Config:
        """Pydantic configuration."""
