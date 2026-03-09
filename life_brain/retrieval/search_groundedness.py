"""
Groundedness scoring for search results.

Scores how well-grounded a search result is based on:
- Similarity score (semantic relevance)
- Metadata completeness (attribution quality)
- Source reliability indicators
- Content length and specificity
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from life_brain.retrieval.semantic_search import SearchResult


@dataclass
class GroundedResult:
    """Search result with groundedness scoring."""

    result: SearchResult
    groundedness_score: float  # 0-1 combined score
    similarity_weight: float  # Contribution from similarity
    metadata_weight: float  # Contribution from metadata
    content_weight: float  # Contribution from content quality

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            **self.result.to_dict(),
            "groundedness_score": round(self.groundedness_score, 3),
            "score_breakdown": {
                "similarity": round(self.similarity_weight, 3),
                "metadata": round(self.metadata_weight, 3),
                "content": round(self.content_weight, 3),
            },
        }


class GroundednessScorer:
    """Score and rank search results by groundedness."""

    # Default weights for each scoring component
    DEFAULT_WEIGHTS = {
        "similarity": 0.6,
        "metadata": 0.25,
        "content": 0.15,
    }

    # Key metadata fields that indicate well-grounded results
    KEY_METADATA_FIELDS = ["company", "domain", "project", "category", "type", "date", "source"]

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """Initialize scorer.

        Args:
            weights: Custom weights for scoring components.
                     Keys: "similarity", "metadata", "content"
                     Values should sum to 1.0
        """
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()

    def score_result(self, result: SearchResult) -> GroundedResult:
        """Score a single search result for groundedness.

        Args:
            result: SearchResult to score

        Returns:
            GroundedResult with groundedness score
        """
        sim_score = self._score_similarity(result.similarity_score)
        meta_score = self._score_metadata(result.metadata)
        content_score = self._score_content(result.content)

        sim_weighted = sim_score * self.weights["similarity"]
        meta_weighted = meta_score * self.weights["metadata"]
        content_weighted = content_score * self.weights["content"]

        groundedness = sim_weighted + meta_weighted + content_weighted
        groundedness = max(0.0, min(1.0, groundedness))

        return GroundedResult(
            result=result,
            groundedness_score=groundedness,
            similarity_weight=sim_weighted,
            metadata_weight=meta_weighted,
            content_weight=content_weighted,
        )

    def score_and_rank(self, results: List[SearchResult]) -> List[GroundedResult]:
        """Score and rank results by groundedness.

        Args:
            results: List of SearchResult objects

        Returns:
            List of GroundedResult sorted by groundedness (highest first)
        """
        grounded = [self.score_result(r) for r in results]
        grounded.sort(key=lambda g: g.groundedness_score, reverse=True)
        return grounded

    def _score_similarity(self, similarity: float) -> float:
        """Score based on semantic similarity.

        Args:
            similarity: Raw similarity score (0-1)

        Returns:
            Similarity component score (0-1)
        """
        return max(0.0, min(1.0, similarity))

    def _score_metadata(self, metadata: Dict[str, Any]) -> float:
        """Score based on metadata completeness.

        Args:
            metadata: Result metadata

        Returns:
            Metadata component score (0-1)
        """
        if not metadata:
            return 0.0

        filled = sum(1 for f in self.KEY_METADATA_FIELDS if metadata.get(f))
        return filled / len(self.KEY_METADATA_FIELDS)

    def _score_content(self, content: str) -> float:
        """Score based on content quality indicators.

        Args:
            content: Result content text

        Returns:
            Content component score (0-1)
        """
        if not content:
            return 0.0

        # Length score: longer content generally more informative
        # Diminishing returns after 500 chars
        length = len(content)
        length_score = min(1.0, length / 500)

        # Specificity: presence of numbers, proper nouns etc.
        specificity = 0.0
        if any(c.isdigit() for c in content):
            specificity += 0.3
        if any(c.isupper() for c in content[1:] if c.isalpha()):
            specificity += 0.3
        if len(content.split()) > 10:
            specificity += 0.4

        specificity = min(1.0, specificity)

        return (length_score * 0.5) + (specificity * 0.5)
