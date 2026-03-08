"""
Mode Selector UI — Display and handle mode selection interface.

Provides:
- Mode selection prompt with clear options
- Button/menu-style UI rendering
- Handler for user selection
- Integration with CitationFormatter for results display
"""

from typing import Optional, Dict, Any, Tuple
from enum import Enum
import logging

from life_brain.conversation.mode_gate import Mode

logger = logging.getLogger(__name__)


class ModeUIStyle(str, Enum):
    """Rendering style for mode selection UI."""
    BUTTONS = "buttons"  # Clickable button-style
    MENU = "menu"  # Text menu with numbers/letters
    INLINE = "inline"  # Inline text with quick options
    MODAL = "modal"  # Modal dialog style


class ModeSelector:
    """Handles mode selection UI and user interaction."""

    def __init__(self, style: ModeUIStyle = ModeUIStyle.MENU):
        """
        Initialize mode selector.

        Args:
            style: UI rendering style (BUTTONS, MENU, INLINE, MODAL)
        """
        self.style = style
        self.selection_history = []

    def render_mode_selection(
        self,
        title: Optional[str] = None,
        context: Optional[str] = None,
    ) -> str:
        """
        Render mode selection UI.

        Args:
            title: Optional custom title
            context: Optional context message (e.g., detected intent)

        Returns:
            Formatted UI string
        """
        if self.style == ModeUIStyle.BUTTONS:
            return self._render_button_style(title, context)
        elif self.style == ModeUIStyle.MENU:
            return self._render_menu_style(title, context)
        elif self.style == ModeUIStyle.INLINE:
            return self._render_inline_style(title, context)
        elif self.style == ModeUIStyle.MODAL:
            return self._render_modal_style(title, context)
        else:
            return self._render_menu_style(title, context)

    def _render_button_style(
        self,
        title: Optional[str],
        context: Optional[str],
    ) -> str:
        """Render as clickable buttons."""
        lines = []

        if title:
            lines.append(title)
            lines.append("")

        if context:
            lines.append(context)
            lines.append("")

        lines.append("Choose your conversation style:")
        lines.append("")
        lines.append("┌─────────────────────────────────────┐")
        lines.append("│ 💬 SMALL TALK                       │")
        lines.append("│ Free-form chat, relaxed capture     │")
        lines.append("│ Confidence: 60%                     │")
        lines.append("│ [Button A]                          │")
        lines.append("├─────────────────────────────────────┤")
        lines.append("│ 🎯 GUIDED                           │")
        lines.append("│ Structured Q&A with expert          │")
        lines.append("│ Confidence: 90%                     │")
        lines.append("│ [Button B]                          │")
        lines.append("└─────────────────────────────────────┘")

        return "\n".join(lines)

    def _render_menu_style(
        self,
        title: Optional[str],
        context: Optional[str],
    ) -> str:
        """Render as text menu."""
        lines = []

        if title:
            lines.append(title)
        else:
            lines.append("Kya conversation style prefer karte ho?")

        lines.append("")

        if context:
            lines.append(f"({context})")
            lines.append("")

        lines.append("[A] 💬 Bas baatein (Small Talk)")
        lines.append("    Free-form conversation, passive capture")
        lines.append("    Confidence: 0.6")
        lines.append("")
        lines.append("[B] 🎯 Kuch record karna (Guided)")
        lines.append("    Structured Q&A with expert guidance")
        lines.append("    Confidence: 0.9")
        lines.append("")
        lines.append("Select A or B:")

        return "\n".join(lines)

    def _render_inline_style(
        self,
        title: Optional[str],
        context: Optional[str],
    ) -> str:
        """Render as inline text."""
        parts = []

        if title:
            parts.append(title)

        if context:
            parts.append(f"({context})")

        parts.append("[A] Bas baatein or [B] Kuch record karna?")

        return " ".join(parts)

    def _render_modal_style(
        self,
        title: Optional[str],
        context: Optional[str],
    ) -> str:
        """Render as modal dialog."""
        lines = [
            "╔══════════════════════════════════════╗",
            "║  CONVERSATION MODE SELECTION        ║",
            "╚══════════════════════════════════════╝",
            "",
        ]

        if title:
            lines.append(f"  {title}")
            lines.append("")

        if context:
            lines.append(f"  {context}")
            lines.append("")

        lines.extend([
            "  How do you prefer to talk?",
            "",
            "  A) 💬 Small Talk",
            "     • Casual, free-form conversation",
            "     • Low-confidence passive capture",
            "",
            "  B) 🎯 Guided",
            "     • Structured Q&A with expert",
            "     • High-confidence detailed capture",
            "",
            "  Enter your choice (A/B):",
        ])

        return "\n".join(lines)

    def handle_selection(
        self,
        user_input: str,
    ) -> Optional[Tuple[Mode, Dict[str, Any]]]:
        """
        Handle user's mode selection.

        Args:
            user_input: User's input (e.g., "A", "B", "small_talk", "guided")

        Returns:
            Tuple of (Mode, metadata) or None if invalid
        """
        # Normalize input
        normalized = user_input.strip().lower()

        # Check various forms
        mode = None
        if normalized in ["a", "small_talk", "bas baatein", "baatein"]:
            mode = Mode.SMALL_TALK
        elif normalized in ["b", "guided", "kuch record karna", "record"]:
            mode = Mode.GUIDED
        else:
            logger.warning(f"Invalid mode selection: {user_input}")
            return None

        # Record selection
        selection_record = {
            "input": user_input,
            "mode": mode.value,
            "timestamp": self._get_timestamp(),
            "selection_order": len(self.selection_history) + 1,
        }
        self.selection_history.append(selection_record)

        logger.info(f"Mode selected: {mode} (from input: {user_input})")

        metadata = {
            "user_input": user_input,
            "selection_timestamp": selection_record["timestamp"],
            "selection_order": selection_record["selection_order"],
        }

        return (mode, metadata)

    def format_mode_confirmation(
        self,
        mode: Mode,
        use_case_id: Optional[str] = None,
    ) -> str:
        """
        Format confirmation message after mode selection.

        Args:
            mode: Selected mode
            use_case_id: Optional use case if in guided mode

        Returns:
            Confirmation message in Hinglish
        """
        if mode == Mode.SMALL_TALK:
            return """Theek hai! 💬 Bas baatein mode mein enter kar rahe ho.

Baat karo naturally — main sunta hun aur important nuggets capture kar loonga.
Kab bhi guided mode mein jaana chahoge, bas bolo. Chale?"""

        elif mode == Mode.GUIDED:
            msg = "Bilkul! 🎯 Guided mode mein enter kar rahe ho."
            if use_case_id:
                msg += f"\n\nTumhare selected use case: {use_case_id}"
            msg += "\n\nMain expert ke saath structured Q&A karte hain. Chale?"
            return msg

        return "Mode selected!"

    def show_mode_options_with_context(
        self,
        detected_intent: Optional[str] = None,
        confidence: float = 0.0,
        reason: Optional[str] = None,
    ) -> str:
        """
        Show mode options with detection context.

        Args:
            detected_intent: What was detected (e.g., "career planning")
            confidence: Detection confidence (0-1)
            reason: Why we're asking (e.g., "intent shift detected")

        Returns:
            Formatted prompt with context
        """
        lines = []

        # Build context message
        if detected_intent and confidence >= 0.7:
            lines.append(f"✓ Detected: {detected_intent} ({int(confidence * 100)}% confidence)")
            lines.append("")

        if reason:
            lines.append(f"({reason})")
            lines.append("")

        # Show mode options
        lines.append("Kya approach prefer karte ho?")
        lines.append("")
        lines.append("[A] 💬 Small Talk — Casual, flexible")
        lines.append("[B] 🎯 Guided — Structured, with expert")
        lines.append("")
        lines.append("Select A or B:")

        return "\n".join(lines)

    def _get_timestamp(self) -> str:
        """Get ISO format timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()


def render_mode_selection_ui(
    style: ModeUIStyle = ModeUIStyle.MENU,
    title: Optional[str] = None,
    context: Optional[str] = None,
    detected_intent: Optional[str] = None,
    confidence: float = 0.0,
) -> str:
    """
    Helper function: Render mode selection UI.

    Args:
        style: UI style to use
        title: Custom title for prompt
        context: Context message
        detected_intent: What was detected
        confidence: Detection confidence

    Returns:
        Formatted UI prompt string
    """
    selector = ModeSelector(style=style)

    if detected_intent and confidence > 0.0:
        full_context = f"{context or ''} (Detected: {detected_intent} {int(confidence * 100)}%)".strip()
    else:
        full_context = context

    return selector.render_mode_selection(title=title, context=full_context)


def handle_mode_selection(user_input: str) -> Optional[Tuple[Mode, Dict[str, Any]]]:
    """
    Helper function: Handle user's mode selection.

    Args:
        user_input: User's input

    Returns:
        Tuple of (Mode, metadata) or None if invalid
    """
    selector = ModeSelector()
    return selector.handle_selection(user_input)
