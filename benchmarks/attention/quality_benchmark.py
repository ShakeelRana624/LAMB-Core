"""
Quality Benchmark for Attention Engine - Human-like attention behavior verification.

This script validates that the Attention Engine behaves in a human-like manner
by testing various attention scenarios against expected outcomes.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from attention.core.interfaces import AttentionContext, TemporalContext, SocialContext
from attention.core.engine import AttentionEngine
from attention.config.defaults import get_default_config


class QualityBenchmark:
    """Quality benchmark for human-like attention behavior."""
    
    def __init__(self):
        """Initialize the quality benchmark."""
        self.test_cases = self._generate_test_cases()
        self.results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_results": [],
        }
    
    def _generate_test_cases(self) -> List[Dict[str, Any]]:
        """Generate test cases for quality benchmark."""
        return [
            {
                "name": "Urgency Detection",
                "description": "Engine should detect urgent information",
                "context": AttentionContext(
                    input_text="This is urgent, need it done today by 5pm",
                    session_id="test-session",
                    agent_id="test-agent",
                    temporal_context=TemporalContext(),
                    social_context=SocialContext(),
                ),
                "expected_signals": {
                    "urgency": {"min_score": 0.7, "should_be_high": True},
                },
            },
            {
                "name": "Novelty Detection",
                "description": "Engine should detect novel information",
                "context": AttentionContext(
                    input_text="I discovered a completely new approach to solving this problem",
                    session_id="test-session",
                    agent_id="test-agent",
                    temporal_context=TemporalContext(),
                    social_context=SocialContext(),
                    metadata={"recent_memories": []},
                ),
                "expected_signals": {
                    "novelty": {"min_score": 0.7, "should_be_high": True},
                },
            },
            {
                "name": "Goal Relevance",
                "description": "Engine should detect goal-relevant information",
                "context": AttentionContext(
                    input_text="I completed the database migration task",
                    session_id="test-session",
                    agent_id="test-agent",
                    current_goal="Complete database migration",
                    temporal_context=TemporalContext(),
                    social_context=SocialContext(),
                ),
                "expected_signals": {
                    "goal_relevance": {"min_score": 0.5, "should_be_high": True},
                },
            },
            {
                "name": "Reward Detection",
                "description": "Engine should detect positive outcomes",
                "context": AttentionContext(
                    input_text="Great job! We successfully achieved our target",
                    session_id="test-session",
                    agent_id="test-agent",
                    temporal_context=TemporalContext(),
                    social_context=SocialContext(),
                ),
                "expected_signals": {
                    "reward": {"min_score": 0.4, "should_be_high": True},
                },
            },
            {
                "name": "Risk Detection",
                "description": "Engine should detect potential threats",
                "context": AttentionContext(
                    input_text="Warning: there is a critical security vulnerability",
                    session_id="test-session",
                    agent_id="test-agent",
                    temporal_context=TemporalContext(),
                    social_context=SocialContext(),
                ),
                "expected_signals": {
                    "risk": {"min_score": 0.4, "should_be_high": True},
                },
            },
            {
                "name": "Emotion Detection",
                "description": "Engine should detect emotional content",
                "context": AttentionContext(
                    input_text="I am very excited and happy about this opportunity!",
                    session_id="test-session",
                    agent_id="test-agent",
                    temporal_context=TemporalContext(),
                    social_context=SocialContext(),
                ),
                "expected_signals": {
                    "emotion": {"min_score": 0.6, "should_be_high": True},
                },
            },
            {
                "name": "Curiosity Detection",
                "description": "Engine should detect information gaps",
                "context": AttentionContext(
                    input_text="I wonder how this works? What is the mechanism behind it?",
                    session_id="test-session",
                    agent_id="test-agent",
                    temporal_context=TemporalContext(),
                    social_context=SocialContext(),
                ),
                "expected_signals": {
                    "curiosity": {"min_score": 0.6, "should_be_high": True},
                },
            },
            {
                "name": "Surprise Detection",
                "description": "Engine should detect unexpected information",
                "context": AttentionContext(
                    input_text="This was completely unexpected! I never thought this would happen",
                    session_id="test-session",
                    agent_id="test-agent",
                    temporal_context=TemporalContext(),
                    social_context=SocialContext(),
                ),
                "expected_signals": {
                    "surprise": {"min_score": 0.3, "should_be_high": True},
                },
            },
            {
                "name": "Confidence Detection",
                "description": "Engine should detect certainty levels",
                "context": AttentionContext(
                    input_text="I am definitely certain about this decision",
                    session_id="test-session",
                    agent_id="test-agent",
                    temporal_context=TemporalContext(),
                    social_context=SocialContext(),
                ),
                "expected_signals": {
                    "confidence": {"min_score": 0.6, "should_be_high": True},
                },
            },
            {
                "name": "Low Attention Baseline",
                "description": "Engine should give low attention to mundane information",
                "context": AttentionContext(
                    input_text="This is a routine task that I do every day",
                    session_id="test-session",
                    agent_id="test-agent",
                    temporal_context=TemporalContext(),
                    social_context=SocialContext(),
                ),
                "expected_signals": {
                    "aggregated_score": {"max_score": 0.4, "should_be_low": True},
                },
            },
            {
                "name": "Task Match",
                "description": "Engine should detect task-relevant information",
                "context": AttentionContext(
                    input_text="Working on the API integration for the payment system",
                    session_id="test-session",
                    agent_id="test-agent",
                    current_task="API integration",
                    temporal_context=TemporalContext(),
                    social_context=SocialContext(),
                ),
                "expected_signals": {
                    "current_task_match": {"min_score": 0.6, "should_be_high": True},
                },
            },
            {
                "name": "Social Importance",
                "description": "Engine should detect socially relevant information",
                "context": AttentionContext(
                    input_text="John said that the team meeting with the stakeholders is critical",
                    session_id="test-session",
                    agent_id="test-agent",
                    temporal_context=TemporalContext(),
                    social_context=SocialContext(group_size=10),
                ),
                "expected_signals": {
                    "social_importance": {"min_score": 0.5, "should_be_high": True},
                },
            },
        ]
    
    async def run_quality_benchmark(self) -> Dict[str, Any]:
        """
        Run the quality benchmark.
        
        Returns:
            Benchmark results dictionary
        """
        # Initialize engine
        config = get_default_config()
        config.enable_caching = False
        config.enable_telemetry = False
        config.enable_logging = False
        
        engine = AttentionEngine(config)
        
        print("Starting Quality Benchmark")
        print(f"Test Cases: {len(self.test_cases)}")
        print("-" * 60)
        
        for test_case in self.test_cases:
            result = await self._run_test_case(engine, test_case)
            self.results["test_results"].append(result)
            
            if result["passed"]:
                self.results["passed_tests"] += 1
                print(f"✓ {test_case['name']}: PASS")
            else:
                self.results["failed_tests"] += 1
                print(f"✗ {test_case['name']}: FAIL - {result['reason']}")
            
            self.results["total_tests"] += 1
        
        self.results["pass_rate"] = self.results["passed_tests"] / self.results["total_tests"] if self.results["total_tests"] > 0 else 0.0
        
        return self.results
    
    async def _run_test_case(
        self,
        engine: AttentionEngine,
        test_case: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Run a single test case.
        
        Args:
            engine: Attention engine instance
            test_case: Test case definition
            
        Returns:
            Test result dictionary
        """
        try:
            # Compute attention
            vector = await engine.compute_attention(test_case["context"])
            
            # Validate against expected signals
            passed = True
            reason = ""
            
            for signal_name, expected in test_case["expected_signals"].items():
                if signal_name == "aggregated_score":
                    score = vector.aggregated_score
                else:
                    score = vector.get_signal_score(signal_name)
                
                if score is None:
                    passed = False
                    reason = f"Signal {signal_name} not computed"
                    break
                
                if expected.get("should_be_high") and score < expected["min_score"]:
                    passed = False
                    reason = f"Signal {signal_name} score {score:.2f} below minimum {expected['min_score']}"
                    break
                
                if expected.get("should_be_low") and score > expected["max_score"]:
                    passed = False
                    reason = f"Signal {signal_name} score {score:.2f} above maximum {expected['max_score']}"
                    break
            
            return {
                "name": test_case["name"],
                "description": test_case["description"],
                "passed": passed,
                "reason": reason,
                "aggregated_score": vector.aggregated_score,
                "signal_scores": {
                    signal: vector.get_signal_score(signal)
                    for signal in [
                        "novelty", "goal_relevance", "urgency", "reward", "risk",
                        "emotion", "curiosity", "surprise", "confidence",
                        "future_utility", "social_importance", "repetition",
                        "current_task_match",
                    ]
                },
            }
            
        except Exception as e:
            return {
                "name": test_case["name"],
                "description": test_case["description"],
                "passed": False,
                "reason": f"Exception: {str(e)}",
                "aggregated_score": None,
                "signal_scores": {},
            }
    
    def print_results(self, results: Dict[str, Any]):
        """Print quality benchmark results."""
        print("\n" + "=" * 60)
        print("QUALITY BENCHMARK RESULTS")
        print("=" * 60)
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed_tests']}")
        print(f"Failed: {results['failed_tests']}")
        print(f"Pass Rate: {results['pass_rate']:.1%}")
        
        print(f"\nDetailed Results:")
        for result in results["test_results"]:
            status = "✓ PASS" if result["passed"] else "✗ FAIL"
            print(f"  {status}: {result['name']}")
            if not result["passed"]:
                print(f"    Reason: {result['reason']}")
            print(f"    Aggregated Score: {result['aggregated_score']:.2f}" if result['aggregated_score'] else "    Aggregated Score: N/A")
        
        # Overall status
        min_pass_rate = 0.8  # 80% pass rate required
        overall_status = "✓ PASS" if results["pass_rate"] >= min_pass_rate else "✗ FAIL"
        
        print(f"\nOverall Status: {overall_status}")
        print(f"Required Pass Rate: {min_pass_rate:.0%}")
        print(f"Actual Pass Rate: {results['pass_rate']:.1%}")
        print("=" * 60)
    
    def save_results(self, results: Dict[str, Any], filename: str = "quality_benchmark_results.json"):
        """Save results to JSON file."""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nResults saved to {filename}")


async def main():
    """Main entry point."""
    benchmark = QualityBenchmark()
    results = await benchmark.run_quality_benchmark()
    benchmark.print_results(results)
    benchmark.save_results(results)


if __name__ == "__main__":
    asyncio.run(main())
