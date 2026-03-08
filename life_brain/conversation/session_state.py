"""
Session state persistence across conversation turns.

Persists: conversation history, extracted knowledge, pending conflicts,
active expert context. Enables seamless resume across sessions.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class TurnMessage:
    """A single conversation turn."""

    role: str       # "user" or "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {"role": self.role, "content": self.content, "timestamp": self.timestamp}


@dataclass
class SessionState:
    """Complete state for one conversation session."""

    session_id: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    # Conversation history
    history: List[TurnMessage] = field(default_factory=list)

    # Context priming data
    active_expert: Optional[str] = None       # Current expert name
    active_mode: Optional[str] = None         # "small_talk", "guided", "adversarial"
    current_topic: Optional[str] = None       # What we're discussing

    # Extracted knowledge from session
    extracted_facts: List[Dict[str, Any]] = field(default_factory=list)
    pending_conflicts: List[Dict[str, Any]] = field(default_factory=list)
    commitments: List[Dict[str, Any]] = field(default_factory=list)

    # Resume context
    session_summary: Optional[str] = None     # Brief summary for next-session priming
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_turn(self, role: str, content: str) -> TurnMessage:
        """Add a conversation turn."""
        turn = TurnMessage(role=role, content=content)
        self.history.append(turn)
        self.last_updated = datetime.now().isoformat()
        return turn

    def get_history_text(self) -> str:
        """Get conversation history as a single text block."""
        lines = []
        for turn in self.history:
            prefix = "User" if turn.role == "user" else "Assistant"
            lines.append(f"{prefix}: {turn.content}")
        return "\n".join(lines)

    def get_user_messages(self) -> List[str]:
        """Get only user messages from history."""
        return [t.content for t in self.history if t.role == "user"]

    def add_extracted_fact(self, fact: Dict[str, Any]) -> None:
        """Add an extracted fact to session."""
        self.extracted_facts.append(fact)
        self.last_updated = datetime.now().isoformat()

    def add_pending_conflict(self, conflict: Dict[str, Any]) -> None:
        """Add a pending conflict that needs resolution."""
        self.pending_conflicts.append(conflict)
        self.last_updated = datetime.now().isoformat()

    def add_commitment(self, commitment: Dict[str, Any]) -> None:
        """Add a user commitment to session."""
        self.commitments.append(commitment)
        self.last_updated = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize session state to dict."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "history": [t.to_dict() for t in self.history],
            "active_expert": self.active_expert,
            "active_mode": self.active_mode,
            "current_topic": self.current_topic,
            "extracted_facts": self.extracted_facts,
            "pending_conflicts": self.pending_conflicts,
            "commitments": self.commitments,
            "session_summary": self.session_summary,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionState":
        """Deserialize session state from dict."""
        history = [
            TurnMessage(
                role=t["role"],
                content=t["content"],
                timestamp=t.get("timestamp", ""),
            )
            for t in data.get("history", [])
        ]
        return cls(
            session_id=data["session_id"],
            created_at=data.get("created_at", ""),
            last_updated=data.get("last_updated", ""),
            history=history,
            active_expert=data.get("active_expert"),
            active_mode=data.get("active_mode"),
            current_topic=data.get("current_topic"),
            extracted_facts=data.get("extracted_facts", []),
            pending_conflicts=data.get("pending_conflicts", []),
            commitments=data.get("commitments", []),
            session_summary=data.get("session_summary"),
            metadata=data.get("metadata", {}),
        )

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "SessionState":
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


class SessionManager:
    """Manage multiple sessions with in-memory persistence."""

    def __init__(self):
        self._sessions: Dict[str, SessionState] = {}

    def create_session(self, session_id: str, metadata: Optional[Dict] = None) -> SessionState:
        """Create a new session.

        Args:
            session_id: Unique session identifier
            metadata: Optional metadata for the session

        Returns:
            New SessionState
        """
        if not session_id or not session_id.strip():
            raise ValueError("session_id cannot be empty")

        state = SessionState(session_id=session_id, metadata=metadata or {})
        self._sessions[session_id] = state
        return state

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Retrieve a session by ID."""
        return self._sessions.get(session_id)

    def save_session(self, state: SessionState) -> None:
        """Save/update a session state."""
        self._sessions[state.session_id] = state
        state.last_updated = datetime.now().isoformat()

    def get_or_create(self, session_id: str) -> SessionState:
        """Get existing session or create new one."""
        if session_id in self._sessions:
            return self._sessions[session_id]
        return self.create_session(session_id)

    def build_priming_context(self, session_id: str) -> Optional[str]:
        """Build context string to prime expert with prior session.

        Args:
            session_id: Session to retrieve context from

        Returns:
            Priming context string, or None if no session found
        """
        state = self.get_session(session_id)
        if not state:
            return None

        lines = ["== PRIOR SESSION CONTEXT =="]

        if state.session_summary:
            lines.append(f"Summary: {state.session_summary}")

        if state.active_expert:
            lines.append(f"Last expert: {state.active_expert}")

        if state.current_topic:
            lines.append(f"Last topic: {state.current_topic}")

        if state.extracted_facts:
            lines.append(f"Extracted {len(state.extracted_facts)} fact(s) this session.")

        if state.pending_conflicts:
            lines.append(f"Pending conflicts: {len(state.pending_conflicts)} unresolved.")

        if state.commitments:
            lines.append(f"Commitments made: {len(state.commitments)}.")

        # Last 3 user messages for context
        recent = state.get_user_messages()[-3:]
        if recent:
            lines.append("Recent messages:")
            for msg in recent:
                lines.append(f"  - {msg[:100]}")

        return "\n".join(lines)

    def list_sessions(self) -> List[str]:
        """List all session IDs."""
        return list(self._sessions.keys())

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get session manager statistics."""
        total = len(self._sessions)
        if total == 0:
            return {"total_sessions": 0}

        total_turns = sum(len(s.history) for s in self._sessions.values())
        total_facts = sum(len(s.extracted_facts) for s in self._sessions.values())
        total_conflicts = sum(len(s.pending_conflicts) for s in self._sessions.values())

        return {
            "total_sessions": total,
            "total_turns": total_turns,
            "total_extracted_facts": total_facts,
            "total_pending_conflicts": total_conflicts,
            "avg_turns_per_session": total_turns / total,
        }
