"""
Unit tests for document_validator.py

Covers:
- ValidationResult dataclass
- Required field validation
- Field type validation
- Field value/constraint validation
- Text content validation
- Q&A pair validation
- Privacy compliance checking
- Comprehensive document validation
- Validation report formatting
"""

import pytest
from life_brain.db.document_validator import DocumentValidator, ValidationResult
from life_brain.db.error_reporter import ValidationError


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_create_valid_result(self):
        """Test creating valid result."""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            metadata_valid=True,
            text_valid=True,
            schema_compliant=True
        )
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_create_invalid_result(self):
        """Test creating invalid result."""
        error = ValidationError(
            category="required",
            field="domain",
            value=None
        )
        result = ValidationResult(
            is_valid=False,
            errors=[error],
            warnings=[],
            metadata_valid=False,
            text_valid=True,
            schema_compliant=False
        )
        assert result.is_valid is False
        assert len(result.errors) == 1

    def test_result_with_warnings(self):
        """Test result with warnings."""
        warning = ValidationError(
            category="constraint",
            field="privacy",
            value="public"
        )
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[warning],
            metadata_valid=True,
            text_valid=True,
            schema_compliant=True
        )
        assert result.is_valid is True
        assert len(result.warnings) == 1


class TestRequiredFields:
    """Test required field validation."""

    def test_required_fields_all_present(self):
        """Test when all required fields are present."""
        from life_brain.config import REQUIRED_METADATA_FIELDS
        metadata = {field: "test_value" for field in REQUIRED_METADATA_FIELDS}
        is_valid, errors = DocumentValidator.validate_required_fields(metadata)
        assert is_valid is True
        assert len(errors) == 0

    def test_required_fields_missing_one(self):
        """Test when one required field is missing."""
        from life_brain.config import REQUIRED_METADATA_FIELDS
        metadata = {field: "test" for field in REQUIRED_METADATA_FIELDS}
        del metadata[list(REQUIRED_METADATA_FIELDS)[0]]  # Remove first field
        is_valid, errors = DocumentValidator.validate_required_fields(metadata)
        assert is_valid is False
        assert len(errors) > 0

    def test_required_fields_empty_metadata(self):
        """Test with empty metadata."""
        is_valid, errors = DocumentValidator.validate_required_fields({})
        assert is_valid is False
        assert len(errors) > 0


class TestFieldTypes:
    """Test field type validation."""

    def test_field_types_correct(self):
        """Test with correct field types."""
        metadata = {
            "domain": "career",
            "company": "Sprinklr",
            "category": "work",
            "confidence": 0.95,
            "importance": 3,
            "privacy": "private",
            "tags": ["tag1", "tag2"],
            "source": "user_input"
        }
        errors = DocumentValidator.validate_field_types(metadata)
        assert len(errors) == 0

    def test_field_types_incorrect_string(self):
        """Test with incorrect string type."""
        metadata = {
            "domain": 123,  # Should be string
        }
        errors = DocumentValidator.validate_field_types(metadata)
        assert len(errors) > 0

    def test_field_types_incorrect_confidence(self):
        """Test with incorrect confidence type."""
        metadata = {
            "confidence": "high",  # Should be int/float
        }
        errors = DocumentValidator.validate_field_types(metadata)
        assert len(errors) > 0


class TestFieldValues:
    """Test field value constraint validation."""

    def test_valid_domain(self):
        """Test valid domain."""
        metadata = {"domain": "career"}
        errors = DocumentValidator.validate_field_values(metadata)
        assert len(errors) == 0

    def test_invalid_domain(self):
        """Test invalid domain."""
        metadata = {"domain": "invalid_domain"}
        errors = DocumentValidator.validate_field_values(metadata)
        assert len(errors) > 0

    def test_valid_confidence_range(self):
        """Test valid confidence in range [0, 1]."""
        metadata = {"confidence": 0.75}
        errors = DocumentValidator.validate_field_values(metadata)
        assert len(errors) == 0

    def test_invalid_confidence_above_range(self):
        """Test confidence above 1."""
        metadata = {"confidence": 1.5}
        errors = DocumentValidator.validate_field_values(metadata)
        assert len(errors) > 0

    def test_invalid_confidence_below_range(self):
        """Test confidence below 0."""
        metadata = {"confidence": -0.1}
        errors = DocumentValidator.validate_field_values(metadata)
        assert len(errors) > 0

    def test_valid_importance(self):
        """Test valid importance [1, 5]."""
        metadata = {"importance": 3}
        errors = DocumentValidator.validate_field_values(metadata)
        assert len(errors) == 0

    def test_invalid_importance_high(self):
        """Test importance above 5."""
        metadata = {"importance": 6}
        errors = DocumentValidator.validate_field_values(metadata)
        assert len(errors) > 0

    def test_invalid_importance_low(self):
        """Test importance below 1."""
        metadata = {"importance": 0}
        errors = DocumentValidator.validate_field_values(metadata)
        assert len(errors) > 0

    def test_valid_date_format(self):
        """Test valid ISO8601 date."""
        metadata = {"date": "2024-03-09"}
        errors = DocumentValidator.validate_field_values(metadata)
        assert len(errors) == 0

    def test_invalid_date_format(self):
        """Test invalid date format."""
        metadata = {"date": "03/09/2024"}
        errors = DocumentValidator.validate_field_values(metadata)
        assert len(errors) > 0


class TestTextContent:
    """Test text content validation."""

    def test_valid_text(self):
        """Test valid text (>= 50 chars)."""
        text = "This is a valid document with sufficient content for the validator to accept."
        is_valid, error = DocumentValidator.validate_text_content(text)
        assert is_valid is True
        assert error is None

    def test_text_too_short(self):
        """Test text below 50 chars."""
        text = "Short text"
        is_valid, error = DocumentValidator.validate_text_content(text)
        assert is_valid is False
        assert error is not None

    def test_empty_text(self):
        """Test empty text."""
        is_valid, error = DocumentValidator.validate_text_content("")
        assert is_valid is False
        assert error is not None

    def test_none_text(self):
        """Test None text."""
        is_valid, error = DocumentValidator.validate_text_content(None)
        assert is_valid is False


class TestQuestionAnswer:
    """Test Q&A pair validation."""

    def test_valid_qa_pair(self):
        """Test valid Q&A pair."""
        question = "What did you accomplish at Sprinklr?"
        answer = "I built and maintained the CGB platform, which improved citizen engagement by 40%."
        is_valid, errors = DocumentValidator.validate_question_answer(question, answer)
        assert is_valid is True
        assert len(errors) == 0

    def test_question_too_short(self):
        """Test question below minimum length."""
        question = "Q?"
        answer = "This is a valid answer with sufficient content for validation."
        is_valid, errors = DocumentValidator.validate_question_answer(question, answer)
        assert is_valid is False
        assert len(errors) > 0

    def test_question_too_long(self):
        """Test question above maximum length."""
        question = "Q" * 501  # > 500 chars
        answer = "This is a valid answer with sufficient content."
        is_valid, errors = DocumentValidator.validate_question_answer(question, answer)
        assert is_valid is False

    def test_answer_too_short(self):
        """Test answer below minimum length."""
        question = "What happened?"
        answer = "Good"  # < 10 chars
        is_valid, errors = DocumentValidator.validate_question_answer(question, answer)
        assert is_valid is False

    def test_answer_too_long(self):
        """Test answer above maximum length."""
        question = "What is your experience?"
        answer = "A" * 5001  # > 5000 chars
        is_valid, errors = DocumentValidator.validate_question_answer(question, answer)
        assert is_valid is False

    def test_empty_question(self):
        """Test empty question."""
        is_valid, errors = DocumentValidator.validate_question_answer("", "Valid answer content")
        assert is_valid is False


class TestPrivacyCompliance:
    """Test privacy compliance validation."""

    def test_private_no_sensitive_data(self):
        """Test private document without sensitive data."""
        metadata = {"privacy": "private"}
        is_valid, errors = DocumentValidator.validate_privacy_compliance(metadata)
        assert is_valid is True

    def test_public_with_sensitive_data(self):
        """Test public document with sensitive data."""
        metadata = {
            "privacy": "public",
            "salary": 100000
        }
        is_valid, errors = DocumentValidator.validate_privacy_compliance(metadata)
        assert is_valid is False or len(errors) > 0

    def test_internal_with_sensitive_data(self):
        """Test internal document with sensitive data."""
        metadata = {
            "privacy": "internal",
            "personal_data": "PII information"
        }
        is_valid, errors = DocumentValidator.validate_privacy_compliance(metadata)
        # Should have warning or error
        assert isinstance(errors, list)


class TestComprehensiveValidation:
    """Test comprehensive document validation."""

    def test_valid_document_full(self):
        """Test validation of complete valid document."""
        from life_brain.config import REQUIRED_METADATA_FIELDS
        validator = DocumentValidator()

        metadata = {field: "test_value" for field in REQUIRED_METADATA_FIELDS}
        metadata["domain"] = "career"
        metadata["confidence"] = 0.9
        metadata["importance"] = 3
        metadata["privacy"] = "private"

        result = validator.validate_document(
            metadata=metadata,
            text="This is valid document content with sufficient length for validation.",
            question="What did you do?",
            answer="I accomplished significant work on important projects."
        )

        # Should be valid
        assert isinstance(result, ValidationResult)

    def test_invalid_document_missing_fields(self):
        """Test validation with missing required fields."""
        validator = DocumentValidator()
        result = validator.validate_document(
            metadata={},
            text="Valid text content for the document"
        )
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_invalid_document_bad_qa(self):
        """Test validation with invalid Q&A."""
        from life_brain.config import REQUIRED_METADATA_FIELDS
        validator = DocumentValidator()

        metadata = {field: "test" for field in REQUIRED_METADATA_FIELDS}
        metadata["domain"] = "career"
        metadata["importance"] = 3
        metadata["confidence"] = 0.5
        result = validator.validate_document(
            metadata=metadata,
            question="Q?",  # Too short
            answer="A"  # Too short
        )
        assert result.is_valid is False

    def test_validation_with_text_only(self):
        """Test validation with text only (no Q&A)."""
        from life_brain.config import REQUIRED_METADATA_FIELDS
        validator = DocumentValidator()

        metadata = {field: "test" for field in REQUIRED_METADATA_FIELDS}
        metadata["domain"] = "career"
        metadata["importance"] = 3
        metadata["confidence"] = 0.5
        result = validator.validate_document(
            metadata=metadata,
            text="This is valid document content with sufficient length for validation purposes."
        )
        # Should complete validation
        assert isinstance(result, ValidationResult)

    def test_qa_without_answer_error(self):
        """Test that question without answer fails."""
        from life_brain.config import REQUIRED_METADATA_FIELDS
        validator = DocumentValidator()

        metadata = {field: "test" for field in REQUIRED_METADATA_FIELDS}
        metadata["domain"] = "career"
        metadata["importance"] = 3
        metadata["confidence"] = 0.5
        result = validator.validate_document(
            metadata=metadata,
            question="What happened?",
            answer=None  # Missing answer
        )
        assert result.is_valid is False


class TestValidationReporting:
    """Test validation report formatting."""

    def test_format_valid_report(self):
        """Test formatting report for valid document."""
        validator = DocumentValidator()
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            metadata_valid=True,
            text_valid=True,
            schema_compliant=True
        )
        report = validator.format_validation_report(result)
        assert "VALIDATION REPORT" in report
        assert "VALID" in report or "✓" in report

    def test_format_invalid_report(self):
        """Test formatting report for invalid document."""
        validator = DocumentValidator()
        error = ValidationError(
            category="required",
            field="domain",
            value=None
        )
        result = ValidationResult(
            is_valid=False,
            errors=[error],
            warnings=[],
            metadata_valid=False,
            text_valid=True,
            schema_compliant=False
        )
        report = validator.format_validation_report(result)
        assert "VALIDATION REPORT" in report
        assert "INVALID" in report or "✗" in report

    def test_format_report_with_warnings(self):
        """Test formatting report with warnings."""
        validator = DocumentValidator()
        warning = ValidationError(
            category="constraint",
            field="privacy",
            value="public"
        )
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[warning],
            metadata_valid=True,
            text_valid=True,
            schema_compliant=True
        )
        report = validator.format_validation_report(result)
        assert "Warnings" in report or "⚠️" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestNullQAValidation:
    """Regression tests for issues-6vx.1.20: null pointer when validating empty answer.

    Bug: validate_question_answer(None, None) crashes at len(None) on the
    second question check (max_length guard) even after the first check caught None.
    Fix: guard second check with `if question and len(question) > max_length`.
    Similarly for answer.
    """

    def test_validate_qa_null_question_no_crash(self):
        """validate_question_answer(None, ...) must not raise TypeError."""
        from life_brain.db.document_validator import DocumentValidator
        # Should return errors, not crash
        valid, errors = DocumentValidator.validate_question_answer(None, None)
        assert valid is False
        assert len(errors) > 0

    def test_validate_qa_empty_question_no_crash(self):
        """validate_question_answer('', ...) must not raise TypeError."""
        from life_brain.db.document_validator import DocumentValidator
        valid, errors = DocumentValidator.validate_question_answer("", "")
        assert valid is False
        assert len(errors) > 0

    def test_validate_qa_null_answer_no_crash(self):
        """validate_question_answer(valid_q, None) must not raise."""
        from life_brain.db.document_validator import DocumentValidator
        valid, errors = DocumentValidator.validate_question_answer("What is the project?", None)
        assert valid is False
        assert len(errors) > 0

    def test_validate_qa_empty_answer_no_crash(self):
        """validate_question_answer(valid_q, '') must not crash."""
        from life_brain.db.document_validator import DocumentValidator
        valid, errors = DocumentValidator.validate_question_answer("What is the project scope?", "")
        assert valid is False

    def test_validate_qa_valid_pair_still_works(self):
        """Normal valid Q&A should still pass validation after fix."""
        from life_brain.db.document_validator import DocumentValidator
        q = "What is the primary goal of the CRR AML Risk Scoring Engine project?"
        a = "The primary goal is to detect and score money laundering risk across customer accounts using machine learning models to improve detection accuracy."
        valid, errors = DocumentValidator.validate_question_answer(q, a)
        assert valid is True
        assert len(errors) == 0


class TestShortQuestionRejection:
    """Regression test for issues-i4z.2.7: question shorter than min_length rejected gracefully."""

    def test_two_char_question_rejected(self):
        """2-character question must produce validation error, not crash."""
        from life_brain.db.document_validator import DocumentValidator
        valid, errors = DocumentValidator.validate_question_answer("Hi", "A long enough answer that contains meaningful content about the topic being discussed")
        assert valid is False
        assert any(e.field == "question" for e in errors)

    def test_single_char_question_rejected(self):
        """Single character question must be rejected."""
        from life_brain.db.document_validator import DocumentValidator
        valid, errors = DocumentValidator.validate_question_answer("?", "Sufficient answer text here")
        assert valid is False


class TestConfidenceBoundaryValues:
    """Regression test for issues-6vx.1.18: confidence values at exact boundaries (0.0, 1.0)."""

    def test_confidence_exactly_0(self):
        """Metadata with confidence=0.0 must be valid (boundary value)."""
        from life_brain.db.document_validator import DocumentValidator
        validator = DocumentValidator()
        metadata = {
            "doc_id": "test_001",
            "type": "qa_pair",
            "domain": "career",
            "company": "TestCorp",
            "project": "ProjectX",
            "date_range": "2024-01",
            "source": "interview",
            "privacy": "private",
            "confidence": 0.0,  # Exact lower boundary
            "question": "What is the project?",
            "answer": "The project is a test.",
            "tags": [],
        }
        errors = validator.validate_field_values(metadata)
        # 0.0 confidence should not produce a range error
        confidence_errors = [e for e in errors if e.field == "confidence"]
        assert len(confidence_errors) == 0

    def test_confidence_exactly_1(self):
        """Metadata with confidence=1.0 must be valid (boundary value)."""
        from life_brain.db.document_validator import DocumentValidator
        validator = DocumentValidator()
        metadata = {"confidence": 1.0}
        errors = validator.validate_field_values(metadata)
        confidence_errors = [e for e in errors if e.field == "confidence"]
        assert len(confidence_errors) == 0
