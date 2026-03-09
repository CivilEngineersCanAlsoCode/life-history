"""
Attribution formatting for search results with source citations.

Provides formatted citations for search results including:
- Document ID references
- Similarity percentage
- Confidence scoring
- Formatted citation strings for display
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from life_brain.retrieval.semantic_search import SearchResult


@dataclass
class Citation:
    """A formatted source citation."""

    doc_id: str
    similarity_pct: float  # 0-100
    confidence_pct: float  # 0-100
    source_label: str  # Human-readable source label
    metadata: Dict[str, Any]

    def format_inline(self) -> str:
        """Format as inline citation: [doc_id | 85% match | 90% confidence]."""
        return (
            f"[{self.source_label} | "
            f"{self.similarity_pct:.0f}% match | "
            f"{self.confidence_pct:.0f}% confidence]"
        )

    def format_footnote(self, index: int) -> str:
        """Format as footnote citation: [1] doc_id (85% match, 90% confidence)."""
        return (
            f"[{index}] {self.source_label} "
            f"({self.similarity_pct:.0f}% match, "
            f"{self.confidence_pct:.0f}% confidence)"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "doc_id": self.doc_id,
            "similarity_pct": round(self.similarity_pct, 1),
            "confidence_pct": round(self.confidence_pct, 1),
            "source_label": self.source_label,
            "metadata": self.metadata,
        }


def compute_confidence(
    similarity_score: float,
    metadata: Dict[str, Any],
) -> float:
    """Compute confidence score for a search result.

    Confidence is based on similarity plus metadata completeness.
    More metadata fields = higher confidence that the result is well-attributed.

    Args:
        similarity_score: Raw similarity score (0-1)
        metadata: Result metadata

    Returns:
        Confidence score (0-1)
    """
    # Base confidence from similarity
    base = similarity_score

    # Metadata completeness bonus (up to 0.1)
    key_fields = ["company", "domain", "project", "category", "type"]
    filled = sum(1 for f in key_fields if metadata.get(f))
    completeness_bonus = (filled / len(key_fields)) * 0.1

    confidence = min(1.0, base + completeness_bonus)
    return max(0.0, confidence)


def build_source_label(doc_id: str, metadata: Dict[str, Any]) -> str:
    """Build a human-readable source label from doc_id and metadata.

    Args:
        doc_id: Document identifier
        metadata: Document metadata

    Returns:
        Human-readable label
    """
    parts = []

    company = metadata.get("company")
    if company:
        parts.append(company)

    project = metadata.get("project")
    if project:
        parts.append(project)

    if not parts:
        return doc_id

    return f"{' / '.join(parts)} ({doc_id})"


class AttributionFormatter:
    """Format search results with source citations."""

    def __init__(self, min_similarity_pct: float = 0.0):
        """Initialize formatter.

        Args:
            min_similarity_pct: Minimum similarity % to include in citations (0-100)
        """
        self.min_similarity_pct = min_similarity_pct

    def create_citation(self, result: SearchResult) -> Citation:
        """Create a citation from a search result.

        Args:
            result: SearchResult to cite

        Returns:
            Citation object
        """
        similarity_pct = result.similarity_score * 100
        confidence = compute_confidence(result.similarity_score, result.metadata)
        confidence_pct = confidence * 100
        source_label = build_source_label(result.doc_id, result.metadata)

        return Citation(
            doc_id=result.doc_id,
            similarity_pct=similarity_pct,
            confidence_pct=confidence_pct,
            source_label=source_label,
            metadata=result.metadata,
        )

    def create_citations(
        self, results: List[SearchResult]
    ) -> List[Citation]:
        """Create citations from search results, filtering by minimum similarity.

        Args:
            results: List of SearchResult objects

        Returns:
            List of Citation objects (filtered and sorted by similarity)
        """
        citations = []
        for result in results:
            citation = self.create_citation(result)
            if citation.similarity_pct >= self.min_similarity_pct:
                citations.append(citation)

        # Sort by similarity descending
        citations.sort(key=lambda c: c.similarity_pct, reverse=True)
        return citations

    def format_inline_citations(self, results: List[SearchResult]) -> str:
        """Format results as inline citation string.

        Args:
            results: Search results

        Returns:
            Inline citations string
        """
        citations = self.create_citations(results)
        if not citations:
            return ""
        return " ".join(c.format_inline() for c in citations)

    def format_footnotes(self, results: List[SearchResult]) -> str:
        """Format results as footnote citations.

        Args:
            results: Search results

        Returns:
            Footnote citations string (one per line)
        """
        citations = self.create_citations(results)
        if not citations:
            return ""
        lines = [c.format_footnote(i + 1) for i, c in enumerate(citations)]
        return "\n".join(lines)

    def format_attribution_block(self, results: List[SearchResult]) -> str:
        """Format a complete attribution block with header and citations.

        Args:
            results: Search results

        Returns:
            Formatted attribution block
        """
        citations = self.create_citations(results)
        if not citations:
            return "No sources found."

        lines = ["Sources:"]
        for i, citation in enumerate(citations):
            lines.append(f"  {citation.format_footnote(i + 1)}")

        return "\n".join(lines)

    def export_citations(self, results: List[SearchResult]) -> List[Dict[str, Any]]:
        """Export citations as list of dicts.

        Args:
            results: Search results

        Returns:
            List of citation dictionaries
        """
        citations = self.create_citations(results)
        return [c.to_dict() for c in citations]
