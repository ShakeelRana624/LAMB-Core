"""
FastAPI endpoints for the Attention Engine.

This module provides REST API endpoints for attention computation,
configuration management, and statistics.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import asyncio

from attention.core.interfaces import AttentionContext, TemporalContext, SocialContext
from attention.core.models import AttentionVector, AttentionConfig, SignalConfig
from attention.core.engine import AttentionEngine
from attention.config.defaults import get_default_config


# Request/Response Models
class AttentionRequest(BaseModel):
    """Request model for attention computation."""
    input_text: str = Field(..., description="Input text to analyze")
    session_id: str = Field(..., description="Session identifier")
    agent_id: str = Field(..., description="Agent identifier")
    current_goal: Optional[str] = Field(None, description="Current agent goal")
    current_task: Optional[str] = Field(None, description="Current agent task")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AttentionResponse(BaseModel):
    """Response model for attention computation."""
    vector: AttentionVector
    should_store: bool
    computation_time_ms: float


class ConfigUpdateRequest(BaseModel):
    """Request model for configuration update."""
    aggregation_strategy: Optional[str] = None
    storage_threshold: Optional[float] = None
    enable_caching: Optional[bool] = None
    signal_configs: Optional[Dict[str, Dict[str, Any]]] = None


class StatisticsResponse(BaseModel):
    """Response model for statistics."""
    aggregator: Dict[str, Any]
    cache: Dict[str, Any]
    registered_signals: int
    enabled_signals: int
    config: Dict[str, Any]


# Router
router = APIRouter(prefix="/attention", tags=["attention"])

# Global engine instance (in production, use dependency injection)
_engine: Optional[AttentionEngine] = None


def get_engine() -> AttentionEngine:
    """Dependency injection for the attention engine."""
    global _engine
    if _engine is None:
        _engine = AttentionEngine(get_default_config())
    return _engine


@router.post("/compute", response_model=AttentionResponse)
async def compute_attention(
    request: AttentionRequest,
    engine: AttentionEngine = Depends(get_engine),
) -> AttentionResponse:
    """
    Compute attention for a given input.
    
    This endpoint computes the attention vector for the input text,
    including all signal scores and the final aggregated score.
    """
    try:
        # Create attention context
        temporal_context = TemporalContext()
        social_context = SocialContext()
        
        context = AttentionContext(
            input_text=request.input_text,
            session_id=request.session_id,
            agent_id=request.agent_id,
            current_goal=request.current_goal,
            current_task=request.current_task,
            temporal_context=temporal_context,
            social_context=social_context,
            metadata=request.metadata,
        )
        
        # Compute attention
        vector = await engine.compute_attention(context)
        
        return AttentionResponse(
            vector=vector,
            should_store=vector.should_store,
            computation_time_ms=vector.computation_time_ms,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals", response_model=list[str])
async def list_signals(
    engine: AttentionEngine = Depends(get_engine),
) -> list[str]:
    """
    List all registered attention signals.
    
    Returns a list of signal names that are currently registered.
    """
    return engine.list_signals()


@router.get("/config", response_model=AttentionConfig)
async def get_config(
    engine: AttentionEngine = Depends(get_engine),
) -> AttentionConfig:
    """
    Get the current attention engine configuration.
    
    Returns the complete configuration including all signal configs.
    """
    return engine.config


@router.post("/config")
async def update_config(
    request: ConfigUpdateRequest,
    engine: AttentionEngine = Depends(get_engine),
) -> Dict[str, str]:
    """
    Update the attention engine configuration.
    
    Allows updating global configuration and individual signal configs.
    """
    try:
        # Create new config from current
        new_config = engine.config.copy()
        
        # Update global settings
        if request.aggregation_strategy:
            new_config.aggregation_strategy = request.aggregation_strategy
        if request.storage_threshold is not None:
            new_config.storage_threshold = request.storage_threshold
        if request.enable_caching is not None:
            new_config.enable_caching = request.enable_caching
        
        # Update signal configs
        if request.signal_configs:
            for signal_name, signal_config_dict in request.signal_configs.items():
                signal_config = SignalConfig(**signal_config_dict)
                new_config.set_signal_config(signal_name, signal_config)
        
        # Apply new config
        engine.update_config(new_config)
        
        return {"status": "success", "message": "Configuration updated"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(
    engine: AttentionEngine = Depends(get_engine),
) -> StatisticsResponse:
    """
    Get attention engine statistics.
    
    Returns statistics including aggregation performance,
    cache stats, and signal counts.
    """
    stats = engine.get_statistics()
    return StatisticsResponse(**stats)


@router.post("/signals/{signal_name}/enable")
async def enable_signal(
    signal_name: str,
    engine: AttentionEngine = Depends(get_engine),
) -> Dict[str, str]:
    """
    Enable a specific attention signal.
    
    Enables the specified signal so it participates in aggregation.
    """
    try:
        signal = engine.get_signal(signal_name)
        signal.enable()
        return {"status": "success", "message": f"Signal '{signal_name}' enabled"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/signals/{signal_name}/disable")
async def disable_signal(
    signal_name: str,
    engine: AttentionEngine = Depends(get_engine),
) -> Dict[str, str]:
    """
    Disable a specific attention signal.
    
    Disables the specified signal so it does not participate in aggregation.
    """
    try:
        signal = engine.get_signal(signal_name)
        signal.disable()
        return {"status": "success", "message": f"Signal '{signal_name}' disabled"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns the health status of the attention engine.
    """
    return {"status": "healthy", "service": "lamb-attention"}
