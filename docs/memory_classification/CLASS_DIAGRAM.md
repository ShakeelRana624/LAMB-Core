# Memory Classification Engine - Class Diagram

## Core Interfaces

```
┌─────────────────────────────────────────────────────────────────┐
│                    MemoryClassifier (ABC)                        │
│  + classify(memory_input: MemoryInput) -> ClassificationResult │
│  + get_supported_types() -> List[MemoryType]                   │
│  + get_confidence_threshold() -> float                          │
└─────────────────────────────────────────────────────────────────┘
                              △
                              │
              ┌───────────────┼───────────────┐
              │               │               │
┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
│   BaseClassifier    │ │  RuleBasedClassifier│ │  EmbeddingClassifier│
│  + _normalize_score │ │  + _match_patterns  │ │  + _compute_similarity│
│  + _generate_reason │ │  + _extract_keywords│ │  + _get_embedding    │
└─────────────────────┘ └─────────────────────┘ └─────────────────────┘
```

## Data Models

```
┌─────────────────────────────────────────────────────────────────┐
│                      MemoryInput (Pydantic)                      │
│  + content: str                                                  │
│  + session_id: str                                              │
│  + agent_id: str                                                │
│  + tenant_id: str                                               │
│  + metadata: Dict[str, Any]                                     │
│  + attention_vector: Optional[AttentionVector]                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  ClassificationResult (Pydantic)                  │
│  + memory_types: List[MemoryType]                               │
│  + confidence_scores: Dict[MemoryType, float]                  │
│  + reasoning: Dict[MemoryType, str]                             │
│  + metadata: Dict[str, Any]                                     │
│  + computation_time_ms: float                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│               UniversalMemoryObject (Pydantic)                    │
│  + id: str                                                       │
│  + content: str                                                  │
│  + memory_types: List[MemoryType]                               │
│  + confidence_scores: Dict[MemoryType, float]                  │
│  + reasoning: Dict[MemoryType, str]                             │
│  + metadata: Dict[str, Any]                                     │
│  + tenant_id: str                                               │
│  + session_id: str                                              │
│  + agent_id: str                                                │
│  + timestamp: float                                             │
│  + attention_vector: Optional[AttentionVector]                  │
└─────────────────────────────────────────────────────────────────┘
```

## Memory Type Enum

```
┌─────────────────────────────────────────────────────────────────┐
│                      MemoryType (Enum)                           │
│  IDENTITY_MEMORY                                                 │
│  GOAL_MEMORY                                                     │
│  PREFERENCE_MEMORY                                               │
│  RELATIONSHIP_MEMORY                                             │
│  PROJECT_MEMORY                                                  │
│  SKILL_MEMORY                                                    │
│  PROCEDURAL_MEMORY                                               │
│  TASK_MEMORY                                                     │
│  EPISODIC_MEMORY                                                 │
│  SEMANTIC_MEMORY                                                 │
│  EMOTIONAL_MEMORY                                                │
│  TEMPORAL_MEMORY                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Classifier Implementations

```
┌─────────────────────────────────────────────────────────────────┐
│                    IdentityClassifier                            │
│  + classify(memory_input) -> ClassificationResult               │
│  + _detect_identity_info(text) -> float                          │
│  + _extract_identity_fields(text) -> Dict[str, str]              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      GoalClassifier                              │
│  + classify(memory_input) -> ClassificationResult               │
│  + _detect_goal_language(text) -> float                           │
│  + _extract_goal_attributes(text) -> Dict[str, Any]               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  PreferenceClassifier                             │
│  + classify(memory_input) -> ClassificationResult               │
│  + _detect_preference_language(text) -> float                     │
│  + _extract_preference_attributes(text) -> Dict[str, Any]          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                RelationshipClassifier                            │
│  + classify(memory_input) -> ClassificationResult               │
│  + _detect_relationship_language(text) -> float                  │
│  + _extract_relationship_attributes(text) -> Dict[str, Any]       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    ProjectClassifier                             │
│  + classify(memory_input) -> ClassificationResult               │
│  + _detect_project_language(text) -> float                       │
│  + _extract_project_attributes(text) -> Dict[str, Any]           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     SkillClassifier                              │
│  + classify(memory_input) -> ClassificationResult               │
│  + _detect_skill_language(text) -> float                         │
│  + _extract_skill_attributes(text) -> Dict[str, Any]             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  ProceduralClassifier                            │
│  + classify(memory_input) -> ClassificationResult               │
│  + _detect_procedural_language(text) -> float                    │
│  + _extract_procedural_attributes(text) -> Dict[str, Any]        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      TaskClassifier                              │
│  + classify(memory_input) -> ClassificationResult               │
│  + _detect_task_language(text) -> float                          │
│  + _extract_task_attributes(text) -> Dict[str, Any]               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   EpisodicClassifier                             │
│  + classify(memory_input) -> ClassificationResult               │
│  + _detect_episodic_language(text) -> float                      │
│  + _extract_episodic_attributes(text) -> Dict[str, Any]           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    SemanticClassifier                             │
│  + classify(memory_input) -> ClassificationResult               │
│  + _detect_semantic_language(text) -> float                     │
│  + _extract_semantic_attributes(text) -> Dict[str, Any]          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   EmotionalClassifier                            │
│  + classify(memory_input) -> ClassificationResult               │
│  + _detect_emotional_language(text) -> float                     │
│  + _extract_emotional_attributes(text) -> Dict[str, Any]        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    TemporalClassifier                             │
│  + classify(memory_input) -> ClassificationResult               │
│  + _detect_temporal_language(text) -> float                      │
│  + _extract_temporal_attributes(text) -> Dict[str, Any]          │
└─────────────────────────────────────────────────────────────────┘
```

## Core Engine Components

```
┌─────────────────────────────────────────────────────────────────┐
│                 ClassificationEngine                              │
│  - classifiers: Dict[MemoryType, MemoryClassifier]               │
│  - config: ClassificationConfig                                  │
│  - logger: ClassificationLogger                                  │
│  + classify(memory_input) -> ClassificationResult               │
│  + batch_classify(inputs) -> List[ClassificationResult]         │
│  + register_classifier(classifier)                              │
│  + unregister_classifier(memory_type)                            │
│  + get_statistics() -> Dict[str, Any]                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      MemoryRouter                                 │
│  - storage_backends: Dict[MemoryType, StorageBackend]            │
│  - deduplication_cache: DeduplicationCache                       │
│  + route(memory_object) -> List[StorageLocation]                │
│  + check_duplicate(memory_object) -> bool                       │
│  + get_storage_policy(memory_type) -> StoragePolicy             │
└─────────────────────────────────────────────────────────────────┘
```

## Registry Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│              MemoryTypeRegistry                                  │
│  - type_definitions: Dict[MemoryType, TypeDefinition]            │
│  + register_type(memory_type, definition)                       │
│  + get_type(memory_type) -> TypeDefinition                       │
│  + get_all_types() -> List[MemoryType]                          │
│  + validate_type(memory_type) -> bool                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              ClassifierRegistry                                  │
│  - classifiers: Dict[MemoryType, MemoryClassifier]               │
│  + register_classifier(classifier)                              │
│  + get_classifier(memory_type) -> MemoryClassifier               │
│  + get_all_classifiers() -> List[MemoryClassifier]               │
│  + unregister_classifier(memory_type)                            │
└─────────────────────────────────────────────────────────────────┘
```

## Infrastructure Components

```
┌─────────────────────────────────────────────────────────────────┐
│              ClassificationLogger                                │
│  + log_classification(result)                                   │
│  + log_error(error, context)                                    │
│  + log_statistics(stats)                                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              ClassificationTelemetry                              │
│  + trace_classification(memory_input, result)                   │
│  + record_metric(metric_name, value)                            │
│  + record_histogram(metric_name, value)                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              ClassificationContainer                             │
│  - services: Dict[str, Any]                                      │
│  + register(service_name, factory)                              │
│  + get(service_name) -> Any                                     │
│  + register_singleton(service_name, instance)                   │
└─────────────────────────────────────────────────────────────────┘
```

## Configuration Models

```
┌─────────────────────────────────────────────────────────────────┐
│              ClassificationConfig (Pydantic)                     │
│  + enable_caching: bool                                         │
│  + enable_telemetry: bool                                       │
│  + enable_logging: bool                                         │
│  + confidence_threshold: float                                  │
│  + max_concurrent_classifications: int                          │
│  + classifier_configs: Dict[MemoryType, ClassifierConfig]       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              ClassifierConfig (Pydantic)                         │
│  + enabled: bool                                                 │
│  + weight: float                                                │
│  + confidence_threshold: float                                  │
│  + method: ClassificationMethod                                  │
│  + parameters: Dict[str, Any]                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Type Definition

```
┌─────────────────────────────────────────────────────────────────┐
│              TypeDefinition                                      │
│  + memory_type: MemoryType                                      │
│  + schema: Dict[str, Any]                                       │
│  + validation_rules: List[ValidationRule]                        │
│  + storage_policy: StoragePolicy                                │
│  + metadata: Dict[str, Any]                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Classification Method Enum

```
┌─────────────────────────────────────────────────────────────────┐
│              ClassificationMethod (Enum)                          │
│  RULE_BASED                                                     │
│  EMBEDDING_BASED                                                │
│  LLM_BASED                                                      │
│  ML_BASED                                                       │
│  HYBRID                                                         │
└─────────────────────────────────────────────────────────────────┘
```

## Relationships

```
MemoryInput ──> ClassificationEngine ──> ClassificationResult
                    │
                    ├──> MemoryClassifier (12 implementations)
                    ├──> MemoryTypeRegistry
                    ├──> ClassifierRegistry
                    ├──> ClassificationLogger
                    └──> ClassificationTelemetry

ClassificationResult ──> UniversalMemoryObject
UniversalMemoryObject ──> MemoryRouter ──> StorageLocation

ClassificationEngine ──> ClassificationContainer (DI)
ClassificationConfig ──> ClassificationEngine
```

## Exception Hierarchy

```
Exception
    └──> ClassificationError
            ├──> ClassifierNotFoundError
            ├──> ClassificationFailedError
            ├──> InvalidMemoryTypeError
            ├──> ConfigurationError
            └──> StorageError
```
