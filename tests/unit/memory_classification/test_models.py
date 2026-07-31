"""
Unit tests for Pydantic models.

This module contains comprehensive unit tests for the Pydantic models
used in the Memory Classification Engine.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from memory_classification.core.types import MemoryType, ClassificationMethod, StoragePolicy
from memory_classification.core.models import (
    MemoryInputModel,
    ClassificationResultModel,
    UniversalMemoryObject,
    ClassifierConfig,
    ClassificationConfig,
    TypeDefinition,
)


class TestMemoryInputModel:
    """Tests for MemoryInputModel."""
    
    def test_valid_memory_input(self):
        """Test creation of valid memory input."""
        memory_input = MemoryInputModel(
            content="Test content",
            session_id="test-session",
            agent_id="test-agent",
            tenant_id="test-tenant",
        )
        
        assert memory_input.content == "Test content"
        assert memory_input.session_id == "test-session"
        assert memory_input.agent_id == "test-agent"
        assert memory_input.tenant_id == "test-tenant"
        assert memory_input.metadata == {}
    
    def test_empty_content_raises_error(self):
        """Test that empty content raises validation error."""
        with pytest.raises(ValidationError):
            MemoryInputModel(
                content="",
                session_id="test-session",
                agent_id="test-agent",
                tenant_id="test-tenant",
            )
    
    def test_whitespace_content_raises_error(self):
        """Test that whitespace-only content raises validation error."""
        with pytest.raises(ValidationError):
            MemoryInputModel(
                content="   ",
                session_id="test-session",
                agent_id="test-agent",
                tenant_id="test-tenant",
            )
    
    def test_empty_session_id_raises_error(self):
        """Test that empty session ID raises validation error."""
        with pytest.raises(ValidationError):
            MemoryInputModel(
                content="Test content",
                session_id="",
                agent_id="test-agent",
                tenant_id="test-tenant",
            )
    
    def test_with_metadata(self):
        """Test memory input with metadata."""
        memory_input = MemoryInputModel(
            content="Test content",
            session_id="test-session",
            agent_id="test-agent",
            tenant_id="test-tenant",
            metadata={"key": "value"},
        )
        
        assert memory_input.metadata == {"key": "value"}


class TestClassificationResultModel:
    """Tests for ClassificationResultModel."""
    
    def test_valid_classification_result(self):
        """Test creation of valid classification result."""
        result = ClassificationResultModel(
            memory_types=[MemoryType.IDENTITY_MEMORY],
            confidence_scores={MemoryType.IDENTITY_MEMORY: 0.8},
            reasoning={MemoryType.IDENTITY_MEMORY: "Identity detected"},
        )
        
        assert MemoryType.IDENTITY_MEMORY in result.memory_types
        assert result.confidence_scores[MemoryType.IDENTITY_MEMORY] == 0.8
        assert result.reasoning[MemoryType.IDENTITY_MEMORY] == "Identity detected"
    
    def test_invalid_confidence_score_raises_error(self):
        """Test that confidence score outside [0,1] raises error."""
        with pytest.raises(ValidationError):
            ClassificationResultModel(
                memory_types=[MemoryType.IDENTITY_MEMORY],
                confidence_scores={MemoryType.IDENTITY_MEMORY: 1.5},
                reasoning={MemoryType.IDENTITY_MEMORY: "Identity detected"},
            )
    
    def test_memory_type_not_in_confidence_scores_raises_error(self):
        """Test that memory type not in confidence scores raises error."""
        with pytest.raises(ValidationError):
            ClassificationResultModel(
                memory_types=[MemoryType.IDENTITY_MEMORY],
                confidence_scores={},
                reasoning={MemoryType.IDENTITY_MEMORY: "Identity detected"},
            )
    
    def test_get_highest_confidence_type(self):
        """Test getting highest confidence type."""
        result = ClassificationResultModel(
            memory_types=[MemoryType.IDENTITY_MEMORY, MemoryType.GOAL_MEMORY],
            confidence_scores={
                MemoryType.IDENTITY_MEMORY: 0.7,
                MemoryType.GOAL_MEMORY: 0.9,
            },
            reasoning={
                MemoryType.IDENTITY_MEMORY: "Identity detected",
                MemoryType.GOAL_MEMORY: "Goal detected",
            },
        )
        
        highest = result.get_highest_confidence_type()
        assert highest == MemoryType.GOAL_MEMORY
    
    def test_get_confidence_for_type(self):
        """Test getting confidence for specific type."""
        result = ClassificationResultModel(
            memory_types=[MemoryType.IDENTITY_MEMORY],
            confidence_scores={MemoryType.IDENTITY_MEMORY: 0.8},
            reasoning={MemoryType.IDENTITY_MEMORY: "Identity detected"},
        )
        
        confidence = result.get_confidence_for_type(MemoryType.IDENTITY_MEMORY)
        assert confidence == 0.8
    
    def test_get_confidence_for_nonexistent_type(self):
        """Test getting confidence for nonexistent type."""
        result = ClassificationResultModel(
            memory_types=[MemoryType.IDENTITY_MEMORY],
            confidence_scores={MemoryType.IDENTITY_MEMORY: 0.8},
            reasoning={MemoryType.IDENTITY_MEMORY: "Identity detected"},
        )
        
        confidence = result.get_confidence_for_type(MemoryType.GOAL_MEMORY)
        assert confidence == 0.0


class TestUniversalMemoryObject:
    """Tests for UniversalMemoryObject."""
    
    def test_valid_memory_object(self):
        """Test creation of valid memory object."""
        memory_object = UniversalMemoryObject(
            content="Test content",
            memory_types=[MemoryType.IDENTITY_MEMORY],
            confidence_scores={MemoryType.IDENTITY_MEMORY: 0.8},
            reasoning={MemoryType.IDENTITY_MEMORY: "Identity detected"},
            tenant_id="test-tenant",
            session_id="test-session",
            agent_id="test-agent",
        )
        
        assert memory_object.content == "Test content"
        assert MemoryType.IDENTITY_MEMORY in memory_object.memory_types
        assert memory_object.tenant_id == "test-tenant"
    
    def test_empty_content_raises_error(self):
        """Test that empty content raises validation error."""
        with pytest.raises(ValidationError):
            UniversalMemoryObject(
                content="",
                memory_types=[],
                confidence_scores={},
                reasoning={},
                tenant_id="test-tenant",
                session_id="test-session",
                agent_id="test-agent",
            )
    
    def test_invalid_confidence_scores_raises_error(self):
        """Test that invalid confidence scores raise error."""
        with pytest.raises(ValidationError):
            UniversalMemoryObject(
                content="Test content",
                memory_types=[MemoryType.IDENTITY_MEMORY],
                confidence_scores={MemoryType.IDENTITY_MEMORY: 1.5},
                reasoning={MemoryType.IDENTITY_MEMORY: "Identity detected"},
                tenant_id="test-tenant",
                session_id="test-session",
                agent_id="test-agent",
            )
    
    def test_has_memory_type(self):
        """Test checking if memory has specific type."""
        memory_object = UniversalMemoryObject(
            content="Test content",
            memory_types=[MemoryType.IDENTITY_MEMORY, MemoryType.GOAL_MEMORY],
            confidence_scores={
                MemoryType.IDENTITY_MEMORY: 0.8,
                MemoryType.GOAL_MEMORY: 0.7,
            },
            reasoning={
                MemoryType.IDENTITY_MEMORY: "Identity detected",
                MemoryType.GOAL_MEMORY: "Goal detected",
            },
            tenant_id="test-tenant",
            session_id="test-session",
            agent_id="test-agent",
        )
        
        assert memory_object.has_memory_type(MemoryType.IDENTITY_MEMORY)
        assert not memory_object.has_memory_type(MemoryType.TASK_MEMORY)
    
    def test_add_tag(self):
        """Test adding tags to memory."""
        memory_object = UniversalMemoryObject(
            content="Test content",
            memory_types=[],
            confidence_scores={},
            reasoning={},
            tenant_id="test-tenant",
            session_id="test-session",
            agent_id="test-agent",
        )
        
        memory_object.add_tag("important")
        assert "important" in memory_object.tags
        
        # Adding same tag should not duplicate
        memory_object.add_tag("important")
        assert memory_object.tags.count("important") == 1
    
    def test_remove_tag(self):
        """Test removing tags from memory."""
        memory_object = UniversalMemoryObject(
            content="Test content",
            memory_types=[],
            confidence_scores={},
            reasoning={},
            tenant_id="test-tenant",
            session_id="test-session",
            agent_id="test-agent",
            tags=["important", "urgent"],
        )
        
        memory_object.remove_tag("important")
        assert "important" not in memory_object.tags
        assert "urgent" in memory_object.tags
    
    def test_to_storage_dict(self):
        """Test converting to storage dictionary."""
        memory_object = UniversalMemoryObject(
            content="Test content",
            memory_types=[MemoryType.IDENTITY_MEMORY],
            confidence_scores={MemoryType.IDENTITY_MEMORY: 0.8},
            reasoning={MemoryType.IDENTITY_MEMORY: "Identity detected"},
            tenant_id="test-tenant",
            session_id="test-session",
            agent_id="test-agent",
        )
        
        storage_dict = memory_object.to_storage_dict()
        
        assert storage_dict["content"] == "Test content"
        assert "identity_memory" in storage_dict["memory_types"]
        assert storage_dict["tenant_id"] == "test-tenant"
    
    def test_from_storage_dict(self):
        """Test creating from storage dictionary."""
        storage_dict = {
            "id": "test-id",
            "content": "Test content",
            "memory_types": ["identity_memory"],
            "confidence_scores": {"identity_memory": 0.8},
            "reasoning": {"identity_memory": "Identity detected"},
            "tenant_id": "test-tenant",
            "session_id": "test-session",
            "agent_id": "test-agent",
            "metadata": {},
            "tags": [],
            "timestamp": 1234567890.0,
            "last_accessed": 1234567890.0,
            "attention_vector": None,
            "storage_policy": "standard",
            "storage_locations": [],
            "classifier_method": "rule_based",
            "classification_metadata": {},
        }
        
        memory_object = UniversalMemoryObject.from_storage_dict(storage_dict)
        
        assert memory_object.id == "test-id"
        assert memory_object.content == "Test content"
        assert MemoryType.IDENTITY_MEMORY in memory_object.memory_types


class TestClassifierConfig:
    """Tests for ClassifierConfig."""
    
    def test_valid_classifier_config(self):
        """Test creation of valid classifier config."""
        config = ClassifierConfig(
            enabled=True,
            weight=1.0,
            confidence_threshold=0.5,
            method=ClassificationMethod.RULE_BASED,
        )
        
        assert config.enabled is True
        assert config.weight == 1.0
        assert config.confidence_threshold == 0.5
        assert config.method == ClassificationMethod.RULE_BASED
    
    def test_invalid_weight_raises_error(self):
        """Test that negative weight raises error."""
        with pytest.raises(ValidationError):
            ClassifierConfig(
                enabled=True,
                weight=-1.0,
                confidence_threshold=0.5,
                method=ClassificationMethod.RULE_BASED,
            )
    
    def test_invalid_confidence_threshold_raises_error(self):
        """Test that confidence threshold outside [0,1] raises error."""
        with pytest.raises(ValidationError):
            ClassifierConfig(
                enabled=True,
                weight=1.0,
                confidence_threshold=1.5,
                method=ClassificationMethod.RULE_BASED,
            )


class TestClassificationConfig:
    """Tests for ClassificationConfig."""
    
    def test_valid_classification_config(self):
        """Test creation of valid classification config."""
        config = ClassificationConfig(
            enable_caching=True,
            enable_telemetry=True,
            enable_logging=True,
            confidence_threshold=0.5,
            max_concurrent_classifications=100,
            batch_size=50,
        )
        
        assert config.enable_caching is True
        assert config.confidence_threshold == 0.5
        assert config.max_concurrent_classifications == 100
    
    def test_invalid_confidence_threshold_raises_error(self):
        """Test that confidence threshold outside [0,1] raises error."""
        with pytest.raises(ValidationError):
            ClassificationConfig(
                confidence_threshold=1.5,
            )
    
    def test_get_classifier_config(self):
        """Test getting classifier-specific config."""
        config = ClassificationConfig(
            classifier_configs={
                MemoryType.IDENTITY_MEMORY: ClassifierConfig(
                    enabled=True,
                    weight=1.0,
                    confidence_threshold=0.6,
                ),
            },
        )
        
        classifier_config = config.get_classifier_config(MemoryType.IDENTITY_MEMORY)
        assert classifier_config.confidence_threshold == 0.6
    
    def test_get_classifier_config_default(self):
        """Test getting default classifier config when not set."""
        config = ClassificationConfig()
        
        classifier_config = config.get_classifier_config(MemoryType.IDENTITY_MEMORY)
        assert classifier_config is not None
    
    def test_set_classifier_config(self):
        """Test setting classifier-specific config."""
        config = ClassificationConfig()
        
        new_config = ClassifierConfig(
            enabled=True,
            weight=1.5,
            confidence_threshold=0.7,
        )
        
        config.set_classifier_config(MemoryType.IDENTITY_MEMORY, new_config)
        
        retrieved_config = config.get_classifier_config(MemoryType.IDENTITY_MEMORY)
        assert retrieved_config.weight == 1.5
        assert retrieved_config.confidence_threshold == 0.7


class TestTypeDefinition:
    """Tests for TypeDefinition."""
    
    def test_valid_type_definition(self):
        """Test creation of valid type definition."""
        definition = TypeDefinition(
            memory_type=MemoryType.IDENTITY_MEMORY,
            schema_definition={"fields": {"name": {"type": "string"}}},
            validation_rules=["content_not_empty"],
            storage_policy=StoragePolicy.LONG_TERM,
            metadata={"description": "Identity memory"},
        )
        
        assert definition.memory_type == MemoryType.IDENTITY_MEMORY
        assert definition.storage_policy == StoragePolicy.LONG_TERM
        assert definition.metadata["description"] == "Identity memory"
