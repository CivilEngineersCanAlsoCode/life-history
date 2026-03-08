"""
Tests for Session Continuity (Context Retrieval & Pending Items)

Covers:
- Context retrieval from current session
- Context retrieval from prior sessions
- Pending item management
- Session summarization
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from life_brain.session.session_manager import (
    SessionManager,
    Session,
    SessionMetadata,
    SessionMessage,
)
from life_brain.session.continuity import (
    ContextRetriever,
    PendingItemManager,
    PendingItemType,
    PendingItem,
)


class TestContextRetriever:
    """Tests for context retrieval."""

    @pytest.fixture
    def temp_session_dir(self):
        """Create temporary session directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def session_manager(self, temp_session_dir):
        """Create session manager with temp storage."""
        return SessionManager(temp_session_dir)

    @pytest.fixture
    def context_retriever(self, session_manager):
        """Create context retriever."""
        return ContextRetriever(session_manager)

    def test_get_recent_context_empty_session(self, context_retriever, session_manager):
        """Test getting context from empty session."""
        session = session_manager.create_session()

        windows = context_retriever.get_recent_context(session)
        assert len(windows) == 0

    def test_get_recent_context_single_turn(self, context_retriever, session_manager):
        """Test getting context with one Q&A pair."""
        session = session_manager.create_session()

        session_manager.add_message(session, "user", "Tell me about interviews")
        session_manager.add_message(session, "assistant", "Great! Let's prepare...")

        windows = context_retriever.get_recent_context(session, lookback_turns=10)
        assert len(windows) == 1
        assert windows[0].topic == "Recent conversation"

    def test_get_recent_context_multiple_turns(self, context_retriever, session_manager):
        """Test getting context with multiple turns."""
        session = session_manager.create_session()

        # Add 4 messages (2 Q&A pairs)
        session_manager.add_message(session, "user", "Question 1")
        session_manager.add_message(session, "assistant", "Answer 1")
        session_manager.add_message(session, "user", "Question 2")
        session_manager.add_message(session, "assistant", "Answer 2")

        windows = context_retriever.get_recent_context(session, lookback_turns=10)
        assert len(windows) == 2

    def test_get_recent_context_lookback_limit(self, context_retriever, session_manager):
        """Test lookback_turns parameter."""
        session = session_manager.create_session()

        # Add 6 messages (3 Q&A pairs)
        for i in range(3):
            session_manager.add_message(session, "user", f"Q{i}")
            session_manager.add_message(session, "assistant", f"A{i}")

        # Get only 1 turn back
        windows = context_retriever.get_recent_context(session, lookback_turns=2)
        assert len(windows) == 1  # Only last pair

    def test_get_recent_context_includes_metadata(self, context_retriever, session_manager):
        """Test that context windows include metadata."""
        session = session_manager.create_session()
        session.current_expert = "Satya"
        session.current_use_case_id = "C1"
        session_manager.save_session(session)

        session_manager.add_message(session, "user", "Interview question")
        session_manager.add_message(session, "assistant", "Let's practice")

        windows = context_retriever.get_recent_context(session)
        assert len(windows) > 0
        assert windows[0].expert == "Satya"
        assert windows[0].use_case == "C1"

    def test_get_prior_session_context(self, context_retriever, session_manager):
        """Test retrieving context from prior sessions."""
        user_id = "test_user_123"

        # Create and close first session
        session1 = session_manager.create_session(user_id=user_id)
        session_manager.add_message(session1, "user", "First question")
        session_manager.add_message(session1, "assistant", "First answer")

        # Create current session
        current_session = session_manager.create_session(user_id=user_id)

        # Get prior context
        prior_windows = context_retriever.get_prior_session_context(
            user_id=user_id,
            current_session_id=current_session.session_id,
            lookback_sessions=5
        )

        assert len(prior_windows) > 0
        assert prior_windows[0].session_id == session1.session_id

    def test_get_conversation_summary(self, context_retriever, session_manager):
        """Test conversation summary generation."""
        session = session_manager.create_session()
        session.current_expert = "Richard"
        session.current_use_case_id = "C2"
        session_manager.save_session(session)

        session_manager.add_message(session, "user", "Question")
        session_manager.add_message(session, "assistant", "Answer")

        summary = context_retriever.get_conversation_summary(session)
        assert "small_talk" in summary or "guided" in summary
        assert "2 messages" in summary
        assert "C2" in summary or "Richard" in summary

    def test_context_window_structure(self, context_retriever, session_manager):
        """Test that context windows have required fields."""
        session = session_manager.create_session()
        session_manager.add_message(session, "user", "Test")
        session_manager.add_message(session, "assistant", "Response")

        windows = context_retriever.get_recent_context(session)
        assert len(windows) > 0

        window = windows[0]
        assert window.window_id
        assert window.session_id == session.session_id
        assert window.turn_range
        assert window.topic
        assert len(window.messages) == 2


class TestPendingItemManager:
    """Tests for pending item management."""

    @pytest.fixture
    def temp_session_dir(self):
        """Create temporary session directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def session_manager(self, temp_session_dir):
        """Create session manager with temp storage."""
        return SessionManager(temp_session_dir)

    @pytest.fixture
    def pending_manager(self, session_manager):
        """Create pending item manager."""
        return PendingItemManager(session_manager)

    def test_add_pending_item(self, pending_manager, session_manager):
        """Test adding a pending item."""
        session = session_manager.create_session()

        item = pending_manager.add_pending_item(
            session,
            PendingItemType.FOLLOW_UP,
            "Tell me about your background",
            "User dodged the question",
            priority=0
        )

        assert item is not None
        assert item.item_type == PendingItemType.FOLLOW_UP
        assert item.priority == 0

    def test_get_pending_items(self, pending_manager, session_manager):
        """Test retrieving pending items."""
        session = session_manager.create_session()

        # Add some items
        pending_manager.add_pending_item(
            session,
            PendingItemType.FOLLOW_UP,
            "Q1",
            "Context 1",
            priority=0
        )
        pending_manager.add_pending_item(
            session,
            PendingItemType.UNANSWERED,
            "Q2",
            "Context 2",
            priority=1
        )

        items = pending_manager.get_pending_items(session)
        assert len(items) == 2
        # Should be sorted by priority
        assert items[0].priority == 0

    def test_get_pending_items_by_type(self, pending_manager, session_manager):
        """Test filtering pending items by type."""
        session = session_manager.create_session()

        pending_manager.add_pending_item(session, PendingItemType.FOLLOW_UP, "Q1", "C1")
        pending_manager.add_pending_item(session, PendingItemType.ACTION_ITEM, "Q2", "C2")
        pending_manager.add_pending_item(session, PendingItemType.FOLLOW_UP, "Q3", "C3")

        follow_ups = pending_manager.get_pending_items(session, PendingItemType.FOLLOW_UP)
        assert len(follow_ups) == 2

        actions = pending_manager.get_pending_items(session, PendingItemType.ACTION_ITEM)
        assert len(actions) == 1

    def test_get_pending_items_by_priority(self, pending_manager, session_manager):
        """Test filtering pending items by priority."""
        session = session_manager.create_session()

        pending_manager.add_pending_item(session, PendingItemType.FOLLOW_UP, "Q1", "C1", priority=0)
        pending_manager.add_pending_item(session, PendingItemType.FOLLOW_UP, "Q2", "C2", priority=1)
        pending_manager.add_pending_item(session, PendingItemType.FOLLOW_UP, "Q3", "C3", priority=2)

        high = pending_manager.get_pending_items(session, priority=0)
        assert len(high) == 1

    def test_resolve_pending_item(self, pending_manager, session_manager):
        """Test resolving a pending item."""
        session = session_manager.create_session()

        item = pending_manager.add_pending_item(
            session,
            PendingItemType.FOLLOW_UP,
            "Test question",
            "Test context"
        )

        # Resolve it
        resolved = pending_manager.resolve_pending_item(
            session,
            item.item_id,
            "User answered in follow-up"
        )

        assert resolved is True

        # Should no longer appear
        remaining = pending_manager.get_pending_items(session)
        assert len(remaining) == 0

    def test_resolve_nonexistent_item(self, pending_manager, session_manager):
        """Test resolving non-existent item returns False."""
        session = session_manager.create_session()

        resolved = pending_manager.resolve_pending_item(
            session,
            "nonexistent_id",
            "Fake resolution"
        )

        assert resolved is False

    def test_pending_summary(self, pending_manager, session_manager):
        """Test pending item summary."""
        session = session_manager.create_session()

        pending_manager.add_pending_item(session, PendingItemType.FOLLOW_UP, "Q1", "C1", priority=0)
        pending_manager.add_pending_item(session, PendingItemType.ACTION_ITEM, "Q2", "C2", priority=1)

        summary = pending_manager.get_pending_summary(session)
        assert "Pending" in summary
        assert "Q1" in summary
        assert "Q2" in summary

    def test_empty_pending_summary(self, pending_manager, session_manager):
        """Test summary when no pending items."""
        session = session_manager.create_session()

        summary = pending_manager.get_pending_summary(session)
        assert "No pending items" in summary


class TestSessionContinuityIntegration:
    """Integration tests for session continuity."""

    @pytest.fixture
    def temp_session_dir(self):
        """Create temporary session directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_end_to_end_session_with_continuity(self, temp_session_dir):
        """Test complete session flow with context and pending items."""
        manager = SessionManager(temp_session_dir)
        context_retriever = ContextRetriever(manager)
        pending_manager = PendingItemManager(manager)

        # Create session
        session = manager.create_session(user_id="user123")

        # Add messages
        manager.add_message(session, "user", "Tell me about interviews")
        manager.add_message(session, "assistant", "Interviews test your thinking...")

        # Add pending item
        pending_manager.add_pending_item(
            session,
            PendingItemType.FOLLOW_UP,
            "Tell me about specific technologies you used",
            "User mentioned projects but didn't specify tech stack",
            priority=0
        )

        # Get context
        context = context_retriever.get_recent_context(session)
        assert len(context) > 0

        # Get summary
        summary = context_retriever.get_conversation_summary(session)
        assert len(summary) > 0

        # Get pending
        pending = pending_manager.get_pending_items(session)
        assert len(pending) == 1

        # Resolve pending
        pending_manager.resolve_pending_item(session, pending[0].item_id, "Resolved in Q2")
        remaining = pending_manager.get_pending_items(session)
        assert len(remaining) == 0

    def test_multi_session_continuity(self, temp_session_dir):
        """Test continuity across multiple sessions."""
        manager = SessionManager(temp_session_dir)
        context_retriever = ContextRetriever(manager)

        user_id = "shared_user"

        # Create first session
        session1 = manager.create_session(user_id=user_id)
        session1.current_use_case_id = "C1"
        manager.save_session(session1)
        manager.add_message(session1, "user", "Preparing for interviews")
        manager.add_message(session1, "assistant", "Let's start with coding...")

        # Create second session (new day, same user)
        session2 = manager.create_session(user_id=user_id)

        # Retrieve context from prior session
        prior_context = context_retriever.get_prior_session_context(
            user_id=user_id,
            current_session_id=session2.session_id
        )

        assert len(prior_context) > 0
        assert prior_context[0].use_case == "C1"
