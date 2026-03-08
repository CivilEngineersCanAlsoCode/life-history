"""Tests for extraction/translation.py — Hinglish ↔ English translation layer."""

import pytest
from unittest.mock import MagicMock, patch

from life_brain.extraction.translation import (
    TranslationLayer,
    get_translator,
    HINGLISH_TO_ENGLISH_PROMPT,
    ENGLISH_TO_HINGLISH_PROMPT,
)
from life_brain.config import PRESERVED_TERMS


def make_mock_response(text: str):
    """Create a mock Anthropic API response."""
    content = MagicMock()
    content.text = text
    response = MagicMock()
    response.content = [content]
    return response


@pytest.fixture
def mock_client():
    with patch("life_brain.extraction.translation.Anthropic") as MockAnthropic:
        client = MagicMock()
        MockAnthropic.return_value = client
        yield client


@pytest.fixture
def translator(mock_client):
    return TranslationLayer()


# ── hinglish_to_english ─────────────────────────────────────────────────────

class TestHinglishToEnglish:
    def test_pure_english_skips_api(self, translator, mock_client):
        # Pure ASCII text should bypass API call
        result = translator.hinglish_to_english("What is AML risk?")
        mock_client.messages.create.assert_not_called()
        assert result == "What is AML risk?"

    def test_hindi_chars_triggers_api(self, translator, mock_client):
        mock_client.messages.create.return_value = make_mock_response("AML risk score")
        result = translator.hinglish_to_english("AML का risk score क्या है?")
        mock_client.messages.create.assert_called_once()
        assert result == "AML risk score"

    def test_api_error_returns_original(self, translator, mock_client):
        mock_client.messages.create.side_effect = Exception("API down")
        original = "AML का risk क्या है?"
        result = translator.hinglish_to_english(original)
        assert result == original

    def test_prompt_contains_preserved_terms(self, translator, mock_client):
        mock_client.messages.create.return_value = make_mock_response("translated")
        translator.hinglish_to_english("CRR का risk क्या है?")
        call_args = mock_client.messages.create.call_args
        prompt = call_args[1]["messages"][0]["content"]
        # At least some preserved terms should appear in prompt
        assert any(term in prompt for term in PRESERVED_TERMS)


# ── english_to_hinglish ─────────────────────────────────────────────────────

class TestEnglishToHinglish:
    def test_calls_api(self, translator, mock_client):
        mock_client.messages.create.return_value = make_mock_response("CRR risk kaafi high hai")
        result = translator.english_to_hinglish("The CRR risk is very high.")
        mock_client.messages.create.assert_called_once()
        assert result == "CRR risk kaafi high hai"

    def test_api_error_returns_original(self, translator, mock_client):
        mock_client.messages.create.side_effect = Exception("API down")
        original = "The CRR score is high."
        result = translator.english_to_hinglish(original)
        assert result == original

    def test_prompt_has_preserved_terms(self, translator, mock_client):
        mock_client.messages.create.return_value = make_mock_response("kuch bhi")
        translator.english_to_hinglish("AML compliance is key.")
        call_args = mock_client.messages.create.call_args
        prompt = call_args[1]["messages"][0]["content"]
        assert any(term in prompt for term in PRESERVED_TERMS)


# ── translate_query ─────────────────────────────────────────────────────────

class TestTranslateQuery:
    def test_pure_english_no_api_call(self, translator, mock_client):
        result = translator.translate_query("What is AML?")
        mock_client.messages.create.assert_not_called()
        assert result == "What is AML?"

    def test_hindi_query_calls_api(self, translator, mock_client):
        mock_client.messages.create.return_value = make_mock_response("What is AML?")
        result = translator.translate_query("AML क्या होता है?")
        mock_client.messages.create.assert_called_once()
        assert result == "What is AML?"


# ── preserve_technical_terms ────────────────────────────────────────────────

class TestPreserveTechnicalTerms:
    def test_returns_text_unchanged(self, translator):
        text = "The AML and CRR systems are fine."
        result = translator.preserve_technical_terms(text)
        assert result == text

    def test_all_terms_present_no_warning(self, translator, caplog):
        # Build text that contains all preserved terms
        text = " ".join(PRESERVED_TERMS)
        with caplog.at_level("WARNING"):
            translator.preserve_technical_terms(text)
        assert "Preserved terms may have been modified" not in caplog.text

    def test_missing_term_logs_warning(self, translator, caplog):
        # Text that contains none of the preserved terms
        with caplog.at_level("WARNING"):
            translator.preserve_technical_terms("unrelated blah blah text here foo bar")
        # Should log a warning about missing terms
        assert "Preserved terms may have been modified" in caplog.text


# ── Prompt templates ────────────────────────────────────────────────────────

class TestPromptTemplates:
    def test_hinglish_prompt_has_placeholders(self):
        # Should be formattable with required keys
        filled = HINGLISH_TO_ENGLISH_PROMPT.format(
            preserved_terms="CRR, AML",
            hinglish_text="kuch bhi"
        )
        assert "CRR, AML" in filled
        assert "kuch bhi" in filled

    def test_english_prompt_has_placeholders(self):
        filled = ENGLISH_TO_HINGLISH_PROMPT.format(
            preserved_terms="CRR, AML",
            english_text="something in english"
        )
        assert "CRR, AML" in filled
        assert "something in english" in filled


# ── get_translator singleton ────────────────────────────────────────────────

class TestGetTranslator:
    def test_singleton(self):
        with patch("life_brain.extraction.translation.Anthropic"):
            import life_brain.extraction.translation as mod
            # Reset singleton
            mod._translator = None
            t1 = get_translator()
            t2 = get_translator()
            assert t1 is t2
            # Cleanup
            mod._translator = None

    def test_returns_translation_layer(self):
        with patch("life_brain.extraction.translation.Anthropic"):
            import life_brain.extraction.translation as mod
            mod._translator = None
            t = get_translator()
            assert isinstance(t, TranslationLayer)
            mod._translator = None


# ── PRESERVED_TERMS config ──────────────────────────────────────────────────

class TestPreservedTermsConfig:
    def test_is_list(self):
        assert isinstance(PRESERVED_TERMS, list)

    def test_contains_core_terms(self):
        assert "CRR" in PRESERVED_TERMS
        assert "AML" in PRESERVED_TERMS
        assert "API" in PRESERVED_TERMS
        assert "Sprinklr" in PRESERVED_TERMS
        assert "AmEx" in PRESERVED_TERMS
