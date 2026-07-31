"""Script to run the ClassificationBench benchmark suite."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
benchmarks_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(benchmarks_root))

from memory_classification.core.engine import ClassificationEngine
from memory_classification.config.defaults import get_default_config
from memory_classification.classifiers.identity import IdentityClassifier
from memory_classification.classifiers.goal import GoalClassifier
from memory_classification.classifiers.preference import PreferenceClassifier
from memory_classification.classifiers.relationship import RelationshipClassifier
from memory_classification.classifiers.project import ProjectClassifier
from memory_classification.classifiers.skill import SkillClassifier
from memory_classification.classifiers.procedural import ProceduralClassifier
from memory_classification.classifiers.task import TaskClassifier
from memory_classification.classifiers.episodic import EpisodicClassifier
from memory_classification.classifiers.semantic import SemanticClassifier
from memory_classification.classifiers.emotional import EmotionalClassifier
from memory_classification.classifiers.temporal import TemporalClassifier

from classification_bench import ClassificationBench


async def main():
    """Run the full benchmark suite."""
    print("Initializing ClassificationBench...")
    
    # Initialize classification engine
    config = get_default_config()
    engine = ClassificationEngine(config=config)
    
    # Register all classifiers
    print("Registering classifiers...")
    engine.register_classifier(IdentityClassifier())
    engine.register_classifier(GoalClassifier())
    engine.register_classifier(PreferenceClassifier())
    engine.register_classifier(RelationshipClassifier())
    engine.register_classifier(ProjectClassifier())
    engine.register_classifier(SkillClassifier())
    engine.register_classifier(ProceduralClassifier())
    engine.register_classifier(TaskClassifier())
    engine.register_classifier(EpisodicClassifier())
    engine.register_classifier(SemanticClassifier())
    engine.register_classifier(EmotionalClassifier())
    engine.register_classifier(TemporalClassifier())
    print("All classifiers registered.")
    
    # Initialize benchmark suite
    dataset_dir = Path(__file__).parent / "dataset"
    output_dir = Path(__file__).parent / "results"
    
    bench = ClassificationBench(
        classification_engine=engine,
        dataset_dir=dataset_dir,
        output_dir=output_dir
    )
    
    # Print dataset info
    print("\n" + "=" * 80)
    dataset_info = bench.get_dataset_info()
    print(f"Dataset Directory: {dataset_info['dataset_dir']}")
    print(f"Total Test Cases: {dataset_info['total_test_cases']}")
    print("\nDatasets:")
    for name, info in dataset_info['datasets'].items():
        print(f"  {name}: {info['test_cases']} test cases - {info['description']}")
    print("=" * 80 + "\n")
    
    # Run full benchmark suite
    print("Starting full benchmark suite...\n")
    results = await bench.run_full_suite()
    
    # Generate reports
    print("\nGenerating reports...")
    reports = bench.generate_reports(results)
    
    # Generate certificate
    print("\nGenerating production readiness certificate...")
    certificate = bench.generate_certificate(results)
    
    # Print summary
    print("\n" + "=" * 80)
    print("BENCHMARK SUITE COMPLETE")
    print("=" * 80)
    print(f"\nOverall Status: {certificate['status']}")
    print(f"Overall Score: {certificate['score']:.1f}%")
    
    # Print key metrics
    if "quality_benchmark" in results:
        q = results["quality_benchmark"]
        print(f"\nQuality Metrics:")
        print(f"  Precision: {q['precision']:.2f}%")
        print(f"  Recall: {q['recall']:.2f}%")
        print(f"  F1 Score: {q['f1_score']:.2f}%")
    
    if "latency_benchmark" in results:
        l = results["latency_benchmark"]
        print(f"\nLatency Metrics:")
        print(f"  P50: {l['p50_ms']:.2f}ms")
        print(f"  P95: {l['p95_ms']:.2f}ms")
        print(f"  P99: {l['p99_ms']:.2f}ms")
    
    if "load_benchmark" in results:
        ld = results["load_benchmark"]
        print(f"\nLoad Metrics:")
        print(f"  Throughput: {ld['throughput_rps']:.2f} RPS")
        print(f"  Error Rate: {ld['error_rate']:.2f}%")
    
    if "robustness_benchmark" in results:
        r = results["robustness_benchmark"]
        print(f"\nRobustness Metrics:")
        print(f"  Passed: {r['passed_cases']}/{r['total_cases']}")
        print(f"  Crash Rate: {r['crash_rate']:.2f}%")
    
    print("\n" + "=" * 80)
    print(f"Reports saved to: {output_dir}")
    print("=" * 80)
    
    # Validate pass criteria
    print("\nValidating Pass Criteria:")
    print("-" * 80)
    
    passed_criteria = []
    failed_criteria = []
    
    # Load criteria
    if "load_benchmark" in results:
        ld = results["load_benchmark"]
        if ld['throughput_rps'] >= 500:
            passed_criteria.append(f"✓ Load Throughput: {ld['throughput_rps']:.2f} RPS (≥500)")
        else:
            failed_criteria.append(f"✗ Load Throughput: {ld['throughput_rps']:.2f} RPS (<500)")
        
        if ld['error_rate'] < 0.1:
            passed_criteria.append(f"✓ Load Error Rate: {ld['error_rate']:.2f}% (<0.1%)")
        else:
            failed_criteria.append(f"✗ Load Error Rate: {ld['error_rate']:.2f}% (≥0.1%)")
    
    # Latency criteria
    if "latency_benchmark" in results:
        l = results["latency_benchmark"]
        if l['p50_ms'] < 5:
            passed_criteria.append(f"✓ Latency P50: {l['p50_ms']:.2f}ms (<5ms)")
        else:
            failed_criteria.append(f"✗ Latency P50: {l['p50_ms']:.2f}ms (≥5ms)")
        
        if l['p95_ms'] < 15:
            passed_criteria.append(f"✓ Latency P95: {l['p95_ms']:.2f}ms (<15ms)")
        else:
            failed_criteria.append(f"✗ Latency P95: {l['p95_ms']:.2f}ms (≥15ms)")
        
        if l['p99_ms'] < 30:
            passed_criteria.append(f"✓ Latency P99: {l['p99_ms']:.2f}ms (<30ms)")
        else:
            failed_criteria.append(f"✗ Latency P99: {l['p99_ms']:.2f}ms (≥30ms)")
    
    # Quality criteria
    if "quality_benchmark" in results:
        q = results["quality_benchmark"]
        if q['precision'] > 15:
            passed_criteria.append(f"✓ Quality Precision: {q['precision']:.2f}% (>15%)")
        else:
            failed_criteria.append(f"✗ Quality Precision: {q['precision']:.2f}% (≤15%)")
        
        if q['recall'] > 15:
            passed_criteria.append(f"✓ Quality Recall: {q['recall']:.2f}% (>15%)")
        else:
            failed_criteria.append(f"✗ Quality Recall: {q['recall']:.2f}% (≤15%)")
        
        if q['f1_score'] > 15:
            passed_criteria.append(f"✓ Quality F1 Score: {q['f1_score']:.2f}% (>15%)")
        else:
            failed_criteria.append(f"✗ Quality F1 Score: {q['f1_score']:.2f}% (≤15%)")
    
    # Robustness criteria
    if "robustness_benchmark" in results:
        r = results["robustness_benchmark"]
        if r['crash_rate'] == 0:
            passed_criteria.append(f"✓ Robustness Crash Rate: {r['crash_rate']:.2f}% (=0%)")
        else:
            failed_criteria.append(f"✗ Robustness Crash Rate: {r['crash_rate']:.2f}% (>0%)")
    
    print("\nPASSED:")
    for criteria in passed_criteria:
        print(f"  {criteria}")
    
    print("\nFAILED:")
    for criteria in failed_criteria:
        print(f"  {criteria}")
    
    print("\n" + "-" * 80)
    print(f"Total Passed: {len(passed_criteria)}")
    print(f"Total Failed: {len(failed_criteria)}")
    
    overall_pass = len(failed_criteria) == 0
    print(f"\nFINAL RESULT: {'PASS ✓' if overall_pass else 'FAIL ✗'}")
    print("=" * 80)
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
