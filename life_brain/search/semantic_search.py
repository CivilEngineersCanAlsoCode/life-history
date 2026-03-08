"""
Semantic search using ChromaDB with metadata filtering.

Provides semantic similarity-based search with:
- Vector similarity matching
- Metadata filtering (domain, company, project)
- Result ranking and scoring
- Batch search operations
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Result from semantic search."""

    doc_id: str
    content: str
    similarity_score: float  # 0-1 cosine similarity
    metadata: Dict[str, Any]
    distance: float  # 1 - similarity_score (for sorting)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "doc_id": self.doc_id,
            "content": self.content,
            "similarity_score": round(self.similarity_score, 3),
            "metadata": self.metadata,
            "distance": round(self.distance, 3),
        }


class SemanticSearch:
    """Semantic search using ChromaDB with metadata filtering."""

    def __init__(self, collection=None):
        """Initialize semantic search.

        Args:
            collection: ChromaDB collection to search in
        """
        self.collection = collection

    def search(
        self,
        query: str,
        query_embedding: Optional[List[float]] = None,
        domain: Optional[str] = None,
        company: Optional[str] = None,
        project: Optional[str] = None,
        top_k: int = 5,
    ) -> Tuple[List[SearchResult], Optional[str]]:
        """Search for similar documents with metadata filtering.

        Args:
            query: Text query for semantic search
            query_embedding: Pre-computed embedding (optional)
            domain: Filter by domain (career, health, etc.)
            company: Filter by company name
            project: Filter by project name
            top_k: Number of top results to return

        Returns:
            (List of SearchResult, error_message if any)
        """
        if not self.collection:
            return [], "Collection not initialized"

        if not query and query_embedding is None:
            return [], "Query or query_embedding required"

        try:
            # Build metadata filter
            where_filter = self._build_metadata_filter(domain, company, project)

            # Query ChromaDB
            if query_embedding:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=where_filter if where_filter else None,
                )
            else:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=top_k,
                    where=where_filter if where_filter else None,
                )

            # Parse results
            search_results = self._parse_query_results(results)

            return search_results, None

        except Exception as e:
            error_msg = f"Search failed: {str(e)}"
            logger.error(error_msg)
            return [], error_msg

    def _build_metadata_filter(
        self, domain: Optional[str], company: Optional[str], project: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Build ChromaDB metadata filter.

        Args:
            domain: Domain filter
            company: Company filter
            project: Project filter

        Returns:
            ChromaDB where filter dict or None
        """
        filters = {}

        if domain:
            filters["domain"] = domain

        if company:
            filters["company"] = company

        if project:
            filters["project"] = project

        if not filters:
            return None

        # Build $and filter for multiple criteria
        if len(filters) == 1:
            key, value = list(filters.items())[0]
            return {key: {"$eq": value}}
        else:
            filter_list = [{key: {"$eq": value}} for key, value in filters.items()]
            return {"$and": filter_list}

    def _parse_query_results(self, results: Dict[str, Any]) -> List[SearchResult]:
        """Parse ChromaDB query results into SearchResult objects.

        Args:
            results: ChromaDB query results

        Returns:
            List of SearchResult objects
        """
        search_results = []

        if not results or "ids" not in results or not results["ids"]:
            return search_results

        # Results structure: ids, documents, distances, metadatas
        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        for doc_id, doc_text, distance, metadata in zip(ids, documents, distances, metadatas):
            # Convert distance to similarity (distance = 1 - cosine_similarity)
            similarity = 1 - distance if distance else 0

            result = SearchResult(
                doc_id=doc_id,
                content=doc_text,
                similarity_score=max(0, min(1, similarity)),  # Clamp to 0-1
                metadata=metadata or {},
                distance=max(0, min(1, distance)) if distance else 1,
            )

            search_results.append(result)

        # Sort by similarity (highest first)
        search_results.sort(key=lambda r: r.similarity_score, reverse=True)

        return search_results

    def batch_search(
        self,
        queries: List[str],
        domain: Optional[str] = None,
        company: Optional[str] = None,
        project: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Tuple[str, List[SearchResult], Optional[str]]]:
        """Batch search for multiple queries.

        Args:
            queries: List of query strings
            domain: Domain filter
            company: Company filter
            project: Project filter
            top_k: Number of top results per query

        Returns:
            List of (query, results, error) tuples
        """
        batch_results = []

        for query in queries:
            results, error = self.search(
                query=query,
                domain=domain,
                company=company,
                project=project,
                top_k=top_k,
            )
            batch_results.append((query, results, error))

        return batch_results

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the collection.

        Returns:
            Dictionary with collection statistics
        """
        if not self.collection:
            return {"collection_initialized": False}

        try:
            count = self.collection.count()

            return {
                "collection_initialized": True,
                "total_documents": count,
            }
        except Exception as e:
            return {
                "collection_initialized": False,
                "error": str(e),
            }

    def filter_by_metadata(
        self,
        domain: Optional[str] = None,
        company: Optional[str] = None,
        project: Optional[str] = None,
        limit: int = 100,
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Get documents filtered by metadata without semantic search.

        Args:
            domain: Domain filter
            company: Company filter
            project: Project filter
            limit: Maximum documents to return

        Returns:
            (List of documents, error_message if any)
        """
        if not self.collection:
            return [], "Collection not initialized"

        try:
            where_filter = self._build_metadata_filter(domain, company, project)

            if where_filter:
                results = self.collection.get(where=where_filter, limit=limit)
            else:
                results = self.collection.get(limit=limit)

            # Parse results
            documents = []
            if results and "ids" in results:
                for doc_id, text, metadata in zip(
                    results.get("ids", []),
                    results.get("documents", []),
                    results.get("metadatas", []),
                ):
                    documents.append(
                        {
                            "doc_id": doc_id,
                            "content": text,
                            "metadata": metadata,
                        }
                    )

            return documents, None

        except Exception as e:
            error_msg = f"Metadata filter failed: {str(e)}"
            logger.error(error_msg)
            return [], error_msg
