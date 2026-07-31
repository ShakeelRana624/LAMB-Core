"""
Latency Test for Attention Engine - P50, P95, P99 measurement.

This script measures detailed latency statistics for the Attention Engine
to ensure it meets performance targets.
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any
from datetime import datetime
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from attention.core.interfaces import AttentionContext, TemporalContext, SocialContext
from attention.core.engine import AttentionEngine
from attention.config.defaults import get_default_config


class LatencyTestRunner:
    """Runner for latency testing the Attention Engine."""
    
    def __init__(self):
        """Initialize the latency test runner."""
        self.results = {
            "latencies": [],
            "signal_latencies": {},
            "aggregation_latencies": [],
            "total_latencies": [],
            "start_time": None,
            "end_time": None,
        }
    
    def generate_test_context(self, index: int) -> AttentionContext:
        """Generate a test attention context."""
        test_inputs = [
            "This is urgent, need it done today",
            "Great job! We successfully completed the task",
            "I wonder how this works? What is the mechanism?",
            "This was completely unexpected! Wow!",
            "We need to plan this for next month",
            "John said that the team meeting is important",
            "Working on the database migration",
            "This is a test input",
            "Complete the project by Friday",
            "Warning: there is a risk of failure",
        ]
        
        return AttentionContext(
            input_text=test_inputs[index % len(test_inputs)],
            session_id=f"session-{index % 1000}",
            agent_id=f"agent-{index % 100}",
            temporal_context=TemporalContext(),
            social_context=SocialContext(),
            metadata={
                "recent_memories": [],
                "current_goal": f"Goal {index % 10}",
            },
        )
    
    async def run_latency_test(
        self,
        iterations: int = 1000,
        warmup_iterations: int = 100,
    ) -> Dict[str, Any]:
        """
        Run the latency test.
        
        Args:
            iterations: Number of iterations for the test
            warmup_iterations: Number of warmup iterations
            
        Returns:
            Test results dictionary
        """
        # Initialize engine with optimized config
        config = get_default_config()
        config.enable_caching = False  # Disable caching for true latency measurement
        config.enable_telemetry = False
        config.enable_logging = False
        config.parallel_execution = True
        
        engine = AttentionEngine(config)
        
        print(f"Starting Latency Test")
        print(f"Iterations: {iterations}")
        print(f"Warmup: {warmup_iterations}")
        print("-" * 60)
        
        self.results["start_time"] = datetime.utcnow()
        
        # Warmup
        print("Warming up...")
        for i in range(warmup_iterations):
            context = self.generate_test_context(i)
            await engine.compute_attention(context)
        
        print("Warmup complete. Starting latency measurement...")
        
        # Main latency test
        for i in range(iterations):
            context = self.generate_test_context(i + warmup_iterations)
            
            start = time.perf_counter()
            await engine.compute_attention(context)
            latency_ms = (time.perf_counter() - start) * 1000
            
            self.results["total_latencies"].append(latency_ms)
            
            # Progress indicator
            if (i + 1) % 100 == 0:
                print(f"Progress: {i + 1}/{iterations}")
        
        self.results["end_time"] = datetime.utcnow()
        
        # Calculate statistics
        if self.results["total_latencies"]:
            latencies = self.results["total_latencies"]
            self.results["mean_latency_ms"] = statistics.mean(latencies)
            self.results["median_latency_ms"] = statistics.median(latencies)
            self.results["std_latency_ms"] = statistics.stdev(latencies) if len(latencies) > 1 else 0.0
            
            # Percentiles
            sorted_latencies = sorted(latencies)
            self.results["p50_latency_ms"] = sorted_latencies[int(len(sorted_latencies) * 0.5)]
            self.results["p75_latency_ms"] = sorted_latencies[int(len(sorted_latencies) * 0.75)]
            self.results["p90_latency_ms"] = sorted_latencies[int(len(sorted_latencies) * 0.9)]
            self.results["p95_latency_ms"] = sorted_latencies[int(len(sorted_latencies) * 0.95)]
            self.results["p99_latency_ms"] = sorted_latencies[int(len(sorted_latencies) * 0.99)]
            self.results["p999_latency_ms"] = sorted_latencies[int(len(sorted_latencies) * 0.999)] if len(sorted_latencies) >= 1000 else sorted_latencies[-1]
            
            self.results["min_latency_ms"] = min(latencies)
            self.results["max_latency_ms"] = max(latencies)
        
        return self.results
    
    def print_results(self, results: Dict[str, Any]):
        """Print latency test results."""
        print("\n" + "=" * 60)
        print("LATENCY TEST RESULTS")
        print("=" * 60)
        print(f"Iterations: {len(results['total_latencies'])}")
        
        if results['total_latencies']:
            print(f"\nLatency Statistics:")
            print(f"  Mean: {results['mean_latency_ms']:.2f}ms")
            print(f"  Median: {results['median_latency_ms']:.2f}ms")
            print(f"  Std Dev: {results['std_latency_ms']:.2f}ms")
            print(f"  Min: {results['min_latency_ms']:.2f}ms")
            print(f"  Max: {results['max_latency_ms']:.2f}ms")
            
            print(f"\nPercentiles:")
            print(f"  P50: {results['p50_latency_ms']:.2f}ms")
            print(f"  P75: {results['p75_latency_ms']:.2f}ms")
            print(f"  P90: {results['p90_latency_ms']:.2f}ms")
            print(f"  P95: {results['p95_latency_ms']:.2f}ms")
            print(f"  P99: {results['p99_latency_ms']:.2f}ms")
            print(f"  P99.9: {results['p999_latency_ms']:.2f}ms")
        
        # Performance targets
        print(f"\nPerformance Targets:")
        p50_target = 50.0
        p95_target = 75.0
        p99_target = 100.0
        
        p50_status = "✓ PASS" if results['p50_latency_ms'] <= p50_target else "✗ FAIL"
        p95_status = "✓ PASS" if results['p95_latency_ms'] <= p95_target else "✗ FAIL"
        p99_status = "✓ PASS" if results['p99_latency_ms'] <= p99_target else "✗ FAIL"
        
        print(f"  P50 Target: {p50_target}ms - Actual: {results['p50_latency_ms']:.2f}ms - {p50_status}")
        print(f"  P95 Target: {p95_target}ms - Actual: {results['p95_latency_ms']:.2f}ms - {p95_status}")
        print(f"  P99 Target: {p99_target}ms - Actual: {results['p99_latency_ms']:.2f}ms - {p99_status}")
        
        # Overall status
        all_pass = (
            results['p50_latency_ms'] <= p50_target and
            results['p95_latency_ms'] <= p95_target and
            results['p99_latency_ms'] <= p99_target
        )
        
        print(f"\nOverall Status: {'✓ PASS' if all_pass else '✗ FAIL'}")
        print("=" * 60)
    
    def save_results(self, results: Dict[str, Any], filename: str = "latency_test_results.json"):
        """Save results to JSON file."""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nResults saved to {filename}")


async def main():
    """Main entry point."""
    runner = LatencyTestRunner()
    results = await runner.run_latency_test(iterations=1000, warmup_iterations=100)
    runner.print_results(results)
    runner.save_results(results)


if __name__ == "__main__":
    asyncio.run(main())
