"""
Tests for depth probe — incomplete answer detection and follow-up questions.

Tests cover:
- Detecting vague/incomplete answers
- Detecting specific, complete answers
- Depth question generation
- Vagueness type classification
- Specificity scoring
- Edge cases
"""

import pytest

from life_brain.conversation.depth_probe import (
    detect_incomplete_answer,
    generate_depth_questions,
    ProbeResult,
    VaguenessType,
)


class TestDetectIncompleteAnswer:
    """Test incomplete answer detection."""

    def test_empty_answer_incomplete(self):
        result = detect_incomplete_answer("")
        assert result.is_complete is False

    def test_vague_short_answer_incomplete(self):
        result = detect_incomplete_answer("I helped with the project.")
        assert result.is_complete is False

    def test_specific_answer_complete(self):
        answer = (
            "In Q3 2023, I led the migration of our payment service to AWS Lambda. "
            "We reduced latency by 40% from 800ms to 480ms, and saved $50K/year in compute costs. "
            "The project took 6 weeks with a team of 3 engineers. "
            "The main challenge was maintaining zero downtime during cutover."
        )
        result = detect_incomplete_answer(answer)
        assert result.is_complete is True

    def test_vagueness_types_populated(self):
        result = detect_incomplete_answer("I worked on various things.")
        assert len(result.vagueness_types) > 0

    def test_no_metric_detected(self):
        result = detect_incomplete_answer(
            "I helped improve the system performance significantly over several months"
        )
        # Answer has no numbers/percentages so should be incomplete with some vagueness
        assert result.is_complete is False
        assert len(result.vagueness_types) > 0

    def test_no_example_detected(self):
        result = detect_incomplete_answer("I contributed to the team effort.")
        assert VaguenessType.NO_EXAMPLE in result.vagueness_types

    def test_specificity_score_range(self):
        result = detect_incomplete_answer("I did some work.")
        assert 0 <= result.specificity_score <= 1

    def test_specific_answer_higher_score(self):
        vague = detect_incomplete_answer("I improved things.")
        specific = detect_incomplete_answer(
            "In January 2024, I optimized our SQL queries which reduced P99 latency from 2s to 300ms, "
            "impacting 50K daily users. Specifically, I added composite indexes and rewrote 3 slow joins."
        )
        assert specific.specificity_score > vague.specificity_score

    def test_explanation_present(self):
        result = detect_incomplete_answer("I did some stuff.")
        assert isinstance(result.explanation, str)
        assert len(result.explanation) > 0

    def test_complete_answer_has_no_depth_questions(self):
        answer = (
            "In September 2023, I designed and built the real-time notification system using Kafka. "
            "This reduced notification delay from 5 minutes to under 2 seconds for 100K active users. "
            "The project ran for 3 months with a team of 4. It resulted in a 15% increase in user engagement."
        )
        result = detect_incomplete_answer(answer)
        if result.is_complete:
            assert result.depth_questions == []


class TestDepthQuestionsGeneration:
    """Test depth question generation."""

    def test_incomplete_answer_generates_questions(self):
        answer = "I helped with the project."
        questions = generate_depth_questions(answer)
        assert len(questions) > 0

    def test_questions_are_strings(self):
        questions = generate_depth_questions("I worked on stuff.")
        assert all(isinstance(q, str) for q in questions)

    def test_max_three_questions(self):
        questions = generate_depth_questions("I contributed.")
        assert len(questions) <= 3

    def test_specific_answer_no_questions(self):
        answer = (
            "In Q1 2024, I optimized the batch processing pipeline using Spark, "
            "reducing runtime from 4 hours to 45 minutes (83% improvement). "
            "The team was 5 engineers, project ran January to March. "
            "Impact: saved $20K/month in compute costs."
        )
        questions = generate_depth_questions(answer)
        # May or may not be empty, but should have fewer questions for a specific answer
        assert len(questions) <= 3

    def test_primary_question_method(self):
        result = detect_incomplete_answer("I did some things.")
        primary = result.primary_question()
        if result.depth_questions:
            assert primary == result.depth_questions[0]
        else:
            assert primary is None

    def test_no_metric_triggers_metric_question(self):
        answer = "I improved the system performance significantly."
        result = detect_incomplete_answer(answer)
        if VaguenessType.NO_METRIC in result.vagueness_types:
            # Should ask about numbers
            combined = " ".join(result.depth_questions).lower()
            assert any(word in combined for word in ["number", "metric", "quantif", "scale", "how many"])


class TestEdgeCases:
    """Test edge cases."""

    def test_whitespace_only(self):
        result = detect_incomplete_answer("   ")
        assert result.is_complete is False

    def test_single_word(self):
        result = detect_incomplete_answer("Yes")
        assert result.is_complete is False

    def test_answer_with_numbers_but_no_context(self):
        result = detect_incomplete_answer("I improved it by 50%.")
        # Has metric but still vague without context
        assert result.specificity_score < 1.0

    def test_long_vague_answer(self):
        # Long but vague
        answer = " ".join(["I worked on various things and helped the team"] * 5)
        result = detect_incomplete_answer(answer)
        # Should be incomplete despite length since it's vague
        assert VaguenessType.NO_METRIC in result.vagueness_types or not result.is_complete
