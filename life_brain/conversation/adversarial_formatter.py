"""
Format adversarial expert responses with clear opposing labels.

Presents two expert perspectives side-by-side with clear labels
so the user can see both sides of a debate.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ExpertOpinion:
    """A single expert's opinion on a question."""

    expert_name: str      # e.g. "Elon Musk", "Warren Buffett"
    stance_label: str     # e.g. "Bold Risk-Taker", "Cautious Value Investor"
    response: str         # The expert's full response
    key_point: str        # One-line summary of their main argument


@dataclass
class AdversarialResponse:
    """Two opposing expert opinions formatted for display."""

    question: str
    expert_a: ExpertOpinion
    expert_b: ExpertOpinion
    synthesis: Optional[str] = None  # Optional synthesis/conclusion


class AdversarialFormatter:
    """Format opposing expert responses with clear labels."""

    def format_side_by_side(self, response: AdversarialResponse) -> str:
        """Format as side-by-side comparison with clear expert labels.

        Args:
            response: AdversarialResponse with two opposing opinions

        Returns:
            Formatted string ready for display
        """
        lines = [
            f"Question: {response.question}",
            "",
            f"{'─' * 60}",
            f"🅰  {response.expert_a.expert_name.upper()} — {response.expert_a.stance_label}",
            f"{'─' * 60}",
            response.expert_a.response,
            f"💡 Key point: {response.expert_a.key_point}",
            "",
            f"{'─' * 60}",
            f"🅱  {response.expert_b.expert_name.upper()} — {response.expert_b.stance_label}",
            f"{'─' * 60}",
            response.expert_b.response,
            f"💡 Key point: {response.expert_b.key_point}",
        ]

        if response.synthesis:
            lines += [
                "",
                f"{'─' * 60}",
                "⚖️  SYNTHESIS",
                f"{'─' * 60}",
                response.synthesis,
            ]

        return "\n".join(lines)

    def format_labeled_responses(self, response: AdversarialResponse) -> str:
        """Format as labeled response blocks (more compact).

        Args:
            response: AdversarialResponse

        Returns:
            Compact formatted string
        """
        a = response.expert_a
        b = response.expert_b

        lines = [
            f"Q: {response.question}",
            "",
            f"[{a.expert_name} / {a.stance_label}]",
            a.response,
            "",
            f"[{b.expert_name} / {b.stance_label}]",
            b.response,
        ]

        if response.synthesis:
            lines += ["", f"[Synthesis]", response.synthesis]

        return "\n".join(lines)

    def format_summary_table(self, response: AdversarialResponse) -> str:
        """Format as a quick summary comparison table.

        Args:
            response: AdversarialResponse

        Returns:
            Summary table string
        """
        a = response.expert_a
        b = response.expert_b

        col_w = 36
        sep = f"+{'-' * col_w}+{'-' * col_w}+"
        header = f"| {'Expert':<{col_w - 2}} | {'Expert':<{col_w - 2}} |"
        a_name = f"| {a.expert_name[:col_w - 2]:<{col_w - 2}} | {b.expert_name[:col_w - 2]:<{col_w - 2}} |"
        a_stance = f"| {a.stance_label[:col_w - 2]:<{col_w - 2}} | {b.stance_label[:col_w - 2]:<{col_w - 2}} |"

        # Key points wrapped to column width
        a_point = a.key_point[:col_w - 2]
        b_point = b.key_point[:col_w - 2]
        point_row = f"| {a_point:<{col_w - 2}} | {b_point:<{col_w - 2}} |"

        table = "\n".join([
            sep, a_name, a_stance, sep, point_row, sep,
        ])
        return table

    def export_dict(self, response: AdversarialResponse) -> Dict:
        """Export response as dictionary."""
        return {
            "question": response.question,
            "expert_a": {
                "name": response.expert_a.expert_name,
                "stance": response.expert_a.stance_label,
                "response": response.expert_a.response,
                "key_point": response.expert_a.key_point,
            },
            "expert_b": {
                "name": response.expert_b.expert_name,
                "stance": response.expert_b.stance_label,
                "response": response.expert_b.response,
                "key_point": response.expert_b.key_point,
            },
            "synthesis": response.synthesis,
        }


def route_to_opposing_experts(
    question: str,
    expert_a_name: str,
    expert_a_stance: str,
    expert_b_name: str,
    expert_b_stance: str,
    expert_a_response: str,
    expert_b_response: str,
    expert_a_key_point: str,
    expert_b_key_point: str,
    synthesis: Optional[str] = None,
) -> AdversarialResponse:
    """Route a question to two opposing experts and build formatted response.

    Args:
        question: The user's question
        expert_a_name: Name of first expert
        expert_a_stance: Stance label for first expert
        expert_b_name: Name of second expert
        expert_b_stance: Stance label for second expert
        expert_a_response: First expert's response text
        expert_b_response: Second expert's response text
        expert_a_key_point: One-line summary of first expert's argument
        expert_b_key_point: One-line summary of second expert's argument
        synthesis: Optional synthesis text

    Returns:
        AdversarialResponse ready for formatting
    """
    return AdversarialResponse(
        question=question,
        expert_a=ExpertOpinion(
            expert_name=expert_a_name,
            stance_label=expert_a_stance,
            response=expert_a_response,
            key_point=expert_a_key_point,
        ),
        expert_b=ExpertOpinion(
            expert_name=expert_b_name,
            stance_label=expert_b_stance,
            response=expert_b_response,
            key_point=expert_b_key_point,
        ),
        synthesis=synthesis,
    )
