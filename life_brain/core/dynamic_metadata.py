"""
Dynamic metadata system for custom key:value pairs.

Allows documents to store custom fields beyond the standard 47-field schema.
Tracks custom field usage for potential promotion to standard schema.
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CustomField:
    """A custom metadata field."""

    key: str
    value: Any
    added_date: str = field(default_factory=lambda: datetime.now().isoformat())
    usage_count: int = 1  # How many times this field appears across documents
    document_ids: Set[str] = field(default_factory=set)  # Which documents have this field

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "value": self.value,
            "added_date": self.added_date,
            "usage_count": self.usage_count,
            "document_ids": list(self.document_ids),
        }

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate custom field."""
        errors = []

        if not self.key or not self.key.strip():
            errors.append("key is required")

        if not isinstance(self.key, str):
            errors.append("key must be a string")

        # Disallow reserved keys
        reserved_keys = [
            "id",
            "content",
            "metadata",
            "embedding",
            "document_id",
        ]
        if self.key.lower() in reserved_keys:
            errors.append(f"key '{self.key}' is reserved")

        return len(errors) == 0, errors


class DynamicMetadata:
    """Manage custom/dynamic metadata fields."""

    # Reserved keys that cannot be used for custom fields
    RESERVED_KEYS = {
        "id",
        "content",
        "metadata",
        "embedding",
        "document_id",
        "chunk_id",
        "collection",
        "domain",
        "source",
        "confidence",
        "created_at",
        "updated_at",
        "version",
    }

    def __init__(self):
        """Initialize dynamic metadata."""
        self.custom_fields: Dict[str, CustomField] = {}  # key -> CustomField
        self.document_metadata: Dict[str, Dict[str, Any]] = {}  # document_id -> custom fields

    def add_custom_field(
        self,
        document_id: str,
        key: str,
        value: Any,
    ) -> Tuple[bool, Optional[str]]:
        """
        Add a custom field to a document.

        Args:
            document_id: Document ID
            key: Field key
            value: Field value

        Returns:
            (success, error_message) tuple
        """
        # Validate key
        if not key or not key.strip():
            return False, "key cannot be empty"

        if not isinstance(key, str):
            return False, "key must be a string"

        key_lower = key.lower()

        if key_lower in self.RESERVED_KEYS:
            return False, f"key '{key}' is reserved"

        # Store custom field globally if new
        if key not in self.custom_fields:
            custom_field = CustomField(key=key, value=value)
            is_valid, errors = custom_field.validate()
            if not is_valid:
                return False, errors[0]

            self.custom_fields[key] = custom_field
        else:
            # Update usage count
            self.custom_fields[key].usage_count += 1

        # Track which documents have this field
        self.custom_fields[key].document_ids.add(document_id)

        # Store in document metadata
        if document_id not in self.document_metadata:
            self.document_metadata[document_id] = {}

        self.document_metadata[document_id][key] = value

        return True, None

    def get_custom_fields_for_document(self, document_id: str) -> Dict[str, Any]:
        """Get all custom fields for a document."""
        return self.document_metadata.get(document_id, {})

    def get_custom_field_value(
        self, document_id: str, key: str
    ) -> Optional[Any]:
        """Get a specific custom field value."""
        doc_metadata = self.document_metadata.get(document_id, {})
        return doc_metadata.get(key)

    def update_custom_field(
        self,
        document_id: str,
        key: str,
        value: Any,
    ) -> Tuple[bool, Optional[str]]:
        """Update a custom field value."""
        if document_id not in self.document_metadata:
            return False, f"document {document_id} not found"

        if key not in self.document_metadata[document_id]:
            return False, f"field '{key}' not found for document {document_id}"

        # Update value
        self.document_metadata[document_id][key] = value
        return True, None

    def delete_custom_field(
        self,
        document_id: str,
        key: str,
    ) -> Tuple[bool, Optional[str]]:
        """Delete a custom field from a document."""
        if document_id not in self.document_metadata:
            return False, f"document {document_id} not found"

        if key not in self.document_metadata[document_id]:
            return False, f"field '{key}' not found"

        del self.document_metadata[document_id][key]

        # Update global usage count
        if key in self.custom_fields:
            self.custom_fields[key].document_ids.discard(document_id)
            self.custom_fields[key].usage_count = max(
                0, self.custom_fields[key].usage_count - 1
            )

        return True, None

    def get_all_custom_fields(self) -> Dict[str, CustomField]:
        """Get all custom fields defined."""
        return self.custom_fields

    def get_fields_by_usage(self, min_usage: int = 1) -> List[Tuple[str, int]]:
        """Get custom fields sorted by usage count."""
        fields = [
            (key, field.usage_count)
            for key, field in self.custom_fields.items()
            if field.usage_count >= min_usage
        ]
        return sorted(fields, key=lambda x: -x[1])

    def get_high_frequency_fields(self, threshold: int = 20) -> List[str]:
        """Get fields appearing 20+ times (candidates for schema promotion)."""
        return [
            key
            for key, field in self.custom_fields.items()
            if field.usage_count >= threshold
        ]

    def merge_custom_fields(
        self,
        base_metadata: Dict[str, Any],
        document_id: str,
    ) -> Dict[str, Any]:
        """
        Merge custom fields into base metadata.

        Args:
            base_metadata: Standard metadata
            document_id: Document ID

        Returns:
            Merged metadata with custom fields
        """
        merged = base_metadata.copy()
        custom_fields = self.get_custom_fields_for_document(document_id)

        # Add custom fields under _custom namespace or directly
        if custom_fields:
            merged["_custom_fields"] = custom_fields

        return merged

    def dynamic_metadata(
        self,
        document_id: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Add multiple custom fields at once.

        Args:
            document_id: Document ID
            **kwargs: Custom field key=value pairs

        Returns:
            Dictionary with success/failure status for each field
        """
        results = {}

        for key, value in kwargs.items():
            success, error = self.add_custom_field(document_id, key, value)
            results[key] = {"success": success, "error": error}

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get dynamic metadata statistics."""
        if not self.custom_fields:
            return {
                "total_custom_fields": 0,
                "total_documents_with_custom": 0,
                "avg_custom_fields_per_doc": 0.0,
                "most_common_fields": [],
            }

        # Calculate stats
        docs_with_custom = len(self.document_metadata)
        total_custom_instances = sum(
            len(fields) for fields in self.document_metadata.values()
        )

        avg_per_doc = (
            total_custom_instances / docs_with_custom if docs_with_custom > 0 else 0
        )

        most_common = sorted(
            [
                (key, field.usage_count)
                for key, field in self.custom_fields.items()
            ],
            key=lambda x: -x[1],
        )[:10]

        return {
            "total_custom_fields": len(self.custom_fields),
            "total_documents_with_custom": docs_with_custom,
            "total_custom_instances": total_custom_instances,
            "avg_custom_fields_per_doc": avg_per_doc,
            "most_common_fields": most_common,
            "promotion_candidates": self.get_high_frequency_fields(),
        }

    def export_custom_fields(self) -> Dict[str, Any]:
        """Export all custom fields and their usage."""
        return {
            key: field.to_dict()
            for key, field in self.custom_fields.items()
        }

    def export_document_custom_metadata(self, document_id: str) -> Dict[str, Any]:
        """Export custom metadata for a document."""
        return {
            "document_id": document_id,
            "custom_fields": self.get_custom_fields_for_document(document_id),
        }
