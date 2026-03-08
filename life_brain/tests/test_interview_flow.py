"""
Test suite for structured interview flow module.

Tests cover:
- Session creation and management
- Question progression
- Response recording
- Stage advancement
- Session lifecycle
"""

import pytest

from life_brain.conversation.interview_flow import (
    InterviewFlowManager,
    InterviewSession,
    InterviewQuestion,
    InterviewStage,
    InterviewStatus,
)


class TestInterviewQuestion:
    """Test InterviewQuestion dataclass."""

    def test_create_question(self):
        """Test creating interview question."""
        question = InterviewQuestion(
            question_id="q1",
            stage=InterviewStage.EXPLORATION,
            question_text="What's the main issue?",
            sequence=1,
        )

        assert question.question_id == "q1"
        assert question.stage == InterviewStage.EXPLORATION


class TestInterviewSession:
    """Test InterviewSession dataclass."""

    def test_create_session(self):
        """Test creating interview session."""
        session = InterviewSession(
            session_id="int_001",
            domain="career",
            respondent_name="John",
        )

        assert session.session_id == "int_001"
        assert session.status == InterviewStatus.PLANNED

    def test_to_dict(self):
        """Test converting session to dict."""
        session = InterviewSession(
            session_id="int_002",
            domain="health",
            respondent_name="Jane",
        )

        d = session.to_dict()
        assert d["session_id"] == "int_002"
        assert d["status"] == "planned"


class TestInterviewFlowManager:
    """Test InterviewFlowManager functionality."""

    def test_create_manager(self):
        """Test creating interview manager."""
        manager = InterviewFlowManager()
        assert len(manager.sessions) == 0

    def test_create_session(self):
        """Test creating interview session."""
        manager = InterviewFlowManager()
        session, error = manager.create_session("career", "John")

        assert error is None
        assert session is not None
        assert session.domain == "career"

    def test_create_session_empty_domain(self):
        """Test creating session with empty domain."""
        manager = InterviewFlowManager()
        session, error = manager.create_session("", "John")

        assert error is not None
        assert session is None

    def test_create_session_custom_id(self):
        """Test creating session with custom ID."""
        manager = InterviewFlowManager()
        session, _ = manager.create_session("health", "Jane", session_id="custom_123")

        assert session.session_id == "custom_123"

    def test_start_session(self):
        """Test starting interview session."""
        manager = InterviewFlowManager()
        session, _ = manager.create_session("career", "John")
        started, error = manager.start_session(session.session_id)

        assert error is None
        assert started.status == InterviewStatus.IN_PROGRESS

    def test_start_nonexistent_session(self):
        """Test starting nonexistent session."""
        manager = InterviewFlowManager()
        session, error = manager.start_session("nonexistent")

        assert error is not None
        assert session is None

    def test_get_current_question(self):
        """Test getting current question."""
        manager = InterviewFlowManager()
        session, _ = manager.create_session("career")
        manager.start_session(session.session_id)

        question, error = manager.get_current_question(session.session_id)

        assert error is None
        assert question is not None

    def test_record_response(self):
        """Test recording response."""
        manager = InterviewFlowManager()
        session, _ = manager.create_session("career")
        manager.start_session(session.session_id)
        question, _ = manager.get_current_question(session.session_id)

        response, error = manager.record_response(
            session.session_id, question.question_id, "This is my answer"
        )

        assert error is None
        assert response is not None
        assert response.respondent_answer == "This is my answer"

    def test_record_empty_response(self):
        """Test recording empty response."""
        manager = InterviewFlowManager()
        session, _ = manager.create_session("career")
        manager.start_session(session.session_id)

        response, error = manager.record_response(
            session.session_id, "q1", ""
        )

        assert error is not None
        assert response is None

    def test_advance_to_next_question(self):
        """Test advancing to next question."""
        manager = InterviewFlowManager()
        session, _ = manager.create_session("career")
        manager.start_session(session.session_id)

        initial_index = session.current_question_index
        manager.advance_to_next_question(session.session_id)

        # Check if index advanced or stage changed
        assert (
            session.current_question_index > initial_index
            or session.current_stage != InterviewStage.INTRO
        )

    def test_pause_session(self):
        """Test pausing interview session."""
        manager = InterviewFlowManager()
        session, _ = manager.create_session("career")
        manager.start_session(session.session_id)
        paused, error = manager.pause_session(session.session_id)

        assert error is None
        assert paused.status == InterviewStatus.PAUSED

    def test_resume_session(self):
        """Test resuming paused session."""
        manager = InterviewFlowManager()
        session, _ = manager.create_session("career")
        manager.start_session(session.session_id)
        manager.pause_session(session.session_id)
        resumed, error = manager.resume_session(session.session_id)

        assert error is None
        assert resumed.status == InterviewStatus.IN_PROGRESS

    def test_end_session(self):
        """Test ending interview session."""
        manager = InterviewFlowManager()
        session, _ = manager.create_session("career")
        manager.start_session(session.session_id)
        ended, error = manager.end_session(session.session_id)

        assert error is None
        assert ended.status == InterviewStatus.COMPLETED

    def test_get_session(self):
        """Test retrieving session."""
        manager = InterviewFlowManager()
        session, _ = manager.create_session("career", "John")

        retrieved = manager.get_session(session.session_id)
        assert retrieved is not None
        assert retrieved.respondent_name == "John"

    def test_get_nonexistent_session(self):
        """Test retrieving nonexistent session."""
        manager = InterviewFlowManager()
        session = manager.get_session("nonexistent")
        assert session is None

    def test_session_summary(self):
        """Test session summary."""
        manager = InterviewFlowManager()
        session, _ = manager.create_session("career")
        manager.start_session(session.session_id)
        question, _ = manager.get_current_question(session.session_id)
        manager.record_response(session.session_id, question.question_id, "Test answer")

        summary = manager.get_session_summary(session.session_id)
        assert summary is not None
        assert summary["total_responses"] == 1

    def test_export_session(self):
        """Test exporting session."""
        manager = InterviewFlowManager()
        session, _ = manager.create_session("career")

        exported = manager.export_session(session.session_id)
        assert exported is not None
        assert exported["session_id"] == session.session_id

    def test_export_nonexistent_session(self):
        """Test exporting nonexistent session."""
        manager = InterviewFlowManager()
        exported = manager.export_session("nonexistent")
        assert exported is None

    def test_export_all_sessions(self):
        """Test exporting all sessions."""
        manager = InterviewFlowManager()

        manager.create_session("career", "John")
        manager.create_session("health", "Jane")

        exported = manager.export_all_sessions()
        assert isinstance(exported, list)

    def test_statistics_empty(self):
        """Test statistics with no sessions."""
        manager = InterviewFlowManager()
        stats = manager.get_statistics()

        assert stats["total_sessions"] == 0

    def test_statistics_with_sessions(self):
        """Test statistics with sessions."""
        manager = InterviewFlowManager()

        session1, _ = manager.create_session("career")
        manager.start_session(session1.session_id)
        manager.end_session(session1.session_id)

        stats = manager.get_statistics()
        assert stats["total_sessions"] == 1
        assert stats["completed"] == 1

    def test_multiple_managers_independent(self):
        """Test multiple managers are independent."""
        m1 = InterviewFlowManager()
        m2 = InterviewFlowManager()

        m1.create_session("career")
        m2.create_session("health")

        assert len(m1.sessions) == 1
        assert len(m2.sessions) == 1

    def test_stage_progression(self):
        """Test interview progresses through stages."""
        manager = InterviewFlowManager()
        session, _ = manager.create_session("career")
        manager.start_session(session.session_id)

        # Should start in INTRO
        assert session.current_stage == InterviewStage.INTRO

    def test_add_custom_questions(self):
        """Test adding custom questions."""
        manager = InterviewFlowManager()

        custom_q = InterviewQuestion(
            question_id="custom_1",
            stage=InterviewStage.DEPTH,
            question_text="Custom question?",
            sequence=1,
        )
        manager.add_custom_questions(InterviewStage.DEPTH, [custom_q])

        # Verify custom questions are available
        assert InterviewStage.DEPTH in manager.custom_questions

    def test_complete_interview_flow(self):
        """Test complete interview workflow."""
        manager = InterviewFlowManager()

        # Create session
        session, _ = manager.create_session("career", "John Doe")
        assert session.status == InterviewStatus.PLANNED

        # Start session
        session, _ = manager.start_session(session.session_id)
        assert session.status == InterviewStatus.IN_PROGRESS

        # Get question and answer
        question, _ = manager.get_current_question(session.session_id)
        assert question is not None

        # Record response
        response, _ = manager.record_response(
            session.session_id, question.question_id, "Test answer"
        )
        assert response is not None

        # Get summary
        summary = manager.get_session_summary(session.session_id)
        assert summary["total_responses"] == 1

    def test_pause_and_resume_flow(self):
        """Test pause and resume workflow."""
        manager = InterviewFlowManager()
        session, _ = manager.create_session("health")
        manager.start_session(session.session_id)

        # Pause
        manager.pause_session(session.session_id)
        assert session.status == InterviewStatus.PAUSED

        # Resume
        manager.resume_session(session.session_id)
        assert session.status == InterviewStatus.IN_PROGRESS

    def test_session_with_multiple_responses(self):
        """Test session with multiple responses."""
        manager = InterviewFlowManager()
        session, _ = manager.create_session("career")
        manager.start_session(session.session_id)

        question, _ = manager.get_current_question(session.session_id)
        manager.record_response(
            session.session_id, question.question_id, "Answer 1"
        )

        manager.advance_to_next_question(session.session_id)
        question2, _ = manager.get_current_question(session.session_id)
        manager.record_response(
            session.session_id, question2.question_id, "Answer 2"
        )

        summary = manager.get_session_summary(session.session_id)
        assert summary["total_responses"] == 2

    def test_respondent_name_tracking(self):
        """Test respondent name is tracked."""
        manager = InterviewFlowManager()
        session, _ = manager.create_session("career", "Alice")

        assert session.respondent_name == "Alice"

    def test_domain_tracking(self):
        """Test domain is tracked."""
        manager = InterviewFlowManager()
        session, _ = manager.create_session("relationships")

        assert session.domain == "relationships"

    def test_response_quality_tracking(self):
        """Test response quality is recorded."""
        manager = InterviewFlowManager()
        session, _ = manager.create_session("career")
        manager.start_session(session.session_id)
        question, _ = manager.get_current_question(session.session_id)

        response, _ = manager.record_response(
            session.session_id, question.question_id, "Test", quality=0.85
        )

        assert response.response_quality == 0.85

    def test_session_persistence(self):
        """Test session data persists."""
        manager = InterviewFlowManager()
        session1, _ = manager.create_session("career", "John")
        session_id = session1.session_id

        # Retrieve same session
        session2 = manager.get_session(session_id)
        assert session2.respondent_name == "John"

    def test_invalid_stage_transition(self):
        """Test handling of invalid transitions."""
        manager = InterviewFlowManager()
        session, _ = manager.create_session("career")

        # Try to get question without starting
        question, error = manager.get_current_question(session.session_id)
        assert error is not None
