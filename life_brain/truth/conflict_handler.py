"""
Conflict Handler — Integrates conflict detection with resolution workflow.

Bridges the gap between conflict_check() (which detects conflicts) and
resolution_workflow (which handles user choices).
"""

from typing import Dict, Any, Optional, Tuple
import logging

from life_brain.truth.conflict import ConflictResult
from life_brain.truth.resolution_workflow import (
    ConflictResolutionWorkflow,
    ConflictResolutionResult
)

logger = logging.getLogger(__name__)


class ConflictHandler:
    """Handles conflict detection → user resolution → action execution."""

    def __init__(self):
        self.workflow = ConflictResolutionWorkflow()

    def handle_hard_conflict(
        self,
        conflict_result: ConflictResult,
        new_doc_id: str,
        new_value: str,
        user_choice: str = "D"  # Default: flag for review if no user input
    ) -> Tuple[ConflictResolutionResult, Optional[Dict[str, Any]]]:
        """
        Handle a HARD conflict (conflict_score > 0.6).

        Prompts user with 4 options and executes their choice.

        Args:
            conflict_result: Result from conflict_check()
            new_doc_id: ID of the new entry attempting to be added
            new_value: Value of the new entry
            user_choice: User's choice (A/B/C/D). Default D (flag for review)

        Returns:
            Tuple of (ConflictResolutionResult, optional_change_log_dict)

        Raises:
            ValueError: If invalid user choice
        """
        logger.warning(f"HARD CONFLICT detected (score: {conflict_result.conflict_score:.2f})")

        # Use correct field names with fallbacks
        existing_id = conflict_result.existing_doc_id or conflict_result.existing_pair_id
        existing_date = conflict_result.existing_entry_date

        # Format conflict prompt for user
        prompt = self.workflow.format_conflict_prompt(
            existing_answer=conflict_result.existing_answer or "Unknown",
            new_answer=new_value,
            conflict_score=conflict_result.conflict_score,
            existing_date=existing_date
        )

        logger.info(f"Conflict prompt prepared for user")

        # Execute user's choice
        result, artifact = self.workflow.execute_resolution(
            choice=user_choice,
            existing_doc_id=existing_id or "unknown",
            new_doc_id=new_doc_id,
            old_value=conflict_result.existing_answer or "Unknown",
            new_value=new_value,
            existing_context=conflict_result.existing_context,
            new_context=None
        )

        logger.info(f"Conflict resolution executed: choice={user_choice}, action={result.action_taken}")

        return (result, artifact)

    def handle_soft_conflict(
        self,
        conflict_result: ConflictResult,
        new_doc_id: str,
        new_value: str,
        auto_proceed: bool = True
    ) -> Tuple[ConflictResolutionResult, None]:
        """
        Handle a SOFT conflict (0.3 < conflict_score <= 0.6).

        For soft conflicts, we warn the user but proceed by default.

        Args:
            conflict_result: Result from conflict_check()
            new_doc_id: ID of the new entry
            new_value: Value of the new entry
            auto_proceed: If True, proceed with new entry anyway (log warning)

        Returns:
            Tuple of (ConflictResolutionResult, None)
        """
        logger.warning(f"SOFT CONFLICT detected (score: {conflict_result.conflict_score:.2f})")

        if auto_proceed:
            # Proceed but log warning
            result = ConflictResolutionResult(
                choice="AUTO_PROCEED",
                action_taken=f"Soft conflict warning logged, proceeded with new entry anyway (score: {conflict_result.conflict_score:.2f}). Existing: {conflict_result.existing_answer}"
            )
            logger.info(f"Soft conflict: Auto-proceeded with new entry after warning")
            return (result, None)
        else:
            # Still ask user for soft conflicts
            return self.handle_hard_conflict(conflict_result, new_doc_id, new_value, user_choice="D")

    def handle_enrichment(
        self,
        conflict_result: ConflictResult,
        new_value: str
    ) -> Tuple[ConflictResolutionResult, None]:
        """
        Handle ENRICHMENT (0.1 < conflict_score <= 0.3).

        New information adds detail to existing entry → auto-update.

        Args:
            conflict_result: Result from conflict_check()
            new_value: New value that adds detail

        Returns:
            Tuple of (ConflictResolutionResult, None)
        """
        logger.info(f"ENRICHMENT detected (score: {conflict_result.conflict_score:.2f})")

        result = ConflictResolutionResult(
            choice="AUTO_ENRICH",
            action_taken=f"Enrichment detected, auto-updated existing entry with new detail (score: {conflict_result.conflict_score:.2f})"
        )

        logger.info(f"Enrichment: Auto-updated existing entry with new information")
        return (result, None)

    def handle_safe(self) -> ConflictResolutionResult:
        """
        Handle SAFE (conflict_score <= 0.1).

        No conflict detected → proceed freely.

        Returns:
            ConflictResolutionResult indicating safe to proceed
        """
        result = ConflictResolutionResult(
            choice="SAFE",
            action_taken="No conflict detected, proceeding with insertion"
        )

        logger.debug(f"No conflict: Safe to proceed")
        return result

    def handle_by_status(
        self,
        conflict_result: ConflictResult,
        new_doc_id: str,
        new_value: str,
        user_choice_for_hard: str = "D"
    ) -> Tuple[ConflictResolutionResult, Optional[Dict[str, Any]]]:
        """
        Route handling based on conflict status.

        Args:
            conflict_result: Result from conflict_check()
            new_doc_id: ID of new entry
            new_value: Value of new entry
            user_choice_for_hard: User choice if HARD conflict (A/B/C/D)

        Returns:
            Tuple of (ConflictResolutionResult, optional_artifact)

        Raises:
            ValueError: If invalid choice for hard conflicts
        """
        status = conflict_result.status

        if status == "CONFLICT":
            return self.handle_hard_conflict(conflict_result, new_doc_id, new_value, user_choice_for_hard)

        elif status == "SOFT":
            return self.handle_soft_conflict(conflict_result, new_doc_id, new_value)

        elif status == "ENRICHMENT":
            return self.handle_enrichment(conflict_result, new_value)

        elif status == "SAFE":
            result = self.handle_safe()
            return (result, None)

        else:
            raise ValueError(f"Unknown conflict status: {status}")

    def format_resolution_summary(self, result: ConflictResolutionResult) -> str:
        """
        Format a human-readable summary of the resolution.

        Returns:
            Hinglish summary string
        """
        choice_names = {
            "A": "Purani baat rakhli",
            "B": "Nayi baat use karli + change log banaya",
            "C": "Dono ko context di alag alag",
            "D": "Dono ko review queue mein dala",
            "AUTO_PROCEED": "Soft conflict ke baad bhi aage badhte",
            "AUTO_ENRICH": "Existing ko detail se update kiya",
            "SAFE": "Koi conflict nahi — aage badh gaye"
        }

        summary = f"""Conflict Resolution Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━
Choice: {choice_names.get(result.choice, result.choice)}
Action: {result.action_taken}

Status: {'✓ Done' if result.action_taken else '? Pending'}"""

        if result.new_doc_id:
            summary += f"\nUpdated Doc: {result.new_doc_id}"

        if result.change_log_id:
            summary += f"\nChange Log: {result.change_log_id}"

        if result.context_qualifiers:
            summary += f"\nContext Qualifiers: {result.context_qualifiers}"

        if result.flagged_doc_ids:
            summary += f"\nFlagged for Review: {result.flagged_doc_ids}"

        return summary
