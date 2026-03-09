"""
Staleness Detection and Auto-Expiry — Detect outdated facts in knowledge base.

Implements:
- Domain-specific expiry windows (finance: 365d, health: 180d, career: 730d, etc.)
- Staleness check against stored expiry_date metadata
- Review queue generation for user verification
- User response handling (still_valid / update / delete)
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


# Domain-specific expiry in days (from spec)
EXPIRY_DAYS_BY_DOMAIN: Dict[str, int] = {
    "finance": 365,       # salary, savings
    "health": 180,        # weight, fitness
    "career": 730,        # role, company
    "relationships": 365,
    "personal_growth": 1825,  # identity/values — 5 years
    "memory": 1825,
}

DEFAULT_EXPIRY_DAYS = 365


@dataclass
class StaleDocument:
    """A document flagged as potentially outdated."""

    doc_id: str
    domain: str
    content_preview: str  # First 100 chars
    stored_at: str        # ISO8601 when originally stored
    expiry_date: str      # ISO8601 expiry date
    days_overdue: int     # How many days past expiry
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "domain": self.domain,
            "content_preview": self.content_preview,
            "stored_at": self.stored_at,
            "expiry_date": self.expiry_date,
            "days_overdue": self.days_overdue,
            "metadata": self.metadata,
        }


@dataclass
class StalenessCheckResult:
    """Result of a staleness check run."""

    checked_at: str
    total_checked: int
    stale_count: int
    stale_documents: List[StaleDocument] = field(default_factory=list)
    by_domain: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checked_at": self.checked_at,
            "total_checked": self.total_checked,
            "stale_count": self.stale_count,
            "stale_documents": [d.to_dict() for d in self.stale_documents],
            "by_domain": self.by_domain,
        }


class StalenessDetector:
    """Detects and manages outdated facts in the knowledge base."""

    def __init__(self, collection=None):
        """
        Args:
            collection: ChromaDB collection (can be None for testing)
        """
        self.collection = collection

    def compute_expiry_date(self, domain: str, stored_at: str) -> str:
        """
        Compute expiry date for a document based on its domain.

        Args:
            domain: Knowledge domain (career, finance, health, etc.)
            stored_at: ISO8601 date when document was stored

        Returns:
            ISO8601 expiry date string
        """
        expiry_days = EXPIRY_DAYS_BY_DOMAIN.get(domain, DEFAULT_EXPIRY_DAYS)
        try:
            stored_dt = datetime.fromisoformat(stored_at)
        except (ValueError, TypeError):
            stored_dt = datetime.now()
        expiry_dt = stored_dt + timedelta(days=expiry_days)
        return expiry_dt.isoformat()

    def is_stale(self, expiry_date: str, reference_date: Optional[str] = None) -> Tuple[bool, int]:
        """
        Check if a document is stale.

        Args:
            expiry_date: ISO8601 expiry date
            reference_date: ISO8601 date to compare against (defaults to now)

        Returns:
            (is_stale, days_overdue) tuple
        """
        try:
            expiry_dt = datetime.fromisoformat(expiry_date)
            ref_dt = datetime.fromisoformat(reference_date) if reference_date else datetime.now()
            if ref_dt > expiry_dt:
                days_overdue = (ref_dt - expiry_dt).days
                return True, days_overdue
            return False, 0
        except (ValueError, TypeError):
            return False, 0

    def check_collection_for_stale(
        self,
        reference_date: Optional[str] = None,
        limit: int = 1000,
    ) -> StalenessCheckResult:
        """
        Check ChromaDB collection for stale documents.

        Args:
            reference_date: Date to check against (defaults to now)
            limit: Max documents to check

        Returns:
            StalenessCheckResult with all stale documents found
        """
        checked_at = datetime.now().isoformat()
        stale_docs = []
        domain_counts: Dict[str, int] = {}

        if not self.collection:
            logger.warning("No collection configured — cannot check staleness")
            return StalenessCheckResult(
                checked_at=checked_at,
                total_checked=0,
                stale_count=0,
            )

        try:
            all_docs = self.collection.get(limit=limit)
        except Exception as e:
            logger.error(f"Failed to fetch documents: {e}")
            return StalenessCheckResult(
                checked_at=checked_at,
                total_checked=0,
                stale_count=0,
            )

        ids = all_docs.get("ids", [])
        documents = all_docs.get("documents", []) or [""] * len(ids)
        metadatas = all_docs.get("metadatas", []) or [{}] * len(ids)

        total_checked = len(ids)

        for doc_id, text, meta in zip(ids, documents, metadatas):
            if not meta:
                meta = {}
            domain = meta.get("domain", "")
            expiry_date = meta.get("expiry_date", "")
            stored_at = meta.get("date", meta.get("stored_at", ""))

            if not expiry_date:
                # Compute from stored_at if not present
                if stored_at and domain:
                    expiry_date = self.compute_expiry_date(domain, stored_at)
                else:
                    continue  # Can't determine expiry

            stale, days_overdue = self.is_stale(expiry_date, reference_date)
            if stale:
                stale_doc = StaleDocument(
                    doc_id=doc_id,
                    domain=domain,
                    content_preview=(text or "")[:100],
                    stored_at=stored_at or "",
                    expiry_date=expiry_date,
                    days_overdue=days_overdue,
                    metadata=meta,
                )
                stale_docs.append(stale_doc)
                domain_counts[domain] = domain_counts.get(domain, 0) + 1

        logger.info(f"Staleness check: {len(stale_docs)}/{total_checked} stale documents found")
        return StalenessCheckResult(
            checked_at=checked_at,
            total_checked=total_checked,
            stale_count=len(stale_docs),
            stale_documents=stale_docs,
            by_domain=domain_counts,
        )

    def format_review_prompt(self, stale_docs: List[StaleDocument]) -> str:
        """
        Format Hinglish review prompt for stale documents.

        Returns:
            Formatted review prompt string
        """
        if not stale_docs:
            return "Sab information up-to-date hai! ✅"

        lines = [
            "⏰ Kuch purani information verify karni hai:",
            "",
        ]

        for doc in stale_docs[:5]:  # Show max 5 at a time
            year = doc.stored_at[:4] if len(doc.stored_at) >= 4 else "pehle"
            preview = doc.content_preview[:60] + "..." if len(doc.content_preview) > 60 else doc.content_preview
            lines.append(f"  📋 [{year}] {preview}")

        lines.extend([
            "",
            "Options:",
            "  [S] Still valid — aab bhi sahi hai",
            "  [U] Update — nayi information do",
            "  [D] Delete — yeh relevant nahi raha",
        ])

        return "\n".join(lines)

    def handle_user_response(
        self,
        doc_id: str,
        response: str,
        new_value: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Handle user's review response for a stale document.

        Args:
            doc_id: Document ID
            response: "still_valid", "update", or "delete"
            new_value: New content if response is "update"

        Returns:
            Action dict with status and next steps
        """
        response = response.lower().strip()

        if response in ("still_valid", "s", "valid"):
            return {
                "action": "reset_expiry",
                "doc_id": doc_id,
                "message": "Expiry date reset for another cycle.",
                "status": "ok",
            }
        elif response in ("update", "u") and new_value:
            return {
                "action": "update_content",
                "doc_id": doc_id,
                "new_value": new_value,
                "message": "Document will be updated and conflict-checked.",
                "status": "ok",
            }
        elif response in ("delete", "d"):
            return {
                "action": "archive",
                "doc_id": doc_id,
                "message": "Document marked as archived (soft delete, audit trail preserved).",
                "status": "ok",
            }
        else:
            return {
                "action": "unknown",
                "doc_id": doc_id,
                "message": f"Unknown response: {response!r}",
                "status": "error",
            }

    def get_expiry_config(self) -> Dict[str, int]:
        """Return current expiry configuration by domain."""
        return dict(EXPIRY_DAYS_BY_DOMAIN)
