"""
Comprehensive unit tests for life_brain/conversation/flows.py

Tests cover:
- FlowState dataclass initialization and updates
- small_talk_flow() - Free-form conversation with passive capture
- guided_flow() - Structured conversation with expert guidance
- process_guided_answer() - Answer processing in guided mode
- wrap_up_flow() - Flow termination and summary
- orchestrate_flow() - Main routing orchestrator
- guided_flow_entry_point() - Entry point integration
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from life_brain.conversation.flows import (
    FlowState,
    small_talk_flow,
    guided_flow,
    process_guided_answer,
    wrap_up_flow,
    orchestrate_flow,
    guided_flow_entry_point,
)


# ──────────────────────────────────────────────────────────────────────────
# Tests for FlowState Dataclass
# ──────────────────────────────────────────────────────────────────────────


class TestFlowStateInitialization:
    """Test FlowState initialization and defaults."""

    def test_flow_state_small_talk_mode(self):
        """Test creating FlowState with small_talk mode."""
        state = FlowState(mode="small_talk")
        assert state.mode == "small_talk"
        assert state.messages == []
        assert state.captured_nuggets == []
        assert state.current_use_case_id is None
        assert state.current_expert is None

    def test_flow_state_guided_mode(self):
        """Test creating FlowState with guided mode."""
        state = FlowState(mode="guided")
        assert state.mode == "guided"
        assert state.messages == []
        assert state.captured_nuggets == []

    def test_flow_state_default_confidence(self):
        """Test default confidence value."""
        state = FlowState(mode="small_talk")
        assert state.confidence == 0.6

    def test_flow_state_custom_confidence(self):
        """Test setting custom confidence value."""
        state = FlowState(mode="guided", confidence=0.9)
        assert state.confidence == 0.9

    def test_flow_state_timestamps_created(self):
        """Test that timestamps are auto-created."""
        state = FlowState(mode="small_talk")
        assert state.created_at is not None
        assert state.last_activity_at is not None
        assert isinstance(state.created_at, str)
        assert isinstance(state.last_activity_at, str)

    def test_flow_state_timestamps_are_iso_format(self):
        """Test timestamps are in ISO format."""
        state = FlowState(mode="small_talk")
        # Should be parseable as ISO datetime
        try:
            datetime.fromisoformat(state.created_at.replace('Z', '+00:00'))
            datetime.fromisoformat(state.last_activity_at.replace('Z', '+00:00'))
        except ValueError:
            pytest.fail("Timestamps are not in ISO format")

    def test_flow_state_messages_list_mutation(self):
        """Test that messages list can be mutated."""
        state = FlowState(mode="small_talk")
        state.messages.append({"role": "user", "content": "test"})
        assert len(state.messages) == 1
        assert state.messages[0]["content"] == "test"

    def test_flow_state_captured_nuggets_mutation(self):
        """Test that captured_nuggets list can be mutated."""
        state = FlowState(mode="small_talk")
        state.captured_nuggets.append({"text": "nugget", "confidence": 0.7})
        assert len(state.captured_nuggets) == 1
        assert state.captured_nuggets[0]["confidence"] == 0.7

    def test_flow_state_independent_instances(self):
        """Test that FlowState instances don't share mutable defaults."""
        state1 = FlowState(mode="small_talk")
        state2 = FlowState(mode="guided")

        state1.messages.append({"role": "user", "content": "state1"})
        assert len(state2.messages) == 0  # Should be independent


# ──────────────────────────────────────────────────────────────────────────
# Tests for small_talk_flow() Function
# ──────────────────────────────────────────────────────────────────────────


class TestSmallTalkFlowBasic:
    """Test basic small_talk_flow() functionality."""

    @patch("life_brain.conversation.flows.IntentDetector")
    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_small_talk_flow_creates_default_detector(self, mock_get_expert, mock_get_use_case, mock_detector_class):
        """Test flow creates IntentDetector if not provided."""
        mock_detector_instance = Mock()
        mock_detector_instance.detect_intent.return_value = (None, 0.3)
        mock_detector_instance.should_suggest_expert.return_value = False
        mock_detector_class.return_value = mock_detector_instance

        result = small_talk_flow("hello")

        assert mock_detector_class.called
        assert result["mode"] == "small_talk"

    @patch("life_brain.conversation.flows.IntentDetector")
    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_small_talk_flow_uses_provided_detector(self, mock_get_expert, mock_get_use_case, mock_detector_class):
        """Test flow uses provided IntentDetector."""
        mock_detector = Mock()
        mock_detector.detect_intent.return_value = (None, 0.3)
        mock_detector.should_suggest_expert.return_value = False

        result = small_talk_flow("hello", detector=mock_detector)

        mock_detector.detect_intent.assert_called()
        assert not mock_detector_class.called

    @patch("life_brain.conversation.flows.IntentDetector")
    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_small_talk_flow_creates_default_state(self, mock_get_expert, mock_get_use_case, mock_detector_class):
        """Test flow creates FlowState if not provided."""
        mock_detector_instance = Mock()
        mock_detector_instance.detect_intent.return_value = (None, 0.3)
        mock_detector_instance.should_suggest_expert.return_value = False
        mock_detector_class.return_value = mock_detector_instance

        result = small_talk_flow("hello")

        assert result["state"] is not None
        assert isinstance(result["state"], FlowState)
        assert result["state"].mode == "small_talk"

    @patch("life_brain.conversation.flows.IntentDetector")
    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_small_talk_flow_uses_provided_state(self, mock_get_expert, mock_get_use_case, mock_detector_class):
        """Test flow uses provided FlowState."""
        mock_detector = Mock()
        mock_detector.detect_intent.return_value = (None, 0.3)
        mock_detector.should_suggest_expert.return_value = False
        mock_detector_class.return_value = mock_detector

        existing_state = FlowState(mode="small_talk")
        existing_state.messages.append({"role": "user", "content": "previous"})

        result = small_talk_flow("hello", state=existing_state)

        assert result["state"] == existing_state
        assert len(result["state"].messages) == 2  # Previous + new

    @patch("life_brain.conversation.flows.IntentDetector")
    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_small_talk_flow_appends_to_messages(self, mock_get_expert, mock_get_use_case, mock_detector_class):
        """Test flow appends user message to state messages."""
        mock_detector = Mock()
        mock_detector.detect_intent.return_value = (None, 0.3)
        mock_detector.should_suggest_expert.return_value = False
        mock_detector_class.return_value = mock_detector

        state = FlowState(mode="small_talk")
        result = small_talk_flow("test message", state=state)

        assert len(result["state"].messages) == 1
        assert result["state"].messages[0]["role"] == "user"
        assert result["state"].messages[0]["content"] == "test message"

    @patch("life_brain.conversation.flows.IntentDetector")
    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_small_talk_flow_returns_dict(self, mock_get_expert, mock_get_use_case, mock_detector_class):
        """Test flow returns proper dict structure."""
        mock_detector = Mock()
        mock_detector.detect_intent.return_value = (None, 0.3)
        mock_detector.should_suggest_expert.return_value = False
        mock_detector_class.return_value = mock_detector

        result = small_talk_flow("test")

        assert isinstance(result, dict)
        assert "mode" in result
        assert "system_message" in result
        assert "next_action" in result
        assert "captured_nuggets" in result
        assert "expert_suggestion" in result
        assert "state" in result

    @patch("life_brain.conversation.flows.IntentDetector")
    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_small_talk_flow_has_system_message(self, mock_get_expert, mock_get_use_case, mock_detector_class):
        """Test flow generates system message."""
        mock_detector = Mock()
        mock_detector.detect_intent.return_value = (None, 0.3)
        mock_detector.should_suggest_expert.return_value = False
        mock_detector_class.return_value = mock_detector

        result = small_talk_flow("test message")

        assert result["system_message"] is not None
        assert isinstance(result["system_message"], str)
        assert len(result["system_message"]) > 0


class TestSmallTalkFlowWithExpertSuggestion:
    """Test small_talk_flow() with expert suggestions."""

    @patch("life_brain.conversation.flows.IntentDetector")
    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_small_talk_suggests_expert_high_confidence(self, mock_get_expert, mock_get_use_case, mock_detector_class):
        """Test flow suggests expert when confidence high and conditions met."""
        mock_detector = Mock()
        mock_detector.detect_intent.return_value = ("C1", 0.9)  # High confidence
        mock_detector.should_suggest_expert.return_value = True
        mock_detector_class.return_value = mock_detector

        mock_use_case = {"expert": "satya_nadella", "title": "Interview Prep"}
        mock_get_use_case.return_value = mock_use_case

        mock_expert = {
            "real_name": "Satya Nadella",
            "role": "Empathetic interviewer",
            "opener": "Tell me about...",
        }
        mock_get_expert.return_value = mock_expert

        result = small_talk_flow("tell me about interview prep")

        assert result["expert_suggestion"] is not None
        assert "Satya Nadella" in result["expert_suggestion"]
        assert result["next_action"] == "suggest_expert"
        mock_detector.mark_expert_suggested.assert_called_once()

    @patch("life_brain.conversation.flows.IntentDetector")
    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_small_talk_no_suggestion_low_confidence(self, mock_get_expert, mock_get_use_case, mock_detector_class):
        """Test flow doesn't suggest expert with low confidence."""
        mock_detector = Mock()
        mock_detector.detect_intent.return_value = ("C1", 0.3)  # Low confidence
        mock_detector.should_suggest_expert.return_value = False
        mock_detector_class.return_value = mock_detector

        result = small_talk_flow("casual chat")

        assert result["expert_suggestion"] is None
        assert result["next_action"] == "continue_small_talk"

    @patch("life_brain.conversation.flows.IntentDetector")
    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_small_talk_expert_not_found(self, mock_get_expert, mock_get_use_case, mock_detector_class):
        """Test flow handles expert not found gracefully."""
        mock_detector = Mock()
        mock_detector.detect_intent.return_value = ("C1", 0.9)
        mock_detector.should_suggest_expert.return_value = True
        mock_detector_class.return_value = mock_detector

        mock_get_use_case.return_value = {"expert": "unknown_expert"}
        mock_get_expert.return_value = None  # Expert not found

        result = small_talk_flow("interview")

        assert result["expert_suggestion"] is None


class TestSmallTalkFlowPassiveCapture:
    """Test passive capture in small_talk_flow()."""

    @patch("life_brain.conversation.flows.IntentDetector")
    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_small_talk_captures_long_messages(self, mock_get_expert, mock_get_use_case, mock_detector_class):
        """Test flow captures messages longer than 20 chars."""
        mock_detector = Mock()
        mock_detector.detect_intent.return_value = (None, 0.3)
        mock_detector.should_suggest_expert.return_value = False
        mock_detector_class.return_value = mock_detector

        long_message = "This is a message that is definitely longer than twenty characters"
        result = small_talk_flow(long_message)

        assert len(result["captured_nuggets"]) > 0
        assert result["captured_nuggets"][0]["raw_text"] == long_message
        assert result["captured_nuggets"][0]["confidence"] == 0.6

    @patch("life_brain.conversation.flows.IntentDetector")
    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_small_talk_ignores_short_messages(self, mock_get_expert, mock_get_use_case, mock_detector_class):
        """Test flow ignores messages shorter than 20 chars."""
        mock_detector = Mock()
        mock_detector.detect_intent.return_value = (None, 0.3)
        mock_detector.should_suggest_expert.return_value = False
        mock_detector_class.return_value = mock_detector

        short_message = "short"
        result = small_talk_flow(short_message)

        assert len(result["captured_nuggets"]) == 0


# ──────────────────────────────────────────────────────────────────────────
# Tests for guided_flow() Function
# ──────────────────────────────────────────────────────────────────────────


class TestGuidedFlowBasic:
    """Test basic guided_flow() functionality."""

    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_guided_flow_with_use_case(self, mock_get_expert, mock_get_use_case):
        """Test guided flow with valid use case."""
        mock_use_case = {
            "id": "C1",
            "title": "Interview Prep",
            "expert": "satya_nadella",
            "questions": ["Question 1?", "Question 2?"],
        }
        mock_get_use_case.return_value = mock_use_case

        mock_expert = {
            "real_name": "Satya Nadella",
            "role": "Interviewer",
            "opener": "Tell me...",
        }
        mock_get_expert.return_value = mock_expert

        result = guided_flow("C1")

        assert result["mode"] == "guided"
        assert result["current_use_case"] == mock_use_case
        assert result["system_message"] is not None

    @patch("life_brain.conversation.flows.get_use_case")
    def test_guided_flow_unknown_use_case_raises(self, mock_get_use_case):
        """Test guided flow raises ValueError for unknown use case."""
        mock_get_use_case.return_value = None

        with pytest.raises(ValueError, match="Unknown use case"):
            guided_flow("UNKNOWN")

    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_guided_flow_creates_default_state(self, mock_get_expert, mock_get_use_case):
        """Test guided flow creates FlowState if not provided."""
        mock_get_use_case.return_value = {"title": "Test", "questions": []}
        mock_get_expert.return_value = None

        result = guided_flow("C1")

        assert result["state"] is not None
        assert isinstance(result["state"], FlowState)
        assert result["state"].mode == "guided"
        assert result["state"].current_use_case_id == "C1"

    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_guided_flow_uses_provided_state(self, mock_get_expert, mock_get_use_case):
        """Test guided flow uses provided state."""
        mock_get_use_case.return_value = {"title": "Test", "questions": []}
        mock_get_expert.return_value = None

        existing_state = FlowState(mode="guided")
        result = guided_flow("C1", state=existing_state)

        assert result["state"] == existing_state
        assert result["state"].current_use_case_id == "C1"

    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_guided_flow_returns_proper_structure(self, mock_get_expert, mock_get_use_case):
        """Test guided flow returns proper dict."""
        mock_use_case = {"title": "Test", "questions": ["Q1?"]}
        mock_get_use_case.return_value = mock_use_case
        mock_get_expert.return_value = {"real_name": "Expert", "opener": "Hi"}

        result = guided_flow("C1", expert_name="expert1")

        assert "mode" in result
        assert "system_message" in result
        assert "next_action" in result
        assert "current_use_case" in result
        assert "current_expert" in result
        assert "state" in result

    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_guided_flow_with_expert_name(self, mock_get_expert, mock_get_use_case):
        """Test guided flow accepts expert name."""
        mock_get_use_case.return_value = {"title": "Test", "questions": []}
        mock_expert = {"real_name": "Satya", "opener": "Hi"}
        mock_get_expert.return_value = mock_expert

        result = guided_flow("C1", expert_name="satya_nadella")

        assert result["current_expert"] == mock_expert
        mock_get_expert.assert_called_with("satya_nadella")

    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_guided_flow_uses_default_expert_from_use_case(self, mock_get_expert, mock_get_use_case):
        """Test guided flow uses expert from use case if not specified."""
        mock_get_use_case.return_value = {
            "title": "Test",
            "expert": "satya_nadella",
            "questions": [],
        }
        mock_expert = {"real_name": "Satya"}
        mock_get_expert.return_value = mock_expert

        result = guided_flow("C1")

        mock_get_expert.assert_called_with("satya_nadella")

    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_guided_flow_without_questions(self, mock_get_expert, mock_get_use_case):
        """Test guided flow handles use case without questions."""
        mock_get_use_case.return_value = {"title": "Test"}
        mock_get_expert.return_value = None

        result = guided_flow("C1")

        assert result["system_message"] is not None


# ──────────────────────────────────────────────────────────────────────────
# Tests for process_guided_answer() Function
# ──────────────────────────────────────────────────────────────────────────


class TestProcessGuidedAnswer:
    """Test process_guided_answer() function."""

    @patch("life_brain.conversation.flows.get_expert")
    def test_process_answer_appends_to_messages(self, mock_get_expert):
        """Test answer is appended to state messages."""
        mock_get_expert.return_value = None
        state = FlowState(mode="guided")

        result = process_guided_answer("My answer", state)

        assert len(result["state"].messages) == 1
        assert result["state"].messages[0]["role"] == "user"
        assert result["state"].messages[0]["content"] == "My answer"

    @patch("life_brain.conversation.flows.get_expert")
    def test_process_answer_with_expert(self, mock_get_expert):
        """Test answer processing with expert guidance."""
        mock_expert = {"depth_trigger": "What about...?"}
        mock_get_expert.return_value = mock_expert
        state = FlowState(mode="guided")

        result = process_guided_answer("My answer", state, expert_name="satya_nadella")

        assert result["system_message"] is not None
        assert "What about...?" in result["system_message"]

    @patch("life_brain.conversation.flows.get_expert")
    def test_process_answer_without_expert(self, mock_get_expert):
        """Test answer processing without expert."""
        mock_get_expert.return_value = None
        state = FlowState(mode="guided")

        result = process_guided_answer("My answer", state)

        assert result["system_message"] is not None
        assert "Theek hai" in result["system_message"]

    def test_process_answer_wrong_mode_raises(self):
        """Test error when processing answer in wrong mode."""
        state = FlowState(mode="small_talk")

        with pytest.raises(ValueError, match="only works in guided mode"):
            process_guided_answer("answer", state)

    @patch("life_brain.conversation.flows.get_expert")
    def test_process_answer_returns_proper_structure(self, mock_get_expert):
        """Test process_answer returns proper dict."""
        mock_get_expert.return_value = None
        state = FlowState(mode="guided")

        result = process_guided_answer("answer", state)

        assert "system_message" in result
        assert "extracted_qa" in result
        assert "next_action" in result
        assert "state" in result


# ──────────────────────────────────────────────────────────────────────────
# Tests for wrap_up_flow() Function
# ──────────────────────────────────────────────────────────────────────────


class TestWrapUpFlow:
    """Test wrap_up_flow() function."""

    def test_wrap_up_small_talk_summary(self):
        """Test wrap-up generates summary for small talk."""
        state = FlowState(mode="small_talk")
        state.captured_nuggets = [{"text": "nugget1"}, {"text": "nugget2"}]

        result = wrap_up_flow(state)

        assert result["summary"] is not None
        assert "2" in result["summary"]
        assert result["next_action"] == "end"

    def test_wrap_up_guided_summary(self):
        """Test wrap-up generates summary for guided."""
        state = FlowState(mode="guided")
        state.current_use_case_id = "C1"
        state.captured_nuggets = [{"qa": "q1"}, {"qa": "q2"}, {"qa": "q3"}]

        result = wrap_up_flow(state)

        assert result["summary"] is not None
        assert "3" in result["summary"]
        assert "C1" in result["summary"]

    def test_wrap_up_returns_proper_structure(self):
        """Test wrap_up returns proper dict."""
        state = FlowState(mode="small_talk")

        result = wrap_up_flow(state)

        assert "summary" in result
        assert "next_action" in result
        assert "state" in result

    def test_wrap_up_preserves_state(self):
        """Test wrap_up preserves state."""
        state = FlowState(mode="guided")
        state.current_use_case_id = "C1"

        result = wrap_up_flow(state)

        assert result["state"] == state
        assert result["state"].current_use_case_id == "C1"


# ──────────────────────────────────────────────────────────────────────────
# Tests for orchestrate_flow() Function
# ──────────────────────────────────────────────────────────────────────────


class TestOrchestrateFlow:
    """Test orchestrate_flow() main routing function."""

    @patch("life_brain.conversation.flows.small_talk_flow")
    def test_orchestrate_small_talk_mode(self, mock_small_talk):
        """Test orchestrate routes to small_talk_flow."""
        mock_small_talk.return_value = {"mode": "small_talk"}
        mock_detector = Mock()

        result = orchestrate_flow("message", mode="small_talk", detector=mock_detector)

        mock_small_talk.assert_called_once()
        assert result["mode"] == "small_talk"

    @patch("life_brain.conversation.flows.guided_flow")
    def test_orchestrate_guided_mode_new_flow(self, mock_guided):
        """Test orchestrate routes to guided_flow for new flow."""
        mock_guided.return_value = {"mode": "guided"}

        result = orchestrate_flow("message", mode="guided", use_case_id="C1")

        mock_guided.assert_called_once()

    @patch("life_brain.conversation.flows.process_guided_answer")
    def test_orchestrate_guided_mode_existing_flow(self, mock_process):
        """Test orchestrate routes to process_guided_answer for continuation."""
        mock_process.return_value = {"mode": "guided"}
        state = FlowState(mode="guided", current_use_case_id="C1")

        result = orchestrate_flow(
            "answer", mode="guided", use_case_id="C1", state=state
        )

        mock_process.assert_called_once()

    def test_orchestrate_guided_requires_use_case_id(self):
        """Test orchestrate requires use_case_id for guided mode."""
        with pytest.raises(ValueError, match="use_case_id required"):
            orchestrate_flow("message", mode="guided")

    def test_orchestrate_invalid_mode(self):
        """Test orchestrate rejects invalid mode."""
        with pytest.raises(ValueError, match="Unknown mode"):
            orchestrate_flow("message", mode="invalid_mode")


# ──────────────────────────────────────────────────────────────────────────
# Tests for guided_flow_entry_point() Function
# ──────────────────────────────────────────────────────────────────────────


class TestGuidedFlowEntryPoint:
    """Test guided_flow_entry_point() integration function."""

    @patch("life_brain.conversation.flows.orchestrate_flow")
    @patch("life_brain.conversation.flows.get_use_case")
    def test_entry_point_routes_to_orchestrate(self, mock_get_use_case, mock_orchestrate):
        """Test entry point calls orchestrate_flow."""
        mock_get_use_case.return_value = {"expert": "satya_nadella"}
        mock_orchestrate.return_value = {"mode": "guided"}

        conversation_result = {"mode": "guided", "use_case_id": "C1"}
        result = guided_flow_entry_point(conversation_result, "message")

        mock_orchestrate.assert_called_once()

    @patch("life_brain.conversation.flows.orchestrate_flow")
    @patch("life_brain.conversation.flows.get_use_case")
    def test_entry_point_merges_results(self, mock_get_use_case, mock_orchestrate):
        """Test entry point merges orchestrate result with conversation result."""
        mock_get_use_case.return_value = {"expert": "satya_nadella"}
        mock_orchestrate.return_value = {"mode": "guided", "state": FlowState(mode="guided")}

        conversation_result = {"mode": "guided", "use_case_id": "C1"}
        result = guided_flow_entry_point(conversation_result, "message")

        assert "initial_detection" in result
        assert result["initial_detection"] == conversation_result

    @patch("life_brain.conversation.flows.orchestrate_flow")
    @patch("life_brain.conversation.flows.get_use_case")
    def test_entry_point_extracts_expert_from_use_case(self, mock_get_use_case, mock_orchestrate):
        """Test entry point extracts expert from use case."""
        mock_get_use_case.return_value = {"expert": "satya_nadella"}
        mock_orchestrate.return_value = {"mode": "guided"}

        conversation_result = {"mode": "guided", "use_case_id": "C1"}
        result = guided_flow_entry_point(conversation_result, "message")

        call_args = mock_orchestrate.call_args
        assert call_args[1]["expert_name"] == "satya_nadella"

    @patch("life_brain.conversation.flows.orchestrate_flow")
    @patch("life_brain.conversation.flows.get_use_case")
    def test_entry_point_handles_no_use_case(self, mock_get_use_case, mock_orchestrate):
        """Test entry point handles missing use case gracefully."""
        mock_get_use_case.return_value = None
        mock_orchestrate.return_value = {"mode": "small_talk"}

        conversation_result = {"mode": "small_talk"}
        result = guided_flow_entry_point(conversation_result, "message")

        # Should still work, just no expert extracted
        assert result is not None


# ──────────────────────────────────────────────────────────────────────────
# Integration Tests (Workflow Tests)
# ──────────────────────────────────────────────────────────────────────────


class TestFlowsIntegration:
    """Integration tests for complete workflow scenarios."""

    @patch("life_brain.conversation.flows.IntentDetector")
    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_small_talk_to_guided_workflow(self, mock_get_expert, mock_get_use_case, mock_detector_class):
        """Test workflow: small talk → expert suggestion → guided flow."""
        # Setup mock detector
        mock_detector = Mock()
        mock_detector_class.return_value = mock_detector
        mock_detector.detect_intent.return_value = ("C1", 0.9)
        mock_detector.should_suggest_expert.return_value = True

        # Setup mock use case and expert
        mock_use_case = {"expert": "satya_nadella", "title": "Interview Prep"}
        mock_get_use_case.return_value = mock_use_case

        mock_expert = {"real_name": "Satya Nadella", "role": "Interviewer", "opener": "Hi"}
        mock_get_expert.return_value = mock_expert

        # Execute small talk
        result1 = small_talk_flow("I have an interview coming up")
        assert result1["next_action"] == "suggest_expert"
        assert result1["expert_suggestion"] is not None

        # Now enter guided flow
        state = result1["state"]
        result2 = guided_flow("C1", state=state)

        assert result2["mode"] == "guided"
        assert result2["state"].current_use_case_id == "C1"

    @patch("life_brain.conversation.flows.get_expert")
    def test_guided_flow_multi_turn_workflow(self, mock_get_expert):
        """Test guided flow across multiple turns."""
        mock_get_expert.return_value = {"depth_trigger": "More?"}

        with patch("life_brain.conversation.flows.get_use_case") as mock_get_use_case:
            mock_get_use_case.return_value = {
                "title": "Test",
                "questions": ["Q1?", "Q2?"],
            }

            # Start guided flow
            result1 = guided_flow("C1")
            state = result1["state"]
            # guided_flow adds first question to messages
            initial_message_count = len(state.messages)

            # Process first answer
            result2 = process_guided_answer("Answer 1", state)
            assert len(result2["state"].messages) == initial_message_count + 1

            # Process second answer
            result3 = process_guided_answer("Answer 2", result2["state"])
            assert len(result3["state"].messages) == initial_message_count + 2

            # Wrap up - process_guided_answer doesn't populate captured_nuggets,
            # so summary will show 0 Q&A pairs (as expected, this is placeholder logic)
            result4 = wrap_up_flow(result3["state"])
            assert "Extracted" in result4["summary"]
            assert "C1" in result4["summary"]

    @patch("life_brain.conversation.flows.IntentDetector")
    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_orchestrate_flow_small_talk_path(self, mock_get_expert, mock_get_use_case, mock_detector_class):
        """Test orchestrate_flow with small_talk path."""
        mock_detector = Mock()
        mock_detector_class.return_value = mock_detector
        mock_detector.detect_intent.return_value = (None, 0.3)
        mock_detector.should_suggest_expert.return_value = False

        result = orchestrate_flow(
            "just chatting", mode="small_talk", detector=mock_detector
        )

        assert result["mode"] == "small_talk"
        assert result["system_message"] is not None

    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_orchestrate_flow_guided_path(self, mock_get_expert, mock_get_use_case):
        """Test orchestrate_flow with guided path."""
        mock_get_use_case.return_value = {"title": "Test", "questions": []}
        mock_get_expert.return_value = None

        result = orchestrate_flow("starting", mode="guided", use_case_id="C1")

        assert result["mode"] == "guided"

    @patch("life_brain.conversation.flows.orchestrate_flow")
    @patch("life_brain.conversation.flows.get_use_case")
    def test_entry_point_full_workflow(self, mock_get_use_case, mock_orchestrate):
        """Test entry point with full workflow."""
        mock_get_use_case.return_value = {"expert": "satya_nadella"}
        mock_orchestrate.return_value = {"mode": "guided", "system_message": "Hi"}

        conversation_result = {"mode": "guided", "use_case_id": "C1"}
        result = guided_flow_entry_point(conversation_result, "Let's start")

        assert "initial_detection" in result
        assert "detector" in result


# ──────────────────────────────────────────────────────────────────────────
# Edge Case and Error Handling Tests
# ──────────────────────────────────────────────────────────────────────────


class TestFlowsEdgeCases:
    """Test edge cases and error conditions."""

    @patch("life_brain.conversation.flows.IntentDetector")
    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_small_talk_empty_message(self, mock_get_expert, mock_get_use_case, mock_detector_class):
        """Test small talk with empty message."""
        mock_detector = Mock()
        mock_detector_class.return_value = mock_detector
        mock_detector.detect_intent.return_value = (None, 0)
        mock_detector.should_suggest_expert.return_value = False

        result = small_talk_flow("")

        assert result["mode"] == "small_talk"
        assert result["system_message"] is not None

    @patch("life_brain.conversation.flows.IntentDetector")
    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_small_talk_very_long_message(self, mock_get_expert, mock_get_use_case, mock_detector_class):
        """Test small talk with very long message."""
        mock_detector = Mock()
        mock_detector_class.return_value = mock_detector
        mock_detector.detect_intent.return_value = (None, 0.3)
        mock_detector.should_suggest_expert.return_value = False

        long_message = "x" * 10000
        result = small_talk_flow(long_message)

        assert result["mode"] == "small_talk"
        assert len(result["state"].messages) > 0

    @patch("life_brain.conversation.flows.get_use_case")
    @patch("life_brain.conversation.flows.get_expert")
    def test_guided_flow_empty_questions(self, mock_get_expert, mock_get_use_case):
        """Test guided flow with empty question list."""
        mock_get_use_case.return_value = {"title": "Test", "questions": []}
        mock_get_expert.return_value = None

        result = guided_flow("C1")

        assert result["mode"] == "guided"
        assert result["system_message"] is not None

    @patch("life_brain.conversation.flows.get_expert")
    def test_process_answer_empty_string(self, mock_get_expert):
        """Test processing empty answer."""
        mock_get_expert.return_value = None
        state = FlowState(mode="guided")

        result = process_guided_answer("", state)

        assert len(result["state"].messages) == 1
        assert result["state"].messages[0]["content"] == ""

    def test_flow_state_with_all_fields_set(self):
        """Test FlowState with all fields explicitly set."""
        messages = [{"role": "user", "content": "msg"}]
        nuggets = [{"text": "nugget"}]

        state = FlowState(
            mode="guided",
            messages=messages,
            current_use_case_id="C1",
            current_expert="satya_nadella",
            captured_nuggets=nuggets,
            confidence=0.9,
        )

        assert state.mode == "guided"
        assert state.messages == messages
        assert state.current_use_case_id == "C1"
        assert state.current_expert == "satya_nadella"
        assert state.captured_nuggets == nuggets
        assert state.confidence == 0.9


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
