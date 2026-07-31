# ClassificationBench

Research-grade benchmark suite for the LAMB Memory Classification Engine.

## Overview

ClassificationBench is a comprehensive benchmark suite designed to validate the scalability, correctness, robustness, latency, and production readiness of the Memory Classification Engine before enterprise deployment.

## Architecture

```
classification_bench/
├── __init__.py
├── orchestrator.py          # Main benchmark orchestrator
├── dataset/                 # Benchmark dataset (300 test cases)
│   ├── __init__.py
│   ├── identity.json
│   ├── goal.json
│   ├── preference.json
│   ├── relationship.json
│   ├── project.json
│   ├── skill.json
│   ├── procedural.json
│   ├── task.json
│   ├── episodic.json
│   ├── semantic.json
│   ├── emotional.json
│   ├── temporal.json
│   └── robustness.json
├── benchmarks/              # Benchmark implementations
│   ├── __init__.py
│   ├── load_benchmark.py
│   ├── latency_benchmark.py
│   ├── quality_benchmark.py
│   ├── robustness_benchmark.py
│   ├── scalability_benchmark.py
│   └── fault_tolerance_benchmark.py
├── metrics/                 # Metrics calculation
│   ├── __init__.py
│   └── calculator.py
├── reporting/               # Report generation
│   ├── __init__.py
│   ├── generator.py
│   └── certificate.py
└── utils/                   # Utilities
    ├── __init__.py
    ├── resource_monitor.py
    └── chart_generator.py
```

## Benchmarks

### 1. Load Benchmark
- Simulate 1 million classifications/day
- Measure throughput (RPS)
- Error rate
- CPU usage
- Memory usage
- Thread utilization
- Horizontal scalability simulation

### 2. Latency Benchmark
- P50, P95, P99 latency
- Average latency
- Standard deviation
- Cold start latency
- Warm cache latency
- Batch latency

### 3. Quality Benchmark
- 300 manually curated test cases
- Precision, Recall, F1 Score
- Exact Match Accuracy
- Multi-label Accuracy
- Hamming Loss
- Top-1 Accuracy
- Top-3 Accuracy

### 4. Robustness Benchmark
- Empty inputs
- Very long text
- Random text
- Mixed languages
- Unicode
- Emojis
- Invalid metadata

### 5. Scalability Benchmark
- 100, 1k, 10k, 100k, 1M memories
- Performance degradation analysis

### 6. Fault Tolerance Benchmark
- Redis unavailable
- Embedding model unavailable
- LLM unavailable
- Timeouts
- Corrupted requests
- Network failures

## Pass Criteria

### Load
- Throughput: ≥1000 RPS
- Error rate: <0.1%

### Latency
- P50: <5ms
- P95: <15ms
- P99: <30ms

### Quality
- Precision: >95%
- Recall: >95%
- F1 Score: >95%

### Availability
- 99.99% uptime

## Usage

```python
from benchmarks.classification_bench.orchestrator import ClassificationBench

# Initialize benchmark suite
bench = ClassificationBench()

# Run all benchmarks
results = await bench.run_full_suite()

# Generate reports
bench.generate_reports(results)

# Check production readiness
certificate = bench.generate_certificate(results)
print(certificate.status)  # PASS or FAIL
```

## Output

- **JSON Report**: Detailed metrics in JSON format
- **CSV Metrics**: Metrics in CSV format for analysis
- **Markdown Summary**: Human-readable summary
- **Performance Charts**: Visual performance analysis
- **Production Readiness Certificate**: PASS/FAIL with bottlenecks
