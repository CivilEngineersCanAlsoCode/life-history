"""
Retry Logic & Deadletter Queue — Resilient ChromaDB ingestion with recovery.

Implements:
- Exponential backoff retry policy
- Deadletter queue for permanent failures
- Ingestion retry wrapper
- Metrics tracking
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import time
from datetime import datetime, timedelta
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class RetryStatus(str, Enum):
    """Status of a retry attempt."""
    PENDING = "pending"
    RETRYING = "retrying"
    SUCCESS = "success"
    DEADLETTER = "deadletter"
    EXPIRED = "expired"


class FailureReason(str, Enum):
    """Categorization of failure reasons."""
    TRANSIENT = "transient"  # Network, timeout, connection issues
    VALIDATION = "validation"  # Data validation failed
    CONFLICT = "conflict"  # Truth engine conflict
    PERMANENT = "permanent"  # Other unrecoverable errors
    UNKNOWN = "unknown"


@dataclass
class RetryPolicy:
    """Configuration for retry behavior."""
    max_retries: int = 3
    initial_backoff_seconds: float = 1.0
    backoff_multiplier: float = 2.0  # Exponential: 1s, 2s, 4s, 8s...
    max_backoff_seconds: float = 60.0
    ttl_seconds: int = 86400  # 24 hours to retry before deadletter

    def get_backoff_seconds(self, attempt_number: int) -> float:
        """
        Calculate backoff time for attempt N.

        Exponential backoff with jitter.
        attempt_number: 0-indexed (0 = first retry after initial failure)
        """
        backoff = self.initial_backoff_seconds * (self.backoff_multiplier ** attempt_number)
        backoff = min(backoff, self.max_backoff_seconds)
        return backoff


@dataclass
class FailedIngestion:
    """A document that failed to ingest."""
    doc_id: str
    text: str
    metadata: Dict[str, Any]
    reason: FailureReason
    error_message: str
    retry_count: int = 0
    first_attempt_ts: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_attempt_ts: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: RetryStatus = RetryStatus.PENDING
    next_retry_ts: Optional[str] = None

    def should_retry(self, policy: RetryPolicy) -> bool:
        """Check if this document should be retried."""
        if self.status == RetryStatus.SUCCESS:
            return False
        if self.status == RetryStatus.DEADLETTER:
            return False
        if self.retry_count >= policy.max_retries:
            return False

        # Check TTL
        first_attempt = datetime.fromisoformat(self.first_attempt_ts)
        ttl_expired = datetime.utcnow() > first_attempt + timedelta(seconds=policy.ttl_seconds)
        if ttl_expired:
            self.status = RetryStatus.EXPIRED
            return False

        # Check if enough time has passed since last attempt
        if self.next_retry_ts:
            next_retry = datetime.fromisoformat(self.next_retry_ts)
            if datetime.utcnow() < next_retry:
                return False

        return True

    def mark_retry_scheduled(self, policy: RetryPolicy):
        """Schedule the next retry."""
        backoff = policy.get_backoff_seconds(self.retry_count)
        next_retry = datetime.utcnow() + timedelta(seconds=backoff)
        self.next_retry_ts = next_retry.isoformat()
        self.status = RetryStatus.RETRYING
        logger.debug(f"Retry scheduled for {self.doc_id} in {backoff}s")

    def mark_success(self):
        """Mark this ingestion as successful."""
        self.status = RetryStatus.SUCCESS
        self.last_attempt_ts = datetime.utcnow().isoformat()
        logger.info(f"Ingestion succeeded after {self.retry_count} retries: {self.doc_id}")

    def mark_deadletter(self):
        """Mark this ingestion as permanently failed (deadletter)."""
        self.status = RetryStatus.DEADLETTER
        self.last_attempt_ts = datetime.utcnow().isoformat()
        logger.error(
            f"Moved to deadletter after {self.retry_count} retries: {self.doc_id} "
            f"(reason: {self.reason.value})"
        )


class DeadletterQueue:
    """Queue for permanently failed ingestions."""

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize deadletter queue.

        Args:
            storage_path: Path to store deadletter JSON file. If None, stores in memory.
        """
        self.storage_path = storage_path
        self.deadletters: Dict[str, FailedIngestion] = {}
        self._load_from_disk()

    def _load_from_disk(self):
        """Load deadletter queue from disk if storage_path exists."""
        if not self.storage_path:
            return

        path = Path(self.storage_path)
        if path.exists():
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    for doc_id, entry in data.items():
                        self.deadletters[doc_id] = FailedIngestion(**entry)
                logger.info(f"Loaded {len(self.deadletters)} deadletters from {self.storage_path}")
            except Exception as e:
                logger.error(f"Failed to load deadletter queue from {self.storage_path}: {e}")

    def _save_to_disk(self):
        """Save deadletter queue to disk."""
        if not self.storage_path:
            return

        try:
            path = Path(self.storage_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w') as f:
                data = {doc_id: asdict(entry) for doc_id, entry in self.deadletters.items()}
                json.dump(data, f, indent=2)
            logger.debug(f"Saved {len(self.deadletters)} deadletters to {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to save deadletter queue: {e}")

    def add(self, failed_ingestion: FailedIngestion):
        """Add a failed ingestion to the deadletter queue."""
        failed_ingestion.mark_deadletter()
        self.deadletters[failed_ingestion.doc_id] = failed_ingestion
        self._save_to_disk()

    def get(self, doc_id: str) -> Optional[FailedIngestion]:
        """Get a specific deadletter entry."""
        return self.deadletters.get(doc_id)

    def list_all(self, filter_reason: Optional[FailureReason] = None) -> List[FailedIngestion]:
        """List all deadletters, optionally filtered by reason."""
        if filter_reason:
            return [d for d in self.deadletters.values() if d.reason == filter_reason]
        return list(self.deadletters.values())

    def get_by_reason(self) -> Dict[str, List[FailedIngestion]]:
        """Group deadletters by failure reason."""
        grouped = {}
        for deadletter in self.deadletters.values():
            reason = deadletter.reason.value
            if reason not in grouped:
                grouped[reason] = []
            grouped[reason].append(deadletter)
        return grouped

    def retry_manual(self, doc_id: str, callback) -> bool:
        """
        Manually retry a deadlettered document.

        Args:
            doc_id: Document ID to retry
            callback: Function to call to retry ingestion

        Returns:
            True if retry succeeded, False otherwise
        """
        if doc_id not in self.deadletters:
            logger.warning(f"Document not in deadletter queue: {doc_id}")
            return False

        failed = self.deadletters[doc_id]
        try:
            callback(failed.doc_id, failed.text, failed.metadata)
            # If callback succeeded, remove from deadletter
            del self.deadletters[doc_id]
            self._save_to_disk()
            logger.info(f"Manual retry succeeded for {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Manual retry failed for {doc_id}: {e}")
            return False

    def stats(self) -> Dict[str, Any]:
        """Get deadletter queue statistics."""
        by_reason = self.get_by_reason()
        return {
            "total_deadletters": len(self.deadletters),
            "by_reason": {reason: len(entries) for reason, entries in by_reason.items()},
            "oldest_entry_ts": min(
                (d.first_attempt_ts for d in self.deadletters.values()),
                default=None
            ),
            "newest_entry_ts": max(
                (d.last_attempt_ts for d in self.deadletters.values()),
                default=None
            ),
        }


class RetryQueue:
    """Queue for documents waiting to be retried."""

    def __init__(self, policy: RetryPolicy):
        """Initialize retry queue with policy."""
        self.policy = policy
        self.pending: Dict[str, FailedIngestion] = {}
        self.deadletter_queue: Optional[DeadletterQueue] = None

    def set_deadletter_queue(self, dlq: DeadletterQueue):
        """Link a deadletter queue for permanent failures."""
        self.deadletter_queue = dlq

    def add(self, failed_ingestion: FailedIngestion):
        """Add a failed ingestion to retry queue."""
        failed_ingestion.retry_count += 1
        failed_ingestion.last_attempt_ts = datetime.utcnow().isoformat()

        if failed_ingestion.retry_count >= self.policy.max_retries:
            # Move to deadletter
            if self.deadletter_queue:
                self.deadletter_queue.add(failed_ingestion)
            else:
                failed_ingestion.mark_deadletter()
            logger.warning(f"Document exceeded max retries, moved to deadletter: {failed_ingestion.doc_id}")
        else:
            # Schedule retry
            failed_ingestion.mark_retry_scheduled(self.policy)
            self.pending[failed_ingestion.doc_id] = failed_ingestion
            logger.info(f"Document queued for retry: {failed_ingestion.doc_id} (attempt {failed_ingestion.retry_count}/{self.policy.max_retries})")

    def get_ready_to_retry(self) -> List[FailedIngestion]:
        """Get all documents ready to retry now."""
        ready = [d for d in self.pending.values() if not d.should_retry(self.policy)]
        return ready

    def get_pending_count(self) -> int:
        """Get count of pending retries."""
        return len(self.pending)

    def remove(self, doc_id: str):
        """Remove a document from retry queue (e.g., after successful retry)."""
        if doc_id in self.pending:
            del self.pending[doc_id]

    def stats(self) -> Dict[str, Any]:
        """Get retry queue statistics."""
        ready = len(self.get_ready_to_retry())
        return {
            "total_pending": len(self.pending),
            "ready_to_retry": ready,
            "waiting": len(self.pending) - ready,
            "policy_max_retries": self.policy.max_retries,
            "policy_ttl_seconds": self.policy.ttl_seconds,
        }


@dataclass
class IngestionMetrics:
    """Track ingestion metrics for monitoring."""
    total_attempts: int = 0
    successful_first_try: int = 0
    successful_with_retries: int = 0
    failed_permanent: int = 0
    total_retry_attempts: int = 0
    avg_retries_per_success: float = 0.0

    def update(self, success: bool, retry_count: int):
        """Update metrics after an ingestion attempt."""
        self.total_attempts += 1

        if success:
            if retry_count == 0:
                self.successful_first_try += 1
            else:
                self.successful_with_retries += 1
                self.total_retry_attempts += retry_count
                self.avg_retries_per_success = (
                    self.total_retry_attempts / self.successful_with_retries
                )
        else:
            self.failed_permanent += 1

    def to_dict(self) -> Dict[str, Any]:
        """Export metrics as dictionary."""
        success_rate = (
            (self.successful_first_try + self.successful_with_retries)
            / self.total_attempts
            * 100
            if self.total_attempts > 0
            else 0
        )
        return {
            "total_attempts": self.total_attempts,
            "successful_first_try": self.successful_first_try,
            "successful_with_retries": self.successful_with_retries,
            "failed_permanent": self.failed_permanent,
            "total_retry_attempts": self.total_retry_attempts,
            "avg_retries_per_success": round(self.avg_retries_per_success, 2),
            "success_rate_percent": round(success_rate, 2),
        }


def categorize_error(error: Exception) -> Tuple[FailureReason, str]:
    """
    Categorize an error to determine if it's retryable.

    Returns:
        Tuple of (FailureReason, error_message)
    """
    error_str = str(error).lower()
    error_type = type(error).__name__

    # Transient errors (retryable)
    # Check error type name first (for TimeoutError, ConnectionError, etc.)
    if error_type in ["TimeoutError", "ConnectionError", "BrokenPipeError", "ConnectionResetError"]:
        return (FailureReason.TRANSIENT, str(error))

    if any(x in error_str for x in ["timeout", "connection", "network", "broken pipe", "connection reset"]):
        return (FailureReason.TRANSIENT, str(error))

    if any(x in error_str for x in ["try again", "temporarily unavailable", "busy"]):
        return (FailureReason.TRANSIENT, str(error))

    # Validation errors (not retryable)
    if "validation" in error_str or error_type == "ValueError":
        return (FailureReason.VALIDATION, str(error))

    # Conflict errors (not retryable)
    if "conflict" in error_str:
        return (FailureReason.CONFLICT, str(error))

    # Default to permanent
    return (FailureReason.PERMANENT, str(error))


def create_failed_ingestion(
    doc_id: str,
    text: str,
    metadata: Dict[str, Any],
    error: Exception
) -> FailedIngestion:
    """
    Create a FailedIngestion record from an error.

    Args:
        doc_id: Document ID that failed
        text: Document text
        metadata: Document metadata
        error: Exception that was raised

    Returns:
        FailedIngestion object
    """
    reason, error_msg = categorize_error(error)
    return FailedIngestion(
        doc_id=doc_id,
        text=text,
        metadata=metadata,
        reason=reason,
        error_message=error_msg
    )
