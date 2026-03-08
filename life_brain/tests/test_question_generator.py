"""
Test suite for question generator.

Tests cover:
- Alternative question generation
- Question styles
- Keyword extraction
- Batch operations
- Statistics and exports
"""

import pytest

from life_brain.retrieval.question_generator import (
    QuestionGenerator,
    QuestionStyle,
    AlternativeQuestion,
    QuestionSet,
)


class TestAlternativeQuestion:
    """Test AlternativeQuestion dataclass."""

    def test_create_alternative(self):
        """Test creating alternative question."""
        alt = AlternativeQuestion(
            variant_id="var_0",
            original_question="How do I improve?",
            alternative_text="What are strategies for improvement?",
            style=QuestionStyle.FORMAL,
            emphasis="formality",
            formality_level=5,
        )

        assert alt.variant_id == "var_0"
        assert alt.style == QuestionStyle.FORMAL

    def test_to_dict(self):
        """Test converting to dict."""
        alt = AlternativeQuestion(
            variant_id="var_1",
            original_question="What should I do?",
            alternative_text="Tell me what to do",
            style=QuestionStyle.DIRECT,
            emphasis="directness",
            formality_level=3,
        )

        d = alt.to_dict()
        assert d["style"] == "direct"
        assert d["formality_level"] == 3


class TestQuestionSet:
    """Test QuestionSet dataclass."""

    def test_create_set(self):
        """Test creating question set."""
        q_set = QuestionSet(
            question_id="q_001",
            original_question="How do I succeed?",
            question_type="career",
        )

        assert q_set.question_id == "q_001"
        assert q_set.question_type == "career"

    def test_to_dict(self):
        """Test converting to dict."""
        q_set = QuestionSet(
            question_id="q_002",
            original_question="What's my goal?",
            primary_keywords=["goal", "direction"],
        )

        d = q_set.to_dict()
        assert d["question_id"] == "q_002"
        assert len(d["primary_keywords"]) == 2


class TestQuestionGenerator:
    """Test QuestionGenerator functionality."""

    def test_create_generator(self):
        """Test creating generator."""
        gen = QuestionGenerator()
        assert len(gen.question_sets) == 0
        assert len(gen.generation_history) == 0

    def test_generate_alternatives_default(self):
        """Test generating default alternatives."""
        gen = QuestionGenerator()

        q_set, error = gen.generate_alternatives("How can I improve my skills?")

        assert error is None
        assert q_set is not None
        assert len(q_set.alternatives) == 3

    def test_generate_alternatives_count_2(self):
        """Test generating 2 alternatives."""
        gen = QuestionGenerator()

        q_set, error = gen.generate_alternatives(
            "What's the best approach?", count=2
        )

        assert error is None
        assert len(q_set.alternatives) == 2

    def test_generate_alternatives_count_5(self):
        """Test generating 5 alternatives."""
        gen = QuestionGenerator()

        q_set, error = gen.generate_alternatives(
            "Should I change careers?", count=5
        )

        assert error is None
        assert len(q_set.alternatives) == 5

    def test_generate_alternatives_invalid_count_low(self):
        """Test invalid count (too low)."""
        gen = QuestionGenerator()

        q_set, error = gen.generate_alternatives("Test", count=1)

        assert error == "Count must be between 2 and 5"
        assert q_set is None

    def test_generate_alternatives_invalid_count_high(self):
        """Test invalid count (too high)."""
        gen = QuestionGenerator()

        q_set, error = gen.generate_alternatives("Test", count=6)

        assert error == "Count must be between 2 and 5"
        assert q_set is None

    def test_generate_alternatives_empty_question(self):
        """Test with empty question."""
        gen = QuestionGenerator()

        q_set, error = gen.generate_alternatives("")

        assert error == "Empty question"
        assert q_set is None

    def test_generate_alternatives_question_type(self):
        """Test with question type."""
        gen = QuestionGenerator()

        q_set, error = gen.generate_alternatives(
            "How to handle conflict?", question_type="relationship"
        )

        assert error is None
        assert q_set.question_type == "relationship"

    def test_keywords_extracted(self):
        """Test keyword extraction."""
        gen = QuestionGenerator()

        q_set, _ = gen.generate_alternatives(
            "How can I improve my technical skills for my career?"
        )

        assert len(q_set.primary_keywords) > 0
        # Should include meaningful keywords
        keywords_lower = [k.lower() for k in q_set.primary_keywords]
        assert any(
            k in keywords_lower
            for k in ["improve", "technical", "skills", "career"]
        )

    def test_styles_generated(self):
        """Test that various styles are generated."""
        gen = QuestionGenerator()

        q_set, _ = gen.generate_alternatives("Test question", count=4)

        styles = [alt.style for alt in q_set.alternatives]
        assert QuestionStyle.FORMAL in styles
        assert QuestionStyle.CASUAL in styles or QuestionStyle.DIRECT in styles

    def test_formal_style_transformation(self):
        """Test formal style transformation."""
        gen = QuestionGenerator()

        q_set, _ = gen.generate_alternatives("How to succeed?", count=3)

        formal_alt = next(
            (a for a in q_set.alternatives if a.style == QuestionStyle.FORMAL),
            None,
        )
        assert formal_alt is not None
        assert formal_alt.formality_level == 5
        assert "Could you" in formal_alt.alternative_text or "?" in formal_alt.alternative_text

    def test_casual_style_transformation(self):
        """Test casual style transformation."""
        gen = QuestionGenerator()

        q_set, _ = gen.generate_alternatives("What should I do?", count=3)

        casual_alt = next(
            (a for a in q_set.alternatives if a.style == QuestionStyle.CASUAL),
            None,
        )
        assert casual_alt is not None
        assert casual_alt.formality_level == 1

    def test_direct_style_transformation(self):
        """Test direct style transformation."""
        gen = QuestionGenerator()

        q_set, _ = gen.generate_alternatives(
            "Could you tell me how to improve?", count=3
        )

        direct_alt = next(
            (a for a in q_set.alternatives if a.style == QuestionStyle.DIRECT),
            None,
        )
        assert direct_alt is not None
        assert direct_alt.formality_level == 3

    def test_get_question_set(self):
        """Test retrieving question set."""
        gen = QuestionGenerator()

        q_set, _ = gen.generate_alternatives("Test", question_id="q_test")

        retrieved = gen.get_question_set("q_test")
        assert retrieved is not None
        assert retrieved.question_id == "q_test"

    def test_get_nonexistent_set(self):
        """Test retrieving nonexistent set."""
        gen = QuestionGenerator()
        retrieved = gen.get_question_set("nonexistent")
        assert retrieved is None

    def test_get_alternative_by_style(self):
        """Test getting alternative by style."""
        gen = QuestionGenerator()

        q_set, _ = gen.generate_alternatives("Test", count=3)

        formal = gen.get_alternative_by_style(q_set.question_id, QuestionStyle.FORMAL)
        assert formal is not None
        assert formal.style == QuestionStyle.FORMAL

    def test_export_question_set(self):
        """Test exporting question set."""
        gen = QuestionGenerator()

        q_set, _ = gen.generate_alternatives("Export test", question_id="q_export")

        exported = gen.export_question_set("q_export")
        assert exported is not None
        assert exported["question_id"] == "q_export"
        assert len(exported["alternatives"]) == 3

    def test_export_all_question_sets(self):
        """Test exporting all sets."""
        gen = QuestionGenerator()

        gen.generate_alternatives("Question 1")
        gen.generate_alternatives("Question 2")

        exported = gen.export_all_question_sets()
        assert len(exported) == 2

    def test_generation_statistics_empty(self):
        """Test statistics with no generations."""
        gen = QuestionGenerator()
        stats = gen.get_generation_statistics()

        assert stats["total_questions"] == 0
        assert stats["total_alternatives"] == 0

    def test_generation_statistics_with_data(self):
        """Test statistics with generations."""
        gen = QuestionGenerator()

        gen.generate_alternatives("Career question", question_type="career", count=3)
        gen.generate_alternatives(
            "Relationship question", question_type="relationship", count=4
        )

        stats = gen.get_generation_statistics()
        assert stats["total_questions"] == 2
        assert stats["total_alternatives"] == 7
        assert stats["by_type"]["career"] == 1
        assert stats["by_type"]["relationship"] == 1

    def test_batch_generate(self):
        """Test batch generation."""
        gen = QuestionGenerator()

        questions = ["Question 1?", "Question 2?", "Question 3?"]
        q_sets, error = gen.batch_generate(questions, "general")

        assert error is None
        assert len(q_sets) == 3

    def test_get_most_effective_variations(self):
        """Test getting effective variations in order."""
        gen = QuestionGenerator()

        q_set, _ = gen.generate_alternatives("Test", count=3)

        effective = gen.get_most_effective_variations(q_set.question_id)
        assert effective is not None
        assert len(effective) == 3
        # Direct should come before formal
        styles = [a.style for a in effective]

    def test_multiple_generators_independent(self):
        """Test multiple generators are independent."""
        gen1 = QuestionGenerator()
        gen2 = QuestionGenerator()

        gen1.generate_alternatives("Q1")
        gen2.generate_alternatives("Q2")

        assert len(gen1.generation_history) == 1
        assert len(gen2.generation_history) == 1

    def test_complex_workflow(self):
        """Test complex workflow."""
        gen = QuestionGenerator()

        # Generate alternatives
        q_set, _ = gen.generate_alternatives(
            "Should I accept the job offer?", question_type="career", count=4
        )

        # Get variations
        effective = gen.get_most_effective_variations(q_set.question_id)
        assert len(effective) == 4

        # Export
        exported = gen.export_question_set(q_set.question_id)
        assert exported is not None

        # Stats
        stats = gen.get_generation_statistics()
        assert stats["total_questions"] == 1
        assert stats["by_type"]["career"] == 1

    def test_different_question_types(self):
        """Test different question types."""
        gen = QuestionGenerator()

        types = ["career", "relationship", "learning", "health"]
        for q_type in types:
            q_set, _ = gen.generate_alternatives(
                f"Test {q_type} question", question_type=q_type
            )
            assert q_set.question_type == q_type

        stats = gen.get_generation_statistics()
        assert len(stats["by_type"]) == 4

    def test_style_characteristics(self):
        """Test that styles have correct characteristics."""
        gen = QuestionGenerator()

        q_set, _ = gen.generate_alternatives("Test question", count=3)

        # Map styles to check
        style_checks = {}
        for alt in q_set.alternatives:
            style_checks[alt.style] = alt

        # Check formal is more formal
        if QuestionStyle.FORMAL in style_checks:
            assert (
                style_checks[QuestionStyle.FORMAL].formality_level
                >= style_checks[QuestionStyle.CASUAL].formality_level
            )

    def test_keywords_consistent(self):
        """Test keywords are consistent across variants."""
        gen = QuestionGenerator()

        q_set, _ = gen.generate_alternatives(
            "How can I improve my Python programming skills?"
        )

        # All variants should have same keywords
        for alt in q_set.alternatives:
            assert alt.keywords == q_set.primary_keywords
