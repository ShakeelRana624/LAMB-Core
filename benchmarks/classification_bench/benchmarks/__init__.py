"""Benchmark implementations for ClassificationBench."""

from .load_benchmark import LoadBenchmark
from .latency_benchmark import LatencyBenchmark
from .quality_benchmark import QualityBenchmark
from .robustness_benchmark import RobustnessBenchmark
from .scalability_benchmark import ScalabilityBenchmark
from .fault_tolerance_benchmark import FaultToleranceBenchmark

__all__ = [
    "LoadBenchmark",
    "LatencyBenchmark",
    "QualityBenchmark",
    "RobustnessBenchmark",
    "ScalabilityBenchmark",
    "FaultToleranceBenchmark"
]
