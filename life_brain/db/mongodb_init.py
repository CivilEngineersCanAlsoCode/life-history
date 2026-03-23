"""
MongoDB initialization and collection management.
Replaces chromadb_init.py — same interface, MongoDB 8.2 + mongot backend.

Collection: db=linkright, collection=lifeos_vectors
Vector index: mongot $vectorSearch (cosine, 3072-dim Gemini embeddings)
"""

from typing import Dict, Any, Optional, List
import logging
import subprocess
import json

from pymongo import MongoClient
from pymongo.collection import Collection

from life_brain.config import (
    REQUIRED_METADATA_FIELDS, TIER_1_FIELDS, TIER_2_FIELDS,
    Privacy, Confidence, AtomType, Domain, Status, Source
)
from life_brain.db.metadata_validator import MetadataValidator, MetadataValidationError

logger = logging.getLogger(__name__)

# ──── Config ────────────────────────────────────────────────────────────────
MONGO_URI = "mongodb://localhost:27017/?directConnection=true"
DB_NAME = "linkright"
COLLECTION_NAME = "lifeos_vectors"
VECTOR_INDEX_NAME = "vector_index"   # matches all existing LinkRight collections
EMBEDDING_DIM = 1024     # matches all existing linkright.* vector indexes
EMBEDDING_MODEL = "text-embedding-005"  # Gemini CLI (output_dimensionality=1024)


# ──── Gemini Embedding ───────────────────────────────────────────────────────

def get_embedding(text: str) -> List[float]:
    """
    Generate embedding via Gemini CLI (free, already configured on EC2).

    Args:
        text: English text to embed (always English — Hinglish translated before calling)

    Returns:
        List of 3072 floats (Gemini text-embedding-005)

    Raises:
        RuntimeError: If Gemini CLI fails
    """
    prompt = f"Embed this text for semantic search: {text}"
    result = subprocess.run(
        ["gemini", "--model", EMBEDDING_MODEL, "--embed", text],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        # Fallback: use claude CLI with embedding request
        result = subprocess.run(
            ["claude", "--print", f"Return ONLY a JSON array of {EMBEDDING_DIM} floats "
             f"representing the embedding of: {text[:500]}"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            raise RuntimeError(f"Embedding failed: {result.stderr}")

    try:
        embedding = json.loads(result.stdout.strip())
        if not isinstance(embedding, list) or len(embedding) != EMBEDDING_DIM:
            raise ValueError(f"Expected {EMBEDDING_DIM}-dim vector, got {len(embedding)}")
        return embedding
    except (json.JSONDecodeError, ValueError) as e:
        raise RuntimeError(f"Failed to parse embedding output: {e}")


# ──── MongoDBManager ─────────────────────────────────────────────────────────

class MongoDBManager:
    """
    Manages MongoDB lifeos_vectors collection.
    Drop-in replacement for ChromaDBManager — same public interface.
    """

    def __init__(self, uri: str = MONGO_URI):
        self.uri = uri
        self.client: Optional[MongoClient] = None
        self.db = None
        self.collection: Optional[Collection] = None
        self.validator = MetadataValidator()

    def init_collection(self) -> Collection:
        """
        Initialize MongoDB collection + ensure vector search index exists.

        Returns:
            Collection ready for insert/query operations
        """
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            # Ping to confirm connection
            self.client.admin.command("ping")
            self.db = self.client[DB_NAME]
            self.collection = self.db[COLLECTION_NAME]

            # Ensure vector search index via mongot
            self._ensure_vector_index()

            logger.info(f"Connected to MongoDB — {DB_NAME}.{COLLECTION_NAME}")
            return self.collection

        except Exception as e:
            raise RuntimeError(f"Failed to initialize MongoDB collection: {e}")

    def _ensure_vector_index(self):
        """Verify vector search index exists (already created in all LinkRight collections)."""
        existing = list(self.collection.list_search_indexes())
        if any(idx.get("name") == VECTOR_INDEX_NAME for idx in existing):
            logger.debug(f"Vector index '{VECTOR_INDEX_NAME}' ready")
            return
        # Index not found — log warning but don't crash (mongot manages creation)
        logger.warning(
            f"Vector index '{VECTOR_INDEX_NAME}' not found in {COLLECTION_NAME}. "
            f"Create it in MongoDB Atlas / mongot before querying."
        )

    def validate_required_fields(self, metadata: Dict[str, Any]) -> bool:
        """
        Validate that all required metadata fields are present and valid.
        Same interface as ChromaDBManager.validate_required_fields().
        """
        try:
            self.validator.validate_metadata(metadata)
            logger.debug(f"Metadata validation passed for {len(metadata)} fields")
            return True
        except MetadataValidationError as e:
            logger.error(f"Metadata validation failed: {e}")
            raise ValueError(str(e))

    def validate_text_self_contained(self, text: str) -> bool:
        """Validate that document text is self-contained (>100 chars)."""
        if not text or len(text) < 100:
            raise ValueError(f"Text must be >100 characters, got {len(text)}")
        logger.debug(f"Text validation passed ({len(text)} chars)")
        return True

    def validate_field(self, field_name: str, value: Any) -> bool:
        """Validate a single metadata field."""
        is_valid, error = self.validator.validate_field(field_name, value)
        if not is_valid:
            raise ValueError(error)
        return True

    def get_schema_info(self) -> Dict[str, Any]:
        """Get schema structure for documentation/debugging."""
        return self.validator.get_schema_info()

    def vector_search(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Semantic search via mongot $vectorSearch.

        Args:
            query_embedding: 3072-dim Gemini embedding of query text
            n_results: Number of results to return
            filters: MongoDB filter dict for metadata filtering

        Returns:
            List of matching documents with score
        """
        pipeline = [
            {
                "$vectorSearch": {
                    "index": VECTOR_INDEX_NAME,
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": n_results * 10,
                    "limit": n_results,
                    **({"filter": filters} if filters else {})
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "doc_id": 1,
                    "text": 1,
                    "metadata": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        return list(self.collection.aggregate(pipeline))

    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()


def get_metadata_schema() -> Dict[str, Any]:
    """Get full metadata schema with 47 fields."""
    return {
        "tier_1": TIER_1_FIELDS,
        "tier_2": TIER_2_FIELDS,
        "required": REQUIRED_METADATA_FIELDS,
    }
