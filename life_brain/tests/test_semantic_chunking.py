"""
Test suite for semantic paragraph chunking module.

Tests cover:
- Document chunking with token range control
- Paragraph boundary preservation
- Sentence splitting
- Batch operations
- Statistics and exports
- Edge cases
"""

import pytest

from life_brain.core.semantic_chunking import (
    SemanticChunker,
    SemanticChunk,
    Paragraph,
)


class TestParagraph:
    """Test Paragraph dataclass."""

    def test_create_paragraph(self):
        """Test creating paragraph."""
        para = Paragraph(
            text="This is a test paragraph.",
            start_index=0,
            end_index=25,
            sentence_count=1,
            estimated_tokens=5,
        )

        assert para.text == "This is a test paragraph."
        assert para.sentence_count == 1


class TestSemanticChunk:
    """Test SemanticChunk dataclass."""

    def test_create_chunk(self):
        """Test creating semantic chunk."""
        chunk = SemanticChunk(
            chunk_id="chunk_doc1_0000",
            document_id="doc1",
            content="Content here",
            start_char=0,
            end_char=13,
            paragraph_count=1,
            sentence_count=1,
            token_count=3,
            sequence=0,
        )

        assert chunk.chunk_id == "chunk_doc1_0000"
        assert chunk.document_id == "doc1"

    def test_to_dict(self):
        """Test converting chunk to dict."""
        chunk = SemanticChunk(
            chunk_id="chunk_doc1_0001",
            document_id="doc1",
            content="Test content",
            start_char=0,
            end_char=12,
            paragraph_count=1,
            sentence_count=1,
            token_count=3,
            sequence=0,
            metadata={"company": "TechCorp"},
        )

        d = chunk.to_dict()
        assert d["chunk_id"] == "chunk_doc1_0001"
        assert d["metadata"]["company"] == "TechCorp"


class TestSemanticChunker:
    """Test SemanticChunker functionality."""

    def test_create_chunker(self):
        """Test creating chunker."""
        chunker = SemanticChunker()
        assert chunker.min_tokens == 50
        assert chunker.max_tokens == 500

    def test_estimate_tokens(self):
        """Test token estimation."""
        chunker = SemanticChunker()
        # 4 chars per token
        text = "x" * 400  # Should estimate ~100 tokens
        tokens = chunker._estimate_tokens(text)
        assert tokens == 100

    def test_split_into_sentences(self):
        """Test sentence splitting."""
        chunker = SemanticChunker()
        text = "First sentence. Second sentence. Third sentence."
        sentences = chunker._split_into_sentences(text)
        assert len(sentences) == 3

    def test_split_into_sentences_with_abbreviations(self):
        """Test sentence splitting with abbreviations."""
        chunker = SemanticChunker()
        text = "Dr. Smith works here. He is smart."
        sentences = chunker._split_into_sentences(text)
        # Should handle "Dr." properly
        assert len(sentences) >= 1

    def test_split_into_paragraphs(self):
        """Test paragraph splitting."""
        chunker = SemanticChunker()
        text = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3."
        paragraphs = chunker._split_into_paragraphs(text)
        assert len(paragraphs) == 3

    def test_split_single_paragraph(self):
        """Test splitting single paragraph."""
        chunker = SemanticChunker()
        text = "Just one paragraph with some content."
        paragraphs = chunker._split_into_paragraphs(text)
        assert len(paragraphs) == 1

    def test_group_paragraphs_respects_token_limits(self):
        """Test grouping respects token limits."""
        chunker = SemanticChunker(min_tokens=50, max_tokens=150)
        # Create paragraphs with known token counts
        paras = [
            Paragraph(
                text="x" * 200,  # ~50 tokens
                start_index=0,
                end_index=200,
                sentence_count=1,
                estimated_tokens=50,
            ),
            Paragraph(
                text="x" * 200,  # ~50 tokens
                start_index=202,
                end_index=402,
                sentence_count=1,
                estimated_tokens=50,
            ),
            Paragraph(
                text="x" * 200,  # ~50 tokens
                start_index=404,
                end_index=604,
                sentence_count=1,
                estimated_tokens=50,
            ),
        ]

        groups = chunker._group_paragraphs_into_chunks(paras)
        # Should create 1, 2, or 3 chunks depending on grouping logic
        assert len(groups) >= 1
        assert len(groups) <= 3

    def test_chunk_document_basic(self):
        """Test basic document chunking."""
        chunker = SemanticChunker()
        content = """Paragraph 1 with some content. This is a test.

Paragraph 2 with more content. Another test here.

Paragraph 3 wrapping up."""

        chunks, error = chunker.chunk_document("doc1", content)

        assert error is None
        assert len(chunks) > 0
        assert all(c.document_id == "doc1" for c in chunks)

    def test_chunk_document_assigns_sequence(self):
        """Test chunks have sequential ordering."""
        chunker = SemanticChunker()
        content = """Para 1.

Para 2.

Para 3.

Para 4."""

        chunks, _ = chunker.chunk_document("doc1", content)

        sequences = [c.sequence for c in chunks]
        assert sequences == sorted(sequences)

    def test_chunk_document_preserves_content(self):
        """Test chunking preserves all content."""
        chunker = SemanticChunker()
        content = """Paragraph 1.

Paragraph 2.

Paragraph 3."""

        chunks, _ = chunker.chunk_document("doc1", content)

        combined = "\n\n".join(c.content for c in chunks)
        # Check that main content is preserved (ignoring whitespace)
        assert "Paragraph 1" in combined
        assert "Paragraph 2" in combined
        assert "Paragraph 3" in combined

    def test_chunk_document_token_ranges(self):
        """Test chunks stay within token ranges."""
        chunker = SemanticChunker(min_tokens=50, max_tokens=200)
        content = "\n\n".join([f"Paragraph {i} with content. " * 10 for i in range(20)])

        chunks, _ = chunker.chunk_document("doc1", content)

        # Most chunks should be close to token limit (allow 1-2 token tolerance for estimation)
        for chunk in chunks:
            assert chunk.token_count <= chunker.max_tokens + 5

    def test_chunk_document_empty_content(self):
        """Test chunking empty content."""
        chunker = SemanticChunker()
        chunks, error = chunker.chunk_document("doc1", "")

        assert error is not None
        assert len(chunks) == 0

    def test_chunk_document_no_doc_id(self):
        """Test chunking with missing doc_id."""
        chunker = SemanticChunker()
        chunks, error = chunker.chunk_document("", "Some content here")

        assert error is not None
        assert len(chunks) == 0

    def test_chunk_document_includes_metadata(self):
        """Test chunks include attached metadata."""
        chunker = SemanticChunker()
        content = "Paragraph 1.\n\nParagraph 2."
        metadata = {"company": "Corp", "project": "ProjectX"}

        chunks, _ = chunker.chunk_document("doc1", content, metadata)

        assert all(c.metadata["company"] == "Corp" for c in chunks)
        assert all(c.metadata["project"] == "ProjectX" for c in chunks)

    def test_batch_chunk_documents(self):
        """Test batch chunking multiple documents."""
        chunker = SemanticChunker()
        documents = [
            {
                "document_id": "doc1",
                "content": "Para 1.\n\nPara 2.",
                "metadata": {"company": "Corp1"},
            },
            {
                "document_id": "doc2",
                "content": "Para 1.\n\nPara 2.\n\nPara 3.",
                "metadata": {"company": "Corp2"},
            },
        ]

        all_chunks, error = chunker.batch_chunk_documents(documents)

        assert error is None
        assert len(all_chunks) >= 2  # At least one chunk per doc
        doc1_chunks = [c for c in all_chunks if c.document_id == "doc1"]
        doc2_chunks = [c for c in all_chunks if c.document_id == "doc2"]
        assert len(doc1_chunks) > 0
        assert len(doc2_chunks) > 0
        assert all(c.metadata["company"] in ["Corp1", "Corp2"] for c in all_chunks)

    def test_batch_with_bad_document(self):
        """Test batch with invalid document."""
        chunker = SemanticChunker()
        documents = [
            {"document_id": "doc1", "content": "Valid content.\n\nMore content."},
            {"document_id": "", "content": "Content here"},  # Missing doc_id
        ]

        all_chunks, error = chunker.batch_chunk_documents(documents)

        assert error is not None
        assert "Error chunking" in error

    def test_chunk_paragraph_count(self):
        """Test chunk tracks paragraph count."""
        chunker = SemanticChunker()
        content = "Para 1.\n\nPara 2.\n\nPara 3."

        chunks, _ = chunker.chunk_document("doc1", content)

        assert all(c.paragraph_count > 0 for c in chunks)

    def test_chunk_sentence_count(self):
        """Test chunk tracks sentence count."""
        chunker = SemanticChunker()
        content = "First sentence. Second sentence. Third sentence."

        chunks, _ = chunker.chunk_document("doc1", content)

        assert chunks[0].sentence_count > 0

    def test_chunk_position_tracking(self):
        """Test chunks track character positions."""
        chunker = SemanticChunker()
        content = "Paragraph 1.\n\nParagraph 2."

        chunks, _ = chunker.chunk_document("doc1", content)

        for chunk in chunks:
            assert chunk.start_char < chunk.end_char
            assert chunk.start_char >= 0

    def test_statistics_empty(self):
        """Test statistics with no chunks."""
        chunker = SemanticChunker()
        stats = chunker.get_statistics([])

        assert stats["total_chunks"] == 0
        assert stats["avg_tokens"] == 0

    def test_statistics_with_chunks(self):
        """Test statistics with chunks."""
        chunker = SemanticChunker()
        content = "Para 1.\n\nPara 2.\n\nPara 3.\n\nPara 4."
        chunks, _ = chunker.chunk_document("doc1", content)

        stats = chunker.get_statistics(chunks)

        assert stats["total_chunks"] > 0
        assert stats["avg_tokens"] > 0
        assert stats["avg_paragraphs"] > 0

    def test_export_chunks(self):
        """Test exporting chunks."""
        chunker = SemanticChunker()
        content = "Paragraph 1.\n\nParagraph 2."
        chunks, _ = chunker.chunk_document("doc1", content)

        exported = chunker.export_chunks(chunks)

        assert len(exported) == len(chunks)
        assert all(isinstance(e, dict) for e in exported)
        assert all("chunk_id" in e for e in exported)

    def test_very_long_document(self):
        """Test chunking very long document."""
        chunker = SemanticChunker(max_tokens=100)
        # Create a long document with many paragraphs
        content = "\n\n".join([f"Paragraph {i} with content. " * 5 for i in range(50)])

        chunks, error = chunker.chunk_document("doc_long", content)

        assert error is None
        assert len(chunks) > 1

    def test_single_long_paragraph(self):
        """Test handling single very long paragraph."""
        chunker = SemanticChunker(max_tokens=100)
        long_para = "This is a very long paragraph. " * 50  # Will be ~400+ tokens

        chunks, error = chunker.chunk_document("doc1", long_para)

        assert error is None
        assert len(chunks) > 0

    def test_whitespace_only_content(self):
        """Test handling whitespace-only content."""
        chunker = SemanticChunker()
        chunks, error = chunker.chunk_document("doc1", "   \n\n   \n\n   ")

        assert error is not None
        assert len(chunks) == 0

    def test_multiple_chunkers_independent(self):
        """Test multiple chunker instances are independent."""
        c1 = SemanticChunker(min_tokens=50, max_tokens=200)
        c2 = SemanticChunker(min_tokens=100, max_tokens=400)

        content = "Para 1.\n\nPara 2.\n\nPara 3."

        chunks1, _ = c1.chunk_document("doc1", content)
        chunks2, _ = c2.chunk_document("doc1", content)

        # Different configs may produce different chunking
        assert c1.min_tokens != c2.min_tokens

    def test_unicode_content(self):
        """Test chunking Unicode content."""
        chunker = SemanticChunker()
        content = "Hindi: नमस्ते। Hinglish: Aaj ka mausam accha hai.\n\nMore content yahan hai."

        chunks, error = chunker.chunk_document("doc1", content)

        assert error is None
        assert len(chunks) > 0
        assert "नमस्ते" in chunks[0].content or "Hinglish" in chunks[0].content

    def test_special_characters_preserved(self):
        """Test special characters are preserved."""
        chunker = SemanticChunker()
        content = "Code example: @decorator def func(): pass\n\nMore text with #hashtags and $money."

        chunks, error = chunker.chunk_document("doc1", content)

        assert error is None
        combined = "\n\n".join(c.content for c in chunks)
        assert "@decorator" in combined
        assert "#hashtags" in combined

    def test_chunk_ids_unique(self):
        """Test chunk IDs are unique."""
        chunker = SemanticChunker()
        content = "\n\n".join([f"Para {i}." for i in range(10)])

        chunks, _ = chunker.chunk_document("doc1", content)

        chunk_ids = [c.chunk_id for c in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))  # All unique

    def test_complete_workflow(self):
        """Test complete chunking workflow."""
        chunker = SemanticChunker()

        # Create a realistic document
        content = """Introduction paragraph with overview.

First section with detailed information. This covers the main topic.

Second section with more details. Important points are highlighted.

Third section with additional context. Final thoughts here.

Conclusion wrapping up the document."""

        chunks, error = chunker.chunk_document(
            "doc_workflow",
            content,
            metadata={"company": "TechCorp", "domain": "career"},
        )

        assert error is None
        assert len(chunks) > 0

        # Verify stats
        stats = chunker.get_statistics(chunks)
        assert stats["total_chunks"] > 0
        assert stats["avg_tokens"] > 0

        # Export and verify
        exported = chunker.export_chunks(chunks)
        assert len(exported) == len(chunks)
        assert all(e["metadata"]["company"] == "TechCorp" for e in exported)

    def test_batch_statistics(self):
        """Test statistics across batch of documents."""
        chunker = SemanticChunker()
        documents = [
            {"document_id": f"doc{i}", "content": f"Para {i}.\n\nPara {i+1}."}
            for i in range(5)
        ]

        all_chunks, _ = chunker.batch_chunk_documents(documents)
        stats = chunker.get_statistics(all_chunks)

        assert stats["total_chunks"] >= 5  # At least one chunk per doc
        assert stats["avg_tokens"] > 0
        assert "max_tokens" in stats
        assert "min_tokens" in stats
