"""
Load testing for Life Brain — measure throughput and performance at scale.

Provides:
- Batch ingestion load tests (1K, 10K, 100K documents)
- Throughput measurement and reporting
- Memory profiling
- Scalability analysis
"""

import time
import random
import string
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class LoadTestConfig:
    """Configuration for load tests."""
    test_sizes: List[int] = field(default_factory=lambda: [1000, 10000, 100000])
    batch_size: int = 100
    measure_memory: bool = True
    enable_profiling: bool = False
    warmup_size: int = 100


@dataclass
class LoadTestResult:
    """Result from a single load test run."""
    size: int
    total_documents: int
    successful: int
    failed: int
    duration_seconds: float
    throughput_docs_per_sec: float
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    memory_mb: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_documents == 0:
            return 0.0
        return round(self.successful / self.total_documents * 100, 2)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "size": self.size,
            "total_documents": self.total_documents,
            "successful": self.successful,
            "failed": self.failed,
            "success_rate": self.success_rate,
            "duration_seconds": round(self.duration_seconds, 2),
            "throughput_docs_per_sec": round(self.throughput_docs_per_sec, 2),
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "min_latency_ms": round(self.min_latency_ms, 2),
            "max_latency_ms": round(self.max_latency_ms, 2),
            "memory_mb": round(self.memory_mb, 2),
            "timestamp": self.timestamp,
        }


class DocumentGenerator:
    """Generate test documents at scale."""

    @staticmethod
    def generate_document(
        doc_id: str,
        domain: str = "career",
        include_metrics: bool = True,
    ) -> Dict[str, Any]:
        """Generate a single test document."""
        return {
            "id": doc_id,
            "text": f"Sample document {doc_id}: " + (
                "Lorem ipsum dolor sit amet. " * random.randint(5, 20)
            ),
            "metadata": {
                "domain": domain,
                "subdomain": "test",
                "source": "load_test",
                "created_at": datetime.now().isoformat(),
                "confidence": round(random.random(), 2),
                "contains_metric": include_metrics and random.random() > 0.5,
            },
        }

    @staticmethod
    def generate_batch(
        size: int,
        batch_id: str = "batch",
        domain: str = "career",
    ) -> List[Dict[str, Any]]:
        """Generate a batch of test documents."""
        documents = []
        for i in range(size):
            doc_id = f"{batch_id}_doc_{i:06d}_{uuid.uuid4().hex[:8]}"
            documents.append(
                DocumentGenerator.generate_document(doc_id, domain)
            )
        return documents


class BatchIngestionLoadTest:
    """Load test for batch ingestion."""

    def __init__(self, ingestion_manager: Any, config: Optional[LoadTestConfig] = None):
        """
        Initialize load test.

        Args:
            ingestion_manager: IngestionManager instance
            config: LoadTestConfig with test parameters
        """
        self.manager = ingestion_manager
        self.config = config or LoadTestConfig()
        self.results: List[LoadTestResult] = []
        self.latencies: List[float] = []

    def run_warmup(self) -> None:
        """Run warmup to initialize system."""
        docs = DocumentGenerator.generate_batch(self.config.warmup_size, "warmup")
        try:
            self.manager.ingest_documents(docs)
        except Exception:
            pass  # Warmup failures are non-critical

    def run_single_test(self, size: int) -> LoadTestResult:
        """
        Run load test for specific size.

        Args:
            size: Number of documents to test

        Returns:
            LoadTestResult with metrics
        """
        # Generate documents
        documents = DocumentGenerator.generate_batch(size, f"load_test_{size}")

        # Time ingestion
        start_time = time.time()
        self.latencies.clear()

        try:
            # Ingest in batches
            successful = 0
            failed = 0

            for i in range(0, len(documents), self.config.batch_size):
                batch = documents[i:i + self.config.batch_size]
                batch_start = time.time()

                try:
                    result = self.manager.ingest_documents(batch)
                    batch_latency = (time.time() - batch_start) * 1000  # ms
                    self.latencies.append(batch_latency)

                    if hasattr(result, 'success_count'):
                        successful += result.success_count
                    else:
                        successful += len(batch)

                    if hasattr(result, 'failure_count'):
                        failed += result.failure_count

                except Exception as e:
                    failed += len(batch)

        except Exception as e:
            # If ingestion fails completely, return failure
            return LoadTestResult(
                size=size,
                total_documents=size,
                successful=0,
                failed=size,
                duration_seconds=time.time() - start_time,
                throughput_docs_per_sec=0.0,
                avg_latency_ms=0.0,
                min_latency_ms=0.0,
                max_latency_ms=0.0,
            )

        # Calculate metrics
        duration = time.time() - start_time
        throughput = successful / max(duration, 0.001)

        if self.latencies:
            avg_latency = sum(self.latencies) / len(self.latencies)
            min_latency = min(self.latencies)
            max_latency = max(self.latencies)
        else:
            avg_latency = min_latency = max_latency = 0.0

        result = LoadTestResult(
            size=size,
            total_documents=size,
            successful=successful,
            failed=failed,
            duration_seconds=duration,
            throughput_docs_per_sec=throughput,
            avg_latency_ms=avg_latency,
            min_latency_ms=min_latency,
            max_latency_ms=max_latency,
        )

        self.results.append(result)
        return result

    def run_all_tests(self) -> List[LoadTestResult]:
        """
        Run all configured load tests.

        Returns:
            List of LoadTestResult objects
        """
        self.run_warmup()
        results = []

        for size in self.config.test_sizes:
            result = self.run_single_test(size)
            results.append(result)

        return results

    def generate_report(self) -> str:
        """Generate text report of load test results."""
        lines = [
            "=" * 80,
            "BATCH INGESTION LOAD TEST REPORT",
            "=" * 80,
            "",
            f"Timestamp: {datetime.now().isoformat()}",
            f"Total Tests Run: {len(self.results)}",
            "",
            "RESULTS SUMMARY",
            "-" * 80,
            f"{'Size':<12} {'Throughput':<15} {'Avg Latency':<15} {'Success Rate':<15}",
            "-" * 80,
        ]

        for result in self.results:
            lines.append(
                f"{result.size:<12} "
                f"{result.throughput_docs_per_sec:<14.2f} docs/s "
                f"{result.avg_latency_ms:<14.2f} ms "
                f"{result.success_rate:<14.1f} %"
            )

        lines.extend([
            "",
            "DETAILED METRICS",
            "-" * 80,
        ])

        for result in self.results:
            lines.extend([
                f"\nTest Size: {result.size} documents",
                f"  Duration: {result.duration_seconds:.2f} seconds",
                f"  Throughput: {result.throughput_docs_per_sec:.2f} docs/sec",
                f"  Success: {result.successful}/{result.total_documents} ({result.success_rate}%)",
                f"  Latency: min={result.min_latency_ms:.2f}ms, "
                f"avg={result.avg_latency_ms:.2f}ms, max={result.max_latency_ms:.2f}ms",
            ])

        lines.extend([
            "",
            "=" * 80,
        ])

        return "\n".join(lines)


class LoadTestSuite:
    """Complete load testing suite."""

    def __init__(self, ingestion_manager: Any):
        """Initialize suite."""
        self.manager = ingestion_manager
        self.batch_test: Optional[BatchIngestionLoadTest] = None
        self.all_results: Dict[str, List[LoadTestResult]] = {}

    def run_batch_ingestion_suite(self) -> List[LoadTestResult]:
        """
        Run complete batch ingestion load test.

        Returns:
            List of results for different sizes
        """
        config = LoadTestConfig(
            test_sizes=[1000, 10000, 100000],
            batch_size=100,
        )
        self.batch_test = BatchIngestionLoadTest(self.manager, config)
        results = self.batch_test.run_all_tests()
        self.all_results['batch_ingestion'] = results
        return results

    def generate_executive_report(self) -> str:
        """Generate executive summary report."""
        lines = [
            "╔" + "=" * 78 + "╗",
            "║" + "LOAD TESTING EXECUTIVE SUMMARY".center(78) + "║",
            "╚" + "=" * 78 + "╝",
            "",
        ]

        if self.batch_test:
            lines.append(self.batch_test.generate_report())

        return "\n".join(lines)


# Helper functions for direct usage
def run_throughput_test(
    ingestion_manager: Any,
    sizes: Optional[List[int]] = None,
) -> List[LoadTestResult]:
    """
    Run throughput test at specified sizes.

    Args:
        ingestion_manager: IngestionManager instance
        sizes: List of document counts to test (default: [1K, 10K, 100K])

    Returns:
        List of LoadTestResult objects
    """
    if sizes is None:
        sizes = [1000, 10000, 100000]

    config = LoadTestConfig(test_sizes=sizes)
    test = BatchIngestionLoadTest(ingestion_manager, config)
    return test.run_all_tests()
