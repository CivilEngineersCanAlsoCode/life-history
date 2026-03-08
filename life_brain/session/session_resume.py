"""
Session resume for continuity and context priming.

Retrieves prior session state and prepares expert context for session continuation
to maintain coherence and conversation flow.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from life_brain.session.state_schema import SessionStateSchema, SessionState


class ResumptionContext(Enum):
    """Context types for session resumption."""

    NEW_SESSION = "new_session"  # First session
    SAME_DAY = "same_day"  # Resumed within same day
    NEXT_DAY = "next_day"  # Resumed next day
    WEEK_LATER = "week_later"  # Resumed after a week
    LONG_BREAK = "long_break"  # Resumed after extended break


@dataclass
class PriorSessionSummary:
    """Summary of prior session for priming."""

    session_id: str
    user_id: str
    duration_minutes: int  # Approximate duration
    turn_count: int
    key_topics: List[str]  # Main topics discussed
    outcomes: List[str]  # Key outcomes or decisions
    open_questions: List[str]  # Unanswered questions
    commitments: List[str]  # Promises/actions from user
    mood_trajectory: str  # Overall mood path (improving/stable/declining)
    avg_sentiment: float  # Average polarity
    expert_used: str  # Primary expert in prior session
    gaps_since_last: str  # Time gap description

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "duration_minutes": self.duration_minutes,
            "turn_count": self.turn_count,
            "key_topics": self.key_topics,
            "outcomes": self.outcomes,
            "open_questions": self.open_questions,
            "commitments": self.commitments,
            "mood_trajectory": self.mood_trajectory,
            "avg_sentiment": self.avg_sentiment,
            "expert_used": self.expert_used,
            "gaps_since_last": self.gaps_since_last,
        }


@dataclass
class ExpertPrimingContext:
    """Context for priming expert in new session."""

    expert_domain: str
    user_background: Dict[str, Any]  # User profile/history
    prior_context: Optional[PriorSessionSummary] = None
    continuity_prompts: List[str] = field(default_factory=list)  # Questions to continuity
    context_awareness: Dict[str, Any] = field(default_factory=dict)  # Situational awareness
    suggested_entry_point: str = ""  # How to start conversation
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "expert_domain": self.expert_domain,
            "user_background": self.user_background,
            "prior_context": self.prior_context.to_dict() if self.prior_context else None,
            "continuity_prompts": self.continuity_prompts,
            "context_awareness": self.context_awareness,
            "suggested_entry_point": self.suggested_entry_point,
            "created_at": self.created_at,
        }


class SessionResumer:
    """Resume sessions and prime expert context."""

    def __init__(self, state_schema: SessionStateSchema):
        """
        Initialize session resumer.

        Args:
            state_schema: SessionStateSchema instance for state retrieval
        """
        self.state_schema = state_schema
        self.priming_contexts: Dict[str, ExpertPrimingContext] = {}

    def session_resume(
        self,
        session_id: str,
        prior_session_id: Optional[str] = None,
        expert_domain: str = "career",
    ) -> Tuple[Optional[ExpertPrimingContext], Optional[str]]:
        """
        Prepare expert context for session continuation.

        Args:
            session_id: Current session ID (new session)
            prior_session_id: Previous session to resume from (if any)
            expert_domain: Expert domain for current session

        Returns:
            (ExpertPrimingContext, error_message) tuple
        """
        # Retrieve prior session if specified
        prior_state = None
        prior_summary = None

        if prior_session_id:
            prior_state = self.state_schema.get_state(prior_session_id)
            if not prior_state:
                return None, f"Prior session {prior_session_id} not found"

            prior_summary = self._create_prior_session_summary(prior_state)

        # Get user background from prior or current session
        user_background = self._extract_user_background(prior_state, session_id)

        # Generate continuity prompts
        continuity_prompts = self._generate_continuity_prompts(prior_state)

        # Create context awareness
        context_awareness = self._build_context_awareness(prior_state, session_id)

        # Generate entry point
        entry_point = self._suggest_entry_point(prior_summary, expert_domain)

        # Create priming context
        priming_context = ExpertPrimingContext(
            expert_domain=expert_domain,
            user_background=user_background,
            prior_context=prior_summary,
            continuity_prompts=continuity_prompts,
            context_awareness=context_awareness,
            suggested_entry_point=entry_point,
        )

        # Store for reference
        self.priming_contexts[session_id] = priming_context

        return priming_context, None

    def _create_prior_session_summary(self, prior_state: SessionState) -> PriorSessionSummary:
        """Create summary of prior session."""
        # Calculate duration (estimate from first and last turn)
        duration_minutes = 0
        if len(prior_state.history) > 0:
            first_turn = prior_state.history[0]
            last_turn = prior_state.history[-1]
            first_time = datetime.fromisoformat(first_turn.timestamp)
            last_time = datetime.fromisoformat(last_turn.timestamp)
            duration_minutes = int((last_time - first_time).total_seconds() / 60)

        # Extract key topics from insights
        key_topics = [
            insight.category
            for insight in prior_state.knowledge[: 3]
        ]

        # Extract outcomes from knowledge
        outcomes = [
            insight.content
            for insight in prior_state.knowledge
            if insight.source == "user_stated"
        ][:3]

        # Extract open questions from active conflicts
        open_questions = [
            f"{conflict.field_name}: {conflict.reason}"
            for conflict in prior_state.conflicts
            if not conflict.resolution_strategy
        ]

        # Extract commitments (would be tracked in a commitment system)
        commitments = []

        # Determine mood trajectory
        mood_trajectory = self._analyze_mood_trajectory(prior_state)

        # Calculate average sentiment
        avg_sentiment = prior_state.get_summary()["avg_sentiment"]

        # Get primary expert
        expert_used = prior_state.context.expert_domain or "career"

        # Calculate gap since last
        gaps_since_last = self._calculate_gap_since_last(prior_state)

        return PriorSessionSummary(
            session_id=prior_state.session_id,
            user_id=prior_state.context.user_id,
            duration_minutes=duration_minutes,
            turn_count=len(prior_state.history),
            key_topics=key_topics,
            outcomes=outcomes,
            open_questions=open_questions,
            commitments=commitments,
            mood_trajectory=mood_trajectory,
            avg_sentiment=avg_sentiment,
            expert_used=expert_used,
            gaps_since_last=gaps_since_last,
        )

    def _extract_user_background(
        self, prior_state: Optional[SessionState], session_id: str
    ) -> Dict[str, Any]:
        """Extract user background information."""
        background = {
            "session_id": session_id,
            "preferences": {},
            "known_facts": [],
            "expertise_areas": [],
            "interests": [],
        }

        if prior_state:
            background["session_id"] = prior_state.context.user_id
            background["preferences"] = {
                "language": prior_state.context.language,
                "communication_style": prior_state.context.communication_style,
                "detail_level": prior_state.context.detail_level,
            }

            # Extract expertise areas and interests from knowledge
            for insight in prior_state.knowledge:
                if insight.category == "expertise":
                    background["expertise_areas"].append(insight.content)
                elif insight.category == "interest":
                    background["interests"].append(insight.content)
                else:
                    background["known_facts"].append(
                        {
                            "fact": insight.content,
                            "category": insight.category,
                            "confidence": insight.confidence,
                        }
                    )

        return background

    def _generate_continuity_prompts(self, prior_state: Optional[SessionState]) -> List[str]:
        """Generate prompts to maintain continuity."""
        prompts = []

        if not prior_state:
            prompts.append("What brings you here today?")
            return prompts

        # Check for open questions from prior session
        active_conflicts = [
            c for c in prior_state.conflicts if not c.resolution_strategy
        ]

        if active_conflicts:
            for conflict in active_conflicts[:2]:
                prompts.append(f"Following up on {conflict.field_name}: {conflict.reason}")

        # Check for incomplete insights
        recent_insights = prior_state.knowledge[-3:] if prior_state.knowledge else []
        if recent_insights:
            prompts.append(
                f"Let's continue discussing {recent_insights[-1].category}..."
            )

        # Add general continuity
        if prior_state.history:
            last_topic = prior_state.history[-1].metadata.get("topic", "previous discussion")
            prompts.append(f"Continuing from {last_topic}...")

        return prompts[:3]  # Top 3 prompts

    def _build_context_awareness(
        self, prior_state: Optional[SessionState], session_id: str
    ) -> Dict[str, Any]:
        """Build situational awareness for expert."""
        awareness = {
            "session_type": "new_session",
            "resumption_context": ResumptionContext.NEW_SESSION.value,
            "recent_events": [],
            "user_state": {},
            "priority_areas": [],
        }

        if prior_state:
            awareness["session_type"] = "continuation"

            # Determine time gap
            gap = self._calculate_gap_since_last(prior_state)
            if "hours" in gap:
                awareness["resumption_context"] = ResumptionContext.SAME_DAY.value
            elif "day" in gap:
                awareness["resumption_context"] = ResumptionContext.NEXT_DAY.value
            elif "week" in gap or "weeks" in gap:
                awareness["resumption_context"] = ResumptionContext.WEEK_LATER.value
            else:
                awareness["resumption_context"] = ResumptionContext.LONG_BREAK.value

            # Recent events from last few turns
            recent_turns = prior_state.history[-3:]
            awareness["recent_events"] = [
                f"Turn {t.turn_number}: {t.metadata.get('topic', 'discussion')}"
                for t in recent_turns
            ]

            # User state from mood
            awareness["user_state"] = {
                "mood_pattern": prior_state.context.mood_pattern,
                "recent_sentiment": prior_state.history[-1].sentiment
                if prior_state.history
                else "neutral",
                "engagement_level": "high" if len(prior_state.history) > 5 else "moderate",
            }

            # Priority areas from open conflicts
            awareness["priority_areas"] = [
                conflict.field_name
                for conflict in prior_state.conflicts
                if not conflict.resolution_strategy
            ][:3]

        return awareness

    def _suggest_entry_point(
        self, prior_summary: Optional[PriorSessionSummary], expert_domain: str
    ) -> str:
        """Suggest how to start the conversation."""
        if not prior_summary:
            return f"Let's start fresh. What would you like to discuss with me as your {expert_domain} expert?"

        # If high engagement before
        if prior_summary.turn_count > 5:
            if prior_summary.open_questions:
                return (
                    f"Great to continue! Let's tackle the {prior_summary.open_questions[0]} "
                    "question from last time."
                )
            else:
                return (
                    f"You were making great progress on {prior_summary.key_topics[0] if prior_summary.key_topics else 'your goals'}. "
                    "Let's keep the momentum!"
                )

        # If low engagement
        if prior_summary.turn_count <= 2:
            return (
                f"Let's pick up where we left off. What aspect of {prior_summary.key_topics[0] if prior_summary.key_topics else expert_domain} "
                "would you like to explore further?"
            )

        # Default
        return f"Welcome back! You previously focused on {prior_summary.key_topics[0] if prior_summary.key_topics else 'your development'}. Shall we continue?"

    def _analyze_mood_trajectory(self, prior_state: SessionState) -> str:
        """Analyze overall mood trajectory in prior session."""
        if len(prior_state.history) < 2:
            return "insufficient_data"

        polarities = [turn.polarity for turn in prior_state.history]

        # Calculate first half vs second half
        mid = len(polarities) // 2
        first_half_avg = sum(polarities[:mid]) / mid if mid > 0 else 0
        second_half_avg = sum(polarities[mid:]) / (len(polarities) - mid) if mid < len(polarities) else 0

        if second_half_avg > first_half_avg + 0.2:
            return "improving"
        elif second_half_avg < first_half_avg - 0.2:
            return "declining"
        else:
            return "stable"

    def _calculate_gap_since_last(self, prior_state: SessionState) -> str:
        """Calculate time gap since last session."""
        if not prior_state.history:
            return "unknown"

        last_activity = datetime.fromisoformat(prior_state.context.last_activity)
        now = datetime.now()
        gap = now - last_activity

        if gap.days == 0:
            hours = gap.seconds // 3600
            if hours == 0:
                return "minutes ago"
            return f"{hours} hours ago"
        elif gap.days == 1:
            return "1 day ago"
        elif gap.days < 7:
            return f"{gap.days} days ago"
        else:
            weeks = gap.days // 7
            return f"{weeks} week(s) ago"

    def get_priming_context(self, session_id: str) -> Optional[ExpertPrimingContext]:
        """Get priming context for session."""
        return self.priming_contexts.get(session_id)

    def export_priming_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export priming context as dictionary."""
        context = self.get_priming_context(session_id)
        return context.to_dict() if context else None

    def get_resumption_report(
        self, session_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get detailed resumption report."""
        context = self.get_priming_context(session_id)
        if not context:
            return None

        return {
            "session_id": session_id,
            "expert": context.expert_domain,
            "user_background": context.user_background,
            "prior_session": context.prior_context.to_dict() if context.prior_context else None,
            "continuity_points": context.continuity_prompts,
            "context_awareness": context.context_awareness,
            "entry_strategy": context.suggested_entry_point,
            "created_at": context.created_at,
        }
