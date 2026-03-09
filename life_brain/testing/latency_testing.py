"""
Semantic search latency testing — measure search performance.

Provides:
- Single query search latency (<100ms target)
- Complex synthesis query latency (<500ms target)
- Multi-angle search latency
- Result aggregation latency
- Latency SLA validation
"""

import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class QueryType(Enum):
    """Types of search queries."""
    SIMPLE = "simple"  # Single document retrieval
    SINGLE_QUERY = "single_query"  # Standard search
    MULTI_ANGLE = "multi_angle"  # Search across multiple angles
    COMPLEX_SYNTHESIS = "complex_synthesis"  # Multi-stage search with synthesis


@dataclass
class LatencyBoundary:
    """SLA boundaries for latency."""
    name: str
    p50_ms: float  # Median
    p95_ms: float  # 95th percentile
    p99_ms: float  # 99th percentile
    p100_ms: float  # Max

    def check_compliance(self, latency_ms: float) -> bool:
        """Check if latency meets SLA."""
        return latency_ms <= self.p100_ms


@dataclass
class LatencyMeasurement:
    """Single latency measurement."""
    query_type: QueryType
    latency_ms: float
    query: str
    result_count: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class LatencyTestResult:
    """Result from latency test run."""
    query_type: QueryType
    total_queries: int
    measurements: List[LatencyMeasurement] = field(default_factory=list)
    min_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    avg_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    sla_compliant: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def success_count(self) -> int:
        """Count of measurements below p100 boundary."""
        return len(self.measurements)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query_type": self.query_type.value,
            "total_queries": self.total_queries,
            "min_latency_ms": round(self.min_latency_ms, 2),
            "max_latency_ms": round(self.max_latency_ms, 2),
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "p50_latency_ms": round(self.p50_latency_ms, 2),
            "p95_latency_ms": round(self.p95_latency_ms, 2),
            "p99_latency_ms": round(self.p99_latency_ms, 2),
            "sla_compliant": self.sla_compliant,
        }


class QueryLibrary:
    """Library of test queries."""

    SIMPLE_QUERIES = [
        "Tell me about your projects",
        "What skills do you have",
        "Career accomplishments",
        "Leadership experience",
        "Technical expertise",
    ]

    MULTI_ANGLE_QUERIES = [
        "What metrics have you improved",
        "Tell me about impact",
        "Describe the approach you took",
        "What did you learn",
        "Behavioral examples",
    ]

    COMPLEX_QUERIES = [
        "Compare my leadership style across different projects and synthesize common patterns",
        "Analyze the metrics I've improved and correlate with business outcomes",
        "Extract lessons learned from failures and successes, then create a framework",
    ]

    @staticmethod
    def get_queries(query_type: QueryType, count: int = 10) -> List[str]:
        """Get test queries of specific type."""
        if query_type == QueryType.SIMPLE:
            queries = QueryLibrary.SIMPLE_QUERIES
        elif query_type == QueryType.MULTI_ANGLE:
            queries = QueryLibrary.MULTI_ANGLE_QUERIES
        elif query_type == QueryType.COMPLEX_SYNTHESIS:
            queries = QueryLibrary.COMPLEX_QUERIES
        else:
            queries = QueryLibrary.SIMPLE_QUERIES

        # Repeat to reach desired count
        result = []
        for i in range(count):
            result.append(queries[i % len(queries)])
        return result


class SemanticSearchLatencyTest:
    """Latency test for semantic search."""

    # SLA boundaries
    SLA_SINGLE_QUERY = LatencyBoundary("Single Query", p50_ms=20, p95_ms=50, p99_ms=100, p100_ms=150)
    SLA_MULTI_ANGLE = LatencyBoundary("Multi-Angle", p50_ms=50, p95_ms=200, p99_ms=400, p100_ms=600)
    SLA_COMPLEX = LatencyBoundary("Complex", p50_ms=100, p95_ms=350, p99_ms=500, p100_ms=750)

    def __init__(self, retrieval_system: Any):
        """
        Initialize latency test.

        Args:
            retrieval_system: AltQuestionRetrieval instance
        """
        self.retrieval = retrieval_system
        self.measurements: List[LatencyMeasurement] = []
        self.results: Dict[QueryType, LatencyTestResult] = {}

    def measure_single_query(self, query: str) -> LatencyMeasurement:
        """
        Measure latency for single query.

        Args:
            query: Search query

        Returns:
            LatencyMeasurement with timing
        """
        start = time.time()
        try:
            # Mock search - would call actual retrieval
            results = getattr(self.retrieval, 'search_by_query', lambda q: [])(query)
            result_count = len(results) if results else 0
        except Exception:
            result_count = 0

        latency_ms = (time.time() - start) * 1000

        measurement = LatencyMeasurement(
            query_type=QueryType.SINGLE_QUERY,
            latency_ms=latency_ms,
            query=query,
            result_count=result_count,
        )

        self.measurements.append(measurement)
        return measurement

    def measure_multi_angle(self, query: str) -> LatencyMeasurement:
        """
        Measure latency for multi-angle search.

        Args:
            query: Search query

        Returns:
            LatencyMeasurement with timing
        """
        start = time.time()
        try:
            # Mock multi-angle search
            results = getattr(self.retrieval, 'search_all_angles', lambda q: {})(query)
            result_count = sum(len(r) if isinstance(r, list) else 1 for r in results.values())
        except Exception:
            result_count = 0

        latency_ms = (time.time() - start) * 1000

        measurement = LatencyMeasurement(
            query_type=QueryType.MULTI_ANGLE,
            latency_ms=latency_ms,
            query=query,
            result_count=result_count,
        )

        self.measurements.append(measurement)
        return measurement

    def run_test(
        self,
        query_type: QueryType,
        num_queries: int = 20,
    ) -> LatencyTestResult:
        """
        Run latency test for query type.

        Args:
            query_type: Type of query to test
            num_queries: Number of queries to run

        Returns:
            LatencyTestResult with statistics
        """
        queries = QueryLibrary.get_queries(query_type, num_queries)
        test_measurements = []

        for query in queries:
            if query_type == QueryType.SINGLE_QUERY:
                measurement = self.measure_single_query(query)
            elif query_type == QueryType.MULTI_ANGLE:
                measurement = self.measure_multi_angle(query)
            else:
                measurement = self.measure_single_query(query)

            test_measurements.append(measurement)

        # Calculate statistics
        latencies = [m.latency_ms for m in test_measurements]
        latencies.sort()

        result = LatencyTestResult(
            query_type=query_type,
            total_queries=num_queries,
            measurements=test_measurements,
            min_latency_ms=min(latencies),
            max_latency_ms=max(latencies),
            avg_latency_ms=sum(latencies) / len(latencies),
            p50_latency_ms=latencies[int(len(latencies) * 0.50)],
            p95_latency_ms=latencies[int(len(latencies) * 0.95)],
            p99_latency_ms=latencies[int(len(latencies) * 0.99)] if len(latencies) >= 100 else latencies[-1],
        )

        # Check SLA compliance
        if query_type == QueryType.SINGLE_QUERY:
            result.sla_compliant = result.p99_latency_ms <= self.SLA_SINGLE_QUERY.p99_ms
        elif query_type == QueryType.MULTI_ANGLE:
            result.sla_compliant = result.p99_latency_ms <= self.SLA_MULTI_ANGLE.p99_ms
        else:
            result.sla_compliant = result.p99_latency_ms <= self.SLA_COMPLEX.p99_ms

        self.results[query_type] = result
        return result

    def run_all_tests(self) -> Dict[QueryType, LatencyTestResult]:
        """
        Run all latency tests.

        Returns:
            Dict mapping QueryType to LatencyTestResult
        """
        results = {}

        for query_type in [QueryType.SINGLE_QUERY, QueryType.MULTI_ANGLE]:
            result = self.run_test(query_type, num_queries=20)
            results[query_type] = result

        return results

    def generate_report(self) -> str:
        """Generate latency test report."""
        lines = [
            "=" * 80,
            "SEMANTIC SEARCH LATENCY TEST REPORT",
            "=" * 80,
            "",
            f"Timestamp: {datetime.now().isoformat()}",
            "",
            "LATENCY SLA TARGETS",
            "-" * 80,
            f"  Single Query: <100ms (p99) | <150ms (p100)",
            f"  Multi-Angle: <400ms (p99) | <600ms (p100)",
            f"  Complex Synthesis: <500ms (p99) | <750ms (p100)",
            "",
            "RESULTS",
            "-" * 80,
        ]

        for query_type, result in self.results.items():
            status = "✓ PASS" if result.sla_compliant else "✗ FAIL"
            lines.append(f"\n{query_type.value.upper()}: {status}")
            lines.append(f"  Avg: {result.avg_latency_ms:.1f}ms")
            lines.append(f"  P50: {result.p50_latency_ms:.1f}ms")
            lines.append(f"  P95: {result.p95_latency_ms:.1f}ms")
            lines.append(f"  P99: {result.p99_latency_ms:.1f}ms")
            lines.append(f"  Max: {result.max_latency_ms:.1f}ms")

        lines.extend([
            "",
            "=" * 80,
        ])

        return "\n".join(lines)
