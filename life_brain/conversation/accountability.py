"""
Accountability partner — extract commitments and follow up on deadlines.

Extracts: "I'll do X by date Y" statements from sessions.
Follows up: "You said March 31 — what happened?"
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, date


# Patterns that signal commitment statements
_COMMITMENT_PATTERNS = [
    r"i(?:'ll| will| am going to| plan to| want to)\s+(.+?)(?:\s+by\s+(.+?))?(?:\.|$)",
    r"(?:by|before|until)\s+([\w\s,]+\d{4}|\w+ \d+|\w+day|\w+ \d+(?:st|nd|rd|th)?),?\s+i(?:'ll| will)\s+(.+?)(?:\.|$)",
    r"i(?:'m| am) going to\s+(.+?)(?:\s+by\s+(.+?))?(?:\.|$)",
    r"(?:need to|have to|must)\s+(.+?)\s+by\s+(.+?)(?:\.|$)",
    r"(?:deadline|due|target)\s+(?:is|:)\s+(.+?)(?:\s+for\s+(.+?))?(?:\.|$)",
]

# Date patterns for deadline extraction
_DATE_PATTERNS = [
    r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?,?\s*\d{0,4}\b",
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
    r"\b(?:next\s+)?(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    r"\b(?:next\s+)?(?:week|month|year)\b",
    r"\b(?:end of|eow|eom|eoy)\b",
    r"\bq[1-4]\s*\d{0,4}\b",
    r"\b\d{4}-\d{2}-\d{2}\b",
]

_COMBINED_DATE = "|".join(f"({p})" for p in _DATE_PATTERNS)


@dataclass
class Commitment:
    """A commitment extracted from a session."""

    commitment_id: str
    session_id: str
    raw_text: str           # Original sentence
    action: str             # What they committed to do
    deadline_text: Optional[str]  # Raw deadline string (e.g., "March 31")
    extracted_at: str = field(default_factory=lambda: datetime.now().isoformat())
    followed_up: bool = False
    status: str = "pending"  # pending, done, missed, extended

    def to_dict(self) -> Dict:
        return {
            "commitment_id": self.commitment_id,
            "session_id": self.session_id,
            "raw_text": self.raw_text,
            "action": self.action,
            "deadline_text": self.deadline_text,
            "extracted_at": self.extracted_at,
            "followed_up": self.followed_up,
            "status": self.status,
        }


def extract_commitments(text: str, session_id: str) -> List[Commitment]:
    """Extract commitment statements from text.

    Args:
        text: Message or session transcript text
        session_id: Session identifier

    Returns:
        List of Commitment objects
    """
    commitments = []
    sentences = _split_sentences(text)

    for sentence in sentences:
        commitment = _try_extract_commitment(sentence, session_id)
        if commitment:
            commitments.append(commitment)

    return commitments


def _split_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    # Split on . ! ? followed by space or end
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]


def _try_extract_commitment(sentence: str, session_id: str) -> Optional[Commitment]:
    """Try to extract a commitment from a single sentence."""
    lower = sentence.lower()

    # Quick filter: must contain commitment-like language
    commitment_signals = [
        "i'll", "i will", "i am going to", "i'm going to",
        "need to", "have to", "must", "plan to", "going to",
        "deadline", "by the end", "before end",
    ]
    if not any(sig in lower for sig in commitment_signals):
        return None

    # Extract deadline if present
    deadline = _extract_deadline(sentence)

    # Extract action (simplified: take text after commitment signal)
    action = _extract_action(sentence)
    if not action or len(action) < 5:
        return None

    import hashlib
    cid = "commit_" + hashlib.md5(f"{session_id}{sentence}".encode()).hexdigest()[:8]

    return Commitment(
        commitment_id=cid,
        session_id=session_id,
        raw_text=sentence,
        action=action.strip(),
        deadline_text=deadline,
    )


def _extract_deadline(sentence: str) -> Optional[str]:
    """Extract deadline text from sentence."""
    # Look for "by <date>" pattern
    by_match = re.search(r"\bby\s+(.{3,30}?)(?:\.|,|$)", sentence, re.IGNORECASE)
    if by_match:
        return by_match.group(1).strip()

    # Look for standalone date patterns
    date_match = re.search(_COMBINED_DATE, sentence, re.IGNORECASE)
    if date_match:
        return date_match.group(0).strip()

    return None


def _extract_action(sentence: str) -> str:
    """Extract the committed action from sentence."""
    # Remove common commitment starters to get the action
    cleaned = re.sub(
        r"^(?:i(?:'ll| will| am going to|'m going to|'m)\s+|need to\s+|have to\s+|must\s+|plan to\s+)",
        "",
        sentence,
        flags=re.IGNORECASE,
    )
    # Remove trailing deadline clause
    cleaned = re.sub(r"\s+by\s+.+$", "", cleaned, flags=re.IGNORECASE)
    # Remove trailing punctuation
    cleaned = cleaned.rstrip(".,!?")
    return cleaned.strip()


class AccountabilityTracker:
    """Track commitments and generate follow-up prompts."""

    def __init__(self):
        self.commitments: Dict[str, Commitment] = {}

    def add_commitments_from_session(
        self, session_id: str, messages: List[str]
    ) -> List[Commitment]:
        """Extract and store commitments from a session.

        Args:
            session_id: Session identifier
            messages: List of user messages

        Returns:
            List of extracted Commitment objects
        """
        full_text = " ".join(messages)
        found = extract_commitments(full_text, session_id)
        for c in found:
            self.commitments[c.commitment_id] = c
        return found

    def get_pending_commitments(self) -> List[Commitment]:
        """Get all commitments that haven't been followed up."""
        return [c for c in self.commitments.values() if not c.followed_up]

    def get_follow_up_prompts(self) -> List[str]:
        """Generate follow-up prompts for pending commitments.

        Returns:
            List of follow-up question strings
        """
        prompts = []
        for c in self.get_pending_commitments():
            prompt = _build_follow_up_prompt(c)
            prompts.append(prompt)
        return prompts

    def mark_followed_up(self, commitment_id: str, status: str = "done") -> bool:
        """Mark a commitment as followed up.

        Args:
            commitment_id: ID of commitment
            status: "done", "missed", or "extended"

        Returns:
            True if found and updated
        """
        if commitment_id not in self.commitments:
            return False
        self.commitments[commitment_id].followed_up = True
        self.commitments[commitment_id].status = status
        return True

    def get_statistics(self) -> Dict:
        """Get accountability statistics."""
        total = len(self.commitments)
        if total == 0:
            return {"total": 0, "pending": 0, "done": 0, "missed": 0}
        pending = sum(1 for c in self.commitments.values() if c.status == "pending")
        done = sum(1 for c in self.commitments.values() if c.status == "done")
        missed = sum(1 for c in self.commitments.values() if c.status == "missed")
        return {"total": total, "pending": pending, "done": done, "missed": missed}


def _build_follow_up_prompt(commitment: Commitment) -> str:
    """Build a follow-up prompt for a commitment."""
    if commitment.deadline_text:
        return (
            f"You mentioned you would {commitment.action} by {commitment.deadline_text}. "
            f"How did that go?"
        )
    return f"Last time you said you'd {commitment.action}. Any update on that?"


def check_deadline_status(
    deadline_text: str, reference_date: Optional[date] = None
) -> Tuple[str, Optional[str]]:
    """Check if a deadline has passed.

    Args:
        deadline_text: Raw deadline string
        reference_date: Date to compare against (defaults to today)

    Returns:
        (status, message) where status is "overdue", "upcoming", or "unknown"
    """
    ref = reference_date or date.today()

    # Try to parse common date formats
    parsed = _parse_date(deadline_text)
    if not parsed:
        return "unknown", None

    if parsed < ref:
        days_overdue = (ref - parsed).days
        msg = f"This was due {days_overdue} day(s) ago ({deadline_text})."
        return "overdue", msg
    else:
        days_left = (parsed - ref).days
        msg = f"{days_left} day(s) remaining until {deadline_text}."
        return "upcoming", msg


def _parse_date(text: str) -> Optional[date]:
    """Try to parse a date string."""
    formats = [
        "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y",
        "%B %d, %Y", "%B %d %Y", "%b %d, %Y",
        "%B %Y", "%b %Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            continue
    return None
