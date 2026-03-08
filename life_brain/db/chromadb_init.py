"""
ChromaDB initialization and collection management.
"""

from typing import Dict, Any, Optional
import chromadb
from chromadb.config import Settings
import logging

from life_brain.config import (
    CHROMA_PATH, COLLECTION_NAME, HNSW_SPACE,
    REQUIRED_METADATA_FIELDS, TIER_1_FIELDS, TIER_2_FIELDS,
    Privacy, Confidence, AtomType, Domain, Status, Source
)
from life_brain.db.metadata_validator import MetadataValidator, MetadataValidationError

logger = logging.getLogger(__name__)


class ChromaDBManager:
    """Manages ChromaDB collection initialization and schema."""

    def __init__(self, path: str = CHROMA_PATH):
        self.path = path
        self.client = None
        self.collection = None
        self.validator = MetadataValidator()

    def init_collection(self) -> chromadb.Collection:
        """
        Initialize ChromaDB collection with proper metadata schema.

        Returns:
            Collection ready for add/query operations
        """
        try:
            # Create persistent client
            self.client = chromadb.PersistentClient(path=self.path)

            # Get or create collection with cosine similarity (best for text embeddings)
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": HNSW_SPACE}
            )

            return self.collection

        except Exception as e:
            raise RuntimeError(f"Failed to initialize ChromaDB collection: {e}")

    def validate_required_fields(self, metadata: Dict[str, Any]) -> bool:
        """
        Validate that all required metadata fields are present and valid.

        Uses comprehensive MetadataValidator to check:
        - All required fields present
        - Type correctness
        - Enum values
        - Numeric ranges
        - Date formats
        - Cross-field constraints

        Args:
            metadata: Metadata dictionary to validate

        Returns:
            True if valid

        Raises:
            MetadataValidationError: If validation fails
        """
        try:
            self.validator.validate_metadata(metadata)
            logger.debug(f"Metadata validation passed for {len(metadata)} fields")
            return True
        except MetadataValidationError as e:
            logger.error(f"Metadata validation failed: {e}")
            raise ValueError(str(e))

    def validate_text_self_contained(self, text: str) -> bool:
        """
        Validate that document text is self-contained (readable without metadata).

        Args:
            text: Document text to validate

        Returns:
            True if self-contained (>100 chars, has context)

        Raises:
            ValueError: If text is too short or not self-contained
        """
        if not text or len(text) < 100:
            raise ValueError(f"Text must be >100 characters, got {len(text)}")

        # Check text doesn't look like just "Q: ... A: ..." without context
        text_lower = text.lower().strip()
        if text_lower.startswith("q:") and "a:" in text_lower:
            # Allow Q&A format, but ensure each part has substance
            parts = text.split("A:")
            if len(parts) > 0 and len(parts[0]) < 50:
                raise ValueError("Text appears to be just Q&A format without sufficient context")

        logger.debug(f"Text validation passed ({len(text)} chars)")
        return True

    def validate_field(self, field_name: str, value: Any) -> bool:
        """
        Validate a single metadata field.

        Args:
            field_name: Field name
            value: Field value

        Returns:
            True if valid

        Raises:
            ValueError: If field invalid
        """
        is_valid, error = self.validator.validate_field(field_name, value)
        if not is_valid:
            raise ValueError(error)
        return True

    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get schema structure and constraints for documentation/debugging.

        Returns:
            Dict with schema info
        """
        return self.validator.get_schema_info()


def get_metadata_schema() -> Dict[str, Any]:
    """
    Get full metadata schema with 47 fields.

    Returns:
        Schema dict for reference/validation
    """
    return {
        "tier_1": TIER_1_FIELDS,
        "tier_2": TIER_2_FIELDS,
        "required": REQUIRED_METADATA_FIELDS,
    }
