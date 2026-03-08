"""
Structural CE (Collectively Exhaustive) validation.

Uses NLP-based atom extraction (no LLM) to verify that Q&A pairs
collectively cover all key information atoms in the raw answer.

Atoms extracted: entities, numbers, key verbs — matched against QA text.
"""

import re
from typing import List, Tuple, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from life_brain.pipelines.qa_generator import QAPair


# Common stopwords to filter from verb atoms
_STOPVERBS = {
    "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might",
    "get", "got", "make", "made", "go", "went",
}


def _extract_numbers(text: str) -> Set[str]:
    """Extract numeric tokens (integers, decimals, percentages)."""
    return set(re.findall(r"\b\d+(?:[.,]\d+)?%?", text))


def _extract_entities(text: str) -> Set[str]:
    """
    Extract capitalized multi-word tokens as named entities.

    Heuristic: sequences of Title-Case words (2+ chars each).
    """
    entities = set()
    # Match Title Case words (min 2 chars, not at sentence start ambiguity)
    pattern = re.compile(r"\b([A-Z][a-z]{1,}(?:\s+[A-Z][a-z]{1,})*)\b")
    for match in pattern.finditer(text):
        entity = match.group(1)
        # Skip single common words that happen to be capitalized at line start
        words = entity.split()
        if len(words) >= 2 or (len(words) == 1 and len(entity) >= 4):
            entities.add(entity.lower())
    return entities


def _extract_key_verbs(text: str) -> Set[str]:
    """
    Extract meaningful verbs using simple word-based heuristics.

    Uses -ed / -ing / -tion endings as proxy for key action words,
    filtered against common stopverbs.
    """
    words = re.findall(r"\b[a-z]{4,}\b", text.lower())
    key_verbs = set()
    for word in words:
        if word in _STOPVERBS:
            continue
        # Keep action-like words: past tense (-ed), gerunds (-ing), nouns(-tion/-ment)
        if (word.endswith("ed") or word.endswith("ing") or
                word.endswith("tion") or word.endswith("ment") or
                word.endswith("ize") or word.endswith("ise")):
            key_verbs.add(word)
    return key_verbs


def extract_atoms(text: str) -> dict:
    """
    Extract structural atoms from text.

    Returns:
        {
            "numbers": set of numeric tokens,
            "entities": set of lowercased named-entity-like phrases,
            "key_verbs": set of meaningful verb-like words,
        }
    """
    return {
        "numbers": _extract_numbers(text),
        "entities": _extract_entities(text),
        "key_verbs": _extract_key_verbs(text),
    }


def _qa_pairs_text(qa_pairs: list) -> str:
    """Concatenate all question + answer text from QA pairs."""
    parts = []
    for pair in qa_pairs:
        if hasattr(pair, "primary_question"):
            parts.append(pair.primary_question)
        elif hasattr(pair, "question"):
            parts.append(pair.question)
        if hasattr(pair, "answer"):
            parts.append(pair.answer)
        if hasattr(pair, "alt_questions"):
            parts.extend(pair.alt_questions)
    return " ".join(parts)


def structural_ce_check(
    raw_answer: str,
    qa_pairs: list,
    min_atom_coverage: float = 0.7,
) -> Tuple[bool, List[str]]:
    """
    Structural CE check: verify Q&A pairs cover key atoms from raw answer.

    Uses NLP-based atom extraction (no LLM) to check collective exhaustiveness.

    Args:
        raw_answer: The original raw answer text.
        qa_pairs: List of QAPair objects (or any object with question/answer attrs).
        min_atom_coverage: Fraction of atoms that must be covered (default 0.7).

    Returns:
        (is_exhaustive, missing_atoms) where:
            is_exhaustive: True if coverage >= min_atom_coverage
            missing_atoms: List of atom strings not found in any QA pair
    """
    if not raw_answer or not qa_pairs:
        return bool(qa_pairs), []

    # Extract atoms from the raw answer
    raw_atoms = extract_atoms(raw_answer)
    all_raw_atoms: Set[str] = (
        raw_atoms["numbers"] | raw_atoms["entities"] | raw_atoms["key_verbs"]
    )

    if not all_raw_atoms:
        return True, []

    # Build searchable text from all QA pairs
    qa_text = _qa_pairs_text(qa_pairs).lower()

    # Check coverage for each atom
    missing = []
    for atom in all_raw_atoms:
        atom_lower = atom.lower()
        if atom_lower not in qa_text:
            missing.append(atom)

    total = len(all_raw_atoms)
    covered = total - len(missing)
    coverage = covered / total if total > 0 else 1.0

    return coverage >= min_atom_coverage, missing
