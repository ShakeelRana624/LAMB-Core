"""Resource monitoring utilities for benchmarking."""

import time
import psutil
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class ResourceSnapshot:
    """Snapshot of system resource usage."""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    thread_count: int
    open_files: int


class ResourceMonitor:
    """Monitor system resources during benchmark execution."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.snapshots: list[ResourceSnapshot] = []
        self.start_time: Optional[float] = None
        self._monitoring = False
    
    def start(self) -> None:
        """Start resource monitoring."""
        self.start_time = time.time()
        self.snapshots = []
        self._monitoring = True
        self._take_snapshot()
    
    def stop(self) -> None:
        """Stop resource monitoring."""
        self._monitoring = False
        self._take_snapshot()
    
    def _take_snapshot(self) -> ResourceSnapshot:
        """Take a snapshot of current resource usage."""
        snapshot = ResourceSnapshot(
            timestamp=time.time(),
            cpu_percent=self.process.cpu_percent(),
            memory_percent=self.process.memory_percent(),
            memory_mb=self.process.memory_info().rss / 1024 / 1024,
            thread_count=self.process.num_threads(),
            open_files=len(self.process.open_files())
        )
        self.snapshots.append(snapshot)
        return snapshot
    
    def get_current_snapshot(self) -> ResourceSnapshot:
        """Get current resource snapshot without storing."""
        return ResourceSnapshot(
            timestamp=time.time(),
            cpu_percent=self.process.cpu_percent(),
            memory_percent=self.process.memory_percent(),
            memory_mb=self.process.memory_info().rss / 1024 / 1024,
            thread_count=self.process.num_threads(),
            open_files=len(self.process.open_files())
        )
    
    def get_average_usage(self) -> Dict[str, float]:
        """Calculate average resource usage over monitoring period."""
        if not self.snapshots:
            return {}
        
        avg_cpu = sum(s.cpu_percent for s in self.snapshots) / len(self.snapshots)
        avg_memory = sum(s.memory_percent for s in self.snapshots) / len(self.snapshots)
        avg_memory_mb = sum(s.memory_mb for s in self.snapshots) / len(self.snapshots)
        avg_threads = sum(s.thread_count for s in self.snapshots) / len(self.snapshots)
        avg_files = sum(s.open_files for s in self.snapshots) / len(self.snapshots)
        
        return {
            "avg_cpu_percent": avg_cpu,
            "avg_memory_percent": avg_memory,
            "avg_memory_mb": avg_memory_mb,
            "avg_threads": avg_threads,
            "avg_open_files": avg_files
        }
    
    def get_peak_usage(self) -> Dict[str, float]:
        """Calculate peak resource usage over monitoring period."""
        if not self.snapshots:
            return {}
        
        return {
            "peak_cpu_percent": max(s.cpu_percent for s in self.snapshots),
            "peak_memory_percent": max(s.memory_percent for s in self.snapshots),
            "peak_memory_mb": max(s.memory_mb for s in self.snapshots),
            "peak_threads": max(s.thread_count for s in self.snapshots),
            "peak_open_files": max(s.open_files for s in self.snapshots)
        }
    
    def get_duration(self) -> float:
        """Get total monitoring duration in seconds."""
        if not self.snapshots:
            return 0.0
        return self.snapshots[-1].timestamp - self.snapshots[0].timestamp
    
    def reset(self) -> None:
        """Reset monitor state."""
        self.snapshots = []
        self.start_time = None
        self._monitoring = False
