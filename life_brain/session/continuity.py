"""
Session Continuity — Context retrieval and pending item tracking across turns.

Extends SessionManager with:
- Context window extraction from prior conversations
- Pending item management (follow-ups, unanswered questions)
- Cross-session state reconciliation
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import logging

from .session_manager import Session, SessionManager, SessionMessage

logger = logging.getLogger(__name__)


class PendingItemType(str, Enum):
    """Types of pending items."""
    FOLLOW_UP = "follow_up"            # Question that needs follow-up
    UNANSWERED = "unanswered"          # User didn't fully answer
    CLARIFICATION_NEEDED = "clarification_needed"  # Answer was unclear
    ACTION_ITEM = "action_item"        # User said they'd do something
    CONFLICT = "conflict"              # Contradiction to resolve


@dataclass
class PendingItem:
    """A pending follow-up or action item."""

    item_id: str                        # Unique ID
    item_type: PendingItemType          # Type of pending item
    original_question: str              # The question that prompted this
    context: str                        # Why it's pending
    priority: int                       # 0=high, 1=medium, 2=low
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    session_id: str = ""                # Which session created it
    turn_number: int = 0                # Which turn in that session


@dataclass
class ContextWindow:
    """A snippet of context from prior conversation."""

    window_id: str                      # Unique ID
    session_id: str                     # Which session
    turn_range: Tuple[int, int]         # Message range (start, end)
    topic: str                          # What was being discussed
    expert: Optional[str] = None        # Which expert
    use_case: Optional[str] = None      # Which use case
    summary: str = ""                   # 1-2 sentence summary
    messages: List[Dict[str, Any]] = field(default_factory=list)  # Actual messages


class ContextRetriever:
    """Retrieve relevant context from prior conversations."""

    def __init__(self, session_manager: SessionManager):
        """Initialize with session manager."""
        self.session_manager = session_manager

    def get_recent_context(
        self,
        session: Session,
        lookback_turns: int = 10
    ) -> List[ContextWindow]:
        """
        Get recent context from current session.

        Returns the last N messages as context windows for LLM.

        Args:
            session: Current session
            lookback_turns: How many turns back to retrieve

        Returns:
            List of ContextWindow objects
        """
        windows = []
        messages = session.messages[-lookback_turns:]

        if not messages:
            return windows

        # Group messages into windows (pairs of user/assistant)
        for i in range(0, len(messages) - 1, 2):
            if i + 1 < len(messages):
                user_msg = messages[i]
                assistant_msg = messages[i + 1]

                window = ContextWindow(
                    window_id=f"window_{session.session_id}_{i}",
                    session_id=session.session_id,
                    turn_range=(len(session.messages) - len(messages) + i,
                               len(session.messages) - len(messages) + i + 1),
                    topic="Recent conversation",
                    expert=session.current_expert,
                    use_case=session.current_use_case_id,
                    summary=f"Turn {i//2 + 1}: User asked about {user_msg.content[:50]}...",
                    messages=[
                        {
                            "role": "user",
                            "content": user_msg.content,
                            "timestamp": user_msg.timestamp,
                        },
                        {
                            "role": "assistant",
                            "content": assistant_msg.content,
                            "timestamp": assistant_msg.timestamp,
                        }
                    ]
                )
                windows.append(window)

        return windows

    def get_prior_session_context(
        self,
        user_id: str,
        current_session_id: str,
        lookback_sessions: int = 3
    ) -> List[ContextWindow]:
        """
        Get context from prior sessions with same user.

        Useful for retrieving background information and ongoing topics.

        Args:
            user_id: User identifier
            current_session_id: Don't include this session
            lookback_sessions: How many prior sessions to scan

        Returns:
            List of ContextWindow from prior sessions
        """
        windows = []

        # Get all sessions for this user
        all_sessions = self.session_manager.list_sessions(user_id=user_id, active_only=False)

        # Filter to prior sessions, most recent first
        prior_sessions = [
            s for s in sorted(all_sessions, key=lambda x: x.created_at, reverse=True)
            if s.session_id != current_session_id
        ][:lookback_sessions]

        # Load each session and extract context
        for session_metadata in prior_sessions:
            session = self.session_manager.load_session(session_metadata.session_id)
            if not session:
                continue

            # Extract key topics from session
            if session.captured_nuggets:
                summary = f"Previous session captured {len(session.captured_nuggets)} nuggets"
            else:
                summary = f"Previous session with {len(session.messages)} messages"

            window = ContextWindow(
                window_id=f"prior_{session.session_id}",
                session_id=session.session_id,
                turn_range=(0, len(session.messages)),
                topic=f"Prior conversation ({session.metadata.mode} mode)",
                expert=session.current_expert,
                use_case=session.current_use_case_id,
                summary=summary,
                messages=[
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp,
                    }
                    for msg in session.messages[-3:]  # Last 3 messages
                ]
            )
            windows.append(window)

        return windows

    def get_conversation_summary(
        self,
        session: Session,
        max_length: int = 500
    ) -> str:
        """
        Generate summary of conversation so far.

        Args:
            session: Current session
            max_length: Max characters in summary

        Returns:
            Text summary of key points
        """
        if not session.messages:
            return "No conversation history."

        # Find main topics
        topics = set()
        if session.current_use_case_id:
            topics.add(f"use case {session.current_use_case_id}")
        if session.current_expert:
            topics.add(f"expert {session.current_expert}")

        # Count captures
        captured = len(session.captured_nuggets)

        summary_parts = [
            f"You're in {session.metadata.mode} mode.",
            f"Conversation has {len(session.messages)} messages.",
        ]

        if topics:
            summary_parts.append(f"Discussing: {', '.join(topics)}")

        if captured > 0:
            summary_parts.append(f"Captured {captured} insights.")

        summary = " ".join(summary_parts)
        return summary[:max_length]


class PendingItemManager:
    """Manage pending items (follow-ups, action items, conflicts)."""

    def __init__(self, session_manager: SessionManager):
        """Initialize with session manager."""
        self.session_manager = session_manager
        self.pending_items: Dict[str, List[PendingItem]] = {}  # session_id -> items

    def add_pending_item(
        self,
        session: Session,
        item_type: PendingItemType,
        original_question: str,
        context: str,
        priority: int = 1
    ) -> PendingItem:
        """
        Track a pending item for follow-up.

        Args:
            session: Current session
            item_type: Type of pending item
            original_question: Question that needs follow-up
            context: Why it's pending
            priority: 0=high, 1=medium, 2=low

        Returns:
            Created PendingItem
        """
        item = PendingItem(
            item_id=f"pending_{session.session_id}_{len(self.get_pending_items(session))}",
            item_type=item_type,
            original_question=original_question,
            context=context,
            priority=priority,
            session_id=session.session_id,
            turn_number=len(session.messages)
        )

        if session.session_id not in self.pending_items:
            self.pending_items[session.session_id] = []

        self.pending_items[session.session_id].append(item)

        # Store in session's extra_context
        if "pending_items" not in session.extra_context:
            session.extra_context["pending_items"] = []

        session.extra_context["pending_items"].append(asdict(item))
        self.session_manager.save_session(session)

        logger.info(f"Added pending item to session {session.session_id}: {item_type.value}")
        return item

    def get_pending_items(
        self,
        session: Session,
        item_type: Optional[PendingItemType] = None,
        priority: Optional[int] = None
    ) -> List[PendingItem]:
        """
        Get pending items from session.

        Args:
            session: Session to get items from
            item_type: Filter by type (optional)
            priority: Filter by priority (optional)

        Returns:
            List of PendingItem
        """
        items = []

        # Load from session's extra_context
        if "pending_items" in session.extra_context:
            for item_data in session.extra_context["pending_items"]:
                item = PendingItem(
                    item_id=item_data["item_id"],
                    item_type=PendingItemType(item_data["item_type"]),
                    original_question=item_data["original_question"],
                    context=item_data["context"],
                    priority=item_data["priority"],
                    session_id=item_data["session_id"],
                    turn_number=item_data["turn_number"],
                    created_at=item_data.get("created_at", "")
                )

                if item_type and item.item_type != item_type:
                    continue
                if priority is not None and item.priority != priority:
                    continue

                items.append(item)

        return sorted(items, key=lambda x: x.priority)

    def resolve_pending_item(
        self,
        session: Session,
        item_id: str,
        resolution: str
    ) -> bool:
        """
        Mark a pending item as resolved.

        Args:
            session: Current session
            item_id: ID of item to resolve
            resolution: How it was resolved

        Returns:
            True if resolved, False if not found
        """
        if "pending_items" not in session.extra_context:
            return False

        # Find and remove the item
        remaining = []
        found = False

        for item_data in session.extra_context["pending_items"]:
            if item_data["item_id"] == item_id:
                found = True
                logger.info(f"Resolved pending item {item_id}: {resolution}")
            else:
                remaining.append(item_data)

        session.extra_context["pending_items"] = remaining
        self.session_manager.save_session(session)

        return found

    def get_pending_summary(self, session: Session) -> str:
        """
        Get human-readable summary of pending items.

        Args:
            session: Session to summarize

        Returns:
            Text summary of pending items
        """
        items = self.get_pending_items(session)

        if not items:
            return "No pending items."

        # Group by priority
        high_priority = [i for i in items if i.priority == 0]
        medium_priority = [i for i in items if i.priority == 1]

        lines = ["📋 Pending Items:"]

        if high_priority:
            lines.append("🔴 High Priority:")
            for item in high_priority:
                lines.append(f"  • {item.original_question}")

        if medium_priority:
            lines.append("🟡 Medium Priority:")
            for item in medium_priority:
                lines.append(f"  • {item.original_question}")

        return "\n".join(lines)
