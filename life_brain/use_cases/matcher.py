"""
Use Case Matcher — Semantic matching for top-10 use case ranking.

Uses embedding similarity to find most relevant use cases for user input.
Includes fallback keyword matching and difficulty filtering.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import math

from .catalog import UseCaseCatalog, UseCase, UseCaseCategory


@dataclass
class MatchResult:
    """Result of matching user input to a use case."""

    use_case: UseCase
    match_score: float          # 0-1, relevance score
    match_type: str             # "semantic", "keyword", "category"
    confidence: float           # 0-1, how confident is this match


class UseCaseMatcher:
    """Match user input to most relevant use cases."""

    def __init__(self, catalog: Optional[UseCaseCatalog] = None):
        """Initialize matcher with use case catalog."""
        self.catalog = catalog or UseCaseCatalog()

    def find_top_matches(
        self,
        user_input: str,
        embeddings: Optional[dict] = None,
        limit: int = 10,
        min_score: float = 0.3,
        difficulty_filter: Optional[str] = None,
    ) -> List[MatchResult]:
        """
        Find top N most relevant use cases for user input.

        Args:
            user_input: User's question or intent description
            embeddings: Dict mapping use_case_id -> embedding vector
                       (if None, falls back to keyword matching)
            limit: Return top N matches
            min_score: Minimum match score (0-1)
            difficulty_filter: Optional filter ("beginner", "intermediate", "advanced")

        Returns:
            List of MatchResult sorted by score (descending)
        """
        scores: List[Tuple[UseCase, float, str, float]] = []

        for uc in self.catalog.get_all():
            # Apply difficulty filter if specified
            if difficulty_filter and uc.difficulty_level != difficulty_filter:
                continue

            if embeddings and uc.use_case_id in embeddings:
                # Semantic matching using embeddings
                score, confidence = self._score_semantic(
                    user_input, uc, embeddings
                )
                match_type = "semantic"
            else:
                # Fallback keyword matching
                score, confidence = self._score_keyword(user_input, uc)
                match_type = "keyword"

            if score >= min_score:
                scores.append((uc, score, match_type, confidence))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)

        # Convert to MatchResult and return top N
        return [
            MatchResult(
                use_case=uc,
                match_score=score,
                match_type=mtype,
                confidence=conf
            )
            for uc, score, mtype, conf in scores[:limit]
        ]

    def _score_semantic(
        self,
        user_input: str,
        use_case: UseCase,
        embeddings: dict
    ) -> Tuple[float, float]:
        """Score semantic similarity using embeddings (cosine distance)."""
        # This is a placeholder - in real implementation would:
        # 1. Get embedding for user_input
        # 2. Get embedding for use_case (from embeddings dict)
        # 3. Compute cosine similarity
        # For now, return placeholder
        return 0.5, 0.5

    def _score_keyword(
        self,
        user_input: str,
        use_case: UseCase
    ) -> Tuple[float, float]:
        """Score keyword similarity with use case."""
        user_lower = user_input.lower()
        title_lower = use_case.title.lower()
        desc_lower = use_case.description.lower()

        # Exact title match
        if user_lower == title_lower:
            return 1.0, 1.0

        # Title contains input
        if user_lower in title_lower or title_lower in user_lower:
            return 0.9, 0.95

        # Count matching keywords
        matched_keywords = [
            kw for kw in use_case.keywords
            if kw.lower() in user_lower or user_lower in kw.lower()
        ]

        if not matched_keywords:
            # No keyword match
            return 0.2, 0.3

        keyword_score = min(len(matched_keywords) / len(use_case.keywords), 1.0)
        base_score = 0.5 + (keyword_score * 0.4)  # 0.5-0.9 range

        # Check description relevance
        desc_words = set(desc_lower.split())
        input_words = set(user_lower.split())
        common_words = desc_words & input_words
        desc_match_ratio = len(common_words) / max(len(input_words), 1)
        base_score = min(base_score + (desc_match_ratio * 0.2), 1.0)

        confidence = min(len(matched_keywords) / max(len(use_case.keywords), 1), 1.0)
        return base_score, confidence

    def rank_by_category(
        self,
        user_input: str,
        embeddings: Optional[dict] = None,
        difficulty_filter: Optional[str] = None,
    ) -> dict:
        """
        Get all use cases ranked by category.

        Useful as fallback when no strong matches found, or when user
        wants to browse by category instead of search.

        Returns:
            Dict mapping category_name -> List of ranked UseCase
        """
        result = {}

        for category in UseCaseCategory:
            uc_list = self.catalog.get_by_category(category)

            # Filter by difficulty if specified
            if difficulty_filter:
                uc_list = [
                    uc for uc in uc_list
                    if uc.difficulty_level == difficulty_filter
                ]

            # Score and sort
            scored = []
            for uc in uc_list:
                if embeddings and uc.use_case_id in embeddings:
                    score, _ = self._score_semantic(user_input, uc, embeddings)
                else:
                    score, _ = self._score_keyword(user_input, uc)
                scored.append((uc, score))

            scored.sort(key=lambda x: x[1], reverse=True)
            result[category.value] = [uc for uc, _ in scored]

        return result

    def get_available_difficulties(self) -> List[str]:
        """Get all available difficulty levels."""
        difficulties = set()
        for uc in self.catalog.get_all():
            difficulties.add(uc.difficulty_level)
        return sorted(list(difficulties))
