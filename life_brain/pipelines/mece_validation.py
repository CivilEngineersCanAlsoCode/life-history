"""
MECE validation pipeline: Mutual Exclusivity + Collectively Exhaustive checks.

ME check: Deduplicate near-identical nuggets (cosine_sim > 0.85)
CE check: Verify all structural elements from raw answer are captured
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from life_brain.utils.claude_cli import Anthropic  # Claude CLI, no API key needed

from life_brain.extraction.nuggets import Nugget


def calculate_nugget_similarity(nugget1: Nugget, nugget2: Nugget) -> float:
    """
    Calculate semantic similarity between two nuggets.

    Uses string representation since nuggets don't have pre-computed embeddings yet.

    Args:
        nugget1: First nugget
        nugget2: Second nugget

    Returns:
        Similarity score (0-1)
    """
    # Combine subject + predicate for comparison
    text1 = f"{nugget1.subject} {nugget1.predicate}".lower()
    text2 = f"{nugget2.subject} {nugget2.predicate}".lower()

    # Simple word overlap based similarity as fallback (before embedding)
    words1 = set(text1.split())
    words2 = set(text2.split())

    if not words1 or not words2:
        return 0.0

    intersection = len(words1 & words2)
    union = len(words1 | words2)

    return intersection / union if union > 0 else 0.0


def me_check(nuggets: List[Nugget]) -> List[Nugget]:
    """
    Mutual Exclusivity validation: Remove duplicate nuggets.

    If two nuggets are semantically similar (cosine_sim > 0.85),
    keep only the one with highest confidence.

    Args:
        nuggets: List of extracted nuggets

    Returns:
        Deduplicated nugget list
    """
    if len(nuggets) <= 1:
        return nuggets

    deduplicated = []
    used_indices = set()

    for i, nugget1 in enumerate(nuggets):
        if i in used_indices:
            continue

        # Check against all remaining nuggets
        duplicates = [nugget1]
        for j, nugget2 in enumerate(nuggets):
            if i != j and j not in used_indices:
                similarity = calculate_nugget_similarity(nugget1, nugget2)

                if similarity > 0.85:  # Threshold for near-duplicates
                    duplicates.append(nugget2)
                    used_indices.add(j)

        # Keep the one with highest confidence
        best_nugget = max(duplicates, key=lambda n: n.confidence)
        deduplicated.append(best_nugget)
        used_indices.add(i)

    return deduplicated


def ce_check(
    nuggets: List[Nugget],
    raw_atoms: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    Collectively Exhaustive validation: Check if nuggets capture all raw atoms.

    Verifies that entities, numbers, verbs, dates from raw answer
    are represented in extracted nuggets.

    Args:
        nuggets: List of extracted nuggets
        raw_atoms: Dict from extract_atoms_from_raw() with entities, numbers, verbs, dates

    Returns:
        Tuple of (is_valid, missing_items)
    """
    missing_items = []
    nugget_text = " ".join([f"{n.subject} {n.predicate}" for n in nuggets]).lower()

    # Check if all numbers are represented
    for number in raw_atoms.get("numbers", []):
        if str(number) not in nugget_text:
            missing_items.append(f"number: {number}")

    # Check if all dates are represented
    for date in raw_atoms.get("dates", []):
        if date.lower() not in nugget_text:
            missing_items.append(f"date: {date}")

    # Check if key verbs are represented
    # (Not all verbs need explicit representation, so be lenient)
    key_verbs = raw_atoms.get("verbs", [])[:3]  # Check top 3 verbs only
    verbs_found = 0
    for verb in key_verbs:
        if verb.lower() in nugget_text:
            verbs_found += 1

    if len(key_verbs) > 0 and verbs_found < len(key_verbs) // 2:
        missing_items.append(f"verbs: only {verbs_found}/{len(key_verbs)} represented")

    # Check if major entities are represented
    entities = raw_atoms.get("entities", [])[:5]  # Check top 5 entities
    for entity in entities:
        if entity.get("text", "").lower() not in nugget_text:
            missing_items.append(f"entity: {entity.get('text')} ({entity.get('label')})")

    is_valid = len(missing_items) == 0

    return is_valid, missing_items


def ce_gap_resolution(
    nuggets: List[Nugget],
    raw_answer: str,
    missing_items: List[str]
) -> List[Nugget]:
    """
    Resolve CE gaps by creating new nuggets for missing elements.

    Args:
        nuggets: Current extracted nuggets
        raw_answer: Original raw answer
        missing_items: List of missing structural elements

    Returns:
        Updated nugget list with gap-filling nuggets
    """
    if not missing_items:
        return nuggets

    client = Anthropic()

    try:
        prompt = f"""Given this raw answer and these MISSING structural elements, create minimal nuggets to fill gaps.

Raw answer: "{raw_answer}"

Missing elements: {', '.join(missing_items)}

Create ONLY the minimal nuggets needed to capture these missing elements. Return JSON format:
[
  {{"subject": "...", "predicate": "...", "atom_type": "METRIC|FACT|STORY|DECISION|LESSON"}},
  ...
]"""

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        import json
        response_text = response.content[0].text

        # Extract JSON
        if "```json" in response_text:
            json_start = response_text.find("[")
            json_end = response_text.rfind("]") + 1
            response_text = response_text[json_start:json_end]

        new_nuggets_dict = json.loads(response_text)

        # Convert to Nugget objects
        for nugget_dict in new_nuggets_dict:
            new_nugget = Nugget(
                subject=nugget_dict.get("subject", ""),
                predicate=nugget_dict.get("predicate", ""),
                atom_type=nugget_dict.get("atom_type", "FACT"),
                confidence=0.7  # Lower confidence for AI-inferred gaps
            )
            nuggets.append(new_nugget)

    except Exception as e:
        # On error, return without gap-filling
        pass

    return nuggets


def validate_mece(
    nuggets: List[Nugget],
    raw_answer: str,
    raw_atoms: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Full MECE validation: ME check + CE check + gap resolution.

    Args:
        nuggets: Extracted nuggets
        raw_answer: Original raw answer text
        raw_atoms: Structural atoms from extract_atoms_from_raw()

    Returns:
        {
            "nuggets": validated_nuggets,
            "me_deduplicated": count_removed,
            "ce_valid": bool,
            "ce_gaps": list_of_gaps,
            "ce_gaps_resolved": bool
        }
    """
    # Step 1: ME check (deduplication)
    original_count = len(nuggets)
    nuggets_after_me = me_check(nuggets)
    me_deduplicated = original_count - len(nuggets_after_me)

    # Step 2: CE check (structural coverage)
    ce_valid, ce_gaps = ce_check(nuggets_after_me, raw_atoms)

    # Step 3: Gap resolution if needed
    ce_gaps_resolved = ce_valid
    if not ce_valid:
        nuggets_final = ce_gap_resolution(nuggets_after_me, raw_answer, ce_gaps)
        # Re-run CE check to confirm
        ce_valid_after, remaining_gaps = ce_check(nuggets_final, raw_atoms)
        ce_gaps_resolved = ce_valid_after
    else:
        nuggets_final = nuggets_after_me

    return {
        "nuggets": nuggets_final,
        "me_deduplicated": me_deduplicated,
        "ce_valid": ce_valid,
        "ce_gaps": ce_gaps,
        "ce_gaps_resolved": ce_gaps_resolved,
        "final_count": len(nuggets_final)
    }
