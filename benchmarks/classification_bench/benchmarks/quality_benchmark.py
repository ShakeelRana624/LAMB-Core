"""Quality benchmark for testing classification accuracy."""

import json
from typing import Dict, Any, List, Set
from pathlib import Path

from classification_bench.metrics.calculator import MetricsCalculator, QualityMetrics
from memory_classification.core.interfaces import MemoryInput


class QualityBenchmark:
    """Benchmark classification quality using curated test cases."""
    
    def __init__(self, classification_engine, dataset_dir: Path):
        self.engine = classification_engine
        self.dataset_dir = dataset_dir
        self.calculator = MetricsCalculator()
    
    async def run(self) -> Dict[str, Any]:
        """Run quality benchmark using all 300 test cases."""
        print("Starting Quality Benchmark")
        
        # Load all test cases
        all_test_cases = self._load_all_test_cases()
        
        predicted_sets: List[Set[str]] = []
        predicted_ranked: List[List[str]] = []
        expected_sets: List[Set[str]] = []
        all_labels: Set[str] = set()
        
        total_cases = len(all_test_cases)
        passed_cases = 0
        failed_cases = 0
        
        for test_case in all_test_cases:
            content = test_case["content"]
            expected_types = set(test_case.get("expected_types", []))
            confidence_threshold = test_case.get("confidence_threshold", 0.5)
            
            # Collect all possible labels
            all_labels.update(expected_types)
            
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
                
                # Extract predicted types from UniversalMemoryObject
                predicted_types = set()
                predicted_ranked_list = []
                
                if hasattr(result, 'memory_types'):
                    predicted_types = set(result.memory_types)
                    predicted_ranked_list = list(result.memory_types)
                
                if hasattr(result, 'confidence_scores'):
                    # Sort by confidence for ranked list
                    predicted_ranked_list = sorted(
                        result.confidence_scores.keys(),
                        key=lambda x: result.confidence_scores[x],
                        reverse=True
                    )
                
                predicted_sets.append(predicted_types)
                predicted_ranked.append(predicted_ranked_list)
                expected_sets.append(expected_types)
                
                # Check if expected types are in predictions
                if expected_types.issubset(predicted_types):
                    passed_cases += 1
                else:
                    failed_cases += 1
                    
            except Exception as e:
                print(f"Classification failed for test case {test_case.get('id', 'unknown')}: {e}")
                predicted_sets.append(set())
                predicted_ranked.append([])
                expected_sets.append(expected_types)
                failed_cases += 1
        
        # Calculate quality metrics
        quality_metrics = self.calculator.calculate_quality_metrics(
            predicted_sets,
            expected_sets,
            predicted_ranked,
            all_labels
        )
        
        results = {
            "total_cases": total_cases,
            "passed_cases": passed_cases,
            "failed_cases": failed_cases,
            "accuracy": (passed_cases / total_cases * 100) if total_cases > 0 else 0,
            "precision": quality_metrics.precision * 100,
            "recall": quality_metrics.recall * 100,
            "f1_score": quality_metrics.f1_score * 100,
            "exact_match_accuracy": quality_metrics.exact_match_accuracy * 100,
            "top1_accuracy": quality_metrics.top1_accuracy * 100,
            "top3_accuracy": quality_metrics.top3_accuracy * 100,
            "hamming_loss": quality_metrics.hamming_loss
        }
        
        print(f"Quality Benchmark Complete: Precision={results['precision']:.2f}%, Recall={results['recall']:.2f}%, F1={results['f1_score']:.2f}%")
        return results
    
    async def run_per_memory_type(self) -> Dict[str, Dict[str, Any]]:
        """Run quality benchmark per memory type."""
        print("Starting Per-Memory-Type Quality Benchmark")
        
        dataset_files = [
            "identity.json", "goal.json", "preference.json",
            "relationship.json", "project.json", "skill.json",
            "procedural.json", "task.json", "episodic.json",
            "semantic.json", "emotional.json", "temporal.json"
        ]
        
        per_type_results = {}
        
        for filename in dataset_files:
            memory_type = filename.replace(".json", "")
            file_path = self.dataset_dir / filename
            
            if not file_path.exists():
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                test_cases = data.get("test_cases", [])
            
            predicted_sets: List[Set[str]] = []
            expected_sets: List[Set[str]] = []
            all_labels: Set[str] = set()
            
            for test_case in test_cases:
                content = test_case["content"]
                expected_types = set(test_case.get("expected_types", [f"{memory_type}_memory"]))
                confidence_threshold = test_case.get("confidence_threshold", 0.5)
                
                all_labels.update(expected_types)
                
                try:
                    result = await self.engine.classify_memory(
                        content=content,
                        metadata={}
                    )
                    
                    predicted_types = set()
                    if hasattr(result, 'classifications'):
                        for classification in result.classifications:
                            if classification.confidence >= confidence_threshold:
                                predicted_types.add(classification.memory_type)
                    
                    predicted_sets.append(predicted_types)
                    expected_sets.append(expected_types)
                    
                except Exception as e:
                    predicted_sets.append(set())
                    expected_sets.append(expected_types)
            
            if predicted_sets:
                precision, recall, f1 = self.calculator.calculate_precision_recall_f1(
                    predicted_sets, expected_sets
                )
                
                per_type_results[memory_type] = {
                    "total_cases": len(test_cases),
                    "precision": precision * 100,
                    "recall": recall * 100,
                    "f1_score": f1 * 100
                }
        
        return per_type_results
    
    def _load_all_test_cases(self) -> list:
        """Load all test cases from all dataset files."""
        all_test_cases = []
        
        dataset_files = [
            "identity.json", "goal.json", "preference.json",
            "relationship.json", "project.json", "skill.json",
            "procedural.json", "task.json", "episodic.json",
            "semantic.json", "emotional.json", "temporal.json",
            "robustness.json"
        ]
        
        for filename in dataset_files:
            file_path = self.dataset_dir / filename
            if file_path.exists():
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_test_cases.extend(data.get("test_cases", []))
        
        return all_test_cases
