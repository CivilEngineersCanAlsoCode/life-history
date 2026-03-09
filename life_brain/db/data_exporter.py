"""
Data Export & Backup — Unified export of ChromaDB knowledge base.

Provides:
- Full collection export to JSON
- Domain-filtered export
- Incremental export (by date range)
- Import/restore from backup
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExportResult:
    """Result of a data export operation."""

    exported_at: str
    total_documents: int
    domains: List[str]
    records: List[Dict[str, Any]] = field(default_factory=list)
    export_format: str = "json"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exported_at": self.exported_at,
            "total_documents": self.total_documents,
            "domains": self.domains,
            "records": self.records,
            "export_format": self.export_format,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize export to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


@dataclass
class ImportResult:
    """Result of an import/restore operation."""

    imported_at: str
    attempted: int
    successful: int
    failed: int
    errors: List[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if self.attempted == 0:
            return 0.0
        return self.successful / self.attempted


class DataExporter:
    """Unified export and backup for ChromaDB knowledge base."""

    def __init__(self, collection=None):
        """
        Args:
            collection: ChromaDB collection (can be None for testing)
        """
        self.collection = collection

    def export_all(self, limit: int = 10000) -> Tuple[Optional[ExportResult], Optional[str]]:
        """
        Export all documents from collection.

        Returns:
            (ExportResult, None) on success, (None, error_str) on failure
        """
        if not self.collection:
            return None, "No collection configured"

        try:
            raw = self.collection.get(limit=limit)
        except Exception as e:
            return None, f"Export failed: {e}"

        return self._build_export_result(raw), None

    def export_by_domain(
        self,
        domain: str,
        limit: int = 5000,
    ) -> Tuple[Optional[ExportResult], Optional[str]]:
        """
        Export documents filtered by domain.

        Args:
            domain: Domain to filter (career, finance, health, etc.)
            limit: Maximum documents to export

        Returns:
            (ExportResult, error) tuple
        """
        if not self.collection:
            return None, "No collection configured"
        if not domain:
            return None, "domain cannot be empty"

        try:
            raw = self.collection.get(
                where={"domain": {"$eq": domain}},
                limit=limit,
            )
        except Exception as e:
            err = str(e)
            if "does not exist" in err or "no documents" in err.lower():
                # Domain has no documents — return empty result
                return ExportResult(
                    exported_at=datetime.now().isoformat(),
                    total_documents=0,
                    domains=[domain],
                ), None
            return None, f"Export failed: {e}"

        return self._build_export_result(raw, filter_domain=domain), None

    def export_by_date_range(
        self,
        start_date: str,
        end_date: Optional[str] = None,
        limit: int = 5000,
    ) -> Tuple[Optional[ExportResult], Optional[str]]:
        """
        Export documents stored within a date range.

        Args:
            start_date: ISO8601 start date (inclusive)
            end_date: ISO8601 end date (inclusive, defaults to now)
            limit: Maximum documents to export
        """
        if not self.collection:
            return None, "No collection configured"
        if not start_date:
            return None, "start_date cannot be empty"

        end = end_date or datetime.now().isoformat()

        try:
            raw = self.collection.get(
                where={"date": {"$gte": start_date, "$lte": end}},
                limit=limit,
            )
        except Exception as e:
            err = str(e)
            if "does not exist" in err:
                return ExportResult(
                    exported_at=datetime.now().isoformat(),
                    total_documents=0,
                    domains=[],
                ), None
            return None, f"Export failed: {e}"

        return self._build_export_result(raw), None

    def export_to_file(
        self,
        filepath: str,
        domain: Optional[str] = None,
        limit: int = 10000,
    ) -> Tuple[bool, Optional[str]]:
        """
        Export collection to a JSON file.

        Args:
            filepath: Output file path
            domain: Optional domain filter
            limit: Max documents

        Returns:
            (success, error) tuple
        """
        if domain:
            result, error = self.export_by_domain(domain, limit=limit)
        else:
            result, error = self.export_all(limit=limit)

        if error:
            return False, error

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(result.to_json())
            logger.info(f"Exported {result.total_documents} documents to {filepath}")
            return True, None
        except (IOError, OSError) as e:
            return False, f"Write failed: {e}"

    def import_from_dict(
        self,
        export_data: Dict[str, Any],
    ) -> ImportResult:
        """
        Restore documents from an export dict.

        Args:
            export_data: Dict from ExportResult.to_dict()

        Returns:
            ImportResult with success/failure counts
        """
        imported_at = datetime.now().isoformat()
        records = export_data.get("records", [])
        attempted = len(records)
        successful = 0
        failed = 0
        errors = []

        if not self.collection:
            return ImportResult(
                imported_at=imported_at,
                attempted=attempted,
                successful=0,
                failed=attempted,
                errors=["No collection configured"],
            )

        for record in records:
            doc_id = record.get("doc_id") or record.get("id")
            text = record.get("text") or record.get("document", "")
            metadata = record.get("metadata", {})

            if not doc_id or not text:
                failed += 1
                errors.append(f"Skipped record with missing doc_id or text: {record.get('doc_id', '?')}")
                continue

            try:
                self.collection.upsert(
                    ids=[doc_id],
                    documents=[text],
                    metadatas=[metadata],
                )
                successful += 1
            except Exception as e:
                failed += 1
                errors.append(f"{doc_id}: {e}")

        logger.info(f"Import: {successful}/{attempted} documents restored")
        return ImportResult(
            imported_at=imported_at,
            attempted=attempted,
            successful=successful,
            failed=failed,
            errors=errors,
        )

    def _build_export_result(
        self,
        raw: Dict[str, Any],
        filter_domain: Optional[str] = None,
    ) -> ExportResult:
        """Convert raw ChromaDB get() result to ExportResult."""
        ids = raw.get("ids", [])
        documents = raw.get("documents", []) or [""] * len(ids)
        metadatas = raw.get("metadatas", []) or [{}] * len(ids)

        records = []
        domains_seen = set()

        for doc_id, text, meta in zip(ids, documents, metadatas):
            if not meta:
                meta = {}
            domain = meta.get("domain", "")
            if domain:
                domains_seen.add(domain)
            records.append({
                "doc_id": doc_id,
                "text": text or "",
                "metadata": meta,
            })

        return ExportResult(
            exported_at=datetime.now().isoformat(),
            total_documents=len(records),
            domains=sorted(domains_seen),
            records=records,
        )
