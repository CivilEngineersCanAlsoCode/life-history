"""
Response formatter for multi-expert panel outputs.

Formats expert responses with clear labels, visual hierarchy, and
multiple output formats for readability and integration.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from life_brain.conversation.panel_router import (
    ExpertResponse,
    PanelSession,
    PanelRole,
)


class OutputFormat(Enum):
    """Output format for responses."""

    TEXT = "text"  # Plain text with ASCII formatting
    MARKDOWN = "markdown"  # Markdown format
    HTML = "html"  # HTML format
    JSON = "json"  # JSON format
    LABELED_TEXT = "labeled_text"  # Plain text with clear labels


class LabelStyle(Enum):
    """Label styling options."""

    MINIMAL = "minimal"  # Just names
    STANDARD = "standard"  # Name + domain + role
    VERBOSE = "verbose"  # Full details with timestamps


@dataclass
class FormattedResponse:
    """Single formatted expert response."""

    expert_name: str
    expert_domain: str
    role: str
    formatted_text: str
    raw_response: ExpertResponse
    format_type: OutputFormat
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "expert_name": self.expert_name,
            "expert_domain": self.expert_domain,
            "role": self.role,
            "formatted_text": self.formatted_text,
            "format_type": self.format_type.value,
            "generated_at": self.generated_at,
        }


@dataclass
class FormattedPanel:
    """Formatted entire panel session."""

    session_id: str
    question: str
    formatted_responses: List[FormattedResponse] = field(default_factory=list)
    aggregated_text: str = ""
    format_type: OutputFormat = OutputFormat.MARKDOWN
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "question": self.question,
            "responses": [r.to_dict() for r in self.formatted_responses],
            "aggregated_text": self.aggregated_text,
            "format_type": self.format_type.value,
            "created_at": self.created_at,
        }


class ResponseFormatter:
    """Format expert responses for various outputs."""

    def __init__(self):
        """Initialize response formatter."""
        self.formatted_panels: Dict[str, FormattedPanel] = {}
        self.format_history: List[FormattedPanel] = []

    def format_response(
        self,
        expert_response: ExpertResponse,
        format_type: OutputFormat = OutputFormat.MARKDOWN,
        label_style: LabelStyle = LabelStyle.STANDARD,
    ) -> FormattedResponse:
        """Format single expert response."""
        label = self._generate_label(
            expert_response.expert_name,
            expert_response.expert_domain,
            expert_response.role,
            label_style,
        )

        formatted_text = self._format_text(
            label, expert_response, format_type, label_style
        )

        return FormattedResponse(
            expert_name=expert_response.expert_name,
            expert_domain=expert_response.expert_domain,
            role=expert_response.role,
            formatted_text=formatted_text,
            raw_response=expert_response,
            format_type=format_type,
        )

    def format_panel(
        self,
        session: PanelSession,
        format_type: OutputFormat = OutputFormat.MARKDOWN,
        label_style: LabelStyle = LabelStyle.STANDARD,
        include_consensus: bool = True,
    ) -> FormattedPanel:
        """Format entire panel session."""
        formatted_responses = []

        # Format each response
        for expert_name, response in session.responses.items():
            formatted_resp = self.format_response(response, format_type, label_style)
            formatted_responses.append(formatted_resp)

        # Create formatted panel
        formatted_panel = FormattedPanel(
            session_id=session.session_id,
            question=session.question.question_text,
            formatted_responses=formatted_responses,
            format_type=format_type,
        )

        # Generate aggregated output
        formatted_panel.aggregated_text = self._aggregate_responses(
            formatted_responses,
            format_type,
            session,
            include_consensus,
        )

        # Store
        self.formatted_panels[session.session_id] = formatted_panel
        self.format_history.append(formatted_panel)

        return formatted_panel

    def _generate_label(
        self,
        expert_name: str,
        expert_domain: str,
        role: str,
        label_style: LabelStyle,
    ) -> str:
        """Generate label for expert."""
        if label_style == LabelStyle.MINIMAL:
            return f"{expert_name}"
        elif label_style == LabelStyle.STANDARD:
            return f"{expert_name} ({expert_domain}) - {role}"
        else:  # VERBOSE
            return f"Expert: {expert_name}\nDomain: {expert_domain}\nRole: {role}"

    def _format_text(
        self,
        label: str,
        response: ExpertResponse,
        format_type: OutputFormat,
        label_style: LabelStyle,
    ) -> str:
        """Format response text in specified format."""
        if format_type == OutputFormat.TEXT:
            return self._format_text_plain(label, response)
        elif format_type == OutputFormat.MARKDOWN:
            return self._format_text_markdown(label, response)
        elif format_type == OutputFormat.HTML:
            return self._format_text_html(label, response)
        elif format_type == OutputFormat.LABELED_TEXT:
            return self._format_text_labeled(label, response)
        else:
            return label + "\n" + response.response_text

    def _format_text_plain(self, label: str, response: ExpertResponse) -> str:
        """Format as plain text."""
        lines = [
            "─" * 60,
            f"[{label}]",
            "",
            response.response_text,
            "",
        ]

        if response.key_insights:
            lines.append("Key Insights:")
            for insight in response.key_insights:
                lines.append(f"  • {insight}")
            lines.append("")

        if response.follow_up_questions:
            lines.append("Follow-up Questions:")
            for q in response.follow_up_questions:
                lines.append(f"  ? {q}")

        return "\n".join(lines)

    def _format_text_markdown(self, label: str, response: ExpertResponse) -> str:
        """Format as markdown."""
        lines = [
            f"### {label}",
            "",
            response.response_text,
            "",
        ]

        if response.key_insights:
            lines.append("#### Key Insights")
            for insight in response.key_insights:
                lines.append(f"- {insight}")
            lines.append("")

        if response.follow_up_questions:
            lines.append("#### Follow-up Questions")
            for q in response.follow_up_questions:
                lines.append(f"- {q}")

        lines.append("")

        return "\n".join(lines)

    def _format_text_html(self, label: str, response: ExpertResponse) -> str:
        """Format as HTML."""
        html_parts = [
            "<div class='expert-response'>",
            f"<h3 class='expert-label'>{label}</h3>",
            f"<p class='expert-text'>{response.response_text}</p>",
        ]

        if response.key_insights:
            html_parts.append("<div class='insights'>")
            html_parts.append("<h4>Key Insights</h4>")
            html_parts.append("<ul>")
            for insight in response.key_insights:
                html_parts.append(f"<li>{insight}</li>")
            html_parts.append("</ul>")
            html_parts.append("</div>")

        if response.follow_up_questions:
            html_parts.append("<div class='questions'>")
            html_parts.append("<h4>Follow-up Questions</h4>")
            html_parts.append("<ul>")
            for q in response.follow_up_questions:
                html_parts.append(f"<li>{q}</li>")
            html_parts.append("</ul>")
            html_parts.append("</div>")

        html_parts.append("</div>")

        return "\n".join(html_parts)

    def _format_text_labeled(self, label: str, response: ExpertResponse) -> str:
        """Format with clear ASCII labels."""
        lines = [
            "",
            "┌" + "─" * 58 + "┐",
            f"│ ► {label:<55} │",
            "├" + "─" * 58 + "┤",
            f"│ {response.response_text:<58} │",
            "└" + "─" * 58 + "┘",
        ]

        if response.key_insights:
            lines.append("")
            lines.append("KEY INSIGHTS:")
            for insight in response.key_insights:
                lines.append(f"  ✓ {insight}")

        if response.follow_up_questions:
            lines.append("")
            lines.append("QUESTIONS:")
            for q in response.follow_up_questions:
                lines.append(f"  → {q}")

        return "\n".join(lines)

    def _aggregate_responses(
        self,
        formatted_responses: List[FormattedResponse],
        format_type: OutputFormat,
        session: PanelSession,
        include_consensus: bool,
    ) -> str:
        """Aggregate all formatted responses."""
        if format_type == OutputFormat.MARKDOWN:
            return self._aggregate_markdown(
                formatted_responses, session, include_consensus
            )
        elif format_type == OutputFormat.HTML:
            return self._aggregate_html(
                formatted_responses, session, include_consensus
            )
        else:
            return self._aggregate_text(
                formatted_responses, session, include_consensus
            )

    def _aggregate_markdown(
        self,
        formatted_responses: List[FormattedResponse],
        session: PanelSession,
        include_consensus: bool,
    ) -> str:
        """Aggregate responses in markdown."""
        lines = [
            f"# Panel Discussion: {session.question.question_text}",
            "",
            f"**Panel:** {', '.join(session.expert_panel)}",
            "",
            "---",
            "",
        ]

        for resp in formatted_responses:
            lines.append(resp.formatted_text)

        if include_consensus and session.consensus_points:
            lines.append("## Consensus Points")
            for point in session.consensus_points:
                lines.append(f"- {point}")
            lines.append("")

        if include_consensus and session.disagreement_points:
            lines.append("## Points of Disagreement")
            for point in session.disagreement_points:
                lines.append(f"- {point}")

        return "\n".join(lines)

    def _aggregate_text(
        self,
        formatted_responses: List[FormattedResponse],
        session: PanelSession,
        include_consensus: bool,
    ) -> str:
        """Aggregate responses in plain text."""
        lines = [
            "═" * 70,
            f"PANEL DISCUSSION: {session.question.question_text}",
            "═" * 70,
            f"Panel Members: {', '.join(session.expert_panel)}",
            "",
        ]

        for resp in formatted_responses:
            lines.append(resp.formatted_text)

        if include_consensus and session.consensus_points:
            lines.append("")
            lines.append("CONSENSUS POINTS:")
            for point in session.consensus_points:
                lines.append(f"  ✓ {point}")

        if include_consensus and session.disagreement_points:
            lines.append("")
            lines.append("AREAS OF DISAGREEMENT:")
            for point in session.disagreement_points:
                lines.append(f"  ✗ {point}")

        return "\n".join(lines)

    def _aggregate_html(
        self,
        formatted_responses: List[FormattedResponse],
        session: PanelSession,
        include_consensus: bool,
    ) -> str:
        """Aggregate responses in HTML."""
        html_parts = [
            "<div class='panel-discussion'>",
            f"<h1>Panel Discussion</h1>",
            f"<p class='question'>{session.question.question_text}</p>",
            f"<p class='panel-members'>Panel: {', '.join(session.expert_panel)}</p>",
            "<div class='responses'>",
        ]

        for resp in formatted_responses:
            html_parts.append(resp.formatted_text)

        html_parts.append("</div>")

        if include_consensus:
            if session.consensus_points:
                html_parts.append("<div class='consensus'>")
                html_parts.append("<h2>Consensus Points</h2>")
                html_parts.append("<ul>")
                for point in session.consensus_points:
                    html_parts.append(f"<li>{point}</li>")
                html_parts.append("</ul>")
                html_parts.append("</div>")

            if session.disagreement_points:
                html_parts.append("<div class='disagreement'>")
                html_parts.append("<h2>Areas of Disagreement</h2>")
                html_parts.append("<ul>")
                for point in session.disagreement_points:
                    html_parts.append(f"<li>{point}</li>")
                html_parts.append("</ul>")
                html_parts.append("</div>")

        html_parts.append("</div>")

        return "\n".join(html_parts)

    def get_formatted_panel(self, session_id: str) -> Optional[FormattedPanel]:
        """Get formatted panel for session."""
        return self.formatted_panels.get(session_id)

    def export_formatted_panel(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export formatted panel data."""
        panel = self.formatted_panels.get(session_id)
        if not panel:
            return None
        return panel.to_dict()

    def export_all_formatted_panels(self) -> List[Dict[str, Any]]:
        """Export all formatted panels."""
        return [p.to_dict() for p in self.format_history]

    def reformat_panel(
        self,
        session_id: str,
        new_format: OutputFormat,
        label_style: LabelStyle = LabelStyle.STANDARD,
    ) -> Optional[FormattedPanel]:
        """Reformat existing panel in different format."""
        panel = self.formatted_panels.get(session_id)
        if not panel:
            return None

        # Reformat each response
        new_responses = []
        for resp in panel.formatted_responses:
            new_formatted = self.format_response(
                resp.raw_response, new_format, label_style
            )
            new_responses.append(new_formatted)

        # Create new formatted panel
        new_panel = FormattedPanel(
            session_id=session_id,
            question=panel.question,
            formatted_responses=new_responses,
            format_type=new_format,
        )

        # Extract session from original formatted responses
        if new_responses:
            session = self._reconstruct_session_from_responses(
                session_id, panel.question, new_responses
            )
            new_panel.aggregated_text = self._aggregate_responses(
                new_responses, new_format, session, include_consensus=True
            )

        return new_panel

    def _reconstruct_session_from_responses(
        self, session_id: str, question: str, responses: List[FormattedResponse]
    ) -> PanelSession:
        """Reconstruct PanelSession from formatted responses."""
        from life_brain.conversation.panel_router import PanelQuestion

        q = PanelQuestion(question_id="q_0", question_text=question)
        experts = [r.expert_name for r in responses]
        s = PanelSession(session_id=session_id, question=q, expert_panel=experts)

        for resp in responses:
            s.responses[resp.expert_name] = resp.raw_response

        return s

    def get_format_statistics(self) -> Dict[str, Any]:
        """Get statistics about formatting."""
        if not self.format_history:
            return {
                "total_formatted_panels": 0,
                "total_responses": 0,
                "format_distribution": {},
                "avg_insights_per_response": 0,
            }

        format_dist = {}
        total_insights = 0
        total_responses = 0

        for panel in self.format_history:
            fmt = panel.format_type.value
            format_dist[fmt] = format_dist.get(fmt, 0) + len(panel.formatted_responses)
            total_responses += len(panel.formatted_responses)
            total_insights += sum(
                len(r.raw_response.key_insights)
                for r in panel.formatted_responses
            )

        return {
            "total_formatted_panels": len(self.format_history),
            "total_responses": total_responses,
            "format_distribution": format_dist,
            "avg_insights_per_response": (
                total_insights / total_responses if total_responses > 0 else 0
            ),
        }
