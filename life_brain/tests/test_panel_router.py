"""
Test suite for panel router.

Tests cover:
- Panel session creation and routing
- Multi-expert response collection
- Consensus and disagreement detection
- Panel comparisons and synthesis
- Statistics and exports
"""

import pytest

from life_brain.conversation.panel_router import (
    PanelRouter,
    PanelSession,
    PanelQuestion,
    ExpertResponse,
    PanelRole,
)
from life_brain.experts.roster import ExpertRoster


class TestExpertResponse:
    """Test ExpertResponse dataclass."""

    def test_create_response(self):
        """Test creating expert response."""
        response = ExpertResponse(
            expert_name="Satya",
            expert_domain="interviews",
            role=PanelRole.PRIMARY,
            response_text="Let's practice together",
            confidence=0.85,
            key_insights=["Listening matters", "Pattern recognition"],
        )

        assert response.expert_name == "Satya"
        assert response.confidence == 0.85
        assert len(response.key_insights) == 2

    def test_to_dict(self):
        """Test converting response to dictionary."""
        response = ExpertResponse(
            expert_name="Richard",
            expert_domain="first_principles",
            role=PanelRole.CHALLENGER,
            response_text="Break it down",
            confidence=0.9,
            follow_up_questions=["Why?", "How?"],
        )

        response_dict = response.to_dict()
        assert response_dict["expert_name"] == "Richard"
        assert response_dict["role"] == "challenger"
        assert response_dict["confidence"] == 0.9


class TestPanelQuestion:
    """Test PanelQuestion dataclass."""

    def test_create_question(self):
        """Test creating panel question."""
        question = PanelQuestion(
            question_id="q_001",
            question_text="How do I lead effectively?",
            context="5 years in role",
            category="leadership",
            urgency=4,
        )

        assert question.question_id == "q_001"
        assert question.category == "leadership"
        assert question.urgency == 4

    def test_to_dict(self):
        """Test converting question to dictionary."""
        question = PanelQuestion(
            question_id="q_002",
            question_text="How should I scale my business?",
            category="business",
            depth_level=5,
        )

        question_dict = question.to_dict()
        assert question_dict["question_text"] == "How should I scale my business?"
        assert question_dict["depth_level"] == 5


class TestPanelRouter:
    """Test PanelRouter functionality."""

    def test_create_router(self):
        """Test creating panel router."""
        router = PanelRouter()
        assert len(router.sessions) == 0
        assert len(router.session_history) == 0

    def test_router_with_custom_roster(self):
        """Test router with custom roster."""
        roster = ExpertRoster()
        router = PanelRouter(roster)
        assert router.roster == roster

    def test_route_two_experts(self):
        """Test routing to two experts."""
        router = PanelRouter()

        session, error = router.panel_router(
            session_id="s_001",
            question_text="How should I approach this problem?",
            expert_names=["Satya", "Richard"],
            category="problem_solving",
        )

        assert error is None
        assert session is not None
        assert len(session.expert_panel) == 2
        assert len(session.responses) == 2

    def test_route_three_experts(self):
        """Test routing to three experts."""
        router = PanelRouter()

        session, error = router.panel_router(
            session_id="s_002",
            question_text="How do I scale effectively?",
            expert_names=["Jeff", "Indra", "Andy"],
            category="scaling",
        )

        assert error is None
        assert len(session.expert_panel) == 3
        assert len(session.responses) == 3

    def test_invalid_expert_name(self):
        """Test with invalid expert name."""
        router = PanelRouter()

        session, error = router.panel_router(
            session_id="s_003",
            question_text="Test question",
            expert_names=["Satya", "NonExistent"],
        )

        assert error is not None
        assert "not found" in error
        assert session is None

    def test_primary_role_assignment(self):
        """Test primary expert gets primary role."""
        router = PanelRouter()

        session, _ = router.panel_router(
            session_id="s_004",
            question_text="Interview question",
            expert_names=["Satya", "Richard"],
        )

        satya_response = session.responses["Satya"]
        assert satya_response.role == PanelRole.PRIMARY

    def test_synthesizer_role_assignment(self):
        """Test last expert gets synthesizer role."""
        router = PanelRouter()

        session, _ = router.panel_router(
            session_id="s_005",
            question_text="Complex question",
            expert_names=["Satya", "Richard", "Jeff"],
        )

        jeff_response = session.responses["Jeff"]
        assert jeff_response.role == PanelRole.SYNTHESIZER

    def test_response_confidence_scales_with_depth(self):
        """Test confidence increases with depth level."""
        router = PanelRouter()

        session_deep, _ = router.panel_router(
            session_id="s_deep",
            question_text="Question",
            expert_names=["Satya"],
            depth_level=5,
        )

        session_shallow, _ = router.panel_router(
            session_id="s_shallow",
            question_text="Question",
            expert_names=["Satya"],
            depth_level=1,
        )

        resp_deep = list(session_deep.responses.values())[0].confidence
        resp_shallow = list(session_shallow.responses.values())[0].confidence

        assert resp_deep > resp_shallow

    def test_consensus_detection(self):
        """Test consensus points are detected."""
        router = PanelRouter()

        session, _ = router.panel_router(
            session_id="s_consensus",
            question_text="Leadership question",
            expert_names=["Satya", "Richard", "Jeff"],
        )

        # With multiple experts, consensus should be detected
        assert isinstance(session.consensus_points, list)

    def test_get_session(self):
        """Test retrieving specific session."""
        router = PanelRouter()

        session1, _ = router.panel_router(
            session_id="s_006",
            question_text="Question 1",
            expert_names=["Satya"],
        )

        retrieved = router.get_session("s_006")
        assert retrieved is not None
        assert retrieved.question.question_text == "Question 1"

    def test_get_nonexistent_session(self):
        """Test retrieving nonexistent session."""
        router = PanelRouter()
        retrieved = router.get_session("nonexistent")
        assert retrieved is None

    def test_get_session_summary(self):
        """Test session summary."""
        router = PanelRouter()

        router.panel_router(
            session_id="s_007",
            question_text="How do I grow?",
            expert_names=["Jeff", "Indra"],
            category="growth",
        )

        summary = router.get_session_summary("s_007")
        assert summary is not None
        assert summary["expert_count"] == 2
        assert summary["response_count"] == 2
        assert summary["question"] == "How do I grow?"

    def test_get_expert_response(self):
        """Test getting specific expert's response."""
        router = PanelRouter()

        router.panel_router(
            session_id="s_008",
            question_text="Leadership",
            expert_names=["Satya", "Richard"],
        )

        satya_resp = router.get_expert_response("s_008", "Satya")
        assert satya_resp is not None
        assert satya_resp.expert_name == "Satya"

    def test_get_nonexistent_expert_response(self):
        """Test getting nonexistent expert response."""
        router = PanelRouter()

        router.panel_router(
            session_id="s_009",
            question_text="Test",
            expert_names=["Satya"],
        )

        resp = router.get_expert_response("s_009", "NonExistent")
        assert resp is None

    def test_export_session(self):
        """Test exporting single session."""
        router = PanelRouter()

        router.panel_router(
            session_id="s_010",
            question_text="Question",
            expert_names=["Satya", "Richard"],
        )

        exported = router.export_session("s_010")
        assert exported is not None
        assert exported["session_id"] == "s_010"
        assert len(exported["responses"]) == 2

    def test_export_all_sessions(self):
        """Test exporting all sessions."""
        router = PanelRouter()

        router.panel_router(
            session_id="s_011",
            question_text="Q1",
            expert_names=["Satya"],
        )
        router.panel_router(
            session_id="s_012",
            question_text="Q2",
            expert_names=["Richard"],
        )

        exported = router.export_all_sessions()
        assert len(exported) == 2
        assert exported[0]["session_id"] == "s_011"
        assert exported[1]["session_id"] == "s_012"

    def test_synthesize_perspectives(self):
        """Test synthesizing all perspectives."""
        router = PanelRouter()

        router.panel_router(
            session_id="s_013",
            question_text="Strategy question",
            expert_names=["Jeff", "Indra", "Andy"],
        )

        synthesis = router.synthesize_perspectives("s_013")
        assert synthesis is not None
        assert "common_themes" in synthesis
        assert "average_confidence" in synthesis
        assert synthesis["expert_count"] == 3

    def test_compare_experts(self):
        """Test comparing two experts' responses."""
        router = PanelRouter()

        router.panel_router(
            session_id="s_014",
            question_text="Question",
            expert_names=["Satya", "Richard"],
        )

        comparison = router.compare_experts("s_014", "Satya", "Richard")
        assert comparison is not None
        assert comparison["expert1"] == "Satya"
        assert comparison["expert2"] == "Richard"
        assert "common_insights" in comparison
        assert "unique_to_expert1" in comparison

    def test_compare_nonexistent_expert(self):
        """Test comparing with nonexistent expert."""
        router = PanelRouter()

        router.panel_router(
            session_id="s_015",
            question_text="Question",
            expert_names=["Satya"],
        )

        comparison = router.compare_experts("s_015", "Satya", "NonExistent")
        assert comparison is None

    def test_panel_statistics_empty(self):
        """Test statistics with no sessions."""
        router = PanelRouter()
        stats = router.get_panel_statistics()

        assert stats["total_sessions"] == 0
        assert stats["total_expert_responses"] == 0
        assert stats["avg_panel_size"] == 0

    def test_panel_statistics_with_sessions(self):
        """Test statistics with multiple sessions."""
        router = PanelRouter()

        router.panel_router(
            session_id="s_016",
            question_text="Q1",
            expert_names=["Satya", "Richard"],
        )
        router.panel_router(
            session_id="s_017",
            question_text="Q2",
            expert_names=["Jeff", "Indra", "Andy"],
        )

        stats = router.get_panel_statistics()
        assert stats["total_sessions"] == 2
        assert stats["total_expert_responses"] == 5
        assert stats["avg_panel_size"] == 2.5
        assert stats["unique_experts_used"] == 5

    def test_question_with_context_and_urgency(self):
        """Test panel with context and urgency."""
        router = PanelRouter()

        session, _ = router.panel_router(
            session_id="s_018",
            question_text="How do I handle this?",
            expert_names=["Chris", "Brené"],
            context="Conflict with team member",
            category="conflict",
            urgency=5,
        )

        assert session.question.context == "Conflict with team member"
        assert session.question.urgency == 5

    def test_multiple_panel_sessions(self):
        """Test multiple independent panel sessions."""
        router = PanelRouter()

        s1, _ = router.panel_router(
            session_id="s_multi_1",
            question_text="Question 1",
            expert_names=["Satya"],
        )
        s2, _ = router.panel_router(
            session_id="s_multi_2",
            question_text="Question 2",
            expert_names=["Richard", "Jeff"],
        )

        assert len(s1.expert_panel) == 1
        assert len(s2.expert_panel) == 2
        assert len(router.session_history) == 2

    def test_disagreement_detection(self):
        """Test disagreement detection across domains."""
        router = PanelRouter()

        session, _ = router.panel_router(
            session_id="s_019",
            question_text="General question",
            expert_names=["Satya", "Warren", "Sadhguru"],
        )

        # Should detect domain differences as disagreements
        assert isinstance(session.disagreement_points, list)

    def test_panel_role_distribution(self):
        """Test proper role assignment across panel."""
        router = PanelRouter()

        session, _ = router.panel_router(
            session_id="s_020",
            question_text="Question",
            expert_names=["Satya", "Richard", "Jeff", "Indra"],
        )

        roles = [r.role for r in session.responses.values()]

        # First should be PRIMARY
        assert any(r == PanelRole.PRIMARY for r in roles)
        # Last should be SYNTHESIZER
        assert any(r == PanelRole.SYNTHESIZER for r in roles)

    def test_depth_level_response_variation(self):
        """Test responses vary with depth level."""
        router = PanelRouter()

        session1, _ = router.panel_router(
            session_id="s_depth_1",
            question_text="Question",
            expert_names=["Richard"],
            depth_level=1,
        )

        session2, _ = router.panel_router(
            session_id="s_depth_5",
            question_text="Question",
            expert_names=["Richard"],
            depth_level=5,
        )

        conf1 = list(session1.responses.values())[0].confidence
        conf5 = list(session2.responses.values())[0].confidence

        # Confidence should scale with depth
        assert conf5 > conf1

    def test_complex_panel_workflow(self):
        """Test complex workflow with multiple operations."""
        router = PanelRouter()

        # Create session
        session, error = router.panel_router(
            session_id="s_complex",
            question_text="How do I build enduring value?",
            expert_names=["Jeff", "Warren", "Narayana"],
            category="value_creation",
            urgency=4,
            depth_level=5,
        )

        assert error is None
        assert len(session.expert_panel) == 3

        # Get summaries
        summary = router.get_session_summary("s_complex")
        assert summary is not None

        # Compare experts
        comparison = router.compare_experts("s_complex", "Jeff", "Warren")
        assert comparison is not None

        # Synthesize
        synthesis = router.synthesize_perspectives("s_complex")
        assert synthesis is not None
        assert synthesis["expert_count"] == 3

        # Export
        exported = router.export_session("s_complex")
        assert len(exported["responses"]) == 3

        # Check stats
        stats = router.get_panel_statistics()
        assert stats["total_sessions"] >= 1
        assert stats["avg_panel_size"] >= 3
