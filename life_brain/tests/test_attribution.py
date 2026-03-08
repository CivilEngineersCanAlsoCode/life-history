"""
Tests for attribution formatting with source citations.

Tests cover:
- Citation creation from search results
- Similarity and confidence percentage accuracy
- Source label generation
- Inline citation formatting
- Footnote citation formatting
- Attribution block formatting
- Minimum similarity filtering
- Export to dict
- Edge cases
"""

import pytest

from life_brain.search.semantic_search import SearchResult
from life_brain.search.attribution import (
    AttributionFormatter,
    Citation,
    compute_confidence,
    build_source_label,
)


def _make_result(doc_id="doc1", similarity=0.85, metadata=None, distance=None):
    """Helper to create SearchResult."""
    if metadata is None:
        metadata = {"company": "Google", "domain": "career"}
    if distance is None:
        distance = 1 - similarity
    return SearchResult(
        doc_id=doc_id,
        content="Test content",
        similarity_score=similarity,
        metadata=metadata,
        distance=distance,
    )


class TestComputeConfidence:
    """Test confidence score computation."""

    def test_base_confidence_from_similarity(self):
        """Confidence should be at least the similarity score."""
        conf = compute_confidence(0.8, {})
        assert conf >= 0.8

    def test_metadata_completeness_bonus(self):
        """More metadata fields should increase confidence."""
        bare = compute_confidence(0.8, {})
        rich = compute_confidence(0.8, {
            "company": "Google",
            "domain": "career",
            "project": "CRR",
            "category": "interview",
            "type": "star_story",
        })
        assert rich > bare

    def test_confidence_clamped_to_one(self):
        """Confidence should not exceed 1.0."""
        conf = compute_confidence(0.99, {
            "company": "X", "domain": "Y", "project": "Z",
            "category": "A", "type": "B",
        })
        assert conf <= 1.0

    def test_confidence_never_negative(self):
        """Confidence should never be negative."""
        conf = compute_confidence(0.0, {})
        assert conf >= 0.0

    def test_partial_metadata_bonus(self):
        """Partial metadata should give partial bonus."""
        partial = compute_confidence(0.5, {"company": "Google"})
        full = compute_confidence(0.5, {
            "company": "Google", "domain": "career", "project": "CRR",
            "category": "interview", "type": "qa",
        })
        assert full > partial


class TestBuildSourceLabel:
    """Test source label generation."""

    def test_label_with_company_and_project(self):
        """Label should include company and project."""
        label = build_source_label("doc1", {"company": "Google", "project": "CRR"})
        assert "Google" in label
        assert "CRR" in label
        assert "doc1" in label

    def test_label_with_company_only(self):
        """Label should include company when no project."""
        label = build_source_label("doc1", {"company": "Google"})
        assert "Google" in label
        assert "doc1" in label

    def test_label_with_no_metadata(self):
        """Label should fall back to doc_id."""
        label = build_source_label("doc1", {})
        assert label == "doc1"

    def test_label_with_project_only(self):
        """Label with only project."""
        label = build_source_label("doc1", {"project": "CRR"})
        assert "CRR" in label
        assert "doc1" in label


class TestCitation:
    """Test Citation dataclass."""

    def test_format_inline(self):
        """Inline citation format."""
        citation = Citation(
            doc_id="doc1",
            similarity_pct=85.0,
            confidence_pct=90.0,
            source_label="Google / CRR (doc1)",
            metadata={"company": "Google"},
        )

        inline = citation.format_inline()
        assert "85%" in inline
        assert "90%" in inline
        assert "Google / CRR (doc1)" in inline
        assert "match" in inline
        assert "confidence" in inline

    def test_format_footnote(self):
        """Footnote citation format."""
        citation = Citation(
            doc_id="doc1",
            similarity_pct=75.0,
            confidence_pct=80.0,
            source_label="Amazon (doc1)",
            metadata={},
        )

        footnote = citation.format_footnote(1)
        assert footnote.startswith("[1]")
        assert "75%" in footnote
        assert "80%" in footnote

    def test_to_dict(self):
        """Citation dict export."""
        citation = Citation(
            doc_id="doc1",
            similarity_pct=85.3456,
            confidence_pct=90.1234,
            source_label="Test",
            metadata={"key": "value"},
        )

        d = citation.to_dict()
        assert d["doc_id"] == "doc1"
        assert d["similarity_pct"] == 85.3
        assert d["confidence_pct"] == 90.1
        assert d["source_label"] == "Test"


class TestAttributionFormatter:
    """Test AttributionFormatter."""

    def test_create_citation_from_result(self):
        """Create citation from search result."""
        result = _make_result(similarity=0.85, metadata={"company": "Google", "domain": "career"})
        formatter = AttributionFormatter()

        citation = formatter.create_citation(result)

        assert citation.doc_id == "doc1"
        assert citation.similarity_pct == 85.0
        assert citation.confidence_pct > 85.0  # Has metadata bonus
        assert "Google" in citation.source_label

    def test_create_citations_sorted(self):
        """Citations should be sorted by similarity descending."""
        results = [
            _make_result("low", similarity=0.3),
            _make_result("high", similarity=0.9),
            _make_result("mid", similarity=0.6),
        ]
        formatter = AttributionFormatter()

        citations = formatter.create_citations(results)

        assert len(citations) == 3
        assert citations[0].doc_id == "high"
        assert citations[1].doc_id == "mid"
        assert citations[2].doc_id == "low"

    def test_min_similarity_filter(self):
        """Results below min similarity should be filtered out."""
        results = [
            _make_result("high", similarity=0.9),
            _make_result("low", similarity=0.2),
        ]
        formatter = AttributionFormatter(min_similarity_pct=50.0)

        citations = formatter.create_citations(results)

        assert len(citations) == 1
        assert citations[0].doc_id == "high"

    def test_format_inline_citations(self):
        """Inline citations string."""
        results = [_make_result("doc1", similarity=0.85)]
        formatter = AttributionFormatter()

        inline = formatter.format_inline_citations(results)

        assert "85%" in inline
        assert "match" in inline
        assert "confidence" in inline

    def test_format_footnotes(self):
        """Footnote citations."""
        results = [
            _make_result("doc1", similarity=0.9),
            _make_result("doc2", similarity=0.7),
        ]
        formatter = AttributionFormatter()

        footnotes = formatter.format_footnotes(results)

        assert "[1]" in footnotes
        assert "[2]" in footnotes
        assert "90%" in footnotes
        assert "70%" in footnotes

    def test_format_attribution_block(self):
        """Full attribution block."""
        results = [
            _make_result("doc1", similarity=0.85, metadata={"company": "Google"}),
        ]
        formatter = AttributionFormatter()

        block = formatter.format_attribution_block(results)

        assert "Sources:" in block
        assert "[1]" in block
        assert "85%" in block

    def test_attribution_block_empty(self):
        """Empty results should show 'No sources found'."""
        formatter = AttributionFormatter()
        block = formatter.format_attribution_block([])
        assert block == "No sources found."

    def test_export_citations(self):
        """Export citations as dicts."""
        results = [_make_result("doc1", similarity=0.85)]
        formatter = AttributionFormatter()

        exported = formatter.export_citations(results)

        assert len(exported) == 1
        assert exported[0]["doc_id"] == "doc1"
        assert "similarity_pct" in exported[0]
        assert "confidence_pct" in exported[0]

    def test_multiple_results_inline(self):
        """Multiple results should produce space-separated inline citations."""
        results = [
            _make_result("d1", similarity=0.9),
            _make_result("d2", similarity=0.8),
            _make_result("d3", similarity=0.7),
        ]
        formatter = AttributionFormatter()

        inline = formatter.format_inline_citations(results)

        # Should contain 3 citations
        assert inline.count("[") == 3
        assert inline.count("]") == 3

    def test_footnotes_newline_separated(self):
        """Footnotes should be separated by newlines."""
        results = [
            _make_result("d1", similarity=0.9),
            _make_result("d2", similarity=0.7),
        ]
        formatter = AttributionFormatter()

        footnotes = formatter.format_footnotes(results)

        lines = footnotes.strip().split("\n")
        assert len(lines) == 2

    def test_empty_inline_citations(self):
        """Empty results should return empty string."""
        formatter = AttributionFormatter()
        assert formatter.format_inline_citations([]) == ""

    def test_empty_footnotes(self):
        """Empty results should return empty string."""
        formatter = AttributionFormatter()
        assert formatter.format_footnotes([]) == ""

    def test_min_filter_removes_all(self):
        """When all results below threshold, return empty."""
        results = [_make_result("d1", similarity=0.1)]
        formatter = AttributionFormatter(min_similarity_pct=50.0)

        assert formatter.format_inline_citations(results) == ""
        assert formatter.format_footnotes(results) == ""
        assert formatter.format_attribution_block(results) == "No sources found."
