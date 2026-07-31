"""Metrics calculator for classification benchmark results."""

import numpy as np
from typing import List, Dict, Set, Any
from dataclasses import dataclass


@dataclass
class QualityMetrics:
    """Quality metrics for classification results."""
    precision: float
    recall: float
    f1_score: float
    exact_match_accuracy: float
    top1_accuracy: float
    top3_accuracy: float
    hamming_loss: float


class MetricsCalculator:
    """Calculate various metrics for benchmark evaluation."""
    
    @staticmethod
    def calculate_precision_recall_f1(
        predicted: List[Set[str]], 
        expected: List[Set[str]]
    ) -> tuple[float, float, float]:
        """Calculate precision, recall, and F1 score."""
        if not predicted or not expected:
            return 0.0, 0.0, 0.0
        
        total_precision = 0.0
        total_recall = 0.0
        valid_samples = 0
        
        for pred_set, exp_set in zip(predicted, expected):
            if not exp_set:
                continue
            
            valid_samples += 1
            true_positives = len(pred_set & exp_set)
            false_positives = len(pred_set - exp_set)
            false_negatives = len(exp_set - pred_set)
            
            precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
            recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
            
            total_precision += precision
            total_recall += recall
        
        avg_precision = total_precision / valid_samples if valid_samples > 0 else 0.0
        avg_recall = total_recall / valid_samples if valid_samples > 0 else 0.0
        
        if avg_precision + avg_recall > 0:
            f1 = 2 * (avg_precision * avg_recall) / (avg_precision + avg_recall)
        else:
            f1 = 0.0
        
        return avg_precision, avg_recall, f1
    
    @staticmethod
    def calculate_exact_match_accuracy(
        predicted: List[Set[str]], 
        expected: List[Set[str]]
    ) -> float:
        """Calculate exact match accuracy."""
        if not predicted or not expected:
            return 0.0
        
        matches = sum(1 for pred, exp in zip(predicted, expected) if pred == exp)
        return matches / len(predicted)
    
    @staticmethod
    def calculate_top_k_accuracy(
        predicted: List[List[str]], 
        expected: List[Set[str]], 
        k: int
    ) -> float:
        """Calculate top-k accuracy."""
        if not predicted or not expected:
            return 0.0
        
        matches = 0
        for pred_list, exp_set in zip(predicted, expected):
            top_k = set(pred_list[:k])
            if top_k & exp_set:
                matches += 1
        
        return matches / len(predicted)
    
    @staticmethod
    def calculate_hamming_loss(
        predicted: List[Set[str]], 
        expected: List[Set[str]],
        all_labels: Set[str]
    ) -> float:
        """Calculate Hamming loss for multi-label classification."""
        if not predicted or not expected or not all_labels:
            return 0.0
        
        total_errors = 0
        total_labels = len(all_labels) * len(predicted)
        
        for pred_set, exp_set in zip(predicted, expected):
            for label in all_labels:
                if (label in pred_set) != (label in exp_set):
                    total_errors += 1
        
        return total_errors / total_labels if total_labels > 0 else 0.0
    
    @staticmethod
    def calculate_percentiles(values: List[float]) -> Dict[str, float]:
        """Calculate P50, P95, P99 percentiles."""
        if not values:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        def get_percentile(p: float) -> float:
            idx = int(p * n)
            return sorted_values[min(idx, n - 1)]
        
        return {
            "p50": get_percentile(0.50),
            "p95": get_percentile(0.95),
            "p99": get_percentile(0.99)
        }
    
    @staticmethod
    def calculate_latency_stats(latencies: List[float]) -> Dict[str, float]:
        """Calculate latency statistics."""
        if not latencies:
            return {
                "avg_ms": 0.0,
                "std_ms": 0.0,
                "min_ms": 0.0,
                "max_ms": 0.0,
                "p50_ms": 0.0,
                "p95_ms": 0.0,
                "p99_ms": 0.0
            }
        
        percentiles = MetricsCalculator.calculate_percentiles(latencies)
        
        return {
            "avg_ms": np.mean(latencies),
            "std_ms": np.std(latencies),
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "p50_ms": percentiles["p50"],
            "p95_ms": percentiles["p95"],
            "p99_ms": percentiles["p99"]
        }
    
    @staticmethod
    def calculate_throughput(
        total_requests: int, 
        duration_seconds: float
    ) -> float:
        """Calculate throughput in requests per second."""
        if duration_seconds <= 0:
            return 0.0
        return total_requests / duration_seconds
    
    @staticmethod
    def calculate_error_rate(
        total_requests: int, 
        failed_requests: int
    ) -> float:
        """Calculate error rate as percentage."""
        if total_requests <= 0:
            return 0.0
        return (failed_requests / total_requests) * 100
    
    @staticmethod
    def calculate_quality_metrics(
        predicted: List[Set[str]],
        expected: List[Set[str]],
        predicted_ranked: List[List[str]],
        all_labels: Set[str]
    ) -> QualityMetrics:
        """Calculate comprehensive quality metrics."""
        precision, recall, f1 = MetricsCalculator.calculate_precision_recall_f1(predicted, expected)
        exact_match = MetricsCalculator.calculate_exact_match_accuracy(predicted, expected)
        top1 = MetricsCalculator.calculate_top_k_accuracy(predicted_ranked, expected, 1)
        top3 = MetricsCalculator.calculate_top_k_accuracy(predicted_ranked, expected, 3)
        hamming = MetricsCalculator.calculate_hamming_loss(predicted, expected, all_labels)
        
        return QualityMetrics(
            precision=precision,
            recall=recall,
            f1_score=f1,
            exact_match_accuracy=exact_match,
            top1_accuracy=top1,
            top3_accuracy=top3,
            hamming_loss=hamming
        )
