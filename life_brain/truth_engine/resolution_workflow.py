"""
Conflict Resolution Workflow — Handle 4-option user resolution protocol.

Implements the conflict resolution orchestration:
  A) Keep old → discard new entry
  B) Keep new → update existing, create change_log
  C) Context-qualify both → add context_qualifier to both entries
  D) Flag for review → mark both as unverified
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ConflictResolutionResult:
    """Result of a conflict resolution."""
    choice: str  # A, B, C, or D
    action_taken: str  # Description of what was done
    new_doc_id: Optional[str] = None  # If B: ID of updated doc
    change_log_id: Optional[str] = None  # If B: ID of change log entry
    context_qualifiers: Optional[Dict[str, str]] = None  # If C: added qualifiers
    flagged_doc_ids: Optional[list] = None  # If D: docs flagged for review
    skip_new: bool = False  # If A: discard new entry


class ConflictResolutionWorkflow:
    """Orchestrates conflict resolution according to user choice."""

    def __init__(self):
        self.logger = logger

    def resolve_choice_a(
        self,
        existing_doc_id: str,
        existing_answer: str,
        new_answer: str
    ) -> ConflictResolutionResult:
        """
        Choice A: Keep old answer, discard new.

        Args:
            existing_doc_id: ID of existing entry (kept)
            existing_answer: Existing answer (kept)
            new_answer: New answer (discarded)

        Returns:
            ConflictResolutionResult with skip_new=True
        """
        self.logger.info(f"Conflict resolution A: Keeping old entry {existing_doc_id}, discarding new")
        return ConflictResolutionResult(
            choice="A",
            action_taken="Discarded new entry, keeping existing",
            skip_new=True
        )

    def resolve_choice_b(
        self,
        existing_doc_id: str,
        old_value: str,
        new_value: str,
        new_doc_id: str,
        context_qualifier: Optional[str] = None
    ) -> Tuple[ConflictResolutionResult, Dict[str, Any]]:
        """
        Choice B: Keep new answer, update existing.

        Creates:
        1. change_log entry documenting the correction
        2. Updated entry for ChromaDB

        Args:
            existing_doc_id: ID of existing entry (being replaced)
            old_value: Old answer text
            new_value: New answer text
            new_doc_id: ID of new entry
            context_qualifier: Optional context (e.g., "semester 2")

        Returns:
            Tuple of (ConflictResolutionResult, change_log_entry_dict)
        """
        from life_brain.truth_engine.conflict import create_change_log_entry

        # Create change log entry
        change_log = create_change_log_entry(
            old_doc_id=existing_doc_id,
            old_value=old_value,
            new_value=new_value,
            resolution="user_chose_new",
            context=context_qualifier
        )

        self.logger.info(f"Conflict resolution B: Updated {existing_doc_id}, created change_log {change_log.get('id')}")

        return (
            ConflictResolutionResult(
                choice="B",
                action_taken=f"Updated existing entry {existing_doc_id} with new value, created change_log",
                new_doc_id=existing_doc_id,
                change_log_id=change_log.get("id")
            ),
            change_log
        )

    def resolve_choice_c(
        self,
        existing_doc_id: str,
        new_doc_id: str,
        existing_context: Optional[str] = None,
        new_context: Optional[str] = None
    ) -> ConflictResolutionResult:
        """
        Choice C: Both are correct in different contexts.

        Adds context_qualifier to both entries to distinguish them.

        Args:
            existing_doc_id: ID of existing entry
            new_doc_id: ID of new entry
            existing_context: Context for existing (e.g., "Sprinklr 2023")
            new_context: Context for new (e.g., "AmEx 2024")

        Returns:
            ConflictResolutionResult with context qualifiers
        """
        qualifiers = {
            existing_doc_id: existing_context or "existing",
            new_doc_id: new_context or "new"
        }

        self.logger.info(f"Conflict resolution C: Added context qualifiers: {qualifiers}")

        return ConflictResolutionResult(
            choice="C",
            action_taken="Added context qualifiers to distinguish both entries",
            context_qualifiers=qualifiers
        )

    def resolve_choice_d(
        self,
        existing_doc_id: str,
        new_doc_id: str,
        review_reason: str = "User marked for manual verification"
    ) -> ConflictResolutionResult:
        """
        Choice D: Mark both for manual review.

        Flags both entries as unverified and adds to review queue.

        Args:
            existing_doc_id: ID of existing entry
            new_doc_id: ID of new entry
            review_reason: Reason for flagging

        Returns:
            ConflictResolutionResult with flagged doc IDs
        """
        flagged_ids = [existing_doc_id, new_doc_id]

        self.logger.info(f"Conflict resolution D: Flagged for review: {flagged_ids}")
        self.logger.info(f"Review reason: {review_reason}")

        return ConflictResolutionResult(
            choice="D",
            action_taken=f"Flagged both entries for manual review: {review_reason}",
            flagged_doc_ids=flagged_ids
        )

    def execute_resolution(
        self,
        choice: str,
        existing_doc_id: str,
        new_doc_id: str,
        old_value: str,
        new_value: str,
        existing_context: Optional[str] = None,
        new_context: Optional[str] = None
    ) -> Tuple[ConflictResolutionResult, Optional[Dict[str, Any]]]:
        """
        Execute the chosen resolution.

        Args:
            choice: User's choice (A, B, C, or D)
            existing_doc_id: ID of existing entry
            new_doc_id: ID of new entry
            old_value: Value of existing entry
            new_value: Value of new entry
            existing_context: Context for existing entry
            new_context: Context for new entry

        Returns:
            Tuple of (ConflictResolutionResult, optional_change_log_dict)

        Raises:
            ValueError: If invalid choice
        """
        choice = choice.upper()

        if choice == "A":
            result = self.resolve_choice_a(existing_doc_id, old_value, new_value)
            return (result, None)

        elif choice == "B":
            result, change_log = self.resolve_choice_b(
                existing_doc_id,
                old_value,
                new_value,
                new_doc_id,
                context_qualifier=existing_context
            )
            return (result, change_log)

        elif choice == "C":
            result = self.resolve_choice_c(
                existing_doc_id,
                new_doc_id,
                existing_context=existing_context,
                new_context=new_context
            )
            return (result, None)

        elif choice == "D":
            result = self.resolve_choice_d(existing_doc_id, new_doc_id)
            return (result, None)

        else:
            raise ValueError(f"Invalid choice: {choice}. Must be A, B, C, or D")

    def format_conflict_prompt(
        self,
        existing_answer: str,
        new_answer: str,
        conflict_score: float,
        existing_date: Optional[str] = None
    ) -> str:
        """
        Format the Hinglish conflict resolution prompt for user.

        Args:
            existing_answer: Previous answer
            new_answer: New answer
            conflict_score: Quantitative conflict score (0-1)
            existing_date: When existing answer was stored

        Returns:
            Hinglish prompt string
        """
        date_str = f" (stored on {existing_date})" if existing_date else ""
        score_pct = int(conflict_score * 100)

        prompt = f"""Ruko ek second —

Tumne pehle kaha tha:
  📌 {existing_answer}{date_str}

Abhi tum bol rahe ho:
  📝 {new_answer}

Yeh dono aapas mein contradict karte hain (conflict score: {score_pct}%).

Kya sahi hai?

[A] Purani baat sahi hai → discard new entry
[B] Nayi baat sahi hai → update purani, create change_log entry
[C] Dono alag contexts mein sahi hain → add context_qualifier to both
[D] Verify karna hai baad mein → flag both as unverified, add to review queue

Select A/B/C/D:"""

        return prompt.strip()
