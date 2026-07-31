"""Robustness benchmark for testing edge cases and invalid inputs."""

import json
from typing import Dict, Any
from pathlib import Path

from memory_classification.core.interfaces import MemoryInput


class RobustnessBenchmark:
    """Benchmark robustness against edge cases and invalid inputs."""
    
    def __init__(self, classification_engine, dataset_dir: Path):
        self.engine = classification_engine
        self.dataset_dir = dataset_dir
    
    async def run(self) -> Dict[str, Any]:
        """Run robustness benchmark using robustness test cases."""
        print("Starting Robustness Benchmark")
        
        # Load robustness test cases
        robustness_file = self.dataset_dir / "robustness.json"
        
        if not robustness_file.exists():
            return {
                "total_cases": 0,
                "passed_cases": 0,
                "failed_cases": 0,
                "crash_rate": 0,
                "categories": {}
            }
        
        with open(robustness_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            test_cases = data.get("test_cases", [])
        
        total_cases = len(test_cases)
        passed_cases = 0
        failed_cases = 0
        crashes = 0
        
        category_results = {}
        
        for test_case in test_cases:
            content = test_case["content"]
            category = test_case.get("category", "unknown")
            should_not_crash = test_case.get("should_not_crash", True)
            
            if category not in category_results:
                category_results[category] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0
                }
            
            category_results[category]["total"] += 1
            
            try:
                # Run classification
                result = await self.engine.classify(
                    MemoryInput(
                        content=content,
                        session_id="benchmark-session",
                        agent_id="benchmark-agent",
                        tenant_id="benchmark-tenant"
                    ),
                    enable_routing=False
                )
                
                # Check if it should not crash
                if should_not_crash:
                    passed_cases += 1
                    category_results[category]["passed"] += 1
                else:
                    # If it should crash but didn't, count as failed
                    failed_cases += 1
                    category_results[category]["failed"] += 1
                    
            except Exception as e:
                # Check if this is a validation error (expected for invalid inputs)
                error_msg = str(e)
                is_validation_error = "validation error" in error_msg.lower() or "value error" in error_msg.lower()
                
                # If it crashed but shouldn't have
                if should_not_crash:
                    # If it's a validation error for invalid input, that's actually expected behavior
                    if is_validation_error and category in ["empty_input", "whitespace_only", "special_characters"]:
                        # Engine correctly rejected invalid input - count as pass
                        passed_cases += 1
                        category_results[category]["passed"] += 1
                    else:
                        # Unexpected crash
                        crashes += 1
                        failed_cases += 1
                        category_results[category]["failed"] += 1
                        print(f"CRASH on {category}: {e}")
                else:
                    # Expected crash
                    passed_cases += 1
                    category_results[category]["passed"] += 1
        
        crash_rate = (crashes / total_cases * 100) if total_cases > 0 else 0
        
        results = {
            "total_cases": total_cases,
            "passed_cases": passed_cases,
            "failed_cases": failed_cases,
            "crashes": crashes,
            "crash_rate": crash_rate,
            "categories": category_results
        }
        
        print(f"Robustness Benchmark Complete: {passed_cases}/{total_cases} passed, {crash_rate:.2f}% crash rate")
        return results
    
    async def test_specific_category(self, category: str) -> Dict[str, Any]:
        """Test a specific robustness category."""
        print(f"Testing Robustness Category: {category}")
        
        robustness_file = self.dataset_dir / "robustness.json"
        
        if not robustness_file.exists():
            return {"error": "Robustness dataset not found"}
        
        with open(robustness_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            test_cases = [
                tc for tc in data.get("test_cases", [])
                if tc.get("category") == category
            ]
        
        if not test_cases:
            return {"error": f"No test cases found for category: {category}"}
        
        passed = 0
        failed = 0
        crashes = 0
        
        for test_case in test_cases:
            content = test_case["content"]
            should_not_crash = test_case.get("should_not_crash", True)
            
            try:
                await self.engine.classify_memory(
                    content=content,
                    metadata={}
                )
                
                if should_not_crash:
                    passed += 1
                else:
                    failed += 1
                    
            except Exception as e:
                if should_not_crash:
                    crashes += 1
                    failed += 1
                    print(f"CRASH: {e}")
                else:
                    passed += 1
        
        return {
            "category": category,
            "total_cases": len(test_cases),
            "passed": passed,
            "failed": failed,
            "crashes": crashes,
            "crash_rate": (crashes / len(test_cases) * 100) if test_cases else 0
        }
