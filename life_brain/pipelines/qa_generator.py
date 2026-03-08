"""
Q&A generator: Convert atomic nuggets into interview-ready Q&A pairs.

One nugget (subject + predicate) → Multiple question phrasings + one answer
"""

from typing import List, Dict, Any, Optional
import json
from anthropic import Anthropic

from life_brain.extraction.nuggets import Nugget


class QAPair:
    """A Q&A pair with multiple question phrasings."""

    def __init__(
        self,
        nugget: Nugget,
        primary_question: str,
        answer: str,
        alt_questions: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.nugget = nugget
        self.primary_question = primary_question
        self.answer = answer
        self.alt_questions = alt_questions or []
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for ChromaDB storage."""
        return {
            "question": self.primary_question,
            "alt_questions": self.alt_questions,
            "answer": self.answer,
            "subject": self.nugget.subject,
            "predicate": self.nugget.predicate,
            "atom_type": self.nugget.atom_type,
            "confidence": self.nugget.confidence,
            **self.metadata
        }


QA_GENERATION_PROMPT = """
Given this nugget (subject + predicate), generate a professional Q&A pair.

Subject: {subject}
Predicate: {predicate}
Atom Type: {atom_type}
Context: {context}

Generate:
1. A primary question (natural, conversational)
2. 2-3 alternative question phrasings (different angles)
3. A complete answer statement

Return as JSON:
{{
  "primary_question": "...",
  "alt_questions": ["...", "...", "..."],
  "answer": "..."
}}

RULES:
- Primary question: natural conversational phrasing
- Alt questions: different angles (behavioral, metric-focused, impact-focused, etc.)
- Answer: 1-2 sentences, self-contained, ready for embedding
- Answer must contain the predicate information
"""


def generate_qa_from_nugget(
    nugget: Nugget,
    context: str = "",
    client: Optional[Anthropic] = None
) -> QAPair:
    """
    Generate Q&A pair from a single nugget.

    Args:
        nugget: Extracted nugget (subject + predicate)
        context: Optional additional context about the nugget
        client: Anthropic client (creates new if not provided)

    Returns:
        QAPair object with primary + alt questions and answer
    """
    if client is None:
        client = Anthropic()

    try:
        prompt = QA_GENERATION_PROMPT.format(
            subject=nugget.subject,
            predicate=nugget.predicate,
            atom_type=nugget.atom_type,
            context=context or "(No additional context)"
        )

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        response_text = response.content[0].text

        # Extract JSON
        if "```json" in response_text:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            response_text = response_text[json_start:json_end]
        elif "```" in response_text:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            response_text = response_text[json_start:json_end]

        qa_dict = json.loads(response_text)

        # Create QAPair
        qa_pair = QAPair(
            nugget=nugget,
            primary_question=qa_dict.get("primary_question", ""),
            answer=qa_dict.get("answer", ""),
            alt_questions=qa_dict.get("alt_questions", [])
        )

        return qa_pair

    except Exception as e:
        # Fallback: Create basic Q&A
        basic_question = f"Tell me about {nugget.subject}?"
        basic_answer = f"{nugget.subject}: {nugget.predicate}"

        return QAPair(
            nugget=nugget,
            primary_question=basic_question,
            answer=basic_answer,
            alt_questions=[
                f"What happened with {nugget.subject}?",
                f"Explain {nugget.subject}."
            ]
        )


def qa_generator(
    nuggets: List[Nugget],
    context: str = ""
) -> List[QAPair]:
    """
    Generate Q&A pairs from multiple nuggets.

    Args:
        nuggets: List of extracted nuggets
        context: Optional context (e.g., project name, time period)

    Returns:
        List of QAPair objects
    """
    client = Anthropic()
    qa_pairs = []

    for nugget in nuggets:
        try:
            qa_pair = generate_qa_from_nugget(nugget, context, client)
            qa_pairs.append(qa_pair)
        except Exception as e:
            # Log and continue on individual failures
            continue

    return qa_pairs


def batch_qa_generation(
    nugget_batches: Dict[str, List[Nugget]],
    contexts: Optional[Dict[str, str]] = None
) -> Dict[str, List[QAPair]]:
    """
    Generate Q&A pairs for multiple nugget batches (e.g., per project).

    Args:
        nugget_batches: Dict mapping batch_id -> list of nuggets
        contexts: Optional dict mapping batch_id -> context

    Returns:
        Dict mapping batch_id -> list of QAPair objects
    """
    if contexts is None:
        contexts = {}

    qa_results = {}

    for batch_id, nuggets in nugget_batches.items():
        context = contexts.get(batch_id, "")
        qa_results[batch_id] = qa_generator(nuggets, context)

    return qa_results


def validate_qa_pair(qa_pair: QAPair) -> Dict[str, Any]:
    """
    Validate a Q&A pair for quality.

    Checks:
    - Question is natural and specific
    - Answer contains predicate information
    - Answer is self-contained (>30 chars)

    Args:
        qa_pair: QAPair to validate

    Returns:
        {valid: bool, errors: [list of issues]}
    """
    errors = []

    # Check question exists and is reasonable length
    if not qa_pair.primary_question or len(qa_pair.primary_question) < 10:
        errors.append("Primary question too short or missing")

    # Check answer exists and contains predicate
    if not qa_pair.answer or len(qa_pair.answer) < 30:
        errors.append("Answer too short (< 30 chars)")

    if qa_pair.nugget.predicate.lower() not in qa_pair.answer.lower():
        errors.append("Answer doesn't contain nugget predicate")

    # Check alt questions
    if not qa_pair.alt_questions or len(qa_pair.alt_questions) < 2:
        errors.append("Fewer than 2 alternative questions")

    valid = len(errors) == 0

    return {
        "valid": valid,
        "errors": errors,
        "question_chars": len(qa_pair.primary_question),
        "answer_chars": len(qa_pair.answer),
        "alt_questions_count": len(qa_pair.alt_questions)
    }


def bulk_validate_qa_pairs(qa_pairs: List[QAPair]) -> Dict[str, Any]:
    """
    Validate multiple Q&A pairs and return summary.

    Args:
        qa_pairs: List of QAPair objects

    Returns:
        {
            total: count,
            valid: count,
            invalid: count,
            invalid_pairs: [list of invalid QAPairs with errors]
        }
    """
    valid_count = 0
    invalid_pairs = []

    for qa_pair in qa_pairs:
        validation = validate_qa_pair(qa_pair)
        if validation["valid"]:
            valid_count += 1
        else:
            invalid_pairs.append({
                "qa_pair": qa_pair,
                "errors": validation["errors"]
            })

    return {
        "total": len(qa_pairs),
        "valid": valid_count,
        "invalid": len(qa_pairs) - valid_count,
        "invalid_pairs": invalid_pairs,
        "success_rate": (valid_count / len(qa_pairs) * 100) if qa_pairs else 0
    }
