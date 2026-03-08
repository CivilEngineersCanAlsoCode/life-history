"""
ChromaDB initialization and collection management.
"""

from typing import Dict, Any, Optional
import chromadb
from chromadb.config import Settings

from life_brain.config import (
    CHROMA_PATH, COLLECTION_NAME, HNSW_SPACE,
    REQUIRED_METADATA_FIELDS, TIER_1_FIELDS, TIER_2_FIELDS,
    Privacy, Confidence, AtomType, Domain, Status
)


class ChromaDBManager:
    """Manages ChromaDB collection initialization and schema."""

    def __init__(self, path: str = CHROMA_PATH):
        self.path = path
        self.client = None
        self.collection = None

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
        Validate that all required metadata fields are present.

        Args:
            metadata: Metadata dictionary to validate

        Returns:
            True if valid

        Raises:
            ValueError: If required field missing
        """
        # Check all required fields present
        missing_fields = []
        for field in REQUIRED_METADATA_FIELDS:
            if field not in metadata or metadata[field] is None:
                missing_fields.append(field)

        if missing_fields:
            raise ValueError(f"Missing required metadata fields: {', '.join(missing_fields)}")

        # Validate enum values
        if metadata.get("privacy") not in [p.value for p in Privacy]:
            raise ValueError(f"Invalid privacy value: {metadata.get('privacy')}")

        if metadata.get("source") not in [s.value for s in Source]:
            raise ValueError(f"Invalid source value: {metadata.get('source')}")

        if metadata.get("confidence") and metadata.get("confidence") not in [c.value for c in Confidence]:
            raise ValueError(f"Invalid confidence value: {metadata.get('confidence')}")

        # Validate schema_version is integer
        if not isinstance(metadata.get("schema_version"), int):
            raise ValueError(f"schema_version must be integer, got {type(metadata.get('schema_version'))}")

        # Validate importance is 1-5
        importance = metadata.get("importance")
        if not isinstance(importance, int) or importance < 1 or importance > 5:
            raise ValueError(f"importance must be integer 1-5, got {importance}")

        return True

    def validate_text_self_contained(self, text: str) -> bool:
        """
        Validate that document text is self-contained (readable without metadata).

        Args:
            text: Document text to validate

        Returns:
            True if self-contained (>100 chars, has context)
        """
        # TODO: Implement
        # Check text length > 100 chars
        # Check it reads standalone (not just "Q: ...", "A: ...")
        pass


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
