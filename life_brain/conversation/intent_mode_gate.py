"""
Mode Gate UI — Present Small Talk vs Guided mode selection buttons.

Implements:
- mode_gate_ui(): Show mode selection interface
- format_mode_buttons(): Format mode buttons in Hinglish
- Handle user selection and routing
"""

from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def format_mode_buttons() -> str:
    """
    Format mode selection buttons in Hinglish.

    Returns:
        Formatted button display string
    """
    display = """
╭─────────────────────────────────────────────────╮
│   Kya chal raha hai? (What's up?)               │
├─────────────────────────────────────────────────┤
│                                                 │
│  [A] Bas baatein करते हैं                      │
│      (Just chat — free talk, no recording)     │
│      Confidence: 0.60 | Mode: SMALL_TALK        │
│                                                 │
│  [B] Kuch record karna hai                     │
│      (I want to document something)             │
│      Confidence: 0.90 | Mode: GUIDED            │
│                                                 │
├─────────────────────────────────────────────────┤
│  Type A or B to select:                         │
╰─────────────────────────────────────────────────╯
""".strip()
    return display


def format_mode_buttons_compact() -> str:
    """
    Compact version of mode buttons (single line).

    Returns:
        Compact button display string
    """
    return "[A] Bas baatein | [B] Record करना → Select A or B:"


def mode_gate_ui(
    detected_mode: Optional[str] = None,
    confidence: float = 0.0,
) -> Dict[str, Any]:
    """
    Main UI for mode selection.

    Flow:
    1. If mode already detected with high confidence: show direct path
    2. Else: show A/B buttons for user selection
    3. Return formatted display + routing info

    Args:
        detected_mode: Pre-detected mode ("small_talk" or "guided") if any
        confidence: Confidence in detected mode

    Returns:
        Dict with:
        - display: Formatted UI string
        - next_action: What to do next
        - requires_selection: Whether user must select
        - timeout_seconds: Time to wait for selection
    """
    result = {
        "display": None,
        "next_action": None,
        "requires_selection": True,
        "timeout_seconds": 60,
    }

    # If mode already detected with high confidence, show streamlined path
    if detected_mode and confidence > 0.75:
        logger.debug(
            f"High confidence mode detected: {detected_mode} ({confidence:.2f})"
        )

        if detected_mode == "guided":
            result["display"] = (
                "Samjha! Tujhe structured guidance chahiye. "
                "Neeche relevant use cases dekh:\n"
            )
            result["next_action"] = "show_use_cases"
            result["requires_selection"] = False
        else:  # small_talk
            result["display"] = "Haan, chaliye baatein karte hain."
            result["next_action"] = "continue_small_talk"
            result["requires_selection"] = False

        logger.debug(f"Mode gate: direct path, action={result['next_action']}")
        return result

    # Otherwise, show mode selection buttons
    logger.debug("Mode gate: showing mode selection buttons")

    result["display"] = format_mode_buttons()
    result["next_action"] = "wait_for_mode_selection"
    result["requires_selection"] = True

    return result


def handle_mode_selection(
    user_selection: str,
) -> Tuple[str, Dict[str, Any]]:
    """
    Handle user's mode selection (A or B).

    Args:
        user_selection: User's input ("A", "B", "a", "b", etc.)

    Returns:
        Tuple of (mode, action_dict) where:
        - mode: "small_talk" or "guided"
        - action_dict: Dict with next_action and metadata
    """
    selection = user_selection.strip().upper()

    action_dict = {
        "mode": None,
        "next_action": None,
        "message": None,
        "confidence": 0.9,  # User explicitly selected
    }

    if selection == "A":
        action_dict["mode"] = "small_talk"
        action_dict["next_action"] = "continue_small_talk"
        action_dict["message"] = "Bilkul! Baatein karte hain. Kya chal raha hai?"
        logger.info("User selected: SMALL_TALK mode")

    elif selection == "B":
        action_dict["mode"] = "guided"
        action_dict["next_action"] = "show_use_cases"
        action_dict["message"] = (
            "Great! Chaliye kuch structured context mein seekhte hain. "
            "Ye relevant topics hain:"
        )
        logger.info("User selected: GUIDED mode")

    else:
        # Invalid selection
        action_dict["next_action"] = "ask_again"
        action_dict["message"] = (
            f"'{selection}' samajh nahi aaya. Kripaya A ya B select karo."
        )
        logger.warning(f"Invalid mode selection: {user_selection}")

    return (action_dict["mode"], action_dict)


def format_mode_help() -> str:
    """
    Format help text for mode selection.

    Returns:
        Help text in Hinglish
    """
    help_text = """
MODE SELECTION GUIDE (मोड चयन गाइड)
════════════════════════════════════════════

[A] Bas baatein (Small Talk)
    ├─ For: Casual conversation, free-form thoughts
    ├─ Confidence: 0.60 (passive capture)
    ├─ Recording: Light (raw text saved)
    └─ Best for: Exploring ideas, venting, reflection

[B] Kuch record karna (Guided)
    ├─ For: Structured learning, goal-setting, deep dives
    ├─ Confidence: 0.90 (high-confidence Q&A)
    ├─ Recording: Deep (Q&A pairs extracted, validated)
    └─ Best for: Interviews, career planning, important decisions

════════════════════════════════════════════
Not sure? Start with [A] — we can suggest [B] anytime!
"""
    return help_text.strip()


def format_mode_transition_prompt(current_mode: str, suggested_mode: str) -> str:
    """
    Format transition prompt when suggesting mode switch.

    Args:
        current_mode: Current mode ("small_talk" or "guided")
        suggested_mode: Suggested new mode

    Returns:
        Transition prompt in Hinglish
    """
    if current_mode == "small_talk" and suggested_mode == "guided":
        return (
            "Lagta hai tujhe guidance chahiye! "
            "Kya main kisi expert se milwau? (Y/N)"
        )
    elif current_mode == "guided" and suggested_mode == "small_talk":
        return (
            "Relax karte hain structured recording se? "
            "Free talk mode mein shift karo? (Y/N)"
        )
    else:
        return "Mode switch karo?"


# ─────────────────────────────────────────────────
# Mode State Machine
# ─────────────────────────────────────────────────

class ModeState:
    """Tracks current mode and allows transitions."""

    def __init__(self, initial_mode: Optional[str] = None):
        """
        Initialize mode state.

        Args:
            initial_mode: Initial mode ("small_talk", "guided", or None)
        """
        self.current_mode = initial_mode
        self.mode_history = []
        if initial_mode:
            self.mode_history.append(initial_mode)

    def set_mode(self, new_mode: str) -> bool:
        """
        Set current mode.

        Args:
            new_mode: New mode to set

        Returns:
            True if mode changed, False if already in that mode
        """
        if new_mode not in ["small_talk", "guided"]:
            logger.error(f"Invalid mode: {new_mode}")
            return False

        if self.current_mode == new_mode:
            logger.debug(f"Already in {new_mode} mode")
            return False

        logger.info(f"Mode transition: {self.current_mode} → {new_mode}")
        self.current_mode = new_mode
        self.mode_history.append(new_mode)
        return True

    def get_current_mode(self) -> Optional[str]:
        """Get current mode."""
        return self.current_mode

    def get_mode_history(self) -> list:
        """Get mode transition history."""
        return self.mode_history.copy()

    def can_transition_to(self, target_mode: str) -> bool:
        """Check if transition is allowed."""
        # Allow transitions between any modes
        return target_mode in ["small_talk", "guided"]
