"""
Unit tests for the Attention Engine.
"""

import pytest
import asyncio
from attention.core.interfaces import AttentionContext, TemporalContext, SocialContext
from attention.core.models import AttentionVector, AttentionConfig, SignalConfig
from attention.core.engine import AttentionEngine
from attention.config.defaults import get_default_config


class TestAttentionEngine:
    """Tests for AttentionEngine."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        config = get_default_config()
        config.enable_caching = False  # Disable caching for tests
        config.enable_telemetry = False  # Disable telemetry for tests
        config.enable_logging = False  # Disable logging for tests
        return config
    
    @pytest.fixture
    def engine(self, config):
        """Create an attention engine instance."""
        return AttentionEngine(config)
    
    @pytest.fixture
    def context(self):
        """Create a test context."""
        return AttentionContext(
            input_text="This is a test input",
            session_id="test-session",
            agent_id="test-agent",
            temporal_context=TemporalContext(),
            social_context=SocialContext(),
        )
    
    @pytest.mark.asyncio
    async def test_compute_attention(self, engine, context):
        """Test basic attention computation."""
        vector = await engine.compute_attention(context)
        assert isinstance(vector, AttentionVector)
        assert 0.0 <= vector.aggregated_score <= 1.0
        assert isinstance(vector.should_store, bool)
    
    @pytest.mark.asyncio
    async def test_compute_attention_with_metadata(self, engine, context):
        """Test attention computation with metadata."""
        context.metadata = {
            "recent_memories": [],
            "current_goal": "Test goal",
            "goal_keywords": ["test", "goal"],
        }
        vector = await engine.compute_attention(context)
        assert isinstance(vector, AttentionVector)
    
    @pytest.mark.asyncio
    async def test_compute_attention_parallel(self, engine, context):
        """Test parallel attention computation."""
        engine.config.parallel_execution = True
        vector = await engine.compute_attention(context)
        assert isinstance(vector, AttentionVector)
    
    @pytest.mark.asyncio
    async def test_compute_attention_sequential(self, engine, context):
        """Test sequential attention computation."""
        engine.config.parallel_execution = False
        vector = await engine.compute_attention(context)
        assert isinstance(vector, AttentionVector)
    
    def test_register_signal(self, engine):
        """Test signal registration."""
        from attention.signals.base import BaseSignal
        from attention.core.interfaces import AttentionResult
        
        class TestSignal(BaseSignal):
            @property
            def signal_name(self):
                return "test_signal"
            
            async def _compute_score(self, context):
                return 0.5
            
            def _generate_explanation(self, score, context):
                return "Test explanation"
        
        signal = TestSignal(weight=0.1, enabled=True)
        engine.register_signal(signal)
        assert "test_signal" in engine.list_signals()
    
    def test_unregister_signal(self, engine):
        """Test signal unregistration."""
        engine.unregister_signal("novelty")
        assert "novelty" not in engine.list_signals()
    
    def test_get_signal(self, engine):
        """Test getting a registered signal."""
        signal = engine.get_signal("novelty")
        assert signal.signal_name == "novelty"
    
    def test_list_signals(self, engine):
        """Test listing all signals."""
        signals = engine.list_signals()
        assert isinstance(signals, list)
        assert len(signals) > 0
    
    def test_get_statistics(self, engine):
        """Test getting engine statistics."""
        stats = engine.get_statistics()
        assert "aggregator" in stats
        assert "cache" in stats
        assert "registered_signals" in stats
        assert "enabled_signals" in stats
    
    def test_update_config(self, engine):
        """Test updating configuration."""
        new_config = get_default_config()
        new_config.storage_threshold = 0.7
        engine.update_config(new_config)
        assert engine.config.storage_threshold == 0.7
    
    @pytest.mark.asyncio
    async def test_storage_threshold(self, engine, context):
        """Test storage threshold decision."""
        engine.config.storage_threshold = 0.9
        context.input_text = "boring text"  # Should get low score
        vector = await engine.compute_attention(context)
        assert vector.should_store == (vector.aggregated_score >= 0.9)
