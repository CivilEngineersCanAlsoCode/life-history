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
