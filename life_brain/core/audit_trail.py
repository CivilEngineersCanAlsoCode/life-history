"""
Audit trail for document corrections and changes.

Logs all document modifications with:
- old_value: Previous value
- new_value: Updated value
- resolution: How/why the change was made
- timestamp: When the change occurred
- change_type: Type of change (correction, enrichment, conflict resolution, etc.)
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class AuditEntry:
    """A single audit trail entry."""

    entry_id: str
    document_id: str
    field_name: str
    old_value: Any
    new_value: Any
    resolution: str  # Why/how the change was made
    change_type: str  # correction, enrichment, conflict_resolution, normalization, etc.
    changed_by: str = "system"  # Who/what made the change
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entry_id": self.entry_id,
            "document_id": self.document_id,
            "field_name": self.field_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "resolution": self.resolution,
            "change_type": self.change_type,
            "changed_by": self.changed_by,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate audit entry."""
        errors = []

        if not self.document_id or not self.document_id.strip():
            errors.append("document_id is required")

        if not self.field_name or not self.field_name.strip():
            errors.append("field_name is required")

        if not self.resolution or not self.resolution.strip():
            errors.append("resolution is required")

        if not self.change_type or not self.change_type.strip():
            errors.append("change_type is required")

        return len(errors) == 0, errors


class AuditTrail:
    """Manage audit trail entries for document corrections."""

    # Valid change types
    CHANGE_TYPES = [
        "correction",
        "enrichment",
        "conflict_resolution",
        "normalization",
        "consolidation",
        "deletion",
        "merging",
        "verification",
    ]

    def __init__(self):
        """Initialize audit trail."""
        self.entries: Dict[str, AuditEntry] = {}  # entry_id -> AuditEntry
        self.document_entries: Dict[str, List[str]] = {}  # document_id -> [entry_ids]

    def audit_trail(
        self,
        document_id: str,
        field_name: str,
        old_value: Any,
        new_value: Any,
        resolution: str,
        change_type: str = "correction",
        changed_by: str = "system",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEntry:
        """
        Log a document correction to audit trail.

        Args:
            document_id: Document being modified
            field_name: Field that changed
            old_value: Previous value
            new_value: Updated value
            resolution: Why/how the change was made
            change_type: Type of change (default: correction)
            changed_by: Who/what made the change (default: system)
            metadata: Additional metadata for the entry

        Returns:
            AuditEntry object

        Raises:
            ValueError: If change_type not in CHANGE_TYPES or resolution empty
        """
        if change_type not in self.CHANGE_TYPES:
            raise ValueError(
                f"Invalid change_type '{change_type}'. Must be one of: {self.CHANGE_TYPES}"
            )

        if not resolution or not resolution.strip():
            raise ValueError("resolution cannot be empty")

        # Create entry
        entry_id = f"audit_{document_id}_{field_name}_{uuid.uuid4().hex[:8]}"

        entry = AuditEntry(
            entry_id=entry_id,
            document_id=document_id,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            resolution=resolution,
            change_type=change_type,
            changed_by=changed_by,
            metadata=metadata or {},
        )

        # Validate
        is_valid, errors = entry.validate()
        if not is_valid:
            raise ValueError(f"Invalid audit entry: {errors}")

        # Store entry
        self.entries[entry_id] = entry

        # Track by document
        if document_id not in self.document_entries:
            self.document_entries[document_id] = []
        self.document_entries[document_id].append(entry_id)

        return entry

    def get_entries_for_document(self, document_id: str) -> List[AuditEntry]:
        """Get all audit entries for a document."""
        entry_ids = self.document_entries.get(document_id, [])
        return [self.entries[entry_id] for entry_id in entry_ids]

    def get_entries_for_field(
        self, document_id: str, field_name: str
    ) -> List[AuditEntry]:
        """Get all audit entries for a specific field in a document."""
        entries = self.get_entries_for_document(document_id)
        return [e for e in entries if e.field_name == field_name]

    def get_entries_by_type(self, change_type: str) -> List[AuditEntry]:
        """Get all audit entries of a specific type."""
        return [e for e in self.entries.values() if e.change_type == change_type]

    def get_entries_by_changed_by(self, changed_by: str) -> List[AuditEntry]:
        """Get all audit entries changed by a specific user/system."""
        return [e for e in self.entries.values() if e.changed_by == changed_by]

    def get_entries_since(self, timestamp: str) -> List[AuditEntry]:
        """Get all audit entries since a given ISO timestamp."""
        return [
            e
            for e in self.entries.values()
            if e.timestamp >= timestamp
        ]

    def get_change_history(self, document_id: str, field_name: str) -> List[Dict[str, Any]]:
        """Get chronological change history for a field."""
        entries = self.get_entries_for_field(document_id, field_name)
        # Sort by timestamp
        sorted_entries = sorted(entries, key=lambda e: e.timestamp)
        return [e.to_dict() for e in sorted_entries]

    def get_statistics(self) -> Dict[str, Any]:
        """Get audit trail statistics."""
        if not self.entries:
            return {
                "total_entries": 0,
                "total_documents": 0,
                "total_fields": 0,
                "change_types": {},
                "changed_by_users": {},
            }

        # Calculate stats
        documents = set(e.document_id for e in self.entries.values())
        fields = set(e.field_name for e in self.entries.values())
        change_types = {}
        for e in self.entries.values():
            change_types[e.change_type] = change_types.get(e.change_type, 0) + 1

        changed_by_users = {}
        for e in self.entries.values():
            changed_by_users[e.changed_by] = (
                changed_by_users.get(e.changed_by, 0) + 1
            )

        return {
            "total_entries": len(self.entries),
            "total_documents": len(documents),
            "total_fields": len(fields),
            "change_types": change_types,
            "changed_by_users": changed_by_users,
        }

    def export_entries(self) -> List[Dict[str, Any]]:
        """Export all audit entries."""
        return sorted(
            [e.to_dict() for e in self.entries.values()],
            key=lambda x: x["timestamp"],
        )

    def export_document_audit(self, document_id: str) -> Dict[str, Any]:
        """Export complete audit log for a document."""
        entries = self.get_entries_for_document(document_id)
        return {
            "document_id": document_id,
            "total_changes": len(entries),
            "entries": sorted(
                [e.to_dict() for e in entries],
                key=lambda x: x["timestamp"],
            ),
        }
