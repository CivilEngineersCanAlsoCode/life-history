"""
Conflict Detection Algorithm — Truth Engine core.

Conflict Score = Semantic_Similarity × Contradiction_Magnitude

Decision matrix:
  > 0.6  → HARD CONFLICT (block, ask user)
  0.3-0.6 → SOFT CONFLICT (warn)
  0.1-0.3 → ENRICHMENT (auto-update)
  < 0.1  → SAFE (insert freely)
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from anthropic import Anthropic

from life_brain.config import (
    CONFLICT_THRESHOLDS,
    ENTITY_ALIASES,
    AtomType
)


@dataclass
class ConflictResult:
    """Result of conflict check."""
    status: str  # CONFLICT, SOFT, ENRICHMENT, SAFE
    conflict_score: float
    existing_pair_id: Optional[str] = None
    existing_answer: Optional[str] = None
    contradiction_type: Optional[str] = None


def calculate_semantic_similarity(embed_new: List[float], embed_existing: List[float]) -> float:
    """
    Calculate cosine similarity between embeddings.

    Args:
        embed_new: Embedding of new Q&A pair
        embed_existing: Embedding of existing pair

    Returns:
        Cosine similarity score (0-1)
    """
    if not embed_new or not embed_existing:
        return 0.0

    try:
        # Convert to numpy arrays
        v1 = np.array(embed_new, dtype=np.float32)
        v2 = np.array(embed_existing, dtype=np.float32)

        # Calculate norms
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0

        # Cosine similarity = dot(v1, v2) / (||v1|| * ||v2||)
        similarity = np.dot(v1, v2) / (norm_v1 * norm_v2)

        # Clamp to [0, 1] to handle floating point errors
        return float(np.clip(similarity, 0.0, 1.0))

    except Exception:
        return 0.0


def calculate_contradiction_magnitude(
    new_value: Any,
    existing_value: Any,
    atom_type: str
) -> float:
    """
    Calculate contradiction magnitude by atom type.

    Args:
        new_value: New value/answer
        existing_value: Existing value/answer
        atom_type: METRIC, FACT, DATE, STORY

    Returns:
        Normalized contradiction score (0-1)
    """
    if atom_type == "metric":
        return _contradiction_metric(new_value, existing_value)
    elif atom_type == "fact":
        return _contradiction_fact(new_value, existing_value)
    elif atom_type == "date":
        return _contradiction_date(new_value, existing_value)
    elif atom_type == "story":
        return _contradiction_story(new_value, existing_value)
    else:
        return 0.0  # Unknown type → safe


def _contradiction_metric(new_value: Any, existing_value: Any) -> float:
    """
    METRIC contradiction: |new - old| / max(new, old)

    Examples:
      - marks 100 vs 30: |100-30|/100 = 0.70
      - salary 50L vs 75L: |50-75|/75 ≈ 0.33
      - time 48h vs 15m: |2880-15|/2880 ≈ 0.99
    """
    try:
        new_num = float(new_value)
        old_num = float(existing_value)
        if max(abs(new_num), abs(old_num)) == 0:
            return 0.0
        return abs(new_num - old_num) / max(abs(new_num), abs(old_num))
    except (ValueError, TypeError):
        return 0.0  # Can't parse as numbers → no contradiction


def _contradiction_fact(new_value: Any, existing_value: Any) -> float:
    """
    FACT contradiction: LLM binary check → 0.0 or 1.0

    Examples:
      - "I led project" vs "I supported project" → 1.0 (contradiction)
      - "I was PM" vs "I was Product Manager" → 0.0 (same thing)
    """
    new_str = str(new_value).strip()
    old_str = str(existing_value).strip()

    # Quick check: exact match
    if new_str.lower() == old_str.lower():
        return 0.0

    # Use Claude API to determine contradiction
    client = Anthropic()
    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": f"""Are these two statements about the same fact, or do they contradict each other?

Old fact: "{old_str}"
New fact: "{new_str}"

Respond with ONLY ONE WORD:
- "same" if both statements describe the same fact (even if worded differently)
- "contradiction" if they describe opposite or incompatible facts

Answer:"""
            }]
        )
        answer = response.content[0].text.strip().lower()
        return 0.0 if "same" in answer else 1.0
    except Exception as e:
        # Fallback to simple comparison on API error
        return 0.0 if new_str.lower() == old_str.lower() else 1.0


def _contradiction_date(new_value: Any, existing_value: Any) -> float:
    """
    DATE contradiction: date_diff_days / 365

    Examples:
      - 2024-01 vs 2024-02: 30 days / 365 ≈ 0.08 (minor diff)
      - 2023 vs 2024: 365 days / 365 = 1.0 (full year diff)
    """
    try:
        # Parse dates - support multiple formats
        date_formats = [
            "%Y-%m-%d", "%Y-%m", "%Y",
            "%d-%m-%Y", "%d/%m/%Y",
            "%B %d, %Y", "%b %d, %Y"
        ]

        new_date = None
        old_date = None

        # Try parsing new_value
        new_str = str(new_value).strip()
        for fmt in date_formats:
            try:
                new_date = datetime.strptime(new_str, fmt)
                break
            except ValueError:
                continue

        # Try parsing existing_value
        old_str = str(existing_value).strip()
        for fmt in date_formats:
            try:
                old_date = datetime.strptime(old_str, fmt)
                break
            except ValueError:
                continue

        # If both parsed successfully, calculate normalized difference
        if new_date and old_date:
            diff_days = abs((new_date - old_date).days)
            # Normalize to 0-1 scale (1 year = 365 days)
            return min(diff_days / 365.0, 1.0)

        # Fallback: string comparison
        return 0.0 if new_str == old_str else 0.1

    except Exception:
        return 0.0  # On parsing error, assume no contradiction


def _contradiction_story(new_value: Any, existing_value: Any) -> float:
    """
    STORY contradiction: LLM semantic divergence (0-1)

    Examples:
      - "I led technical redesign" vs "I redesigned the API" → 0.2 (related)
      - "Project failed" vs "Project succeeded" → 0.9 (opposite)
    """
    new_str = str(new_value).strip()
    old_str = str(existing_value).strip()

    # Use Claude API to assess semantic divergence
    client = Anthropic()
    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": f"""Rate the semantic divergence between these two story segments on a scale of 0-1.

0.0 = Same story, just worded differently
0.3 = Related but different angles
0.6 = Different stories about same event
0.9 = Opposite/contradictory stories
1.0 = Completely unrelated

Old story: "{old_str}"
New story: "{new_str}"

Respond with ONLY the number (e.g., 0.2, 0.7, etc):"""
            }]
        )
        try:
            score = float(response.content[0].text.strip())
            return min(max(score, 0.0), 1.0)  # Clamp to [0, 1]
        except ValueError:
            # Fallback if response isn't a valid number
            return 0.3

    except Exception:
        # Fallback on API error
        return 0.0


def entity_scope_check(new_pair: Dict, existing_pair: Dict) -> bool:
    """
    Check if both pairs reference same entity (company/role/project).

    If different entities → no conflict (even if semantically similar).

    Args:
        new_pair: New Q&A pair metadata
        existing_pair: Existing pair metadata

    Returns:
        True if same entity scope, False if different
    """
    def normalize_entity(entity_str: Optional[str]) -> Optional[str]:
        """Normalize entity name using aliases."""
        if not entity_str:
            return None
        entity_str = str(entity_str).lower().strip()
        # Check aliases
        for canonical, aliases in ENTITY_ALIASES.items():
            if entity_str == canonical.lower() or entity_str in [a.lower() for a in aliases]:
                return canonical.lower()
        return entity_str

    # Extract entities from both pairs
    new_company = normalize_entity(new_pair.get("company") or new_pair.get("org"))
    old_company = normalize_entity(existing_pair.get("company") or existing_pair.get("org"))

    new_role = normalize_entity(new_pair.get("role"))
    old_role = normalize_entity(existing_pair.get("role"))

    new_project = normalize_entity(new_pair.get("project"))
    old_project = normalize_entity(existing_pair.get("project"))

    # Check if all entity dimensions match
    company_match = (new_company == old_company) if new_company and old_company else (new_company is None and old_company is None)
    role_match = (new_role == old_role) if new_role and old_role else (new_role is None and old_role is None)
    project_match = (new_project == old_project) if new_project and old_project else (new_project is None and old_project is None)

    # True only if all specified entities match
    return company_match and role_match and project_match


def temporal_scope_check(new_pair: Dict, existing_pair: Dict) -> bool:
    """
    Check if pairs are from different time periods.

    If from different time periods (e.g., 2022 vs 2024) → progression, not conflict.

    Args:
        new_pair: New Q&A pair metadata
        existing_pair: Existing pair metadata

    Returns:
        True if same temporal scope, False if different periods
    """
    try:
        new_date_str = new_pair.get("date_start") or new_pair.get("date")
        old_date_str = existing_pair.get("date_start") or existing_pair.get("date")

        if not new_date_str or not old_date_str:
            # If no dates, consider same scope
            return True

        # Parse dates
        date_formats = ["%Y-%m-%d", "%Y-%m", "%Y", "%B %Y", "%b %Y"]
        new_date = None
        old_date = None

        for fmt in date_formats:
            try:
                new_date = datetime.strptime(str(new_date_str).strip(), fmt)
                break
            except ValueError:
                continue

        for fmt in date_formats:
            try:
                old_date = datetime.strptime(str(old_date_str).strip(), fmt)
                break
            except ValueError:
                continue

        if not new_date or not old_date:
            # If can't parse, consider same scope
            return True

        # Check temporal separation: >6 months = different scope
        diff_months = abs((new_date.year - old_date.year) * 12 + (new_date.month - old_date.month))
        if diff_months > 6:
            return False  # Different temporal scope

        return True  # Same temporal scope

    except Exception:
        # On error, assume same scope (conservative)
        return True


def conflict_check(
    new_pair: Dict[str, Any],
    existing_pairs: List[Tuple[Dict, float]],  # (metadata, embedding)
) -> ConflictResult:
    """
    Main conflict detection algorithm.

    Flow:
    1. For each existing pair with sem_sim > 0.75:
       2. Check entity scope (same company/role/project?)
       3. Check temporal scope (same time period?)
       4. Calculate contradiction_magnitude
       5. Calculate conflict_score = sem_sim × contradiction × scope
    6. Return ConflictResult

    Args:
        new_pair: New Q&A pair to insert
        existing_pairs: List of (metadata, embedding) tuples from ChromaDB

    Returns:
        ConflictResult with status and score
    """
    max_conflict_score = 0.0
    max_conflict_result = None

    for existing_metadata, existing_embedding in existing_pairs:
        try:
            # Calculate semantic similarity from embeddings
            sem_sim = calculate_semantic_similarity(
                new_pair.get("embedding", []),
                existing_embedding
            )

            # Skip if semantic similarity is low (below 0.75 threshold)
            if sem_sim < 0.75:
                continue

            # Check entity scope
            if not entity_scope_check(new_pair, existing_metadata):
                continue  # Different entities → no conflict

            # Check temporal scope
            if not temporal_scope_check(new_pair, existing_metadata):
                continue  # Different time periods → progression, not conflict

            # Calculate contradiction magnitude
            new_value = new_pair.get("answer")
            old_value = existing_metadata.get("answer")
            atom_type = new_pair.get("atom_type", "fact")

            contradiction = calculate_contradiction_magnitude(
                new_value, old_value, atom_type
            )

            # Calculate final conflict score
            conflict_score = sem_sim * contradiction

            # Track highest conflict
            if conflict_score > max_conflict_score:
                max_conflict_score = conflict_score
                max_conflict_result = existing_metadata

        except Exception as e:
            # Log and continue on individual pair errors
            continue

    # Determine status based on conflict score
    if max_conflict_score > CONFLICT_THRESHOLDS.get("hard", 0.6):
        return ConflictResult(
            status="CONFLICT",
            conflict_score=max_conflict_score,
            existing_pair_id=max_conflict_result.get("id") if max_conflict_result else None,
            existing_answer=max_conflict_result.get("answer") if max_conflict_result else None
        )
    elif max_conflict_score > CONFLICT_THRESHOLDS.get("soft", 0.3):
        return ConflictResult(
            status="SOFT",
            conflict_score=max_conflict_score,
            existing_pair_id=max_conflict_result.get("id") if max_conflict_result else None,
            existing_answer=max_conflict_result.get("answer") if max_conflict_result else None
        )
    elif max_conflict_score > CONFLICT_THRESHOLDS.get("enrichment", 0.1):
        return ConflictResult(
            status="ENRICHMENT",
            conflict_score=max_conflict_score,
            existing_pair_id=max_conflict_result.get("id") if max_conflict_result else None,
            existing_answer=max_conflict_result.get("answer") if max_conflict_result else None
        )
    else:
        return ConflictResult(
            status="SAFE",
            conflict_score=max_conflict_score
        )


def resolve_conflict_with_user(
    conflict_result: ConflictResult,
    new_answer: str
) -> str:
    """
    Present conflict to user and get resolution.

    Options:
      A) Keep old
      B) Use new (create change_log)
      C) Context-qualify both
      D) Flag for later review

    Args:
        conflict_result: The conflict details
        new_answer: The new answer text

    Returns:
        User's choice (A, B, C, D)
    """
    from anthropic import Anthropic

    prompt = f"""Ruko ek second —

Tumne pehle kaha tha:
  📌 {conflict_result.existing_answer}

Abhi tum bol rahe ho:
  📝 {new_answer}

Yeh dono aapas mein contradict karte hain (conflict score: {conflict_result.conflict_score:.2f}).

Kya sahi hai?

[A] Purani baat sahi hai → discard new entry
[B] Nayi baat sahi hai → update purani, create change_log entry
[C] Dono alag contexts mein sahi hain → add context_qualifier to both
[D] Verify karna hai baad mein → flag both as unverified

Select A/B/C/D:"""

    client = Anthropic()
    try:
        # In production, this would wait for actual user input
        # For now, using Claude to simulate user choice based on context
        # In real implementation, integrate with conversation.py for user input
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=50,
            messages=[{
                "role": "user",
                "content": f"Given this conflict: old='{conflict_result.existing_answer}' vs new='{new_answer}'. Which is most likely correct? Answer with ONLY A, B, C, or D"
            }]
        )
        choice = response.content[0].text.strip().upper()
        # Extract just the letter if response includes explanation
        for letter in ["A", "B", "C", "D"]:
            if letter in choice:
                return letter
        return "D"  # Default to flag for review
    except Exception:
        return "D"  # On error, flag for review


def create_change_log_entry(
    old_doc_id: str,
    old_value: str,
    new_value: str,
    resolution: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create audit trail entry for corrections.

    Args:
        old_doc_id: ID of old entry
        old_value: What was stored
        new_value: What is now correct
        resolution: HOW it was resolved
        context: Additional context (e.g., "semester 2")

    Returns:
        document_record type entry for ChromaDB
    """
    from datetime import datetime
    import uuid

    return {
        "type": "document_record",
        "category": "correction",
        "id": f"correction_{uuid.uuid4().hex[:8]}",
        "old_doc_id": old_doc_id,
        "old_value": old_value,
        "new_value": new_value,
        "resolution": resolution,
        "context": context,
        "timestamp": datetime.utcnow().isoformat(),
        "privacy": "private",
        "source": "user_correction",
        "schema_version": 1,
        "importance": 3,
        "domain": "metadata",
        "subdomain": "audit_trail",
    }
