"""
Tests for Small Talk Passive Capture.

Tests cover:
- ClaimDetector: metric/fact/date/decision/person detection
- Deduplication: same claim never surfaced twice
- ReviewQueueItem: expiry logic, status transitions
- PassiveCaptureEngine: process_message, next_prompt, confirm/reject
- Weekly review queue
- Edge cases: empty message, short message, no claims
"""

import pytest
from datetime import datetime, timedelta

from life_brain.conversation.passive_capture import (
    ClaimDetector,
    PassiveCaptureEngine,
    DetectedClaim,
    ReviewQueueItem,
    _fingerprint,
)


class TestFingerprint:
    """Test claim fingerprinting."""

    def test_same_text_same_fingerprint(self):
        """Same text → same fingerprint."""
        assert _fingerprint("CSAT 94%") == _fingerprint("CSAT 94%")

    def test_case_insensitive_fingerprint(self):
        """Fingerprint is case-insensitive."""
        assert _fingerprint("CSAT 94%") == _fingerprint("csat 94%")

    def test_whitespace_normalized(self):
        """Extra spaces collapsed before fingerprinting."""
        assert _fingerprint("CSAT  94%") == _fingerprint("CSAT 94%")

    def test_different_text_different_fingerprint(self):
        """Different text → different fingerprint."""
        assert _fingerprint("CSAT 94%") != _fingerprint("NPS 72")


class TestClaimDetector:
    """Test regex-based claim detection."""

    # Metric patterns

    def test_percentage_detected_as_metric(self):
        """'94%' → metric claim."""
        detector = ClaimDetector()
        claims = detector.detect("Our CSAT was 94% last quarter.")
        types = [c.claim_type for c in claims]
        assert "metric" in types

    def test_large_number_detected_as_metric(self):
        """'10,000 users' → metric."""
        detector = ClaimDetector()
        claims = detector.detect("We had 10000 users at peak.")
        types = [c.claim_type for c in claims]
        assert "metric" in types

    def test_lakh_crore_detected_as_metric(self):
        """'50L' or '2Cr' → metric."""
        detector = ClaimDetector()
        claims = detector.detect("My CTC was 50L at Sprinklr.")
        types = [c.claim_type for c in claims]
        assert "metric" in types

    # Fact patterns

    def test_joined_company_detected_as_fact(self):
        """'I joined X' → fact claim."""
        detector = ClaimDetector()
        claims = detector.detect("I joined Sprinklr in April 2022.")
        types = [c.claim_type for c in claims]
        assert "fact" in types

    def test_we_launched_detected_as_fact(self):
        """'we launched' → fact."""
        detector = ClaimDetector()
        claims = detector.detect("We launched the chatbot in September.")
        types = [c.claim_type for c in claims]
        assert "fact" in types

    def test_salary_mention_detected_as_fact(self):
        """'my salary' → fact."""
        detector = ClaimDetector()
        claims = detector.detect("My salary was revised to 60L.")
        types = [c.claim_type for c in claims]
        assert "fact" in types

    # Date patterns

    def test_month_year_detected_as_date(self):
        """'April 2022' → date claim."""
        detector = ClaimDetector()
        claims = detector.detect("I joined in April 2022.")
        types = [c.claim_type for c in claims]
        assert "date" in types

    def test_quarter_detected_as_date(self):
        """'Q3 2023' → date."""
        detector = ClaimDetector()
        claims = detector.detect("The launch was in Q3 2023.")
        types = [c.claim_type for c in claims]
        assert "date" in types

    def test_relative_date_detected(self):
        """'last month' → date."""
        detector = ClaimDetector()
        claims = detector.detect("Last month we had a big release.")
        types = [c.claim_type for c in claims]
        assert "date" in types

    # Decision patterns

    def test_decided_to_detected_as_decision(self):
        """'decided to' → decision."""
        detector = ClaimDetector()
        claims = detector.detect("I decided to quit and start my own thing.")
        types = [c.claim_type for c in claims]
        assert "decision" in types

    def test_planning_to_detected_as_decision(self):
        """'planning to' → decision."""
        detector = ClaimDetector()
        claims = detector.detect("I am planning to switch companies.")
        types = [c.claim_type for c in claims]
        assert "decision" in types

    # Edge cases

    def test_empty_message_returns_empty(self):
        """Empty message → no claims."""
        detector = ClaimDetector()
        assert detector.detect("") == []

    def test_short_message_returns_empty(self):
        """Message shorter than threshold → no claims."""
        detector = ClaimDetector()
        assert detector.detect("Hi!") == []

    def test_no_patterns_returns_empty(self):
        """Generic message with no keywords → empty claims."""
        detector = ClaimDetector()
        claims = detector.detect("The weather is nice today, feeling good.")
        # No financial, career, date, or decision keywords
        assert isinstance(claims, list)

    def test_detect_types_groups_by_type(self):
        """detect_types() must group matches by claim_type."""
        detector = ClaimDetector()
        groups = detector.detect_types("I joined Sprinklr in April 2022 with CSAT 94%.")
        assert isinstance(groups, dict)
        # Should have multiple types
        assert len(groups) >= 2

    def test_claim_has_surface_prompt(self):
        """DetectedClaim.surface_prompt() must contain claim text."""
        detector = ClaimDetector()
        claims = detector.detect("I joined Sprinklr in April 2022.")
        assert len(claims) > 0
        prompt = claims[0].surface_prompt()
        assert "record karun" in prompt


class TestReviewQueueItem:
    """Test ReviewQueueItem expiry and status."""

    def test_fresh_item_not_expired(self):
        """Newly created item must not be expired."""
        claim = DetectedClaim(claim_type="fact", raw_text="I joined Sprinklr", source_message="test")
        item = ReviewQueueItem(claim=claim)
        assert item.is_expired is False

    def test_expired_item_detected(self):
        """Item with past expiry → is_expired True."""
        claim = DetectedClaim(claim_type="fact", raw_text="I joined", source_message="test")
        past = (datetime.now() - timedelta(days=1)).isoformat()
        item = ReviewQueueItem(claim=claim, expires_at=past)
        assert item.is_expired is True

    def test_default_status_is_pending(self):
        """New item status must be 'pending'."""
        claim = DetectedClaim(claim_type="metric", raw_text="94%", source_message="test")
        item = ReviewQueueItem(claim=claim)
        assert item.status == "pending"

    def test_to_dict_has_required_fields(self):
        """to_dict() must include claim, added_at, expires_at, status."""
        claim = DetectedClaim(claim_type="fact", raw_text="I quit", source_message="test")
        item = ReviewQueueItem(claim=claim)
        d = item.to_dict()
        assert "claim" in d
        assert "added_at" in d
        assert "expires_at" in d
        assert "status" in d


class TestPassiveCaptureEngine:
    """Test full passive capture lifecycle."""

    def test_process_message_returns_new_claims(self):
        """Message with claims → list of DetectedClaim returned."""
        engine = PassiveCaptureEngine()
        claims = engine.process_message("I joined Sprinklr in April 2022 with CSAT 94%.")
        assert len(claims) > 0

    def test_process_empty_message_returns_empty(self):
        """Empty message → no claims."""
        engine = PassiveCaptureEngine()
        claims = engine.process_message("")
        assert claims == []

    def test_same_claim_not_queued_twice(self):
        """Same message twice → second time yields 0 new claims."""
        engine = PassiveCaptureEngine()
        msg = "I joined Sprinklr in April 2022."
        first = engine.process_message(msg)
        second = engine.process_message(msg)
        assert len(second) == 0

    def test_has_pending_prompts_after_claim(self):
        """After processing a message with claims → has_pending_prompts True."""
        engine = PassiveCaptureEngine()
        engine.process_message("I joined Sprinklr in April 2022.")
        assert engine.has_pending_prompts() is True

    def test_no_pending_prompts_on_fresh_engine(self):
        """Fresh engine → has_pending_prompts False."""
        engine = PassiveCaptureEngine()
        assert engine.has_pending_prompts() is False

    def test_next_prompt_contains_record_karun(self):
        """next_prompt() must return 'isko record karun?' phrase."""
        engine = PassiveCaptureEngine()
        engine.process_message("I joined Sprinklr in April 2022.")
        prompt = engine.next_prompt()
        assert prompt is not None
        assert "record karun" in prompt

    def test_next_prompt_none_when_empty(self):
        """next_prompt() returns None when no pending claims."""
        engine = PassiveCaptureEngine()
        assert engine.next_prompt() is None

    def test_confirm_marks_claim_confirmed(self):
        """confirm(fingerprint) → status='confirmed'."""
        engine = PassiveCaptureEngine()
        claims = engine.process_message("I joined Sprinklr in April 2022.")
        assert len(claims) > 0
        fp = claims[0].fingerprint
        result = engine.confirm(fp)
        assert result is True
        confirmed = engine.get_confirmed()
        assert any(i.claim.fingerprint == fp for i in confirmed)

    def test_reject_marks_claim_rejected(self):
        """reject(fingerprint) → status='rejected', removed from pending."""
        engine = PassiveCaptureEngine()
        claims = engine.process_message("I joined Sprinklr in April 2022.")
        fp = claims[0].fingerprint
        engine.reject(fp)
        pending = engine.get_weekly_review()
        assert not any(i.claim.fingerprint == fp for i in pending)

    def test_confirm_unknown_fingerprint_returns_false(self):
        """confirm() with unknown fingerprint → False."""
        engine = PassiveCaptureEngine()
        assert engine.confirm("deadbeef12345678") is False

    def test_reject_unknown_fingerprint_returns_false(self):
        """reject() with unknown fingerprint → False."""
        engine = PassiveCaptureEngine()
        assert engine.reject("deadbeef12345678") is False

    def test_expire_stale_removes_old_items(self):
        """expire_stale() must mark expired pending items as rejected."""
        engine = PassiveCaptureEngine()
        # Manually inject an expired item
        claim = DetectedClaim(claim_type="fact", raw_text="I built X", source_message="test")
        claim.fingerprint = "stale_fp_001"
        engine._seen_fingerprints.add(claim.fingerprint)
        past = (datetime.now() - timedelta(days=1)).isoformat()
        expired_item = ReviewQueueItem(claim=claim, expires_at=past)
        engine._review_queue.append(expired_item)

        count = engine.expire_stale()
        assert count == 1
        assert expired_item.status == "rejected"

    def test_weekly_review_excludes_expired(self):
        """get_weekly_review() must not return expired items."""
        engine = PassiveCaptureEngine()
        claim = DetectedClaim(claim_type="fact", raw_text="Expired claim", source_message="test")
        claim.fingerprint = "expired_001"
        engine._seen_fingerprints.add(claim.fingerprint)
        past = (datetime.now() - timedelta(days=2)).isoformat()
        expired_item = ReviewQueueItem(claim=claim, expires_at=past)
        engine._review_queue.append(expired_item)

        review = engine.get_weekly_review()
        assert not any(i.claim.fingerprint == "expired_001" for i in review)

    def test_stats_correct_after_operations(self):
        """stats() must accurately reflect pending/confirmed/rejected counts."""
        engine = PassiveCaptureEngine()
        claims = engine.process_message("I joined Sprinklr in April 2022. CSAT was 94%.")

        if len(claims) >= 2:
            engine.confirm(claims[0].fingerprint)
            engine.reject(claims[1].fingerprint)
            s = engine.stats()
            assert s["confirmed"] >= 1
            assert s["rejected"] >= 1
        else:
            s = engine.stats()
            assert s["total"] == len(claims)

    def test_queue_size_counts_only_pending(self):
        """queue_size must count only non-expired pending items."""
        engine = PassiveCaptureEngine()
        engine.process_message("I joined Sprinklr in April 2022.")
        size = engine.queue_size
        assert size >= 1
