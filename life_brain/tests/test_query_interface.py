"""
Tests for Search & Query Interface and Vector Quality Validation.

Tests cover:
- QueryParser: domain/company/atom_type extraction from natural language
- SearchQueryInterface: search, search_by_example, multi_search, evaluate_queries
- RankedResult: confidence labels, ranking, formatting
- Vector quality metrics: precision@K, recall@K, MRR
- Edge cases: empty query, no collection, no results, error handling
"""

import pytest
from unittest.mock import Mock

from life_brain.retrieval.query_interface import (
    QueryParser,
    SearchQueryInterface,
    QueryResult,
    RankedResult,
    ParsedQuery,
    _confidence_label,
)


# ---------- Helpers ----------

def _make_collection(ids=None, docs=None, metas=None, dists=None):
    """Build a mock ChromaDB collection."""
    n = len(ids or [])
    mock = Mock()
    mock.query.return_value = {
        "ids": [ids or []],
        "documents": [docs or [""] * n],
        "metadatas": [metas or [{}] * n],
        "distances": [dists or [0.2] * n],
    }
    return mock


# ---------- QueryParser Tests ----------

class TestQueryParser:
    """Test natural language query parsing."""

    def test_career_domain_detected(self):
        """'career' keyword → domain=career."""
        parser = QueryParser()
        parsed = parser.parse("career highlights from Sprinklr")
        assert parsed.domain == "career"

    def test_job_keyword_maps_to_career(self):
        """'job' keyword → domain=career."""
        parser = QueryParser()
        parsed = parser.parse("my job achievements")
        assert parsed.domain == "career"

    def test_finance_domain_detected(self):
        """'salary', 'money', 'finance' → domain=finance."""
        parser = QueryParser()
        assert parser.parse("salary metrics").domain == "finance"
        assert parser.parse("money saved in 2023").domain == "finance"

    def test_health_domain_detected(self):
        """'workout', 'sleep', 'health' → domain=health."""
        parser = QueryParser()
        assert parser.parse("workout goals").domain == "health"
        assert parser.parse("sleep patterns").domain == "health"

    def test_relationships_domain_detected(self):
        """'relationship', 'friend', 'family' → domain=relationships."""
        parser = QueryParser()
        assert parser.parse("relationship advice").domain == "relationships"
        assert parser.parse("family decisions").domain == "relationships"

    def test_memory_domain_detected(self):
        """'memory', 'memories' → domain=memory."""
        parser = QueryParser()
        assert parser.parse("best memories from college").domain == "memory"

    def test_sprinklr_company_detected(self):
        """'sprinklr' → company=Sprinklr (capitalized)."""
        parser = QueryParser()
        parsed = parser.parse("ML projects at Sprinklr")
        assert parsed.company == "Sprinklr"

    def test_amex_alias_detected(self):
        """'amex' → company=American Express."""
        parser = QueryParser()
        parsed = parser.parse("amex risk scoring project")
        assert parsed.company == "American Express"

    def test_american_express_full_name_detected(self):
        """'american express' → company=American Express."""
        parser = QueryParser()
        parsed = parser.parse("American Express work highlights")
        assert parsed.company == "American Express"

    def test_metric_atom_type_detected(self):
        """'metrics', 'numbers', 'stat' → atom_type=metric."""
        parser = QueryParser()
        assert parser.parse("CSAT metrics").atom_type == "metric"
        assert parser.parse("revenue numbers").atom_type == "metric"

    def test_story_atom_type_detected(self):
        """'story', 'stories' → atom_type=story."""
        parser = QueryParser()
        assert parser.parse("leadership stories").atom_type == "story"

    def test_lesson_atom_type_detected(self):
        """'lesson', 'learned' → atom_type=lesson."""
        parser = QueryParser()
        assert parser.parse("what I learned from failures").atom_type == "lesson"

    def test_unknown_query_returns_none_filters(self):
        """Query with no known keywords → all filters None."""
        parser = QueryParser()
        parsed = parser.parse("xyz abc def")
        assert parsed.domain is None
        assert parsed.company is None
        assert parsed.atom_type is None

    def test_empty_query_parsed_safely(self):
        """Empty query parses without crash."""
        parser = QueryParser()
        parsed = parser.parse("")
        assert parsed.raw_query == ""
        assert parsed.domain is None

    def test_raw_query_preserved(self):
        """Raw query stored verbatim on parsed object."""
        parser = QueryParser()
        q = "Show me ML metrics at Sprinklr"
        parsed = parser.parse(q)
        assert parsed.raw_query == q


# ---------- ConfidenceLabel Tests ----------

class TestConfidenceLabel:
    """Test similarity → confidence label mapping."""

    def test_high_confidence(self):
        assert _confidence_label(0.8) == "high"
        assert _confidence_label(0.75) == "high"
        assert _confidence_label(1.0) == "high"

    def test_medium_confidence(self):
        assert _confidence_label(0.6) == "medium"
        assert _confidence_label(0.5) == "medium"

    def test_low_confidence(self):
        assert _confidence_label(0.4) == "low"
        assert _confidence_label(0.0) == "low"
        assert _confidence_label(0.49) == "low"


# ---------- SearchQueryInterface Tests ----------

class TestSearchQueryInterface:
    """Test high-level search interface."""

    def test_no_collection_returns_error(self):
        """No collection → search returns error, not crash."""
        searcher = SearchQueryInterface(collection=None)
        result = searcher.search("test query")
        assert result.search_error is not None
        assert result.total_found == 0

    def test_empty_query_returns_error(self):
        """Empty query → error message returned."""
        mock = _make_collection(ids=["d1"])
        searcher = SearchQueryInterface(collection=mock)
        result = searcher.search("")
        assert result.search_error is not None
        assert result.has_results is False

    def test_whitespace_query_returns_error(self):
        """Whitespace-only query → error."""
        mock = _make_collection(ids=["d1"])
        searcher = SearchQueryInterface(collection=mock)
        result = searcher.search("   ")
        assert result.search_error is not None

    def test_search_returns_query_result(self):
        """Valid search → QueryResult with correct query field."""
        mock = _make_collection(ids=["d1", "d2"], dists=[0.1, 0.3])
        searcher = SearchQueryInterface(collection=mock)
        result = searcher.search("career highlights")
        assert isinstance(result, QueryResult)
        assert result.query == "career highlights"

    def test_results_ranked_by_similarity(self):
        """Results must be ranked 1, 2, 3... by similarity descending."""
        mock = _make_collection(
            ids=["d1", "d2", "d3"],
            dists=[0.1, 0.3, 0.2],  # d1 closest
        )
        searcher = SearchQueryInterface(collection=mock)
        result = searcher.search("test")
        ranks = [r.rank for r in result.results]
        assert ranks == [1, 2, 3]
        # First result must have highest similarity
        assert result.results[0].similarity_score >= result.results[1].similarity_score

    def test_total_found_matches_results_count(self):
        """total_found must equal len(results)."""
        mock = _make_collection(ids=["d1", "d2", "d3"])
        searcher = SearchQueryInterface(collection=mock)
        result = searcher.search("test")
        assert result.total_found == len(result.results)

    def test_confidence_labels_assigned(self):
        """Each ranked result must have a confidence_label."""
        mock = _make_collection(ids=["d1"], dists=[0.1])  # similarity=0.9 → high
        searcher = SearchQueryInterface(collection=mock)
        result = searcher.search("career")
        assert result.results[0].confidence_label == "high"

    def test_explicit_domain_overrides_auto_detected(self):
        """Explicit domain= param takes priority over parsed domain."""
        mock = _make_collection(ids=["d1"])
        searcher = SearchQueryInterface(collection=mock)
        # Query says "work" (career) but explicit domain overrides to "health"
        result = searcher.search("work goals", domain="health")
        assert result.parsed.domain == "health"

    def test_explicit_company_overrides_auto_detected(self):
        """Explicit company= param takes priority."""
        mock = _make_collection(ids=["d1"])
        searcher = SearchQueryInterface(collection=mock)
        result = searcher.search("amex project", company="Google")
        assert result.parsed.company == "Google"

    def test_has_results_true_when_results(self):
        """has_results True when results list non-empty."""
        mock = _make_collection(ids=["d1"])
        searcher = SearchQueryInterface(collection=mock)
        result = searcher.search("test")
        assert result.has_results is True

    def test_has_results_false_when_empty(self):
        """has_results False when no results."""
        mock = _make_collection(ids=[])
        searcher = SearchQueryInterface(collection=mock)
        result = searcher.search("zzz_no_match")
        assert result.has_results is False


class TestSearchByExample:
    """Test search_by_example method."""

    def test_search_by_example_returns_similar(self):
        """search_by_example must return docs similar to input text."""
        mock = _make_collection(ids=["similar1", "similar2"], dists=[0.15, 0.25])
        searcher = SearchQueryInterface(collection=mock)
        result = searcher.search_by_example("My experience with chatbots at Sprinklr")
        assert result.total_found == 2

    def test_search_by_example_excludes_perfect_matches(self):
        """exclude_self=True must filter out near-identical docs (score >= 0.999)."""
        # Use distance=0.001 so similarity ≈ 0.999 → exactly at threshold
        mock = _make_collection(
            ids=["exact_match", "similar"],
            dists=[0.001, 0.25],  # 0.001 distance ≈ 0.999 similarity
        )
        searcher = SearchQueryInterface(collection=mock)
        result = searcher.search_by_example("example text", exclude_self=True)
        ids = [r.doc_id for r in result.results]
        assert "exact_match" not in ids

    def test_search_by_example_include_self(self):
        """exclude_self=False must include near-identical docs."""
        mock = _make_collection(ids=["exact"], dists=[0.0])
        searcher = SearchQueryInterface(collection=mock)
        result = searcher.search_by_example("text", exclude_self=False)
        assert any(r.doc_id == "exact" for r in result.results)


class TestMultiSearch:
    """Test multi_search method."""

    def test_multi_search_returns_one_result_per_query(self):
        """multi_search must return same number of QueryResults as queries."""
        mock = _make_collection(ids=["d1"])
        searcher = SearchQueryInterface(collection=mock)
        queries = ["career", "health", "finance"]
        results = searcher.multi_search(queries)
        assert len(results) == 3

    def test_multi_search_preserves_query_text(self):
        """Each result must reflect its original query."""
        mock = _make_collection(ids=["d1"])
        searcher = SearchQueryInterface(collection=mock)
        queries = ["career", "health"]
        results = searcher.multi_search(queries)
        assert results[0].query == "career"
        assert results[1].query == "health"

    def test_multi_search_empty_list(self):
        """Empty queries list → empty results list."""
        searcher = SearchQueryInterface(collection=None)
        results = searcher.multi_search([])
        assert results == []


# ---------- Vector Quality / MRR Tests ----------

class TestEvaluateQueries:
    """Test search quality evaluation metrics."""

    def _make_collection_with_known_doc(self, relevant_id: str, rank: int, total: int = 5):
        """
        Build a mock collection where `relevant_id` appears at a specific rank.
        rank is 1-based. Distances arranged so relevant_id is at given rank.
        """
        # Create ids: fill around the relevant_id position
        ids = [f"irrelevant_{i}" for i in range(total)]
        dists = [0.1 + i * 0.05 for i in range(total)]
        if rank <= total:
            ids[rank - 1] = relevant_id
            dists[rank - 1] = 0.1 + (rank - 1) * 0.05  # Consistent ordering
        # Sort so closest (smallest dist) comes first
        paired = sorted(zip(dists, ids))
        dists_sorted = [p[0] for p in paired]
        ids_sorted = [p[1] for p in paired]
        return _make_collection(ids=ids_sorted, dists=dists_sorted)

    def test_empty_queries_returns_zero_metrics(self):
        """Zero queries → all metrics 0.0."""
        searcher = SearchQueryInterface(collection=None)
        metrics = searcher.evaluate_queries([])
        assert metrics["precision_at_k"] == 0.0
        assert metrics["recall_at_k"] == 0.0
        assert metrics["mrr"] == 0.0
        assert metrics["total_queries"] == 0

    def test_perfect_recall_when_relevant_in_results(self):
        """Relevant doc in top-K → recall=1.0."""
        relevant_id = "leadership_doc"
        mock = self._make_collection_with_known_doc(relevant_id, rank=1, total=5)
        searcher = SearchQueryInterface(collection=mock)
        metrics = searcher.evaluate_queries([("leadership examples", relevant_id)], top_k=5)
        assert metrics["recall_at_k"] == 1.0

    def test_zero_recall_when_relevant_not_in_results(self):
        """Relevant doc not in results → recall=0.0."""
        mock = _make_collection(ids=["d1", "d2", "d3"])
        searcher = SearchQueryInterface(collection=mock)
        metrics = searcher.evaluate_queries([("some query", "missing_doc_id")], top_k=5)
        assert metrics["recall_at_k"] == 0.0

    def test_mrr_rank1_is_1(self):
        """Relevant doc at rank 1 → MRR = 1.0."""
        relevant_id = "top_doc"
        mock = self._make_collection_with_known_doc(relevant_id, rank=1, total=3)
        searcher = SearchQueryInterface(collection=mock)
        metrics = searcher.evaluate_queries([("test query", relevant_id)], top_k=5)
        assert abs(metrics["mrr"] - 1.0) < 0.01

    def test_mrr_rank2_is_half(self):
        """Relevant doc at rank 2 → MRR = 0.5."""
        relevant_id = "second_doc"
        mock = self._make_collection_with_known_doc(relevant_id, rank=2, total=3)
        searcher = SearchQueryInterface(collection=mock)
        metrics = searcher.evaluate_queries([("test query", relevant_id)], top_k=5)
        assert abs(metrics["mrr"] - 0.5) < 0.01

    def test_mrr_averaged_over_multiple_queries(self):
        """MRR is mean over all queries."""
        # Query 1: relevant at rank 1 → RR = 1.0
        # Query 2: relevant not found → RR = 0.0
        # Expected MRR = (1.0 + 0.0) / 2 = 0.5
        mock1 = _make_collection(ids=["relevant_a", "d2"], dists=[0.1, 0.3])
        mock2 = _make_collection(ids=["irrelevant_1", "irrelevant_2"], dists=[0.1, 0.3])

        # Use separate searcher instances for isolation
        s1 = SearchQueryInterface(collection=mock1)
        s2 = SearchQueryInterface(collection=mock2)

        r1 = s1.evaluate_queries([("query1", "relevant_a")], top_k=5)
        r2 = s2.evaluate_queries([("query2", "relevant_b")], top_k=5)

        avg_mrr = (r1["mrr"] + r2["mrr"]) / 2
        assert abs(avg_mrr - 0.5) < 0.01

    def test_total_queries_in_metrics(self):
        """total_queries field must match input count."""
        mock = _make_collection(ids=["d1"])
        searcher = SearchQueryInterface(collection=mock)
        pairs = [("q1", "d1"), ("q2", "d2"), ("q3", "d3")]
        metrics = searcher.evaluate_queries(pairs, top_k=5)
        assert metrics["total_queries"] == 3


# ---------- QueryResult Formatting ----------

class TestQueryResultFormatting:
    """Test format_text() and to_dict() output."""

    def test_format_text_includes_query(self):
        """format_text must include the original query."""
        mock = _make_collection(ids=["d1"], dists=[0.1])
        searcher = SearchQueryInterface(collection=mock)
        result = searcher.search("leadership stories")
        text = result.format_text()
        assert "leadership stories" in text

    def test_format_text_no_results_message(self):
        """No results → format_text says 'No matching documents found'."""
        mock = _make_collection(ids=[])
        searcher = SearchQueryInterface(collection=mock)
        result = searcher.search("zzz_nothing")
        text = result.format_text()
        assert "No matching documents found" in text

    def test_to_dict_has_required_fields(self):
        """to_dict must have query, filters, total_found, results, error."""
        mock = _make_collection(ids=["d1"])
        searcher = SearchQueryInterface(collection=mock)
        result = searcher.search("test")
        d = result.to_dict()
        assert "query" in d
        assert "filters" in d
        assert "total_found" in d
        assert "results" in d
        assert "error" in d

    def test_ranked_result_to_dict_truncates_long_content(self):
        """RankedResult.to_dict() must truncate content > 300 chars."""
        rr = RankedResult(
            rank=1, doc_id="d1",
            content="x" * 500,
            similarity_score=0.8,
            confidence_label="high",
            metadata={},
        )
        d = rr.to_dict()
        assert len(d["content"]) <= 305  # 300 + "..."

    def test_format_text_shows_confidence_label(self):
        """format_text output must include HIGH/MEDIUM/LOW label."""
        mock = _make_collection(ids=["d1"], dists=[0.1])  # similarity=0.9 → HIGH
        searcher = SearchQueryInterface(collection=mock)
        result = searcher.search("test")
        text = result.format_text()
        assert "HIGH" in text
