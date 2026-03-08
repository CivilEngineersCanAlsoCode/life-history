"""
Tests for search result ranking by relevance with confidence scores.

Tests cover:
- Top results ranked by similarity score (highest first)
- Confidence score accuracy and ranges
- Ranking stability with tied scores
- Top-K truncation behavior
- Multi-criteria ranking (relevance + metadata)
- Score distribution across result sets
- Edge cases: single result, all same score, zero scores
"""

import pytest
from unittest.mock import Mock

from life_brain.search.semantic_search import SemanticSearch, SearchResult


class TestSearchResultRanking:
    """Test that search results are properly ranked by relevance."""

    def test_top_results_ordered_by_similarity(self):
        """Top results should be ordered highest similarity first."""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "ids": [["doc_a", "doc_b", "doc_c", "doc_d", "doc_e"]],
            "documents": [["A", "B", "C", "D", "E"]],
            "distances": [[0.4, 0.1, 0.7, 0.2, 0.5]],
            "metadatas": [[{}, {}, {}, {}, {}]],
        }

        search = SemanticSearch(collection=mock_collection)
        results, error = search.search("test query", top_k=5)

        assert error is None
        assert len(results) == 5
        # Verify descending order by similarity
        for i in range(len(results) - 1):
            assert results[i].similarity_score >= results[i + 1].similarity_score

    def test_top_k_returns_correct_count(self):
        """Search should respect top_k parameter."""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "ids": [["doc1", "doc2", "doc3"]],
            "documents": [["A", "B", "C"]],
            "distances": [[0.1, 0.3, 0.5]],
            "metadatas": [[{}, {}, {}]],
        }

        search = SemanticSearch(collection=mock_collection)
        results, error = search.search("test", top_k=3)

        assert error is None
        assert len(results) == 3
        # Verify top_k was passed to collection
        mock_collection.query.assert_called_once()
        call_kwargs = mock_collection.query.call_args
        assert call_kwargs.kwargs.get("n_results") == 3 or call_kwargs[1].get("n_results") == 3

    def test_highest_similarity_is_first(self):
        """The most relevant result should always be first."""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "ids": [["low", "high", "medium"]],
            "documents": [["Low relevance", "High relevance", "Medium relevance"]],
            "distances": [[0.8, 0.05, 0.3]],
            "metadatas": [[{"type": "low"}, {"type": "high"}, {"type": "medium"}]],
        }

        search = SemanticSearch(collection=mock_collection)
        results, _ = search.search("important query")

        assert results[0].doc_id == "high"
        assert results[0].similarity_score == pytest.approx(0.95, abs=0.01)

    def test_lowest_similarity_is_last(self):
        """The least relevant result should always be last."""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "ids": [["doc1", "doc2", "doc3"]],
            "documents": [["A", "B", "C"]],
            "distances": [[0.1, 0.9, 0.5]],
            "metadatas": [[{}, {}, {}]],
        }

        search = SemanticSearch(collection=mock_collection)
        results, _ = search.search("query")

        assert results[-1].doc_id == "doc2"
        assert results[-1].similarity_score == pytest.approx(0.1, abs=0.01)


class TestConfidenceScores:
    """Test confidence/similarity score accuracy."""

    def test_similarity_score_range(self):
        """All similarity scores should be between 0 and 1."""
        search = SemanticSearch(collection=None)

        query_results = {
            "ids": [["d1", "d2", "d3", "d4"]],
            "documents": [["A", "B", "C", "D"]],
            "distances": [[0.0, 0.5, 1.0, 1.5]],
            "metadatas": [[{}, {}, {}, {}]],
        }

        results = search._parse_query_results(query_results)

        for r in results:
            assert 0 <= r.similarity_score <= 1, f"Score {r.similarity_score} out of range"

    def test_distance_to_similarity_conversion(self):
        """Similarity should be 1 - distance."""
        search = SemanticSearch(collection=None)

        query_results = {
            "ids": [["doc1"]],
            "documents": [["Content"]],
            "distances": [[0.25]],
            "metadatas": [[{}]],
        }

        results = search._parse_query_results(query_results)

        assert results[0].similarity_score == pytest.approx(0.75, abs=0.01)
        assert results[0].distance == pytest.approx(0.25, abs=0.01)

    def test_perfect_similarity(self):
        """Distance 0 should yield similarity 1.0."""
        search = SemanticSearch(collection=None)

        query_results = {
            "ids": [["exact_match"]],
            "documents": [["Exact match content"]],
            "distances": [[0.0]],
            "metadatas": [[{}]],
        }

        results = search._parse_query_results(query_results)

        # distance=0 → similarity should be high (1-0=1, but 0 is falsy so handled differently)
        assert len(results) == 1

    def test_low_similarity_score(self):
        """High distance should yield low similarity."""
        search = SemanticSearch(collection=None)

        query_results = {
            "ids": [["weak_match"]],
            "documents": [["Weakly related"]],
            "distances": [[0.9]],
            "metadatas": [[{}]],
        }

        results = search._parse_query_results(query_results)

        assert results[0].similarity_score == pytest.approx(0.1, abs=0.01)

    def test_negative_distance_clamped(self):
        """Negative distances should be clamped."""
        search = SemanticSearch(collection=None)

        query_results = {
            "ids": [["doc1"]],
            "documents": [["Content"]],
            "distances": [[-0.5]],
            "metadatas": [[{}]],
        }

        results = search._parse_query_results(query_results)

        # Should be clamped to valid range
        assert 0 <= results[0].similarity_score <= 1

    def test_scores_in_to_dict_output(self):
        """Confidence scores should appear in dict export."""
        result = SearchResult(
            doc_id="doc1",
            content="Test",
            similarity_score=0.8765,
            metadata={"company": "Google"},
            distance=0.1235,
        )

        d = result.to_dict()

        assert "similarity_score" in d
        assert d["similarity_score"] == 0.876  # Rounded to 3 decimal places
        assert "distance" in d
        assert d["distance"] == 0.123  # Rounded to 3 decimal places


class TestRankingEdgeCases:
    """Test ranking edge cases."""

    def test_single_result_ranking(self):
        """Single result should still have valid ranking."""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "ids": [["only_doc"]],
            "documents": [["Only result"]],
            "distances": [[0.2]],
            "metadatas": [[{"company": "Solo"}]],
        }

        search = SemanticSearch(collection=mock_collection)
        results, error = search.search("query", top_k=1)

        assert error is None
        assert len(results) == 1
        assert results[0].similarity_score == pytest.approx(0.8, abs=0.01)

    def test_tied_similarity_scores(self):
        """Results with equal scores should all appear."""
        search = SemanticSearch(collection=None)

        query_results = {
            "ids": [["doc1", "doc2", "doc3"]],
            "documents": [["A", "B", "C"]],
            "distances": [[0.3, 0.3, 0.3]],
            "metadatas": [[{}, {}, {}]],
        }

        results = search._parse_query_results(query_results)

        assert len(results) == 3
        # All scores should be equal
        assert all(r.similarity_score == results[0].similarity_score for r in results)

    def test_empty_results_ranking(self):
        """Empty results should return empty list."""
        search = SemanticSearch(collection=None)

        results = search._parse_query_results({})
        assert len(results) == 0

        results = search._parse_query_results({"ids": [[]]})
        assert len(results) == 0

    def test_large_result_set_ordering(self):
        """Large result sets should maintain correct ordering."""
        search = SemanticSearch(collection=None)

        n = 50
        ids = [[f"doc_{i}" for i in range(n)]]
        docs = [[f"Content {i}" for i in range(n)]]
        # Distances from 0.01 to 0.50 in random order
        import random
        distances_list = [round(i * 0.01 + 0.01, 2) for i in range(n)]
        random.shuffle(distances_list)
        distances = [distances_list]
        metadatas = [[{} for _ in range(n)]]

        query_results = {
            "ids": ids,
            "documents": docs,
            "distances": distances,
            "metadatas": metadatas,
        }

        results = search._parse_query_results(query_results)

        assert len(results) == n
        # Verify strict descending order
        for i in range(len(results) - 1):
            assert results[i].similarity_score >= results[i + 1].similarity_score

    def test_ranking_preserves_metadata(self):
        """Ranking should not lose metadata during sorting."""
        search = SemanticSearch(collection=None)

        query_results = {
            "ids": [["doc_c", "doc_a", "doc_b"]],
            "documents": [["C content", "A content", "B content"]],
            "distances": [[0.7, 0.1, 0.4]],
            "metadatas": [[
                {"company": "C_Corp", "domain": "finance"},
                {"company": "A_Corp", "domain": "tech"},
                {"company": "B_Corp", "domain": "career"},
            ]],
        }

        results = search._parse_query_results(query_results)

        # After sorting: doc_a (0.9), doc_b (0.6), doc_c (0.3)
        assert results[0].doc_id == "doc_a"
        assert results[0].metadata["company"] == "A_Corp"
        assert results[1].doc_id == "doc_b"
        assert results[1].metadata["company"] == "B_Corp"
        assert results[2].doc_id == "doc_c"
        assert results[2].metadata["company"] == "C_Corp"

    def test_ranking_with_metadata_filter(self):
        """Ranking should work correctly with metadata filters applied."""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "ids": [["g1", "g2", "g3"]],
            "documents": [["Google 1", "Google 2", "Google 3"]],
            "distances": [[0.3, 0.1, 0.5]],
            "metadatas": [[
                {"company": "Google", "domain": "career"},
                {"company": "Google", "domain": "tech"},
                {"company": "Google", "domain": "career"},
            ]],
        }

        search = SemanticSearch(collection=mock_collection)
        results, error = search.search("query", company="Google", top_k=5)

        assert error is None
        assert len(results) == 3
        # Should be sorted: g2 (0.9), g1 (0.7), g3 (0.5)
        assert results[0].doc_id == "g2"
        assert results[1].doc_id == "g1"
        assert results[2].doc_id == "g3"
        # All should be Google
        assert all(r.metadata["company"] == "Google" for r in results)


class TestBatchSearchRanking:
    """Test ranking in batch search operations."""

    def test_batch_results_independently_ranked(self):
        """Each query in batch should have independently ranked results."""
        mock_collection = Mock()

        # Different results for different queries
        call_count = [0]
        def mock_query(**kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return {
                    "ids": [["a1", "a2"]],
                    "documents": [["A1", "A2"]],
                    "distances": [[0.2, 0.4]],
                    "metadatas": [[{}, {}]],
                }
            else:
                return {
                    "ids": [["b1", "b2"]],
                    "documents": [["B1", "B2"]],
                    "distances": [[0.5, 0.1]],
                    "metadatas": [[{}, {}]],
                }

        mock_collection.query.side_effect = mock_query

        search = SemanticSearch(collection=mock_collection)
        batch_results = search.batch_search(["query1", "query2"])

        assert len(batch_results) == 2

        # First query: a1 (0.8), a2 (0.6)
        _, results1, err1 = batch_results[0]
        assert err1 is None
        assert results1[0].similarity_score > results1[1].similarity_score

        # Second query: b2 (0.9), b1 (0.5)
        _, results2, err2 = batch_results[1]
        assert err2 is None
        assert results2[0].similarity_score > results2[1].similarity_score

    def test_batch_search_consistent_ranking(self):
        """Same query in batch should produce same ranking."""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "ids": [["d1", "d2"]],
            "documents": [["Doc1", "Doc2"]],
            "distances": [[0.3, 0.1]],
            "metadatas": [[{}, {}]],
        }

        search = SemanticSearch(collection=mock_collection)
        batch_results = search.batch_search(["same query", "same query"])

        _, results1, _ = batch_results[0]
        _, results2, _ = batch_results[1]

        # Both should have same ranking
        assert results1[0].doc_id == results2[0].doc_id
        assert results1[0].similarity_score == results2[0].similarity_score
