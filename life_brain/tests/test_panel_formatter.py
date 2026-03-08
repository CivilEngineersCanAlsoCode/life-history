"""Tests for panel_formatter.py — expert response labeling."""

import json
import pytest

from life_brain.conversation.panel_formatter import (
    PanelFormatter,
    PanelOutput,
    PanelResponse,
    OutputFormat,
)


@pytest.fixture
def formatter():
    return PanelFormatter()


@pytest.fixture
def simple_panel():
    return PanelOutput(
        question="What is success?",
        responses=[
            PanelResponse(expert_name="Elon Musk", response_text="Build rockets."),
            PanelResponse(expert_name="Warren Buffett", response_text="Compound slowly."),
        ],
    )


@pytest.fixture
def panel_with_roles():
    return PanelOutput(
        question="How to invest?",
        responses=[
            PanelResponse(expert_name="Warren Buffett", response_text="Buy and hold.", role="Lead"),
            PanelResponse(expert_name="Elon Musk", response_text="Bet on the future.", role="Contrarian"),
        ],
        moderator_note="Opposing views presented.",
    )


# ── PanelResponse.label() ───────────────────────────────────────────────────

class TestPanelResponseLabel:
    def test_first_name_only(self):
        r = PanelResponse(expert_name="Warren Buffett", response_text="x")
        assert r.label() == "Warren"

    def test_single_name(self):
        r = PanelResponse(expert_name="Satvik", response_text="x")
        assert r.label() == "Satvik"

    def test_with_role(self):
        r = PanelResponse(expert_name="Elon Musk", response_text="x", role="Lead")
        assert r.label() == "Elon (Lead)"

    def test_role_none(self):
        r = PanelResponse(expert_name="Steve Jobs", response_text="x", role=None)
        assert r.label() == "Steve"


# ── PanelOutput.to_dict() ───────────────────────────────────────────────────

class TestPanelOutputToDict:
    def test_structure(self, simple_panel):
        d = simple_panel.to_dict()
        assert d["question"] == "What is success?"
        assert len(d["responses"]) == 2
        assert d["moderator_note"] is None

    def test_response_fields(self, simple_panel):
        r = simple_panel.to_dict()["responses"][0]
        assert r["expert"] == "Elon Musk"
        assert r["label"] == "Elon"
        assert r["response"] == "Build rockets."
        assert r["role"] is None


# ── Markdown formatting ─────────────────────────────────────────────────────

class TestMarkdownFormat:
    def test_question_header(self, formatter, simple_panel):
        out = formatter.format(simple_panel)
        assert "**Question:** What is success?" in out

    def test_expert_labels(self, formatter, simple_panel):
        out = formatter.format(simple_panel)
        assert "**[Elon]:** Build rockets." in out
        assert "**[Warren]:** Compound slowly." in out

    def test_with_role_label(self, formatter, panel_with_roles):
        out = formatter.format(panel_with_roles)
        assert "**[Warren (Lead)]:**" in out
        assert "**[Elon (Contrarian)]:**" in out

    def test_moderator_note(self, formatter, panel_with_roles):
        out = formatter.format(panel_with_roles)
        assert "*Moderator: Opposing views presented.*" in out

    def test_no_moderator_when_absent(self, formatter, simple_panel):
        out = formatter.format(simple_panel)
        assert "Moderator" not in out

    def test_default_format_is_markdown(self, formatter, simple_panel):
        out_default = formatter.format(simple_panel)
        out_md = formatter.format(simple_panel, OutputFormat.MARKDOWN)
        assert out_default == out_md


# ── Plain text formatting ───────────────────────────────────────────────────

class TestPlainFormat:
    def test_no_bold_syntax(self, formatter, simple_panel):
        out = formatter.format(simple_panel, OutputFormat.PLAIN)
        assert "**" not in out
        assert "[Elon]: Build rockets." in out
        assert "[Warren]: Compound slowly." in out

    def test_question_prefix(self, formatter, simple_panel):
        out = formatter.format(simple_panel, OutputFormat.PLAIN)
        assert out.startswith("Question: What is success?")

    def test_moderator_note_plain(self, formatter, panel_with_roles):
        out = formatter.format(panel_with_roles, OutputFormat.PLAIN)
        assert "Note: Opposing views presented." in out


# ── JSON formatting ─────────────────────────────────────────────────────────

class TestJsonFormat:
    def test_valid_json(self, formatter, simple_panel):
        out = formatter.format(simple_panel, OutputFormat.JSON)
        data = json.loads(out)
        assert data["question"] == "What is success?"

    def test_json_response_count(self, formatter, simple_panel):
        out = formatter.format(simple_panel, OutputFormat.JSON)
        data = json.loads(out)
        assert len(data["responses"]) == 2

    def test_json_fields(self, formatter, simple_panel):
        out = formatter.format(simple_panel, OutputFormat.JSON)
        data = json.loads(out)
        r = data["responses"][0]
        assert "expert" in r and "label" in r and "response" in r


# ── format_single_response() ────────────────────────────────────────────────

class TestFormatSingleResponse:
    def test_markdown(self, formatter):
        out = formatter.format_single_response("Elon Musk", "Build it.", fmt=OutputFormat.MARKDOWN)
        assert out == "**[Elon]:** Build it."

    def test_plain(self, formatter):
        out = formatter.format_single_response("Warren Buffett", "Invest.", fmt=OutputFormat.PLAIN)
        assert out == "[Warren]: Invest."

    def test_with_role(self, formatter):
        out = formatter.format_single_response("Steve Jobs", "Think different.", role="Visionary")
        assert "Steve (Visionary)" in out


# ── format_responses_list() ─────────────────────────────────────────────────

class TestFormatResponsesList:
    def test_basic(self, formatter):
        responses = [
            {"expert": "Elon Musk", "response": "First."},
            {"expert": "Warren Buffett", "response": "Second."},
        ]
        out = formatter.format_responses_list(responses)
        assert "**[Elon]:** First." in out
        assert "**[Warren]:** Second." in out

    def test_plain_mode(self, formatter):
        responses = [{"expert": "Steve Jobs", "response": "Think."}]
        out = formatter.format_responses_list(responses, OutputFormat.PLAIN)
        assert "[Steve]: Think." in out

    def test_with_role(self, formatter):
        responses = [{"expert": "Elon Musk", "response": "X.", "role": "Lead"}]
        out = formatter.format_responses_list(responses)
        assert "Elon (Lead)" in out

    def test_missing_expert_defaults(self, formatter):
        responses = [{"response": "Anonymous."}]
        out = formatter.format_responses_list(responses)
        assert "[Expert]:" in out

    def test_double_newline_separator(self, formatter):
        responses = [
            {"expert": "A Expert", "response": "First."},
            {"expert": "B Expert", "response": "Second."},
        ]
        out = formatter.format_responses_list(responses)
        assert "\n\n" in out


class TestNullExpertResponseBug:
    """Regression tests for issues-ly2.20.4: null expert response crashes formatter.

    Bug: PanelFormatter crashes when expert_name is None or response_text is None.
    Fix: __post_init__ defaults, label() guard, format_responses_list() uses `or`.
    """

    def test_null_response_text_does_not_crash(self):
        """PanelResponse with None response_text should default to empty string."""
        resp = PanelResponse(expert_name="Elon Musk", response_text=None)
        assert resp.response_text == ""

    def test_null_expert_name_defaults_to_expert(self):
        """PanelResponse with None expert_name should default to 'Expert'."""
        resp = PanelResponse(expert_name=None, response_text="hello")
        assert resp.expert_name == "Expert"

    def test_empty_expert_name_defaults(self):
        """PanelResponse with empty string expert_name should default."""
        resp = PanelResponse(expert_name="", response_text="hi")
        assert resp.expert_name == "Expert"

    def test_format_with_null_response_text(self):
        """Formatter should not crash when response_text is None."""
        formatter = PanelFormatter()
        panel = PanelOutput(
            question="Q?",
            responses=[PanelResponse(expert_name="Alice", response_text=None)],
        )
        out = formatter.format(panel)
        assert "[Alice]:" in out  # Should render without crash

    def test_format_responses_list_null_response(self):
        """format_responses_list should handle null 'response' value."""
        formatter = PanelFormatter()
        responses = [{"expert": "Bob", "response": None}]
        out = formatter.format_responses_list(responses)
        assert "[Bob]:" in out  # No crash

    def test_format_responses_list_null_expert(self):
        """format_responses_list should handle null 'expert' value."""
        formatter = PanelFormatter()
        responses = [{"expert": None, "response": "Some response"}]
        out = formatter.format_responses_list(responses)
        assert "[Expert]:" in out
