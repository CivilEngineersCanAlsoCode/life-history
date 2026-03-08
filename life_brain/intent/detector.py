"""
Intent Detector — Detect user intent from keywords matching to 40+ use cases.

Implements:
- detect_intent(): Keyword-based matching to use cases with confidence scoring
- Multi-level matching: exact, partial, semantic
- Confidence scoring based on keyword overlap and context
- Continuous detection even within small talk
"""

from typing import Dict, List, Tuple, Optional, Any
import logging
from dataclasses import dataclass
from anthropic import Anthropic

from life_brain.conversation.use_cases import (
    USE_CASES,
    get_use_case,
    get_use_case_keywords,
)

logger = logging.getLogger(__name__)


@dataclass
class IntentMatch:
    """Result of intent detection."""
    use_case_id: Optional[str]
    use_case_title: Optional[str]
    confidence: float  # 0.0-1.0
    matched_keywords: List[str]
    match_type: str  # "exact", "partial", "semantic", "none"


class IntentDetector:
    """Detects user intent from keywords matching to 40+ use cases."""

    def __init__(self, use_llm_ranking: bool = True):
        """
        Initialize IntentDetector.

        Args:
            use_llm_ranking: Whether to use LLM for ranking ambiguous matches
        """
        self.client = Anthropic()
        self.use_llm_ranking = use_llm_ranking
        self.use_cases = USE_CASES
        self.keyword_map = get_use_case_keywords()

    def detect_intent(
        self,
        user_input: str,
        top_n: int = 1,
        confidence_threshold: float = 0.5,
    ) -> Tuple[Optional[str], float, IntentMatch]:
        """
        Detect intent from user input using keyword matching.

        Algorithm:
        1. Extract keywords from user input
        2. Match keywords to use cases
        3. Score each matching use case
        4. Return top match with confidence

        Args:
            user_input: User's message or query
            top_n: Number of top matches to consider (for LLM ranking)
            confidence_threshold: Minimum confidence to return match

        Returns:
            Tuple of (use_case_id, confidence, IntentMatch)
            Returns (None, 0.0, IntentMatch) if no match above threshold
        """
        logger.debug(f"Detecting intent from: {user_input[:100]}")

        # Step 1: Extract keywords
        keywords = self._extract_keywords(user_input)
        logger.debug(f"Extracted keywords: {keywords}")

        # Step 2: Find matching use cases
        matches = self._find_matching_use_cases(keywords)
        logger.debug(f"Found {len(matches)} matching use cases")

        if not matches:
            logger.debug("No use cases matched")
            return (None, 0.0, IntentMatch(None, None, 0.0, [], "none"))

        # Step 3: Score matches
        scored_matches = [
            (uc_id, self._score_match(uc_id, keywords))
            for uc_id in matches
        ]
        scored_matches.sort(key=lambda x: x[1], reverse=True)

        # Step 4: Use LLM to rank ambiguous cases if enabled
        if self.use_llm_ranking and len(scored_matches) > 1 and scored_matches[0][1] < 0.85:
            best_id = self._rank_with_llm(user_input, scored_matches[:top_n])
        else:
            best_id = scored_matches[0][0]

        best_score = self._score_match(best_id, keywords)

        # Step 5: Build match result
        use_case = get_use_case(best_id)
        match_result = IntentMatch(
            use_case_id=best_id,
            use_case_title=use_case.get("title") if use_case else None,
            confidence=best_score,
            matched_keywords=keywords,
            match_type=self._get_match_type(best_score),
        )

        logger.debug(
            f"Intent detected: {best_id} (confidence: {best_score:.2f}, "
            f"match_type: {match_result.match_type})"
        )

        if best_score < confidence_threshold:
            logger.debug(f"Confidence {best_score:.2f} below threshold {confidence_threshold}")
            return (None, 0.0, match_result)

        return (best_id, best_score, match_result)

    def detect_intent_continuous(
        self,
        messages: List[Dict[str, str]],
        confidence_threshold: float = 0.6,
    ) -> Tuple[Optional[str], float, IntentMatch]:
        """
        Detect intent from conversation history (continuous detection).

        Useful for detecting intent shift during small talk.

        Args:
            messages: List of message dicts with "role" and "content"
            confidence_threshold: Minimum confidence to return match

        Returns:
            Tuple of (use_case_id, confidence, IntentMatch)
        """
        # Combine all user messages into one context
        user_inputs = [
            msg["content"]
            for msg in messages
            if msg.get("role") == "user"
        ]

        if not user_inputs:
            return (None, 0.0, IntentMatch(None, None, 0.0, [], "none"))

        combined_input = " ".join(user_inputs)
        logger.debug(
            f"Continuous intent detection from {len(user_inputs)} messages "
            f"({len(combined_input)} chars)"
        )

        return self.detect_intent(combined_input, confidence_threshold=confidence_threshold)

    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text.

        Simple approach: split on whitespace and filter short words.
        Can be enhanced with NLP/stemming in production.

        Args:
            text: Text to extract keywords from

        Returns:
            List of keywords
        """
        words = text.lower().split()
        # Filter: remove short words, punctuation
        keywords = [
            w.strip(".,!?;:\"'") for w in words
            if len(w.strip(".,!?;:\"'")) > 2
        ]
        return keywords

    def _find_matching_use_cases(self, keywords: List[str]) -> List[str]:
        """
        Find use cases matching given keywords.

        Args:
            keywords: List of keywords to match

        Returns:
            List of matching use case IDs
        """
        matching_uc_ids = set()

        for keyword in keywords:
            keyword_lower = keyword.lower()

            # Exact and partial matches in keyword map
            for kw, uc_ids in self.keyword_map.items():
                if keyword_lower == kw.lower() or keyword_lower in kw.lower():
                    matching_uc_ids.update(uc_ids)

        return sorted(list(matching_uc_ids))

    def _score_match(self, use_case_id: str, keywords: List[str]) -> float:
        """
        Score a use case match based on keyword overlap.

        Scoring algorithm:
        - Exact keyword matches: +0.3 each (max 0.6)
        - Partial matches: +0.15 each (max 0.3)
        - Category/domain bonus: +0.1

        Args:
            use_case_id: Use case ID to score
            keywords: Keywords to match against

        Returns:
            Score from 0.0 to 1.0
        """
        use_case = get_use_case(use_case_id)
        if not use_case:
            return 0.0

        uc_keywords = use_case.get("keywords", [])
        uc_keywords_lower = [kw.lower() for kw in uc_keywords]
        uc_title = use_case.get("title", "").lower()
        uc_description = use_case.get("description", "").lower()

        score = 0.0

        # Keyword matching
        exact_matches = 0
        partial_matches = 0

        for keyword in keywords:
            keyword_lower = keyword.lower()

            # Exact match in keywords
            if keyword_lower in uc_keywords_lower:
                exact_matches += 1
            # Partial match in keywords
            elif any(keyword_lower in kw for kw in uc_keywords_lower):
                partial_matches += 1
            # Match in title or description
            elif keyword_lower in uc_title or keyword_lower in uc_description:
                partial_matches += 0.5

        # Score calculation
        score += min(exact_matches * 0.3, 0.6)  # Exact: +0.3 each, max 0.6
        score += min(partial_matches * 0.15, 0.3)  # Partial: +0.15 each, max 0.3

        # Bonus if multiple matches
        total_matches = exact_matches + partial_matches
        if total_matches >= 2:
            score += 0.05

        # Cap at 1.0
        score = min(score, 1.0)

        logger.debug(
            f"  Score for {use_case_id}: {score:.2f} "
            f"(exact: {exact_matches}, partial: {partial_matches})"
        )

        return score

    def _get_match_type(self, confidence: float) -> str:
        """
        Determine match type based on confidence.

        Args:
            confidence: Confidence score

        Returns:
            Match type: "exact", "partial", "semantic", or "none"
        """
        if confidence >= 0.85:
            return "exact"
        elif confidence >= 0.65:
            return "partial"
        elif confidence >= 0.5:
            return "semantic"
        else:
            return "none"

    def _rank_with_llm(
        self,
        user_input: str,
        candidates: List[Tuple[str, float]],
    ) -> str:
        """
        Use LLM to rank ambiguous matches.

        Args:
            user_input: Original user input
            candidates: List of (use_case_id, score) tuples to rank

        Returns:
            Best use case ID according to LLM
        """
        if not candidates:
            return None

        # If only one candidate, return it
        if len(candidates) == 1:
            return candidates[0][0]

        try:
            # Build candidate descriptions
            candidate_lines = []
            for uc_id, score in candidates:
                use_case = get_use_case(uc_id)
                if use_case:
                    title = use_case.get("title", uc_id)
                    desc = use_case.get("description", "")[:80]
                    candidate_lines.append(
                        f"{uc_id}. {title} — {desc}"
                    )

            candidates_text = "\n".join(candidate_lines)

            prompt = f"""Given this user input, which use case is most relevant?

User input: "{user_input}"

Candidates:
{candidates_text}

Respond with ONLY the use case ID (e.g., "C1"). If none are relevant, respond "NONE"."""

            response = self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}]
            )

            best_id = response.content[0].text.strip()
            if best_id == "NONE":
                return candidates[0][0]  # Fallback to top keyword match

            # Validate response
            valid_ids = {uc_id for uc_id, _ in candidates}
            if best_id not in valid_ids:
                logger.warning(f"LLM returned invalid ID: {best_id}, using top match")
                return candidates[0][0]

            logger.debug(f"LLM ranked: {best_id}")
            return best_id

        except Exception as e:
            logger.error(f"Error in LLM ranking: {e}, using top keyword match")
            return candidates[0][0]

    def get_all_use_cases(self) -> Dict[str, Dict[str, Any]]:
        """Get all use cases."""
        return self.use_cases

    def get_use_cases_by_domain(self, domain: str) -> Dict[str, Dict[str, Any]]:
        """Get use cases in a domain."""
        return {
            uc_id: uc for uc_id, uc in self.use_cases.items()
            if uc.get("domain") == domain
        }
