"""
FastAPI endpoints for the Memory Classification Engine.

This module provides REST API endpoints for memory classification,
configuration management, and system monitoring.
"""

import time
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from memory_classification.core.interfaces import MemoryInput
from memory_classification.core.engine import ClassificationEngine
from memory_classification.core.models import ClassificationConfig
from memory_classification.config.defaults import get_default_config
from memory_classification.registry.classifier_registry import get_global_classifier_registry
from memory_classification.registry.memory_type_registry import get_global_registry
from memory_classification.api.models import (
    ClassificationRequest,
    BatchClassificationRequest,
    ClassificationResponse,
    BatchClassificationResponse,
    ConfigUpdateRequest,
    ClassifierConfigUpdateRequest,
    HealthResponse,
    StatisticsResponse,
    MemoryTypeResponse,
    RegistryInfoResponse,
    ErrorResponse,
)

# Create router
router = APIRouter(prefix="/api/v1/classification", tags=["classification"])

# Global engine instance (will be initialized on startup)
_classification_engine: ClassificationEngine = None
_service_start_time = time.time()


def get_classification_engine() -> ClassificationEngine:
    """Get the global classification engine instance."""
    global _classification_engine
    if _classification_engine is None:
        _classification_engine = ClassificationEngine(config=get_default_config())
    return _classification_engine


def initialize_engine(engine: ClassificationEngine) -> None:
    """Initialize the global classification engine."""
    global _classification_engine
    _classification_engine = engine


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns the service status and component health.
    """
    uptime = time.time() - _service_start_time
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        uptime_seconds=uptime,
        components={
            "classification_engine": "healthy",
            "classifier_registry": "healthy",
            "memory_type_registry": "healthy",
        },
    )


@router.post("/classify", response_model=ClassificationResponse)
async def classify_memory(request: ClassificationRequest) -> ClassificationResponse:
    """
    Classify a single memory.
    
    Args:
        request: Classification request
        
    Returns:
        Classification response with memory object
    """
    start_time = time.perf_counter()
    
    try:
        engine = get_classification_engine()
        
        # Convert request to MemoryInput
        memory_input = MemoryInput(
            content=request.content,
            session_id=request.session_id,
            agent_id=request.agent_id,
            tenant_id=request.tenant_id,
            metadata=request.metadata,
        )
        
        # Classify
        memory_object = await engine.classify(
            memory_input,
            enable_routing=request.enable_routing,
        )
        
        computation_time_ms = (time.perf_counter() - start_time) * 1000
        
        return ClassificationResponse(
            success=True,
            memory_object=memory_object,
            computation_time_ms=computation_time_ms,
        )
        
    except Exception as e:
        computation_time_ms = (time.perf_counter() - start_time) * 1000
        return ClassificationResponse(
            success=False,
            memory_object=None,
            error=str(e),
            computation_time_ms=computation_time_ms,
        )


@router.post("/classify/batch", response_model=BatchClassificationResponse)
async def classify_batch(request: BatchClassificationRequest) -> BatchClassificationResponse:
    """
    Classify multiple memories in batch.
    
    Args:
        request: Batch classification request
        
    Returns:
        Batch classification response
    """
    start_time = time.perf_counter()
    
    try:
        engine = get_classification_engine()
        
        # Convert requests to MemoryInput objects
        memory_inputs = [
            MemoryInput(
                content=mem.content,
                session_id=mem.session_id,
                agent_id=mem.agent_id,
                tenant_id=mem.tenant_id,
                metadata=mem.metadata,
            )
            for mem in request.memories
        ]
        
        # Classify batch
        memory_objects = await engine.batch_classify(
            memory_inputs,
            enable_routing=request.enable_routing,
        )
        
        computation_time_ms = (time.perf_counter() - start_time) * 1000
        
        # Create individual responses
        results = [
            ClassificationResponse(
                success=True,
                memory_object=mem_obj,
                computation_time_ms=computation_time_ms / len(memory_objects),
            )
            for mem_obj in memory_objects
        ]
        
        return BatchClassificationResponse(
            success=True,
            results=results,
            total_count=len(request.memories),
            successful_count=len(memory_objects),
            failed_count=0,
            total_computation_time_ms=computation_time_ms,
        )
        
    except Exception as e:
        computation_time_ms = (time.perf_counter() - start_time) * 1000
        return BatchClassificationResponse(
            success=False,
            results=[],
            total_count=len(request.memories),
            successful_count=0,
            failed_count=len(request.memories),
            total_computation_time_ms=computation_time_ms,
        )


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics() -> StatisticsResponse:
    """
    Get classification statistics.
    
    Returns:
        Statistics response with classification metrics
    """
    try:
        engine = get_classification_engine()
        stats = engine.get_statistics()
        
        return StatisticsResponse(
            total_classifications=stats["total_classifications"],
            successful_classifications=stats["successful_classifications"],
            failed_classifications=stats["failed_classifications"],
            success_rate=stats["success_rate"],
            average_computation_time_ms=stats["average_computation_time_ms"],
            classifier_usage={k.value: v for k, v in stats["classifier_usage"].items()},
            classifier_registry_info=stats["classifier_registry_info"],
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}",
        )


@router.get("/config")
async def get_config() -> Dict[str, Any]:
    """
    Get current configuration.
    
    Returns:
        Current configuration dictionary
    """
    try:
        engine = get_classification_engine()
        config_dict = engine.config.dict()
        
        # Convert enum values to strings
        config_dict["classifier_configs"] = {
            k.value: v.dict() for k, v in config_dict["classifier_configs"].items()
        }
        
        return config_dict
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve configuration: {str(e)}",
        )


@router.put("/config")
async def update_config(request: ConfigUpdateRequest) -> Dict[str, Any]:
    """
    Update global configuration.
    
    Args:
        request: Configuration update request
        
    Returns:
        Updated configuration dictionary
    """
    try:
        engine = get_classification_engine()
        current_config = engine.config
        
        # Update only provided fields
        if request.enable_caching is not None:
            current_config.enable_caching = request.enable_caching
        if request.enable_telemetry is not None:
            current_config.enable_telemetry = request.enable_telemetry
        if request.enable_logging is not None:
            current_config.enable_logging = request.enable_logging
        if request.confidence_threshold is not None:
            current_config.confidence_threshold = request.confidence_threshold
        if request.max_concurrent_classifications is not None:
            current_config.max_concurrent_classifications = request.max_concurrent_classifications
        if request.batch_size is not None:
            current_config.batch_size = request.batch_size
        if request.enable_deduplication is not None:
            current_config.enable_deduplication = request.enable_deduplication
        if request.deduplication_similarity_threshold is not None:
            current_config.deduplication_similarity_threshold = request.deduplication_similarity_threshold
        
        # Convert to dict for response
        config_dict = current_config.dict()
        config_dict["classifier_configs"] = {
            k.value: v.dict() for k, v in config_dict["classifier_configs"].items()
        }
        
        return config_dict
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update configuration: {str(e)}",
        )


@router.get("/classifiers")
async def get_classifiers() -> List[str]:
    """
    Get list of registered classifiers.
    
    Returns:
        List of memory types with registered classifiers
    """
    try:
        registry = get_global_classifier_registry()
        memory_types = [mt.value for mt in registry.get_supported_memory_types()]
        return memory_types
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve classifiers: {str(e)}",
        )


@router.get("/classifiers/{memory_type}", response_model=MemoryTypeResponse)
async def get_classifier_config(memory_type: str) -> MemoryTypeResponse:
    """
    Get configuration for a specific classifier.
    
    Args:
        memory_type: Memory type identifier
        
    Returns:
        Classifier configuration
    """
    try:
        from memory_classification.core.types import MemoryType as MT
        
        mt_enum = MT(memory_type)
        engine = get_classification_engine()
        config = engine.config.get_classifier_config(mt_enum)
        
        return MemoryTypeResponse(
            memory_type=mt_enum,
            enabled=config.enabled,
            confidence_threshold=config.confidence_threshold,
            method=config.method,
            weight=config.weight,
            parameters=config.parameters,
        )
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid memory type: {memory_type}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve classifier config: {str(e)}",
        )


@router.put("/classifiers/{memory_type}")
async def update_classifier_config(memory_type: str, request: ClassifierConfigUpdateRequest) -> Dict[str, Any]:
    """
    Update configuration for a specific classifier.
    
    Args:
        memory_type: Memory type identifier
        request: Classifier configuration update request
        
    Returns:
        Updated classifier configuration
    """
    try:
        from memory_classification.core.types import MemoryType as MT
        
        mt_enum = MT(memory_type)
        engine = get_classification_engine()
        
        # Get current config
        current_config = engine.config.get_classifier_config(mt_enum)
        
        # Update only provided fields
        if request.enabled is not None:
            current_config.enabled = request.enabled
        if request.weight is not None:
            current_config.weight = request.weight
        if request.confidence_threshold is not None:
            current_config.confidence_threshold = request.confidence_threshold
        if request.method is not None:
            current_config.method = request.method
        if request.parameters is not None:
            current_config.parameters = request.parameters
        
        # Update engine config
        engine.config.set_classifier_config(mt_enum, current_config)
        
        return current_config.dict()
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid memory type: {memory_type}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update classifier config: {str(e)}",
        )


@router.post("/classifiers/{memory_type}/enable")
async def enable_classifier(memory_type: str) -> Dict[str, str]:
    """
    Enable a classifier.
    
    Args:
        memory_type: Memory type identifier
        
    Returns:
        Status message
    """
    try:
        from memory_classification.core.types import MemoryType as MT
        
        mt_enum = MT(memory_type)
        engine = get_classification_engine()
        engine.enable_classifier(mt_enum)
        
        return {"status": "enabled", "memory_type": memory_type}
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid memory type: {memory_type}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable classifier: {str(e)}",
        )


@router.post("/classifiers/{memory_type}/disable")
async def disable_classifier(memory_type: str) -> Dict[str, str]:
    """
    Disable a classifier.
    
    Args:
        memory_type: Memory type identifier
        
    Returns:
        Status message
    """
    try:
        from memory_classification.core.types import MemoryType as MT
        
        mt_enum = MT(memory_type)
        engine = get_classification_engine()
        engine.disable_classifier(mt_enum)
        
        return {"status": "disabled", "memory_type": memory_type}
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid memory type: {memory_type}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disable classifier: {str(e)}",
        )


@router.get("/registry/memory-types", response_model=RegistryInfoResponse)
async def get_memory_type_registry() -> RegistryInfoResponse:
    """
    Get memory type registry information.
    
    Returns:
        Memory type registry information
    """
    try:
        registry = get_global_registry()
        info = registry.get_registry_info()
        
        return RegistryInfoResponse(
            total_types=info["total_types"],
            types=info["types"],
            storage_policies=info["storage_policies"],
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve registry info: {str(e)}",
        )


@router.post("/statistics/reset")
async def reset_statistics() -> Dict[str, str]:
    """
    Reset classification statistics.
    
    Returns:
        Status message
    """
    try:
        engine = get_classification_engine()
        engine.reset_statistics()
        
        return {"status": "reset"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset statistics: {str(e)}",
        )
