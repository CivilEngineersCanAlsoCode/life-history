"""
Resolution logger for recording conflict resolution decisions.

Logs all conflict resolutions with decision, reasoning, and metadata
for audit trail and analysis.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    """Log level for resolution logging."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ResolutionLog:
    """A single resolution log entry."""

    log_id: str
    document_id: str
    field_name: str
    existing_value: Any
    new_value: Any
    chosen_resolution: str  # keep_existing, use_new, merge, manual, skip
    resolved_value: Any
    reasoning: str
    decided_by: str = "system"  # user, system, auto, admin
    log_level: LogLevel = LogLevel.INFO
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    affected_downstream: List[str] = field(default_factory=list)  # Fields that depend on this

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "log_id": self.log_id,
            "document_id": self.document_id,
            "field_name": self.field_name,
            "existing_value": self.existing_value,
            "new_value": self.new_value,
            "chosen_resolution": self.chosen_resolution,
            "resolved_value": self.resolved_value,
            "reasoning": self.reasoning,
            "decided_by": self.decided_by,
            "log_level": self.log_level.value,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "affected_downstream": self.affected_downstream,
        }

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate log entry."""
        errors = []

        if not self.document_id or not self.document_id.strip():
            errors.append("document_id is required")

        if not self.field_name or not self.field_name.strip():
            errors.append("field_name is required")

        if not self.reasoning or not self.reasoning.strip():
            errors.append("reasoning is required")

        valid_resolutions = ["keep_existing", "use_new", "merge", "manual", "skip"]
        if self.chosen_resolution not in valid_resolutions:
            errors.append(f"chosen_resolution must be one of: {valid_resolutions}")

        return len(errors) == 0, errors


class ResolutionLogger:
    """Log and manage resolution decisions."""

    def __init__(self):
        """Initialize resolution logger."""
        self.logs: Dict[str, ResolutionLog] = {}  # log_id -> ResolutionLog
        self.document_logs: Dict[str, List[str]] = {}  # document_id -> [log_ids]
        self.field_logs: Dict[str, List[str]] = {}  # field_name -> [log_ids]

    def resolution_logger(
        self,
        document_id: str,
        field_name: str,
        existing_value: Any,
        new_value: Any,
        chosen_resolution: str,
        resolved_value: Any,
        reasoning: str,
        decided_by: str = "system",
        log_level: LogLevel = LogLevel.INFO,
        metadata: Optional[Dict[str, Any]] = None,
        affected_downstream: Optional[List[str]] = None,
    ) -> ResolutionLog:
        """
        Log a conflict resolution decision.

        Args:
            document_id: Document ID
            field_name: Field that was resolved
            existing_value: Original value
            new_value: Proposed value
            chosen_resolution: Which option was chosen
            resolved_value: Final resolved value
            reasoning: Why this decision was made
            decided_by: Who/what made decision (user, system, auto, admin)
            log_level: Logging level (info, warning, error, etc.)
            metadata: Additional metadata
            affected_downstream: Fields that depend on this resolution

        Returns:
            ResolutionLog object
        """
        # Create log entry
        log_id = f"reslog_{document_id}_{field_name}_{hash(str(resolved_value)) % 10000:04d}"

        log_entry = ResolutionLog(
            log_id=log_id,
            document_id=document_id,
            field_name=field_name,
            existing_value=existing_value,
            new_value=new_value,
            chosen_resolution=chosen_resolution,
            resolved_value=resolved_value,
            reasoning=reasoning,
            decided_by=decided_by,
            log_level=log_level,
            metadata=metadata or {},
            affected_downstream=affected_downstream or [],
        )

        # Validate
        is_valid, errors = log_entry.validate()
        if not is_valid:
            raise ValueError(f"Invalid resolution log: {errors}")

        # Store log
        self.logs[log_id] = log_entry

        # Track by document
        if document_id not in self.document_logs:
            self.document_logs[document_id] = []
        self.document_logs[document_id].append(log_id)

        # Track by field
        if field_name not in self.field_logs:
            self.field_logs[field_name] = []
        self.field_logs[field_name].append(log_id)

        return log_entry

    def get_logs_for_document(self, document_id: str) -> List[ResolutionLog]:
        """Get all logs for a document."""
        log_ids = self.document_logs.get(document_id, [])
        return [self.logs[log_id] for log_id in log_ids]

    def get_logs_for_field(self, field_name: str) -> List[ResolutionLog]:
        """Get all logs for a specific field."""
        log_ids = self.field_logs.get(field_name, [])
        return [self.logs[log_id] for log_id in log_ids]

    def get_logs_by_decision_maker(self, decided_by: str) -> List[ResolutionLog]:
        """Get logs by who made the decision."""
        return [
            log for log in self.logs.values()
            if log.decided_by == decided_by
        ]

    def get_logs_by_level(self, log_level: LogLevel) -> List[ResolutionLog]:
        """Get logs by level."""
        return [
            log for log in self.logs.values()
            if log.log_level == log_level
        ]

    def get_logs_since(self, timestamp: str) -> List[ResolutionLog]:
        """Get logs since given ISO timestamp."""
        return [
            log for log in self.logs.values()
            if log.timestamp >= timestamp
        ]

    def get_logs_for_document_field(
        self,
        document_id: str,
        field_name: str,
    ) -> List[ResolutionLog]:
        """Get resolution history for a specific field in a document."""
        doc_logs = self.get_logs_for_document(document_id)
        return [log for log in doc_logs if log.field_name == field_name]

    def get_document_audit_trail(self, document_id: str) -> Dict[str, Any]:
        """Get complete audit trail for a document."""
        logs = self.get_logs_for_document(document_id)
        return {
            "document_id": document_id,
            "total_resolutions": len(logs),
            "by_resolution": self._count_resolutions(logs),
            "by_decided_by": self._count_decision_makers(logs),
            "logs": sorted(
                [log.to_dict() for log in logs],
                key=lambda x: x["timestamp"],
            ),
        }

    def get_field_resolution_history(self, field_name: str) -> Dict[str, Any]:
        """Get resolution history for a field across all documents."""
        logs = self.get_logs_for_field(field_name)
        return {
            "field_name": field_name,
            "total_resolutions": len(logs),
            "documents_affected": len(set(log.document_id for log in logs)),
            "by_resolution": self._count_resolutions(logs),
            "logs": sorted(
                [log.to_dict() for log in logs],
                key=lambda x: x["timestamp"],
                reverse=True,
            ),
        }

    def _count_resolutions(self, logs: List[ResolutionLog]) -> Dict[str, int]:
        """Count resolutions by type."""
        counts = {}
        for log in logs:
            counts[log.chosen_resolution] = counts.get(log.chosen_resolution, 0) + 1
        return counts

    def _count_decision_makers(self, logs: List[ResolutionLog]) -> Dict[str, int]:
        """Count decisions by maker."""
        counts = {}
        for log in logs:
            counts[log.decided_by] = counts.get(log.decided_by, 0) + 1
        return counts

    def get_statistics(self) -> Dict[str, Any]:
        """Get logging statistics."""
        if not self.logs:
            return {
                "total_logs": 0,
                "total_documents": 0,
                "total_fields": 0,
                "by_resolution": {},
                "by_decided_by": {},
                "by_level": {},
            }

        documents = set(log.document_id for log in self.logs.values())
        fields = set(log.field_name for log in self.logs.values())

        by_resolution = self._count_resolutions(list(self.logs.values()))
        by_decided_by = self._count_decision_makers(list(self.logs.values()))

        by_level = {}
        for log in self.logs.values():
            level = log.log_level.value
            by_level[level] = by_level.get(level, 0) + 1

        return {
            "total_logs": len(self.logs),
            "total_documents": len(documents),
            "total_fields": len(fields),
            "by_resolution": by_resolution,
            "by_decided_by": by_decided_by,
            "by_level": by_level,
        }

    def export_logs(self) -> List[Dict[str, Any]]:
        """Export all logs."""
        return sorted(
            [log.to_dict() for log in self.logs.values()],
            key=lambda x: x["timestamp"],
            reverse=True,
        )

    def export_document_logs(self, document_id: str) -> List[Dict[str, Any]]:
        """Export logs for a document."""
        logs = self.get_logs_for_document(document_id)
        return sorted(
            [log.to_dict() for log in logs],
            key=lambda x: x["timestamp"],
        )

    def get_warnings_and_errors(self) -> Dict[str, Any]:
        """Get all warning and error level logs."""
        warnings = self.get_logs_by_level(LogLevel.WARNING)
        errors = self.get_logs_by_level(LogLevel.ERROR)
        critical = self.get_logs_by_level(LogLevel.CRITICAL)

        return {
            "warnings": len(warnings),
            "errors": len(errors),
            "critical": len(critical),
            "warning_logs": [log.to_dict() for log in warnings],
            "error_logs": [log.to_dict() for log in errors],
            "critical_logs": [log.to_dict() for log in critical],
        }

    def get_most_common_resolutions(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Get most common resolution choices."""
        stats = self.get_statistics()
        by_resolution = stats["by_resolution"]
        return sorted(
            by_resolution.items(),
            key=lambda x: -x[1],
        )[:limit]

    def get_decision_maker_distribution(self) -> Dict[str, int]:
        """Get distribution of who made decisions."""
        stats = self.get_statistics()
        return stats["by_decided_by"]
