"""
Test suite for concurrent ingestion testing.

Tests cover:
- Concurrent document processing
- Memory monitoring
- Thread safety
- Scalability validation
"""

import pytest
from unittest.mock import Mock, patch
import time

from life_brain.testing.concurrent_testing import (
    MemorySnapshot,
    MemoryMonitor,
    ConcurrentIngestionTest,
    ConcurrentTestResult,
)


class TestMemorySnapshot:
    """Test MemorySnapshot."""

    def test_create_snapshot(self):
        """Test creating memory snapshot."""
        snapshot = MemorySnapshot(
            timestamp="2024-03-09T10:00:00",
            rss_mb=100.5,
            vms_mb=200.0,
            percent=2.5,
        )

        assert snapshot.rss_mb == 100.5
        assert snapshot.vms_mb == 200.0

    def test_snapshot_to_dict(self):
        """Test converting snapshot to dict."""
        snapshot = MemorySnapshot(
            timestamp="2024-03-09T10:00:00",
            rss_mb=100.5,
            vms_mb=200.0,
            percent=2.5,
        )

        dict_form = snapshot.to_dict()
        assert dict_form["rss_mb"] == 100.5
        assert dict_form["vms_mb"] == 200.0


class TestMemoryMonitor:
    """Test MemoryMonitor."""

    def test_create_monitor(self):
        """Test creating memory monitor."""
        monitor = MemoryMonitor()
        assert monitor.snapshots == []
        assert monitor.peak_memory_mb == 0.0

    def test_take_snapshot(self):
        """Test taking memory snapshot."""
        monitor = MemoryMonitor()
        snapshot = monitor.take_snapshot()

        assert snapshot is not None
        assert snapshot.rss_mb > 0
        assert len(monitor.snapshots) == 1

    def test_multiple_snapshots(self):
        """Test taking multiple snapshots."""
        monitor = MemoryMonitor()
        monitor.take_snapshot()
        monitor.take_snapshot()
        monitor.take_snapshot()

        assert len(monitor.snapshots) == 3

    def test_peak_memory_tracking(self):
        """Test peak memory tracking."""
        monitor = MemoryMonitor()
        monitor.take_snapshot()

        peak = monitor.get_peak_memory()
        assert peak > 0


class TestConcurrentTestResult:
    """Test ConcurrentTestResult."""

    def test_create_result(self):
        """Test creating result."""
        result = ConcurrentTestResult(
            concurrent_count=10,
            total_documents=100,
            successful=95,
            failed=5,
            duration_seconds=10.0,
            memory_start_mb=50.0,
            memory_peak_mb=60.0,
            memory_end_mb=52.0,
            memory_growth_mb=2.0,
            throughput_docs_per_sec=9.5,
        )

        assert result.concurrent_count == 10
        assert result.total_documents == 100

    def test_success_rate(self):
        """Test success rate calculation."""
        result = ConcurrentTestResult(
            concurrent_count=10,
            total_documents=100,
            successful=95,
            failed=5,
            duration_seconds=10.0,
            memory_start_mb=50.0,
            memory_peak_mb=60.0,
            memory_end_mb=52.0,
            memory_growth_mb=2.0,
            throughput_docs_per_sec=9.5,
        )

        assert result.success_rate == 95.0

    def test_result_to_dict(self):
        """Test converting result to dict."""
        result = ConcurrentTestResult(
            concurrent_count=10,
            total_documents=100,
            successful=95,
            failed=5,
            duration_seconds=10.0,
            memory_start_mb=50.0,
            memory_peak_mb=60.0,
            memory_end_mb=52.0,
            memory_growth_mb=2.0,
            throughput_docs_per_sec=9.5,
        )

        dict_form = result.to_dict()
        assert dict_form["concurrent_count"] == 10
        assert dict_form["success_rate"] == 95.0


class TestConcurrentIngestionTest:
    """Test ConcurrentIngestionTest."""

    def test_create_test(self):
        """Test creating concurrent test."""
        mock_manager = Mock()
        test = ConcurrentIngestionTest(mock_manager)

        assert test.manager is mock_manager
        assert test.results == []

    def test_ingest_document_worker_success(self):
        """Test successful document ingestion worker."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 1
        mock_manager.ingest_documents.return_value = mock_result

        test = ConcurrentIngestionTest(mock_manager)
        doc = {"id": "doc1", "text": "Test"}

        success = test.ingest_document_worker(doc)
        assert success is True

    def test_ingest_document_worker_failure(self):
        """Test failed document ingestion worker."""
        mock_manager = Mock()
        mock_manager.ingest_documents.side_effect = Exception("Test error")

        test = ConcurrentIngestionTest(mock_manager)
        doc = {"id": "doc1", "text": "Test"}

        success = test.ingest_document_worker(doc)
        assert success is False

    def test_run_concurrent_test(self):
        """Test running concurrent test."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 1
        mock_manager.ingest_documents.return_value = mock_result

        test = ConcurrentIngestionTest(mock_manager)
        documents = [
            {"id": f"doc_{i}", "text": f"Document {i}"}
            for i in range(10)
        ]

        result = test.run_concurrent_test(documents, concurrent_count=5)

        assert result.concurrent_count == 5
        assert result.total_documents == 10
        assert isinstance(result, ConcurrentTestResult)

    def test_concurrent_documents_processed(self):
        """Test that concurrent test processes documents."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 1
        mock_manager.ingest_documents.return_value = mock_result

        test = ConcurrentIngestionTest(mock_manager)
        documents = [
            {"id": f"doc_{i}", "text": f"Document {i}"}
            for i in range(20)
        ]

        result = test.run_concurrent_test(documents, concurrent_count=10)

        # All documents should be attempted
        assert result.total_documents == 20

    def test_memory_tracking(self):
        """Test memory tracking during concurrent test."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 1
        mock_manager.ingest_documents.return_value = mock_result

        test = ConcurrentIngestionTest(mock_manager)
        documents = [
            {"id": f"doc_{i}", "text": f"Document {i}"}
            for i in range(5)
        ]

        result = test.run_concurrent_test(documents, concurrent_count=2)

        # Memory metrics should be tracked
        assert result.memory_start_mb > 0
        assert result.memory_peak_mb > 0
        assert result.memory_end_mb > 0

    def test_run_all_tests(self):
        """Test running all concurrent tests."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 1
        mock_manager.ingest_documents.return_value = mock_result

        test = ConcurrentIngestionTest(mock_manager)
        results = test.run_all_tests(test_sizes=[10, 20])

        assert len(results) == 2
        assert results[0].total_documents == 10
        assert results[1].total_documents == 20

    def test_generate_report(self):
        """Test report generation."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 1
        mock_manager.ingest_documents.return_value = mock_result

        test = ConcurrentIngestionTest(mock_manager)
        documents = [
            {"id": f"doc_{i}", "text": f"Document {i}"}
            for i in range(10)
        ]

        test.run_concurrent_test(documents, concurrent_count=5)
        report = test.generate_report()

        assert "CONCURRENT INGESTION STRESS TEST REPORT" in report
        assert "10" in report  # Document count


class TestConcurrentTestingIntegration:
    """Integration tests for concurrent testing."""

    def test_full_concurrent_workflow(self):
        """Test complete concurrent testing workflow."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 1
        mock_manager.ingest_documents.return_value = mock_result

        test = ConcurrentIngestionTest(mock_manager)

        # Run tests with different document counts
        doc_counts = [10, 20, 30]
        for count in doc_counts:
            documents = [
                {"id": f"doc_{i}", "text": f"Document {i}"}
                for i in range(count)
            ]
            result = test.run_concurrent_test(documents, concurrent_count=10)
            assert result.total_documents == count

        # All results should be recorded
        assert len(test.results) == 3

    def test_memory_growth_tracking(self):
        """Test memory growth measurement."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 1
        mock_manager.ingest_documents.return_value = mock_result

        test = ConcurrentIngestionTest(mock_manager)
        documents = [
            {"id": f"doc_{i}", "text": f"Document {i}" * 100}
            for i in range(50)
        ]

        result = test.run_concurrent_test(documents, concurrent_count=10)

        # Memory metrics should be valid
        assert result.memory_start_mb >= 0
        assert result.memory_peak_mb >= result.memory_start_mb
        assert result.memory_end_mb >= 0

    def test_concurrent_scalability(self):
        """Test scalability with different worker counts."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 1
        mock_manager.ingest_documents.return_value = mock_result

        test = ConcurrentIngestionTest(mock_manager)
        documents = [
            {"id": f"doc_{i}", "text": f"Document {i}"}
            for i in range(100)
        ]

        # Test with different concurrent counts
        for concurrent_count in [5, 10, 20]:
            result = test.run_concurrent_test(documents, concurrent_count=concurrent_count)
            assert result.concurrent_count == concurrent_count
            assert result.throughput_docs_per_sec > 0
