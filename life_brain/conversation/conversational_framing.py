"""
Conversational Framing — Differentiated question delivery by use case category.

Problem: Numbered clinical questions ('Q3 of 7: Tumhe kaisa laga?') feel
interrogative for emotional use cases (relationships, health, personal growth).
Esther Perel and Brene Brown never conduct therapy with a progress tracker.

Solution: Two delivery modes selected automatically from the use case ID.

STRUCTURED mode (career, finance, productivity):
  - Numbered progress visible: 'Q3 of 8'
  - Direct, efficient questions
  - Explicit transitions between topics
  - User knows how many questions remain

CONVERSATIONAL mode (relationships, health, memories):
  - NO question numbers, NO progress tracker
  - Questions disguised as curiosity: 'Aur... us moment mein andar kya hua?'
  - Natural transitions, no 'Theek hai, ab next topic...'
  - Expert signature phrases used organically
  - Silence allowed — no rushing to next question

HYBRID mode (goals, habits, learning):
  - Structured goal-setting framework
  - Empathetic, warm tone throughout
  - Progress visible but phrased gently
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict


class QuestionMode(str, Enum):
    """Delivery mode for questions in a session."""
    STRUCTURED = "structured"          # Numbered, direct, time-boxed
    CONVERSATIONAL = "conversational"  # Flowing, empathetic, no counters
    HYBRID = "hybrid"                  # Structured goal + empathetic tone


# Use case category → QuestionMode mapping
_USE_CASE_MODE: Dict[str, QuestionMode] = {
    # Career (C1–C12): structured, direct, efficient
    "C1": QuestionMode.STRUCTURED, "C2": QuestionMode.STRUCTURED,
    "C3": QuestionMode.STRUCTURED, "C4": QuestionMode.STRUCTURED,
    "C5": QuestionMode.STRUCTURED, "C6": QuestionMode.STRUCTURED,
    "C7": QuestionMode.STRUCTURED, "C8": QuestionMode.STRUCTURED,
    "C9": QuestionMode.STRUCTURED, "C10": QuestionMode.STRUCTURED,
    "C11": QuestionMode.STRUCTURED, "C12": QuestionMode.STRUCTURED,
    # Finance (F1–F5): structured
    "F1": QuestionMode.STRUCTURED, "F2": QuestionMode.STRUCTURED,
    "F3": QuestionMode.STRUCTURED, "F4": QuestionMode.STRUCTURED,
    "F5": QuestionMode.STRUCTURED,
    # Creativity (CR1–CR3): structured
    "CR1": QuestionMode.STRUCTURED, "CR2": QuestionMode.STRUCTURED,
    "CR3": QuestionMode.STRUCTURED,
    # Relationships (R1–R7): conversational — empathy over efficiency
    "R1": QuestionMode.CONVERSATIONAL, "R2": QuestionMode.CONVERSATIONAL,
    "R3": QuestionMode.CONVERSATIONAL, "R4": QuestionMode.CONVERSATIONAL,
    "R5": QuestionMode.CONVERSATIONAL, "R6": QuestionMode.CONVERSATIONAL,
    "R7": QuestionMode.CONVERSATIONAL,
    # Health / mental wellness (H1–H6): conversational
    "H1": QuestionMode.CONVERSATIONAL, "H2": QuestionMode.CONVERSATIONAL,
    "H3": QuestionMode.CONVERSATIONAL, "H4": QuestionMode.CONVERSATIONAL,
    "H5": QuestionMode.CONVERSATIONAL, "H6": QuestionMode.CONVERSATIONAL,
    # Memories (M1–M3): conversational — reflection, not interrogation
    "M1": QuestionMode.CONVERSATIONAL, "M2": QuestionMode.CONVERSATIONAL,
    "M3": QuestionMode.CONVERSATIONAL,
    # Personal journaling (P3) and identity (P5): conversational
    "P3": QuestionMode.CONVERSATIONAL, "P5": QuestionMode.CONVERSATIONAL,
    # Goals (P1), habits (P2), learning (P4), review (P6): hybrid
    "P1": QuestionMode.HYBRID, "P2": QuestionMode.HYBRID,
    "P4": QuestionMode.HYBRID, "P6": QuestionMode.HYBRID,
}

_DEFAULT_MODE = QuestionMode.STRUCTURED


@dataclass
class FramedQuestion:
    """A question ready for delivery in the right tone."""
    question_text: str              # The core question
    question_mode: QuestionMode     # Mode this was framed for
    progress_label: Optional[str]   # "Q3 of 8" or None if conversational
    transition: Optional[str]       # Opening phrase before the question
    use_case_id: str = ""


@dataclass
class FramingConfig:
    """Configuration for a session's question delivery style."""
    use_case_id: str
    mode: QuestionMode
    show_progress: bool                    # Whether to show Q-of-N label
    show_explicit_transitions: bool        # "Theek hai, ab next..." visible?
    expert_signature_phrases: List[str] = field(default_factory=list)

    @classmethod
    def from_use_case(cls, use_case_id: str) -> "FramingConfig":
        """Build framing config from use case ID."""
        mode = _USE_CASE_MODE.get(use_case_id, _DEFAULT_MODE)
        return cls(
            use_case_id=use_case_id,
            mode=mode,
            show_progress=(mode in (QuestionMode.STRUCTURED, QuestionMode.HYBRID)),
            show_explicit_transitions=(mode == QuestionMode.STRUCTURED),
        )


# Conversational transition openers — organic, not mechanical
_CONVERSATIONAL_OPENERS = [
    "Aur...",
    "Interesting.",
    "Hm.",
    "Suno...",
    "Ek cheez aur —",
    "Us baat se yaad aaya —",
    "Agar thoda aur peeche jaayein —",
    "Tell me more —",
]

# Structured transition openers — explicit, efficient
_STRUCTURED_OPENERS = [
    "Theek hai, ab next topic —",
    "Got it. Moving on —",
    "Samajh gaya. Ab —",
    "Okay, next question:",
]

# Hybrid openers — structured frame, warm delivery
_HYBRID_OPENERS = [
    "Accha, is track par —",
    "Thoda aur detail mein —",
    "Ek related cheez —",
]


class ConversationalFramer:
    """
    Frames questions in the appropriate delivery style based on use case.

    Usage:
        framer = ConversationalFramer()
        framed = framer.frame_question(
            use_case_id="R2",
            question_text="Us moment mein andar kya hua?",
            question_index=2,
            total_questions=6,
        )
    """

    def get_mode(self, use_case_id: str) -> QuestionMode:
        """Return the QuestionMode for a given use case ID."""
        return _USE_CASE_MODE.get(use_case_id, _DEFAULT_MODE)

    def get_config(self, use_case_id: str) -> FramingConfig:
        """Return the full FramingConfig for a use case."""
        return FramingConfig.from_use_case(use_case_id)

    def frame_question(
        self,
        use_case_id: str,
        question_text: str,
        question_index: int,        # 0-based
        total_questions: int,
        opener_index: int = 0,      # Which opener to pick (for variety)
    ) -> FramedQuestion:
        """
        Frame a question for delivery in the correct mode.

        Args:
            use_case_id: e.g. "C1", "R3", "P2"
            question_text: The raw question text
            question_index: 0-based position in sequence
            total_questions: Total questions in session
            opener_index: Index into opener list (for rotation)

        Returns:
            FramedQuestion ready for display
        """
        mode = self.get_mode(use_case_id)
        config = FramingConfig.from_use_case(use_case_id)

        progress_label: Optional[str] = None
        transition: Optional[str] = None

        if mode == QuestionMode.STRUCTURED:
            progress_label = f"Q{question_index + 1} of {total_questions}"
            if question_index > 0:
                openers = _STRUCTURED_OPENERS
                transition = openers[opener_index % len(openers)]

        elif mode == QuestionMode.CONVERSATIONAL:
            # No progress label, no mechanical transitions
            if question_index > 0:
                openers = _CONVERSATIONAL_OPENERS
                transition = openers[opener_index % len(openers)]

        elif mode == QuestionMode.HYBRID:
            # Show progress but use warm openers
            progress_label = f"Q{question_index + 1} of {total_questions}"
            if question_index > 0:
                openers = _HYBRID_OPENERS
                transition = openers[opener_index % len(openers)]

        return FramedQuestion(
            question_text=question_text,
            question_mode=mode,
            progress_label=progress_label,
            transition=transition,
            use_case_id=use_case_id,
        )

    def render(self, framed: FramedQuestion) -> str:
        """
        Render a FramedQuestion to the final display string.

        Args:
            framed: FramedQuestion to render

        Returns:
            Display string ready to show user
        """
        parts = []

        if framed.progress_label:
            parts.append(f"**{framed.progress_label}**")

        if framed.transition:
            parts.append(framed.transition)

        parts.append(framed.question_text)

        # STRUCTURED: join with separator; CONVERSATIONAL: keep it flowing
        if framed.question_mode == QuestionMode.STRUCTURED:
            # "Q3 of 8 | Theek hai, ab next — Question text?"
            if len(parts) >= 3:
                return f"{parts[0]} — {parts[1]} {parts[2]}"
            elif len(parts) == 2:
                return f"{parts[0]} — {parts[1]}"
            return parts[0]
        else:
            # Conversational: newline separation feels natural
            if len(parts) >= 2:
                return "\n".join(parts)
            return parts[0]

    def render_question(
        self,
        use_case_id: str,
        question_text: str,
        question_index: int,
        total_questions: int,
        opener_index: int = 0,
    ) -> str:
        """Convenience: frame + render in one call."""
        framed = self.frame_question(
            use_case_id=use_case_id,
            question_text=question_text,
            question_index=question_index,
            total_questions=total_questions,
            opener_index=opener_index,
        )
        return self.render(framed)

    def is_conversational(self, use_case_id: str) -> bool:
        """True if this use case should use conversational (no counter) mode."""
        return self.get_mode(use_case_id) == QuestionMode.CONVERSATIONAL

    def is_structured(self, use_case_id: str) -> bool:
        """True if this use case should use structured (numbered) mode."""
        return self.get_mode(use_case_id) == QuestionMode.STRUCTURED
