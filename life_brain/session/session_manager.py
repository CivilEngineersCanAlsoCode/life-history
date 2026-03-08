"""
Session State Management — Store and retrieve conversation session state.

Manages:
- Session creation and lifecycle
- Multi-turn state persistence
- Session timeout handling
- Session history and audit
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
import json
import logging
import uuid
import os

logger = logging.getLogger(__name__)

# Session storage path
SESSION_STORAGE_PATH = os.getenv("LIFE_BRAIN_SESSION_PATH", "./sessions")


@dataclass
class SessionMetadata:
    """Metadata about a session."""
    session_id: str
    user_id: Optional[str] = None
    mode: str = "small_talk"  # small_talk or guided
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_activity_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    timeout_seconds: int = 86400  # 24 hours default
    is_active: bool = True
    message_count: int = 0
    captured_nuggets_count: int = 0


@dataclass
class SessionMessage:
    """A single message in a session."""
    role: str  # "user" or "system"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Session:
    """Complete session state."""
    session_id: str
    metadata: SessionMetadata
    messages: List[SessionMessage] = field(default_factory=list)
    current_use_case_id: Optional[str] = None
    current_expert: Optional[str] = None
    captured_nuggets: List[Dict[str, Any]] = field(default_factory=list)
    extra_context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            "session_id": self.session_id,
            "metadata": asdict(self.metadata),
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    "timestamp": m.timestamp,
                    "metadata": m.metadata
                }
                for m in self.messages
            ],
            "current_use_case_id": self.current_use_case_id,
            "current_expert": self.current_expert,
            "captured_nuggets": self.captured_nuggets,
            "extra_context": self.extra_context,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Session":
        """Create Session from dict."""
        session = Session(
            session_id=data["session_id"],
            metadata=SessionMetadata(**data["metadata"]),
            current_use_case_id=data.get("current_use_case_id"),
            current_expert=data.get("current_expert"),
            captured_nuggets=data.get("captured_nuggets", []),
            extra_context=data.get("extra_context", {}),
        )
        # Reconstruct messages
        for msg_data in data.get("messages", []):
            session.messages.append(
                SessionMessage(
                    role=msg_data["role"],
                    content=msg_data["content"],
                    timestamp=msg_data.get("timestamp"),
                    metadata=msg_data.get("metadata"),
                )
            )
        return session


class SessionManager:
    """Manages session lifecycle and persistence."""

    def __init__(self, storage_path: str = SESSION_STORAGE_PATH):
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        """Ensure storage directory exists."""
        os.makedirs(self.storage_path, exist_ok=True)
        logger.debug(f"Session storage ensured at {self.storage_path}")

    def _get_session_file(self, session_id: str) -> str:
        """Get path to session file."""
        return os.path.join(self.storage_path, f"{session_id}.json")

    def create_session(
        self,
        mode: str = "small_talk",
        user_id: Optional[str] = None,
        timeout_seconds: int = 86400
    ) -> Session:
        """
        Create a new session.

        Args:
            mode: "small_talk" or "guided"
            user_id: Optional user identifier
            timeout_seconds: Session timeout (default 24 hours)

        Returns:
            New Session instance
        """
        session_id = f"session_{uuid.uuid4().hex[:12]}"

        metadata = SessionMetadata(
            session_id=session_id,
            user_id=user_id,
            mode=mode,
            timeout_seconds=timeout_seconds,
        )

        session = Session(
            session_id=session_id,
            metadata=metadata,
        )

        self.save_session(session)
        logger.info(f"Created new session: {session_id} (mode: {mode}, user: {user_id})")

        return session

    def save_session(self, session: Session) -> None:
        """
        Persist session to storage.

        Args:
            session: Session to save
        """
        try:
            file_path = self._get_session_file(session.session_id)
            with open(file_path, "w") as f:
                json.dump(session.to_dict(), f, indent=2)

            # Update last_activity_at
            session.metadata.last_activity_at = datetime.utcnow().isoformat()

            logger.debug(f"Saved session: {session.session_id}")
        except Exception as e:
            logger.error(f"Failed to save session {session.session_id}: {e}")
            raise

    def load_session(self, session_id: str) -> Optional[Session]:
        """
        Load session from storage.

        Args:
            session_id: Session ID to load

        Returns:
            Session instance or None if not found/expired
        """
        try:
            file_path = self._get_session_file(session_id)

            if not os.path.exists(file_path):
                logger.warning(f"Session not found: {session_id}")
                return None

            with open(file_path, "r") as f:
                data = json.load(f)

            session = Session.from_dict(data)

            # Check if expired
            if self.is_session_expired(session):
                logger.info(f"Session expired: {session_id}")
                self.delete_session(session_id)
                return None

            # Update last activity
            session.metadata.last_activity_at = datetime.utcnow().isoformat()
            self.save_session(session)

            logger.debug(f"Loaded session: {session_id}")
            return session

        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session ID to delete

        Returns:
            True if deleted, False if not found
        """
        try:
            file_path = self._get_session_file(session_id)

            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted session: {session_id}")
                return True

            logger.warning(f"Session not found for deletion: {session_id}")
            return False

        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False

    def is_session_expired(self, session: Session) -> bool:
        """
        Check if session has expired.

        Args:
            session: Session to check

        Returns:
            True if expired, False otherwise
        """
        last_activity = datetime.fromisoformat(session.metadata.last_activity_at)
        timeout = timedelta(seconds=session.metadata.timeout_seconds)
        now = datetime.utcnow()

        is_expired = (now - last_activity) > timeout

        if is_expired:
            logger.debug(f"Session expired: {session.session_id}")

        return is_expired

    def add_message(
        self,
        session: Session,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a message to session.

        Args:
            session: Session to add message to
            role: "user" or "system"
            content: Message content
            metadata: Optional metadata
        """
        message = SessionMessage(role=role, content=content, metadata=metadata)
        session.messages.append(message)
        session.metadata.message_count = len(session.messages)
        self.save_session(session)

        logger.debug(f"Added message to session {session.session_id}: {role}")

    def add_captured_nugget(
        self,
        session: Session,
        nugget: Dict[str, Any]
    ) -> None:
        """
        Add captured nugget to session.

        Args:
            session: Session
            nugget: Captured nugget data
        """
        session.captured_nuggets.append(nugget)
        session.metadata.captured_nuggets_count = len(session.captured_nuggets)
        self.save_session(session)

        logger.debug(f"Added nugget to session {session.session_id}")

    def list_sessions(self, user_id: Optional[str] = None, active_only: bool = True) -> List[SessionMetadata]:
        """
        List all sessions (optionally filtered by user).

        Args:
            user_id: Filter by user ID
            active_only: Only return active sessions

        Returns:
            List of session metadata
        """
        try:
            sessions = []

            if not os.path.exists(self.storage_path):
                return sessions

            for filename in os.listdir(self.storage_path):
                if not filename.endswith(".json"):
                    continue

                file_path = os.path.join(self.storage_path, filename)

                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)

                    metadata = SessionMetadata(**data["metadata"])

                    # Filter by user_id if specified
                    if user_id and metadata.user_id != user_id:
                        continue

                    # Filter expired sessions
                    if active_only and self.is_session_expired(Session.from_dict(data)):
                        continue

                    sessions.append(metadata)

                except Exception as e:
                    logger.warning(f"Error reading session file {filename}: {e}")
                    continue

            logger.debug(f"Listed {len(sessions)} sessions")
            return sessions

        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []

    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.

        Returns:
            Number of sessions deleted
        """
        try:
            count = 0

            if not os.path.exists(self.storage_path):
                return count

            for filename in os.listdir(self.storage_path):
                if not filename.endswith(".json"):
                    continue

                file_path = os.path.join(self.storage_path, filename)
                session_id = filename.replace(".json", "")

                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)

                    session = Session.from_dict(data)

                    if self.is_session_expired(session):
                        self.delete_session(session_id)
                        count += 1

                except Exception as e:
                    logger.warning(f"Error checking session {filename}: {e}")
                    continue

            logger.info(f"Cleaned up {count} expired sessions")
            return count

        except Exception as e:
            logger.error(f"Failed to cleanup sessions: {e}")
            return 0

    def get_session_summary(self, session: Session) -> Dict[str, Any]:
        """
        Get summary of session.

        Returns:
            Dict with session statistics
        """
        return {
            "session_id": session.session_id,
            "mode": session.metadata.mode,
            "user_id": session.metadata.user_id,
            "created_at": session.metadata.created_at,
            "last_activity_at": session.metadata.last_activity_at,
            "is_active": session.metadata.is_active,
            "is_expired": self.is_session_expired(session),
            "message_count": session.metadata.message_count,
            "captured_nuggets_count": session.metadata.captured_nuggets_count,
            "current_use_case": session.current_use_case_id,
            "current_expert": session.current_expert,
        }
