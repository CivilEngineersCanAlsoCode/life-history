"""
Test suite for career-specific metadata.

Tests cover:
- Career metadata creation and validation
- Field normalization
- Extraction and merging
- Compliance enforcement
"""

import pytest

from life_brain.db.career_metadata import (
    CareerMetadata,
    CareerMetadataManager,
)


class TestCareerMetadata:
    """Test CareerMetadata dataclass."""

    def test_create_metadata(self):
        """Test creating career metadata."""
        metadata = CareerMetadata(
            company_name="American Express",
            project_name="CRR AML Risk Scoring",
            role_title="Senior Associate PM",
            date_range="Jul 2024 - Present",
        )

        assert metadata.company_name == "American Express"
        assert metadata.project_name == "CRR AML Risk Scoring"

    def test_to_dict(self):
        """Test converting to dictionary."""
        metadata = CareerMetadata(
            company_name="American Express",
            project_name="CRR AML",
            role_title="PM",
            date_range="2024-2025",
            impact_metric="4x faster",
        )

        dict_form = metadata.to_dict()
        assert dict_form["company_name"] == "American Express"
        assert dict_form["impact_metric"] == "4x faster"

    def test_validate_valid_metadata(self):
        """Test validating valid metadata."""
        metadata = CareerMetadata(
            company_name="American Express",
            project_name="Project X",
            role_title="PM",
            date_range="2024-2025",
        )

        is_valid, errors = metadata.validate()
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_missing_fields(self):
        """Test validation with missing fields."""
        metadata = CareerMetadata(
            company_name="",
            project_name="Project X",
            role_title="PM",
            date_range="2024-2025",
        )

        is_valid, errors = metadata.validate()
        assert is_valid is False
        assert len(errors) > 0


class TestCareerMetadataManager:
    """Test CareerMetadataManager."""

    def test_normalize_company_alias(self):
        """Test normalizing company with alias."""
        normalized = CareerMetadataManager.normalize_company("amex")
        assert normalized == "American Express"

        normalized = CareerMetadataManager.normalize_company("sprinklr")
        assert normalized == "Sprinklr"

    def test_normalize_company_title_case(self):
        """Test normalizing company to title case."""
        normalized = CareerMetadataManager.normalize_company("google")
        assert normalized == "Google"

    def test_normalize_role_template(self):
        """Test normalizing role from template."""
        normalized = CareerMetadataManager.normalize_role("pm")
        assert normalized == "Product Manager"

        normalized = CareerMetadataManager.normalize_role("eng_sr")
        assert normalized == "Senior Software Engineer"

    def test_extract_impact_metric(self):
        """Test extracting impact metric from text."""
        text = "We improved performance 4x faster than before"
        metric = CareerMetadataManager.extract_impact_metric(text)
        assert metric is not None
        assert "4x faster" in metric

    def test_validate_career_metadata_valid(self):
        """Test validating valid career metadata."""
        metadata = {
            "company_name": "American Express",
            "project_name": "CRR",
            "role_title": "PM",
            "date_range": "2024-01 - 2024-12",
        }

        is_valid, errors = CareerMetadataManager.validate_career_metadata(metadata)
        assert is_valid is True

    def test_validate_career_metadata_missing_field(self):
        """Test validation with missing required field."""
        metadata = {
            "company_name": "American Express",
            "project_name": "CRR",
            "role_title": "PM",
            # Missing date_range
        }

        is_valid, errors = CareerMetadataManager.validate_career_metadata(metadata)
        assert is_valid is False
        assert any("date_range" in e for e in errors)

    def test_validate_career_metadata_bad_date_format(self):
        """Test validation with bad date format."""
        metadata = {
            "company_name": "American Express",
            "project_name": "CRR",
            "role_title": "PM",
            "date_range": "2024",  # Missing range
        }

        is_valid, errors = CareerMetadataManager.validate_career_metadata(metadata)
        assert is_valid is False

    def test_create_career_metadata(self):
        """Test creating career metadata with normalization."""
        metadata = CareerMetadataManager.create_career_metadata(
            company_name="amex",
            project_name="CRR",
            role_title="pm",
            date_range="2024-01 - 2024-12",
            impact_metric="4x improvement",
            skills=["Python", "SQL"],
        )

        assert metadata.company_name == "American Express"
        assert metadata.role_title == "Product Manager"
        assert metadata.impact_metric == "4x improvement"

    def test_merge_metadata(self):
        """Test merging career metadata into base."""
        base_metadata = {
            "domain": "career",
            "source": "resume",
            "confidence": 0.95,
        }

        career_metadata = CareerMetadata(
            company_name="American Express",
            project_name="CRR",
            role_title="PM",
            date_range="2024-2025",
        )

        merged = CareerMetadataManager.merge_metadata(base_metadata, career_metadata)

        assert merged["company_name"] == "American Express"
        assert merged["domain"] == "career"
        assert merged["has_career_metadata"] is True

    def test_get_career_fields_from_metadata(self):
        """Test extracting career fields from full metadata."""
        metadata = {
            "company_name": "American Express",
            "project_name": "CRR",
            "role_title": "PM",
            "date_range": "2024-2025",
            "impact_metric": "4x",
            "domain": "career",
        }

        career = CareerMetadataManager.get_career_fields_from_metadata(metadata)

        assert career is not None
        assert career.company_name == "American Express"
        assert career.impact_metric == "4x"

    def test_get_career_fields_incomplete(self):
        """Test extraction fails with incomplete fields."""
        metadata = {
            "company_name": "American Express",
            "project_name": "CRR",
            # Missing role_title and date_range
        }

        career = CareerMetadataManager.get_career_fields_from_metadata(metadata)
        assert career is None


class TestCareerMetadataIntegration:
    """Integration tests for career metadata."""

    def test_full_career_workflow(self):
        """Test complete career metadata workflow."""
        # Create with normalization
        metadata = CareerMetadataManager.create_career_metadata(
            company_name="amex",
            project_name="CRR AML",
            role_title="pm_sr",
            date_range="Jul 2024 - Present",
            impact_metric="4x faster investigation",
            skills=["Python", "SQL", "Django"],
        )

        # Validate
        is_valid, errors = metadata.validate()
        assert is_valid

        # Merge with base
        base = {"domain": "career", "source": "resume"}
        merged = CareerMetadataManager.merge_metadata(base, metadata)

        # Extract back
        extracted = CareerMetadataManager.get_career_fields_from_metadata(merged)
        assert extracted.company_name == "American Express"
        assert extracted.role_title == "Senior Product Manager"

    def test_normalize_all_fields(self):
        """Test normalization of all fields."""
        metadata = CareerMetadataManager.create_career_metadata(
            company_name="amex",
            project_name="PROJECT",
            role_title="eng_sr",
            date_range="2024-2025",
        )

        assert metadata.company_name == "American Express"
        assert metadata.project_name == "PROJECT"
        assert metadata.role_title == "Senior Software Engineer"

    def test_validate_all_scenarios(self):
        """Test validation across different scenarios."""
        valid_cases = [
            {
                "company_name": "Google",
                "project_name": "Search",
                "role_title": "Engineer",
                "date_range": "2020 - 2024",
            },
            {
                "company_name": "Meta",
                "project_name": "AI",
                "role_title": "ML Engineer",
                "date_range": "2023-01-01 - 2024-12-31",
            },
        ]

        for case in valid_cases:
            is_valid, errors = CareerMetadataManager.validate_career_metadata(case)
            assert is_valid, f"Failed for {case}: {errors}"
