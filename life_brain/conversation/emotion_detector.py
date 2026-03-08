"""
Emotional tone detection for proactive mental health expert suggestions.

Detects: stressed, anxious, excited, uncertain, frustrated, neutral.
Suggests mental health expert when stress/anxiety signals detected.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Keyword signals per emotion
_EMOTION_SIGNALS: Dict[str, List[str]] = {
    "stressed": [
        "overwhelmed", "can't handle", "too much", "burning out", "exhausted",
        "no time", "deadlines", "pressure", "stressed", "stressed out",
        "can't cope", "falling behind", "behind schedule", "workload",
        "impossible", "burnout", "drained", "swamped", "drowning",
    ],
    "anxious": [
        "worried", "nervous", "anxious", "scared", "fear", "afraid",
        "what if", "panic", "don't know what to do", "lost", "unsure",
        "not sure", "terrified", "dreading", "uncertain about", "will i",
    ],
    "frustrated": [
        "frustrated", "annoyed", "irritated", "fed up", "sick of",
        "waste of time", "pointless", "useless", "stupid", "hate this",
        "doesn't work", "nothing works", "keeps failing", "again",
    ],
    "excited": [
        "excited", "can't wait", "amazing", "great news", "thrilled",
        "fantastic", "love this", "so happy", "awesome", "pumped",
        "looking forward", "best day", "nailed it", "crushed it",
    ],
    "uncertain": [
        "not sure", "don't know", "confused", "unclear", "maybe",
        "might", "perhaps", "possibly", "wondering", "thinking about",
        "should i", "what should", "help me decide", "torn between",
    ],
}

# Emotions that warrant a mental health expert suggestion
_MENTAL_HEALTH_TRIGGER_EMOTIONS = {"stressed", "anxious", "frustrated"}

# Confidence thresholds
_CONFIDENCE_THRESHOLD = 0.3  # Minimum to detect emotion
_SUGGESTION_THRESHOLD = 0.5  # Minimum to suggest expert


@dataclass
class EmotionResult:
    """Result of emotion detection."""

    primary_emotion: str          # Top detected emotion
    confidence: float             # 0-1 confidence
    all_emotions: Dict[str, float]  # All detected emotions with scores
    suggest_mental_health: bool   # Whether to proactively suggest MH expert
    suggestion_message: Optional[str]  # Ready-to-display suggestion (if any)


def _score_message(message: str) -> Dict[str, float]:
    """Score a message against all emotion signal lists.

    Returns dict of {emotion: score} where score is 0-1.
    """
    lower = message.lower()
    scores: Dict[str, float] = {}

    for emotion, signals in _EMOTION_SIGNALS.items():
        matches = sum(1 for signal in signals if signal in lower)
        # Normalize: 1 match = 0.5, 2+ matches = approaches 1.0
        score = min(1.0, matches * 0.4) if matches > 0 else 0.0
        if score > 0:
            scores[emotion] = score

    return scores


def detect_emotion(message: str) -> EmotionResult:
    """Detect emotional tone in a single message.

    Args:
        message: User's message text

    Returns:
        EmotionResult with detected emotion and suggestion flag
    """
    if not message or not message.strip():
        return EmotionResult(
            primary_emotion="neutral",
            confidence=0.0,
            all_emotions={},
            suggest_mental_health=False,
            suggestion_message=None,
        )

    scores = _score_message(message)

    if not scores:
        return EmotionResult(
            primary_emotion="neutral",
            confidence=0.0,
            all_emotions={},
            suggest_mental_health=False,
            suggestion_message=None,
        )

    primary = max(scores, key=lambda e: scores[e])
    confidence = scores[primary]

    should_suggest = (
        primary in _MENTAL_HEALTH_TRIGGER_EMOTIONS
        and confidence >= _SUGGESTION_THRESHOLD
    )

    suggestion = _build_suggestion(primary, confidence) if should_suggest else None

    return EmotionResult(
        primary_emotion=primary if confidence >= _CONFIDENCE_THRESHOLD else "neutral",
        confidence=confidence,
        all_emotions=scores,
        suggest_mental_health=should_suggest,
        suggestion_message=suggestion,
    )


def detect_emotion_from_history(messages: List[str]) -> EmotionResult:
    """Detect emotional tone across a conversation history.

    Aggregates scores across messages — persistent signals are weighted higher.

    Args:
        messages: List of user messages (chronological)

    Returns:
        EmotionResult representing overall emotional tone
    """
    if not messages:
        return EmotionResult(
            primary_emotion="neutral",
            confidence=0.0,
            all_emotions={},
            suggest_mental_health=False,
            suggestion_message=None,
        )

    aggregated: Dict[str, float] = {}
    for msg in messages:
        scores = _score_message(msg)
        for emotion, score in scores.items():
            # Recent messages weighted slightly more (last message = 1.2x)
            weight = 1.2 if msg == messages[-1] else 1.0
            aggregated[emotion] = max(aggregated.get(emotion, 0.0), score * weight)

    if not aggregated:
        return EmotionResult(
            primary_emotion="neutral",
            confidence=0.0,
            all_emotions={},
            suggest_mental_health=False,
            suggestion_message=None,
        )

    # Clamp to 1.0
    aggregated = {e: min(1.0, s) for e, s in aggregated.items()}

    primary = max(aggregated, key=lambda e: aggregated[e])
    confidence = aggregated[primary]

    should_suggest = (
        primary in _MENTAL_HEALTH_TRIGGER_EMOTIONS
        and confidence >= _SUGGESTION_THRESHOLD
    )

    suggestion = _build_suggestion(primary, confidence) if should_suggest else None

    return EmotionResult(
        primary_emotion=primary if confidence >= _CONFIDENCE_THRESHOLD else "neutral",
        confidence=confidence,
        all_emotions=aggregated,
        suggest_mental_health=should_suggest,
        suggestion_message=suggestion,
    )


def _build_suggestion(emotion: str, confidence: float) -> str:
    """Build a proactive mental health expert suggestion message."""
    messages = {
        "stressed": (
            "It sounds like you're under a lot of pressure right now. "
            "Would you like to talk to our mental health expert? "
            "Sometimes an outside perspective helps."
        ),
        "anxious": (
            "I'm picking up some worry in what you're sharing. "
            "Our mental health expert is here if you'd like to talk through it."
        ),
        "frustrated": (
            "That does sound frustrating. If it's getting to you, "
            "our mental health expert can help you work through it."
        ),
    }
    return messages.get(emotion, "Would you like to speak with a mental health expert?")
