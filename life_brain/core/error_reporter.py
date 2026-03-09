"""
Validation Error Reporting — Detailed error messages for debugging.

Provides:
- Categorized error messages
- Debugging context
- Fix suggestions
- Error tracking and aggregation
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """A single validation error with context."""
    category: str  # "type", "enum", "range", "format", "required", "constraint"
    field: str
    value: Any
    expected: Optional[str] = None
    message: str = ""
    suggestion: str = ""
    severity: str = "error"  # error, warning, info


class ErrorReporter:
    """Generates helpful error messages for validation failures."""

    @staticmethod
    def format_type_error(field: str, value: Any, expected_type: str) -> ValidationError:
        """Format type mismatch error."""
        actual_type = type(value).__name__

        if expected_type == "int":
            suggestion = f"Ensure {field} is a whole number, not '{actual_type}'"
        elif expected_type == "float":
            suggestion = f"Ensure {field} is a decimal number, not '{actual_type}'"
        elif expected_type == "str":
            suggestion = f"Ensure {field} is text, not {actual_type}"
        else:
            suggestion = f"Expected {expected_type}, got {actual_type}"

        return ValidationError(
            category="type",
            field=field,
            value=value,
            expected=expected_type,
            message=f"Type mismatch: {field} is {actual_type}, expected {expected_type}",
            suggestion=suggestion,
            severity="error"
        )

    @staticmethod
    def format_enum_error(field: str, value: str, allowed_values: List[str]) -> ValidationError:
        """Format enum/choice error."""
        allowed_str = ", ".join(f"'{v}'" for v in allowed_values[:5])
        if len(allowed_values) > 5:
            allowed_str += f", ... ({len(allowed_values) - 5} more)"

        return ValidationError(
            category="enum",
            field=field,
            value=value,
            expected=allowed_str,
            message=f"Invalid value for {field}: '{value}'",
            suggestion=f"Choose from: {allowed_str}",
            severity="error"
        )

    @staticmethod
    def format_range_error(field: str, value: float, min_val: float, max_val: float) -> ValidationError:
        """Format numeric range error."""
        if min_val is not None and value < min_val:
            suggestion = f"{field} must be at least {min_val}, got {value}"
        elif max_val is not None and value > max_val:
            suggestion = f"{field} must be at most {max_val}, got {value}"
        else:
            suggestion = f"{field} must be between {min_val} and {max_val}, got {value}"

        return ValidationError(
            category="range",
            field=field,
            value=value,
            expected=f"{min_val}-{max_val}",
            message=f"Value out of range: {field}={value}",
            suggestion=suggestion,
            severity="error"
        )

    @staticmethod
    def format_format_error(field: str, value: str, format_name: str) -> ValidationError:
        """Format format/pattern error."""
        format_hints = {
            "ISO8601": "Date must be in format: 2026-03-08 or 2026-03-08T14:30:00",
            "email": "Email must be valid: user@example.com",
            "url": "URL must be valid: https://example.com",
            "phone": "Phone must be valid: +1-234-567-8900",
            "uuid": "UUID must be valid: 550e8400-e29b-41d4-a716-446655440000",
        }

        hint = format_hints.get(format_name, f"Invalid {format_name} format")

        return ValidationError(
            category="format",
            field=field,
            value=value,
            expected=format_name,
            message=f"Invalid format for {field}: {value}",
            suggestion=hint,
            severity="error"
        )

    @staticmethod
    def format_required_error(field: str) -> ValidationError:
        """Format missing required field error."""
        return ValidationError(
            category="required",
            field=field,
            value=None,
            message=f"Required field missing: {field}",
            suggestion=f"Provide a value for {field}",
            severity="error"
        )

    @staticmethod
    def format_constraint_error(field: str, constraint: str, details: str = "") -> ValidationError:
        """Format cross-field constraint error."""
        return ValidationError(
            category="constraint",
            field=field,
            value=None,
            message=f"Constraint violated: {constraint}",
            suggestion=f"Fix: {details}" if details else f"Review {constraint} constraint",
            severity="error"
        )

    @staticmethod
    def format_error_report(errors: List[ValidationError]) -> str:
        """
        Format multiple errors into readable report.

        Args:
            errors: List of ValidationError objects

        Returns:
            Formatted error report string
        """
        if not errors:
            return "✓ No validation errors"

        report = f"❌ VALIDATION ERRORS ({len(errors)} total)\n"
        report += "=" * 60 + "\n\n"

        # Group by category
        by_category = {}
        for error in errors:
            cat = error.category
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(error)

        # Report each category
        for category in sorted(by_category.keys()):
            cat_errors = by_category[category]
            report += f"🔴 {category.upper()} ({len(cat_errors)})\n"
            report += "-" * 40 + "\n"

            for error in cat_errors:
                report += f"  Field: {error.field}\n"
                report += f"  Message: {error.message}\n"
                if error.value is not None:
                    report += f"  Got: {error.value}\n"
                if error.expected:
                    report += f"  Expected: {error.expected}\n"
                report += f"  💡 Suggestion: {error.suggestion}\n"
                report += "\n"

        return report.strip()

    @staticmethod
    def categorize_errors(errors: List[ValidationError]) -> Dict[str, List[ValidationError]]:
        """
        Categorize errors for analysis.

        Returns:
            Dict of category → list of errors
        """
        categorized = {}
        for error in errors:
            cat = error.category
            if cat not in categorized:
                categorized[cat] = []
            categorized[cat].append(error)
        return categorized

    @staticmethod
    def get_error_summary(errors: List[ValidationError]) -> Dict[str, Any]:
        """
        Get summary statistics of validation errors.

        Returns:
            Dict with counts and breakdown
        """
        by_category = ErrorReporter.categorize_errors(errors)

        return {
            "total": len(errors),
            "by_category": {cat: len(errs) for cat, errs in by_category.items()},
            "critical": sum(1 for e in errors if e.severity == "error"),
            "warnings": sum(1 for e in errors if e.severity == "warning"),
            "info": sum(1 for e in errors if e.severity == "info"),
            "fields_affected": len(set(e.field for e in errors)),
        }

    @staticmethod
    def log_errors(errors: List[ValidationError], doc_id: str = "") -> None:
        """
        Log validation errors to logger.

        Args:
            errors: List of errors
            doc_id: Document ID for context
        """
        summary = ErrorReporter.get_error_summary(errors)

        logger.error(
            f"Validation failed for {doc_id}: "
            f"{summary['total']} errors ({summary['critical']} critical)",
            extra={"summary": summary}
        )

        for error in errors:
            if error.severity == "error":
                logger.error(f"  {error.field}: {error.message}")
            elif error.severity == "warning":
                logger.warning(f"  {error.field}: {error.message}")
            else:
                logger.info(f"  {error.field}: {error.message}")


def create_debug_context(
    field_name: str,
    value: Any,
    metadata: Dict[str, Any],
    error: ValidationError
) -> Dict[str, Any]:
    """
    Create debugging context for error investigation.

    Returns:
        Dict with debugging info
    """
    return {
        "field": field_name,
        "value": value,
        "value_type": type(value).__name__,
        "value_length": len(str(value)) if value else 0,
        "metadata_keys": list(metadata.keys()),
        "error": {
            "category": error.category,
            "message": error.message,
            "suggestion": error.suggestion,
        },
        "debug_info": {
            "is_none": value is None,
            "is_empty_string": value == "" if isinstance(value, str) else False,
            "is_zero": value == 0 if isinstance(value, (int, float)) else False,
            "repr": repr(value)[:100],
        }
    }
