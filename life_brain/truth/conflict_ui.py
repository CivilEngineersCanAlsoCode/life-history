"""
Conflict UI prompts — blocking and warning messages for conflict resolution.

Differentiates by conflict severity:
  HARD (>0.6)  → Blocking prompt, must resolve before proceeding
  SOFT (0.3-0.6) → Warning prompt, can proceed or resolve
  ENRICHMENT   → Informational only, auto-proceeds
  SAFE         → Silent, no prompt
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class ConflictPrompt:
    """Structured conflict prompt for display."""

    severity: str          # HARD, SOFT, ENRICHMENT, SAFE
    is_blocking: bool      # True = must resolve before proceeding
    header: str            # Short headline
    existing_answer: str
    new_answer: str
    conflict_score_pct: int
    resolution_options: str
    full_prompt: str


def format_hard_conflict_prompt(
    existing_answer: str,
    new_answer: str,
    conflict_score: float,
    existing_date: Optional[str] = None,
) -> ConflictPrompt:
    """Format blocking prompt for HARD conflicts (score > 0.6).

    These block ingestion — user MUST pick a resolution before proceeding.
    """
    date_str = f" (stored: {existing_date})" if existing_date else ""
    score_pct = int(conflict_score * 100)

    options = (
        "[A] Keep old  → discard new entry\n"
        "[B] Use new   → update existing, log the change\n"
        "[C] Both valid → add context qualifier to each\n"
        "[D] Review later → flag both as unverified"
    )

    header = f"⛔ CONFLICT DETECTED ({score_pct}% conflict) — Action required"

    body = f"""{header}

Previously stored:
  📌 {existing_answer}{date_str}

New entry:
  📝 {new_answer}

These contradict each other. You must resolve this before proceeding.

{options}

Select A/B/C/D:"""

    return ConflictPrompt(
        severity="HARD",
        is_blocking=True,
        header=header,
        existing_answer=existing_answer,
        new_answer=new_answer,
        conflict_score_pct=score_pct,
        resolution_options=options,
        full_prompt=body.strip(),
    )


def format_soft_conflict_prompt(
    existing_answer: str,
    new_answer: str,
    conflict_score: float,
    existing_date: Optional[str] = None,
) -> ConflictPrompt:
    """Format warning prompt for SOFT conflicts (score 0.3-0.6).

    Non-blocking — user can skip or resolve.
    """
    date_str = f" (stored: {existing_date})" if existing_date else ""
    score_pct = int(conflict_score * 100)

    options = (
        "[A] Keep old  → discard new entry\n"
        "[B] Use new   → update existing, log the change\n"
        "[C] Both valid → add context qualifier to each\n"
        "[D] Review later → flag both as unverified\n"
        "[S] Skip       → proceed without resolving"
    )

    header = f"⚠️  SOFT CONFLICT ({score_pct}% conflict) — Optional review"

    body = f"""{header}

Previously stored:
  📌 {existing_answer}{date_str}

New entry:
  📝 {new_answer}

These may conflict. You can resolve now or skip.

{options}

Select A/B/C/D/S:"""

    return ConflictPrompt(
        severity="SOFT",
        is_blocking=False,
        header=header,
        existing_answer=existing_answer,
        new_answer=new_answer,
        conflict_score_pct=score_pct,
        resolution_options=options,
        full_prompt=body.strip(),
    )


def format_enrichment_prompt(
    existing_answer: str,
    new_answer: str,
    conflict_score: float,
) -> ConflictPrompt:
    """Format informational notice for ENRICHMENT (score 0.1-0.3).

    Auto-proceeds — just informational.
    """
    score_pct = int(conflict_score * 100)
    header = f"ℹ️  ENRICHMENT ({score_pct}% overlap) — Auto-updating"

    body = f"""{header}

Existing:  {existing_answer}
Addition:  {new_answer}

New information is complementary. Auto-ingesting."""

    return ConflictPrompt(
        severity="ENRICHMENT",
        is_blocking=False,
        header=header,
        existing_answer=existing_answer,
        new_answer=new_answer,
        conflict_score_pct=score_pct,
        resolution_options="",
        full_prompt=body.strip(),
    )


def get_conflict_prompt(
    status: str,
    existing_answer: str,
    new_answer: str,
    conflict_score: float,
    existing_date: Optional[str] = None,
) -> Optional[ConflictPrompt]:
    """Get the appropriate prompt for a conflict status.

    Args:
        status: CONFLICT, SOFT, ENRICHMENT, or SAFE
        existing_answer: Previously stored answer
        new_answer: New answer being ingested
        conflict_score: Raw conflict score (0-1)
        existing_date: When existing entry was stored

    Returns:
        ConflictPrompt, or None if SAFE (no prompt needed)
    """
    if status == "CONFLICT":
        return format_hard_conflict_prompt(existing_answer, new_answer, conflict_score, existing_date)
    elif status == "SOFT":
        return format_soft_conflict_prompt(existing_answer, new_answer, conflict_score, existing_date)
    elif status == "ENRICHMENT":
        return format_enrichment_prompt(existing_answer, new_answer, conflict_score)
    else:  # SAFE
        return None


def is_valid_resolution_choice(choice: str, severity: str) -> bool:
    """Check if a resolution choice is valid for the given severity.

    Args:
        choice: User input (A, B, C, D, or S for SOFT)
        severity: HARD or SOFT

    Returns:
        True if valid choice
    """
    choice = choice.strip().upper()
    valid = {"A", "B", "C", "D"}
    if severity == "SOFT":
        valid.add("S")
    return choice in valid
