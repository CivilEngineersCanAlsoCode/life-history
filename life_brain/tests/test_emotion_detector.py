"""
Tests for emotional tone detection and mental health expert suggestion.

Tests cover:
- Detecting stressed, anxious, frustrated, excited, uncertain, neutral
- Confidence scoring
- Mental health suggestion trigger logic
- History-based detection
- Edge cases
"""

import pytest

from life_brain.conversation.emotion_detector import (
    detect_emotion,
    detect_emotion_from_history,
    EmotionResult,
)


class TestDetectEmotion:
    """Test single-message emotion detection."""

    def test_detect_stressed(self):
        result = detect_emotion("I'm completely overwhelmed with deadlines")
        assert result.primary_emotion == "stressed"
        assert result.confidence > 0

    def test_detect_anxious(self):
        result = detect_emotion("I'm so worried about the interview, what if I fail")
        assert result.primary_emotion == "anxious"
        assert result.confidence > 0

    def test_detect_frustrated(self):
        result = detect_emotion("This is so frustrating, nothing works and I'm fed up")
        assert result.primary_emotion == "frustrated"
        assert result.confidence > 0

    def test_detect_excited(self):
        result = detect_emotion("I'm so excited, this is amazing news!")
        assert result.primary_emotion == "excited"
        assert result.confidence > 0

    def test_detect_uncertain(self):
        result = detect_emotion("I'm not sure what I should do, maybe I should switch jobs")
        assert result.primary_emotion == "uncertain"
        assert result.confidence > 0

    def test_neutral_empty_message(self):
        result = detect_emotion("")
        assert result.primary_emotion == "neutral"
        assert result.confidence == 0.0
        assert result.suggest_mental_health is False

    def test_neutral_no_signals(self):
        result = detect_emotion("The weather is nice today.")
        assert result.primary_emotion == "neutral"
        assert result.suggest_mental_health is False

    def test_confidence_range(self):
        result = detect_emotion("I'm stressed and overwhelmed by the workload")
        assert 0 <= result.confidence <= 1

    def test_all_emotions_in_result(self):
        result = detect_emotion("I'm overwhelmed and worried")
        assert isinstance(result.all_emotions, dict)


class TestMentalHealthSuggestion:
    """Test mental health expert suggestion logic."""

    def test_stressed_triggers_suggestion(self):
        result = detect_emotion("I'm completely overwhelmed and burning out, can't cope anymore")
        assert result.suggest_mental_health is True
        assert result.suggestion_message is not None

    def test_anxious_triggers_suggestion(self):
        result = detect_emotion("I'm so worried and anxious, I don't know what to do")
        assert result.suggest_mental_health is True
        assert result.suggestion_message is not None

    def test_frustrated_triggers_suggestion(self):
        result = detect_emotion("I'm so frustrated and fed up, sick of this, nothing works")
        assert result.suggest_mental_health is True
        assert result.suggestion_message is not None

    def test_excited_does_not_trigger(self):
        result = detect_emotion("I'm so excited and thrilled about this!")
        assert result.suggest_mental_health is False

    def test_neutral_does_not_trigger(self):
        result = detect_emotion("Tell me about my career history")
        assert result.suggest_mental_health is False

    def test_suggestion_message_is_string(self):
        result = detect_emotion("I'm overwhelmed and stressed and can't cope")
        if result.suggest_mental_health:
            assert isinstance(result.suggestion_message, str)
            assert len(result.suggestion_message) > 0

    def test_no_suggestion_when_none(self):
        result = detect_emotion("Everything is going well today")
        assert result.suggestion_message is None


class TestHistoryDetection:
    """Test emotion detection across conversation history."""

    def test_history_empty(self):
        result = detect_emotion_from_history([])
        assert result.primary_emotion == "neutral"
        assert result.suggest_mental_health is False

    def test_history_single_message(self):
        result = detect_emotion_from_history(["I'm overwhelmed with deadlines"])
        assert result.primary_emotion == "stressed"

    def test_history_persistent_stress(self):
        messages = [
            "I'm really stressed about the project",
            "The workload is overwhelming me",
            "I can't cope with all these deadlines",
        ]
        result = detect_emotion_from_history(messages)
        assert result.primary_emotion == "stressed"
        assert result.suggest_mental_health is True

    def test_history_mixed_emotions(self):
        messages = [
            "Great news today!",
            "But I'm worried about the next step",
        ]
        result = detect_emotion_from_history(messages)
        assert result.primary_emotion in ["anxious", "uncertain", "excited"]

    def test_history_confidence_range(self):
        messages = ["I'm stressed", "overwhelmed", "burning out"]
        result = detect_emotion_from_history(messages)
        assert 0 <= result.confidence <= 1

    def test_all_emotions_tracked_in_history(self):
        messages = ["I'm anxious about the deadline and stressed about workload"]
        result = detect_emotion_from_history(messages)
        assert isinstance(result.all_emotions, dict)


class TestEdgeCases:
    """Test edge cases."""

    def test_whitespace_only(self):
        result = detect_emotion("   ")
        assert result.primary_emotion == "neutral"

    def test_very_long_message(self):
        msg = "I'm so stressed " * 50
        result = detect_emotion(msg)
        assert result.primary_emotion == "stressed"
        assert 0 <= result.confidence <= 1

    def test_mixed_case_detection(self):
        result = detect_emotion("I am OVERWHELMED and STRESSED OUT")
        assert result.primary_emotion == "stressed"

    def test_result_has_required_fields(self):
        result = detect_emotion("test message")
        assert hasattr(result, "primary_emotion")
        assert hasattr(result, "confidence")
        assert hasattr(result, "all_emotions")
        assert hasattr(result, "suggest_mental_health")
        assert hasattr(result, "suggestion_message")
