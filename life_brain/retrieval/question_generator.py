"""
Alternative question generation for improved retrieval and understanding.

Generates 2-3 alternative phrasings of a question with different angles,
emphasis, and formality levels to improve retrieval and comprehension.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re


class QuestionStyle(Enum):
    """Question phrasing styles."""

    FORMAL = "formal"  # Professional, academic
    CASUAL = "casual"  # Conversational, friendly
    DIRECT = "direct"  # Straightforward, blunt
    EXPLORATORY = "exploratory"  # Open-ended, curious
    PROBLEM_FOCUSED = "problem_focused"  # What's wrong?
    SOLUTION_FOCUSED = "solution_focused"  # What's the fix?
    CONTEXT_FOCUSED = "context_focused"  # What's the situation?


@dataclass
class AlternativeQuestion:
    """Alternative phrasing of a question."""

    variant_id: str
    original_question: str
    alternative_text: str
    style: QuestionStyle
    emphasis: str  # What part is emphasized
    formality_level: int  # 1-5, 1=very casual, 5=very formal
    keywords: List[str] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "variant_id": self.variant_id,
            "original_question": self.original_question,
            "alternative_text": self.alternative_text,
            "style": self.style.value,
            "emphasis": self.emphasis,
            "formality_level": self.formality_level,
            "keywords": self.keywords,
            "generated_at": self.generated_at,
        }


@dataclass
class QuestionSet:
    """Set of alternative question phrasings."""

    question_id: str
    original_question: str
    alternatives: List[AlternativeQuestion] = field(default_factory=list)
    primary_keywords: List[str] = field(default_factory=list)
    question_type: str = "general"  # "career", "relationship", "learning", etc.
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "question_id": self.question_id,
            "original_question": self.original_question,
            "alternatives": [a.to_dict() for a in self.alternatives],
            "primary_keywords": self.primary_keywords,
            "question_type": self.question_type,
            "created_at": self.created_at,
        }


class QuestionGenerator:
    """Generate alternative question phrasings."""

    # Question type patterns
    QUESTION_PATTERNS = {
        "advice": ["advice", "should", "how to", "what should", "best way"],
        "understanding": ["what", "explain", "understand", "mean", "definition"],
        "decision": ["choose", "decide", "option", "pick", "which"],
        "problem": ["problem", "issue", "wrong", "stuck", "challenge"],
        "goal": ["goal", "want", "achieve", "reach", "accomplish"],
        "relationship": ["how to", "communicate", "deal with", "handle", "manage"],
    }

    # Transformation templates
    TRANSFORMATIONS = {
        QuestionStyle.FORMAL: {
            "prefix": "Could you please clarify: ",
            "suffix": "?",
            "replacements": {"wanna": "want to", "gonna": "going to", "gotta": "have to"},
        },
        QuestionStyle.CASUAL: {
            "prefix": "So like, ",
            "suffix": "?",
            "replacements": {"could": "can", "please": "pls", "would": "d"},
        },
        QuestionStyle.DIRECT: {
            "prefix": "",
            "suffix": "?",
            "replacements": {"could you": "tell me", "can you": "tell me"},
        },
        QuestionStyle.EXPLORATORY: {
            "prefix": "I'm curious: ",
            "suffix": " What are your thoughts?",
            "replacements": {},
        },
    }

    def __init__(self):
        """Initialize question generator."""
        self.question_sets: Dict[str, QuestionSet] = {}
        self.generation_history: List[QuestionSet] = []

    def generate_alternatives(
        self,
        question: str,
        question_type: str = "general",
        count: int = 3,
        question_id: str = "",
    ) -> Tuple[Optional[QuestionSet], Optional[str]]:
        """
        Generate alternative question phrasings.

        Args:
            question: Original question
            question_type: Type of question ("career", "relationship", etc.)
            count: Number of alternatives (2-5)
            question_id: Optional question ID

        Returns:
            (QuestionSet, error if any)
        """
        if not question or not question.strip():
            return None, "Empty question"

        if count < 2 or count > 5:
            return None, "Count must be between 2 and 5"

        if not question_id:
            question_id = f"q_{len(self.question_sets):04d}"

        # Extract keywords
        keywords = self._extract_keywords(question)

        # Create question set
        question_set = QuestionSet(
            question_id=question_id,
            original_question=question,
            primary_keywords=keywords,
            question_type=question_type,
        )

        # Generate alternatives
        styles = [QuestionStyle.FORMAL, QuestionStyle.CASUAL, QuestionStyle.DIRECT]
        if count > 3:
            styles.append(QuestionStyle.EXPLORATORY)
        if count > 4:
            styles.append(QuestionStyle.PROBLEM_FOCUSED)

        for i, style in enumerate(styles[:count]):
            alternative = self._generate_alternative(
                question, keywords, style, i
            )
            question_set.alternatives.append(alternative)

        # Store
        self.question_sets[question_id] = question_set
        self.generation_history.append(question_set)

        return question_set, None

    def _extract_keywords(self, question: str) -> List[str]:
        """Extract key terms from question."""
        keywords = []

        # Remove common words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at",
            "to", "for", "of", "with", "by", "from", "is", "are", "be",
            "do", "does", "did", "can", "could", "would", "should", "may",
            "might", "must", "will", "shall", "have", "has", "had"
        }

        words = re.findall(r'\b\w+\b', question.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 3]

        return list(set(keywords))[:5]  # Top 5 unique

    def _generate_alternative(
        self,
        question: str,
        keywords: List[str],
        style: QuestionStyle,
        index: int,
    ) -> AlternativeQuestion:
        """Generate single alternative phrasing."""
        variant_id = f"var_{index}"

        # Apply style transformation
        if style == QuestionStyle.FORMAL:
            alternative = self._transform_formal(question)
            emphasis = "formality"
            formality = 5
        elif style == QuestionStyle.CASUAL:
            alternative = self._transform_casual(question)
            emphasis = "conversational"
            formality = 1
        elif style == QuestionStyle.DIRECT:
            alternative = self._transform_direct(question)
            emphasis = "directness"
            formality = 3
        elif style == QuestionStyle.EXPLORATORY:
            alternative = self._transform_exploratory(question)
            emphasis = "curiosity"
            formality = 2
        elif style == QuestionStyle.PROBLEM_FOCUSED:
            alternative = self._transform_problem_focused(question)
            emphasis = "problem definition"
            formality = 3
        else:  # SOLUTION_FOCUSED
            alternative = self._transform_solution_focused(question)
            emphasis = "solution focus"
            formality = 3

        return AlternativeQuestion(
            variant_id=variant_id,
            original_question=question,
            alternative_text=alternative,
            style=style,
            emphasis=emphasis,
            formality_level=formality,
            keywords=keywords,
        )

    def _transform_formal(self, question: str) -> str:
        """Transform to formal style."""
        # Remove contractions
        text = question.replace("don't", "do not")
        text = text.replace("can't", "cannot")
        text = text.replace("won't", "will not")

        # Add formal prefix
        if not text.lower().startswith(("could you", "would you", "can you")):
            text = "Could you please clarify: " + text

        # Ensure question mark
        if not text.endswith("?"):
            text += "?"

        return text

    def _transform_casual(self, question: str) -> str:
        """Transform to casual style."""
        text = question.lower()

        # Add casual prefix
        if not text.startswith(("so ", "like ", "hey ")):
            text = "So like, " + text

        # Remove "please"
        text = text.replace(" please", "")

        if not text.endswith("?"):
            text += "?"

        return text

    def _transform_direct(self, question: str) -> str:
        """Transform to direct style."""
        text = question.strip()

        # Remove politeness markers
        text = text.replace("Could you please", "Tell me")
        text = text.replace("Could you", "Tell me")
        text = text.replace("Can you", "Tell me")
        text = text.replace("Would you", "Tell me")

        if not text.endswith("?"):
            text += "?"

        return text

    def _transform_exploratory(self, question: str) -> str:
        """Transform to exploratory style."""
        text = "I'm curious about something: " + question.lower()

        if not text.endswith(("?", ".")):
            text += "?"

        # Add exploratory suffix
        text += " What are your thoughts?"

        return text

    def _transform_problem_focused(self, question: str) -> str:
        """Transform to problem-focused style."""
        text = question.lower()

        # Emphasize the problem
        if "how to" in text or "should i" in text:
            text = "What's the main challenge with " + text.replace(
                "how to", ""
            ).replace("should i", "")

        if not text.endswith("?"):
            text += "?"

        return text

    def _transform_solution_focused(self, question: str) -> str:
        """Transform to solution-focused style."""
        text = question.lower()

        # Emphasize solutions
        if "problem" in text or "wrong" in text:
            text = text.replace("what's wrong", "how can we fix")
            text = text.replace("problem", "solution")

        if not text.endswith("?"):
            text += "?"

        return text

    def get_question_set(self, question_id: str) -> Optional[QuestionSet]:
        """Get specific question set."""
        return self.question_sets.get(question_id)

    def get_alternative_by_style(
        self, question_id: str, style: QuestionStyle
    ) -> Optional[AlternativeQuestion]:
        """Get alternative with specific style."""
        q_set = self.question_sets.get(question_id)
        if not q_set:
            return None

        for alt in q_set.alternatives:
            if alt.style == style:
                return alt

        return None

    def export_question_set(self, question_id: str) -> Optional[Dict[str, Any]]:
        """Export question set."""
        q_set = self.question_sets.get(question_id)
        if not q_set:
            return None
        return q_set.to_dict()

    def export_all_question_sets(self) -> List[Dict[str, Any]]:
        """Export all question sets."""
        return [q.to_dict() for q in self.generation_history]

    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get statistics about generation."""
        if not self.generation_history:
            return {
                "total_questions": 0,
                "total_alternatives": 0,
                "by_type": {},
                "by_style": {},
                "avg_keywords_per_question": 0,
            }

        total_alternatives = 0
        by_type = {}
        by_style = {}
        total_keywords = 0

        for q_set in self.generation_history:
            # Count by type
            q_type = q_set.question_type
            by_type[q_type] = by_type.get(q_type, 0) + 1

            # Count alternatives by style
            for alt in q_set.alternatives:
                total_alternatives += 1
                style = alt.style.value
                by_style[style] = by_style.get(style, 0) + 1

            # Track keywords
            total_keywords += len(q_set.primary_keywords)

        avg_keywords = (
            total_keywords / len(self.generation_history)
            if self.generation_history
            else 0
        )

        return {
            "total_questions": len(self.generation_history),
            "total_alternatives": total_alternatives,
            "by_type": by_type,
            "by_style": by_style,
            "avg_keywords_per_question": avg_keywords,
        }

    def batch_generate(
        self, questions: List[str], question_type: str = "general"
    ) -> Tuple[List[QuestionSet], Optional[str]]:
        """Batch generate for multiple questions."""
        question_sets = []

        for question in questions:
            q_set, error = self.generate_alternatives(
                question, question_type, count=3
            )
            if q_set:
                question_sets.append(q_set)

        return question_sets, None

    def get_most_effective_variations(
        self, question_id: str
    ) -> Optional[List[AlternativeQuestion]]:
        """Get variations in recommended order."""
        q_set = self.question_sets.get(question_id)
        if not q_set:
            return None

        # Order by style: Direct > Casual > Formal > Exploratory
        priority = {
            QuestionStyle.DIRECT: 1,
            QuestionStyle.CASUAL: 2,
            QuestionStyle.FORMAL: 3,
            QuestionStyle.EXPLORATORY: 4,
            QuestionStyle.PROBLEM_FOCUSED: 5,
            QuestionStyle.SOLUTION_FOCUSED: 6,
            QuestionStyle.CONTEXT_FOCUSED: 7,
        }

        sorted_alts = sorted(
            q_set.alternatives, key=lambda a: priority.get(a.style, 99)
        )

        return sorted_alts
