"""
Tests for emotion trend tracking across sessions.

Tests cover:
- Recording session emotion snapshots
- Rising stress detection
- Persistent stress flagging
- Trend direction (rising/falling/stable)
- Alert generation
- Insufficient data handling
"""

import pytest
from datetime import datetime, timedelta

from life_brain.conversation.emotion_tracker import (
    EmotionTrendTracker,
    SessionEmotionSnapshot,
    EmotionTrend,
)


def _make_snapshot(session_id, stress_score, emotion="stressed", ts=None):
    """Helper to create a test snapshot."""
    return SessionEmotionSnapshot(
        session_id=session_id,
        timestamp=ts or datetime.now().isoformat(),
        primary_emotion=emotion,
        confidence=stress_score,
        stress_score=stress_score,
        all_emotions={"stressed": stress_score} if emotion == "stressed" else {},
    )


class TestRecordSession:
    """Test session recording."""

    def test_record_session_from_messages(self):
        tracker = EmotionTrendTracker()
        messages = ["I'm overwhelmed and stressed about deadlines"]
        snap = tracker.record_session("s1", messages)

        assert snap.session_id == "s1"
        assert snap.stress_score >= 0
        assert snap.primary_emotion in ["stressed", "neutral", "anxious", "frustrated"]

    def test_record_empty_session(self):
        tracker = EmotionTrendTracker()
        snap = tracker.record_session("s1", [])

        assert snap.session_id == "s1"
        assert snap.stress_score == 0.0
        assert snap.primary_emotion == "neutral"

    def test_multiple_sessions_stored(self):
        tracker = EmotionTrendTracker()
        tracker.record_session("s1", ["stressed about work"])
        tracker.record_session("s2", ["doing fine today"])

        assert len(tracker.session_snapshots) == 2

    def test_record_snapshot_directly(self):
        tracker = EmotionTrendTracker()
        snap = _make_snapshot("s1", 0.7)
        tracker.record_snapshot(snap)

        assert len(tracker.session_snapshots) == 1


class TestAnalyzeTrend:
    """Test trend analysis."""

    def test_insufficient_data_single_session(self):
        tracker = EmotionTrendTracker()
        tracker.record_snapshot(_make_snapshot("s1", 0.6))

        trend = tracker.analyze_trend()
        assert trend.trend_direction == "insufficient_data"
        assert trend.should_alert is False

    def test_insufficient_data_no_sessions(self):
        tracker = EmotionTrendTracker()
        trend = tracker.analyze_trend()
        assert trend.trend_direction == "insufficient_data"

    def test_rising_stress_detected(self):
        tracker = EmotionTrendTracker()
        # Stress going from 0.2 → 0.7 (delta = 0.5, above threshold of 0.2)
        tracker.record_snapshot(_make_snapshot("s1", 0.2))
        tracker.record_snapshot(_make_snapshot("s2", 0.4))
        tracker.record_snapshot(_make_snapshot("s3", 0.7))

        trend = tracker.analyze_trend()
        assert trend.is_rising_stress is True
        assert trend.trend_direction == "rising"
        assert trend.stress_score_delta > 0

    def test_falling_stress_detected(self):
        tracker = EmotionTrendTracker()
        tracker.record_snapshot(_make_snapshot("s1", 0.8))
        tracker.record_snapshot(_make_snapshot("s2", 0.5))
        tracker.record_snapshot(_make_snapshot("s3", 0.2))

        trend = tracker.analyze_trend()
        assert trend.trend_direction == "falling"
        assert trend.is_rising_stress is False

    def test_stable_stress(self):
        tracker = EmotionTrendTracker()
        tracker.record_snapshot(_make_snapshot("s1", 0.3))
        tracker.record_snapshot(_make_snapshot("s2", 0.32))
        tracker.record_snapshot(_make_snapshot("s3", 0.31))

        trend = tracker.analyze_trend()
        assert trend.trend_direction == "stable"

    def test_persistent_stress_alert(self):
        tracker = EmotionTrendTracker(high_stress_threshold=0.5)
        # 3 consecutive high-stress sessions
        tracker.record_snapshot(_make_snapshot("s1", 0.6))
        tracker.record_snapshot(_make_snapshot("s2", 0.7))
        tracker.record_snapshot(_make_snapshot("s3", 0.65))

        trend = tracker.analyze_trend()
        assert trend.consecutive_high_stress >= 3
        assert trend.should_alert is True
        assert trend.alert_message is not None

    def test_non_persistent_no_alert(self):
        tracker = EmotionTrendTracker(high_stress_threshold=0.5)
        # Only 1 high-stress session
        tracker.record_snapshot(_make_snapshot("s1", 0.2))
        tracker.record_snapshot(_make_snapshot("s2", 0.3))

        trend = tracker.analyze_trend()
        assert trend.consecutive_high_stress < 3

    def test_rising_stress_triggers_alert(self):
        tracker = EmotionTrendTracker()
        tracker.record_snapshot(_make_snapshot("s1", 0.1))
        tracker.record_snapshot(_make_snapshot("s2", 0.7))

        trend = tracker.analyze_trend()
        assert trend.should_alert is True
        assert trend.alert_message is not None

    def test_alert_message_is_string(self):
        tracker = EmotionTrendTracker()
        tracker.record_snapshot(_make_snapshot("s1", 0.1))
        tracker.record_snapshot(_make_snapshot("s2", 0.8))

        trend = tracker.analyze_trend()
        if trend.should_alert:
            assert isinstance(trend.alert_message, str)
            assert len(trend.alert_message) > 0

    def test_window_limits_sessions_analyzed(self):
        tracker = EmotionTrendTracker()
        for i in range(10):
            tracker.record_snapshot(_make_snapshot(f"s{i}", 0.3 + i * 0.05))

        trend = tracker.analyze_trend(window=5)
        assert trend.sessions_analyzed == 5

    def test_delta_accuracy(self):
        tracker = EmotionTrendTracker()
        tracker.record_snapshot(_make_snapshot("s1", 0.2))
        tracker.record_snapshot(_make_snapshot("s2", 0.6))

        trend = tracker.analyze_trend()
        assert trend.stress_score_delta == pytest.approx(0.4, abs=0.01)


class TestStressHistory:
    """Test stress history retrieval."""

    def test_history_empty(self):
        tracker = EmotionTrendTracker()
        history = tracker.get_stress_history()
        assert history == []

    def test_history_contains_all_sessions(self):
        tracker = EmotionTrendTracker()
        tracker.record_snapshot(_make_snapshot("s1", 0.3))
        tracker.record_snapshot(_make_snapshot("s2", 0.6))

        history = tracker.get_stress_history()
        assert len(history) == 2

    def test_history_has_required_fields(self):
        tracker = EmotionTrendTracker()
        tracker.record_snapshot(_make_snapshot("s1", 0.5))

        history = tracker.get_stress_history()
        entry = history[0]
        assert "session_id" in entry
        assert "stress_score" in entry
        assert "primary_emotion" in entry
        assert "timestamp" in entry
