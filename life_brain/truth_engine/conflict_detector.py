"""
Conflict Detection Engine — Wave 1 F5.1 Implementation

Detects contradictions between retrieved documents using semantic similarity
and contradiction magnitude scoring.

Algorithm: conflict_score = semantic_similarity × contradiction_magnitude

Features:
- Extracts key claims from document pairs
- Calculates semantic similarity using cosine distance on embeddings
- Calculates contradiction magnitude by type (QUANTITATIVE, QUALITATIVE, SEMANTIC)
- Classifies conflicts by type
- Returns sorted list of ConflictResult objects (high score first)
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Optional, Dict, Any
import re
import logging
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATACLASSES
# ============================================================================

class ConflictType(str, Enum):
    """Type of conflict detected between documents."""
    QUANTITATIVE = "quantitative"  # Numeric ranges differ
    QUALITATIVE = "qualitative"    # Different interpretations
    SEMANTIC = "semantic"          # Different truth values
    NONE = "none"                  # No conflict


@dataclass
class ConflictResult:
    """Result of conflict comparison between two documents."""

    doc_pair: Tuple[int, int]       # Indices of conflicting docs (e.g., (0, 1))
    conflict_score: float            # 0-1, magnitude of conflict
    conflict_type: ConflictType      # QUANTITATIVE, QUALITATIVE, SEMANTIC, NONE
    severity: str                    # "low", "medium", "high"
    claim1: str                      # First conflicting claim (from doc at index doc_pair[0])
    claim2: str                      # Second conflicting claim (from doc at index doc_pair[1])
    explanation: str                 # Human-readable explanation of the conflict


# ============================================================================
# CONFLICT DETECTOR
# ============================================================================

class ConflictDetector:
    """
    Detect contradictions between retrieved documents.

    Algorithm: conflict_score = semantic_similarity × contradiction_magnitude
    """

    # Contradiction magnitude thresholds for severity classification
    SEVERITY_THRESHOLDS = {
        "high": 0.6,      # High severity: conflict_score >= 0.6
        "medium": 0.3,    # Medium severity: 0.3 <= score < 0.6
        "low": 0.1,       # Low severity: 0.1 <= score < 0.3
    }

    # Keywords for conflict type detection
    QUANTITATIVE_KEYWORDS = {
        "numbers", "amount", "count", "percent", "range", "salary", "price",
        "duration", "time", "date", "year", "month", "day", "hour", "minute"
    }

    QUALITATIVE_KEYWORDS = {
        "good", "bad", "success", "failure", "failed", "succeeded", "better", "worse", "improve",
        "decline", "expert", "novice", "major", "minor", "challenge", "benefit", "strength", "weakness"
    }

    SEMANTIC_KEYWORDS = {
        "success", "failure", "led", "contributed", "managed", "participated",
        "achieved", "completed", "failed", "succeeded", "enabled", "prevented"
    }

    def __init__(self):
        """Initialize the ConflictDetector."""
        pass

    def detect_conflicts(self, docs: List[Any]) -> List[ConflictResult]:
        """
        Compare all document pairs for contradictions.

        Args:
            docs: List of RetrievedDocument objects (usually 3, max 3)

        Returns:
            List of ConflictResult objects, one per conflicting pair
            Empty list if no conflicts detected
            Sorted by conflict_score (descending)

        Algorithm:
        1. For each pair of documents (doc_i, doc_j):
           a. Extract key claims from both documents
           b. Compute semantic similarity of claims
           c. Calculate contradiction magnitude
           d. Score conflict = similarity × contradiction
           e. Categorize conflict type
           f. Append to results if score > 0.1

        2. Return results sorted by conflict_score (descending)
        """
        if not docs or len(docs) < 2:
            return []

        results: List[ConflictResult] = []

        # Iterate through all document pairs
        for i in range(len(docs)):
            for j in range(i + 1, len(docs)):
                doc_i = docs[i]
                doc_j = docs[j]

                # Extract key claims from both documents
                claims_i = self._extract_claims(doc_i.text)
                claims_j = self._extract_claims(doc_j.text)

                if not claims_i or not claims_j:
                    continue

                # Compare each pair of claims
                for claim1 in claims_i:
                    for claim2 in claims_j:
                        # Compute semantic similarity
                        similarity = self._compute_semantic_similarity(
                            doc_i, doc_j, claim1, claim2
                        )

                        # Skip very low similarity pairs (but lower threshold to catch more conflicts)
                        if similarity < 0.4:
                            continue

                        # Calculate contradiction magnitude
                        contradiction = self._calculate_contradiction_magnitude(
                            claim1, claim2
                        )

                        # Calculate conflict score — clamp to [0,1] defensively
                        # (similarity or contradiction can slightly exceed 1.0 due to
                        # floating-point arithmetic)
                        conflict_score = min(1.0, max(0.0, similarity * contradiction))

                        # Skip very low scores
                        if conflict_score < 0.1:
                            continue

                        # Categorize conflict type
                        conflict_type = self.categorize_conflict(
                            claim1, claim2, conflict_score
                        )

                        # Determine severity
                        severity = self._determine_severity(conflict_score)

                        # Create result
                        result = ConflictResult(
                            doc_pair=(i, j),
                            conflict_score=conflict_score,
                            conflict_type=conflict_type,
                            severity=severity,
                            claim1=claim1,
                            claim2=claim2,
                            explanation=self._generate_explanation(
                                claim1, claim2, conflict_type, conflict_score
                            )
                        )

                        results.append(result)

        # Sort by conflict_score (descending)
        results.sort(key=lambda r: r.conflict_score, reverse=True)

        # Remove duplicates (same pair, keep highest score)
        unique_results = {}
        for result in results:
            key = (result.doc_pair, result.conflict_type)
            if key not in unique_results or result.conflict_score > unique_results[key].conflict_score:
                unique_results[key] = result

        return list(unique_results.values())

    def score_conflict(self, claim1: str, claim2: str) -> float:
        """
        Compute conflict score between two claims (0-1).

        Algorithm:
            score = semantic_similarity(claim1, claim2) × contradiction_magnitude(claim1, claim2)

        Args:
            claim1: First claim text
            claim2: Second claim text

        Returns:
            Conflict score 0-1

        Examples:
            - "Salary $150k-200k" vs "$120k-180k": 0.25 (partial overlap)
            - "Led redesign" vs "Contributed to improvements": 0.75 (different levels)
            - "Project succeeded" vs "Project failed": 0.95 (direct opposite)
        """
        if not claim1 or not claim2:
            return 0.0

        # Compute semantic similarity using embeddings or enhanced token matching
        # Use the smart similarity that boosts for semantic opposites, leadership conflicts, etc.
        similarity = self._compute_semantic_similarity(None, None, claim1, claim2)

        # Calculate contradiction magnitude
        contradiction = self._calculate_contradiction_magnitude(claim1, claim2)

        # Score = similarity × contradiction
        score = similarity * contradiction

        # Clamp to [0, 1]
        return min(max(score, 0.0), 1.0)

    def categorize_conflict(
        self,
        claim1: str,
        claim2: str,
        conflict_score: float
    ) -> ConflictType:
        """
        Classify conflict as QUANTITATIVE, QUALITATIVE, or SEMANTIC.

        Args:
            claim1: First claim
            claim2: Second claim
            conflict_score: Pre-computed conflict score

        Returns:
            ConflictType enum value

        Heuristics:
            QUANTITATIVE: Both claims contain numbers/ranges
                Example: "$150k-200k" vs "$120k-180k"

            QUALITATIVE: Different interpretations of same concept (includes semantic opposites about outcomes)
                Example: "major success" vs "ultimately deprecated"

            SEMANTIC: Different leadership/responsibility claims
                Example: "led" vs "contributed"
        """
        # Check if claims contain numbers/dates (QUANTITATIVE)
        claim1_has_numbers = self._has_numbers(claim1)
        claim2_has_numbers = self._has_numbers(claim2)

        # Only QUANTITATIVE if BOTH have numbers (salary, dates, metrics)
        if claim1_has_numbers and claim2_has_numbers:
            # Make sure it's not outcome-related judgment keywords
            outcome_keywords = {"success", "failure", "succeeded", "failed", "deprecated"}
            has_outcome = any(kw in claim1.lower() or kw in claim2.lower() for kw in outcome_keywords)
            if not has_outcome:
                return ConflictType.QUANTITATIVE

        # Check for semantic opposites (SEMANTIC or QUALITATIVE)
        # "success" vs "failure/deprecated", "major" vs "limited"
        if self._are_semantic_opposites(claim1, claim2):
            # Check if both are pure binary opposites (succeeded/failed)
            # vs interpretive differences (major success vs ultimately deprecated)
            binary_opposites = [
                ("succeeded", "failed"),
                ("success", "failure"),
            ]
            has_binary = any(
                (word1 in claim1.lower() and word2 in claim2.lower()) or
                (word2 in claim1.lower() and word1 in claim2.lower())
                for word1, word2 in binary_opposites
            )

            if has_binary and len(claim1.split()) <= 3 and len(claim2.split()) <= 3:
                # Short, binary statements are SEMANTIC (succeeded vs failed)
                return ConflictType.SEMANTIC
            else:
                # Longer statements with interpretations are QUALITATIVE
                # (major success with details vs ultimately deprecated with reasons)
                return ConflictType.QUALITATIVE

        # Check for different leadership levels (SEMANTIC)
        if self._qualitative_contradiction(claim1, claim2) > 0.5:
            return ConflictType.SEMANTIC

        # Check for different interpretations (QUALITATIVE)
        if self._has_qualitative_keywords(claim1) or self._has_qualitative_keywords(claim2):
            return ConflictType.QUALITATIVE

        # Default based on score magnitude
        if conflict_score > 0.7:
            return ConflictType.SEMANTIC
        elif conflict_score > 0.3:
            return ConflictType.QUALITATIVE
        else:
            return ConflictType.NONE

    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================

    def _extract_claims(self, text: str, max_claims: int = 5) -> List[str]:
        """
        Extract key claims from document text.

        Strategy: Extract sentences with strong verbs (led, contributed, achieved, etc.)
        or numeric statements.

        Args:
            text: Document text
            max_claims: Maximum claims to extract

        Returns:
            List of claim strings (up to max_claims)
        """
        if not text:
            return []

        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        claims = []

        for sentence in sentences:
            # Look for sentences with strong verbs
            if any(verb in sentence.lower() for verb in [
                "led", "managed", "contributed", "achieved", "created",
                "built", "designed", "implemented", "developed", "launched",
                "succeeded", "failed", "improved", "reduced", "increased",
                "worked", "worked on", "support", "deprecat"
            ]):
                claims.append(sentence)

            # Or sentences with numbers/dates
            elif self._has_numbers(sentence):
                claims.append(sentence)

            # Or sentences with qualitative statements
            elif any(word in sentence.lower() for word in [
                "success", "failure", "challenge", "problem", "solution",
                "benefit", "disadvantage", "strength", "weakness"
            ]):
                claims.append(sentence)

        # Return most relevant claims (up to max_claims)
        return claims[:max_claims]

    def _compute_semantic_similarity(
        self,
        doc1: Any,
        doc2: Any,
        claim1: str,
        claim2: str
    ) -> float:
        """
        Compute semantic similarity between two claims.

        Uses embeddings if available, otherwise falls back to token similarity.
        Special handling for numeric claims (salary, dates, etc).

        Args:
            doc1: First document (has embedding)
            doc2: Second document (has embedding)
            claim1: First claim
            claim2: Second claim

        Returns:
            Similarity score 0-1
        """
        # Try to use embeddings if available
        if hasattr(doc1, 'embedding') and hasattr(doc2, 'embedding') and \
           doc1.embedding and doc2.embedding:
            try:
                return self._cosine_similarity(doc1.embedding, doc2.embedding)
            except Exception:
                pass

        # Special handling for semantic opposites
        # If they're opposite statements about same entity, boost similarity
        if self._are_semantic_opposites(claim1, claim2):
            # Opposite claims about same topic are highly similar (in terms of relevance)
            # but have high contradiction. Use high similarity since they're about same thing.
            return 0.92

        # Special handling for leadership/responsibility conflicts
        # If they have qualitative contradiction (led vs contributed), boost similarity
        qual_cont = self._qualitative_contradiction(claim1, claim2)
        if qual_cont > 0.5:
            # These are about same project/work but different responsibility levels
            # Boost similarity since they're about same thing with different claims
            token_sim = self._token_similarity(claim1, claim2)
            return max(token_sim, 0.75)

        # Special handling for numeric claims (salary, dates)
        # If both have numbers, boost similarity since they're comparing same concept
        if self._has_numbers(claim1) and self._has_numbers(claim2):
            # These are likely about same concept (salary, date, etc)
            # Even if wording is different, they're comparable
            token_sim = self._token_similarity(claim1, claim2)

            # Check if it's a date-based conflict (contains month/year patterns)
            full_months = ["january", "february", "march", "april", "may", "june",
                          "july", "august", "september", "october", "november", "december"]
            has_month = any(re.search(r'\b' + m + r'\b', (claim1 + claim2).lower()) for m in full_months)
            has_year = bool(re.search(r'\b(20\d{2}|19\d{2})\b', claim1 + claim2))
            has_date_keywords = has_month or has_year

            if has_date_keywords:
                # Date conflicts need higher similarity (these are about same period)
                return max(token_sim, 0.65)
            else:
                # Other numeric conflicts (salaries, metrics) use moderate boost
                return max(token_sim, 0.45)

        # Fall back to token-based similarity
        return self._token_similarity(claim1, claim2)

    def _token_similarity(self, claim1: str, claim2: str) -> float:
        """
        Calculate token-based similarity (Jaccard index).

        Args:
            claim1: First claim
            claim2: Second claim

        Returns:
            Similarity score 0-1
        """
        if not claim1 or not claim2:
            return 0.0

        # Tokenize (case-insensitive)
        tokens1 = set(claim1.lower().split())
        tokens2 = set(claim2.lower().split())

        if not tokens1 or not tokens2:
            return 0.0

        # Remove common stop words that reduce meaningful similarity
        stop_words = {"a", "an", "the", "and", "or", "in", "to", "of", "for", "is", "was", "were", "be", "at", "by"}
        tokens1 = tokens1 - stop_words
        tokens2 = tokens2 - stop_words

        # If after removing stop words both are empty, fall back to original
        if not tokens1 or not tokens2:
            tokens1 = set(claim1.lower().split())
            tokens2 = set(claim2.lower().split())

        # Jaccard similarity = intersection / union
        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score 0-1
        """
        if not vec1 or not vec2 or len(vec1) == 0 or len(vec2) == 0:
            return 0.0

        try:
            v1 = np.array(vec1, dtype=np.float32)
            v2 = np.array(vec2, dtype=np.float32)

            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = np.dot(v1, v2) / (norm1 * norm2)
            return float(np.clip(similarity, 0.0, 1.0))

        except Exception as e:
            logger.warning(f"Error computing cosine similarity: {e}")
            return 0.0

    def _calculate_contradiction_magnitude(self, claim1: str, claim2: str) -> float:
        """
        Calculate magnitude of contradiction between claims.

        Strategy:
        1. If identical: return 0
        2. If both are numeric: compute normalized difference
        3. If semantic opposites: return high score
        4. Otherwise: use keyword matching

        Args:
            claim1: First claim
            claim2: Second claim

        Returns:
            Contradiction magnitude 0-1
        """
        if not claim1 or not claim2:
            return 0.0

        # Check for identical claims
        if claim1.strip().lower() == claim2.strip().lower():
            return 0.0

        # Check for semantic opposites (highest contradiction)
        if self._are_semantic_opposites(claim1, claim2):
            return 0.95

        # Check for numeric difference
        magnitude = self._numeric_contradiction(claim1, claim2)
        if magnitude > 0:
            return magnitude

        # Check for qualitative differences
        magnitude = self._qualitative_contradiction(claim1, claim2)
        if magnitude > 0:
            return magnitude

        # Default: low contradiction
        return 0.2

    def _numeric_contradiction(self, claim1: str, claim2: str) -> float:
        """
        Calculate contradiction for numeric claims.

        Uses range overlap calculation: contradiction = 1 - (overlap / union)

        Args:
            claim1: First claim
            claim2: Second claim

        Returns:
            0 if no numbers found, otherwise contradiction magnitude
        """
        # Extract all numbers from claims
        numbers1 = re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', claim1)
        numbers2 = re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', claim2)

        if not numbers1 or not numbers2:
            return 0.0

        try:
            # Convert to floats
            nums1 = [float(n.replace(',', '')) for n in numbers1]
            nums2 = [float(n.replace(',', '')) for n in numbers2]

            # Find min and max for range comparison
            min1, max1 = min(nums1), max(nums1)
            min2, max2 = min(nums2), max(nums2)

            # Calculate overlap and union
            # overlap = max(0, min(B,D) - max(A,C))
            # union = max(B,D) - min(A,C)
            overlap_start = max(min1, min2)
            overlap_end = min(max1, max2)
            overlap = max(0, overlap_end - overlap_start)

            # Union = span from smallest min to largest max
            union_start = min(min1, min2)
            union_end = max(max1, max2)
            union = union_end - union_start

            # Intersection over Union (IoU)
            # High IoU = low contradiction
            iou = overlap / union if union > 0 else 0

            # Contradiction = 1 - IoU
            contradiction = 1.0 - iou
            return min(max(contradiction, 0.0), 1.0)

        except Exception as e:
            logger.warning(f"Error computing numeric contradiction: {e}")
            return 0.0

    def _qualitative_contradiction(self, claim1: str, claim2: str) -> float:
        """
        Calculate contradiction for qualitative claims.

        Args:
            claim1: First claim
            claim2: Second claim

        Returns:
            Contradiction magnitude 0-1
        """
        claim1_lower = claim1.lower()
        claim2_lower = claim2.lower()

        # Check for opposed keywords
        opposed_pairs = [
            ("led", "contributed"),
            ("led", "participated"),
            ("led", "supported"),
            ("managed", "worked on"),
            ("success", "failure"),
            ("succeeded", "failed"),
            ("improved", "declined"),
            ("senior", "junior"),
            ("major", "minor"),
        ]

        for word1, word2 in opposed_pairs:
            if (word1 in claim1_lower and word2 in claim2_lower) or \
               (word2 in claim1_lower and word1 in claim2_lower):
                # Higher contradiction for leadership conflicts
                if word1 in ["led", "managed"] or word2 in ["led", "managed"]:
                    return 1.0
                return 0.7

        # Check for level differences (led vs contributed)
        leadership_verbs = {"led", "managed", "directed", "oversaw"}
        contribution_verbs = {"contributed", "participated", "worked on", "supported"}

        has_leadership_1 = any(v in claim1_lower for v in leadership_verbs)
        has_contribution_1 = any(v in claim1_lower for v in contribution_verbs)
        has_leadership_2 = any(v in claim2_lower for v in leadership_verbs)
        has_contribution_2 = any(v in claim2_lower for v in contribution_verbs)

        if (has_leadership_1 and has_contribution_2) or (has_contribution_1 and has_leadership_2):
            return 1.0

        return 0.0

    def _are_semantic_opposites(self, claim1: str, claim2: str) -> bool:
        """
        Check if claims are semantic opposites.

        Args:
            claim1: First claim
            claim2: Second claim

        Returns:
            True if opposites, False otherwise
        """
        claim1_lower = claim1.lower()
        claim2_lower = claim2.lower()

        opposites = [
            ("success", "failure"),
            ("succeeded", "failed"),
            ("succeeded", "deprecated"),
            ("success", "deprecated"),
            ("improvement", "decline"),
            ("improved", "deprecated"),
            ("positive", "negative"),
            ("major", "limited"),
            ("major success", "ultimately deprecated"),
            ("succeeded", "ultimately deprecated"),
            ("success", "ultimately deprecated"),
        ]

        for word1, word2 in opposites:
            # Check both directions
            if (word1 in claim1_lower and word2 in claim2_lower) or \
               (word2 in claim1_lower and word1 in claim2_lower):
                return True

        # Additional checks for opposite verbs
        opposite_verbs = [
            ("led", "deprecated"),
            ("created", "deprecated"),
            ("built", "deprecated"),
        ]

        for verb1, verb2 in opposite_verbs:
            if (verb1 in claim1_lower and verb2 in claim2_lower) or \
               (verb2 in claim1_lower and verb1 in claim2_lower):
                return True

        return False

    def _has_numbers(self, text: str) -> bool:
        """
        Check if text contains numbers or date references.

        Args:
            text: Text to check

        Returns:
            True if contains numbers/dates
        """
        # Check for numbers (digits)
        if re.search(r'\d+', text):
            return True

        # Check for full month names (word boundary)
        full_months = [
            "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october", "november", "december"
        ]
        for month in full_months:
            if re.search(r'\b' + month + r'\b', text.lower()):
                return True

        # Check for year patterns (4 consecutive digits within word boundaries)
        if re.search(r'\b(20\d{2}|19\d{2})\b', text):
            return True

        return False

    def _has_qualitative_keywords(self, text: str) -> bool:
        """
        Check if text contains qualitative keywords (judgment words).

        Args:
            text: Text to check

        Returns:
            True if contains qualitative keywords
        """
        keywords = [
            "success", "failure", "challenge", "benefit", "strength",
            "weakness", "improvement", "decline", "senior", "junior",
            "major", "minor", "good", "bad", "better", "worse",
            "succeeded", "failed"
        ]
        return any(keyword in text.lower() for keyword in keywords)

    def _determine_severity(self, conflict_score: float) -> str:
        """
        Determine severity level based on conflict score.

        Args:
            conflict_score: Conflict score 0-1

        Returns:
            "low", "medium", or "high"
        """
        if conflict_score >= self.SEVERITY_THRESHOLDS["high"]:
            return "high"
        elif conflict_score >= self.SEVERITY_THRESHOLDS["medium"]:
            return "medium"
        else:
            return "low"

    def _generate_explanation(
        self,
        claim1: str,
        claim2: str,
        conflict_type: ConflictType,
        conflict_score: float
    ) -> str:
        """
        Generate human-readable explanation of the conflict.

        Args:
            claim1: First claim
            claim2: Second claim
            conflict_type: Type of conflict
            conflict_score: Conflict score

        Returns:
            Explanation string
        """
        if conflict_type == ConflictType.QUANTITATIVE:
            return f"Quantitative discrepancy: '{claim1}' vs '{claim2}' (score: {conflict_score:.2f})"
        elif conflict_type == ConflictType.QUALITATIVE:
            return f"Qualitative difference: '{claim1}' vs '{claim2}' (score: {conflict_score:.2f})"
        elif conflict_type == ConflictType.SEMANTIC:
            return f"Semantic contradiction: '{claim1}' vs '{claim2}' (score: {conflict_score:.2f})"
        else:
            return f"Minor discrepancy: '{claim1}' vs '{claim2}' (score: {conflict_score:.2f})"
