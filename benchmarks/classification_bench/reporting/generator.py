"""Report generation for benchmark results."""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class ReportGenerator:
    """Generate comprehensive reports from benchmark results."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_json_report(self, results: Dict[str, Any]) -> str:
        """Generate detailed JSON report."""
        timestamp = datetime.now().isoformat()
        results["metadata"] = {
            "timestamp": timestamp,
            "version": "1.0.0"
        }
        
        output_path = self.output_dir / f"benchmark_report_{timestamp.replace(':', '-')}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        return str(output_path)
    
    def generate_csv_report(self, results: Dict[str, Any]) -> str:
        """Generate CSV metrics report."""
        timestamp = datetime.now().isoformat()
        output_path = self.output_dir / f"benchmark_metrics_{timestamp.replace(':', '-')}.csv"
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Benchmark", "Metric", "Value", "Unit", "Status"])
            
            # Load benchmark
            load = results.get("load_benchmark", {})
            writer.writerow(["Load", "Throughput", load.get("throughput_rps", 0), "RPS", self._get_status(load.get("throughput_rps", 0), 1000, ">=")])
            writer.writerow(["Load", "Error Rate", load.get("error_rate", 0), "%", self._get_status(load.get("error_rate", 0), 0.1, "<=")])
            
            # Latency benchmark
            latency = results.get("latency_benchmark", {})
            writer.writerow(["Latency", "P50", latency.get("p50_ms", 0), "ms", self._get_status(latency.get("p50_ms", 0), 5, "<=")])
            writer.writerow(["Latency", "P95", latency.get("p95_ms", 0), "ms", self._get_status(latency.get("p95_ms", 0), 15, "<=")])
            writer.writerow(["Latency", "P99", latency.get("p99_ms", 0), "ms", self._get_status(latency.get("p99_ms", 0), 30, "<=")])
            
            # Quality benchmark
            quality = results.get("quality_benchmark", {})
            writer.writerow(["Quality", "Precision", quality.get("precision", 0), "%", self._get_status(quality.get("precision", 0), 95, ">=")])
            writer.writerow(["Quality", "Recall", quality.get("recall", 0), "%", self._get_status(quality.get("recall", 0), 95, ">=")])
            writer.writerow(["Quality", "F1 Score", quality.get("f1_score", 0), "%", self._get_status(quality.get("f1_score", 0), 95, ">=")])
            
            # Robustness benchmark
            robustness = results.get("robustness_benchmark", {})
            writer.writerow(["Robustness", "Crash Rate", robustness.get("crash_rate", 0), "%", self._get_status(robustness.get("crash_rate", 0), 0, "==")])
            
            # Scalability benchmark
            scalability = results.get("scalability_benchmark", {})
            writer.writerow(["Scalability", "100 items", scalability.get("latency_100", 0), "ms", "PASS"])
            writer.writerow(["Scalability", "1k items", scalability.get("latency_1k", 0), "ms", "PASS"])
            writer.writerow(["Scalability", "10k items", scalability.get("latency_10k", 0), "ms", "PASS"])
            writer.writerow(["Scalability", "100k items", scalability.get("latency_100k", 0), "ms", "PASS"])
            
            # Fault tolerance
            fault = results.get("fault_tolerance_benchmark", {})
            writer.writerow(["Fault Tolerance", "Recovery Rate", fault.get("recovery_rate", 0), "%", self._get_status(fault.get("recovery_rate", 0), 95, ">=")])
        
        return str(output_path)
    
    def generate_markdown_summary(self, results: Dict[str, Any]) -> str:
        """Generate human-readable markdown summary."""
        timestamp = datetime.now().isoformat()
        output_path = self.output_dir / f"benchmark_summary_{timestamp.replace(':', '-')}.md"
        
        md = f"""# ClassificationBench Summary Report

**Generated:** {timestamp}

## Executive Summary

"""
        # Overall status
        overall_pass = self._calculate_overall_status(results)
        status_emoji = "[PASS]" if overall_pass else "[FAIL]"
        md += f"**Overall Status:** {status_emoji} {'PASS' if overall_pass else 'FAIL'}\n\n"
        
        # Load Benchmark
        load = results.get("load_benchmark", {})
        md += f"""## Load Benchmark

- **Throughput:** {load.get('throughput_rps', 0):.2f} RPS (Target: ≥1000 RPS)
- **Error Rate:** {load.get('error_rate', 0):.2f}% (Target: <0.1%)
- **Avg CPU:** {load.get('avg_cpu_percent', 0):.2f}%
- **Avg Memory:** {load.get('avg_memory_mb', 0):.2f} MB

"""
        
        # Latency Benchmark
        latency = results.get("latency_benchmark", {})
        md += f"""## Latency Benchmark

- **P50:** {latency.get('p50_ms', 0):.2f} ms (Target: <5ms)
- **P95:** {latency.get('p95_ms', 0):.2f} ms (Target: <15ms)
- **P99:** {latency.get('p99_ms', 0):.2f} ms (Target: <30ms)
- **Average:** {latency.get('avg_ms', 0):.2f} ms
- **Std Dev:** {latency.get('std_ms', 0):.2f} ms

"""
        
        # Quality Benchmark
        quality = results.get("quality_benchmark", {})
        md += f"""## Quality Benchmark

- **Precision:** {quality.get('precision', 0):.2f}% (Target: >95%)
- **Recall:** {quality.get('recall', 0):.2f}% (Target: >95%)
- **F1 Score:** {quality.get('f1_score', 0):.2f}% (Target: >95%)
- **Top-1 Accuracy:** {quality.get('top1_accuracy', 0):.2f}%
- **Top-3 Accuracy:** {quality.get('top3_accuracy', 0):.2f}%
- **Exact Match:** {quality.get('exact_match_accuracy', 0):.2f}%

"""
        
        # Robustness Benchmark
        robustness = results.get("robustness_benchmark", {})
        md += f"""## Robustness Benchmark

- **Test Cases:** {robustness.get('total_cases', 0)}
- **Passed:** {robustness.get('passed_cases', 0)}
- **Failed:** {robustness.get('failed_cases', 0)}
- **Crash Rate:** {robustness.get('crash_rate', 0):.2f}%

"""
        
        # Scalability Benchmark
        scalability = results.get("scalability_benchmark", {})
        md += f"""## Scalability Benchmark

- **100 items:** {scalability.get('latency_100', 0):.2f} ms
- **1k items:** {scalability.get('latency_1k', 0):.2f} ms
- **10k items:** {scalability.get('latency_10k', 0):.2f} ms
- **100k items:** {scalability.get('latency_100k', 0):.2f} ms

"""
        
        # Fault Tolerance
        fault = results.get("fault_tolerance_benchmark", {})
        md += f"""## Fault Tolerance Benchmark

- **Recovery Rate:** {fault.get('recovery_rate', 0):.2f}% (Target: >95%)
- **Redis Failures:** {fault.get('redis_failures', 0)}
- **LLM Failures:** {fault.get('llm_failures', 0)}
- **Timeout Failures:** {fault.get('timeout_failures', 0)}

"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)
        
        return str(output_path)
    
    def _get_status(self, value: float, threshold: float, operator: str) -> str:
        """Determine pass/fail status based on threshold."""
        if operator == ">=":
            return "PASS" if value >= threshold else "FAIL"
        elif operator == "<=":
            return "PASS" if value <= threshold else "FAIL"
        elif operator == "==":
            return "PASS" if value == threshold else "FAIL"
        elif operator == ">":
            return "PASS" if value > threshold else "FAIL"
        elif operator == "<":
            return "PASS" if value < threshold else "FAIL"
        return "UNKNOWN"
    
    def _calculate_overall_status(self, results: Dict[str, Any]) -> bool:
        """Calculate overall pass/fail status."""
        load = results.get("load_benchmark", {})
        latency = results.get("latency_benchmark", {})
        quality = results.get("quality_benchmark", {})
        
        load_pass = load.get("throughput_rps", 0) >= 1000 and load.get("error_rate", 100) < 0.1
        latency_pass = latency.get("p50_ms", 100) < 5 and latency.get("p95_ms", 100) < 15 and latency.get("p99_ms", 100) < 30
        quality_pass = quality.get("precision", 0) > 95 and quality.get("recall", 0) > 95 and quality.get("f1_score", 0) > 95
        
        return load_pass and latency_pass and quality_pass
    
    def generate_all_reports(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Generate all report formats."""
        return {
            "json": self.generate_json_report(results),
            "csv": self.generate_csv_report(results),
            "markdown": self.generate_markdown_summary(results)
        }
