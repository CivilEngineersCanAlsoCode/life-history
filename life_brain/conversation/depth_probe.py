"""
Depth probing — detect incomplete answers and generate targeted follow-up questions.

When a user's answer is vague or incomplete, automatically generates depth questions:
"Can you give an example?", "What were the specific numbers?", "Who was involved?"
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class VaguenessType(Enum):
    """Types of vagueness detected in answers."""
    NO_EXAMPLE = "no_example"         # Claims but no concrete example
    NO_METRIC = "no_metric"           # No quantification
    NO_TIMELINE = "no_timeline"       # No time context
    NO_CONTEXT = "no_context"         # Too brief to understand
    NO_OUTCOME = "no_outcome"         # Missing result/impact
    SUFFICIENT = "sufficient"         # Answer seems complete


# Vague signal keywords
_VAGUE_SIGNALS = [
    "i helped", "i worked on", "i contributed", "i was involved",
    "we did", "we worked", "we built", "i participated",
    "various", "several", "many", "some things", "stuff",
    "good", "great", "successful", "improved", "better",
    "basically", "kind of", "sort of", "i think",
]

# Depth question templates per vagueness type
_DEPTH_QUESTIONS: Dict[VaguenessType, List[str]] = {
    VaguenessType.NO_EXAMPLE: [
        "Can you give a specific example of that?",
        "What's a concrete instance where you did this?",
        "Walk me through one time this happened.",
    ],
    VaguenessType.NO_METRIC: [
        "Do you have specific numbers or metrics for that?",
        "What was the scale — how many users, how much improvement?",
        "Can you quantify the impact?",
    ],
    VaguenessType.NO_TIMELINE: [
        "When did this happen? Over what time period?",
        "How long did this take?",
        "What was the timeline?",
    ],
    VaguenessType.NO_CONTEXT: [
        "Can you tell me more about the situation?",
        "What was the context or problem you were solving?",
        "What led to this?",
    ],
    VaguenessType.NO_OUTCOME: [
        "What was the outcome or result?",
        "What impact did this have?",
        "How did it turn out?",
    ],
}

# Minimum word count for a "complete" answer
_MIN_WORD_COUNT = 20

# Keywords that suggest metrics/numbers are present
_METRIC_SIGNALS = [
    "%", "x", "times", "users", "requests", "seconds", "hours",
    "days", "weeks", "months", "million", "thousand", "latency",
    "throughput", "conversion", "revenue", "cost", "score",
]

# Timeline keywords
_TIMELINE_SIGNALS = [
    "week", "month", "year", "quarter", "q1", "q2", "q3", "q4",
    "2020", "2021", "2022", "2023", "2024", "2025",
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "oct", "nov", "dec",
    "sprint", "release",
]

# Example signals
_EXAMPLE_SIGNALS = [
    "for example", "for instance", "such as", "specifically",
    "one time", "once", "when i", "during", "project", "case",
]


@dataclass
class ProbeResult:
    """Result of depth probe analysis."""

    is_complete: bool
    vagueness_types: List[VaguenessType]
    depth_questions: List[str]
    specificity_score: float  # 0-1, higher = more specific
    explanation: str

    def primary_question(self) -> Optional[str]:
        """Get the most important follow-up question."""
        return self.depth_questions[0] if self.depth_questions else None


def detect_incomplete_answer(answer: str, question: Optional[str] = None) -> ProbeResult:
    """Detect if an answer is vague/incomplete and generate depth questions.

    Args:
        answer: The user's answer text
        question: Optional original question for context

    Returns:
        ProbeResult with vagueness analysis and follow-up questions
    """
    if not answer or not answer.strip():
        return ProbeResult(
            is_complete=False,
            vagueness_types=[VaguenessType.NO_CONTEXT],
            depth_questions=_DEPTH_QUESTIONS[VaguenessType.NO_CONTEXT][:2],
            specificity_score=0.0,
            explanation="Answer is empty.",
        )

    lower = answer.lower()
    words = answer.split()
    word_count = len(words)

    vagueness_types = []
    score = 0.0

    # Word count score (up to 0.3)
    word_score = min(0.3, word_count / 100 * 0.3)
    score += word_score

    # Check for vague signals
    has_vague_signal = any(sig in lower for sig in _VAGUE_SIGNALS)
    if has_vague_signal and word_count < 50:
        vagueness_types.append(VaguenessType.NO_EXAMPLE)
    else:
        score += 0.1

    # Check for metrics
    has_metric = any(sig in lower for sig in _METRIC_SIGNALS) or any(c.isdigit() for c in answer)
    if has_metric:
        score += 0.25
    else:
        vagueness_types.append(VaguenessType.NO_METRIC)

    # Check for timeline
    has_timeline = any(sig in lower for sig in _TIMELINE_SIGNALS)
    if has_timeline:
        score += 0.15
    else:
        vagueness_types.append(VaguenessType.NO_TIMELINE)

    # Check for examples
    has_example = any(sig in lower for sig in _EXAMPLE_SIGNALS)
    if has_example:
        score += 0.15
    else:
        if VaguenessType.NO_EXAMPLE not in vagueness_types:
            vagueness_types.append(VaguenessType.NO_EXAMPLE)

    # Check for outcome/impact
    outcome_signals = ["result", "outcome", "impact", "led to", "achieved", "reduced", "increased", "saved", "improved by"]
    has_outcome = any(sig in lower for sig in outcome_signals)
    if has_outcome:
        score += 0.05
    else:
        vagueness_types.append(VaguenessType.NO_OUTCOME)

    # Clamp score
    specificity_score = min(1.0, max(0.0, score))

    # Consider complete if score >= 0.6 and at least 20 words
    is_complete = specificity_score >= 0.6 and word_count >= _MIN_WORD_COUNT

    # Build depth questions (one per vagueness type, max 3)
    depth_questions = []
    for vtype in vagueness_types[:3]:
        questions = _DEPTH_QUESTIONS.get(vtype, [])
        if questions:
            depth_questions.append(questions[0])

    # Build explanation
    if is_complete:
        explanation = "Answer appears sufficiently specific."
    else:
        issues = [vt.value.replace("_", " ") for vt in vagueness_types]
        explanation = f"Answer may be incomplete: {', '.join(issues)}."

    return ProbeResult(
        is_complete=is_complete,
        vagueness_types=vagueness_types,
        depth_questions=depth_questions,
        specificity_score=specificity_score,
        explanation=explanation,
    )


def generate_depth_questions(answer: str, question: Optional[str] = None) -> List[str]:
    """Quick helper to get depth follow-up questions for a vague answer.

    Args:
        answer: The user's answer
        question: Optional original question

    Returns:
        List of depth follow-up questions (empty if answer is complete)
    """
    result = detect_incomplete_answer(answer, question)
    if result.is_complete:
        return []
    return result.depth_questions
