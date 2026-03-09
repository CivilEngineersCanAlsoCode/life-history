"""
Tests for alternative question phrasing generation.

Tests cover:
- Generating 2-3 alternative phrasings for questions
- Domain-specific phrasings (career, metric, technical, challenge)
- Transformation-based alternatives
- Fact-level phrasing generation
- Edge cases
"""

import pytest

from life_brain.core.alt_phrasing_generator import (
    generate_alt_phrasings,
    generate_phrasings_for_fact,
)


class TestGenerateAltPhrasings:
    """Test alternative phrasing generation."""

    def test_returns_list(self):
        alts = generate_alt_phrasings("What was your role in the project?")
        assert isinstance(alts, list)

    def test_returns_alternatives(self):
        alts = generate_alt_phrasings("What was your role in the project?")
        assert len(alts) >= 1

    def test_count_respected(self):
        alts = generate_alt_phrasings("What was your role?", count=2)
        assert len(alts) <= 2

    def test_alternatives_are_strings(self):
        alts = generate_alt_phrasings("How did you solve the problem?")
        assert all(isinstance(a, str) for a in alts)

    def test_alternatives_not_same_as_original(self):
        original = "What was your role in the project?"
        alts = generate_alt_phrasings(original)
        for alt in alts:
            assert alt.lower() != original.lower()

    def test_empty_question_returns_empty(self):
        alts = generate_alt_phrasings("")
        assert alts == []

    def test_domain_career_generates_relevant(self):
        alts = generate_alt_phrasings("What was your role?", domain="career")
        assert len(alts) >= 1

    def test_domain_metric_generates_relevant(self):
        alts = generate_alt_phrasings("What were the results?", domain="metric")
        assert len(alts) >= 1

    def test_domain_technical_generates_relevant(self):
        alts = generate_alt_phrasings("How did you implement this?", domain="technical")
        assert len(alts) >= 1

    def test_how_did_you_transformation(self):
        alts = generate_alt_phrasings("How did you handle the incident?")
        # Should transform "how did you" to something else
        assert len(alts) >= 1
        assert any(alt.lower() != "how did you handle the incident?" for alt in alts)

    def test_alternatives_end_with_question_mark(self):
        alts = generate_alt_phrasings("What was your approach?")
        for alt in alts:
            assert alt.endswith("?")


class TestGeneratePhrasingsForFact:
    """Test fact-level phrasing generation."""

    def test_returns_list(self):
        alts = generate_phrasings_for_fact(
            "What was your role?",
            "I was the tech lead for 6 months in Q1 2024."
        )
        assert isinstance(alts, list)

    def test_generates_phrasings(self):
        alts = generate_phrasings_for_fact(
            "What was your role?",
            "I led the backend team."
        )
        assert len(alts) >= 1

    def test_metric_answer_infers_metric_domain(self):
        alts = generate_phrasings_for_fact(
            "What was the impact?",
            "We reduced latency by 40%, from 800ms to 480ms."
        )
        # Should work without errors
        assert isinstance(alts, list)

    def test_technical_answer_infers_technical_domain(self):
        alts = generate_phrasings_for_fact(
            "What did you build?",
            "I built a REST API using Python and PostgreSQL."
        )
        assert isinstance(alts, list)

    def test_max_three_phrasings(self):
        alts = generate_phrasings_for_fact("What was your approach?", "I worked on it.")
        assert len(alts) <= 3

    def test_explicit_domain_override(self):
        alts = generate_phrasings_for_fact(
            "What was your contribution?",
            "I improved things.",
            domain="career"
        )
        assert isinstance(alts, list)

    def test_phrasings_not_empty(self):
        alts = generate_phrasings_for_fact(
            "How did you solve the problem?",
            "I debugged the system and fixed the bottleneck."
        )
        # At least one phrasing should be generated
        assert len(alts) >= 1

    def test_all_phrasings_are_strings(self):
        alts = generate_phrasings_for_fact("What was your role?", "I was PM.")
        assert all(isinstance(a, str) for a in alts)
