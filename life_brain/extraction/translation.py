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
   - "hona chahiye" → "should be"
   - "kar raha hun" → progressive tense
4. Output: pure English, ready for embedding models

ORIGINAL (Hinglish):
{hinglish_text}

TRANSLATION (English):
"""

ENGLISH_TO_HINGLISH_PROMPT = """
Translate this English text back to casual Hinglish for a friendly conversation.

RULES:
1. Use conversational Hinglish (mixture of Hindi + English)
2. Preserve technical terms exactly as-is: {preserved_terms}
3. Make it sound like a natural conversation, not formal
4. Preserve all metrics and numbers
5. Use Hinglish particles: "kya", "par", "kitna", "hona chahiye", etc.

ORIGINAL (English):
{english_text}

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
        # Quick check: if no Hindi characters, likely already English
        if not any(ord(c) > 127 for c in hinglish_text):
            return hinglish_text

        try:
            prompt = HINGLISH_TO_ENGLISH_PROMPT.format(
                preserved_terms=self.preserved_terms,
                hinglish_text=hinglish_text
            )

            response = self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            english_text = response.content[0].text.strip()

            # Verify preserved terms weren't modified
            self.preserve_technical_terms(english_text)

            return english_text

        except Exception as e:
            # On error, return original text
            return hinglish_text

    def english_to_hinglish(self, english_text: str) -> str:
        """
        Translate English (from ChromaDB) back to Hinglish for user.

        Args:
            english_text: Text from ChromaDB or LLM output

        Returns:
            Hinglish conversation text
        """
        try:
            prompt = ENGLISH_TO_HINGLISH_PROMPT.format(
                preserved_terms=self.preserved_terms,
                english_text=english_text
            )

            response = self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            hinglish_text = response.content[0].text.strip()

            # Verify preserved terms are intact
            self.preserve_technical_terms(hinglish_text)

            return hinglish_text

        except Exception as e:
            # On error, return original text
            return english_text

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
        import logging

        logger = logging.getLogger(__name__)
        missing_terms = []

        for term in PRESERVED_TERMS:
            if term.lower() not in text.lower():
                missing_terms.append(term)

        if missing_terms:
            logger.warning(f"Preserved terms may have been modified: {missing_terms}")

        return text


# Singleton instance
_translator: Optional[TranslationLayer] = None


def get_translator() -> TranslationLayer:
    """Get or create translation layer singleton."""
    global _translator
    if _translator is None:
        _translator = TranslationLayer()
    return _translator
