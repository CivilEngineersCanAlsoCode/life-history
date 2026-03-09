"""
Ingestion Wrapper — Resilient document ingestion with retry logic.

Wraps the core ingestion pipeline with:
- Automatic retry on transient failures
- Error categorization and routing to deadletter queue
- Metrics tracking
- Graceful degradation
"""

from typing import Dict, Any, List, Optional, Callable
import logging
import time
import chromadb

from life_brain.core.ingestion import add_to_life_brain, QAPair, batch_ingest
from life_brain.core.retry_manager import (
    RetryPolicy,
    RetryQueue,
    DeadletterQueue,
    IngestionMetrics,
    FailedIngestion,
    create_failed_ingestion,
    categorize_error,
)

logger = logging.getLogger(__name__)


class ResilientIngestion:
    """
    Resilient ingestion wrapper with automatic retry and deadletter handling.
    """

    def __init__(
        self,
        collection: chromadb.Collection,
        policy: Optional[RetryPolicy] = None,
        deadletter_path: Optional[str] = None,
    ):
        """
        Initialize resilient ingestion.

        Args:
            collection: ChromaDB collection to ingest into
            policy: RetryPolicy configuration (uses defaults if None)
            deadletter_path: Path to persist deadletter queue (JSON file)
        """
        self.collection = collection
        self.policy = policy or RetryPolicy()
        self.deadletter_queue = DeadletterQueue(storage_path=deadletter_path)
        self.retry_queue = RetryQueue(policy=self.policy)
        self.retry_queue.set_deadletter_queue(self.deadletter_queue)
        self.metrics = IngestionMetrics()

    def ingest_with_retry(
        self,
        doc_id: str,
        text: str,
        metadata: Dict[str, Any],
        manual_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Attempt to ingest a document with automatic retry on transient failures.

        Args:
            doc_id: Unique document identifier
            text: Document text content
            metadata: 47-field metadata dict
            manual_callback: Optional callback for manual retries (for deadletters)

        Returns:
            Dict with:
            - status: "success", "retry_scheduled", "deadletter", "validation_error"
            - doc_id: The document ID
            - message: Status message
            - retry_count: Number of retries attempted
            - reason: Failure reason if applicable
        """
        try:
            # Attempt initial ingestion
            doc_id_result = add_to_life_brain(
                collection=self.collection,
                doc_id=doc_id,
                text=text,
                metadata=metadata,
            )

            # Success on first try
            self.metrics.update(success=True, retry_count=0)
            logger.info(f"Successfully ingested (first try): {doc_id}")

            return {
                "status": "success",
                "doc_id": doc_id_result,
                "message": "Document ingested successfully",
                "retry_count": 0,
            }

        except Exception as error:
            # Categorize error to determine handling
            reason, error_msg = categorize_error(error)

            logger.warning(
                f"Ingestion failed for {doc_id}: {reason.value} — {error_msg}"
            )

            # Create failed ingestion record
            failed = create_failed_ingestion(doc_id, text, metadata, error)

            # Route based on error category
            if reason.value == "transient":
                # Schedule for retry
                self.retry_queue.add(failed)
                return {
                    "status": "retry_scheduled",
                    "doc_id": doc_id,
                    "message": f"Transient failure. Retry scheduled in {self.policy.get_backoff_seconds(0)}s",
                    "retry_count": 1,
                    "reason": reason.value,
                }

            elif reason.value in ["validation", "conflict"]:
                # Non-retryable - move to deadletter immediately
                self.deadletter_queue.add(failed)
                self.metrics.update(success=False, retry_count=0)
                return {
                    "status": "deadletter",
                    "doc_id": doc_id,
                    "message": f"Non-retryable error: {reason.value}. Moved to deadletter queue.",
                    "retry_count": 0,
                    "reason": reason.value,
                }

            else:
                # Unknown error - attempt retry anyway
                self.retry_queue.add(failed)
                return {
                    "status": "retry_scheduled",
                    "doc_id": doc_id,
                    "message": "Unknown error. Retrying...",
                    "retry_count": 1,
                    "reason": reason.value,
                }

    def process_retry_queue(self) -> Dict[str, Any]:
        """
        Process documents ready to retry.

        Checks retry queue for documents that are ready to retry based on backoff timing.

        Returns:
            Dict with:
            - retried: Number of documents retried
            - successful: Number of successful retries
            - failed_again: Number of failed retries (moved to deadletter)
            - still_waiting: Number still waiting for retry window
        """
        ready_documents = self.retry_queue.get_ready_to_retry()

        if not ready_documents:
            return {
                "retried": 0,
                "successful": 0,
                "failed_again": 0,
                "still_waiting": 0,
            }

        retried = 0
        successful = 0
        failed_again = 0

        for failed in ready_documents:
            retried += 1
            logger.info(
                f"Retrying document: {failed.doc_id} "
                f"(attempt {failed.retry_count + 1}/{self.policy.max_retries})"
            )

            try:
                # Attempt retry
                doc_id_result = add_to_life_brain(
                    collection=self.collection,
                    doc_id=failed.doc_id,
                    text=failed.text,
                    metadata=failed.metadata,
                )

                # Success
                failed.mark_success()
                self.retry_queue.remove(failed.doc_id)
                successful += 1
                self.metrics.update(success=True, retry_count=failed.retry_count)
                logger.info(f"Retry succeeded: {failed.doc_id}")

            except Exception as error:
                # Retry failed
                reason, error_msg = categorize_error(error)
                logger.warning(f"Retry failed for {failed.doc_id}: {reason.value}")

                # Update failed record
                failed.error_message = error_msg
                failed.reason = reason

                # Add back to retry queue
                self.retry_queue.add(failed)
                failed_again += 1

        still_waiting = self.retry_queue.get_pending_count()

        logger.info(
            f"Retry processing complete: {successful}/{retried} succeeded, "
            f"{failed_again} failed again, {still_waiting} still waiting"
        )

        return {
            "retried": retried,
            "successful": successful,
            "failed_again": failed_again,
            "still_waiting": still_waiting,
        }

    def batch_ingest_resilient(
        self, pairs: List[QAPair]
    ) -> Dict[str, Any]:
        """
        Batch ingest multiple Q&A pairs with resilience.

        Args:
            pairs: List of QAPair objects

        Returns:
            Dict with:
            - total: Total documents processed
            - inserted_first_try: Successfully inserted on first attempt
            - retry_scheduled: Scheduled for retry
            - deadlettered: Moved to deadletter immediately
            - metrics: Overall metrics
        """
        inserted_first_try = []
        retry_scheduled = []
        deadlettered = []

        for pair in pairs:
            text = f"Q: {pair.question}\nA: {pair.answer}"
            result = self.ingest_with_retry(
                doc_id=pair.doc_id, text=text, metadata=pair.metadata
            )

            if result["status"] == "success":
                inserted_first_try.append(pair.doc_id)
            elif result["status"] == "retry_scheduled":
                retry_scheduled.append(pair.doc_id)
            elif result["status"] == "deadletter":
                deadlettered.append(pair.doc_id)

        return {
            "total": len(pairs),
            "inserted_first_try": len(inserted_first_try),
            "retry_scheduled": len(retry_scheduled),
            "deadlettered": len(deadlettered),
            "details": {
                "inserted": inserted_first_try,
                "retrying": retry_scheduled,
                "deadlettered": deadlettered,
            },
            "metrics": self.get_metrics(),
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get current ingestion metrics."""
        return {
            "ingestion": self.metrics.to_dict(),
            "retry_queue": self.retry_queue.stats(),
            "deadletter_queue": self.deadletter_queue.stats(),
        }

    def get_deadletters(
        self, reason: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get deadletter entries.

        Args:
            reason: Optional filter by reason ("transient", "validation", "conflict", "permanent")

        Returns:
            List of deadletter entries as dicts
        """
        from life_brain.core.retry_manager import FailureReason

        if reason:
            try:
                reason_enum = FailureReason[reason.upper()]
                deadletters = self.deadletter_queue.list_all(filter_reason=reason_enum)
            except KeyError:
                logger.warning(f"Unknown failure reason: {reason}")
                deadletters = []
        else:
            deadletters = self.deadletter_queue.list_all()

        return [
            {
                "doc_id": d.doc_id,
                "reason": d.reason.value,
                "error": d.error_message,
                "retry_count": d.retry_count,
                "first_attempt": d.first_attempt_ts,
                "last_attempt": d.last_attempt_ts,
            }
            for d in deadletters
        ]

    def retry_deadletter_manual(self, doc_id: str) -> bool:
        """
        Attempt manual retry of a deadlettered document.

        Args:
            doc_id: Document ID in deadletter queue

        Returns:
            True if retry succeeded, False otherwise
        """

        def callback(doc_id, text, metadata):
            add_to_life_brain(
                collection=self.collection,
                doc_id=doc_id,
                text=text,
                metadata=metadata,
            )

        success = self.deadletter_queue.retry_manual(doc_id, callback)
        if success:
            self.metrics.update(success=True, retry_count=0)
        return success
