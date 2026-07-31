"""
Unit tests for Classification Engine.

This module contains comprehensive unit tests for the Classification Engine orchestrator.
"""

import pytest
import asyncio
from memory_classification.core.interfaces import MemoryInput
from memory_classification.core.engine import ClassificationEngine
from memory_classification.core.models import ClassificationConfig
from memory_classification.config.defaults import get_default_config
from memory_classification.classifiers.identity import IdentityClassifier
from memory_classification.classifiers.goal import GoalClassifier
from memory_classification.classifiers.episodic import EpisodicClassifier
from memory_classification.classifiers.semantic import SemanticClassifier


class TestClassificationEngine:
    """Tests for ClassificationEngine."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return get_default_config()
    
    @pytest.fixture
    def engine(self, config):
        """Create classification engine instance."""
        return ClassificationEngine(config=config)
    
    @pytest.fixture
    def engine_with_classifiers(self, engine):
        """Create engine with registered classifiers."""
        engine.register_classifier(IdentityClassifier())
        engine.register_classifier(GoalClassifier())
        engine.register_classifier(EpisodicClassifier())
        engine.register_classifier(SemanticClassifier())
        return engine
    
    @pytest.mark.asyncio
    async def test_classify_single_memory(self, engine_with_classifiers):
        """Test classification of a single memory."""
        memory_input = MemoryInput(
            content="My name is John and I want to achieve my goal",
            session_id="test-session",
            agent_id="test-agent",
            tenant_id="test-tenant",
        )
        
        result = await engine_with_classifiers.classify(memory_input)
        
        assert result is not None
        assert result.content == memory_input.content
        assert result.tenant_id == memory_input.tenant_id
        assert len(result.memory_types) > 0
    
    @pytest.mark.asyncio
    async def test_classify_with_no_classifiers(self, engine):
        """Test classification with no registered classifiers."""
        memory_input = MemoryInput(
            content="Test content",
            session_id="test-session",
            agent_id="test-agent",
            tenant_id="test-tenant",
        )
        
        with pytest.raises(Exception):
            await engine.classify(memory_input)
    
    @pytest.mark.asyncio
    async def test_batch_classify(self, engine_with_classifiers):
        """Test batch classification of multiple memories."""
        memory_inputs = [
            MemoryInput(
                content=f"Test content {i}",
                session_id="test-session",
                agent_id="test-agent",
                tenant_id="test-tenant",
            )
            for i in range(5)
        ]
        
        results = await engine_with_classifiers.batch_classify(memory_inputs)
        
        assert len(results) == len(memory_inputs)
        for result in results:
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_confidence_threshold_filtering(self, engine_with_classifiers):
        """Test that confidence threshold filtering works."""
        # Set high confidence threshold
        engine_with_classifiers.config.confidence_threshold = 0.9
        
        memory_input = MemoryInput(
            content="Test content",
            session_id="test-session",
            agent_id="test-agent",
            tenant_id="test-tenant",
        )
        
        result = await engine_with_classifiers.classify(memory_input)
        
        # With high threshold, should have fewer or no memory types
        assert len(result.memory_types) <= 4  # Max 4 classifiers registered
    
    def test_register_classifier(self, engine):
        """Test classifier registration."""
        classifier = IdentityClassifier()
        engine.register_classifier(classifier)
        
        assert engine.classifier_registry.has_classifier(classifier.memory_type)
    
    def test_unregister_classifier(self, engine_with_classifiers):
        """Test classifier unregistration."""
        from memory_classification.core.types import MemoryType
        
        engine_with_classifiers.unregister_classifier(MemoryType.IDENTITY_MEMORY)
        
        assert not engine_with_classifiers.classifier_registry.has_classifier(MemoryType.IDENTITY_MEMORY)
    
    def test_enable_disable_classifier(self, engine_with_classifiers):
        """Test enabling and disabling classifiers."""
        from memory_classification.core.types import MemoryType
        
        # Disable classifier
        engine_with_classifiers.disable_classifier(MemoryType.IDENTITY_MEMORY)
        assert not engine_with_classifiers.classifier_registry.get_classifier(MemoryType.IDENTITY_MEMORY).is_enabled()
        
        # Enable classifier
        engine_with_classifiers.enable_classifier(MemoryType.IDENTITY_MEMORY)
        assert engine_with_classifiers.classifier_registry.get_classifier(MemoryType.IDENTITY_MEMORY).is_enabled()
    
    def test_get_statistics(self, engine_with_classifiers):
        """Test getting engine statistics."""
        stats = engine_with_classifiers.get_statistics()
        
        assert "total_classifications" in stats
        assert "successful_classifications" in stats
        assert "failed_classifications" in stats
        assert "success_rate" in stats
        assert "average_computation_time_ms" in stats
        assert "classifier_usage" in stats
    
    def test_reset_statistics(self, engine_with_classifiers):
        """Test resetting statistics."""
        # First, run a classification to generate stats
        async def run_classification():
            memory_input = MemoryInput(
                content="Test content",
                session_id="test-session",
                agent_id="test-agent",
                tenant_id="test-tenant",
            )
            await engine_with_classifiers.classify(memory_input)
        
        asyncio.run(run_classification())
        
        # Reset statistics
        engine_with_classifiers.reset_statistics()
        
        stats = engine_with_classifiers.get_statistics()
        assert stats["total_classifications"] == 0
    
    def test_update_config(self, engine):
        """Test updating engine configuration."""
        new_config = ClassificationConfig(
            confidence_threshold=0.7,
            max_concurrent_classifications=50,
        )
        
        engine.update_config(new_config)
        
        assert engine.config.confidence_threshold == 0.7
        assert engine.config.max_concurrent_classifications == 50


class TestClassificationEngineIntegration:
    """Integration tests for ClassificationEngine."""
    
    @pytest.mark.asyncio
    async def test_full_classification_pipeline(self):
        """Test the full classification pipeline with all components."""
        config = get_default_config()
        engine = ClassificationEngine(config=config)
        
        # Register all classifiers
        from memory_classification.classifiers.identity import IdentityClassifier
        from memory_classification.classifiers.goal import GoalClassifier
        from memory_classification.classifiers.preference import PreferenceClassifier
        from memory_classification.classifiers.relationship import RelationshipClassifier
        from memory_classification.classifiers.project import ProjectClassifier
        from memory_classification.classifiers.skill import SkillClassifier
        from memory_classification.classifiers.procedural import ProceduralClassifier
        from memory_classification.classifiers.task import TaskClassifier
        from memory_classification.classifiers.episodic import EpisodicClassifier
        from memory_classification.classifiers.semantic import SemanticClassifier
        from memory_classification.classifiers.emotional import EmotionalClassifier
        from memory_classification.classifiers.temporal import TemporalClassifier
        
        classifiers = [
            IdentityClassifier(),
            GoalClassifier(),
            PreferenceClassifier(),
            RelationshipClassifier(),
            ProjectClassifier(),
            SkillClassifier(),
            ProceduralClassifier(),
            TaskClassifier(),
            EpisodicClassifier(),
            SemanticClassifier(),
            EmotionalClassifier(),
            TemporalClassifier(),
        ]
        
        for classifier in classifiers:
            engine.register_classifier(classifier)
        
        # Test classification
        memory_input = MemoryInput(
            content="My name is John and I want to achieve my goal of completing the project by Friday",
            session_id="test-session",
            agent_id="test-agent",
            tenant_id="test-tenant",
        )
        
        result = await engine.classify(memory_input)
        
        assert result is not None
        assert result.content == memory_input.content
        assert len(result.memory_types) > 0
        assert result.confidence_scores is not None
        assert result.reasoning is not None
