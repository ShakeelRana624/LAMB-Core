"""
Unit tests for Pydantic models.
"""

import pytest
from datetime import datetime
from attention.core.models import AttentionVector, AttentionConfig, SignalConfig
from attention.core.exceptions import ConfigurationError


class TestSignalConfig:
    """Tests for SignalConfig."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = SignalConfig()
        assert config.enabled is True
        assert config.weight == 1.0
        assert config.threshold == 0.0
        assert config.parameters == {}
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = SignalConfig(
            enabled=False,
            weight=0.5,
            threshold=0.3,
            parameters={"param1": "value1"},
        )
        assert config.enabled is False
        assert config.weight == 0.5
        assert config.threshold == 0.3
        assert config.parameters == {"param1": "value1"}
    
    def test_weight_validation(self):
        """Test weight validation."""
        with pytest.raises(ValueError):
            SignalConfig(weight=1.5)  # Invalid weight
    
    def test_threshold_validation(self):
        """Test threshold validation."""
        with pytest.raises(ValueError):
            SignalConfig(threshold=1.5)  # Invalid threshold


class TestAttentionConfig:
    """Tests for AttentionConfig."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = AttentionConfig()
        assert config.aggregation_strategy == "weighted_sum"
        assert config.storage_threshold == 0.5
        assert config.enable_caching is True
        assert config.enable_telemetry is True
        assert config.enable_logging is True
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = AttentionConfig(
            aggregation_strategy="geometric_mean",
            storage_threshold=0.7,
            enable_caching=False,
        )
        assert config.aggregation_strategy == "geometric_mean"
        assert config.storage_threshold == 0.7
        assert config.enable_caching is False
    
    def test_signal_config_management(self):
        """Test signal configuration management."""
        config = AttentionConfig()
        signal_config = SignalConfig(weight=0.5, enabled=True)
        config.set_signal_config("test_signal", signal_config)
        
        retrieved = config.get_signal_config("test_signal")
        assert retrieved.weight == 0.5
        assert retrieved.enabled is True
    
    def test_get_enabled_signals(self):
        """Test getting enabled signals."""
        config = AttentionConfig()
        config.signals = {
            "signal1": SignalConfig(enabled=True),
            "signal2": SignalConfig(enabled=False),
            "signal3": SignalConfig(enabled=True),
        }
        enabled = config.get_enabled_signals()
        assert "signal1" in enabled
        assert "signal2" not in enabled
        assert "signal3" in enabled
    
    def test_log_level_validation(self):
        """Test log level validation."""
        with pytest.raises(ValueError):
            AttentionConfig(log_level="INVALID")
    
    def test_storage_threshold_validation(self):
        """Test storage threshold validation."""
        with pytest.raises(ValueError):
            AttentionConfig(storage_threshold=1.5)


class TestAttentionVector:
    """Tests for AttentionVector."""
    
    def test_default_vector(self):
        """Test default attention vector."""
        vector = AttentionVector(
            session_id="test-session",
            agent_id="test-agent",
        )
        assert vector.session_id == "test-session"
        assert vector.agent_id == "test-agent"
        assert vector.aggregated_score == 0.0
        assert vector.should_store is False
    
    def test_set_signal_result(self):
        """Test setting signal result."""
        vector = AttentionVector(
            session_id="test-session",
            agent_id="test-agent",
        )
        result = {
            "score": 0.8,
            "explanation": "Test explanation",
            "signal_name": "test_signal",
        }
        vector.set_signal_result("test_signal", result)
        
        assert vector.signal_results["test_signal"] == result
        assert vector.get_signal_score("test_signal") == 0.8
    
    def test_get_signal_score(self):
        """Test getting signal score."""
        vector = AttentionVector(
            session_id="test-session",
            agent_id="test-agent",
        )
        vector.signal_results = {
            "test_signal": {"score": 0.8},
        }
        assert vector.get_signal_score("test_signal") == 0.8
        assert vector.get_signal_score("nonexistent") is None
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        vector = AttentionVector(
            session_id="test-session",
            agent_id="test-agent",
            aggregated_score=0.7,
            should_store=True,
        )
        vector.set_signal_result("test_signal", {"score": 0.8})
        
        result = vector.to_dict()
        assert "signals" in result
        assert "signal_results" in result
        assert "aggregated_score" in result
        assert "should_store" in result
        assert result["aggregated_score"] == 0.7
        assert result["should_store"] is True
    
    def test_aggregated_score_validation(self):
        """Test aggregated score validation."""
        with pytest.raises(ValueError):
            AttentionVector(
                session_id="test",
                agent_id="test",
                aggregated_score=1.5,  # Invalid score
            )
