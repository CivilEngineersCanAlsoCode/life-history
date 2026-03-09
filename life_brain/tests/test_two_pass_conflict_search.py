"""
Tests for two-pass conflict candidate pool.

Tests cover:
- Pass 1: semantic search
- Pass 2: structural metadata filter
- Union and deduplication
- Atom type filtering (METRIC/FACT only for Pass 2)
- Error handling
- Edge cases (no collection, empty metadata)
"""

import pytest
from unittest.mock import Mock, call

from life_brain.truth.two_pass_conflict_search import (
    two_pass_conflict_search,
    should_run_structural_pass,
    STRUCTURAL_CONFLICT_TYPES,
)


def _make_query_result(ids=None, docs=None, metas=None, dists=None):
    """Build a ChromaDB query() return value."""
    n = len(ids or [])
    return {
        "ids": [ids or []],
        "documents": [docs or [""] * n],
        "metadatas": [metas or [{}] * n],
        "distances": [dists or [0.2] * n],
    }


def _make_get_result(ids=None, docs=None, metas=None):
    """Build a ChromaDB get() return value."""
    n = len(ids or [])
    return {
        "ids": ids or [],
        "documents": docs or [""] * n,
        "metadatas": metas or [{}] * n,
    }


class TestStructuralPassFilter:
    """Test which atom types trigger structural pass."""

    def test_metric_triggers_structural(self):
        assert should_run_structural_pass("metric") is True

    def test_fact_triggers_structural(self):
        assert should_run_structural_pass("fact") is True

    def test_story_skips_structural(self):
        assert should_run_structural_pass("story") is False

    def test_decision_skips_structural(self):
        assert should_run_structural_pass("decision") is False

    def test_lesson_skips_structural(self):
        assert should_run_structural_pass("lesson") is False

    def test_case_insensitive(self):
        assert should_run_structural_pass("METRIC") is True
        assert should_run_structural_pass("Fact") is True


class TestPass1SemanticSearch:
    """Test Pass 1 — semantic similarity."""

    def test_no_collection_returns_empty(self):
        """No collection → empty candidates, no crash."""
        candidates, p1, p2 = two_pass_conflict_search(
            collection=None,
            query_text="test",
            query_embedding=None,
            atom_type="metric",
            metadata_filters={},
        )
        assert candidates == []
        assert p1 == 0
        assert p2 == 0

    def test_pass1_returns_semantic_candidates(self):
        """Semantic pass returns candidates from collection.query()."""
        mock = Mock()
        mock.query.return_value = _make_query_result(
            ids=["doc1", "doc2"],
            docs=["Content A", "Content B"],
            dists=[0.1, 0.3],
        )

        candidates, p1, p2 = two_pass_conflict_search(
            collection=mock,
            query_text="salary metric",
            query_embedding=None,
            atom_type="story",  # No structural pass for story
            metadata_filters={"company": "Google"},
        )

        assert p1 == 2
        assert p2 == 0  # No structural pass for story type
        assert len(candidates) == 2

    def test_pass1_similarity_computed(self):
        """Similarity score must be 1 - distance."""
        mock = Mock()
        mock.query.return_value = _make_query_result(
            ids=["doc1"],
            dists=[0.25],
        )

        candidates, _, _ = two_pass_conflict_search(
            collection=mock,
            query_text="test",
            query_embedding=None,
            atom_type="story",
            metadata_filters={},
        )

        assert abs(candidates[0]["similarity_score"] - 0.75) < 0.001

    def test_pass1_uses_embedding_when_provided(self):
        """If embedding provided, must pass query_embeddings to collection.query()."""
        mock = Mock()
        mock.query.return_value = _make_query_result(ids=["d1"])

        embedding = [0.1, 0.2, 0.3]
        two_pass_conflict_search(
            collection=mock,
            query_text="",
            query_embedding=embedding,
            atom_type="story",
            metadata_filters={},
        )

        call_kwargs = mock.query.call_args[1]
        assert "query_embeddings" in call_kwargs
        assert call_kwargs["query_embeddings"] == [embedding]

    def test_pass1_error_handled_gracefully(self):
        """collection.query() error → empty Pass 1, no crash."""
        mock = Mock()
        mock.query.side_effect = Exception("connection error")

        candidates, p1, p2 = two_pass_conflict_search(
            collection=mock,
            query_text="test",
            query_embedding=None,
            atom_type="story",
            metadata_filters={},
        )

        assert p1 == 0
        assert candidates == []


class TestPass2StructuralSearch:
    """Test Pass 2 — structural metadata filter."""

    def test_pass2_runs_for_metric_type(self):
        """Structural pass must run for 'metric' atom type."""
        mock = Mock()
        mock.query.return_value = _make_query_result(ids=["doc1"])
        mock.get.return_value = _make_get_result(ids=["doc2"])

        candidates, p1, p2 = two_pass_conflict_search(
            collection=mock,
            query_text="metric",
            query_embedding=None,
            atom_type="metric",
            metadata_filters={"company": "Google"},
        )

        assert mock.get.called  # Structural pass was executed
        assert p2 >= 0

    def test_pass2_skips_for_story_type(self):
        """Structural pass must NOT run for 'story' atom type."""
        mock = Mock()
        mock.query.return_value = _make_query_result(ids=["doc1"])

        two_pass_conflict_search(
            collection=mock,
            query_text="story",
            query_embedding=None,
            atom_type="story",
            metadata_filters={"company": "Google"},
        )

        mock.get.assert_not_called()

    def test_pass2_deduplicates_with_pass1(self):
        """Document found in both passes must appear only once in candidates."""
        mock = Mock()
        # Both passes return the same doc ID
        mock.query.return_value = _make_query_result(
            ids=["shared_doc", "semantic_only"],
            docs=["Shared content", "Semantic content"],
            dists=[0.1, 0.2],
        )
        mock.get.return_value = _make_get_result(
            ids=["shared_doc", "structural_only"],
            docs=["Shared content", "Structural content"],
        )

        candidates, p1, p2 = two_pass_conflict_search(
            collection=mock,
            query_text="metric test",
            query_embedding=None,
            atom_type="metric",
            metadata_filters={"company": "Google"},
        )

        # shared_doc must appear exactly once
        shared_ids = [c["doc_id"] for c in candidates if c["doc_id"] == "shared_doc"]
        assert len(shared_ids) == 1

        # Total: shared_doc(1) + semantic_only(1) + structural_only(1) = 3
        assert len(candidates) == 3

    def test_pass2_found_by_label(self):
        """Candidates from Pass 2 must have found_by='structural'."""
        mock = Mock()
        mock.query.return_value = _make_query_result(ids=["doc1"])
        mock.get.return_value = _make_get_result(ids=["doc2_structural"])

        candidates, _, _ = two_pass_conflict_search(
            collection=mock,
            query_text="fact",
            query_embedding=None,
            atom_type="fact",
            metadata_filters={"company": "Amazon"},
        )

        structural_candidates = [c for c in candidates if c["found_by"] == "structural"]
        assert len(structural_candidates) >= 1

    def test_pass2_skips_when_no_metadata_filters(self):
        """With no metadata filters, structural pass has no where clause → skips."""
        mock = Mock()
        mock.query.return_value = _make_query_result(ids=["doc1"])

        candidates, p1, p2 = two_pass_conflict_search(
            collection=mock,
            query_text="metric",
            query_embedding=None,
            atom_type="metric",
            metadata_filters={},  # No filters
        )

        assert p2 == 0  # Structural pass skipped (no filters to apply)

    def test_pass2_error_handled_gracefully(self):
        """collection.get() error in Pass 2 → Pass 1 results still returned."""
        mock = Mock()
        mock.query.return_value = _make_query_result(ids=["doc1"])
        mock.get.side_effect = Exception("metadata search error")

        candidates, p1, p2 = two_pass_conflict_search(
            collection=mock,
            query_text="metric",
            query_embedding=None,
            atom_type="metric",
            metadata_filters={"company": "Google"},
        )

        assert p1 == 1   # Pass 1 still worked
        assert p2 == 0   # Pass 2 failed but no crash
        assert len(candidates) == 1


class TestReturnStructure:
    """Test return value structure."""

    def test_returns_tuple_of_3(self):
        """Must return (candidates, p1_count, p2_count) tuple."""
        result = two_pass_conflict_search(
            collection=None,
            query_text="test",
            query_embedding=None,
            atom_type="metric",
            metadata_filters={},
        )
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_candidate_has_required_fields(self):
        """Each candidate dict must have doc_id, text, metadata, similarity_score, found_by."""
        mock = Mock()
        mock.query.return_value = _make_query_result(
            ids=["doc1"],
            docs=["Content"],
            metas=[{"company": "Google"}],
            dists=[0.2],
        )

        candidates, _, _ = two_pass_conflict_search(
            collection=mock,
            query_text="test",
            query_embedding=None,
            atom_type="story",
            metadata_filters={},
        )

        for c in candidates:
            assert "doc_id" in c
            assert "text" in c
            assert "metadata" in c
            assert "similarity_score" in c
            assert "found_by" in c

    def test_pass1_count_matches_semantic_results(self):
        """p1_count must equal number of unique semantic results."""
        mock = Mock()
        mock.query.return_value = _make_query_result(ids=["d1", "d2", "d3"])

        _, p1, _ = two_pass_conflict_search(
            collection=mock,
            query_text="test",
            query_embedding=None,
            atom_type="story",
            metadata_filters={},
        )

        assert p1 == 3
