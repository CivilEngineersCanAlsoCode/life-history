"""
Test suite for response formatter.

Tests cover:
- Single response formatting
- Panel aggregation
- Multiple output formats
- Label styles
- Format statistics
- Reformatting capabilities
"""

import pytest

from life_brain.conversation.response_formatter import (
    ResponseFormatter,
    OutputFormat,
    LabelStyle,
    FormattedResponse,
    FormattedPanel,
)
from life_brain.conversation.panel_router import (
    ExpertResponse,
    PanelRole,
    PanelRouter,
    PanelQuestion,
    PanelSession,
)


class TestFormattedResponse:
    """Test FormattedResponse dataclass."""

    def test_create_formatted_response(self):
        """Test creating formatted response."""
        raw = ExpertResponse(
            expert_name="Satya",
            expert_domain="interviews",
            role=PanelRole.PRIMARY,
            response_text="Let's practice",
            confidence=0.8,
        )

        formatted = FormattedResponse(
            expert_name="Satya",
            expert_domain="interviews",
            role="primary",
            formatted_text="### Satya\nLet's practice",
            raw_response=raw,
            format_type=OutputFormat.MARKDOWN,
        )

        assert formatted.expert_name == "Satya"
        assert formatted.format_type == OutputFormat.MARKDOWN

    def test_to_dict(self):
        """Test converting formatted response to dict."""
        raw = ExpertResponse(
            expert_name="Richard",
            expert_domain="first_principles",
            role=PanelRole.CHALLENGER,
            response_text="Break it down",
            confidence=0.9,
        )

        formatted = FormattedResponse(
            expert_name="Richard",
            expert_domain="first_principles",
            role="challenger",
            formatted_text="Text",
            raw_response=raw,
            format_type=OutputFormat.TEXT,
        )

        d = formatted.to_dict()
        assert d["expert_name"] == "Richard"
        assert d["format_type"] == "text"


class TestFormattedPanel:
    """Test FormattedPanel dataclass."""

    def test_create_formatted_panel(self):
        """Test creating formatted panel."""
        panel = FormattedPanel(
            session_id="s_001",
            question="How do I lead?",
            format_type=OutputFormat.MARKDOWN,
        )

        assert panel.session_id == "s_001"
        assert panel.question == "How do I lead?"

    def test_to_dict(self):
        """Test converting formatted panel to dict."""
        panel = FormattedPanel(
            session_id="s_002",
            question="Scale question",
            format_type=OutputFormat.HTML,
        )

        d = panel.to_dict()
        assert d["session_id"] == "s_002"
        assert d["format_type"] == "html"


class TestResponseFormatter:
    """Test ResponseFormatter functionality."""

    def test_create_formatter(self):
        """Test creating formatter."""
        formatter = ResponseFormatter()
        assert len(formatter.formatted_panels) == 0
        assert len(formatter.format_history) == 0

    def test_format_single_response_markdown(self):
        """Test formatting single response in markdown."""
        formatter = ResponseFormatter()

        response = ExpertResponse(
            expert_name="Satya",
            expert_domain="interviews",
            role=PanelRole.PRIMARY,
            response_text="Practice mock interviews",
            confidence=0.85,
            key_insights=["Listening matters"],
        )

        formatted = formatter.format_response(
            response, OutputFormat.MARKDOWN, LabelStyle.STANDARD
        )

        assert formatted.expert_name == "Satya"
        assert "Satya" in formatted.formatted_text
        assert "interviews" in formatted.formatted_text

    def test_format_single_response_plain_text(self):
        """Test formatting in plain text."""
        formatter = ResponseFormatter()

        response = ExpertResponse(
            expert_name="Richard",
            expert_domain="first_principles",
            role=PanelRole.CHALLENGER,
            response_text="Break down the problem",
            confidence=0.9,
        )

        formatted = formatter.format_response(
            response, OutputFormat.TEXT, LabelStyle.MINIMAL
        )

        assert "Richard" in formatted.formatted_text
        assert "Break down" in formatted.formatted_text

    def test_format_single_response_html(self):
        """Test formatting in HTML."""
        formatter = ResponseFormatter()

        response = ExpertResponse(
            expert_name="Jeff",
            expert_domain="scale",
            role=PanelRole.PRIMARY,
            response_text="Think long term",
            confidence=0.8,
        )

        formatted = formatter.format_response(
            response, OutputFormat.HTML, LabelStyle.STANDARD
        )

        assert "<div" in formatted.formatted_text or "<h" in formatted.formatted_text

    def test_format_single_response_labeled_text(self):
        """Test formatting with labeled text style."""
        formatter = ResponseFormatter()

        response = ExpertResponse(
            expert_name="Indra",
            expert_domain="strategy",
            role=PanelRole.SYNTHESIZER,
            response_text="Strategic choices",
            confidence=0.85,
        )

        formatted = formatter.format_response(
            response, OutputFormat.LABELED_TEXT, LabelStyle.STANDARD
        )

        assert "Indra" in formatted.formatted_text

    def test_label_styles(self):
        """Test different label styles."""
        formatter = ResponseFormatter()

        response = ExpertResponse(
            expert_name="Chris",
            expert_domain="negotiation",
            role=PanelRole.PRIMARY,
            response_text="Empathy first",
            confidence=0.9,
        )

        minimal = formatter.format_response(
            response, OutputFormat.TEXT, LabelStyle.MINIMAL
        )
        standard = formatter.format_response(
            response, OutputFormat.TEXT, LabelStyle.STANDARD
        )
        verbose = formatter.format_response(
            response, OutputFormat.TEXT, LabelStyle.VERBOSE
        )

        # Check increasing verbosity
        assert len(minimal.formatted_text) <= len(standard.formatted_text)
        assert len(standard.formatted_text) <= len(verbose.formatted_text)

    def test_format_panel_markdown(self):
        """Test formatting entire panel in markdown."""
        router = PanelRouter()
        formatter = ResponseFormatter()

        session, _ = router.panel_router(
            session_id="s_001",
            question_text="How do I lead?",
            expert_names=["Satya", "Richard"],
            category="leadership",
        )

        formatted_panel = formatter.format_panel(
            session, OutputFormat.MARKDOWN, LabelStyle.STANDARD
        )

        assert formatted_panel.session_id == "s_001"
        assert len(formatted_panel.formatted_responses) == 2
        assert "How do I lead?" in formatted_panel.aggregated_text

    def test_format_panel_text(self):
        """Test formatting panel in plain text."""
        router = PanelRouter()
        formatter = ResponseFormatter()

        session, _ = router.panel_router(
            session_id="s_002",
            question_text="Scale question",
            expert_names=["Jeff", "Indra"],
        )

        formatted_panel = formatter.format_panel(
            session, OutputFormat.TEXT, LabelStyle.STANDARD
        )

        assert len(formatted_panel.formatted_responses) == 2
        assert "Scale question" in formatted_panel.aggregated_text

    def test_format_panel_with_consensus(self):
        """Test including consensus in formatted panel."""
        router = PanelRouter()
        formatter = ResponseFormatter()

        session, _ = router.panel_router(
            session_id="s_003",
            question_text="Test question",
            expert_names=["Satya", "Richard", "Jeff"],
        )

        formatted_panel = formatter.format_panel(
            session,
            OutputFormat.MARKDOWN,
            LabelStyle.STANDARD,
            include_consensus=True,
        )

        assert formatted_panel is not None

    def test_format_panel_without_consensus(self):
        """Test excluding consensus from formatted panel."""
        router = PanelRouter()
        formatter = ResponseFormatter()

        session, _ = router.panel_router(
            session_id="s_004",
            question_text="Question",
            expert_names=["Satya"],
        )

        formatted_panel = formatter.format_panel(
            session,
            OutputFormat.MARKDOWN,
            include_consensus=False,
        )

        assert formatted_panel is not None

    def test_get_formatted_panel(self):
        """Test retrieving formatted panel."""
        router = PanelRouter()
        formatter = ResponseFormatter()

        session, _ = router.panel_router(
            session_id="s_005",
            question_text="Question",
            expert_names=["Richard"],
        )

        formatter.format_panel(session)

        retrieved = formatter.get_formatted_panel("s_005")
        assert retrieved is not None
        assert retrieved.session_id == "s_005"

    def test_get_nonexistent_formatted_panel(self):
        """Test retrieving nonexistent formatted panel."""
        formatter = ResponseFormatter()
        retrieved = formatter.get_formatted_panel("nonexistent")
        assert retrieved is None

    def test_export_formatted_panel(self):
        """Test exporting formatted panel."""
        router = PanelRouter()
        formatter = ResponseFormatter()

        session, _ = router.panel_router(
            session_id="s_006",
            question_text="Question",
            expert_names=["Satya", "Richard"],
        )

        formatter.format_panel(session)

        exported = formatter.export_formatted_panel("s_006")
        assert exported is not None
        assert len(exported["responses"]) == 2

    def test_export_all_formatted_panels(self):
        """Test exporting all formatted panels."""
        router = PanelRouter()
        formatter = ResponseFormatter()

        session1, _ = router.panel_router(
            session_id="s_007",
            question_text="Q1",
            expert_names=["Satya"],
        )
        session2, _ = router.panel_router(
            session_id="s_008",
            question_text="Q2",
            expert_names=["Richard"],
        )

        formatter.format_panel(session1)
        formatter.format_panel(session2)

        exported = formatter.export_all_formatted_panels()
        assert len(exported) == 2

    def test_reformat_panel_markdown_to_html(self):
        """Test reformatting panel from markdown to HTML."""
        router = PanelRouter()
        formatter = ResponseFormatter()

        session, _ = router.panel_router(
            session_id="s_009",
            question_text="Question",
            expert_names=["Satya", "Richard"],
        )

        formatter.format_panel(session, OutputFormat.MARKDOWN)

        # Reformat to HTML
        reformatted = formatter.reformat_panel("s_009", OutputFormat.HTML)
        assert reformatted is not None
        assert reformatted.format_type == OutputFormat.HTML

    def test_reformat_panel_text_to_markdown(self):
        """Test reformatting panel from text to markdown."""
        router = PanelRouter()
        formatter = ResponseFormatter()

        session, _ = router.panel_router(
            session_id="s_010",
            question_text="Question",
            expert_names=["Jeff"],
        )

        formatter.format_panel(session, OutputFormat.TEXT)

        reformatted = formatter.reformat_panel("s_010", OutputFormat.MARKDOWN)
        assert reformatted is not None
        assert reformatted.format_type == OutputFormat.MARKDOWN

    def test_reformat_nonexistent_panel(self):
        """Test reformatting nonexistent panel."""
        formatter = ResponseFormatter()
        reformatted = formatter.reformat_panel("nonexistent", OutputFormat.HTML)
        assert reformatted is None

    def test_response_with_insights_and_questions(self):
        """Test formatting response with insights and follow-up questions."""
        formatter = ResponseFormatter()

        response = ExpertResponse(
            expert_name="Andy",
            expert_domain="systems",
            role=PanelRole.PRIMARY,
            response_text="Focus on output",
            confidence=0.85,
            key_insights=["Measurement matters", "Culture first"],
            follow_up_questions=["What's your OKR?", "How do you measure?"],
        )

        formatted = formatter.format_response(
            response, OutputFormat.MARKDOWN, LabelStyle.STANDARD
        )

        assert "Measurement matters" in formatted.formatted_text or "Key Insights" in formatted.formatted_text
        assert "OKR" in formatted.formatted_text or "Follow-up" in formatted.formatted_text

    def test_format_statistics_empty(self):
        """Test statistics with no formatted panels."""
        formatter = ResponseFormatter()
        stats = formatter.get_format_statistics()

        assert stats["total_formatted_panels"] == 0
        assert stats["total_responses"] == 0

    def test_format_statistics_with_panels(self):
        """Test statistics with formatted panels."""
        router = PanelRouter()
        formatter = ResponseFormatter()

        session1, _ = router.panel_router(
            session_id="s_011",
            question_text="Q1",
            expert_names=["Satya", "Richard"],
        )
        session2, _ = router.panel_router(
            session_id="s_012",
            question_text="Q2",
            expert_names=["Jeff"],
        )

        formatter.format_panel(session1, OutputFormat.MARKDOWN)
        formatter.format_panel(session2, OutputFormat.TEXT)

        stats = formatter.get_format_statistics()
        assert stats["total_formatted_panels"] == 2
        assert stats["total_responses"] == 3
        assert "markdown" in stats["format_distribution"]
        assert "text" in stats["format_distribution"]

    def test_multiple_formatters_independent(self):
        """Test multiple formatters are independent."""
        formatter1 = ResponseFormatter()
        formatter2 = ResponseFormatter()

        router = PanelRouter()

        session1, _ = router.panel_router(
            session_id="s_013",
            question_text="Q1",
            expert_names=["Satya"],
        )
        session2, _ = router.panel_router(
            session_id="s_014",
            question_text="Q2",
            expert_names=["Richard"],
        )

        formatter1.format_panel(session1)
        formatter2.format_panel(session2)

        assert len(formatter1.formatted_panels) == 1
        assert len(formatter2.formatted_panels) == 1
        assert formatter1.get_formatted_panel("s_013") is not None
        assert formatter2.get_formatted_panel("s_014") is not None

    def test_complex_formatting_workflow(self):
        """Test complex workflow with multiple formats."""
        router = PanelRouter()
        formatter = ResponseFormatter()

        # Create panel
        session, _ = router.panel_router(
            session_id="s_complex",
            question_text="How do I build value?",
            expert_names=["Jeff", "Warren", "Narayana"],
            category="value_creation",
        )

        # Format in multiple formats
        md_panel = formatter.format_panel(session, OutputFormat.MARKDOWN)
        txt_panel = formatter.reformat_panel("s_complex", OutputFormat.TEXT)
        html_panel = formatter.reformat_panel("s_complex", OutputFormat.HTML)

        assert md_panel is not None
        assert txt_panel is not None
        assert html_panel is not None

        # Check they're different formats
        assert md_panel.format_type == OutputFormat.MARKDOWN
        assert txt_panel.format_type == OutputFormat.TEXT
        assert html_panel.format_type == OutputFormat.HTML

        # Check exports work
        exports = formatter.export_all_formatted_panels()
        assert len(exports) >= 1

        # Check stats
        stats = formatter.get_format_statistics()
        assert stats["total_formatted_panels"] >= 1
