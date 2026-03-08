"""
Panel response formatter — label expert responses clearly in panel discussions.

Formats multi-expert panel outputs with consistent expert identifiers:
**[Elon]:** response text
**[Warren]:** response text
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class OutputFormat(Enum):
    MARKDOWN = "markdown"
    PLAIN = "plain"
    JSON = "json"


@dataclass
class PanelResponse:
    """A single expert's response in a panel."""

    expert_name: str
    response_text: str
    role: Optional[str] = None  # e.g. "Lead", "Contrarian"

    def __post_init__(self):
        """Ensure no null values crash downstream formatting."""
        if not self.expert_name:
            self.expert_name = "Expert"
        if self.response_text is None:
            self.response_text = ""

    def label(self) -> str:
        """Generate the expert label."""
        first_name = self.expert_name.split()[0] if self.expert_name.split() else "Expert"
        if self.role:
            return f"{first_name} ({self.role})"
        return first_name


@dataclass
class PanelOutput:
    """Complete panel discussion output."""

    question: str
    responses: List[PanelResponse]
    moderator_note: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question": self.question,
            "responses": [
                {
                    "expert": r.expert_name,
                    "label": r.label(),
                    "role": r.role,
                    "response": r.response_text,
                }
                for r in self.responses
            ],
            "moderator_note": self.moderator_note,
        }


class PanelFormatter:
    """Format panel discussions with clear expert labels."""

    def format(
        self,
        panel: PanelOutput,
        fmt: OutputFormat = OutputFormat.MARKDOWN,
    ) -> str:
        """Format a panel output in the specified format.

        Args:
            panel: Panel discussion to format
            fmt: Output format (markdown, plain, json)

        Returns:
            Formatted string
        """
        if fmt == OutputFormat.MARKDOWN:
            return self._format_markdown(panel)
        elif fmt == OutputFormat.PLAIN:
            return self._format_plain(panel)
        elif fmt == OutputFormat.JSON:
            import json
            return json.dumps(panel.to_dict(), indent=2)
        else:
            return self._format_markdown(panel)

    def _format_markdown(self, panel: PanelOutput) -> str:
        """Format as markdown with bold expert labels."""
        lines = [f"**Question:** {panel.question}", ""]

        for resp in panel.responses:
            label = resp.label()
            lines.append(f"**[{label}]:** {resp.response_text}")
            lines.append("")

        if panel.moderator_note:
            lines.append(f"*Moderator: {panel.moderator_note}*")

        return "\n".join(lines).strip()

    def _format_plain(self, panel: PanelOutput) -> str:
        """Format as plain text with bracketed expert labels."""
        lines = [f"Question: {panel.question}", ""]

        for resp in panel.responses:
            label = resp.label()
            lines.append(f"[{label}]: {resp.response_text}")
            lines.append("")

        if panel.moderator_note:
            lines.append(f"Note: {panel.moderator_note}")

        return "\n".join(lines).strip()

    def format_single_response(
        self,
        expert_name: str,
        response_text: str,
        role: Optional[str] = None,
        fmt: OutputFormat = OutputFormat.MARKDOWN,
    ) -> str:
        """Format a single expert response with label.

        Args:
            expert_name: Expert's full name
            response_text: Response content
            role: Optional role label
            fmt: Output format

        Returns:
            Labeled response string
        """
        resp = PanelResponse(expert_name=expert_name, response_text=response_text, role=role)
        label = resp.label()

        if fmt == OutputFormat.MARKDOWN:
            return f"**[{label}]:** {response_text}"
        else:
            return f"[{label}]: {response_text}"

    def format_responses_list(
        self,
        responses: List[Dict[str, str]],
        fmt: OutputFormat = OutputFormat.MARKDOWN,
    ) -> str:
        """Format a list of expert response dicts.

        Args:
            responses: List of {"expert": name, "response": text, "role": optional}
            fmt: Output format

        Returns:
            Formatted multi-expert response string
        """
        lines = []
        for r in responses:
            name = r.get("expert") or "Expert"
            text = r.get("response") or ""
            role = r.get("role")
            resp = PanelResponse(expert_name=name, response_text=text, role=role)
            label = resp.label()

            if fmt == OutputFormat.MARKDOWN:
                lines.append(f"**[{label}]:** {text}")
            else:
                lines.append(f"[{label}]: {text}")

        return "\n\n".join(lines)
