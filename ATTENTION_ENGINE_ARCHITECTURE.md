# LAMB Attention Engine - Architectural Design Document

## Executive Summary

The Attention Engine is a neuroscience-inspired subsystem that computes multi-dimensional attention signals before memory storage. It serves as the cognitive gatekeeper for the LAMB Cognitive Operating System, determining which information deserves persistent storage based on 13 distinct attention signals.

## Design Principles

1. **SOLID Compliance**: Single responsibility, open/closed, Liskov substitution, interface segregation, dependency inversion
2. **Pluggable Architecture**: Every attention signal is independently swappable
3. **Horizontal Scalability**: Stateless signal computation, cache-friendly
4. **Observability**: Structured logging + OpenTelemetry tracing throughout
5. **Type Safety**: Comprehensive typing with mypy compatibility
6. **Configuration-Driven**: All weights and thresholds externally configurable
7. **Future-Proof**: Interface design supports ML model substitution without code changes

## Proposed Folder Structure

```
lamb/
├── attention/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── interfaces.py          # Base interfaces (AttentionSignal, AttentionResult)
│   │   ├── models.py              # Pydantic models (AttentionVector, AttentionConfig)
│   │   ├── exceptions.py          # Custom exceptions
│   │   └── types.py               # Type aliases and enums
│   ├── signals/
│   │   ├── __init__.py
│   │   ├── base.py                # Abstract base implementation
│   │   ├── novelty.py             # Novelty signal
│   │   ├── goal_relevance.py      # Goal Relevance signal
│   │   ├── urgency.py             # Urgency signal
│   │   ├── reward.py              # Reward signal
│   │   ├── risk.py                # Risk signal
│   │   ├── emotion.py             # Emotion signal
│   │   ├── curiosity.py           # Curiosity signal
│   │   ├── surprise.py            # Surprise signal
│   │   ├── confidence.py          # Confidence signal
│   │   ├── future_utility.py      # Future Utility signal
│   │   ├── social_importance.py   # Social Importance signal
│   │   ├── repetition.py          # Repetition signal
│   │   └── current_task_match.py  # Current Task Match signal
│   ├── aggregation/
│   │   ├── __init__.py
│   │   ├── aggregator.py          # Attention Aggregator
│   │   └── strategies.py          # Aggregation strategies (weighted, geometric, etc.)
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── container.py           # Dependency injection container
│   │   ├── logging.py             # Structured logging setup
│   │   ├── telemetry.py           # OpenTelemetry instrumentation
│   │   └── cache.py               # Redis cache integration
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py            # Pydantic settings
│   │   └── defaults.py            # Default configurations
│   └── api/
│       ├── __init__.py
│       └── endpoints.py           # FastAPI endpoints
├── tests/
│   ├── unit/
│   │   ├── attention/
│   │   │   ├── test_signals/
│   │   │   ├── test_aggregation/
│   │   │   └── test_infrastructure/
│   ├── integration/
│   │   └── attention/
│   └── benchmarks/
│       └── attention/
└── docs/
    └── attention/
        ├── CLASS_DIAGRAM.md
        ├── API_REFERENCE.md
        └── PERFORMANCE_GUIDE.md
```

## Class Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    AttentionSignal (ABC)                         │
│  + compute(context: AttentionContext) -> AttentionResult        │
│  + get_weight() -> float                                        │
│  + is_enabled() -> bool                                         │
└─────────────────────────────────────────────────────────────────┘
                              △
                              │ implements
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ NoveltySignal │    │  UrgencySignal │    │ RewardSignal  │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    (13 signal implementations)

┌─────────────────────────────────────────────────────────────────┐
│                  AttentionResult (Pydantic)                      │
│  + score: float (0.0 - 1.0)                                     │
│  + explanation: str                                             │
│  + metadata: dict[str, Any]                                     │
│  + computation_time_ms: float                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  AttentionVector (Pydantic)                      │
│  + novelty: AttentionResult                                     │
│  + goal_relevance: AttentionResult                              │
│  + urgency: AttentionResult                                     │
│  + ... (13 signals)                                             │
│  + aggregated_score: float                                       │
│  + should_store: bool                                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  AttentionContext (Pydantic)                      │
│  + input_text: str                                              │
│  + session_id: str                                              │
│  + agent_id: str                                                │
│  + current_goal: Optional[str]                                 │
│  + current_task: Optional[str]                                  │
│  + temporal_context: TemporalContext                            │
│  + social_context: SocialContext                                │
│  + metadata: dict[str, Any]                                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                AttentionAggregator                               │
│  - strategy: AggregationStrategy                                 │
│  - signal_weights: dict[str, float]                              │
│  + aggregate(vector: AttentionVector) -> float                    │
│  + should_store(score: float) -> bool                            │
└─────────────────────────────────────────────────────────────────┘
                              △
                              │ implements
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│WeightedStrategy│    │GeometricStrategy│   │MaxStrategy    │
└───────────────┘    └───────────────┘    └───────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                AttentionEngine (Facade)                          │
│  - signal_registry: SignalRegistry                               │
│  - aggregator: AttentionAggregator                               │
│  - config: AttentionConfig                                      │
│  + compute_attention(context: AttentionContext) -> AttentionVector│
│  + register_signal(signal: AttentionSignal) -> None             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                DIContainer                                        │
│  + register[T](factory: Callable[..., T]) -> None                │
│  + resolve[T]() -> T                                             │
│  + register_singleton[T](instance: T) -> None                   │
└─────────────────────────────────────────────────────────────────┘
```

## Interface Definitions

### AttentionSignal Interface

```python
from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass

@dataclass
class AttentionContext:
    """Context provided to all attention signals."""
    input_text: str
    session_id: str
    agent_id: str
    current_goal: Optional[str] = None
    current_task: Optional[str] = None
    temporal_context: Optional["TemporalContext"] = None
    social_context: Optional["SocialContext"] = None
    metadata: dict = None

@dataclass
class AttentionResult:
    """Result from a single attention signal."""
    score: float  # Normalized 0.0 - 1.0
    explanation: str
    metadata: dict = None
    computation_time_ms: float = 0.0
    signal_name: str = ""

class AttentionSignal(ABC):
    """Base interface for all attention signals."""
    
    @abstractmethod
    async def compute(self, context: AttentionContext) -> AttentionResult:
        """Compute the attention signal score."""
        pass
    
    @abstractmethod
    def get_weight(self) -> float:
        """Return the configured weight for this signal."""
        pass
    
    @abstractmethod
    def is_enabled(self) -> bool:
        """Return whether this signal is enabled."""
        pass
    
    @property
    @abstractmethod
    def signal_name(self) -> str:
        """Return the unique name of this signal."""
        pass
```

## Signal Specifications

### Core Signals (High Priority)

1. **NoveltySignal**: Measures how different the input is from recent memories
   - Uses cosine distance from recent embeddings
   - Higher novelty = more attention
   - Weight: 0.15

2. **GoalRelevanceSignal**: Measures alignment with current agent goals
   - Semantic similarity to goal statement
   - Goal hierarchy support (primary, secondary, tertiary)
   - Weight: 0.12

3. **UrgencySignal**: Detects time-sensitive information
   - Pattern matching for temporal keywords (deadline, asap, urgent)
   - Temporal extraction (dates, times)
   - Weight: 0.10

4. **RewardSignal**: Detects positive outcomes or achievements
   - Pattern matching for success indicators
   - Sentiment analysis for positive sentiment
   - Weight: 0.08

5. **RiskSignal**: Detects potential threats or negative outcomes
   - Pattern matching for risk indicators
   - Sentiment analysis for negative sentiment
   - Weight: 0.10

### Secondary Signals (Medium Priority)

6. **EmotionSignal**: Detects emotional content
   - Emotion classification (joy, anger, fear, sadness, surprise)
   - Intensity scoring
   - Weight: 0.07

7. **CuriositySignal**: Measures information gap or learning opportunity
   - Question detection
   - Uncertainty indicators
   - Weight: 0.05

8. **SurpriseSignal**: Detects unexpected information
   - Bayesian surprise calculation
   - Deviation from expected patterns
   - Weight: 0.06

9. **ConfidenceSignal**: Measures certainty level of the information
   - Hedge word detection (maybe, possibly, probably)
   - Certainty language analysis
   - Weight: 0.04

### Tertiary Signals (Contextual)

10. **FutureUtilitySignal**: Predicts future usefulness
    - Pattern matching for planning language
    - Reference to future events
    - Weight: 0.08

11. **SocialImportanceSignal**: Detects socially relevant information
    - Entity recognition (people, organizations)
    - Social relationship indicators
    - Weight: 0.05

12. **RepetitionSignal**: Detects recurring information
    - Frequency analysis across session
    - Reinforcement pattern detection
    - Weight: 0.06

13. **CurrentTaskMatchSignal**: Measures alignment with active task
    - Task similarity calculation
    - Subtask hierarchy support
    - Weight: 0.09

## Aggregation Strategies

### Weighted Sum (Default)
```
final_score = Σ(signal_score × signal_weight)
```

### Geometric Mean
```
final_score = (Π signal_score^weight)^(1/Σweight)
```

### Maximum
```
final_score = max(signal_scores)
```

### Custom ML Model
```
final_score = ml_model.predict(signal_vector)
```

## Configuration Model

```python
from pydantic import BaseModel, Field
from typing import Dict, Optional

class SignalConfig(BaseModel):
    """Configuration for a single attention signal."""
    enabled: bool = True
    weight: float = Field(ge=0.0, le=1.0)
    threshold: float = Field(ge=0.0, le=1.0, default=0.0)
    parameters: Dict[str, Any] = Field(default_factory=dict)

class AttentionConfig(BaseModel):
    """Global attention engine configuration."""
    signals: Dict[str, SignalConfig] = Field(default_factory=dict)
    aggregation_strategy: str = "weighted_sum"
    storage_threshold: float = Field(ge=0.0, le=1.0, default=0.5)
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    enable_telemetry: bool = True
    enable_logging: bool = True
    log_level: str = "INFO"
```

## Performance Considerations

### Latency Budget
- Target: < 50ms per attention computation
- Signal computation: < 5ms per signal
- Aggregation: < 5ms
- Total: 13 signals × 5ms + 5ms = 70ms (with parallel execution: < 50ms)

### Optimization Strategies
1. **Parallel Signal Execution**: asyncio.gather for independent signals
2. **Caching**: Redis cache for expensive computations (novelty, goal relevance)
3. **Batch Processing**: Vectorized operations where possible
4. **Lazy Loading**: Load ML models on-demand
5. **Connection Pooling**: Reuse database/external service connections

### Horizontal Scaling
- Stateless signal computation
- Shared Redis cache
- Load balancer distribution
- Circuit breakers for external dependencies

## Future Extension Strategy

### Phase 1: Rule-Based (Current)
- Pattern matching
- Heuristic scoring
- Configurable weights

### Phase 2: Hybrid
- ML models for specific signals (emotion, sentiment)
- Ensemble approaches
- A/B testing framework

### Phase 3: Neural
- End-to-end attention model
- Reinforcement learning for weight optimization
- Online learning from user feedback

### Extension Points
1. **Custom Signals**: Implement AttentionSignal interface
2. **Custom Aggregators**: Implement AggregationStrategy interface
3. **ML Models**: Swap rule-based for ML without interface changes
4. **External Services**: Hook in external APIs for specialized computation
