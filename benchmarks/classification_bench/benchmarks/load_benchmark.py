"""Load benchmark for testing throughput and resource usage."""

import asyncio
import time
from typing import Dict, Any, Optional
from pathlib import Path

from classification_bench.utils.resource_monitor import ResourceMonitor
from classification_bench.metrics.calculator import MetricsCalculator
from memory_classification.core.interfaces import MemoryInput


class LoadBenchmark:
    """Benchmark load handling capacity and resource usage."""
    
    def __init__(self, classification_engine, dataset_dir: Path):
        self.engine = classification_engine
        self.dataset_dir = dataset_dir
        self.monitor = ResourceMonitor()
    
    async def run(self, target_rps: int = 1000, duration_seconds: int = 10) -> Dict[str, Any]:
        """Run load benchmark simulating 1M classifications/day."""
        print(f"Starting Load Benchmark: Target {target_rps} RPS for {duration_seconds}s")
        
        self.monitor.start()
        
        total_requests = 0
        failed_requests = 0
        start_time = time.time()
        
        # Load sample test data
        test_cases = self._load_test_cases()
        
        # Simulate load - run as fast as possible to measure max throughput
        end_time = start_time + duration_seconds
        
        while time.time() < end_time:
            try:
                # Get test case
                test_case = test_cases[total_requests % len(test_cases)]
                
                # Run classification
                result = await self.engine.classify(
                    MemoryInput(
                        content=test_case["content"],
                        session_id="benchmark-session",
                        agent_id="benchmark-agent",
                        tenant_id="benchmark-tenant"
                    ),
                    enable_routing=False
                )
                
                total_requests += 1
                        
            except Exception as e:
                failed_requests += 1
                print(f"Request failed: {e}")
        
        self.monitor.stop()
        
        # Calculate metrics
        actual_duration = time.time() - start_time
        throughput = MetricsCalculator.calculate_throughput(total_requests, actual_duration)
        error_rate = MetricsCalculator.calculate_error_rate(total_requests, failed_requests)
        
        avg_usage = self.monitor.get_average_usage()
        peak_usage = self.monitor.get_peak_usage()
        
        results = {
            "target_rps": target_rps,
            "duration_seconds": actual_duration,
            "total_requests": total_requests,
            "failed_requests": failed_requests,
            "throughput_rps": throughput,
            "error_rate": error_rate,
            "avg_cpu_percent": avg_usage.get("avg_cpu_percent", 0),
            "avg_memory_percent": avg_usage.get("avg_memory_percent", 0),
            "avg_memory_mb": avg_usage.get("avg_memory_mb", 0),
            "peak_cpu_percent": peak_usage.get("peak_cpu_percent", 0),
            "peak_memory_percent": peak_usage.get("peak_memory_percent", 0),
            "peak_memory_mb": peak_usage.get("peak_memory_mb", 0)
        }
        
        print(f"Load Benchmark Complete: {throughput:.2f} RPS, {error_rate:.2f}% error rate")
        return results
    
    def _load_test_cases(self) -> list:
        """Load test cases from dataset."""
        test_cases = []
        
        # Load from various dataset files
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
