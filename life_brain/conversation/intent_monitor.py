"""
Intent Shift Monitoring — Detect and track mode transitions.

Monitors user intent shifts between Small Talk and Guided modes.
Tracks confidence levels, transition patterns, and provides analytics.
"""

from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class IntentShift(str, Enum):
    """Types of intent shifts detected."""
    SMALL_TALK_TO_GUIDED = "small_talk_to_guided"
    GUIDED_TO_SMALL_TALK = "guided_to_small_talk"
    WITHIN_SMALL_TALK = "within_small_talk"
    WITHIN_GUIDED = "within_guided"
    NO_SHIFT = "no_shift"


class IntentMonitor:
    """Monitors intent shifts and mode transitions in conversation."""

    def __init__(self):
        """Initialize intent monitor with empty history."""
        self.shift_history: List[Dict[str, Any]] = []
        self.previous_mode: Optional[str] = None
        self.previous_use_case_id: Optional[str] = None
        self.previous_confidence: float = 0.0
        self.session_start_ts: str = datetime.utcnow().isoformat()

    def detect_shift(
        self,
        current_mode: str,
        current_use_case_id: Optional[str] = None,
        current_confidence: float = 0.0,
        user_message: Optional[str] = None,
    ) -> Tuple[IntentShift, Dict[str, Any]]:
        """
        Detect if user intent has shifted between modes.

        Args:
            current_mode: Current mode ("small_talk" or "guided")
            current_use_case_id: Use case ID if in guided mode
            current_confidence: Confidence score for current intent
            user_message: User's message (optional, for logging)

        Returns:
            Tuple of (IntentShift enum, shift_details dict)
        """
        shift_type = IntentShift.NO_SHIFT
        shift_details = {
            "timestamp": datetime.utcnow().isoformat(),
            "previous_mode": self.previous_mode,
            "current_mode": current_mode,
            "previous_use_case_id": self.previous_use_case_id,
            "current_use_case_id": current_use_case_id,
            "confidence_delta": current_confidence - self.previous_confidence,
            "user_message_preview": user_message[:50] if user_message else None,
        }

        # Detect shift type
        if self.previous_mode is None:
            # First turn - no shift
            shift_type = IntentShift.NO_SHIFT
            logger.debug(f"Initial mode: {current_mode}")

        elif self.previous_mode == "small_talk" and current_mode == "guided":
            shift_type = IntentShift.SMALL_TALK_TO_GUIDED
            logger.info(f"Intent shift: Small Talk → Guided (use_case: {current_use_case_id})")

        elif self.previous_mode == "guided" and current_mode == "small_talk":
            shift_type = IntentShift.GUIDED_TO_SMALL_TALK
            logger.info(f"Intent shift: Guided → Small Talk (was: {self.previous_use_case_id})")

        elif self.previous_mode == "small_talk" and current_mode == "small_talk":
            shift_type = IntentShift.WITHIN_SMALL_TALK
            logger.debug("Continuing in small talk mode")

        elif self.previous_mode == "guided" and current_mode == "guided":
            # Same mode, but check if use case changed
            if current_use_case_id != self.previous_use_case_id:
                shift_type = IntentShift.WITHIN_GUIDED
                logger.info(
                    f"Use case change within guided mode: "
                    f"{self.previous_use_case_id} → {current_use_case_id}"
                )
            else:
                shift_type = IntentShift.WITHIN_GUIDED
                logger.debug("Continuing in same guided use case")

        shift_details["shift_type"] = shift_type.value

        # Update state
        self.previous_mode = current_mode
        self.previous_use_case_id = current_use_case_id
        self.previous_confidence = current_confidence

        # Record in history
        self.shift_history.append(shift_details)

        return (shift_type, shift_details)

    def should_prompt_mode_switch(self, shift_type: IntentShift) -> bool:
        """
        Determine if user should be prompted about mode options.

        Returns True when user shows intent to switch modes.

        Args:
            shift_type: Detected shift type

        Returns:
            True if should prompt mode options
        """
        # Prompt on explicit shifts between modes
        if shift_type in [
            IntentShift.SMALL_TALK_TO_GUIDED,
            IntentShift.GUIDED_TO_SMALL_TALK,
        ]:
            return True

        # Also prompt if user seems uncertain (low confidence)
        if self.previous_confidence > 0.0 and self.previous_confidence < 0.5:
            return True

        return False

    def get_shift_analytics(self) -> Dict[str, Any]:
        """
        Get analytics on intent shifts in this session.

        Returns:
            Dict with:
            - total_shifts: Count of mode transitions
            - shift_types: Count by type
            - session_duration: Time in session
            - primary_mode: Most common mode
            - mode_switches_count: Total back-and-forth switches
        """
        if not self.shift_history:
            return {
                "total_shifts": 0,
                "shift_types": {},
                "session_duration_seconds": 0,
                "primary_mode": None,
                "mode_switches_count": 0,
            }

        # Count shift types
        shift_types = {}
        for shift in self.shift_history:
            stype = shift.get("shift_type", "unknown")
            shift_types[stype] = shift_types.get(stype, 0) + 1

        # Count mode transitions
        mode_transitions = [
            s for s in self.shift_history
            if s["shift_type"] in [
                IntentShift.SMALL_TALK_TO_GUIDED.value,
                IntentShift.GUIDED_TO_SMALL_TALK.value,
            ]
        ]

        # Determine primary mode
        mode_counts = {}
        for shift in self.shift_history:
            mode = shift.get("current_mode")
            if mode:
                mode_counts[mode] = mode_counts.get(mode, 0) + 1
        primary_mode = max(mode_counts, key=mode_counts.get) if mode_counts else None

        # Calculate session duration
        if self.shift_history:
            first_ts = datetime.fromisoformat(self.session_start_ts)
            last_ts = datetime.fromisoformat(self.shift_history[-1]["timestamp"])
            duration_seconds = (last_ts - first_ts).total_seconds()
        else:
            duration_seconds = 0

        return {
            "total_shifts": len(self.shift_history),
            "shift_types": shift_types,
            "session_duration_seconds": int(duration_seconds),
            "primary_mode": primary_mode,
            "mode_switches_count": len(mode_transitions),
        }

    def reset(self) -> None:
        """Reset monitor for new session."""
        self.shift_history = []
        self.previous_mode = None
        self.previous_use_case_id = None
        self.previous_confidence = 0.0
        self.session_start_ts = datetime.utcnow().isoformat()
        logger.debug("Intent monitor reset for new session")


def monitor_intent_shift(
    current_mode: str,
    current_use_case_id: Optional[str] = None,
    current_confidence: float = 0.0,
    monitor: Optional[IntentMonitor] = None,
    user_message: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Helper function: Detect intent shift and suggest mode switch if needed.

    Args:
        current_mode: Current mode ("small_talk" or "guided")
        current_use_case_id: Use case ID if in guided mode
        current_confidence: Confidence score
        monitor: Optional existing monitor instance
        user_message: User's message for context

    Returns:
        Dict with:
        - shift_type: Type of shift detected
        - should_prompt_mode_options: Whether to show mode selection
        - mode_options_prompt: Text to display if prompting
        - monitor: Updated monitor instance (for session continuity)
    """
    if monitor is None:
        monitor = IntentMonitor()

    shift_type, shift_details = monitor.detect_shift(
        current_mode=current_mode,
        current_use_case_id=current_use_case_id,
        current_confidence=current_confidence,
        user_message=user_message,
    )

    should_prompt = monitor.should_prompt_mode_switch(shift_type)

    # Format mode options prompt in Hinglish
    mode_options_prompt = None
    if should_prompt:
        if shift_type == IntentShift.SMALL_TALK_TO_GUIDED:
            mode_options_prompt = """Samjha! Tujhe structured guidance chahiye. Tujhe kya approach prefer hai?

[A] 🎯 Guided — Ek expert ke saath structured Q&A (confidence: 0.9)
[B] 💬 Small Talk — Bas baatein, passive capture (confidence: 0.6)

Select A or B:"""

        elif shift_type == IntentShift.GUIDED_TO_SMALL_TALK:
            mode_options_prompt = """Lagta hai tune guided mode se door jaana chahte ho. Kya tum prefer karte ho?

[A] 💬 Small Talk — Free-form conversation, relaxed capture
[B] 🎯 Guided — Structured approach with expert guidance

Select A or B:"""

        elif shift_type == IntentShift.NO_SHIFT and current_confidence < 0.5:
            mode_options_prompt = """Hmm, thoda uncertain lag raha hai. Kya mode choose karna chahoge?

[A] 💬 Small Talk — Casual conversation, flexible
[B] 🎯 Guided — Structured with expert, detailed capture

Select A or B:"""

    return {
        "shift_type": shift_type.value,
        "shift_details": shift_details,
        "should_prompt_mode_options": should_prompt,
        "mode_options_prompt": mode_options_prompt,
        "monitor": monitor,
    }
