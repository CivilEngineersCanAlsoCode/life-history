"""
Mode Gate — Detect whether user wants small talk or guided structured conversation.

Also: Intent detection to proactively suggest experts even in small talk.
"""

from typing import Optional, Tuple
from enum import Enum
from anthropic import Anthropic


class Mode(str, Enum):
    SMALL_TALK = "small_talk"
    GUIDED = "guided"


class IntentDetector:
    """Detects user intent and suggests relevant experts."""

    def __init__(self):
        self.client = Anthropic()

    def detect_mode(self, user_message: str) -> Mode:
        """
        Detect if user wants small talk or structured guidance.

        Logic:
          - If message has strong keywords (interview, salary, relationship, health)
            → suggest use case directly (GUIDED implicit)
          - Else → ask user to choose [A] Bas baatein [B] Kuch record karna

        Args:
            user_message: User's opening message

        Returns:
            Mode.SMALL_TALK or Mode.GUIDED
        """
        domain, confidence = detect_keywords_simple(user_message)
        if confidence > 0.7:
            return Mode.GUIDED
        else:
            return Mode.SMALL_TALK

    def detect_intent(self, small_talk_message: str) -> Tuple[Optional[str], float]:
        """
        Detect use case from small talk (even casual messages).

        Args:
            small_talk_message: User's casual message

        Returns:
            Tuple of (use_case_id, confidence) or (None, 0.0) if no match
        """
        # TODO: Implement
        # Match message to USE_CASES using semantic similarity
        # Return top match with confidence score
        # confidence > 0.7 → suggest expert (but only once, never repeat)
        pass

    def should_suggest_expert(self, intent_confidence: float) -> bool:
        """
        Determine if we should suggest an expert.

        Args:
            intent_confidence: Confidence score from detect_intent

        Returns:
            True if should suggest (confidence > 0.7 and not suggested before)
        """
        # TODO: Implement
        # Check: confidence > 0.7
        # Check: haven't suggested in this session
        # Return boolean
        pass

    def format_mode_prompt() -> str:
        """
        Format the mode selection prompt for user.

        Returns:
            Hinglish prompt: "Kya chal raha hai? [A] Bas baatein [B] Kuch record karna"
        """
        # TODO: Implement
        return """
Kya chal raha hai?

[A] Bas baatein (Free talk — passive capture, confidence: 0.6)
[B] Kuch record karna (Guided — structured with expert)

Select A or B:
        """.strip()


def detect_keywords_simple(message: str) -> Tuple[str, float]:
    """
    Simple keyword-based intent detection (fallback).

    Returns:
        Tuple of (domain, confidence)
    """
    msg_lower = message.lower()

    # Domain keywords (domain -> keywords list)
    keywords_map = {
        "career": ["interview", "job", "role", "position", "project", "promotion", "boss", "manager", "work", "salary", "offer", "raise", "skill"],
        "relationships": ["friend", "boyfriend", "girlfriend", "wife", "husband", "partner", "conflict", "breakup", "family", "relationship"],
        "health": ["health", "fitness", "sleep", "diet", "anxiety", "stress", "energy", "mental", "exercise", "wellness"],
        "finance": ["money", "investment", "budget", "loan", "spend", "save", "financial", "expense", "income"],
        "goals": ["goal", "dream", "plan", "achieve", "ambition", "target"],
        "personal_growth": ["learn", "grow", "improve", "change", "habit", "skill", "strength", "weakness"],
    }

    # Score each domain
    scores = {}
    for domain, keywords in keywords_map.items():
        matches = sum(1 for kw in keywords if kw in msg_lower)
        scores[domain] = matches

    # Get top domain
    if sum(scores.values()) == 0:
        return ("none", 0.0)  # No keywords found

    top_domain = max(scores, key=scores.get)
    max_matches = scores[top_domain]
    total_keywords = sum(len(kws) for kws in keywords_map.values())

    # Confidence: max_matches / total_keywords (or 0.7+ if strong match)
    confidence = max_matches / 10.0  # Heuristic: 3+ matches → 0.3+, 7+ → 0.7+
    confidence = min(confidence, 1.0)

    return (top_domain, confidence)
