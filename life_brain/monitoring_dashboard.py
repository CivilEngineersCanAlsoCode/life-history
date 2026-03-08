"""
Monitoring dashboard for Life Brain — batch metrics, error summaries, success rates.

Provides:
- Real-time batch operation tracking
- Error categorization and summary
- Success rate calculations
- Performance trending
- Dashboard visualization
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json


class MetricType(Enum):
    """Types of metrics."""
    THROUGHPUT = "throughput"  # docs/sec
    LATENCY = "latency"  # milliseconds
    SUCCESS_RATE = "success_rate"  # percentage
    ERROR_RATE = "error_rate"  # percentage
    MEMORY_USAGE = "memory_usage"  # megabytes


@dataclass
class BatchMetric:
    """Single batch operation metric."""
    batch_id: str
    operation: str
    start_time: str
    end_time: str
    total_docs: int
    successful_docs: int
    failed_docs: int
    errors: Dict[str, int] = field(default_factory=dict)
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "batch_id": self.batch_id,
            "operation": self.operation,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_docs": self.total_docs,
            "successful_docs": self.successful_docs,
            "failed_docs": self.failed_docs,
            "success_rate": round(self.successful_docs / max(self.total_docs, 1) * 100, 2),
            "error_rate": round(self.failed_docs / max(self.total_docs, 1) * 100, 2),
            "errors": self.errors,
            "duration_seconds": round(self.duration_seconds, 2),
        }


@dataclass
class DashboardMetrics:
    """Aggregated dashboard metrics."""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    total_batches: int = 0
    total_documents: int = 0
    successful_documents: int = 0
    failed_documents: int = 0
    avg_throughput: float = 0.0
    p95_latency: float = 0.0
    error_summary: Dict[str, int] = field(default_factory=dict)
    recent_batches: List[BatchMetric] = field(default_factory=list)

    @property
    def overall_success_rate(self) -> float:
        """Calculate overall success rate."""
        if self.total_documents == 0:
            return 0.0
        return round(self.successful_documents / self.total_documents * 100, 2)

    @property
    def overall_error_rate(self) -> float:
        """Calculate overall error rate."""
        if self.total_documents == 0:
            return 0.0
        return round(self.failed_documents / self.total_documents * 100, 2)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "summary": {
                "total_batches": self.total_batches,
                "total_documents": self.total_documents,
                "successful_documents": self.successful_documents,
                "failed_documents": self.failed_documents,
                "overall_success_rate": self.overall_success_rate,
                "overall_error_rate": self.overall_error_rate,
            },
            "performance": {
                "avg_throughput_docs_per_sec": round(self.avg_throughput, 2),
                "p95_latency_ms": round(self.p95_latency, 2),
            },
            "errors": self.error_summary,
        }


class MonitoringDashboard:
    """Main monitoring dashboard manager."""

    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self.batches: List[BatchMetric] = []
        self.metrics = DashboardMetrics()

    def record_batch(
        self,
        batch_id: str,
        operation: str,
        total_docs: int,
        successful_docs: int,
        failed_docs: int,
        errors: Optional[Dict[str, int]] = None,
        duration_seconds: float = 0.0,
    ) -> BatchMetric:
        """Record a batch operation."""
        metric = BatchMetric(
            batch_id=batch_id,
            operation=operation,
            start_time=datetime.now().isoformat(),
            end_time=datetime.now().isoformat(),
            total_docs=total_docs,
            successful_docs=successful_docs,
            failed_docs=failed_docs,
            errors=errors or {},
            duration_seconds=duration_seconds,
        )

        self.batches.append(metric)
        self._update_aggregate_metrics()
        return metric

    def _update_aggregate_metrics(self) -> None:
        """Update aggregated metrics."""
        if not self.batches:
            return

        # Aggregate batch metrics
        total_docs = sum(b.total_docs for b in self.batches)
        successful = sum(b.successful_docs for b in self.batches)
        failed = sum(b.failed_docs for b in self.batches)

        # Aggregate errors
        error_summary = {}
        for batch in self.batches:
            for error_type, count in batch.errors.items():
                error_summary[error_type] = error_summary.get(error_type, 0) + count

        # Calculate performance metrics
        total_duration = sum(b.duration_seconds for b in self.batches)
        throughput = total_docs / max(total_duration, 1)

        # Calculate p95 latency
        durations = sorted([b.duration_seconds for b in self.batches])
        p95_index = max(0, int(len(durations) * 0.95))
        p95_latency = durations[p95_index] if durations else 0.0

        # Update metrics
        self.metrics.total_batches = len(self.batches)
        self.metrics.total_documents = total_docs
        self.metrics.successful_documents = successful
        self.metrics.failed_documents = failed
        self.metrics.avg_throughput = throughput
        self.metrics.p95_latency = p95_latency
        self.metrics.error_summary = error_summary
        self.metrics.recent_batches = self.batches[-10:]  # Keep last 10

    def get_dashboard(self) -> Dict[str, Any]:
        """Get full dashboard."""
        return {
            "dashboard": self.metrics.to_dict(),
            "batches_detail": [b.to_dict() for b in self.batches[-10:]],
        }

    def get_health_status(self) -> Dict[str, str]:
        """Get system health status."""
        if self.metrics.total_documents == 0:
            return {"status": "no_data"}

        success_rate = self.metrics.overall_success_rate

        if success_rate >= 99:
            status = "healthy"
        elif success_rate >= 95:
            status = "warning"
        elif success_rate >= 90:
            status = "degraded"
        else:
            status = "critical"

        return {
            "status": status,
            "success_rate": f"{success_rate}%",
            "total_documents": str(self.metrics.total_documents),
            "failed_documents": str(self.metrics.failed_documents),
        }

    def get_error_report(self) -> Dict[str, Any]:
        """Get detailed error report."""
        error_details = {}

        for batch in self.batches:
            if batch.errors:
                error_details[batch.batch_id] = {
                    "operation": batch.operation,
                    "total_errors": sum(batch.errors.values()),
                    "error_breakdown": batch.errors,
                }

        return {
            "total_errors": sum(self.metrics.error_summary.values()),
            "error_types": self.metrics.error_summary,
            "batch_details": error_details,
        }

    def format_text_report(self) -> str:
        """Format dashboard as human-readable text report."""
        lines = [
            "=" * 70,
            "LIFE BRAIN MONITORING DASHBOARD",
            "=" * 70,
            "",
            f"Timestamp: {self.metrics.timestamp}",
            "",
            "SUMMARY",
            "-" * 70,
            f"  Total Batches: {self.metrics.total_batches}",
            f"  Total Documents: {self.metrics.total_documents}",
            f"  Successful: {self.metrics.successful_documents}",
            f"  Failed: {self.metrics.failed_documents}",
            "",
            "SUCCESS METRICS",
            "-" * 70,
            f"  Overall Success Rate: {self.metrics.overall_success_rate}%",
            f"  Overall Error Rate: {self.metrics.overall_error_rate}%",
            "",
            "PERFORMANCE",
            "-" * 70,
            f"  Average Throughput: {self.metrics.avg_throughput:.2f} docs/sec",
            f"  P95 Latency: {self.metrics.p95_latency:.2f} sec",
            "",
            "ERROR SUMMARY",
            "-" * 70,
        ]

        if self.metrics.error_summary:
            for error_type, count in sorted(
                self.metrics.error_summary.items(),
                key=lambda x: x[1],
                reverse=True,
            ):
                lines.append(f"  {error_type}: {count}")
        else:
            lines.append("  No errors recorded")

        lines.extend([
            "",
            "=" * 70,
        ])

        return "\n".join(lines)

    def cleanup_old_batches(self) -> int:
        """Remove batches older than retention period."""
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        cutoff_iso = cutoff_time.isoformat()

        original_count = len(self.batches)
        self.batches = [
            b for b in self.batches
            if b.start_time > cutoff_iso
        ]

        removed = original_count - len(self.batches)
        self._update_aggregate_metrics()
        return removed


# Global dashboard instance
_dashboard_instance: Optional[MonitoringDashboard] = None


def get_dashboard() -> MonitoringDashboard:
    """Get or create global dashboard."""
    global _dashboard_instance
    if _dashboard_instance is None:
        _dashboard_instance = MonitoringDashboard()
    return _dashboard_instance


def record_batch(
    batch_id: str,
    operation: str,
    total_docs: int,
    successful_docs: int,
    failed_docs: int,
    errors: Optional[Dict[str, int]] = None,
    duration_seconds: float = 0.0,
) -> BatchMetric:
    """Record batch to global dashboard."""
    return get_dashboard().record_batch(
        batch_id=batch_id,
        operation=operation,
        total_docs=total_docs,
        successful_docs=successful_docs,
        failed_docs=failed_docs,
        errors=errors,
        duration_seconds=duration_seconds,
    )
