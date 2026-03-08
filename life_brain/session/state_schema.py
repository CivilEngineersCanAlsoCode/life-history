"""
Session state schema for tracking and persisting session context.

Captures session context, conversation history, learned knowledge,
and conflict resolutions for continuity across sessions.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class StateComponent(Enum):
    """Session state components."""

    CONTEXT = "context"  # Session metadata
    HISTORY = "history"  # Conversation turns
    KNOWLEDGE = "knowledge"  # Learned insights
    CONFLICTS = "conflicts"  # Unresolved issues


@dataclass
class SessionStateContext:
    """Session context information."""

    session_id: str
    user_id: str
    language: str  # english, hinglish, hindi
    communication_style: str  # formal, conversational, etc
    detail_level: int  # 1-10
    expert_domain: Optional[str] = None  # Current expert
    turn_count: int = 0
    session_start: str = field(default_factory=lambda: datetime.now().isoformat())
    last_activity: str = field(default_factory=lambda: datetime.now().isoformat())
    session_notes: str = ""  # User/system notes about session
    mood_pattern: Optional[str] = None  # Last detected mood
    trend_direction: Optional[str] = None  # Emotional trend

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "language": self.language,
            "communication_style": self.communication_style,
            "detail_level": self.detail_level,
            "expert_domain": self.expert_domain,
            "turn_count": self.turn_count,
            "session_start": self.session_start,
            "last_activity": self.last_activity,
            "session_notes": self.session_notes,
            "mood_pattern": self.mood_pattern,
            "trend_direction": self.trend_direction,
        }


@dataclass
class ConversationTurn:
    """Single conversation turn."""

    turn_number: int
    user_message: str
    assistant_response: str
    sentiment: str  # very_positive, positive, neutral, negative, very_negative
    polarity: float  # -1 to +1
    emotions: Dict[str, float]  # emotion -> score
    expert_used: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "turn_number": self.turn_number,
            "user_message": self.user_message[:200],  # Truncate for storage
            "assistant_response": self.assistant_response[:200],
            "sentiment": self.sentiment,
            "polarity": self.polarity,
            "emotions": self.emotions,
            "expert_used": self.expert_used,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class LearnedInsight:
    """Knowledge learned during session."""

    insight_id: str
    content: str
    category: str  # career, personal, technical, domain, etc
    confidence: float  # 0-1, how confident we are about this
    learned_at_turn: int
    source: str  # "user_stated", "inferred", "context"
    related_topics: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "insight_id": self.insight_id,
            "content": self.content,
            "category": self.category,
            "confidence": self.confidence,
            "learned_at_turn": self.learned_at_turn,
            "source": self.source,
            "related_topics": self.related_topics,
            "timestamp": self.timestamp,
        }


@dataclass
class UnresolvedConflict:
    """Unresolved conflict during session."""

    conflict_id: str
    field_name: str
    existing_value: str
    new_value: str
    reason: str
    severity: str  # low, medium, high
    identified_at_turn: int
    resolution_strategy: Optional[str] = None  # keep_existing, use_new, merge, skip, manual
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "conflict_id": self.conflict_id,
            "field_name": self.field_name,
            "existing_value": self.existing_value,
            "new_value": self.new_value,
            "reason": self.reason,
            "severity": self.severity,
            "identified_at_turn": self.identified_at_turn,
            "resolution_strategy": self.resolution_strategy,
            "timestamp": self.timestamp,
        }


@dataclass
class SessionState:
    """Complete session state snapshot."""

    session_id: str
    context: SessionStateContext
    history: List[ConversationTurn] = field(default_factory=list)
    knowledge: List[LearnedInsight] = field(default_factory=list)
    conflicts: List[UnresolvedConflict] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "context": self.context.to_dict(),
            "history": [turn.to_dict() for turn in self.history],
            "knowledge": [insight.to_dict() for insight in self.knowledge],
            "conflicts": [conflict.to_dict() for conflict in self.conflicts],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of session state."""
        return {
            "session_id": self.session_id,
            "user_id": self.context.user_id,
            "turn_count": self.context.turn_count,
            "knowledge_items": len(self.knowledge),
            "active_conflicts": len([c for c in self.conflicts if not c.resolution_strategy]),
            "resolved_conflicts": len([c for c in self.conflicts if c.resolution_strategy]),
            "avg_sentiment": self._calculate_avg_sentiment(),
            "mood_pattern": self.context.mood_pattern,
            "trend": self.context.trend_direction,
        }

    def _calculate_avg_sentiment(self) -> float:
        """Calculate average polarity from history."""
        if not self.history:
            return 0.0
        polarities = [turn.polarity for turn in self.history]
        return sum(polarities) / len(polarities) if polarities else 0.0


class SessionStateSchema:
    """Manage session state schema and operations."""

    def __init__(self):
        """Initialize state schema manager."""
        self.states: Dict[str, SessionState] = {}  # session_id -> SessionState
        self.state_history: List[SessionState] = []  # Snapshots over time

    def session_state_schema(
        self,
        session_id: str,
        user_id: str,
        language: str = "hinglish",
        communication_style: str = "conversational",
        detail_level: int = 5,
        expert_domain: Optional[str] = None,
        session_notes: str = "",
    ) -> SessionState:
        """
        Create or initialize session state.

        Args:
            session_id: Session identifier
            user_id: User identifier
            language: Language preference
            communication_style: Communication style
            detail_level: Response detail (1-10)
            expert_domain: Primary expert for session
            session_notes: Initial session notes

        Returns:
            SessionState object
        """
        context = SessionStateContext(
            session_id=session_id,
            user_id=user_id,
            language=language,
            communication_style=communication_style,
            detail_level=detail_level,
            expert_domain=expert_domain,
            session_notes=session_notes,
        )

        state = SessionState(
            session_id=session_id,
            context=context,
        )

        self.states[session_id] = state
        self.state_history.append(state)

        return state

    def add_turn(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        sentiment: str,
        polarity: float,
        emotions: Dict[str, float],
        expert_used: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[ConversationTurn]:
        """Add conversation turn to session state."""
        if session_id not in self.states:
            return None

        state = self.states[session_id]
        turn_number = len(state.history) + 1

        turn = ConversationTurn(
            turn_number=turn_number,
            user_message=user_message,
            assistant_response=assistant_response,
            sentiment=sentiment,
            polarity=polarity,
            emotions=emotions,
            expert_used=expert_used,
            metadata=metadata or {},
        )

        state.history.append(turn)
        state.context.turn_count = turn_number
        state.context.last_activity = datetime.now().isoformat()
        state.updated_at = datetime.now().isoformat()

        return turn

    def add_insight(
        self,
        session_id: str,
        insight_id: str,
        content: str,
        category: str,
        confidence: float,
        source: str,
        related_topics: Optional[List[str]] = None,
    ) -> Optional[LearnedInsight]:
        """Add learned insight to session state."""
        if session_id not in self.states:
            return None

        state = self.states[session_id]
        turn_number = state.context.turn_count

        insight = LearnedInsight(
            insight_id=insight_id,
            content=content,
            category=category,
            confidence=confidence,
            learned_at_turn=turn_number,
            source=source,
            related_topics=related_topics or [],
        )

        state.knowledge.append(insight)
        state.updated_at = datetime.now().isoformat()

        return insight

    def add_conflict(
        self,
        session_id: str,
        conflict_id: str,
        field_name: str,
        existing_value: str,
        new_value: str,
        reason: str,
        severity: str = "medium",
    ) -> Optional[UnresolvedConflict]:
        """Add unresolved conflict to session state."""
        if session_id not in self.states:
            return None

        state = self.states[session_id]
        turn_number = state.context.turn_count

        conflict = UnresolvedConflict(
            conflict_id=conflict_id,
            field_name=field_name,
            existing_value=existing_value,
            new_value=new_value,
            reason=reason,
            severity=severity,
            identified_at_turn=turn_number,
        )

        state.conflicts.append(conflict)
        state.updated_at = datetime.now().isoformat()

        return conflict

    def resolve_conflict(
        self,
        session_id: str,
        conflict_id: str,
        resolution_strategy: str,
    ) -> Tuple[bool, Optional[str]]:
        """Mark conflict as resolved."""
        if session_id not in self.states:
            return False, f"Session {session_id} not found"

        state = self.states[session_id]

        for conflict in state.conflicts:
            if conflict.conflict_id == conflict_id:
                conflict.resolution_strategy = resolution_strategy
                state.updated_at = datetime.now().isoformat()
                return True, None

        return False, f"Conflict {conflict_id} not found"

    def update_context(
        self,
        session_id: str,
        **updates,
    ) -> Tuple[bool, Optional[str]]:
        """Update session context."""
        if session_id not in self.states:
            return False, f"Session {session_id} not found"

        state = self.states[session_id]

        # Update allowed fields
        allowed_fields = {
            "expert_domain",
            "session_notes",
            "mood_pattern",
            "trend_direction",
            "communication_style",
            "detail_level",
        }

        for key, value in updates.items():
            if key in allowed_fields:
                setattr(state.context, key, value)

        state.context.last_activity = datetime.now().isoformat()
        state.updated_at = datetime.now().isoformat()

        return True, None

    def get_state(self, session_id: str) -> Optional[SessionState]:
        """Get session state."""
        return self.states.get(session_id)

    def get_recent_turns(self, session_id: str, limit: int = 5) -> List[ConversationTurn]:
        """Get recent turns from session."""
        state = self.get_state(session_id)
        if not state:
            return []
        return state.history[-limit:]

    def get_active_conflicts(self, session_id: str) -> List[UnresolvedConflict]:
        """Get unresolved conflicts."""
        state = self.get_state(session_id)
        if not state:
            return []
        return [c for c in state.conflicts if not c.resolution_strategy]

    def get_knowledge(
        self, session_id: str, category: Optional[str] = None
    ) -> List[LearnedInsight]:
        """Get learned insights, optionally filtered by category."""
        state = self.get_state(session_id)
        if not state:
            return []

        if category:
            return [k for k in state.knowledge if k.category == category]
        return state.knowledge

    def export_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export complete session state."""
        state = self.get_state(session_id)
        return state.to_dict() if state else None

    def export_state_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export session state summary."""
        state = self.get_state(session_id)
        return state.get_summary() if state else None

    def get_all_states(self) -> List[SessionState]:
        """Get all session states."""
        return list(self.states.values())

    def get_state_statistics(self) -> Dict[str, Any]:
        """Get statistics across all states."""
        if not self.states:
            return {
                "total_sessions": 0,
                "total_turns": 0,
                "total_insights": 0,
                "total_conflicts": 0,
            }

        total_turns = sum(len(state.history) for state in self.states.values())
        total_insights = sum(len(state.knowledge) for state in self.states.values())
        total_conflicts = sum(len(state.conflicts) for state in self.states.values())

        return {
            "total_sessions": len(self.states),
            "total_turns": total_turns,
            "total_insights": total_insights,
            "total_conflicts": total_conflicts,
            "avg_turns_per_session": total_turns / len(self.states) if self.states else 0,
            "avg_insights_per_session": (
                total_insights / len(self.states) if self.states else 0
            ),
        }

    def export_all_states(self) -> List[Dict[str, Any]]:
        """Export all session states."""
        return [state.to_dict() for state in self.states.values()]
