"""
Performance testing module — load tests, latency tests, and benchmarking.

Provides:
- Batch ingestion load testing (1K, 10K, 100K documents)
- Semantic search latency validation
- Concurrent operation stress tests
- Memory profiling
"""

from life_brain.performance.load_testing import (
    BatchIngestionLoadTest,
    DocumentGenerator,
    LoadTestConfig,
    LoadTestResult,
    LoadTestSuite,
    run_throughput_test,
)
from life_brain.performance.latency_testing import (
    QueryType,
    QueryLibrary,
    LatencyBoundary,
    LatencyMeasurement,
    LatencyTestResult,
    SemanticSearchLatencyTest,
)
from life_brain.performance.concurrent_testing import (
    MemorySnapshot,
    MemoryMonitor,
    ConcurrentIngestionTest,
    ConcurrentTestResult,
)

__all__ = [
    # Load testing
    "BatchIngestionLoadTest",
    "DocumentGenerator",
    "LoadTestConfig",
    "LoadTestResult",
    "LoadTestSuite",
    "run_throughput_test",
    # Latency testing
    "QueryType",
    "QueryLibrary",
    "LatencyBoundary",
    "LatencyMeasurement",
    "LatencyTestResult",
    "SemanticSearchLatencyTest",
    # Concurrent testing
    "MemorySnapshot",
    "MemoryMonitor",
    "ConcurrentIngestionTest",
    "ConcurrentTestResult",
]
