"""
Unit tests for error_reporter.py

Covers:
- Error formatting (type, enum, range, format, required, constraint)
- Error report generation
- Error categorization
- Error summary statistics
"""

import pytest
from life_brain.core.error_reporter import ValidationError, ErrorReporter


class TestValidationError:
    """Test ValidationError dataclass."""

    def test_create_validation_error(self):
        """Test creating a validation error."""
        error = ValidationError(
            category="type",
            field="age",
            value="twenty",
            expected="int",
            message="Type mismatch",
            suggestion="Provide an integer"
        )
        assert error.category == "type"
        assert error.field == "age"
        assert error.severity == "error"

    def test_validation_error_defaults(self):
        """Test ValidationError default values."""
        error = ValidationError(
            category="required",
            field="name",
            value=None
        )
        assert error.severity == "error"
        assert error.message == ""
        assert error.suggestion == ""


class TestErrorFormattingTypeError:
    """Test type error formatting."""

    def test_format_int_type_error(self):
        """Test formatting int type mismatch."""
        error = ErrorReporter.format_type_error("age", "twenty", "int")
        assert error.category == "type"
        assert error.field == "age"
        assert error.expected == "int"
        assert "whole number" in error.suggestion

    def test_format_float_type_error(self):
        """Test formatting float type mismatch."""
        error = ErrorReporter.format_type_error("salary", "1000k", "float")
        assert error.expected == "float"
        assert "decimal" in error.suggestion

    def test_format_str_type_error(self):
        """Test formatting str type mismatch."""
        error = ErrorReporter.format_type_error("name", 123, "str")
        assert error.expected == "str"
        assert "text" in error.suggestion

    def test_format_custom_type_error(self):
        """Test formatting custom type error."""
        error = ErrorReporter.format_type_error("data", [1, 2], "dict")
        assert error.expected == "dict"
        assert "dict" in error.suggestion


class TestErrorFormattingEnumError:
    """Test enum error formatting."""

    def test_format_enum_error_short_list(self):
        """Test enum error with short allowed values."""
        allowed = ["career", "relationships", "health"]
        error = ErrorReporter.format_enum_error("domain", "finance", allowed)
        assert error.category == "enum"
        assert error.field == "domain"
        assert "career" in error.suggestion
        assert "relationships" in error.suggestion

    def test_format_enum_error_long_list(self):
        """Test enum error with many allowed values."""
        allowed = [f"option_{i}" for i in range(20)]
        error = ErrorReporter.format_enum_error("choice", "invalid", allowed)
        assert "..." in error.suggestion
        assert "15 more" in error.suggestion or "15 more" in error.expected


class TestErrorFormattingRangeError:
    """Test range error formatting."""

    def test_format_range_below_min(self):
        """Test value below minimum."""
        error = ErrorReporter.format_range_error("age", 10, 18, 120)
        assert error.category == "range"
        assert "at least" in error.suggestion

    def test_format_range_above_max(self):
        """Test value above maximum."""
        error = ErrorReporter.format_range_error("age", 150, 18, 120)
        assert "at most" in error.suggestion

    def test_format_range_between(self):
        """Test value in range."""
        error = ErrorReporter.format_range_error("score", 10, 0, 100)
        assert "between" in error.suggestion


class TestErrorFormattingFormatError:
    """Test format error formatting."""

    def test_format_iso8601_error(self):
        """Test ISO8601 format error."""
        error = ErrorReporter.format_format_error("date", "03/08/2026", "ISO8601")
        assert error.category == "format"
        assert "2026-03-08" in error.suggestion

    def test_format_email_error(self):
        """Test email format error."""
        error = ErrorReporter.format_format_error("email", "invalid.email", "email")
        assert "@example.com" in error.suggestion

    def test_format_url_error(self):
        """Test URL format error."""
        error = ErrorReporter.format_format_error("website", "not-a-url", "url")
        assert "https://" in error.suggestion

    def test_format_uuid_error(self):
        """Test UUID format error."""
        error = ErrorReporter.format_format_error("id", "not-a-uuid", "uuid")
        assert "550e8400" in error.suggestion


class TestErrorFormattingRequiredError:
    """Test required field error formatting."""

    def test_format_required_error(self):
        """Test required field error."""
        error = ErrorReporter.format_required_error("name")
        assert error.category == "required"
        assert error.field == "name"
        assert error.value is None
        assert "missing" in error.message.lower()
        assert "Provide" in error.suggestion


class TestErrorFormattingConstraintError:
    """Test constraint error formatting."""

    def test_format_constraint_error_no_details(self):
        """Test constraint error without details."""
        error = ErrorReporter.format_constraint_error(
            "date_range",
            "start_date must be before end_date"
        )
        assert error.category == "constraint"
        assert "Constraint violated" in error.message

    def test_format_constraint_error_with_details(self):
        """Test constraint error with details."""
        error = ErrorReporter.format_constraint_error(
            "dates",
            "temporal_ordering",
            "Ensure start_date < end_date"
        )
        assert "Ensure start_date" in error.suggestion


class TestErrorReporting:
    """Test error report generation."""

    def test_format_empty_errors(self):
        """Test report with no errors."""
        report = ErrorReporter.format_error_report([])
        assert "No validation errors" in report

    def test_format_single_error(self):
        """Test report with single error."""
        errors = [
            ErrorReporter.format_type_error("age", "twenty", "int")
        ]
        report = ErrorReporter.format_error_report(errors)
        assert "age" in report
        assert "TYPE" in report
        assert "1 total" in report

    def test_format_multiple_errors_same_category(self):
        """Test report with multiple errors in same category."""
        errors = [
            ErrorReporter.format_type_error("age", "twenty", "int"),
            ErrorReporter.format_type_error("score", "high", "float"),
        ]
        report = ErrorReporter.format_error_report(errors)
        assert "2 total" in report
        assert "TYPE" in report
        assert "age" in report
        assert "score" in report

    def test_format_multiple_errors_different_categories(self):
        """Test report with errors in different categories."""
        errors = [
            ErrorReporter.format_type_error("age", "twenty", "int"),
            ErrorReporter.format_required_error("name"),
            ErrorReporter.format_enum_error("domain", "invalid", ["career", "health"]),
        ]
        report = ErrorReporter.format_error_report(errors)
        assert "3 total" in report
        assert "TYPE" in report
        assert "REQUIRED" in report
        assert "ENUM" in report

    def test_report_includes_suggestions(self):
        """Test that report includes suggestions."""
        errors = [ErrorReporter.format_type_error("age", "twenty", "int")]
        report = ErrorReporter.format_error_report(errors)
        assert "Suggestion" in report or "💡" in report


class TestErrorCategorization:
    """Test error categorization."""

    def test_categorize_single_error(self):
        """Test categorizing single error."""
        errors = [ErrorReporter.format_type_error("age", "x", "int")]
        categorized = ErrorReporter.categorize_errors(errors)
        assert "type" in categorized
        assert len(categorized["type"]) == 1

    def test_categorize_multiple_categories(self):
        """Test categorizing errors from different categories."""
        errors = [
            ErrorReporter.format_type_error("age", "x", "int"),
            ErrorReporter.format_required_error("name"),
            ErrorReporter.format_type_error("score", "high", "float"),
        ]
        categorized = ErrorReporter.categorize_errors(errors)
        assert "type" in categorized
        assert "required" in categorized
        assert len(categorized["type"]) == 2
        assert len(categorized["required"]) == 1


class TestErrorSummary:
    """Test error summary statistics."""

    def test_summary_empty_errors(self):
        """Test summary with no errors."""
        summary = ErrorReporter.get_error_summary([])
        assert summary["total"] == 0
        assert summary["critical"] == 0

    def test_summary_single_error(self):
        """Test summary with single error."""
        errors = [ErrorReporter.format_type_error("age", "x", "int")]
        summary = ErrorReporter.get_error_summary(errors)
        assert summary["total"] == 1
        assert summary["critical"] == 1
        assert summary["by_category"]["type"] == 1
        assert summary["fields_affected"] == 1

    def test_summary_multiple_errors_same_field(self):
        """Test summary with multiple errors on same field."""
        errors = [
            ErrorReporter.format_type_error("age", "x", "int"),
            ErrorReporter.format_range_error("age", -5, 0, 150),
        ]
        summary = ErrorReporter.get_error_summary(errors)
        assert summary["total"] == 2
        assert summary["fields_affected"] == 1

    def test_summary_different_severity_levels(self):
        """Test summary with different severity levels."""
        error1 = ErrorReporter.format_required_error("name")
        error1.severity = "error"

        error2 = ErrorReporter.format_type_error("age", "x", "int")
        error2.severity = "warning"

        error3 = ErrorReporter.format_enum_error("type", "invalid", ["A", "B"])
        error3.severity = "info"

        summary = ErrorReporter.get_error_summary([error1, error2, error3])
        assert summary["total"] == 3
        assert summary["critical"] == 1  # errors
        assert summary["warnings"] == 1
        assert summary["info"] == 1

    def test_summary_multiple_errors_multiple_fields(self):
        """Test summary with errors across multiple fields."""
        errors = [
            ErrorReporter.format_type_error("age", "x", "int"),
            ErrorReporter.format_required_error("name"),
            ErrorReporter.format_enum_error("domain", "invalid", ["A", "B"]),
        ]
        summary = ErrorReporter.get_error_summary(errors)
        assert summary["total"] == 3
        assert summary["fields_affected"] == 3


class TestErrorLogging:
    """Test error logging."""

    def test_log_errors_with_doc_id(self, caplog):
        """Test logging errors with document ID."""
        import logging
        caplog.set_level(logging.INFO)

        errors = [ErrorReporter.format_type_error("age", "x", "int")]
        ErrorReporter.log_errors(errors, doc_id="doc_123")
        # The function logs, so we just verify it doesn't raise an error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
