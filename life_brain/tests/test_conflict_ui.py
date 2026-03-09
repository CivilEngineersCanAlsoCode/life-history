"""
Tests for conflict blocking/warning UI prompts.

Tests cover:
- HARD conflict blocking prompt format
- SOFT conflict warning prompt format
- ENRICHMENT informational prompt
- SAFE → no prompt
- Severity routing via get_conflict_prompt()
- is_valid_resolution_choice()
- Prompt content accuracy
"""

import pytest

from life_brain.truth.conflict_ui import (
    ConflictPrompt,
    format_hard_conflict_prompt,
    format_soft_conflict_prompt,
    format_enrichment_prompt,
    get_conflict_prompt,
    is_valid_resolution_choice,
)


OLD = "I led the team as a PM"
NEW = "I was a support engineer on the team"


class TestHardConflictPrompt:
    """Test HARD (blocking) conflict prompts."""

    def test_hard_prompt_is_blocking(self):
        prompt = format_hard_conflict_prompt(OLD, NEW, 0.75)
        assert prompt.is_blocking is True

    def test_hard_prompt_severity(self):
        prompt = format_hard_conflict_prompt(OLD, NEW, 0.75)
        assert prompt.severity == "HARD"

    def test_hard_prompt_shows_score(self):
        prompt = format_hard_conflict_prompt(OLD, NEW, 0.75)
        assert "75%" in prompt.full_prompt

    def test_hard_prompt_shows_both_answers(self):
        prompt = format_hard_conflict_prompt(OLD, NEW, 0.75)
        assert OLD in prompt.full_prompt
        assert NEW in prompt.full_prompt

    def test_hard_prompt_has_all_four_options(self):
        prompt = format_hard_conflict_prompt(OLD, NEW, 0.75)
        assert "[A]" in prompt.resolution_options
        assert "[B]" in prompt.resolution_options
        assert "[C]" in prompt.resolution_options
        assert "[D]" in prompt.resolution_options

    def test_hard_prompt_no_skip_option(self):
        """HARD conflicts should not have skip option."""
        prompt = format_hard_conflict_prompt(OLD, NEW, 0.75)
        assert "[S]" not in prompt.resolution_options

    def test_hard_prompt_with_date(self):
        prompt = format_hard_conflict_prompt(OLD, NEW, 0.75, existing_date="2024-01-15")
        assert "2024-01-15" in prompt.full_prompt

    def test_hard_prompt_without_date(self):
        prompt = format_hard_conflict_prompt(OLD, NEW, 0.75)
        # Date should not appear (the "stored: <date>" part)
        assert "stored:" not in prompt.existing_answer

    def test_hard_prompt_conflict_score_stored(self):
        prompt = format_hard_conflict_prompt(OLD, NEW, 0.82)
        assert prompt.conflict_score_pct == 82

    def test_hard_prompt_action_required_text(self):
        prompt = format_hard_conflict_prompt(OLD, NEW, 0.75)
        assert "Action required" in prompt.header or "required" in prompt.full_prompt.lower()


class TestSoftConflictPrompt:
    """Test SOFT (warning) conflict prompts."""

    def test_soft_prompt_not_blocking(self):
        prompt = format_soft_conflict_prompt(OLD, NEW, 0.45)
        assert prompt.is_blocking is False

    def test_soft_prompt_severity(self):
        prompt = format_soft_conflict_prompt(OLD, NEW, 0.45)
        assert prompt.severity == "SOFT"

    def test_soft_prompt_has_skip_option(self):
        """SOFT conflicts should include skip option."""
        prompt = format_soft_conflict_prompt(OLD, NEW, 0.45)
        assert "[S]" in prompt.resolution_options

    def test_soft_prompt_shows_score(self):
        prompt = format_soft_conflict_prompt(OLD, NEW, 0.45)
        assert "45%" in prompt.full_prompt

    def test_soft_prompt_shows_both_answers(self):
        prompt = format_soft_conflict_prompt(OLD, NEW, 0.45)
        assert OLD in prompt.full_prompt
        assert NEW in prompt.full_prompt

    def test_soft_prompt_optional_text(self):
        prompt = format_soft_conflict_prompt(OLD, NEW, 0.45)
        assert "Optional" in prompt.header or "optional" in prompt.full_prompt.lower()

    def test_soft_prompt_with_date(self):
        prompt = format_soft_conflict_prompt(OLD, NEW, 0.45, existing_date="2023-06")
        assert "2023-06" in prompt.full_prompt


class TestEnrichmentPrompt:
    """Test ENRICHMENT informational prompts."""

    def test_enrichment_not_blocking(self):
        prompt = format_enrichment_prompt(OLD, NEW, 0.15)
        assert prompt.is_blocking is False

    def test_enrichment_severity(self):
        prompt = format_enrichment_prompt(OLD, NEW, 0.15)
        assert prompt.severity == "ENRICHMENT"

    def test_enrichment_no_resolution_options(self):
        prompt = format_enrichment_prompt(OLD, NEW, 0.15)
        assert prompt.resolution_options == ""

    def test_enrichment_auto_proceeds(self):
        prompt = format_enrichment_prompt(OLD, NEW, 0.15)
        assert "auto" in prompt.full_prompt.lower()

    def test_enrichment_shows_score(self):
        prompt = format_enrichment_prompt(OLD, NEW, 0.15)
        assert "15%" in prompt.full_prompt


class TestGetConflictPrompt:
    """Test routing to correct prompt type."""

    def test_conflict_status_returns_hard(self):
        prompt = get_conflict_prompt("CONFLICT", OLD, NEW, 0.75)
        assert prompt is not None
        assert prompt.severity == "HARD"
        assert prompt.is_blocking is True

    def test_soft_status_returns_soft(self):
        prompt = get_conflict_prompt("SOFT", OLD, NEW, 0.45)
        assert prompt is not None
        assert prompt.severity == "SOFT"
        assert prompt.is_blocking is False

    def test_enrichment_status_returns_enrichment(self):
        prompt = get_conflict_prompt("ENRICHMENT", OLD, NEW, 0.15)
        assert prompt is not None
        assert prompt.severity == "ENRICHMENT"

    def test_safe_status_returns_none(self):
        """SAFE should return no prompt — silent auto-proceed."""
        prompt = get_conflict_prompt("SAFE", OLD, NEW, 0.05)
        assert prompt is None

    def test_unknown_status_returns_none(self):
        prompt = get_conflict_prompt("UNKNOWN", OLD, NEW, 0.0)
        assert prompt is None


class TestIsValidResolutionChoice:
    """Test resolution choice validation."""

    def test_abcd_valid_for_hard(self):
        for choice in ["A", "B", "C", "D"]:
            assert is_valid_resolution_choice(choice, "HARD") is True

    def test_s_invalid_for_hard(self):
        assert is_valid_resolution_choice("S", "HARD") is False

    def test_abcds_valid_for_soft(self):
        for choice in ["A", "B", "C", "D", "S"]:
            assert is_valid_resolution_choice(choice, "SOFT") is True

    def test_lowercase_valid(self):
        assert is_valid_resolution_choice("a", "HARD") is True
        assert is_valid_resolution_choice("b", "SOFT") is True

    def test_invalid_choice(self):
        assert is_valid_resolution_choice("X", "HARD") is False
        assert is_valid_resolution_choice("1", "SOFT") is False
        assert is_valid_resolution_choice("", "HARD") is False

    def test_whitespace_stripped(self):
        assert is_valid_resolution_choice("  A  ", "HARD") is True
