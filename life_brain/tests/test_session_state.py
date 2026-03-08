"""
Tests for session state persistence and continuity.

Tests cover:
- Session creation and retrieval
- Turn-by-turn history management
- State persistence (to_dict/from_dict, JSON)
- Expert priming context generation
- Knowledge accumulation (facts, conflicts, commitments)
- Session manager operations
- Edge cases
"""

import pytest
import json

from life_brain.conversation.session_state import (
    SessionState,
    SessionManager,
    TurnMessage,
)


class TestTurnMessage:
    """Test TurnMessage."""

    def test_create_turn(self):
        turn = TurnMessage(role="user", content="Hello there")
        assert turn.role == "user"
        assert turn.content == "Hello there"
        assert turn.timestamp  # auto-populated

    def test_to_dict(self):
        turn = TurnMessage(role="assistant", content="Hi!")
        d = turn.to_dict()
        assert d["role"] == "assistant"
        assert d["content"] == "Hi!"
        assert "timestamp" in d


class TestSessionState:
    """Test SessionState."""

    def test_create_session(self):
        state = SessionState(session_id="s1")
        assert state.session_id == "s1"
        assert state.history == []
        assert state.extracted_facts == []

    def test_add_turn(self):
        state = SessionState(session_id="s1")
        turn = state.add_turn("user", "Hello")
        assert len(state.history) == 1
        assert turn.role == "user"

    def test_multiple_turns(self):
        state = SessionState(session_id="s1")
        state.add_turn("user", "Hi")
        state.add_turn("assistant", "Hello!")
        state.add_turn("user", "How are you?")
        assert len(state.history) == 3

    def test_get_history_text(self):
        state = SessionState(session_id="s1")
        state.add_turn("user", "Hello")
        state.add_turn("assistant", "Hi there")
        text = state.get_history_text()
        assert "User: Hello" in text
        assert "Assistant: Hi there" in text

    def test_get_user_messages(self):
        state = SessionState(session_id="s1")
        state.add_turn("user", "Message A")
        state.add_turn("assistant", "Response A")
        state.add_turn("user", "Message B")
        msgs = state.get_user_messages()
        assert msgs == ["Message A", "Message B"]

    def test_add_extracted_fact(self):
        state = SessionState(session_id="s1")
        state.add_extracted_fact({"type": "metric", "value": "4x improvement"})
        assert len(state.extracted_facts) == 1

    def test_add_pending_conflict(self):
        state = SessionState(session_id="s1")
        state.add_pending_conflict({"doc_id": "d1", "score": 0.75})
        assert len(state.pending_conflicts) == 1

    def test_add_commitment(self):
        state = SessionState(session_id="s1")
        state.add_commitment({"action": "submit report", "deadline": "March 31"})
        assert len(state.commitments) == 1

    def test_to_dict_structure(self):
        state = SessionState(session_id="s1")
        state.add_turn("user", "Hello")
        d = state.to_dict()

        assert "session_id" in d
        assert "history" in d
        assert "extracted_facts" in d
        assert "pending_conflicts" in d
        assert "commitments" in d
        assert "session_summary" in d
        assert "metadata" in d

    def test_from_dict_roundtrip(self):
        state = SessionState(session_id="s1")
        state.add_turn("user", "Hello")
        state.add_turn("assistant", "Hi!")
        state.active_expert = "Career Coach"
        state.session_summary = "Discussed career options"

        d = state.to_dict()
        restored = SessionState.from_dict(d)

        assert restored.session_id == "s1"
        assert len(restored.history) == 2
        assert restored.active_expert == "Career Coach"
        assert restored.session_summary == "Discussed career options"

    def test_json_roundtrip(self):
        state = SessionState(session_id="s1")
        state.add_turn("user", "Hello")
        state.extracted_facts.append({"key": "value"})

        json_str = state.to_json()
        assert isinstance(json_str, str)

        restored = SessionState.from_json(json_str)
        assert restored.session_id == "s1"
        assert len(restored.history) == 1
        assert len(restored.extracted_facts) == 1

    def test_from_dict_history_turns(self):
        data = {
            "session_id": "s1",
            "history": [
                {"role": "user", "content": "Hi", "timestamp": "2024-01-01"},
                {"role": "assistant", "content": "Hello", "timestamp": "2024-01-01"},
            ],
            "extracted_facts": [],
            "pending_conflicts": [],
            "commitments": [],
        }
        state = SessionState.from_dict(data)
        assert len(state.history) == 2
        assert state.history[0].role == "user"


class TestSessionManager:
    """Test SessionManager."""

    def test_create_session(self):
        mgr = SessionManager()
        state = mgr.create_session("s1")
        assert state.session_id == "s1"

    def test_create_empty_id_raises(self):
        mgr = SessionManager()
        with pytest.raises(ValueError):
            mgr.create_session("")

    def test_get_session(self):
        mgr = SessionManager()
        mgr.create_session("s1")
        retrieved = mgr.get_session("s1")
        assert retrieved is not None
        assert retrieved.session_id == "s1"

    def test_get_nonexistent_session(self):
        mgr = SessionManager()
        assert mgr.get_session("nonexistent") is None

    def test_save_session(self):
        mgr = SessionManager()
        state = mgr.create_session("s1")
        state.active_expert = "Career Coach"
        mgr.save_session(state)

        retrieved = mgr.get_session("s1")
        assert retrieved.active_expert == "Career Coach"

    def test_get_or_create_new(self):
        mgr = SessionManager()
        state = mgr.get_or_create("new_session")
        assert state.session_id == "new_session"

    def test_get_or_create_existing(self):
        mgr = SessionManager()
        s1 = mgr.create_session("s1")
        s1.active_expert = "Coach"
        s2 = mgr.get_or_create("s1")
        assert s2.active_expert == "Coach"

    def test_build_priming_context_no_session(self):
        mgr = SessionManager()
        ctx = mgr.build_priming_context("nonexistent")
        assert ctx is None

    def test_build_priming_context_with_session(self):
        mgr = SessionManager()
        state = mgr.create_session("s1")
        state.active_expert = "Career Coach"
        state.current_topic = "Promotion strategy"
        state.session_summary = "Discussed career goals"
        state.add_turn("user", "What should I do?")

        ctx = mgr.build_priming_context("s1")

        assert ctx is not None
        assert "Career Coach" in ctx
        assert "Promotion strategy" in ctx
        assert "Discussed career goals" in ctx

    def test_priming_context_includes_recent_messages(self):
        mgr = SessionManager()
        state = mgr.create_session("s1")
        state.add_turn("user", "Message one")
        state.add_turn("user", "Message two")
        state.add_turn("user", "Message three")

        ctx = mgr.build_priming_context("s1")
        assert "Message" in ctx

    def test_priming_context_includes_pending_counts(self):
        mgr = SessionManager()
        state = mgr.create_session("s1")
        state.add_pending_conflict({"id": "c1"})
        state.add_commitment({"action": "do it"})

        ctx = mgr.build_priming_context("s1")
        assert "conflict" in ctx.lower()
        assert "commitment" in ctx.lower()

    def test_list_sessions(self):
        mgr = SessionManager()
        mgr.create_session("s1")
        mgr.create_session("s2")
        sessions = mgr.list_sessions()
        assert "s1" in sessions
        assert "s2" in sessions

    def test_delete_session(self):
        mgr = SessionManager()
        mgr.create_session("s1")
        result = mgr.delete_session("s1")
        assert result is True
        assert mgr.get_session("s1") is None

    def test_delete_nonexistent_session(self):
        mgr = SessionManager()
        result = mgr.delete_session("nonexistent")
        assert result is False

    def test_statistics_empty(self):
        mgr = SessionManager()
        stats = mgr.get_statistics()
        assert stats["total_sessions"] == 0

    def test_statistics_with_data(self):
        mgr = SessionManager()
        s1 = mgr.create_session("s1")
        s1.add_turn("user", "Hello")
        s1.add_turn("assistant", "Hi")
        s1.add_extracted_fact({"key": "val"})

        s2 = mgr.create_session("s2")
        s2.add_turn("user", "World")

        stats = mgr.get_statistics()
        assert stats["total_sessions"] == 2
        assert stats["total_turns"] == 3
        assert stats["total_extracted_facts"] == 1
        assert stats["avg_turns_per_session"] == 1.5
