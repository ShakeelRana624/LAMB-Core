"""
Load Test for Attention Engine - 1M requests/day simulation.

This script simulates 1 million attention requests per day to validate
the engine's performance under sustained load.
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any
from datetime import datetime
import json
import random
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from attention.core.interfaces import AttentionContext, TemporalContext, SocialContext
from attention.core.engine import AttentionEngine
from attention.config.defaults import get_default_config


class LoadTestRunner:
    """Runner for load testing the Attention Engine."""
    
    def __init__(self, requests_per_day: int = 1_000_000):
        """
        Initialize the load test runner.
        
        Args:
            requests_per_day: Number of requests to simulate per day
        """
        self.requests_per_day = requests_per_day
        self.requests_per_second = requests_per_day / 86400  # 86400 seconds in a day
        self.results = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "latencies": [],
            "errors": [],
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
    
    async def run_load_test(
        self,
        duration_seconds: int = 60,
        concurrent_requests: int = 10,
    ) -> Dict[str, Any]:
        """
        Run the load test.
        
        Args:
            duration_seconds: Duration of the test in seconds
            concurrent_requests: Number of concurrent requests
            
        Returns:
            Test results dictionary
        """
        # Initialize engine with optimized config
        config = get_default_config()
        config.enable_caching = True
        config.enable_telemetry = False
        config.enable_logging = False
        config.parallel_execution = True
        
        engine = AttentionEngine(config)
        
        print(f"Starting Load Test: {self.requests_per_day} requests/day simulation")
        print(f"Target RPS: {self.requests_per_second:.2f}")
        print(f"Duration: {duration_seconds} seconds")
        print(f"Concurrent requests: {concurrent_requests}")
        print("-" * 60)
        
        self.results["start_time"] = datetime.utcnow()
        
        # Calculate total requests for the test duration
        total_test_requests = int(self.requests_per_second * duration_seconds)
        
        # Run load test
        semaphore = asyncio.Semaphore(concurrent_requests)
        
        async def process_request(index: int):
            async with semaphore:
                try:
                    context = self.generate_test_context(index)
                    start = time.perf_counter()
                    await engine.compute_attention(context)
                    latency_ms = (time.perf_counter() - start) * 1000
                    
                    self.results["latencies"].append(latency_ms)
                    self.results["successful_requests"] += 1
                except Exception as e:
                    self.results["errors"].append(str(e))
                    self.results["failed_requests"] += 1
                finally:
                    self.results["total_requests"] += 1
        
        # Create tasks
        tasks = [process_request(i) for i in range(total_test_requests)]
        
        # Execute with progress tracking
        start_time = time.time()
        await asyncio.gather(*tasks)
        end_time = time.time()
        
        self.results["end_time"] = datetime.utcnow()
        actual_duration = end_time - start_time
        
        # Calculate statistics
        if self.results["latencies"]:
            self.results["p50_latency_ms"] = statistics.median(self.results["latencies"])
            self.results["p95_latency_ms"] = statistics.quantiles(self.results["latencies"], n=20)[18] if len(self.results["latencies"]) >= 20 else max(self.results["latencies"])
            self.results["p99_latency_ms"] = statistics.quantiles(self.results["latencies"], n=100)[98] if len(self.results["latencies"]) >= 100 else max(self.results["latencies"])
            self.results["mean_latency_ms"] = statistics.mean(self.results["latencies"])
            self.results["min_latency_ms"] = min(self.results["latencies"])
            self.results["max_latency_ms"] = max(self.results["latencies"])
        
        self.results["actual_duration_seconds"] = actual_duration
        self.results["actual_rps"] = self.results["total_requests"] / actual_duration
        self.results["error_rate"] = self.results["failed_requests"] / self.results["total_requests"] if self.results["total_requests"] > 0 else 0
        
        return self.results
    
    def print_results(self, results: Dict[str, Any]):
        """Print load test results."""
        print("\n" + "=" * 60)
        print("LOAD TEST RESULTS")
        print("=" * 60)
        print(f"Total Requests: {results['total_requests']}")
        print(f"Successful: {results['successful_requests']}")
        print(f"Failed: {results['failed_requests']}")
        print(f"Error Rate: {results['error_rate']:.2%}")
        print(f"\nDuration: {results['actual_duration_seconds']:.2f}s")
        print(f"Actual RPS: {results['actual_rps']:.2f}")
        print(f"Target RPS: {self.requests_per_second:.2f}")
        
        if results['latencies']:
            print(f"\nLatency Statistics:")
            print(f"  Mean: {results['mean_latency_ms']:.2f}ms")
            print(f"  P50: {results['p50_latency_ms']:.2f}ms")
            print(f"  P95: {results['p95_latency_ms']:.2f}ms")
            print(f"  P99: {results['p99_latency_ms']:.2f}ms")
            print(f"  Min: {results['min_latency_ms']:.2f}ms")
            print(f"  Max: {results['max_latency_ms']:.2f}ms")
        
        # Performance targets
        print(f"\nPerformance Targets:")
        target_rps = self.requests_per_second
        actual_rps = results['actual_rps']
        rps_ratio = actual_rps / target_rps
        
        print(f"  RPS Target: {target_rps:.2f} RPS")
        print(f"  RPS Actual: {actual_rps:.2f} RPS")
        print(f"  RPS Ratio: {rps_ratio:.2%}")
        
        if rps_ratio >= 0.9:
            print(f"  Status: ✓ PASS (>= 90% of target)")
        else:
            print(f"  Status: ✗ FAIL (< 90% of target)")
        
        if results['error_rate'] <= 0.01:
            print(f"  Error Rate: ✓ PASS (<= 1%)")
        else:
            print(f"  Error Rate: ✗ FAIL (> 1%)")
        
        print("=" * 60)
    
    def save_results(self, results: Dict[str, Any], filename: str = "load_test_results.json"):
        """Save results to JSON file."""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nResults saved to {filename}")


async def main():
    """Main entry point."""
    # 1M requests/day = ~11.57 RPS
    runner = LoadTestRunner(requests_per_day=1_000_000)
    
    # Run 60-second test (should process ~694 requests)
    results = await runner.run_load_test(duration_seconds=60, concurrent_requests=10)
    
    runner.print_results(results)
    runner.save_results(results)


if __name__ == "__main__":
    asyncio.run(main())
