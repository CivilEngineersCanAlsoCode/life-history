"""
Sentiment analyzer for emotional tone detection in messages.

Detects emotional sentiment, tone, and emotional keywords to understand
user mood and emotional state across conversations.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Sentiment(Enum):
    """Sentiment classification."""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class Emotion(Enum):
    """Emotion categories."""
    JOY = "joy"
    TRUST = "trust"
    FEAR = "fear"
    SURPRISE = "surprise"
    SADNESS = "sadness"
    DISGUST = "disgust"
    ANGER = "anger"
    ANTICIPATION = "anticipation"


@dataclass
class SentimentScore:
    """Sentiment analysis result."""
    
    text: str
    overall_sentiment: Sentiment
    confidence: float  # 0-1
    polarity: float  # -1 (negative) to +1 (positive)
    emotions: Dict[Emotion, float] = field(default_factory=dict)  # emotion -> score
    keywords: List[str] = field(default_factory=list)  # Emotional keywords found
    tone: str = "neutral"  # formal, casual, urgent, sarcastic, sincere, etc.
    intensity: int = 5  # 1-10 scale
    analyzed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "overall_sentiment": self.overall_sentiment.value,
            "confidence": self.confidence,
            "polarity": self.polarity,
            "emotions": {e.value: v for e, v in self.emotions.items()},
            "keywords": self.keywords,
            "tone": self.tone,
            "intensity": self.intensity,
            "analyzed_at": self.analyzed_at,
        }


class SentimentAnalyzer:
    """Analyze sentiment and emotional tone."""
    
    # Positive keywords
    POSITIVE_KEYWORDS = {
        "good", "great", "excellent", "amazing", "wonderful", "fantastic",
        "love", "beautiful", "happy", "awesome", "brilliant", "perfect",
        "success", "achievement", "proud", "excited", "grateful", "thankful",
        "accomplished", "thrilled", "delighted", "impressed", "inspired",
    }
    
    # Negative keywords
    NEGATIVE_KEYWORDS = {
        "bad", "terrible", "awful", "horrible", "hate", "disappointing",
        "sad", "angry", "frustrated", "annoyed", "upset", "worried",
        "scared", "confused", "lost", "tired", "exhausted", "overwhelmed",
        "failed", "mistake", "problem", "issue", "wrong", "broken",
    }
    
    # Emotion keywords mapping
    EMOTION_KEYWORDS = {
        Emotion.JOY: ["happy", "joy", "delighted", "thrilled", "excited", "pleased"],
        Emotion.TRUST: ["trust", "confident", "sure", "positive", "faith", "belief"],
        Emotion.FEAR: ["fear", "afraid", "scared", "worried", "anxious", "nervous"],
        Emotion.SURPRISE: ["surprised", "amazed", "shocked", "astonished", "unexpected"],
        Emotion.SADNESS: ["sad", "unhappy", "depressed", "down", "miserable", "grief"],
        Emotion.DISGUST: ["disgusted", "horrible", "offensive", "gross", "repulsive"],
        Emotion.ANGER: ["angry", "furious", "rage", "mad", "livid", "hostile"],
        Emotion.ANTICIPATION: ["looking forward", "expecting", "anticipating", "hope"],
    }
    
    # Tone markers
    URGENT_MARKERS = ["urgent", "immediate", "asap", "quickly", "emergency", "critical"]
    SARCASTIC_MARKERS = ["yeah right", "sure", "obviously", "as if", "naturally"]
    FORMAL_MARKERS = ["therefore", "moreover", "nonetheless", "accordingly", "respectfully"]
    
    def __init__(self):
        """Initialize sentiment analyzer."""
        self.analyses: Dict[str, SentimentScore] = {}  # text_hash -> SentimentScore
        self.emotion_history: List[SentimentScore] = []

    def sentiment_analyzer(
        self,
        text: str,
        context: Optional[str] = None,
    ) -> SentimentScore:
        """
        Analyze sentiment and emotional tone of text.

        Args:
            text: Text to analyze
            context: Optional context for better analysis

        Returns:
            SentimentScore with detailed analysis
        """
        # Clean and prepare text
        text_lower = text.lower()
        words = set(text_lower.split())
        
        # Count emotional keywords
        positive_count = len(words & self.POSITIVE_KEYWORDS)
        negative_count = len(words & self.NEGATIVE_KEYWORDS)
        
        # Determine overall sentiment and polarity
        total_emotional = positive_count + negative_count
        if total_emotional == 0:
            overall_sentiment = Sentiment.NEUTRAL
            polarity = 0.0
            confidence = 0.5
        else:
            net_polarity = positive_count - negative_count
            polarity = net_polarity / total_emotional
            
            if polarity > 0.4:
                overall_sentiment = Sentiment.VERY_POSITIVE if polarity > 0.7 else Sentiment.POSITIVE
            elif polarity < -0.4:
                overall_sentiment = Sentiment.VERY_NEGATIVE if polarity < -0.7 else Sentiment.NEGATIVE
            else:
                overall_sentiment = Sentiment.NEUTRAL
            
            confidence = min(0.95, abs(polarity) * 0.9 + 0.1)
        
        # Detect emotions
        emotions = {}
        found_keywords = []
        
        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            emotion_count = len(words & set(keywords))
            if emotion_count > 0:
                emotions[emotion] = min(1.0, emotion_count / len(keywords))
                found_keywords.extend(keywords[:emotion_count])
        
        # Detect tone
        tone = self._detect_tone(text_lower, words)
        
        # Calculate intensity (1-10)
        intensity = max(1, min(10, 3 + int(abs(polarity) * 5)))
        
        # Create score
        score = SentimentScore(
            text=text[:100],  # Store first 100 chars
            overall_sentiment=overall_sentiment,
            confidence=confidence,
            polarity=polarity,
            emotions=emotions,
            keywords=list(set(found_keywords)),
            tone=tone,
            intensity=intensity,
        )
        
        # Store
        text_hash = f"{hash(text) & 0x7fffffff:010d}"
        self.analyses[text_hash] = score
        self.emotion_history.append(score)
        
        return score
    
    def _detect_tone(self, text_lower: str, words: set) -> str:
        """Detect tone of message."""
        if any(marker in text_lower for marker in self.URGENT_MARKERS):
            return "urgent"
        
        if any(marker in text_lower for marker in self.SARCASTIC_MARKERS):
            return "sarcastic"
        
        if any(marker in text_lower for marker in self.FORMAL_MARKERS):
            return "formal"
        
        if "?" in text_lower:
            return "questioning"
        
        if "!" in text_lower:
            return "emphatic"
        
        return "neutral"
    
    def get_dominant_emotion(self, score: SentimentScore) -> Optional[Emotion]:
        """Get dominant emotion from score."""
        if not score.emotions:
            return None
        return max(score.emotions, key=score.emotions.get)
    
    def get_analysis_history(self, limit: int = 10) -> List[SentimentScore]:
        """Get recent analyses."""
        return self.emotion_history[-limit:]
    
    def get_sentiment_trend(self, window: int = 5) -> Dict[str, Any]:
        """Get sentiment trend over recent messages."""
        if len(self.emotion_history) < 1:
            return {
                "trend": "insufficient_data",
                "recent_sentiment": None,
                "avg_polarity": 0.0,
            }
        
        recent = self.emotion_history[-window:]
        sentiments = [s.overall_sentiment for s in recent]
        polarities = [s.polarity for s in recent]
        
        avg_polarity = sum(polarities) / len(polarities) if polarities else 0.0
        
        # Determine trend
        if len(recent) >= 2:
            first_half_avg = sum(s.polarity for s in recent[:len(recent)//2]) / (len(recent)//2) if recent else 0
            second_half_avg = sum(s.polarity for s in recent[len(recent)//2:]) / (len(recent) - len(recent)//2) if recent else 0
            
            if second_half_avg > first_half_avg + 0.2:
                trend = "improving"
            elif second_half_avg < first_half_avg - 0.2:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "single_message"
        
        return {
            "trend": trend,
            "recent_sentiment": sentiments[-1].value if sentiments else None,
            "avg_polarity": avg_polarity,
            "messages_analyzed": len(recent),
        }
    
    def get_emotional_profile(self) -> Dict[str, Any]:
        """Get overall emotional profile from all analyses."""
        if not self.emotion_history:
            return {
                "overall_sentiment": "no_data",
                "avg_polarity": 0.0,
                "dominant_emotions": [],
                "emotion_distribution": {},
            }
        
        # Get average polarity
        avg_polarity = sum(s.polarity for s in self.emotion_history) / len(self.emotion_history)
        
        # Get overall sentiment
        sentiment_counts = {}
        for score in self.emotion_history:
            s = score.overall_sentiment.value
            sentiment_counts[s] = sentiment_counts.get(s, 0) + 1
        
        overall = max(sentiment_counts, key=sentiment_counts.get) if sentiment_counts else "neutral"
        
        # Get emotion distribution
        emotion_totals = {}
        emotion_counts = {}
        for score in self.emotion_history:
            for emotion, value in score.emotions.items():
                emotion_totals[emotion] = emotion_totals.get(emotion, 0) + value
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        emotion_distribution = {
            e.value: emotion_totals.get(e, 0) / emotion_counts.get(e, 1)
            for e in Emotion
        }
        
        return {
            "overall_sentiment": overall,
            "avg_polarity": avg_polarity,
            "messages_analyzed": len(self.emotion_history),
            "emotion_distribution": emotion_distribution,
        }
    
    def export_analyses(self) -> List[Dict[str, Any]]:
        """Export all analyses."""
        return [s.to_dict() for s in self.emotion_history]
