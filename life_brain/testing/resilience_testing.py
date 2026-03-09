"""
Resilience testing — validate retry logic and deadletter queue handling.

Provides:
- Retry mechanism validation (exponential backoff)
- Deadletter queue functionality testing
- Transient error recovery
- Max retry enforcement
- Failure categorization
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ErrorCategory(Enum):
    """Categories of errors."""
    TRANSIENT = "transient"  # Network, timeout - retry candidate
    VALIDATION = "validation"  # Invalid data - not retryable
    CONFLICT = "conflict"  # Data conflict - manual review needed
    SYSTEM = "system"  # System error - non-retryable


@dataclass
class RetryAttempt:
    """Single retry attempt."""
    attempt_number: int
    backoff_seconds: float
    error: str
    success: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DeadletterEntry:
    """Entry in deadletter queue."""
    doc_id: str
    document: Dict[str, Any]
    error_category: ErrorCategory
    error_message: str
    final_error: str
    max_retries_exceeded: bool
    attempts: List[RetryAttempt] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ResilienceTestResult:
    """Result from resilience test."""
    total_documents: int
    successful: int
    retried: int
    deadlettered: int
    max_retries_exceeded: int
    duration_seconds: float
    avg_retry_count: float
    transient_errors: int
    validation_errors: int
    conflict_errors: int
    system_errors: int
    deadletter_entries: List[DeadletterEntry] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_documents == 0:
            return 0.0
        return round(self.successful / self.total_documents * 100, 2)

    @property
    def deadletter_rate(self) -> float:
        """Calculate deadletter rate."""
        if self.total_documents == 0:
            return 0.0
        return round(self.deadlettered / self.total_documents * 100, 2)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_documents": self.total_documents,
            "successful": self.successful,
            "retried": self.retried,
            "deadlettered": self.deadlettered,
            "success_rate": self.success_rate,
            "deadletter_rate": self.deadletter_rate,
            "max_retries_exceeded": self.max_retries_exceeded,
            "avg_retry_count": round(self.avg_retry_count, 2),
            "error_breakdown": {
                "transient": self.transient_errors,
                "validation": self.validation_errors,
                "conflict": self.conflict_errors,
                "system": self.system_errors,
            },
        }


class RetryPolicy:
    """Exponential backoff retry policy."""

    def __init__(
        self,
        max_retries: int = 3,
        initial_backoff: float = 1.0,
        max_backoff: float = 60.0,
        multiplier: float = 2.0,
    ):
        """
        Initialize retry policy.

        Args:
            max_retries: Maximum number of retries
            initial_backoff: Initial backoff in seconds
            max_backoff: Maximum backoff in seconds
            multiplier: Backoff multiplier per attempt
        """
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.max_backoff = max_backoff
        self.multiplier = multiplier

    def get_backoff(self, attempt: int) -> float:
        """
        Get backoff time for attempt.

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            Backoff time in seconds
        """
        backoff = self.initial_backoff * (self.multiplier ** attempt)
        return min(backoff, self.max_backoff)

    def should_retry(self, attempt: int, error_category: ErrorCategory) -> bool:
        """
        Determine if should retry.

        Args:
            attempt: Attempt number (0-indexed)
            error_category: Category of error

        Returns:
            True if should retry
        """
        # Only retry transient errors
        if error_category != ErrorCategory.TRANSIENT:
            return False

        # Check max retries
        return attempt < self.max_retries


class ResilienceTest:
    """Test resilience mechanisms (retries, deadletter queue)."""

    def __init__(
        self,
        ingestion_manager: Any,
        retry_policy: Optional[RetryPolicy] = None,
    ):
        """Initialize resilience test."""
        self.manager = ingestion_manager
        self.retry_policy = retry_policy or RetryPolicy()
        self.deadletter_queue: List[DeadletterEntry] = []

    def categorize_error(self, error: str) -> ErrorCategory:
        """
        Categorize error for retry decision.

        Args:
            error: Error message

        Returns:
            ErrorCategory
        """
        error_lower = error.lower()

        if any(x in error_lower for x in ["timeout", "connection", "network", "temporarily"]):
            return ErrorCategory.TRANSIENT
        elif any(x in error_lower for x in ["validation", "invalid", "schema", "format"]):
            return ErrorCategory.VALIDATION
        elif any(x in error_lower for x in ["conflict", "duplicate", "exists"]):
            return ErrorCategory.CONFLICT
        else:
            return ErrorCategory.SYSTEM

    def ingest_with_retry(
        self,
        document: Dict[str, Any],
        attempt: int = 0,
    ) -> bool:
        """
        Ingest document with retry logic.

        Args:
            document: Document to ingest
            attempt: Current attempt number

        Returns:
            True if successful
        """
        try:
            result = self.manager.ingest_documents([document])
            if hasattr(result, 'success_count') and result.success_count > 0:
                return True

            # Check for errors to decide on retry
            return False

        except Exception as e:
            error_message = str(e)
            error_category = self.categorize_error(error_message)

            # Decide if should retry
            if self.retry_policy.should_retry(attempt, error_category):
                # Would normally wait before retry
                backoff = self.retry_policy.get_backoff(attempt)

                # Attempt retry
                return self.ingest_with_retry(document, attempt + 1)
            else:
                # Add to deadletter queue
                entry = DeadletterEntry(
                    doc_id=document.get("id", f"unknown_{attempt}"),
                    document=document,
                    error_category=error_category,
                    error_message=error_message,
                    final_error=error_message,
                    max_retries_exceeded=(
                        attempt >= self.retry_policy.max_retries
                        if error_category == ErrorCategory.TRANSIENT
                        else False
                    ),
                )
                self.deadletter_queue.append(entry)
                return False

    def run_resilience_test(
        self,
        documents: List[Dict[str, Any]],
    ) -> ResilienceTestResult:
        """
        Run resilience test on batch of documents.

        Args:
            documents: Documents to test

        Returns:
            ResilienceTestResult with metrics
        """
        import time
        start_time = time.time()

        successful = 0
        retried = 0
        deadlettered = 0
        max_retries_exceeded = 0

        for doc in documents:
            success = self.ingest_with_retry(doc)
            if success:
                successful += 1
            else:
                deadlettered += 1

        duration = time.time() - start_time

        # Calculate average retry count (estimate)
        total_attempts = len(documents) + sum(
            len(entry.attempts) for entry in self.deadletter_queue
        )
        avg_retries = total_attempts / max(len(documents), 1) - 1

        # Count errors by category
        transient_errors = sum(
            1 for e in self.deadletter_queue
            if e.error_category == ErrorCategory.TRANSIENT
        )
        validation_errors = sum(
            1 for e in self.deadletter_queue
            if e.error_category == ErrorCategory.VALIDATION
        )
        conflict_errors = sum(
            1 for e in self.deadletter_queue
            if e.error_category == ErrorCategory.CONFLICT
        )
        system_errors = sum(
            1 for e in self.deadletter_queue
            if e.error_category == ErrorCategory.SYSTEM
        )

        result = ResilienceTestResult(
            total_documents=len(documents),
            successful=successful,
            retried=retried,
            deadlettered=deadlettered,
            max_retries_exceeded=max_retries_exceeded,
            duration_seconds=duration,
            avg_retry_count=avg_retries,
            transient_errors=transient_errors,
            validation_errors=validation_errors,
            conflict_errors=conflict_errors,
            system_errors=system_errors,
            deadletter_entries=self.deadletter_queue,
        )

        return result

    def generate_report(self, result: ResilienceTestResult) -> str:
        """Generate resilience test report."""
        lines = [
            "=" * 80,
            "RESILIENCE & DEADLETTER QUEUE TEST REPORT",
            "=" * 80,
            "",
            f"Timestamp: {datetime.now().isoformat()}",
            "",
            "SUMMARY",
            "-" * 80,
            f"Total Documents: {result.total_documents}",
            f"Successful: {result.successful} ({result.success_rate}%)",
            f"Deadlettered: {result.deadlettered} ({result.deadletter_rate}%)",
            f"Duration: {result.duration_seconds:.2f} seconds",
            "",
            "ERROR BREAKDOWN",
            "-" * 80,
            f"Transient Errors (retryable): {result.transient_errors}",
            f"Validation Errors: {result.validation_errors}",
            f"Conflict Errors: {result.conflict_errors}",
            f"System Errors: {result.system_errors}",
            "",
            "DEADLETTER QUEUE",
            "-" * 80,
            f"Total Entries: {len(result.deadletter_entries)}",
            f"Max Retries Exceeded: {result.max_retries_exceeded}",
        ]

        if result.deadletter_entries:
            lines.extend([
                "",
                "DEADLETTER DETAILS",
                "-" * 80,
            ])
            for entry in result.deadletter_entries[:10]:  # Show first 10
                lines.extend([
                    f"\nDoc ID: {entry.doc_id}",
                    f"  Category: {entry.error_category.value}",
                    f"  Error: {entry.error_message[:60]}...",
                    f"  Max Retries Exceeded: {entry.max_retries_exceeded}",
                ])

        lines.extend([
            "",
            "=" * 80,
        ])

        return "\n".join(lines)
