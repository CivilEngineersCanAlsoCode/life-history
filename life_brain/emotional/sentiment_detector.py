"""
Sentiment detector for mood-based expert suggestion.

Maps emotional state and mood patterns to appropriate expert recommendations
for session initialization and guidance.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from life_brain.emotional.sentiment_analyzer import (
    SentimentAnalyzer,
    Sentiment,
    Emotion,
    SentimentScore,
)
from life_brain.emotional.trend_detector import (
    TrendDetector,
    SessionMoodPattern,
    TrendDirection,
)
from life_brain.session.preferences import ExpertDomain


@dataclass
class ExpertSuggestion:
    """Expert suggestion based on mood and emotional state."""

    expert_domain: ExpertDomain
    confidence: float  # 0-1, how confident in this suggestion
    reasoning: List[str]  # Why this expert was suggested
    emotional_factors: Dict[str, float]  # Emotion → contribution score
    suggested_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "expert_domain": self.expert_domain.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "emotional_factors": self.emotional_factors,
            "suggested_at": self.suggested_at,
        }


@dataclass
class MoodAnalysis:
    """Complete mood analysis with expert suggestions."""

    session_id: str
    text: str
    sentiment_score: SentimentScore
    mood_pattern: Optional[SessionMoodPattern] = None
    trend_direction: Optional[TrendDirection] = None
    primary_expert: Optional[ExpertSuggestion] = None
    alternate_experts: List[ExpertSuggestion] = field(default_factory=list)
    analysis_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "text": self.text,
            "sentiment": self.sentiment_score.to_dict(),
            "mood_pattern": self.mood_pattern.value if self.mood_pattern else None,
            "trend_direction": self.trend_direction.value if self.trend_direction else None,
            "primary_expert": self.primary_expert.to_dict() if self.primary_expert else None,
            "alternate_experts": [e.to_dict() for e in self.alternate_experts],
            "analysis_at": self.analysis_at,
        }


class SentimentDetector:
    """Detect mood and suggest appropriate expert."""

    # Emotion to Expert mapping
    EMOTION_EXPERT_MAP = {
        Emotion.JOY: (ExpertDomain.CAREER, 0.8),  # Career growth
        Emotion.TRUST: (ExpertDomain.PRODUCT, 0.7),  # Product confidence
        Emotion.FEAR: (ExpertDomain.CAREER, 0.9),  # Career guidance
        Emotion.SURPRISE: (ExpertDomain.PRODUCT, 0.6),  # Explore new
        Emotion.SADNESS: (ExpertDomain.LIFE, 0.8),  # Life support
        Emotion.DISGUST: (ExpertDomain.CAREER, 0.7),  # Career reevaluation
        Emotion.ANGER: (ExpertDomain.ENGINEERING, 0.8),  # Problem-solving
        Emotion.ANTICIPATION: (ExpertDomain.CAREER, 0.7),  # Career planning
    }

    # Mood pattern to Expert mapping
    MOOD_EXPERT_MAP = {
        SessionMoodPattern.UPBEAT: (ExpertDomain.PRODUCT, 0.8),  # Growth
        SessionMoodPattern.ENGAGED: (ExpertDomain.ENGINEERING, 0.8),  # Active work
        SessionMoodPattern.CAUTIOUS: (ExpertDomain.CAREER, 0.75),  # Careful guidance
        SessionMoodPattern.FRUSTRATED: (ExpertDomain.ENGINEERING, 0.85),  # Problem-solve
        SessionMoodPattern.OVERWHELMED: (ExpertDomain.LIFE, 0.9),  # Refocus
        SessionMoodPattern.WITHDRAWN: (ExpertDomain.CAREER, 0.8),  # Re-engagement
    }

    # Sentiment to Expert mapping
    SENTIMENT_EXPERT_MAP = {
        Sentiment.VERY_POSITIVE: (ExpertDomain.PRODUCT, 0.7),
        Sentiment.POSITIVE: (ExpertDomain.CAREER, 0.6),
        Sentiment.NEUTRAL: (ExpertDomain.DATA, 0.5),
        Sentiment.NEGATIVE: (ExpertDomain.CAREER, 0.75),
        Sentiment.VERY_NEGATIVE: (ExpertDomain.LIFE, 0.85),
    }

    # Trend to Expert mapping
    TREND_EXPERT_MAP = {
        TrendDirection.IMPROVING: (ExpertDomain.CAREER, 0.6),  # Momentum
        TrendDirection.STABLE: (ExpertDomain.DATA, 0.5),  # Analysis
        TrendDirection.DECLINING: (ExpertDomain.LIFE, 0.8),  # Support
        TrendDirection.VOLATILE: (ExpertDomain.ENGINEERING, 0.7),  # Stabilize
    }

    def __init__(self):
        """Initialize sentiment detector."""
        self.sentiment_analyzer = SentimentAnalyzer()
        self.trend_detector = TrendDetector()
        self.analyses: Dict[str, MoodAnalysis] = {}
        self.suggestion_history: List[MoodAnalysis] = []

    def sentiment_detector(
        self,
        session_id: str,
        text: str,
        mood_pattern: Optional[SessionMoodPattern] = None,
        trend_direction: Optional[TrendDirection] = None,
    ) -> MoodAnalysis:
        """
        Analyze mood and suggest appropriate expert.

        Args:
            session_id: Session identifier
            text: User message to analyze
            mood_pattern: Optional pre-classified mood pattern
            trend_direction: Optional trend from historical analysis

        Returns:
            MoodAnalysis with expert suggestion
        """
        # Analyze sentiment
        sentiment_score = self.sentiment_analyzer.sentiment_analyzer(text)

        # Classify mood pattern if not provided
        if not mood_pattern:
            mood_pattern = self._classify_mood_pattern(sentiment_score)

        # Calculate expert suggestions
        primary_expert, primary_confidence = self._suggest_primary_expert(
            sentiment_score, mood_pattern, trend_direction
        )

        # Get alternate experts
        alternate_experts = self._get_alternate_experts(
            sentiment_score, mood_pattern, trend_direction, primary_expert
        )

        # Create primary suggestion
        primary_suggestion = ExpertSuggestion(
            expert_domain=primary_expert,
            confidence=primary_confidence,
            reasoning=self._generate_reasoning(
                sentiment_score, mood_pattern, trend_direction, primary_expert
            ),
            emotional_factors=self._calculate_emotional_factors(
                sentiment_score, primary_expert
            ),
        )

        # Create analysis
        analysis = MoodAnalysis(
            session_id=session_id,
            text=text,
            sentiment_score=sentiment_score,
            mood_pattern=mood_pattern,
            trend_direction=trend_direction,
            primary_expert=primary_suggestion,
            alternate_experts=alternate_experts,
        )

        # Store
        self.analyses[session_id] = analysis
        self.suggestion_history.append(analysis)

        return analysis

    def _classify_mood_pattern(self, sentiment_score: SentimentScore) -> SessionMoodPattern:
        """Classify mood pattern from sentiment."""
        polarity = sentiment_score.polarity
        intensity = sentiment_score.intensity

        if polarity > 0.5 and intensity >= 6:
            return SessionMoodPattern.UPBEAT
        elif polarity > 0.3 and intensity >= 5:
            return SessionMoodPattern.ENGAGED
        elif polarity > 0 and intensity <= 5:
            return SessionMoodPattern.CAUTIOUS
        elif polarity < -0.3 and intensity >= 6:
            return SessionMoodPattern.FRUSTRATED
        elif polarity < -0.5 and intensity >= 7:
            return SessionMoodPattern.OVERWHELMED
        else:
            return SessionMoodPattern.WITHDRAWN

    def _suggest_primary_expert(
        self,
        sentiment_score: SentimentScore,
        mood_pattern: SessionMoodPattern,
        trend_direction: Optional[TrendDirection],
    ) -> Tuple[ExpertDomain, float]:
        """Suggest primary expert based on mood factors."""
        scores = {}

        # Score from sentiment
        sentiment = sentiment_score.overall_sentiment
        if sentiment in self.SENTIMENT_EXPERT_MAP:
            expert, confidence = self.SENTIMENT_EXPERT_MAP[sentiment]
            scores[expert] = scores.get(expert, 0) + confidence

        # Score from mood pattern
        if mood_pattern in self.MOOD_EXPERT_MAP:
            expert, confidence = self.MOOD_EXPERT_MAP[mood_pattern]
            scores[expert] = scores.get(expert, 0) + confidence

        # Score from trend
        if trend_direction and trend_direction in self.TREND_EXPERT_MAP:
            expert, confidence = self.TREND_EXPERT_MAP[trend_direction]
            scores[expert] = scores.get(expert, 0) + confidence

        # Score from dominant emotion
        dominant_emotion = self.sentiment_analyzer.get_dominant_emotion(sentiment_score)
        if dominant_emotion and dominant_emotion in self.EMOTION_EXPERT_MAP:
            expert, confidence = self.EMOTION_EXPERT_MAP[dominant_emotion]
            scores[expert] = scores.get(expert, 0) + confidence * 0.8

        # Normalize scores
        if scores:
            max_score = max(scores.values())
            normalized = {e: s / max_score for e, s in scores.items()}
            best_expert = max(normalized, key=normalized.get)
            confidence = min(1.0, normalized[best_expert])
            return best_expert, confidence
        else:
            return ExpertDomain.CAREER, 0.5

    def _get_alternate_experts(
        self,
        sentiment_score: SentimentScore,
        mood_pattern: SessionMoodPattern,
        trend_direction: Optional[TrendDirection],
        primary_expert: ExpertDomain,
    ) -> List[ExpertSuggestion]:
        """Get alternate expert suggestions."""
        alternates = []
        scores = {}

        # Collect all scored experts
        sentiment = sentiment_score.overall_sentiment
        if sentiment in self.SENTIMENT_EXPERT_MAP:
            expert, confidence = self.SENTIMENT_EXPERT_MAP[sentiment]
            scores[expert] = scores.get(expert, 0) + confidence

        if mood_pattern in self.MOOD_EXPERT_MAP:
            expert, confidence = self.MOOD_EXPERT_MAP[mood_pattern]
            scores[expert] = scores.get(expert, 0) + confidence

        if trend_direction and trend_direction in self.TREND_EXPERT_MAP:
            expert, confidence = self.TREND_EXPERT_MAP[trend_direction]
            scores[expert] = scores.get(expert, 0) + confidence

        dominant_emotion = self.sentiment_analyzer.get_dominant_emotion(sentiment_score)
        if dominant_emotion and dominant_emotion in self.EMOTION_EXPERT_MAP:
            expert, confidence = self.EMOTION_EXPERT_MAP[dominant_emotion]
            scores[expert] = scores.get(expert, 0) + confidence * 0.8

        # Get top 2 non-primary experts
        sorted_experts = sorted(
            ((e, s) for e, s in scores.items() if e != primary_expert),
            key=lambda x: x[1],
            reverse=True,
        )

        for expert, score in sorted_experts[:2]:
            confidence = min(1.0, score / max(scores.values()) if scores else 0.5)
            suggestion = ExpertSuggestion(
                expert_domain=expert,
                confidence=confidence,
                reasoning=[f"Secondary consideration based on mood analysis"],
                emotional_factors=self._calculate_emotional_factors(
                    sentiment_score, expert
                ),
            )
            alternates.append(suggestion)

        return alternates

    def _calculate_emotional_factors(
        self,
        sentiment_score: SentimentScore,
        expert: ExpertDomain,
    ) -> Dict[str, float]:
        """Calculate contribution of each emotion to expert suggestion."""
        factors = {}

        for emotion, score_value in sentiment_score.emotions.items():
            if emotion in self.EMOTION_EXPERT_MAP:
                emotion_expert, _ = self.EMOTION_EXPERT_MAP[emotion]
                if emotion_expert == expert:
                    factors[emotion.value] = score_value

        return factors

    def _generate_reasoning(
        self,
        sentiment_score: SentimentScore,
        mood_pattern: SessionMoodPattern,
        trend_direction: Optional[TrendDirection],
        primary_expert: ExpertDomain,
    ) -> List[str]:
        """Generate reasoning for expert suggestion."""
        reasons = []

        # Sentiment reason
        sentiment = sentiment_score.overall_sentiment
        reasons.append(f"Detected {sentiment.value} sentiment ({sentiment_score.confidence:.1%} confidence)")

        # Mood reason
        reasons.append(f"Mood pattern: {mood_pattern.value}")

        # Emotional reason
        if sentiment_score.emotions:
            top_emotions = sorted(
                sentiment_score.emotions.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:2]
            emotion_str = ", ".join(e[0].value for e in top_emotions)
            reasons.append(f"Dominant emotions: {emotion_str}")

        # Trend reason
        if trend_direction:
            reasons.append(f"Trend: {trend_direction.value}")

        # Intensity reason
        if sentiment_score.intensity >= 7:
            reasons.append("High intensity indicates need for expert guidance")
        elif sentiment_score.intensity <= 3:
            reasons.append("Low intensity suggests exploratory discussion")

        # Tone reason
        if sentiment_score.tone != "neutral":
            reasons.append(f"Tone is {sentiment_score.tone}, indicating specific context")

        return reasons

    def get_analysis(self, session_id: str) -> Optional[MoodAnalysis]:
        """Get analysis for session."""
        return self.analyses.get(session_id)

    def get_recent_analyses(self, limit: int = 10) -> List[MoodAnalysis]:
        """Get recent analyses."""
        return self.suggestion_history[-limit:]

    def get_expert_suggestion_distribution(self) -> Dict[str, int]:
        """Get distribution of expert suggestions."""
        dist = {}
        for analysis in self.suggestion_history:
            if analysis.primary_expert:
                expert = analysis.primary_expert.expert_domain.value
                dist[expert] = dist.get(expert, 0) + 1
        return dist

    def export_analyses(self) -> List[Dict[str, Any]]:
        """Export all mood analyses."""
        return [a.to_dict() for a in self.suggestion_history]

    def export_session_analysis(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export analysis for specific session."""
        analysis = self.get_analysis(session_id)
        return analysis.to_dict() if analysis else None
