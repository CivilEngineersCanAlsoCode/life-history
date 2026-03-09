"""
Test suite for conflict resolution.

Tests cover:
- Conflict creation and validation
- Conflict prompt generation
- Resolution options and workflow
- Statistics and reporting
"""

import pytest
from datetime import datetime

from life_brain.truth.conflict_resolution import (
    Conflict,
    ConflictPrompt,
    ConflictResolver,
    ResolutionOption,
)


class TestConflict:
    """Test Conflict dataclass."""

    def test_create_conflict(self):
        """Test creating a conflict."""
        conflict = Conflict(
            field_name="company",
            existing_value="Amex",
            new_value="American Express",
        )

        assert conflict.field_name == "company"
        assert conflict.existing_value == "Amex"
        assert conflict.new_value == "American Express"

    def test_to_dict(self):
        """Test converting conflict to dictionary."""
        conflict = Conflict(
            field_name="company",
            existing_value="Amex",
            new_value="American Express",
        )

        conf_dict = conflict.to_dict()
        assert conf_dict["field_name"] == "company"
        assert conf_dict["existing_value"] == "Amex"

    def test_validate_valid_conflict(self):
        """Test validating valid conflict."""
        conflict = Conflict(
            field_name="company",
            existing_value="Amex",
            new_value="American Express",
            confidence_existing=0.9,
            confidence_new=0.8,
        )

        is_valid, errors = conflict.validate()
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_invalid_confidence(self):
        """Test validation with invalid confidence."""
        conflict = Conflict(
            field_name="company",
            existing_value="Amex",
            new_value="American Express",
            confidence_existing=1.5,  # Invalid
        )

        is_valid, errors = conflict.validate()
        assert is_valid is False
        assert any("confidence" in e for e in errors)

    def test_validate_invalid_severity(self):
        """Test validation with invalid severity."""
        conflict = Conflict(
            field_name="company",
            existing_value="Amex",
            new_value="American Express",
            severity="invalid",
        )

        is_valid, errors = conflict.validate()
        assert is_valid is False
        assert any("severity" in e for e in errors)


class TestConflictPrompt:
    """Test ConflictPrompt dataclass."""

    def test_create_prompt(self):
        """Test creating a conflict prompt."""
        conflict = Conflict(
            field_name="company",
            existing_value="Amex",
            new_value="American Express",
        )

        prompt = ConflictPrompt(
            prompt_id="conflict_001",
            document_id="doc_001",
            conflict=conflict,
        )

        assert prompt.prompt_id == "conflict_001"
        assert prompt.document_id == "doc_001"

    def test_to_display_dict(self):
        """Test converting prompt to display format."""
        conflict = Conflict(
            field_name="company",
            existing_value="Amex",
            new_value="American Express",
            confidence_existing=0.9,
            confidence_new=0.95,
        )

        prompt = ConflictPrompt(
            prompt_id="conflict_001",
            document_id="doc_001",
            conflict=conflict,
        )

        display = prompt.to_display_dict()
        assert display["field"] == "company"
        assert display["existing"]["value"] == "Amex"
        assert "%" in display["existing"]["confidence"]


class TestConflictResolver:
    """Test ConflictResolver functionality."""

    def test_create_resolver(self):
        """Test creating conflict resolver."""
        resolver = ConflictResolver()
        assert len(resolver.active_prompts) == 0
        assert len(resolver.resolutions) == 0

    def test_conflict_prompt_creation(self):
        """Test creating a conflict prompt."""
        resolver = ConflictResolver()

        prompt = resolver.conflict_prompt(
            document_id="doc_001",
            field_name="company",
            existing_value="Amex",
            new_value="American Express",
        )

        assert prompt.document_id == "doc_001"
        assert prompt.conflict.field_name == "company"
        assert len(resolver.active_prompts) == 1

    def test_severity_determination(self):
        """Test automatic severity determination."""
        resolver = ConflictResolver()

        # High confidence new > existing
        prompt1 = resolver.conflict_prompt(
            "doc_001",
            "field1",
            "old",
            "new",
            confidence_existing=0.5,
            confidence_new=0.95,
        )
        assert prompt1.conflict.severity == "high"

        # Medium confidence similar
        prompt2 = resolver.conflict_prompt(
            "doc_002",
            "field2",
            "old",
            "new",
            confidence_existing=0.8,
            confidence_new=0.75,
        )
        assert prompt2.conflict.severity == "medium"

    def test_get_active_prompts(self):
        """Test retrieving active prompts."""
        resolver = ConflictResolver()

        for i in range(3):
            resolver.conflict_prompt(
                f"doc_{i:03d}",
                f"field_{i}",
                "old",
                "new",
            )

        active = resolver.get_active_prompts()
        assert len(active) == 3

    def test_get_prompts_for_document(self):
        """Test getting conflicts for a document."""
        resolver = ConflictResolver()

        # Add multiple conflicts for doc_001
        resolver.conflict_prompt("doc_001", "field1", "old1", "new1")
        resolver.conflict_prompt("doc_001", "field2", "old2", "new2")
        resolver.conflict_prompt("doc_002", "field1", "old", "new")

        doc_001_conflicts = resolver.get_prompts_for_document("doc_001")
        assert len(doc_001_conflicts) == 2

    def test_get_prompts_by_severity(self):
        """Test filtering by severity."""
        resolver = ConflictResolver()

        resolver.conflict_prompt(
            "doc_001",
            "field1",
            "old",
            "new",
            confidence_existing=0.5,
            confidence_new=0.95,
        )  # high

        resolver.conflict_prompt(
            "doc_002",
            "field2",
            "old",
            "new",
            confidence_existing=0.8,
            confidence_new=0.75,
        )  # medium

        high_severity = resolver.get_prompts_by_severity("high")
        assert len(high_severity) == 1

    def test_resolve_keep_existing(self):
        """Test resolving by keeping existing value."""
        resolver = ConflictResolver()

        prompt = resolver.conflict_prompt(
            "doc_001",
            "company",
            "American Express",
            "Amex",
        )

        success, error = resolver.resolve_conflict(
            prompt.prompt_id,
            ResolutionOption.KEEP_EXISTING,
            reasoning="Existing is more formal",
        )

        assert success is True
        assert len(resolver.active_prompts) == 0
        assert prompt.prompt_id in resolver.resolutions

        resolution = resolver.resolutions[prompt.prompt_id]
        assert resolution["resolved_value"] == "American Express"

    def test_resolve_use_new(self):
        """Test resolving by using new value."""
        resolver = ConflictResolver()

        prompt = resolver.conflict_prompt(
            "doc_001",
            "company",
            "Amex",
            "American Express",
        )

        success, error = resolver.resolve_conflict(
            prompt.prompt_id,
            ResolutionOption.USE_NEW,
            reasoning="New is more accurate",
        )

        assert success is True
        resolution = resolver.resolutions[prompt.prompt_id]
        assert resolution["resolved_value"] == "American Express"

    def test_resolve_merge_lists(self):
        """Test merging list values."""
        resolver = ConflictResolver()

        prompt = resolver.conflict_prompt(
            "doc_001",
            "skills",
            ["Python", "SQL"],
            ["Python", "Django"],
        )

        success, error = resolver.resolve_conflict(
            prompt.prompt_id,
            ResolutionOption.MERGE,
        )

        assert success is True
        resolution = resolver.resolutions[prompt.prompt_id]
        resolved = set(resolution["resolved_value"])
        assert "Python" in resolved
        assert "SQL" in resolved
        assert "Django" in resolved

    def test_resolve_merge_dicts(self):
        """Test merging dict values."""
        resolver = ConflictResolver()

        prompt = resolver.conflict_prompt(
            "doc_001",
            "metadata",
            {"key1": "val1", "key2": "val2"},
            {"key2": "new_val2", "key3": "val3"},
        )

        success, error = resolver.resolve_conflict(
            prompt.prompt_id,
            ResolutionOption.MERGE,
        )

        assert success is True
        resolution = resolver.resolutions[prompt.prompt_id]
        assert resolution["resolved_value"]["key1"] == "val1"
        assert resolution["resolved_value"]["key2"] == "new_val2"
        assert resolution["resolved_value"]["key3"] == "val3"

    def test_resolve_manual(self):
        """Test manual resolution."""
        resolver = ConflictResolver()

        prompt = resolver.conflict_prompt(
            "doc_001",
            "company",
            "Amex",
            "American Express",
        )

        custom_value = "American Express (Amex)"
        success, error = resolver.resolve_conflict(
            prompt.prompt_id,
            ResolutionOption.MANUAL,
            custom_value=custom_value,
        )

        assert success is True
        resolution = resolver.resolutions[prompt.prompt_id]
        assert resolution["resolved_value"] == custom_value

    def test_resolve_skip(self):
        """Test skipping a conflict."""
        resolver = ConflictResolver()

        prompt = resolver.conflict_prompt(
            "doc_001",
            "company",
            "Amex",
            "American Express",
        )

        success, error = resolver.resolve_conflict(
            prompt.prompt_id,
            ResolutionOption.SKIP,
        )

        assert success is True
        resolution = resolver.resolutions[prompt.prompt_id]
        assert resolution["resolved_value"] is None

    def test_resolve_nonexistent_prompt(self):
        """Test resolving nonexistent prompt."""
        resolver = ConflictResolver()

        success, error = resolver.resolve_conflict(
            "nonexistent",
            ResolutionOption.KEEP_EXISTING,
        )

        assert success is False
        assert "not found" in error

    def test_get_resolution(self):
        """Test retrieving resolution."""
        resolver = ConflictResolver()

        prompt = resolver.conflict_prompt(
            "doc_001",
            "field",
            "old",
            "new",
        )

        resolver.resolve_conflict(
            prompt.prompt_id,
            ResolutionOption.USE_NEW,
        )

        resolution = resolver.get_resolution(prompt.prompt_id)
        assert resolution is not None
        assert resolution["resolved_value"] == "new"

    def test_conflict_history(self):
        """Test conflict resolution history."""
        resolver = ConflictResolver()

        # Create and resolve multiple conflicts
        for i in range(3):
            prompt = resolver.conflict_prompt(
                f"doc_{i}",
                f"field_{i}",
                "old",
                "new",
            )
            resolver.resolve_conflict(
                prompt.prompt_id,
                ResolutionOption.USE_NEW,
            )

        history = resolver.get_conflict_history()
        assert len(history) == 3

    def test_get_document_conflicts(self):
        """Test getting all conflicts for a document."""
        resolver = ConflictResolver()

        # Add conflicts for doc_001
        prompt1 = resolver.conflict_prompt("doc_001", "field1", "old1", "new1")
        prompt2 = resolver.conflict_prompt("doc_001", "field2", "old2", "new2")

        # Resolve one
        resolver.resolve_conflict(prompt1.prompt_id, ResolutionOption.USE_NEW)

        doc_conflicts = resolver.get_document_conflicts("doc_001")

        assert doc_conflicts["active_conflicts"] == 1
        assert doc_conflicts["resolved_conflicts"] == 1

    def test_get_statistics_empty(self):
        """Test statistics on empty resolver."""
        resolver = ConflictResolver()
        stats = resolver.get_statistics()

        assert stats["active_prompts"] == 0
        assert stats["resolved_conflicts"] == 0

    def test_get_statistics_populated(self):
        """Test statistics on populated resolver."""
        resolver = ConflictResolver()

        # Add conflicts with different severities
        for i in range(2):
            resolver.conflict_prompt(
                f"doc_high_{i}",
                f"field_{i}",
                "old",
                "new",
                confidence_existing=0.5,
                confidence_new=0.95,
            )

        for i in range(3):
            prompt = resolver.conflict_prompt(
                f"doc_low_{i}",
                f"field_{i}",
                "old",
                "new",
                confidence_existing=0.9,
                confidence_new=0.85,
            )
            resolver.resolve_conflict(
                prompt.prompt_id,
                ResolutionOption.USE_NEW,
            )

        stats = resolver.get_statistics()

        assert stats["active_prompts"] == 2
        assert stats["resolved_conflicts"] == 3

    def test_export_active_conflicts(self):
        """Test exporting active conflicts."""
        resolver = ConflictResolver()

        resolver.conflict_prompt("doc_001", "field1", "old", "new")
        resolver.conflict_prompt("doc_002", "field2", "old", "new")

        exported = resolver.export_active_conflicts()
        assert len(exported) == 2
        assert all("field" in e for e in exported)

    def test_export_resolution_history(self):
        """Test exporting resolution history."""
        resolver = ConflictResolver()

        # Create and resolve conflicts
        for i in range(3):
            prompt = resolver.conflict_prompt(
                f"doc_{i}",
                f"field_{i}",
                "old",
                "new",
            )
            resolver.resolve_conflict(
                prompt.prompt_id,
                ResolutionOption.USE_NEW,
            )

        history = resolver.export_resolution_history()
        assert len(history) == 3
        assert all("resolved_at" in e for e in history)

    def test_complex_resolution_workflow(self):
        """Test complex workflow with multiple conflicts."""
        resolver = ConflictResolver()

        # Create conflicts for multiple documents
        prompts = {}
        for doc_id in ["doc_1", "doc_2", "doc_3"]:
            for i in range(2):
                prompt = resolver.conflict_prompt(
                    doc_id,
                    f"field_{i}",
                    f"old_{i}",
                    f"new_{i}",
                )
                prompts[f"{doc_id}_field_{i}"] = prompt

        # Get initial state
        assert len(resolver.active_prompts) == 6

        # Resolve some conflicts
        for key in list(prompts.keys())[:3]:
            resolver.resolve_conflict(
                prompts[key].prompt_id,
                ResolutionOption.USE_NEW,
            )

        # Check final state
        assert len(resolver.active_prompts) == 3
        assert len(resolver.conflict_history) == 3

        # Verify document statistics
        doc_1_conflicts = resolver.get_document_conflicts("doc_1")
        assert doc_1_conflicts["active_conflicts"] + doc_1_conflicts["resolved_conflicts"] == 2
