"""
Tests for data export and backup functionality.

Tests cover:
- Full collection export
- Domain-filtered export
- Date range export
- File export
- Import/restore
- Edge cases (no collection, empty, errors)
"""

import json
import os
import tempfile
import pytest
from unittest.mock import Mock

from life_brain.db.data_exporter import DataExporter, ExportResult, ImportResult


def _make_mock_collection(n=3, domain="career"):
    """Create mock ChromaDB collection with n documents."""
    mock = Mock()
    mock.get.return_value = {
        "ids": [f"doc{i}" for i in range(n)],
        "documents": [f"Career content {i}" for i in range(n)],
        "metadatas": [{"domain": domain, "company": "Google", "date": "2024-01-01"}] * n,
    }
    return mock


class TestExportAll:
    """Test full collection export."""

    def test_export_all_no_collection_returns_error(self):
        """No collection → returns error."""
        exporter = DataExporter(collection=None)
        result, error = exporter.export_all()
        assert result is None
        assert error is not None

    def test_export_all_returns_export_result(self):
        """Valid collection → returns ExportResult."""
        exporter = DataExporter(collection=_make_mock_collection(5))
        result, error = exporter.export_all()
        assert error is None
        assert isinstance(result, ExportResult)
        assert result.total_documents == 5

    def test_export_all_records_have_required_fields(self):
        """Each record must have doc_id, text, metadata."""
        exporter = DataExporter(collection=_make_mock_collection(3))
        result, _ = exporter.export_all()
        for rec in result.records:
            assert "doc_id" in rec
            assert "text" in rec
            assert "metadata" in rec

    def test_export_all_domains_extracted(self):
        """Export result must list all unique domains."""
        mock = Mock()
        mock.get.return_value = {
            "ids": ["d1", "d2"],
            "documents": ["A", "B"],
            "metadatas": [{"domain": "career"}, {"domain": "finance"}],
        }
        exporter = DataExporter(collection=mock)
        result, _ = exporter.export_all()
        assert "career" in result.domains
        assert "finance" in result.domains

    def test_export_all_to_json_string(self):
        """ExportResult.to_json() must produce valid JSON."""
        exporter = DataExporter(collection=_make_mock_collection(2))
        result, _ = exporter.export_all()
        json_str = result.to_json()
        parsed = json.loads(json_str)
        assert parsed["total_documents"] == 2
        assert "records" in parsed

    def test_export_all_collection_error_returns_error(self):
        """ChromaDB error → returns error message, not crash."""
        mock = Mock()
        mock.get.side_effect = Exception("connection failed")
        exporter = DataExporter(collection=mock)
        result, error = exporter.export_all()
        assert result is None
        assert error is not None
        assert "Export failed" in error or "connection" in error.lower()


class TestExportByDomain:
    """Test domain-filtered export."""

    def test_export_career_domain(self):
        """Export with domain filter calls collection.get with where clause."""
        mock = _make_mock_collection(3, domain="career")
        exporter = DataExporter(collection=mock)
        result, error = exporter.export_by_domain("career")
        assert error is None
        assert result.total_documents == 3
        mock.get.assert_called_once()
        call_kwargs = mock.get.call_args[1]
        assert "where" in call_kwargs

    def test_export_empty_domain_returns_error(self):
        """Empty domain string → returns error."""
        exporter = DataExporter(collection=Mock())
        result, error = exporter.export_by_domain("")
        assert result is None
        assert error is not None

    def test_export_nonexistent_domain_returns_empty(self):
        """Domain with no docs → empty ExportResult, no error."""
        mock = Mock()
        mock.get.side_effect = Exception("Value 'nosuchdomainxyz' does not exist in column")
        exporter = DataExporter(collection=mock)
        result, error = exporter.export_by_domain("nosuchdomainxyz")
        assert error is None
        assert result.total_documents == 0

    def test_export_domain_filters_records_by_domain(self):
        """Records returned should match the requested domain."""
        mock = _make_mock_collection(2, domain="finance")
        exporter = DataExporter(collection=mock)
        result, _ = exporter.export_by_domain("finance")
        for rec in result.records:
            assert rec["metadata"].get("domain") == "finance"


class TestExportToFile:
    """Test file-based export."""

    def test_export_to_file_creates_json(self):
        """export_to_file must create a valid JSON file."""
        exporter = DataExporter(collection=_make_mock_collection(3))
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            success, error = exporter.export_to_file(filepath)
            assert success is True
            assert error is None
            with open(filepath) as f:
                data = json.load(f)
            assert data["total_documents"] == 3
        finally:
            os.unlink(filepath)

    def test_export_to_file_no_collection_fails(self):
        """No collection → export_to_file returns False with error."""
        exporter = DataExporter(collection=None)
        success, error = exporter.export_to_file("/tmp/test_export.json")
        assert success is False
        assert error is not None

    def test_export_to_file_invalid_path_fails(self):
        """Invalid file path → returns False with error."""
        exporter = DataExporter(collection=_make_mock_collection(2))
        success, error = exporter.export_to_file("/nonexistent_dir/nope/export.json")
        assert success is False
        assert error is not None


class TestImportRestore:
    """Test import/restore from backup."""

    def test_import_empty_records_succeeds(self):
        """Import with 0 records → ImportResult with 0 attempted."""
        mock = Mock()
        exporter = DataExporter(collection=mock)
        result = exporter.import_from_dict({"records": []})
        assert result.attempted == 0
        assert result.successful == 0

    def test_import_valid_records(self):
        """Import 3 valid records → 3 successful upserts."""
        mock = Mock()
        mock.upsert.return_value = None  # No error
        exporter = DataExporter(collection=mock)
        records = [
            {"doc_id": "d1", "text": "Career content 1", "metadata": {"domain": "career"}},
            {"doc_id": "d2", "text": "Career content 2", "metadata": {"domain": "career"}},
            {"doc_id": "d3", "text": "Career content 3", "metadata": {"domain": "career"}},
        ]
        result = exporter.import_from_dict({"records": records})
        assert result.successful == 3
        assert result.failed == 0
        assert mock.upsert.call_count == 3

    def test_import_no_collection_fails_all(self):
        """Import without collection → all fail, no crash."""
        exporter = DataExporter(collection=None)
        records = [{"doc_id": "d1", "text": "content", "metadata": {}}]
        result = exporter.import_from_dict({"records": records})
        assert result.successful == 0
        assert result.failed == 1

    def test_import_missing_doc_id_skipped(self):
        """Records with no doc_id must be skipped with failed count."""
        mock = Mock()
        exporter = DataExporter(collection=mock)
        records = [{"text": "content without doc_id", "metadata": {}}]
        result = exporter.import_from_dict({"records": records})
        assert result.failed == 1
        assert result.successful == 0
        mock.upsert.assert_not_called()

    def test_import_upsert_error_counted_as_failed(self):
        """ChromaDB upsert error → counted as failed, not crash."""
        mock = Mock()
        mock.upsert.side_effect = Exception("upsert failed")
        exporter = DataExporter(collection=mock)
        records = [{"doc_id": "d1", "text": "content", "metadata": {}}]
        result = exporter.import_from_dict({"records": records})
        assert result.failed == 1
        assert len(result.errors) == 1

    def test_import_success_rate_computed(self):
        """success_rate property must be correct."""
        result = ImportResult(
            imported_at="2024-01-01T00:00:00",
            attempted=10,
            successful=7,
            failed=3,
        )
        assert result.success_rate == 0.7

    def test_import_success_rate_zero_attempted(self):
        """success_rate with 0 attempted must be 0.0, not ZeroDivisionError."""
        result = ImportResult(
            imported_at="2024-01-01T00:00:00",
            attempted=0,
            successful=0,
            failed=0,
        )
        assert result.success_rate == 0.0


class TestRoundTripExport:
    """Test export → import round trip."""

    def test_export_then_import_preserves_records(self):
        """Export + import must reproduce the same documents."""
        # Export
        original_mock = _make_mock_collection(3)
        exporter = DataExporter(collection=original_mock)
        result, _ = exporter.export_all()
        assert result.total_documents == 3

        # Import back
        import_mock = Mock()
        import_mock.upsert.return_value = None
        importer = DataExporter(collection=import_mock)
        import_result = importer.import_from_dict(result.to_dict())

        assert import_result.successful == 3
        assert import_result.failed == 0
