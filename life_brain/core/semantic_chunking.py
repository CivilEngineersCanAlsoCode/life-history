"""
Semantic paragraph chunking for document ingestion.

Chunks documents into semantically meaningful units (paragraphs) while:
- Preserving natural boundaries (paragraph breaks, sentence boundaries)
- Maintaining token count within configured range (50-500 tokens)
- Tagging chunks with metadata references
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import re


@dataclass
class Paragraph:
    """Represents a paragraph extracted from text."""

    text: str
    start_index: int  # Character position in original text
    end_index: int
    sentence_count: int
    estimated_tokens: int


@dataclass
class SemanticChunk:
    """Represents a semantic chunk ready for embedding."""

    chunk_id: str
    document_id: str
    content: str
    start_char: int  # Position in original document
    end_char: int
    paragraph_count: int
    sentence_count: int
    token_count: int
    sequence: int  # Position in document's chunk sequence
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "content": self.content,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "paragraph_count": self.paragraph_count,
            "sentence_count": self.sentence_count,
            "token_count": self.token_count,
            "sequence": self.sequence,
            "metadata": self.metadata,
        }


class SemanticChunker:
    """Chunk documents into semantic units while preserving boundaries."""

    # Token estimation: ~4 characters per token (conservative)
    CHARS_PER_TOKEN = 4
    MIN_TOKENS = 50
    MAX_TOKENS = 500
    TARGET_TOKENS = 300  # Try to aim for mid-range

    def __init__(
        self,
        min_tokens: int = MIN_TOKENS,
        max_tokens: int = MAX_TOKENS,
        target_tokens: int = TARGET_TOKENS,
    ):
        """Initialize semantic chunker.

        Args:
            min_tokens: Minimum tokens per chunk
            max_tokens: Maximum tokens per chunk
            target_tokens: Target tokens per chunk (try to hit this)
        """
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.target_tokens = target_tokens

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count from character count."""
        return max(1, len(text) // self.CHARS_PER_TOKEN)

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences, preserving original spacing.

        Returns list of sentences (including whitespace).
        """
        # Match common sentence endings: . ! ? followed by space and capital letter
        # Also handle abbreviations like "Dr.", "Mr.", etc.
        pattern = r"(?<=[.!?])\s+(?=[A-Z])"
        sentences = re.split(pattern, text)
        return [s for s in sentences if s.strip()]

    def _split_into_paragraphs(self, text: str) -> List[Paragraph]:
        """Split text into paragraphs.

        Paragraphs are separated by double newlines or significant whitespace.
        """
        # Split by multiple newlines (paragraph boundaries)
        para_texts = re.split(r"\n\n+", text)

        paragraphs = []
        current_index = 0

        for para_text in para_texts:
            if not para_text.strip():
                # Skip empty paragraphs but track position
                current_index += len(para_text) + 2  # +2 for the \n\n
                continue

            sentences = self._split_into_sentences(para_text)
            sentence_count = len(sentences)
            token_count = self._estimate_tokens(para_text)

            para = Paragraph(
                text=para_text,
                start_index=current_index,
                end_index=current_index + len(para_text),
                sentence_count=sentence_count,
                estimated_tokens=token_count,
            )

            paragraphs.append(para)
            current_index += len(para_text) + 2  # +2 for paragraph boundary

        return paragraphs

    def _group_paragraphs_into_chunks(
        self, paragraphs: List[Paragraph]
    ) -> List[List[Paragraph]]:
        """Group paragraphs into chunks based on token count.

        Respects paragraph boundaries - never splits a paragraph.
        """
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            if not current_chunk:
                # Start new chunk with this paragraph
                current_chunk.append(para)
                current_tokens = para.estimated_tokens
            elif current_tokens + para.estimated_tokens <= self.max_tokens:
                # Paragraph fits in current chunk
                current_chunk.append(para)
                current_tokens += para.estimated_tokens
            else:
                # Paragraph doesn't fit
                if current_tokens >= self.min_tokens:
                    # Current chunk is big enough, start new one
                    chunks.append(current_chunk)
                    current_chunk = [para]
                    current_tokens = para.estimated_tokens
                else:
                    # Current chunk is too small, but we can't make it bigger
                    # (next para doesn't fit either)
                    # Add this paragraph anyway to avoid losing content
                    current_chunk.append(para)
                    current_tokens += para.estimated_tokens
                    chunks.append(current_chunk)
                    current_chunk = []
                    current_tokens = 0

        # Don't forget the last chunk
        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def chunk_document(
        self,
        document_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[SemanticChunk], Optional[str]]:
        """Chunk a document into semantic units.

        Args:
            document_id: ID of the document
            content: Full document content
            metadata: Optional metadata to attach to chunks

        Returns:
            (List of SemanticChunk, error if any)
        """
        if not content or not content.strip():
            return [], "Empty document content"

        if not document_id:
            return [], "Empty document_id"

        # Parse paragraphs
        paragraphs = self._split_into_paragraphs(content)

        if not paragraphs:
            return [], "Could not extract paragraphs from content"

        # Group into chunks
        para_groups = self._group_paragraphs_into_chunks(paragraphs)

        # Create semantic chunks
        chunks = []
        metadata = metadata or {}

        for sequence, para_group in enumerate(para_groups):
            chunk_text = "\n\n".join(p.text for p in para_group)
            start_char = para_group[0].start_index
            end_char = para_group[-1].end_index

            chunk_id = f"chunk_{document_id}_{sequence:04d}"
            token_count = self._estimate_tokens(chunk_text)
            para_count = len(para_group)
            sentence_count = sum(p.sentence_count for p in para_group)

            chunk = SemanticChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                content=chunk_text,
                start_char=start_char,
                end_char=end_char,
                paragraph_count=para_count,
                sentence_count=sentence_count,
                token_count=token_count,
                sequence=sequence,
                metadata=metadata.copy(),
            )

            chunks.append(chunk)

        return chunks, None

    def batch_chunk_documents(
        self, documents: List[Dict[str, Any]]
    ) -> Tuple[List[SemanticChunk], Optional[str]]:
        """Chunk multiple documents.

        Args:
            documents: List of dicts with "document_id", "content", optional "metadata"

        Returns:
            (All chunks from all documents, error if any)
        """
        all_chunks = []

        for doc in documents:
            doc_id = doc.get("document_id")
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})

            chunks, error = self.chunk_document(doc_id, content, metadata)

            if error:
                return [], f"Error chunking {doc_id}: {error}"

            all_chunks.extend(chunks)

        return all_chunks, None

    def get_statistics(self, chunks: List[SemanticChunk]) -> Dict[str, Any]:
        """Get statistics about chunks."""
        if not chunks:
            return {
                "total_chunks": 0,
                "avg_tokens": 0,
                "avg_paragraphs": 0,
                "avg_sentences": 0,
                "total_content_chars": 0,
            }

        total_tokens = sum(c.token_count for c in chunks)
        total_paras = sum(c.paragraph_count for c in chunks)
        total_sentences = sum(c.sentence_count for c in chunks)
        total_chars = sum(len(c.content) for c in chunks)

        return {
            "total_chunks": len(chunks),
            "avg_tokens": total_tokens / len(chunks),
            "avg_paragraphs": total_paras / len(chunks),
            "avg_sentences": total_sentences / len(chunks),
            "total_content_chars": total_chars,
            "min_tokens": min(c.token_count for c in chunks),
            "max_tokens": max(c.token_count for c in chunks),
        }

    def export_chunks(self, chunks: List[SemanticChunk]) -> List[Dict[str, Any]]:
        """Export chunks as dictionaries."""
        return [c.to_dict() for c in chunks]
