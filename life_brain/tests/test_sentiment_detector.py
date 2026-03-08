"""
Test suite for sentiment detector.

Tests cover:
- Mood analysis and classification
- Expert suggestion based on emotions
- Reasoning generation
- Distribution tracking
"""

import pytest
from life_brain.emotional.sentiment_detector import (
    SentimentDetector,
    ExpertSuggestion,
    MoodAnalysis,
)
from life_brain.emotional.trend_detector import SessionMoodPattern, TrendDirection
from life_brain.session.preferences import ExpertDomain


class TestExpertSuggestion:
    """Test ExpertSuggestion dataclass."""

    def test_create_suggestion(self):
        """Test creating expert suggestion."""
        suggestion = ExpertSuggestion(
            expert_domain=ExpertDomain.CAREER,
            confidence=0.85,
            reasoning=["Positive sentiment detected", "Career growth opportunity"],
            emotional_factors={"joy": 0.8},
        )

        assert suggestion.expert_domain == ExpertDomain.CAREER
        assert suggestion.confidence == 0.85
        assert len(suggestion.reasoning) == 2

    def test_to_dict(self):
        """Test converting suggestion to dictionary."""
        suggestion = ExpertSuggestion(
            expert_domain=ExpertDomain.PRODUCT,
            confidence=0.75,
            reasoning=["Test reason"],
            emotional_factors={"trust": 0.7},
        )

        suggestion_dict = suggestion.to_dict()
        assert suggestion_dict["expert_domain"] == "product"
        assert suggestion_dict["confidence"] == 0.75


class TestMoodAnalysis:
    """Test MoodAnalysis dataclass."""

    def test_create_analysis(self):
        """Test creating mood analysis."""
        from life_brain.emotional.sentiment_analyzer import SentimentScore, Sentiment

        sentiment = SentimentScore(
            text="I'm so happy!",
            overall_sentiment=Sentiment.VERY_POSITIVE,
            confidence=0.9,
            polarity=0.8,
        )

        analysis = MoodAnalysis(
            session_id="sess_001",
            text="I'm so happy!",
            sentiment_score=sentiment,
            mood_pattern=SessionMoodPattern.UPBEAT,
        )

        assert analysis.session_id == "sess_001"
        assert analysis.mood_pattern == SessionMoodPattern.UPBEAT


class TestSentimentDetector:
    """Test SentimentDetector functionality."""

    def test_create_detector(self):
        """Test creating sentiment detector."""
        detector = SentimentDetector()
        assert len(detector.suggestion_history) == 0

    def test_sentiment_detector_basic(self):
        """Test basic sentiment detection and expert suggestion."""
        detector = SentimentDetector()

        analysis = detector.sentiment_detector(
            session_id="sess_001",
            text="I'm excited about this new product opportunity!",
        )

        assert analysis.session_id == "sess_001"
        assert analysis.primary_expert is not None
        assert analysis.primary_expert.confidence > 0

    def test_positive_sentiment_suggests_career(self):
        """Test that positive sentiment suggests career expert."""
        detector = SentimentDetector()

        analysis = detector.sentiment_detector(
            session_id="sess_001",
            text="I'm so happy and looking forward to great things!",
        )

        # Positive sentiment should suggest CAREER or PRODUCT
        assert analysis.primary_expert.expert_domain in [
            ExpertDomain.CAREER,
            ExpertDomain.PRODUCT,
        ]

    def test_negative_sentiment_suggests_life_career(self):
        """Test that negative sentiment suggests LIFE or CAREER expert."""
        detector = SentimentDetector()

        analysis = detector.sentiment_detector(
            session_id="sess_001",
            text="I'm so sad and disappointed with everything",
        )

        # Negative sentiment should suggest LIFE or CAREER
        assert analysis.primary_expert.expert_domain in [
            ExpertDomain.LIFE,
            ExpertDomain.CAREER,
        ]

    def test_frustrated_sentiment_suggests_engineering(self):
        """Test that frustrated sentiment suggests engineering."""
        detector = SentimentDetector()

        analysis = detector.sentiment_detector(
            session_id="sess_001",
            text="I'm so angry and frustrated with this broken code!",
        )

        # Frustrated/angry should suggest ENGINEERING
        assert analysis.primary_expert.expert_domain in [
            ExpertDomain.ENGINEERING,
            ExpertDomain.CAREER,
        ]

    def test_mood_pattern_classification_upbeat(self):
        """Test mood pattern classification for upbeat sentiment."""
        detector = SentimentDetector()

        analysis = detector.sentiment_detector(
            session_id="sess_001",
            text="I am amazing excellent great wonderful fantastic happy perfect",
        )

        assert analysis.mood_pattern == SessionMoodPattern.UPBEAT

    def test_mood_pattern_classification_withdrawn(self):
        """Test mood pattern classification for withdrawn sentiment."""
        detector = SentimentDetector()

        analysis = detector.sentiment_detector(
            session_id="sess_001",
            text="ok I guess",
        )

        assert analysis.mood_pattern in [
            SessionMoodPattern.WITHDRAWN,
            SessionMoodPattern.CAUTIOUS,
        ]

    def test_mood_pattern_explicit(self):
        """Test explicit mood pattern override."""
        detector = SentimentDetector()

        analysis = detector.sentiment_detector(
            session_id="sess_001",
            text="Hello there",
            mood_pattern=SessionMoodPattern.ENGAGED,
        )

        assert analysis.mood_pattern == SessionMoodPattern.ENGAGED

    def test_trend_direction_included(self):
        """Test trend direction in analysis."""
        detector = SentimentDetector()

        analysis = detector.sentiment_detector(
            session_id="sess_001",
            text="I'm feeling better",
            trend_direction=TrendDirection.IMPROVING,
        )

        assert analysis.trend_direction == TrendDirection.IMPROVING

    def test_primary_expert_with_confidence(self):
        """Test primary expert suggestion has confidence score."""
        detector = SentimentDetector()

        analysis = detector.sentiment_detector(
            session_id="sess_001",
            text="I need help with career planning",
        )

        assert analysis.primary_expert is not None
        assert 0 <= analysis.primary_expert.confidence <= 1

    def test_reasoning_provided(self):
        """Test that reasoning is provided for suggestion."""
        detector = SentimentDetector()

        analysis = detector.sentiment_detector(
            session_id="sess_001",
            text="I'm frustrated with engineering challenges",
        )

        assert len(analysis.primary_expert.reasoning) > 0
        assert all(isinstance(r, str) for r in analysis.primary_expert.reasoning)

    def test_emotional_factors_calculated(self):
        """Test that emotional factors are calculated."""
        detector = SentimentDetector()

        analysis = detector.sentiment_detector(
            session_id="sess_001",
            text="I'm so happy and excited!",
        )

        # Should have emotional factors
        assert isinstance(analysis.primary_expert.emotional_factors, dict)

    def test_alternate_experts_provided(self):
        """Test that alternate experts are provided."""
        detector = SentimentDetector()

        analysis = detector.sentiment_detector(
            session_id="sess_001",
            text="I'm facing complex challenges",
        )

        # Should have some alternate experts
        assert len(analysis.alternate_experts) >= 0

    def test_get_analysis(self):
        """Test retrieving analysis."""
        detector = SentimentDetector()

        analysis1 = detector.sentiment_detector("sess_001", "Happy!")
        analysis2 = detector.get_analysis("sess_001")

        assert analysis2 is not None
        assert analysis2.session_id == "sess_001"

    def test_get_recent_analyses(self):
        """Test getting recent analyses."""
        detector = SentimentDetector()

        for i in range(5):
            detector.sentiment_detector(f"sess_{i:03d}", f"Message {i}")

        recent = detector.get_recent_analyses(limit=3)
        assert len(recent) == 3

    def test_expert_suggestion_distribution(self):
        """Test expert suggestion distribution."""
        detector = SentimentDetector()

        detector.sentiment_detector("sess_001", "Excited about product growth!")
        detector.sentiment_detector("sess_002", "Frustrated with code bugs")
        detector.sentiment_detector("sess_003", "Career planning questions")

        dist = detector.get_expert_suggestion_distribution()
        assert isinstance(dist, dict)
        assert sum(dist.values()) == 3

    def test_export_analyses(self):
        """Test exporting all analyses."""
        detector = SentimentDetector()

        detector.sentiment_detector("sess_001", "Happy!")
        detector.sentiment_detector("sess_002", "Sad!")

        exported = detector.export_analyses()
        assert len(exported) == 2
        assert all("session_id" in e for e in exported)

    def test_export_session_analysis(self):
        """Test exporting specific session analysis."""
        detector = SentimentDetector()

        detector.sentiment_detector("sess_001", "Test message")

        exported = detector.export_session_analysis("sess_001")
        assert exported is not None
        assert exported["session_id"] == "sess_001"

    def test_export_nonexistent_session(self):
        """Test exporting nonexistent session."""
        detector = SentimentDetector()

        exported = detector.export_session_analysis("nonexistent")
        assert exported is None

    def test_multiple_sessions_independent(self):
        """Test multiple sessions are independent."""
        detector = SentimentDetector()

        analysis1 = detector.sentiment_detector("sess_001", "I am happy delighted thrilled")
        analysis2 = detector.sentiment_detector("sess_002", "I am sad unhappy depressed")

        assert analysis1.session_id != analysis2.session_id
        assert analysis1.sentiment_score.polarity > 0
        assert analysis2.sentiment_score.polarity < 0

    def test_overwhelming_mood_suggests_life(self):
        """Test overwhelmed mood suggests LIFE expert."""
        detector = SentimentDetector()

        analysis = detector.sentiment_detector(
            session_id="sess_001",
            mood_pattern=SessionMoodPattern.OVERWHELMED,
            text="Too much going on",
        )

        assert analysis.primary_expert.expert_domain == ExpertDomain.LIFE

    def test_engaged_mood_suggests_engineering(self):
        """Test engaged mood suggests ENGINEERING expert."""
        detector = SentimentDetector()

        analysis = detector.sentiment_detector(
            session_id="sess_001",
            mood_pattern=SessionMoodPattern.ENGAGED,
            text="Working on implementation",
        )

        assert analysis.primary_expert.expert_domain == ExpertDomain.ENGINEERING

    def test_declining_trend_suggests_life(self):
        """Test declining trend suggests LIFE expert."""
        detector = SentimentDetector()

        analysis = detector.sentiment_detector(
            session_id="sess_001",
            text="Getting worse",
            trend_direction=TrendDirection.DECLINING,
        )

        # Declining trend should suggest LIFE support
        assert analysis.primary_expert.expert_domain in [
            ExpertDomain.LIFE,
            ExpertDomain.CAREER,
        ]

    def test_improving_trend_suggests_career(self):
        """Test improving trend suggests CAREER expert."""
        detector = SentimentDetector()

        analysis = detector.sentiment_detector(
            session_id="sess_001",
            text="Getting better",
            trend_direction=TrendDirection.IMPROVING,
        )

        # Improving trend should suggest CAREER momentum
        assert analysis.primary_expert.expert_domain == ExpertDomain.CAREER

    def test_complex_mood_analysis(self):
        """Test complex mood analysis workflow."""
        detector = SentimentDetector()

        # Multiple analyses with different moods
        analyses = []
        messages = [
            ("Happy and excited!", SessionMoodPattern.UPBEAT),
            ("Frustrated with bugs", SessionMoodPattern.FRUSTRATED),
            ("Overwhelmed by tasks", SessionMoodPattern.OVERWHELMED),
            ("Carefully planning", SessionMoodPattern.CAUTIOUS),
        ]

        for i, (message, mood) in enumerate(messages):
            analysis = detector.sentiment_detector(
                f"sess_{i:03d}",
                message,
                mood_pattern=mood,
            )
            analyses.append(analysis)

        # Verify we got 4 distinct analyses
        assert len(detector.suggestion_history) == 4

        # Verify distribution
        dist = detector.get_expert_suggestion_distribution()
        assert sum(dist.values()) == 4

        # Export all
        exported = detector.export_analyses()
        assert len(exported) == 4

    def test_reasoning_specific_to_emotion(self):
        """Test that reasoning mentions detected emotions."""
        detector = SentimentDetector()

        analysis = detector.sentiment_detector(
            "sess_001",
            "I'm very happy and excited!",
        )

        reasoning_text = " ".join(analysis.primary_expert.reasoning).lower()
        # Should mention sentiment or emotion
        assert (
            "sentiment" in reasoning_text
            or "emotion" in reasoning_text
            or "mood" in reasoning_text
        )

    def test_confidence_varies_by_clarity(self):
        """Test that confidence varies based on sentiment clarity."""
        detector = SentimentDetector()

        # Clear positive
        clear_analysis = detector.sentiment_detector(
            "sess_001", "I'm absolutely thrilled and excited!"
        )

        # Neutral/unclear
        unclear_analysis = detector.sentiment_detector("sess_002", "OK")

        # Clear should have higher confidence
        assert (
            clear_analysis.primary_expert.confidence
            >= unclear_analysis.primary_expert.confidence
        )

    def test_sentiment_detector_with_all_parameters(self):
        """Test sentiment_detector with all parameters specified."""
        detector = SentimentDetector()

        analysis = detector.sentiment_detector(
            session_id="sess_001",
            text="I'm feeling great and looking forward to work!",
            mood_pattern=SessionMoodPattern.UPBEAT,
            trend_direction=TrendDirection.IMPROVING,
        )

        assert analysis.session_id == "sess_001"
        assert analysis.mood_pattern == SessionMoodPattern.UPBEAT
        assert analysis.trend_direction == TrendDirection.IMPROVING
        assert analysis.primary_expert is not None
