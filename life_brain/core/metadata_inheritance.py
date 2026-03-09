"""
Metadata inheritance for document chunks.

Manages inheritance of metadata from parent documents to child chunks,
ensuring rich context is preserved while allowing per-chunk overrides.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DocumentMetadata:
    """Metadata for a parent document."""

    doc_id: str
    title: str
    company: str = ""
    project: str = ""
    domain: str = ""  # career, health, relationships, etc.
    category: str = ""  # subcategory
    author: str = ""
    date_created: str = ""
    date_modified: str = ""
    source_url: str = ""
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    confidence: float = 1.0  # 0-1
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "company": self.company,
            "project": self.project,
            "domain": self.domain,
            "category": self.category,
            "author": self.author,
            "date_created": self.date_created,
            "date_modified": self.date_modified,
            "source_url": self.source_url,
            "version": self.version,
            "tags": self.tags,
            "confidence": self.confidence,
            "custom_fields": self.custom_fields,
        }


@dataclass
class ChunkMetadata:
    """Metadata for a document chunk."""

    chunk_id: str
    parent_doc_id: str
    sequence: int  # Position in parent document
    # Inherited from parent
    company: str = ""
    project: str = ""
    domain: str = ""
    category: str = ""
    author: str = ""
    source_url: str = ""
    tags: List[str] = field(default_factory=list)
    # Chunk-specific
    chunk_type: str = "text"  # text, code, table, heading, etc.
    token_count: int = 0
    char_count: int = 0
    confidence: float = 1.0
    chunk_tags: List[str] = field(default_factory=list)  # Chunk-specific tags
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "parent_doc_id": self.parent_doc_id,
            "sequence": self.sequence,
            "company": self.company,
            "project": self.project,
            "domain": self.domain,
            "category": self.category,
            "author": self.author,
            "source_url": self.source_url,
            "tags": self.tags,
            "chunk_type": self.chunk_type,
            "token_count": self.token_count,
            "char_count": self.char_count,
            "confidence": self.confidence,
            "chunk_tags": self.chunk_tags,
        }


class MetadataInheritanceManager:
    """Manage metadata inheritance from documents to chunks."""

    def __init__(self):
        """Initialize metadata inheritance manager."""
        self.parent_documents: Dict[str, DocumentMetadata] = {}
        self.chunks: Dict[str, Tuple[str, ChunkMetadata]] = {}  # chunk_id -> (content, metadata)
        self.chunk_history: List[Tuple[str, ChunkMetadata]] = []

    def register_document(
        self,
        doc_id: str,
        title: str,
        company: str = "",
        project: str = "",
        domain: str = "",
        category: str = "",
        tags: List[str] = None,
        **kwargs
    ) -> DocumentMetadata:
        """
        Register a parent document for metadata inheritance.

        Args:
            doc_id: Unique document ID
            title: Document title
            company: Company name
            project: Project name
            domain: Domain (career, health, etc.)
            category: Category
            tags: List of tags
            **kwargs: Additional metadata

        Returns:
            DocumentMetadata object
        """
        if not doc_id:
            raise ValueError("doc_id cannot be null or empty")

        metadata = DocumentMetadata(
            doc_id=doc_id,
            title=title,
            company=company,
            project=project,
            domain=domain,
            category=category,
            tags=tags or [],
            **kwargs
        )

        self.parent_documents[doc_id] = metadata
        return metadata

    def create_chunk(
        self,
        parent_doc_id: str,
        chunk_content: str,
        sequence: int,
        chunk_id: str = "",
        chunk_type: str = "text",
        override_metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Optional[ChunkMetadata], Optional[str]]:
        """
        Create a chunk with inherited metadata from parent document.

        Args:
            parent_doc_id: ID of parent document
            chunk_content: Content of the chunk
            sequence: Position in parent document
            chunk_id: Optional custom chunk ID
            chunk_type: Type of chunk (text, code, table, etc.)
            override_metadata: Optional metadata to override

        Returns:
            (ChunkMetadata, error if any)
        """
        if not parent_doc_id:
            return None, "parent_doc_id cannot be null or empty"

        parent = self.parent_documents.get(parent_doc_id)
        if not parent:
            return None, f"Parent document {parent_doc_id} not found"

        if not chunk_id:
            chunk_id = f"chunk_{parent_doc_id}_{sequence:04d}"

        # Create chunk metadata with inherited values
        chunk_meta = ChunkMetadata(
            chunk_id=chunk_id,
            parent_doc_id=parent_doc_id,
            sequence=sequence,
            company=parent.company,
            project=parent.project,
            domain=parent.domain,
            category=parent.category,
            author=parent.author,
            source_url=parent.source_url,
            tags=parent.tags.copy(),
            chunk_type=chunk_type,
            char_count=len(chunk_content),
            token_count=self._estimate_tokens(chunk_content),
        )

        # Apply overrides if provided
        if override_metadata:
            for key, value in override_metadata.items():
                if hasattr(chunk_meta, key):
                    setattr(chunk_meta, key, value)

        self.chunks[chunk_id] = (chunk_content, chunk_meta)
        self.chunk_history.append((chunk_content, chunk_meta))

        return chunk_meta, None

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (simple heuristic)."""
        # Rough estimate: ~4 characters per token
        return max(1, len(text) // 4)

    def batch_create_chunks(
        self,
        parent_doc_id: str,
        chunks_content: List[str],
        chunk_type: str = "text",
        override_metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[ChunkMetadata], Optional[str]]:
        """
        Create multiple chunks from a document.

        Args:
            parent_doc_id: ID of parent document
            chunks_content: List of chunk contents
            chunk_type: Type of chunks
            override_metadata: Metadata to override for all chunks

        Returns:
            (List of ChunkMetadata, error if any)
        """
        created_chunks = []
        for sequence, content in enumerate(chunks_content):
            meta, error = self.create_chunk(
                parent_doc_id,
                content,
                sequence,
                chunk_type=chunk_type,
                override_metadata=override_metadata,
            )
            if meta:
                created_chunks.append(meta)

        return created_chunks, None

    def get_chunk(self, chunk_id: str) -> Optional[Tuple[str, ChunkMetadata]]:
        """Get chunk content and metadata."""
        return self.chunks.get(chunk_id)

    def get_chunks_for_document(self, parent_doc_id: str) -> List[Tuple[str, ChunkMetadata]]:
        """Get all chunks for a document."""
        return [
            chunk for chunk in self.chunk_history
            if chunk[1].parent_doc_id == parent_doc_id
        ]

    def get_chunks_by_domain(self, domain: str) -> List[Tuple[str, ChunkMetadata]]:
        """Get all chunks for a domain."""
        return [
            chunk for chunk in self.chunk_history
            if chunk[1].domain == domain
        ]

    def get_chunks_by_project(self, project: str) -> List[Tuple[str, ChunkMetadata]]:
        """Get all chunks for a project."""
        return [
            chunk for chunk in self.chunk_history
            if chunk[1].project == project
        ]

    def get_chunks_by_company(self, company: str) -> List[Tuple[str, ChunkMetadata]]:
        """Get all chunks for a company."""
        return [
            chunk for chunk in self.chunk_history
            if chunk[1].company == company
        ]

    def get_chunks_by_tag(self, tag: str) -> List[Tuple[str, ChunkMetadata]]:
        """Get all chunks with a tag."""
        return [
            chunk for chunk in self.chunk_history
            if tag in chunk[1].tags
        ]

    def update_chunk_metadata(
        self,
        chunk_id: str,
        **updates
    ) -> Tuple[Optional[ChunkMetadata], Optional[str]]:
        """Update chunk metadata."""
        chunk_data = self.chunks.get(chunk_id)
        if not chunk_data:
            return None, f"Chunk {chunk_id} not found"

        content, metadata = chunk_data
        for key, value in updates.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)

        self.chunks[chunk_id] = (content, metadata)
        return metadata, None

    def export_chunk(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Export chunk with metadata."""
        chunk_data = self.get_chunk(chunk_id)
        if not chunk_data:
            return None

        content, metadata = chunk_data
        return {
            "chunk_id": chunk_id,
            "content": content[:200] + "..." if len(content) > 200 else content,
            "metadata": metadata.to_dict(),
        }

    def export_all_chunks_for_document(self, parent_doc_id: str) -> List[Dict[str, Any]]:
        """Export all chunks for a document."""
        chunks = self.get_chunks_for_document(parent_doc_id)
        return [
            {
                "chunk_id": chunk[1].chunk_id,
                "content": chunk[0][:100] + "..." if len(chunk[0]) > 100 else chunk[0],
                "metadata": chunk[1].to_dict(),
            }
            for chunk in chunks
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about chunks and metadata."""
        if not self.chunk_history:
            return {
                "total_chunks": 0,
                "total_documents": len(self.parent_documents),
                "by_domain": {},
                "by_company": {},
                "avg_tokens": 0,
            }

        by_domain = {}
        by_company = {}
        total_tokens = 0

        for _, metadata in self.chunk_history:
            domain = metadata.domain or "uncategorized"
            company = metadata.company or "uncategorized"

            by_domain[domain] = by_domain.get(domain, 0) + 1
            by_company[company] = by_company.get(company, 0) + 1
            total_tokens += metadata.token_count

        avg_tokens = total_tokens / len(self.chunk_history) if self.chunk_history else 0

        return {
            "total_chunks": len(self.chunk_history),
            "total_documents": len(self.parent_documents),
            "by_domain": by_domain,
            "by_company": by_company,
            "avg_tokens": avg_tokens,
            "total_tokens": total_tokens,
        }

    def get_inheritance_map(self) -> Dict[str, Dict[str, Any]]:
        """Get mapping of documents to chunks."""
        mapping = {}
        for doc_id in self.parent_documents:
            chunks = self.get_chunks_for_document(doc_id)
            mapping[doc_id] = {
                "doc_title": self.parent_documents[doc_id].title,
                "chunk_count": len(chunks),
                "chunks": [chunk[1].chunk_id for chunk in chunks],
            }
        return mapping
