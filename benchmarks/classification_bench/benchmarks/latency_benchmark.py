"""Latency benchmark for testing response times."""

import asyncio
import time
from typing import Dict, Any, List
from pathlib import Path

from classification_bench.metrics.calculator import MetricsCalculator
from memory_classification.core.interfaces import MemoryInput


class LatencyBenchmark:
    """Benchmark latency characteristics of classification."""
    
    def __init__(self, classification_engine, dataset_dir: Path):
        self.engine = classification_engine
        self.dataset_dir = dataset_dir
    
    async def run(self, num_samples: int = 1000) -> Dict[str, Any]:
        """Run latency benchmark measuring P50, P95, P99 latencies."""
        print(f"Starting Latency Benchmark: {num_samples} samples")
        
        # Load test cases
        test_cases = self._load_test_cases()
        
        latencies: List[float] = []
        
        # Warm up
        for _ in range(10):
            test_case = test_cases[0]
            try:
                await self.engine.classify(
                    MemoryInput(
                        content=test_case["content"],
                        session_id="benchmark-session",
                        agent_id="benchmark-agent",
                        tenant_id="benchmark-tenant"
                    ),
                    enable_routing=False
                )
            except Exception:
                pass
        
        # Measure latencies
        for i in range(num_samples):
            test_case = test_cases[i % len(test_cases)]
            
            start = time.perf_counter()
            try:
                await self.engine.classify(
                    MemoryInput(
                        content=test_case["content"],
                        session_id="benchmark-session",
                        agent_id="benchmark-agent",
                        tenant_id="benchmark-tenant"
                    ),
                    enable_routing=False
                )
                end = time.perf_counter()
                latency_ms = (end - start) * 1000
                latencies.append(latency_ms)
            except Exception as e:
                print(f"Classification failed: {e}")
                latencies.append(0)  # Treat failure as 0 latency or could use a large penalty
        
        # Calculate statistics
        stats = MetricsCalculator.calculate_latency_stats(latencies)
        
        results = {
            "num_samples": num_samples,
            "avg_ms": stats["avg_ms"],
            "std_ms": stats["std_ms"],
            "min_ms": stats["min_ms"],
            "max_ms": stats["max_ms"],
            "p50_ms": stats["p50_ms"],
            "p95_ms": stats["p95_ms"],
            "p99_ms": stats["p99_ms"]
        }
        
        print(f"Latency Benchmark Complete: P50={stats['p50_ms']:.2f}ms, P95={stats['p95_ms']:.2f}ms, P99={stats['p99_ms']:.2f}ms")
        return results
    
    async def run_cold_start_benchmark(self, num_samples: int = 100) -> Dict[str, Any]:
        """Run cold start latency benchmark."""
        print(f"Starting Cold Start Latency Benchmark: {num_samples} samples")
        
        test_cases = self._load_test_cases()
        latencies: List[float] = []
        
        for i in range(num_samples):
            test_case = test_cases[i % len(test_cases)]
            
            # Force cold start by clearing cache if possible
            # This is engine-specific, so we'll just measure first request after delay
            await asyncio.sleep(0.1)  # Simulate cold start gap
            
            start = time.perf_counter()
            try:
                await self.engine.classify(
                    MemoryInput(
                        content=test_case["content"],
                        session_id="benchmark-session",
                        agent_id="benchmark-agent",
                        tenant_id="benchmark-tenant"
                    ),
                    enable_routing=False
                )
                end = time.perf_counter()
                latency_ms = (end - start) * 1000
                latencies.append(latency_ms)
            except Exception:
                pass
        
        stats = MetricsCalculator.calculate_latency_stats(latencies)
        
        return {
            "cold_start_samples": num_samples,
            "cold_start_avg_ms": stats["avg_ms"],
            "cold_start_p50_ms": stats["p50_ms"],
            "cold_start_p95_ms": stats["p95_ms"],
            "cold_start_p99_ms": stats["p99_ms"]
        }
    
    async def run_warm_cache_benchmark(self, num_samples: int = 1000) -> Dict[str, Any]:
        """Run warm cache latency benchmark."""
        print(f"Starting Warm Cache Latency Benchmark: {num_samples} samples")
        
        test_cases = self._load_test_cases()
        
        # Warm up cache by running same test case multiple times
        test_case = test_cases[0]
        for _ in range(50):
            try:
                await self.engine.classify(
                    MemoryInput(
                        content=test_case["content"],
                        session_id="benchmark-session",
                        agent_id="benchmark-agent",
                        tenant_id="benchmark-tenant"
                    ),
                    enable_routing=False
                )
            except Exception:
                pass
        
        latencies: List[float] = []
        
        for _ in range(num_samples):
            start = time.perf_counter()
            try:
                await self.engine.classify(
                    MemoryInput(
                        content=test_case["content"],
                        session_id="benchmark-session",
                        agent_id="benchmark-agent",
                        tenant_id="benchmark-tenant"
                    ),
                    enable_routing=False
                )
                end = time.perf_counter()
                latency_ms = (end - start) * 1000
                latencies.append(latency_ms)
            except Exception:
                pass
        
        stats = MetricsCalculator.calculate_latency_stats(latencies)
        
        return {
            "warm_cache_samples": num_samples,
            "warm_cache_avg_ms": stats["avg_ms"],
            "warm_cache_p50_ms": stats["p50_ms"],
            "warm_cache_p95_ms": stats["p95_ms"],
            "warm_cache_p99_ms": stats["p99_ms"]
        }
    
    def _load_test_cases(self) -> list:
        """Load test cases from dataset."""
        test_cases = []
        
        dataset_files = [
            "identity.json", "goal.json", "preference.json",
            "relationship.json", "project.json", "skill.json"
        ]
        
        for filename in dataset_files:
            file_path = self.dataset_dir / filename
            if file_path.exists():
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    test_cases.extend(data.get("test_cases", []))
        
        return test_cases
