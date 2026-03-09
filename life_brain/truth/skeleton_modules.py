"""
Skeleton Modules for Wave 1 Implementation

This file provides the EXACT dataclasses, enums, and function signatures
that F5.1, F5.2, and F5.4 agents MUST implement.

Copy these into your implementation files and fill in the logic.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Optional, Dict, Any


# ============================================================================
# F5.1: CONFLICT DETECTION ENGINE
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


class ConflictDetector:
    """
    Detect contradictions between retrieved documents.

    Algorithm: conflict_score = semantic_similarity × contradiction_magnitude
    """

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
        pass

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
        pass

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

            QUALITATIVE: Different interpretations of same concept
                Example: "senior" vs "junior" engineer

            SEMANTIC: Same concept but different truth values
                Example: "succeeded" vs "failed"
        """
        pass


# ============================================================================
# F5.2: SOURCE CREDIBILITY SCORING
# ============================================================================

@dataclass
class CredibilityScore:
    """Trustworthiness assessment of a source document."""

    doc_id: str                      # Same as RetrievedDocument.doc_id
    credibility: float               # 0-1, overall trustworthiness score
    category: str                    # "expert", "verified", "personal", "questionable"
    recency_score: float             # Component (0-1), how recent is the document?
    authority_score: float           # Component (0-1), how authoritative?
    accuracy_score: float            # Component (0-1), how accurate/verified?
    explanation: str                 # Human-readable justification


class CredibilityScorer:
    """
    Score trustworthiness of documents based on recency, authority, accuracy.

    Formula: credibility = (recency × 0.3) + (authority × 0.4) + (accuracy × 0.3)
    """

    def __init__(self):
        """Initialize the CredibilityScorer."""
        pass

    def score_source(
        self,
        doc: Any,  # RetrievedDocument
        context: Optional[Dict[str, Any]] = None
    ) -> CredibilityScore:
        """
        Compute credibility score for a document.

        Args:
            doc: RetrievedDocument object
            context: Optional context dict (query intent, user profile, etc.)

        Returns:
            CredibilityScore with component breakdown

        Algorithm:
        1. Extract recency score from doc.metadata["date"]
        2. Extract authority score from doc.metadata["source"] and ["author"]
        3. Extract accuracy score from corroboration, contradictions
        4. Compute overall score using weighted formula
        5. Classify category (expert, verified, personal, questionable)
        6. Generate human-readable explanation
        """
        pass

    def rank_by_credibility(self, docs: List[Any]) -> List[Any]:
        """
        Sort documents by credibility score (descending).

        Args:
            docs: List of RetrievedDocument objects

        Returns:
            Same list sorted by credibility (highest first)
        """
        pass

    def get_credibility_explanation(self, doc: Any) -> str:
        """
        Generate human-readable explanation of credibility assessment.

        Args:
            doc: RetrievedDocument object

        Returns:
            String like: "Recent (2024), official research, verified facts"
        """
        pass

    @staticmethod
    def _calculate_recency_score(date_str: str) -> float:
        """
        Score document by recency.

        Scoring:
            < 3 months: 1.0
            3-6 months: 0.8
            6-12 months: 0.6
            > 12 months: 0.4
        """
        pass

    @staticmethod
    def _calculate_authority_score(
        source: str,
        author: str,
        authority_type: Optional[str] = None
    ) -> float:
        """
        Score document by authority of source and author.

        Scoring:
            Official/researched: 1.0
            Professional/verified: 0.8
            Personal/expert: 0.7
            Community/unverified: 0.5
            Unknown: 0.3
        """
        pass

    @staticmethod
    def _calculate_accuracy_score(
        doc: Any,
        corroborated_by: Optional[List[str]] = None,
        contradicted_by: Optional[List[str]] = None
    ) -> float:
        """
        Score document by accuracy based on verification.

        Scoring:
            Verified fact: 1.0
            Corroborated (2+ sources): 0.9
            Single source: 0.7
            Potentially outdated: 0.5
            Contradicted: 0.2
        """
        pass


# ============================================================================
# F5.4: HALLUCINATION PREVENTION RULES
# ============================================================================

@dataclass
class RuleViolation:
    """A single rule violation in answer validation."""

    rule_name: str                   # E.g., "confidence_floor", "date_integrity"
    severity: str                    # "error" (fails validation) or "warning" (flag but allow)
    message: str                     # Explanation of violation


@dataclass
class ValidationResult:
    """Result of hallucination prevention validation."""

    is_valid: bool                   # Does answer pass all rules?
    passed_rules: List[str]          # Rule names that passed
    violated_rules: List[RuleViolation]  # Rules that failed
    rejection_reason: Optional[str]  # If is_valid=False, why?


class HallucinationPrevention:
    """
    Hard validation rules to prevent hallucinations before generation.

    Five rules, applied in order:
    1. Synthesis Limits (max 3 docs, no synthesis across contradictions)
    2. Confidence Floor (groundedness >= 0.50)
    3. Date Integrity (don't cite old documents for recent questions)
    4. Authority Matching (match document type to question type)
    5. Factuality Checks (numeric consistency ±10%, date alignment)
    """

    def __init__(self):
        """Initialize the HallucinationPrevention validator."""
        pass

    def validate_answer(
        self,
        answer: str,
        docs: List[Any],  # RetrievedDocument
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Check answer against 5 prevention rules.

        Args:
            answer: Generated answer text
            docs: Supporting documents (1-3)
            context: Optional context with:
                - groundedness_score (0-1)
                - conflicts (List[ConflictResult])
                - credibility_scores (List[CredibilityScore])
                - user_query (str)

        Returns:
            ValidationResult with passed/violated rules

        Algorithm:
        1. Run Rule 1: Check synthesis limits
        2. Run Rule 2: Check confidence floor
        3. Run Rule 3: Check date integrity
        4. Run Rule 4: Check authority matching
        5. Run Rule 5: Check factuality
        6. Aggregate results and return
        """
        pass

    def get_rejection_reason(self, violation: RuleViolation) -> str:
        """
        Generate human-understandable rejection reason.

        Args:
            violation: A RuleViolation object

        Returns:
            String like: "I don't have enough recent information to answer this."
        """
        pass

    @staticmethod
    def _rule_synthesis_limits(docs: List[Any], answer: str) -> Tuple[bool, Optional[str]]:
        """
        Rule 1: Synthesis Limits

        - Max 3 documents per answer ✓
        - No synthesis across contradictory sources

        Returns:
            (is_valid, error_message)
        """
        pass

    @staticmethod
    def _rule_confidence_floor(
        groundedness_score: float,
        conflicts: Optional[List[ConflictResult]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Rule 2: Confidence Floor

        - If groundedness < 0.50 → invalid ("I don't know")
        - If conflicts + low credibility → invalid

        Returns:
            (is_valid, error_message)
        """
        pass

    @staticmethod
    def _rule_date_integrity(
        docs: List[Any],
        user_query: str,
        max_doc_age_days: int = 365
    ) -> Tuple[bool, Optional[str]]:
        """
        Rule 3: Date Integrity

        - Don't cite facts from documents older than threshold
        - Example: Career trends from 2020 ≠ 2024 market trends

        Returns:
            (is_valid, error_message)
        """
        pass

    @staticmethod
    def _rule_authority_matching(
        docs: List[Any],
        user_query: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Rule 4: Authority Matching

        - Match document authority to question type
        - Example: Career guidance → require personal experience OR expert source

        Returns:
            (is_valid, error_message)
        """
        pass

    @staticmethod
    def _rule_factuality_checks(
        answer: str,
        docs: List[Any],
        numeric_tolerance: float = 0.1  # ±10%
    ) -> Tuple[bool, Optional[str]]:
        """
        Rule 5: Factuality Checks

        - Numeric facts must be consistent across sources (±10%)
        - Dates must align with known events
        - Names/titles must be verified

        Returns:
            (is_valid, error_message)
        """
        pass


# ============================================================================
# INTEGRATION HELPER
# ============================================================================

@dataclass
class E5TruthEngineContext:
    """Context passed from F5.1→F5.3, F5.2→F5.3, F5.3→F5.5."""

    conflicts: List[ConflictResult]          # From F5.1
    credibility_scores: List[CredibilityScore]  # From F5.2
    validation_result: Optional[ValidationResult]  # From F5.4
    retrieved_docs: List[Any]                # Original RetrievedDocument list
    groundedness_score: float                # From E4
    user_query: str                          # Original user query


if __name__ == "__main__":
    print("✓ Skeleton modules loaded")
    print("✓ ConflictDetector ready for implementation")
    print("✓ CredibilityScorer ready for implementation")
    print("✓ HallucinationPrevention ready for implementation")
