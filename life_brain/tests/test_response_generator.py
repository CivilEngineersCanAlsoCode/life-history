"""
Test suite for response generator.

Tests cover:
- Language-adapted responses (English/Hindi/Hinglish)
- Response templates and types
- Language variants
- Batch generation
- Expert response styles
- Statistics and exports
"""

import pytest

from life_brain.conversation.response_generator import (
    ResponseGenerator,
    LanguageType,
    ResponseTemplate,
    LanguageVariant,
    GeneratedResponse,
)


class TestLanguageVariant:
    """Test LanguageVariant dataclass."""

    def test_create_variant(self):
        """Test creating language variant."""
        variant = LanguageVariant(
            language=LanguageType.ENGLISH,
            text="Hello, how are you?",
            is_native=True,
            tone="friendly",
        )

        assert variant.language == LanguageType.ENGLISH
        assert variant.is_native is True

    def test_to_dict(self):
        """Test converting variant to dict."""
        variant = LanguageVariant(
            language=LanguageType.HINDI,
            text="नमस्ते",
            is_native=False,
            tone="respectful",
        )

        d = variant.to_dict()
        assert d["language"] == "hindi"
        assert d["tone"] == "respectful"


class TestGeneratedResponse:
    """Test GeneratedResponse dataclass."""

    def test_create_response(self):
        """Test creating generated response."""
        response = GeneratedResponse(
            response_id="resp_001",
            user_language=LanguageType.ENGLISH,
            template_type=ResponseTemplate.GUIDANCE,
            original_text="Practice makes perfect",
            generated_text="Practice makes perfect",
            expert_name="Satya",
        )

        assert response.response_id == "resp_001"
        assert response.template_type == ResponseTemplate.GUIDANCE

    def test_to_dict(self):
        """Test converting response to dict."""
        response = GeneratedResponse(
            response_id="resp_002",
            user_language=LanguageType.HINGLISH,
            template_type=ResponseTemplate.CHALLENGE,
            original_text="Question your assumptions",
            generated_text="Apne assumptions ko question karo yaar!",
            expert_name="Richard",
        )

        d = response.to_dict()
        assert d["response_id"] == "resp_002"
        assert d["user_language"] == "hinglish"


class TestResponseGenerator:
    """Test ResponseGenerator functionality."""

    def test_create_generator(self):
        """Test creating generator."""
        gen = ResponseGenerator()
        assert len(gen.generated_responses) == 0
        assert len(gen.generation_history) == 0

    def test_generate_response_english(self):
        """Test generating English response."""
        gen = ResponseGenerator()

        response, error = gen.generate_response(
            "Let's practice together",
            LanguageType.ENGLISH,
            "Satya",
            ResponseTemplate.GUIDANCE,
        )

        assert error is None
        assert response is not None
        assert response.user_language == LanguageType.ENGLISH
        assert response.generated_text == "Let's practice together"

    def test_generate_response_hinglish(self):
        """Test generating Hinglish response."""
        gen = ResponseGenerator()

        response, error = gen.generate_response(
            "Let's break this down",
            LanguageType.HINGLISH,
            "Richard",
            ResponseTemplate.GUIDANCE,
        )

        assert error is None
        assert response is not None
        assert response.user_language == LanguageType.HINGLISH
        # Should have some Hinglish adaptation
        assert response.generated_text != "Let's break this down" or response.generated_text.endswith(
            "!"
        )

    def test_generate_response_hindi(self):
        """Test generating Hindi response."""
        gen = ResponseGenerator()

        response, error = gen.generate_response(
            "Thank you for asking",
            LanguageType.HINDI,
            "Chris",
            ResponseTemplate.GUIDANCE,
        )

        assert error is None
        assert response is not None
        assert response.user_language == LanguageType.HINDI

    def test_generate_response_empty_text(self):
        """Test generating response with empty text."""
        gen = ResponseGenerator()

        response, error = gen.generate_response(
            "", LanguageType.ENGLISH, "Satya", ResponseTemplate.GUIDANCE
        )

        assert error == "Empty response text"
        assert response is None

    def test_generate_guidance(self):
        """Test generating guidance response."""
        gen = ResponseGenerator()

        response, error = gen.generate_guidance(
            "Start with first principles", LanguageType.ENGLISH, "Richard"
        )

        assert error is None
        assert response.template_type == ResponseTemplate.GUIDANCE

    def test_generate_question(self):
        """Test generating question response."""
        gen = ResponseGenerator()

        response, error = gen.generate_question(
            "What's your main challenge?", LanguageType.ENGLISH, "Satya"
        )

        assert error is None
        assert response.template_type == ResponseTemplate.QUESTION

    def test_generate_challenge(self):
        """Test generating challenge response."""
        gen = ResponseGenerator()

        response, error = gen.generate_challenge(
            "But what if you're wrong?", LanguageType.ENGLISH, "Charlie"
        )

        assert error is None
        assert response.template_type == ResponseTemplate.CHALLENGE

    def test_language_variants_generation(self):
        """Test that variants are generated."""
        gen = ResponseGenerator()

        response, _ = gen.generate_response(
            "Test response", LanguageType.ENGLISH, "Satya"
        )

        assert len(response.variants) >= 3  # English, Hindi, Hinglish
        languages = [v.language for v in response.variants]
        assert LanguageType.ENGLISH in languages
        assert LanguageType.HINDI in languages
        assert LanguageType.HINGLISH in languages

    def test_get_variant_english(self):
        """Test getting English variant."""
        gen = ResponseGenerator()

        response, _ = gen.generate_response(
            "Hello world", LanguageType.ENGLISH, "Satya"
        )

        variant = gen.get_variant(response.response_id, LanguageType.ENGLISH)
        assert variant is not None
        assert variant.language == LanguageType.ENGLISH
        assert variant.is_native is True

    def test_get_variant_hindi(self):
        """Test getting Hindi variant."""
        gen = ResponseGenerator()

        response, _ = gen.generate_response(
            "Hello world", LanguageType.ENGLISH, "Satya"
        )

        variant = gen.get_variant(response.response_id, LanguageType.HINDI)
        assert variant is not None
        assert variant.language == LanguageType.HINDI

    def test_get_variant_hinglish(self):
        """Test getting Hinglish variant."""
        gen = ResponseGenerator()

        response, _ = gen.generate_response(
            "Hello world", LanguageType.ENGLISH, "Satya"
        )

        variant = gen.get_variant(response.response_id, LanguageType.HINGLISH)
        assert variant is not None
        assert variant.language == LanguageType.HINGLISH

    def test_get_nonexistent_variant(self):
        """Test getting nonexistent variant."""
        gen = ResponseGenerator()
        variant = gen.get_variant("nonexistent", LanguageType.ENGLISH)
        assert variant is None

    def test_get_response(self):
        """Test retrieving response."""
        gen = ResponseGenerator()

        response, _ = gen.generate_response(
            "Test", LanguageType.ENGLISH, "Satya", response_id="resp_test"
        )

        retrieved = gen.get_response("resp_test")
        assert retrieved is not None
        assert retrieved.response_id == "resp_test"

    def test_get_nonexistent_response(self):
        """Test getting nonexistent response."""
        gen = ResponseGenerator()
        response = gen.get_response("nonexistent")
        assert response is None

    def test_export_response(self):
        """Test exporting single response."""
        gen = ResponseGenerator()

        response, _ = gen.generate_response(
            "Export test", LanguageType.ENGLISH, "Satya", response_id="resp_export"
        )

        exported = gen.export_response("resp_export")
        assert exported is not None
        assert exported["response_id"] == "resp_export"

    def test_export_all_responses(self):
        """Test exporting all responses."""
        gen = ResponseGenerator()

        gen.generate_response("Response 1", LanguageType.ENGLISH, "Satya")
        gen.generate_response("Response 2", LanguageType.HINDI, "Richard")

        exported = gen.export_all_responses()
        assert len(exported) == 2

    def test_generation_statistics_empty(self):
        """Test statistics with no responses."""
        gen = ResponseGenerator()
        stats = gen.get_generation_statistics()

        assert stats["total_responses"] == 0
        assert stats["avg_confidence"] == 0

    def test_generation_statistics_with_responses(self):
        """Test statistics with responses."""
        gen = ResponseGenerator()

        gen.generate_response("Test 1", LanguageType.ENGLISH, "Satya")
        gen.generate_response("Test 2", LanguageType.HINGLISH, "Richard")
        gen.generate_response("Test 3", LanguageType.HINDI, "Chris")

        stats = gen.get_generation_statistics()
        assert stats["total_responses"] == 3
        assert stats["by_language"]["english"] >= 1
        assert stats["by_language"]["hinglish"] >= 1
        assert stats["by_language"]["hindi"] >= 1

    def test_batch_generate_responses(self):
        """Test batch generating responses."""
        gen = ResponseGenerator()

        texts = [
            "Guidance 1",
            "Guidance 2",
            "Guidance 3",
        ]

        responses, error = gen.batch_generate_responses(
            texts, LanguageType.ENGLISH, "Satya"
        )

        assert error is None
        assert len(responses) == 3

    def test_adapt_to_language_english(self):
        """Test adapting to English."""
        gen = ResponseGenerator()

        adapted = gen.adapt_to_language("Hello world", LanguageType.ENGLISH)
        assert adapted == "Hello world"

    def test_adapt_to_language_hinglish(self):
        """Test adapting to Hinglish."""
        gen = ResponseGenerator()

        adapted = gen.adapt_to_language("Thank you", LanguageType.HINGLISH)
        assert "shukriya" in adapted.lower() or "thank" in adapted.lower()

    def test_adapt_to_language_hindi(self):
        """Test adapting to Hindi."""
        gen = ResponseGenerator()

        adapted = gen.adapt_to_language("Thank you", LanguageType.HINDI)
        # Should contain Hindi characters or Hindi transliteration
        assert adapted != "Thank you" or "धन्यवाद" in adapted

    def test_expert_response_style_satya(self):
        """Test getting Satya's response style."""
        gen = ResponseGenerator()

        style = gen.get_expert_response_style("Satya")
        assert style["tone"] == "encouraging"
        assert "{topic}" in style["pattern"]

    def test_expert_response_style_richard(self):
        """Test getting Richard's response style."""
        gen = ResponseGenerator()

        style = gen.get_expert_response_style("Richard")
        assert style["tone"] == "curious"

    def test_expert_response_style_jeff(self):
        """Test getting Jeff's response style."""
        gen = ResponseGenerator()

        style = gen.get_expert_response_style("Jeff")
        assert style["tone"] == "strategic"

    def test_expert_response_style_unknown(self):
        """Test getting unknown expert's style."""
        gen = ResponseGenerator()

        style = gen.get_expert_response_style("Unknown")
        assert style["tone"] == "neutral"

    def test_confidence_scores(self):
        """Test confidence scoring by language."""
        gen = ResponseGenerator()

        resp_en, _ = gen.generate_response(
            "Test", LanguageType.ENGLISH, "Satya"
        )
        resp_hl, _ = gen.generate_response(
            "Test", LanguageType.HINGLISH, "Satya"
        )
        resp_hi, _ = gen.generate_response(
            "Test", LanguageType.HINDI, "Satya"
        )

        # English should have highest confidence
        assert resp_en.confidence == 0.95
        # Hinglish should be middle
        assert resp_hl.confidence == 0.80
        # Hindi should be lower
        assert resp_hi.confidence == 0.75

    def test_multiple_generators_independent(self):
        """Test multiple generators are independent."""
        gen1 = ResponseGenerator()
        gen2 = ResponseGenerator()

        gen1.generate_response("Test 1", LanguageType.ENGLISH, "Satya")
        gen2.generate_response("Test 2", LanguageType.HINGLISH, "Richard")

        assert len(gen1.generation_history) == 1
        assert len(gen2.generation_history) == 1

    def test_hinglish_phrases_conversion(self):
        """Test Hinglish phrase conversions."""
        gen = ResponseGenerator()

        response, _ = gen.generate_response(
            "Please understand and thank you",
            LanguageType.HINGLISH,
            "Expert",
        )

        # Should have some Hinglish adaptations
        assert response.generated_text != "Please understand and thank you"

    def test_response_type_distribution(self):
        """Test response type distribution."""
        gen = ResponseGenerator()

        gen.generate_guidance("Guidance text", LanguageType.ENGLISH, "Satya")
        gen.generate_question("Question?", LanguageType.ENGLISH, "Richard")
        gen.generate_challenge("Challenge", LanguageType.ENGLISH, "Charlie")

        stats = gen.get_generation_statistics()
        assert stats["by_template"]["guidance"] >= 1
        assert stats["by_template"]["question"] >= 1
        assert stats["by_template"]["challenge"] >= 1

    def test_complex_workflow(self):
        """Test complex response generation workflow."""
        gen = ResponseGenerator()

        # Generate multiple responses in different languages
        resp_en, _ = gen.generate_guidance(
            "Start with understanding the problem",
            LanguageType.ENGLISH,
            "Richard",
        )
        resp_hl, _ = gen.generate_guidance(
            "Focus on long-term value",
            LanguageType.HINGLISH,
            "Jeff",
        )
        resp_hi, _ = gen.generate_question(
            "What is your main concern?",
            LanguageType.HINDI,
            "Chris",
        )

        # Get variants
        en_variant = gen.get_variant(resp_en.response_id, LanguageType.ENGLISH)
        hi_variant = gen.get_variant(resp_en.response_id, LanguageType.HINDI)

        assert en_variant is not None
        assert hi_variant is not None

        # Check statistics
        stats = gen.get_generation_statistics()
        assert stats["total_responses"] == 3
        assert stats["avg_confidence"] > 0

        # Export
        exported = gen.export_all_responses()
        assert len(exported) == 3
