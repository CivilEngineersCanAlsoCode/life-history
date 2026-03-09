"""
Schema monitor for tracking custom field promotion candidates.

Monitors custom field usage across documents and recommends fields
for promotion to standard schema when they reach 20+ usage threshold.
"""

from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class PromotionStatus(Enum):
    """Status of a field promotion candidate."""
    MONITORING = "monitoring"
    READY = "ready"
    PROMOTED = "promoted"
    ARCHIVED = "archived"


@dataclass
class FieldCandidate:
    """A candidate for schema promotion."""

    field_name: str
    usage_count: int
    first_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    last_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    documents_using: Set[str] = field(default_factory=set)
    status: PromotionStatus = PromotionStatus.MONITORING
    promotion_date: Optional[str] = None
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "field_name": self.field_name,
            "usage_count": self.usage_count,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "documents_using": list(self.documents_using),
            "status": self.status.value,
            "promotion_date": self.promotion_date,
            "notes": self.notes,
        }

    def get_promotion_score(self) -> float:
        """
        Calculate promotion score (0-100).

        Factors:
        - Usage count (weight: 0.6)
        - Document diversity (weight: 0.3)
        - Age/maturity (weight: 0.1)
        """
        # Usage score (0-60)
        usage_score = min(60, self.usage_count / 20 * 60)

        # Document diversity score (0-30)
        diversity_score = min(30, len(self.documents_using) / 10 * 30)

        # Age score (0-10) - older fields get higher score
        first_seen_dt = datetime.fromisoformat(self.first_seen)
        age_days = (datetime.now() - first_seen_dt).days
        age_score = min(10, age_days / 30 * 10)

        return usage_score + diversity_score + age_score


class SchemaMonitor:
    """Monitor custom fields for schema promotion."""

    PROMOTION_THRESHOLD = 20  # Usage count threshold for promotion readiness
    MIN_UNIQUE_DOCUMENTS = 5  # Minimum unique documents using field
    ARCHIVE_THRESHOLD = 90  # Days before archiving inactive fields

    def __init__(self):
        """Initialize schema monitor."""
        self.candidates: Dict[str, FieldCandidate] = {}
        self.promotion_history: List[Dict[str, Any]] = []

    def schema_monitor(
        self,
        field_name: str,
        usage_count: int,
        document_ids: Set[str],
        notes: str = "",
    ) -> FieldCandidate:
        """
        Monitor a custom field for potential promotion.

        Args:
            field_name: Name of the field
            usage_count: How many times it appears
            document_ids: Set of documents using this field
            notes: Additional context/notes

        Returns:
            FieldCandidate object
        """
        # Check if already monitoring
        if field_name in self.candidates:
            candidate = self.candidates[field_name]
            candidate.usage_count = usage_count
            candidate.documents_using = document_ids
            candidate.last_seen = datetime.now().isoformat()

            # Check if ready for promotion
            if (
                usage_count >= self.PROMOTION_THRESHOLD
                and len(document_ids) >= self.MIN_UNIQUE_DOCUMENTS
                and candidate.status == PromotionStatus.MONITORING
            ):
                candidate.status = PromotionStatus.READY
        else:
            # Create new candidate
            candidate = FieldCandidate(
                field_name=field_name,
                usage_count=usage_count,
                documents_using=document_ids,
                notes=notes,
            )

            # Check if ready immediately
            if (
                usage_count >= self.PROMOTION_THRESHOLD
                and len(document_ids) >= self.MIN_UNIQUE_DOCUMENTS
            ):
                candidate.status = PromotionStatus.READY

            self.candidates[field_name] = candidate

        return candidate

    def get_candidates(
        self,
        status: Optional[PromotionStatus] = None,
    ) -> List[FieldCandidate]:
        """Get candidates, optionally filtered by status."""
        candidates = list(self.candidates.values())

        if status:
            candidates = [c for c in candidates if c.status == status]

        return sorted(
            candidates,
            key=lambda c: c.get_promotion_score(),
            reverse=True,
        )

    def get_ready_for_promotion(self) -> List[FieldCandidate]:
        """Get fields ready for schema promotion (20+ usage, 5+ documents)."""
        return self.get_candidates(status=PromotionStatus.READY)

    def promote_field(
        self,
        field_name: str,
        promoted_to: str = "standard_schema",
    ) -> Tuple[bool, Optional[str]]:
        """
        Promote a custom field to standard schema.

        Args:
            field_name: Field to promote
            promoted_to: Where it's being promoted to

        Returns:
            (success, error_message)
        """
        if field_name not in self.candidates:
            return False, f"Field '{field_name}' not found"

        candidate = self.candidates[field_name]

        if candidate.status == PromotionStatus.PROMOTED:
            return False, f"Field '{field_name}' already promoted"

        if candidate.usage_count < self.PROMOTION_THRESHOLD:
            return False, f"Field not ready (usage: {candidate.usage_count}, need: {self.PROMOTION_THRESHOLD})"

        # Mark as promoted
        candidate.status = PromotionStatus.PROMOTED
        candidate.promotion_date = datetime.now().isoformat()

        # Record in history
        self.promotion_history.append({
            "field_name": field_name,
            "promoted_to": promoted_to,
            "promotion_date": candidate.promotion_date,
            "usage_count": candidate.usage_count,
            "documents_using": len(candidate.documents_using),
        })

        return True, None

    def archive_field(
        self,
        field_name: str,
        reason: str = "inactive",
    ) -> Tuple[bool, Optional[str]]:
        """Archive an inactive field."""
        if field_name not in self.candidates:
            return False, f"Field '{field_name}' not found"

        candidate = self.candidates[field_name]
        candidate.status = PromotionStatus.ARCHIVED
        candidate.notes = f"{candidate.notes} [ARCHIVED: {reason}]"

        return True, None

    def get_promotion_candidates_summary(self) -> Dict[str, Any]:
        """Get summary of promotion candidates by status."""
        summary = {
            "monitoring": [],
            "ready": [],
            "promoted": [],
            "archived": [],
        }

        for candidate in self.candidates.values():
            status_key = candidate.status.value
            summary[status_key].append({
                "field_name": candidate.field_name,
                "usage_count": candidate.usage_count,
                "documents": len(candidate.documents_using),
                "score": candidate.get_promotion_score(),
            })

        # Sort by score
        for key in summary:
            summary[key] = sorted(
                summary[key],
                key=lambda x: x["score"],
                reverse=True,
            )

        return summary

    def get_promotion_history(self) -> List[Dict[str, Any]]:
        """Get history of promoted fields."""
        return self.promotion_history

    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        if not self.candidates:
            return {
                "total_candidates": 0,
                "monitoring": 0,
                "ready": 0,
                "promoted": 0,
                "archived": 0,
                "promotion_rate": 0.0,
            }

        statuses = {}
        for candidate in self.candidates.values():
            status = candidate.status.value
            statuses[status] = statuses.get(status, 0) + 1

        promoted = statuses.get("promoted", 0)
        total = len(self.candidates)
        promotion_rate = (promoted / total * 100) if total > 0 else 0

        return {
            "total_candidates": total,
            "monitoring": statuses.get("monitoring", 0),
            "ready": statuses.get("ready", 0),
            "promoted": promoted,
            "archived": statuses.get("archived", 0),
            "promotion_rate": promotion_rate,
        }

    def export_candidates(self) -> List[Dict[str, Any]]:
        """Export all candidates."""
        return sorted(
            [c.to_dict() for c in self.candidates.values()],
            key=lambda x: x["usage_count"],
            reverse=True,
        )

    def get_field_promotion_timeline(self) -> Dict[str, Any]:
        """Get timeline of field promotions."""
        timeline = {}

        for entry in self.promotion_history:
            date = entry["promotion_date"].split("T")[0]  # Extract date
            if date not in timeline:
                timeline[date] = []

            timeline[date].append({
                "field": entry["field_name"],
                "usage_count": entry["usage_count"],
                "documents": entry["documents_using"],
            })

        return dict(sorted(timeline.items()))

    def get_promotion_readiness(self) -> Dict[str, Any]:
        """Detailed readiness assessment for all candidates."""
        readiness = {}

        for field_name, candidate in self.candidates.items():
            usage_pct = min(100, candidate.usage_count / self.PROMOTION_THRESHOLD * 100)
            doc_pct = min(
                100,
                len(candidate.documents_using) / self.MIN_UNIQUE_DOCUMENTS * 100,
            )

            readiness[field_name] = {
                "status": candidate.status.value,
                "usage_readiness": f"{usage_pct:.1f}%",
                "document_readiness": f"{doc_pct:.1f}%",
                "promotion_score": candidate.get_promotion_score(),
                "ready_for_promotion": candidate.status == PromotionStatus.READY,
            }

        return dict(
            sorted(
                readiness.items(),
                key=lambda x: x[1]["promotion_score"],
                reverse=True,
            )
        )
