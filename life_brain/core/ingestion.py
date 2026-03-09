"""
Document ingestion pipeline — add Q&A pairs to ChromaDB with validation.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import uuid
import logging
import chromadb

from life_brain.config import REQUIRED_METADATA_FIELDS, Privacy
from life_brain.truth.conflict import conflict_check, ConflictResult
from life_brain.core.chromadb_init import ChromaDBManager

logger = logging.getLogger(__name__)


@dataclass
class QAPair:
    """A single Q&A pair — atomic knowledge unit."""
    question: str
    answer: str
    doc_id: str
    metadata: Dict[str, Any]
    alt_questions: Optional[List[str]] = None  # in tags


def add_to_life_brain(
    collection: chromadb.Collection,
    doc_id: str,
    text: str,
    metadata: Dict[str, Any]
) -> str:
    """
    Add one atomic knowledge unit (Q&A pair) to ChromaDB.

    Flow:
    1. Validate required metadata fields
    2. Validate text is self-contained
    3. Run conflict_check() against existing pairs
    4. If no conflict → upsert to collection
    5. Return doc_id

    Args:
        collection: ChromaDB collection
        doc_id: Unique document identifier
        text: Self-contained Q&A pair text
        metadata: 47-field metadata dict

    Returns:
        doc_id if inserted, or raises exception

    Raises:
        ValueError: If validation fails or conflict detected
    """
    try:
        # Step 1: Validate required metadata fields
        manager = ChromaDBManager()
        manager.validate_required_fields(metadata)
        logger.debug(f"Metadata validation passed for {doc_id}")

        # Step 2: Validate text is self-contained (>100 chars, readable standalone)
        if not text or len(text) < 100:
            raise ValueError(f"Text must be >100 characters, got {len(text)}")

        # Check text doesn't look like just "Q: ... A: ..." without context
        if text.lower().strip().startswith("q:") and text.count("a:") > 0:
            # Allow Q&A format, but ensure each part has substance
            parts = text.split("A:")
            if len(parts[0]) < 50:  # Q part too short
                raise ValueError("Answer section too brief for self-contained understanding")

        logger.debug(f"Text validation passed for {doc_id} ({len(text)} chars)")

        # Step 3: Run conflict check against existing pairs
        # Query collection for semantically similar documents
        try:
            # Query with the text to find similar entries
            results = collection.query(
                query_texts=[text],
                n_results=5
            )

            if results and results.get("ids") and len(results["ids"]) > 0:
                # Construct existing_pairs list from query results
                existing_pairs = []
                for i, result_id in enumerate(results["ids"][0]):
                    existing_metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                    existing_embedding = results["embeddings"][0][i] if results.get("embeddings") else []
                    existing_pairs.append((existing_metadata, existing_embedding))

                # Check for conflicts
                conflict_result = conflict_check(metadata, existing_pairs)

                if conflict_result.status == "CONFLICT":
                    # Hard conflict detected
                    raise ValueError(
                        f"HARD CONFLICT detected (score: {conflict_result.conflict_score:.2f}). "
                        f"Existing answer: {conflict_result.existing_answer}. "
                        f"Resolve manually using resolve_conflict_with_user()."
                    )

                elif conflict_result.status == "SOFT":
                    # Soft conflict detected - warn but allow with log
                    logger.warning(
                        f"SOFT CONFLICT for {doc_id} (score: {conflict_result.conflict_score:.2f}). "
                        f"Existing: {conflict_result.existing_answer[:100]}... "
                        f"Proceeding with insertion."
                    )

                elif conflict_result.status == "ENRICHMENT":
                    # Enrichment detected - this is OK, auto-update
                    logger.info(
                        f"ENRICHMENT detected for {doc_id} (score: {conflict_result.conflict_score:.2f}). "
                        f"Will update existing entry."
                    )

                # SAFE status: proceed normally

                logger.debug(f"Conflict check passed: {conflict_result.status}")

        except Exception as conflict_error:
            # If conflict check fails, log but don't block (first-run scenario)
            logger.warning(f"Conflict check skipped (likely empty collection): {conflict_error}")

        # Step 4: Upsert to ChromaDB
        collection.upsert(
            ids=[doc_id],
            metadatas=[metadata],
            documents=[text]
        )

        logger.info(f"Successfully ingested: {doc_id}")
        return doc_id

    except ValueError as e:
        logger.error(f"Validation failed for {doc_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Ingestion failed for {doc_id}: {e}")
        raise RuntimeError(f"Failed to add document to ChromaDB: {e}")


def batch_ingest(
    collection: chromadb.Collection,
    pairs: List[QAPair]
) -> Dict[str, Any]:
    """
    Batch insert multiple Q&A pairs.

    Returns summary: {inserted: count, skipped: count, conflicts: list}
    """
    inserted = []
    skipped = []
    conflicts = []

    for pair in pairs:
        try:
            # Format text as "Q: {question}\nA: {answer}"
            text = f"Q: {pair.question}\nA: {pair.answer}"

            # Attempt ingestion
            doc_id = add_to_life_brain(
                collection=collection,
                doc_id=pair.doc_id,
                text=text,
                metadata=pair.metadata
            )

            inserted.append({
                "doc_id": doc_id,
                "question": pair.question
            })

        except ValueError as e:
            # Conflict detected - collect for review
            if "CONFLICT" in str(e) or "SOFT" in str(e):
                conflicts.append({
                    "doc_id": pair.doc_id,
                    "question": pair.question,
                    "error": str(e)
                })
                logger.warning(f"Conflict in batch: {pair.doc_id}")
            else:
                # Validation error - skip
                skipped.append({
                    "doc_id": pair.doc_id,
                    "question": pair.question,
                    "reason": str(e)
                })
                logger.error(f"Skipped due to validation: {pair.doc_id}")

        except Exception as e:
            # Other errors - skip and log
            skipped.append({
                "doc_id": pair.doc_id,
                "question": pair.question,
                "reason": f"Ingestion error: {str(e)}"
            })
            logger.error(f"Skipped due to error: {pair.doc_id}")

    return {
        "total": len(pairs),
        "inserted": len(inserted),
        "skipped": len(skipped),
        "conflicts": len(conflicts),
        "inserted_details": inserted,
        "skipped_details": skipped,
        "conflicts_details": conflicts,
        "success_rate": (len(inserted) / len(pairs) * 100) if pairs else 0
    }


def validate_document_batch(pairs: List[QAPair]) -> Tuple[List[str], List[Tuple[str, str]]]:
    """
    Validate entire batch for duplicates and structural issues.

    Returns:
        Tuple of (valid_doc_ids, invalid_docs_with_reasons)
    """
    valid_ids = []
    invalid_docs = []

    manager = ChromaDBManager()

    for pair in pairs:
        errors = []

        # Check required fields in metadata
        try:
            manager.validate_required_fields(pair.metadata)
        except ValueError as e:
            errors.append(str(e))

        # Check text quality
        text = f"Q: {pair.question}\nA: {pair.answer}"
        if len(text) < 100:
            errors.append(f"Text too short: {len(text)} chars (min 100)")

        if not pair.question or len(pair.question) < 5:
            errors.append("Question too short")

        if not pair.answer or len(pair.answer) < 10:
            errors.append("Answer too short")

        # Check for duplicates within batch
        duplicate_in_batch = [
            p for p in pairs
            if p.doc_id != pair.doc_id and
            p.question.lower() == pair.question.lower()
        ]
        if duplicate_in_batch:
            errors.append(f"Duplicate question in batch: {duplicate_in_batch[0].doc_id}")

        # Classify
        if errors:
            invalid_docs.append((pair.doc_id, "; ".join(errors)))
            logger.warning(f"Invalid doc {pair.doc_id}: {errors}")
        else:
            valid_ids.append(pair.doc_id)
            logger.debug(f"Valid doc: {pair.doc_id}")

    logger.info(
        f"Batch validation: {len(valid_ids)} valid, {len(invalid_docs)} invalid "
        f"out of {len(pairs)} total"
    )

    return valid_ids, invalid_docs
