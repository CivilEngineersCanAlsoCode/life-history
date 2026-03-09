"""
Search & Query Interface — High-level search over the Life Brain vector database.

Supports natural language queries like:
- "Projects involving ML at Sprinklr"
- "Leadership examples in first 6 months"
- "All salary metrics across companies"
- "Health goals from last year"

Parses query modifiers, applies metadata filters, ranks results,
and returns formatted output with confidence scores and source metadata.
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from life_brain.search.semantic_search import SearchResult, SemanticSearch

logger = logging.getLogger(__name__)


# Known domain keywords → domain label
_DOMAIN_KEYWORDS: Dict[str, str] = {
    "career": "career", "job": "career", "work": "career", "sprinklr": "career",
    "amex": "career", "american express": "career",
    "finance": "finance", "money": "finance", "salary": "finance",
    "investment": "finance", "savings": "finance", "spend": "finance",
    "health": "health", "workout": "health", "sleep": "health",
    "wellness": "health", "mental": "health",
    "relationship": "relationships", "relationships": "relationships",
    "friend": "relationships", "family": "relationships",
    "memory": "memory", "memories": "memory", "remember": "memory",
    "goal": "personal_growth", "habit": "personal_growth",
    "learning": "personal_growth", "growth": "personal_growth",
    "belief": "personal_growth",
}

# Known company aliases
_COMPANY_ALIASES: Dict[str, str] = {
    "sprinklr": "Sprinklr",
    "amex": "American Express",
    "american express": "American Express",
    "google": "Google",
    "amazon": "Amazon",
    "meta": "Meta",
    "facebook": "Facebook",
}

# Atom type keywords
_ATOM_TYPE_KEYWORDS: Dict[str, str] = {
    "metric": "metric", "metrics": "metric", "number": "metric",
    "numbers": "metric", "stat": "metric", "statistics": "metric",
    "story": "story", "stories": "story", "star": "story",
    "fact": "fact", "facts": "fact",
    "decision": "decision", "decisions": "decision",
    "lesson": "lesson", "lessons": "lesson", "learned": "lesson",
    "goal": "goal", "goals": "goal",
    "belief": "belief", "beliefs": "belief",
}


@dataclass
class ParsedQuery:
    """A natural language query parsed into structured filters."""
    raw_query: str
    clean_query: str            # Query text after removing filter modifiers
    domain: Optional[str] = None
    company: Optional[str] = None
    project: Optional[str] = None
    atom_type: Optional[str] = None
    top_k: int = 5


@dataclass
class RankedResult:
    """A search result with ranking metadata."""
    rank: int
    doc_id: str
    content: str
    similarity_score: float
    confidence_label: str       # "high" / "medium" / "low"
    metadata: Dict[str, Any]
    found_by: str = "semantic"  # "semantic" or "structural"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rank": self.rank,
            "doc_id": self.doc_id,
            "content": self.content[:300] + ("..." if len(self.content) > 300 else ""),
            "similarity_score": round(self.similarity_score, 3),
            "confidence_label": self.confidence_label,
            "metadata": self.metadata,
            "found_by": self.found_by,
        }


@dataclass
class QueryResult:
    """Full result from a search query."""
    query: str
    parsed: ParsedQuery
    results: List[RankedResult]
    total_found: int
    search_error: Optional[str] = None

    @property
    def has_results(self) -> bool:
        return len(self.results) > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "filters": {
                "domain": self.parsed.domain,
                "company": self.parsed.company,
                "atom_type": self.parsed.atom_type,
            },
            "total_found": self.total_found,
            "results": [r.to_dict() for r in self.results],
            "error": self.search_error,
        }

    def format_text(self) -> str:
        """Format results as readable text output."""
        lines = [f'Search: "{self.query}"']
        if self.parsed.domain or self.parsed.company:
            filters = []
            if self.parsed.domain:
                filters.append(f"domain={self.parsed.domain}")
            if self.parsed.company:
                filters.append(f"company={self.parsed.company}")
            lines.append(f"Filters: {', '.join(filters)}")
        lines.append(f"Found: {self.total_found} results\n")

        if self.search_error:
            lines.append(f"Error: {self.search_error}")
            return "\n".join(lines)

        if not self.results:
            lines.append("No matching documents found.")
            return "\n".join(lines)

        for r in self.results:
            lines.append(f"[{r.rank}] {r.confidence_label.upper()} ({r.similarity_score:.2f})")
            meta_parts = []
            if r.metadata.get("company"):
                meta_parts.append(r.metadata["company"])
            if r.metadata.get("atom_type"):
                meta_parts.append(r.metadata["atom_type"])
            if r.metadata.get("date"):
                meta_parts.append(r.metadata["date"])
            if meta_parts:
                lines.append(f"    [{' | '.join(meta_parts)}]")
            snippet = r.content[:200].replace("\n", " ")
            if len(r.content) > 200:
                snippet += "..."
            lines.append(f"    {snippet}")
            lines.append("")

        return "\n".join(lines).strip()


def _confidence_label(score: float) -> str:
    """Map similarity score to confidence label."""
    if score >= 0.75:
        return "high"
    elif score >= 0.5:
        return "medium"
    return "low"


class QueryParser:
    """Parse natural language search queries into structured filters."""

    def parse(self, raw_query: str, top_k: int = 5) -> ParsedQuery:
        """
        Parse a natural language query.

        Examples:
            "ML projects at Sprinklr" → domain=career, company=Sprinklr
            "leadership examples" → domain=career (inferred)
            "health goals last year" → domain=health, atom_type=goal
            "salary metrics at Amex" → domain=finance, company=American Express, atom_type=metric

        Args:
            raw_query: Natural language query string
            top_k: Number of results to return

        Returns:
            ParsedQuery with extracted filters
        """
        query_lower = raw_query.lower()
        clean = raw_query.strip()

        domain = self._extract_domain(query_lower)
        company = self._extract_company(query_lower)
        atom_type = self._extract_atom_type(query_lower)

        return ParsedQuery(
            raw_query=raw_query,
            clean_query=clean,
            domain=domain,
            company=company,
            atom_type=atom_type,
            top_k=top_k,
        )

    def _extract_domain(self, query_lower: str) -> Optional[str]:
        """Extract domain from query keywords."""
        # Check multi-word matches first
        for keyword, domain in sorted(_DOMAIN_KEYWORDS.items(), key=lambda x: -len(x[0])):
            if keyword in query_lower:
                return domain
        return None

    def _extract_company(self, query_lower: str) -> Optional[str]:
        """Extract company from query keywords."""
        for alias, canonical in sorted(_COMPANY_ALIASES.items(), key=lambda x: -len(x[0])):
            if alias in query_lower:
                return canonical
        return None

    def _extract_atom_type(self, query_lower: str) -> Optional[str]:
        """Extract atom type hint from query keywords."""
        for keyword, atype in sorted(_ATOM_TYPE_KEYWORDS.items(), key=lambda x: -len(x[0])):
            if keyword in query_lower:
                return atype
        return None


class SearchQueryInterface:
    """
    High-level search interface for the Life Brain database.

    Usage:
        searcher = SearchQueryInterface(collection=chroma_collection)

        # Natural language query
        result = searcher.search("ML projects at Sprinklr")
        print(result.format_text())

        # Explicit filters
        result = searcher.search(
            "leadership examples",
            domain="career",
            company="Sprinklr",
            top_k=10,
        )

        # Multi-query search (MRR evaluation)
        metrics = searcher.evaluate_queries([
            ("ML projects", "sprinklr_ml_doc_id"),
            ("leadership", "leadership_doc_id"),
        ])
    """

    def __init__(self, collection=None):
        self.collection = collection
        self._semantic = SemanticSearch(collection=collection)
        self._parser = QueryParser()

    def search(
        self,
        query: str,
        domain: Optional[str] = None,
        company: Optional[str] = None,
        project: Optional[str] = None,
        atom_type: Optional[str] = None,
        top_k: int = 5,
        parse_filters: bool = True,
    ) -> QueryResult:
        """
        Search the Life Brain database.

        Args:
            query: Natural language search query
            domain: Override domain filter (auto-detected if None)
            company: Override company filter (auto-detected if None)
            project: Override project filter
            atom_type: Override atom_type filter (auto-detected if None)
            top_k: Number of results
            parse_filters: Whether to auto-extract filters from query text

        Returns:
            QueryResult with ranked results and metadata
        """
        if not query or not query.strip():
            parsed = ParsedQuery(raw_query=query, clean_query=query, top_k=top_k)
            return QueryResult(
                query=query, parsed=parsed, results=[], total_found=0,
                search_error="Query cannot be empty",
            )

        # Parse query for auto-detected filters
        parsed = self._parser.parse(query, top_k=top_k)

        # Explicit overrides take priority over auto-detected
        effective_domain = domain or parsed.domain
        effective_company = company or parsed.company
        effective_project = project or parsed.project
        # atom_type used for context, not directly passed to SemanticSearch
        # (SemanticSearch filters by domain/company/project)

        # Update parsed with effective values
        parsed.domain = effective_domain
        parsed.company = effective_company
        parsed.project = effective_project
        parsed.atom_type = atom_type or parsed.atom_type

        # Execute search
        raw_results, error = self._semantic.search(
            query=query,
            domain=effective_domain,
            company=effective_company,
            project=effective_project,
            top_k=top_k,
        )

        # Rank and label results
        ranked = self._rank_results(raw_results)

        return QueryResult(
            query=query,
            parsed=parsed,
            results=ranked,
            total_found=len(ranked),
            search_error=error,
        )

    def search_by_example(
        self,
        example_text: str,
        top_k: int = 5,
        exclude_self: bool = True,
    ) -> QueryResult:
        """
        Find documents similar to a given piece of text.
        Useful for finding related experiences or potential conflicts.

        Args:
            example_text: Text to find similar documents for
            top_k: Number of similar results
            exclude_self: Skip exact matches (same text)

        Returns:
            QueryResult with similar documents
        """
        parsed = ParsedQuery(
            raw_query=example_text[:100],
            clean_query=example_text,
            top_k=top_k,
        )

        raw_results, error = self._semantic.search(query=example_text, top_k=top_k + 1)

        # Optionally filter near-identical matches
        if exclude_self:
            raw_results = [r for r in raw_results if r.similarity_score < 0.999]

        ranked = self._rank_results(raw_results[:top_k])
        return QueryResult(
            query=example_text[:100],
            parsed=parsed,
            results=ranked,
            total_found=len(ranked),
            search_error=error,
        )

    def multi_search(
        self,
        queries: List[str],
        top_k: int = 5,
    ) -> List[QueryResult]:
        """
        Execute multiple queries, return results for each.

        Args:
            queries: List of query strings
            top_k: Results per query

        Returns:
            List of QueryResult, one per input query
        """
        return [self.search(q, top_k=top_k) for q in queries]

    def evaluate_queries(
        self,
        query_relevant_pairs: List[Tuple[str, str]],
        top_k: int = 10,
    ) -> Dict[str, Any]:
        """
        Evaluate search quality using known relevant document IDs.

        Metrics computed:
        - Precision@K: fraction of returned docs that are relevant
        - Recall@K: fraction of relevant docs found in top-K
        - MRR: Mean Reciprocal Rank (rank of first relevant doc)

        Args:
            query_relevant_pairs: List of (query, relevant_doc_id) pairs
            top_k: Results per query

        Returns:
            Dict with precision, recall, mrr metrics
        """
        total_queries = len(query_relevant_pairs)
        if total_queries == 0:
            return {"precision_at_k": 0.0, "recall_at_k": 0.0, "mrr": 0.0, "total_queries": 0}

        precision_sum = 0.0
        recall_sum = 0.0
        reciprocal_rank_sum = 0.0

        for query, relevant_doc_id in query_relevant_pairs:
            result = self.search(query, top_k=top_k)
            returned_ids = [r.doc_id for r in result.results]

            # Precision@K: is the relevant doc in results?
            hits = sum(1 for doc_id in returned_ids if doc_id == relevant_doc_id)
            precision = hits / len(returned_ids) if returned_ids else 0.0
            precision_sum += precision

            # Recall@K: same as precision here (single relevant doc)
            recall_sum += 1.0 if relevant_doc_id in returned_ids else 0.0

            # MRR: reciprocal of rank where relevant doc appears
            rr = 0.0
            for rank, doc_id in enumerate(returned_ids, start=1):
                if doc_id == relevant_doc_id:
                    rr = 1.0 / rank
                    break
            reciprocal_rank_sum += rr

        return {
            "total_queries": total_queries,
            "precision_at_k": round(precision_sum / total_queries, 4),
            "recall_at_k": round(recall_sum / total_queries, 4),
            "mrr": round(reciprocal_rank_sum / total_queries, 4),
        }

    def _rank_results(self, raw_results: List[SearchResult]) -> List[RankedResult]:
        """Convert raw SearchResults to ranked RankedResults."""
        # Sort by similarity descending (already sorted by ChromaDB, but be safe)
        sorted_results = sorted(raw_results, key=lambda r: r.similarity_score, reverse=True)
        ranked = []
        for i, r in enumerate(sorted_results, start=1):
            ranked.append(RankedResult(
                rank=i,
                doc_id=r.doc_id,
                content=r.content,
                similarity_score=r.similarity_score,
                confidence_label=_confidence_label(r.similarity_score),
                metadata=r.metadata,
            ))
        return ranked
