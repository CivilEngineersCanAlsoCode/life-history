"""
Two-Pass Conflict Candidate Pool — Expanded conflict detection at scale.

Problem: semantic-only search (n=5) misses conflicts at rank 6-10 when
facts use different phrasing but same structural position.

Solution:
  Pass 1 (Semantic):  Top 5 by cosine similarity (existing approach)
  Pass 2 (Structural): Metadata filter by {company, type, category}
                       — no n_results limit (fast indexed lookup)
  Union → deduplicate → run conflict scoring on all

Pass 2 only runs for METRIC and FACT atom types.
"""

from typing import Dict, List, Any, Optional, Set, Tuple
import logging

logger = logging.getLogger(__name__)

# Atom types that benefit from structural conflict search
STRUCTURAL_CONFLICT_TYPES = {"metric", "fact", "measurement", "statistic", "number"}


def two_pass_conflict_search(
    collection,
    query_text: str,
    query_embedding: Optional[List[float]],
    atom_type: str,
    metadata_filters: Dict[str, Any],
    semantic_top_k: int = 5,
    structural_limit: int = 100,
) -> Tuple[List[Dict[str, Any]], int, int]:
    """
    Perform two-pass conflict candidate search.

    Pass 1: Semantic similarity search (top-k by cosine similarity)
    Pass 2: Structural metadata filter search (only for METRIC/FACT types)
    Returns union of both passes, deduplicated.

    Args:
        collection: ChromaDB collection
        query_text: Query text for semantic search
        query_embedding: Pre-computed embedding (if available)
        atom_type: Atom type (metric, fact, story, decision, lesson)
        metadata_filters: Dict of metadata to filter on (company, category, type)
        semantic_top_k: Number of semantic results (Pass 1)
        structural_limit: Max structural results (Pass 2)

    Returns:
        (candidates, pass1_count, pass2_count) tuple
    """
    if not collection:
        return [], 0, 0

    all_ids: Set[str] = set()
    candidates: List[Dict[str, Any]] = []

    # ---------- Pass 1: Semantic search ----------
    pass1_count = 0
    try:
        query_kwargs: Dict[str, Any] = {
            "n_results": semantic_top_k,
            "include": ["documents", "metadatas", "distances"],
        }
        if query_embedding:
            query_kwargs["query_embeddings"] = [query_embedding]
        else:
            query_kwargs["query_texts"] = [query_text]

        results = collection.query(**query_kwargs)
        ids = results.get("ids", [[]])[0]
        docs = (results.get("documents", [[]])[0]) or [""] * len(ids)
        metas = (results.get("metadatas", [[]])[0]) or [{}] * len(ids)
        dists = (results.get("distances", [[]])[0]) or [1.0] * len(ids)

        for doc_id, text, meta, dist in zip(ids, docs, metas, dists):
            if doc_id not in all_ids:
                all_ids.add(doc_id)
                similarity = max(0.0, 1.0 - float(dist))
                candidates.append({
                    "doc_id": doc_id,
                    "text": text or "",
                    "metadata": meta or {},
                    "similarity_score": similarity,
                    "found_by": "semantic",
                })
                pass1_count += 1

        logger.debug(f"Pass 1 (semantic): {pass1_count} candidates")

    except Exception as e:
        logger.warning(f"Pass 1 semantic search failed: {e}")

    # ---------- Pass 2: Structural metadata filter ----------
    # Only for fact/metric types — structural conflicts most common there
    pass2_count = 0
    if atom_type.lower() in STRUCTURAL_CONFLICT_TYPES and metadata_filters:
        try:
            # Build where filter from metadata
            where_clauses = {}
            for key in ("company", "category", "doc_type"):
                if key in metadata_filters and metadata_filters[key]:
                    where_clauses[key] = {"$eq": str(metadata_filters[key])}

            if where_clauses:
                get_kwargs: Dict[str, Any] = {
                    "limit": structural_limit,
                    "include": ["documents", "metadatas"],
                }
                if len(where_clauses) == 1:
                    get_kwargs["where"] = where_clauses
                else:
                    get_kwargs["where"] = {"$and": [{k: v} for k, v in where_clauses.items()]}

                struct_results = collection.get(**get_kwargs)
                struct_ids = struct_results.get("ids", [])
                struct_docs = struct_results.get("documents", []) or [""] * len(struct_ids)
                struct_metas = struct_results.get("metadatas", []) or [{}] * len(struct_ids)

                for doc_id, text, meta in zip(struct_ids, struct_docs, struct_metas):
                    if doc_id not in all_ids:
                        all_ids.add(doc_id)
                        candidates.append({
                            "doc_id": doc_id,
                            "text": text or "",
                            "metadata": meta or {},
                            "similarity_score": 0.0,  # No embedding used
                            "found_by": "structural",
                        })
                        pass2_count += 1

                logger.debug(f"Pass 2 (structural): {pass2_count} new candidates")

        except Exception as e:
            logger.warning(f"Pass 2 structural search failed: {e}")

    total = len(candidates)
    logger.info(
        f"Two-pass conflict search: {total} candidates "
        f"(semantic={pass1_count}, structural={pass2_count})"
    )
    return candidates, pass1_count, pass2_count


def should_run_structural_pass(atom_type: str) -> bool:
    """Return True if atom type warrants a structural conflict search."""
    return atom_type.lower() in STRUCTURAL_CONFLICT_TYPES
