"""
Merge/Equivalence (ME) check for detecting and merging duplicate documents.

Identifies duplicate documents using cosine similarity and manages merging of
equivalent content to maintain a clean, deduplicated knowledge base.
"""

from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import math


class MergeStatus(Enum):
    """Status of merge operation."""

    PENDING = "pending"  # Duplicates detected, awaiting decision
    APPROVED = "approved"  # Merge approved
    REJECTED = "rejected"  # Marked as not duplicates
    MERGED = "merged"  # Successfully merged
    FAILED = "failed"  # Merge failed


@dataclass
class DuplicateCandidate:
    """Potential duplicate pair."""

    doc_id_1: str
    doc_id_2: str
    similarity_score: float  # 0-1
    overlap_percentage: float  # % of common content
    merge_confidence: float  # 0-1, confidence in merge recommendation


@dataclass
class MergeDecision:
    """Decision to merge two documents."""

    merge_id: str
    doc_id_1: str
    doc_id_2: str
    primary_doc_id: str  # Which document to keep
    status: MergeStatus
    similarity_score: float
    reason: str  # Why merging
    merged_content: str = ""  # Combined content if merged
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "merge_id": self.merge_id,
            "doc_id_1": self.doc_id_1,
            "doc_id_2": self.doc_id_2,
            "primary_doc_id": self.primary_doc_id,
            "status": self.status.value,
            "similarity_score": self.similarity_score,
            "reason": self.reason,
            "merged_content": self.merged_content[:100] + "..."
            if len(self.merged_content) > 100
            else self.merged_content,
            "created_at": self.created_at,
        }


class MergeEquivalenceValidator:
    """Detect and manage document merging."""

    # Minimum cosine similarity for considering documents equivalent
    SIMILARITY_THRESHOLD = 0.85

    # Similarity tiers
    VERY_HIGH_SIMILARITY = 0.95  # Likely duplicates
    HIGH_SIMILARITY = 0.85  # Probable duplicates
    MEDIUM_SIMILARITY = 0.7  # Possibly related
    LOW_SIMILARITY = 0.5  # Loosely related

    def __init__(self):
        """Initialize ME validator."""
        self.documents: Dict[str, str] = {}  # doc_id -> content
        self.duplicates: List[DuplicateCandidate] = []
        self.merge_decisions: Dict[str, MergeDecision] = {}
        self.merge_history: List[MergeDecision] = []
        self.merged_mapping: Dict[str, str] = {}  # old_doc_id -> new_doc_id

    def add_document(self, doc_id: str, content: str) -> None:
        """Add document to collection."""
        self.documents[doc_id] = content

    def detect_duplicates(self) -> List[DuplicateCandidate]:
        """Detect potential duplicate documents."""
        self.duplicates = []
        doc_ids = list(self.documents.keys())

        # Compare all document pairs
        for i, doc_id_1 in enumerate(doc_ids):
            for doc_id_2 in doc_ids[i + 1 :]:
                content_1 = self.documents[doc_id_1]
                content_2 = self.documents[doc_id_2]

                # Calculate similarity
                similarity = self._calculate_cosine_similarity(content_1, content_2)

                # Flag if above threshold
                if similarity >= self.SIMILARITY_THRESHOLD:
                    overlap = self._calculate_overlap_percentage(content_1, content_2)
                    confidence = self._calculate_merge_confidence(
                        similarity, overlap, content_1, content_2
                    )

                    candidate = DuplicateCandidate(
                        doc_id_1=doc_id_1,
                        doc_id_2=doc_id_2,
                        similarity_score=similarity,
                        overlap_percentage=overlap,
                        merge_confidence=confidence,
                    )
                    self.duplicates.append(candidate)

        return self.duplicates

    def _calculate_cosine_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts."""
        # Normalize texts
        text1 = self._normalize_text(text1)
        text2 = self._normalize_text(text2)

        # Build term frequency vectors
        vector1 = self._build_term_vector(text1)
        vector2 = self._build_term_vector(text2)

        # Get all unique terms
        all_terms = set(vector1.keys()) | set(vector2.keys())

        if not all_terms:
            return 0.0

        # Calculate dot product
        dot_product = sum(
            vector1.get(term, 0) * vector2.get(term, 0) for term in all_terms
        )

        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(v * v for v in vector1.values()))
        magnitude2 = math.sqrt(sum(v * v for v in vector2.values()))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        # Cosine similarity
        return dot_product / (magnitude1 * magnitude2)

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        # Convert to lowercase
        text = text.lower()
        # Remove special characters except spaces
        text = re.sub(r"[^\w\s]", " ", text)
        # Remove extra whitespace
        text = " ".join(text.split())
        return text

    def _build_term_vector(self, text: str) -> Dict[str, float]:
        """Build term frequency vector from text."""
        words = text.split()
        vector = {}

        for word in words:
            if len(word) > 2:  # Ignore very short words
                vector[word] = vector.get(word, 0) + 1

        # Normalize by document length
        if words:
            for key in vector:
                vector[key] = vector[key] / len(words)

        return vector

    def _calculate_overlap_percentage(self, text1: str, text2: str) -> float:
        """Calculate percentage of overlapping content."""
        norm1 = self._normalize_text(text1)
        norm2 = self._normalize_text(text2)

        words1 = set(norm1.split())
        words2 = set(norm2.split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _calculate_merge_confidence(
        self, similarity: float, overlap: float, text1: str, text2: str
    ) -> float:
        """Calculate confidence in merge recommendation."""
        # Base confidence from similarity
        confidence = similarity * 0.5 + overlap * 0.3

        # Length similarity bonus
        len1, len2 = len(text1), len(text2)
        max_len = max(len1, len2)
        min_len = min(len1, len2)
        if max_len > 0:
            length_ratio = min_len / max_len
            confidence += length_ratio * 0.2

        return min(1.0, confidence)

    def propose_merge(
        self,
        doc_id_1: str,
        doc_id_2: str,
        primary_doc_id: Optional[str] = None,
    ) -> Tuple[Optional[MergeDecision], Optional[str]]:
        """Propose merging two documents."""
        if doc_id_1 not in self.documents:
            return None, f"Document {doc_id_1} not found"
        if doc_id_2 not in self.documents:
            return None, f"Document {doc_id_2} not found"

        # Calculate similarity
        similarity = self._calculate_cosine_similarity(
            self.documents[doc_id_1], self.documents[doc_id_2]
        )

        if similarity < self.SIMILARITY_THRESHOLD:
            return None, f"Similarity {similarity:.2f} below threshold {self.SIMILARITY_THRESHOLD}"

        # Determine primary document
        if not primary_doc_id:
            primary_doc_id = (
                doc_id_1
                if len(self.documents[doc_id_1]) >= len(self.documents[doc_id_2])
                else doc_id_2
            )

        merge_id = f"me_{len(self.merge_decisions):04d}"

        decision = MergeDecision(
            merge_id=merge_id,
            doc_id_1=doc_id_1,
            doc_id_2=doc_id_2,
            primary_doc_id=primary_doc_id,
            status=MergeStatus.PENDING,
            similarity_score=similarity,
            reason=f"Duplicate content detected (similarity: {similarity:.2f})",
        )

        self.merge_decisions[merge_id] = decision
        return decision, None

    def approve_merge(self, merge_id: str) -> Tuple[Optional[MergeDecision], Optional[str]]:
        """Approve and execute merge."""
        decision = self.merge_decisions.get(merge_id)
        if not decision:
            return None, f"Merge decision {merge_id} not found"

        if decision.status != MergeStatus.PENDING:
            return None, f"Merge already {decision.status.value}"

        # Merge content
        primary_content = self.documents[decision.primary_doc_id]
        secondary_content = self.documents[
            decision.doc_id_2
            if decision.primary_doc_id == decision.doc_id_1
            else decision.doc_id_1
        ]
        secondary_id = (
            decision.doc_id_2
            if decision.primary_doc_id == decision.doc_id_1
            else decision.doc_id_1
        )

        # Combine content (keep primary, note secondary)
        merged_content = f"{primary_content}\n[MERGED FROM: {secondary_id}]\n{secondary_content}"

        # Update decision
        decision.status = MergeStatus.MERGED
        decision.merged_content = merged_content

        # Update mapping
        self.merged_mapping[secondary_id] = decision.primary_doc_id

        # Update documents
        self.documents[decision.primary_doc_id] = merged_content
        del self.documents[secondary_id]

        self.merge_history.append(decision)

        return decision, None

    def reject_merge(self, merge_id: str, reason: str = "") -> Tuple[Optional[MergeDecision], Optional[str]]:
        """Reject merge decision."""
        decision = self.merge_decisions.get(merge_id)
        if not decision:
            return None, f"Merge decision {merge_id} not found"

        decision.status = MergeStatus.REJECTED
        decision.reason = reason or "Marked as not duplicates"

        return decision, None

    def get_merge_decision(self, merge_id: str) -> Optional[MergeDecision]:
        """Get specific merge decision."""
        return self.merge_decisions.get(merge_id)

    def get_pending_merges(self) -> List[MergeDecision]:
        """Get all pending merge decisions."""
        return [
            decision
            for decision in self.merge_decisions.values()
            if decision.status == MergeStatus.PENDING
        ]

    def get_merge_mapping(self) -> Dict[str, str]:
        """Get mapping of merged document IDs."""
        return self.merged_mapping.copy()

    def batch_detect_and_propose(self) -> Tuple[List[MergeDecision], Optional[str]]:
        """Detect duplicates and propose merges in batch."""
        # Detect duplicates
        duplicates = self.detect_duplicates()

        # Propose merges for all detected duplicates
        decisions = []
        for candidate in duplicates:
            decision, _ = self.propose_merge(
                candidate.doc_id_1, candidate.doc_id_2
            )
            if decision:
                decisions.append(decision)

        return decisions, None

    def export_merge_decision(self, merge_id: str) -> Optional[Dict[str, Any]]:
        """Export merge decision."""
        decision = self.get_merge_decision(merge_id)
        if not decision:
            return None
        return decision.to_dict()

    def export_all_decisions(self) -> List[Dict[str, Any]]:
        """Export all merge decisions."""
        return [decision.to_dict() for decision in self.merge_history]

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about merge operations."""
        return {
            "total_documents": len(self.documents),
            "total_duplicates_detected": len(self.duplicates),
            "total_merges_proposed": len(self.merge_decisions),
            "merges_completed": sum(
                1 for d in self.merge_decisions.values()
                if d.status == MergeStatus.MERGED
            ),
            "merges_rejected": sum(
                1 for d in self.merge_decisions.values()
                if d.status == MergeStatus.REJECTED
            ),
            "merges_pending": len(self.get_pending_merges()),
            "merged_documents": len(self.merged_mapping),
            "avg_similarity": (
                sum(d.similarity_score for d in self.duplicates) / len(self.duplicates)
                if self.duplicates
                else 0.0
            ),
        }
