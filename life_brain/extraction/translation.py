"""
Hinglish ↔ English translation layer.

User speaks Hinglish → Silent translation to English for ChromaDB
Query retrieval in English → Silent translation back to Hinglish for user

Technical terms (CRR, AML, API, Sprinklr) preserved as-is.
"""

from typing import Optional, List
import os
from anthropic import Anthropic

from life_brain.config import PRESERVED_TERMS


# Translation prompts
HINGLISH_TO_ENGLISH_PROMPT = """
Translate this Hinglish (Hindi-English mix) text to professional English.

RULES:
1. Preserve EXACTLY these technical terms — do NOT translate:
   {preserved_terms}
2. Preserve all numbers and metrics exactly
3. Convert casual Hinglish markers to English equivalents:
   - "kya" → question marks
   - "par" → "but"
   - "kitna" → "how much"
   - "CGB mein" → "In CGB"
4. Output: pure English, ready for embedding models

ORIGINAL (Hinglish):
{original_text}

TRANSLATION (English):
"""

ENGLISH_TO_HINGLISH_PROMPT = """
Translate this English text back to casual Hinglish for a friendly conversation.

RULES:
1. Use conversational Hinglish (mixture of Hindi + English)
2. Preserve technical terms exactly as-is: {preserved_terms}
3. Make it sound like a natural conversation, not formal
4. Preserve all metrics and numbers

ORIGINAL (English):
{original_text}

TRANSLATION (Hinglish):
"""


class TranslationLayer:
    """Manages Hinglish ↔ English translation."""

    def __init__(self):
        self.client = Anthropic()
        self.preserved_terms = ", ".join(PRESERVED_TERMS)

    def hinglish_to_english(self, hinglish_text: str) -> str:
        """
        Translate Hinglish input to English for ChromaDB storage.

        Args:
            hinglish_text: User input in Hinglish

        Returns:
            English translation ready for embedding
        """
        # TODO: Implement
        # 1. Call Claude API with HINGLISH_TO_ENGLISH_PROMPT
        # 2. Preserve technical terms (check against PRESERVED_TERMS)
        # 3. Return English text
        pass

    def english_to_hinglish(self, english_text: str) -> str:
        """
        Translate English (from ChromaDB) back to Hinglish for user.

        Args:
            english_text: Text from ChromaDB or LLM output

        Returns:
            Hinglish conversation text
        """
        # TODO: Implement
        # 1. Call Claude API with ENGLISH_TO_HINGLISH_PROMPT
        # 2. Make it conversational and friendly
        # 3. Preserve technical terms
        # 4. Return Hinglish
        pass

    def translate_query(self, hinglish_query: str) -> str:
        """
        Translate query text for ChromaDB retrieval.

        Args:
            hinglish_query: User's question in Hinglish

        Returns:
            English query ready for semantic search
        """
        # Reuse hinglish_to_english
        return self.hinglish_to_english(hinglish_query)

    def preserve_technical_terms(self, text: str) -> str:
        """
        Ensure technical terms from PRESERVED_TERMS are not modified.

        Args:
            text: Text to check

        Returns:
            Text with preserved terms intact
        """
        # TODO: Implement
        # Verify all PRESERVED_TERMS appear unchanged in text
        # If any are missing/modified, log warning
        pass


# Singleton instance
_translator: Optional[TranslationLayer] = None


def get_translator() -> TranslationLayer:
    """Get or create translation layer singleton."""
    global _translator
    if _translator is None:
        _translator = TranslationLayer()
    return _translator
