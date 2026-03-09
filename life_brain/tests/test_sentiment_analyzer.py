"""Test suite for sentiment analyzer."""

import pytest
from life_brain.conversation.sentiment_analyzer import (
    SentimentAnalyzer,
    SentimentScore,
    Sentiment,
    Emotion,
)


class TestSentimentScore:
    """Test SentimentScore dataclass."""

    def test_create_score(self):
        """Test creating sentiment score."""
        score = SentimentScore(
            text="I am very happy",
            overall_sentiment=Sentiment.POSITIVE,
            confidence=0.9,
            polarity=0.8,
        )

        assert score.text == "I am very happy"
        assert score.overall_sentiment == Sentiment.POSITIVE

    def test_to_dict(self):
        """Test converting to dictionary."""
        score = SentimentScore(
            text="Test",
            overall_sentiment=Sentiment.NEUTRAL,
            confidence=0.5,
            polarity=0.0,
        )

        score_dict = score.to_dict()
        assert score_dict["overall_sentiment"] == "neutral"


class TestSentimentAnalyzer:
    """Test SentimentAnalyzer."""

    def test_create_analyzer(self):
        """Test creating analyzer."""
        analyzer = SentimentAnalyzer()
        assert len(analyzer.emotion_history) == 0

    def test_sentiment_positive(self):
        """Test analyzing positive sentiment."""
        analyzer = SentimentAnalyzer()

        score = analyzer.sentiment_analyzer("I love this! It is amazing and wonderful.")
        assert score.overall_sentiment in [Sentiment.POSITIVE, Sentiment.VERY_POSITIVE]
        assert score.polarity > 0

    def test_sentiment_negative(self):
        """Test analyzing negative sentiment."""
        analyzer = SentimentAnalyzer()

        score = analyzer.sentiment_analyzer("I hate this. It is terrible and awful.")
        assert score.overall_sentiment in [Sentiment.NEGATIVE, Sentiment.VERY_NEGATIVE]
        assert score.polarity < 0

    def test_sentiment_neutral(self):
        """Test analyzing neutral sentiment."""
        analyzer = SentimentAnalyzer()

        score = analyzer.sentiment_analyzer("This is a document about procedures.")
        assert score.overall_sentiment == Sentiment.NEUTRAL
        assert score.polarity == 0.0

    def test_emotion_detection_joy(self):
        """Test detecting joy emotion."""
        analyzer = SentimentAnalyzer()

        score = analyzer.sentiment_analyzer("I am so happy and excited about this!")
        assert Emotion.JOY in score.emotions or len(score.emotions) > 0

    def test_tone_detection_urgent(self):
        """Test detecting urgent tone."""
        analyzer = SentimentAnalyzer()

        score = analyzer.sentiment_analyzer("This is urgent and needs immediate attention!")
        assert score.tone == "urgent"

    def test_tone_detection_emphatic(self):
        """Test detecting emphatic tone."""
        analyzer = SentimentAnalyzer()

        score = analyzer.sentiment_analyzer("This is incredible!")
        assert score.tone == "emphatic"

    def test_tone_detection_formal(self):
        """Test detecting formal tone."""
        analyzer = SentimentAnalyzer()

        score = analyzer.sentiment_analyzer("Therefore, we should proceed accordingly.")
        assert score.tone == "formal"

    def test_intensity_calculation(self):
        """Test intensity calculation."""
        analyzer = SentimentAnalyzer()

        neutral = analyzer.sentiment_analyzer("Normal text")
        positive = analyzer.sentiment_analyzer("Very good great amazing wonderful")

        assert positive.intensity > neutral.intensity

    def test_get_dominant_emotion(self):
        """Test getting dominant emotion."""
        analyzer = SentimentAnalyzer()

        score = analyzer.sentiment_analyzer("I am very happy and joyful!")
        dominant = analyzer.get_dominant_emotion(score)
        
        # Should have some emotion detected
        if score.emotions:
            assert dominant is not None

    def test_get_analysis_history(self):
        """Test getting analysis history."""
        analyzer = SentimentAnalyzer()

        for i in range(5):
            analyzer.sentiment_analyzer(f"Message {i}")

        history = analyzer.get_analysis_history(limit=3)
        assert len(history) == 3

    def test_get_sentiment_trend(self):
        """Test getting sentiment trend."""
        analyzer = SentimentAnalyzer()

        analyzer.sentiment_analyzer("Good")
        analyzer.sentiment_analyzer("Better")
        analyzer.sentiment_analyzer("Excellent")

        trend = analyzer.get_sentiment_trend(window=3)
        assert trend["trend"] in ["improving", "declining", "stable", "single_message"]

    def test_get_emotional_profile(self):
        """Test getting emotional profile."""
        analyzer = SentimentAnalyzer()

        for text in ["happy", "sad", "angry", "excited"]:
            analyzer.sentiment_analyzer(text)

        profile = analyzer.get_emotional_profile()
        assert profile["messages_analyzed"] == 4
        assert "emotion_distribution" in profile

    def test_export_analyses(self):
        """Test exporting analyses."""
        analyzer = SentimentAnalyzer()

        analyzer.sentiment_analyzer("Good")
        analyzer.sentiment_analyzer("Bad")

        exported = analyzer.export_analyses()
        assert len(exported) == 2
        assert all("overall_sentiment" in e for e in exported)

    def test_confidence_scores(self):
        """Test confidence calculation."""
        analyzer = SentimentAnalyzer()

        strong = analyzer.sentiment_analyzer("Good great excellent amazing wonderful")
        weak = analyzer.sentiment_analyzer("ok")

        assert strong.confidence > weak.confidence

    def test_multiple_analyses(self):
        """Test multiple sequential analyses."""
        analyzer = SentimentAnalyzer()

        messages = [
            "I am happy!",
            "This is neutral.",
            "I am sad.",
            "Excellent work!",
        ]

        for msg in messages:
            analyzer.sentiment_analyzer(msg)

        assert len(analyzer.emotion_history) == 4

    def test_mixed_sentiment(self):
        """Test analyzing mixed sentiment."""
        analyzer = SentimentAnalyzer()

        score = analyzer.sentiment_analyzer("I love the good parts but hate the bad parts.")
        # Should detect mixed sentiment, polarity close to neutral or slightly positive
        assert -0.5 <= score.polarity <= 0.5
