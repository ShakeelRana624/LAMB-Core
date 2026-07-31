"""
Attention Aggregator.

Combines individual attention signal scores into a final
attention score using configurable aggregation strategies.
"""

from typing import Dict, Optional
import time

from attention.core.models import AttentionVector, AttentionConfig
from attention.core.types import AggregationStrategy
from attention.core.exceptions import AggregationError
from attention.aggregation.strategies import get_strategy


class AttentionAggregator:
    """
    Aggregates attention signal scores into a final attention score.
    
    This class is responsible for:
    - Combining individual signal scores using a strategy
    - Applying signal weights
    - Determining whether to store based on threshold
    - Providing aggregation statistics
    """
    
    def __init__(self, config: AttentionConfig):
        """
        Initialize the attention aggregator.
        
        Args:
            config: Attention configuration
        """
        self.config = config
        self.strategy = get_strategy(config.aggregation_strategy)
        self._aggregation_count = 0
        self._aggregation_times = []
    
    def aggregate(self, vector: AttentionVector) -> float:
        """
        Aggregate signal scores into a final attention score.
        
        Args:
            vector: Attention vector with individual signal scores
            
        Returns:
            Aggregated attention score between 0.0 and 1.0
            
        Raises:
            AggregationError: If aggregation fails
        """
        start_time = time.perf_counter()
        
        try:
            # Extract signal scores from vector
            signal_scores = self._extract_signal_scores(vector)
            
            # Get signal weights from config
            signal_weights = self._extract_signal_weights()
            
            # Apply aggregation strategy
            aggregated_score = self.strategy.aggregate(signal_scores, signal_weights)
            
            # Clamp to valid range
            aggregated_score = max(0.0, min(1.0, aggregated_score))
            
            # Track statistics
            end_time = time.perf_counter()
            aggregation_time_ms = (end_time - start_time) * 1000
            self._aggregation_count += 1
            self._aggregation_times.append(aggregation_time_ms)
            
            # Keep only last 1000 aggregation times
            if len(self._aggregation_times) > 1000:
                self._aggregation_times = self._aggregation_times[-1000:]
            
            return aggregated_score
            
        except Exception as e:
            raise AggregationError(f"Aggregation failed: {str(e)}")
    
    def should_store(self, score: float) -> bool:
        """
        Determine whether to store based on aggregated score.
        
        Args:
            score: Aggregated attention score
            
        Returns:
            True if score exceeds storage threshold
        """
        return score >= self.config.storage_threshold
    
    def finalize_vector(self, vector: AttentionVector) -> AttentionVector:
        """
        Finalize an attention vector by computing aggregated score.
        
        Args:
            vector: Attention vector with individual signal scores
            
        Returns:
            Attention vector with aggregated score and storage decision
        """
        # Compute aggregated score
        aggregated_score = self.aggregate(vector)
        
        # Update vector
        vector.aggregated_score = aggregated_score
        vector.should_store = self.should_store(aggregated_score)
        
        return vector
    
    def _extract_signal_scores(self, vector: AttentionVector) -> Dict[str, float]:
        """
        Extract signal scores from attention vector.
        
        Args:
            vector: Attention vector
            
        Returns:
            Dictionary mapping signal names to scores
        """
        signal_scores = {}
        
        # Extract from signal_results
        for signal_name, result in vector.signal_results.items():
            if result and "score" in result:
                signal_scores[signal_name] = result["score"]
        
        # Also check direct fields
        for signal_name in ["novelty", "goal_relevance", "urgency", "reward", "risk",
                           "emotion", "curiosity", "surprise", "confidence",
                           "future_utility", "social_importance", "repetition",
                           "current_task_match"]:
            score = getattr(vector, signal_name, None)
            if score is not None and signal_name not in signal_scores:
                signal_scores[signal_name] = score
        
        return signal_scores
    
    def _extract_signal_weights(self) -> Dict[str, float]:
        """
        Extract signal weights from configuration.
        
        Returns:
            Dictionary mapping signal names to weights
        """
        signal_weights = {}
        
        for signal_name, signal_config in self.config.signals.items():
            if signal_config.enabled:
                signal_weights[signal_name] = signal_config.weight
        
        return signal_weights
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get aggregation statistics.
        
        Returns:
            Dictionary with aggregation statistics
        """
        if not self._aggregation_times:
            return {
                "aggregation_count": 0,
                "avg_time_ms": 0.0,
                "min_time_ms": 0.0,
                "max_time_ms": 0.0,
            }
        
        return {
            "aggregation_count": self._aggregation_count,
            "avg_time_ms": sum(self._aggregation_times) / len(self._aggregation_times),
            "min_time_ms": min(self._aggregation_times),
            "max_time_ms": max(self._aggregation_times),
            "strategy": self.strategy.strategy_name,
        }
    
    def reset_statistics(self) -> None:
        """Reset aggregation statistics."""
        self._aggregation_count = 0
        self._aggregation_times = []
    
    def update_strategy(self, strategy_name: AggregationStrategy) -> None:
        """
        Update the aggregation strategy.
        
        Args:
            strategy_name: Name of the new strategy
        """
        self.strategy = get_strategy(strategy_name)
        self.config.aggregation_strategy = strategy_name
