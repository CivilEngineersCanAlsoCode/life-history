"""
Small Talk Passive Capture — Extract and queue claims from casual conversation.

Problem: In small talk mode, users mention facts, metrics, dates, and decisions
casually without intending to formally record them. These are valuable atoms
that should be offered for recording — but never intrusively repeated.

Features:
- Claim detection: regex + keyword patterns for facts/metrics/dates/decisions/people
- Deduplication: SHA-256 fingerprint per normalized claim, never surface twice
- Surface prompt: "Tumne kaha ki X — isko record karun?"
- Weekly review queue: claims pending confirmation, auto-expires after 7 days
- Once-per-claim: if user says no, never ask again for that claim

Claim types detected:
- METRIC: numbers with units/percentages ("CSAT 94%", "₹50L", "10,000 users")
- FACT: subject-verb-object patterns ("I joined X", "We launched Y")
- DATE: specific dates or time anchors ("April 2022", "last quarter")
- DECISION: decision keywords ("decided to", "chose to", "going to")
- PERSON: names mentioned with context ("talked to Rahul from Google")
"""

from __future__ import annotations

import hashlib
import re
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------- Claim Detection Patterns ----------

_METRIC_PATTERNS = [
    r"\b\d+[\.,]?\d*\s*%",                       # 94%, 12.5%
    r"\b\d+[\.,]?\d*\s*(L|Cr|K|M|B)\b",          # ₹50L, 10K, 2M
    r"\b\d{4,}[\.,]?\d*\b",                       # 10000, 1,00,000
    r"\b\d+\s+(users?|customers?|queries?|requests?|clients?|employees?)\b",
    r"\bCSAT\b.*\d+",                              # CSAT 94
    r"\bNPS\b.*\d+",                               # NPS 72
    r"\bARR\b.*\d+",                               # ARR mention
    r"\d+\s*(hours?|days?|weeks?|months?|years?)\s*(per|a)\b",  # 40 hours per week
]

_FACT_PATTERNS = [
    r"\bI (joined|started|left|quit|resigned|got (offered|promoted|hired))\b",
    r"\bwe (launched|shipped|built|deployed|created|released)\b",
    r"\bI (built|created|designed|led|managed|owned|ran)\b",
    r"\bmy (salary|CTC|package|compensation|role|title)\b",
    r"\b(got|received|accepted|rejected)\b.{3,30}\b(offer|promotion|award|raise)\b",
]

_DATE_PATTERNS = [
    r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
    r"\bQ[1-4]\s+\d{4}\b",                        # Q3 2023
    r"\b(last|this|next)\s+(week|month|quarter|year)\b",
    r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",               # 01/03/2024
    r"\b(FY|CY)\s*\d{2,4}\b",                     # FY24, CY2024
    r"\b\d+ (months?|years?) ago\b",               # 6 months ago
]

_DECISION_PATTERNS = [
    r"\b(decided|choosing|chose|planning|going)\s+to\b",
    r"\bI (will|won't|am|am not|am going to)\b",
    r"\b(accepted|rejected|declined|postponed)\b",
    r"\b(committed to|agreed to|signed up for)\b",
]

_PERSON_PATTERNS = [
    r"\btalked to\b.{3,30}\b(from|at|of)\b",
    r"\bmet\b.{3,30}\b(from|at|of)\b",
    r"\b[A-Z][a-z]+ [A-Z][a-z]+\b.{0,20}\b(from|at|of)\b",  # First Last from/at
    r"\b(my|our)\s+(manager|lead|mentor|CEO|CTO|VP|director|boss)\b",
]

_PATTERN_MAP = {
    "metric": _METRIC_PATTERNS,
    "fact": _FACT_PATTERNS,
    "date": _DATE_PATTERNS,
    "decision": _DECISION_PATTERNS,
    "person": _PERSON_PATTERNS,
}

# Minimum text length to bother extracting claims
_MIN_CLAIM_LENGTH = 15


# ---------- Data Classes ----------

@dataclass
class DetectedClaim:
    """A claim detected in a small talk message."""
    claim_type: str         # metric / fact / date / decision / person
    raw_text: str           # Original text span
    source_message: str     # Full message it was found in
    confidence: float = 0.6
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())
    fingerprint: str = ""   # SHA-256 of normalized text

    def __post_init__(self):
        if not self.fingerprint:
            self.fingerprint = _fingerprint(self.raw_text)

    def surface_prompt(self) -> str:
        """Generate the 'tumne kaha ki X — isko record karun?' prompt."""
        snippet = self.raw_text[:80] + ("..." if len(self.raw_text) > 80 else "")
        return f'Tumne kaha ki "{snippet}" — isko record karun?'

    def to_dict(self) -> Dict:
        return {
            "claim_type": self.claim_type,
            "raw_text": self.raw_text,
            "source_message": self.source_message,
            "confidence": self.confidence,
            "detected_at": self.detected_at,
            "fingerprint": self.fingerprint,
        }


@dataclass
class ReviewQueueItem:
    """A claim pending user confirmation in the weekly review queue."""
    claim: DetectedClaim
    added_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: str = ""
    status: str = "pending"   # pending / confirmed / rejected

    def __post_init__(self):
        if not self.expires_at:
            expiry = datetime.now() + timedelta(days=7)
            self.expires_at = expiry.isoformat()

    @property
    def is_expired(self) -> bool:
        try:
            return datetime.now() > datetime.fromisoformat(self.expires_at)
        except (ValueError, TypeError):
            return False

    def to_dict(self) -> Dict:
        return {
            "claim": self.claim.to_dict(),
            "added_at": self.added_at,
            "expires_at": self.expires_at,
            "status": self.status,
        }


# ---------- Helpers ----------

def _fingerprint(text: str) -> str:
    """Stable SHA-256 fingerprint of normalized claim text."""
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


# ---------- Core Classes ----------

class ClaimDetector:
    """
    Detect factual claims in small talk messages.

    Applies regex patterns to extract metrics, facts, dates, decisions,
    and people mentions from casual conversation.
    """

    def detect(self, message: str) -> List[DetectedClaim]:
        """
        Detect all claim types in a message.

        Args:
            message: User's casual message

        Returns:
            List of DetectedClaim (may be empty)
        """
        if not message or len(message) < _MIN_CLAIM_LENGTH:
            return []

        claims: List[DetectedClaim] = []
        seen_fingerprints = set()

        for claim_type, patterns in _PATTERN_MAP.items():
            for pattern in patterns:
                for match in re.finditer(pattern, message, re.IGNORECASE):
                    raw = match.group(0).strip()
                    if len(raw) < 3:
                        continue
                    fp = _fingerprint(raw)
                    if fp in seen_fingerprints:
                        continue
                    seen_fingerprints.add(fp)
                    claims.append(DetectedClaim(
                        claim_type=claim_type,
                        raw_text=raw,
                        source_message=message,
                    ))

        return claims

    def detect_types(self, message: str) -> Dict[str, List[str]]:
        """
        Return detected claim texts grouped by type.

        Args:
            message: User's message

        Returns:
            Dict mapping claim_type → list of raw text matches
        """
        claims = self.detect(message)
        result: Dict[str, List[str]] = {}
        for c in claims:
            result.setdefault(c.claim_type, []).append(c.raw_text)
        return result


class PassiveCaptureEngine:
    """
    Manages the full passive capture lifecycle:
    1. Detect claims in new small talk messages
    2. Deduplicate against already-seen fingerprints
    3. Queue new unique claims for user confirmation
    4. Surface one pending claim at a time
    5. Handle user accept/reject
    6. Weekly review: expire stale items

    Usage:
        engine = PassiveCaptureEngine()

        # Called after each small talk message
        new_claims = engine.process_message(user_message)
        if engine.has_pending_prompts():
            prompt = engine.next_prompt()    # Show to user
    """

    def __init__(self):
        self._detector = ClaimDetector()
        self._seen_fingerprints: set = set()     # Never surface these again
        self._review_queue: List[ReviewQueueItem] = []

    @property
    def queue_size(self) -> int:
        """Number of pending (non-expired) items in review queue."""
        return len([i for i in self._review_queue if i.status == "pending" and not i.is_expired])

    def process_message(self, message: str) -> List[DetectedClaim]:
        """
        Process a small talk message: detect and queue new unique claims.

        Args:
            message: User's casual message

        Returns:
            List of newly detected (not previously seen) claims added to queue
        """
        claims = self._detector.detect(message)
        new_claims = []

        for claim in claims:
            if claim.fingerprint in self._seen_fingerprints:
                logger.debug(f"Skipping duplicate claim: {claim.raw_text[:40]}")
                continue
            # New unique claim — add to queue
            self._seen_fingerprints.add(claim.fingerprint)
            item = ReviewQueueItem(claim=claim)
            self._review_queue.append(item)
            new_claims.append(claim)
            logger.info(f"New claim queued ({claim.claim_type}): {claim.raw_text[:60]}")

        return new_claims

    def has_pending_prompts(self) -> bool:
        """True if there are non-expired pending claims to surface."""
        return self.queue_size > 0

    def next_prompt(self) -> Optional[str]:
        """
        Get the surface prompt for the next pending claim.

        Returns:
            "Tumne kaha ki X — isko record karun?" or None if no pending.
        """
        for item in self._review_queue:
            if item.status == "pending" and not item.is_expired:
                return item.claim.surface_prompt()
        return None

    def next_pending_claim(self) -> Optional[ReviewQueueItem]:
        """Return the next pending ReviewQueueItem (for programmatic use)."""
        for item in self._review_queue:
            if item.status == "pending" and not item.is_expired:
                return item
        return None

    def confirm(self, fingerprint: str) -> bool:
        """
        Mark a claim as confirmed (user said yes, record it).

        Args:
            fingerprint: Claim fingerprint to confirm

        Returns:
            True if found and updated, False if not found
        """
        for item in self._review_queue:
            if item.claim.fingerprint == fingerprint and item.status == "pending":
                item.status = "confirmed"
                logger.info(f"Claim confirmed: {item.claim.raw_text[:60]}")
                return True
        return False

    def reject(self, fingerprint: str) -> bool:
        """
        Mark a claim as rejected (user said no, never ask again).

        Args:
            fingerprint: Claim fingerprint to reject

        Returns:
            True if found and updated, False if not found
        """
        for item in self._review_queue:
            if item.claim.fingerprint == fingerprint and item.status == "pending":
                item.status = "rejected"
                logger.info(f"Claim rejected: {item.claim.raw_text[:60]}")
                return True
        return False

    def expire_stale(self) -> int:
        """
        Remove expired pending items from queue.

        Returns:
            Number of items expired
        """
        expired = 0
        for item in self._review_queue:
            if item.status == "pending" and item.is_expired:
                item.status = "rejected"  # Treat as soft-rejected
                expired += 1
        if expired:
            logger.info(f"Expired {expired} stale pending claims")
        return expired

    def get_weekly_review(self) -> List[ReviewQueueItem]:
        """
        Return all pending (non-expired) items for weekly review.

        Returns:
            List of ReviewQueueItem with status='pending'
        """
        self.expire_stale()
        return [i for i in self._review_queue if i.status == "pending"]

    def get_confirmed(self) -> List[ReviewQueueItem]:
        """Return all confirmed claims (ready for ChromaDB ingestion)."""
        return [i for i in self._review_queue if i.status == "confirmed"]

    def stats(self) -> Dict[str, int]:
        """Return queue statistics."""
        return {
            "total": len(self._review_queue),
            "pending": sum(1 for i in self._review_queue if i.status == "pending"),
            "confirmed": sum(1 for i in self._review_queue if i.status == "confirmed"),
            "rejected": sum(1 for i in self._review_queue if i.status == "rejected"),
            "expired": sum(
                1 for i in self._review_queue
                if i.status == "pending" and i.is_expired
            ),
        }
