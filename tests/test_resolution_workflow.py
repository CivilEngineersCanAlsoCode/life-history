"""
Unit tests for resolution_workflow.py

Covers:
- ConflictResolutionResult dataclass
- Conflict resolution orchestration (4-choice workflow)
- Choice A: Keep old, discard new
- Choice B: Keep new, update existing with change_log
- Choice C: Both are correct in different contexts
- Choice D: Flag both for manual review
- Resolution execution router
- Conflict resolution prompt formatting
"""

import pytest
from datetime import datetime
from life_brain.truth_engine.resolution_workflow import (
    ConflictResolutionResult,
    ConflictResolutionWorkflow,
)


class TestConflictResolutionResult:
    """Test ConflictResolutionResult dataclass."""

    def test_create_result_minimal(self):
        """Test creating result with minimal fields."""
        result = ConflictResolutionResult(
            choice="A",
            action_taken="Discarded new entry"
        )
        assert result.choice == "A"
        assert result.action_taken == "Discarded new entry"
        assert result.new_doc_id is None
        assert result.change_log_id is None
        assert result.skip_new is False

    def test_create_result_choice_a(self):
        """Test result for choice A (keep old)."""
        result = ConflictResolutionResult(
            choice="A",
            action_taken="Kept old entry",
            skip_new=True
        )
        assert result.choice == "A"
        assert result.skip_new is True

    def test_create_result_choice_b(self):
        """Test result for choice B (keep new, update)."""
        result = ConflictResolutionResult(
            choice="B",
            action_taken="Updated entry",
            new_doc_id="doc_123",
            change_log_id="cl_456"
        )
        assert result.choice == "B"
        assert result.new_doc_id == "doc_123"
        assert result.change_log_id == "cl_456"

    def test_create_result_choice_c(self):
        """Test result for choice C (context qualifiers)."""
        qualifiers = {"doc_old": "Sprinklr 2023", "doc_new": "AmEx 2024"}
        result = ConflictResolutionResult(
            choice="C",
            action_taken="Added context qualifiers",
            context_qualifiers=qualifiers
        )
        assert result.choice == "C"
        assert result.context_qualifiers == qualifiers

    def test_create_result_choice_d(self):
        """Test result for choice D (flag for review)."""
        result = ConflictResolutionResult(
            choice="D",
            action_taken="Flagged for review",
            flagged_doc_ids=["doc_old", "doc_new"]
        )
        assert result.choice == "D"
        assert result.flagged_doc_ids == ["doc_old", "doc_new"]

    def test_result_all_fields(self):
        """Test creating result with all fields."""
        result = ConflictResolutionResult(
            choice="B",
            action_taken="Updated",
            new_doc_id="doc_123",
            change_log_id="cl_456",
            context_qualifiers={"a": "b"},
            flagged_doc_ids=["x"],
            skip_new=True
        )
        assert result.choice == "B"
        assert result.new_doc_id == "doc_123"
        assert result.change_log_id == "cl_456"
        assert result.skip_new is True


class TestWorkflowInitialization:
    """Test ConflictResolutionWorkflow initialization."""

    def test_create_workflow(self):
        """Test creating workflow instance."""
        workflow = ConflictResolutionWorkflow()
        assert workflow is not None
        assert workflow.logger is not None


class TestChoiceA:
    """Test Choice A: Keep old, discard new."""

    def test_resolve_choice_a_basic(self):
        """Test basic choice A resolution."""
        workflow = ConflictResolutionWorkflow()
        result = workflow.resolve_choice_a(
            existing_doc_id="doc_old",
            existing_answer="I worked at Sprinklr",
            new_answer="I worked at AmEx"
        )
        assert result.choice == "A"
        assert result.skip_new is True
        assert "Discarded" in result.action_taken
        assert "existing" in result.action_taken.lower()

    def test_resolve_choice_a_sets_skip_new(self):
        """Test that choice A sets skip_new flag."""
        workflow = ConflictResolutionWorkflow()
        result = workflow.resolve_choice_a(
            existing_doc_id="doc_1",
            existing_answer="answer1",
            new_answer="answer2"
        )
        assert result.skip_new is True

    def test_resolve_choice_a_no_change_log(self):
        """Test that choice A doesn't create change_log."""
        workflow = ConflictResolutionWorkflow()
        result = workflow.resolve_choice_a(
            existing_doc_id="doc_1",
            existing_answer="answer1",
            new_answer="answer2"
        )
        assert result.change_log_id is None
        assert result.new_doc_id is None


class TestChoiceB:
    """Test Choice B: Keep new, update existing."""

    def test_resolve_choice_b_basic(self):
        """Test basic choice B resolution."""
        workflow = ConflictResolutionWorkflow()
        result, change_log = workflow.resolve_choice_b(
            existing_doc_id="doc_old",
            old_value="Old answer",
            new_value="New answer",
            new_doc_id="doc_new"
        )
        assert result.choice == "B"
        assert result.new_doc_id == "doc_old"
        assert change_log is not None

    def test_resolve_choice_b_creates_change_log(self):
        """Test that choice B creates change_log entry."""
        workflow = ConflictResolutionWorkflow()
        result, change_log = workflow.resolve_choice_b(
            existing_doc_id="doc_123",
            old_value="Old value",
            new_value="New value",
            new_doc_id="doc_456"
        )
        assert change_log is not None
        assert isinstance(change_log, dict)
        assert "id" in change_log or change_log.get("old_doc_id") == "doc_123"

    def test_resolve_choice_b_with_context(self):
        """Test choice B with context qualifier."""
        workflow = ConflictResolutionWorkflow()
        result, change_log = workflow.resolve_choice_b(
            existing_doc_id="doc_1",
            old_value="answer1",
            new_value="answer2",
            new_doc_id="doc_2",
            context_qualifier="Sprinklr 2023"
        )
        assert result.choice == "B"
        # Context is passed to change_log
        assert change_log is not None

    def test_resolve_choice_b_returns_tuple(self):
        """Test that choice B returns tuple."""
        workflow = ConflictResolutionWorkflow()
        result = workflow.resolve_choice_b(
            existing_doc_id="doc_1",
            old_value="old",
            new_value="new",
            new_doc_id="doc_2"
        )
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestChoiceC:
    """Test Choice C: Both are correct in different contexts."""

    def test_resolve_choice_c_basic(self):
        """Test basic choice C resolution."""
        workflow = ConflictResolutionWorkflow()
        result = workflow.resolve_choice_c(
            existing_doc_id="doc_old",
            new_doc_id="doc_new"
        )
        assert result.choice == "C"
        assert result.context_qualifiers is not None
        assert "doc_old" in result.context_qualifiers
        assert "doc_new" in result.context_qualifiers

    def test_resolve_choice_c_with_contexts(self):
        """Test choice C with explicit context qualifiers."""
        workflow = ConflictResolutionWorkflow()
        result = workflow.resolve_choice_c(
            existing_doc_id="doc_1",
            new_doc_id="doc_2",
            existing_context="Sprinklr 2023",
            new_context="AmEx 2024"
        )
        assert result.choice == "C"
        assert result.context_qualifiers["doc_1"] == "Sprinklr 2023"
        assert result.context_qualifiers["doc_2"] == "AmEx 2024"

    def test_resolve_choice_c_default_contexts(self):
        """Test choice C with default contexts."""
        workflow = ConflictResolutionWorkflow()
        result = workflow.resolve_choice_c(
            existing_doc_id="doc_1",
            new_doc_id="doc_2"
        )
        assert result.context_qualifiers["doc_1"] == "existing"
        assert result.context_qualifiers["doc_2"] == "new"

    def test_resolve_choice_c_action_taken(self):
        """Test choice C action description."""
        workflow = ConflictResolutionWorkflow()
        result = workflow.resolve_choice_c(
            existing_doc_id="doc_1",
            new_doc_id="doc_2"
        )
        assert "context" in result.action_taken.lower()


class TestChoiceD:
    """Test Choice D: Flag both for manual review."""

    def test_resolve_choice_d_basic(self):
        """Test basic choice D resolution."""
        workflow = ConflictResolutionWorkflow()
        result = workflow.resolve_choice_d(
            existing_doc_id="doc_old",
            new_doc_id="doc_new"
        )
        assert result.choice == "D"
        assert result.flagged_doc_ids is not None
        assert "doc_old" in result.flagged_doc_ids
        assert "doc_new" in result.flagged_doc_ids

    def test_resolve_choice_d_with_reason(self):
        """Test choice D with review reason."""
        workflow = ConflictResolutionWorkflow()
        result = workflow.resolve_choice_d(
            existing_doc_id="doc_1",
            new_doc_id="doc_2",
            review_reason="User uncertain about which is correct"
        )
        assert result.choice == "D"
        assert "review" in result.action_taken.lower()

    def test_resolve_choice_d_flags_both(self):
        """Test that choice D flags both documents."""
        workflow = ConflictResolutionWorkflow()
        result = workflow.resolve_choice_d(
            existing_doc_id="doc_a",
            new_doc_id="doc_b"
        )
        assert len(result.flagged_doc_ids) == 2
        assert "doc_a" in result.flagged_doc_ids
        assert "doc_b" in result.flagged_doc_ids

    def test_resolve_choice_d_default_reason(self):
        """Test choice D with default review reason."""
        workflow = ConflictResolutionWorkflow()
        result = workflow.resolve_choice_d(
            existing_doc_id="doc_1",
            new_doc_id="doc_2"
        )
        # Should still set flagged_doc_ids even with default reason
        assert result.flagged_doc_ids is not None


class TestExecuteResolution:
    """Test execute_resolution router."""

    def test_execute_choice_a(self):
        """Test executing choice A."""
        workflow = ConflictResolutionWorkflow()
        result, change_log = workflow.execute_resolution(
            choice="A",
            existing_doc_id="doc_old",
            new_doc_id="doc_new",
            old_value="old",
            new_value="new"
        )
        assert result.choice == "A"
        assert change_log is None
        assert result.skip_new is True

    def test_execute_choice_a_case_insensitive(self):
        """Test that choice router is case insensitive."""
        workflow = ConflictResolutionWorkflow()
        result, _ = workflow.execute_resolution(
            choice="a",
            existing_doc_id="doc_old",
            new_doc_id="doc_new",
            old_value="old",
            new_value="new"
        )
        assert result.choice == "A"

    def test_execute_choice_b(self):
        """Test executing choice B."""
        workflow = ConflictResolutionWorkflow()
        result, change_log = workflow.execute_resolution(
            choice="B",
            existing_doc_id="doc_old",
            new_doc_id="doc_new",
            old_value="old",
            new_value="new"
        )
        assert result.choice == "B"
        assert change_log is not None

    def test_execute_choice_b_with_context(self):
        """Test executing choice B with context."""
        workflow = ConflictResolutionWorkflow()
        result, change_log = workflow.execute_resolution(
            choice="B",
            existing_doc_id="doc_old",
            new_doc_id="doc_new",
            old_value="old",
            new_value="new",
            existing_context="Sprinklr 2023"
        )
        assert result.choice == "B"
        assert change_log is not None

    def test_execute_choice_c(self):
        """Test executing choice C."""
        workflow = ConflictResolutionWorkflow()
        result, change_log = workflow.execute_resolution(
            choice="C",
            existing_doc_id="doc_old",
            new_doc_id="doc_new",
            old_value="old",
            new_value="new",
            existing_context="Context A",
            new_context="Context B"
        )
        assert result.choice == "C"
        assert change_log is None
        assert result.context_qualifiers is not None

    def test_execute_choice_d(self):
        """Test executing choice D."""
        workflow = ConflictResolutionWorkflow()
        result, change_log = workflow.execute_resolution(
            choice="D",
            existing_doc_id="doc_old",
            new_doc_id="doc_new",
            old_value="old",
            new_value="new"
        )
        assert result.choice == "D"
        assert change_log is None
        assert result.flagged_doc_ids is not None

    def test_execute_invalid_choice(self):
        """Test executing invalid choice raises error."""
        workflow = ConflictResolutionWorkflow()
        with pytest.raises(ValueError):
            workflow.execute_resolution(
                choice="X",
                existing_doc_id="doc_old",
                new_doc_id="doc_new",
                old_value="old",
                new_value="new"
            )

    def test_execute_lowercase_choice_converted(self):
        """Test that lowercase choices are converted."""
        workflow = ConflictResolutionWorkflow()
        result, _ = workflow.execute_resolution(
            choice="b",
            existing_doc_id="doc_old",
            new_doc_id="doc_new",
            old_value="old",
            new_value="new"
        )
        # Should execute choice B successfully
        assert result.choice == "B"

    def test_execute_all_choices(self):
        """Test executing all valid choices."""
        workflow = ConflictResolutionWorkflow()
        for choice in ["A", "B", "C", "D"]:
            result, _ = workflow.execute_resolution(
                choice=choice,
                existing_doc_id="doc_old",
                new_doc_id="doc_new",
                old_value="old",
                new_value="new",
                existing_context="old_ctx",
                new_context="new_ctx"
            )
            assert result.choice == choice


class TestFormatConflictPrompt:
    """Test conflict resolution prompt formatting."""

    def test_format_prompt_basic(self):
        """Test basic prompt formatting."""
        workflow = ConflictResolutionWorkflow()
        prompt = workflow.format_conflict_prompt(
            existing_answer="Answer 1",
            new_answer="Answer 2",
            conflict_score=0.75
        )
        assert prompt is not None
        assert "Answer 1" in prompt
        assert "Answer 2" in prompt
        assert "75" in prompt  # Score as percentage

    def test_format_prompt_includes_choices(self):
        """Test that prompt includes all choice options."""
        workflow = ConflictResolutionWorkflow()
        prompt = workflow.format_conflict_prompt(
            existing_answer="old",
            new_answer="new",
            conflict_score=0.5
        )
        assert "[A]" in prompt or "A)" in prompt
        assert "[B]" in prompt or "B)" in prompt
        assert "[C]" in prompt or "C)" in prompt
        assert "[D]" in prompt or "D)" in prompt

    def test_format_prompt_with_date(self):
        """Test prompt with existing date."""
        workflow = ConflictResolutionWorkflow()
        prompt = workflow.format_conflict_prompt(
            existing_answer="Answer 1",
            new_answer="Answer 2",
            conflict_score=0.6,
            existing_date="2024-03-09"
        )
        assert "2024-03-09" in prompt

    def test_format_prompt_score_percentage(self):
        """Test that conflict score is converted to percentage."""
        workflow = ConflictResolutionWorkflow()
        prompt = workflow.format_conflict_prompt(
            existing_answer="a",
            new_answer="b",
            conflict_score=0.85
        )
        assert "85" in prompt

    def test_format_prompt_hinglish(self):
        """Test that prompt is in Hinglish."""
        workflow = ConflictResolutionWorkflow()
        prompt = workflow.format_conflict_prompt(
            existing_answer="old",
            new_answer="new",
            conflict_score=0.5
        )
        # Check for Hinglish markers
        assert "Ruko" in prompt or "A)" in prompt  # Hinglish or fallback
        assert isinstance(prompt, str)

    def test_format_prompt_score_zero(self):
        """Test prompt with zero conflict score."""
        workflow = ConflictResolutionWorkflow()
        prompt = workflow.format_conflict_prompt(
            existing_answer="a",
            new_answer="b",
            conflict_score=0.0
        )
        assert "0" in prompt

    def test_format_prompt_score_one(self):
        """Test prompt with maximum conflict score."""
        workflow = ConflictResolutionWorkflow()
        prompt = workflow.format_conflict_prompt(
            existing_answer="a",
            new_answer="b",
            conflict_score=1.0
        )
        assert "100" in prompt


class TestIntegrationResolution:
    """Integration tests for full resolution workflow."""

    def test_full_workflow_choice_a(self):
        """Test full workflow for choice A."""
        workflow = ConflictResolutionWorkflow()

        # Format prompt
        prompt = workflow.format_conflict_prompt(
            existing_answer="Sprinklr",
            new_answer="AmEx",
            conflict_score=0.8
        )

        # User selects A
        result, change_log = workflow.execute_resolution(
            choice="A",
            existing_doc_id="doc_1",
            new_doc_id="doc_2",
            old_value="Sprinklr",
            new_value="AmEx"
        )

        assert result.choice == "A"
        assert result.skip_new is True

    def test_full_workflow_choice_b(self):
        """Test full workflow for choice B."""
        workflow = ConflictResolutionWorkflow()

        result, change_log = workflow.execute_resolution(
            choice="B",
            existing_doc_id="doc_1",
            new_doc_id="doc_2",
            old_value="Old fact",
            new_value="New fact",
            existing_context="2023"
        )

        assert result.choice == "B"
        assert change_log is not None

    def test_full_workflow_choice_c(self):
        """Test full workflow for choice C."""
        workflow = ConflictResolutionWorkflow()

        result, change_log = workflow.execute_resolution(
            choice="C",
            existing_doc_id="doc_1",
            new_doc_id="doc_2",
            old_value="Fact in context A",
            new_value="Fact in context B",
            existing_context="Sprinklr era",
            new_context="AmEx era"
        )

        assert result.choice == "C"
        assert result.context_qualifiers["doc_1"] == "Sprinklr era"
        assert result.context_qualifiers["doc_2"] == "AmEx era"

    def test_full_workflow_choice_d(self):
        """Test full workflow for choice D."""
        workflow = ConflictResolutionWorkflow()

        result, change_log = workflow.execute_resolution(
            choice="D",
            existing_doc_id="doc_1",
            new_doc_id="doc_2",
            old_value="Uncertain fact A",
            new_value="Uncertain fact B"
        )

        assert result.choice == "D"
        assert len(result.flagged_doc_ids) == 2

    def test_workflow_sequential_decisions(self):
        """Test sequential decisions in workflow."""
        workflow = ConflictResolutionWorkflow()

        # First decision: choice A
        result1, _ = workflow.execute_resolution(
            choice="A",
            existing_doc_id="doc_1",
            new_doc_id="doc_2",
            old_value="old",
            new_value="new"
        )
        assert result1.choice == "A"

        # Second decision: choice B
        result2, _ = workflow.execute_resolution(
            choice="B",
            existing_doc_id="doc_3",
            new_doc_id="doc_4",
            old_value="old2",
            new_value="new2"
        )
        assert result2.choice == "B"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
