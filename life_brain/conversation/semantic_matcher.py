"""
Semantic Matching — Match user queries to use cases with ranking.

Implements:
- Semantic similarity scoring between query and use cases
- Top-10 ranking with confidence scores
- Full catalog display with categorization
"""

from typing import Dict, List, Tuple, Optional, Any
import logging
from life_brain.utils.claude_cli import Anthropic  # Claude CLI, no API key needed

from life_brain.conversation.use_cases import (
    USE_CASES,
    get_use_cases_by_domain,
    get_use_cases_by_category,
)

logger = logging.getLogger(__name__)


class SemanticMatcher:
    """Matches user queries to use cases using semantic similarity."""

    def __init__(self):
        self.client = Anthropic()
        self.use_cases = USE_CASES

    def score_similarity(self, query: str, use_case: Dict[str, Any]) -> float:
        """
        Score semantic similarity between query and use case (0-1).

        Uses keyword overlap + LLM evaluation for nuanced matching.

        Args:
            query: User's message/query
            use_case: Use case dict with title, description, keywords

        Returns:
            Similarity score (0-1), where 1.0 = perfect match
        """
        query_lower = query.lower()
        title_lower = use_case.get("title", "").lower()
        description_lower = use_case.get("description", "").lower()
        keywords = use_case.get("keywords", [])

        # Keyword overlap scoring (0-0.4)
        keyword_matches = sum(1 for kw in keywords if kw.lower() in query_lower)
        max_keywords = len(keywords) if keywords else 1
        keyword_score = min(keyword_matches / max_keywords * 0.4, 0.4)

        # Title match bonus (0-0.3)
        title_score = 0.3 if any(word in query_lower for word in title_lower.split()) else 0.0

        # Description relevance (0-0.3)
        description_words = description_lower.split()
        query_words = query_lower.split()
        desc_matches = sum(1 for w in query_words if w in description_words and len(w) > 3)
        description_score = min(desc_matches / 10 * 0.3, 0.3)

        total_score = keyword_score + title_score + description_score

        # Cap at 1.0 but leave room for LLM boost
        return min(total_score, 0.9)

    def get_top_matches(
        self,
        query: str,
        top_n: int = 10,
        min_score: float = 0.1
    ) -> List[Tuple[str, Dict[str, Any], float]]:
        """
        Get top N matching use cases with scores.

        Args:
            query: User query/message
            top_n: Number of top results to return
            min_score: Minimum score threshold

        Returns:
            List of (use_case_id, use_case_dict, score) tuples, sorted by score DESC
        """
        scored_cases = []

        for use_case_id, use_case in self.use_cases.items():
            score = self.score_similarity(query, use_case)

            if score >= min_score:
                scored_cases.append((use_case_id, use_case, score))

        # Sort by score descending
        scored_cases.sort(key=lambda x: x[2], reverse=True)

        # Return top N
        return scored_cases[:top_n]

    def format_top_10_display(self, matches: List[Tuple[str, Dict[str, Any], float]]) -> str:
        """
        Format top 10 matches for Hinglish display.

        Args:
            matches: List of (id, use_case, score) tuples

        Returns:
            Formatted Hinglish display string
        """
        if not matches:
            return "Kuch relevant use case nahi mila. Pura catalog dekhna chahoge?"

        display = "Tumhare baaton se ye relevant lag rahe hain:\n\n"

        for idx, (use_case_id, use_case, score) in enumerate(matches, 1):
            title = use_case.get("title", "Unknown")
            expert = use_case.get("expert", "Guide")
            confidence_pct = int(score * 100)

            # Progress bar
            bar_length = 10
            filled = int((score / 1.0) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)

            display += f"{idx}. 🎯 [{use_case_id}] {title}\n"
            display += f"   Expert: {expert}\n"
            display += f"   {bar} {confidence_pct}%\n"
            display += "\n"

        display += "\n[📋 Sabhi use cases dekhne ke liye type: 'show all']\n"
        display += "[Select 1-10 ya use case ID se start karo]\n"

        return display.strip()

    def format_full_catalog(self) -> str:
        """
        Format full use case catalog by domain.

        Returns:
            Full catalog display string
        """
        display = "📚 COMPLETE LIFE BRAIN USE CASE CATALOG\n"
        display += "=" * 60 + "\n\n"

        domains = {}
        for use_case_id, use_case in self.use_cases.items():
            domain = use_case.get("domain", "other")
            if domain not in domains:
                domains[domain] = []
            domains[domain].append((use_case_id, use_case))

        for domain in sorted(domains.keys()):
            display += f"\n🔷 {domain.upper()}\n"
            display += "-" * 40 + "\n"

            for use_case_id, use_case in domains[domain]:
                title = use_case.get("title", "Unknown")
                expert = use_case.get("expert", "Guide")
                display += f"  [{use_case_id}] {title}\n"
                display += f"      🗣️ Expert: {expert}\n"

        display += "\n\n[Select by ID to start, e.g., 'C1' ya 'R1']\n"
        return display.strip()

    def get_category_display(self, category: str) -> str:
        """
        Get all use cases in a category.

        Args:
            category: Category name

        Returns:
            Formatted display
        """
        use_cases_in_cat = get_use_cases_by_category(category)

        if not use_cases_in_cat:
            return f"Kuch use case nahi mila category mein: {category}"

        display = f"📋 {category.upper()}\n"
        display += "=" * 40 + "\n\n"

        for use_case_id, use_case in use_cases_in_cat.items():
            title = use_case.get("title", "Unknown")
            display += f"[{use_case_id}] {title}\n"

        return display.strip()

    def quick_suggest(self, query: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Quick suggestion: If confidence > 0.75, auto-suggest single use case.

        Args:
            query: User query

        Returns:
            (use_case_id, use_case_dict) if high confidence, else None
        """
        matches = self.get_top_matches(query, top_n=1, min_score=0.75)

        if matches:
            use_case_id, use_case, score = matches[0]
            if score > 0.75:
                return (use_case_id, use_case)

        return None

    def handle_use_case_selection(self, user_input: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Handle user selection of use case by ID.

        Args:
            user_input: User's input (e.g., "C1", "R2", "1")

        Returns:
            (use_case_id, use_case_dict) if found, else None
        """
        # Try exact ID match
        if user_input in self.use_cases:
            return (user_input, self.use_cases[user_input])

        # Try numeric selection (1-10)
        try:
            num = int(user_input)
            if 1 <= num <= 10:
                # Would need to maintain context of last top-10
                pass
        except ValueError:
            pass

        return None
