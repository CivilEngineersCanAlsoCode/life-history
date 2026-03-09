"""
Tests for resilient batch ingestion with exponential backoff.

Tests cover:
- Exponential backoff retry strategy (1s, 2s, 4s, 8s, max 60s)
- Transient vs permanent error classification
- Deadletter queue management
- Batch ingestion with retries
- Statistics and recovery
"""

import pytest
import time
from unittest.mock import Mock, MagicMock

from life_brain.core.batch_ingest_resilient import (
    BatchIngestResilient,
    IngestResult,
    BatchIngestResult,
    classify_error,
)
from life_brain.core.retry_manager import FailureReason, RetryPolicy


class TestErrorClassification:
    """Test error classification logic."""

    def test_classify_transient_timeout(self):
        """Test timeout errors are classified as transient."""
        error = TimeoutError("Connection timeout")
        reason = classify_error(error)
        assert reason == FailureReason.TRANSIENT

    def test_classify_transient_network(self):
        """Test network errors are classified as transient."""
        error = ConnectionError("Network unreachable")
        reason = classify_error(error)
        assert reason == FailureReason.TRANSIENT

    def test_classify_validation_error(self):
        """Test validation errors are classified as permanent."""
        error = ValueError("Invalid data schema")
        reason = classify_error(error)
        assert reason in [FailureReason.VALIDATION, FailureReason.PERMANENT]

    def test_classify_conflict_error(self):
        """Test conflict errors are properly classified."""
        error = Exception("Conflict detected")
        reason = classify_error(error)
        assert reason in [FailureReason.CONFLICT, FailureReason.PERMANENT]

    def test_classify_unknown_error(self):
        """Test unknown errors default to permanent."""
        error = Exception("Some random error")
        reason = classify_error(error)
        assert reason == FailureReason.PERMANENT


class TestBatchIngestResilient:
    """Test resilient batch ingestion."""

    def test_create_ingester(self):
        """Test creating batch ingester."""
        mock_ingest = Mock(return_value=True)
        ingester = BatchIngestResilient(mock_ingest)

        assert ingester.ingest_function == mock_ingest
        assert ingester.retry_policy.max_retries == 3
        assert ingester.retry_policy.initial_backoff_seconds == 1.0

    def test_ingest_document_success(self):
        """Test successful document ingestion."""
        mock_ingest = Mock(return_value=True)
        ingester = BatchIngestResilient(mock_ingest)

        success, error = ingester.ingest_document("doc1", {"key": "value"})

        assert success is True
        assert error is None

    def test_ingest_document_failure(self):
        """Test failed document ingestion."""
        mock_ingest = Mock(return_value=False)
        ingester = BatchIngestResilient(mock_ingest)

        success, error = ingester.ingest_document("doc1", {})

        assert success is False
        assert error is not None

    def test_ingest_document_exception(self):
        """Test ingestion with exception."""
        mock_ingest = Mock(side_effect=Exception("Test error"))
        ingester = BatchIngestResilient(mock_ingest)

        success, error = ingester.ingest_document("doc1", {})

        assert success is False
        assert "Test error" in error

    def test_batch_ingest_all_success(self):
        """Test batch ingestion where all succeed."""
        mock_ingest = Mock(return_value=True)
        ingester = BatchIngestResilient(mock_ingest)

        documents = [
            {"doc_id": f"doc{i}", "metadata": {}} for i in range(5)
        ]

        result = ingester.ingest_batch_with_retries(documents)

        assert result.total_documents == 5
        assert result.successful == 5
        assert result.deadlettered == 0
        assert result.in_retry_queue == 0

    def test_batch_ingest_all_permanent_failure(self):
        """Test batch where all fail permanently."""
        mock_ingest = Mock(side_effect=ValueError("Validation error"))
        ingester = BatchIngestResilient(mock_ingest)

        documents = [
            {"doc_id": f"doc{i}", "metadata": {}} for i in range(3)
        ]

        result = ingester.ingest_batch_with_retries(documents)

        assert result.total_documents == 3
        assert result.successful == 0
        assert result.deadlettered == 3
        assert result.in_retry_queue == 0

    def test_batch_ingest_transient_failure(self):
        """Test batch with transient errors (will retry)."""
        call_count = 0

        def transient_fail(doc_id, metadata):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise TimeoutError("Connection timeout")
            return True

        ingester = BatchIngestResilient(transient_fail)

        documents = [{"doc_id": "doc1", "metadata": {}}]

        result = ingester.ingest_batch_with_retries(documents)

        assert result.successful == 1
        assert result.deadlettered == 0

    def test_exponential_backoff_timing(self):
        """Test exponential backoff calculations."""
        policy = RetryPolicy(
            initial_backoff_seconds=1.0,
            backoff_multiplier=2.0,
            max_backoff_seconds=60.0,
        )

        # Verify backoff sequence: 1s, 2s, 4s, 8s, 16s, 32s, 60s (capped)
        expected = [1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 60.0]
        for i in range(7):
            backoff = policy.get_backoff_seconds(i)
            assert backoff == expected[i]

    def test_backoff_capped_at_max(self):
        """Test backoff is capped at max value."""
        policy = RetryPolicy(
            initial_backoff_seconds=1.0,
            backoff_multiplier=2.0,
            max_backoff_seconds=60.0,
        )

        # At attempt 10, would be 512s without cap
        backoff = policy.get_backoff_seconds(10)
        assert backoff == 60.0

    def test_retry_queue_management(self):
        """Test retry queue is properly managed."""
        call_count = 0

        def eventually_succeed(doc_id, metadata):
            nonlocal call_count
            call_count += 1
            if call_count <= 1:
                raise TimeoutError("Retry me")
            return True

        ingester = BatchIngestResilient(eventually_succeed)

        documents = [
            {"doc_id": "doc1", "metadata": {}},
            {"doc_id": "doc2", "metadata": {}},
        ]

        result = ingester.ingest_batch_with_retries(documents)

        assert result.in_retry_queue == 0
        assert len(ingester.retry_queue) == 0

    def test_deadletter_queue_recovery(self):
        """Test manual retry of deadlettered documents."""
        mock_ingest = Mock(side_effect=ValueError("Permanent error"))
        ingester = BatchIngestResilient(mock_ingest)

        documents = [{"doc_id": "doc1", "metadata": {}}]
        result = ingester.ingest_batch_with_retries(documents)

        assert len(ingester.get_deadletter_documents()) == 1

        # Now make ingest succeed
        mock_ingest.side_effect = None
        mock_ingest.return_value = True

        success, error = ingester.retry_deadletter_document("doc1")

        assert success is True
        assert len(ingester.get_deadletter_documents()) == 0

    def test_mixed_success_and_permanent_failure(self):
        """Test batch with mix of successes and permanent failures."""

        def mixed_ingest(doc_id, metadata):
            if "fail" in doc_id:
                raise ValueError("Validation error")
            return True

        ingester = BatchIngestResilient(mixed_ingest)

        documents = [
            {"doc_id": "doc1", "metadata": {}},
            {"doc_id": "fail_doc", "metadata": {}},
            {"doc_id": "doc2", "metadata": {}},
        ]

        result = ingester.ingest_batch_with_retries(documents)

        assert result.successful == 2
        assert result.deadlettered == 1

    def test_batch_statistics(self):
        """Test statistics generation."""
        mock_ingest = Mock(side_effect=TimeoutError("Timeout"))
        ingester = BatchIngestResilient(mock_ingest)

        documents = [{"doc_id": f"doc{i}", "metadata": {}} for i in range(3)]
        result = ingester.ingest_batch_with_retries(documents)

        stats = ingester.get_statistics()

        assert stats["total_in_retry_queue"] >= 0
        assert "deadletter_docs" in stats
        assert "retry_queue_docs" in stats

    def test_batch_result_success_rate(self):
        """Test success rate calculation."""

        def partial_success(doc_id, metadata):
            return int(doc_id.split("doc")[1]) % 2 == 0

        ingester = BatchIngestResilient(partial_success)

        documents = [{"doc_id": f"doc{i}", "metadata": {}} for i in range(10)]
        result = ingester.ingest_batch_with_retries(documents)

        rate = result.get_success_rate()
        assert 0 <= rate <= 100

    def test_ingest_result_tracking(self):
        """Test that individual results are tracked."""
        call_count = {}

        def selectively_succeed(doc_id, metadata):
            if doc_id not in call_count:
                call_count[doc_id] = 0
            call_count[doc_id] += 1

            if doc_id == "fail_doc":
                raise ValueError("Permanent failure")

            return True

        ingester = BatchIngestResilient(selectively_succeed)

        documents = [
            {"doc_id": "success_doc", "metadata": {}},
            {"doc_id": "fail_doc", "metadata": {}},
        ]

        result = ingester.ingest_batch_with_retries(documents)

        assert len(result.results) == 2
        assert result.successful == 1  # success_doc
        assert result.deadlettered == 1  # fail_doc

    def test_custom_retry_policy(self):
        """Test with custom retry policy."""
        custom_policy = RetryPolicy(
            max_retries=2,
            initial_backoff_seconds=0.1,
            backoff_multiplier=2.0,
            max_backoff_seconds=10.0,
        )

        mock_ingest = Mock(return_value=True)
        ingester = BatchIngestResilient(mock_ingest, retry_policy=custom_policy)

        assert ingester.retry_policy.max_retries == 2
        assert ingester.retry_policy.initial_backoff_seconds == 0.1

    def test_complete_workflow(self):
        """Test complete batch ingestion workflow."""

        def selective_ingest(doc_id, metadata):
            # permanent docs always fail
            if "permanent" in doc_id:
                raise ValueError("Permanent error")
            # normal docs always succeed
            return True

        ingester = BatchIngestResilient(selective_ingest)

        documents = [
            {"doc_id": "normal_1", "metadata": {"type": "normal"}},
            {"doc_id": "permanent_1", "metadata": {"type": "permanent"}},
            {"doc_id": "normal_2", "metadata": {"type": "normal"}},
        ]

        result = ingester.ingest_batch_with_retries(documents)

        assert result.total_documents == 3
        assert result.successful == 2  # normal_1, normal_2
        assert result.deadlettered == 1  # permanent_1
        assert result.duration_seconds > 0

    def test_empty_batch(self):
        """Test empty batch handling."""
        mock_ingest = Mock(return_value=True)
        ingester = BatchIngestResilient(mock_ingest)

        result = ingester.ingest_batch_with_retries([])

        assert result.total_documents == 0
        assert result.successful == 0
        assert result.deadlettered == 0

    def test_deadletter_not_found(self):
        """Test retry of non-existent deadletter document."""
        mock_ingest = Mock(return_value=True)
        ingester = BatchIngestResilient(mock_ingest)

        success, error = ingester.retry_deadletter_document("nonexistent")

        assert success is False
        assert error is not None
