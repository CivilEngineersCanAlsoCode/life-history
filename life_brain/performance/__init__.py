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

__all__ = [
    "BatchIngestionLoadTest",
    "DocumentGenerator",
    "LoadTestConfig",
    "LoadTestResult",
    "LoadTestSuite",
    "run_throughput_test",
]
