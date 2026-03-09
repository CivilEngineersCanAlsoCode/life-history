"""
Concurrent ingestion testing — stress tests and memory profiling.

Provides:
- Parallel document ingestion (10, 50, 100 concurrent documents)
- Memory footprint tracking
- Resource utilization monitoring
- Concurrent operation stability validation
"""

import threading
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import os


@dataclass
class MemorySnapshot:
    """Memory state at a point in time."""
    timestamp: str
    rss_mb: float  # Resident set size (actual physical memory)
    vms_mb: float  # Virtual memory size
    percent: float  # Percentage of system memory

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "rss_mb": round(self.rss_mb, 2),
            "vms_mb": round(self.vms_mb, 2),
            "percent": round(self.percent, 2),
        }


@dataclass
class ConcurrentTestResult:
    """Result from concurrent ingestion test."""
    concurrent_count: int
    total_documents: int
    successful: int
    failed: int
    duration_seconds: float
    memory_start_mb: float
    memory_peak_mb: float
    memory_end_mb: float
    memory_growth_mb: float
    throughput_docs_per_sec: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_documents == 0:
            return 0.0
        return round(self.successful / self.total_documents * 100, 2)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "concurrent_count": self.concurrent_count,
            "total_documents": self.total_documents,
            "successful": self.successful,
            "failed": self.failed,
            "success_rate": self.success_rate,
            "duration_seconds": round(self.duration_seconds, 2),
            "memory_start_mb": round(self.memory_start_mb, 2),
            "memory_peak_mb": round(self.memory_peak_mb, 2),
            "memory_end_mb": round(self.memory_end_mb, 2),
            "memory_growth_mb": round(self.memory_growth_mb, 2),
            "throughput_docs_per_sec": round(self.throughput_docs_per_sec, 2),
        }


class MemoryMonitor:
    """Monitor memory usage during operations."""

    def __init__(self):
        """Initialize memory monitor."""
        self.process = psutil.Process(os.getpid())
        self.snapshots: List[MemorySnapshot] = []
        self.peak_memory_mb = 0.0

    def take_snapshot(self) -> MemorySnapshot:
        """Take memory snapshot."""
        mem_info = self.process.memory_info()
        mem_percent = self.process.memory_percent()

        rss_mb = mem_info.rss / 1024 / 1024
        vms_mb = mem_info.vms / 1024 / 1024

        snapshot = MemorySnapshot(
            timestamp=datetime.now().isoformat(),
            rss_mb=rss_mb,
            vms_mb=vms_mb,
            percent=mem_percent,
        )

        self.snapshots.append(snapshot)

        if rss_mb > self.peak_memory_mb:
            self.peak_memory_mb = rss_mb

        return snapshot

    def get_start_memory(self) -> float:
        """Get initial memory usage."""
        if self.snapshots:
            return self.snapshots[0].rss_mb
        return 0.0

    def get_peak_memory(self) -> float:
        """Get peak memory usage."""
        return self.peak_memory_mb

    def get_end_memory(self) -> float:
        """Get final memory usage."""
        if self.snapshots:
            return self.snapshots[-1].rss_mb
        return 0.0


class ConcurrentIngestionTest:
    """Test concurrent document ingestion."""

    def __init__(self, ingestion_manager: Any):
        """Initialize test."""
        self.manager = ingestion_manager
        self.results: List[ConcurrentTestResult] = []
        self.monitor = MemoryMonitor()

    def ingest_document_worker(
        self,
        document: Dict[str, Any],
    ) -> bool:
        """Worker function for document ingestion."""
        try:
            result = self.manager.ingest_documents([document])
            if hasattr(result, 'success_count'):
                return result.success_count > 0
            return True
        except Exception:
            return False

    def run_concurrent_test(
        self,
        documents: List[Dict[str, Any]],
        concurrent_count: int = 10,
    ) -> ConcurrentTestResult:
        """
        Run concurrent ingestion test.

        Args:
            documents: Documents to ingest
            concurrent_count: Number of concurrent workers

        Returns:
            ConcurrentTestResult with metrics
        """
        # Take initial memory snapshot
        self.monitor.take_snapshot()
        start_memory = self.monitor.get_start_memory()

        # Start timing
        start_time = time.time()

        # Ingest documents concurrently
        successful = 0
        failed = 0

        try:
            with ThreadPoolExecutor(max_workers=concurrent_count) as executor:
                futures = []

                for doc in documents:
                    future = executor.submit(self.ingest_document_worker, doc)
                    futures.append(future)

                # Wait for all to complete and collect results
                for future in as_completed(futures):
                    try:
                        if future.result():
                            successful += 1
                        else:
                            failed += 1
                    except Exception:
                        failed += 1

                    # Take memory snapshots periodically
                    if (successful + failed) % max(1, len(documents) // 10) == 0:
                        self.monitor.take_snapshot()

        except Exception:
            failed += len(documents) - successful

        # Take final memory snapshot
        self.monitor.take_snapshot()

        # Calculate metrics
        duration = time.time() - start_time
        peak_memory = self.monitor.get_peak_memory()
        end_memory = self.monitor.get_end_memory()
        memory_growth = end_memory - start_memory
        throughput = successful / max(duration, 0.001)

        result = ConcurrentTestResult(
            concurrent_count=concurrent_count,
            total_documents=len(documents),
            successful=successful,
            failed=failed,
            duration_seconds=duration,
            memory_start_mb=start_memory,
            memory_peak_mb=peak_memory,
            memory_end_mb=end_memory,
            memory_growth_mb=memory_growth,
            throughput_docs_per_sec=throughput,
        )

        self.results.append(result)
        return result

    def run_all_tests(
        self,
        test_sizes: Optional[List[int]] = None,
    ) -> List[ConcurrentTestResult]:
        """
        Run all concurrent tests.

        Args:
            test_sizes: Document counts to test (default: [10, 50, 100])

        Returns:
            List of ConcurrentTestResult
        """
        if test_sizes is None:
            test_sizes = [10, 50, 100]

        results = []

        for size in test_sizes:
            # Generate test documents
            documents = [
                {
                    "id": f"concurrent_test_{size}_{i}",
                    "text": f"Document {i} for concurrent testing",
                    "metadata": {"test": "concurrent", "size": size},
                }
                for i in range(size)
            ]

            # Run test
            result = self.run_concurrent_test(documents, concurrent_count=10)
            results.append(result)

        return results

    def generate_report(self) -> str:
        """Generate test report."""
        lines = [
            "=" * 80,
            "CONCURRENT INGESTION STRESS TEST REPORT",
            "=" * 80,
            "",
            f"Timestamp: {datetime.now().isoformat()}",
            "",
            "RESULTS",
            "-" * 80,
            f"{'Docs':<8} {'Concurrent':<12} {'Duration':<12} {'Throughput':<15} {'Memory Growth':<15}",
            "-" * 80,
        ]

        for result in self.results:
            lines.append(
                f"{result.total_documents:<8} "
                f"{result.concurrent_count:<12} "
                f"{result.duration_seconds:<11.2f}s "
                f"{result.throughput_docs_per_sec:<14.2f} docs/s "
                f"{result.memory_growth_mb:<14.2f} MB"
            )

        lines.extend([
            "",
            "DETAILED METRICS",
            "-" * 80,
        ])

        for result in self.results:
            lines.extend([
                f"\nConcurrent Count: {result.concurrent_count}, Total Docs: {result.total_documents}",
                f"  Success Rate: {result.success_rate}%",
                f"  Duration: {result.duration_seconds:.2f} seconds",
                f"  Throughput: {result.throughput_docs_per_sec:.2f} docs/sec",
                f"  Memory Start: {result.memory_start_mb:.1f} MB",
                f"  Memory Peak: {result.memory_peak_mb:.1f} MB",
                f"  Memory End: {result.memory_end_mb:.1f} MB",
                f"  Memory Growth: {result.memory_growth_mb:.1f} MB",
            ])

        lines.extend([
            "",
            "=" * 80,
        ])

        return "\n".join(lines)
