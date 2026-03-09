"""
Metadata Schema Validation — Comprehensive validation for all 47 metadata fields.

Validates:
1. Required fields presence
2. Type correctness (str, int, float)
3. Enum values for constrained fields
4. Field-specific constraints (e.g., importance: 0-10, rating: 0-100)
5. Date format (ISO 8601)
6. Dynamic extension via tags and extra_metadata
"""

from typing import Dict, Any, List, Tuple
import re
from datetime import datetime
import logging

from life_brain.config import (
    Domain,
    AtomType,
    Privacy,
    Confidence,
    Source,
    Status,
    REQUIRED_METADATA_FIELDS,
    TIER_1_FIELDS,
    TIER_2_FIELDS,
)

logger = logging.getLogger(__name__)


class MetadataValidationError(ValueError):
    """Raised when metadata validation fails."""
    pass


class MetadataValidator:
    """Validates metadata against schema and constraints."""

    # Field constraints: field_name -> (type, min, max, allowed_values, pattern)
    FIELD_CONSTRAINTS = {
        # TIER 1: Classification
        "domain": (str, None, None, [d.value for d in Domain], None),
        "subdomain": (str, None, None, None, None),  # Free-text, but related to domain
        "type": (str, None, None, [t.value for t in AtomType], None),
        "tags": (str, None, None, None, None),  # CSV list

        # TIER 1: Temporal
        "date": (str, None, None, None, r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?"),  # ISO 8601
        "date_start": (str, None, None, None, r"^\d{4}-\d{2}-\d{2}"),
        "date_end": (str, None, None, None, r"^\d{4}-\d{2}-\d{2}"),
        "life_phase": (str, None, None, None, None),  # e.g., "college", "first_job", "startup"

        # TIER 1: People
        "people": (str, None, None, None, None),  # CSV names
        "relationships": (str, None, None, None, None),  # CSV types
        "organization": (str, None, None, None, None),
        "role": (str, None, None, None, None),

        # TIER 1: Location
        "location": (str, None, None, None, None),
        "country": (str, None, None, None, None),
        "context": (str, None, None, None, None),

        # TIER 1: Career
        "company": (str, None, None, None, None),
        "project": (str, None, None, None, None),
        "category": (str, None, None, None, None),

        # TIER 1: Meta
        "importance": (int, 0, 10, None, None),  # 0-10 scale
        "emotion": (str, None, None, None, None),  # e.g., "happy", "stressed", "neutral"
        "sentiment": (str, None, None, None, None),  # e.g., "positive", "negative", "neutral"
        "privacy": (str, None, None, [p.value for p in Privacy], None),
        "confidence": (str, None, None, [c.value for c in Confidence], None),
        "source": (str, None, None, [s.value for s in Source], None),
        "schema_version": (int, 1, None, None, None),

        # TIER 2: Status
        "status": (str, None, None, [st.value for st in Status], None),
        "outcome": (str, None, None, None, None),
        "resolution_status": (str, None, None, None, None),
        "follow_up_status": (str, None, None, None, None),

        # TIER 2: Quantitative
        "monetary_value": (float, None, None, None, None),
        "currency": (str, None, None, None, None),  # ISO 4217 code
        "rating": (int, 0, 100, None, None),  # 0-100 scale
        "energy_level": (int, 0, 10, None, None),  # 0-10 scale
        "severity": (int, 0, 10, None, None),  # 0-10 scale

        # TIER 2: Content Reference
        "title": (str, None, None, None, None),
        "author_creator": (str, None, None, None, None),
        "medium": (str, None, None, None, None),  # e.g., "video", "article", "podcast"
        "platform": (str, None, None, None, None),  # e.g., "youtube", "twitter"

        # TIER 2: Triggers & Patterns
        "trigger": (str, None, None, None, None),
        "pattern_id": (str, None, None, None, None),
        "related_id": (str, None, None, None, None),

        # TIER 2: Temporal Extras
        "duration": (str, None, None, None, None),  # e.g., "2h 30m"
        "frequency": (str, None, None, None, None),  # e.g., "weekly", "daily"
        "expiry_date": (str, None, None, None, r"^\d{4}-\d{2}-\d{2}"),
        "time_of_day": (str, None, None, None, None),  # e.g., "morning", "evening"

        # TIER 2: Items & Events
        "item": (str, None, None, None, None),
        "event_name": (str, None, None, None, None),
        "environment": (str, None, None, None, None),
    }

    @staticmethod
    def validate_required_fields(metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Check that all required fields are present and non-empty.

        Returns:
            Tuple of (is_valid, missing_fields)
        """
        missing = []
        for field in REQUIRED_METADATA_FIELDS:
            if field not in metadata or metadata[field] is None or metadata[field] == "":
                missing.append(field)

        is_valid = len(missing) == 0
        if missing:
            logger.warning(f"Missing required fields: {missing}")
        return (is_valid, missing)

    @staticmethod
    def validate_type(field_name: str, value: Any, expected_type: type) -> Tuple[bool, str]:
        """
        Validate that value is of correct type.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None:
            return (True, "")  # None is OK for optional fields

        if expected_type == str and not isinstance(value, str):
            return (False, f"{field_name}: expected str, got {type(value).__name__}")
        elif expected_type == int and not isinstance(value, int):
            return (False, f"{field_name}: expected int, got {type(value).__name__}")
        elif expected_type == float and not isinstance(value, (int, float)):
            return (False, f"{field_name}: expected float, got {type(value).__name__}")

        return (True, "")

    @staticmethod
    def validate_range(field_name: str, value: Any, min_val: float, max_val: float) -> Tuple[bool, str]:
        """
        Validate numeric value is within range.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None:
            return (True, "")

        if min_val is not None and value < min_val:
            return (False, f"{field_name}: value {value} below minimum {min_val}")
        if max_val is not None and value > max_val:
            return (False, f"{field_name}: value {value} above maximum {max_val}")

        return (True, "")

    @staticmethod
    def validate_enum(field_name: str, value: str, allowed_values: List[str]) -> Tuple[bool, str]:
        """
        Validate that value is in allowed list.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None:
            return (True, "")

        if value not in allowed_values:
            return (False, f"{field_name}: value '{value}' not in allowed values: {allowed_values}")

        return (True, "")

    @staticmethod
    def validate_pattern(field_name: str, value: str, pattern: str) -> Tuple[bool, str]:
        """
        Validate that value matches regex pattern.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None:
            return (True, "")

        if not re.match(pattern, value):
            return (False, f"{field_name}: value '{value}' does not match pattern '{pattern}'")

        return (True, "")

    @staticmethod
    def validate_iso_date(value: str) -> Tuple[bool, str]:
        """
        Validate ISO 8601 date format.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None:
            return (True, "")

        try:
            # Try parsing with and without time
            if "T" in value:
                datetime.fromisoformat(value)
            else:
                datetime.strptime(value, "%Y-%m-%d")
            return (True, "")
        except ValueError:
            return (False, f"Invalid ISO 8601 date: {value}")

    def validate_field(self, field_name: str, value: Any) -> Tuple[bool, str]:
        """
        Validate a single field against all constraints.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if field_name not in self.FIELD_CONSTRAINTS:
            # Unknown field → skip validation (allowed via tags/extra_metadata)
            return (True, "")

        constraint = self.FIELD_CONSTRAINTS[field_name]
        expected_type, min_val, max_val, allowed_vals, pattern = constraint

        # Check type
        is_valid, error = self.validate_type(field_name, value, expected_type)
        if not is_valid:
            return (False, error)

        # Skip further checks if value is None
        if value is None:
            return (True, "")

        # Check range (for numeric types)
        if expected_type in (int, float) and (min_val is not None or max_val is not None):
            is_valid, error = self.validate_range(field_name, value, min_val, max_val)
            if not is_valid:
                return (False, error)

        # Check enum (for string types with restricted values)
        if expected_type == str and allowed_vals is not None:
            is_valid, error = self.validate_enum(field_name, value, allowed_vals)
            if not is_valid:
                return (False, error)

        # Check pattern (for formatted strings)
        if expected_type == str and pattern is not None:
            is_valid, error = self.validate_pattern(field_name, value, pattern)
            if not is_valid:
                return (False, error)

        return (True, "")

    def validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate entire metadata dict. Raises MetadataValidationError if invalid.

        Returns:
            Validated metadata dict (same object, modified in place for logging)

        Raises:
            MetadataValidationError: If validation fails
        """
        errors = []

        # Step 1: Check required fields
        is_valid, missing = self.validate_required_fields(metadata)
        if not is_valid:
            errors.append(f"Missing required fields: {', '.join(missing)}")

        # Step 2: Validate each field
        for field_name, value in metadata.items():
            is_valid, error = self.validate_field(field_name, value)
            if not is_valid:
                errors.append(error)

        # Step 3: Cross-field validation
        # Validate date ranges if both start and end provided
        if "date_start" in metadata and "date_end" in metadata:
            start = metadata.get("date_start")
            end = metadata.get("date_end")
            if start and end:
                start_dt = datetime.fromisoformat(start.replace("T", " "))
                end_dt = datetime.fromisoformat(end.replace("T", " "))
                if start_dt > end_dt:
                    errors.append("date_start must be before date_end")

        # If there are any errors, raise exception
        if errors:
            error_message = "Metadata validation failed:\n  - " + "\n  - ".join(errors)
            logger.error(error_message)
            raise MetadataValidationError(error_message)

        logger.debug(f"Metadata validation passed for fields: {list(metadata.keys())}")
        return metadata

    @staticmethod
    def get_schema_info() -> Dict[str, Any]:
        """
        Get schema metadata for documentation/debugging.

        Returns:
            Dict with schema structure and constraints
        """
        return {
            "required_fields": REQUIRED_METADATA_FIELDS,
            "tier_1_fields": list(TIER_1_FIELDS.keys()),
            "tier_2_fields": list(TIER_2_FIELDS.keys()),
            "total_fields": len(TIER_1_FIELDS) + len(TIER_2_FIELDS),
            "enum_fields": {
                "domain": [d.value for d in Domain],
                "type": [t.value for t in AtomType],
                "privacy": [p.value for p in Privacy],
                "confidence": [c.value for c in Confidence],
                "source": [s.value for s in Source],
                "status": [st.value for st in Status],
            },
            "numeric_fields": {
                "importance": {"min": 0, "max": 10},
                "rating": {"min": 0, "max": 100},
                "energy_level": {"min": 0, "max": 10},
                "severity": {"min": 0, "max": 10},
                "schema_version": {"min": 1},
            },
        }
