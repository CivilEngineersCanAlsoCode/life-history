"""Test suite for session management."""

import pytest
from datetime import datetime

from life_brain.session.session_manager import SessionManager, SessionContext, SessionStatus


class TestSessionContext:
    """Test SessionContext dataclass."""

    def test_create_context(self):
        """Test creating session context."""
        ctx = SessionContext(
            session_id="sess_001",
            user_id="user_001",
        )

        assert ctx.session_id == "sess_001"
        assert ctx.user_id == "user_001"
        assert ctx.status == SessionStatus.INITIALIZED

    def test_to_dict(self):
        """Test converting context to dictionary."""
        ctx = SessionContext(
            session_id="sess_001",
            user_id="user_001",
            language="english",
            detail_level=8,
        )

        ctx_dict = ctx.to_dict()
        assert ctx_dict["session_id"] == "sess_001"
        assert ctx_dict["language"] == "english"


class TestSessionManager:
    """Test SessionManager."""

    def test_create_manager(self):
        """Test creating session manager."""
        manager = SessionManager()
        assert len(manager.sessions) == 0

    def test_session_init(self):
        """Test initializing a session."""
        manager = SessionManager()

        context = manager.session_init(
            session_id="sess_001",
            user_id="user_001",
            language="english",
            detail_level=7,
        )

        assert context.session_id == "sess_001"
        assert context.language == "english"
        assert context.status == SessionStatus.INITIALIZED

    def test_get_session(self):
        """Test retrieving a session."""
        manager = SessionManager()

        manager.session_init("sess_001", "user_001", language="english")
        context = manager.get_session("sess_001")

        assert context is not None
        assert context.language == "english"

    def test_get_user_sessions(self):
        """Test getting all sessions for user."""
        manager = SessionManager()

        manager.session_init("sess_001", "user_001")
        manager.session_init("sess_002", "user_001")
        manager.session_init("sess_003", "user_002")

        user_001_sessions = manager.get_user_sessions("user_001")
        assert len(user_001_sessions) == 2

    def test_activate_session(self):
        """Test activating a session."""
        manager = SessionManager()

        manager.session_init("sess_001", "user_001")
        success, error = manager.activate_session("sess_001")

        assert success is True
        context = manager.get_session("sess_001")
        assert context.status == SessionStatus.ACTIVE

    def test_pause_session(self):
        """Test pausing a session."""
        manager = SessionManager()

        manager.session_init("sess_001", "user_001")
        manager.activate_session("sess_001")
        success, error = manager.pause_session("sess_001")

        assert success is True
        context = manager.get_session("sess_001")
        assert context.status == SessionStatus.PAUSED

    def test_close_session(self):
        """Test closing a session."""
        manager = SessionManager()

        manager.session_init("sess_001", "user_001")
        success, error = manager.close_session("sess_001")

        assert success is True
        context = manager.get_session("sess_001")
        assert context.status == SessionStatus.CLOSED

    def test_record_turn(self):
        """Test recording conversation turns."""
        manager = SessionManager()

        manager.session_init("sess_001", "user_001")
        assert manager.get_session("sess_001").turn_count == 0

        for i in range(5):
            manager.record_turn("sess_001")

        assert manager.get_session("sess_001").turn_count == 5

    def test_update_session_context(self):
        """Test updating session context."""
        manager = SessionManager()

        manager.session_init("sess_001", "user_001", language="hinglish")
        success, error = manager.update_session_context(
            "sess_001",
            language="english",
            detail_level=9,
        )

        assert success is True
        context = manager.get_session("sess_001")
        assert context.language == "english"
        assert context.detail_level == 9

    def test_get_session_history(self):
        """Test getting session history."""
        manager = SessionManager()

        manager.session_init("sess_001", "user_001")
        manager.activate_session("sess_001")
        manager.update_session_context("sess_001", note="test update")

        history = manager.get_session_history("sess_001")
        assert len(history) >= 3  # init, activate, update

    def test_get_session_summary(self):
        """Test getting session summary."""
        manager = SessionManager()

        manager.session_init("sess_001", "user_001", language="english")
        manager.activate_session("sess_001")
        for _ in range(3):
            manager.record_turn("sess_001")

        summary = manager.get_session_summary("sess_001")

        assert summary["session_id"] == "sess_001"
        assert summary["turn_count"] == 3
        assert summary["status"] == "active"

    def test_get_active_session(self):
        """Test getting active session for user."""
        manager = SessionManager()

        manager.session_init("sess_001", "user_001")
        manager.session_init("sess_002", "user_001")

        manager.activate_session("sess_001")

        active = manager.get_active_session("user_001")
        assert active.session_id == "sess_001"

    def test_get_statistics(self):
        """Test getting statistics."""
        manager = SessionManager()

        # Create multiple sessions
        for i in range(3):
            manager.session_init(f"sess_{i:03d}", f"user_{i // 2}")

        manager.activate_session("sess_000")
        manager.close_session("sess_001")

        for _ in range(5):
            manager.record_turn("sess_000")

        stats = manager.get_statistics()

        assert stats["total_sessions"] == 3
        assert stats["active_sessions"] == 1
        assert stats["closed_sessions"] == 1

    def test_export_session(self):
        """Test exporting session data."""
        manager = SessionManager()

        manager.session_init("sess_001", "user_001", language="english")
        manager.activate_session("sess_001")

        exported = manager.export_session("sess_001")

        assert exported is not None
        assert "context" in exported
        assert "history" in exported
        assert "summary" in exported

    def test_export_user_sessions(self):
        """Test exporting all user sessions."""
        manager = SessionManager()

        manager.session_init("sess_001", "user_001")
        manager.session_init("sess_002", "user_001")
        manager.session_init("sess_003", "user_002")

        exported = manager.export_user_sessions("user_001")
        assert len(exported) == 2

    def test_session_workflow(self):
        """Test complete session workflow."""
        manager = SessionManager()

        # Initialize
        ctx = manager.session_init("sess_001", "user_001", language="english")
        assert ctx.status == SessionStatus.INITIALIZED

        # Activate
        manager.activate_session("sess_001")
        assert manager.get_session("sess_001").status == SessionStatus.ACTIVE

        # Record interactions
        for i in range(3):
            manager.record_turn("sess_001")

        # Pause
        manager.pause_session("sess_001")
        assert manager.get_session("sess_001").status == SessionStatus.PAUSED

        # Resume
        manager.activate_session("sess_001")

        # Close
        manager.close_session("sess_001")
        assert manager.get_session("sess_001").status == SessionStatus.CLOSED

        # Verify summary
        summary = manager.get_session_summary("sess_001")
        assert summary["turn_count"] == 3
        assert summary["status"] == "closed"
