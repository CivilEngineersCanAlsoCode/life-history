"""
Tests for semantic search with metadata filtering.

Tests cover:
- Semantic similarity search
- Metadata filtering (domain, company, project)
- Result ranking and scoring
- Batch search operations
- Edge cases and error handling
"""

import pytest
from unittest.mock import Mock, MagicMock

from life_brain.search.semantic_search import (
    SemanticSearch,
    SearchResult,
)


class TestSearchResult:
    """Test SearchResult dataclass."""

    def test_create_search_result(self):
        """Test creating search result."""
        result = SearchResult(
            doc_id="doc1",
            content="This is content",
            similarity_score=0.85,
            metadata={"company": "Google", "domain": "career"},
            distance=0.15,
        )

        assert result.doc_id == "doc1"
        assert result.similarity_score == 0.85

    def test_search_result_to_dict(self):
        """Test converting search result to dict."""
        result = SearchResult(
            doc_id="doc1",
            content="Content",
            similarity_score=0.92,
            metadata={"company": "Tech"},
            distance=0.08,
        )

        d = result.to_dict()
        assert d["doc_id"] == "doc1"
        assert d["similarity_score"] == 0.92
        assert d["metadata"]["company"] == "Tech"


class TestSemanticSearch:
    """Test semantic search functionality."""

    def test_create_search_no_collection(self):
        """Test creating search without collection."""
        search = SemanticSearch(collection=None)
        assert search.collection is None

    def test_search_without_collection(self):
        """Test searching when collection is not initialized."""
        search = SemanticSearch(collection=None)
        results, error = search.search("test query")

        assert len(results) == 0
        assert error is not None

    def test_search_empty_query(self):
        """Test searching with empty query."""
        mock_collection = Mock()
        search = SemanticSearch(collection=mock_collection)

        results, error = search.search("", query_embedding=None)

        assert len(results) == 0
        assert error is not None

    def test_build_metadata_filter_single(self):
        """Test building metadata filter with single criterion."""
        search = SemanticSearch(collection=None)

        filter_dict = search._build_metadata_filter(domain="career", company=None, project=None)

        assert filter_dict is not None
        assert "domain" in filter_dict

    def test_build_metadata_filter_multiple(self):
        """Test building metadata filter with multiple criteria."""
        search = SemanticSearch(collection=None)

        filter_dict = search._build_metadata_filter(
            domain="career", company="Google", project="ProjectX"
        )

        assert filter_dict is not None

    def test_build_metadata_filter_none(self):
        """Test building metadata filter with no criteria."""
        search = SemanticSearch(collection=None)

        filter_dict = search._build_metadata_filter(domain=None, company=None, project=None)

        assert filter_dict is None

    def test_parse_query_results_empty(self):
        """Test parsing empty query results."""
        search = SemanticSearch(collection=None)

        results = search._parse_query_results({})

        assert len(results) == 0

    def test_parse_query_results_single(self):
        """Test parsing single query result."""
        search = SemanticSearch(collection=None)

        query_results = {
            "ids": [["doc1"]],
            "documents": [["This is content"]],
            "distances": [[0.15]],
            "metadatas": [[{"company": "Google"}]],
        }

        results = search._parse_query_results(query_results)

        assert len(results) == 1
        assert results[0].doc_id == "doc1"
        assert results[0].similarity_score == 0.85  # 1 - 0.15

    def test_parse_query_results_multiple(self):
        """Test parsing multiple query results."""
        search = SemanticSearch(collection=None)

        query_results = {
            "ids": [["doc1", "doc2", "doc3"]],
            "documents": [["Content 1", "Content 2", "Content 3"]],
            "distances": [[0.10, 0.25, 0.45]],
            "metadatas": [[{"company": "A"}, {"company": "B"}, {"company": "C"}]],
        }

        results = search._parse_query_results(query_results)

        assert len(results) == 3
        # Should be sorted by similarity (highest first)
        assert results[0].similarity_score > results[1].similarity_score
        assert results[1].similarity_score > results[2].similarity_score

    def test_search_with_mocked_collection(self):
        """Test search with mocked ChromaDB collection."""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "ids": [["doc1"]],
            "documents": [["Test content"]],
            "distances": [[0.1]],
            "metadatas": [[{"company": "Google"}]],
        }

        search = SemanticSearch(collection=mock_collection)
        results, error = search.search("test query", top_k=5)

        assert error is None
        assert len(results) == 1
        assert results[0].doc_id == "doc1"

    def test_search_with_metadata_filtering(self):
        """Test search with metadata filters."""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "ids": [["doc1"]],
            "documents": [["Content"]],
            "distances": [[0.15]],
            "metadatas": [[{"company": "Google", "domain": "career"}]],
        }

        search = SemanticSearch(collection=mock_collection)
        results, error = search.search(
            "test query", domain="career", company="Google", top_k=5
        )

        assert error is None
        mock_collection.query.assert_called_once()

    def test_search_with_query_embedding(self):
        """Test search using pre-computed embedding."""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "ids": [["doc1"]],
            "documents": [["Content"]],
            "distances": [[0.2]],
            "metadatas": [[{}]],
        }

        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        search = SemanticSearch(collection=mock_collection)
        results, error = search.search("test query", query_embedding=embedding)

        assert error is None

    def test_batch_search(self):
        """Test batch search with multiple queries."""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "ids": [["doc1"]],
            "documents": [["Content"]],
            "distances": [[0.15]],
            "metadatas": [[{"company": "Google"}]],
        }

        search = SemanticSearch(collection=mock_collection)
        queries = ["query1", "query2", "query3"]
        batch_results = search.batch_search(queries, company="Google")

        assert len(batch_results) == 3
        for query, results, error in batch_results:
            assert query in queries
            assert isinstance(results, list)

    def test_get_statistics_no_collection(self):
        """Test getting statistics without collection."""
        search = SemanticSearch(collection=None)
        stats = search.get_statistics()

        assert stats["collection_initialized"] is False

    def test_get_statistics_with_collection(self):
        """Test getting statistics with collection."""
        mock_collection = Mock()
        mock_collection.count.return_value = 100

        search = SemanticSearch(collection=mock_collection)
        stats = search.get_statistics()

        assert stats["collection_initialized"] is True
        assert stats["total_documents"] == 100

    def test_filter_by_metadata_no_collection(self):
        """Test metadata filtering without collection."""
        search = SemanticSearch(collection=None)
        results, error = search.filter_by_metadata(company="Google")

        assert len(results) == 0
        assert error is not None

    def test_filter_by_metadata_with_collection(self):
        """Test metadata filtering with collection."""
        mock_collection = Mock()
        mock_collection.get.return_value = {
            "ids": ["doc1", "doc2"],
            "documents": ["Content 1", "Content 2"],
            "metadatas": [{"company": "Google"}, {"company": "Google"}],
        }

        search = SemanticSearch(collection=mock_collection)
        results, error = search.filter_by_metadata(company="Google")

        assert error is None
        assert len(results) == 2

    def test_similarity_score_clamping(self):
        """Test similarity scores are clamped to 0-1."""
        search = SemanticSearch(collection=None)

        # Test with invalid distance
        query_results = {
            "ids": [["doc1"]],
            "documents": [["Content"]],
            "distances": [[1.5]],  # Invalid distance
            "metadatas": [[{}]],
        }

        results = search._parse_query_results(query_results)

        assert len(results) > 0
        assert 0 <= results[0].similarity_score <= 1

    def test_result_ranking_by_similarity(self):
        """Test results are ranked by similarity score."""
        search = SemanticSearch(collection=None)

        query_results = {
            "ids": [["doc3", "doc1", "doc2"]],
            "documents": [["C", "A", "B"]],
            "distances": [[0.5, 0.1, 0.3]],
            "metadatas": [[{}, {}, {}]],
        }

        results = search._parse_query_results(query_results)

        # Should be sorted: doc1 (0.9), doc2 (0.7), doc3 (0.5)
        assert results[0].doc_id == "doc1"
        assert results[1].doc_id == "doc2"
        assert results[2].doc_id == "doc3"

    def test_metadata_preservation_in_results(self):
        """Test metadata is preserved in results."""
        search = SemanticSearch(collection=None)

        metadata = {"company": "Google", "domain": "career", "project": "CRR"}
        query_results = {
            "ids": [["doc1"]],
            "documents": [["Content"]],
            "distances": [[0.15]],
            "metadatas": [[metadata]],
        }

        results = search._parse_query_results(query_results)

        assert results[0].metadata["company"] == "Google"
        assert results[0].metadata["domain"] == "career"
        assert results[0].metadata["project"] == "CRR"

    def test_search_error_handling(self):
        """Test error handling in search."""
        mock_collection = Mock()
        mock_collection.query.side_effect = Exception("ChromaDB error")

        search = SemanticSearch(collection=mock_collection)
        results, error = search.search("test query")

        assert len(results) == 0
        assert error is not None
        assert "ChromaDB error" in error

    def test_whitespace_only_query_rejected(self):
        """issues-e6m: whitespace-only query must return error, not crash."""
        mock_collection = Mock()
        search = SemanticSearch(collection=mock_collection)

        results, error = search.search("   ", query_embedding=None)

        assert len(results) == 0
        assert error is not None
        assert "empty" in error.lower() or "whitespace" in error.lower()
        # Collection should NOT be called
        mock_collection.query.assert_not_called()

    def test_nonexistent_domain_returns_empty_not_error(self):
        """issues-ed3: querying a non-existent domain should return [] with no error."""
        mock_collection = Mock()
        mock_collection.query.side_effect = Exception(
            "Value 'does not exist' does not exist in column"
        )
        search = SemanticSearch(collection=mock_collection)

        results, error = search.search("career advice", domain="nonexistent_domain")

        assert len(results) == 0
        assert error is None  # Graceful empty return, not an error

    def test_complete_search_workflow(self):
        """Test complete search workflow."""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "ids": [["doc1", "doc2"]],
            "documents": [["Content 1", "Content 2"]],
            "distances": [[0.1, 0.3]],
            "metadatas": [[{"company": "Google", "domain": "career"}, {"company": "Google"}]],
        }

        search = SemanticSearch(collection=mock_collection)

        # Search with metadata filter
        results, error = search.search(
            "machine learning",
            domain="career",
            company="Google",
            top_k=10,
        )

        # Verify results
        assert error is None
        assert len(results) == 2
        assert results[0].similarity_score > results[1].similarity_score
        assert all(r.metadata["company"] == "Google" for r in results)

        # Export as dicts
        exported = [r.to_dict() for r in results]
        assert all("doc_id" in e for e in exported)
        assert all("similarity_score" in e for e in exported)


class TestNullEmbeddingHandling:
    """Regression test for issues-2p4: null document embedding error."""

    def test_search_with_null_embedding_query(self):
        """Searching with None query_embedding and empty query must return error."""
        mock_collection = Mock()
        search = SemanticSearch(collection=mock_collection)
        results, error = search.search("", query_embedding=None)
        assert len(results) == 0
        assert error is not None

    def test_search_with_valid_embedding_bypasses_text_query(self):
        """Non-null embedding should allow empty text query."""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "ids": [["doc1"]],
            "documents": [["Some content"]],
            "distances": [[0.2]],
            "metadatas": [[{}]],
        }
        search = SemanticSearch(collection=mock_collection)
        # Empty text but valid embedding → should work
        results, error = search.search("", query_embedding=[0.1, 0.2, 0.3])
        assert error is None
        assert len(results) == 1


class TestLargeResultSets:
    """Regression tests for issues-y2g: search with >1000 results — verify pagination."""

    def test_top_k_1000_accepted(self):
        """Requesting top_k=1000 must not crash — collection called with that value."""
        from unittest.mock import Mock
        from life_brain.search.semantic_search import SemanticSearch

        mock_collection = Mock()
        # Return 1000 mock results
        mock_collection.query.return_value = {
            "ids": [[f"doc{i}" for i in range(1000)]],
            "documents": [[f"Content {i}" for i in range(1000)]],
            "distances": [[0.1 + (i / 10000) for i in range(1000)]],
            "metadatas": [[{"company": "Google"}] * 1000],
        }

        search = SemanticSearch(collection=mock_collection)
        results, error = search.search("career advice", top_k=1000)

        assert error is None
        assert len(results) == 1000
        # Verify query was called with correct n_results
        call_kwargs = mock_collection.query.call_args[1]
        assert call_kwargs.get("n_results") == 1000

    def test_large_result_set_sorted_by_similarity(self):
        """1000-result set must still be sorted by similarity (highest first)."""
        from unittest.mock import Mock
        from life_brain.search.semantic_search import SemanticSearch

        mock_collection = Mock()
        # Return results in random order
        import random
        n = 500
        distances = [random.uniform(0.05, 0.95) for _ in range(n)]
        mock_collection.query.return_value = {
            "ids": [[f"doc{i}" for i in range(n)]],
            "documents": [[f"Content {i}" for i in range(n)]],
            "distances": [distances],
            "metadatas": [[{}] * n],
        }

        search = SemanticSearch(collection=mock_collection)
        results, error = search.search("test", top_k=n)

        assert error is None
        for i in range(len(results) - 1):
            assert results[i].similarity_score >= results[i + 1].similarity_score

    def test_filter_by_metadata_limit_respected(self):
        """filter_by_metadata with limit=1000 should call collection.get with that limit."""
        from unittest.mock import Mock
        from life_brain.search.semantic_search import SemanticSearch

        mock_collection = Mock()
        mock_collection.get.return_value = {
            "ids": [f"doc{i}" for i in range(500)],
            "documents": [f"Content {i}" for i in range(500)],
            "metadatas": [{"company": "Amazon"}] * 500,
        }

        search = SemanticSearch(collection=mock_collection)
        results, error = search.filter_by_metadata(company="Amazon", limit=1000)

        assert error is None
        call_kwargs = mock_collection.get.call_args[1]
        assert call_kwargs.get("limit") == 1000

    def test_top_k_exceeds_collection_size_no_crash(self):
        """Requesting more results than collection size must not crash."""
        from unittest.mock import Mock
        from life_brain.search.semantic_search import SemanticSearch

        mock_collection = Mock()
        # Collection has only 5 docs but we request 1000
        mock_collection.query.return_value = {
            "ids": [["doc1", "doc2", "doc3"]],
            "documents": [["Content 1", "Content 2", "Content 3"]],
            "distances": [[0.1, 0.2, 0.3]],
            "metadatas": [[{}, {}, {}]],
        }

        search = SemanticSearch(collection=mock_collection)
        results, error = search.search("test query", top_k=1000)

        # Should return however many docs the collection has
        assert error is None
        assert len(results) == 3


class TestPerformanceMockTests:
    """Regression tests for issues-85d/q5w: performance edge cases (mocked)."""

    def test_batch_search_100_queries_no_crash(self):
        """batch_search with 100 queries must complete without crash."""
        from unittest.mock import Mock
        from life_brain.search.semantic_search import SemanticSearch

        mock_collection = Mock()
        mock_collection.query.return_value = {
            "ids": [["doc1"]],
            "documents": [["Content"]],
            "distances": [[0.2]],
            "metadatas": [[{"company": "Google"}]],
        }

        search = SemanticSearch(collection=mock_collection)
        queries = [f"query {i}" for i in range(100)]
        batch_results = search.batch_search(queries)

        assert len(batch_results) == 100
        assert all(isinstance(r, tuple) and len(r) == 3 for r in batch_results)

    def test_search_returns_quickly_with_small_k(self):
        """Search with top_k=5 must return in reasonable time (< 1 second with mock)."""
        from unittest.mock import Mock
        from life_brain.search.semantic_search import SemanticSearch
        import time

        mock_collection = Mock()
        mock_collection.query.return_value = {
            "ids": [["doc1"]],
            "documents": [["Content"]],
            "distances": [[0.1]],
            "metadatas": [[{}]],
        }

        search = SemanticSearch(collection=mock_collection)
        start = time.monotonic()
        results, error = search.search("test query", top_k=5)
        elapsed = time.monotonic() - start

        assert elapsed < 1.0  # Should be instant with mock
        assert error is None

    def test_ingestion_batch_timeout_scenario(self):
        """Simulate batch ingestion with mock — verify timeout scenario handled."""
        from unittest.mock import Mock
        from life_brain.db.ingestion_wrapper import ResilientIngestion

        # Simulate a collection that raises on upsert (timeout scenario)
        mock_collection = Mock()
        mock_collection.upsert.side_effect = TimeoutError("Operation timed out")

        wrapper = ResilientIngestion(collection=mock_collection)
        result = wrapper.ingest_with_retry(
            doc_id="timeout_doc_001",
            text="Test content for timeout scenario. " * 5,
            metadata={"company": "TestCo", "domain": "career"},
        )

        # Should fail gracefully with a non-success status
        assert result["status"] != "success"
