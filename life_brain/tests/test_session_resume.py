"""
Test suite for session resume functionality.

Tests cover:
- Prior session analysis and summarization
- Expert priming context generation
- Continuity prompts
- Entry point suggestions
- Resumption workflows
"""

import pytest
from datetime import datetime, timedelta

from life_brain.session.session_resume import (
    SessionResumer,
    ResumptionContext,
    PriorSessionSummary,
    ExpertPrimingContext,
)
from life_brain.session.state_schema import SessionStateSchema


class TestResumptionContext:
    """Test ResumptionContext enum."""

    def test_enum_values(self):
        """Test enum values."""
        assert ResumptionContext.NEW_SESSION.value == "new_session"
        assert ResumptionContext.SAME_DAY.value == "same_day"
        assert ResumptionContext.NEXT_DAY.value == "next_day"


class TestPriorSessionSummary:
    """Test PriorSessionSummary dataclass."""

    def test_create_summary(self):
        """Test creating prior session summary."""
        summary = PriorSessionSummary(
            session_id="sess_001",
            user_id="user_001",
            duration_minutes=30,
            turn_count=5,
            key_topics=["career", "growth"],
            outcomes=["Set career goal"],
            open_questions=["Role selection"],
            commitments=["Update resume"],
            mood_trajectory="improving",
            avg_sentiment=0.6,
            expert_used="career",
            gaps_since_last="1 day ago",
        )

        assert summary.session_id == "sess_001"
        assert summary.turn_count == 5

    def test_to_dict(self):
        """Test converting summary to dictionary."""
        summary = PriorSessionSummary(
            session_id="sess_001",
            user_id="user_001",
            duration_minutes=30,
            turn_count=5,
            key_topics=["career"],
            outcomes=["Goal set"],
            open_questions=[],
            commitments=[],
            mood_trajectory="stable",
            avg_sentiment=0.5,
            expert_used="career",
            gaps_since_last="1 day ago",
        )

        summary_dict = summary.to_dict()
        assert summary_dict["session_id"] == "sess_001"
        assert summary_dict["turn_count"] == 5


class TestExpertPrimingContext:
    """Test ExpertPrimingContext dataclass."""

    def test_create_priming_context(self):
        """Test creating expert priming context."""
        context = ExpertPrimingContext(
            expert_domain="career",
            user_background={"preferences": {"language": "english"}},
            continuity_prompts=["What's next?"],
        )

        assert context.expert_domain == "career"
        assert len(context.continuity_prompts) == 1

    def test_to_dict(self):
        """Test converting priming context to dictionary."""
        context = ExpertPrimingContext(
            expert_domain="product",
            user_background={"name": "test"},
            continuity_prompts=["Continue", "Follow up"],
        )

        context_dict = context.to_dict()
        assert context_dict["expert_domain"] == "product"
        assert len(context_dict["continuity_prompts"]) == 2


class TestSessionResumer:
    """Test SessionResumer functionality."""

    def test_create_resumer(self):
        """Test creating session resumer."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)
        assert resumer.state_schema == schema

    def test_session_resume_new_session(self):
        """Test resuming with no prior session."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        context, error = resumer.session_resume(
            session_id="sess_001",
            prior_session_id=None,
            expert_domain="career",
        )

        assert error is None
        assert context is not None
        assert context.expert_domain == "career"
        assert context.prior_context is None

    def test_session_resume_with_prior_session(self):
        """Test resuming with prior session."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        # Create prior session with data
        schema.session_state_schema(
            "sess_001", "user_001", language="english", detail_level=7
        )
        schema.add_turn(
            session_id="sess_001",
            user_message="Hello",
            assistant_response="Hi",
            sentiment="positive",
            polarity=0.5,
            emotions={"joy": 0.6},
        )
        schema.add_insight(
            session_id="sess_001",
            insight_id="ins_001",
            content="User is a PM",
            category="career",
            confidence=0.9,
            source="user_stated",
        )

        # Resume with prior
        context, error = resumer.session_resume(
            session_id="sess_002",
            prior_session_id="sess_001",
            expert_domain="product",
        )

        assert error is None
        assert context is not None
        assert context.prior_context is not None
        assert context.prior_context.session_id == "sess_001"

    def test_session_resume_missing_prior_session(self):
        """Test resuming with missing prior session."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        context, error = resumer.session_resume(
            session_id="sess_001",
            prior_session_id="nonexistent",
            expert_domain="career",
        )

        assert error is not None
        assert "not found" in error
        assert context is None

    def test_prior_session_summary_creation(self):
        """Test prior session summary creation."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        # Create session with multiple turns
        schema.session_state_schema("sess_001", "user_001")
        for i in range(3):
            schema.add_turn(
                session_id="sess_001",
                user_message=f"Message {i}",
                assistant_response=f"Response {i}",
                sentiment="positive" if i < 2 else "neutral",
                polarity=0.5 if i < 2 else 0.0,
                emotions={},
            )

        schema.add_insight(
            session_id="sess_001",
            insight_id="ins_001",
            content="Career goal",
            category="career",
            confidence=0.9,
            source="user_stated",
        )

        context, _ = resumer.session_resume(
            session_id="sess_002",
            prior_session_id="sess_001",
            expert_domain="career",
        )

        summary = context.prior_context
        assert summary.turn_count == 3
        assert len(summary.key_topics) > 0
        assert len(summary.outcomes) > 0

    def test_user_background_extraction(self):
        """Test user background extraction."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        schema.session_state_schema(
            "sess_001",
            "user_001",
            language="hinglish",
            communication_style="formal",
            detail_level=8,
        )

        schema.add_insight(
            session_id="sess_001",
            insight_id="ins_001",
            content="Python and product management",
            category="expertise",
            confidence=0.9,
            source="user_stated",
        )

        context, _ = resumer.session_resume(
            session_id="sess_002",
            prior_session_id="sess_001",
            expert_domain="product",
        )

        background = context.user_background
        assert background["preferences"]["language"] == "hinglish"
        assert background["preferences"]["detail_level"] == 8
        assert len(background["expertise_areas"]) > 0

    def test_continuity_prompts_generation(self):
        """Test continuity prompts generation."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        schema.session_state_schema("sess_001", "user_001")
        schema.add_turn(
            session_id="sess_001",
            user_message="Interested in career change",
            assistant_response="Let's explore that",
            sentiment="positive",
            polarity=0.5,
            emotions={},
        )

        schema.add_conflict(
            session_id="sess_001",
            conflict_id="conf_001",
            field_name="role",
            existing_value="PM",
            new_value="Engineering Manager",
            reason="Considering transition",
        )

        context, _ = resumer.session_resume(
            session_id="sess_002",
            prior_session_id="sess_001",
            expert_domain="career",
        )

        prompts = context.continuity_prompts
        assert len(prompts) > 0
        assert any("role" in p for p in prompts)

    def test_entry_point_new_session(self):
        """Test entry point for new session."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        context, _ = resumer.session_resume(
            session_id="sess_001",
            prior_session_id=None,
            expert_domain="career",
        )

        entry = context.suggested_entry_point
        assert "career" in entry.lower()

    def test_entry_point_high_engagement_prior(self):
        """Test entry point with high engagement in prior session."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        schema.session_state_schema("sess_001", "user_001")

        # Many turns = high engagement
        for i in range(8):
            schema.add_turn(
                session_id="sess_001",
                user_message=f"Message {i}",
                assistant_response=f"Response {i}",
                sentiment="positive",
                polarity=0.5,
                emotions={},
            )

        context, _ = resumer.session_resume(
            session_id="sess_002",
            prior_session_id="sess_001",
            expert_domain="product",
        )

        entry = context.suggested_entry_point
        assert "momentum" in entry.lower() or "great" in entry.lower()

    def test_context_awareness_new_session(self):
        """Test context awareness for new session."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        context, _ = resumer.session_resume(
            session_id="sess_001",
            prior_session_id=None,
            expert_domain="career",
        )

        awareness = context.context_awareness
        assert awareness["session_type"] == "new_session"
        assert (
            awareness["resumption_context"]
            == ResumptionContext.NEW_SESSION.value
        )

    def test_context_awareness_continuation(self):
        """Test context awareness for continuation."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        schema.session_state_schema("sess_001", "user_001")
        schema.add_turn(
            session_id="sess_001",
            user_message="Let's discuss career",
            assistant_response="Sure!",
            sentiment="positive",
            polarity=0.5,
            emotions={},
        )

        context, _ = resumer.session_resume(
            session_id="sess_002",
            prior_session_id="sess_001",
            expert_domain="career",
        )

        awareness = context.context_awareness
        assert awareness["session_type"] == "continuation"

    def test_get_priming_context(self):
        """Test retrieving priming context."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        context, _ = resumer.session_resume(
            session_id="sess_001",
            prior_session_id=None,
            expert_domain="career",
        )

        retrieved = resumer.get_priming_context("sess_001")
        assert retrieved == context

    def test_get_nonexistent_priming_context(self):
        """Test retrieving nonexistent priming context."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        context = resumer.get_priming_context("nonexistent")
        assert context is None

    def test_export_priming_context(self):
        """Test exporting priming context."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        context, _ = resumer.session_resume(
            session_id="sess_001",
            prior_session_id=None,
            expert_domain="career",
        )

        exported = resumer.export_priming_context("sess_001")
        assert exported is not None
        assert exported["expert_domain"] == "career"

    def test_get_resumption_report(self):
        """Test getting resumption report."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        schema.session_state_schema("sess_001", "user_001")
        schema.add_turn(
            session_id="sess_001",
            user_message="Test",
            assistant_response="Response",
            sentiment="neutral",
            polarity=0.0,
            emotions={},
        )

        context, _ = resumer.session_resume(
            session_id="sess_002",
            prior_session_id="sess_001",
            expert_domain="career",
        )

        report = resumer.get_resumption_report("sess_002")
        assert report is not None
        assert report["session_id"] == "sess_002"
        assert report["expert"] == "career"
        assert report["prior_session"] is not None

    def test_complex_resumption_workflow(self):
        """Test complex workflow with multiple sessions."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        # Session 1: Initial session
        schema.session_state_schema("sess_001", "user_001", language="english")
        for i in range(3):
            schema.add_turn(
                session_id="sess_001",
                user_message=f"Career question {i}",
                assistant_response=f"Guidance {i}",
                sentiment="positive",
                polarity=0.6,
                emotions={"joy": 0.5},
            )

        schema.add_insight(
            session_id="sess_001",
            insight_id="ins_001",
            content="Interested in PM roles",
            category="career",
            confidence=0.85,
            source="user_stated",
        )

        schema.add_conflict(
            session_id="sess_001",
            conflict_id="conf_001",
            field_name="role_preference",
            existing_value="IC",
            new_value="Manager",
            reason="Career growth",
        )

        # Resume to Session 2
        context, error = resumer.session_resume(
            session_id="sess_002",
            prior_session_id="sess_001",
            expert_domain="product",
        )

        assert error is None
        assert context.prior_context is not None
        assert len(context.continuity_prompts) > 0
        assert context.suggested_entry_point != ""

        # Verify report
        report = resumer.get_resumption_report("sess_002")
        assert report["prior_session"]["turn_count"] == 3
        assert len(report["continuity_points"]) > 0

    def test_mood_trajectory_analysis(self):
        """Test mood trajectory analysis."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        # Improving trajectory
        schema.session_state_schema("sess_001", "user_001")
        schema.add_turn(
            session_id="sess_001",
            user_message="I'm worried",
            assistant_response="Let's work through it",
            sentiment="negative",
            polarity=-0.3,
            emotions={},
        )
        schema.add_turn(
            session_id="sess_001",
            user_message="That helped",
            assistant_response="Great!",
            sentiment="positive",
            polarity=0.6,
            emotions={"joy": 0.7},
        )

        context, _ = resumer.session_resume(
            session_id="sess_002",
            prior_session_id="sess_001",
            expert_domain="career",
        )

        trajectory = context.prior_context.mood_trajectory
        assert trajectory == "improving"

    def test_multiple_resumers_independent(self):
        """Test multiple resumers are independent."""
        schema1 = SessionStateSchema()
        schema2 = SessionStateSchema()

        resumer1 = SessionResumer(schema1)
        resumer2 = SessionResumer(schema2)

        schema1.session_state_schema("sess_001", "user_001")
        context1, _ = resumer1.session_resume("sess_001_new", expert_domain="career")

        schema2.session_state_schema("sess_002", "user_002")
        context2, _ = resumer2.session_resume("sess_002_new", expert_domain="product")

        assert context1.expert_domain == "career"
        assert context2.expert_domain == "product"


class TestZeroPriorSessions:
    """Regression tests for issues-ly2.14.6: session init when user has 0 prior sessions."""

    def test_resume_with_no_prior_session_succeeds(self):
        """session_resume with no prior_session_id must return valid context, not crash."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)
        context, error = resumer.session_resume("brand_new_session")
        assert error is None
        assert context is not None
        assert context.expert_domain == "career"

    def test_new_session_has_new_session_resumption_context(self):
        """First-time session should have NEW_SESSION resumption context."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)
        context, _ = resumer.session_resume("first_session")
        awareness = context.context_awareness
        assert awareness["resumption_context"] == ResumptionContext.NEW_SESSION.value

    def test_new_session_has_no_prior_context(self):
        """First session must have None prior_context (no prior summary)."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)
        context, _ = resumer.session_resume("first_session_x")
        assert context.prior_context is None

    def test_new_session_has_entry_point(self):
        """Even without prior sessions, entry point suggestion must be returned."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)
        context, _ = resumer.session_resume("fresh_session_001")
        assert context.suggested_entry_point is not None
        assert len(context.suggested_entry_point) > 0


class TestCorruptedSessionFile:
    """Regression tests for issues-ly2.14.7: corrupted/unreadable session context file."""

    def test_resume_with_invalid_prior_session_id(self):
        """Resuming with a prior_session_id that doesn't exist returns error gracefully."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)
        context, error = resumer.session_resume(
            "new_session_001",
            prior_session_id="nonexistent_session_abc"
        )
        assert context is None
        assert error is not None
        assert "not found" in error.lower() or "nonexistent_session_abc" in error

    def test_state_schema_get_missing_session_returns_none(self):
        """get_state() for unknown session ID must return None, not raise."""
        schema = SessionStateSchema()
        result = schema.get_state("missing_session_id_xyz")
        assert result is None

    def test_resume_after_state_cleared_graceful(self):
        """Resuming after states cleared should not crash."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)
        # Create and then clear
        schema.session_state_schema("temp_session", "user_001")
        schema.states.clear()
        # Now try to resume it
        context, error = resumer.session_resume(
            "new_session_z",
            prior_session_id="temp_session"
        )
        assert context is None
        assert error is not None


class TestStaleSessionHandling:
    """Regression tests for issues-ly2.14.9: session resume when prior data is >7 days old."""

    def test_week_old_session_resume_no_crash(self):
        """Prior session 10 days old must not crash — returns valid context."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        schema.session_state_schema("old_sess_10d", "user_001")
        prior_state = schema.get_state("old_sess_10d")

        schema.add_turn(
            "old_sess_10d",
            user_message="test",
            assistant_response="response",
            sentiment="neutral",
            polarity=0.0,
            emotions={},
        )
        ten_days_ago = (datetime.now() - timedelta(days=10)).isoformat()
        prior_state.history[0].timestamp = ten_days_ago
        prior_state.context.last_activity = ten_days_ago

        context, error = resumer.session_resume(
            "resume_10d",
            prior_session_id="old_sess_10d"
        )
        assert error is None
        assert context is not None

    def test_week_old_session_classified_as_week_later(self):
        """Prior session 7+ days old → gap string contains 'week' → WEEK_LATER context."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        schema.session_state_schema("week_old_sess", "user_002")
        prior_state = schema.get_state("week_old_sess")

        schema.add_turn(
            "week_old_sess",
            user_message="test",
            assistant_response="response",
            sentiment="neutral",
            polarity=0.0,
            emotions={},
        )
        eight_days_ago = (datetime.now() - timedelta(days=8)).isoformat()
        prior_state.history[0].timestamp = eight_days_ago
        prior_state.context.last_activity = eight_days_ago

        context, error = resumer.session_resume(
            "resume_8d",
            prior_session_id="week_old_sess"
        )
        assert error is None
        awareness = context.context_awareness
        # 8 days → "1 week(s) ago" → contains "week" → WEEK_LATER
        assert awareness["resumption_context"] == ResumptionContext.WEEK_LATER.value

    def test_1_day_old_session_classified_as_next_day(self):
        """Prior session 1 day old → gap string "1 day ago" → NEXT_DAY context."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        schema.session_state_schema("day_old_sess", "user_003")
        prior_state = schema.get_state("day_old_sess")

        schema.add_turn(
            "day_old_sess",
            user_message="test",
            assistant_response="response",
            sentiment="neutral",
            polarity=0.0,
            emotions={},
        )
        one_day_ago = (datetime.now() - timedelta(days=1, hours=2)).isoformat()
        prior_state.history[0].timestamp = one_day_ago
        prior_state.context.last_activity = one_day_ago

        context, error = resumer.session_resume(
            "next_day_sess",
            prior_session_id="day_old_sess"
        )
        assert error is None
        awareness = context.context_awareness
        # 1 day → "1 day ago" contains "day" → NEXT_DAY
        assert awareness["resumption_context"] == ResumptionContext.NEXT_DAY.value


class TestVeryOldSessionHandling:
    """Regression tests for issues-7rs: session resume when >30 days old — should warn user."""

    def test_30_day_old_session_resume_no_crash(self):
        """Prior session 32 days old must not crash — returns valid context."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        schema.session_state_schema("old_30d_sess", "user_999")
        prior_state = schema.get_state("old_30d_sess")

        schema.add_turn(
            "old_30d_sess",
            user_message="old message",
            assistant_response="old response",
            sentiment="neutral",
            polarity=0.0,
            emotions={},
        )
        thirty_days_ago = (datetime.now() - timedelta(days=32)).isoformat()
        prior_state.history[0].timestamp = thirty_days_ago
        prior_state.context.last_activity = thirty_days_ago

        context, error = resumer.session_resume("new_after_30d", prior_session_id="old_30d_sess")
        assert error is None
        assert context is not None

    def test_30_day_old_session_classified_as_week_later(self):
        """32-day-old session → gap '4 week(s) ago' → contains 'week' → WEEK_LATER context."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        schema.session_state_schema("very_old_sess", "user_888")
        prior_state = schema.get_state("very_old_sess")

        schema.add_turn(
            "very_old_sess",
            user_message="test",
            assistant_response="resp",
            sentiment="neutral",
            polarity=0.0,
            emotions={},
        )
        thirty_two_days_ago = (datetime.now() - timedelta(days=32)).isoformat()
        prior_state.history[0].timestamp = thirty_two_days_ago
        prior_state.context.last_activity = thirty_two_days_ago

        context, error = resumer.session_resume(
            "resume_from_32d", prior_session_id="very_old_sess"
        )
        assert error is None
        awareness = context.context_awareness
        # 32 days → "4 week(s) ago" → contains "week" → WEEK_LATER
        assert awareness["resumption_context"] == ResumptionContext.WEEK_LATER.value

    def test_very_old_session_has_prior_context_summary(self):
        """Very old session resume must still provide prior context summary."""
        schema = SessionStateSchema()
        resumer = SessionResumer(schema)

        schema.session_state_schema("ancient_sess", "user_777")
        prior_state = schema.get_state("ancient_sess")

        schema.add_turn(
            "ancient_sess",
            user_message="I want to improve my career",
            assistant_response="Let's discuss it.",
            sentiment="positive",
            polarity=0.5,
            emotions={"excited": 0.7},
        )
        very_old = (datetime.now() - timedelta(days=60)).isoformat()
        prior_state.history[0].timestamp = very_old
        prior_state.context.last_activity = very_old

        context, error = resumer.session_resume(
            "new_after_60d", prior_session_id="ancient_sess"
        )
        assert error is None
        # Prior context should exist (not None) since prior session had history
        assert context.prior_context is not None
