# Memory Classification Engine Architecture

## Overview

The Memory Classification Engine is a production-grade cognitive infrastructure component that classifies incoming memories into cognitive memory types using a hybrid approach (rule-based + embeddings + LLM + ML). It sits between the Attention Engine and persistence layers, ensuring intelligent memory organization without duplication.

## Design Principles

- **SOLID Principles**: Single responsibility, open/closed, Liskov substitution, interface segregation, dependency inversion
- **Clean Architecture**: Domain logic independent of frameworks, databases, and external services
- **Domain-Driven Design**: Bounded contexts, ubiquitous language, domain models
- **Dependency Inversion**: Depend on abstractions, not concrete implementations
- **Multi-Label Classification**: Each memory can belong to multiple types with confidence scores
- **Extensibility**: Interface-based design allows swapping classifiers without changing core logic
- **Horizontal Scalability**: Stateless design for distributed deployment
- **Multi-Tenancy**: Tenant isolation with configurable resource quotas

## Folder Structure

```
d:\lamb\memory_classification\
├── __init__.py
├── core\
│   ├── __init__.py
│   ├── types.py                    # Enum definitions (MemoryType, ClassificationMethod)
│   ├── exceptions.py               # Custom exceptions
│   ├── interfaces.py              # Core interfaces (MemoryClassifier, ClassificationResult)
│   ├── models.py                  # Pydantic models (UniversalMemoryObject, ClassificationResult)
│   ├── engine.py                  # Main ClassificationEngine orchestrator
│   └── router.py                  # MemoryRouter for routing without duplication
├── classifiers\
│   ├── __init__.py
│   ├── base.py                    # BaseClassifier abstract class
│   ├── identity.py                # IdentityMemory classifier
│   ├── goal.py                    # GoalMemory classifier
│   ├── preference.py              # PreferenceMemory classifier
│   ├── relationship.py            # RelationshipMemory classifier
│   ├── project.py                 # ProjectMemory classifier
│   ├── skill.py                   # SkillMemory classifier
│   ├── procedural.py              # ProceduralMemory classifier
│   ├── task.py                    # TaskMemory classifier
│   ├── episodic.py                # EpisodicMemory classifier
│   ├── semantic.py                # SemanticMemory classifier
│   ├── emotional.py               # EmotionalMemory classifier
│   └── temporal.py                # TemporalMemory classifier
├── registry\
│   ├── __init__.py
│   ├── memory_type_registry.py    # Registry pattern for memory types
│   └── classifier_registry.py     # Registry for classifier instances
├── infrastructure\
│   ├── __init__.py
│   ├── logging.py                 # Structured logging with JSON formatting
│   ├── telemetry.py               # OpenTelemetry integration
│   ├── container.py               # Dependency injection container
│   ├── cache.py                   # Redis cache for classification results
│   └── embeddings.py              # Embedding service for semantic similarity
├── config\
│   ├── __init__.py
│   ├── defaults.py                # Default configuration
│   └── settings.py                # Configuration re-exports
├── api\
│   ├── __init__.py
│   ├── endpoints.py               # FastAPI endpoints
│   └── models.py                  # API request/response models
└── utils\
    ├── __init__.py
    ├── text_processing.py        # Text processing utilities
    └── similarity.py              # Similarity computation utilities

tests\
├── unit\
│   └── memory_classification\
│       ├── __init__.py
│       ├── test_classifiers.py    # Tests for individual classifiers
│       ├── test_engine.py         # Tests for ClassificationEngine
│       ├── test_router.py         # Tests for MemoryRouter
│       ├── test_registry.py       # Tests for registries
│       └── test_models.py         # Tests for Pydantic models
└── benchmarks\
    └── memory_classification\
        ├── __init__.py
        ├── load_test.py           # Load testing
        ├── latency_test.py        # Latency testing
        └── quality_benchmark.py   # Quality benchmarking

docs\
└── memory_classification\
    ├── ARCHITECTURE.md           # This file
    ├── CLASS_DIAGRAM.md          # Class diagram documentation
    ├── MULTI_TENANT.md           # Multi-tenant strategy
    ├── SCALABILITY.md            # Scalability strategy
    └── FAILURE_HANDLING.md       # Failure handling strategies
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Attention Engine                             │
│                    (Input: AttentionVector)                      │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Memory Classification Engine                    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              ClassificationEngine (Orchestrator)          │  │
│  │  + classify(memory_input) -> ClassificationResult        │  │
│  │  + batch_classify(inputs) -> List[ClassificationResult]   │  │
│  └───────────────────────┬──────────────────────────────────┘  │
│                          │                                       │
│          ┌───────────────┼───────────────┐                     │
│          ▼               ▼               ▼                     │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐         │
│  │  Classifier   │ │  Classifier   │ │  Classifier   │         │
│  │  Registry     │ │  Router       │ │  Engine       │         │
│  └───────────────┘ └───────────────┘ └───────────────┘         │
│          │               │               │                       │
│          └───────────────┼───────────────┘                       │
│                          ▼                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Memory Classifiers (12 types)                 │  │
│  │  Identity, Goal, Preference, Relationship, Project,       │  │
│  │  Skill, Procedural, Task, Episodic, Semantic, Emotional,  │  │
│  │  Temporal                                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Universal Memory Object                         │
│  + id: str                                                       │
│  + content: str                                                  │
│  + memory_types: List[MemoryType]                               │
│  + confidence_scores: Dict[MemoryType, float]                  │
│  + reasoning: Dict[MemoryType, str]                             │
│  + metadata: Dict[str, Any]                                     │
│  + tenant_id: str                                               │
│  + timestamp: float                                             │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Persistence Layer                           │
│              (ChromaDB, PostgreSQL, etc.)                        │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Core Interfaces

**MemoryClassifier Interface**
```python
class MemoryClassifier(ABC):
    @abstractmethod
    async def classify(self, memory_input: MemoryInput) -> ClassificationResult:
        """Classify memory input into memory types."""
        pass
    
    @abstractmethod
    def get_supported_types(self) -> List[MemoryType]:
        """Return list of memory types this classifier handles."""
        pass
```

**ClassificationResult**
```python
class ClassificationResult(BaseModel):
    memory_types: List[MemoryType]
    confidence_scores: Dict[MemoryType, float]
    reasoning: Dict[MemoryType, str]
    metadata: Dict[str, Any]
    computation_time_ms: float
```

### 2. Universal Memory Object

**UniversalMemoryObject**
```python
class UniversalMemoryObject(BaseModel):
    id: str
    content: str
    memory_types: List[MemoryType]
    confidence_scores: Dict[MemoryType, float]
    reasoning: Dict[MemoryType, str]
    metadata: Dict[str, Any]
    tenant_id: str
    session_id: str
    agent_id: str
    timestamp: float
    attention_vector: Optional[AttentionVector]
```

### 3. Memory Type Registry

Registry pattern for managing memory types and their metadata:
- Type definitions
- Type-specific schemas
- Type validation rules
- Type-specific storage policies

### 4. Memory Router

Routes classified memories to appropriate storage locations:
- Deduplication logic
- Multi-label routing
- Storage policy enforcement
- Tenant isolation

### 5. Classification Engine

Main orchestrator that:
- Coordinates multiple classifiers
- Merges classification results
- Applies confidence thresholds
- Generates final classification
- Routes to storage

## Memory Types

### 1. IdentityMemory
- Personal identity information (name, age, location)
- Self-referential statements
- Personal attributes

### 2. GoalMemory
- Goals, objectives, targets
- Desired outcomes
- Achievement criteria

### 3. PreferenceMemory
- Likes, dislikes, preferences
- Choices and decisions
- Personal tastes

### 4. RelationshipMemory
- Social relationships
- Interpersonal connections
- Group memberships

### 5. ProjectMemory
- Project information
- Work assignments
- Collaborative efforts

### 6. SkillMemory
- Skills, abilities, competencies
- Learning progress
- Expertise areas

### 7. ProceduralMemory
- How-to procedures
- Step-by-step processes
- Methodologies

### 8. TaskMemory
- Tasks, to-dos, action items
- Task states and progress
- Task dependencies

### 9. EpisodicMemory
- Specific events and experiences
- Time-bound occurrences
- Contextual situations

### 10. SemanticMemory
- General knowledge
- Facts and concepts
- Declarative information

### 11. EmotionalMemory
- Emotional experiences
- Mood states
- Affective reactions

### 12. TemporalMemory
- Time-related information
- Schedules, deadlines
- Temporal patterns

## Classification Methods

### 1. Rule-Based Classification
- Pattern matching
- Keyword detection
- Heuristic rules
- Fast, deterministic

### 2. Embedding-Based Classification
- Semantic similarity
- Vector embeddings
- Clustering
- Context-aware

### 3. LLM-Based Classification
- Natural language understanding
- Contextual reasoning
- Complex pattern recognition
- Higher accuracy, slower

### 4. ML-Based Classification
- Trained models
- Feature extraction
- Predictive classification
- Scalable, requires training

## Performance Targets

- **Latency**: P50 < 10ms, P95 < 25ms, P99 < 50ms
- **Throughput**: > 10,000 classifications/second
- **Scalability**: Support millions of memories, thousands of tenants
- **Accuracy**: > 85% classification accuracy on benchmark dataset
- **Availability**: 99.9% uptime

## Multi-Tenancy

- Tenant isolation at all levels
- Per-tenant configuration
- Resource quotas and limits
- Tenant-specific classifiers
- Isolated storage namespaces

## Failure Handling

- Graceful degradation
- Circuit breakers for external services
- Retry logic with exponential backoff
- Fallback to rule-based classification
- Comprehensive error logging
- Dead letter queue for failed classifications

## Extensibility

- Interface-based classifier design
- Plugin architecture for new classifiers
- Configuration-driven behavior
- Versioned classifier schemas
- Backward compatibility guarantees
