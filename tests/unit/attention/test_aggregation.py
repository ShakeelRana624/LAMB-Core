"""
Unit tests for aggregation strategies.
"""

import pytest
from attention.aggregation.strategies import (
    WeightedSumStrategy,
    GeometricMeanStrategy,
    MaximumStrategy,
    MinimumStrategy,
    HarmonicMeanStrategy,
    get_strategy,
)
from attention.core.exceptions import AggregationError


class TestWeightedSumStrategy:
    """Tests for WeightedSumStrategy."""
    
    @pytest.fixture
    def strategy(self):
        """Create a weighted sum strategy instance."""
        return WeightedSumStrategy()
    
    def test_aggregate_basic(self, strategy):
        """Test basic aggregation."""
        signal_scores = {"novelty": 0.8, "urgency": 0.6, "reward": 0.4}
        signal_weights = {"novelty": 0.5, "urgency": 0.3, "reward": 0.2}
        result = strategy.aggregate(signal_scores, signal_weights)
        assert 0.0 <= result <= 1.0
    
    def test_aggregate_empty(self, strategy):
        """Test aggregation with empty scores."""
        result = strategy.aggregate({}, {})
        assert result == 0.0
    
    def test_aggregate_none_scores(self, strategy):
        """Test aggregation with None scores."""
        signal_scores = {"novelty": None, "urgency": 0.6}
        signal_weights = {"novelty": 0.5, "urgency": 0.3}
        result = strategy.aggregate(signal_scores, signal_weights)
        assert result == 0.6  # Only urgency contributes
    
    def test_strategy_name(self, strategy):
        """Test strategy name property."""
        assert strategy.strategy_name == "weighted_sum"


class TestGeometricMeanStrategy:
    """Tests for GeometricMeanStrategy."""
    
    @pytest.fixture
    def strategy(self):
        """Create a geometric mean strategy instance."""
        return GeometricMeanStrategy()
    
    def test_aggregate_basic(self, strategy):
        """Test basic aggregation."""
        signal_scores = {"novelty": 0.8, "urgency": 0.6, "reward": 0.4}
        signal_weights = {"novelty": 0.5, "urgency": 0.3, "reward": 0.2}
        result = strategy.aggregate(signal_scores, signal_weights)
        assert 0.0 <= result <= 1.0
    
    def test_aggregate_empty(self, strategy):
        """Test aggregation with empty scores."""
        result = strategy.aggregate({}, {})
        assert result == 0.0
    
    def test_aggregate_zero_score(self, strategy):
        """Test aggregation with zero score."""
        signal_scores = {"novelty": 0.0, "urgency": 0.6}
        signal_weights = {"novelty": 0.5, "urgency": 0.3}
        result = strategy.aggregate(signal_scores, signal_weights)
        assert result == 0.0  # Zero score makes geometric mean zero
    
    def test_strategy_name(self, strategy):
        """Test strategy name property."""
        assert strategy.strategy_name == "geometric_mean"


class TestMaximumStrategy:
    """Tests for MaximumStrategy."""
    
    @pytest.fixture
    def strategy(self):
        """Create a maximum strategy instance."""
        return MaximumStrategy()
    
    def test_aggregate_basic(self, strategy):
        """Test basic aggregation."""
        signal_scores = {"novelty": 0.8, "urgency": 0.6, "reward": 0.4}
        signal_weights = {}  # Weights are ignored
        result = strategy.aggregate(signal_scores, signal_weights)
        assert result == 0.8  # Maximum score
    
    def test_aggregate_empty(self, strategy):
        """Test aggregation with empty scores."""
        result = strategy.aggregate({}, {})
        assert result == 0.0
    
    def test_strategy_name(self, strategy):
        """Test strategy name property."""
        assert strategy.strategy_name == "maximum"


class TestMinimumStrategy:
    """Tests for MinimumStrategy."""
    
    @pytest.fixture
    def strategy(self):
        """Create a minimum strategy instance."""
        return MinimumStrategy()
    
    def test_aggregate_basic(self, strategy):
        """Test basic aggregation."""
        signal_scores = {"novelty": 0.8, "urgency": 0.6, "reward": 0.4}
        signal_weights = {}  # Weights are ignored
        result = strategy.aggregate(signal_scores, signal_weights)
        assert result == 0.4  # Minimum score
    
    def test_aggregate_empty(self, strategy):
        """Test aggregation with empty scores."""
        result = strategy.aggregate({}, {})
        assert result == 0.0
    
    def test_strategy_name(self, strategy):
        """Test strategy name property."""
        assert strategy.strategy_name == "minimum"


class TestHarmonicMeanStrategy:
    """Tests for HarmonicMeanStrategy."""
    
    @pytest.fixture
    def strategy(self):
        """Create a harmonic mean strategy instance."""
        return HarmonicMeanStrategy()
    
    def test_aggregate_basic(self, strategy):
        """Test basic aggregation."""
        signal_scores = {"novelty": 0.8, "urgency": 0.6, "reward": 0.4}
        signal_weights = {"novelty": 0.5, "urgency": 0.3, "reward": 0.2}
        result = strategy.aggregate(signal_scores, signal_weights)
        assert 0.0 <= result <= 1.0
    
    def test_aggregate_empty(self, strategy):
        """Test aggregation with empty scores."""
        result = strategy.aggregate({}, {})
        assert result == 0.0
    
    def test_strategy_name(self, strategy):
        """Test strategy name property."""
        assert strategy.strategy_name == "harmonic_mean"


class TestGetStrategy:
    """Tests for get_strategy factory function."""
    
    def test_get_weighted_sum(self):
        """Test getting weighted sum strategy."""
        strategy = get_strategy("weighted_sum")
        assert isinstance(strategy, WeightedSumStrategy)
    
    def test_get_geometric_mean(self):
        """Test getting geometric mean strategy."""
        strategy = get_strategy("geometric_mean")
        assert isinstance(strategy, GeometricMeanStrategy)
    
    def test_get_maximum(self):
        """Test getting maximum strategy."""
        strategy = get_strategy("maximum")
        assert isinstance(strategy, MaximumStrategy)
    
    def test_get_minimum(self):
        """Test getting minimum strategy."""
        strategy = get_strategy("minimum")
        assert isinstance(strategy, MinimumStrategy)
    
    def test_get_harmonic_mean(self):
        """Test getting harmonic mean strategy."""
        strategy = get_strategy("harmonic_mean")
        assert isinstance(strategy, HarmonicMeanStrategy)
    
    def test_get_unknown_strategy(self):
        """Test getting unknown strategy raises error."""
        with pytest.raises(AggregationError):
            get_strategy("unknown_strategy")
