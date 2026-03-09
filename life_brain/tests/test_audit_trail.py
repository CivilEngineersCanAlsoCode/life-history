"""
Test suite for audit trail functionality.

Tests cover:
- Audit entry creation and validation
- Logging document corrections
- Change history tracking
- Filtering and retrieval
- Statistics and reporting
"""

import pytest
from datetime import datetime, timedelta

from life_brain.core.audit_trail import AuditEntry, AuditTrail


class TestAuditEntry:
    """Test AuditEntry dataclass."""

    def test_create_entry(self):
        """Test creating audit entry."""
        entry = AuditEntry(
            entry_id="audit_001",
            document_id="doc_001",
            field_name="title",
            old_value="Old Title",
            new_value="New Title",
            resolution="Fixed typo",
            change_type="correction",
        )

        assert entry.entry_id == "audit_001"
        assert entry.document_id == "doc_001"
        assert entry.field_name == "title"

    def test_to_dict(self):
        """Test converting entry to dictionary."""
        entry = AuditEntry(
            entry_id="audit_001",
            document_id="doc_001",
            field_name="title",
            old_value="Old",
            new_value="New",
            resolution="Fixed",
            change_type="correction",
        )

        entry_dict = entry.to_dict()
        assert entry_dict["entry_id"] == "audit_001"
        assert entry_dict["old_value"] == "Old"
        assert entry_dict["new_value"] == "New"

    def test_validate_valid_entry(self):
        """Test validating valid entry."""
        entry = AuditEntry(
            entry_id="audit_001",
            document_id="doc_001",
            field_name="title",
            old_value="Old",
            new_value="New",
            resolution="Fixed",
            change_type="correction",
        )

        is_valid, errors = entry.validate()
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_missing_fields(self):
        """Test validation with missing fields."""
        entry = AuditEntry(
            entry_id="audit_001",
            document_id="",  # Empty
            field_name="title",
            old_value="Old",
            new_value="New",
            resolution="Fixed",
            change_type="correction",
        )

        is_valid, errors = entry.validate()
        assert is_valid is False
        assert any("document_id" in e for e in errors)

    def test_validate_empty_resolution(self):
        """Test validation with empty resolution."""
        entry = AuditEntry(
            entry_id="audit_001",
            document_id="doc_001",
            field_name="title",
            old_value="Old",
            new_value="New",
            resolution="",  # Empty
            change_type="correction",
        )

        is_valid, errors = entry.validate()
        assert is_valid is False
        assert any("resolution" in e for e in errors)


class TestAuditTrail:
    """Test AuditTrail functionality."""

    def test_create_audit_trail(self):
        """Test creating audit trail."""
        trail = AuditTrail()
        assert len(trail.entries) == 0
        assert len(trail.document_entries) == 0

    def test_audit_trail_single_entry(self):
        """Test logging a single audit entry."""
        trail = AuditTrail()

        entry = trail.audit_trail(
            document_id="doc_001",
            field_name="title",
            old_value="Old Title",
            new_value="New Title",
            resolution="Fixed typo in title",
            change_type="correction",
        )

        assert entry.document_id == "doc_001"
        assert entry.old_value == "Old Title"
        assert entry.new_value == "New Title"
        assert len(trail.entries) == 1

    def test_audit_trail_invalid_change_type(self):
        """Test audit trail with invalid change type."""
        trail = AuditTrail()

        with pytest.raises(ValueError, match="Invalid change_type"):
            trail.audit_trail(
                document_id="doc_001",
                field_name="title",
                old_value="Old",
                new_value="New",
                resolution="Fixed",
                change_type="invalid_type",
            )

    def test_audit_trail_empty_resolution(self):
        """Test audit trail with empty resolution."""
        trail = AuditTrail()

        with pytest.raises(ValueError, match="resolution cannot be empty"):
            trail.audit_trail(
                document_id="doc_001",
                field_name="title",
                old_value="Old",
                new_value="New",
                resolution="",
            )

    def test_get_entries_for_document(self):
        """Test retrieving entries for a document."""
        trail = AuditTrail()

        trail.audit_trail("doc_001", "title", "Old", "New", "Fixed typo")
        trail.audit_trail("doc_001", "description", "Old desc", "New desc", "Updated")
        trail.audit_trail("doc_002", "title", "Old", "Updated", "Fixed")

        doc_001_entries = trail.get_entries_for_document("doc_001")
        assert len(doc_001_entries) == 2

        doc_002_entries = trail.get_entries_for_document("doc_002")
        assert len(doc_002_entries) == 1

    def test_get_entries_for_field(self):
        """Test retrieving entries for a specific field."""
        trail = AuditTrail()

        trail.audit_trail("doc_001", "title", "Old1", "New1", "Fixed")
        trail.audit_trail("doc_001", "title", "New1", "New2", "Updated")
        trail.audit_trail("doc_001", "description", "Old", "New", "Added")

        title_entries = trail.get_entries_for_field("doc_001", "title")
        assert len(title_entries) == 2

        desc_entries = trail.get_entries_for_field("doc_001", "description")
        assert len(desc_entries) == 1

    def test_get_entries_by_type(self):
        """Test filtering entries by change type."""
        trail = AuditTrail()

        trail.audit_trail(
            "doc_001", "field1", "Old", "New", "Fixed", change_type="correction"
        )
        trail.audit_trail(
            "doc_002", "field2", "Old", "New", "Added", change_type="enrichment"
        )
        trail.audit_trail(
            "doc_003", "field3", "Old", "New", "Resolved", change_type="conflict_resolution"
        )

        corrections = trail.get_entries_by_type("correction")
        assert len(corrections) == 1

        enrichments = trail.get_entries_by_type("enrichment")
        assert len(enrichments) == 1

    def test_get_entries_by_changed_by(self):
        """Test filtering entries by changed_by."""
        trail = AuditTrail()

        trail.audit_trail(
            "doc_001",
            "field",
            "Old",
            "New",
            "Fixed",
            changed_by="user_1",
        )
        trail.audit_trail(
            "doc_002",
            "field",
            "Old",
            "New",
            "Fixed",
            changed_by="system",
        )
        trail.audit_trail(
            "doc_003",
            "field",
            "Old",
            "New",
            "Fixed",
            changed_by="user_1",
        )

        user_1_entries = trail.get_entries_by_changed_by("user_1")
        assert len(user_1_entries) == 2

        system_entries = trail.get_entries_by_changed_by("system")
        assert len(system_entries) == 1

    def test_get_change_history(self):
        """Test getting chronological change history."""
        trail = AuditTrail()

        trail.audit_trail("doc_001", "title", "Original", "Version1", "First change")
        trail.audit_trail("doc_001", "title", "Version1", "Version2", "Second change")
        trail.audit_trail("doc_001", "title", "Version2", "Final", "Third change")

        history = trail.get_change_history("doc_001", "title")
        assert len(history) == 3
        assert history[0]["old_value"] == "Original"
        assert history[2]["new_value"] == "Final"

    def test_get_entries_since(self):
        """Test filtering entries by timestamp."""
        trail = AuditTrail()

        entry1 = trail.audit_trail(
            "doc_001", "field1", "Old", "New", "Fixed", changed_by="user_1"
        )

        # Get timestamp slightly before now
        past_timestamp = datetime.now() - timedelta(seconds=1)
        past_iso = past_timestamp.isoformat()

        entry2 = trail.audit_trail(
            "doc_002", "field2", "Old", "New", "Fixed", changed_by="user_2"
        )

        entries_since = trail.get_entries_since(past_iso)
        assert len(entries_since) >= 1

    def test_get_statistics_empty(self):
        """Test statistics on empty audit trail."""
        trail = AuditTrail()
        stats = trail.get_statistics()

        assert stats["total_entries"] == 0
        assert stats["total_documents"] == 0
        assert stats["total_fields"] == 0

    def test_get_statistics_populated(self):
        """Test statistics on populated audit trail."""
        trail = AuditTrail()

        trail.audit_trail(
            "doc_001",
            "title",
            "Old",
            "New",
            "Fixed",
            change_type="correction",
            changed_by="user_1",
        )
        trail.audit_trail(
            "doc_001",
            "description",
            "Old",
            "New",
            "Updated",
            change_type="enrichment",
            changed_by="user_1",
        )
        trail.audit_trail(
            "doc_002",
            "title",
            "Old",
            "New",
            "Fixed",
            change_type="correction",
            changed_by="system",
        )

        stats = trail.get_statistics()

        assert stats["total_entries"] == 3
        assert stats["total_documents"] == 2
        assert stats["total_fields"] == 2
        assert stats["change_types"]["correction"] == 2
        assert stats["change_types"]["enrichment"] == 1
        assert stats["changed_by_users"]["user_1"] == 2
        assert stats["changed_by_users"]["system"] == 1

    def test_export_entries(self):
        """Test exporting all entries."""
        trail = AuditTrail()

        trail.audit_trail("doc_001", "field1", "Old", "New", "Fixed")
        trail.audit_trail("doc_002", "field2", "Old", "New", "Updated")

        exported = trail.export_entries()
        assert len(exported) == 2
        assert all("entry_id" in e for e in exported)
        assert all("timestamp" in e for e in exported)

    def test_export_document_audit(self):
        """Test exporting audit log for a document."""
        trail = AuditTrail()

        trail.audit_trail("doc_001", "title", "Old1", "New1", "Fixed")
        trail.audit_trail("doc_001", "description", "Old2", "New2", "Updated")
        trail.audit_trail("doc_002", "title", "Old", "New", "Fixed")

        audit_doc = trail.export_document_audit("doc_001")

        assert audit_doc["document_id"] == "doc_001"
        assert audit_doc["total_changes"] == 2
        assert len(audit_doc["entries"]) == 2

    def test_all_change_types(self):
        """Test all valid change types."""
        trail = AuditTrail()

        for change_type in AuditTrail.CHANGE_TYPES:
            entry = trail.audit_trail(
                f"doc_{change_type}",
                "field",
                "Old",
                "New",
                f"Testing {change_type}",
                change_type=change_type,
            )
            assert entry.change_type == change_type

        assert len(trail.entries) == len(AuditTrail.CHANGE_TYPES)

    def test_multiple_corrections_same_field(self):
        """Test multiple corrections to the same field."""
        trail = AuditTrail()

        # Simulate multiple corrections to the same field
        trail.audit_trail("doc_001", "company_name", "Amex", "American Express", "Normalization")
        trail.audit_trail("doc_001", "company_name", "American Express", "Amex Corp", "Correction")
        trail.audit_trail("doc_001", "company_name", "Amex Corp", "American Express", "Final fix")

        history = trail.get_change_history("doc_001", "company_name")
        assert len(history) == 3
        assert history[0]["old_value"] == "Amex"
        assert history[1]["old_value"] == "American Express"
        assert history[2]["new_value"] == "American Express"

    def test_audit_trail_with_metadata(self):
        """Test audit trail entry with custom metadata."""
        trail = AuditTrail()

        entry = trail.audit_trail(
            "doc_001",
            "field",
            "Old",
            "New",
            "Fixed with ML",
            change_type="correction",
            metadata={"ml_model": "bert-v2", "confidence": 0.95},
        )

        assert entry.metadata["ml_model"] == "bert-v2"
        assert entry.metadata["confidence"] == 0.95
