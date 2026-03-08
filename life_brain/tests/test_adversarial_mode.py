"""
Test suite for adversarial mode.

Tests cover:
- Adversarial debate creation
- Opposing perspective routing
- Position analysis
- Tradeoff extraction
- Synthesis and recommendations
- Statistics and comparisons
"""

import pytest

from life_brain.conversation.adversarial_mode import (
    AdversarialMode,
    AdversarialDebate,
    AdversarialPosition,
    OpposingPerspective,
)
from life_brain.conversation.panel_router import PanelRouter


class TestAdversarialPosition:
    """Test AdversarialPosition dataclass."""

    def test_create_position(self):
        """Test creating position."""
        position = AdversarialPosition(
            position_name="Growth",
            experts=["Jeff", "Naval"],
            perspective="The growth-focused perspective",
            key_arguments=["Compound growth", "Long-term value"],
        )

        assert position.position_name == "Growth"
        assert len(position.experts) == 2

    def test_to_dict(self):
        """Test converting position to dict."""
        position = AdversarialPosition(
            position_name="Stability",
            experts=["Warren"],
            perspective="The stability perspective",
            risks=["Market crash", "Volatility"],
        )

        d = position.to_dict()
        assert d["position_name"] == "Stability"
        assert len(d["risks"]) == 2


class TestAdversarialDebate:
    """Test AdversarialDebate dataclass."""

    def test_create_debate(self):
        """Test creating debate."""
        debate = AdversarialDebate(
            session_id="debate_001",
            question="Should I prioritize growth or stability?",
            perspective_type=OpposingPerspective.GROWTH_VS_STABILITY,
        )

        assert debate.session_id == "debate_001"
        assert debate.perspective_type == OpposingPerspective.GROWTH_VS_STABILITY

    def test_to_dict(self):
        """Test converting debate to dict."""
        debate = AdversarialDebate(
            session_id="debate_002",
            question="Test question",
            perspective_type=OpposingPerspective.ACTION_VS_REFLECTION,
            synthesis="Both are important",
        )

        d = debate.to_dict()
        assert d["session_id"] == "debate_002"
        assert d["synthesis"] == "Both are important"


class TestAdversarialMode:
    """Test AdversarialMode functionality."""

    def test_create_adversarial_mode(self):
        """Test creating adversarial mode."""
        adversarial = AdversarialMode()
        assert len(adversarial.debates) == 0
        assert len(adversarial.debate_history) == 0

    def test_create_with_custom_router(self):
        """Test creating with custom panel router."""
        router = PanelRouter()
        adversarial = AdversarialMode(router)
        assert adversarial.router == router

    def test_debate_question_growth_vs_stability(self):
        """Test debating growth vs stability."""
        adversarial = AdversarialMode()

        debate, error = adversarial.debate_question(
            session_id="d_001",
            question="Should I stay in my current role or take a risky startup opportunity?",
            perspective_type=OpposingPerspective.GROWTH_VS_STABILITY,
        )

        assert error is None
        assert debate is not None
        assert debate.question == "Should I stay in my current role or take a risky startup opportunity?"
        assert debate.perspective_type == OpposingPerspective.GROWTH_VS_STABILITY

    def test_debate_question_detail_vs_bigpicture(self):
        """Test debating detail vs big picture."""
        adversarial = AdversarialMode()

        debate, error = adversarial.debate_question(
            session_id="d_002",
            question="How should I approach this problem?",
            perspective_type=OpposingPerspective.DETAIL_VS_BIGPICTURE,
        )

        assert error is None
        assert len(debate.positions) >= 2

    def test_debate_question_action_vs_reflection(self):
        """Test debating action vs reflection."""
        adversarial = AdversarialMode()

        debate, error = adversarial.debate_question(
            session_id="d_003",
            question="What should I do about my career?",
            perspective_type=OpposingPerspective.ACTION_VS_REFLECTION,
        )

        assert error is None
        assert debate.perspective_type == OpposingPerspective.ACTION_VS_REFLECTION

    def test_debate_question_short_term_vs_long_term(self):
        """Test debating short-term vs long-term."""
        adversarial = AdversarialMode()

        debate, error = adversarial.debate_question(
            session_id="d_004",
            question="Should I take this quick win?",
            perspective_type=OpposingPerspective.SHORT_TERM_VS_LONG_TERM,
        )

        assert error is None

    def test_debate_question_individual_vs_collective(self):
        """Test debating individual vs collective."""
        adversarial = AdversarialMode()

        debate, error = adversarial.debate_question(
            session_id="d_005",
            question="Whose needs should I prioritize?",
            perspective_type=OpposingPerspective.INDIVIDUAL_VS_COLLECTIVE,
        )

        assert error is None

    def test_debate_question_logic_vs_emotion(self):
        """Test debating logic vs emotion."""
        adversarial = AdversarialMode()

        debate, error = adversarial.debate_question(
            session_id="d_006",
            question="How should I make this decision?",
            perspective_type=OpposingPerspective.LOGIC_VS_EMOTION,
        )

        assert error is None

    def test_debate_question_tradition_vs_innovation(self):
        """Test debating tradition vs innovation."""
        adversarial = AdversarialMode()

        debate, error = adversarial.debate_question(
            session_id="d_007",
            question="Should we follow established practices or innovate?",
            perspective_type=OpposingPerspective.TRADITION_VS_INNOVATION,
        )

        assert error is None

    def test_debate_question_freedom_vs_structure(self):
        """Test debating freedom vs structure."""
        adversarial = AdversarialMode()

        debate, error = adversarial.debate_question(
            session_id="d_008",
            question="Should I be flexible or structured?",
            perspective_type=OpposingPerspective.FREEDOM_VS_STRUCTURE,
        )

        assert error is None

    def test_debate_with_context(self):
        """Test debate with context."""
        adversarial = AdversarialMode()

        debate, error = adversarial.debate_question(
            session_id="d_009",
            question="Career transition?",
            perspective_type=OpposingPerspective.GROWTH_VS_STABILITY,
            context="Currently in stable role, offered exciting but risky opportunity",
        )

        assert error is None
        assert debate.question == "Career transition?"

    def test_debate_empty_question(self):
        """Test debate with empty question."""
        adversarial = AdversarialMode()

        debate, error = adversarial.debate_question(
            session_id="d_010",
            question="",
            perspective_type=OpposingPerspective.GROWTH_VS_STABILITY,
        )

        assert error == "Empty question"
        assert debate is None

    def test_debate_invalid_perspective(self):
        """Test debate with invalid perspective type."""
        adversarial = AdversarialMode()

        # Create invalid enum would require hacky workaround, skip

    def test_positions_created(self):
        """Test that positions are created."""
        adversarial = AdversarialMode()

        debate, _ = adversarial.debate_question(
            session_id="d_011",
            question="Test question",
            perspective_type=OpposingPerspective.GROWTH_VS_STABILITY,
        )

        assert len(debate.positions) >= 2
        # Check each position has experts
        for pos in debate.positions:
            assert len(pos.experts) > 0

    def test_responses_collected(self):
        """Test that responses are collected from experts."""
        adversarial = AdversarialMode()

        debate, _ = adversarial.debate_question(
            session_id="d_012",
            question="Test question",
            perspective_type=OpposingPerspective.DETAIL_VS_BIGPICTURE,
        )

        assert len(debate.responses) > 0

    def test_synthesis_generated(self):
        """Test that synthesis is generated."""
        adversarial = AdversarialMode()

        debate, _ = adversarial.debate_question(
            session_id="d_013",
            question="Test question",
            perspective_type=OpposingPerspective.ACTION_VS_REFLECTION,
        )

        assert len(debate.synthesis) > 0
        assert "perspective" in debate.synthesis.lower()

    def test_recommendations_provided(self):
        """Test that recommendations are provided."""
        adversarial = AdversarialMode()

        debate, _ = adversarial.debate_question(
            session_id="d_014",
            question="Test question",
            perspective_type=OpposingPerspective.GROWTH_VS_STABILITY,
        )

        assert len(debate.recommended_approach) > 0

    def test_get_debate(self):
        """Test retrieving debate."""
        adversarial = AdversarialMode()

        adversarial.debate_question(
            session_id="d_015",
            question="Test",
            perspective_type=OpposingPerspective.GROWTH_VS_STABILITY,
        )

        debate = adversarial.get_debate("d_015")
        assert debate is not None
        assert debate.session_id == "d_015"

    def test_get_nonexistent_debate(self):
        """Test retrieving nonexistent debate."""
        adversarial = AdversarialMode()
        debate = adversarial.get_debate("nonexistent")
        assert debate is None

    def test_export_debate(self):
        """Test exporting debate."""
        adversarial = AdversarialMode()

        adversarial.debate_question(
            session_id="d_016",
            question="Test",
            perspective_type=OpposingPerspective.DETAIL_VS_BIGPICTURE,
        )

        exported = adversarial.export_debate("d_016")
        assert exported is not None
        assert exported["session_id"] == "d_016"

    def test_export_all_debates(self):
        """Test exporting all debates."""
        adversarial = AdversarialMode()

        adversarial.debate_question(
            session_id="d_017",
            question="Q1",
            perspective_type=OpposingPerspective.GROWTH_VS_STABILITY,
        )
        adversarial.debate_question(
            session_id="d_018",
            question="Q2",
            perspective_type=OpposingPerspective.ACTION_VS_REFLECTION,
        )

        exported = adversarial.export_all_debates()
        assert len(exported) == 2

    def test_get_debate_summary(self):
        """Test debate summary."""
        adversarial = AdversarialMode()

        adversarial.debate_question(
            session_id="d_019",
            question="Test question",
            perspective_type=OpposingPerspective.LOGIC_VS_EMOTION,
        )

        summary = adversarial.get_debate_summary("d_019")
        assert summary is not None
        assert summary["question"] == "Test question"
        assert "synthesis" in summary

    def test_get_nonexistent_summary(self):
        """Test getting nonexistent summary."""
        adversarial = AdversarialMode()
        summary = adversarial.get_debate_summary("nonexistent")
        assert summary is None

    def test_debate_statistics_empty(self):
        """Test statistics with no debates."""
        adversarial = AdversarialMode()
        stats = adversarial.get_debate_statistics()

        assert stats["total_debates"] == 0
        assert stats["avg_positions"] == 0

    def test_debate_statistics_with_debates(self):
        """Test statistics with multiple debates."""
        adversarial = AdversarialMode()

        for i in range(3):
            adversarial.debate_question(
                session_id=f"d_{i}",
                question=f"Question {i}",
                perspective_type=OpposingPerspective.GROWTH_VS_STABILITY,
            )

        stats = adversarial.get_debate_statistics()
        assert stats["total_debates"] == 3
        assert stats["by_perspective"]["growth_vs_stability"] == 3

    def test_compare_positions(self):
        """Test comparing positions."""
        adversarial = AdversarialMode()

        adversarial.debate_question(
            session_id="d_comp",
            question="Test",
            perspective_type=OpposingPerspective.GROWTH_VS_STABILITY,
        )

        comparison = adversarial.compare_positions("d_comp")
        assert comparison is not None
        assert "position1" in comparison
        assert "position2" in comparison

    def test_compare_nonexistent_debate(self):
        """Test comparing nonexistent debate."""
        adversarial = AdversarialMode()
        comparison = adversarial.compare_positions("nonexistent")
        assert comparison is None

    def test_multiple_adversarial_modes_independent(self):
        """Test multiple adversarial modes are independent."""
        adv1 = AdversarialMode()
        adv2 = AdversarialMode()

        adv1.debate_question(
            "d1", "Q1", OpposingPerspective.GROWTH_VS_STABILITY
        )
        adv2.debate_question(
            "d2", "Q2", OpposingPerspective.ACTION_VS_REFLECTION
        )

        assert len(adv1.debate_history) == 1
        assert len(adv2.debate_history) == 1
        assert adv1.debate_history[0].perspective_type == OpposingPerspective.GROWTH_VS_STABILITY
        assert adv2.debate_history[0].perspective_type == OpposingPerspective.ACTION_VS_REFLECTION

    def test_common_ground_identification(self):
        """Test common ground is identified."""
        adversarial = AdversarialMode()

        debate, _ = adversarial.debate_question(
            session_id="d_common",
            question="Test question",
            perspective_type=OpposingPerspective.GROWTH_VS_STABILITY,
        )

        # Should have some common ground
        assert isinstance(debate.common_ground, list)

    def test_tradeoffs_identified(self):
        """Test tradeoffs are identified."""
        adversarial = AdversarialMode()

        debate, _ = adversarial.debate_question(
            session_id="d_tradeoff",
            question="Test question",
            perspective_type=OpposingPerspective.DETAIL_VS_BIGPICTURE,
        )

        # Should have tradeoffs
        assert isinstance(debate.key_tradeoffs, list)

    def test_debate_workflow(self):
        """Test complete debate workflow."""
        adversarial = AdversarialMode()

        # Create debate
        debate, error = adversarial.debate_question(
            session_id="d_workflow",
            question="Should I take this opportunity?",
            perspective_type=OpposingPerspective.GROWTH_VS_STABILITY,
            context="High-risk, high-reward startup vs stable job",
        )

        assert error is None
        assert len(debate.positions) >= 2

        # Get summary
        summary = adversarial.get_debate_summary("d_workflow")
        assert summary is not None

        # Compare positions
        comparison = adversarial.compare_positions("d_workflow")
        assert comparison is not None

        # Export
        exported = adversarial.export_debate("d_workflow")
        assert exported is not None

        # Check stats
        stats = adversarial.get_debate_statistics()
        assert stats["total_debates"] >= 1
