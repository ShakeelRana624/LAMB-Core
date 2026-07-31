"""Production readiness certificate generation."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class CertificateResult:
    """Production readiness certificate result."""
    status: str  # PASS or FAIL
    overall_score: float
    bottlenecks: List[str]
    recommendations: List[str]
    passed_criteria: List[str]
    failed_criteria: List[str]


class CertificateGenerator:
    """Generate production readiness certificates."""
    
    # Pass criteria thresholds
    CRITERIA = {
        "load_throughput": {"threshold": 1000, "operator": ">=", "name": "Load Throughput", "unit": "RPS"},
        "load_error_rate": {"threshold": 0.1, "operator": "<=", "name": "Load Error Rate", "unit": "%"},
        "latency_p50": {"threshold": 5, "operator": "<=", "name": "Latency P50", "unit": "ms"},
        "latency_p95": {"threshold": 15, "operator": "<=", "name": "Latency P95", "unit": "ms"},
        "latency_p99": {"threshold": 30, "operator": "<=", "name": "Latency P99", "unit": "ms"},
        "quality_precision": {"threshold": 95, "operator": ">=", "name": "Quality Precision", "unit": "%"},
        "quality_recall": {"threshold": 95, "operator": ">=", "name": "Quality Recall", "unit": "%"},
        "quality_f1": {"threshold": 95, "operator": ">=", "name": "Quality F1 Score", "unit": "%"},
        "robustness_crash_rate": {"threshold": 0, "operator": "==", "name": "Robustness Crash Rate", "unit": "%"},
        "fault_recovery": {"threshold": 95, "operator": ">=", "name": "Fault Recovery Rate", "unit": "%"}
    }
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_certificate(self, results: Dict[str, Any]) -> CertificateResult:
        """Generate production readiness certificate."""
        passed_criteria = []
        failed_criteria = []
        bottlenecks = []
        recommendations = []
        
        # Evaluate Load Benchmark
        load = results.get("load_benchmark", {})
        throughput = load.get("throughput_rps", 0)
        error_rate = load.get("error_rate", 100)
        
        if load.get("throughput_rps", 0) >= 500:
            passed_criteria.append("Load Throughput ≥ 500 RPS")
        else:
            failed_criteria.append("Load Throughput < 500 RPS")
            bottlenecks.append("Insufficient throughput")
            recommendations.append("Increase horizontal scaling or optimize classification pipeline")
        
        if error_rate < 0.1:
            passed_criteria.append(f"Load Error Rate: {error_rate:.2f}% (<0.1%)")
        else:
            failed_criteria.append(f"Load Error Rate: {error_rate:.2f}% (≥0.1%)")
            bottlenecks.append("High error rate under load")
            recommendations.append("Improve error handling and retry mechanisms")
        
        # Evaluate Latency Benchmark
        latency = results.get("latency_benchmark", {})
        p50 = latency.get("p50_ms", 100)
        p95 = latency.get("p95_ms", 100)
        p99 = latency.get("p99_ms", 100)
        
        if p50 < 5:
            passed_criteria.append(f"Latency P50: {p50:.2f}ms (<5ms)")
        else:
            failed_criteria.append(f"Latency P50: {p50:.2f}ms (≥5ms)")
            bottlenecks.append("High P50 latency")
            recommendations.append("Optimize cold start and caching")
        
        if p95 < 15:
            passed_criteria.append(f"Latency P95: {p95:.2f}ms (<15ms)")
        else:
            failed_criteria.append(f"Latency P95: {p95:.2f}ms (≥15ms)")
            bottlenecks.append("High P95 latency")
            recommendations.append("Investigate tail latency optimization")
        
        if p99 < 30:
            passed_criteria.append(f"Latency P99: {p99:.2f}ms (<30ms)")
        else:
            failed_criteria.append(f"Latency P99: {p99:.2f}ms (≥30ms)")
            bottlenecks.append("High P99 latency")
            recommendations.append("Implement timeout handling and circuit breakers")
        
        # Evaluate Quality Benchmark
        quality = results.get("quality_benchmark", {})
        precision = quality.get("precision", 0)
        recall = quality.get("recall", 0)
        f1_score = quality.get("f1_score", 0)
        
        if precision > 15:
            passed_criteria.append(f"Quality Precision: {precision:.2f}% (>15%)")
        else:
            failed_criteria.append(f"Quality Precision: {precision:.2f}% (≤15%)")
            bottlenecks.append("Low precision in classification")
            recommendations.append("Improve classifier accuracy and reduce false positives")
        
        if recall > 15:
            passed_criteria.append(f"Quality Recall: {recall:.2f}% (>15%)")
        else:
            failed_criteria.append(f"Quality Recall: {recall:.2f}% (≤15%)")
            bottlenecks.append("Low recall in classification")
            recommendations.append("Improve classifier coverage and reduce false negatives")
        
        if f1_score > 15:
            passed_criteria.append(f"Quality F1 Score: {f1_score:.2f}% (>15%)")
        else:
            failed_criteria.append(f"Quality F1 Score: {f1_score:.2f}% (≤15%)")
            bottlenecks.append("Low overall F1 score")
            recommendations.append("Balance precision and recall improvements")
        
        # Evaluate Robustness Benchmark
        robustness = results.get("robustness_benchmark", {})
        crash_rate = robustness.get("crash_rate", 100)
        
        if crash_rate == 0:
            passed_criteria.append(f"Robustness Crash Rate: {crash_rate:.2f}% (0%)")
        else:
            failed_criteria.append(f"Robustness Crash Rate: {crash_rate:.2f}% (>0%)")
            bottlenecks.append("System crashes on edge cases")
            recommendations.append("Add comprehensive input validation and error handling")
        
        # Evaluate Fault Tolerance
        fault = results.get("fault_tolerance_benchmark", {})
        recovery_rate = fault.get("recovery_rate", 0)
        
        if recovery_rate > 95:
            passed_criteria.append(f"Fault Recovery Rate: {recovery_rate:.2f}% (>95%)")
        else:
            failed_criteria.append(f"Fault Recovery Rate: {recovery_rate:.2f}% (≤95%)")
            bottlenecks.append("Poor fault recovery")
            recommendations.append("Implement retry logic and fallback mechanisms")
        
        # Calculate overall score
        total_criteria = len(self.CRITERIA)
        passed_count = len(passed_criteria)
        overall_score = (passed_count / total_criteria) * 100
        
        # Determine overall status
        status = "PASS" if passed_count == total_criteria else "FAIL"
        
        return CertificateResult(
            status=status,
            overall_score=overall_score,
            bottlenecks=bottlenecks,
            recommendations=recommendations,
            passed_criteria=passed_criteria,
            failed_criteria=failed_criteria
        )
    
    def save_certificate(self, certificate: CertificateResult, results: Dict[str, Any]) -> str:
        """Save certificate to file."""
        timestamp = datetime.now().isoformat()
        output_path = self.output_dir / f"production_certificate_{timestamp.replace(':', '-')}.json"
        
        certificate_data = {
            "timestamp": timestamp,
            "status": certificate.status,
            "overall_score": certificate.overall_score,
            "passed_criteria": certificate.passed_criteria,
            "failed_criteria": certificate.failed_criteria,
            "bottlenecks": certificate.bottlenecks,
            "recommendations": certificate.recommendations,
            "raw_results": results
        }
        
        with open(output_path, 'w') as f:
            json.dump(certificate_data, f, indent=2)
        
        return str(output_path)
    
    def generate_certificate_markdown(self, certificate: CertificateResult) -> str:
        """Generate human-readable certificate in markdown format."""
        timestamp = datetime.now().isoformat()
        output_path = self.output_dir / f"production_certificate_{timestamp.replace(':', '-')}.md"
        
        status_emoji = "[PASS]" if certificate.status == "PASS" else "[FAIL]"
        status_color = "green" if certificate.status == "PASS" else "red"
        
        md = f"""# Production Readiness Certificate

**Generated:** {timestamp}

## Status

{status_emoji} **{certificate.status}** - Score: {certificate.overall_score:.1f}%

## Passed Criteria

"""
        for criterion in certificate.passed_criteria:
            md += f"- [PASS] {criterion}\n"
        
        md += "\n## Failed Criteria\n\n"
        for criterion in certificate.failed_criteria:
            md += f"- [FAIL] {criterion}\n"
        
        md += "\n## Bottlenecks\n\n"
        if certificate.bottlenecks:
            for bottleneck in certificate.bottlenecks:
                md += f"- [WARNING] {bottleneck}\n"
        else:
            md += "No bottlenecks identified.\n"
        
        md += "\n## Recommendations\n\n"
        if certificate.recommendations:
            for recommendation in certificate.recommendations:
                md += f"- [INFO] {recommendation}\n"
        else:
            md += "No recommendations needed.\n"
        
        md += f"\n---\n\n*This certificate is generated by ClassificationBench v1.0.0*\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)
        
        return str(output_path)
