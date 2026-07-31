"""
Unit tests for attention signals.
"""

import pytest
import asyncio
from attention.core.interfaces import AttentionContext, TemporalContext, SocialContext
from attention.signals import (
    NoveltySignal,
    GoalRelevanceSignal,
    UrgencySignal,
    RewardSignal,
    RiskSignal,
    EmotionSignal,
    CuriositySignal,
    SurpriseSignal,
    ConfidenceSignal,
    FutureUtilitySignal,
    SocialImportanceSignal,
    RepetitionSignal,
    CurrentTaskMatchSignal,
)


class TestNoveltySignal:
    """Tests for NoveltySignal."""
    
    @pytest.fixture
    def signal(self):
        """Create a novelty signal instance."""
        return NoveltySignal(weight=0.15, enabled=True)
    
    @pytest.fixture
    def context(self):
        """Create a test context."""
        return AttentionContext(
            input_text="This is a test input",
            session_id="test-session",
            agent_id="test-agent",
            metadata={"recent_memories": []},
        )
    
    @pytest.mark.asyncio
    async def test_compute_no_recent_memories(self, signal, context):
        """Test computation with no recent memories."""
        result = await signal.compute(context)
        assert result.score == 1.0  # Maximum novelty when no recent memories
        assert result.signal_name == "novelty"
    
    @pytest.mark.asyncio
    async def test_compute_with_recent_memories(self, signal, context):
        """Test computation with recent memories."""
        context.metadata["recent_memories"] = [
            {"text": "This is a test input"},
            {"text": "Another similar input"},
        ]
        result = await signal.compute(context)
        assert 0.0 <= result.score <= 1.0
        assert result.signal_name == "novelty"
    
    def test_signal_name(self, signal):
        """Test signal name property."""
        assert signal.signal_name == "novelty"
    
    def test_weight(self, signal):
        """Test weight property."""
        assert signal.get_weight() == 0.15
        signal.set_weight(0.2)
        assert signal.get_weight() == 0.2
    
    def test_enable_disable(self, signal):
        """Test enable/disable functionality."""
        assert signal.is_enabled() is True
        signal.disable()
        assert signal.is_enabled() is False
        signal.enable()
        assert signal.is_enabled() is True


class TestGoalRelevanceSignal:
    """Tests for GoalRelevanceSignal."""
    
    @pytest.fixture
    def signal(self):
        """Create a goal relevance signal instance."""
        return GoalRelevanceSignal(weight=0.12, enabled=True)
    
    @pytest.fixture
    def context(self):
        """Create a test context."""
        return AttentionContext(
            input_text="Complete the project by Friday",
            session_id="test-session",
            agent_id="test-agent",
            current_goal="Complete the project",
            metadata={
                "goal_priority": "primary",
                "goal_keywords": ["project", "complete", "finish"],
            },
        )
    
    @pytest.mark.asyncio
    async def test_compute_with_goal(self, signal, context):
        """Test computation with a current goal."""
        result = await signal.compute(context)
        assert 0.0 <= result.score <= 1.0
        assert result.signal_name == "goal_relevance"
    
    @pytest.mark.asyncio
    async def test_compute_without_goal(self, signal, context):
        """Test computation without a current goal."""
        context.current_goal = None
        result = await signal.compute(context)
        assert result.score == 0.5  # Neutral relevance when no goal
    
    def test_signal_name(self, signal):
        """Test signal name property."""
        assert signal.signal_name == "goal_relevance"


class TestUrgencySignal:
    """Tests for UrgencySignal."""
    
    @pytest.fixture
    def signal(self):
        """Create an urgency signal instance."""
        return UrgencySignal(weight=0.10, enabled=True)
    
    @pytest.fixture
    def context(self):
        """Create a test context."""
        return AttentionContext(
            input_text="This is urgent, need it done today",
            session_id="test-session",
            agent_id="test-agent",
        )
    
    @pytest.mark.asyncio
    async def test_compute_high_urgency(self, signal, context):
        """Test computation with high urgency indicators."""
        result = await signal.compute(context)
        assert result.score >= 0.5  # Should detect urgency
        assert result.signal_name == "urgency"
    
    @pytest.mark.asyncio
    async def test_compute_low_urgency(self, signal, context):
        """Test computation with low urgency indicators."""
        context.input_text = "This can be done eventually"
        result = await signal.compute(context)
        assert 0.0 <= result.score <= 1.0
        assert result.signal_name == "urgency"
    
    def test_signal_name(self, signal):
        """Test signal name property."""
        assert signal.signal_name == "urgency"


class TestRewardSignal:
    """Tests for RewardSignal."""
    
    @pytest.fixture
    def signal(self):
        """Create a reward signal instance."""
        return RewardSignal(weight=0.08, enabled=True)
    
    @pytest.fixture
    def context(self):
        """Create a test context."""
        return AttentionContext(
            input_text="Great job! We successfully completed the task",
            session_id="test-session",
            agent_id="test-agent",
        )
    
    @pytest.mark.asyncio
    async def test_compute_positive(self, signal, context):
        """Test computation with positive indicators."""
        result = await signal.compute(context)
        assert 0.0 <= result.score <= 1.0
        assert result.signal_name == "reward"
    
    def test_signal_name(self, signal):
        """Test signal name property."""
        assert signal.signal_name == "reward"


class TestRiskSignal:
    """Tests for RiskSignal."""
    
    @pytest.fixture
    def signal(self):
        """Create a risk signal instance."""
        return RiskSignal(weight=0.10, enabled=True)
    
    @pytest.fixture
    def context(self):
        """Create a test context."""
        return AttentionContext(
            input_text="Warning: there is a risk of failure",
            session_id="test-session",
            agent_id="test-agent",
        )
    
    @pytest.mark.asyncio
    async def test_compute_risk(self, signal, context):
        """Test computation with risk indicators."""
        result = await signal.compute(context)
        assert 0.0 <= result.score <= 1.0
        assert result.signal_name == "risk"
    
    def test_signal_name(self, signal):
        """Test signal name property."""
        assert signal.signal_name == "risk"


class TestEmotionSignal:
    """Tests for EmotionSignal."""
    
    @pytest.fixture
    def signal(self):
        """Create an emotion signal instance."""
        return EmotionSignal(weight=0.07, enabled=True)
    
    @pytest.fixture
    def context(self):
        """Create a test context."""
        return AttentionContext(
            input_text="I am very happy and excited about this!",
            session_id="test-session",
            agent_id="test-agent",
        )
    
    @pytest.mark.asyncio
    async def test_compute_emotion(self, signal, context):
        """Test computation with emotional content."""
        result = await signal.compute(context)
        assert 0.0 <= result.score <= 1.0
        assert result.signal_name == "emotion"
    
    def test_signal_name(self, signal):
        """Test signal name property."""
        assert signal.signal_name == "emotion"


class TestCuriositySignal:
    """Tests for CuriositySignal."""
    
    @pytest.fixture
    def signal(self):
        """Create a curiosity signal instance."""
        return CuriositySignal(weight=0.05, enabled=True)
    
    @pytest.fixture
    def context(self):
        """Create a test context."""
        return AttentionContext(
            input_text="I wonder how this works? What is the mechanism?",
            session_id="test-session",
            agent_id="test-agent",
        )
    
    @pytest.mark.asyncio
    async def test_compute_curiosity(self, signal, context):
        """Test computation with curiosity indicators."""
        result = await signal.compute(context)
        assert 0.0 <= result.score <= 1.0
        assert result.signal_name == "curiosity"
    
    def test_signal_name(self, signal):
        """Test signal name property."""
        assert signal.signal_name == "curiosity"


class TestSurpriseSignal:
    """Tests for SurpriseSignal."""
    
    @pytest.fixture
    def signal(self):
        """Create a surprise signal instance."""
        return SurpriseSignal(weight=0.06, enabled=True)
    
    @pytest.fixture
    def context(self):
        """Create a test context."""
        return AttentionContext(
            input_text="This was completely unexpected! Wow!",
            session_id="test-session",
            agent_id="test-agent",
        )
    
    @pytest.mark.asyncio
    async def test_compute_surprise(self, signal, context):
        """Test computation with surprise indicators."""
        result = await signal.compute(context)
        assert 0.0 <= result.score <= 1.0
        assert result.signal_name == "surprise"
    
    def test_signal_name(self, signal):
        """Test signal name property."""
        assert signal.signal_name == "surprise"


class TestConfidenceSignal:
    """Tests for ConfidenceSignal."""
    
    @pytest.fixture
    def signal(self):
        """Create a confidence signal instance."""
        return ConfidenceSignal(weight=0.04, enabled=True)
    
    @pytest.fixture
    def context(self):
        """Create a test context."""
        return AttentionContext(
            input_text="I am definitely certain about this",
            session_id="test-session",
            agent_id="test-agent",
        )
    
    @pytest.mark.asyncio
    async def test_compute_confidence(self, signal, context):
        """Test computation with confidence indicators."""
        result = await signal.compute(context)
        assert 0.0 <= result.score <= 1.0
        assert result.signal_name == "confidence"
    
    def test_signal_name(self, signal):
        """Test signal name property."""
        assert signal.signal_name == "confidence"


class TestFutureUtilitySignal:
    """Tests for FutureUtilitySignal."""
    
    @pytest.fixture
    def signal(self):
        """Create a future utility signal instance."""
        return FutureUtilitySignal(weight=0.08, enabled=True)
    
    @pytest.fixture
    def context(self):
        """Create a test context."""
        return AttentionContext(
            input_text="We need to plan this for next month",
            session_id="test-session",
            agent_id="test-agent",
        )
    
    @pytest.mark.asyncio
    async def test_compute_future_utility(self, signal, context):
        """Test computation with future utility indicators."""
        result = await signal.compute(context)
        assert 0.0 <= result.score <= 1.0
        assert result.signal_name == "future_utility"
    
    def test_signal_name(self, signal):
        """Test signal name property."""
        assert signal.signal_name == "future_utility"


class TestSocialImportanceSignal:
    """Tests for SocialImportanceSignal."""
    
    @pytest.fixture
    def signal(self):
        """Create a social importance signal instance."""
        return SocialImportanceSignal(weight=0.05, enabled=True)
    
    @pytest.fixture
    def context(self):
        """Create a test context."""
        return AttentionContext(
            input_text="John said that the team meeting is important",
            session_id="test-session",
            agent_id="test-agent",
            social_context=SocialContext(group_size=5),
        )
    
    @pytest.mark.asyncio
    async def test_compute_social_importance(self, signal, context):
        """Test computation with social importance indicators."""
        result = await signal.compute(context)
        assert 0.0 <= result.score <= 1.0
        assert result.signal_name == "social_importance"
    
    def test_signal_name(self, signal):
        """Test signal name property."""
        assert signal.signal_name == "social_importance"


class TestRepetitionSignal:
    """Tests for RepetitionSignal."""
    
    @pytest.fixture
    def signal(self):
        """Create a repetition signal instance."""
        return RepetitionSignal(weight=0.06, enabled=True)
    
    @pytest.fixture
    def context(self):
        """Create a test context."""
        return AttentionContext(
            input_text="This is important",
            session_id="test-session",
            agent_id="test-agent",
            metadata={
                "recent_inputs": [
                    {"text": "This is important"},
                    {"text": "This is important"},
                ],
            },
        )
    
    @pytest.mark.asyncio
    async def test_compute_repetition(self, signal, context):
        """Test computation with repetition indicators."""
        result = await signal.compute(context)
        assert 0.0 <= result.score <= 1.0
        assert result.signal_name == "repetition"
    
    def test_signal_name(self, signal):
        """Test signal name property."""
        assert signal.signal_name == "repetition"


class TestCurrentTaskMatchSignal:
    """Tests for CurrentTaskMatchSignal."""
    
    @pytest.fixture
    def signal(self):
        """Create a current task match signal instance."""
        return CurrentTaskMatchSignal(weight=0.09, enabled=True)
    
    @pytest.fixture
    def context(self):
        """Create a test context."""
        return AttentionContext(
            input_text="Working on the database migration",
            session_id="test-session",
            agent_id="test-agent",
            current_task="Database migration",
            metadata={"task_level": "primary"},
        )
    
    @pytest.mark.asyncio
    async def test_compute_task_match(self, signal, context):
        """Test computation with task match indicators."""
        result = await signal.compute(context)
        assert 0.0 <= result.score <= 1.0
        assert result.signal_name == "current_task_match"
    
    def test_signal_name(self, signal):
        """Test signal name property."""
        assert signal.signal_name == "current_task_match"
