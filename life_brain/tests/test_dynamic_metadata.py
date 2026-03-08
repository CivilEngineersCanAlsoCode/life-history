"""
Test suite for dynamic metadata.

Tests cover:
- Custom field creation and validation
- Adding/updating/deleting custom fields
- Merging with base metadata
- Usage tracking and statistics
- Field promotion candidates
"""

import pytest

from life_brain.db.dynamic_metadata import CustomField, DynamicMetadata


class TestCustomField:
    """Test CustomField dataclass."""

    def test_create_field(self):
        """Test creating a custom field."""
        field = CustomField(key="custom_tag", value="important")

        assert field.key == "custom_tag"
        assert field.value == "important"
        assert field.usage_count == 1

    def test_to_dict(self):
        """Test converting field to dictionary."""
        field = CustomField(key="custom_tag", value="test")
        field.document_ids.add("doc_001")

        field_dict = field.to_dict()
        assert field_dict["key"] == "custom_tag"
        assert field_dict["value"] == "test"
        assert "doc_001" in field_dict["document_ids"]

    def test_validate_valid_field(self):
        """Test validating valid field."""
        field = CustomField(key="custom_tag", value="test")

        is_valid, errors = field.validate()
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_empty_key(self):
        """Test validation with empty key."""
        field = CustomField(key="", value="test")

        is_valid, errors = field.validate()
        assert is_valid is False
        assert any("key is required" in e for e in errors)

    def test_validate_reserved_key(self):
        """Test validation rejects reserved keys."""
        field = CustomField(key="document_id", value="test")

        is_valid, errors = field.validate()
        assert is_valid is False
        assert any("reserved" in e for e in errors)


class TestDynamicMetadata:
    """Test DynamicMetadata functionality."""

    def test_create_dynamic_metadata(self):
        """Test creating dynamic metadata system."""
        dm = DynamicMetadata()
        assert len(dm.custom_fields) == 0
        assert len(dm.document_metadata) == 0

    def test_add_custom_field(self):
        """Test adding a custom field."""
        dm = DynamicMetadata()

        success, error = dm.add_custom_field("doc_001", "priority", "high")
        assert success is True
        assert error is None
        assert "priority" in dm.custom_fields

    def test_add_multiple_custom_fields(self):
        """Test adding multiple custom fields."""
        dm = DynamicMetadata()

        dm.add_custom_field("doc_001", "priority", "high")
        dm.add_custom_field("doc_001", "team", "data-science")
        dm.add_custom_field("doc_002", "priority", "urgent")

        assert len(dm.custom_fields) == 2
        assert len(dm.document_metadata) == 2

    def test_add_custom_field_reserved_key(self):
        """Test adding custom field with reserved key."""
        dm = DynamicMetadata()

        success, error = dm.add_custom_field("doc_001", "document_id", "test")
        assert success is False
        assert "reserved" in error

    def test_add_custom_field_empty_key(self):
        """Test adding custom field with empty key."""
        dm = DynamicMetadata()

        success, error = dm.add_custom_field("doc_001", "", "value")
        assert success is False
        assert "empty" in error

    def test_get_custom_fields_for_document(self):
        """Test retrieving custom fields for a document."""
        dm = DynamicMetadata()

        dm.add_custom_field("doc_001", "priority", "high")
        dm.add_custom_field("doc_001", "team", "data")
        dm.add_custom_field("doc_002", "priority", "low")

        doc_001_fields = dm.get_custom_fields_for_document("doc_001")
        assert len(doc_001_fields) == 2
        assert doc_001_fields["priority"] == "high"

        doc_002_fields = dm.get_custom_fields_for_document("doc_002")
        assert len(doc_002_fields) == 1
        assert doc_002_fields["priority"] == "low"

    def test_get_custom_field_value(self):
        """Test getting a specific custom field value."""
        dm = DynamicMetadata()

        dm.add_custom_field("doc_001", "priority", "high")

        value = dm.get_custom_field_value("doc_001", "priority")
        assert value == "high"

        value = dm.get_custom_field_value("doc_001", "nonexistent")
        assert value is None

    def test_update_custom_field(self):
        """Test updating a custom field."""
        dm = DynamicMetadata()

        dm.add_custom_field("doc_001", "priority", "high")
        success, error = dm.update_custom_field("doc_001", "priority", "urgent")

        assert success is True
        assert dm.get_custom_field_value("doc_001", "priority") == "urgent"

    def test_update_nonexistent_field(self):
        """Test updating nonexistent field."""
        dm = DynamicMetadata()

        success, error = dm.update_custom_field("doc_001", "priority", "high")
        assert success is False
        assert "not found" in error

    def test_delete_custom_field(self):
        """Test deleting a custom field."""
        dm = DynamicMetadata()

        dm.add_custom_field("doc_001", "priority", "high")
        success, error = dm.delete_custom_field("doc_001", "priority")

        assert success is True
        value = dm.get_custom_field_value("doc_001", "priority")
        assert value is None

    def test_delete_nonexistent_field(self):
        """Test deleting nonexistent field."""
        dm = DynamicMetadata()

        success, error = dm.delete_custom_field("doc_001", "priority")
        assert success is False

    def test_get_fields_by_usage(self):
        """Test getting fields sorted by usage."""
        dm = DynamicMetadata()

        # Add priority to 3 documents
        dm.add_custom_field("doc_001", "priority", "high")
        dm.add_custom_field("doc_002", "priority", "high")
        dm.add_custom_field("doc_003", "priority", "high")

        # Add team to 2 documents
        dm.add_custom_field("doc_001", "team", "backend")
        dm.add_custom_field("doc_002", "team", "frontend")

        # Add status to 1 document
        dm.add_custom_field("doc_001", "status", "active")

        fields_by_usage = dm.get_fields_by_usage()
        assert fields_by_usage[0] == ("priority", 3)
        assert fields_by_usage[1] == ("team", 2)
        assert fields_by_usage[2] == ("status", 1)

    def test_get_high_frequency_fields(self):
        """Test getting fields appearing 20+ times."""
        dm = DynamicMetadata()

        # Add field to 25 documents
        for i in range(25):
            dm.add_custom_field(f"doc_{i:03d}", "frequent_field", "value")

        # Add another to 15 documents (below threshold)
        for i in range(15):
            dm.add_custom_field(f"doc_freq_{i:03d}", "rare_field", "value")

        high_freq = dm.get_high_frequency_fields(threshold=20)
        assert "frequent_field" in high_freq
        assert "rare_field" not in high_freq

    def test_merge_custom_fields(self):
        """Test merging custom fields with base metadata."""
        dm = DynamicMetadata()

        dm.add_custom_field("doc_001", "priority", "high")
        dm.add_custom_field("doc_001", "team", "backend")

        base_metadata = {"domain": "career", "source": "resume"}
        merged = dm.merge_custom_fields(base_metadata, "doc_001")

        assert merged["domain"] == "career"
        assert "_custom_fields" in merged
        assert merged["_custom_fields"]["priority"] == "high"

    def test_dynamic_metadata_batch(self):
        """Test adding multiple custom fields at once."""
        dm = DynamicMetadata()

        results = dm.dynamic_metadata(
            "doc_001",
            priority="high",
            team="backend",
            status="active",
        )

        assert len(results) == 3
        assert all(results[key]["success"] for key in results)

    def test_dynamic_metadata_with_reserved_keys(self):
        """Test batch add with reserved keys."""
        dm = DynamicMetadata()

        # Test with reserved key 'id' instead of 'document_id' to avoid parameter conflict
        results = dm.dynamic_metadata(
            "doc_001",
            priority="high",
            id="bad",  # Reserved
            team="backend",
        )

        assert results["priority"]["success"] is True
        assert results["id"]["success"] is False
        assert results["team"]["success"] is True

    def test_get_statistics_empty(self):
        """Test statistics on empty system."""
        dm = DynamicMetadata()
        stats = dm.get_statistics()

        assert stats["total_custom_fields"] == 0
        assert stats["total_documents_with_custom"] == 0

    def test_get_statistics_populated(self):
        """Test statistics on populated system."""
        dm = DynamicMetadata()

        # Add 3 fields appearing different times
        for i in range(5):
            dm.add_custom_field(f"doc_{i}", "priority", "high")

        for i in range(3):
            dm.add_custom_field(f"doc_{i}", "team", "backend")

        dm.add_custom_field("doc_0", "status", "active")

        stats = dm.get_statistics()

        assert stats["total_custom_fields"] == 3
        assert stats["total_documents_with_custom"] == 5
        assert "priority" in [f[0] for f in stats["most_common_fields"]]
        assert len(stats["most_common_fields"]) <= 10

    def test_export_custom_fields(self):
        """Test exporting all custom fields."""
        dm = DynamicMetadata()

        dm.add_custom_field("doc_001", "priority", "high")
        dm.add_custom_field("doc_002", "priority", "low")
        dm.add_custom_field("doc_001", "team", "backend")

        exported = dm.export_custom_fields()

        assert "priority" in exported
        assert "team" in exported
        assert exported["priority"]["usage_count"] == 2
        assert exported["team"]["usage_count"] == 1

    def test_export_document_custom_metadata(self):
        """Test exporting custom metadata for a document."""
        dm = DynamicMetadata()

        dm.add_custom_field("doc_001", "priority", "high")
        dm.add_custom_field("doc_001", "team", "backend")

        exported = dm.export_document_custom_metadata("doc_001")

        assert exported["document_id"] == "doc_001"
        assert len(exported["custom_fields"]) == 2
        assert exported["custom_fields"]["priority"] == "high"

    def test_usage_count_tracking(self):
        """Test usage count increases properly."""
        dm = DynamicMetadata()

        # First document with field
        dm.add_custom_field("doc_001", "priority", "high")
        assert dm.custom_fields["priority"].usage_count == 1

        # Second document with same field
        dm.add_custom_field("doc_002", "priority", "high")
        assert dm.custom_fields["priority"].usage_count == 2

        # Third document with same field
        dm.add_custom_field("doc_003", "priority", "high")
        assert dm.custom_fields["priority"].usage_count == 3

    def test_document_tracking(self):
        """Test which documents have each field."""
        dm = DynamicMetadata()

        dm.add_custom_field("doc_001", "priority", "high")
        dm.add_custom_field("doc_002", "priority", "high")
        dm.add_custom_field("doc_001", "team", "backend")

        priority_field = dm.custom_fields["priority"]
        assert "doc_001" in priority_field.document_ids
        assert "doc_002" in priority_field.document_ids

        team_field = dm.custom_fields["team"]
        assert "doc_001" in team_field.document_ids
        assert "doc_002" not in team_field.document_ids

    def test_complex_workflow(self):
        """Test complex workflow with multiple operations."""
        dm = DynamicMetadata()

        # Add multiple fields to multiple documents
        for i in range(30):
            dm.add_custom_field(f"doc_{i:03d}", "priority", f"level_{i % 3}")
            if i % 2 == 0:
                dm.add_custom_field(f"doc_{i:03d}", "team", f"team_{i % 5}")

        # Get stats
        stats = dm.get_statistics()
        assert stats["total_custom_fields"] == 2
        assert stats["total_documents_with_custom"] == 30

        # Check promotion candidate
        high_freq = dm.get_high_frequency_fields(threshold=20)
        assert "priority" in high_freq

        # Update some fields
        dm.update_custom_field("doc_000", "priority", "urgent")

        # Delete a field
        dm.delete_custom_field("doc_000", "team")

        # Verify final state
        final_stats = dm.get_statistics()
        assert final_stats["total_custom_fields"] == 2
