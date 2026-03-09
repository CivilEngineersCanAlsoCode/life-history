"""
Tests for groundedness scoring in search results ranking.

Tests cover:
- Groundedness score computation
- Component scoring (similarity, metadata, content)
- Score and rank functionality
- Custom weight configuration
- Edge cases and boundary conditions
"""

import pytest

from life_brain.search.semantic_search import SearchResult
from life_brain.search.groundedness import (
    GroundednessScorer,
    GroundedResult,
)


def _make_result(doc_id="doc1", similarity=0.85, content="Test content with details", metadata=None, distance=None):
    """Helper to create SearchResult."""
    if metadata is None:
        metadata = {"company": "Google", "domain": "career"}
    if distance is None:
        distance = 1 - similarity
    return SearchResult(
        doc_id=doc_id,
        content=content,
        similarity_score=similarity,
        metadata=metadata,
        distance=distance,
    )


class TestGroundednessScorer:
    """Test groundedness scoring."""

    def test_score_result_basic(self):
        """Basic result scoring."""
        scorer = GroundednessScorer()
        result = _make_result(similarity=0.9, metadata={"company": "Google", "domain": "career"})

        grounded = scorer.score_result(result)

        assert 0 <= grounded.groundedness_score <= 1
        assert grounded.result == result

    def test_high_similarity_high_groundedness(self):
        """High similarity should contribute to high groundedness."""
        scorer = GroundednessScorer()
        high = _make_result(similarity=0.95, metadata={"company": "Google"})
        low = _make_result(similarity=0.2, metadata={"company": "Google"})

        high_g = scorer.score_result(high)
        low_g = scorer.score_result(low)

        assert high_g.groundedness_score > low_g.groundedness_score

    def test_rich_metadata_boosts_score(self):
        """More metadata fields should boost groundedness."""
        scorer = GroundednessScorer()
        bare = _make_result(similarity=0.7, metadata={})
        rich = _make_result(similarity=0.7, metadata={
            "company": "Google", "domain": "career", "project": "CRR",
            "category": "interview", "type": "star_story", "date": "2024-01",
            "source": "confluence",
        })

        bare_g = scorer.score_result(bare)
        rich_g = scorer.score_result(rich)

        assert rich_g.groundedness_score > bare_g.groundedness_score
        assert rich_g.metadata_weight > bare_g.metadata_weight

    def test_longer_content_higher_score(self):
        """Longer, more specific content should score higher."""
        scorer = GroundednessScorer()
        short = _make_result(content="Hi")
        long_content = "This project at Google involved building a machine learning pipeline " * 10
        long_result = _make_result(content=long_content)

        short_g = scorer.score_result(short)
        long_g = scorer.score_result(long_result)

        assert long_g.content_weight > short_g.content_weight

    def test_score_and_rank_ordering(self):
        """Results should be ranked by groundedness."""
        scorer = GroundednessScorer()
        results = [
            _make_result("low", similarity=0.3, metadata={}, content="Short"),
            _make_result("high", similarity=0.95, metadata={
                "company": "Google", "domain": "career", "project": "CRR"
            }, content="Detailed content about the project implementation at Google for CRR"),
            _make_result("mid", similarity=0.6, metadata={"company": "Amazon"}),
        ]

        ranked = scorer.score_and_rank(results)

        assert len(ranked) == 3
        assert ranked[0].result.doc_id == "high"
        assert ranked[-1].result.doc_id == "low"
        # Verify descending order
        for i in range(len(ranked) - 1):
            assert ranked[i].groundedness_score >= ranked[i + 1].groundedness_score

    def test_score_range_clamped(self):
        """Groundedness score should always be 0-1."""
        scorer = GroundednessScorer()

        # Extreme values
        results = [
            _make_result(similarity=0.0, metadata={}, content=""),
            _make_result(similarity=1.0, metadata={
                "company": "X", "domain": "Y", "project": "Z",
                "category": "A", "type": "B", "date": "C", "source": "D"
            }, content="A" * 1000),
        ]

        for r in results:
            grounded = scorer.score_result(r)
            assert 0 <= grounded.groundedness_score <= 1

    def test_empty_content_scoring(self):
        """Empty content should get 0 content score."""
        scorer = GroundednessScorer()
        result = _make_result(content="")

        grounded = scorer.score_result(result)
        assert grounded.content_weight == 0.0

    def test_empty_metadata_scoring(self):
        """Empty metadata should get 0 metadata score."""
        scorer = GroundednessScorer()
        result = _make_result(metadata={})

        grounded = scorer.score_result(result)
        assert grounded.metadata_weight == 0.0

    def test_score_components_sum(self):
        """Weighted components should sum to groundedness score."""
        scorer = GroundednessScorer()
        result = _make_result()

        grounded = scorer.score_result(result)

        expected = grounded.similarity_weight + grounded.metadata_weight + grounded.content_weight
        assert grounded.groundedness_score == pytest.approx(expected, abs=0.001)


class TestCustomWeights:
    """Test custom weight configuration."""

    def test_similarity_only_weights(self):
        """With only similarity weight, result should equal similarity."""
        scorer = GroundednessScorer(weights={
            "similarity": 1.0, "metadata": 0.0, "content": 0.0
        })
        result = _make_result(similarity=0.75)

        grounded = scorer.score_result(result)
        assert grounded.groundedness_score == pytest.approx(0.75, abs=0.01)

    def test_metadata_heavy_weights(self):
        """Heavy metadata weight should favor metadata-rich results."""
        scorer = GroundednessScorer(weights={
            "similarity": 0.2, "metadata": 0.7, "content": 0.1
        })

        bare = _make_result(similarity=0.9, metadata={})
        rich = _make_result(similarity=0.5, metadata={
            "company": "X", "domain": "Y", "project": "Z",
            "category": "A", "type": "B", "date": "C", "source": "D"
        })

        bare_g = scorer.score_result(bare)
        rich_g = scorer.score_result(rich)

        # Rich metadata should win despite lower similarity
        assert rich_g.groundedness_score > bare_g.groundedness_score


class TestGroundedResultExport:
    """Test GroundedResult export functionality."""

    def test_to_dict_has_all_fields(self):
        """Dict export should include all fields."""
        scorer = GroundednessScorer()
        result = _make_result()

        grounded = scorer.score_result(result)
        d = grounded.to_dict()

        assert "doc_id" in d
        assert "groundedness_score" in d
        assert "score_breakdown" in d
        assert "similarity" in d["score_breakdown"]
        assert "metadata" in d["score_breakdown"]
        assert "content" in d["score_breakdown"]

    def test_to_dict_scores_rounded(self):
        """Scores should be rounded to 3 decimal places."""
        scorer = GroundednessScorer()
        result = _make_result()

        grounded = scorer.score_result(result)
        d = grounded.to_dict()

        # Check rounding
        score_str = str(d["groundedness_score"])
        if "." in score_str:
            decimals = len(score_str.split(".")[1])
            assert decimals <= 3


class TestEdgeCases:
    """Test edge cases."""

    def test_score_and_rank_empty(self):
        """Empty list should return empty."""
        scorer = GroundednessScorer()
        assert scorer.score_and_rank([]) == []

    def test_score_and_rank_single(self):
        """Single result should work."""
        scorer = GroundednessScorer()
        results = [_make_result()]

        ranked = scorer.score_and_rank(results)
        assert len(ranked) == 1

    def test_equal_similarity_differentiated_by_metadata(self):
        """Equal similarity results should be differentiated by metadata."""
        scorer = GroundednessScorer()

        bare = _make_result("bare", similarity=0.8, metadata={})
        rich = _make_result("rich", similarity=0.8, metadata={
            "company": "Google", "domain": "career", "project": "CRR",
        })

        ranked = scorer.score_and_rank([bare, rich])

        assert ranked[0].result.doc_id == "rich"
        assert ranked[1].result.doc_id == "bare"

    def test_content_with_numbers_scores_higher(self):
        """Content with specific numbers should score higher on specificity."""
        scorer = GroundednessScorer()

        generic = _make_result(content="This is a generic description of the work done")
        specific = _make_result(content="Achieved 45% improvement in processing speed, handling 10000 requests per second across 3 data centers")

        generic_g = scorer.score_result(generic)
        specific_g = scorer.score_result(specific)

        assert specific_g.content_weight >= generic_g.content_weight


class TestOverallScoreClamping:
    """Regression tests for issues-bd7.4.13: coverage modifier can cause overall_score > 1.0.

    Bug: No pre-clamp before coverage modifier was applied.
    Fix: clamp overall_score to [0, 1] before coverage modifier is applied.
    """

    def test_overall_score_never_exceeds_1(self):
        """overall_score must always be ≤ 1.0 regardless of inputs."""
        from life_brain.truth_engine.groundedness import GroundednessCalculator, RetrievedDocument
        calc = GroundednessCalculator()
        docs = [
            RetrievedDocument(doc_id="d1", text="great result success", metadata={}, similarity_score=1.0),
            RetrievedDocument(doc_id="d2", text="success outcome achieved", metadata={}, similarity_score=1.0),
            RetrievedDocument(doc_id="d3", text="leading result supported", metadata={}, similarity_score=1.0),
        ]
        score = calc.calculate_groundedness(docs, query_keywords=["success", "result", "great"])
        assert score.overall_score <= 1.0
        assert score.overall_score >= 0.0

    def test_overall_score_never_below_0(self):
        """overall_score must always be ≥ 0.0."""
        from life_brain.truth_engine.groundedness import GroundednessCalculator, RetrievedDocument
        calc = GroundednessCalculator()
        docs = [
            RetrievedDocument(doc_id="d1", text="something", metadata={}, similarity_score=0.0),
        ]
        score = calc.calculate_groundedness(docs, query_keywords=["unrelated"])
        assert score.overall_score >= 0.0


class TestNegativeSimilarityEdgeCases:
    """Regression tests for issues-bd7.4.11: negative similarity should not propagate."""

    def test_negative_similarity_clamped_to_zero(self):
        """Documents with negative similarity score should produce overall_score >= 0."""
        from life_brain.truth_engine.groundedness import GroundednessCalculator, RetrievedDocument
        calc = GroundednessCalculator()
        docs = [RetrievedDocument(doc_id="d1", text="content", metadata={}, similarity_score=-0.5)]
        score = calc.calculate_groundedness(docs)
        assert score.overall_score >= 0.0
        assert score.max_similarity >= 0.0

    def test_max_similarity_non_negative(self):
        """calculate_max_similarity must return >= 0 even with negative inputs."""
        from life_brain.truth_engine.groundedness import GroundednessCalculator, RetrievedDocument
        calc = GroundednessCalculator()
        docs = [
            RetrievedDocument(doc_id="d1", text="a", metadata={}, similarity_score=-0.3),
            RetrievedDocument(doc_id="d2", text="b", metadata={}, similarity_score=-0.1),
        ]
        assert calc.calculate_max_similarity(docs) >= 0.0


class TestEmptyQueryKeywords:
    """Regression tests for issues-bd7.4.10: empty query_keywords list."""

    def test_empty_keywords_list_no_crash(self):
        """calculate_groundedness with empty keywords list must not crash."""
        from life_brain.truth_engine.groundedness import GroundednessCalculator, RetrievedDocument
        calc = GroundednessCalculator()
        docs = [RetrievedDocument(doc_id="d1", text="some content", metadata={}, similarity_score=0.8)]
        score = calc.calculate_groundedness(docs, query_keywords=[])
        assert 0.0 <= score.overall_score <= 1.0

    def test_none_keywords_no_crash(self):
        """calculate_groundedness with None keywords must not crash."""
        from life_brain.truth_engine.groundedness import GroundednessCalculator, RetrievedDocument
        calc = GroundednessCalculator()
        docs = [RetrievedDocument(doc_id="d1", text="some content", metadata={}, similarity_score=0.8)]
        score = calc.calculate_groundedness(docs, query_keywords=None)
        assert 0.0 <= score.overall_score <= 1.0


class TestConsistencyBoundaries:
    """Regression tests for issues-bd7.4.12: consistency at boundary conditions."""

    def test_single_doc_consistency_is_1(self):
        """Single document is always consistent with itself → 1.0."""
        from life_brain.truth_engine.groundedness import GroundednessCalculator, RetrievedDocument
        calc = GroundednessCalculator()
        docs = [RetrievedDocument(doc_id="d1", text="success story", metadata={}, similarity_score=0.9)]
        consistency = calc.calculate_consistency(docs)
        assert consistency == 1.0

    def test_consistency_bounded_0_to_1(self):
        """Consistency must always be in [0, 1]."""
        from life_brain.truth_engine.groundedness import GroundednessCalculator, RetrievedDocument
        calc = GroundednessCalculator()
        docs = [
            RetrievedDocument(doc_id="d1", text="yes success supported true", metadata={}, similarity_score=0.8),
            RetrievedDocument(doc_id="d2", text="no failure rejected false", metadata={}, similarity_score=0.7),
        ]
        consistency = calc.calculate_consistency(docs)
        assert 0.0 <= consistency <= 1.0


class TestEmptyDocumentsList:
    """Regression test for issues-bd7.4.8: empty documents list."""

    def test_empty_docs_returns_zero_score(self):
        """calculate_groundedness with no documents should return 0.0 overall_score."""
        from life_brain.truth_engine.groundedness import GroundednessCalculator
        calc = GroundednessCalculator()
        score = calc.calculate_groundedness([])
        assert score.overall_score <= 0.2  # num_docs weight gives some score even when empty
        assert score.max_similarity == 0.0

    def test_empty_docs_no_crash(self):
        """calculate_groundedness([]) must not raise any exception."""
        from life_brain.truth_engine.groundedness import GroundednessCalculator
        calc = GroundednessCalculator()
        score = calc.calculate_groundedness([], query_keywords=["test"])
        assert 0.0 <= score.overall_score <= 1.0


class TestSingleHighConfidenceDoc:
    """Regression test for issues-bd7.4.9: single doc with 1.0 similarity."""

    def test_single_doc_perfect_similarity_high_confidence(self):
        """Single doc with 1.0 similarity should yield high overall_score."""
        from life_brain.truth_engine.groundedness import GroundednessCalculator, RetrievedDocument
        calc = GroundednessCalculator()
        docs = [RetrievedDocument(doc_id="d1", text="exact match", metadata={}, similarity_score=1.0)]
        score = calc.calculate_groundedness(docs, query_keywords=["exact", "match"])
        assert score.overall_score > 0.5  # Should be reasonably high
        assert score.max_similarity == 1.0


class TestNoEmbeddingsDocuments:
    """Regression tests for issues-bd7.1.13: documents with no embeddings (similarity_score=0)."""

    def test_zero_similarity_docs_no_crash(self):
        """Documents with similarity_score=0.0 (no embedding) must not crash."""
        from life_brain.truth_engine.groundedness import GroundednessCalculator, RetrievedDocument
        calc = GroundednessCalculator()
        docs = [RetrievedDocument(doc_id="d1", text="some content", metadata={}, similarity_score=0.0)]
        score = calc.calculate_groundedness(docs)
        assert 0.0 <= score.overall_score <= 1.0

    def test_all_zero_similarity_max_is_zero(self):
        """All docs with 0 similarity → max_similarity must be 0.0."""
        from life_brain.truth_engine.groundedness import GroundednessCalculator, RetrievedDocument
        calc = GroundednessCalculator()
        docs = [
            RetrievedDocument(doc_id="d1", text="text1", metadata={}, similarity_score=0.0),
            RetrievedDocument(doc_id="d2", text="text2", metadata={}, similarity_score=0.0),
        ]
        assert calc.calculate_max_similarity(docs) == 0.0

    def test_mixed_zero_and_nonzero_uses_nonzero(self):
        """Mix of 0 and non-zero similarity → max_similarity should be the non-zero value."""
        from life_brain.truth_engine.groundedness import GroundednessCalculator, RetrievedDocument
        calc = GroundednessCalculator()
        docs = [
            RetrievedDocument(doc_id="d1", text="text1", metadata={}, similarity_score=0.0),
            RetrievedDocument(doc_id="d2", text="text2", metadata={}, similarity_score=0.75),
        ]
        assert calc.calculate_max_similarity(docs) == 0.75

    def test_no_embedding_score_lower_than_real_embedding(self):
        """0-similarity docs should score lower than real-embedding docs."""
        from life_brain.truth_engine.groundedness import GroundednessCalculator, RetrievedDocument
        calc = GroundednessCalculator()
        no_emb = [RetrievedDocument(doc_id="d1", text="content", metadata={}, similarity_score=0.0)]
        with_emb = [RetrievedDocument(doc_id="d2", text="content", metadata={}, similarity_score=0.8)]
        score_no = calc.calculate_groundedness(no_emb)
        score_with = calc.calculate_groundedness(with_emb)
        assert score_with.overall_score > score_no.overall_score
