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
        # TODO: Implement
        # Check for domain keywords (career, relationships, health, finance, etc.)
        # If strong match (confidence > 0.7) → return GUIDED (will auto-suggest)
        # Else → return SMALL_TALK (show mode menu)
        pass

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
    # TODO: Implement
    # Check for domain keywords
    # Return top domain + confidence
    pass
