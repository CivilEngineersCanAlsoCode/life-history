"""
Test suite for resilience and deadletter queue testing.

Tests cover:
- Retry policy and exponential backoff
- Error categorization
- Deadletter queue management
- Resilience metrics
"""

import pytest
from unittest.mock import Mock, MagicMock

from life_brain.performance.resilience_testing import (
    ErrorCategory,
    RetryAttempt,
    DeadletterEntry,
    ResilienceTestResult,
    RetryPolicy,
    ResilienceTest,
)


class TestErrorCategory:
    """Test ErrorCategory enum."""

    def test_error_categories_exist(self):
        """Test that error categories exist."""
        assert ErrorCategory.TRANSIENT is not None
        assert ErrorCategory.VALIDATION is not None
        assert ErrorCategory.CONFLICT is not None
        assert ErrorCategory.SYSTEM is not None


class TestRetryAttempt:
    """Test RetryAttempt."""

    def test_create_attempt(self):
        """Test creating retry attempt."""
        attempt = RetryAttempt(
            attempt_number=1,
            backoff_seconds=1.0,
            error="Test error",
            success=False,
        )

        assert attempt.attempt_number == 1
        assert attempt.backoff_seconds == 1.0


class TestDeadletterEntry:
    """Test DeadletterEntry."""

    def test_create_entry(self):
        """Test creating deadletter entry."""
        entry = DeadletterEntry(
            doc_id="doc_001",
            document={"id": "doc_001", "text": "Test"},
            error_category=ErrorCategory.VALIDATION,
            error_message="Invalid format",
            final_error="Invalid format",
            max_retries_exceeded=False,
        )

        assert entry.doc_id == "doc_001"
        assert entry.error_category == ErrorCategory.VALIDATION


class TestRetryPolicy:
    """Test RetryPolicy."""

    def test_default_policy(self):
        """Test default retry policy."""
        policy = RetryPolicy()
        assert policy.max_retries == 3
        assert policy.initial_backoff == 1.0

    def test_custom_policy(self):
        """Test custom retry policy."""
        policy = RetryPolicy(
            max_retries=5,
            initial_backoff=2.0,
            max_backoff=120.0,
        )

        assert policy.max_retries == 5
        assert policy.initial_backoff == 2.0

    def test_exponential_backoff(self):
        """Test exponential backoff calculation."""
        policy = RetryPolicy(
            initial_backoff=1.0,
            max_backoff=60.0,
            multiplier=2.0,
        )

        backoff_0 = policy.get_backoff(0)
        backoff_1 = policy.get_backoff(1)
        backoff_2 = policy.get_backoff(2)

        assert backoff_0 == 1.0
        assert backoff_1 == 2.0
        assert backoff_2 == 4.0

    def test_backoff_cap(self):
        """Test backoff maximum cap."""
        policy = RetryPolicy(
            initial_backoff=1.0,
            max_backoff=10.0,
            multiplier=2.0,
        )

        backoff_10 = policy.get_backoff(10)
        assert backoff_10 <= 10.0

    def test_should_retry_transient(self):
        """Test retry decision for transient errors."""
        policy = RetryPolicy(max_retries=3)

        # Transient errors should retry
        assert policy.should_retry(0, ErrorCategory.TRANSIENT) is True
        assert policy.should_retry(1, ErrorCategory.TRANSIENT) is True
        assert policy.should_retry(2, ErrorCategory.TRANSIENT) is True

        # Should not retry after max retries
        assert policy.should_retry(3, ErrorCategory.TRANSIENT) is False

    def test_should_not_retry_validation(self):
        """Test that validation errors don't retry."""
        policy = RetryPolicy()

        # Validation errors should not retry
        assert policy.should_retry(0, ErrorCategory.VALIDATION) is False
        assert policy.should_retry(1, ErrorCategory.VALIDATION) is False


class TestResilienceTestResult:
    """Test ResilienceTestResult."""

    def test_create_result(self):
        """Test creating result."""
        result = ResilienceTestResult(
            total_documents=100,
            successful=90,
            retried=5,
            deadlettered=10,
            max_retries_exceeded=2,
            duration_seconds=10.0,
            avg_retry_count=1.2,
            transient_errors=5,
            validation_errors=3,
            conflict_errors=2,
            system_errors=0,
        )

        assert result.total_documents == 100
        assert result.successful == 90

    def test_success_rate(self):
        """Test success rate calculation."""
        result = ResilienceTestResult(
            total_documents=100,
            successful=90,
            retried=5,
            deadlettered=10,
            max_retries_exceeded=0,
            duration_seconds=10.0,
            avg_retry_count=0.0,
            transient_errors=0,
            validation_errors=0,
            conflict_errors=0,
            system_errors=0,
        )

        assert result.success_rate == 90.0

    def test_deadletter_rate(self):
        """Test deadletter rate calculation."""
        result = ResilienceTestResult(
            total_documents=100,
            successful=90,
            retried=0,
            deadlettered=10,
            max_retries_exceeded=0,
            duration_seconds=10.0,
            avg_retry_count=0.0,
            transient_errors=0,
            validation_errors=0,
            conflict_errors=0,
            system_errors=0,
        )

        assert result.deadletter_rate == 10.0


class TestResilienceTest:
    """Test ResilienceTest."""

    def test_create_test(self):
        """Test creating resilience test."""
        mock_manager = Mock()
        test = ResilienceTest(mock_manager)

        assert test.manager is mock_manager
        assert test.retry_policy is not None

    def test_error_categorization_transient(self):
        """Test transient error categorization."""
        mock_manager = Mock()
        test = ResilienceTest(mock_manager)

        # Should categorize as transient
        category = test.categorize_error("Connection timeout")
        assert category == ErrorCategory.TRANSIENT

        category = test.categorize_error("Network error temporarily unavailable")
        assert category == ErrorCategory.TRANSIENT

    def test_error_categorization_validation(self):
        """Test validation error categorization."""
        mock_manager = Mock()
        test = ResilienceTest(mock_manager)

        category = test.categorize_error("Invalid format")
        assert category == ErrorCategory.VALIDATION

        category = test.categorize_error("Schema validation failed")
        assert category == ErrorCategory.VALIDATION

    def test_error_categorization_conflict(self):
        """Test conflict error categorization."""
        mock_manager = Mock()
        test = ResilienceTest(mock_manager)

        category = test.categorize_error("Document conflict detected")
        assert category == ErrorCategory.CONFLICT

        category = test.categorize_error("Duplicate document exists")
        assert category == ErrorCategory.CONFLICT

    def test_ingest_with_retry_success(self):
        """Test successful ingestion with retry."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 1
        mock_manager.ingest_documents.return_value = mock_result

        test = ResilienceTest(mock_manager)
        doc = {"id": "doc_1", "text": "Test"}

        success = test.ingest_with_retry(doc)
        assert success is True

    def test_ingest_with_retry_failure(self):
        """Test failed ingestion."""
        mock_manager = Mock()
        mock_manager.ingest_documents.side_effect = Exception("System error")

        test = ResilienceTest(mock_manager)
        doc = {"id": "doc_1", "text": "Test"}

        success = test.ingest_with_retry(doc)
        # Should fail and not deadletter (validation errors don't deadletter)
        assert success is False

    def test_run_resilience_test(self):
        """Test running resilience test."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 1
        mock_manager.ingest_documents.return_value = mock_result

        test = ResilienceTest(mock_manager)
        documents = [
            {"id": f"doc_{i}", "text": f"Document {i}"}
            for i in range(10)
        ]

        result = test.run_resilience_test(documents)

        assert result.total_documents == 10
        assert isinstance(result, ResilienceTestResult)

    def test_generate_report(self):
        """Test report generation."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 1
        mock_manager.ingest_documents.return_value = mock_result

        test = ResilienceTest(mock_manager)
        documents = [
            {"id": f"doc_{i}", "text": f"Document {i}"}
            for i in range(5)
        ]

        test_result = test.run_resilience_test(documents)
        report = test.generate_report(test_result)

        assert "RESILIENCE & DEADLETTER QUEUE TEST REPORT" in report
        assert "SUCCESS" in report.upper() or "SUCCESSFUL" in report.upper()


class TestResilienceIntegration:
    """Integration tests for resilience testing."""

    def test_full_resilience_workflow(self):
        """Test complete resilience testing workflow."""
        mock_manager = Mock()
        mock_result = Mock()
        mock_result.success_count = 1
        mock_manager.ingest_documents.return_value = mock_result

        # Create test with custom policy
        policy = RetryPolicy(max_retries=3, initial_backoff=0.1)
        test = ResilienceTest(mock_manager, policy)

        documents = [
            {"id": f"doc_{i}", "text": f"Document {i}"}
            for i in range(20)
        ]

        result = test.run_resilience_test(documents)

        assert result.total_documents == 20
        assert result.successful > 0

    def test_error_categorization_accuracy(self):
        """Test accuracy of error categorization."""
        mock_manager = Mock()
        test = ResilienceTest(mock_manager)

        test_cases = [
            ("timeout", ErrorCategory.TRANSIENT),
            ("connection", ErrorCategory.TRANSIENT),
            ("invalid schema", ErrorCategory.VALIDATION),
            ("duplicate", ErrorCategory.CONFLICT),
            ("unknown error", ErrorCategory.SYSTEM),
        ]

        for error_msg, expected_category in test_cases:
            category = test.categorize_error(error_msg)
            assert category == expected_category, f"Failed for: {error_msg}"

    def test_retry_policy_enforcement(self):
        """Test that retry policy is enforced."""
        mock_manager = Mock()
        policy = RetryPolicy(max_retries=3)
        test = ResilienceTest(mock_manager, policy)

        # Verify policy is set
        assert test.retry_policy.max_retries == 3

        # Transient errors should respect max retries
        for attempt in range(5):
            should_retry = policy.should_retry(attempt, ErrorCategory.TRANSIENT)
            if attempt >= 3:
                assert should_retry is False
