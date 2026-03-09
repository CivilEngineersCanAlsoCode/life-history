"""
Auto-generate alternative question phrasings for atomic facts.

For each Q&A pair, generates 2-3 alternative ways to ask the same question
so retrieval handles paraphrasing and users can find answers regardless of phrasing.
"""

from typing import Dict, List, Optional, Tuple
import re


# Question transformation templates
_TRANSFORMATIONS = [
    # How/What swaps
    ("what was your", "how did you"),
    ("how did you", "what was your approach to"),
    ("what did you do", "how did you handle"),
    ("what is", "can you describe"),
    ("can you tell me about", "what was"),
    ("describe your", "what was your experience with"),
    # Passive/active reframe
    ("what were the results", "what impact did you have"),
    ("what happened when", "what was the outcome when"),
    ("what was the impact of", "how did"),
    # Specificity rewrites
    ("how did you", "walk me through how you"),
    ("what role did you play", "what was your contribution to"),
    ("what challenges did you face", "what obstacles came up during"),
    ("what skills did you use", "what capabilities did you demonstrate in"),
]

# Domain-specific question patterns
_DOMAIN_PATTERNS: Dict[str, List[str]] = {
    "career": [
        "What was your specific contribution to {topic}?",
        "Can you walk me through your role in {topic}?",
        "How did you approach {topic}?",
    ],
    "metric": [
        "What were the measurable results of {topic}?",
        "How did you quantify the impact of {topic}?",
        "What numbers or metrics can you share about {topic}?",
    ],
    "technical": [
        "What technologies did you use for {topic}?",
        "How did you technically implement {topic}?",
        "What was the architecture behind {topic}?",
    ],
    "challenge": [
        "What obstacles did you face with {topic}?",
        "How did you overcome challenges in {topic}?",
        "What went wrong and how did you fix it in {topic}?",
    ],
}


def generate_alt_phrasings(
    question: str,
    domain: Optional[str] = None,
    count: int = 2,
) -> List[str]:
    """Generate alternative phrasings for a question.

    Args:
        question: Original question text
        domain: Optional domain for domain-specific alternatives (career, metric, technical)
        count: Number of alternatives to generate (default 2)

    Returns:
        List of alternative question strings
    """
    if not question or not question.strip():
        return []

    alts = set()
    lower_q = question.lower().strip().rstrip("?")

    # Apply transformations
    for old, new in _TRANSFORMATIONS:
        if old in lower_q:
            alt = lower_q.replace(old, new, 1)
            alt = alt.strip().capitalize()
            if not alt.endswith("?"):
                alt += "?"
            if alt.lower() != question.lower():
                alts.add(alt)
        if len(alts) >= count:
            break

    # Add domain-specific alternatives if provided
    if domain and domain.lower() in _DOMAIN_PATTERNS:
        topic = _extract_topic(question)
        patterns = _DOMAIN_PATTERNS[domain.lower()]
        for pattern in patterns:
            if topic:
                alt = pattern.format(topic=topic)
                if alt.lower() != question.lower():
                    alts.add(alt)
            if len(alts) >= count:
                break

    # Fallback: generic rewrites
    if len(alts) < count:
        fallbacks = _generate_fallback_phrasings(question)
        for fb in fallbacks:
            if len(alts) >= count:
                break
            if fb.lower() != question.lower():
                alts.add(fb)

    return list(alts)[:count]


def generate_phrasings_for_fact(
    question: str,
    answer: str,
    domain: Optional[str] = None,
) -> List[str]:
    """Generate 2-3 alt phrasings for an atomic fact's question.

    Args:
        question: The canonical question
        answer: The answer (used for context clues)
        domain: Optional domain for targeted phrasings

    Returns:
        List of 2-3 alternative phrasings
    """
    # Infer domain from answer if not provided
    if not domain:
        domain = _infer_domain_from_answer(answer)

    alts = generate_alt_phrasings(question, domain=domain, count=3)
    return alts


def _extract_topic(question: str) -> Optional[str]:
    """Extract the main topic/noun phrase from a question."""
    # Remove question words and get the remaining topic
    cleaned = re.sub(
        r"^(?:what|how|when|why|who|describe|tell me about|can you tell me|walk me through)\s+",
        "",
        question.lower().strip().rstrip("?"),
        flags=re.IGNORECASE,
    )
    # Remove common starters
    cleaned = re.sub(r"^(?:was|were|did|your|you|the|a|an)\s+", "", cleaned)

    # Get first 5 words max as topic
    topic_words = cleaned.split()[:5]
    if not topic_words:
        return None
    return " ".join(topic_words)


def _infer_domain_from_answer(answer: str) -> Optional[str]:
    """Infer domain from answer content."""
    lower = answer.lower()

    metric_keywords = ["%", "x faster", "reduced", "increased", "users", "latency"]
    if any(kw in lower for kw in metric_keywords):
        return "metric"

    tech_keywords = ["api", "database", "code", "deploy", "python", "java", "sql"]
    if any(kw in lower for kw in tech_keywords):
        return "technical"

    challenge_keywords = ["challenge", "obstacle", "problem", "issue", "difficult"]
    if any(kw in lower for kw in challenge_keywords):
        return "challenge"

    return "career"  # Default domain


def _generate_fallback_phrasings(question: str) -> List[str]:
    """Generate generic fallback alternative phrasings."""
    q = question.strip().rstrip("?")
    alts = []

    # "Tell me about X" -> "Describe X"
    if q.lower().startswith("tell me about"):
        topic = q[13:].strip()
        alts.append(f"Describe {topic}?")
        alts.append(f"What is your experience with {topic}?")

    # "What was your X" -> "Can you describe your X"
    elif "what was your" in q.lower():
        alt = q.lower().replace("what was your", "can you describe your")
        alts.append(alt.capitalize() + "?")

    # "How did you" -> "What was your approach to"
    elif "how did you" in q.lower():
        alt = q.lower().replace("how did you", "what was your approach to")
        alts.append(alt.capitalize() + "?")

    else:
        # Generic prefixes
        alts.append(f"Can you elaborate on: {q}?")
        alts.append(f"Please describe: {q}?")

    return alts
