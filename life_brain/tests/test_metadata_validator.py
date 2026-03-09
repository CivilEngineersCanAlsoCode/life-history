"""
Unit tests for metadata_validator.py

Covers:
- Required field validation
- Field type validation (str, int, float)
- Field range validation (numeric constraints)
- Enum value validation
- Regex pattern validation
- ISO 8601 date validation
- Single field validation
- Comprehensive metadata validation
- Cross-field validation (date ranges)
- Schema information retrieval
"""

import pytest
from datetime import datetime
from life_brain.core.metadata_validator import MetadataValidator, MetadataValidationError
from life_brain.config import REQUIRED_METADATA_FIELDS


class TestMetadataValidatorInit:
    """Test MetadataValidator initialization."""

    def test_create_validator(self):
        """Test creating validator instance."""
        validator = MetadataValidator()
        assert validator is not None
        assert hasattr(validator, "FIELD_CONSTRAINTS")

    def test_field_constraints_exist(self):
        """Test that field constraints are defined."""
        validator = MetadataValidator()
        assert len(validator.FIELD_CONSTRAINTS) > 0
        assert "domain" in validator.FIELD_CONSTRAINTS
        assert "importance" in validator.FIELD_CONSTRAINTS


class TestRequiredFields:
    """Test required field validation."""

    def test_all_required_fields_present(self):
        """Test when all required fields are present."""
        metadata = {field: "test_value" for field in REQUIRED_METADATA_FIELDS}
        is_valid, missing = MetadataValidator.validate_required_fields(metadata)
        assert is_valid is True
        assert len(missing) == 0

    def test_missing_one_field(self):
        """Test when one required field is missing."""
        metadata = {field: "test" for field in REQUIRED_METADATA_FIELDS}
        first_field = list(REQUIRED_METADATA_FIELDS)[0]
        del metadata[first_field]
        is_valid, missing = MetadataValidator.validate_required_fields(metadata)
        assert is_valid is False
        assert first_field in missing

    def test_missing_multiple_fields(self):
        """Test when multiple fields are missing."""
        metadata = {field: "test" for field in REQUIRED_METADATA_FIELDS}
        fields_to_remove = list(REQUIRED_METADATA_FIELDS)[:3]
        for field in fields_to_remove:
            del metadata[field]
        is_valid, missing = MetadataValidator.validate_required_fields(metadata)
        assert is_valid is False
        assert len(missing) == 3

    def test_empty_field_value(self):
        """Test that empty field value counts as missing."""
        metadata = {field: "" for field in REQUIRED_METADATA_FIELDS}
        is_valid, missing = MetadataValidator.validate_required_fields(metadata)
        assert is_valid is False
        assert len(missing) > 0

    def test_none_field_value(self):
        """Test that None field value counts as missing."""
        metadata = {field: None for field in REQUIRED_METADATA_FIELDS}
        is_valid, missing = MetadataValidator.validate_required_fields(metadata)
        assert is_valid is False


class TestTypeValidation:
    """Test type validation."""

    def test_valid_string_type(self):
        """Test valid string type."""
        is_valid, error = MetadataValidator.validate_type("name", "value", str)
        assert is_valid is True
        assert error == ""

    def test_invalid_string_type(self):
        """Test invalid string type."""
        is_valid, error = MetadataValidator.validate_type("name", 123, str)
        assert is_valid is False
        assert "expected str" in error

    def test_valid_int_type(self):
        """Test valid int type."""
        is_valid, error = MetadataValidator.validate_type("count", 5, int)
        assert is_valid is True

    def test_invalid_int_type(self):
        """Test invalid int type."""
        is_valid, error = MetadataValidator.validate_type("count", "five", int)
        assert is_valid is False
        assert "expected int" in error

    def test_valid_float_type(self):
        """Test valid float type."""
        is_valid, error = MetadataValidator.validate_type("score", 0.95, float)
        assert is_valid is True

    def test_float_accepts_int(self):
        """Test that float type accepts int."""
        is_valid, error = MetadataValidator.validate_type("score", 5, float)
        assert is_valid is True

    def test_none_type_always_valid(self):
        """Test that None is valid for any type."""
        assert MetadataValidator.validate_type("field", None, str)[0] is True
        assert MetadataValidator.validate_type("field", None, int)[0] is True
        assert MetadataValidator.validate_type("field", None, float)[0] is True


class TestRangeValidation:
    """Test range validation."""

    def test_value_in_range(self):
        """Test value within range."""
        is_valid, error = MetadataValidator.validate_range("importance", 5, 0, 10)
        assert is_valid is True
        assert error == ""

    def test_value_at_min(self):
        """Test value at minimum."""
        is_valid, error = MetadataValidator.validate_range("importance", 0, 0, 10)
        assert is_valid is True

    def test_value_at_max(self):
        """Test value at maximum."""
        is_valid, error = MetadataValidator.validate_range("importance", 10, 0, 10)
        assert is_valid is True

    def test_value_below_min(self):
        """Test value below minimum."""
        is_valid, error = MetadataValidator.validate_range("importance", -1, 0, 10)
        assert is_valid is False
        assert "below minimum" in error

    def test_value_above_max(self):
        """Test value above maximum."""
        is_valid, error = MetadataValidator.validate_range("importance", 11, 0, 10)
        assert is_valid is False
        assert "above maximum" in error

    def test_range_with_none_min(self):
        """Test range with no minimum."""
        is_valid, error = MetadataValidator.validate_range("field", -100, None, 10)
        assert is_valid is True

    def test_range_with_none_max(self):
        """Test range with no maximum."""
        is_valid, error = MetadataValidator.validate_range("field", 1000, 0, None)
        assert is_valid is True

    def test_none_value_valid(self):
        """Test that None is always valid for range."""
        is_valid, _ = MetadataValidator.validate_range("field", None, 0, 10)
        assert is_valid is True


class TestEnumValidation:
    """Test enum validation."""

    def test_valid_enum_value(self):
        """Test valid enum value."""
        allowed = ["low", "medium", "high"]
        is_valid, error = MetadataValidator.validate_enum("level", "medium", allowed)
        assert is_valid is True
        assert error == ""

    def test_invalid_enum_value(self):
        """Test invalid enum value."""
        allowed = ["low", "medium", "high"]
        is_valid, error = MetadataValidator.validate_enum("level", "invalid", allowed)
        assert is_valid is False
        assert "not in allowed values" in error

    def test_enum_case_sensitive(self):
        """Test that enum is case-sensitive."""
        allowed = ["Low", "Medium", "High"]
        is_valid, error = MetadataValidator.validate_enum("level", "low", allowed)
        assert is_valid is False

    def test_none_enum_valid(self):
        """Test that None is valid for enum."""
        allowed = ["a", "b", "c"]
        is_valid, _ = MetadataValidator.validate_enum("field", None, allowed)
        assert is_valid is True


class TestPatternValidation:
    """Test regex pattern validation."""

    def test_valid_pattern(self):
        """Test value matching pattern."""
        pattern = r"^\d{4}-\d{2}-\d{2}$"
        is_valid, error = MetadataValidator.validate_pattern("date", "2024-03-09", pattern)
        assert is_valid is True
        assert error == ""

    def test_invalid_pattern(self):
        """Test value not matching pattern."""
        pattern = r"^\d{4}-\d{2}-\d{2}$"
        is_valid, error = MetadataValidator.validate_pattern("date", "03/09/2024", pattern)
        assert is_valid is False
        assert "does not match pattern" in error

    def test_iso_pattern(self):
        """Test ISO 8601 pattern."""
        pattern = r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?"
        assert MetadataValidator.validate_pattern("date", "2024-03-09", pattern)[0] is True
        assert MetadataValidator.validate_pattern("date", "2024-03-09T12:30:45", pattern)[0] is True

    def test_none_pattern_valid(self):
        """Test that None is valid for pattern."""
        is_valid, _ = MetadataValidator.validate_pattern("field", None, r"\d+")
        assert is_valid is True


class TestISODateValidation:
    """Test ISO 8601 date validation."""

    def test_valid_iso_date(self):
        """Test valid ISO date."""
        is_valid, error = MetadataValidator.validate_iso_date("2024-03-09")
        assert is_valid is True
        assert error == ""

    def test_valid_iso_datetime(self):
        """Test valid ISO datetime."""
        is_valid, error = MetadataValidator.validate_iso_date("2024-03-09T12:30:45")
        assert is_valid is True

    def test_invalid_iso_date(self):
        """Test invalid ISO date."""
        is_valid, error = MetadataValidator.validate_iso_date("03/09/2024")
        assert is_valid is False
        assert "Invalid ISO 8601" in error

    def test_invalid_month(self):
        """Test invalid month."""
        is_valid, error = MetadataValidator.validate_iso_date("2024-13-01")
        assert is_valid is False

    def test_invalid_day(self):
        """Test invalid day."""
        is_valid, error = MetadataValidator.validate_iso_date("2024-02-30")
        assert is_valid is False

    def test_none_date_valid(self):
        """Test that None is valid for date."""
        is_valid, _ = MetadataValidator.validate_iso_date(None)
        assert is_valid is True


class TestFieldValidation:
    """Test single field validation."""

    def test_validate_domain_valid(self):
        """Test validating valid domain."""
        validator = MetadataValidator()
        is_valid, error = validator.validate_field("domain", "career")
        assert is_valid is True

    def test_validate_domain_invalid(self):
        """Test validating invalid domain."""
        validator = MetadataValidator()
        is_valid, error = validator.validate_field("domain", "invalid_domain")
        assert is_valid is False

    def test_validate_importance_in_range(self):
        """Test validating importance in range."""
        validator = MetadataValidator()
        is_valid, error = validator.validate_field("importance", 5)
        assert is_valid is True

    def test_validate_importance_out_of_range(self):
        """Test validating importance out of range."""
        validator = MetadataValidator()
        is_valid, error = validator.validate_field("importance", 15)
        assert is_valid is False

    def test_validate_date_format(self):
        """Test validating date format."""
        validator = MetadataValidator()
        is_valid, error = validator.validate_field("date", "2024-03-09")
        assert is_valid is True

    def test_validate_unknown_field(self):
        """Test validating unknown field (should be allowed)."""
        validator = MetadataValidator()
        is_valid, error = validator.validate_field("custom_field", "any_value")
        assert is_valid is True  # Unknown fields are allowed


class TestComprehensiveValidation:
    """Test comprehensive metadata validation."""

    def test_validate_valid_metadata(self):
        """Test validating valid metadata."""
        validator = MetadataValidator()
        metadata = {field: "test" for field in REQUIRED_METADATA_FIELDS}
        metadata["domain"] = "career"
        metadata["type"] = "fact"
        metadata["importance"] = 5
        metadata["privacy"] = "private"
        metadata["source"] = "interview"
        metadata["schema_version"] = 1

        # Should not raise exception
        result = validator.validate_metadata(metadata)
        assert result is not None

    def test_validate_missing_required_field(self):
        """Test validation fails with missing required field."""
        validator = MetadataValidator()
        metadata = {}

        with pytest.raises(MetadataValidationError):
            validator.validate_metadata(metadata)

    def test_validate_invalid_field_type(self):
        """Test validation fails with wrong field type."""
        validator = MetadataValidator()
        metadata = {field: "test" for field in REQUIRED_METADATA_FIELDS}
        metadata["importance"] = "not_an_int"  # Should be int

        with pytest.raises(MetadataValidationError):
            validator.validate_metadata(metadata)

    def test_validate_invalid_enum(self):
        """Test validation fails with invalid enum value."""
        validator = MetadataValidator()
        metadata = {field: "test" for field in REQUIRED_METADATA_FIELDS}
        metadata["domain"] = "invalid_domain"

        with pytest.raises(MetadataValidationError):
            validator.validate_metadata(metadata)

    def test_validate_date_range_valid(self):
        """Test valid date range (start < end)."""
        validator = MetadataValidator()
        metadata = {field: "test" for field in REQUIRED_METADATA_FIELDS}
        metadata["domain"] = "career"
        metadata["subdomain"] = "work"
        metadata["type"] = "fact"
        metadata["importance"] = 5
        metadata["privacy"] = "private"
        metadata["source"] = "interview"
        metadata["schema_version"] = 1
        metadata["date_start"] = "2024-01-01"
        metadata["date_end"] = "2024-12-31"

        # Should not raise exception
        result = validator.validate_metadata(metadata)
        assert result is not None

    def test_validate_date_range_invalid(self):
        """Test invalid date range (start > end)."""
        validator = MetadataValidator()
        metadata = {field: "test" for field in REQUIRED_METADATA_FIELDS}
        metadata["date_start"] = "2024-12-31"
        metadata["date_end"] = "2024-01-01"

        with pytest.raises(MetadataValidationError) as exc_info:
            validator.validate_metadata(metadata)
        assert "date_start must be before date_end" in str(exc_info.value)


class TestSchemaInfo:
    """Test schema information retrieval."""

    def test_get_schema_info(self):
        """Test getting schema information."""
        schema = MetadataValidator.get_schema_info()
        assert schema is not None
        assert isinstance(schema, dict)

    def test_schema_has_required_fields(self):
        """Test schema contains required fields."""
        schema = MetadataValidator.get_schema_info()
        assert "required_fields" in schema
        assert len(schema["required_fields"]) > 0

    def test_schema_has_tier_fields(self):
        """Test schema contains tier fields."""
        schema = MetadataValidator.get_schema_info()
        assert "tier_1_fields" in schema
        assert "tier_2_fields" in schema

    def test_schema_has_enum_fields(self):
        """Test schema contains enum fields."""
        schema = MetadataValidator.get_schema_info()
        assert "enum_fields" in schema
        assert "domain" in schema["enum_fields"]
        assert "privacy" in schema["enum_fields"]

    def test_schema_has_numeric_fields(self):
        """Test schema contains numeric field constraints."""
        schema = MetadataValidator.get_schema_info()
        assert "numeric_fields" in schema
        assert "importance" in schema["numeric_fields"]
        assert schema["numeric_fields"]["importance"]["max"] == 10

    def test_schema_total_fields(self):
        """Test schema reports total field count."""
        schema = MetadataValidator.get_schema_info()
        assert "total_fields" in schema
        assert schema["total_fields"] > 0


class TestIntegrationMetadata:
    """Integration tests for metadata validation."""

    def test_full_career_metadata(self):
        """Test validation of complete career metadata."""
        validator = MetadataValidator()
        metadata = {field: "test_value" for field in REQUIRED_METADATA_FIELDS}
        metadata["domain"] = "career"
        metadata["type"] = "fact"
        metadata["company"] = "Sprinklr"
        metadata["project"] = "CGB"
        metadata["importance"] = 8
        metadata["privacy"] = "private"
        metadata["confidence"] = "verified"
        metadata["source"] = "interview"
        metadata["schema_version"] = 1
        metadata["date_start"] = "2022-04-01"
        metadata["date_end"] = "2024-07-31"

        result = validator.validate_metadata(metadata)
        assert result is not None

    def test_validation_error_contains_details(self):
        """Test that validation error contains details."""
        validator = MetadataValidator()
        metadata = {}

        try:
            validator.validate_metadata(metadata)
        except MetadataValidationError as e:
            error_msg = str(e)
            assert "Missing required fields" in error_msg or "validation failed" in error_msg.lower()

    def test_multiple_field_errors(self):
        """Test that validation reports multiple errors."""
        validator = MetadataValidator()
        metadata = {field: "test" for field in REQUIRED_METADATA_FIELDS}
        metadata["importance"] = 15  # Out of range
        metadata["domain"] = "invalid"  # Invalid enum

        try:
            validator.validate_metadata(metadata)
        except MetadataValidationError as e:
            error_msg = str(e)
            # Should mention multiple errors
            assert "validation failed" in error_msg.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
