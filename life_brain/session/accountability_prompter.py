"""
Accountability prompter for checking progress on prior commitments.

Tracks user progress on prior commitments and generates prompts
to maintain accountability and motivate follow-through.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from life_brain.session.commitment_extractor import (
    CommitmentExtractor,
    Commitment,
    CommitmentStatus,
)


class ProgressStatus(Enum):
    """User progress on commitment."""

    COMPLETED = "completed"  # Done as promised
    IN_PROGRESS = "in_progress"  # Working on it
    DELAYED = "delayed"  # Behind schedule
    ABANDONED = "abandoned"  # Gave up
    NOT_STARTED = "not_started"  # Didn't start yet
    UNKNOWN = "unknown"  # No update provided


class PromptType(Enum):
    """Types of accountability prompts."""

    CHECK_IN = "check_in"  # How's it going?
    REMINDER = "reminder"  # Deadline approaching
    OVERDUE = "overdue"  # Past deadline
    CELEBRATION = "celebration"  # Completed!
    RESET = "reset"  # Start fresh
    SUPPORT = "support"  # Offer help


@dataclass
class CommitmentCheckIn:
    """Check-in on a commitment's progress."""

    commitment_id: str
    description: str
    original_deadline: Optional[str]
    status: ProgressStatus
    progress_percentage: int  # 0-100
    notes: str = ""
    updated_deadline: Optional[str] = None  # If adjusted
    checked_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "commitment_id": self.commitment_id,
            "description": self.description,
            "original_deadline": self.original_deadline,
            "status": self.status.value,
            "progress_percentage": self.progress_percentage,
            "notes": self.notes,
            "updated_deadline": self.updated_deadline,
            "checked_at": self.checked_at,
        }


@dataclass
class AccountabilityPrompt:
    """Prompt for user accountability."""

    prompt_id: str
    prompt_type: PromptType
    commitment_id: str
    commitment_text: str
    prompt_text: str
    urgency: int  # 1-5, how urgent
    suggested_actions: List[str] = field(default_factory=list)
    follow_up_questions: List[str] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "prompt_id": self.prompt_id,
            "prompt_type": self.prompt_type.value,
            "commitment_id": self.commitment_id,
            "commitment_text": self.commitment_text,
            "prompt_text": self.prompt_text,
            "urgency": self.urgency,
            "suggested_actions": self.suggested_actions,
            "follow_up_questions": self.follow_up_questions,
            "generated_at": self.generated_at,
        }


class AccountabilityPrompter:
    """Generate accountability prompts based on prior commitments."""

    def __init__(self, commitment_extractor: CommitmentExtractor):
        """
        Initialize accountability prompter.

        Args:
            commitment_extractor: CommitmentExtractor instance with prior commitments
        """
        self.commitment_extractor = commitment_extractor
        self.check_ins: Dict[str, CommitmentCheckIn] = {}
        self.prompts: List[AccountabilityPrompt] = []
        self.prompt_history: List[AccountabilityPrompt] = []

    def accountability_prompter(
        self,
        session_id: str,
        user_id: str,
    ) -> Tuple[List[AccountabilityPrompt], Dict[str, Any]]:
        """
        Generate accountability prompts for session.

        Args:
            session_id: Current session ID
            user_id: User ID

        Returns:
            (list of prompts, summary stats)
        """
        # Get all pending commitments
        pending = self.commitment_extractor.get_pending_commitments()
        in_progress = [
            c for c in self.commitment_extractor.commitment_history
            if c.status == CommitmentStatus.IN_PROGRESS
        ]

        all_active = pending + in_progress

        generated_prompts = []
        stats = {
            "session_id": session_id,
            "user_id": user_id,
            "total_commitments": len(all_active),
            "overdue": 0,
            "urgent": 0,
            "completed": 0,
            "prompts_generated": 0,
            "compliance_rate": 0.0,
        }

        # Generate prompts for each commitment
        for commitment in all_active:
            prompt = self._generate_prompt_for_commitment(commitment, session_id)

            if prompt:
                generated_prompts.append(prompt)
                self.prompts.append(prompt)
                self.prompt_history.append(prompt)

                # Update stats
                if prompt.prompt_type == PromptType.OVERDUE:
                    stats["overdue"] += 1
                if prompt.urgency >= 4:
                    stats["urgent"] += 1

        # Add summary prompts for overall accountability
        summary_prompt = self._generate_summary_prompt(
            all_active, session_id
        )
        if summary_prompt:
            generated_prompts.append(summary_prompt)

        # Calculate compliance rate
        completed = len(
            [c for c in self.commitment_extractor.commitment_history
             if c.status == CommitmentStatus.COMPLETED]
        )
        if self.commitment_extractor.commitment_history:
            stats["compliance_rate"] = (
                completed / len(self.commitment_extractor.commitment_history)
            )
            stats["completed"] = completed

        stats["prompts_generated"] = len(generated_prompts)

        return generated_prompts, stats

    def _generate_prompt_for_commitment(
        self,
        commitment: Commitment,
        session_id: str,
    ) -> Optional[AccountabilityPrompt]:
        """Generate prompt for specific commitment."""
        prompt_id = f"prom_{len(self.prompts):04d}"

        # Determine prompt type and urgency
        if commitment.is_overdue():
            prompt_type = PromptType.OVERDUE
            urgency = 5
            prompt_text = f"You mentioned: \"{commitment.description}\" - this was due by {commitment.target_date}. What happened? Should we reschedule?"
        elif commitment.target_date:
            days_until = commitment.days_until_deadline()
            if days_until is not None and days_until <= 1:
                prompt_type = PromptType.REMINDER
                urgency = 4
                prompt_text = f"Quick check-in: \"{commitment.description}\" is due {days_until} day(s) away. How's it going?"
            elif days_until is not None and days_until <= 3:
                prompt_type = PromptType.REMINDER
                urgency = 3
                prompt_text = f"Reminder: \"{commitment.description}\" is coming up in {days_until} days."
            else:
                prompt_type = PromptType.CHECK_IN
                urgency = 2
                prompt_text = f"How's progress on \"{commitment.description}\"? Target: {commitment.target_date}"
        else:
            prompt_type = PromptType.CHECK_IN
            urgency = commitment.priority
            prompt_text = f"Following up on: \"{commitment.description}\" - what's your status?"

        # Generate suggested actions
        suggested_actions = self._suggest_actions(commitment, prompt_type)

        # Generate follow-up questions
        follow_up_questions = self._generate_follow_up_questions(
            commitment, prompt_type
        )

        prompt = AccountabilityPrompt(
            prompt_id=prompt_id,
            prompt_type=prompt_type,
            commitment_id=commitment.commitment_id,
            commitment_text=commitment.description,
            prompt_text=prompt_text,
            urgency=urgency,
            suggested_actions=suggested_actions,
            follow_up_questions=follow_up_questions,
        )

        return prompt

    def _generate_summary_prompt(
        self,
        commitments: List[Commitment],
        session_id: str,
    ) -> Optional[AccountabilityPrompt]:
        """Generate overall accountability summary prompt."""
        if not commitments:
            return None

        prompt_id = f"prom_{len(self.prompts):05d}"

        # Count by status
        completed = len(
            [c for c in commitments if c.status == CommitmentStatus.COMPLETED]
        )
        in_progress = len(
            [c for c in commitments if c.status == CommitmentStatus.IN_PROGRESS]
        )
        pending = len(
            [c for c in commitments if c.status == CommitmentStatus.PENDING]
        )
        overdue = len([c for c in commitments if c.is_overdue()])

        # Determine tone
        if completed == len(commitments):
            prompt_type = PromptType.CELEBRATION
            prompt_text = (
                f"🎉 Wow! You've completed all {completed} commitments from last time. "
                "That's amazing follow-through!"
            )
            urgency = 1
        elif overdue > 0:
            prompt_type = PromptType.OVERDUE
            prompt_text = (
                f"We have {overdue} overdue commitment(s) from last session. "
                f"You're working on {in_progress}, and {pending} are pending. "
                "Let's prioritize and get back on track."
            )
            urgency = 5
        elif in_progress > 0:
            prompt_type = PromptType.CHECK_IN
            prompt_text = (
                f"Good progress! You've completed {completed} of {len(commitments)} commitments. "
                f"{in_progress} are in progress. Let's keep the momentum!"
            )
            urgency = 2
        else:
            prompt_type = PromptType.REMINDER
            prompt_text = (
                f"You have {len(commitments)} commitments from last time. "
                f"{completed} completed, {pending} pending. Which one shall we tackle first?"
            )
            urgency = 3

        suggested_actions = [
            "Review all commitments for this session",
            "Identify blockers to progress",
            "Reschedule or reset commitments as needed",
        ]

        return AccountabilityPrompt(
            prompt_id=prompt_id,
            prompt_type=prompt_type,
            commitment_id="summary",
            commitment_text="Overall accountability summary",
            prompt_text=prompt_text,
            urgency=urgency,
            suggested_actions=suggested_actions,
        )

    def _suggest_actions(
        self,
        commitment: Commitment,
        prompt_type: PromptType,
    ) -> List[str]:
        """Generate suggested actions."""
        actions = []

        if prompt_type == PromptType.OVERDUE:
            actions.extend([
                "Reschedule the commitment to a new realistic date",
                "Break it into smaller steps if too big",
                "Identify what blocked progress",
                "Consider if this is still important to you",
            ])
        elif prompt_type == PromptType.REMINDER:
            actions.extend([
                "Start or continue work on this commitment",
                "Block time on calendar if needed",
                "Ask for help if facing obstacles",
                "Update deadline if timeline shifted",
            ])
        else:  # CHECK_IN
            actions.extend([
                "Share current progress percentage",
                "Identify any blockers",
                "Commit to next steps and timeline",
                "Get accountability from a partner if needed",
            ])

        return actions

    def _generate_follow_up_questions(
        self,
        commitment: Commitment,
        prompt_type: PromptType,
    ) -> List[str]:
        """Generate follow-up questions."""
        questions = []

        if prompt_type == PromptType.OVERDUE:
            questions.extend([
                "What was the biggest blocker?",
                "Is this still a priority?",
                "What would help you complete it now?",
            ])
        elif prompt_type == PromptType.REMINDER:
            questions.extend([
                "What's your current progress?",
                "Do you need help with anything?",
                "Any changes to your timeline?",
            ])
        else:  # CHECK_IN or CELEBRATION
            questions.extend([
                "What's working well?",
                "Any learnings to share?",
                "What's next?",
            ])

        return questions

    def record_check_in(
        self,
        commitment_id: str,
        progress_percentage: int,
        status: ProgressStatus,
        notes: str = "",
        updated_deadline: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Record check-in on commitment progress."""
        commitment = self.commitment_extractor.get_commitment(commitment_id)

        if not commitment:
            return False, f"Commitment {commitment_id} not found"

        check_in = CommitmentCheckIn(
            commitment_id=commitment_id,
            description=commitment.description,
            original_deadline=commitment.target_date,
            status=status,
            progress_percentage=progress_percentage,
            notes=notes,
            updated_deadline=updated_deadline,
        )

        self.check_ins[commitment_id] = check_in

        # Update commitment status - map ProgressStatus to CommitmentStatus
        status_map = {
            ProgressStatus.COMPLETED: CommitmentStatus.COMPLETED,
            ProgressStatus.IN_PROGRESS: CommitmentStatus.IN_PROGRESS,
            ProgressStatus.ABANDONED: CommitmentStatus.ABANDONED,
            ProgressStatus.DELAYED: CommitmentStatus.DEFERRED,
            ProgressStatus.NOT_STARTED: CommitmentStatus.PENDING,
            ProgressStatus.UNKNOWN: CommitmentStatus.PENDING,
        }
        commit_status = status_map.get(status, CommitmentStatus.PENDING)
        self.commitment_extractor.update_commitment_status(commitment_id, commit_status)

        # Update deadline if provided
        if updated_deadline:
            commitment.target_date = updated_deadline

        return True, None

    def get_check_in(self, commitment_id: str) -> Optional[CommitmentCheckIn]:
        """Get check-in for commitment."""
        return self.check_ins.get(commitment_id)

    def get_prompts(self) -> List[AccountabilityPrompt]:
        """Get all prompts."""
        return self.prompts

    def get_prompts_by_type(self, prompt_type: PromptType) -> List[AccountabilityPrompt]:
        """Get prompts by type."""
        return [p for p in self.prompts if p.prompt_type == prompt_type]

    def get_urgent_prompts(self) -> List[AccountabilityPrompt]:
        """Get high urgency prompts (4-5)."""
        return [p for p in self.prompts if p.urgency >= 4]

    def export_prompts(self) -> List[Dict[str, Any]]:
        """Export all prompts."""
        return [p.to_dict() for p in self.prompts]

    def export_check_ins(self) -> List[Dict[str, Any]]:
        """Export all check-ins."""
        return [c.to_dict() for c in self.check_ins.values()]

    def get_accountability_report(self) -> Dict[str, Any]:
        """Get comprehensive accountability report."""
        total_commitments = len(self.commitment_extractor.commitment_history)
        completed = len(
            [c for c in self.commitment_extractor.commitment_history
             if c.status == CommitmentStatus.COMPLETED]
        )
        in_progress = len(
            [c for c in self.commitment_extractor.commitment_history
             if c.status == CommitmentStatus.IN_PROGRESS]
        )
        overdue = len(self.commitment_extractor.get_overdue_commitments())

        compliance_rate = (
            completed / total_commitments if total_commitments > 0 else 0
        )

        return {
            "total_commitments": total_commitments,
            "completed": completed,
            "in_progress": in_progress,
            "overdue": overdue,
            "pending": total_commitments - completed - in_progress,
            "compliance_rate": compliance_rate,
            "total_prompts": len(self.prompts),
            "urgent_prompts": len(self.get_urgent_prompts()),
            "check_ins_recorded": len(self.check_ins),
            "prompt_types_distribution": {
                pt.value: len(self.get_prompts_by_type(pt))
                for pt in PromptType
            },
        }
