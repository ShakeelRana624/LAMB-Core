"""
Main Attention Engine facade.

This module provides the main interface for the Attention Engine,
orchestrating signal computation, aggregation, and storage decisions.
"""

import asyncio
import time
from typing import Dict, List, Optional
from datetime import datetime

from attention.core.interfaces import (
    AttentionSignal,
    AttentionContext,
    AttentionResult,
)
from attention.core.models import AttentionVector, AttentionConfig
from attention.core.exceptions import AttentionEngineError, SignalNotFoundError
from attention.core.types import SignalName
from attention.aggregation.aggregator import AttentionAggregator
from attention.infrastructure.logging import AttentionLogger
from attention.infrastructure.telemetry import TelemetryManager
from attention.infrastructure.cache import RedisCache
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


class AttentionEngine:
    """
    Main Attention Engine facade.
    
    Orchestrates the entire attention computation pipeline:
    1. Signal registration and management
    2. Parallel signal computation
    3. Aggregation of signal results
    4. Storage decision based on threshold
    5. Logging and telemetry
    
    This is the primary entry point for the Attention Engine.
    """
    
    def __init__(self, config: Optional[AttentionConfig] = None):
        """
        Initialize the Attention Engine.
        
        Args:
            config: Attention configuration (uses defaults if None)
        """
        from attention.config.defaults import get_default_config
        
        self.config = config or get_default_config()
        self.aggregator = AttentionAggregator(self.config)
        self.logger = AttentionLogger(self.config)
        self.telemetry = TelemetryManager(
            service_name="lamb-attention",
            enable_telemetry=self.config.enable_telemetry,
        )
        self.cache = RedisCache(
            ttl_seconds=self.config.cache_ttl_seconds,
            enable_cache=self.config.enable_caching,
        )
        
        # Signal registry
        self._signals: Dict[str, AttentionSignal] = {}
        
        # Register default signals
        self._register_default_signals()
    
    def _register_default_signals(self) -> None:
        """Register all default attention signals."""
        signal_classes = {
            SignalName.NOVELTY.value: NoveltySignal,
            SignalName.GOAL_RELEVANCE.value: GoalRelevanceSignal,
            SignalName.URGENCY.value: UrgencySignal,
            SignalName.REWARD.value: RewardSignal,
            SignalName.RISK.value: RiskSignal,
            SignalName.EMOTION.value: EmotionSignal,
            SignalName.CURIOSITY.value: CuriositySignal,
            SignalName.SURPRISE.value: SurpriseSignal,
            SignalName.CONFIDENCE.value: ConfidenceSignal,
            SignalName.FUTURE_UTILITY.value: FutureUtilitySignal,
            SignalName.SOCIAL_IMPORTANCE.value: SocialImportanceSignal,
            SignalName.REPETITION.value: RepetitionSignal,
            SignalName.CURRENT_TASK_MATCH.value: CurrentTaskMatchSignal,
        }
        
        for signal_name, signal_class in signal_classes.items():
            signal_config = self.config.get_signal_config(signal_name)
            signal = signal_class(
                weight=signal_config.weight,
                enabled=signal_config.enabled,
                **signal_config.parameters,
            )
            self.register_signal(signal)
    
    def register_signal(self, signal: AttentionSignal) -> None:
        """
        Register an attention signal.
        
        Args:
            signal: Attention signal to register
        """
        self._signals[signal.signal_name] = signal
    
    def unregister_signal(self, signal_name: str) -> None:
        """
        Unregister an attention signal.
        
        Args:
            signal_name: Name of the signal to unregister
            
        Raises:
            SignalNotFoundError: If signal not found
        """
        if signal_name not in self._signals:
            raise SignalNotFoundError(signal_name)
        del self._signals[signal_name]
    
    def get_signal(self, signal_name: str) -> AttentionSignal:
        """
        Get a registered attention signal.
        
        Args:
            signal_name: Name of the signal
            
        Returns:
            Attention signal instance
            
        Raises:
            SignalNotFoundError: If signal not found
        """
        if signal_name not in self._signals:
            raise SignalNotFoundError(signal_name)
        return self._signals[signal_name]
    
    def list_signals(self) -> List[str]:
        """
        List all registered signal names.
        
        Returns:
            List of signal names
        """
        return list(self._signals.keys())
    
    async def compute_attention(
        self,
        context: AttentionContext,
    ) -> AttentionVector:
        """
        Compute attention for a given context.
        
        This is the main entry point for attention computation.
        It orchestrates:
        1. Parallel signal computation
        2. Result aggregation
        3. Storage decision
        
        Args:
            context: Attention context
            
        Returns:
            Complete attention vector with all signal results
            
        Raises:
            AttentionEngineError: If computation fails
        """
        start_time = time.perf_counter()
        
        # Initialize attention vector
        vector = AttentionVector(
            session_id=context.session_id,
            agent_id=context.agent_id,
        )
        
        try:
            # Compute all enabled signals
            if self.config.parallel_execution:
                signal_results = await self._compute_signals_parallel(context)
            else:
                signal_results = await self._compute_signals_sequential(context)
            
            # Populate vector with results
            for signal_name, result in signal_results.items():
                vector.set_signal_result(signal_name, result.to_dict())
                
                # Log signal computation
                if self.config.log_computation_times:
                    self.logger.log_signal_computation(
                        signal_name=signal_name,
                        score=result.score,
                        computation_time_ms=result.computation_time_ms,
                        session_id=context.session_id,
                        agent_id=context.agent_id,
                    )
            
            # Aggregate results
            vector = self.aggregator.finalize_vector(vector)
            
            # Log aggregation
            if self.config.log_computation_times:
                self.logger.log_aggregation(
                    aggregated_score=vector.aggregated_score,
                    should_store=vector.should_store,
                    computation_time_ms=vector.computation_time_ms,
                    session_id=context.session_id,
                    agent_id=context.agent_id,
                )
            
            # Update computation time
            end_time = time.perf_counter()
            vector.computation_time_ms = (end_time - start_time) * 1000
            
            return vector
            
        except Exception as e:
            self.logger.log_error(
                error=e,
                context={"context": str(context)},
                session_id=context.session_id,
                agent_id=context.agent_id,
            )
            raise AttentionEngineError(f"Attention computation failed: {str(e)}")
    
    async def _compute_signals_parallel(
        self,
        context: AttentionContext,
    ) -> Dict[str, AttentionResult]:
        """
        Compute all enabled signals in parallel.
        
        Args:
            context: Attention context
            
        Returns:
            Dictionary mapping signal names to results
        """
        # Get enabled signals
        enabled_signals = [
            (name, signal)
            for name, signal in self._signals.items()
            if signal.is_enabled()
        ]
        
        # Limit concurrent signals if configured
        max_concurrent = self.config.max_concurrent_signals
        if len(enabled_signals) > max_concurrent:
            # Process in batches
            results = {}
            for i in range(0, len(enabled_signals), max_concurrent):
                batch = enabled_signals[i:i + max_concurrent]
                batch_results = await asyncio.gather(
                    *[self._compute_single_signal(signal, context) for _, signal in batch],
                    return_exceptions=True,
                )
                for (name, _), result in zip(batch, batch_results):
                    if isinstance(result, Exception):
                        # Log error but continue
                        self.logger.log_error(
                            error=result,
                            context={"signal_name": name},
                            session_id=context.session_id,
                            agent_id=context.agent_id,
                        )
                    else:
                        results[name] = result
            return results
        else:
            # Process all at once
            results = await asyncio.gather(
                *[self._compute_single_signal(signal, context) for _, signal in enabled_signals],
                return_exceptions=True,
            )
            signal_results = {}
            for (name, _), result in zip(enabled_signals, results):
                if isinstance(result, Exception):
                    self.logger.log_error(
                        error=result,
                        context={"signal_name": name},
                        session_id=context.session_id,
                        agent_id=context.agent_id,
                    )
                else:
                    signal_results[name] = result
            return signal_results
    
    async def _compute_signals_sequential(
        self,
        context: AttentionContext,
    ) -> Dict[str, AttentionResult]:
        """
        Compute all enabled signals sequentially.
        
        Args:
            context: Attention context
            
        Returns:
            Dictionary mapping signal names to results
        """
        signal_results = {}
        
        for name, signal in self._signals.items():
            if not signal.is_enabled():
                continue
            
            try:
                result = await self._compute_single_signal(signal, context)
                signal_results[name] = result
            except Exception as e:
                self.logger.log_error(
                    error=e,
                    context={"signal_name": name},
                    session_id=context.session_id,
                    agent_id=context.agent_id,
                )
        
        return signal_results
    
    async def _compute_single_signal(
        self,
        signal: AttentionSignal,
        context: AttentionContext,
    ) -> AttentionResult:
        """
        Compute a single signal with caching and telemetry.
        
        Args:
            signal: Attention signal to compute
            context: Attention context
            
        Returns:
            Attention result
        """
        # Check cache
        if self.config.enable_caching:
            cached = self.cache.get(
                signal_name=signal.signal_name,
                input_text=context.input_text,
                context=context.metadata,
            )
            if cached:
                return AttentionResult(**cached)
        
        # Compute with telemetry
        if self.config.enable_telemetry:
            decorated = self.telemetry.trace_signal_computation(signal.signal_name)(
                signal.compute_with_timing
            )
        else:
            decorated = signal.compute_with_timing
        
        result = await decorated(context)
        
        # Cache result
        if self.config.enable_caching:
            self.cache.set(
                signal_name=signal.signal_name,
                input_text=context.input_text,
                context=context.metadata,
                value=result.to_dict(),
            )
        
        return result
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get engine statistics.
        
        Returns:
            Dictionary with engine statistics
        """
        return {
            "aggregator": self.aggregator.get_statistics(),
            "cache": self.cache.get_stats(),
            "registered_signals": len(self._signals),
            "enabled_signals": sum(1 for s in self._signals.values() if s.is_enabled()),
            "config": {
                "aggregation_strategy": self.config.aggregation_strategy,
                "storage_threshold": self.config.storage_threshold,
                "parallel_execution": self.config.parallel_execution,
                "enable_caching": self.config.enable_caching,
                "enable_telemetry": self.config.enable_telemetry,
            },
        }
    
    def update_config(self, config: AttentionConfig) -> None:
        """
        Update the engine configuration.
        
        Args:
            config: New configuration
        """
        self.config = config
        self.aggregator = AttentionAggregator(config)
        self.logger = AttentionLogger(config)
        
        # Re-register signals with new config
        self._signals.clear()
        self._register_default_signals()
