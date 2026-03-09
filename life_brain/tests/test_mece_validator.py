"""Tests for mece_validator.py — mutual exclusivity validation."""

import math
import pytest

from life_brain.db.mece_validator import (
    AtomicQuery,
    DuplicateCandidate,
    MECEReport,
    MECEValidator,
    cosine_similarity,
    DUPLICATE_THRESHOLD,
)


# ── cosine_similarity ───────────────────────────────────────────────────────

class TestCosineSimilarity:
    def test_identical_vectors(self):
        v = [1.0, 0.0, 0.0]
        assert cosine_similarity(v, v) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)

    def test_opposite_vectors_clamped_to_zero(self):
        # cosine of 180° = -1, clamped to 0
        result = cosine_similarity([1.0, 0.0], [-1.0, 0.0])
        assert result == pytest.approx(0.0)

    def test_empty_vector(self):
        assert cosine_similarity([], [1.0]) == 0.0

    def test_length_mismatch(self):
        assert cosine_similarity([1.0], [1.0, 2.0]) == 0.0

    def test_zero_vector(self):
        assert cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0

    def test_similar_vectors(self):
        v1 = [1.0, 0.5]
        v2 = [1.0, 0.5]
        assert cosine_similarity(v1, v2) == pytest.approx(1.0)

    def test_partial_similarity(self):
        v1 = [1.0, 0.0]
        v2 = [0.707, 0.707]
        result = cosine_similarity(v1, v2)
        assert 0.5 < result < 1.0


# ── AtomicQuery ─────────────────────────────────────────────────────────────

class TestAtomicQuery:
    def test_defaults(self):
        q = AtomicQuery(query_id="q1", question="What is AML?")
        assert q.answer is None
        assert q.embedding is None
        assert q.metadata == {}

    def test_with_all_fields(self):
        q = AtomicQuery(
            query_id="q2",
            question="What is CRR?",
            answer="Credit Risk Rating",
            metadata={"domain": "career"},
            embedding=[0.1, 0.2],
        )
        assert q.answer == "Credit Risk Rating"
        assert q.embedding == [0.1, 0.2]


# ── MECEValidator.validate() ─────────────────────────────────────────────────

class TestMECEValidatorValidate:
    def test_empty_list(self):
        v = MECEValidator()
        report = v.validate([])
        assert report.total_queries == 0
        assert report.duplicates_found == 0

    def test_single_query(self):
        v = MECEValidator()
        q = AtomicQuery(query_id="q1", question="What is AML?")
        report = v.validate([q])
        assert report.total_queries == 1
        assert report.duplicates_found == 0

    def test_no_duplicates_different_text(self):
        v = MECEValidator()
        queries = [
            AtomicQuery("q1", "What is AML?"),
            AtomicQuery("q2", "Who invented calculus?"),
        ]
        report = v.validate(queries)
        assert report.duplicates_found == 0

    def test_exact_duplicate_by_text(self):
        # Jaccard of identical strings = 1.0 (> 0.85)
        v = MECEValidator()
        queries = [
            AtomicQuery("q1", "What is the AML risk score?"),
            AtomicQuery("q2", "What is the AML risk score?"),
        ]
        report = v.validate(queries)
        assert report.duplicates_found == 1
        assert report.merges_suggested == 1

    def test_duplicate_by_embedding(self):
        v = MECEValidator(threshold=0.85)
        # Identical embeddings → similarity 1.0
        embed = [1.0, 0.0, 0.0]
        queries = [
            AtomicQuery("q1", "Question A", embedding=embed),
            AtomicQuery("q2", "Question B", embedding=embed),
        ]
        report = v.validate(queries)
        assert report.duplicates_found == 1

    def test_no_duplicate_low_similarity_embedding(self):
        v = MECEValidator()
        queries = [
            AtomicQuery("q1", "A", embedding=[1.0, 0.0]),
            AtomicQuery("q2", "B", embedding=[0.0, 1.0]),
        ]
        report = v.validate(queries)
        assert report.duplicates_found == 0

    def test_report_counts(self):
        v = MECEValidator()
        embed = [1.0, 0.0]
        queries = [
            AtomicQuery("q1", "X", embedding=embed),
            AtomicQuery("q2", "Y", embedding=embed),
            AtomicQuery("q3", "Z", embedding=[0.0, 1.0]),
        ]
        report = v.validate(queries)
        assert report.total_queries == 3
        assert report.duplicates_found == 1

    def test_custom_threshold(self):
        # With threshold=0.5, near-similar embeddings are duplicates
        v = MECEValidator(threshold=0.5)
        v1 = [1.0, 0.0]
        v2 = [0.8, 0.6]  # cosine ~0.8
        queries = [
            AtomicQuery("q1", "A", embedding=v1),
            AtomicQuery("q2", "B", embedding=v2),
        ]
        report = v.validate(queries)
        assert report.duplicates_found >= 1


# ── MECEValidator.check_new_query() ─────────────────────────────────────────

class TestCheckNewQuery:
    def test_unique_new_query(self):
        v = MECEValidator()
        existing = [AtomicQuery("e1", "Completely unrelated sentence about space.")]
        new_q = AtomicQuery("n1", "What is the AML regulation?")
        candidates = v.check_new_query(new_q, existing)
        assert candidates == []

    def test_duplicate_new_query(self):
        v = MECEValidator()
        existing = [AtomicQuery("e1", "What is the AML risk score?")]
        new_q = AtomicQuery("n1", "What is the AML risk score?")
        candidates = v.check_new_query(new_q, existing)
        assert len(candidates) == 1
        assert candidates[0].query_a_id == "n1"
        assert candidates[0].query_b_id == "e1"

    def test_reason_contains_similarity(self):
        v = MECEValidator()
        embed = [1.0, 0.0]
        existing = [AtomicQuery("e1", "Q", embedding=embed)]
        new_q = AtomicQuery("n1", "Q", embedding=embed)
        candidates = v.check_new_query(new_q, existing)
        assert "100.0%" in candidates[0].merge_reason or "similar" in candidates[0].merge_reason

    def test_empty_existing(self):
        v = MECEValidator()
        candidates = v.check_new_query(AtomicQuery("n1", "Question?"), [])
        assert candidates == []


# ── MECEValidator.merge_queries() ───────────────────────────────────────────

class TestMergeQueries:
    def test_keeps_primary_question(self):
        v = MECEValidator()
        q_a = AtomicQuery("a", "Question A", answer="Answer A")
        q_b = AtomicQuery("b", "Question B", answer="Answer B")
        merged = v.merge_queries(q_a, q_b, keep_a=True)
        assert merged.question == "Question A"
        assert merged.query_id == "a"

    def test_keeps_b_when_specified(self):
        v = MECEValidator()
        q_a = AtomicQuery("a", "Question A", answer="Answer A")
        q_b = AtomicQuery("b", "Question B", answer="Answer B")
        merged = v.merge_queries(q_a, q_b, keep_a=False)
        assert merged.question == "Question B"
        assert merged.query_id == "b"

    def test_answers_merged_when_different(self):
        v = MECEValidator()
        q_a = AtomicQuery("a", "Q", answer="Answer A")
        q_b = AtomicQuery("b", "Q", answer="Answer B")
        merged = v.merge_queries(q_a, q_b)
        assert "Answer A" in merged.answer
        assert "Answer B" in merged.answer

    def test_same_answers_not_duplicated(self):
        v = MECEValidator()
        q_a = AtomicQuery("a", "Q", answer="Same Answer")
        q_b = AtomicQuery("b", "Q", answer="Same Answer")
        merged = v.merge_queries(q_a, q_b)
        assert merged.answer == "Same Answer"

    def test_metadata_merged(self):
        v = MECEValidator()
        q_a = AtomicQuery("a", "Q", metadata={"domain": "career", "source": "interview"})
        q_b = AtomicQuery("b", "Q", metadata={"domain": "finance", "tag": "aml"})
        merged = v.merge_queries(q_a, q_b)
        # Primary (a) values should win for overlapping keys
        assert merged.metadata["domain"] == "career"
        # Non-overlapping from b should be included
        assert merged.metadata["tag"] == "aml"

    def test_no_answer_both(self):
        v = MECEValidator()
        q_a = AtomicQuery("a", "Q")
        q_b = AtomicQuery("b", "Q")
        merged = v.merge_queries(q_a, q_b)
        assert merged.answer is None


# ── MECEReport.to_dict() ─────────────────────────────────────────────────────

class TestMECEReport:
    def test_to_dict_structure(self):
        report = MECEReport(
            total_queries=5,
            duplicates_found=2,
            merges_suggested=2,
            kept_both=0,
            candidates=[
                DuplicateCandidate("q1", "q2", 0.91, "merge", "High similarity"),
            ],
        )
        d = report.to_dict()
        assert d["total_queries"] == 5
        assert d["duplicates_found"] == 2
        assert len(d["candidates"]) == 1
        c = d["candidates"][0]
        assert c["query_a"] == "q1"
        assert c["similarity"] == 0.91
        assert c["decision"] == "merge"

    def test_similarity_rounded(self):
        report = MECEReport(
            total_queries=2,
            duplicates_found=1,
            merges_suggested=1,
            kept_both=0,
            candidates=[DuplicateCandidate("a", "b", 0.91234, "merge", "reason")],
        )
        d = report.to_dict()
        assert d["candidates"][0]["similarity"] == 0.912


# ── Default threshold constant ───────────────────────────────────────────────

def test_default_threshold():
    assert DUPLICATE_THRESHOLD == 0.85


class TestHighlySimilarAtomsMerge:
    """Regression test for issues-i4z.3.4: MECE check when atoms >95% similar should merge."""

    def test_near_identical_queries_detected_as_duplicate(self):
        """Two queries with very high similarity (>95%) should be flagged for merge."""
        validator = MECEValidator()
        q1 = AtomicQuery(query_id="q1", question="What is the project goal?", embedding=[1.0, 0.0, 0.0])
        q2 = AtomicQuery(query_id="q2", question="What is the project objective?", embedding=[0.999, 0.001, 0.0])
        report = validator.validate([q1, q2])
        # If similarity > threshold, should find at least 1 duplicate candidate
        sim = cosine_similarity(q1.embedding, q2.embedding)
        if sim >= DUPLICATE_THRESHOLD:
            assert report.duplicates_found >= 1
            assert report.merges_suggested >= 1

    def test_very_high_similarity_vectors(self):
        """Vectors at 0.99+ cosine similarity are clearly duplicates."""
        sim = cosine_similarity([1.0, 0.01, 0.0], [1.0, 0.01, 0.0])
        assert sim >= 0.99
