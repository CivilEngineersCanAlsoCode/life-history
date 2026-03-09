"""Test suite for trend detector."""

import pytest
from life_brain.conversation.trend_detector import (
    TrendDetector,
    SessionSentiment,
    TrendDirection,
    SessionMoodPattern,
)


class TestSessionSentiment:
    """Test SessionSentiment dataclass."""

    def test_create_sentiment(self):
        """Test creating session sentiment."""
        sentiment = SessionSentiment(
            session_id="sess_001",
            avg_polarity=0.7,
            sentiment_distribution={"positive": 5, "neutral": 1},
            emotion_profile={"joy": 0.8},
        )

        assert sentiment.session_id == "sess_001"
        assert sentiment.avg_polarity == 0.7


class TestTrendDetector:
    """Test TrendDetector."""

    def test_create_detector(self):
        """Test creating trend detector."""
        detector = TrendDetector()
        assert len(detector.session_sentiments) == 0

    def test_trend_detector_record(self):
        """Test recording session sentiment."""
        detector = TrendDetector()

        sentiment = detector.trend_detector(
            "sess_001",
            avg_polarity=0.8,
            sentiment_distribution={"positive": 5},
            emotion_profile={"joy": 0.8},
            messages_count=5,
        )

        assert sentiment.session_id == "sess_001"
        assert len(detector.session_sentiments) == 1

    def test_analyze_trend_single_session(self):
        """Test analyzing trend from single session."""
        detector = TrendDetector()

        detector.trend_detector(
            "sess_001",
            avg_polarity=0.7,
            sentiment_distribution={"positive": 5},
            emotion_profile={"joy": 0.8},
        )

        trend = detector.analyze_trend(period="session")

        assert trend.sessions_analyzed == 1
        assert trend.direction == TrendDirection.STABLE

    def test_analyze_trend_improving(self):
        """Test detecting improving trend."""
        detector = TrendDetector()

        detector.trend_detector("sess_001", 0.2, {}, {})
        detector.trend_detector("sess_002", 0.5, {}, {})
        detector.trend_detector("sess_003", 0.8, {}, {})

        trend = detector.analyze_trend(window_size=3)

        assert trend.polarity_change >= 0

    def test_analyze_trend_declining(self):
        """Test detecting declining trend."""
        detector = TrendDetector()

        detector.trend_detector("sess_001", 0.8, {}, {})
        detector.trend_detector("sess_002", 0.5, {}, {})
        detector.trend_detector("sess_003", 0.2, {}, {})

        trend = detector.analyze_trend(window_size=3)

        assert trend.polarity_change <= 0

    def test_analyze_trend_stable(self):
        """Test detecting stable trend."""
        detector = TrendDetector()

        for i in range(3):
            detector.trend_detector(f"sess_{i}", 0.5, {}, {})

        trend = detector.analyze_trend()

        assert trend.direction == TrendDirection.STABLE

    def test_get_recent_trends(self):
        """Test getting recent trends."""
        detector = TrendDetector()

        for i in range(5):
            detector.trend_detector(f"sess_{i}", 0.2 + i * 0.1, {}, {})

        trends = detector.get_recent_trends(num_periods=2)

        assert len(trends) <= 2

    def test_get_overall_emotional_arc(self):
        """Test getting overall emotional arc."""
        detector = TrendDetector()

        detector.trend_detector("sess_001", 0.2, {}, {})
        detector.trend_detector("sess_002", 0.5, {}, {})
        detector.trend_detector("sess_003", 0.8, {}, {})

        arc = detector.get_overall_emotional_arc()

        assert arc["arc"] == "rising"
        assert arc["peak_polarity"] == 0.8
        assert arc["sessions_tracked"] == 3

    def test_detect_mood_shift_significant(self):
        """Test detecting significant mood shift."""
        detector = TrendDetector()

        detector.trend_detector("sess_001", 0.8, {}, {})
        detector.trend_detector("sess_002", -0.6, {}, {})

        shift = detector.detect_mood_shift(threshold=0.5)

        assert shift is not None
        assert shift[0] == "positive"
        assert shift[1] == "negative"

    def test_detect_mood_shift_minor(self):
        """Test not detecting minor mood shift."""
        detector = TrendDetector()

        detector.trend_detector("sess_001", 0.8, {}, {})
        detector.trend_detector("sess_002", 0.7, {}, {})

        shift = detector.detect_mood_shift(threshold=0.5)

        assert shift is None

    def test_export_session_history(self):
        """Test exporting session history."""
        detector = TrendDetector()

        detector.trend_detector("sess_001", 0.5, {}, {"joy": 0.7})
        detector.trend_detector("sess_002", 0.8, {}, {"joy": 0.9})

        history = detector.export_session_history()

        assert len(history) == 2
        assert history[0]["session_id"] == "sess_001"

    def test_classify_mood_pattern_upbeat(self):
        """Test classifying upbeat mood."""
        detector = TrendDetector()

        detector.trend_detector("sess_001", 0.8, {}, {})
        detector.trend_detector("sess_002", 0.7, {}, {})

        trend = detector.analyze_trend()

        assert trend.mood_pattern == SessionMoodPattern.UPBEAT

    def test_volatility_calculation(self):
        """Test volatility calculation."""
        detector = TrendDetector()

        # Stable
        for _ in range(3):
            detector.trend_detector("sess", 0.5, {}, {})

        stable_trend = detector.analyze_trend(window_size=3)

        # Volatile
        detector2 = TrendDetector()
        detector2.trend_detector("sess_1", 0.9, {}, {})
        detector2.trend_detector("sess_2", 0.1, {}, {})
        detector2.trend_detector("sess_3", 0.8, {}, {})

        volatile_trend = detector2.analyze_trend(window_size=3)

        assert stable_trend.volatility < volatile_trend.volatility

    def test_complex_trend_analysis(self):
        """Test complex trend analysis workflow."""
        detector = TrendDetector()

        # Simulate session history
        polarities = [0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.75, 0.8]

        for i, polarity in enumerate(polarities):
            detector.trend_detector(
                f"sess_{i:03d}",
                polarity,
                {},
                {"joy": polarity},
                messages_count=5 + i,
            )

        # Get overall arc
        arc = detector.get_overall_emotional_arc()
        assert arc["arc"] == "rising"
        assert arc["overall_trend"] == "generally_positive"

        # Get recent trends
        trends = detector.get_recent_trends(num_periods=2)
        assert len(trends) > 0

        # Check for mood shifts
        last_shift = detector.detect_mood_shift(threshold=0.3)
        # Should not detect big shift between last 2 (0.8 vs 0.75)
        assert last_shift is None
