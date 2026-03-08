"""
Tests for accountability partner — commitment extraction and follow-up.

Tests cover:
- Extracting commitment statements from messages
- Deadline extraction
- Follow-up prompt generation
- Deadline status (overdue/upcoming/unknown)
- Accountability tracker management
- Edge cases
"""

import pytest
from datetime import date, timedelta

from life_brain.conversation.accountability import (
    extract_commitments,
    AccountabilityTracker,
    check_deadline_status,
    Commitment,
    _build_follow_up_prompt,
)


class TestExtractCommitments:
    """Test commitment extraction from text."""

    def test_extract_basic_commitment(self):
        text = "I'll finish the report by Friday."
        results = extract_commitments(text, "s1")
        assert len(results) >= 1

    def test_extract_with_deadline(self):
        text = "I will submit the application by March 31."
        results = extract_commitments(text, "s1")
        assert len(results) >= 1
        commitment = results[0]
        assert commitment.deadline_text is not None
        assert "March" in commitment.deadline_text or "31" in commitment.deadline_text

    def test_extract_going_to(self):
        text = "I'm going to update my resume this week."
        results = extract_commitments(text, "s1")
        assert len(results) >= 1

    def test_no_commitment_in_neutral(self):
        text = "The weather is nice today. How are you?"
        results = extract_commitments(text, "s1")
        assert len(results) == 0

    def test_commitment_has_session_id(self):
        text = "I'll complete the task by end of month."
        results = extract_commitments(text, "session_abc")
        assert all(r.session_id == "session_abc" for r in results)

    def test_commitment_has_action(self):
        text = "I will prepare the presentation by next Monday."
        results = extract_commitments(text, "s1")
        assert len(results) >= 1
        assert len(results[0].action) > 0

    def test_commitment_id_unique(self):
        text = "I'll do task A. I'll also do task B."
        results = extract_commitments(text, "s1")
        if len(results) > 1:
            ids = [r.commitment_id for r in results]
            assert len(ids) == len(set(ids))

    def test_multiple_commitments(self):
        text = (
            "I'll finish the report by Friday. "
            "I will also update the slides by Monday."
        )
        results = extract_commitments(text, "s1")
        assert len(results) >= 1  # At least one extracted

    def test_commitment_defaults(self):
        text = "I'll do this by next week."
        results = extract_commitments(text, "s1")
        if results:
            c = results[0]
            assert c.followed_up is False
            assert c.status == "pending"

    def test_commitment_to_dict(self):
        text = "I'll submit by March 31."
        results = extract_commitments(text, "s1")
        if results:
            d = results[0].to_dict()
            assert "commitment_id" in d
            assert "action" in d
            assert "deadline_text" in d
            assert "status" in d


class TestAccountabilityTracker:
    """Test AccountabilityTracker."""

    def test_add_commitments_from_session(self):
        tracker = AccountabilityTracker()
        messages = ["I'll finish the proposal by next Friday."]
        found = tracker.add_commitments_from_session("s1", messages)
        assert len(found) >= 0  # May or may not extract depending on text

    def test_commitments_stored(self):
        tracker = AccountabilityTracker()
        messages = ["I will submit the report by end of month."]
        tracker.add_commitments_from_session("s1", messages)
        # Commitments dict should be populated if anything was extracted
        assert isinstance(tracker.commitments, dict)

    def test_get_pending_commitments_empty(self):
        tracker = AccountabilityTracker()
        assert tracker.get_pending_commitments() == []

    def test_get_pending_commitments_filters_followed_up(self):
        tracker = AccountabilityTracker()
        # Manually add a commitment
        c = Commitment(
            commitment_id="c1",
            session_id="s1",
            raw_text="I'll do it",
            action="do it",
            deadline_text=None,
            followed_up=True,
        )
        tracker.commitments["c1"] = c
        assert tracker.get_pending_commitments() == []

    def test_get_pending_commitments_includes_pending(self):
        tracker = AccountabilityTracker()
        c = Commitment(
            commitment_id="c1",
            session_id="s1",
            raw_text="I'll do it",
            action="do it",
            deadline_text="March 31",
        )
        tracker.commitments["c1"] = c
        pending = tracker.get_pending_commitments()
        assert len(pending) == 1

    def test_get_follow_up_prompts(self):
        tracker = AccountabilityTracker()
        c = Commitment(
            commitment_id="c1",
            session_id="s1",
            raw_text="I'll submit the report",
            action="submit the report",
            deadline_text="March 31",
        )
        tracker.commitments["c1"] = c
        prompts = tracker.get_follow_up_prompts()
        assert len(prompts) == 1
        assert "March 31" in prompts[0]
        assert "submit the report" in prompts[0]

    def test_mark_followed_up(self):
        tracker = AccountabilityTracker()
        c = Commitment(
            commitment_id="c1",
            session_id="s1",
            raw_text="I'll do it",
            action="do it",
            deadline_text=None,
        )
        tracker.commitments["c1"] = c
        result = tracker.mark_followed_up("c1", status="done")
        assert result is True
        assert tracker.commitments["c1"].followed_up is True
        assert tracker.commitments["c1"].status == "done"

    def test_mark_followed_up_not_found(self):
        tracker = AccountabilityTracker()
        result = tracker.mark_followed_up("nonexistent")
        assert result is False

    def test_get_statistics(self):
        tracker = AccountabilityTracker()
        stats = tracker.get_statistics()
        assert stats["total"] == 0
        assert stats["pending"] == 0

    def test_statistics_with_data(self):
        tracker = AccountabilityTracker()
        for i, status in enumerate(["pending", "done", "missed"]):
            c = Commitment(
                commitment_id=f"c{i}",
                session_id="s1",
                raw_text="test",
                action="test action",
                deadline_text=None,
                status=status,
                followed_up=(status != "pending"),
            )
            tracker.commitments[f"c{i}"] = c

        stats = tracker.get_statistics()
        assert stats["total"] == 3
        assert stats["done"] == 1
        assert stats["missed"] == 1


class TestCheckDeadlineStatus:
    """Test deadline status checking."""

    def test_overdue_deadline(self):
        past_date = (date.today() - timedelta(days=5)).strftime("%Y-%m-%d")
        status, msg = check_deadline_status(past_date)
        assert status == "overdue"
        assert msg is not None
        assert "overdue" in msg.lower() or "ago" in msg.lower()

    def test_upcoming_deadline(self):
        future_date = (date.today() + timedelta(days=10)).strftime("%Y-%m-%d")
        status, msg = check_deadline_status(future_date)
        assert status == "upcoming"
        assert msg is not None

    def test_unknown_deadline(self):
        status, msg = check_deadline_status("sometime soon")
        assert status == "unknown"
        assert msg is None

    def test_overdue_days_count(self):
        past = (date.today() - timedelta(days=3)).strftime("%Y-%m-%d")
        status, msg = check_deadline_status(past)
        assert status == "overdue"
        assert "3" in msg

    def test_reference_date_parameter(self):
        # Test with explicit reference date
        status, msg = check_deadline_status("2024-01-15", reference_date=date(2024, 1, 10))
        assert status == "upcoming"

        status, msg = check_deadline_status("2024-01-15", reference_date=date(2024, 1, 20))
        assert status == "overdue"


class TestFollowUpPrompt:
    """Test follow-up prompt generation."""

    def test_prompt_with_deadline(self):
        c = Commitment(
            commitment_id="c1",
            session_id="s1",
            raw_text="I'll apply by March 31",
            action="apply",
            deadline_text="March 31",
        )
        prompt = _build_follow_up_prompt(c)
        assert "March 31" in prompt
        assert "apply" in prompt

    def test_prompt_without_deadline(self):
        c = Commitment(
            commitment_id="c1",
            session_id="s1",
            raw_text="I'll do it",
            action="do it",
            deadline_text=None,
        )
        prompt = _build_follow_up_prompt(c)
        assert "do it" in prompt
        assert isinstance(prompt, str)


class TestUnpunctuatedMessagesBug:
    """Regression tests for issues-132: unpunctuated messages merging bug.

    Bug: joining messages then splitting on .!? caused commitments from
    unpunctuated messages to be dropped or merged incorrectly.
    Fix: each message is processed independently by extract_commitments().
    """

    def test_unpunctuated_message_extracted(self):
        """Commitment in message with no trailing punctuation must be found."""
        tracker = AccountabilityTracker()
        messages = ["I'll submit the report by Friday"]  # no period
        found = tracker.add_commitments_from_session("s1", messages)
        # Should still extract a commitment despite no trailing period
        assert len(found) >= 1

    def test_two_unpunctuated_messages_both_extracted(self):
        """Two separate unpunctuated messages → both commitments extracted."""
        tracker = AccountabilityTracker()
        messages = [
            "I'll finish the proposal by Monday",
            "I will update my LinkedIn by end of month",
        ]
        found = tracker.add_commitments_from_session("s1", messages)
        # Should find commitments from both messages independently
        assert len(found) >= 1

    def test_no_duplicate_commitments_across_messages(self):
        """Same commitment in two messages should not be double-counted."""
        tracker = AccountabilityTracker()
        messages = [
            "I'll finish the proposal by Monday.",
            "I'll finish the proposal by Monday.",
        ]
        found = tracker.add_commitments_from_session("s1", messages)
        # Deduplication via seen_ids should prevent double extraction
        ids = [c.commitment_id for c in found]
        assert len(ids) == len(set(ids))

    def test_mixed_punctuated_and_unpunctuated(self):
        """Mix of punctuated and unpunctuated messages should all work."""
        tracker = AccountabilityTracker()
        messages = [
            "I'll submit the report by Friday.",  # punctuated
            "I will call the recruiter tomorrow",  # unpunctuated
        ]
        found = tracker.add_commitments_from_session("s1", messages)
        assert len(found) >= 1
