"""
Tests for adversarial expert response formatting.

Tests cover:
- Side-by-side formatting with expert labels
- Compact labeled response format
- Summary table format
- Export to dict
- Synthesis inclusion
- Edge cases (long names, missing synthesis)
"""

import pytest

from life_brain.conversation.adversarial_formatter import (
    AdversarialFormatter,
    AdversarialResponse,
    ExpertOpinion,
    route_to_opposing_experts,
)


def _make_response(with_synthesis: bool = False) -> AdversarialResponse:
    """Helper to create a test AdversarialResponse."""
    return AdversarialResponse(
        question="Should I take the high-risk startup job?",
        expert_a=ExpertOpinion(
            expert_name="Elon Musk",
            stance_label="Bold Risk-Taker",
            response="Absolutely — if you're not failing you're not trying hard enough. Jump in.",
            key_point="High risk = high reward. Take the leap.",
        ),
        expert_b=ExpertOpinion(
            expert_name="Warren Buffett",
            stance_label="Cautious Value Investor",
            response="Don't risk what you have and need for what you don't need. Be patient.",
            key_point="Preserve capital, be selective, long-term thinking wins.",
        ),
        synthesis="Both experts agree due diligence matters. The right choice depends on your runway and risk tolerance." if with_synthesis else None,
    )


class TestExpertOpinion:
    """Test ExpertOpinion dataclass."""

    def test_create_opinion(self):
        opinion = ExpertOpinion(
            expert_name="Elon Musk",
            stance_label="Bold",
            response="Take the risk.",
            key_point="Risk = Reward",
        )
        assert opinion.expert_name == "Elon Musk"
        assert opinion.stance_label == "Bold"


class TestAdversarialFormatter:
    """Test AdversarialFormatter."""

    def test_format_side_by_side_contains_experts(self):
        fmt = AdversarialFormatter()
        resp = _make_response()
        output = fmt.format_side_by_side(resp)

        assert "ELON MUSK" in output
        assert "WARREN BUFFETT" in output

    def test_format_side_by_side_contains_stances(self):
        fmt = AdversarialFormatter()
        resp = _make_response()
        output = fmt.format_side_by_side(resp)

        assert "Bold Risk-Taker" in output
        assert "Cautious Value Investor" in output

    def test_format_side_by_side_contains_responses(self):
        fmt = AdversarialFormatter()
        resp = _make_response()
        output = fmt.format_side_by_side(resp)

        assert "Jump in" in output
        assert "Be patient" in output

    def test_format_side_by_side_contains_key_points(self):
        fmt = AdversarialFormatter()
        resp = _make_response()
        output = fmt.format_side_by_side(resp)

        assert "High risk = high reward" in output
        assert "Preserve capital" in output

    def test_format_side_by_side_with_synthesis(self):
        fmt = AdversarialFormatter()
        resp = _make_response(with_synthesis=True)
        output = fmt.format_side_by_side(resp)

        assert "SYNTHESIS" in output
        assert "due diligence" in output

    def test_format_side_by_side_without_synthesis(self):
        fmt = AdversarialFormatter()
        resp = _make_response(with_synthesis=False)
        output = fmt.format_side_by_side(resp)

        assert "SYNTHESIS" not in output

    def test_format_labeled_responses_contains_labels(self):
        fmt = AdversarialFormatter()
        resp = _make_response()
        output = fmt.format_labeled_responses(resp)

        assert "[Elon Musk" in output
        assert "[Warren Buffett" in output

    def test_format_labeled_responses_contains_stances(self):
        fmt = AdversarialFormatter()
        resp = _make_response()
        output = fmt.format_labeled_responses(resp)

        assert "Bold Risk-Taker" in output
        assert "Cautious Value Investor" in output

    def test_format_labeled_responses_question(self):
        fmt = AdversarialFormatter()
        resp = _make_response()
        output = fmt.format_labeled_responses(resp)

        assert resp.question in output

    def test_format_labeled_with_synthesis(self):
        fmt = AdversarialFormatter()
        resp = _make_response(with_synthesis=True)
        output = fmt.format_labeled_responses(resp)

        assert "[Synthesis]" in output
        assert "due diligence" in output

    def test_format_summary_table_returns_string(self):
        fmt = AdversarialFormatter()
        resp = _make_response()
        table = fmt.format_summary_table(resp)

        assert isinstance(table, str)
        assert len(table) > 0

    def test_format_summary_table_contains_names(self):
        fmt = AdversarialFormatter()
        resp = _make_response()
        table = fmt.format_summary_table(resp)

        assert "Elon Musk" in table
        assert "Warren Buffett" in table

    def test_format_summary_table_has_separators(self):
        fmt = AdversarialFormatter()
        resp = _make_response()
        table = fmt.format_summary_table(resp)

        assert "+" in table or "-" in table  # Table borders

    def test_export_dict_structure(self):
        fmt = AdversarialFormatter()
        resp = _make_response()
        d = fmt.export_dict(resp)

        assert "question" in d
        assert "expert_a" in d
        assert "expert_b" in d
        assert "name" in d["expert_a"]
        assert "stance" in d["expert_a"]
        assert "response" in d["expert_a"]
        assert "key_point" in d["expert_a"]

    def test_export_dict_values(self):
        fmt = AdversarialFormatter()
        resp = _make_response()
        d = fmt.export_dict(resp)

        assert d["expert_a"]["name"] == "Elon Musk"
        assert d["expert_b"]["name"] == "Warren Buffett"
        assert d["question"] == resp.question

    def test_export_dict_synthesis_none(self):
        fmt = AdversarialFormatter()
        resp = _make_response(with_synthesis=False)
        d = fmt.export_dict(resp)

        assert d["synthesis"] is None

    def test_export_dict_synthesis_present(self):
        fmt = AdversarialFormatter()
        resp = _make_response(with_synthesis=True)
        d = fmt.export_dict(resp)

        assert d["synthesis"] is not None


class TestRouteToOpposingExperts:
    """Test route_to_opposing_experts helper."""

    def test_creates_adversarial_response(self):
        resp = route_to_opposing_experts(
            question="Should I quit my job?",
            expert_a_name="Elon Musk",
            expert_a_stance="Bold",
            expert_b_name="Warren Buffett",
            expert_b_stance="Cautious",
            expert_a_response="Yes, take the leap.",
            expert_b_response="Be careful and plan first.",
            expert_a_key_point="Risk = Opportunity",
            expert_b_key_point="Stability matters",
        )

        assert isinstance(resp, AdversarialResponse)
        assert resp.expert_a.expert_name == "Elon Musk"
        assert resp.expert_b.expert_name == "Warren Buffett"
        assert resp.question == "Should I quit my job?"
        assert resp.synthesis is None

    def test_with_synthesis(self):
        resp = route_to_opposing_experts(
            question="Q?",
            expert_a_name="A",
            expert_a_stance="Stance A",
            expert_b_name="B",
            expert_b_stance="Stance B",
            expert_a_response="Response A",
            expert_b_response="Response B",
            expert_a_key_point="Point A",
            expert_b_key_point="Point B",
            synthesis="Both have good points.",
        )

        assert resp.synthesis == "Both have good points."

    def test_formatted_output_usable(self):
        resp = route_to_opposing_experts(
            question="Should I take risk?",
            expert_a_name="Bold Expert",
            expert_a_stance="Risk-Taker",
            expert_b_name="Safe Expert",
            expert_b_stance="Conservative",
            expert_a_response="Take the risk!",
            expert_b_response="Be careful.",
            expert_a_key_point="Bold moves win",
            expert_b_key_point="Safety first",
        )

        fmt = AdversarialFormatter()
        output = fmt.format_side_by_side(resp)
        assert "BOLD EXPERT" in output
        assert "SAFE EXPERT" in output
        assert "Risk-Taker" in output
        assert "Conservative" in output
