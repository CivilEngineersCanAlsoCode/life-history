"""
Language detector for Hindi/English/Hinglish identification.

Detects language composition, script type, code-switching patterns,
and transliteration styles in user messages.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re


class LanguageType(Enum):
    """Language types."""

    HINDI = "hindi"  # Pure Hindi (Devanagari script)
    ENGLISH = "english"  # Pure English (Latin script)
    HINGLISH = "hinglish"  # Hindi-English mix
    ROMAN_HINDI = "roman_hindi"  # Hindi in Latin characters


class ScriptType(Enum):
    """Script types."""

    DEVANAGARI = "devanagari"  # Hindi script
    LATIN = "latin"  # English/Roman
    MIXED = "mixed"  # Mix of scripts


@dataclass
class LanguageComposition:
    """Language composition analysis."""

    text: str
    primary_language: LanguageType
    script_type: ScriptType
    hindi_percentage: float  # 0-100
    english_percentage: float  # 0-100
    hinglish_markers: List[str] = field(default_factory=list)
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())
    confidence: float = 0.8  # 0-1 scale

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "primary_language": self.primary_language.value,
            "script_type": self.script_type.value,
            "hindi_percentage": self.hindi_percentage,
            "english_percentage": self.english_percentage,
            "hinglish_markers": self.hinglish_markers,
            "detected_at": self.detected_at,
            "confidence": self.confidence,
        }


@dataclass
class LanguageMessage:
    """Message with language metadata."""

    message_id: str
    text: str
    composition: LanguageComposition
    is_code_switching: bool = False
    transliteration_style: Optional[str] = None
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "message_id": self.message_id,
            "text": self.text,
            "composition": self.composition.to_dict(),
            "is_code_switching": self.is_code_switching,
            "transliteration_style": self.transliteration_style,
            "detected_at": self.detected_at,
        }


class LanguageDetector:
    """Detect language composition in messages."""

    # Devanagari character ranges
    DEVANAGARI_START = 0x0900
    DEVANAGARI_END = 0x097F

    # Hinglish markers and code-switch patterns
    HINGLISH_PARTICLES = [
        "hai",  # is
        "hain",  # are
        "kya",  # what
        "toh",  # then
        "par",  # but
        "aur",  # and
        "ki",  # of
        "ne",  # verb particle
        "ko",  # to/object
        "se",  # from
        "ab",  # now
        "yaar",  # friend/buddy
        "bas",  # just/only
        "dekho",  # see
        "suno",  # listen
        "jhooth",  # lie
        "sach",  # truth
        "samjho",  # understand
    ]

    # Common Hinglish word patterns
    ROMAN_HINDI_WORDS = [
        r"\bhello\b",  # English
        r"\bnamaskar\b",  # Hindi transliterated
        r"\bvanakkam\b",  # Tamil transliterated
        r"\bsup\b",  # Slang English
        r"\bacha\b",  # okay (Hindi)
        r"\btheek\b",  # okay (Hindi)
        r"\bshukriya\b",  # thanks (Urdu-Hindi)
        r"\bdhanyavaad\b",  # thanks (Sanskrit)
    ]

    def __init__(self):
        """Initialize language detector."""
        self.detected_messages: Dict[str, LanguageMessage] = {}
        self.detection_history: List[LanguageMessage] = []

    def detect_language(self, text: str, message_id: str = "") -> Tuple[
        LanguageComposition, Optional[str]
    ]:
        """
        Detect language composition in text.

        Args:
            text: Text to analyze
            message_id: Unique message ID

        Returns:
            (LanguageComposition, error if any)
        """
        if not text or not text.strip():
            return (
                LanguageComposition(
                    text=text,
                    primary_language=LanguageType.ENGLISH,
                    script_type=ScriptType.LATIN,
                    hindi_percentage=0,
                    english_percentage=0,
                    confidence=0.0,
                ),
                "Empty text",
            )

        # Analyze script composition
        script_info = self._analyze_scripts(text)
        script_type = script_info["script_type"]

        # Detect language based on script
        if script_type == ScriptType.DEVANAGARI:
            composition = self._analyze_hindi(text, script_info)
        elif script_type == ScriptType.LATIN:
            composition = self._analyze_english_hinglish(text, script_info)
        else:  # MIXED
            composition = self._analyze_mixed(text, script_info)

        return composition, None

    def detect_language_message(
        self, text: str, message_id: str = ""
    ) -> Tuple[Optional[LanguageMessage], Optional[str]]:
        """
        Detect language and track message.

        Args:
            text: Message text
            message_id: Unique message ID (auto-generated if empty)

        Returns:
            (LanguageMessage, error if any)
        """
        if not message_id:
            message_id = f"msg_{len(self.detected_messages):04d}"

        composition, error = self.detect_language(text, message_id)
        if error:
            return None, error

        # Check for code-switching
        is_code_switching = self._detect_code_switching(text, composition)

        # Detect transliteration style
        transliteration_style = self._detect_transliteration_style(text, composition)

        message = LanguageMessage(
            message_id=message_id,
            text=text,
            composition=composition,
            is_code_switching=is_code_switching,
            transliteration_style=transliteration_style,
        )

        self.detected_messages[message_id] = message
        self.detection_history.append(message)

        return message, None

    def _analyze_scripts(self, text: str) -> Dict[str, Any]:
        """Analyze script composition."""
        devanagari_count = 0
        latin_count = 0

        for char in text:
            code_point = ord(char)
            if self.DEVANAGARI_START <= code_point <= self.DEVANAGARI_END:
                devanagari_count += 1
            elif char.isascii() and char.isalpha():
                latin_count += 1

        total_chars = devanagari_count + latin_count

        if total_chars == 0:
            return {
                "script_type": ScriptType.LATIN,
                "devanagari_percentage": 0,
                "latin_percentage": 0,
            }

        devanagari_pct = (devanagari_count / total_chars) * 100
        latin_pct = (latin_count / total_chars) * 100

        if devanagari_pct > 80:
            script_type = ScriptType.DEVANAGARI
        elif latin_pct > 80:
            script_type = ScriptType.LATIN
        else:
            script_type = ScriptType.MIXED

        return {
            "script_type": script_type,
            "devanagari_percentage": devanagari_pct,
            "latin_percentage": latin_pct,
        }

    def _analyze_hindi(self, text: str, script_info: Dict) -> LanguageComposition:
        """Analyze Hindi content (Devanagari script)."""
        hinglish_markers = self._find_hinglish_markers(text)

        composition = LanguageComposition(
            text=text,
            primary_language=LanguageType.HINDI,
            script_type=ScriptType.DEVANAGARI,
            hindi_percentage=script_info["devanagari_percentage"],
            english_percentage=script_info["latin_percentage"],
            hinglish_markers=hinglish_markers,
            confidence=0.95 if script_info["devanagari_percentage"] > 90 else 0.85,
        )

        return composition

    def _analyze_english_hinglish(
        self, text: str, script_info: Dict
    ) -> LanguageComposition:
        """Analyze English or Roman Hindi content."""
        hinglish_markers = self._find_hinglish_markers(text)
        is_roman_hindi = self._is_roman_hindi(text, hinglish_markers)

        if is_roman_hindi and hinglish_markers:
            language_type = LanguageType.HINGLISH
            hindi_pct = len(hinglish_markers) * 15  # Rough estimate
            hindi_pct = min(hindi_pct, 50)  # Cap at 50%
            english_pct = 100 - hindi_pct
        else:
            language_type = LanguageType.ENGLISH
            hindi_pct = 10 if hinglish_markers else 0
            english_pct = 100 - hindi_pct

        composition = LanguageComposition(
            text=text,
            primary_language=language_type,
            script_type=ScriptType.LATIN,
            hindi_percentage=hindi_pct,
            english_percentage=english_pct,
            hinglish_markers=hinglish_markers,
            confidence=0.9 if hinglish_markers else 0.95,
        )

        return composition

    def _analyze_mixed(self, text: str, script_info: Dict) -> LanguageComposition:
        """Analyze mixed script content."""
        hinglish_markers = self._find_hinglish_markers(text)

        composition = LanguageComposition(
            text=text,
            primary_language=LanguageType.HINGLISH,
            script_type=ScriptType.MIXED,
            hindi_percentage=script_info["devanagari_percentage"],
            english_percentage=script_info["latin_percentage"],
            hinglish_markers=hinglish_markers,
            confidence=0.85,
        )

        return composition

    def _find_hinglish_markers(self, text: str) -> List[str]:
        """Find Hinglish markers in text."""
        markers = []
        text_lower = text.lower()

        for marker in self.HINGLISH_PARTICLES:
            pattern = r"\b" + marker + r"\b"
            if re.search(pattern, text_lower):
                markers.append(marker)

        return markers[:5]  # Return top 5

    def _is_roman_hindi(self, text: str, markers: List[str]) -> bool:
        """Check if text is Roman Hindi (Hindi words in Latin script)."""
        if not markers:
            return False

        # If has Hinglish markers, likely Roman Hindi
        marker_count = len(markers)
        words = text.split()

        # If marker words make up >10% of text, likely Roman Hindi
        if marker_count > len(words) * 0.1:
            return True

        return marker_count >= 2

    def _detect_code_switching(
        self, text: str, composition: LanguageComposition
    ) -> bool:
        """Detect code-switching (alternating between languages)."""
        # Code-switching happens when switching between languages within sentences
        words = text.split()

        if len(words) < 4:
            return False

        hindi_words = 0
        english_words = 0

        for word in words:
            has_devanagari = any(
                self.DEVANAGARI_START <= ord(c) <= self.DEVANAGARI_END for c in word
            )
            has_latin = any(c.isascii() and c.isalpha() for c in word)

            if has_devanagari:
                hindi_words += 1
            if has_latin:
                english_words += 1

        # Code-switching: both languages present and relatively balanced
        if hindi_words > 0 and english_words > 0:
            ratio = min(hindi_words, english_words) / max(hindi_words, english_words)
            return ratio > 0.2  # At least 20% of each language

        return False

    def _detect_transliteration_style(
        self, text: str, composition: LanguageComposition
    ) -> Optional[str]:
        """Detect transliteration style (IAST, HK, ITrans, etc)."""
        if composition.primary_language != LanguageType.ROMAN_HINDI:
            return None

        text_lower = text.lower()

        # Simple heuristics for different transliteration styles
        if "ã" in text_lower or "ī" in text_lower or "ū" in text_lower:
            return "IAST"  # International Alphabet of Sanskrit Transliteration
        elif "aa" in text_lower or "ii" in text_lower:
            return "HK"  # Harvard-Kyoto
        elif "ch" in text_lower and "sh" in text_lower:
            return "ITrans"  # ITRANS
        else:
            return "Simple"  # Simple Latin representation

    def get_message(self, message_id: str) -> Optional[LanguageMessage]:
        """Get specific detected message."""
        return self.detected_messages.get(message_id)

    def get_messages_by_language(self, language: LanguageType) -> List[LanguageMessage]:
        """Get all messages of specific language."""
        return [
            m
            for m in self.detection_history
            if m.composition.primary_language == language
        ]

    def get_language_statistics(self) -> Dict[str, Any]:
        """Get statistics about detected languages."""
        if not self.detection_history:
            return {
                "total_messages": 0,
                "hindi_count": 0,
                "english_count": 0,
                "hinglish_count": 0,
                "code_switching_count": 0,
                "avg_hindi_percentage": 0,
            }

        hindi_count = 0
        english_count = 0
        hinglish_count = 0
        code_switching_count = 0
        total_hindi_pct = 0

        for msg in self.detection_history:
            if msg.composition.primary_language == LanguageType.HINDI:
                hindi_count += 1
            elif msg.composition.primary_language == LanguageType.ENGLISH:
                english_count += 1
            elif msg.composition.primary_language == LanguageType.HINGLISH:
                hinglish_count += 1

            if msg.is_code_switching:
                code_switching_count += 1

            total_hindi_pct += msg.composition.hindi_percentage

        return {
            "total_messages": len(self.detection_history),
            "hindi_count": hindi_count,
            "english_count": english_count,
            "hinglish_count": hinglish_count,
            "code_switching_count": code_switching_count,
            "avg_hindi_percentage": (
                total_hindi_pct / len(self.detection_history)
                if self.detection_history
                else 0
            ),
        }

    def export_messages(self) -> List[Dict[str, Any]]:
        """Export all detected messages."""
        return [m.to_dict() for m in self.detection_history]

    def get_language_preference(self) -> Optional[LanguageType]:
        """Get user's preferred language based on detection history."""
        if not self.detection_history:
            return None

        stats = self.get_language_statistics()

        if stats["hindi_count"] > stats["english_count"]:
            return LanguageType.HINDI
        elif stats["english_count"] > stats["hindi_count"]:
            return LanguageType.ENGLISH
        elif stats["hinglish_count"] > 0:
            return LanguageType.HINGLISH
        else:
            return self.detection_history[-1].composition.primary_language
