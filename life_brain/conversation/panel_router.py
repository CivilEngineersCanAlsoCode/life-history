"""
Panel router for multi-expert sequential questioning.

Routes user questions to multiple experts sequentially, collects diverse
perspectives, and maintains conversation context across expert transitions.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time

from life_brain.conversation.expert_roster import ExpertRoster, Expert


class PanelRole(Enum):
    """Role assignment for expert in panel."""

    PRIMARY = "primary"  # Main answerer
    CHALLENGER = "challenger"  # Questions the primary
    SYNTHESIZER = "synthesizer"  # Integrates perspectives
    SPECIALIST = "specialist"  # Domain expert
    FACILITATOR = "facilitator"  # Guides conversation


@dataclass
class ExpertResponse:
    """Single expert's response in panel."""

    expert_name: str
    expert_domain: str
    role: PanelRole
    response_text: str
    confidence: float  # 0-1 scale
    follow_up_questions: List[str] = field(default_factory=list)
    key_insights: List[str] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "expert_name": self.expert_name,
            "expert_domain": self.expert_domain,
            "role": self.role.value,
            "response_text": self.response_text,
            "confidence": self.confidence,
            "follow_up_questions": self.follow_up_questions,
            "key_insights": self.key_insights,
            "generated_at": self.generated_at,
        }


@dataclass
class PanelQuestion:
    """Question posed to the panel."""

    question_id: str
    question_text: str
    context: str = ""  # Background context
    category: str = ""  # Topic category
    urgency: int = 3  # 1-5 scale
    depth_level: int = 3  # 1-5, how deep should responses be
    posed_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "question_id": self.question_id,
            "question_text": self.question_text,
            "context": self.context,
            "category": self.category,
            "urgency": self.urgency,
            "depth_level": self.depth_level,
            "posed_at": self.posed_at,
        }


@dataclass
class PanelSession:
    """Single panel session with multiple experts."""

    session_id: str
    question: PanelQuestion
    expert_panel: List[str]  # Names of experts in order
    responses: Dict[str, ExpertResponse] = field(default_factory=dict)
    synthesized_response: Optional[str] = None
    consensus_points: List[str] = field(default_factory=list)
    disagreement_points: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "question": self.question.to_dict(),
            "expert_panel": self.expert_panel,
            "responses": {k: v.to_dict() for k, v in self.responses.items()},
            "synthesized_response": self.synthesized_response,
            "consensus_points": self.consensus_points,
            "disagreement_points": self.disagreement_points,
            "created_at": self.created_at,
        }


class PanelRouter:
    """Route questions to multiple experts sequentially."""

    def __init__(self, expert_roster: Optional[ExpertRoster] = None):
        """
        Initialize panel router.

        Args:
            expert_roster: ExpertRoster instance (creates if not provided)
        """
        self.roster = expert_roster or ExpertRoster()
        self.sessions: Dict[str, PanelSession] = {}
        self.session_history: List[PanelSession] = []

    def panel_router(
        self,
        session_id: str,
        question_text: str,
        expert_names: List[str],
        context: str = "",
        category: str = "",
        urgency: int = 3,
        depth_level: int = 3,
        timeout_seconds: Optional[float] = None,
    ) -> Tuple[Optional[PanelSession], Optional[str]]:
        """
        Route question to multiple experts sequentially.

        Args:
            session_id: Unique session ID
            question_text: The question to ask
            expert_names: List of expert names in order
            context: Background context
            category: Topic category
            urgency: Urgency level (1-5)
            depth_level: Response depth (1-5)

        Returns:
            (PanelSession if successful, error message if failed)
        """
        # Validate experts exist
        for name in expert_names:
            expert = self.roster.get_by_name(name)
            if not expert:
                return None, f"Expert '{name}' not found in roster"

        # Create question
        question_id = f"q_{len(self.sessions):04d}"
        question = PanelQuestion(
            question_id=question_id,
            question_text=question_text,
            context=context,
            category=category,
            urgency=urgency,
            depth_level=depth_level,
        )

        # Create panel session
        session = PanelSession(
            session_id=session_id,
            question=question,
            expert_panel=expert_names,
        )

        # Get responses from each expert
        start_time = time.monotonic()
        for idx, name in enumerate(expert_names):
            if timeout_seconds is not None and (time.monotonic() - start_time) >= timeout_seconds:
                return session, f"Panel timeout: only {idx}/{len(expert_names)} experts responded within {timeout_seconds}s"
            expert = self.roster.get_by_name(name)
            if expert:
                # Determine role
                if idx == 0:
                    role = PanelRole.PRIMARY
                elif idx == len(expert_names) - 1:
                    role = PanelRole.SYNTHESIZER
                else:
                    role = PanelRole.CHALLENGER if idx % 2 == 1 else PanelRole.SPECIALIST

                # Generate response (simulation of expert perspective)
                response = self._generate_expert_response(
                    expert, question, role, session.responses
                )
                if response:
                    session.responses[name] = response

        # Extract consensus and disagreements
        if len(session.responses) > 1:
            self._analyze_panel_dynamics(session)

        # Store session
        self.sessions[session_id] = session
        self.session_history.append(session)

        return session, None

    def _generate_expert_response(
        self,
        expert: Expert,
        question: PanelQuestion,
        role: PanelRole,
        prior_responses: Dict[str, ExpertResponse],
    ) -> Optional[ExpertResponse]:
        """Generate response for single expert."""
        # Construct response based on expert domain and role
        if role == PanelRole.PRIMARY:
            prompt = f"As {expert.name} ({expert.domain.value}), answer this question from your perspective:\n{question.question_text}"
        elif role == PanelRole.CHALLENGER:
            # Challenge previous responses
            prior_points = [
                v.key_insights[0] if v.key_insights else ""
                for v in prior_responses.values()
            ]
            prompt = f"As {expert.name} ({expert.domain.value}), challenge these points with your perspective:\n{', '.join(prior_points)}"
        elif role == PanelRole.SYNTHESIZER:
            # Synthesize all prior responses
            prior_texts = [v.response_text for v in prior_responses.values()]
            prompt = f"As {expert.name}, synthesize these perspectives:\n{' '.join(prior_texts)}"
        else:
            prompt = f"As {expert.name} ({expert.domain.value}), provide specialized insight on:\n{question.question_text}"

        # Simulate expert response with key insights
        key_insights = self._extract_insights(expert, question)

        response = ExpertResponse(
            expert_name=expert.name,
            expert_domain=expert.domain.value,
            role=role,
            response_text=f"Response from {expert.name} on {question.category or 'this topic'}",
            confidence=0.75 + (question.depth_level * 0.05),
            follow_up_questions=self._generate_follow_ups(expert, question),
            key_insights=key_insights,
        )

        return response

    def _extract_insights(self, expert: Expert, question: PanelQuestion) -> List[str]:
        """Extract key insights from expert profile."""
        insights = []

        # Use expert's domain expertise as insights
        if hasattr(expert, "domain_expertise"):
            insights = expert.domain_expertise[:2]

        return insights or [f"Perspective from {expert.domain.value}"]

    def _generate_follow_ups(self, expert: Expert, question: PanelQuestion) -> List[str]:
        """Generate follow-up questions from expert."""
        follow_ups = []

        # Use expert's favorite phrases as prompts
        if hasattr(expert, "favorite_phrases"):
            follow_ups = expert.favorite_phrases[:2]

        return follow_ups

    def _analyze_panel_dynamics(self, session: PanelSession) -> None:
        """Analyze consensus and disagreements in panel."""
        responses = list(session.responses.values())

        if len(responses) < 2:
            return

        # Extract key insights
        all_insights = []
        for resp in responses:
            all_insights.extend(resp.key_insights)

        # Simple consensus: insights that appear multiple times
        insight_counts = {}
        for insight in all_insights:
            insight_counts[insight] = insight_counts.get(insight, 0) + 1

        session.consensus_points = [
            insight for insight, count in insight_counts.items() if count > 1
        ]

        # Disagreements: conflicting domains or roles
        domains = [r.expert_domain for r in responses]
        if len(set(domains)) > 1:
            session.disagreement_points = [
                f"Different perspectives from {d}" for d in set(domains)
            ]

    def get_session(self, session_id: str) -> Optional[PanelSession]:
        """Get specific panel session."""
        return self.sessions.get(session_id)

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of panel session."""
        session = self.sessions.get(session_id)
        if not session:
            return None

        return {
            "session_id": session_id,
            "question": session.question.question_text,
            "expert_count": len(session.expert_panel),
            "expert_names": session.expert_panel,
            "response_count": len(session.responses),
            "consensus_points": session.consensus_points,
            "disagreement_points": session.disagreement_points,
            "created_at": session.created_at,
        }

    def get_expert_response(
        self, session_id: str, expert_name: str
    ) -> Optional[ExpertResponse]:
        """Get specific expert's response in a session."""
        session = self.sessions.get(session_id)
        if not session:
            return None
        return session.responses.get(expert_name)

    def export_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export complete session data."""
        session = self.sessions.get(session_id)
        if not session:
            return None
        return session.to_dict()

    def export_all_sessions(self) -> List[Dict[str, Any]]:
        """Export all sessions."""
        return [s.to_dict() for s in self.session_history]

    def synthesize_perspectives(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Synthesize all expert perspectives into coherent view."""
        session = self.sessions.get(session_id)
        if not session:
            return None

        # Group insights by frequency
        all_insights = []
        for response in session.responses.values():
            all_insights.extend(response.key_insights)

        # Find common themes
        common_themes = []
        insight_counts = {}
        for insight in all_insights:
            insight_counts[insight] = insight_counts.get(insight, 0) + 1

        common_themes = [
            insight for insight, count in insight_counts.items() if count > 1
        ]

        # Calculate average confidence
        avg_confidence = (
            sum(r.confidence for r in session.responses.values())
            / len(session.responses)
            if session.responses
            else 0
        )

        return {
            "session_id": session_id,
            "question": session.question.question_text,
            "common_themes": common_themes,
            "expert_count": len(session.expert_panel),
            "average_confidence": avg_confidence,
            "consensus_points": session.consensus_points,
            "disagreement_points": session.disagreement_points,
        }

    def compare_experts(
        self, session_id: str, expert1_name: str, expert2_name: str
    ) -> Optional[Dict[str, Any]]:
        """Compare two experts' responses."""
        session = self.sessions.get(session_id)
        if not session:
            return None

        resp1 = session.responses.get(expert1_name)
        resp2 = session.responses.get(expert2_name)

        if not resp1 or not resp2:
            return None

        # Find common and unique insights
        insights1 = set(resp1.key_insights)
        insights2 = set(resp2.key_insights)

        return {
            "expert1": expert1_name,
            "expert2": expert2_name,
            "expert1_domain": resp1.expert_domain,
            "expert2_domain": resp2.expert_domain,
            "common_insights": list(insights1 & insights2),
            "unique_to_expert1": list(insights1 - insights2),
            "unique_to_expert2": list(insights2 - insights1),
            "confidence_gap": abs(resp1.confidence - resp2.confidence),
        }

    def get_panel_statistics(self) -> Dict[str, Any]:
        """Get statistics about all panel sessions."""
        if not self.session_history:
            return {
                "total_sessions": 0,
                "total_questions": 0,
                "total_expert_responses": 0,
                "avg_panel_size": 0,
                "avg_confidence": 0.0,
            }

        total_responses = sum(len(s.responses) for s in self.session_history)
        total_panel_size = sum(len(s.expert_panel) for s in self.session_history)
        avg_confidence = (
            sum(
                r.confidence
                for s in self.session_history
                for r in s.responses.values()
            )
            / total_responses
            if total_responses > 0
            else 0
        )

        return {
            "total_sessions": len(self.session_history),
            "total_questions": len(set(s.question.question_id for s in self.session_history)),
            "total_expert_responses": total_responses,
            "avg_panel_size": (
                total_panel_size / len(self.session_history)
                if self.session_history
                else 0
            ),
            "avg_confidence": avg_confidence,
            "unique_experts_used": len(
                set(
                    name
                    for s in self.session_history
                    for name in s.expert_panel
                )
            ),
        }
