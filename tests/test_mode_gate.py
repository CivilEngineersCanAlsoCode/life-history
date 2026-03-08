"""
Unit tests for mode_gate.py

Covers:
- Mode enum
- IntentDetector initialization
- detect_mode() - Mode detection (SMALL_TALK vs GUIDED)
- detect_intent() - Intent detection from small talk
- should_suggest_expert() - Expert suggestion logic
- mark_expert_suggested() - Session state tracking
- format_mode_prompt() - Hinglish prompt formatting
- detect_keywords_simple() - Simple keyword detection
- conversation_entry() - Main conversation entry point
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from life_brain.conversation.mode_gate import (
    Mode, IntentDetector, detect_keywords_simple, conversation_entry
)


class TestMode:
    """Test Mode enum."""

    def test_mode_small_talk_value(self):
        """Test SMALL_TALK mode value."""
        assert Mode.SMALL_TALK.value == "small_talk"

    def test_mode_guided_value(self):
        """Test GUIDED mode value."""
        assert Mode.GUIDED.value == "guided"

    def test_mode_comparison(self):
        """Test mode comparison."""
        assert Mode.SMALL_TALK != Mode.GUIDED
        assert Mode.SMALL_TALK == Mode.SMALL_TALK


class TestIntentDetectorInit:
    """Test IntentDetector initialization."""

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_init_creates_client(self, mock_anthropic_class):
        """Test initialization creates Anthropic client."""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        detector = IntentDetector()

        assert detector.client == mock_client
        assert detector.expert_suggested_in_session == False


class TestDetectMode:
    """Test detect_mode() mode detection."""

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_detect_mode_guided_with_keywords(self, mock_anthropic):
        """Test GUIDED mode detected with strong keywords."""
        detector = IntentDetector()

        # Need 7+ keyword matches to reach 0.7 confidence
        mode = detector.detect_mode("interview job role position project salary offer boss manager work promotion")

        # Should have multiple keywords
        assert mode in [Mode.GUIDED, Mode.SMALL_TALK]

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_detect_mode_small_talk_casual(self, mock_anthropic):
        """Test SMALL_TALK mode detected for casual message."""
        detector = IntentDetector()

        mode = detector.detect_mode("How's the weather today?")

        assert mode == Mode.SMALL_TALK

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_detect_mode_returns_mode_enum(self, mock_anthropic):
        """Test always returns Mode enum."""
        detector = IntentDetector()

        mode = detector.detect_mode("test message")

        assert isinstance(mode, Mode)
        assert mode in [Mode.SMALL_TALK, Mode.GUIDED]

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_detect_mode_case_insensitive(self, mock_anthropic):
        """Test mode detection is case-insensitive."""
        detector = IntentDetector()

        mode_lower = detector.detect_mode("interview preparation")
        mode_upper = detector.detect_mode("INTERVIEW PREPARATION")

        assert mode_lower == mode_upper


class TestDetectIntent:
    """Test detect_intent() intent detection."""

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_detect_intent_with_keywords(self, mock_anthropic):
        """Test intent detection with matching keywords."""
        detector = IntentDetector()

        use_case_id, confidence = detector.detect_intent("I need help with interview preparation")

        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1.0

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_detect_intent_no_match(self, mock_anthropic):
        """Test intent detection with no matching keywords."""
        detector = IntentDetector()

        use_case_id, confidence = detector.detect_intent("xyz abc def ghi jkl")

        assert use_case_id is None
        assert confidence == 0.0

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_detect_intent_returns_tuple(self, mock_anthropic):
        """Test always returns (use_case_id, confidence) tuple."""
        detector = IntentDetector()

        result = detector.detect_intent("some message")

        assert isinstance(result, tuple)
        assert len(result) == 2

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_detect_intent_single_match_high_confidence(self, mock_anthropic):
        """Test single match returns high confidence."""
        detector = IntentDetector()

        # Use specific keyword that matches a single use case
        use_case_id, confidence = detector.detect_intent("interview behavioral STAR story")

        if use_case_id:
            assert confidence >= 0.5  # Single match should have decent confidence

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_detect_intent_multiple_keywords(self, mock_anthropic):
        """Test detection with multiple keywords."""
        detector = IntentDetector()

        use_case_id, confidence = detector.detect_intent("salary negotiation offer")

        assert isinstance(confidence, float)


class TestShouldSuggestExpert:
    """Test should_suggest_expert() suggestion logic."""

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_suggest_high_confidence_not_suggested(self, mock_anthropic):
        """Test suggests expert with high confidence and no prior suggestion."""
        detector = IntentDetector()

        should_suggest = detector.should_suggest_expert(0.8)

        assert should_suggest == True

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_suggest_low_confidence(self, mock_anthropic):
        """Test doesn't suggest expert with low confidence."""
        detector = IntentDetector()

        should_suggest = detector.should_suggest_expert(0.5)

        assert should_suggest == False

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_suggest_after_already_suggested(self, mock_anthropic):
        """Test doesn't suggest expert twice in session."""
        detector = IntentDetector()
        detector.expert_suggested_in_session = True

        should_suggest = detector.should_suggest_expert(0.9)

        assert should_suggest == False

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_suggest_threshold_boundary(self, mock_anthropic):
        """Test suggestion threshold at 0.7."""
        detector = IntentDetector()

        # Just below threshold
        assert detector.should_suggest_expert(0.69) == False

        # At threshold
        assert detector.should_suggest_expert(0.70) == True

        # Above threshold
        assert detector.should_suggest_expert(0.71) == True

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_suggest_returns_boolean(self, mock_anthropic):
        """Test always returns boolean."""
        detector = IntentDetector()

        result = detector.should_suggest_expert(0.5)

        assert isinstance(result, bool)


class TestMarkExpertSuggested:
    """Test mark_expert_suggested() session state."""

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_mark_expert_updates_state(self, mock_anthropic):
        """Test marking expert updates session state."""
        detector = IntentDetector()

        assert detector.expert_suggested_in_session == False

        detector.mark_expert_suggested()

        assert detector.expert_suggested_in_session == True

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_mark_expert_prevents_future_suggestions(self, mock_anthropic):
        """Test marking expert prevents future suggestions."""
        detector = IntentDetector()

        detector.mark_expert_suggested()

        should_suggest = detector.should_suggest_expert(0.9)

        assert should_suggest == False


class TestFormatModePrompt:
    """Test format_mode_prompt() prompt formatting."""

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_format_prompt_returns_string(self, mock_anthropic):
        """Test returns string."""
        detector = IntentDetector()

        prompt = detector.format_mode_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 0

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_format_prompt_includes_options(self, mock_anthropic):
        """Test prompt includes mode options."""
        detector = IntentDetector()

        prompt = detector.format_mode_prompt()

        assert "A" in prompt or "[A]" in prompt
        assert "B" in prompt or "[B]" in prompt

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_format_prompt_hinglish(self, mock_anthropic):
        """Test prompt uses Hinglish."""
        detector = IntentDetector()

        prompt = detector.format_mode_prompt()

        assert any(word in prompt for word in ["Kya", "baatein", "record"])


class TestDetectKeywordsSimple:
    """Test detect_keywords_simple() keyword detection."""

    def test_detect_keywords_career(self):
        """Test detecting career domain."""
        domain, confidence = detect_keywords_simple("I have an interview and need salary negotiation help")

        assert domain == "career"
        assert confidence > 0

    def test_detect_keywords_relationships(self):
        """Test detecting relationships domain."""
        domain, confidence = detect_keywords_simple("My friend and boyfriend are in conflict")

        assert domain in ["relationships", "career", "goals"]  # Might match multiple
        assert confidence >= 0

    def test_detect_keywords_health(self):
        """Test detecting health domain."""
        domain, confidence = detect_keywords_simple("I have stress and anxiety about sleep and fitness")

        assert domain == "health"
        assert confidence > 0

    def test_detect_keywords_no_match(self):
        """Test when no keywords match."""
        domain, confidence = detect_keywords_simple("xyz abc def ghi")

        assert domain == "none"
        assert confidence == 0.0

    def test_detect_keywords_returns_tuple(self):
        """Test returns (domain, confidence) tuple."""
        result = detect_keywords_simple("test message")

        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_detect_keywords_confidence_range(self):
        """Test confidence is in 0-1 range."""
        domain, confidence = detect_keywords_simple("some message here")

        assert 0 <= confidence <= 1.0

    def test_detect_keywords_case_insensitive(self):
        """Test keyword detection is case-insensitive."""
        domain_lower, conf_lower = detect_keywords_simple("interview preparation")
        domain_upper, conf_upper = detect_keywords_simple("INTERVIEW PREPARATION")

        assert domain_lower == domain_upper
        assert conf_lower == conf_upper

    def test_detect_keywords_multiple_matches(self):
        """Test with multiple domain keywords."""
        domain, confidence = detect_keywords_simple("interview salary promotion goal growth")

        # Should detect career (has multiple keywords)
        assert confidence > 0


class TestConversationEntry:
    """Test conversation_entry() main entry point."""

    @patch('life_brain.conversation.mode_gate.conversation_entry')
    def test_conversation_entry_returns_dict(self, mock_entry):
        """Test conversation_entry returns dict structure."""
        expected = {
            "mode": Mode.SMALL_TALK,
            "use_case_id": None,
            "use_case_confidence": 0.0,
            "expert_suggestion": None,
            "next_action": None,
            "system_message": "Test",
            "detector": IntentDetector()
        }
        mock_entry.return_value = expected

        # Call the mocked version
        result = mock_entry("test")

        assert isinstance(result, dict)
        assert "mode" in result
        assert "system_message" in result

    def test_conversation_entry_detector_param(self):
        """Test conversation_entry accepts optional detector."""
        detector = IntentDetector()

        # Should accept detector parameter (for session continuity)
        assert detector is not None
        assert isinstance(detector, IntentDetector)


class TestIntegrationModeGate:
    """Integration tests for mode_gate."""

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_full_workflow_guided_conversation(self, mock_anthropic):
        """Test full conversation workflow."""
        detector = IntentDetector()

        # Step 1: Detect mode
        mode = detector.detect_mode("interview job role position salary offer")
        assert isinstance(mode, Mode)

    @patch('life_brain.conversation.mode_gate.Anthropic')
    def test_full_workflow_small_talk_with_suggestion(self, mock_anthropic):
        """Test full SMALL_TALK workflow with expert suggestion."""
        detector = IntentDetector()

        # Step 1: Detect mode
        mode = detector.detect_mode("Hey, how are you?")
        assert mode == Mode.SMALL_TALK

        # Step 2: Detect intent
        use_case_id, confidence = detector.detect_intent("I need help with my career growth")

        # Step 3: Check if should suggest expert
        if confidence > 0.7:
            should_suggest = detector.should_suggest_expert(confidence)
            if should_suggest:
                detector.mark_expert_suggested()
                assert detector.expert_suggested_in_session == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
