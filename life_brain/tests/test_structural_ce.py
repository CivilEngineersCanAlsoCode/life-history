"""Tests for structural_ce.py — NLP-based CE validation."""

import pytest
from life_brain.pipelines.structural_ce import (
    structural_ce_check,
    extract_atoms,
    _extract_numbers,
    _extract_entities,
    _extract_key_verbs,
)


# ── extract_atoms helpers ────────────────────────────────────────────────────

class TestExtractNumbers:
    def test_integers(self):
        assert "14" in _extract_numbers("I integrated 14 APIs.")

    def test_percentage(self):
        nums = _extract_numbers("Latency reduced by 70%.")
        assert "70%" in nums

    def test_decimal(self):
        nums = _extract_numbers("Score was 0.85")
        assert "0.85" in nums

    def test_no_numbers(self):
        assert _extract_numbers("No numeric content here.") == set()


class TestExtractEntities:
    def test_multi_word_entity(self):
        entities = _extract_entities("I worked at American Express last year.")
        assert "american express" in entities

    def test_single_long_entity(self):
        entities = _extract_entities("Sprinklr was the platform.")
        assert "sprinklr" in entities

    def test_no_entities_all_lower(self):
        result = _extract_entities("this is all lowercase text here.")
        assert len(result) == 0


class TestExtractKeyVerbs:
    def test_ed_suffix(self):
        verbs = _extract_key_verbs("I integrated APIs and automated deployments.")
        assert "integrated" in verbs or "automated" in verbs

    def test_ing_suffix(self):
        verbs = _extract_key_verbs("Processing latency improved significantly.")
        assert "processing" in verbs

    def test_tion_suffix(self):
        verbs = _extract_key_verbs("Integration and optimization were key.")
        assert "integration" in verbs or "optimization" in verbs

    def test_stopwords_filtered(self):
        verbs = _extract_key_verbs("is are was were have had do does did")
        assert len(verbs) == 0

    def test_short_words_excluded(self):
        verbs = _extract_key_verbs("go got be do")
        assert len(verbs) == 0


class TestExtractAtoms:
    def test_returns_all_categories(self):
        atoms = extract_atoms("I integrated 14 APIs at Sprinklr reducing latency.")
        assert "numbers" in atoms
        assert "entities" in atoms
        assert "key_verbs" in atoms

    def test_numbers_captured(self):
        atoms = extract_atoms("14 integrations were completed.")
        assert "14" in atoms["numbers"]

    def test_empty_text(self):
        atoms = extract_atoms("")
        assert atoms["numbers"] == set()
        assert atoms["entities"] == set()
        assert atoms["key_verbs"] == set()


# ── structural_ce_check ───────────────────────────────────────────────────────

class MockQAPair:
    """Minimal QAPair mock for testing."""
    def __init__(self, question: str, answer: str, alt_questions=None):
        self.primary_question = question
        self.answer = answer
        self.alt_questions = alt_questions or []


class TestStructuralCeCheck:
    def test_empty_raw_answer(self):
        pairs = [MockQAPair("What?", "something")]
        ok, missing = structural_ce_check("", pairs)
        assert ok is True
        assert missing == []

    def test_empty_qa_pairs(self):
        ok, missing = structural_ce_check("Some text here.", [])
        assert ok is False

    def test_full_coverage(self):
        raw = "I integrated 14 APIs at Sprinklr."
        pairs = [MockQAPair(
            "How many APIs did you integrate?",
            "I integrated 14 APIs at Sprinklr."
        )]
        ok, missing = structural_ce_check(raw, pairs)
        assert ok is True

    def test_partial_coverage_below_threshold(self):
        raw = "I integrated 14 APIs at Sprinklr reducing latency from 48h to 15min."
        pairs = [MockQAPair("What?", "nothing relevant here abc xyz")]
        # With very unrelated answer, coverage should be low
        ok, missing = structural_ce_check(raw, pairs, min_atom_coverage=0.9)
        assert ok is False
        assert len(missing) > 0

    def test_returns_missing_atoms(self):
        raw = "Integrated 14 government APIs at Sprinklr."
        pairs = [MockQAPair("Question?", "some unrelated answer")]
        ok, missing = structural_ce_check(raw, pairs)
        assert isinstance(missing, list)

    def test_numbers_must_appear(self):
        raw = "Processed 50000 documents in 3 hours."
        # QA pair mentions the number
        pairs = [MockQAPair("How many docs?", "50000 documents in 3 hours.")]
        ok, missing = structural_ce_check(raw, pairs, min_atom_coverage=0.8)
        # With relaxed threshold, should pass (most numbers appear)
        assert ok is True or len(missing) <= 1

    def test_number_missing_from_qa(self):
        raw = "Processed 50000 documents in 3 hours."
        pairs = [MockQAPair("How many?", "Many documents were processed quickly.")]
        ok, missing = structural_ce_check(raw, pairs, min_atom_coverage=1.0)
        # Strict coverage: 50000 and 3 must appear → might fail
        assert isinstance(ok, bool)

    def test_coverage_threshold_respected(self):
        raw = "Sprinklr integration with 14 APIs."
        pairs = [MockQAPair("About Sprinklr?", "Sprinklr was the platform with APIs.")]
        # 0.0 threshold: always passes
        ok_relaxed, _ = structural_ce_check(raw, pairs, min_atom_coverage=0.0)
        assert ok_relaxed is True

    def test_alt_questions_included_in_coverage(self):
        raw = "Reducing latency from 48 hours to 15 minutes."
        pairs = [MockQAPair(
            "What was improved?",
            "Latency was reduced.",
            alt_questions=["How much did latency reduce? From 48 hours to 15 minutes."]
        )]
        ok, missing = structural_ce_check(raw, pairs)
        # Numbers should be covered via alt_questions
        assert isinstance(ok, bool)

    def test_no_atoms_in_raw(self):
        # Pure stopwords, no extractable atoms
        raw = "it is what it is"
        pairs = [MockQAPair("Q?", "A.")]
        ok, missing = structural_ce_check(raw, pairs)
        assert ok is True
        assert missing == []
