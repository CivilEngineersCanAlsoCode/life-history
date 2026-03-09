"""
MECE (Mutually Exclusive, Collectively Exhaustive) validation.

Detects duplicate or highly similar atomic queries (cosine_sim > 0.85)
and suggests merges to prevent duplicate storage.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import math


# Similarity threshold above which two queries are considered duplicates
DUPLICATE_THRESHOLD = 0.85


@dataclass
class AtomicQuery:
    """An atomic query/nugget to validate."""

    query_id: str
    question: str
    answer: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None


@dataclass
class DuplicateCandidate:
    """A pair of queries with high similarity."""

    query_a_id: str
    query_b_id: str
    similarity_score: float
    decision: str  # "merge" or "keep_both"
    merge_reason: str


@dataclass
class MECEReport:
    """Report of MECE validation results."""

    total_queries: int
    duplicates_found: int
    merges_suggested: int
    kept_both: int
    candidates: List[DuplicateCandidate] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_queries": self.total_queries,
            "duplicates_found": self.duplicates_found,
            "merges_suggested": self.merges_suggested,
            "kept_both": self.kept_both,
            "candidates": [
                {
                    "query_a": c.query_a_id,
                    "query_b": c.query_b_id,
                    "similarity": round(c.similarity_score, 3),
                    "decision": c.decision,
                    "reason": c.merge_reason,
                }
                for c in self.candidates
            ],
        }


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Compute cosine similarity between two vectors.

    Args:
        v1: First vector
        v2: Second vector

    Returns:
        Cosine similarity (0-1)
    """
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0

    try:
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return max(0.0, min(1.0, dot / (norm1 * norm2)))
    except Exception:
        return 0.0


def _text_similarity(text_a: str, text_b: str) -> float:
    """Simple text-based similarity using word overlap (Jaccard).

    Used as fallback when no embeddings are available.
    """
    if not text_a or not text_b:
        return 0.0

    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())

    if not words_a or not words_b:
        return 0.0

    intersection = words_a & words_b
    union = words_a | words_b

    return len(intersection) / len(union)


class MECEValidator:
    """Validate atomic queries for mutual exclusivity."""

    def __init__(self, threshold: float = DUPLICATE_THRESHOLD):
        """Initialize validator.

        Args:
            threshold: Similarity threshold for duplicate detection (default 0.85)
        """
        self.threshold = threshold

    def validate(self, queries: List[AtomicQuery]) -> MECEReport:
        """Validate a list of atomic queries for duplicates.

        Args:
            queries: List of AtomicQuery objects to validate

        Returns:
            MECEReport with duplicate candidates and decisions
        """
        candidates = []
        checked_pairs = set()

        for i, q_a in enumerate(queries):
            for j, q_b in enumerate(queries):
                if i >= j:
                    continue
                pair_key = (q_a.query_id, q_b.query_id)
                if pair_key in checked_pairs:
                    continue
                checked_pairs.add(pair_key)

                similarity = self._compute_similarity(q_a, q_b)

                if similarity >= self.threshold:
                    candidate = DuplicateCandidate(
                        query_a_id=q_a.query_id,
                        query_b_id=q_b.query_id,
                        similarity_score=similarity,
                        decision="merge",
                        merge_reason=f"Cosine similarity {similarity:.3f} exceeds threshold {self.threshold}",
                    )
                    candidates.append(candidate)

        merges = sum(1 for c in candidates if c.decision == "merge")
        kept = sum(1 for c in candidates if c.decision == "keep_both")

        return MECEReport(
            total_queries=len(queries),
            duplicates_found=len(candidates),
            merges_suggested=merges,
            kept_both=kept,
            candidates=candidates,
        )

    def check_new_query(
        self, new_query: AtomicQuery, existing: List[AtomicQuery]
    ) -> List[DuplicateCandidate]:
        """Check if a new query duplicates any existing queries.

        Args:
            new_query: New query to validate
            existing: List of existing queries

        Returns:
            List of duplicate candidates (empty if unique)
        """
        candidates = []
        for existing_q in existing:
            similarity = self._compute_similarity(new_query, existing_q)
            if similarity >= self.threshold:
                candidates.append(DuplicateCandidate(
                    query_a_id=new_query.query_id,
                    query_b_id=existing_q.query_id,
                    similarity_score=similarity,
                    decision="merge",
                    merge_reason=(
                        f"New query is {similarity:.1%} similar to existing '{existing_q.question[:50]}'"
                    ),
                ))
        return candidates

    def _compute_similarity(self, q_a: AtomicQuery, q_b: AtomicQuery) -> float:
        """Compute similarity between two queries.

        Uses embeddings if both available, otherwise falls back to text similarity.
        """
        if q_a.embedding and q_b.embedding:
            return cosine_similarity(q_a.embedding, q_b.embedding)

        # Fallback: text similarity on question text
        return _text_similarity(q_a.question, q_b.question)

    def merge_queries(
        self, q_a: AtomicQuery, q_b: AtomicQuery, keep_a: bool = True
    ) -> AtomicQuery:
        """Merge two duplicate queries into one.

        Args:
            q_a: First query
            q_b: Second query
            keep_a: If True, keep q_a's question; otherwise keep q_b's

        Returns:
            Merged AtomicQuery
        """
        primary = q_a if keep_a else q_b
        secondary = q_b if keep_a else q_a

        # Merge metadata — take union, preferring primary values
        merged_meta = {**secondary.metadata, **primary.metadata}

        # Combine answers if both have them
        if primary.answer and secondary.answer and primary.answer != secondary.answer:
            merged_answer = f"{primary.answer} [{secondary.answer}]"
        else:
            merged_answer = primary.answer or secondary.answer

        return AtomicQuery(
            query_id=primary.query_id,
            question=primary.question,
            answer=merged_answer,
            metadata=merged_meta,
            embedding=primary.embedding,
        )
