"""
Emotion trend tracking across sessions.

Tracks emotional tone over time and flags rising stress patterns.
Persists session emotion snapshots and computes trends.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from life_brain.conversation.emotion_detector import EmotionResult, detect_emotion_from_history

# Stress-related emotions to watch for trend
_STRESS_EMOTIONS = {"stressed", "anxious", "frustrated"}

# Rising stress threshold: score increase between sessions
_RISING_STRESS_DELTA = 0.2

# Alert if stress has been high for this many sessions consecutively
_PERSISTENT_STRESS_SESSIONS = 3


@dataclass
class SessionEmotionSnapshot:
    """Emotion state at end of a session."""

    session_id: str
    timestamp: str
    primary_emotion: str
    confidence: float
    stress_score: float  # Max score across stress-related emotions
    all_emotions: Dict[str, float]


@dataclass
class EmotionTrend:
    """Result of trend analysis across sessions."""

    trend_direction: str       # "rising", "falling", "stable", "insufficient_data"
    stress_score_delta: float  # Change in stress score (positive = rising)
    is_rising_stress: bool     # True if stress is trending up significantly
    consecutive_high_stress: int  # Number of consecutive high-stress sessions
    should_alert: bool          # True if alert warranted
    alert_message: Optional[str]
    sessions_analyzed: int


class EmotionTrendTracker:
    """Track emotional trends across sessions and flag rising stress."""

    def __init__(self, high_stress_threshold: float = 0.5):
        """Initialize tracker.

        Args:
            high_stress_threshold: Score above which stress is considered 'high'
        """
        self.high_stress_threshold = high_stress_threshold
        self.session_snapshots: List[SessionEmotionSnapshot] = []

    def record_session(
        self,
        session_id: str,
        messages: List[str],
        timestamp: Optional[str] = None,
    ) -> SessionEmotionSnapshot:
        """Record emotion snapshot for a completed session.

        Args:
            session_id: Unique session identifier
            messages: All user messages from the session
            timestamp: ISO timestamp (defaults to now)

        Returns:
            SessionEmotionSnapshot
        """
        ts = timestamp or datetime.now().isoformat()
        result = detect_emotion_from_history(messages)

        stress_score = max(
            result.all_emotions.get(e, 0.0) for e in _STRESS_EMOTIONS
        ) if result.all_emotions else 0.0

        snapshot = SessionEmotionSnapshot(
            session_id=session_id,
            timestamp=ts,
            primary_emotion=result.primary_emotion,
            confidence=result.confidence,
            stress_score=stress_score,
            all_emotions=result.all_emotions,
        )
        self.session_snapshots.append(snapshot)
        return snapshot

    def record_snapshot(self, snapshot: SessionEmotionSnapshot) -> None:
        """Record a pre-built snapshot (for testing / manual use)."""
        self.session_snapshots.append(snapshot)

    def analyze_trend(self, window: int = 5) -> EmotionTrend:
        """Analyze stress trend across recent sessions.

        Args:
            window: Number of recent sessions to analyze

        Returns:
            EmotionTrend with direction and alert status
        """
        recent = self.session_snapshots[-window:]

        if len(recent) < 2:
            return EmotionTrend(
                trend_direction="insufficient_data",
                stress_score_delta=0.0,
                is_rising_stress=False,
                consecutive_high_stress=0,
                should_alert=False,
                alert_message=None,
                sessions_analyzed=len(recent),
            )

        first_score = recent[0].stress_score
        last_score = recent[-1].stress_score
        delta = last_score - first_score

        # Count consecutive high-stress sessions from the end
        consecutive = 0
        for snap in reversed(recent):
            if snap.stress_score >= self.high_stress_threshold:
                consecutive += 1
            else:
                break

        is_rising = delta >= _RISING_STRESS_DELTA
        is_persistent = consecutive >= _PERSISTENT_STRESS_SESSIONS

        if delta > 0.1:
            direction = "rising"
        elif delta < -0.1:
            direction = "falling"
        else:
            direction = "stable"

        should_alert = is_rising or is_persistent
        alert_msg = None
        if should_alert:
            if is_persistent:
                alert_msg = (
                    f"You've been showing signs of stress for {consecutive} sessions in a row. "
                    "Would you like to talk to a mental health expert?"
                )
            else:
                alert_msg = (
                    "I've noticed your stress levels have been rising lately. "
                    "Would you like to speak with a mental health expert?"
                )

        return EmotionTrend(
            trend_direction=direction,
            stress_score_delta=round(delta, 3),
            is_rising_stress=is_rising,
            consecutive_high_stress=consecutive,
            should_alert=should_alert,
            alert_message=alert_msg,
            sessions_analyzed=len(recent),
        )

    def get_stress_history(self) -> List[Dict]:
        """Get stress scores across all recorded sessions."""
        return [
            {
                "session_id": s.session_id,
                "timestamp": s.timestamp,
                "stress_score": s.stress_score,
                "primary_emotion": s.primary_emotion,
            }
            for s in self.session_snapshots
        ]
