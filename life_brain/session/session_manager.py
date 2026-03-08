"""
Session management with initialization and context loading.

Handles session creation, preference loading, context initialization,
and session state management.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SessionStatus(Enum):
    """Session status."""
    INITIALIZED = "initialized"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


@dataclass
class SessionContext:
    """User context for a session."""

    session_id: str
    user_id: str
    language: str = "hinglish"
    communication_style: str = "conversational"
    preferred_experts: List[str] = field(default_factory=lambda: ["career"])
    timezone: str = "UTC"
    detail_level: int = 5
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_activity: str = field(default_factory=lambda: datetime.now().isoformat())
    status: SessionStatus = SessionStatus.INITIALIZED
    turn_count: int = 0  # Number of exchanges in session
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "language": self.language,
            "communication_style": self.communication_style,
            "preferred_experts": self.preferred_experts,
            "timezone": self.timezone,
            "detail_level": self.detail_level,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "status": self.status.value,
            "turn_count": self.turn_count,
            "metadata": self.metadata,
        }


class SessionManager:
    """Manage user sessions."""

    def __init__(self):
        """Initialize session manager."""
        self.sessions: Dict[str, SessionContext] = {}  # session_id -> SessionContext
        self.user_sessions: Dict[str, List[str]] = {}  # user_id -> [session_ids]
        self.session_history: Dict[str, List[Dict[str, Any]]] = {}  # session_id -> history

    def session_init(
        self,
        session_id: str,
        user_id: str,
        language: str = "hinglish",
        communication_style: str = "conversational",
        preferred_experts: Optional[List[str]] = None,
        timezone: str = "UTC",
        detail_level: int = 5,
        **metadata,
    ) -> SessionContext:
        """
        Initialize a session with user context and preferences.

        Args:
            session_id: Unique session identifier
            user_id: User ID
            language: Language preference
            communication_style: Communication style
            preferred_experts: List of expert domains
            timezone: User's timezone
            detail_level: Response detail level (1-10)
            **metadata: Additional session metadata

        Returns:
            SessionContext object
        """
        # Create session context
        context = SessionContext(
            session_id=session_id,
            user_id=user_id,
            language=language,
            communication_style=communication_style,
            preferred_experts=preferred_experts or ["career"],
            timezone=timezone,
            detail_level=detail_level,
            metadata=metadata,
        )

        # Store session
        self.sessions[session_id] = context

        # Track user sessions
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []
        self.user_sessions[user_id].append(session_id)

        # Initialize history
        self.session_history[session_id] = [{
            "timestamp": datetime.now().isoformat(),
            "event": "session_initialized",
            "context": context.to_dict(),
        }]

        return context

    def get_session(self, session_id: str) -> Optional[SessionContext]:
        """Get session context."""
        return self.sessions.get(session_id)

    def get_user_sessions(
        self,
        user_id: str,
        status: Optional[SessionStatus] = None,
    ) -> List[SessionContext]:
        """Get all sessions for user, optionally filtered by status."""
        session_ids = self.user_sessions.get(user_id, [])
        sessions = [self.sessions[sid] for sid in session_ids if sid in self.sessions]

        if status:
            sessions = [s for s in sessions if s.status == status]

        return sorted(sessions, key=lambda s: s.last_activity, reverse=True)

    def get_active_session(self, user_id: str) -> Optional[SessionContext]:
        """Get active session for user."""
        active = self.get_user_sessions(user_id, status=SessionStatus.ACTIVE)
        return active[0] if active else None

    def activate_session(self, session_id: str) -> Tuple[bool, Optional[str]]:
        """Activate a session."""
        if session_id not in self.sessions:
            return False, f"Session {session_id} not found"

        session = self.sessions[session_id]
        session.status = SessionStatus.ACTIVE
        session.last_activity = datetime.now().isoformat()

        self.session_history[session_id].append({
            "timestamp": datetime.now().isoformat(),
            "event": "session_activated",
        })

        return True, None

    def pause_session(self, session_id: str) -> Tuple[bool, Optional[str]]:
        """Pause a session."""
        if session_id not in self.sessions:
            return False, f"Session {session_id} not found"

        session = self.sessions[session_id]
        session.status = SessionStatus.PAUSED
        session.last_activity = datetime.now().isoformat()

        self.session_history[session_id].append({
            "timestamp": datetime.now().isoformat(),
            "event": "session_paused",
        })

        return True, None

    def close_session(self, session_id: str) -> Tuple[bool, Optional[str]]:
        """Close a session."""
        if session_id not in self.sessions:
            return False, f"Session {session_id} not found"

        session = self.sessions[session_id]
        session.status = SessionStatus.CLOSED
        session.last_activity = datetime.now().isoformat()

        self.session_history[session_id].append({
            "timestamp": datetime.now().isoformat(),
            "event": "session_closed",
        })

        return True, None

    def record_turn(self, session_id: str) -> Tuple[bool, Optional[str]]:
        """Record a turn (user-assistant exchange)."""
        if session_id not in self.sessions:
            return False, f"Session {session_id} not found"

        session = self.sessions[session_id]
        session.turn_count += 1
        session.last_activity = datetime.now().isoformat()

        return True, None

    def update_session_context(
        self,
        session_id: str,
        **updates,
    ) -> Tuple[bool, Optional[str]]:
        """Update session context."""
        if session_id not in self.sessions:
            return False, f"Session {session_id} not found"

        session = self.sessions[session_id]

        # Update fields
        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)
            else:
                session.metadata[key] = value

        session.last_activity = datetime.now().isoformat()

        # Record update
        self.session_history[session_id].append({
            "timestamp": datetime.now().isoformat(),
            "event": "context_updated",
            "updates": updates,
        })

        return True, None

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get session history."""
        return self.session_history.get(session_id, [])

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session summary."""
        session = self.get_session(session_id)
        if not session:
            return None

        history = self.get_session_history(session_id)

        return {
            "session_id": session_id,
            "user_id": session.user_id,
            "created_at": session.created_at,
            "last_activity": session.last_activity,
            "status": session.status.value,
            "turn_count": session.turn_count,
            "duration_minutes": self._calculate_duration(session),
            "events": len(history),
            "language": session.language,
            "communication_style": session.communication_style,
        }

    def _calculate_duration(self, session: SessionContext) -> int:
        """Calculate session duration in minutes."""
        created = datetime.fromisoformat(session.created_at)
        last = datetime.fromisoformat(session.last_activity)
        delta = last - created
        return int(delta.total_seconds() / 60)

    def get_statistics(self) -> Dict[str, Any]:
        """Get session statistics."""
        if not self.sessions:
            return {
                "total_sessions": 0,
                "active_sessions": 0,
                "closed_sessions": 0,
                "total_users": 0,
                "avg_turns_per_session": 0,
            }

        sessions = list(self.sessions.values())
        active = [s for s in sessions if s.status == SessionStatus.ACTIVE]
        closed = [s for s in sessions if s.status == SessionStatus.CLOSED]

        total_turns = sum(s.turn_count for s in sessions)
        avg_turns = total_turns / len(sessions) if sessions else 0

        return {
            "total_sessions": len(sessions),
            "active_sessions": len(active),
            "closed_sessions": len(closed),
            "total_users": len(self.user_sessions),
            "avg_turns_per_session": avg_turns,
            "total_turns": total_turns,
        }

    def export_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export complete session data."""
        session = self.get_session(session_id)
        if not session:
            return None

        return {
            "context": session.to_dict(),
            "history": self.get_session_history(session_id),
            "summary": self.get_session_summary(session_id),
        }

    def export_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Export all sessions for a user."""
        sessions = self.get_user_sessions(user_id)
        return [
            {
                "context": s.to_dict(),
                "summary": self.get_session_summary(s.session_id),
            }
            for s in sessions
        ]
