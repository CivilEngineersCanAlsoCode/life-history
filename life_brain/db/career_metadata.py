"""
Career-specific metadata fields — extend schema for career domain.

Adds domain-specific fields:
- company_name: Company/organization name
- project_name: Project/initiative name
- role_title: Job title/role
- date_range: Employment/project period
- skills: Technologies/capabilities used
- impact_metric: Quantified result (e.g., "4x faster")
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CareerMetadata:
    """Career-specific metadata fields."""
    # Core career fields
    company_name: str
    project_name: str
    role_title: str
    date_range: str  # e.g., "Jul 2024 - Present" or "2024-07-01 to 2024-09-15"

    # Extended fields
    skills: Optional[List[str]] = None
    impact_metric: Optional[str] = None
    domain_area: Optional[str] = None  # e.g., "backend", "frontend", "data"
    team_size: Optional[int] = None
    technologies: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "company_name": self.company_name,
            "project_name": self.project_name,
            "role_title": self.role_title,
            "date_range": self.date_range,
            "skills": self.skills or [],
            "impact_metric": self.impact_metric,
            "domain_area": self.domain_area,
            "team_size": self.team_size,
            "technologies": self.technologies or [],
        }

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate required fields."""
        errors = []

        if not self.company_name or not self.company_name.strip():
            errors.append("company_name is required")

        if not self.project_name or not self.project_name.strip():
            errors.append("project_name is required")

        if not self.role_title or not self.role_title.strip():
            errors.append("role_title is required")

        if not self.date_range or not self.date_range.strip():
            errors.append("date_range is required")

        return len(errors) == 0, errors


class CareerMetadataManager:
    """Manage career-specific metadata."""

    # Standard career fields
    REQUIRED_FIELDS = ["company_name", "project_name", "role_title", "date_range"]
    OPTIONAL_FIELDS = ["skills", "impact_metric", "domain_area", "team_size", "technologies"]

    # Company name alternatives
    COMPANY_ALIASES = {
        "amex": "American Express",
        "sprinklr": "Sprinklr",
        "google": "Google",
        "meta": "Meta",
        "amazon": "Amazon",
    }

    # Common role titles
    ROLE_TEMPLATES = {
        "pm": "Product Manager",
        "pm_sr": "Senior Product Manager",
        "eng": "Software Engineer",
        "eng_sr": "Senior Software Engineer",
        "lead": "Technical Lead",
        "manager": "Engineering Manager",
        "designer": "Product Designer",
        "analyst": "Data Analyst",
    }

    # Common impact metrics
    IMPACT_PATTERNS = [
        "x faster",
        "% improvement",
        "% reduction",
        "x increase",
        "customers",
        "revenue",
        "cost savings",
    ]

    @staticmethod
    def extract_from_text(text: str) -> Optional[CareerMetadata]:
        """
        Try to extract career metadata from document text.

        Args:
            text: Document text

        Returns:
            CareerMetadata if found, None otherwise
        """
        # This would use NLP/pattern matching to extract fields
        # For now, return None (would be implemented with actual extraction)
        return None

    @staticmethod
    def normalize_company(company: str) -> str:
        """Normalize company name."""
        company_lower = company.lower().strip()

        for alias, canonical in CareerMetadataManager.COMPANY_ALIASES.items():
            if alias in company_lower:
                return canonical

        return company.strip().title()

    @staticmethod
    def normalize_role(role: str) -> str:
        """Normalize role title."""
        role_lower = role.lower().strip()

        # Try exact match first (longer matches first to avoid partial matches)
        sorted_templates = sorted(
            CareerMetadataManager.ROLE_TEMPLATES.items(),
            key=lambda x: -len(x[0])
        )

        for template_key, canonical in sorted_templates:
            if template_key == role_lower:  # Exact match
                return canonical

        # Try partial match
        for template_key, canonical in sorted_templates:
            if template_key in role_lower:
                return canonical

        return role.strip().title()

    @staticmethod
    def extract_impact_metric(text: str) -> Optional[str]:
        """Extract impact metric from text."""
        for pattern in CareerMetadataManager.IMPACT_PATTERNS:
            if pattern in text.lower():
                # Find the metric clause
                idx = text.lower().find(pattern)
                # Extract surrounding text
                start = max(0, idx - 20)
                end = min(len(text), idx + len(pattern) + 20)
                return text[start:end].strip()

        return None

    @staticmethod
    def validate_career_metadata(metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate career metadata.

        Args:
            metadata: Metadata dictionary

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        for field in CareerMetadataManager.REQUIRED_FIELDS:
            if field not in metadata or not metadata[field]:
                errors.append(f"Required field missing: {field}")

        # Validate field types
        if "skills" in metadata and not isinstance(metadata["skills"], list):
            errors.append("skills must be a list")

        if "technologies" in metadata and not isinstance(metadata["technologies"], list):
            errors.append("technologies must be a list")

        if "team_size" in metadata and metadata["team_size"]:
            if not isinstance(metadata["team_size"], int) or metadata["team_size"] < 0:
                errors.append("team_size must be a positive integer")

        # Validate date range format
        date_range = metadata.get("date_range", "")
        if date_range and "-" not in date_range:
            errors.append("date_range must include a range (e.g., '2024-01-01 - 2024-12-31')")

        return len(errors) == 0, errors

    @staticmethod
    def create_career_metadata(
        company_name: str,
        project_name: str,
        role_title: str,
        date_range: str,
        **optional_fields,
    ) -> CareerMetadata:
        """
        Create career metadata with normalization.

        Args:
            company_name: Company name
            project_name: Project name
            role_title: Role title
            date_range: Date range
            **optional_fields: Additional fields

        Returns:
            CareerMetadata instance
        """
        return CareerMetadata(
            company_name=CareerMetadataManager.normalize_company(company_name),
            project_name=project_name.strip(),
            role_title=CareerMetadataManager.normalize_role(role_title),
            date_range=date_range.strip(),
            skills=optional_fields.get("skills"),
            impact_metric=optional_fields.get("impact_metric"),
            domain_area=optional_fields.get("domain_area"),
            team_size=optional_fields.get("team_size"),
            technologies=optional_fields.get("technologies"),
        )

    @staticmethod
    def merge_metadata(
        base_metadata: Dict[str, Any],
        career_metadata: CareerMetadata,
    ) -> Dict[str, Any]:
        """
        Merge career metadata into base metadata.

        Args:
            base_metadata: Base 47-field metadata
            career_metadata: Career-specific metadata

        Returns:
            Merged metadata dictionary
        """
        merged = base_metadata.copy()
        merged.update(career_metadata.to_dict())
        merged["has_career_metadata"] = True

        return merged

    @staticmethod
    def get_career_fields_from_metadata(metadata: Dict[str, Any]) -> Optional[CareerMetadata]:
        """
        Extract career metadata from full metadata dict.

        Args:
            metadata: Full metadata dictionary

        Returns:
            CareerMetadata if career fields present, None otherwise
        """
        career_fields = {
            "company_name": metadata.get("company_name"),
            "project_name": metadata.get("project_name"),
            "role_title": metadata.get("role_title"),
            "date_range": metadata.get("date_range"),
        }

        # All required fields must be present
        if all(career_fields.values()):
            return CareerMetadata(
                company_name=career_fields["company_name"],
                project_name=career_fields["project_name"],
                role_title=career_fields["role_title"],
                date_range=career_fields["date_range"],
                skills=metadata.get("skills"),
                impact_metric=metadata.get("impact_metric"),
                domain_area=metadata.get("domain_area"),
                team_size=metadata.get("team_size"),
                technologies=metadata.get("technologies"),
            )

        return None
