"""
Store alternative question phrasings as separate ChromaDB documents.

Each alt phrasing gets its own document linked back to the parent Q&A pair.
This lets retrieval find answers via multiple question angles.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import hashlib


@dataclass
class AltQuestionDocument:
    """A single alternative question phrasing document."""

    doc_id: str            # Unique ID for this alt phrasing
    parent_id: str         # ID of the canonical Q&A pair
    phrasing: str          # The alternative question text
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_chromadb_dict(self) -> Dict[str, Any]:
        """Convert to ChromaDB-compatible document dict."""
        meta = {
            **self.metadata,
            "parent_id": self.parent_id,
            "doc_type": "alt_question",
            "original_question": self.phrasing,
        }
        return {
            "id": self.doc_id,
            "document": self.phrasing,
            "metadata": meta,
        }


def generate_alt_question_id(parent_id: str, phrasing: str) -> str:
    """Generate stable unique ID for an alt question document.

    Args:
        parent_id: ID of the parent Q&A pair
        phrasing: The alternative phrasing text

    Returns:
        Deterministic doc_id string
    """
    content = f"{parent_id}::{phrasing.strip().lower()}"
    hash_hex = hashlib.md5(content.encode()).hexdigest()[:10]
    return f"alt_{parent_id}_{hash_hex}"


class AltQuestionStore:
    """Manage alternative question phrasings linked to parent documents."""

    def __init__(self, collection=None):
        """Initialize store.

        Args:
            collection: Optional ChromaDB collection
        """
        self.collection = collection
        # In-memory store when no collection provided
        self._store: Dict[str, AltQuestionDocument] = {}
        self._parent_index: Dict[str, List[str]] = {}  # parent_id -> [doc_ids]

    def add_phrasings(
        self,
        parent_id: str,
        phrasings: List[str],
        base_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[AltQuestionDocument]:
        """Add alternative phrasings for a parent document.

        Args:
            parent_id: ID of the canonical Q&A pair
            phrasings: List of alternative question formulations
            base_metadata: Metadata to attach to each alt doc (e.g. company, domain)

        Returns:
            List of created AltQuestionDocument objects
        """
        if not parent_id or not parent_id.strip():
            raise ValueError("parent_id cannot be empty")

        created = []
        meta = base_metadata or {}

        for phrasing in phrasings:
            if not phrasing or not phrasing.strip():
                continue

            doc_id = generate_alt_question_id(parent_id, phrasing)

            doc = AltQuestionDocument(
                doc_id=doc_id,
                parent_id=parent_id,
                phrasing=phrasing.strip(),
                metadata=dict(meta),
            )

            # Store in memory
            self._store[doc_id] = doc
            if parent_id not in self._parent_index:
                self._parent_index[parent_id] = []
            if doc_id not in self._parent_index[parent_id]:
                self._parent_index[parent_id].append(doc_id)

            # Write to ChromaDB if available
            if self.collection is not None:
                chroma_doc = doc.to_chromadb_dict()
                try:
                    self.collection.upsert(
                        ids=[chroma_doc["id"]],
                        documents=[chroma_doc["document"]],
                        metadatas=[chroma_doc["metadata"]],
                    )
                except Exception:
                    pass  # Store in memory regardless

            created.append(doc)

        return created

    def get_phrasings_for_parent(self, parent_id: str) -> List[AltQuestionDocument]:
        """Get all alt phrasings for a parent document.

        Args:
            parent_id: Parent document ID

        Returns:
            List of AltQuestionDocument objects
        """
        doc_ids = self._parent_index.get(parent_id, [])
        return [self._store[did] for did in doc_ids if did in self._store]

    def get_parent_id(self, alt_doc_id: str) -> Optional[str]:
        """Look up the parent_id for an alt question document.

        Args:
            alt_doc_id: ID of the alt question document

        Returns:
            Parent document ID, or None if not found
        """
        doc = self._store.get(alt_doc_id)
        return doc.parent_id if doc else None

    def remove_phrasings_for_parent(self, parent_id: str) -> int:
        """Remove all alt phrasings for a parent document.

        Args:
            parent_id: Parent document ID

        Returns:
            Number of documents removed
        """
        doc_ids = self._parent_index.pop(parent_id, [])
        removed = 0
        for did in doc_ids:
            if did in self._store:
                del self._store[did]
                removed += 1
        return removed

    def get_statistics(self) -> Dict[str, Any]:
        """Get store statistics."""
        return {
            "total_alt_docs": len(self._store),
            "total_parents": len(self._parent_index),
            "avg_phrasings_per_parent": (
                len(self._store) / len(self._parent_index)
                if self._parent_index else 0.0
            ),
        }

    def export_for_parent(self, parent_id: str) -> List[Dict[str, Any]]:
        """Export all alt docs for a parent as ChromaDB-ready dicts.

        Args:
            parent_id: Parent document ID

        Returns:
            List of ChromaDB document dicts
        """
        docs = self.get_phrasings_for_parent(parent_id)
        return [d.to_chromadb_dict() for d in docs]
