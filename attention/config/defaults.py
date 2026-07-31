"""
Default configuration for the Attention Engine.

This module provides default configurations for all attention signals
and global settings, ensuring the system works out-of-the-box.
"""

from attention.core.models import AttentionConfig, SignalConfig
from attention.core.types import SignalName


def get_default_config() -> AttentionConfig:
    """
    Get the default attention engine configuration.
    
    Returns:
        AttentionConfig with default values
    """
    # Default signal configurations
    signal_configs = {
        SignalName.NOVELTY.value: SignalConfig(
            enabled=True,
            weight=0.15,
            threshold=0.0,
            parameters={
                "recent_memory_count": 10,
                "embedding_model": "all-MiniLM-L6-v2",
            },
        ),
        SignalName.GOAL_RELEVANCE.value: SignalConfig(
            enabled=True,
            weight=0.12,
            threshold=0.0,
            parameters={
                "primary_goal_weight": 1.0,
                "secondary_goal_weight": 0.7,
                "tertiary_goal_weight": 0.4,
            },
        ),
        SignalName.URGENCY.value: SignalConfig(
            enabled=True,
            weight=0.10,
            threshold=0.0,
            parameters={
                "enable_temporal_extraction": True,
            },
        ),
        SignalName.REWARD.value: SignalConfig(
            enabled=True,
            weight=0.08,
            threshold=0.0,
            parameters={
                "enable_sentiment_analysis": True,
            },
        ),
        SignalName.RISK.value: SignalConfig(
            enabled=True,
            weight=0.10,
            threshold=0.0,
            parameters={
                "enable_sentiment_analysis": True,
            },
        ),
        SignalName.EMOTION.value: SignalConfig(
            enabled=True,
            weight=0.07,
            threshold=0.0,
            parameters={
                "enable_intensity_detection": True,
            },
        ),
        SignalName.CURIOSITY.value: SignalConfig(
            enabled=True,
            weight=0.05,
            threshold=0.0,
            parameters={},
        ),
        SignalName.SURPRISE.value: SignalConfig(
            enabled=True,
            weight=0.06,
            threshold=0.0,
            parameters={
                "enable_bayesian_surprise": True,
                "history_window": 10,
            },
        ),
        SignalName.CONFIDENCE.value: SignalConfig(
            enabled=True,
            weight=0.04,
            threshold=0.0,
            parameters={},
        ),
        SignalName.FUTURE_UTILITY.value: SignalConfig(
            enabled=True,
            weight=0.08,
            threshold=0.0,
            parameters={},
        ),
        SignalName.SOCIAL_IMPORTANCE.value: SignalConfig(
            enabled=True,
            weight=0.05,
            threshold=0.0,
            parameters={
                "enable_entity_recognition": True,
            },
        ),
        SignalName.REPETITION.value: SignalConfig(
            enabled=True,
            weight=0.06,
            threshold=0.0,
            parameters={
                "frequency_window": 20,
            },
        ),
        SignalName.CURRENT_TASK_MATCH.value: SignalConfig(
            enabled=True,
            weight=0.09,
            threshold=0.0,
            parameters={
                "embedding_model": "all-MiniLM-L6-v2",
            },
        ),
    }
    
    # Global configuration
    return AttentionConfig(
        signals=signal_configs,
        aggregation_strategy="weighted_sum",
        storage_threshold=0.5,
        enable_caching=True,
        cache_ttl_seconds=300,
        parallel_execution=True,
        max_concurrent_signals=13,
        enable_telemetry=True,
        enable_logging=True,
        log_level="INFO",
        log_computation_times=True,
        enable_ml_signals=False,
        enable_external_services=False,
    )
