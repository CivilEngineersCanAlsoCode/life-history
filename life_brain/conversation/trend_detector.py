"""
Trend detector for tracking emotional patterns across sessions.

Analyzes emotional trends over time to identify mood patterns,
emotional arcs, and overall emotional trajectory.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class TrendDirection(Enum):
    """Trend direction."""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"


class SessionMoodPattern(Enum):
    """Session mood patterns."""
    UPBEAT = "upbeat"  # Consistently positive
    ENGAGED = "engaged"  # Actively processing
    CAUTIOUS = "cautious"  # Careful, reserved
    FRUSTRATED = "frustrated"  # Showing difficulty
    OVERWHELMED = "overwhelmed"  # Too much
    WITHDRAWN = "withdrawn"  # Low engagement


@dataclass
class SessionSentiment:
    """Sentiment snapshot for a session."""
    
    session_id: str
    avg_polarity: float  # -1 to +1
    sentiment_distribution: Dict[str, int]  # sentiment -> count
    emotion_profile: Dict[str, float]  # emotion -> avg score
    dominant_emotion: Optional[str] = None
    messages_count: int = 0
    session_date: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class EmotionalTrend:
    """Emotional trend over period."""
    
    period: str  # "week", "month", "session", etc.
    direction: TrendDirection
    polarity_change: float  # Change in polarity
    sessions_analyzed: int
    mood_pattern: SessionMoodPattern
    peak_emotion: Optional[str] = None
    low_point: Optional[str] = None
    volatility: float = 0.0  # 0-1 scale
    confidence: float = 0.5


class TrendDetector:
    """Detect emotional trends across sessions."""
    
    def __init__(self):
        """Initialize trend detector."""
        self.session_sentiments: List[SessionSentiment] = []
        self.trends: Dict[str, EmotionalTrend] = {}

    def trend_detector(
        self,
        session_id: str,
        avg_polarity: float,
        sentiment_distribution: Dict[str, int],
        emotion_profile: Dict[str, float],
        messages_count: int = 0,
    ) -> SessionSentiment:
        """
        Record session sentiment for trend analysis.

        Args:
            session_id: Session identifier
            avg_polarity: Average polarity (-1 to +1)
            sentiment_distribution: Distribution of sentiments
            emotion_profile: Emotion scores
            messages_count: Number of messages analyzed

        Returns:
            SessionSentiment snapshot
        """
        # Get dominant emotion
        dominant_emotion = (
            max(emotion_profile, key=emotion_profile.get)
            if emotion_profile else None
        )
        
        # Create session sentiment
        sentiment = SessionSentiment(
            session_id=session_id,
            avg_polarity=avg_polarity,
            sentiment_distribution=sentiment_distribution,
            emotion_profile=emotion_profile,
            dominant_emotion=dominant_emotion,
            messages_count=messages_count,
        )
        
        self.session_sentiments.append(sentiment)
        
        return sentiment

    def analyze_trend(
        self,
        period: str = "session",
        window_size: Optional[int] = None,
    ) -> EmotionalTrend:
        """
        Analyze emotional trend over period.

        Args:
            period: "session", "week", "month"
            window_size: Optional custom window (number of sessions)

        Returns:
            EmotionalTrend object
        """
        if not self.session_sentiments:
            return EmotionalTrend(
                period=period,
                direction=TrendDirection.STABLE,
                polarity_change=0.0,
                sessions_analyzed=0,
                mood_pattern=SessionMoodPattern.CAUTIOUS,
            )
        
        # Determine window
        if window_size:
            sessions = self.session_sentiments[-window_size:]
        elif period == "session" and len(self.session_sentiments) > 0:
            sessions = [self.session_sentiments[-1]]
        else:
            # Use all sessions (for now)
            sessions = self.session_sentiments
        
        if not sessions:
            return EmotionalTrend(
                period=period,
                direction=TrendDirection.STABLE,
                polarity_change=0.0,
                sessions_analyzed=0,
                mood_pattern=SessionMoodPattern.CAUTIOUS,
            )
        
        # Calculate trend metrics
        polarities = [s.avg_polarity for s in sessions]
        avg_polarity = sum(polarities) / len(polarities) if polarities else 0
        
        # Polarity change
        if len(polarities) >= 2:
            polarity_change = polarities[-1] - polarities[0]
        else:
            polarity_change = 0
        
        # Determine direction
        if len(polarities) >= 2:
            first_half = sum(polarities[:len(polarities)//2]) / (len(polarities)//2)
            second_half = sum(polarities[len(polarities)//2:]) / (len(polarities) - len(polarities)//2)
            
            if second_half > first_half + 0.2:
                direction = TrendDirection.IMPROVING
            elif second_half < first_half - 0.2:
                direction = TrendDirection.DECLINING
            else:
                direction = TrendDirection.STABLE
        else:
            direction = TrendDirection.STABLE
        
        # Volatility
        if len(polarities) >= 2:
            mean = avg_polarity
            variance = sum((p - mean) ** 2 for p in polarities) / len(polarities)
            volatility = min(1.0, (variance ** 0.5) * 0.5)  # Normalize
        else:
            volatility = 0.0
        
        if volatility > 0.5:
            direction = TrendDirection.VOLATILE
        
        # Mood pattern
        mood_pattern = self._classify_mood_pattern(avg_polarity, volatility)
        
        # Peak and low emotions
        all_emotions = {}
        for s in sessions:
            for emotion, score in s.emotion_profile.items():
                all_emotions[emotion] = all_emotions.get(emotion, 0) + score
        
        peak_emotion = max(all_emotions, key=all_emotions.get) if all_emotions else None
        low_point = (
            "negative" if avg_polarity < -0.3 else
            "neutral" if avg_polarity < 0.3 else
            "positive"
        )
        
        return EmotionalTrend(
            period=period,
            direction=direction,
            polarity_change=polarity_change,
            sessions_analyzed=len(sessions),
            mood_pattern=mood_pattern,
            peak_emotion=peak_emotion,
            low_point=low_point,
            volatility=volatility,
            confidence=min(0.95, abs(avg_polarity) * 0.8 + 0.2),
        )

    def _classify_mood_pattern(self, polarity: float, volatility: float) -> SessionMoodPattern:
        """Classify mood pattern from metrics."""
        if polarity > 0.5 and volatility < 0.3:
            return SessionMoodPattern.UPBEAT
        elif polarity > 0.2 and volatility < 0.5:
            return SessionMoodPattern.ENGAGED
        elif abs(polarity) < 0.2:
            return SessionMoodPattern.CAUTIOUS
        elif polarity < -0.3 and volatility > 0.4:
            return SessionMoodPattern.FRUSTRATED
        elif polarity < -0.5:
            return SessionMoodPattern.OVERWHELMED
        else:
            return SessionMoodPattern.WITHDRAWN

    def get_recent_trends(self, num_periods: int = 3) -> List[EmotionalTrend]:
        """Get recent emotional trends."""
        trends = []
        
        # Analyze recent sessions in groups
        if len(self.session_sentiments) > 0:
            sessions_per_period = max(1, len(self.session_sentiments) // num_periods)
            
            for i in range(num_periods):
                start = i * sessions_per_period
                end = start + sessions_per_period
                
                if i == num_periods - 1:
                    end = len(self.session_sentiments)
                
                if start < len(self.session_sentiments):
                    trend = self.analyze_trend(
                        period=f"period_{i}",
                        window_size=end-start,
                    )
                    trends.append(trend)
        
        return trends

    def get_overall_emotional_arc(self) -> Dict[str, Any]:
        """Get overall emotional arc across all sessions."""
        if not self.session_sentiments:
            return {
                "arc": "no_data",
                "starting_polarity": 0.0,
                "ending_polarity": 0.0,
                "peak_polarity": 0.0,
                "low_polarity": 0.0,
                "overall_trend": "stable",
            }
        
        polarities = [s.avg_polarity for s in self.session_sentiments]
        
        return {
            "arc": self._classify_arc(polarities),
            "starting_polarity": polarities[0],
            "ending_polarity": polarities[-1],
            "peak_polarity": max(polarities),
            "low_polarity": min(polarities),
            "overall_trend": self._get_overall_trend(polarities),
            "sessions_tracked": len(self.session_sentiments),
        }

    def _classify_arc(self, polarities: List[float]) -> str:
        """Classify emotional arc."""
        if len(polarities) < 2:
            return "insufficient_data"
        
        if polarities[-1] > polarities[0]:
            return "rising"
        elif polarities[-1] < polarities[0]:
            return "falling"
        else:
            return "cyclical"

    def _get_overall_trend(self, polarities: List[float]) -> str:
        """Get overall trend from polarities."""
        if len(polarities) < 3:
            return "single_or_few_sessions"
        
        avg = sum(polarities) / len(polarities)
        
        if avg > 0.3:
            return "generally_positive"
        elif avg < -0.3:
            return "generally_negative"
        else:
            return "mixed_neutral"

    def detect_mood_shift(self, threshold: float = 0.5) -> Optional[Tuple[str, str]]:
        """Detect significant mood shifts between recent sessions."""
        if len(self.session_sentiments) < 2:
            return None
        
        recent_polarity = self.session_sentiments[-1].avg_polarity
        previous_polarity = self.session_sentiments[-2].avg_polarity
        
        shift = abs(recent_polarity - previous_polarity)
        
        if shift > threshold:
            old_mood = "positive" if previous_polarity > 0 else "negative"
            new_mood = "positive" if recent_polarity > 0 else "negative"
            return (old_mood, new_mood)
        
        return None

    def export_session_history(self) -> List[Dict[str, Any]]:
        """Export all session sentiment history."""
        return [
            {
                "session_id": s.session_id,
                "polarity": s.avg_polarity,
                "date": s.session_date,
                "messages": s.messages_count,
                "dominant_emotion": s.dominant_emotion,
            }
            for s in self.session_sentiments
        ]
