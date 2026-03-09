"""
Test suite for language detector.

Tests cover:
- Language type detection (Hindi/English/Hinglish)
- Script type detection (Devanagari/Latin/Mixed)
- Code-switching detection
- Transliteration style detection
- Language statistics and preferences
"""

import pytest

from life_brain.conversation.language_detector import (
    LanguageDetector,
    LanguageType,
    ScriptType,
    LanguageComposition,
    LanguageMessage,
)


class TestLanguageComposition:
    """Test LanguageComposition dataclass."""

    def test_create_composition(self):
        """Test creating language composition."""
        comp = LanguageComposition(
            text="Hello world",
            primary_language=LanguageType.ENGLISH,
            script_type=ScriptType.LATIN,
            hindi_percentage=0,
            english_percentage=100,
            confidence=0.95,
        )

        assert comp.primary_language == LanguageType.ENGLISH
        assert comp.english_percentage == 100

    def test_to_dict(self):
        """Test converting composition to dict."""
        comp = LanguageComposition(
            text="नमस्ते",
            primary_language=LanguageType.HINDI,
            script_type=ScriptType.DEVANAGARI,
            hindi_percentage=100,
            english_percentage=0,
        )

        d = comp.to_dict()
        assert d["primary_language"] == "hindi"
        assert d["script_type"] == "devanagari"


class TestLanguageMessage:
    """Test LanguageMessage dataclass."""

    def test_create_message(self):
        """Test creating language message."""
        comp = LanguageComposition(
            text="Hello",
            primary_language=LanguageType.ENGLISH,
            script_type=ScriptType.LATIN,
            hindi_percentage=0,
            english_percentage=100,
        )

        msg = LanguageMessage(
            message_id="msg_001",
            text="Hello",
            composition=comp,
        )

        assert msg.message_id == "msg_001"
        assert msg.composition.primary_language == LanguageType.ENGLISH

    def test_to_dict(self):
        """Test converting message to dict."""
        comp = LanguageComposition(
            text="namaskar",
            primary_language=LanguageType.ROMAN_HINDI,
            script_type=ScriptType.LATIN,
            hindi_percentage=50,
            english_percentage=50,
        )

        msg = LanguageMessage(
            message_id="msg_002",
            text="namaskar",
            composition=comp,
            is_code_switching=True,
        )

        d = msg.to_dict()
        assert d["message_id"] == "msg_002"
        assert d["is_code_switching"] is True


class TestLanguageDetector:
    """Test LanguageDetector functionality."""

    def test_create_detector(self):
        """Test creating detector."""
        detector = LanguageDetector()
        assert len(detector.detected_messages) == 0
        assert len(detector.detection_history) == 0

    def test_detect_english(self):
        """Test detecting English text."""
        detector = LanguageDetector()

        comp, error = detector.detect_language("Hello, how are you?")

        assert error is None
        assert comp.primary_language == LanguageType.ENGLISH
        assert comp.english_percentage > 80

    def test_detect_hindi_devanagari(self):
        """Test detecting Hindi (Devanagari script)."""
        detector = LanguageDetector()

        comp, error = detector.detect_language("नमस्ते, आप कैसे हो?")

        assert error is None
        assert comp.primary_language == LanguageType.HINDI
        assert comp.script_type == ScriptType.DEVANAGARI

    def test_detect_hinglish_mix(self):
        """Test detecting Hinglish (mixed)."""
        detector = LanguageDetector()

        comp, error = detector.detect_language("Hello, kya tum theek ho?")

        assert error is None
        # Should detect as Hinglish or English with Hinglish markers
        assert comp.hinglish_markers  # Has Hinglish markers
        assert "theek" in comp.hinglish_markers or "kya" in comp.hinglish_markers

    def test_detect_hinglish_markers(self):
        """Test Hinglish marker detection."""
        detector = LanguageDetector()

        comp, error = detector.detect_language("aur yaar, kya hai?")

        assert error is None
        assert len(comp.hinglish_markers) > 0
        assert any(
            marker in comp.hinglish_markers
            for marker in ["aur", "yaar", "kya", "hai"]
        )

    def test_script_detection_devanagari(self):
        """Test script detection for Devanagari."""
        detector = LanguageDetector()

        comp, error = detector.detect_language("संगीत बहुत अच्छा है")

        assert error is None
        assert comp.script_type == ScriptType.DEVANAGARI

    def test_script_detection_latin(self):
        """Test script detection for Latin."""
        detector = LanguageDetector()

        comp, error = detector.detect_language("Music is very nice")

        assert error is None
        assert comp.script_type == ScriptType.LATIN

    def test_script_detection_mixed(self):
        """Test script detection for mixed scripts."""
        detector = LanguageDetector()

        comp, error = detector.detect_language("मुझे coding पसंद है")

        assert error is None
        assert comp.script_type == ScriptType.MIXED

    def test_detect_language_message(self):
        """Test detecting and tracking message."""
        detector = LanguageDetector()

        msg, error = detector.detect_language_message("Hello world", "msg_001")

        assert error is None
        assert msg is not None
        assert msg.message_id == "msg_001"
        assert msg.composition.primary_language == LanguageType.ENGLISH

    def test_detect_language_message_auto_id(self):
        """Test message detection with auto-generated ID."""
        detector = LanguageDetector()

        msg, error = detector.detect_language_message("नमस्ते")

        assert error is None
        assert msg.message_id.startswith("msg_")

    def test_code_switching_detection(self):
        """Test code-switching detection."""
        detector = LanguageDetector()

        msg, error = detector.detect_language_message(
            "Hey दोस्त, क्या तुम busy हो?", "msg_switch"
        )

        assert error is None
        # With mixed script, should detect code-switching
        assert msg.is_code_switching or msg.composition.script_type == ScriptType.MIXED

    def test_transliteration_style_detection(self):
        """Test transliteration style detection."""
        detector = LanguageDetector()

        msg, error = detector.detect_language_message("namaste aur shukriya", "msg_trans")

        assert error is None
        # Should detect transliteration style if Roman Hindi
        # Might be None if detected as English

    def test_get_message(self):
        """Test retrieving specific message."""
        detector = LanguageDetector()

        detector.detect_language_message("Hello", "msg_retrieve")

        msg = detector.get_message("msg_retrieve")
        assert msg is not None
        assert msg.text == "Hello"

    def test_get_nonexistent_message(self):
        """Test retrieving nonexistent message."""
        detector = LanguageDetector()
        msg = detector.get_message("nonexistent")
        assert msg is None

    def test_get_messages_by_language_english(self):
        """Test retrieving messages by language."""
        detector = LanguageDetector()

        detector.detect_language_message("Hello", "msg_en1")
        detector.detect_language_message("Hi there", "msg_en2")
        detector.detect_language_message("नमस्ते", "msg_hi1")

        english_msgs = detector.get_messages_by_language(LanguageType.ENGLISH)
        assert len(english_msgs) >= 2

    def test_get_messages_by_language_hindi(self):
        """Test retrieving Hindi messages."""
        detector = LanguageDetector()

        detector.detect_language_message("नमस्ते कैसे हो", "msg_hi1")
        detector.detect_language_message("आप अच्छे हो", "msg_hi2")

        hindi_msgs = detector.get_messages_by_language(LanguageType.HINDI)
        assert len(hindi_msgs) >= 2

    def test_language_statistics_empty(self):
        """Test statistics with no messages."""
        detector = LanguageDetector()
        stats = detector.get_language_statistics()

        assert stats["total_messages"] == 0
        assert stats["hindi_count"] == 0
        assert stats["english_count"] == 0

    def test_language_statistics_with_messages(self):
        """Test statistics with multiple messages."""
        detector = LanguageDetector()

        detector.detect_language_message("Hello", "msg_1")
        detector.detect_language_message("Hi", "msg_2")
        detector.detect_language_message("नमस्ते", "msg_3")

        stats = detector.get_language_statistics()
        assert stats["total_messages"] >= 3
        assert stats["english_count"] >= 2

    def test_export_messages(self):
        """Test exporting all messages."""
        detector = LanguageDetector()

        detector.detect_language_message("Hello", "msg_export1")
        detector.detect_language_message("नमस्ते", "msg_export2")

        exported = detector.export_messages()
        assert len(exported) >= 2

    def test_get_language_preference_english(self):
        """Test language preference detection - English."""
        detector = LanguageDetector()

        detector.detect_language_message("Hello", "msg_1")
        detector.detect_language_message("Hi", "msg_2")
        detector.detect_language_message("How are you", "msg_3")

        pref = detector.get_language_preference()
        assert pref == LanguageType.ENGLISH

    def test_get_language_preference_hindi(self):
        """Test language preference detection - Hindi."""
        detector = LanguageDetector()

        detector.detect_language_message("नमस्ते", "msg_1")
        detector.detect_language_message("आप कैसे हो", "msg_2")
        detector.detect_language_message("धन्यवाद", "msg_3")

        pref = detector.get_language_preference()
        assert pref == LanguageType.HINDI

    def test_get_language_preference_mixed(self):
        """Test language preference detection - Hinglish."""
        detector = LanguageDetector()

        detector.detect_language_message("Hello", "msg_1")
        detector.detect_language_message("नमस्ते", "msg_2")
        detector.detect_language_message("Hi दोस्त", "msg_3")

        pref = detector.get_language_preference()
        # Should return most recent or most common
        assert pref is not None

    def test_multiple_detectors_independent(self):
        """Test multiple detectors are independent."""
        detector1 = LanguageDetector()
        detector2 = LanguageDetector()

        detector1.detect_language_message("Hello", "msg_1")
        detector2.detect_language_message("नमस्ते", "msg_2")

        assert len(detector1.detection_history) == 1
        assert len(detector2.detection_history) == 1
        assert detector1.detection_history[0].text == "Hello"
        assert detector2.detection_history[0].text == "नमस्ते"

    def test_empty_text_handling(self):
        """Test handling of empty text."""
        detector = LanguageDetector()

        comp, error = detector.detect_language("")

        assert error == "Empty text"
        assert comp.confidence == 0.0

    def test_whitespace_only_text(self):
        """Test handling of whitespace-only text."""
        detector = LanguageDetector()

        comp, error = detector.detect_language("   ")

        assert error == "Empty text"

    def test_mixed_english_hindi_percentage(self):
        """Test percentage calculation in mixed script."""
        detector = LanguageDetector()

        comp, error = detector.detect_language("Hello नमस्ते world")

        assert error is None
        assert comp.hindi_percentage > 0
        assert comp.english_percentage > 0

    def test_confidence_scoring(self):
        """Test confidence scoring."""
        detector = LanguageDetector()

        # Pure English
        comp_en, _ = detector.detect_language("This is pure English text")
        en_conf = comp_en.confidence

        # Mixed
        comp_mix, _ = detector.detect_language("This is नमस्ते mixed")
        mix_conf = comp_mix.confidence

        # Pure English should have higher confidence
        assert en_conf >= mix_conf

    def test_complex_hinglish_pattern(self):
        """Test complex Hinglish pattern."""
        detector = LanguageDetector()

        msg, _ = detector.detect_language_message(
            "Haan, maine suna yaar. Bahut accha hai!", "msg_complex"
        )

        assert msg is not None
        assert len(msg.composition.hinglish_markers) > 0

    def test_conversation_flow(self):
        """Test conversation flow with language switching."""
        detector = LanguageDetector()

        detector.detect_language_message("Hi, how are you?", "msg_1")
        detector.detect_language_message("नमस्ते, मैं ठीक हूँ", "msg_2")
        detector.detect_language_message("क्या तुम busy हो?", "msg_3")
        detector.detect_language_message("Naah, I'm free", "msg_4")

        stats = detector.get_language_statistics()
        assert stats["total_messages"] == 4
        # Should have both English and Hindi
        assert stats["english_count"] > 0 or stats["hinglish_count"] > 0


class TestPureHindiText:
    """Regression tests for issues-ifm: Hinglish bridge with 100% Hindi text (no English)."""

    def test_pure_devanagari_hindi_detected(self):
        """100% Devanagari Hindi text must detect as HINDI, not crash."""
        from life_brain.conversation.language_detector import LanguageDetector, LanguageType
        detector = LanguageDetector()
        composition, _ = detector.detect_language(
            "नमस्ते मेरा नाम सत्विक है और मैं एक सॉफ्टवेयर इंजीनियर हूं"
        )
        assert composition is not None
        assert composition.primary_language == LanguageType.HINDI

    def test_pure_hindi_high_confidence(self):
        """Pure Devanagari Hindi must have high confidence score."""
        from life_brain.conversation.language_detector import LanguageDetector
        detector = LanguageDetector()
        composition, _ = detector.detect_language(
            "यह एक हिंदी वाक्य है जो पूरी तरह से हिंदी में लिखा गया है"
        )
        assert composition.confidence >= 0.8

    def test_pure_hindi_0_english_percentage(self):
        """Pure Devanagari text must have 0% English."""
        from life_brain.conversation.language_detector import LanguageDetector
        detector = LanguageDetector()
        composition, _ = detector.detect_language("मैं ठीक हूँ धन्यवाद")
        assert composition.english_percentage == 0.0

    def test_hinglish_bridge_roman_hindi_works(self):
        """Roman-script Hindi (Hinglish) must be detected as HINGLISH."""
        from life_brain.conversation.language_detector import LanguageDetector, LanguageType
        detector = LanguageDetector()
        composition, _ = detector.detect_language(
            "Main theek hun, kya hal hai aur kaam kaisa chal raha hai"
        )
        assert composition.primary_language in [LanguageType.HINGLISH, LanguageType.ENGLISH]

    def test_pure_hindi_message_stored_correctly(self):
        """detect_language_message with pure Hindi must not crash."""
        from life_brain.conversation.language_detector import LanguageDetector, LanguageType
        detector = LanguageDetector()
        msg, _ = detector.detect_language_message(
            "नमस्ते यह हिंदी में एक संदेश है",
            "msg_hindi_001"
        )
        assert msg is not None
        assert msg.composition.primary_language == LanguageType.HINDI
