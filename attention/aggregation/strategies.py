"""
Aggregation strategies for combining attention signals.

This module implements various strategies for aggregating
individual attention signal scores into a final attention score.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import numpy as np

from attention.core.models import AttentionVector
from attention.core.types import AggregationStrategy
from attention.core.exceptions import AggregationError


class AggregationStrategy(ABC):
    """
    Abstract base class for aggregation strategies.
    
    Each strategy implements a different method for combining
    individual signal scores into a final aggregated score.
    """
    
    @abstractmethod
    def aggregate(
        self,
        signal_scores: Dict[str, float],
        signal_weights: Dict[str, float],
    ) -> float:
        """
        Aggregate signal scores into a final score.
        
        Args:
            signal_scores: Dictionary mapping signal names to scores
            signal_weights: Dictionary mapping signal names to weights
            
        Returns:
            Aggregated score between 0.0 and 1.0
            
        Raises:
            AggregationError: If aggregation fails
        """
        pass
    
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Return the strategy name."""
        pass


class WeightedSumStrategy(AggregationStrategy):
    """
    Weighted sum aggregation strategy.
    
    Computes the weighted sum of all signal scores.
    This is the default and most commonly used strategy.
    
    Formula: final_score = Σ(signal_score × signal_weight) / Σ(weights)
    """
    
    def aggregate(
        self,
        signal_scores: Dict[str, float],
        signal_weights: Dict[str, float],
    ) -> float:
        """
        Aggregate using weighted sum.
        
        Args:
            signal_scores: Dictionary mapping signal names to scores
            signal_weights: Dictionary mapping signal names to weights
            
        Returns:
            Weighted sum score
        """
        if not signal_scores:
            return 0.0
        
        try:
            total_weight = 0.0
            weighted_sum = 0.0
            
            for signal_name, score in signal_scores.items():
                if score is None:
                    continue
                
                weight = signal_weights.get(signal_name, 1.0)
                weighted_sum += score * weight
                total_weight += weight
            
            if total_weight == 0.0:
                return 0.0
            
            return weighted_sum / total_weight
        except Exception as e:
            raise AggregationError(f"Weighted sum aggregation failed: {str(e)}")
    
    @property
    def strategy_name(self) -> str:
        """Return the strategy name."""
        return "weighted_sum"


class GeometricMeanStrategy(AggregationStrategy):
    """
    Geometric mean aggregation strategy.
    
    Computes the weighted geometric mean of signal scores.
    This strategy penalizes low scores more heavily than weighted sum.
    
    Formula: final_score = (Π signal_score^weight)^(1/Σweights)
    """
    
    def aggregate(
        self,
        signal_scores: Dict[str, float],
        signal_weights: Dict[str, float],
    ) -> float:
        """
        Aggregate using geometric mean.
        
        Args:
            signal_scores: Dictionary mapping signal names to scores
            signal_weights: Dictionary mapping signal names to weights
            
        Returns:
            Geometric mean score
        """
        if not signal_scores:
            return 0.0
        
        try:
            total_weight = 0.0
            product = 1.0
            
            for signal_name, score in signal_scores.items():
                if score is None or score <= 0.0:
                    continue
                
                weight = signal_weights.get(signal_name, 1.0)
                product *= score ** weight
                total_weight += weight
            
            if total_weight == 0.0:
                return 0.0
            
            return product ** (1.0 / total_weight)
        except Exception as e:
            raise AggregationError(f"Geometric mean aggregation failed: {str(e)}")
    
    @property
    def strategy_name(self) -> str:
        """Return the strategy name."""
        return "geometric_mean"


class MaximumStrategy(AggregationStrategy):
    """
    Maximum aggregation strategy.
    
    Returns the maximum signal score.
    This strategy is useful when any high signal should trigger attention.
    
    Formula: final_score = max(signal_scores)
    """
    
    def aggregate(
        self,
        signal_scores: Dict[str, float],
        signal_weights: Dict[str, float],
    ) -> float:
        """
        Aggregate using maximum.
        
        Args:
            signal_scores: Dictionary mapping signal names to scores
            signal_weights: Dictionary mapping signal names to weights (ignored)
            
        Returns:
            Maximum score
        """
        if not signal_scores:
            return 0.0
        
        try:
            valid_scores = [s for s in signal_scores.values() if s is not None]
            if not valid_scores:
                return 0.0
            
            return max(valid_scores)
        except Exception as e:
            raise AggregationError(f"Maximum aggregation failed: {str(e)}")
    
    @property
    def strategy_name(self) -> str:
        """Return the strategy name."""
        return "maximum"


class MinimumStrategy(AggregationStrategy):
    """
    Minimum aggregation strategy.
    
    Returns the minimum signal score.
    This strategy is useful when all signals must be high.
    
    Formula: final_score = min(signal_scores)
    """
    
    def aggregate(
        self,
        signal_scores: Dict[str, float],
        signal_weights: Dict[str, float],
    ) -> float:
        """
        Aggregate using minimum.
        
        Args:
            signal_scores: Dictionary mapping signal names to scores
            signal_weights: Dictionary mapping signal names to weights (ignored)
            
        Returns:
            Minimum score
        """
        if not signal_scores:
            return 0.0
        
        try:
            valid_scores = [s for s in signal_scores.values() if s is not None]
            if not valid_scores:
                return 0.0
            
            return min(valid_scores)
        except Exception as e:
            raise AggregationError(f"Minimum aggregation failed: {str(e)}")
    
    @property
    def strategy_name(self) -> str:
        """Return the strategy name."""
        return "minimum"


class HarmonicMeanStrategy(AggregationStrategy):
    """
    Harmonic mean aggregation strategy.
    
    Computes the weighted harmonic mean of signal scores.
    This strategy heavily penalizes low scores.
    
    Formula: final_score = Σ(weights) / Σ(weight / score)
    """
    
    def aggregate(
        self,
        signal_scores: Dict[str, float],
        signal_weights: Dict[str, float],
    ) -> float:
        """
        Aggregate using harmonic mean.
        
        Args:
            signal_scores: Dictionary mapping signal names to scores
            signal_weights: Dictionary mapping signal names to weights
            
        Returns:
            Harmonic mean score
        """
        if not signal_scores:
            return 0.0
        
        try:
            total_weight = 0.0
            weighted_inverse_sum = 0.0
            
            for signal_name, score in signal_scores.items():
                if score is None or score <= 0.0:
                    continue
                
                weight = signal_weights.get(signal_name, 1.0)
                weighted_inverse_sum += weight / score
                total_weight += weight
            
            if total_weight == 0.0 or weighted_inverse_sum == 0.0:
                return 0.0
            
            return total_weight / weighted_inverse_sum
        except Exception as e:
            raise AggregationError(f"Harmonic mean aggregation failed: {str(e)}")
    
    @property
    def strategy_name(self) -> str:
        """Return the strategy name."""
        return "harmonic_mean"


def get_strategy(strategy_name: AggregationStrategy) -> AggregationStrategy:
    """
    Factory function to get an aggregation strategy by name.
    
    Args:
        strategy_name: Name of the strategy
        
    Returns:
        AggregationStrategy instance
        
    Raises:
        AggregationError: If strategy name is unknown
    """
    strategies = {
        "weighted_sum": WeightedSumStrategy(),
        "geometric_mean": GeometricMeanStrategy(),
        "maximum": MaximumStrategy(),
        "minimum": MinimumStrategy(),
        "harmonic_mean": HarmonicMeanStrategy(),
    }
    
    if strategy_name not in strategies:
        raise AggregationError(f"Unknown aggregation strategy: {strategy_name}")
    
    return strategies[strategy_name]
