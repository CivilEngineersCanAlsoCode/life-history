"""
Test suite for semantic search latency testing.

Tests cover:
- Query types and library
- Latency measurements
- SLA boundaries and compliance
- Test execution and reporting
"""

import pytest
from unittest.mock import Mock, patch
import time

from life_brain.testing.latency_testing import (
    QueryType,
    QueryLibrary,
    LatencyBoundary,
    LatencyMeasurement,
    LatencyTestResult,
    SemanticSearchLatencyTest,
)


class TestQueryType:
    """Test QueryType enum."""

    def test_query_types_exist(self):
        """Test that all query types are defined."""
        assert QueryType.SIMPLE is not None
        assert QueryType.SINGLE_QUERY is not None
        assert QueryType.MULTI_ANGLE is not None
        assert QueryType.COMPLEX_SYNTHESIS is not None

    def test_query_type_values(self):
        """Test query type values."""
        assert QueryType.SIMPLE.value == "simple"
        assert QueryType.SINGLE_QUERY.value == "single_query"


class TestQueryLibrary:
    """Test QueryLibrary."""

    def test_simple_queries(self):
        """Test simple query library."""
        queries = QueryLibrary.get_queries(QueryType.SIMPLE, count=5)
        assert len(queries) == 5
        assert all(isinstance(q, str) for q in queries)

    def test_multi_angle_queries(self):
        """Test multi-angle query library."""
        queries = QueryLibrary.get_queries(QueryType.MULTI_ANGLE, count=5)
        assert len(queries) == 5

    def test_complex_queries(self):
        """Test complex query library."""
        queries = QueryLibrary.get_queries(QueryType.COMPLEX_SYNTHESIS, count=3)
        assert len(queries) == 3

    def test_queries_repeatability(self):
        """Test that queries repeat when count exceeds available."""
        queries = QueryLibrary.get_queries(QueryType.SIMPLE, count=20)
        assert len(queries) == 20


class TestLatencyBoundary:
    """Test LatencyBoundary."""

    def test_create_boundary(self):
        """Test creating SLA boundary."""
        boundary = LatencyBoundary(
            name="Test",
            p50_ms=20,
            p95_ms=50,
            p99_ms=100,
            p100_ms=150,
        )

        assert boundary.name == "Test"
        assert boundary.p100_ms == 150

    def test_compliance_check(self):
        """Test SLA compliance check."""
        boundary = LatencyBoundary(
            name="Test",
            p50_ms=20,
            p95_ms=50,
            p99_ms=100,
            p100_ms=150,
        )

        assert boundary.check_compliance(100) is True
        assert boundary.check_compliance(150) is True
        assert boundary.check_compliance(200) is False


class TestLatencyMeasurement:
    """Test LatencyMeasurement."""

    def test_create_measurement(self):
        """Test creating measurement."""
        measurement = LatencyMeasurement(
            query_type=QueryType.SINGLE_QUERY,
            latency_ms=50.5,
            query="Test query",
            result_count=5,
        )

        assert measurement.latency_ms == 50.5
        assert measurement.result_count == 5

    def test_measurement_timestamp(self):
        """Test that measurement has timestamp."""
        measurement = LatencyMeasurement(
            query_type=QueryType.SINGLE_QUERY,
            latency_ms=50.0,
            query="Test",
        )

        assert measurement.timestamp is not None


class TestLatencyTestResult:
    """Test LatencyTestResult."""

    def test_create_result(self):
        """Test creating result."""
        result = LatencyTestResult(
            query_type=QueryType.SINGLE_QUERY,
            total_queries=20,
            min_latency_ms=10.0,
            max_latency_ms=150.0,
            avg_latency_ms=50.0,
            p50_latency_ms=40.0,
            p95_latency_ms=80.0,
            p99_latency_ms=120.0,
        )

        assert result.query_type == QueryType.SINGLE_QUERY
        assert result.total_queries == 20

    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = LatencyTestResult(
            query_type=QueryType.SINGLE_QUERY,
            total_queries=20,
            min_latency_ms=10.0,
            max_latency_ms=150.0,
            avg_latency_ms=50.0,
            p50_latency_ms=40.0,
            p95_latency_ms=80.0,
            p99_latency_ms=120.0,
        )

        dict_form = result.to_dict()
        assert dict_form["query_type"] == "single_query"
        assert dict_form["total_queries"] == 20
        assert dict_form["p99_latency_ms"] == 120.0


class TestSemanticSearchLatencyTest:
    """Test SemanticSearchLatencyTest."""

    def test_create_test(self):
        """Test creating latency test."""
        mock_retrieval = Mock()
        test = SemanticSearchLatencyTest(mock_retrieval)

        assert test.retrieval is mock_retrieval
        assert test.measurements == []

    def test_measure_single_query(self):
        """Test measuring single query latency."""
        mock_retrieval = Mock()
        mock_retrieval.search_by_query.return_value = [{"id": "doc1"}]

        test = SemanticSearchLatencyTest(mock_retrieval)
        measurement = test.measure_single_query("Test query")

        assert measurement.query_type == QueryType.SINGLE_QUERY
        assert measurement.latency_ms >= 0
        assert measurement.query == "Test query"

    def test_measure_multi_angle(self):
        """Test measuring multi-angle search latency."""
        mock_retrieval = Mock()
        mock_retrieval.search_all_angles.return_value = {"behavioral": [], "metric": []}

        test = SemanticSearchLatencyTest(mock_retrieval)
        measurement = test.measure_multi_angle("Test query")

        assert measurement.query_type == QueryType.MULTI_ANGLE
        assert measurement.latency_ms >= 0

    def test_run_test_single_query(self):
        """Test running single query latency test."""
        mock_retrieval = Mock()
        mock_retrieval.search_by_query.return_value = [{"id": "doc1"}]

        test = SemanticSearchLatencyTest(mock_retrieval)
        result = test.run_test(QueryType.SINGLE_QUERY, num_queries=10)

        assert result.query_type == QueryType.SINGLE_QUERY
        assert result.total_queries == 10
        assert result.avg_latency_ms >= 0

    def test_run_test_multi_angle(self):
        """Test running multi-angle latency test."""
        mock_retrieval = Mock()
        mock_retrieval.search_all_angles.return_value = {"behavioral": []}

        test = SemanticSearchLatencyTest(mock_retrieval)
        result = test.run_test(QueryType.MULTI_ANGLE, num_queries=10)

        assert result.query_type == QueryType.MULTI_ANGLE
        assert len(result.measurements) == 10

    def test_latency_statistics(self):
        """Test latency statistics calculation."""
        mock_retrieval = Mock()
        mock_retrieval.search_by_query.return_value = []

        test = SemanticSearchLatencyTest(mock_retrieval)
        result = test.run_test(QueryType.SINGLE_QUERY, num_queries=20)

        # Check that statistics are in order
        assert result.min_latency_ms <= result.p50_latency_ms
        assert result.p50_latency_ms <= result.p95_latency_ms
        assert result.p95_latency_ms <= result.p99_latency_ms
        assert result.p99_latency_ms <= result.max_latency_ms

    def test_sla_compliance_check(self):
        """Test SLA compliance."""
        mock_retrieval = Mock()
        mock_retrieval.search_by_query.return_value = []

        test = SemanticSearchLatencyTest(mock_retrieval)
        result = test.run_test(QueryType.SINGLE_QUERY, num_queries=20)

        # Result should have SLA compliance status
        assert isinstance(result.sla_compliant, bool)

    def test_run_all_tests(self):
        """Test running all latency tests."""
        mock_retrieval = Mock()
        mock_retrieval.search_by_query.return_value = []
        mock_retrieval.search_all_angles.return_value = {}

        test = SemanticSearchLatencyTest(mock_retrieval)
        results = test.run_all_tests()

        assert len(results) == 2  # single_query and multi_angle
        assert QueryType.SINGLE_QUERY in results
        assert QueryType.MULTI_ANGLE in results

    def test_generate_report(self):
        """Test report generation."""
        mock_retrieval = Mock()
        mock_retrieval.search_by_query.return_value = []

        test = SemanticSearchLatencyTest(mock_retrieval)
        test.run_test(QueryType.SINGLE_QUERY, num_queries=10)

        report = test.generate_report()

        assert "SEMANTIC SEARCH LATENCY TEST REPORT" in report
        assert "single_query" in report.lower()


class TestLatencyTestingIntegration:
    """Integration tests for latency testing."""

    def test_full_latency_test_workflow(self):
        """Test complete latency test workflow."""
        mock_retrieval = Mock()
        mock_retrieval.search_by_query.return_value = [{"id": "doc1"}]
        mock_retrieval.search_all_angles.return_value = {"behavioral": []}

        test = SemanticSearchLatencyTest(mock_retrieval)

        # Run tests
        single_result = test.run_test(QueryType.SINGLE_QUERY, num_queries=10)
        multi_result = test.run_test(QueryType.MULTI_ANGLE, num_queries=10)

        # Check results
        assert single_result.total_queries == 10
        assert multi_result.total_queries == 10
        assert single_result.avg_latency_ms >= 0
        assert multi_result.avg_latency_ms >= 0

    def test_latency_percentile_ordering(self):
        """Test that latency percentiles are properly ordered."""
        mock_retrieval = Mock()
        mock_retrieval.search_by_query.return_value = []

        test = SemanticSearchLatencyTest(mock_retrieval)
        result = test.run_test(QueryType.SINGLE_QUERY, num_queries=100)

        # Percentiles should be in strict increasing order
        assert result.p50_latency_ms <= result.p95_latency_ms
        assert result.p95_latency_ms <= result.p99_latency_ms
        assert result.p99_latency_ms <= result.max_latency_ms

    def test_sla_boundaries_correctness(self):
        """Test that SLA boundaries are reasonable."""
        # Single query should be fastest
        single_sla = SemanticSearchLatencyTest.SLA_SINGLE_QUERY
        multi_sla = SemanticSearchLatencyTest.SLA_MULTI_ANGLE

        # Multi-angle should have higher latency budget
        assert multi_sla.p99_ms >= single_sla.p99_ms
        assert multi_sla.p100_ms >= single_sla.p100_ms
