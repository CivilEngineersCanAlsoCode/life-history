"""
Test suite for accountability prompter.

Tests cover:
- Prompt generation for different commitment types
- Urgency determination
- Progress tracking
- Check-in recording
- Accountability reporting
"""

import pytest
from datetime import datetime, timedelta

from life_brain.session.accountability_prompter import (
    AccountabilityPrompter,
    AccountabilityPrompt,
    CommitmentCheckIn,
    ProgressStatus,
    PromptType,
)
from life_brain.session.commitment_extractor import (
    CommitmentExtractor,
    CommitmentStatus,
)


class TestCommitmentCheckIn:
    """Test CommitmentCheckIn dataclass."""

    def test_create_check_in(self):
        """Test creating check-in."""
        check_in = CommitmentCheckIn(
            commitment_id="comp_001",
            description="Update resume",
            original_deadline="2026-03-15",
            status=ProgressStatus.IN_PROGRESS,
            progress_percentage=50,
        )

        assert check_in.commitment_id == "comp_001"
        assert check_in.progress_percentage == 50

    def test_to_dict(self):
        """Test converting to dictionary."""
        check_in = CommitmentCheckIn(
            commitment_id="comp_001",
            description="Learn Python",
            original_deadline="2026-03-20",
            status=ProgressStatus.COMPLETED,
            progress_percentage=100,
        )

        check_in_dict = check_in.to_dict()
        assert check_in_dict["status"] == "completed"


class TestAccountabilityPrompt:
    """Test AccountabilityPrompt dataclass."""

    def test_create_prompt(self):
        """Test creating prompt."""
        prompt = AccountabilityPrompt(
            prompt_id="prom_001",
            prompt_type=PromptType.CHECK_IN,
            commitment_id="comp_001",
            commitment_text="Update resume",
            prompt_text="How's the resume update going?",
            urgency=2,
        )

        assert prompt.prompt_id == "prom_001"
        assert prompt.urgency == 2

    def test_to_dict(self):
        """Test converting prompt to dictionary."""
        prompt = AccountabilityPrompt(
            prompt_id="prom_001",
            prompt_type=PromptType.OVERDUE,
            commitment_id="comp_001",
            commitment_text="Submit project",
            prompt_text="This was due!",
            urgency=5,
        )

        prompt_dict = prompt.to_dict()
        assert prompt_dict["prompt_type"] == "overdue"
        assert prompt_dict["urgency"] == 5


class TestAccountabilityPrompter:
    """Test AccountabilityPrompter functionality."""

    def test_create_prompter(self):
        """Test creating accountability prompter."""
        extractor = CommitmentExtractor()
        prompter = AccountabilityPrompter(extractor)

        assert len(prompter.prompts) == 0

    def test_generate_prompts_empty(self):
        """Test generating prompts with no commitments."""
        extractor = CommitmentExtractor()
        prompter = AccountabilityPrompter(extractor)

        prompts, stats = prompter.accountability_prompter(
            session_id="sess_001",
            user_id="user_001",
        )

        assert stats["total_commitments"] == 0
        assert stats["prompts_generated"] == 0

    def test_generate_prompts_with_pending(self):
        """Test generating prompts for pending commitments."""
        extractor = CommitmentExtractor()
        prompter = AccountabilityPrompter(extractor)

        # Create commitment
        commitment = extractor.commitment_extractor("I will do important work")

        if commitment:
            prompts, stats = prompter.accountability_prompter(
                session_id="sess_001",
                user_id="user_001",
            )

            assert stats["total_commitments"] >= 1
            assert len(prompts) >= 1

    def test_generate_overdue_prompt(self):
        """Test generating overdue prompt."""
        extractor = CommitmentExtractor()
        prompter = AccountabilityPrompter(extractor)

        # Create commitment with past deadline
        commitment = extractor.commitment_extractor("I will finish the project")
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        commitment.target_date = past_date
        commitment.status = CommitmentStatus.PENDING

        prompts, stats = prompter.accountability_prompter(
            session_id="sess_001",
            user_id="user_001",
        )

        assert stats["overdue"] >= 1
        # Check for overdue prompt
        overdue_prompts = [p for p in prompts if p.prompt_type == PromptType.OVERDUE]
        assert len(overdue_prompts) >= 1

    def test_generate_reminder_prompt(self):
        """Test generating reminder prompt for soon deadline."""
        extractor = CommitmentExtractor()
        prompter = AccountabilityPrompter(extractor)

        # Create commitment with near deadline
        commitment = extractor.commitment_extractor("I will do important work by tomorrow")
        if commitment:
            near_date = (datetime.now() + timedelta(days=1)).isoformat()
            commitment.target_date = near_date

            prompts, stats = prompter.accountability_prompter(
                session_id="sess_001",
                user_id="user_001",
            )

            # Should have reminder or check-in prompts
            assert len(prompts) >= 1

    def test_record_check_in(self):
        """Test recording check-in."""
        extractor = CommitmentExtractor()
        prompter = AccountabilityPrompter(extractor)

        commitment = extractor.commitment_extractor("I will learn Python")
        commitment_id = commitment.commitment_id

        success, error = prompter.record_check_in(
            commitment_id=commitment_id,
            progress_percentage=75,
            status=ProgressStatus.IN_PROGRESS,
            notes="Making good progress, half done",
        )

        assert success is True
        check_in = prompter.get_check_in(commitment_id)
        assert check_in is not None
        assert check_in.progress_percentage == 75

    def test_record_completion_check_in(self):
        """Test recording completion check-in."""
        extractor = CommitmentExtractor()
        prompter = AccountabilityPrompter(extractor)

        commitment = extractor.commitment_extractor("I will do important work")
        if commitment:
            commitment_id = commitment.commitment_id

            success, error = prompter.record_check_in(
                commitment_id=commitment_id,
                progress_percentage=100,
                status=ProgressStatus.COMPLETED,
                notes="Done!",
            )

            assert success is True
            check_in = prompter.get_check_in(commitment_id)
            assert check_in.status == ProgressStatus.COMPLETED

    def test_get_prompts_by_type(self):
        """Test filtering prompts by type."""
        extractor = CommitmentExtractor()
        prompter = AccountabilityPrompter(extractor)

        # Create multiple commitments
        extractor.commitment_extractor("I will do X")
        extractor.commitment_extractor("I will do Y")

        prompts, _ = prompter.accountability_prompter("sess_001", "user_001")

        # Get check-in prompts
        check_in_prompts = prompter.get_prompts_by_type(PromptType.CHECK_IN)
        assert isinstance(check_in_prompts, list)

    def test_get_urgent_prompts(self):
        """Test getting urgent prompts."""
        extractor = CommitmentExtractor()
        prompter = AccountabilityPrompter(extractor)

        # Create overdue commitment
        commitment = extractor.commitment_extractor("I will do this")
        past_date = (datetime.now() - timedelta(days=5)).isoformat()
        commitment.target_date = past_date
        commitment.status = CommitmentStatus.PENDING

        prompts, _ = prompter.accountability_prompter("sess_001", "user_001")

        urgent = prompter.get_urgent_prompts()
        assert len(urgent) >= 1

    def test_export_prompts(self):
        """Test exporting prompts."""
        extractor = CommitmentExtractor()
        prompter = AccountabilityPrompter(extractor)

        commitment = extractor.commitment_extractor("I will do important work")
        if commitment:
            prompter.accountability_prompter("sess_001", "user_001")

            exported = prompter.export_prompts()
            assert len(exported) > 0
            assert all("prompt_type" in p for p in exported)

    def test_export_check_ins(self):
        """Test exporting check-ins."""
        extractor = CommitmentExtractor()
        prompter = AccountabilityPrompter(extractor)

        commitment = extractor.commitment_extractor("I will learn new skills")
        prompter.record_check_in(
            commitment.commitment_id,
            50,
            ProgressStatus.IN_PROGRESS,
            "Halfway there",
        )

        exported = prompter.export_check_ins()
        assert len(exported) >= 1

    def test_get_accountability_report(self):
        """Test getting accountability report."""
        extractor = CommitmentExtractor()
        prompter = AccountabilityPrompter(extractor)

        extractor.commitment_extractor("I will do X")
        extractor.commitment_extractor("I will do Y")

        report = prompter.get_accountability_report()

        assert report["total_commitments"] >= 2
        assert "compliance_rate" in report
        assert "urgent_prompts" in report

    def test_suggested_actions_for_overdue(self):
        """Test suggested actions for overdue commitment."""
        extractor = CommitmentExtractor()
        prompter = AccountabilityPrompter(extractor)

        commitment = extractor.commitment_extractor("Finish the task")
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        commitment.target_date = past_date
        commitment.status = CommitmentStatus.PENDING

        prompts, _ = prompter.accountability_prompter("sess_001", "user_001")

        overdue_prompt = None
        for p in prompts:
            if p.prompt_type == PromptType.OVERDUE:
                overdue_prompt = p
                break

        if overdue_prompt:
            assert len(overdue_prompt.suggested_actions) > 0
            assert len(overdue_prompt.follow_up_questions) > 0

    def test_compliance_rate_calculation(self):
        """Test compliance rate calculation."""
        extractor = CommitmentExtractor()
        prompter = AccountabilityPrompter(extractor)

        # Create 2 commitments
        c1 = extractor.commitment_extractor("I will do X")
        c2 = extractor.commitment_extractor("I will do Y")

        if c1 and c2:
            # Mark one as completed
            extractor.update_commitment_status(c1.commitment_id, CommitmentStatus.COMPLETED)

            report = prompter.get_accountability_report()

            assert report["total_commitments"] == 2
            assert report["completed"] == 1
            assert report["compliance_rate"] == 0.5

    def test_complex_accountability_workflow(self):
        """Test complex workflow with multiple commitments."""
        extractor = CommitmentExtractor()
        prompter = AccountabilityPrompter(extractor)

        # Create diverse commitments
        c1 = extractor.commitment_extractor("I will do X")  # Generic
        c2 = extractor.commitment_extractor("I will do Y by tomorrow")  # With deadline
        c3 = extractor.commitment_extractor("I will do Z by next week")  # Future

        if c1 and c2 and c3:
            # Mark c2 as overdue
            past = (datetime.now() - timedelta(days=1)).isoformat()
            c2.target_date = past

            # Generate prompts
            prompts, stats = prompter.accountability_prompter(
                "sess_001",
                "user_001",
            )

            assert stats["total_commitments"] == 3

            # Record check-ins
            prompter.record_check_in(
                c1.commitment_id,
                50,
                ProgressStatus.IN_PROGRESS,
                "Working on it",
            )
            prompter.record_check_in(
                c2.commitment_id,
                0,
                ProgressStatus.UNKNOWN,
                "Haven't checked status yet",
            )
            prompter.record_check_in(
                c3.commitment_id,
                100,
                ProgressStatus.COMPLETED,
                "Done early!",
            )

        # Get report
        report = prompter.get_accountability_report()
        assert report["completed"] >= 1
        assert report["in_progress"] >= 1

    def test_summary_prompt_generation(self):
        """Test summary prompt generation."""
        extractor = CommitmentExtractor()
        prompter = AccountabilityPrompter(extractor)

        # Multiple commitments
        for i in range(3):
            extractor.commitment_extractor(f"I will do commitment {i}")

        if len(extractor.commitment_history) >= 1:
            prompts, _ = prompter.accountability_prompter("sess_001", "user_001")

            # Should have at least some prompts
            assert len(prompts) >= 1

    def test_multiple_prompters_independent(self):
        """Test multiple prompters are independent."""
        ext1 = CommitmentExtractor()
        ext2 = CommitmentExtractor()

        prompter1 = AccountabilityPrompter(ext1)
        prompter2 = AccountabilityPrompter(ext2)

        c1 = ext1.commitment_extractor("I will do user 1 commitment")
        c2a = ext2.commitment_extractor("I will do user 2 commitment A")
        c2b = ext2.commitment_extractor("I will do user 2 commitment B")

        if c2a and c2b:
            prompts1, _ = prompter1.accountability_prompter("s1", "u1")
            prompts2, stats2 = prompter2.accountability_prompter("s2", "u2")

            assert stats2["total_commitments"] == 2

    def test_update_deadline_on_check_in(self):
        """Test updating deadline during check-in."""
        extractor = CommitmentExtractor()
        prompter = AccountabilityPrompter(extractor)

        commitment = extractor.commitment_extractor("I will finish by tomorrow")
        new_deadline = (datetime.now() + timedelta(days=7)).isoformat()

        prompter.record_check_in(
            commitment.commitment_id,
            30,
            ProgressStatus.IN_PROGRESS,
            "Need more time",
            updated_deadline=new_deadline,
        )

        check_in = prompter.get_check_in(commitment.commitment_id)
        assert check_in.updated_deadline == new_deadline
