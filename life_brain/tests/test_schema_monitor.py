"""
Test suite for schema monitor.

Tests cover:
- Field candidate creation and tracking
- Promotion readiness detection
- Field promotion workflow
- Statistics and reporting
- Promotion history tracking
"""

import pytest
from datetime import datetime, timedelta

from life_brain.db.schema_monitor import (
    FieldCandidate,
    SchemaMonitor,
    PromotionStatus,
)


class TestFieldCandidate:
    """Test FieldCandidate dataclass."""

    def test_create_candidate(self):
        """Test creating a field candidate."""
        candidate = FieldCandidate(
            field_name="priority",
            usage_count=25,
            documents_using={"doc_1", "doc_2", "doc_3"},
        )

        assert candidate.field_name == "priority"
        assert candidate.usage_count == 25
        assert candidate.status == PromotionStatus.MONITORING

    def test_to_dict(self):
        """Test converting candidate to dictionary."""
        candidate = FieldCandidate(
            field_name="priority",
            usage_count=25,
            documents_using={"doc_1", "doc_2"},
        )

        cand_dict = candidate.to_dict()
        assert cand_dict["field_name"] == "priority"
        assert cand_dict["usage_count"] == 25
        assert cand_dict["status"] == "monitoring"

    def test_promotion_score_calculation(self):
        """Test promotion score calculation."""
        # High usage, good diversity, recent
        candidate = FieldCandidate(
            field_name="priority",
            usage_count=30,
            documents_using={"doc_1", "doc_2", "doc_3", "doc_4", "doc_5"},
        )

        score = candidate.get_promotion_score()
        assert score > 0
        assert score <= 100


class TestSchemaMonitor:
    """Test SchemaMonitor functionality."""

    def test_create_monitor(self):
        """Test creating schema monitor."""
        monitor = SchemaMonitor()
        assert len(monitor.candidates) == 0

    def test_schema_monitor_new_field(self):
        """Test monitoring a new field."""
        monitor = SchemaMonitor()

        candidate = monitor.schema_monitor(
            field_name="priority",
            usage_count=25,
            document_ids={"doc_1", "doc_2", "doc_3", "doc_4", "doc_5"},
        )

        assert candidate.field_name == "priority"
        assert candidate.usage_count == 25
        assert candidate.status == PromotionStatus.READY

    def test_schema_monitor_not_ready(self):
        """Test monitoring a field not yet ready."""
        monitor = SchemaMonitor()

        candidate = monitor.schema_monitor(
            field_name="priority",
            usage_count=10,  # Below threshold
            document_ids={"doc_1", "doc_2"},
        )

        assert candidate.status == PromotionStatus.MONITORING

    def test_schema_monitor_update_existing(self):
        """Test updating existing monitored field."""
        monitor = SchemaMonitor()

        # First add
        monitor.schema_monitor(
            field_name="priority",
            usage_count=15,
            document_ids={"doc_1", "doc_2"},
        )

        # Update with more usage
        candidate = monitor.schema_monitor(
            field_name="priority",
            usage_count=25,
            document_ids={"doc_1", "doc_2", "doc_3", "doc_4", "doc_5"},
        )

        assert candidate.usage_count == 25
        assert candidate.status == PromotionStatus.READY

    def test_get_candidates_by_status(self):
        """Test filtering candidates by status."""
        monitor = SchemaMonitor()

        # Ready candidate
        monitor.schema_monitor(
            "priority",
            25,
            {"doc_1", "doc_2", "doc_3", "doc_4", "doc_5"},
        )

        # Not ready
        monitor.schema_monitor(
            "team",
            10,
            {"doc_1", "doc_2"},
        )

        ready = monitor.get_candidates(status=PromotionStatus.READY)
        assert len(ready) == 1
        assert ready[0].field_name == "priority"

        monitoring = monitor.get_candidates(status=PromotionStatus.MONITORING)
        assert len(monitoring) == 1
        assert monitoring[0].field_name == "team"

    def test_get_ready_for_promotion(self):
        """Test getting fields ready for promotion."""
        monitor = SchemaMonitor()

        # Add multiple ready fields
        for i in range(3):
            monitor.schema_monitor(
                f"field_{i}",
                25 + i,
                {f"doc_{j}" for j in range(5)},
            )

        # Add non-ready field
        monitor.schema_monitor(
            "not_ready",
            5,
            {"doc_1"},
        )

        ready = monitor.get_ready_for_promotion()
        assert len(ready) == 3
        assert all(c.status == PromotionStatus.READY for c in ready)

    def test_promote_field(self):
        """Test promoting a field to standard schema."""
        monitor = SchemaMonitor()

        monitor.schema_monitor(
            "priority",
            25,
            {"doc_1", "doc_2", "doc_3", "doc_4", "doc_5"},
        )

        success, error = monitor.promote_field("priority")
        assert success is True
        assert error is None
        assert monitor.candidates["priority"].status == PromotionStatus.PROMOTED

    def test_promote_field_not_ready(self):
        """Test promoting a field that's not ready."""
        monitor = SchemaMonitor()

        monitor.schema_monitor(
            "priority",
            10,  # Below threshold
            {"doc_1", "doc_2"},
        )

        success, error = monitor.promote_field("priority")
        assert success is False
        assert "not ready" in error.lower()

    def test_promote_field_already_promoted(self):
        """Test re-promoting already promoted field."""
        monitor = SchemaMonitor()

        monitor.schema_monitor(
            "priority",
            25,
            {"doc_1", "doc_2", "doc_3", "doc_4", "doc_5"},
        )

        monitor.promote_field("priority")
        success, error = monitor.promote_field("priority")

        assert success is False
        assert "already promoted" in error.lower()

    def test_archive_field(self):
        """Test archiving an inactive field."""
        monitor = SchemaMonitor()

        monitor.schema_monitor(
            "deprecated",
            5,
            {"doc_1"},
        )

        success, error = monitor.archive_field("deprecated", reason="no longer used")
        assert success is True
        assert monitor.candidates["deprecated"].status == PromotionStatus.ARCHIVED

    def test_get_promotion_candidates_summary(self):
        """Test getting summary of candidates."""
        monitor = SchemaMonitor()

        # Ready
        monitor.schema_monitor(
            "ready_1",
            25,
            {"doc_1", "doc_2", "doc_3", "doc_4", "doc_5"},
        )

        # Monitoring
        monitor.schema_monitor(
            "monitoring_1",
            10,
            {"doc_1", "doc_2"},
        )

        # Promote one
        monitor.promote_field("ready_1")

        summary = monitor.get_promotion_candidates_summary()

        assert len(summary["ready"]) == 0  # Promoted, not ready
        assert len(summary["promoted"]) == 1
        assert len(summary["monitoring"]) == 1

    def test_get_promotion_history(self):
        """Test getting promotion history."""
        monitor = SchemaMonitor()

        # Promote multiple fields
        for i in range(3):
            monitor.schema_monitor(
                f"field_{i}",
                25,
                {"doc_1", "doc_2", "doc_3", "doc_4", "doc_5"},
            )
            monitor.promote_field(f"field_{i}")

        history = monitor.get_promotion_history()
        assert len(history) == 3
        assert all("promotion_date" in entry for entry in history)

    def test_get_statistics_empty(self):
        """Test statistics on empty monitor."""
        monitor = SchemaMonitor()
        stats = monitor.get_statistics()

        assert stats["total_candidates"] == 0
        assert stats["promotion_rate"] == 0.0

    def test_get_statistics_populated(self):
        """Test statistics on populated monitor."""
        monitor = SchemaMonitor()

        # Add 5 ready, 3 monitoring, 2 promoted
        for i in range(5):
            monitor.schema_monitor(
                f"ready_{i}",
                25,
                {"doc_1", "doc_2", "doc_3", "doc_4", "doc_5"},
            )

        for i in range(3):
            monitor.schema_monitor(
                f"monitor_{i}",
                10,
                {"doc_1", "doc_2"},
            )

        for i in range(2):
            monitor.schema_monitor(
                f"promoted_{i}",
                25,
                {"doc_1", "doc_2", "doc_3", "doc_4", "doc_5"},
            )
            monitor.promote_field(f"promoted_{i}")

        stats = monitor.get_statistics()

        assert stats["total_candidates"] == 10
        assert stats["ready"] == 5
        assert stats["monitoring"] == 3
        assert stats["promoted"] == 2

    def test_export_candidates(self):
        """Test exporting candidates."""
        monitor = SchemaMonitor()

        monitor.schema_monitor("field_1", 30, {"doc_1", "doc_2", "doc_3"})
        monitor.schema_monitor("field_2", 20, {"doc_1", "doc_2"})

        exported = monitor.export_candidates()
        assert len(exported) == 2
        assert exported[0]["usage_count"] >= exported[1]["usage_count"]

    def test_get_promotion_readiness(self):
        """Test getting readiness assessment."""
        monitor = SchemaMonitor()

        # Ready field
        monitor.schema_monitor(
            "ready",
            25,
            {"doc_1", "doc_2", "doc_3", "doc_4", "doc_5"},
        )

        # Not ready
        monitor.schema_monitor(
            "not_ready",
            10,
            {"doc_1"},
        )

        readiness = monitor.get_promotion_readiness()

        assert readiness["ready"]["ready_for_promotion"] is True
        assert readiness["not_ready"]["ready_for_promotion"] is False
        assert "%" in readiness["not_ready"]["usage_readiness"]

    def test_field_threshold_boundary(self):
        """Test threshold boundary conditions."""
        monitor = SchemaMonitor()

        # Exactly at threshold (20 usage, 5 documents)
        candidate = monitor.schema_monitor(
            "boundary",
            20,
            {"doc_1", "doc_2", "doc_3", "doc_4", "doc_5"},
        )

        assert candidate.status == PromotionStatus.READY

        # Just below threshold
        candidate2 = monitor.schema_monitor(
            "almost",
            19,
            {"doc_1", "doc_2", "doc_3", "doc_4", "doc_5"},
        )

        assert candidate2.status == PromotionStatus.MONITORING

    def test_get_field_promotion_timeline(self):
        """Test promotion timeline."""
        monitor = SchemaMonitor()

        # Promote fields
        for i in range(3):
            monitor.schema_monitor(
                f"field_{i}",
                25,
                {"doc_1", "doc_2", "doc_3", "doc_4", "doc_5"},
            )
            monitor.promote_field(f"field_{i}")

        timeline = monitor.get_field_promotion_timeline()

        assert len(timeline) >= 1
        assert all(isinstance(date, str) for date in timeline.keys())

    def test_promotion_candidate_notes(self):
        """Test adding notes to candidates."""
        monitor = SchemaMonitor()

        candidate = monitor.schema_monitor(
            "priority",
            25,
            {"doc_1", "doc_2", "doc_3", "doc_4", "doc_5"},
            notes="Used across all career documents",
        )

        assert "career documents" in candidate.notes

    def test_complex_promotion_workflow(self):
        """Test complex workflow with multiple fields."""
        monitor = SchemaMonitor()

        # Monitor multiple fields
        fields = ["priority", "team", "status", "region", "category"]

        for i, field in enumerate(fields):
            monitor.schema_monitor(
                field,
                20 + i,  # Increasing usage
                {f"doc_{j}" for j in range(5 + i)},  # Increasing documents
            )

        # Promote top fields
        ready_fields = monitor.get_ready_for_promotion()
        for field in ready_fields[:2]:
            monitor.promote_field(field.field_name)

        # Check final state
        stats = monitor.get_statistics()
        assert stats["promoted"] >= 2
        assert stats["ready"] >= 2

        # Get readiness report
        readiness = monitor.get_promotion_readiness()
        assert len(readiness) >= 3
