"""
Tests for Conversational Framing — differentiated question delivery by use case.

Tests cover:
- Mode selection (structured/conversational/hybrid) for each use case category
- Progress label presence/absence
- Transition opener presence/absence
- Render output format
- Edge cases (unknown use case, first question, opener rotation)
"""

import pytest
from life_brain.conversation.conversational_framing import (
    ConversationalFramer,
    QuestionMode,
    FramingConfig,
)


class TestModeSelection:
    """Test that use cases map to the correct QuestionMode."""

    def test_career_use_case_is_structured(self):
        """C1–C12 must map to STRUCTURED mode."""
        framer = ConversationalFramer()
        for uc in ["C1", "C2", "C5", "C10", "C12"]:
            assert framer.get_mode(uc) == QuestionMode.STRUCTURED, f"{uc} should be STRUCTURED"

    def test_finance_use_case_is_structured(self):
        """F1–F5 must map to STRUCTURED mode."""
        framer = ConversationalFramer()
        for uc in ["F1", "F2", "F3", "F4", "F5"]:
            assert framer.get_mode(uc) == QuestionMode.STRUCTURED

    def test_creativity_use_case_is_structured(self):
        """CR1–CR3 must map to STRUCTURED mode."""
        framer = ConversationalFramer()
        for uc in ["CR1", "CR2", "CR3"]:
            assert framer.get_mode(uc) == QuestionMode.STRUCTURED

    def test_relationships_use_case_is_conversational(self):
        """R1–R7 must map to CONVERSATIONAL mode."""
        framer = ConversationalFramer()
        for uc in ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]:
            assert framer.get_mode(uc) == QuestionMode.CONVERSATIONAL, f"{uc} should be CONVERSATIONAL"

    def test_health_use_case_is_conversational(self):
        """H1–H6 must map to CONVERSATIONAL mode."""
        framer = ConversationalFramer()
        for uc in ["H1", "H2", "H3", "H4", "H5", "H6"]:
            assert framer.get_mode(uc) == QuestionMode.CONVERSATIONAL

    def test_memories_use_case_is_conversational(self):
        """M1–M3 must map to CONVERSATIONAL mode."""
        framer = ConversationalFramer()
        for uc in ["M1", "M2", "M3"]:
            assert framer.get_mode(uc) == QuestionMode.CONVERSATIONAL

    def test_personal_journaling_identity_is_conversational(self):
        """P3 (journaling) and P5 (identity) must be CONVERSATIONAL."""
        framer = ConversationalFramer()
        assert framer.get_mode("P3") == QuestionMode.CONVERSATIONAL
        assert framer.get_mode("P5") == QuestionMode.CONVERSATIONAL

    def test_goals_habits_learning_is_hybrid(self):
        """P1 (goals), P2 (habits), P4 (learning), P6 (review) must be HYBRID."""
        framer = ConversationalFramer()
        for uc in ["P1", "P2", "P4", "P6"]:
            assert framer.get_mode(uc) == QuestionMode.HYBRID, f"{uc} should be HYBRID"

    def test_unknown_use_case_defaults_to_structured(self):
        """Unknown use case ID must default to STRUCTURED (safe fallback)."""
        framer = ConversationalFramer()
        assert framer.get_mode("UNKNOWN") == QuestionMode.STRUCTURED
        assert framer.get_mode("") == QuestionMode.STRUCTURED
        assert framer.get_mode("Z99") == QuestionMode.STRUCTURED


class TestFramingConfig:
    """Test FramingConfig properties."""

    def test_structured_config_shows_progress(self):
        """STRUCTURED mode must have show_progress=True."""
        config = FramingConfig.from_use_case("C1")
        assert config.show_progress is True
        assert config.show_explicit_transitions is True

    def test_conversational_config_hides_progress(self):
        """CONVERSATIONAL mode must have show_progress=False."""
        config = FramingConfig.from_use_case("R2")
        assert config.show_progress is False
        assert config.show_explicit_transitions is False

    def test_hybrid_config_shows_progress(self):
        """HYBRID mode must have show_progress=True (but empathetic openers)."""
        config = FramingConfig.from_use_case("P1")
        assert config.show_progress is True

    def test_config_contains_use_case_id(self):
        """Config must store the use case ID."""
        config = FramingConfig.from_use_case("H3")
        assert config.use_case_id == "H3"
        assert config.mode == QuestionMode.CONVERSATIONAL


class TestProgressLabel:
    """Test Q-of-N progress label visibility."""

    def test_structured_first_question_has_progress(self):
        """First question in structured mode must show Q1 of N."""
        framer = ConversationalFramer()
        framed = framer.frame_question("C1", "Tell me about yourself?", 0, 8)
        assert framed.progress_label == "Q1 of 8"

    def test_structured_mid_question_has_progress(self):
        """Mid-session structured question must show correct Q-of-N."""
        framer = ConversationalFramer()
        framed = framer.frame_question("F2", "What's your monthly spend?", 4, 10)
        assert framed.progress_label == "Q5 of 10"

    def test_conversational_first_question_no_progress(self):
        """Conversational mode must never show progress label."""
        framer = ConversationalFramer()
        framed = framer.frame_question("R3", "Kya hua us raat?", 0, 6)
        assert framed.progress_label is None

    def test_conversational_mid_question_no_progress(self):
        """Conversational mid-session questions must also hide progress."""
        framer = ConversationalFramer()
        framed = framer.frame_question("H2", "Yeh feeling kab se hai?", 3, 6)
        assert framed.progress_label is None

    def test_hybrid_shows_progress(self):
        """Hybrid mode must show progress label."""
        framer = ConversationalFramer()
        framed = framer.frame_question("P2", "Kitne din tak maintain kiya?", 2, 7)
        assert framed.progress_label == "Q3 of 7"


class TestTransitions:
    """Test transition opener presence/absence."""

    def test_first_question_no_transition(self):
        """First question (index 0) must have no transition in any mode."""
        framer = ConversationalFramer()
        for uc in ["C1", "R2", "P1"]:
            framed = framer.frame_question(uc, "Question text?", 0, 5)
            assert framed.transition is None, f"{uc} Q1 should have no transition"

    def test_structured_transition_is_explicit(self):
        """Structured transitions must be explicit: 'Theek hai, ab next topic...'"""
        framer = ConversationalFramer()
        framed = framer.frame_question("C3", "What was your biggest win?", 2, 8)
        assert framed.transition is not None
        # Structured openers are formal/direct
        assert len(framed.transition) > 3

    def test_conversational_transition_is_organic(self):
        """Conversational transitions must be soft/organic, not mechanical."""
        framer = ConversationalFramer()
        framed = framer.frame_question("M1", "Aur kya feel hua?", 1, 5)
        assert framed.transition is not None
        # Should NOT be mechanical
        assert "Theek hai, ab next" not in framed.transition
        assert "Moving on" not in framed.transition

    def test_opener_rotation(self):
        """Different opener_index values must produce different transitions."""
        framer = ConversationalFramer()
        framed0 = framer.frame_question("R1", "Question?", 2, 6, opener_index=0)
        framed1 = framer.frame_question("R1", "Question?", 2, 6, opener_index=1)
        # Different openers (unless list has only 1 item, which it doesn't)
        assert framed0.transition != framed1.transition


class TestRenderOutput:
    """Test rendered output format."""

    def test_structured_first_question_format(self):
        """Structured Q1 has 'Q1 of N — question text' format."""
        framer = ConversationalFramer()
        output = framer.render_question("C1", "Tell me about yourself?", 0, 8)
        assert "Q1 of 8" in output
        assert "Tell me about yourself?" in output

    def test_conversational_no_counter_in_output(self):
        """Conversational output must NOT contain Q-of-N pattern."""
        framer = ConversationalFramer()
        output = framer.render_question("R2", "Kya hua us moment mein?", 3, 6)
        assert "Q4 of 6" not in output
        assert "Kya hua us moment mein?" in output

    def test_render_first_question_no_transition_text(self):
        """First question render must not include a transition phrase."""
        framer = ConversationalFramer()
        output = framer.render_question("H1", "Kab se yeh feel ho raha hai?", 0, 5)
        assert "Kab se yeh feel ho raha hai?" in output
        # No "Moving on" or "Theek hai, ab" in first question
        assert "Moving on" not in output
        assert "Theek hai" not in output

    def test_hybrid_output_has_progress(self):
        """Hybrid render must include progress label."""
        framer = ConversationalFramer()
        output = framer.render_question("P2", "Daily routine kya hai?", 1, 6)
        assert "Q2 of 6" in output


class TestHelperMethods:
    """Test is_conversational and is_structured helpers."""

    def test_is_conversational_true_for_relationships(self):
        framer = ConversationalFramer()
        assert framer.is_conversational("R5") is True

    def test_is_conversational_false_for_career(self):
        framer = ConversationalFramer()
        assert framer.is_conversational("C4") is False

    def test_is_structured_true_for_finance(self):
        framer = ConversationalFramer()
        assert framer.is_structured("F3") is True

    def test_is_structured_false_for_health(self):
        framer = ConversationalFramer()
        assert framer.is_structured("H4") is False

    def test_is_structured_false_for_hybrid(self):
        """Hybrid is NOT structured (has different openers)."""
        framer = ConversationalFramer()
        assert framer.is_structured("P1") is False
        assert framer.is_conversational("P1") is False
