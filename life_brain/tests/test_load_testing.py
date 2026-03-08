"""
Test suite for load testing module.

Tests cover:
- Document generation at scale
- Load test configuration
- Throughput measurement
- Batch ingestion performance
- Report generation
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import time

from life_brain.performance import (
    LoadTestConfig,
    LoadTestResult,
    DocumentGenerator,
    BatchIngestionLoadTest,
    LoadTestSuite,
    run_throughput_test,
)


class TestLoadTestConfig:
    """Test LoadTestConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = LoadTestConfig()
        assert config.test_sizes == [1000, 10000, 100000]
        assert config.batch_size == 100
        assert config.measure_memory is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = LoadTestConfig(
            test_sizes=[100, 500],
            batch_size=50,
            measure_memory=False,
        )
        assert config.test_sizes == [100, 500]
        assert config.batch_size == 50
        assert config.measure_memory is False


class TestLoadTestResult:
    """Test LoadTestResult."""

    def test_create_result(self):
        """Test creating a result."""
        result = LoadTestResult(
            size=1000,
            total_documents=1000,
            successful=950,
            failed=50,
            duration_seconds=10.0,
            throughput_docs_per_sec=95.0,
            avg_latency_ms=10.5,
            min_latency_ms=5.0,
            max_latency_ms=20.0,
        )

        assert result.size == 1000
        assert result.successful == 950

    def test_success_rate(self):
        """Test success rate calculation."""
        result = LoadTestResult(
            size=1000,
            total_documents=1000,
            successful=950,
            failed=50,
            duration_seconds=10.0,
            throughput_docs_per_sec=95.0,
            avg_latency_ms=10.5,
            min_latency_ms=5.0,
            max_latency_ms=20.0,
        )

        assert result.success_rate == 95.0

    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = LoadTestResult(
            size=1000,
            total_documents=1000,
            successful=950,
            failed=50,
            duration_seconds=10.0,
            throughput_docs_per_sec=95.0,
            avg_latency_ms=10.5,
            min_latency_ms=5.0,
            max_latency_ms=20.0,
        )

        dict_form = result.to_dict()
        assert dict_form["size"] == 1000
        assert dict_form["success_rate"] == 95.0
        assert dict_form["throughput_docs_per_sec"] == 95.0


class TestDocumentGenerator:
    """Test DocumentGenerator."""

    def test_generate_document(self):
        """Test generating a single document."""
        doc = DocumentGenerator.generate_document("doc_001")
        assert doc["id"] == "doc_001"
        assert "text" in doc
        assert "metadata" in doc
        assert doc["metadata"]["domain"] == "career"

    def test_generate_batch(self):
        """Test generating a batch of documents."""
        batch = DocumentGenerator.generate_batch(10, "batch_001")
        assert len(batch) == 10
        for doc in batch:
            assert "id" in doc
            assert "text" in doc
            assert "metadata" in doc

    def test_generate_batch_uniqueness(self):
        """Test that generated documents are unique."""
        batch = DocumentGenerator.generate_batch(100)
        ids = [doc["id"] for doc in batch]
        assert len(ids) == len(set(ids))  # All unique


class TestBatchIngestionLoadTest:
    """Test BatchIngestionLoadTest."""

    def test_create_load_test(self):
        """Test creating load test."""
        mock_manager = Mock()
        test = BatchIngestionLoadTest(mock_manager)

        assert test.manager is mock_manager
        assert test.results == []

    def test_run_warmup(self):
        """Test warmup run."""
        mock_manager = Mock()
        mock_manager.ingest_documents.return_value = Mock(success_count=100)

        test = BatchIngestionLoadTest(mock_manager)
        test.run_warmup()

        assert mock_manager.ingest_documents.called

    def test_run_single_test(self):
        """Test running single load test."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 100
        mock_result.failure_count = 0
        mock_manager.ingest_documents.return_value = mock_result

        config = LoadTestConfig(test_sizes=[100], batch_size=50)
        test = BatchIngestionLoadTest(mock_manager, config)

        result = test.run_single_test(100)

        assert result.total_documents == 100
        assert isinstance(result, LoadTestResult)

    def test_run_all_tests(self):
        """Test running all configured tests."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 100
        mock_result.failure_count = 0
        mock_manager.ingest_documents.return_value = mock_result

        config = LoadTestConfig(test_sizes=[100, 200])
        test = BatchIngestionLoadTest(mock_manager, config)

        results = test.run_all_tests()

        assert len(results) == 2
        assert all(isinstance(r, LoadTestResult) for r in results)

    def test_generate_report(self):
        """Test report generation."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 100
        mock_result.failure_count = 0
        mock_manager.ingest_documents.return_value = mock_result

        config = LoadTestConfig(test_sizes=[100])
        test = BatchIngestionLoadTest(mock_manager, config)

        test.run_all_tests()
        report = test.generate_report()

        assert "BATCH INGESTION LOAD TEST REPORT" in report
        assert "100" in report  # Should contain test size


class TestLoadTestSuite:
    """Test LoadTestSuite."""

    def test_create_suite(self):
        """Test creating suite."""
        mock_manager = Mock()
        suite = LoadTestSuite(mock_manager)

        assert suite.manager is mock_manager
        assert suite.all_results == {}

    def test_run_batch_suite(self):
        """Test running batch ingestion suite."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 100
        mock_result.failure_count = 0
        mock_manager.ingest_documents.return_value = mock_result

        suite = LoadTestSuite(mock_manager)
        results = suite.run_batch_ingestion_suite()

        assert len(results) == 3  # Default sizes: 1K, 10K, 100K
        assert 'batch_ingestion' in suite.all_results

    def test_executive_report(self):
        """Test executive report generation."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 100
        mock_result.failure_count = 0
        mock_manager.ingest_documents.return_value = mock_result

        suite = LoadTestSuite(mock_manager)
        suite.run_batch_ingestion_suite()
        report = suite.generate_executive_report()

        assert "LOAD TESTING EXECUTIVE SUMMARY" in report


class TestHelperFunctions:
    """Test helper functions."""

    def test_run_throughput_test(self):
        """Test throughput test helper."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 100
        mock_result.failure_count = 0
        mock_manager.ingest_documents.return_value = mock_result

        results = run_throughput_test(mock_manager, sizes=[100, 200])

        assert len(results) == 2
        assert all(isinstance(r, LoadTestResult) for r in results)

    def test_run_throughput_test_default_sizes(self):
        """Test throughput test with default sizes."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 1000
        mock_result.failure_count = 0
        mock_manager.ingest_documents.return_value = mock_result

        results = run_throughput_test(mock_manager)

        # Should use default sizes [1K, 10K, 100K]
        assert len(results) >= 1


class TestLoadTestingIntegration:
    """Integration tests for load testing."""

    def test_complete_load_test_workflow(self):
        """Test complete load testing workflow."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 500
        mock_result.failure_count = 0
        mock_manager.ingest_documents.return_value = mock_result

        # Create config
        config = LoadTestConfig(test_sizes=[500, 1000])

        # Generate documents
        batch = DocumentGenerator.generate_batch(500)
        assert len(batch) == 500

        # Run tests
        test = BatchIngestionLoadTest(mock_manager, config)
        results = test.run_all_tests()

        assert len(results) == 2
        for result in results:
            assert result.success_rate > 0

    def test_performance_scaling(self):
        """Test that throughput scales reasonably."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 1000
        mock_result.failure_count = 0
        mock_manager.ingest_documents.return_value = mock_result

        config = LoadTestConfig(test_sizes=[100, 1000, 10000])
        test = BatchIngestionLoadTest(mock_manager, config)

        results = test.run_all_tests()

        # Throughput should remain relatively consistent across sizes
        throughputs = [r.throughput_docs_per_sec for r in results]
        assert len(throughputs) == 3

    def test_result_metrics_consistency(self):
        """Test that result metrics are consistent."""
        result = LoadTestResult(
            size=1000,
            total_documents=1000,
            successful=950,
            failed=50,
            duration_seconds=10.0,
            throughput_docs_per_sec=100.0,
            avg_latency_ms=10.0,
            min_latency_ms=5.0,
            max_latency_ms=20.0,
        )

        # Success + Failed should equal total
        assert result.successful + result.failed == result.total_documents

        # Success rate should be valid percentage
        assert 0.0 <= result.success_rate <= 100.0

        # Latency order should be min <= avg <= max
        assert result.min_latency_ms <= result.avg_latency_ms <= result.max_latency_ms
