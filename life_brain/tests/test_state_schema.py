"""
Test suite for session state schema.

Tests cover:
- Session state initialization and management
- Conversation turn tracking
- Learned insights
- Conflict management
- State persistence and export
"""

import pytest
from life_brain.session.state_schema import (
    SessionStateSchema,
    SessionState,
    SessionStateContext,
    ConversationTurn,
    LearnedInsight,
    UnresolvedConflict,
    StateComponent,
)


class TestSessionStateContext:
    """Test SessionStateContext dataclass."""

    def test_create_context(self):
        """Test creating session context."""
        context = SessionStateContext(
            session_id="sess_001",
            user_id="user_001",
            language="english",
            communication_style="formal",
            detail_level=7,
        )

        assert context.session_id == "sess_001"
        assert context.user_id == "user_001"
        assert context.language == "english"

    def test_to_dict(self):
        """Test converting context to dictionary."""
        context = SessionStateContext(
            session_id="sess_001",
            user_id="user_001",
            language="hinglish",
            communication_style="conversational",
            detail_level=5,
            expert_domain="product",
        )

        context_dict = context.to_dict()
        assert context_dict["session_id"] == "sess_001"
        assert context_dict["expert_domain"] == "product"


class TestConversationTurn:
    """Test ConversationTurn dataclass."""

    def test_create_turn(self):
        """Test creating conversation turn."""
        turn = ConversationTurn(
            turn_number=1,
            user_message="Hello, how are you?",
            assistant_response="I'm doing well, thanks!",
            sentiment="positive",
            polarity=0.5,
            emotions={"joy": 0.6},
        )

        assert turn.turn_number == 1
        assert turn.user_message == "Hello, how are you?"


class TestLearnedInsight:
    """Test LearnedInsight dataclass."""

    def test_create_insight(self):
        """Test creating learned insight."""
        insight = LearnedInsight(
            insight_id="ins_001",
            content="User prefers detail level 8",
            category="preferences",
            confidence=0.9,
            learned_at_turn=1,
            source="user_stated",
        )

        assert insight.insight_id == "ins_001"
        assert insight.confidence == 0.9


class TestUnresolvedConflict:
    """Test UnresolvedConflict dataclass."""

    def test_create_conflict(self):
        """Test creating unresolved conflict."""
        conflict = UnresolvedConflict(
            conflict_id="conf_001",
            field_name="role",
            existing_value="Engineer",
            new_value="Senior Engineer",
            reason="Promotion mentioned",
            severity="medium",
            identified_at_turn=2,
        )

        assert conflict.conflict_id == "conf_001"
        assert conflict.field_name == "role"


class TestSessionState:
    """Test SessionState dataclass."""

    def test_create_state(self):
        """Test creating session state."""
        context = SessionStateContext(
            session_id="sess_001",
            user_id="user_001",
            language="english",
            communication_style="formal",
            detail_level=7,
        )

        state = SessionState(
            session_id="sess_001",
            context=context,
        )

        assert state.session_id == "sess_001"
        assert len(state.history) == 0

    def test_to_dict(self):
        """Test converting state to dictionary."""
        context = SessionStateContext(
            session_id="sess_001",
            user_id="user_001",
            language="english",
            communication_style="formal",
            detail_level=7,
        )

        state = SessionState(session_id="sess_001", context=context)
        state_dict = state.to_dict()

        assert state_dict["session_id"] == "sess_001"
        assert "context" in state_dict
        assert "history" in state_dict

    def test_get_summary(self):
        """Test getting state summary."""
        context = SessionStateContext(
            session_id="sess_001",
            user_id="user_001",
            language="english",
            communication_style="formal",
            detail_level=7,
        )

        state = SessionState(session_id="sess_001", context=context)
        summary = state.get_summary()

        assert summary["session_id"] == "sess_001"
        assert summary["turn_count"] == 0


class TestSessionStateSchema:
    """Test SessionStateSchema functionality."""

    def test_create_schema(self):
        """Test creating state schema."""
        schema = SessionStateSchema()
        assert len(schema.states) == 0

    def test_session_state_schema_init(self):
        """Test initializing session state."""
        schema = SessionStateSchema()

        state = schema.session_state_schema(
            session_id="sess_001",
            user_id="user_001",
            language="english",
            communication_style="formal",
            detail_level=7,
        )

        assert state.session_id == "sess_001"
        assert len(schema.states) == 1

    def test_add_turn(self):
        """Test adding conversation turn."""
        schema = SessionStateSchema()

        schema.session_state_schema("sess_001", "user_001")
        turn = schema.add_turn(
            session_id="sess_001",
            user_message="Hello",
            assistant_response="Hi there!",
            sentiment="positive",
            polarity=0.5,
            emotions={"joy": 0.6},
            expert_used="career",
        )

        assert turn is not None
        assert turn.turn_number == 1

    def test_multiple_turns(self):
        """Test adding multiple turns."""
        schema = SessionStateSchema()

        schema.session_state_schema("sess_001", "user_001")

        for i in range(3):
            schema.add_turn(
                session_id="sess_001",
                user_message=f"Message {i}",
                assistant_response=f"Response {i}",
                sentiment="neutral",
                polarity=0.0,
                emotions={},
            )

        state = schema.get_state("sess_001")
        assert len(state.history) == 3
        assert state.context.turn_count == 3

    def test_add_insight(self):
        """Test adding learned insight."""
        schema = SessionStateSchema()

        schema.session_state_schema("sess_001", "user_001")
        insight = schema.add_insight(
            session_id="sess_001",
            insight_id="ins_001",
            content="User is a product manager",
            category="career",
            confidence=0.9,
            source="user_stated",
        )

        assert insight is not None
        assert len(schema.get_knowledge("sess_001")) == 1

    def test_add_conflict(self):
        """Test adding unresolved conflict."""
        schema = SessionStateSchema()

        schema.session_state_schema("sess_001", "user_001")
        conflict = schema.add_conflict(
            session_id="sess_001",
            conflict_id="conf_001",
            field_name="role",
            existing_value="PM",
            new_value="Senior PM",
            reason="Promotion",
        )

        assert conflict is not None
        assert len(schema.get_active_conflicts("sess_001")) == 1

    def test_resolve_conflict(self):
        """Test resolving conflict."""
        schema = SessionStateSchema()

        schema.session_state_schema("sess_001", "user_001")
        schema.add_conflict(
            session_id="sess_001",
            conflict_id="conf_001",
            field_name="role",
            existing_value="PM",
            new_value="Senior PM",
            reason="Promotion",
        )

        success, error = schema.resolve_conflict(
            session_id="sess_001",
            conflict_id="conf_001",
            resolution_strategy="use_new",
        )

        assert success is True
        assert len(schema.get_active_conflicts("sess_001")) == 0

    def test_update_context(self):
        """Test updating session context."""
        schema = SessionStateSchema()

        schema.session_state_schema("sess_001", "user_001", expert_domain="product")
        success, error = schema.update_context(
            session_id="sess_001",
            expert_domain="engineering",
            mood_pattern="upbeat",
        )

        assert success is True
        state = schema.get_state("sess_001")
        assert state.context.expert_domain == "engineering"
        assert state.context.mood_pattern == "upbeat"

    def test_get_state(self):
        """Test retrieving state."""
        schema = SessionStateSchema()

        schema.session_state_schema("sess_001", "user_001")
        state = schema.get_state("sess_001")

        assert state is not None
        assert state.session_id == "sess_001"

    def test_get_nonexistent_state(self):
        """Test retrieving nonexistent state."""
        schema = SessionStateSchema()

        state = schema.get_state("nonexistent")
        assert state is None

    def test_get_recent_turns(self):
        """Test getting recent turns."""
        schema = SessionStateSchema()

        schema.session_state_schema("sess_001", "user_001")

        for i in range(5):
            schema.add_turn(
                session_id="sess_001",
                user_message=f"Message {i}",
                assistant_response=f"Response {i}",
                sentiment="neutral",
                polarity=0.0,
                emotions={},
            )

        recent = schema.get_recent_turns("sess_001", limit=3)
        assert len(recent) == 3

    def test_get_active_conflicts(self):
        """Test getting active conflicts."""
        schema = SessionStateSchema()

        schema.session_state_schema("sess_001", "user_001")

        # Add and resolve one conflict
        schema.add_conflict(
            session_id="sess_001",
            conflict_id="conf_001",
            field_name="role",
            existing_value="PM",
            new_value="Senior PM",
            reason="Promotion",
        )

        # Add unresolved conflict
        schema.add_conflict(
            session_id="sess_001",
            conflict_id="conf_002",
            field_name="company",
            existing_value="Sprinklr",
            new_value="Amex",
            reason="Career change",
        )

        # Resolve first
        schema.resolve_conflict("sess_001", "conf_001", "use_new")

        active = schema.get_active_conflicts("sess_001")
        assert len(active) == 1
        assert active[0].conflict_id == "conf_002"

    def test_get_knowledge(self):
        """Test getting learned knowledge."""
        schema = SessionStateSchema()

        schema.session_state_schema("sess_001", "user_001")

        schema.add_insight(
            session_id="sess_001",
            insight_id="ins_001",
            content="Product manager",
            category="career",
            confidence=0.9,
            source="user_stated",
        )

        schema.add_insight(
            session_id="sess_001",
            insight_id="ins_002",
            content="Prefers formal style",
            category="preferences",
            confidence=0.8,
            source="inferred",
        )

        knowledge = schema.get_knowledge("sess_001")
        assert len(knowledge) == 2

        career_knowledge = schema.get_knowledge("sess_001", category="career")
        assert len(career_knowledge) == 1

    def test_export_state(self):
        """Test exporting state."""
        schema = SessionStateSchema()

        schema.session_state_schema("sess_001", "user_001")
        schema.add_turn(
            session_id="sess_001",
            user_message="Hello",
            assistant_response="Hi",
            sentiment="positive",
            polarity=0.5,
            emotions={},
        )

        exported = schema.export_state("sess_001")
        assert exported is not None
        assert exported["session_id"] == "sess_001"
        assert len(exported["history"]) == 1

    def test_export_state_summary(self):
        """Test exporting state summary."""
        schema = SessionStateSchema()

        schema.session_state_schema("sess_001", "user_001")
        schema.add_turn(
            session_id="sess_001",
            user_message="Hello",
            assistant_response="Hi",
            sentiment="positive",
            polarity=0.5,
            emotions={},
        )

        summary = schema.export_state_summary("sess_001")
        assert summary is not None
        assert summary["turn_count"] == 1

    def test_get_all_states(self):
        """Test getting all states."""
        schema = SessionStateSchema()

        for i in range(3):
            schema.session_state_schema(f"sess_{i:03d}", f"user_{i:03d}")

        states = schema.get_all_states()
        assert len(states) == 3

    def test_get_state_statistics(self):
        """Test getting statistics."""
        schema = SessionStateSchema()

        schema.session_state_schema("sess_001", "user_001")
        schema.add_turn(
            session_id="sess_001",
            user_message="Hello",
            assistant_response="Hi",
            sentiment="positive",
            polarity=0.5,
            emotions={},
        )

        schema.session_state_schema("sess_002", "user_002")

        stats = schema.get_state_statistics()
        assert stats["total_sessions"] == 2
        assert stats["total_turns"] == 1

    def test_export_all_states(self):
        """Test exporting all states."""
        schema = SessionStateSchema()

        for i in range(3):
            schema.session_state_schema(f"sess_{i:03d}", f"user_{i:03d}")

        exported = schema.export_all_states()
        assert len(exported) == 3

    def test_complex_workflow(self):
        """Test complex workflow with multiple operations."""
        schema = SessionStateSchema()

        # Initialize
        schema.session_state_schema(
            "sess_001", "user_001", language="english", detail_level=7
        )

        # Add turns
        for turn_num in range(3):
            schema.add_turn(
                session_id="sess_001",
                user_message=f"User message {turn_num}",
                assistant_response=f"Assistant response {turn_num}",
                sentiment="positive" if turn_num % 2 == 0 else "neutral",
                polarity=0.5 if turn_num % 2 == 0 else 0.0,
                emotions={"joy": 0.5} if turn_num % 2 == 0 else {},
                expert_used="career" if turn_num == 0 else None,
            )

        # Add insights
        schema.add_insight(
            session_id="sess_001",
            insight_id="ins_001",
            content="User is a senior PM",
            category="career",
            confidence=0.9,
            source="user_stated",
        )

        # Add conflict
        schema.add_conflict(
            session_id="sess_001",
            conflict_id="conf_001",
            field_name="role",
            existing_value="PM",
            new_value="Senior PM",
            reason="Promotion",
            severity="medium",
        )

        # Update context
        schema.update_context(
            session_id="sess_001",
            mood_pattern="upbeat",
            expert_domain="product",
        )

        # Verify
        state = schema.get_state("sess_001")
        assert len(state.history) == 3
        assert len(state.knowledge) == 1
        assert len(state.conflicts) == 1
        assert state.context.mood_pattern == "upbeat"

        # Export
        exported = schema.export_state("sess_001")
        assert exported["context"]["mood_pattern"] == "upbeat"

    def test_multiple_sessions_independent(self):
        """Test multiple sessions are independent."""
        schema = SessionStateSchema()

        schema.session_state_schema("sess_001", "user_001")
        schema.session_state_schema("sess_002", "user_001")

        schema.add_turn(
            session_id="sess_001",
            user_message="Sess 1 message",
            assistant_response="Sess 1 response",
            sentiment="positive",
            polarity=0.5,
            emotions={},
        )

        schema.add_turn(
            session_id="sess_002",
            user_message="Sess 2 message",
            assistant_response="Sess 2 response",
            sentiment="negative",
            polarity=-0.5,
            emotions={},
        )

        state1 = schema.get_state("sess_001")
        state2 = schema.get_state("sess_002")

        assert len(state1.history) == 1
        assert len(state2.history) == 1
        assert state1.history[0].polarity > 0
        assert state2.history[0].polarity < 0

    def test_conflict_with_multiple_resolutions(self):
        """Test conflict resolution tracking."""
        schema = SessionStateSchema()

        schema.session_state_schema("sess_001", "user_001")

        for i in range(3):
            schema.add_conflict(
                session_id="sess_001",
                conflict_id=f"conf_{i:03d}",
                field_name=f"field_{i}",
                existing_value=f"old_{i}",
                new_value=f"new_{i}",
                reason=f"Change {i}",
            )

        # Resolve 2 conflicts
        schema.resolve_conflict("sess_001", "conf_000", "use_new")
        schema.resolve_conflict("sess_001", "conf_001", "keep_existing")

        active = schema.get_active_conflicts("sess_001")
        assert len(active) == 1

        state = schema.get_state("sess_001")
        resolved = [c for c in state.conflicts if c.resolution_strategy]
        assert len(resolved) == 2

    def test_insight_with_topics(self):
        """Test insight with related topics."""
        schema = SessionStateSchema()

        schema.session_state_schema("sess_001", "user_001")

        schema.add_insight(
            session_id="sess_001",
            insight_id="ins_001",
            content="Product strategy focus",
            category="career",
            confidence=0.9,
            source="user_stated",
            related_topics=["product_management", "strategy", "growth"],
        )

        knowledge = schema.get_knowledge("sess_001")
        assert knowledge[0].related_topics == [
            "product_management",
            "strategy",
            "growth",
        ]
