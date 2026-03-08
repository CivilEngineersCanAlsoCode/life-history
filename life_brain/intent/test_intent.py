"""
Tests for Intent Detection System.

Tests cover:
- Keyword extraction and matching
- Intent detection accuracy with 40+ use cases
- Confidence scoring
- Continuous detection
- Mode gate UI rendering
"""

import pytest
from typing import List, Dict, Any

from life_brain.intent.detector import IntentDetector, IntentMatch
from life_brain.intent.mode_gate import (
    format_mode_buttons,
    handle_mode_selection,
    ModeState,
    format_mode_transition_prompt,
)


class TestIntentDetector:
    """Test suite for IntentDetector."""

    @pytest.fixture
    def detector(self):
        """Create detector instance."""
        return IntentDetector(use_llm_ranking=False)

    def test_detector_initialization(self, detector):
        """Test detector initializes with 40+ use cases."""
        assert detector.use_cases is not None
        assert len(detector.use_cases) >= 40, f"Expected 40+ use cases, got {len(detector.use_cases)}"
        assert detector.keyword_map is not None

    def test_extract_keywords_simple(self, detector):
        """Test keyword extraction."""
        keywords = detector._extract_keywords("Tell me about interviews")
        assert "interviews" in keywords
        assert len(keywords) > 0

    def test_detect_intent_career_interview(self, detector):
        """Test detection of career/interview use case."""
        use_case_id, confidence, match = detector.detect_intent(
            "Tell me about preparing for a behavioral interview"
        )
        assert use_case_id is not None
        assert confidence > 0.3
        assert "C" in use_case_id  # Career domain

    def test_detect_intent_salary(self, detector):
        """Test detection of salary/compensation use case."""
        use_case_id, confidence, match = detector.detect_intent(
            "How do I negotiate my salary?",
            confidence_threshold=0.0
        )
        assert use_case_id is not None
        assert confidence > 0.2

    def test_detect_intent_relationships_conflict(self, detector):
        """Test detection of relationship conflict use case."""
        use_case_id, confidence, match = detector.detect_intent(
            "I'm having conflict with my partner"
        )
        assert use_case_id is not None
        assert confidence > 0.3

    def test_detect_intent_health_fitness(self, detector):
        """Test detection of health/fitness use case."""
        use_case_id, confidence, match = detector.detect_intent(
            "How can I improve my fitness and exercise?"
        )
        assert use_case_id is not None
        assert confidence > 0.3

    def test_detect_intent_mental_health(self, detector):
        """Test detection of mental health use case."""
        use_case_id, confidence, match = detector.detect_intent(
            "I'm feeling stressed and anxious",
            confidence_threshold=0.0
        )
        assert use_case_id is not None
        assert confidence > 0.05  # Prefix match on "stressed" -> "stress"

    def test_detect_intent_finance_budgeting(self, detector):
        """Test detection of budgeting use case."""
        use_case_id, confidence, match = detector.detect_intent(
            "How do I create a budget?",
            confidence_threshold=0.0
        )
        assert use_case_id is not None
        assert confidence > 0.2

    def test_detect_intent_personal_growth_habit(self, detector):
        """Test detection of habit building use case."""
        use_case_id, confidence, match = detector.detect_intent(
            "I want to build better habits",
            confidence_threshold=0.0
        )
        assert use_case_id is not None
        assert confidence > 0.1  # Exact match on "habit" -> "habit"

    def test_detect_intent_continuous_multi_turn(self, detector):
        """Test continuous detection across conversation."""
        messages = [
            {"role": "user", "content": "Hey how are you?"},
            {"role": "assistant", "content": "I'm good!"},
            {"role": "user", "content": "I want to prepare for an interview"},
        ]
        use_case_id, confidence, _ = detector.detect_intent_continuous(messages, confidence_threshold=0.0)
        assert use_case_id is not None
        assert confidence > 0.2

    def test_confidence_threshold_enforcement(self, detector):
        """Test confidence threshold."""
        use_case_id, confidence, _ = detector.detect_intent(
            "interview",
            confidence_threshold=0.5
        )
        if use_case_id is not None:
            assert confidence >= 0.5

    def test_empty_input_returns_none(self, detector):
        """Test empty input handling."""
        use_case_id, confidence, _ = detector.detect_intent("")
        assert use_case_id is None
        assert confidence == 0.0

    def test_match_type_classification(self, detector):
        """Test match type is correctly classified."""
        _, _, match = detector.detect_intent("Tell me about interview prep")
        assert match.match_type in ["exact", "partial", "semantic", "none"]


class TestModeGateUI:
    """Test suite for Mode Gate UI."""

    def test_format_mode_buttons(self):
        """Test mode buttons formatting."""
        display = format_mode_buttons()
        assert "Bas baatein" in display
        assert "record" in display.lower()
        assert "[A]" in display
        assert "[B]" in display

    def test_handle_mode_selection_a(self):
        """Test handling of mode selection A."""
        mode, action = handle_mode_selection("A")
        assert mode == "small_talk"
        assert action["next_action"] == "continue_small_talk"

    def test_handle_mode_selection_b(self):
        """Test handling of mode selection B."""
        mode, action = handle_mode_selection("B")
        assert mode == "guided"
        assert action["next_action"] == "show_use_cases"

    def test_handle_mode_selection_lowercase(self):
        """Test case-insensitive selection."""
        mode_a, _ = handle_mode_selection("a")
        mode_b, _ = handle_mode_selection("b")
        assert mode_a == "small_talk"
        assert mode_b == "guided"

    def test_handle_mode_selection_invalid(self):
        """Test invalid selection handling."""
        mode, action = handle_mode_selection("invalid")
        assert mode is None
        assert action["next_action"] == "ask_again"

    def test_mode_state_initialization(self):
        """Test ModeState initialization."""
        state = ModeState()
        assert state.current_mode is None

    def test_mode_state_set_mode(self):
        """Test setting mode."""
        state = ModeState("small_talk")
        assert state.current_mode == "small_talk"

    def test_mode_state_transition(self):
        """Test mode transition."""
        state = ModeState("small_talk")
        changed = state.set_mode("guided")
        assert changed is True
        assert state.current_mode == "guided"

    def test_mode_state_history(self):
        """Test mode history tracking."""
        state = ModeState("small_talk")
        state.set_mode("guided")
        history = state.get_mode_history()
        assert "small_talk" in history
        assert "guided" in history

    def test_format_mode_transition_prompt(self):
        """Test transition prompt formatting."""
        prompt = format_mode_transition_prompt("small_talk", "guided")
        assert len(prompt) > 0


class TestIntentIntegration:
    """Integration tests."""

    def test_end_to_end_workflow(self):
        """Test end-to-end intent detection + mode selection."""
        detector = IntentDetector(use_llm_ranking=False)

        user_input = "I want to prepare for an interview"
        use_case_id, confidence, match = detector.detect_intent(user_input, confidence_threshold=0.0)

        assert use_case_id is not None
        assert confidence > 0.2

        mode, action = handle_mode_selection("B")
        assert mode == "guided"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
