"""
Response generator for language-adapted expert responses.

Generates responses in user's preferred language (English, Hindi, Hinglish),
adapting expert guidance while maintaining meaning and expertise.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from life_brain.conversation.language_detector import (
    LanguageType,
    LanguageDetector,
)


class ResponseTemplate(Enum):
    """Common response templates."""

    GUIDANCE = "guidance"  # Expert advice
    QUESTION = "question"  # Clarifying questions
    CHALLENGE = "challenge"  # Challenge assumptions
    AFFIRMATION = "affirmation"  # Positive reinforcement
    SYNTHESIS = "synthesis"  # Synthesizing perspectives


@dataclass
class LanguageVariant:
    """Language variant of a response."""

    language: LanguageType
    text: str
    is_native: bool = False  # True if originally in this language
    transliteration_style: Optional[str] = None
    tone: str = "neutral"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "language": self.language.value,
            "text": self.text,
            "is_native": self.is_native,
            "transliteration_style": self.transliteration_style,
            "tone": self.tone,
        }


@dataclass
class GeneratedResponse:
    """Generated response with metadata."""

    response_id: str
    user_language: LanguageType
    template_type: ResponseTemplate
    original_text: str
    generated_text: str
    expert_name: str
    variants: List[LanguageVariant] = field(default_factory=list)
    confidence: float = 0.8
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "response_id": self.response_id,
            "user_language": self.user_language.value,
            "template_type": self.template_type.value,
            "original_text": self.original_text,
            "generated_text": self.generated_text,
            "expert_name": self.expert_name,
            "variants": [v.to_dict() for v in self.variants],
            "confidence": self.confidence,
            "generated_at": self.generated_at,
        }


class ResponseGenerator:
    """Generate language-adapted expert responses."""

    # Hinglish conversions - English -> Hinglish
    HINGLISH_CONVERSIONS = {
        "hello": "namaskar / hey",
        "thank you": "shukriya / dhanyavaad",
        "okay": "theek hai / acha",
        "understand": "samjho",
        "agree": "bilkul",
        "but": "par / lekin",
        "and": "aur",
        "please": "please / meherbani se",
        "what": "kya",
        "how": "kaise",
        "why": "kyun",
        "when": "jab",
        "where": "kahan",
        "who": "kaun",
        "i": "main",
        "you": "tum / aap",
        "he": "woh",
        "she": "woh",
        "good": "accha / badhiya",
        "bad": "bura / kharab",
        "important": "zaroori",
        "problem": "masala",
        "solution": "samadhan",
        "try": "try karo",
        "work": "kaam",
        "success": "kamyabi",
        "failure": "nakamyabi",
        "together": "milkar",
        "remember": "yaad rakho",
        "think": "socho",
        "discuss": "discuss karo / baat karo",
        "question": "prashna / sawaal",
        "answer": "jawab / uttar",
    }

    # Hindi common phrases
    HINDI_PHRASES = {
        "hello": "नमस्ते",
        "thank you": "धन्यवाद",
        "okay": "ठीक है",
        "understand": "समझ गया",
        "agree": "बिलकुल",
        "but": "लेकिन",
        "and": "और",
        "please": "कृपया",
        "good": "अच्छा",
        "problem": "समस्या",
        "important": "जरूरी",
        "success": "सफलता",
        "try": "कोशिश करो",
        "think": "सोचो",
        "remember": "याद रखो",
        "question": "सवाल",
        "answer": "जवाब",
    }

    def __init__(self):
        """Initialize response generator."""
        self.generated_responses: Dict[str, GeneratedResponse] = {}
        self.generation_history: List[GeneratedResponse] = []
        self.language_detector = LanguageDetector()

    def generate_response(
        self,
        text: str,
        user_language: LanguageType,
        expert_name: str = "Expert",
        template_type: ResponseTemplate = ResponseTemplate.GUIDANCE,
        response_id: str = "",
    ) -> Tuple[GeneratedResponse, Optional[str]]:
        """
        Generate response adapted to user's language.

        Args:
            text: Original response text
            user_language: User's preferred language
            expert_name: Name of expert providing response
            template_type: Type of response
            response_id: Optional response ID

        Returns:
            (GeneratedResponse, error if any)
        """
        if not text or not text.strip():
            return None, "Empty response text"

        if not response_id:
            response_id = f"resp_{len(self.generated_responses):04d}"

        # Generate adapted response
        if user_language == LanguageType.HINDI:
            adapted_text = self._adapt_to_hindi(text)
            confidence = 0.75
        elif user_language == LanguageType.HINGLISH:
            adapted_text = self._adapt_to_hinglish(text)
            confidence = 0.80
        else:  # ENGLISH
            adapted_text = text
            confidence = 0.95

        # Create generated response
        response = GeneratedResponse(
            response_id=response_id,
            user_language=user_language,
            template_type=template_type,
            original_text=text,
            generated_text=adapted_text,
            expert_name=expert_name,
            confidence=confidence,
        )

        # Generate variants
        response.variants = self._generate_variants(text, expert_name)

        # Store
        self.generated_responses[response_id] = response
        self.generation_history.append(response)

        return response, None

    def _adapt_to_hindi(self, text: str) -> str:
        """Adapt response to Hindi."""
        adapted = text

        # Simple phrase replacements
        for english, hindi in self.HINDI_PHRASES.items():
            # Case-insensitive replacement of whole words
            import re

            pattern = r"\b" + english + r"\b"
            adapted = re.sub(pattern, hindi, adapted, flags=re.IGNORECASE)

        # Add Hindi greeting patterns
        if adapted.lower().startswith("hello"):
            adapted = "नमस्ते" + adapted[5:]

        return adapted

    def _adapt_to_hinglish(self, text: str) -> str:
        """Adapt response to Hinglish."""
        adapted = text

        # Replace some English words with Hinglish
        for english, hinglish in self.HINGLISH_CONVERSIONS.items():
            # Use first variant if multiple
            hinglish_text = hinglish.split("/")[0].strip()

            import re

            pattern = r"\b" + english + r"\b"
            adapted = re.sub(pattern, hinglish_text, adapted, flags=re.IGNORECASE)

        # Add Hinglish particles
        if not adapted.lower().startswith(("acha", "theek", "bilkul")):
            adapted = "Haan toh, " + adapted

        # Add Hinglish ending
        if not adapted.endswith(("?", "!")):
            adapted += " yaar!"
        elif adapted.endswith("?"):
            adapted = adapted[:-1] + " haan?"

        return adapted

    def _generate_variants(
        self, text: str, expert_name: str
    ) -> List[LanguageVariant]:
        """Generate all language variants."""
        variants = []

        # English variant (original)
        variants.append(
            LanguageVariant(
                language=LanguageType.ENGLISH,
                text=text,
                is_native=True,
                tone="professional",
            )
        )

        # Hindi variant
        hindi_text = self._adapt_to_hindi(text)
        variants.append(
            LanguageVariant(
                language=LanguageType.HINDI,
                text=hindi_text,
                is_native=False,
                tone="respectful",
            )
        )

        # Hinglish variant
        hinglish_text = self._adapt_to_hinglish(text)
        variants.append(
            LanguageVariant(
                language=LanguageType.HINGLISH,
                text=hinglish_text,
                is_native=False,
                tone="casual",
            )
        )

        return variants

    def generate_guidance(
        self,
        guidance_text: str,
        user_language: LanguageType,
        expert_name: str = "Expert",
    ) -> Tuple[GeneratedResponse, Optional[str]]:
        """Generate expert guidance in user's language."""
        return self.generate_response(
            guidance_text,
            user_language,
            expert_name,
            ResponseTemplate.GUIDANCE,
        )

    def generate_question(
        self,
        question_text: str,
        user_language: LanguageType,
        expert_name: str = "Expert",
    ) -> Tuple[GeneratedResponse, Optional[str]]:
        """Generate clarifying question in user's language."""
        return self.generate_response(
            question_text,
            user_language,
            expert_name,
            ResponseTemplate.QUESTION,
        )

    def generate_challenge(
        self,
        challenge_text: str,
        user_language: LanguageType,
        expert_name: str = "Expert",
    ) -> Tuple[GeneratedResponse, Optional[str]]:
        """Generate challenging response in user's language."""
        return self.generate_response(
            challenge_text,
            user_language,
            expert_name,
            ResponseTemplate.CHALLENGE,
        )

    def get_response(self, response_id: str) -> Optional[GeneratedResponse]:
        """Get specific generated response."""
        return self.generated_responses.get(response_id)

    def get_variant(
        self, response_id: str, language: LanguageType
    ) -> Optional[LanguageVariant]:
        """Get specific language variant of response."""
        response = self.generated_responses.get(response_id)
        if not response:
            return None

        for variant in response.variants:
            if variant.language == language:
                return variant

        return None

    def export_response(self, response_id: str) -> Optional[Dict[str, Any]]:
        """Export single response."""
        response = self.generated_responses.get(response_id)
        if not response:
            return None
        return response.to_dict()

    def export_all_responses(self) -> List[Dict[str, Any]]:
        """Export all generated responses."""
        return [r.to_dict() for r in self.generation_history]

    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get statistics about response generation."""
        if not self.generation_history:
            return {
                "total_responses": 0,
                "by_language": {},
                "by_template": {},
                "avg_confidence": 0,
            }

        by_language = {}
        by_template = {}
        total_confidence = 0

        for resp in self.generation_history:
            # Count by language
            lang = resp.user_language.value
            by_language[lang] = by_language.get(lang, 0) + 1

            # Count by template
            tmpl = resp.template_type.value
            by_template[tmpl] = by_template.get(tmpl, 0) + 1

            # Sum confidence
            total_confidence += resp.confidence

        avg_confidence = (
            total_confidence / len(self.generation_history)
            if self.generation_history
            else 0
        )

        return {
            "total_responses": len(self.generation_history),
            "by_language": by_language,
            "by_template": by_template,
            "avg_confidence": avg_confidence,
        }

    def batch_generate_responses(
        self,
        texts: List[str],
        user_language: LanguageType,
        expert_name: str = "Expert",
    ) -> Tuple[List[GeneratedResponse], Optional[str]]:
        """Generate multiple responses at once."""
        responses = []

        for text in texts:
            response, error = self.generate_response(
                text, user_language, expert_name
            )
            if response:
                responses.append(response)

        return responses, None

    def adapt_to_language(
        self, text: str, target_language: LanguageType
    ) -> str:
        """Adapt text to target language."""
        if target_language == LanguageType.HINDI:
            return self._adapt_to_hindi(text)
        elif target_language == LanguageType.HINGLISH:
            return self._adapt_to_hinglish(text)
        else:
            return text

    def get_expert_response_style(self, expert_name: str) -> Dict[str, str]:
        """Get typical response style for expert."""
        styles = {
            "Satya": {
                "tone": "encouraging",
                "pattern": "Tell me more about {topic}. Walk me through your thinking.",
            },
            "Richard": {
                "tone": "curious",
                "pattern": "Let's break this down to fundamentals. What does {topic} really mean?",
            },
            "Jeff": {
                "tone": "strategic",
                "pattern": "Think long-term. How does {topic} impact your 10-year vision?",
            },
            "Chris": {
                "tone": "empathetic",
                "pattern": "I understand how you feel about {topic}. Help me understand your perspective.",
            },
            "Andy": {
                "tone": "pragmatic",
                "pattern": "Let's measure {topic}. What are your OKRs?",
            },
        }

        return styles.get(expert_name, {"tone": "neutral", "pattern": "{topic}"})
