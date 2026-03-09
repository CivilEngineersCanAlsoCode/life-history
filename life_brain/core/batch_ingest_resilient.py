"""
Resilient batch ingestion with exponential backoff.

Provides batch ingestion with:
- Exponential backoff retry (1s, 2s, 4s, 8s, max 60s)
- Transient vs permanent error classification
- Deadletter queue for unrecoverable failures
- Progress tracking and metrics
"""

from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import time

from life_brain.core.retry_manager import (
    RetryPolicy,
    FailedIngestion,
    FailureReason,
    RetryStatus,
    DeadletterQueue,
)

logger = logging.getLogger(__name__)


@dataclass
class IngestResult:
    """Result of a single ingestion attempt."""

    doc_id: str
    success: bool
    error_message: Optional[str] = None
    retry_count: int = 0
    total_duration_seconds: float = 0.0
    failure_reason: Optional[FailureReason] = None


@dataclass
class BatchIngestResult:
    """Result of batch ingestion."""

    total_documents: int
    successful: int
    deadlettered: int
    in_retry_queue: int
    results: List[IngestResult] = field(default_factory=list)
    duration_seconds: float = 0.0

    def get_success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.total_documents == 0:
            return 0.0
        return (self.successful / self.total_documents) * 100


def classify_error(error: Exception) -> FailureReason:
    """Classify error as transient or permanent.

    Args:
        error: Exception to classify

    Returns:
        FailureReason enum value
    """
    error_str = str(error).lower()
    error_type = type(error).__name__

    # Transient errors - can retry
    transient_keywords = [
        "timeout",
        "connection",
        "network",
        "unavailable",
        "temporarily",
        "connrefused",
        "broken pipe",
    ]
    for keyword in transient_keywords:
        if keyword in error_str:
            return FailureReason.TRANSIENT

    # Validation errors - cannot retry
    if "validation" in error_type.lower() or "schema" in error_str:
        return FailureReason.VALIDATION

    # Conflict errors - special handling
    if "conflict" in error_type.lower() or "conflict" in error_str:
        return FailureReason.CONFLICT

    # Default to permanent
    return FailureReason.PERMANENT


class BatchIngestResilient:
    """Resilient batch ingestion with exponential backoff."""

    def __init__(
        self,
        ingest_function: Callable[[str, Dict[str, Any]], bool],
        retry_policy: Optional[RetryPolicy] = None,
        deadletter_path: Optional[str] = None,
    ):
        """Initialize resilient batch ingester.

        Args:
            ingest_function: Function(doc_id, metadata) -> bool that ingests a document
            retry_policy: Custom retry policy (uses defaults if None)
            deadletter_path: Path to store deadletter queue
        """
        self.ingest_function = ingest_function
        self.retry_policy = retry_policy or RetryPolicy(
            max_retries=3,
            initial_backoff_seconds=1.0,
            backoff_multiplier=2.0,
            max_backoff_seconds=60.0,
        )
        self.deadletter_queue = DeadletterQueue(deadletter_path)
        self.retry_queue: Dict[str, FailedIngestion] = {}

    def ingest_document(
        self, doc_id: str, metadata: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """Attempt to ingest a single document.

        Args:
            doc_id: Document ID
            metadata: Document metadata

        Returns:
            (success: bool, error_message: str or None)
        """
        try:
            result = self.ingest_function(doc_id, metadata)
            if result:
                return True, None
            else:
                return False, "Ingestion function returned False"
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Ingestion failed for {doc_id}: {error_msg}")
            return False, error_msg

    def ingest_batch_with_retries(
        self, documents: List[Dict[str, Any]]
    ) -> BatchIngestResult:
        """Ingest a batch of documents with exponential backoff retries.

        Args:
            documents: List of dicts with 'doc_id' and 'metadata' keys

        Returns:
            BatchIngestResult with statistics
        """
        start_time = time.time()
        result = BatchIngestResult(
            total_documents=len(documents),
            successful=0,
            deadlettered=0,
            in_retry_queue=0,
        )

        # First attempt - try all documents
        for doc in documents:
            doc_id = doc.get("doc_id")
            metadata = doc.get("metadata", {})

            success, error = self.ingest_document(doc_id, metadata)

            if success:
                result.successful += 1
                result.results.append(IngestResult(doc_id=doc_id, success=True))
            else:
                # Classify error
                error_reason = FailureReason.UNKNOWN
                if error:
                    try:
                        error_obj = Exception(error)
                        error_reason = classify_error(error_obj)
                    except:
                        error_reason = FailureReason.UNKNOWN

                # Add to retry queue if transient
                if error_reason == FailureReason.TRANSIENT:
                    failed = FailedIngestion(
                        doc_id=doc_id,
                        text="",  # Text not needed for metadata
                        metadata=metadata,
                        reason=error_reason,
                        error_message=error or "Unknown error",
                    )
                    self.retry_queue[doc_id] = failed
                    result.in_retry_queue += 1
                else:
                    # Permanent failure - deadletter
                    failed = FailedIngestion(
                        doc_id=doc_id,
                        text="",
                        metadata=metadata,
                        reason=error_reason,
                        error_message=error or "Unknown error",
                    )
                    failed.mark_deadletter()
                    self.deadletter_queue.deadletters[doc_id] = failed
                    result.deadlettered += 1

                result.results.append(
                    IngestResult(
                        doc_id=doc_id,
                        success=False,
                        error_message=error,
                        failure_reason=error_reason,
                    )
                )

        # Retry loop with exponential backoff
        retry_count = 0
        while self.retry_queue and retry_count < self.retry_policy.max_retries:
            retry_count += 1
            docs_to_retry = list(self.retry_queue.values())

            # Wait for backoff
            if retry_count > 1:
                backoff = self.retry_policy.get_backoff_seconds(retry_count - 1)
                backoff = min(backoff, 60.0)  # Cap at 60 seconds
                logger.info(f"Retry attempt {retry_count}: waiting {backoff}s before retrying...")
                time.sleep(backoff)

            # Retry documents
            for failed in docs_to_retry:
                if not failed.should_retry(self.retry_policy):
                    # Move to deadletter if TTL expired
                    if failed.status == RetryStatus.EXPIRED:
                        failed.mark_deadletter()
                        self.deadletter_queue.deadletters[failed.doc_id] = failed
                        del self.retry_queue[failed.doc_id]
                        result.deadlettered += 1
                        result.in_retry_queue -= 1
                    continue

                # Attempt retry
                success, error = self.ingest_document(failed.doc_id, failed.metadata)

                if success:
                    failed.mark_success()
                    result.successful += 1
                    result.in_retry_queue -= 1
                    del self.retry_queue[failed.doc_id]
                    logger.info(
                        f"Retry succeeded for {failed.doc_id} after {retry_count} attempts"
                    )
                else:
                    # Still failing - schedule next retry
                    failed.retry_count += 1
                    failed.mark_retry_scheduled(self.retry_policy)
                    logger.warning(
                        f"Retry {retry_count} failed for {failed.doc_id}: {error}"
                    )

        # Move any remaining retries to deadletter
        for doc_id, failed in list(self.retry_queue.items()):
            failed.mark_deadletter()
            self.deadletter_queue.deadletters[doc_id] = failed
            result.deadlettered += 1
            result.in_retry_queue -= 1

        result.duration_seconds = time.time() - start_time
        return result

    def get_deadletter_documents(self) -> List[str]:
        """Get list of document IDs in deadletter queue.

        Returns:
            List of deadlettered doc_ids
        """
        return list(self.deadletter_queue.deadletters.keys())

    def retry_deadletter_document(self, doc_id: str) -> Tuple[bool, Optional[str]]:
        """Manually retry a deadlettered document.

        Args:
            doc_id: Document ID to retry

        Returns:
            (success: bool, error_message: str or None)
        """
        if doc_id not in self.deadletter_queue.deadletters:
            return False, "Document not in deadletter queue"

        failed = self.deadletter_queue.deadletters[doc_id]
        success, error = self.ingest_document(doc_id, failed.metadata)

        if success:
            failed.mark_success()
            del self.deadletter_queue.deadletters[doc_id]
            return True, None
        else:
            return False, error

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about ingestion state.

        Returns:
            Dictionary with statistics
        """
        total_deadlettered = len(self.deadletter_queue.deadletters)
        total_in_retry = len(self.retry_queue)

        return {
            "total_deadlettered": total_deadlettered,
            "total_in_retry_queue": total_in_retry,
            "deadletter_docs": list(self.deadletter_queue.deadletters.keys()),
            "retry_queue_docs": list(self.retry_queue.keys()),
        }
