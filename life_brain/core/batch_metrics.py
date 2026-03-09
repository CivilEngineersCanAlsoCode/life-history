"""
Batch Ingestion Metrics & Reporting — Comprehensive tracking and analysis.

Provides:
- Batch operation metrics and statistics
- Progress tracking for large ingestions
- Error summary and categorization
- Performance analytics (throughput, success rate)
- Report generation (text, JSON)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class BatchOperation:
    """Tracks a single batch ingestion operation."""

    batch_id: str
    total_documents: int
    start_ts: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    end_ts: Optional[str] = None
    successful: int = 0
    failed_first_try: int = 0
    deadlettered: int = 0
    in_retry_queue: int = 0
    errors_by_type: Dict[str, int] = field(default_factory=dict)
    duration_seconds: float = 0.0

    def complete(self):
        """Mark batch as complete and calculate duration."""
        self.end_ts = datetime.utcnow().isoformat()
        start = datetime.fromisoformat(self.start_ts)
        end = datetime.fromisoformat(self.end_ts)
        self.duration_seconds = (end - start).total_seconds()

    def add_error(self, error_type: str, count: int = 1):
        """Add error count for a given error type."""
        if error_type not in self.errors_by_type:
            self.errors_by_type[error_type] = 0
        self.errors_by_type[error_type] += count

    def get_success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.total_documents == 0:
            return 0.0
        return (self.successful / self.total_documents) * 100

    def get_throughput(self) -> float:
        """Get documents per second throughput."""
        if self.duration_seconds == 0:
            return 0.0
        return self.total_documents / self.duration_seconds

    def to_dict(self) -> Dict[str, Any]:
        """Export batch operation as dictionary."""
        return asdict(self)


@dataclass
class BatchMetrics:
    """Aggregated metrics for batch ingestion operations."""

    total_batches: int = 0
    total_documents: int = 0
    total_successful: int = 0
    total_deadlettered: int = 0
    total_in_retry: int = 0
    total_duration_seconds: float = 0.0
    batches: List[BatchOperation] = field(default_factory=list)
    error_summary: Dict[str, int] = field(default_factory=dict)

    def add_batch(self, batch: BatchOperation):
        """Add a completed batch operation."""
        self.batches.append(batch)
        self.total_batches += 1
        self.total_documents += batch.total_documents
        self.total_successful += batch.successful
        self.total_deadlettered += batch.deadlettered
        self.total_in_retry += batch.in_retry_queue
        self.total_duration_seconds += batch.duration_seconds

        # Merge error types
        for error_type, count in batch.errors_by_type.items():
            if error_type not in self.error_summary:
                self.error_summary[error_type] = 0
            self.error_summary[error_type] += count

    def get_overall_success_rate(self) -> float:
        """Get overall success rate as percentage."""
        if self.total_documents == 0:
            return 0.0
        return (self.total_successful / self.total_documents) * 100

    def get_overall_throughput(self) -> float:
        """Get average documents per second across all batches."""
        if self.total_duration_seconds == 0:
            return 0.0
        return self.total_documents / self.total_duration_seconds

    def get_most_common_error(self) -> Optional[str]:
        """Get the most common error type."""
        if not self.error_summary:
            return None
        return max(self.error_summary, key=self.error_summary.get)

    def to_dict(self) -> Dict[str, Any]:
        """Export metrics as dictionary."""
        return {
            "total_batches": self.total_batches,
            "total_documents": self.total_documents,
            "total_successful": self.total_successful,
            "total_deadlettered": self.total_deadlettered,
            "total_in_retry": self.total_in_retry,
            "total_duration_seconds": round(self.total_duration_seconds, 2),
            "overall_success_rate": round(self.get_overall_success_rate(), 2),
            "overall_throughput_docs_per_sec": round(self.get_overall_throughput(), 2),
            "error_summary": self.error_summary,
            "most_common_error": self.get_most_common_error(),
        }


class BatchProgressTracker:
    """Tracks progress of a batch ingestion in real-time."""

    def __init__(self, batch_id: str, total: int):
        """
        Initialize progress tracker.

        Args:
            batch_id: Unique batch identifier
            total: Total documents in batch
        """
        self.batch = BatchOperation(batch_id=batch_id, total_documents=total)
        self.processed = 0
        self.last_update_ts = datetime.utcnow()

    def record_success(self):
        """Record a successful ingestion."""
        self.batch.successful += 1
        self.processed += 1
        self._log_progress()

    def record_failed_first_try(self, error_type: str):
        """Record a failure on first attempt."""
        self.batch.failed_first_try += 1
        self.batch.add_error(error_type)
        self.processed += 1
        self._log_progress()

    def record_deadlettered(self, error_type: str):
        """Record a document moved to deadletter."""
        self.batch.deadlettered += 1
        self.batch.add_error(error_type)
        self.processed += 1
        self._log_progress()

    def record_retry_scheduled(self, error_type: str):
        """Record a document scheduled for retry."""
        self.batch.in_retry_queue += 1
        self.batch.add_error(error_type)
        self.processed += 1
        self._log_progress()

    def _log_progress(self):
        """Log progress at intervals (every 10% or 100 docs)."""
        should_log = False

        # Log every 10%
        if self.processed % max(1, self.batch.total_documents // 10) == 0:
            should_log = True

        # Log every 10 seconds
        if (datetime.utcnow() - self.last_update_ts).total_seconds() > 10:
            should_log = True

        if should_log:
            percent = (self.processed / self.batch.total_documents * 100) if self.batch.total_documents > 0 else 0
            logger.info(
                f"Batch {self.batch.batch_id} progress: {self.processed}/{self.batch.total_documents} "
                f"({percent:.1f}%) - Success: {self.batch.successful}, Retry: {self.batch.in_retry_queue}, "
                f"Deadletter: {self.batch.deadlettered}"
            )
            self.last_update_ts = datetime.utcnow()

    def complete(self) -> BatchOperation:
        """Complete batch and return operation stats."""
        self.batch.complete()
        logger.info(
            f"Batch {self.batch.batch_id} complete: "
            f"{self.batch.successful} successful, {self.batch.in_retry_queue} in retry, "
            f"{self.batch.deadlettered} deadlettered in {self.batch.duration_seconds:.2f}s"
        )
        return self.batch


class BatchReporter:
    """Generate reports from batch metrics."""

    @staticmethod
    def format_text_report(batch: BatchOperation) -> str:
        """
        Format batch operation as readable text report.

        Args:
            batch: Completed BatchOperation

        Returns:
            Formatted text report
        """
        report = f"""
╔═══════════════════════════════════════════════════════════════════╗
║                   BATCH INGESTION REPORT                          ║
╚═══════════════════════════════════════════════════════════════════╝

📊 Batch ID: {batch.batch_id}

⏱️ Duration: {batch.duration_seconds:.2f} seconds

📈 Results:
  ✓ Successful:        {batch.successful:6d} ({batch.get_success_rate():.1f}%)
  ⏳ In Retry Queue:   {batch.in_retry_queue:6d}
  ❌ Deadlettered:    {batch.deadlettered:6d}
  ─────────────────────────────────
  📊 Total:            {batch.total_documents:6d}

⚡ Throughput: {batch.get_throughput():.1f} docs/sec

❌ Errors by Type:
"""
        if batch.errors_by_type:
            for error_type, count in sorted(batch.errors_by_type.items(), key=lambda x: -x[1]):
                pct = (count / batch.total_documents * 100) if batch.total_documents > 0 else 0
                report += f"  • {error_type:<25} {count:6d} ({pct:5.1f}%)\n"
        else:
            report += "  (No errors)\n"

        report += f"""
⏰ Started: {batch.start_ts}
⏰ Ended:   {batch.end_ts}
"""
        return report.strip()

    @staticmethod
    def format_aggregate_report(metrics: BatchMetrics) -> str:
        """
        Format aggregate metrics as readable text report.

        Args:
            metrics: Aggregated BatchMetrics

        Returns:
            Formatted text report
        """
        report = f"""
╔═══════════════════════════════════════════════════════════════════╗
║                 AGGREGATE INGESTION REPORT                        ║
╚═══════════════════════════════════════════════════════════════════╝

📊 Overall Statistics:
  • Batches Processed:   {metrics.total_batches:6d}
  • Total Documents:     {metrics.total_documents:6d}
  • Total Duration:      {metrics.total_duration_seconds:6.1f} seconds

📈 Cumulative Results:
  ✓ Successful:          {metrics.total_successful:6d} ({metrics.get_overall_success_rate():.1f}%)
  ⏳ In Retry Queue:      {metrics.total_in_retry:6d}
  ❌ Deadlettered:       {metrics.total_deadlettered:6d}

⚡ Average Throughput: {metrics.get_overall_throughput():.1f} docs/sec

❌ Top Errors:
"""
        if metrics.error_summary:
            sorted_errors = sorted(metrics.error_summary.items(), key=lambda x: -x[1])[:5]
            for error_type, count in sorted_errors:
                pct = (count / metrics.total_documents * 100) if metrics.total_documents > 0 else 0
                report += f"  • {error_type:<25} {count:6d} ({pct:5.1f}%)\n"
        else:
            report += "  (No errors)\n"

        if metrics.batches:
            report += f"""
📋 Batches:
"""
            for batch in metrics.batches:
                report += f"  • {batch.batch_id:<20} {batch.successful:5d}/{batch.total_documents:5d} ({batch.get_success_rate():5.1f}%)\n"

        return report.strip()

    @staticmethod
    def export_json(batch: BatchOperation) -> str:
        """Export batch operation as JSON."""
        return json.dumps(batch.to_dict(), indent=2)

    @staticmethod
    def export_aggregate_json(metrics: BatchMetrics) -> str:
        """Export aggregate metrics as JSON."""
        return json.dumps(metrics.to_dict(), indent=2)


class ErrorSummary:
    """Analyze and summarize errors from batch operations."""

    def __init__(self):
        """Initialize error summary."""
        self.errors_by_type: Dict[str, int] = {}
        self.errors_by_doc_id: Dict[str, str] = {}
        self.recurring_patterns: Dict[str, List[str]] = {}

    def add_error(self, error_type: str, doc_id: str, error_message: str = ""):
        """Add an error to summary."""
        if error_type not in self.errors_by_type:
            self.errors_by_type[error_type] = 0
        self.errors_by_type[error_type] += 1

        self.errors_by_doc_id[doc_id] = error_type

        # Extract patterns (first 50 chars of error message)
        pattern = error_message[:50] if error_message else error_type
        if pattern not in self.recurring_patterns:
            self.recurring_patterns[pattern] = []
        self.recurring_patterns[pattern].append(doc_id)

    def get_top_errors(self, limit: int = 10) -> List[tuple]:
        """Get top N error types by frequency."""
        return sorted(self.errors_by_type.items(), key=lambda x: -x[1])[:limit]

    def get_recurring_patterns(self) -> Dict[str, int]:
        """Get error patterns with frequency."""
        return {pattern: len(docs) for pattern, docs in self.recurring_patterns.items()}

    def get_affected_documents(self, error_type: str) -> List[str]:
        """Get all documents affected by a specific error type."""
        return [doc_id for doc_id, err_type in self.errors_by_doc_id.items() if err_type == error_type]

    def format_summary(self) -> str:
        """Format error summary as readable text."""
        summary = f"""
╔═══════════════════════════════════════════════════════════════════╗
║                     ERROR SUMMARY                                 ║
╚═══════════════════════════════════════════════════════════════════╝

📊 Total Unique Errors: {len(self.errors_by_doc_id)}

🔴 Top Error Types:
"""
        for error_type, count in self.get_top_errors(10):
            pct = (count / len(self.errors_by_doc_id) * 100) if self.errors_by_doc_id else 0
            summary += f"  • {error_type:<30} {count:5d} ({pct:5.1f}%)\n"

        summary += f"""
🔍 Recurring Patterns:
"""
        patterns = self.get_recurring_patterns()
        for pattern, count in sorted(patterns.items(), key=lambda x: -x[1])[:5]:
            summary += f"  • [{count:3d}x] {pattern[:50]}...\n"

        return summary.strip()
