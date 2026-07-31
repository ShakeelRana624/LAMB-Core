"""
Default configuration for the Memory Classification Engine.

This module provides default configuration values for the classification
system, including classifier-specific settings and global parameters.
"""

from memory_classification.core.types import MemoryType, ClassificationMethod, StoragePolicy
from memory_classification.core.models import ClassificationConfig, ClassifierConfig


def get_default_config() -> ClassificationConfig:
    """
    Get the default classification configuration.
    
    Returns:
        Default ClassificationConfig instance
    """
    return ClassificationConfig(
        # Feature flags
        enable_caching=True,
        enable_telemetry=True,
        enable_logging=True,
        
        # Performance parameters
        confidence_threshold=0.5,
        max_concurrent_classifications=100,
        batch_size=50,
        
        # Storage parameters
        enable_deduplication=True,
        deduplication_similarity_threshold=0.95,
        
        # Multi-tenant parameters
        enable_multi_tenancy=True,
        tenant_isolation_level="strict",
        
        # Classifier configurations
        classifier_configs={
            # Core memory types
            MemoryType.EPISODIC_MEMORY: ClassifierConfig(
                enabled=True,
                weight=1.0,
                confidence_threshold=0.5,
                method=ClassificationMethod.RULE_BASED,
                parameters={"enable_temporal_detection": True},
            ),
            MemoryType.SEMANTIC_MEMORY: ClassifierConfig(
                enabled=True,
                weight=1.0,
                confidence_threshold=0.5,
                method=ClassificationMethod.RULE_BASED,
                parameters={"enable_domain_detection": True},
            ),
            MemoryType.GOAL_MEMORY: ClassifierConfig(
                enabled=True,
                weight=1.0,
                confidence_threshold=0.5,
                method=ClassificationMethod.RULE_BASED,
                parameters={"enable_priority_detection": True},
            ),
            MemoryType.TASK_MEMORY: ClassifierConfig(
                enabled=True,
                weight=1.0,
                confidence_threshold=0.5,
                method=ClassificationMethod.RULE_BASED,
                parameters={"_enable_deadline_detection": True},
            ),
            
            # Secondary memory types
            MemoryType.IDENTITY_MEMORY: ClassifierConfig(
                enabled=True,
                weight=0.8,
                confidence_threshold=0.6,
                method=ClassificationMethod.RULE_BASED,
                parameters={"enable_attribute_extraction": True},
            ),
            MemoryType.PREFERENCE_MEMORY: ClassifierConfig(
                enabled=True,
                weight=0.8,
                confidence_threshold=0.5,
                method=ClassificationMethod.RULE_BASED,
                parameters={"enable_sentiment_detection": True},
            ),
            MemoryType.RELATIONSHIP_MEMORY: ClassifierConfig(
                enabled=True,
                weight=0.8,
                confidence_threshold=0.5,
                method=ClassificationMethod.RULE_BASED,
                parameters={"enable_entity_extraction": True},
            ),
            MemoryType.PROJECT_MEMORY: ClassifierConfig(
                enabled=True,
                weight=0.8,
                confidence_threshold=0.5,
                method=ClassificationMethod.RULE_BASED,
                parameters={"enable_status_detection": True},
            ),
            MemoryType.SKILL_MEMORY: ClassifierConfig(
                enabled=True,
                weight=0.8,
                confidence_threshold=0.5,
                method=ClassificationMethod.RULE_BASED,
                parameters={"enable_level_detection": True},
            ),
            
            # Specialized memory types
            MemoryType.PROCEDURAL_MEMORY: ClassifierConfig(
                enabled=True,
                weight=0.7,
                confidence_threshold=0.5,
                method=ClassificationMethod.RULE_BASED,
                parameters={"enable_step_detection": True},
            ),
            MemoryType.EMOTIONAL_MEMORY: ClassifierConfig(
                enabled=True,
                weight=0.7,
                confidence_threshold=0.5,
                method=ClassificationMethod.RULE_BASED,
                parameters={"enable_intensity_detection": True},
            ),
            MemoryType.TEMPORAL_MEMORY: ClassifierConfig(
                enabled=True,
                weight=0.7,
                confidence_threshold=0.5,
                method=ClassificationMethod.RULE_BASED,
                parameters={"enable_duration_detection": True},
            ),
        },
    )


def get_minimal_config() -> ClassificationConfig:
    """
    Get a minimal configuration for testing or lightweight usage.
    
    Returns:
        Minimal ClassificationConfig instance
    """
    return ClassificationConfig(
        # Feature flags
        enable_caching=False,
        enable_telemetry=False,
        enable_logging=False,
        
        # Performance parameters
        confidence_threshold=0.5,
        max_concurrent_classifications=10,
        batch_size=10,
        
        # Storage parameters
        enable_deduplication=False,
        deduplication_similarity_threshold=0.95,
        
        # Multi-tenant parameters
        enable_multi_tenancy=False,
        tenant_isolation_level="none",
        
        # Classifier configurations (only core types enabled)
        classifier_configs={
            MemoryType.EPISODIC_MEMORY: ClassifierConfig(
                enabled=True,
                weight=1.0,
                confidence_threshold=0.5,
                method=ClassificationMethod.RULE_BASED,
            ),
            MemoryType.SEMANTIC_MEMORY: ClassifierConfig(
                enabled=True,
                weight=1.0,
                confidence_threshold=0.5,
                method=ClassificationMethod.RULE_BASED,
            ),
        },
    )


def get_high_performance_config() -> ClassificationConfig:
    """
    Get a high-performance configuration for production use.
    
    Returns:
        High-performance ClassificationConfig instance
    """
    return ClassificationConfig(
        # Feature flags
        enable_caching=True,
        enable_telemetry=True,
        enable_logging=True,
        
        # Performance parameters
        confidence_threshold=0.5,
        max_concurrent_classifications=500,
        batch_size=100,
        
        # Storage parameters
        enable_deduplication=True,
        deduplication_similarity_threshold=0.95,
        
        # Multi-tenant parameters
        enable_multi_tenancy=True,
        tenant_isolation_level="strict",
        
        # Classifier configurations (all enabled with optimized settings)
        classifier_configs={
            memory_type: ClassifierConfig(
                enabled=True,
                weight=1.0,
                confidence_threshold=0.5,
                method=ClassificationMethod.RULE_BASED,
            )
            for memory_type in MemoryType
        },
    )


def get_development_config() -> ClassificationConfig:
    """
    Get a development configuration with verbose logging and debugging.
    
    Returns:
        Development ClassificationConfig instance
    """
    return ClassificationConfig(
        # Feature flags
        enable_caching=False,
        enable_telemetry=False,
        enable_logging=True,
        
        # Performance parameters
        confidence_threshold=0.3,  # Lower threshold for testing
        max_concurrent_classifications=20,
        batch_size=20,
        
        # Storage parameters
        enable_deduplication=False,
        deduplication_similarity_threshold=0.95,
        
        # Multi-tenant parameters
        enable_multi_tenancy=False,
        tenant_isolation_level="none",
        
        # Classifier configurations (all enabled)
        classifier_configs={
            memory_type: ClassifierConfig(
                enabled=True,
                weight=1.0,
                confidence_threshold=0.3,  # Lower threshold for testing
                method=ClassificationMethod.RULE_BASED,
            )
            for memory_type in MemoryType
        },
    )
