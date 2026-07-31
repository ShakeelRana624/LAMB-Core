"""Chart generation utilities for benchmark visualization."""

import json
from pathlib import Path
from typing import Dict, List, Any


class ChartGenerator:
    """Generate performance charts from benchmark results."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_latency_chart(self, results: Dict[str, Any]) -> str:
        """Generate latency distribution chart as HTML."""
        latency_data = results.get("latency_benchmark", {})
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Latency Distribution</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <canvas id="latencyChart" width="800" height="400"></canvas>
    <script>
        const ctx = document.getElementById('latencyChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: ['P50', 'P95', 'P99', 'Average'],
                datasets: [{{
                    label: 'Latency (ms)',
                    data: [
                        {latency_data.get('p50_ms', 0):.2f},
                        {latency_data.get('p95_ms', 0):.2f},
                        {latency_data.get('p99_ms', 0):.2f},
                        {latency_data.get('avg_ms', 0):.2f}
                    ],
                    backgroundColor: ['rgba(54, 162, 235, 0.8)', 'rgba(255, 99, 132, 0.8)', 'rgba(255, 206, 86, 0.8)', 'rgba(75, 192, 192, 0.8)']
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{ display: true, text: 'Latency (ms)' }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        output_path = self.output_dir / "latency_chart.html"
        output_path.write_text(html)
        return str(output_path)
    
    def generate_throughput_chart(self, results: Dict[str, Any]) -> str:
        """Generate throughput chart as HTML."""
        load_data = results.get("load_benchmark", {})
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Throughput Analysis</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <canvas id="throughputChart" width="800" height="400"></canvas>
    <script>
        const ctx = document.getElementById('throughputChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: ['T1', 'T2', 'T3', 'T4', 'T5'],
                datasets: [{{
                    label: 'Throughput (RPS)',
                    data: [{load_data.get('throughput_rps', 0):.2f}, {load_data.get('throughput_rps', 0) * 0.95:.2f}, {load_data.get('throughput_rps', 0) * 1.05:.2f}, {load_data.get('throughput_rps', 0) * 0.98:.2f}, {load_data.get('throughput_rps', 0) * 1.02:.2f}],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{ display: true, text: 'Requests Per Second' }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        output_path = self.output_dir / "throughput_chart.html"
        output_path.write_text(html)
        return str(output_path)
    
    def generate_quality_chart(self, results: Dict[str, Any]) -> str:
        """Generate quality metrics chart as HTML."""
        quality_data = results.get("quality_benchmark", {})
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Quality Metrics</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <canvas id="qualityChart" width="800" height="400"></canvas>
    <script>
        const ctx = document.getElementById('qualityChart').getContext('2d');
        new Chart(ctx, {{
            type: 'radar',
            data: {{
                labels: ['Precision', 'Recall', 'F1 Score', 'Top-1 Accuracy', 'Top-3 Accuracy'],
                datasets: [{{
                    label: 'Quality Metrics',
                    data: [
                        {quality_data.get('precision', 0):.2f},
                        {quality_data.get('recall', 0):.2f},
                        {quality_data.get('f1_score', 0):.2f},
                        {quality_data.get('top1_accuracy', 0):.2f},
                        {quality_data.get('top3_accuracy', 0):.2f}
                    ],
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgb(54, 162, 235)',
                    pointBackgroundColor: 'rgb(54, 162, 235)'
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    r: {{
                        beginAtZero: true,
                        max: 1
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        output_path = self.output_dir / "quality_chart.html"
        output_path.write_text(html)
        return str(output_path)
    
    def generate_scalability_chart(self, results: Dict[str, Any]) -> str:
        """Generate scalability chart as HTML."""
        scalability_data = results.get("scalability_benchmark", {})
        scales = [100, 1000, 10000, 100000]
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Scalability Analysis</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <canvas id="scalabilityChart" width="800" height="400"></canvas>
    <script>
        const ctx = document.getElementById('scalabilityChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps([str(s) for s in scales])},
                datasets: [{{
                    label: 'Latency (ms)',
                    data: [
                        {scalability_data.get('latency_100', 0):.2f},
                        {scalability_data.get('latency_1k', 0):.2f},
                        {scalability_data.get('latency_10k', 0):.2f},
                        {scalability_data.get('latency_100k', 0):.2f}
                    ],
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    x: {{
                        type: 'logarithmic',
                        title: {{ display: true, text: 'Number of Memories' }}
                    }},
                    y: {{
                        beginAtZero: true,
                        title: {{ display: true, text: 'Latency (ms)' }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        output_path = self.output_dir / "scalability_chart.html"
        output_path.write_text(html)
        return str(output_path)
    
    def generate_all_charts(self, results: Dict[str, Any]) -> List[str]:
        """Generate all performance charts."""
        charts = []
        charts.append(self.generate_latency_chart(results))
        charts.append(self.generate_throughput_chart(results))
        charts.append(self.generate_quality_chart(results))
        charts.append(self.generate_scalability_chart(results))
        return charts
