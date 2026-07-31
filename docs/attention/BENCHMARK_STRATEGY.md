# Attention Engine Benchmark Strategy

## Overview

This document outlines the comprehensive benchmark strategy for the LAMB Attention Engine, ensuring performance, reliability, and correctness across production workloads.

## Benchmark Objectives

1. **Performance**: Measure latency and throughput under various load conditions
2. **Correctness**: Validate signal computation accuracy and aggregation logic
3. **Scalability**: Test horizontal scaling and resource utilization
4. **Reliability**: Ensure stability under stress and failure conditions
5. **Regression Detection**: Identify performance degradation over time

## Benchmark Categories

### 1. Signal-Level Benchmarks

#### Objective
Measure individual signal computation performance and accuracy.

#### Metrics
- **Latency**: Per-signal computation time (target: < 5ms per signal)
- **Accuracy**: Score correctness against ground truth
- **Resource Usage**: CPU and memory per signal

#### Test Cases
```python
# Novelty Signal Benchmark
- Empty recent memories (baseline)
- 10 recent memories
- 100 recent memories
- 1000 recent memories (stress test)

# Goal Relevance Signal Benchmark
- No current goal
- Primary goal match
- Secondary goal match
- Tertiary goal match
- No match

# Urgency Signal Benchmark
- High urgency patterns
- Medium urgency patterns
- Low urgency patterns
- No urgency
```

#### Execution
```bash
python -m benchmarks.attention.signal_benchmarks \
    --signal novelty \
    --iterations 1000 \
    --warmup 10
```

### 2. Aggregation Benchmarks

#### Objective
Measure aggregation strategy performance across different signal counts.

#### Metrics
- **Latency**: Aggregation computation time (target: < 5ms)
- **Strategy Comparison**: Compare all aggregation strategies
- **Scalability**: Performance vs. number of signals

#### Test Cases
```python
# Weighted Sum Strategy
- 5 signals
- 10 signals
- 13 signals (default)
- 20 signals (future-proofing)

# Geometric Mean Strategy
- Same signal counts as above

# Maximum/Minimum Strategies
- Same signal counts as above
```

#### Execution
```bash
python -m benchmarks.attention.aggregation_benchmarks \
    --strategy weighted_sum \
    --signal-counts 5,10,13,20 \
    --iterations 10000
```

### 3. End-to-End Benchmarks

#### Objective
Measure complete attention computation pipeline performance.

#### Metrics
- **Total Latency**: End-to-end computation time (target: < 50ms)
- **Parallel vs Sequential**: Compare execution modes
- **Cache Hit Rate**: Measure caching effectiveness
- **Throughput**: Requests per second

#### Test Cases
```python
# Standard Workload
- 13 signals enabled
- Parallel execution
- Caching enabled
- Telemetry enabled

# High-Performance Mode
- 13 signals enabled
- Parallel execution
- Caching enabled
- Telemetry disabled

# Minimal Mode
- 5 signals enabled
- Sequential execution
- Caching disabled
- Telemetry disabled
```

#### Execution
```bash
python -m benchmarks.attention.e2e_benchmarks \
    --mode standard \
    --concurrent-requests 10 \
    --duration 60
```

### 4. Load Testing

#### Objective
Test system behavior under sustained load.

#### Metrics
- **Throughput**: Maximum sustained requests per second
- **Latency Percentiles**: p50, p95, p99 latency
- **Error Rate**: Percentage of failed requests
- **Resource Utilization**: CPU, memory, network

#### Test Cases
```python
# Ramp Test
- 1 RPS → 100 RPS over 5 minutes
- Monitor for degradation

# Sustained Load
- 50 RPS for 30 minutes
- Monitor for memory leaks

# Spike Test
- Baseline 10 RPS
- Spike to 200 RPS for 30 seconds
- Return to baseline
```

#### Execution
```bash
python -m benchmarks.attention.load_test \
    --rps 50 \
    --duration 1800 \
    --ramp-up 300
```

### 5. Accuracy Benchmarks

#### Objective
Validate signal computation correctness against labeled datasets.

#### Metrics
- **Precision**: True positive rate
- **Recall**: True positive coverage
- **F1 Score**: Harmonic mean of precision and recall
- **Correlation**: Score correlation with human judgments

#### Test Cases
```python
# Novelty Accuracy
- Dataset: 1000 labeled inputs with novelty scores
- Metric: Correlation with human ratings

# Goal Relevance Accuracy
- Dataset: 1000 goal-context pairs
- Metric: Precision/recall for goal match

# Urgency Accuracy
- Dataset: 1000 urgency-labeled inputs
- Metric: Classification accuracy
```

#### Execution
```bash
python -m benchmarks.attention.accuracy_benchmarks \
    --dataset novelty_labeled.json \
    --signal novelty
```

## Benchmark Infrastructure

### Test Data

#### Synthetic Data Generation
```python
# Generate test inputs
def generate_test_inputs(n: int) -> List[AttentionContext]:
    contexts = []
    for i in range(n):
        contexts.append(AttentionContext(
            input_text=f"Test input {i}",
            session_id=f"session-{i % 100}",
            agent_id=f"agent-{i % 10}",
            metadata={"recent_memories": generate_memories(i)},
        ))
    return contexts
```

#### Real-World Data Collection
- Collect production anonymized inputs
- Label subset for accuracy benchmarks
- Maintain separate test dataset

### Benchmark Runner

```python
class BenchmarkRunner:
    """Runs attention engine benchmarks."""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.results = []
    
    async def run_benchmark(self, benchmark: Benchmark) -> BenchmarkResult:
        """Run a single benchmark."""
        # Warmup
        for _ in range(benchmark.warmup_iterations):
            await benchmark.run()
        
        # Actual benchmark
        times = []
        for _ in range(benchmark.iterations):
            start = time.perf_counter()
            await benchmark.run()
            times.append(time.perf_counter() - start)
        
        return BenchmarkResult(
            mean=np.mean(times),
            std=np.std(times),
            p50=np.percentile(times, 50),
            p95=np.percentile(times, 95),
            p99=np.percentile(times, 99),
        )
```

### Reporting

#### JSON Report
```json
{
  "benchmark_id": "attention_e2e_standard",
  "timestamp": "2026-07-29T14:00:00Z",
  "results": {
    "mean_latency_ms": 45.2,
    "p95_latency_ms": 52.1,
    "p99_latency_ms": 68.3,
    "throughput_rps": 22.1,
    "error_rate": 0.0
  },
  "metadata": {
    "config": {...},
    "environment": {...}
  }
}
```

#### Human-Readable Report
```
Attention Engine End-to-End Benchmark
=====================================

Configuration:
- Signals: 13 enabled
- Execution: Parallel
- Caching: Enabled
- Telemetry: Enabled

Results:
- Mean Latency: 45.2ms (target: < 50ms) ✓
- P95 Latency: 52.1ms (target: < 75ms) ✓
- P99 Latency: 68.3ms (target: < 100ms) ✓
- Throughput: 22.1 RPS
- Error Rate: 0.0%

Status: PASSED
```

## Continuous Integration

### Automated Benchmarks

#### CI Pipeline Integration
```yaml
# .github/workflows/benchmarks.yml
name: Attention Engine Benchmarks

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  benchmarks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-asyncio
      - name: Run benchmarks
        run: |
          python -m benchmarks.attention.run_all \
            --output benchmark_results.json
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-results
          path: benchmark_results.json
```

### Regression Detection

#### Baseline Comparison
```python
def detect_regression(current: BenchmarkResult, baseline: BenchmarkResult) -> bool:
    """Detect performance regression."""
    # Check if latency increased by > 10%
    if current.mean_latency_ms > baseline.mean_latency_ms * 1.1:
        return True
    
    # Check if throughput decreased by > 10%
    if current.throughput_rps < baseline.throughput_rps * 0.9:
        return True
    
    return False
```

#### Alerting
- Slack notification on regression
- GitHub issue creation for investigation
- Block merge if regression detected

## Performance Targets

### Latency Targets
| Component | Target | P95 Target | P99 Target |
|-----------|--------|------------|------------|
| Individual Signal | < 5ms | < 10ms | < 20ms |
| Aggregation | < 5ms | < 10ms | < 15ms |
| End-to-End | < 50ms | < 75ms | < 100ms |

### Throughput Targets
| Configuration | Target |
|---------------|--------|
| Single Instance | > 20 RPS |
| 10 Instances | > 200 RPS |
| 100 Instances | > 2000 RPS |

### Resource Targets
| Metric | Target |
|--------|--------|
| CPU per Request | < 100ms |
| Memory per Request | < 10MB |
| Memory Overhead | < 500MB |

## Benchmark Schedule

### Regular Benchmarks
- **Daily**: Signal-level benchmarks (CI)
- **Weekly**: End-to-end benchmarks (CI)
- **Monthly**: Load testing (dedicated environment)
- **Quarterly**: Full regression suite (dedicated environment)

### Event-Driven Benchmarks
- Before major releases
- After significant code changes
- When performance issues are reported
- When infrastructure changes occur

## Benchmark Tools

### Recommended Tools
- **Locust**: Load testing
- **pytest-benchmark**: Micro-benchmarks
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **pytest-asyncio**: Async testing

### Custom Tools
- `benchmarks/attention/signal_benchmarks.py`: Signal-level benchmarks
- `benchmarks/attention/aggregation_benchmarks.py`: Aggregation benchmarks
- `benchmarks/attention/e2e_benchmarks.py`: End-to-end benchmarks
- `benchmarks/attention/load_test.py`: Load testing
- `benchmarks/attention/accuracy_benchmarks.py`: Accuracy benchmarks

## Analysis and Optimization

### Performance Profiling
```python
# Profile signal computation
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Run benchmark
await engine.compute_attention(context)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### Optimization Workflow
1. Run benchmarks to identify bottlenecks
2. Profile slow components
3. Implement optimizations
4. Re-run benchmarks to validate
5. Document changes

## Conclusion

This benchmark strategy ensures the Attention Engine meets performance targets, maintains correctness, and scales effectively in production. Regular benchmarking enables early detection of regressions and informs optimization efforts.
