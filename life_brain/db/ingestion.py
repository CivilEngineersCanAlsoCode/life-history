"""
Document ingestion pipeline — add Q&A pairs to MongoDB with validation.
Migrated from ChromaDB to MongoDB 8.2 + mongot for vector search.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

from pymongo.collection import Collection

from life_brain.config import REQUIRED_METADATA_FIELDS, Privacy
from life_brain.truth_engine.conflict import conflict_check, ConflictResult
from life_brain.db.mongodb_init import MongoDBManager, get_embedding

logger = logging.getLogger(__name__)


@dataclass
class QAPair:
    """A single Q&A pair — atomic knowledge unit."""
    question: str
    answer: str
    doc_id: str
    metadata: Dict[str, Any]
    alt_questions: Optional[List[str]] = None


def add_to_life_brain(
    collection: Collection,
    doc_id: str,
    text: str,
    metadata: Dict[str, Any]
) -> str:
    """
    Add one atomic knowledge unit (Q&A pair) to MongoDB lifeos_vectors.

    Flow:
    1. Validate required metadata fields
    2. Validate text is self-contained (>100 chars)
    3. Generate Gemini embedding
    4. Run conflict_check() via $vectorSearch
    5. If no conflict → upsert to MongoDB
    6. Return doc_id

    Args:
        collection: MongoDB Collection (lifeos_vectors)
        doc_id: Unique document identifier
        text: Self-contained Q&A pair text (must be English)
        metadata: 47-field metadata dict

    Returns:
        doc_id if inserted

    Raises:
        ValueError: If validation fails or hard conflict detected
    """
    manager = MongoDBManager()

    # Step 1: Validate required metadata fields
    manager.validate_required_fields(metadata)
    logger.debug(f"Metadata validation passed for {doc_id}")

    # Step 2: Validate text is self-contained
    if not text or len(text) < 100:
        raise ValueError(f"Text must be >100 characters, got {len(text)}")
    logger.debug(f"Text validation passed ({len(text)} chars)")

    # Step 3: Generate Gemini embedding
    embedding = get_embedding(text)
    logger.debug(f"Embedding generated: {len(embedding)}-dim")

    # Step 4: Conflict check via MongoDB $vectorSearch
    mgr = MongoDBManager()
    mgr.client = collection.database.client
    mgr.db = collection.database
    mgr.collection = collection

    similar_docs = mgr.vector_search(
        query_embedding=embedding,
        n_results=5,
        filters={"metadata.domain": metadata.get("domain")} if metadata.get("domain") else None
    )

    if similar_docs:
        existing_pairs = [
            (doc.get("metadata", {}), doc.get("embedding", []))
            for doc in similar_docs
        ]
        conflict_result = conflict_check(metadata, existing_pairs)

        if conflict_result.status == "CONFLICT":
            raise ValueError(
                f"HARD CONFLICT (score: {conflict_result.conflict_score:.2f}). "
                f"Existing: {conflict_result.existing_answer}. "
                f"Resolve manually before inserting."
            )
        elif conflict_result.status == "SOFT_CONFLICT":
            logger.warning(
                f"SOFT CONFLICT (score: {conflict_result.conflict_score:.2f}). "
                f"Inserting with warning — review recommended."
            )

    # Step 5: Upsert to MongoDB
    doc = {
        "doc_id": doc_id,
        "text": text,
        "embedding": embedding,
        "metadata": metadata,
        "inserted_at": datetime.utcnow().isoformat(),
        "schema_version": metadata.get("schema_version", 1),
    }
    collection.update_one(
        {"doc_id": doc_id},
        {"$set": doc},
        upsert=True
    )
    logger.info(f"Upserted doc: {doc_id}")
    return doc_id


def batch_add_to_life_brain(
    collection: Collection,
    pairs: List[QAPair]
) -> Dict[str, Any]:
    """
    Add multiple Q&A pairs with progress tracking.

    Args:
        collection: MongoDB Collection
        pairs: List of QAPair objects

    Returns:
        Summary: {inserted, skipped, errors}
    """
    results = {"inserted": 0, "skipped": 0, "errors": []}

    for pair in pairs:
        text = f"Q: {pair.question}\nA: {pair.answer}"
        try:
            add_to_life_brain(collection, pair.doc_id, text, pair.metadata)
            results["inserted"] += 1
        except ValueError as e:
            if "CONFLICT" in str(e):
                results["skipped"] += 1
                logger.warning(f"Skipped {pair.doc_id}: {e}")
            else:
                results["errors"].append({"doc_id": pair.doc_id, "error": str(e)})
                logger.error(f"Error on {pair.doc_id}: {e}")

    return results


def query_life_brain(
    collection: Collection,
    query_text: str,
    filters: Optional[Dict] = None,
    n_results: int = 10,
    min_score: float = 0.70
) -> List[Dict]:
    """
    Semantic search over lifeos_vectors.

    Args:
        collection: MongoDB Collection
        query_text: English query text
        filters: MongoDB metadata filters (e.g., {"metadata.domain": "career"})
        n_results: Max results
        min_score: Minimum cosine similarity score

    Returns:
        List of matching docs with score + metadata
    """
    query_embedding = get_embedding(query_text)

    mgr = MongoDBManager()
    mgr.client = collection.database.client
    mgr.db = collection.database
    mgr.collection = collection

    results = mgr.vector_search(
        query_embedding=query_embedding,
        n_results=n_results,
        filters=filters
    )

    # Filter by minimum score
    filtered = [r for r in results if r.get("score", 0) >= min_score]

    if not filtered:
        logger.info(f"No results above {min_score} for: {query_text[:50]}")

    return filtered
