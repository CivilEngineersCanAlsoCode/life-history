"""
Structured interview flow for domain-specific questioning.

Manages a guided interview process where questions are asked sequentially,
responses are collected, and the interview progresses through defined stages.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class InterviewStage(Enum):
    """Stage of interview progression."""

    INTRO = "intro"  # Introduction and context setting
    EXPLORATION = "exploration"  # Initial discovery questions
    DEPTH = "depth"  # Deep dive into specific areas
    SYNTHESIS = "synthesis"  # Tying together themes
    CONCLUSION = "conclusion"  # Wrapping up and next steps


class InterviewStatus(Enum):
    """Status of interview."""

    PLANNED = "planned"  # Interview planned but not started
    IN_PROGRESS = "in_progress"  # Currently being conducted
    PAUSED = "paused"  # Temporarily paused
    COMPLETED = "completed"  # Finished
    ABANDONED = "abandoned"  # Stopped without completion


@dataclass
class InterviewQuestion:
    """Single question in interview flow."""

    question_id: str
    stage: InterviewStage
    question_text: str
    sequence: int  # Order in interview
    follow_up_questions: List[str] = field(default_factory=list)
    category: str = ""  # Topic category
    required: bool = True  # Must be answered
    skip_conditions: List[str] = field(default_factory=list)  # When to skip


@dataclass
class InterviewResponse:
    """Response to interview question."""

    response_id: str
    question_id: str
    respondent_answer: str
    follow_up_given: bool = False
    response_quality: float = 0.5  # 0-1, how complete/useful
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class InterviewSession:
    """Complete interview session."""

    session_id: str
    domain: str  # Topic domain (career, relationship, health, etc)
    respondent_name: str = "Anonymous"
    status: InterviewStatus = InterviewStatus.PLANNED
    current_stage: InterviewStage = InterviewStage.INTRO
    current_question_index: int = 0
    responses: Dict[str, InterviewResponse] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: str = ""
    completed_at: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "domain": self.domain,
            "respondent_name": self.respondent_name,
            "status": self.status.value,
            "current_stage": self.current_stage.value,
            "current_question_index": self.current_question_index,
            "total_responses": len(self.responses),
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


class InterviewFlowManager:
    """Manage structured interview flow."""

    # Default questions by stage
    DEFAULT_QUESTIONS = {
        InterviewStage.INTRO: [
            InterviewQuestion(
                question_id="intro_1",
                stage=InterviewStage.INTRO,
                question_text="What brings you here today?",
                sequence=1,
                category="context",
            ),
        ],
        InterviewStage.EXPLORATION: [
            InterviewQuestion(
                question_id="expl_1",
                stage=InterviewStage.EXPLORATION,
                question_text="Can you describe the situation in more detail?",
                sequence=2,
                category="exploration",
            ),
        ],
        InterviewStage.DEPTH: [
            InterviewQuestion(
                question_id="depth_1",
                stage=InterviewStage.DEPTH,
                question_text="What have you tried so far?",
                sequence=3,
                category="actions",
            ),
        ],
        InterviewStage.SYNTHESIS: [
            InterviewQuestion(
                question_id="syn_1",
                stage=InterviewStage.SYNTHESIS,
                question_text="What's the most important takeaway?",
                sequence=4,
                category="synthesis",
            ),
        ],
        InterviewStage.CONCLUSION: [
            InterviewQuestion(
                question_id="conc_1",
                stage=InterviewStage.CONCLUSION,
                question_text="What's your next step?",
                sequence=5,
                category="action_items",
            ),
        ],
    }

    def __init__(self):
        """Initialize interview flow manager."""
        self.sessions: Dict[str, InterviewSession] = {}
        self.session_history: List[InterviewSession] = []
        self.custom_questions: Dict[InterviewStage, List[InterviewQuestion]] = {}

    def create_session(
        self, domain: str, respondent_name: str = "Anonymous", session_id: str = ""
    ) -> Tuple[InterviewSession, Optional[str]]:
        """
        Create new interview session.

        Args:
            domain: Topic domain
            respondent_name: Name of respondent
            session_id: Optional custom session ID

        Returns:
            (InterviewSession, error if any)
        """
        if not domain or not domain.strip():
            return None, "Domain required"

        if not session_id:
            session_id = f"int_{len(self.sessions):04d}"

        session = InterviewSession(
            session_id=session_id,
            domain=domain,
            respondent_name=respondent_name,
        )

        self.sessions[session_id] = session
        return session, None

    def start_session(self, session_id: str) -> Tuple[Optional[InterviewSession], Optional[str]]:
        """Start interview session."""
        session = self.sessions.get(session_id)
        if not session:
            return None, f"Session {session_id} not found"

        if session.status != InterviewStatus.PLANNED:
            return None, f"Session already {session.status.value}"

        session.status = InterviewStatus.IN_PROGRESS
        session.started_at = datetime.now().isoformat()
        session.current_stage = InterviewStage.INTRO

        return session, None

    def get_current_question(self, session_id: str) -> Tuple[Optional[InterviewQuestion], Optional[str]]:
        """Get current question for session."""
        session = self.sessions.get(session_id)
        if not session:
            return None, f"Session {session_id} not found"

        if session.status not in [InterviewStatus.IN_PROGRESS, InterviewStatus.PAUSED]:
            return None, f"Session is {session.status.value}"

        # Get questions for current stage
        questions = self._get_stage_questions(session.current_stage)

        if session.current_question_index >= len(questions):
            return None, "No more questions in this stage"

        return questions[session.current_question_index], None

    def record_response(
        self, session_id: str, question_id: str, answer: str, quality: float = 0.7
    ) -> Tuple[Optional[InterviewResponse], Optional[str]]:
        """Record response to question."""
        session = self.sessions.get(session_id)
        if not session:
            return None, f"Session {session_id} not found"

        if not answer or not answer.strip():
            return None, "Empty answer"

        response_id = f"resp_{len(session.responses):04d}"
        response = InterviewResponse(
            response_id=response_id,
            question_id=question_id,
            respondent_answer=answer,
            response_quality=quality,
        )

        session.responses[response_id] = response
        return response, None

    def advance_to_next_question(self, session_id: str) -> Tuple[Optional[InterviewSession], Optional[str]]:
        """Move to next question in current stage."""
        session = self.sessions.get(session_id)
        if not session:
            return None, f"Session {session_id} not found"

        session.current_question_index += 1

        # Check if we've reached end of current stage
        stage_questions = self._get_stage_questions(session.current_stage)
        if session.current_question_index >= len(stage_questions):
            # Advance to next stage
            success, error = self._advance_stage(session)
            if error:
                return None, error

        return session, None

    def _advance_stage(self, session: InterviewSession) -> Tuple[bool, Optional[str]]:
        """Advance to next interview stage."""
        stages = [
            InterviewStage.INTRO,
            InterviewStage.EXPLORATION,
            InterviewStage.DEPTH,
            InterviewStage.SYNTHESIS,
            InterviewStage.CONCLUSION,
        ]

        current_idx = stages.index(session.current_stage)
        if current_idx < len(stages) - 1:
            session.current_stage = stages[current_idx + 1]
            session.current_question_index = 0
            return True, None
        else:
            # Interview complete
            session.status = InterviewStatus.COMPLETED
            session.completed_at = datetime.now().isoformat()
            self.session_history.append(session)
            return True, None

    def pause_session(self, session_id: str) -> Tuple[Optional[InterviewSession], Optional[str]]:
        """Pause interview session."""
        session = self.sessions.get(session_id)
        if not session:
            return None, f"Session {session_id} not found"

        if session.status != InterviewStatus.IN_PROGRESS:
            return None, f"Cannot pause session in {session.status.value} status"

        session.status = InterviewStatus.PAUSED
        return session, None

    def resume_session(self, session_id: str) -> Tuple[Optional[InterviewSession], Optional[str]]:
        """Resume paused interview session."""
        session = self.sessions.get(session_id)
        if not session:
            return None, f"Session {session_id} not found"

        if session.status != InterviewStatus.PAUSED:
            return None, f"Session is {session.status.value}, not paused"

        session.status = InterviewStatus.IN_PROGRESS
        return session, None

    def end_session(self, session_id: str, reason: str = "") -> Tuple[Optional[InterviewSession], Optional[str]]:
        """End interview session."""
        session = self.sessions.get(session_id)
        if not session:
            return None, f"Session {session_id} not found"

        session.status = InterviewStatus.COMPLETED
        session.completed_at = datetime.now().isoformat()
        session.notes = reason
        self.session_history.append(session)

        return session, None

    def _get_stage_questions(self, stage: InterviewStage) -> List[InterviewQuestion]:
        """Get questions for a stage."""
        if stage in self.custom_questions:
            return self.custom_questions[stage]
        return self.DEFAULT_QUESTIONS.get(stage, [])

    def add_custom_questions(
        self, stage: InterviewStage, questions: List[InterviewQuestion]
    ) -> None:
        """Add custom questions for a stage."""
        if stage not in self.custom_questions:
            self.custom_questions[stage] = []
        self.custom_questions[stage].extend(questions)

    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        """Get specific session."""
        return self.sessions.get(session_id)

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of interview session."""
        session = self.get_session(session_id)
        if not session:
            return None

        return {
            "session_id": session.session_id,
            "domain": session.domain,
            "status": session.status.value,
            "current_stage": session.current_stage.value,
            "total_responses": len(session.responses),
            "responses": [
                {
                    "question_id": r.question_id,
                    "answer": r.respondent_answer[:100] + "..."
                    if len(r.respondent_answer) > 100
                    else r.respondent_answer,
                    "quality": r.response_quality,
                }
                for r in session.responses.values()
            ],
            "created_at": session.created_at,
            "completed_at": session.completed_at,
        }

    def export_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export complete session data."""
        session = self.get_session(session_id)
        if not session:
            return None

        return session.to_dict()

    def export_all_sessions(self) -> List[Dict[str, Any]]:
        """Export all sessions."""
        return [s.to_dict() for s in self.session_history]

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about interviews."""
        if not self.session_history:
            return {
                "total_sessions": 0,
                "completed": 0,
                "abandoned": 0,
                "avg_responses": 0,
            }

        completed_count = sum(
            1 for s in self.session_history if s.status == InterviewStatus.COMPLETED
        )
        abandoned_count = sum(
            1 for s in self.session_history if s.status == InterviewStatus.ABANDONED
        )
        avg_responses = (
            sum(len(s.responses) for s in self.session_history) / len(self.session_history)
        )

        return {
            "total_sessions": len(self.session_history),
            "completed": completed_count,
            "abandoned": abandoned_count,
            "avg_responses": avg_responses,
        }
