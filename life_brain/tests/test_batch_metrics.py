"""
Unit tests for batch_metrics.py

Covers:
- BatchOperation metrics tracking
- BatchMetrics aggregation
- BatchProgressTracker real-time progress
- BatchReporter report generation
"""

import pytest
from datetime import datetime, timedelta
from time import sleep
from life_brain.db.batch_metrics import (
    BatchOperation,
    BatchMetrics,
    BatchProgressTracker,
    BatchReporter,
)


class TestBatchOperation:
    """Test single batch operation tracking."""

    def test_create_batch_operation(self):
        """Test creating a batch operation."""
        batch = BatchOperation(batch_id="batch_1", total_documents=100)
        assert batch.batch_id == "batch_1"
        assert batch.total_documents == 100
        assert batch.successful == 0
        assert batch.failed_first_try == 0
        assert batch.deadlettered == 0
        assert batch.start_ts is not None

    def test_record_success(self):
        """Test recording successful documents."""
        batch = BatchOperation(batch_id="batch_1", total_documents=10)
        batch.successful = 7
        assert batch.successful == 7

    def test_record_errors(self):
        """Test recording errors by type."""
        batch = BatchOperation(batch_id="batch_1", total_documents=10)
        batch.add_error("ValidationError", 3)
        batch.add_error("ValidationError", 2)
        batch.add_error("ConflictError", 1)

        assert batch.errors_by_type["ValidationError"] == 5
        assert batch.errors_by_type["ConflictError"] == 1

    def test_add_error_new_type(self):
        """Test adding a new error type."""
        batch = BatchOperation(batch_id="batch_1", total_documents=10)
        batch.add_error("NewError")
        assert batch.errors_by_type["NewError"] == 1

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        batch = BatchOperation(batch_id="batch_1", total_documents=100)
        batch.successful = 85
        assert batch.get_success_rate() == 85.0

    def test_success_rate_zero_documents(self):
        """Test success rate with zero documents."""
        batch = BatchOperation(batch_id="batch_1", total_documents=0)
        assert batch.get_success_rate() == 0.0

    def test_throughput_calculation(self):
        """Test throughput calculation."""
        batch = BatchOperation(batch_id="batch_1", total_documents=100)
        batch.duration_seconds = 10.0
        assert batch.get_throughput() == 10.0  # 100 docs / 10 seconds

    def test_throughput_zero_duration(self):
        """Test throughput with zero duration."""
        batch = BatchOperation(batch_id="batch_1", total_documents=100)
        assert batch.get_throughput() == 0.0

    def test_complete_batch(self):
        """Test completing a batch."""
        batch = BatchOperation(batch_id="batch_1", total_documents=10)
        batch.successful = 8
        batch.complete()

        assert batch.end_ts is not None
        assert batch.duration_seconds >= 0

    def test_batch_to_dict(self):
        """Test exporting batch as dictionary."""
        batch = BatchOperation(batch_id="batch_1", total_documents=100)
        batch.successful = 95
        batch.deadlettered = 5
        batch.complete()

        result = batch.to_dict()
        assert result["batch_id"] == "batch_1"
        assert result["total_documents"] == 100
        assert result["successful"] == 95
        assert result["deadlettered"] == 5


class TestBatchMetrics:
    """Test aggregated batch metrics."""

    def test_create_batch_metrics(self):
        """Test creating batch metrics."""
        metrics = BatchMetrics()
        assert metrics.total_batches == 0
        assert metrics.total_documents == 0
        assert metrics.total_successful == 0

    def test_add_single_batch(self):
        """Test adding a single batch."""
        metrics = BatchMetrics()
        batch = BatchOperation(batch_id="batch_1", total_documents=100)
        batch.successful = 90
        batch.deadlettered = 10
        batch.duration_seconds = 5.0

        metrics.add_batch(batch)

        assert metrics.total_batches == 1
        assert metrics.total_documents == 100
        assert metrics.total_successful == 90
        assert metrics.total_deadlettered == 10

    def test_add_multiple_batches(self):
        """Test adding multiple batches."""
        metrics = BatchMetrics()

        for i in range(3):
            batch = BatchOperation(batch_id=f"batch_{i}", total_documents=100)
            batch.successful = 90
            batch.duration_seconds = 5.0
            metrics.add_batch(batch)

        assert metrics.total_batches == 3
        assert metrics.total_documents == 300
        assert metrics.total_successful == 270

    def test_error_aggregation(self):
        """Test error aggregation across batches."""
        metrics = BatchMetrics()

        batch1 = BatchOperation(batch_id="batch_1", total_documents=100)
        batch1.add_error("ValidationError", 5)
        batch1.add_error("ConflictError", 3)
        metrics.add_batch(batch1)

        batch2 = BatchOperation(batch_id="batch_2", total_documents=100)
        batch2.add_error("ValidationError", 7)
        batch2.add_error("TimeoutError", 2)
        metrics.add_batch(batch2)

        assert metrics.error_summary["ValidationError"] == 12
        assert metrics.error_summary["ConflictError"] == 3
        assert metrics.error_summary["TimeoutError"] == 2

    def test_overall_success_rate(self):
        """Test overall success rate calculation."""
        metrics = BatchMetrics()

        for i in range(2):
            batch = BatchOperation(batch_id=f"batch_{i}", total_documents=100)
            batch.successful = 80
            metrics.add_batch(batch)

        assert metrics.get_overall_success_rate() == 80.0

    def test_overall_throughput(self):
        """Test overall throughput calculation."""
        metrics = BatchMetrics()

        batch1 = BatchOperation(batch_id="batch_1", total_documents=100)
        batch1.duration_seconds = 10.0
        metrics.add_batch(batch1)

        batch2 = BatchOperation(batch_id="batch_2", total_documents=100)
        batch2.duration_seconds = 10.0
        metrics.add_batch(batch2)

        # 200 docs / 20 seconds = 10 docs/sec
        assert metrics.get_overall_throughput() == 10.0

    def test_most_common_error(self):
        """Test finding most common error type."""
        metrics = BatchMetrics()

        batch = BatchOperation(batch_id="batch_1", total_documents=100)
        batch.add_error("ValidationError", 50)
        batch.add_error("ConflictError", 20)
        batch.add_error("TimeoutError", 5)
        metrics.add_batch(batch)

        assert metrics.get_most_common_error() == "ValidationError"

    def test_most_common_error_empty(self):
        """Test most common error with no errors."""
        metrics = BatchMetrics()
        assert metrics.get_most_common_error() is None

    def test_metrics_to_dict(self):
        """Test exporting metrics as dictionary."""
        metrics = BatchMetrics()
        batch = BatchOperation(batch_id="batch_1", total_documents=100)
        batch.successful = 85
        batch.duration_seconds = 10.0
        metrics.add_batch(batch)

        result = metrics.to_dict()
        assert result["total_batches"] == 1
        assert result["total_documents"] == 100
        assert result["total_successful"] == 85
        assert "overall_success_rate" in result
        assert "overall_throughput_docs_per_sec" in result


class TestBatchProgressTracker:
    """Test real-time batch progress tracking."""

    def test_create_progress_tracker(self):
        """Test creating progress tracker."""
        tracker = BatchProgressTracker(batch_id="batch_1", total=100)
        assert tracker.batch.batch_id == "batch_1"
        assert tracker.batch.total_documents == 100
        assert tracker.processed == 0

    def test_record_success(self):
        """Test recording successful ingestion."""
        tracker = BatchProgressTracker(batch_id="batch_1", total=100)
        tracker.record_success()

        assert tracker.processed == 1
        assert tracker.batch.successful == 1

    def test_record_failed_first_try(self):
        """Test recording first-attempt failure."""
        tracker = BatchProgressTracker(batch_id="batch_1", total=100)
        tracker.record_failed_first_try("ValidationError")

        assert tracker.processed == 1
        assert tracker.batch.failed_first_try == 1
        assert tracker.batch.errors_by_type["ValidationError"] == 1

    def test_record_deadlettered(self):
        """Test recording deadlettered document."""
        tracker = BatchProgressTracker(batch_id="batch_1", total=100)
        tracker.record_deadlettered("ConflictError")

        assert tracker.processed == 1
        assert tracker.batch.deadlettered == 1
        assert tracker.batch.errors_by_type["ConflictError"] == 1

    def test_record_retry_scheduled(self):
        """Test recording retry scheduling."""
        tracker = BatchProgressTracker(batch_id="batch_1", total=100)
        tracker.record_retry_scheduled("TimeoutError")

        assert tracker.processed == 1
        assert tracker.batch.in_retry_queue == 1
        assert tracker.batch.errors_by_type["TimeoutError"] == 1

    def test_mixed_operations(self):
        """Test tracking mixed operation outcomes."""
        tracker = BatchProgressTracker(batch_id="batch_1", total=100)

        for i in range(80):
            tracker.record_success()

        for i in range(15):
            tracker.record_retry_scheduled("TimeoutError")

        for i in range(5):
            tracker.record_deadlettered("ConflictError")

        assert tracker.processed == 100
        assert tracker.batch.successful == 80
        assert tracker.batch.in_retry_queue == 15
        assert tracker.batch.deadlettered == 5

    def test_complete_tracker(self):
        """Test completing progress tracker."""
        tracker = BatchProgressTracker(batch_id="batch_1", total=100)
        tracker.record_success()
        tracker.record_success()

        batch = tracker.complete()

        assert batch.batch_id == "batch_1"
        assert batch.successful == 2
        assert batch.duration_seconds >= 0
        assert batch.end_ts is not None


class TestBatchReporter:
    """Test batch report generation."""

    def test_format_text_report_success(self):
        """Test formatting successful batch report."""
        batch = BatchOperation(batch_id="batch_1", total_documents=100)
        batch.successful = 95
        batch.in_retry_queue = 3
        batch.deadlettered = 2
        batch.duration_seconds = 10.0
        batch.add_error("ValidationError", 3)
        batch.add_error("TimeoutError", 2)

        report = BatchReporter.format_text_report(batch)

        assert "batch_1" in report
        assert "95" in report  # successful count
        assert "10.00 seconds" in report
        assert "ValidationError" in report
        assert "TimeoutError" in report

    def test_format_text_report_no_errors(self):
        """Test formatting report with no errors."""
        batch = BatchOperation(batch_id="batch_2", total_documents=50)
        batch.successful = 50
        batch.duration_seconds = 5.0

        report = BatchReporter.format_text_report(batch)

        assert "batch_2" in report
        assert "(No errors)" in report

    def test_format_text_report_all_failed(self):
        """Test formatting report with all failures."""
        batch = BatchOperation(batch_id="batch_3", total_documents=100)
        batch.successful = 0
        batch.deadlettered = 100
        batch.duration_seconds = 2.0
        batch.add_error("PermanentError", 100)

        report = BatchReporter.format_text_report(batch)

        assert "batch_3" in report
        assert "0.0%" in report or "0%" in report  # success rate
        assert "PermanentError" in report
        assert "100" in report


class TestIntegrationBatchMetrics:
    """Integration tests for batch metrics workflow."""

    def test_full_batch_workflow(self):
        """Test full batch ingestion workflow."""
        # Create progress tracker
        tracker = BatchProgressTracker(batch_id="batch_1", total=100)

        # Simulate ingestion
        for i in range(100):
            if i < 80:
                tracker.record_success()
            elif i < 90:
                tracker.record_retry_scheduled("TransientError")
            else:
                tracker.record_deadlettered("ConflictError")

        # Complete batch
        batch = tracker.complete()

        # Add to metrics
        metrics = BatchMetrics()
        metrics.add_batch(batch)

        # Verify end-to-end
        assert metrics.total_batches == 1
        assert metrics.total_documents == 100
        assert metrics.total_successful == 80
        assert metrics.total_in_retry == 10
        assert metrics.total_deadlettered == 10
        assert metrics.get_overall_success_rate() == 80.0

    def test_multiple_batch_aggregation(self):
        """Test aggregating multiple batches."""
        metrics = BatchMetrics()

        # Batch 1: 95% success
        tracker1 = BatchProgressTracker(batch_id="batch_1", total=100)
        for i in range(95):
            tracker1.record_success()
        for i in range(5):
            tracker1.record_deadlettered("Error1")
        metrics.add_batch(tracker1.complete())

        # Batch 2: 90% success
        tracker2 = BatchProgressTracker(batch_id="batch_2", total=100)
        for i in range(90):
            tracker2.record_success()
        for i in range(10):
            tracker2.record_deadlettered("Error2")
        metrics.add_batch(tracker2.complete())

        # Verify aggregation
        assert metrics.total_batches == 2
        assert metrics.total_documents == 200
        assert metrics.total_successful == 185
        assert metrics.get_overall_success_rate() == 92.5
        assert "Error1" in metrics.error_summary
        assert "Error2" in metrics.error_summary
        assert metrics.error_summary["Error1"] == 5
        assert metrics.error_summary["Error2"] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
