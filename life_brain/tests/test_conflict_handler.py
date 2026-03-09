"""
Unit tests for conflict_handler.py

Covers:
- ConflictHandler initialization
- Hard conflict handling (CONFLICT > 0.6)
- Soft conflict handling (0.3 < SOFT <= 0.6)
- Enrichment handling (0.1 < ENRICHMENT <= 0.3)
- Safe handling (SAFE <= 0.1)
- Status-based routing
- Resolution summary formatting
"""

import pytest
from life_brain.truth.conflict import ConflictResult
from life_brain.truth.resolution_workflow import ConflictResolutionResult
from life_brain.truth.conflict_handler import ConflictHandler


class TestConflictHandlerInit:
    """Test ConflictHandler initialization."""

    def test_create_handler(self):
        """Test creating conflict handler."""
        handler = ConflictHandler()
        assert handler is not None
        assert handler.workflow is not None

    def test_handler_has_workflow(self):
        """Test that handler has workflow attribute."""
        handler = ConflictHandler()
        assert hasattr(handler, "workflow")
        from life_brain.truth.resolution_workflow import ConflictResolutionWorkflow
        assert isinstance(handler.workflow, ConflictResolutionWorkflow)


class TestHandleHardConflict:
    """Test hard conflict handling."""

    def test_handle_hard_conflict_choice_a(self):
        """Test hard conflict with choice A (keep old)."""
        handler = ConflictHandler()
        conflict = ConflictResult(
            status="CONFLICT",
            conflict_score=0.75,
            existing_pair_id="doc_old",
            existing_answer="Old fact"
        )
        result, artifact = handler.handle_hard_conflict(
            conflict, "doc_new", "New fact", user_choice="A"
        )
        assert result.choice == "A"
        assert result.skip_new is True

    def test_handle_hard_conflict_choice_b(self):
        """Test hard conflict with choice B (keep new, update)."""
        handler = ConflictHandler()
        conflict = ConflictResult(
            status="CONFLICT",
            conflict_score=0.8,
            existing_pair_id="doc_old",
            existing_answer="Old fact"
        )
        result, artifact = handler.handle_hard_conflict(
            conflict, "doc_new", "New fact", user_choice="B"
        )
        assert result.choice == "B"
        assert artifact is not None

    def test_handle_hard_conflict_choice_c(self):
        """Test hard conflict with choice C (context-qualify both)."""
        handler = ConflictHandler()
        conflict = ConflictResult(
            status="CONFLICT",
            conflict_score=0.7,
            existing_pair_id="doc_old",
            existing_answer="Old fact",
            existing_context="Sprinklr era"
        )
        result, artifact = handler.handle_hard_conflict(
            conflict, "doc_new", "New fact", user_choice="C"
        )
        assert result.choice == "C"
        assert result.context_qualifiers is not None

    def test_handle_hard_conflict_choice_d(self):
        """Test hard conflict with choice D (flag for review)."""
        handler = ConflictHandler()
        conflict = ConflictResult(
            status="CONFLICT",
            conflict_score=0.85,
            existing_pair_id="doc_old",
            existing_answer="Old fact"
        )
        result, artifact = handler.handle_hard_conflict(
            conflict, "doc_new", "New fact", user_choice="D"
        )
        assert result.choice == "D"
        assert result.flagged_doc_ids is not None

    def test_handle_hard_conflict_default_choice(self):
        """Test hard conflict with default choice."""
        handler = ConflictHandler()
        conflict = ConflictResult(
            status="CONFLICT",
            conflict_score=0.75,
            existing_pair_id="doc_old",
            existing_answer="Old fact"
        )
        result, artifact = handler.handle_hard_conflict(
            conflict, "doc_new", "New fact"
        )
        # Default is "D"
        assert result.choice == "D"
        assert result.flagged_doc_ids is not None

    def test_handle_hard_conflict_returns_tuple(self):
        """Test that hard conflict returns tuple."""
        handler = ConflictHandler()
        conflict = ConflictResult(
            status="CONFLICT",
            conflict_score=0.75,
            existing_pair_id="doc_old",
            existing_answer="Old fact"
        )
        result = handler.handle_hard_conflict(
            conflict, "doc_new", "New fact"
        )
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_handle_hard_conflict_with_existing_doc_id(self):
        """Test hard conflict with existing_doc_id fallback."""
        handler = ConflictHandler()
        conflict = ConflictResult(
            status="CONFLICT",
            conflict_score=0.75,
            existing_doc_id="doc_via_alias",
            existing_answer="Old fact"
        )
        result, artifact = handler.handle_hard_conflict(
            conflict, "doc_new", "New fact", user_choice="A"
        )
        assert result.choice == "A"


class TestHandleSoftConflict:
    """Test soft conflict handling."""

    def test_handle_soft_conflict_auto_proceed(self):
        """Test soft conflict with auto-proceed."""
        handler = ConflictHandler()
        conflict = ConflictResult(
            status="SOFT",
            conflict_score=0.45,
            existing_pair_id="doc_old",
            existing_answer="Old fact"
        )
        result, artifact = handler.handle_soft_conflict(
            conflict, "doc_new", "New fact", auto_proceed=True
        )
        assert result.choice == "AUTO_PROCEED"
        assert artifact is None
        assert "Soft conflict" in result.action_taken.lower() or "soft" in result.action_taken.lower()

    def test_handle_soft_conflict_no_auto_proceed(self):
        """Test soft conflict without auto-proceed."""
        handler = ConflictHandler()
        conflict = ConflictResult(
            status="SOFT",
            conflict_score=0.45,
            existing_pair_id="doc_old",
            existing_answer="Old fact"
        )
        result, artifact = handler.handle_soft_conflict(
            conflict, "doc_new", "New fact", auto_proceed=False
        )
        # Should ask user (choice D by default)
        assert result.choice == "D"

    def test_handle_soft_conflict_returns_tuple(self):
        """Test that soft conflict returns tuple."""
        handler = ConflictHandler()
        conflict = ConflictResult(
            status="SOFT",
            conflict_score=0.45,
            existing_pair_id="doc_old",
            existing_answer="Old fact"
        )
        result = handler.handle_soft_conflict(conflict, "doc_new", "New fact")
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestHandleEnrichment:
    """Test enrichment handling."""

    def test_handle_enrichment(self):
        """Test enrichment handling."""
        handler = ConflictHandler()
        conflict = ConflictResult(
            status="ENRICHMENT",
            conflict_score=0.2,
            existing_pair_id="doc_old",
            existing_answer="Old fact"
        )
        result, artifact = handler.handle_enrichment(conflict, "New detailed fact")
        assert result.choice == "AUTO_ENRICH"
        assert artifact is None
        assert "enrich" in result.action_taken.lower() or "Enrichment" in result.action_taken

    def test_handle_enrichment_returns_tuple(self):
        """Test that enrichment returns tuple."""
        handler = ConflictHandler()
        conflict = ConflictResult(
            status="ENRICHMENT",
            conflict_score=0.15,
            existing_pair_id="doc_old",
            existing_answer="Old fact"
        )
        result = handler.handle_enrichment(conflict, "New fact")
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestHandleSafe:
    """Test safe conflict handling."""

    def test_handle_safe(self):
        """Test safe handling."""
        handler = ConflictHandler()
        result = handler.handle_safe()
        assert result.choice == "SAFE"
        assert "No conflict" in result.action_taken
        assert result.change_log_id is None

    def test_handle_safe_returns_result(self):
        """Test that safe returns ConflictResolutionResult."""
        handler = ConflictHandler()
        result = handler.handle_safe()
        assert isinstance(result, ConflictResolutionResult)


class TestHandleByStatus:
    """Test status-based routing."""

    def test_route_conflict(self):
        """Test routing CONFLICT status."""
        handler = ConflictHandler()
        conflict = ConflictResult(
            status="CONFLICT",
            conflict_score=0.75,
            existing_pair_id="doc_old",
            existing_answer="Old fact"
        )
        result, artifact = handler.handle_by_status(
            conflict, "doc_new", "New fact", user_choice_for_hard="A"
        )
        assert result.choice == "A"

    def test_route_soft(self):
        """Test routing SOFT status."""
        handler = ConflictHandler()
        conflict = ConflictResult(
            status="SOFT",
            conflict_score=0.45,
            existing_pair_id="doc_old",
            existing_answer="Old fact"
        )
        result, artifact = handler.handle_by_status(
            conflict, "doc_new", "New fact"
        )
        assert result.choice == "AUTO_PROCEED"

    def test_route_enrichment(self):
        """Test routing ENRICHMENT status."""
        handler = ConflictHandler()
        conflict = ConflictResult(
            status="ENRICHMENT",
            conflict_score=0.2,
            existing_pair_id="doc_old",
            existing_answer="Old fact"
        )
        result, artifact = handler.handle_by_status(
            conflict, "doc_new", "New fact"
        )
        assert result.choice == "AUTO_ENRICH"

    def test_route_safe(self):
        """Test routing SAFE status."""
        handler = ConflictHandler()
        conflict = ConflictResult(
            status="SAFE",
            conflict_score=0.05
        )
        result, artifact = handler.handle_by_status(
            conflict, "doc_new", "New fact"
        )
        assert result.choice == "SAFE"
        assert artifact is None

    def test_route_invalid_status(self):
        """Test routing invalid status raises error."""
        handler = ConflictHandler()
        conflict = ConflictResult(
            status="INVALID",
            conflict_score=0.5
        )
        with pytest.raises(ValueError):
            handler.handle_by_status(conflict, "doc_new", "New fact")

    def test_route_all_statuses(self):
        """Test routing all valid statuses."""
        handler = ConflictHandler()
        statuses = ["CONFLICT", "SOFT", "ENRICHMENT", "SAFE"]

        for status in statuses:
            conflict = ConflictResult(
                status=status,
                conflict_score=0.5 if status != "CONFLICT" else 0.75,
                existing_pair_id="doc_old",
                existing_answer="Old fact"
            )
            result, artifact = handler.handle_by_status(
                conflict, "doc_new", "New fact", user_choice_for_hard="D"
            )
            assert result is not None


class TestResolutionSummary:
    """Test resolution summary formatting."""

    def test_format_summary_choice_a(self):
        """Test summary formatting for choice A."""
        handler = ConflictHandler()
        result = ConflictResolutionResult(
            choice="A",
            action_taken="Kept old entry"
        )
        summary = handler.format_resolution_summary(result)
        assert "Conflict Resolution Summary" in summary
        assert "A" in summary or "Purani" in summary

    def test_format_summary_choice_b(self):
        """Test summary formatting for choice B."""
        handler = ConflictHandler()
        result = ConflictResolutionResult(
            choice="B",
            action_taken="Updated entry",
            new_doc_id="doc_updated",
            change_log_id="cl_123"
        )
        summary = handler.format_resolution_summary(result)
        assert "Conflict Resolution Summary" in summary
        assert "doc_updated" in summary
        assert "cl_123" in summary

    def test_format_summary_choice_c(self):
        """Test summary formatting for choice C."""
        handler = ConflictHandler()
        result = ConflictResolutionResult(
            choice="C",
            action_taken="Added context",
            context_qualifiers={"doc_1": "Sprinklr", "doc_2": "AmEx"}
        )
        summary = handler.format_resolution_summary(result)
        assert "Conflict Resolution Summary" in summary
        assert "Sprinklr" in summary or "Context" in summary

    def test_format_summary_choice_d(self):
        """Test summary formatting for choice D."""
        handler = ConflictHandler()
        result = ConflictResolutionResult(
            choice="D",
            action_taken="Flagged for review",
            flagged_doc_ids=["doc_old", "doc_new"]
        )
        summary = handler.format_resolution_summary(result)
        assert "Conflict Resolution Summary" in summary
        assert "doc_old" in summary or "Flagged" in summary

    def test_format_summary_auto_proceed(self):
        """Test summary formatting for auto-proceed."""
        handler = ConflictHandler()
        result = ConflictResolutionResult(
            choice="AUTO_PROCEED",
            action_taken="Proceeded with soft conflict"
        )
        summary = handler.format_resolution_summary(result)
        assert "Conflict Resolution Summary" in summary

    def test_format_summary_auto_enrich(self):
        """Test summary formatting for auto-enrich."""
        handler = ConflictHandler()
        result = ConflictResolutionResult(
            choice="AUTO_ENRICH",
            action_taken="Auto-enriched entry"
        )
        summary = handler.format_resolution_summary(result)
        assert "Conflict Resolution Summary" in summary

    def test_format_summary_safe(self):
        """Test summary formatting for safe."""
        handler = ConflictHandler()
        result = ConflictResolutionResult(
            choice="SAFE",
            action_taken="No conflict, proceeding"
        )
        summary = handler.format_resolution_summary(result)
        assert "Conflict Resolution Summary" in summary
        assert "SAFE" in summary or "Koi conflict" in summary

    def test_format_summary_includes_status(self):
        """Test that summary includes done status."""
        handler = ConflictHandler()
        result = ConflictResolutionResult(
            choice="A",
            action_taken="Done"
        )
        summary = handler.format_resolution_summary(result)
        assert "Status:" in summary or "✓ Done" in summary


class TestIntegrationConflictHandler:
    """Integration tests for conflict handler."""

    def test_full_workflow_hard_conflict(self):
        """Test full workflow for hard conflict."""
        handler = ConflictHandler()

        # Detect conflict
        conflict = ConflictResult(
            status="CONFLICT",
            conflict_score=0.8,
            existing_pair_id="doc_old",
            existing_answer="Old answer"
        )

        # Handle conflict
        result, artifact = handler.handle_by_status(
            conflict, "doc_new", "New answer", user_choice_for_hard="B"
        )

        # Format summary
        summary = handler.format_resolution_summary(result)

        assert result.choice == "B"
        assert "Conflict Resolution Summary" in summary

    def test_full_workflow_soft_conflict(self):
        """Test full workflow for soft conflict."""
        handler = ConflictHandler()

        conflict = ConflictResult(
            status="SOFT",
            conflict_score=0.45,
            existing_pair_id="doc_old",
            existing_answer="Old answer"
        )

        result, artifact = handler.handle_by_status(
            conflict, "doc_new", "New answer"
        )

        summary = handler.format_resolution_summary(result)

        assert result.choice == "AUTO_PROCEED"
        assert "Conflict Resolution Summary" in summary

    def test_full_workflow_enrichment(self):
        """Test full workflow for enrichment."""
        handler = ConflictHandler()

        conflict = ConflictResult(
            status="ENRICHMENT",
            conflict_score=0.2,
            existing_pair_id="doc_old",
            existing_answer="Existing detail"
        )

        result, artifact = handler.handle_by_status(
            conflict, "doc_new", "More detailed info"
        )

        summary = handler.format_resolution_summary(result)

        assert result.choice == "AUTO_ENRICH"
        assert "Conflict Resolution Summary" in summary

    def test_full_workflow_safe(self):
        """Test full workflow for safe."""
        handler = ConflictHandler()

        conflict = ConflictResult(
            status="SAFE",
            conflict_score=0.05
        )

        result, artifact = handler.handle_by_status(
            conflict, "doc_new", "New answer"
        )

        summary = handler.format_resolution_summary(result)

        assert result.choice == "SAFE"
        assert "Conflict Resolution Summary" in summary

    def test_multiple_conflicts_sequential(self):
        """Test handling multiple conflicts sequentially."""
        handler = ConflictHandler()

        conflicts = [
            ConflictResult(status="CONFLICT", conflict_score=0.75, existing_pair_id="doc_1", existing_answer="old"),
            ConflictResult(status="SOFT", conflict_score=0.45, existing_pair_id="doc_2", existing_answer="old"),
            ConflictResult(status="ENRICHMENT", conflict_score=0.2, existing_pair_id="doc_3", existing_answer="old"),
            ConflictResult(status="SAFE", conflict_score=0.05),
        ]

        results = []
        for i, conflict in enumerate(conflicts):
            result, artifact = handler.handle_by_status(
                conflict, f"doc_new_{i}", f"new_{i}", user_choice_for_hard="D"
            )
            results.append(result)

        assert len(results) == 4
        assert results[0].choice == "D"  # Hard conflict
        assert results[1].choice == "AUTO_PROCEED"  # Soft
        assert results[2].choice == "AUTO_ENRICH"  # Enrichment
        assert results[3].choice == "SAFE"  # Safe


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
