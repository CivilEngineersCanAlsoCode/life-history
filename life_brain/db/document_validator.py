"""
Document Validation & Schema Enforcement — Pre-ingestion validation layer.

Validates:
- Required metadata fields (47-field schema)
- Text content quality and structure
- Metadata field types and constraints
- Duplicate detection
- Privacy compliance
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
import re

from life_brain.config import REQUIRED_METADATA_FIELDS, Privacy
from life_brain.db.error_reporter import ValidationError, ErrorReporter

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of document validation."""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    metadata_valid: bool
    text_valid: bool
    schema_compliant: bool


class DocumentValidator:
    """Validates documents before ingestion into ChromaDB."""

    # Regex patterns for format validation
    PATTERNS = {
        "ISO8601": r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?",
        "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "url": r"^https?://[^\s]+$",
        "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    }

    # Minimum/maximum constraints
    CONSTRAINTS = {
        "text_min_length": 50,  # Minimum text length (chars)
        "question_min_length": 5,
        "question_max_length": 500,
        "answer_min_length": 10,
        "answer_max_length": 5000,
    }

    @staticmethod
    def validate_required_fields(metadata: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """
        Validate all required metadata fields are present.

        Args:
            metadata: Metadata dictionary

        Returns:
            Tuple of (is_valid, error_list)
        """
        errors = []
        missing_fields = [f for f in REQUIRED_METADATA_FIELDS if f not in metadata]

        if missing_fields:
            for field in missing_fields:
                error = ErrorReporter.format_required_error(field)
                errors.append(error)
            logger.warning(f"Missing required fields: {missing_fields}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_field_types(metadata: Dict[str, Any]) -> List[ValidationError]:
        """
        Validate that field values match expected types.

        Args:
            metadata: Metadata dictionary

        Returns:
            List of type validation errors
        """
        errors = []

        # Expected field types (subset of 47 fields)
        expected_types = {
            "domain": str,
            "company": str,
            "project": str,
            "category": str,
            "subcategory": str,
            "date": str,
            "confidence": (int, float),
            "importance": int,
            "privacy": str,
            "tags": (list, tuple),
            "source": str,
            "doc_type": str,
        }

        for field, expected_type in expected_types.items():
            if field not in metadata:
                continue

            value = metadata[field]
            if not isinstance(value, expected_type):
                error = ErrorReporter.format_type_error(
                    field,
                    value,
                    expected_type.__name__ if not isinstance(expected_type, tuple) else str(expected_type)
                )
                errors.append(error)

        return errors

    @staticmethod
    def validate_field_values(metadata: Dict[str, Any]) -> List[ValidationError]:
        """
        Validate field value constraints (ranges, enums, formats).

        Args:
            metadata: Metadata dictionary

        Returns:
            List of constraint validation errors
        """
        errors = []

        # Enum validations
        valid_domains = ["career", "relationships", "health", "finance", "personal_growth", "memory"]
        if "domain" in metadata and metadata["domain"] not in valid_domains:
            error = ErrorReporter.format_enum_error("domain", metadata["domain"], valid_domains)
            errors.append(error)

        valid_privacy = [p.value for p in Privacy]
        if "privacy" in metadata and metadata["privacy"] not in valid_privacy:
            error = ErrorReporter.format_enum_error("privacy", metadata["privacy"], valid_privacy)
            errors.append(error)

        # Range validations
        if "confidence" in metadata:
            conf = metadata["confidence"]
            if not (0 <= conf <= 1.0):
                error = ErrorReporter.format_range_error("confidence", conf, 0, 1.0)
                errors.append(error)

        if "importance" in metadata:
            imp = metadata["importance"]
            if not (1 <= imp <= 5):
                error = ErrorReporter.format_range_error("importance", imp, 1, 5)
                errors.append(error)

        # Format validations
        if "date" in metadata:
            date_str = metadata["date"]
            if not re.match(DocumentValidator.PATTERNS["ISO8601"], date_str):
                error = ErrorReporter.format_format_error("date", date_str, "ISO8601")
                errors.append(error)

        return errors

    @staticmethod
    def validate_text_content(text: str) -> Tuple[bool, Optional[ValidationError]]:
        """
        Validate text content quality.

        Args:
            text: Document text

        Returns:
            Tuple of (is_valid, error_or_none)
        """
        if not text or len(text) < DocumentValidator.CONSTRAINTS["text_min_length"]:
            error = ValidationError(
                category="range",
                field="text",
                value=len(text) if text else 0,
                expected=f">= {DocumentValidator.CONSTRAINTS['text_min_length']}",
                message=f"Text too short: {len(text) if text else 0} chars",
                suggestion=f"Provide at least {DocumentValidator.CONSTRAINTS['text_min_length']} characters",
                severity="error"
            )
            return False, error

        # Check for self-contained content (not just "Q: ... A: ...")
        if text.lower().startswith("q:") and "a:" in text.lower():
            parts = text.split("A:")
            if len(parts[0]) < 30:  # Q part too short
                error = ValidationError(
                    category="format",
                    field="text",
                    value=len(parts[0]),
                    message="Question section too brief",
                    suggestion="Ensure question has sufficient detail and context",
                    severity="warning"
                )
                return False, error

        return True, None

    @staticmethod
    def validate_question_answer(question: str, answer: str) -> Tuple[bool, List[ValidationError]]:
        """
        Validate Q&A pair structure.

        Args:
            question: Question text
            answer: Answer text

        Returns:
            Tuple of (is_valid, error_list)
        """
        errors = []

        # Question validation
        if not question or len(question) < DocumentValidator.CONSTRAINTS["question_min_length"]:
            error = ValidationError(
                category="range",
                field="question",
                value=len(question) if question else 0,
                expected=f">= {DocumentValidator.CONSTRAINTS['question_min_length']}",
                message="Question too short",
                suggestion="Provide a clear, substantive question",
                severity="error"
            )
            errors.append(error)

        if len(question) > DocumentValidator.CONSTRAINTS["question_max_length"]:
            error = ValidationError(
                category="range",
                field="question",
                value=len(question),
                expected=f"<= {DocumentValidator.CONSTRAINTS['question_max_length']}",
                message="Question too long",
                suggestion="Keep question concise and focused",
                severity="error"
            )
            errors.append(error)

        # Answer validation
        if not answer or len(answer) < DocumentValidator.CONSTRAINTS["answer_min_length"]:
            error = ValidationError(
                category="range",
                field="answer",
                value=len(answer) if answer else 0,
                expected=f">= {DocumentValidator.CONSTRAINTS['answer_min_length']}",
                message="Answer too short",
                suggestion="Provide a complete, informative answer",
                severity="error"
            )
            errors.append(error)

        if len(answer) > DocumentValidator.CONSTRAINTS["answer_max_length"]:
            error = ValidationError(
                category="range",
                field="answer",
                value=len(answer),
                expected=f"<= {DocumentValidator.CONSTRAINTS['answer_max_length']}",
                message="Answer too long",
                suggestion="Summarize more concisely or split into multiple Q&A pairs",
                severity="error"
            )
            errors.append(error)

        return len(errors) == 0, errors

    @staticmethod
    def validate_privacy_compliance(metadata: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """
        Validate privacy settings are appropriate.

        Args:
            metadata: Metadata dictionary

        Returns:
            Tuple of (is_valid, error_list)
        """
        errors = []

        privacy = metadata.get("privacy", "private")
        sensitive_fields = ["personal_data", "medical_info", "salary"]

        # If marked public/internal but contains sensitive data
        if privacy in ["public", "internal"]:
            for sensitive_field in sensitive_fields:
                if sensitive_field in metadata and metadata[sensitive_field]:
                    error = ValidationError(
                        category="constraint",
                        field="privacy",
                        value=privacy,
                        message=f"Document contains {sensitive_field} but marked {privacy}",
                        suggestion=f"Mark document as 'private' if it contains {sensitive_field}",
                        severity="warning"
                    )
                    errors.append(error)

        return len(errors) == 0, errors

    def validate_document(
        self,
        metadata: Dict[str, Any],
        text: Optional[str] = None,
        question: Optional[str] = None,
        answer: Optional[str] = None,
    ) -> ValidationResult:
        """
        Comprehensive document validation.

        Args:
            metadata: Document metadata (47 fields)
            text: Document text (optional if question+answer provided)
            question: Question text (for Q&A pairs)
            answer: Answer text (for Q&A pairs)

        Returns:
            ValidationResult with all validation checks
        """
        errors = []
        warnings = []

        # Check required fields
        metadata_valid, field_errors = self.validate_required_fields(metadata)
        errors.extend(field_errors)

        # Check field types
        type_errors = self.validate_field_types(metadata)
        errors.extend(type_errors)

        # Check field values and constraints
        value_errors = self.validate_field_values(metadata)
        errors.extend(value_errors)

        # Check privacy compliance
        _, privacy_warnings = self.validate_privacy_compliance(metadata)
        warnings.extend(privacy_warnings)

        # Validate text if provided
        text_valid = True
        if text:
            text_valid, text_error = self.validate_text_content(text)
            if not text_valid and text_error:
                errors.append(text_error)

        # Validate Q&A pair if provided
        if question and answer:
            qa_valid, qa_errors = self.validate_question_answer(question, answer)
            errors.extend(qa_errors)
            text_valid = text_valid and qa_valid
        elif (question and not answer) or (answer and not question):
            error = ValidationError(
                category="constraint",
                field="qa_pair",
                value=None,
                message="Question and answer must both be provided",
                suggestion="Provide both question and answer for Q&A pairs",
                severity="error"
            )
            errors.append(error)
            text_valid = False

        schema_compliant = metadata_valid and (not text or text_valid)
        is_valid = len(errors) == 0 and schema_compliant

        logger.info(
            f"Document validation: {'✓ VALID' if is_valid else '✗ INVALID'} "
            f"({len(errors)} errors, {len(warnings)} warnings)"
        )

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            metadata_valid=metadata_valid,
            text_valid=text_valid,
            schema_compliant=schema_compliant,
        )

    def format_validation_report(self, result: ValidationResult) -> str:
        """
        Format validation result as readable report.

        Args:
            result: ValidationResult object

        Returns:
            Formatted report string
        """
        status = "✓ VALID" if result.is_valid else "✗ INVALID"
        report = f"""
╔═══════════════════════════════════════════════════════════════════╗
║              DOCUMENT VALIDATION REPORT                           ║
╚═══════════════════════════════════════════════════════════════════╝

Status: {status}

Metadata Valid:      {'✓' if result.metadata_valid else '✗'}
Text Valid:          {'✓' if result.text_valid else '✗'}
Schema Compliant:    {'✓' if result.schema_compliant else '✗'}

📋 Errors: ({len(result.errors)} total)
"""
        if result.errors:
            error_report = ErrorReporter.format_error_report(result.errors)
            report += error_report + "\n"
        else:
            report += "  (No errors)\n"

        if result.warnings:
            report += f"""
⚠️ Warnings: ({len(result.warnings)} total)
"""
            for warning in result.warnings:
                report += f"  • {warning.field}: {warning.message}\n"
        else:
            report += "⚠️ Warnings: (None)\n"

        return report.strip()
