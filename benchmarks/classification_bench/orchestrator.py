"""Main orchestrator for ClassificationBench benchmark suite."""

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .benchmarks import (
    LoadBenchmark,
    LatencyBenchmark,
    QualityBenchmark,
    RobustnessBenchmark,
    ScalabilityBenchmark,
    FaultToleranceBenchmark
)
from .reporting import ReportGenerator, CertificateGenerator
from .utils import ChartGenerator
from .dataset import DatasetLoader


class ClassificationBench:
    """Main benchmark orchestrator for Memory Classification Engine."""
    
    def __init__(
        self,
        classification_engine,
        dataset_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None
    ):
        """Initialize the benchmark suite.
        
        Args:
            classification_engine: The classification engine to benchmark
            dataset_dir: Directory containing benchmark datasets
            output_dir: Directory for benchmark reports and outputs
        """
        self.engine = classification_engine
        
        # Set default directories
        if dataset_dir is None:
            dataset_dir = Path(__file__).parent / "dataset"
        if output_dir is None:
            output_dir = Path(__file__).parent / "results"
        
        self.dataset_dir = Path(dataset_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.dataset_loader = DatasetLoader(self.dataset_dir)
        self.report_generator = ReportGenerator(self.output_dir)
        self.certificate_generator = CertificateGenerator(self.output_dir)
        self.chart_generator = ChartGenerator(self.output_dir)
        
        # Initialize benchmarks
        self.load_benchmark = LoadBenchmark(self.engine, self.dataset_dir)
        self.latency_benchmark = LatencyBenchmark(self.engine, self.dataset_dir)
        self.quality_benchmark = QualityBenchmark(self.engine, self.dataset_dir)
        self.robustness_benchmark = RobustnessBenchmark(self.engine, self.dataset_dir)
        self.scalability_benchmark = ScalabilityBenchmark(self.engine, self.dataset_dir)
        self.fault_tolerance_benchmark = FaultToleranceBenchmark(self.engine, self.dataset_dir)
    
    async def run_full_suite(self) -> Dict[str, Any]:
        """Run the complete benchmark suite."""
        print("=" * 80)
        print("ClassificationBench - Full Benchmark Suite")
        print("=" * 80)
        print(f"Started at: {datetime.now().isoformat()}")
        print(f"Dataset directory: {self.dataset_dir}")
        print(f"Output directory: {self.output_dir}")
        print()
        
        results = {}
        
        # Run all benchmarks
        try:
            print("Running Quality Benchmark...")
            results["quality_benchmark"] = await self.quality_benchmark.run()
            print()
            
            print("Running Latency Benchmark...")
            results["latency_benchmark"] = await self.latency_benchmark.run()
            print()
            
            print("Running Robustness Benchmark...")
            results["robustness_benchmark"] = await self.robustness_benchmark.run()
            print()
            
            print("Running Scalability Benchmark...")
            results["scalability_benchmark"] = await self.scalability_benchmark.run()
            print()
            
            print("Running Fault Tolerance Benchmark...")
            results["fault_tolerance_benchmark"] = await self.fault_tolerance_benchmark.run()
            print()
            
            print("Running Load Benchmark...")
            results["load_benchmark"] = await self.load_benchmark.run()
            print()
            
        except Exception as e:
            print(f"Error during benchmark execution: {e}")
            results["error"] = str(e)
        
        print(f"Completed at: {datetime.now().isoformat()}")
        print("=" * 80)
        
        return results
    
    async def run_quick_suite(self) -> Dict[str, Any]:
        """Run a quick benchmark subset for faster feedback."""
        print("Running Quick Benchmark Suite...")
        
        results = {}
        
        # Run only quality and latency for quick feedback
        try:
            results["quality_benchmark"] = await self.quality_benchmark.run()
            results["latency_benchmark"] = await self.latency_benchmark.run()
            results["robustness_benchmark"] = await self.robustness_benchmark.run()
        except Exception as e:
            print(f"Error during quick benchmark: {e}")
            results["error"] = str(e)
        
        return results
    
    async def run_specific_benchmark(self, benchmark_name: str) -> Dict[str, Any]:
        """Run a specific benchmark by name."""
        print(f"Running {benchmark_name}...")
        
        benchmarks = {
            "load": self.load_benchmark,
            "latency": self.latency_benchmark,
            "quality": self.quality_benchmark,
            "robustness": self.robustness_benchmark,
            "scalability": self.scalability_benchmark,
            "fault_tolerance": self.fault_tolerance_benchmark
        }
        
        if benchmark_name not in benchmarks:
            raise ValueError(f"Unknown benchmark: {benchmark_name}")
        
        benchmark = benchmarks[benchmark_name]
        return await benchmark.run()
    
    def generate_reports(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Generate all reports from benchmark results."""
        print("Generating reports...")
        
        # Generate JSON, CSV, and Markdown reports
        reports = self.report_generator.generate_all_reports(results)
        
        # Generate performance charts
        charts = self.chart_generator.generate_all_charts(results)
        
        print(f"Reports generated:")
        for report_type, path in reports.items():
            print(f"  {report_type}: {path}")
        
        print(f"Charts generated:")
        for chart_path in charts:
            print(f"  chart: {chart_path}")
        
        return reports
    
    def generate_certificate(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Generate production readiness certificate."""
        print("Generating production readiness certificate...")
        
        certificate = self.certificate_generator.generate_certificate(results)
        
        # Save certificate files
        json_path = self.certificate_generator.save_certificate(certificate, results)
        md_path = self.certificate_generator.generate_certificate_markdown(certificate)
        
        print(f"Certificate Status: {certificate.status}")
        print(f"Overall Score: {certificate.overall_score:.1f}%")
        print(f"Certificate saved to: {json_path}")
        print(f"Certificate summary saved to: {md_path}")
        
        return {
            "status": certificate.status,
            "score": certificate.overall_score,
            "json_path": json_path,
            "markdown_path": md_path
        }
    
    async def run_and_report(self) -> Dict[str, Any]:
        """Run full suite and generate all reports."""
        # Run benchmarks
        results = await self.run_full_suite()
        
        # Generate reports
        reports = self.generate_reports(results)
        
        # Generate certificate
        certificate = self.generate_certificate(results)
        
        return {
            "results": results,
            "reports": reports,
            "certificate": certificate
        }
    
    def get_dataset_info(self) -> Dict[str, Any]:
        """Get information about available datasets."""
        total_cases = self.dataset_loader.get_total_test_case_count()
        datasets = self.dataset_loader.load_all_datasets()
        
        info = {
            "dataset_dir": str(self.dataset_dir),
            "total_test_cases": total_cases,
            "datasets": {}
        }
        
        for name, dataset in datasets.items():
            info["datasets"][name] = {
                "description": dataset.get("description", ""),
                "test_cases": len(dataset.get("test_cases", []))
            }
        
        return info
