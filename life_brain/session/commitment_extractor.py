"""
Commitment extractor for identifying promises and deadlines.

Analyzes conversation history to extract user commitments,
promises, and action items with associated deadlines.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import re


class CommitmentType(Enum):
    """Types of commitments."""

    ACTION = "action"  # Specific action to take
    GOAL = "goal"  # Long-term goal
    PROMISE = "promise"  # Commitment to someone
    DEADLINE = "deadline"  # Time-bound commitment
    EXPERIMENT = "experiment"  # Try something new
    REFLECTION = "reflection"  # Self-reflection task
    LEARNING = "learning"  # Learning objective


class CommitmentStatus(Enum):
    """Commitment status."""

    PENDING = "pending"  # Not yet started
    IN_PROGRESS = "in_progress"  # Active work
    COMPLETED = "completed"  # Finished
    DEFERRED = "deferred"  # Postponed
    ABANDONED = "abandoned"  # Gave up


@dataclass
class Commitment:
    """User commitment or promise."""

    commitment_id: str
    description: str  # What was committed
    commitment_type: CommitmentType
    status: CommitmentStatus = CommitmentStatus.PENDING
    target_date: Optional[str] = None  # ISO format date
    priority: int = 3  # 1-5 scale, 1 = highest
    confidence: float = 0.8  # How confident we are (0-1)
    context: str = ""  # Additional context
    source_turn: int = 0  # Which turn this was mentioned
    identified_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    accountability_partner: Optional[str] = None  # Who to report to

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "commitment_id": self.commitment_id,
            "description": self.description,
            "commitment_type": self.commitment_type.value,
            "status": self.status.value,
            "target_date": self.target_date,
            "priority": self.priority,
            "confidence": self.confidence,
            "context": self.context,
            "source_turn": self.source_turn,
            "identified_at": self.identified_at,
            "tags": self.tags,
            "accountability_partner": self.accountability_partner,
        }

    def is_overdue(self) -> bool:
        """Check if commitment is overdue."""
        if not self.target_date:
            return False
        try:
            target = datetime.fromisoformat(self.target_date)
            return datetime.now() > target and self.status != CommitmentStatus.COMPLETED
        except ValueError:
            return False

    def days_until_deadline(self) -> Optional[int]:
        """Days until deadline."""
        if not self.target_date:
            return None
        try:
            target = datetime.fromisoformat(self.target_date)
            delta = target - datetime.now()
            return delta.days
        except ValueError:
            return None


class CommitmentExtractor:
    """Extract commitments from conversation."""

    # Commitment keywords
    COMMITMENT_KEYWORDS = {
        "commitment": ["commit", "promise", "guarantee", "vow", "pledge", "undertake"],
        "action": ["will do", "will start", "will begin", "plan to", "going to", "decide to"],
        "goal": ["goal", "target", "aim", "objective", "aspiration"],
        "deadline": ["by", "before", "until", "by the end of", "within", "in"],
        "experiment": ["try", "experiment", "test", "explore", "attempt"],
        "reflection": ["reflect", "think about", "consider", "ponder", "review"],
        "learning": ["learn", "study", "understand", "master", "improve at"],
    }

    # Time expressions
    TIME_PATTERNS = {
        "today": 0,
        "tomorrow": 1,
        "next week": 7,
        "next month": 30,
        "end of this week": 5,
        "end of month": 30,
        "in a week": 7,
        "in 2 weeks": 14,
        "in a month": 30,
        "before end of day": 0,
    }

    def __init__(self):
        """Initialize commitment extractor."""
        self.commitments: Dict[str, Commitment] = {}
        self.commitment_history: List[Commitment] = []

    def commitment_extractor(
        self,
        text: str,
        turn_number: int = 0,
        source_session_id: str = "",
        confidence_override: Optional[float] = None,
    ) -> Optional[Commitment]:
        """
        Extract commitment from text.

        Args:
            text: Text to analyze
            turn_number: Conversation turn number
            source_session_id: Source session ID
            confidence_override: Override confidence calculation

        Returns:
            Commitment object if found, None otherwise
        """
        text_lower = text.lower()

        # Check if text contains commitment keywords
        commitment_type, type_confidence = self._detect_commitment_type(text_lower)

        if commitment_type is None:
            return None

        # Extract target date if present
        target_date = self._extract_target_date(text_lower)

        # Determine priority
        priority = self._determine_priority(text, commitment_type)

        # Extract clean commitment description
        description = self._extract_description(text)

        # Calculate confidence
        if confidence_override is not None:
            confidence = confidence_override
        else:
            confidence = type_confidence

        # Generate commitment ID
        commitment_id = f"comp_{len(self.commitments):04d}"

        # Create commitment
        commitment = Commitment(
            commitment_id=commitment_id,
            description=description,
            commitment_type=commitment_type,
            target_date=target_date,
            priority=priority,
            confidence=confidence,
            source_turn=turn_number,
            context=text[:100],
            tags=self._extract_tags(text_lower),
            accountability_partner=(
                "user"  # Could be extracted from context later
            ),
        )

        # Store
        self.commitments[commitment_id] = commitment
        self.commitment_history.append(commitment)

        return commitment

    def _detect_commitment_type(self, text: str) -> Tuple[Optional[CommitmentType], float]:
        """Detect commitment type from text."""
        scores = {}

        for ctype, keywords in self.COMMITMENT_KEYWORDS.items():
            # Skip keys that aren't commitment types
            try:
                type_enum = CommitmentType[ctype.upper()]
            except KeyError:
                continue

            for keyword in keywords:
                if keyword in text:
                    scores[type_enum] = scores.get(type_enum, 0) + 1

        if not scores:
            return None, 0.0

        best_type = max(scores, key=scores.get)
        confidence = min(1.0, scores[best_type] / 3)

        return best_type, confidence

    def _extract_target_date(self, text: str) -> Optional[str]:
        """Extract target date from text."""
        # Check for relative time expressions
        for time_expr, days in self.TIME_PATTERNS.items():
            if time_expr in text:
                target = datetime.now() + timedelta(days=days)
                return target.isoformat()

        # Check for specific dates (YYYY-MM-DD)
        date_pattern = r"\d{4}-\d{2}-\d{2}"
        match = re.search(date_pattern, text)
        if match:
            return match.group(0)

        # Check for month/day (e.g., "by March 15")
        month_day_pattern = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})"
        match = re.search(month_day_pattern, text, re.IGNORECASE)
        if match:
            # Could enhance this to handle year, but for now just mark as detected
            return None

        return None

    def _determine_priority(self, text: str, commitment_type: CommitmentType) -> int:
        """Determine commitment priority."""
        text_lower = text.lower()

        # High priority markers
        if any(word in text_lower for word in ["critical", "urgent", "asap", "immediately", "must"]):
            return 1

        # Medium-high priority markers
        if any(word in text_lower for word in ["important", "key", "essential", "need to"]):
            return 2

        # Medium priority (default)
        if commitment_type == CommitmentType.GOAL:
            return 3

        # Medium-low priority
        if commitment_type == CommitmentType.EXPERIMENT:
            return 4

        # Low priority
        return 5

    def _extract_description(self, text: str) -> str:
        """Extract clean commitment description from text."""
        # Remove common prefixes
        description = text.strip()

        # Remove leading punctuation
        description = re.sub(r"^[\.\!?\-\s]+", "", description)

        # Truncate to reasonable length
        if len(description) > 200:
            description = description[:197] + "..."

        return description

    def _extract_tags(self, text: str) -> List[str]:
        """Extract tags from text."""
        tags = []

        # Check for career tags
        if any(word in text for word in ["career", "job", "role", "promotion", "interview"]):
            tags.append("career")

        # Check for personal tags
        if any(word in text for word in ["health", "fitness", "wellness", "personal", "family"]):
            tags.append("personal")

        # Check for learning tags
        if any(word in text for word in ["learn", "study", "skill", "training", "course"]):
            tags.append("learning")

        # Check for project tags
        if any(word in text for word in ["project", "build", "develop", "create", "design"]):
            tags.append("project")

        return tags

    def extract_commitments_from_history(
        self,
        history: List[Dict[str, str]],
        source_session_id: str = "",
    ) -> List[Commitment]:
        """
        Extract commitments from conversation history.

        Args:
            history: List of turn dicts with "user_message" and "turn_number"
            source_session_id: Source session ID

        Returns:
            List of extracted commitments
        """
        extracted = []

        for turn in history:
            if "user_message" in turn:
                commitment = self.commitment_extractor(
                    text=turn["user_message"],
                    turn_number=turn.get("turn_number", 0),
                    source_session_id=source_session_id,
                )

                if commitment:
                    extracted.append(commitment)

        return extracted

    def get_commitment(self, commitment_id: str) -> Optional[Commitment]:
        """Get specific commitment."""
        return self.commitments.get(commitment_id)

    def get_pending_commitments(self) -> List[Commitment]:
        """Get all pending commitments."""
        return [
            c
            for c in self.commitment_history
            if c.status == CommitmentStatus.PENDING
        ]

    def get_overdue_commitments(self) -> List[Commitment]:
        """Get overdue commitments."""
        return [c for c in self.commitment_history if c.is_overdue()]

    def get_commitments_by_priority(self, priority: int) -> List[Commitment]:
        """Get commitments by priority level."""
        return [c for c in self.commitment_history if c.priority == priority]

    def get_commitments_by_type(self, commitment_type: CommitmentType) -> List[Commitment]:
        """Get commitments by type."""
        return [c for c in self.commitment_history if c.commitment_type == commitment_type]

    def update_commitment_status(
        self, commitment_id: str, status: CommitmentStatus
    ) -> Tuple[bool, Optional[str]]:
        """Update commitment status."""
        if commitment_id not in self.commitments:
            return False, f"Commitment {commitment_id} not found"

        self.commitments[commitment_id].status = status
        return True, None

    def get_upcoming_deadlines(self, days_ahead: int = 7) -> List[Commitment]:
        """Get commitments with deadlines in next N days."""
        upcoming = []

        for commitment in self.commitment_history:
            if commitment.target_date:
                days_until = commitment.days_until_deadline()
                if (
                    days_until is not None
                    and 0 <= days_until <= days_ahead
                ):
                    upcoming.append(commitment)

        return sorted(upcoming, key=lambda c: c.days_until_deadline() or 999)

    def get_statistics(self) -> Dict[str, Any]:
        """Get commitment statistics."""
        if not self.commitment_history:
            return {
                "total_commitments": 0,
                "pending": 0,
                "completed": 0,
                "overdue": 0,
            }

        return {
            "total_commitments": len(self.commitment_history),
            "pending": len(self.get_pending_commitments()),
            "completed": len(
                [c for c in self.commitment_history
                 if c.status == CommitmentStatus.COMPLETED]
            ),
            "overdue": len(self.get_overdue_commitments()),
            "in_progress": len(
                [c for c in self.commitment_history
                 if c.status == CommitmentStatus.IN_PROGRESS]
            ),
            "by_type": {
                ctype.value: len(self.get_commitments_by_type(ctype))
                for ctype in CommitmentType
            },
        }

    def export_commitments(self) -> List[Dict[str, Any]]:
        """Export all commitments."""
        return [c.to_dict() for c in self.commitment_history]

    def export_pending_commitments(self) -> List[Dict[str, Any]]:
        """Export pending commitments only."""
        return [c.to_dict() for c in self.get_pending_commitments()]

    def export_overdue_commitments(self) -> List[Dict[str, Any]]:
        """Export overdue commitments."""
        return [c.to_dict() for c in self.get_overdue_commitments()]
