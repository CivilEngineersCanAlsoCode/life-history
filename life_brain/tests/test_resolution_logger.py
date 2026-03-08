"""
Test suite for resolution logger.

Tests cover:
- Resolution log creation and validation
- Logging decisions with reasoning
- Query and retrieval
- Statistics and reporting
- Audit trail generation
"""

import pytest
from datetime import datetime, timedelta

from life_brain.conflict.resolution_logger import (
    ResolutionLog,
    ResolutionLogger,
    LogLevel,
)


class TestResolutionLog:
    """Test ResolutionLog dataclass."""

    def test_create_log(self):
        """Test creating a resolution log."""
        log = ResolutionLog(
            log_id="log_001",
            document_id="doc_001",
            field_name="company",
            existing_value="Amex",
            new_value="American Express",
            chosen_resolution="use_new",
            resolved_value="American Express",
            reasoning="New value is more formal and accurate",
        )

        assert log.document_id == "doc_001"
        assert log.field_name == "company"
        assert log.reasoning == "New value is more formal and accurate"

    def test_to_dict(self):
        """Test converting log to dictionary."""
        log = ResolutionLog(
            log_id="log_001",
            document_id="doc_001",
            field_name="company",
            existing_value="Amex",
            new_value="American Express",
            chosen_resolution="use_new",
            resolved_value="American Express",
            reasoning="Accurate name",
        )

        log_dict = log.to_dict()
        assert log_dict["document_id"] == "doc_001"
        assert log_dict["chosen_resolution"] == "use_new"

    def test_validate_valid_log(self):
        """Test validating valid log."""
        log = ResolutionLog(
            log_id="log_001",
            document_id="doc_001",
            field_name="company",
            existing_value="Amex",
            new_value="American Express",
            chosen_resolution="use_new",
            resolved_value="American Express",
            reasoning="Accurate",
        )

        is_valid, errors = log.validate()
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_empty_reasoning(self):
        """Test validation with empty reasoning."""
        log = ResolutionLog(
            log_id="log_001",
            document_id="doc_001",
            field_name="company",
            existing_value="Amex",
            new_value="American Express",
            chosen_resolution="use_new",
            resolved_value="American Express",
            reasoning="",  # Empty
        )

        is_valid, errors = log.validate()
        assert is_valid is False
        assert any("reasoning" in e for e in errors)

    def test_validate_invalid_resolution(self):
        """Test validation with invalid resolution."""
        log = ResolutionLog(
            log_id="log_001",
            document_id="doc_001",
            field_name="company",
            existing_value="Amex",
            new_value="American Express",
            chosen_resolution="invalid",  # Invalid
            resolved_value="American Express",
            reasoning="Test",
        )

        is_valid, errors = log.validate()
        assert is_valid is False
        assert any("chosen_resolution" in e for e in errors)


class TestResolutionLogger:
    """Test ResolutionLogger functionality."""

    def test_create_logger(self):
        """Test creating resolution logger."""
        logger = ResolutionLogger()
        assert len(logger.logs) == 0

    def test_resolution_logger_single_entry(self):
        """Test logging a single resolution."""
        logger = ResolutionLogger()

        log = logger.resolution_logger(
            document_id="doc_001",
            field_name="company",
            existing_value="Amex",
            new_value="American Express",
            chosen_resolution="use_new",
            resolved_value="American Express",
            reasoning="New value is more accurate",
        )

        assert log.document_id == "doc_001"
        assert log.field_name == "company"
        assert len(logger.logs) == 1

    def test_resolution_logger_multiple_entries(self):
        """Test logging multiple resolutions."""
        logger = ResolutionLogger()

        for i in range(3):
            logger.resolution_logger(
                document_id=f"doc_{i:03d}",
                field_name=f"field_{i}",
                existing_value=f"old_{i}",
                new_value=f"new_{i}",
                chosen_resolution="keep_existing",
                resolved_value=f"old_{i}",
                reasoning=f"Reason {i}",
            )

        assert len(logger.logs) == 3

    def test_get_logs_for_document(self):
        """Test retrieving logs for a document."""
        logger = ResolutionLogger()

        logger.resolution_logger(
            "doc_001",
            "field1",
            "old1",
            "new1",
            "use_new",
            "new1",
            "Reason 1",
        )
        logger.resolution_logger(
            "doc_001",
            "field2",
            "old2",
            "new2",
            "keep_existing",
            "old2",
            "Reason 2",
        )
        logger.resolution_logger(
            "doc_002",
            "field1",
            "old",
            "new",
            "merge",
            "merged",
            "Reason 3",
        )

        doc_001_logs = logger.get_logs_for_document("doc_001")
        assert len(doc_001_logs) == 2

    def test_get_logs_for_field(self):
        """Test retrieving logs for a field."""
        logger = ResolutionLogger()

        for i in range(3):
            logger.resolution_logger(
                f"doc_{i}",
                "company",
                "old",
                "new",
                "use_new",
                "new",
                f"Reason {i}",
            )

        logger.resolution_logger(
            "doc_3",
            "role",
            "old",
            "new",
            "use_new",
            "new",
            "Reason 4",
        )

        company_logs = logger.get_logs_for_field("company")
        assert len(company_logs) == 3

    def test_get_logs_by_decision_maker(self):
        """Test filtering by decision maker."""
        logger = ResolutionLogger()

        logger.resolution_logger(
            "doc_001",
            "field1",
            "old",
            "new",
            "use_new",
            "new",
            "User decided",
            decided_by="user",
        )

        logger.resolution_logger(
            "doc_002",
            "field2",
            "old",
            "new",
            "keep_existing",
            "old",
            "System decided",
            decided_by="system",
        )

        logger.resolution_logger(
            "doc_003",
            "field3",
            "old",
            "new",
            "merge",
            "merged",
            "Auto decided",
            decided_by="auto",
        )

        user_logs = logger.get_logs_by_decision_maker("user")
        assert len(user_logs) == 1

    def test_get_logs_by_level(self):
        """Test filtering by log level."""
        logger = ResolutionLogger()

        logger.resolution_logger(
            "doc_001",
            "field1",
            "old",
            "new",
            "use_new",
            "new",
            "Info level",
            log_level=LogLevel.INFO,
        )

        logger.resolution_logger(
            "doc_002",
            "field2",
            "old",
            "new",
            "keep_existing",
            "old",
            "Warning level",
            log_level=LogLevel.WARNING,
        )

        logger.resolution_logger(
            "doc_003",
            "field3",
            "old",
            "new",
            "merge",
            "merged",
            "Error level",
            log_level=LogLevel.ERROR,
        )

        warning_logs = logger.get_logs_by_level(LogLevel.WARNING)
        assert len(warning_logs) == 1

    def test_get_logs_for_document_field(self):
        """Test getting resolution history for field in document."""
        logger = ResolutionLogger()

        # Multiple resolutions for same field
        logger.resolution_logger(
            "doc_001",
            "company",
            "Amex",
            "American Express",
            "use_new",
            "American Express",
            "First resolution",
        )

        logger.resolution_logger(
            "doc_001",
            "company",
            "American Express",
            "AmEx",
            "keep_existing",
            "American Express",
            "Second resolution",
        )

        logger.resolution_logger(
            "doc_001",
            "role",
            "PM",
            "Product Manager",
            "use_new",
            "Product Manager",
            "Third resolution",
        )

        company_history = logger.get_logs_for_document_field("doc_001", "company")
        assert len(company_history) == 2

    def test_get_document_audit_trail(self):
        """Test getting complete audit trail for document."""
        logger = ResolutionLogger()

        logger.resolution_logger(
            "doc_001",
            "field1",
            "old1",
            "new1",
            "use_new",
            "new1",
            "Reason 1",
        )
        logger.resolution_logger(
            "doc_001",
            "field2",
            "old2",
            "new2",
            "keep_existing",
            "old2",
            "Reason 2",
        )

        audit = logger.get_document_audit_trail("doc_001")

        assert audit["document_id"] == "doc_001"
        assert audit["total_resolutions"] == 2
        assert "use_new" in audit["by_resolution"]

    def test_get_field_resolution_history(self):
        """Test getting field resolution history across documents."""
        logger = ResolutionLogger()

        for i in range(3):
            logger.resolution_logger(
                f"doc_{i}",
                "priority",
                "low",
                "high",
                "use_new",
                "high",
                f"Reason {i}",
            )

        history = logger.get_field_resolution_history("priority")

        assert history["field_name"] == "priority"
        assert history["total_resolutions"] == 3
        assert history["documents_affected"] == 3

    def test_get_statistics_empty(self):
        """Test statistics on empty logger."""
        logger = ResolutionLogger()
        stats = logger.get_statistics()

        assert stats["total_logs"] == 0
        assert stats["total_documents"] == 0

    def test_get_statistics_populated(self):
        """Test statistics on populated logger."""
        logger = ResolutionLogger()

        # Add various resolutions
        logger.resolution_logger(
            "doc_1",
            "field1",
            "old",
            "new",
            "use_new",
            "new",
            "Reason 1",
            decided_by="user",
        )
        logger.resolution_logger(
            "doc_1",
            "field2",
            "old",
            "new",
            "keep_existing",
            "old",
            "Reason 2",
            decided_by="system",
        )
        logger.resolution_logger(
            "doc_2",
            "field1",
            "old",
            "new",
            "merge",
            "merged",
            "Reason 3",
            decided_by="user",
        )

        stats = logger.get_statistics()

        assert stats["total_logs"] == 3
        assert stats["total_documents"] == 2
        assert stats["total_fields"] == 2
        assert stats["by_resolution"]["use_new"] == 1

    def test_export_logs(self):
        """Test exporting all logs."""
        logger = ResolutionLogger()

        logger.resolution_logger(
            "doc_001",
            "field1",
            "old",
            "new",
            "use_new",
            "new",
            "Reason 1",
        )
        logger.resolution_logger(
            "doc_002",
            "field2",
            "old",
            "new",
            "keep_existing",
            "old",
            "Reason 2",
        )

        exported = logger.export_logs()
        assert len(exported) == 2
        assert all("timestamp" in log for log in exported)

    def test_export_document_logs(self):
        """Test exporting logs for a document."""
        logger = ResolutionLogger()

        logger.resolution_logger(
            "doc_001",
            "field1",
            "old1",
            "new1",
            "use_new",
            "new1",
            "Reason 1",
        )
        logger.resolution_logger(
            "doc_001",
            "field2",
            "old2",
            "new2",
            "keep_existing",
            "old2",
            "Reason 2",
        )

        exported = logger.export_document_logs("doc_001")
        assert len(exported) == 2

    def test_get_warnings_and_errors(self):
        """Test filtering warnings and errors."""
        logger = ResolutionLogger()

        logger.resolution_logger(
            "doc_001",
            "field1",
            "old",
            "new",
            "use_new",
            "new",
            "Warning case",
            log_level=LogLevel.WARNING,
        )

        logger.resolution_logger(
            "doc_002",
            "field2",
            "old",
            "new",
            "keep_existing",
            "old",
            "Error case",
            log_level=LogLevel.ERROR,
        )

        logger.resolution_logger(
            "doc_003",
            "field3",
            "old",
            "new",
            "merge",
            "merged",
            "Critical case",
            log_level=LogLevel.CRITICAL,
        )

        issues = logger.get_warnings_and_errors()
        assert issues["warnings"] == 1
        assert issues["errors"] == 1
        assert issues["critical"] == 1

    def test_get_most_common_resolutions(self):
        """Test identifying most common resolution choices."""
        logger = ResolutionLogger()

        # 5 use_new resolutions
        for i in range(5):
            logger.resolution_logger(
                f"doc_{i}",
                "field",
                "old",
                "new",
                "use_new",
                "new",
                f"Reason {i}",
            )

        # 3 keep_existing
        for i in range(3):
            logger.resolution_logger(
                f"doc_{5+i}",
                "field",
                "old",
                "new",
                "keep_existing",
                "old",
                f"Reason {i}",
            )

        # 1 merge
        logger.resolution_logger(
            "doc_8",
            "field",
            "old",
            "new",
            "merge",
            "merged",
            "Reason merge",
        )

        most_common = logger.get_most_common_resolutions(limit=2)
        assert most_common[0] == ("use_new", 5)
        assert most_common[1] == ("keep_existing", 3)

    def test_log_with_affected_downstream(self):
        """Test logging with downstream impact tracking."""
        logger = ResolutionLogger()

        log = logger.resolution_logger(
            "doc_001",
            "company",
            "Amex",
            "American Express",
            "use_new",
            "American Express",
            "Changed company name",
            affected_downstream=["company_description", "company_website"],
        )

        assert log.affected_downstream == ["company_description", "company_website"]

    def test_complex_logging_workflow(self):
        """Test complex workflow with multiple documents and fields."""
        logger = ResolutionLogger()

        # Log resolutions for multiple documents
        for doc_id in ["doc_1", "doc_2", "doc_3"]:
            for field_id in range(3):
                logger.resolution_logger(
                    doc_id,
                    f"field_{field_id}",
                    f"old_{field_id}",
                    f"new_{field_id}",
                    ["use_new", "keep_existing", "merge"][field_id % 3],
                    f"resolved_{field_id}",
                    f"Resolution for {field_id}",
                    decided_by=["user", "system"][doc_id[-1] == "1"],
                )

        stats = logger.get_statistics()
        assert stats["total_logs"] == 9
        assert stats["total_documents"] == 3
        assert stats["total_fields"] == 3
        assert stats["by_resolution"]["use_new"] == 3
