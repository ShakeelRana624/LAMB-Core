"""
Unit tests for memory classifiers.

This module contains comprehensive unit tests for all 12 memory type classifiers.
"""

import pytest
import asyncio
from memory_classification.core.types import MemoryType
from memory_classification.core.interfaces import MemoryInput
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


class TestIdentityClassifier:
    """Tests for IdentityClassifier."""
    
    @pytest.fixture
    def classifier(self):
        """Create identity classifier instance."""
        return IdentityClassifier()
    
    @pytest.mark.asyncio
    async def test_classify_identity_statement(self, classifier):
        """Test classification of identity statement."""
        memory_input = MemoryInput(
            content="My name is John and I am 30 years old",
            session_id="test-session",
            agent_id="test-agent",
            tenant_id="test-tenant",
        )
        
        result = await classifier.classify(memory_input)
        
        assert result.memory_types == [MemoryType.IDENTITY_MEMORY]
        assert result.confidence_scores[MemoryType.IDENTITY_MEMORY] >= 0.5
        assert "identity" in result.reasoning[MemoryType.IDENTITY_MEMORY].lower()
    
    @pytest.mark.asyncio
    async def test_classify_non_identity(self, classifier):
        """Test classification of non-identity statement."""
        memory_input = MemoryInput(
            content="The weather is nice today",
            session_id="test-session",
            agent_id="test-agent",
            tenant_id="test-tenant",
        )
        
        result = await classifier.classify(memory_input)
        
        assert MemoryType.IDENTITY_MEMORY not in result.memory_types or \
               result.confidence_scores[MemoryType.IDENTITY_MEMORY] < 0.5
    
    def test_get_supported_types(self, classifier):
        """Test getting supported memory types."""
        types = classifier.get_supported_types()
        assert MemoryType.IDENTITY_MEMORY in types
    
    def test_enable_disable(self, classifier):
        """Test enabling and disabling classifier."""
        assert classifier.is_enabled()
        
        classifier.disable()
        assert not classifier.is_enabled()
        
        classifier.enable()
        assert classifier.is_enabled()


class TestGoalClassifier:
    """Tests for GoalClassifier."""
    
    @pytest.fixture
    def classifier(self):
        """Create goal classifier instance."""
        return GoalClassifier()
    
    @pytest.mark.asyncio
    async def test_classify_goal_statement(self, classifier):
        """Test classification of goal statement."""
        memory_input = MemoryInput(
            content="I want to achieve my goal of completing the project by Friday",
            session_id="test-session",
            agent_id="test-agent",
            tenant_id="test-tenant",
        )
        
        result = await classifier.classify(memory_input)
        
        assert result.memory_types == [MemoryType.GOAL_MEMORY]
        assert result.confidence_scores[MemoryType.GOAL_MEMORY] >= 0.5
    
    @pytest.mark.asyncio
    async def test_classify_non_goal(self, classifier):
        """Test classification of non-goal statement."""
        memory_input = MemoryInput(
            content="The weather is nice today",
            session_id="test-session",
            agent_id="test-agent",
            tenant_id="test-tenant",
        )
        
        result = await classifier.classify(memory_input)
        
        assert MemoryType.GOAL_MEMORY not in result.memory_types or \
               result.confidence_scores[MemoryType.GOAL_MEMORY] < 0.5


class TestPreferenceClassifier:
    """Tests for PreferenceClassifier."""
    
    @pytest.fixture
    def classifier(self):
        """Create preference classifier instance."""
        return PreferenceClassifier()
    
    @pytest.mark.asyncio
    async def test_classify_preference_statement(self, classifier):
        """Test classification of preference statement."""
        memory_input = MemoryInput(
            content="I really like chocolate ice cream",
            session_id="test-session",
            agent_id="test-agent",
            tenant_id="test-tenant",
        )
        
        result = await classifier.classify(memory_input)
        
        assert result.memory_types == [MemoryType.PREFERENCE_MEMORY]
        assert result.confidence_scores[MemoryType.PREFERENCE_MEMORY] >= 0.5


class TestRelationshipClassifier:
    """Tests for RelationshipClassifier."""
    
    @pytest.fixture
    def classifier(self):
        """Create relationship classifier instance."""
        return RelationshipClassifier()
    
    @pytest.mark.asyncio
    async def test_classify_relationship_statement(self, classifier):
        """Test classification of relationship statement."""
        memory_input = MemoryInput(
            content="My friend John is coming to the meeting",
            session_id="test-session",
            agent_id="test-agent",
            tenant_id="test-tenant",
        )
        
        result = await classifier.classify(memory_input)
        
        assert result.memory_types == [MemoryType.RELATIONSHIP_MEMORY]
        assert result.confidence_scores[MemoryType.RELATIONSHIP_MEMORY] >= 0.5


class TestProjectClassifier:
    """Tests for ProjectClassifier."""
    
    @pytest.fixture
    def classifier(self):
        """Create project classifier instance."""
        return ProjectClassifier()
    
    @pytest.mark.asyncio
    async def test_classify_project_statement(self, classifier):
        """Test classification of project statement."""
        memory_input = MemoryInput(
            content="I am working on the database migration project",
            session_id="test-session",
            agent_id="test-agent",
            tenant_id="test-tenant",
        )
        
        result = await classifier.classify(memory_input)
        
        assert result.memory_types == [MemoryType.PROJECT_MEMORY]
        assert result.confidence_scores[MemoryType.PROJECT_MEMORY] >= 0.5


class TestSkillClassifier:
    """Tests for SkillClassifier."""
    
    @pytest.fixture
    def classifier(self):
        """Create skill classifier instance."""
        return SkillClassifier()
    
    @pytest.mark.asyncio
    async def test_classify_skill_statement(self, classifier):
        """Test classification of skill statement."""
        memory_input = MemoryInput(
            content="I am learning Python programming",
            session_id="test-session",
            agent_id="test-agent",
            tenant_id="test-tenant",
        )
        
        result = await classifier.classify(memory_input)
        
        assert result.memory_types == [MemoryType.SKILL_MEMORY]
        assert result.confidence_scores[MemoryType.SKILL_MEMORY] >= 0.5


class TestProceduralClassifier:
    """Tests for ProceduralClassifier."""
    
    @pytest.fixture
    def classifier(self):
        """Create procedural classifier instance."""
        return ProceduralClassifier()
    
    @pytest.mark.asyncio
    async def test_classify_procedural_statement(self, classifier):
        """Test classification of procedural statement."""
        memory_input = MemoryInput(
            content="First, mix the ingredients. Second, bake at 350 degrees for 30 minutes.",
            session_id="test-session",
            agent_id="test-agent",
            tenant_id="test-tenant",
        )
        
        result = await classifier.classify(memory_input)
        
        assert result.memory_types == [MemoryType.PROCEDURAL_MEMORY]
        assert result.confidence_scores[MemoryType.PROCEDURAL_MEMORY] >= 0.5


class TestTaskClassifier:
    """Tests for TaskClassifier."""
    
    @pytest.fixture
    def classifier(self):
        """Create task classifier instance."""
        return TaskClassifier()
    
    @pytest.mark.asyncio
    async def test_classify_task_statement(self, classifier):
        """Test classification of task statement."""
        memory_input = MemoryInput(
            content="I need to complete the report by Friday",
            session_id="test-session",
            agent_id="test-agent",
            tenant_id="test-tenant",
        )
        
        result = await classifier.classify(memory_input)
        
        assert result.memory_types == [MemoryType.TASK_MEMORY]
        assert result.confidence_scores[MemoryType.TASK_MEMORY] >= 0.5


class TestEpisodicClassifier:
    """Tests for EpisodicClassifier."""
    
    @pytest.fixture
    def classifier(self):
        """Create episodic classifier instance."""
        return EpisodicClassifier()
    
    @pytest.mark.asyncio
    async def test_classify_episodic_statement(self, classifier):
        """Test classification of episodic statement."""
        memory_input = MemoryInput(
            content="Yesterday, I went to the park with my friends",
            session_id="test-session",
            agent_id="test-agent",
            tenant_id="test-tenant",
        )
        
        result = await classifier.classify(memory_input)
        
        assert result.memory_types == [MemoryType.EPISODIC_MEMORY]
        assert result.confidence_scores[MemoryType.EPISODIC_MEMORY] >= 0.5


class TestSemanticClassifier:
    """Tests for SemanticClassifier."""
    
    @pytest.fixture
    def classifier(self):
        """Create semantic classifier instance."""
        return SemanticClassifier()
    
    @pytest.mark.asyncio
    async def test_classify_semantic_statement(self, classifier):
        """Test classification of semantic statement."""
        memory_input = MemoryInput(
            content="Water boils at 100 degrees Celsius at sea level",
            session_id="test-session",
            agent_id="test-agent",
            tenant_id="test-tenant",
        )
        
        result = await classifier.classify(memory_input)
        
        assert result.memory_types == [MemoryType.SEMANTIC_MEMORY]
        assert result.confidence_scores[MemoryType.SEMANTIC_MEMORY] >= 0.5


class TestEmotionalClassifier:
    """Tests for EmotionalClassifier."""
    
    @pytest.fixture
    def classifier(self):
        """Create emotional classifier instance."""
        return EmotionalClassifier()
    
    @pytest.mark.asyncio
    async def test_classify_emotional_statement(self, classifier):
        """Test classification of emotional statement."""
        memory_input = MemoryInput(
            content="I feel very happy about the good news",
            session_id="test-session",
            agent_id="test-agent",
            tenant_id="test-tenant",
        )
        
        result = await classifier.classify(memory_input)
        
        assert result.memory_types == [MemoryType.EMOTIONAL_MEMORY]
        assert result.confidence_scores[MemoryType.EMOTIONAL_MEMORY] >= 0.5


class TestTemporalClassifier:
    """Tests for TemporalClassifier."""
    
    @pytest.fixture
    def classifier(self):
        """Create temporal classifier instance."""
        return TemporalClassifier()
    
    @pytest.mark.asyncio
    async def test_classify_temporal_statement(self, classifier):
        """Test classification of temporal statement."""
        memory_input = MemoryInput(
            content="The meeting is scheduled for tomorrow at 2pm",
            session_id="test-session",
            agent_id="test-agent",
            tenant_id="test-tenant",
        )
        
        result = await classifier.classify(memory_input)
        
        assert result.memory_types == [MemoryType.TEMPORAL_MEMORY]
        assert result.confidence_scores[MemoryType.TEMPORAL_MEMORY] >= 0.5
