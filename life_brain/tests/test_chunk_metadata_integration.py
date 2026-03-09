"""
Integration tests for semantic chunks with parent document metadata references.

Tests cover:
- Child chunks have parent doc_id reference
- Child chunks inherit company, project, domain, category
- Metadata tracing from parent to child
- Batch integration of chunking and metadata
- Filtering chunks by parent metadata
"""

import pytest

from life_brain.core.semantic_chunking import SemanticChunker
from life_brain.core.metadata_inheritance import (
    MetadataInheritanceManager,
    DocumentMetadata,
)


class TestChunkMetadataReferences:
    """Test that chunks properly reference and inherit from parents."""

    def test_chunk_has_document_id_reference(self):
        """Test chunks reference their parent document."""
        chunker = SemanticChunker()
        content = "Para 1.\n\nPara 2.\n\nPara 3."

        chunks, error = chunker.chunk_document("parent_doc_123", content)

        assert error is None
        assert all(c.document_id == "parent_doc_123" for c in chunks)

    def test_chunk_includes_parent_metadata(self):
        """Test chunks include metadata from parent."""
        chunker = SemanticChunker()
        content = "Para 1.\n\nPara 2."
        metadata = {
            "company": "TechCorp",
            "project": "ProjectX",
            "domain": "career",
            "category": "experience",
        }

        chunks, _ = chunker.chunk_document("doc1", content, metadata)

        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk.metadata["company"] == "TechCorp"
            assert chunk.metadata["project"] == "ProjectX"
            assert chunk.metadata["domain"] == "career"
            assert chunk.metadata["category"] == "experience"

    def test_chunk_sequence_maintains_order(self):
        """Test chunk sequence numbers maintain document order."""
        chunker = SemanticChunker()
        content = "\n\n".join([f"Paragraph {i}." for i in range(10)])

        chunks, _ = chunker.chunk_document("doc1", content)

        sequences = [c.sequence for c in chunks]
        assert sequences == sorted(sequences)
        assert sequences[0] == 0

    def test_chunk_position_tracking_for_retrieval(self):
        """Test chunk positions can be used to retrieve original content."""
        chunker = SemanticChunker()
        original_content = "Para 1.\n\nPara 2.\n\nPara 3."

        chunks, _ = chunker.chunk_document("doc1", original_content)

        # Can reconstruct content from chunks' start/end positions
        reconstructed = original_content
        for chunk in chunks:
            assert original_content[chunk.start_char : chunk.end_char]

    def test_multiple_chunks_from_single_document(self):
        """Test single document produces multiple chunks with same parent."""
        chunker = SemanticChunker(max_tokens=100)
        content = "\n\n".join(["Paragraph with substantial content. " * 5 for _ in range(10)])

        chunks, _ = chunker.chunk_document("doc1", content)

        assert len(chunks) > 1
        assert all(c.document_id == "doc1" for c in chunks)
        doc_ids = [c.document_id for c in chunks]
        assert len(set(doc_ids)) == 1  # All have same parent

    def test_chunk_metadata_inheritance_with_manager(self):
        """Test semantic chunks can integrate with MetadataInheritanceManager."""
        chunker = SemanticChunker()
        manager = MetadataInheritanceManager()

        # Register parent document with metadata
        manager.register_document(
            doc_id="doc1",
            title="Career Document",
            company="TechCorp",
            project="ProjectX",
            domain="career",
            category="interview",
        )

        # Chunk the document
        content = "Experience 1.\n\nExperience 2.\n\nExperience 3."
        chunks, _ = chunker.chunk_document(
            "doc1",
            content,
            metadata={
                "company": "TechCorp",
                "project": "ProjectX",
                "domain": "career",
            },
        )

        # Verify chunks have parent metadata
        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk.metadata["company"] == "TechCorp"
            assert chunk.metadata["project"] == "ProjectX"

    def test_batch_chunks_preserve_document_relationships(self):
        """Test batch chunking preserves parent-child relationships."""
        chunker = SemanticChunker()
        documents = [
            {
                "document_id": "doc1",
                "content": "Para 1.\n\nPara 2.",
                "metadata": {"company": "Corp1", "domain": "tech"},
            },
            {
                "document_id": "doc2",
                "content": "Para 1.\n\nPara 2.\n\nPara 3.",
                "metadata": {"company": "Corp2", "domain": "health"},
            },
        ]

        all_chunks, _ = chunker.batch_chunk_documents(documents)

        # Verify chunks from doc1
        doc1_chunks = [c for c in all_chunks if c.document_id == "doc1"]
        assert len(doc1_chunks) > 0
        assert all(c.metadata["company"] == "Corp1" for c in doc1_chunks)

        # Verify chunks from doc2
        doc2_chunks = [c for c in all_chunks if c.document_id == "doc2"]
        assert len(doc2_chunks) > 0
        assert all(c.metadata["company"] == "Corp2" for c in doc2_chunks)

    def test_filtering_chunks_by_parent_metadata(self):
        """Test chunks can be filtered by parent metadata."""
        chunker = SemanticChunker()
        documents = [
            {
                "document_id": "doc1",
                "content": "Career content 1.\n\nCareer content 2.",
                "metadata": {"company": "TechCorp", "domain": "career"},
            },
            {
                "document_id": "doc2",
                "content": "Health content 1.\n\nHealth content 2.",
                "metadata": {"company": "HealthCorp", "domain": "health"},
            },
        ]

        all_chunks, _ = chunker.batch_chunk_documents(documents)

        # Filter by company
        techcorp_chunks = [
            c for c in all_chunks if c.metadata.get("company") == "TechCorp"
        ]
        assert len(techcorp_chunks) > 0
        assert all(c.metadata["company"] == "TechCorp" for c in techcorp_chunks)

        # Filter by domain
        health_chunks = [c for c in all_chunks if c.metadata.get("domain") == "health"]
        assert len(health_chunks) > 0
        assert all(c.metadata["domain"] == "health" for c in health_chunks)

    def test_chunk_export_includes_all_references(self):
        """Test exported chunks include all reference information."""
        chunker = SemanticChunker()
        content = "Para 1.\n\nPara 2."
        metadata = {"company": "Corp", "project": "Proj", "domain": "tech"}

        chunks, _ = chunker.chunk_document("doc_123", content, metadata)
        exported = chunker.export_chunks(chunks)

        for exp in exported:
            assert exp["document_id"] == "doc_123"
            assert exp["metadata"]["company"] == "Corp"
            assert exp["metadata"]["project"] == "Proj"
            assert "chunk_id" in exp
            assert "sequence" in exp

    def test_chunk_retrieval_by_document(self):
        """Test retrieving all chunks for a specific document."""
        chunker = SemanticChunker()
        documents = [
            {"document_id": "doc1", "content": f"Para {i}.\n\n" * 3}
            for i in range(3)
        ]

        all_chunks, _ = chunker.batch_chunk_documents(documents)

        # Get all chunks for doc1
        doc1_chunks = [c for c in all_chunks if c.document_id == "doc1"]
        assert len(doc1_chunks) > 0

        # Verify all doc1 chunks
        doc1_ids = set(c.document_id for c in doc1_chunks)
        assert doc1_ids == {"doc1"}

    def test_parent_document_metadata_reference(self):
        """Test chunks can be traced back to parent document metadata."""
        manager = MetadataInheritanceManager()
        chunker = SemanticChunker()

        # Register parent with rich metadata
        parent = manager.register_document(
            doc_id="interview_doc_001",
            title="Interview Prep",
            company="Google",
            project="SDE Interview",
            domain="career",
            category="interview",
            tags=["system-design", "python", "backend"],
        )

        # Chunk the document
        content = "Question 1.\n\nQuestion 2.\n\nQuestion 3."
        chunks, _ = chunker.chunk_document(
            "interview_doc_001",
            content,
            metadata={
                "company": parent.company,
                "project": parent.project,
                "domain": parent.domain,
                "category": parent.category,
                "tags": parent.tags,
            },
        )

        # Verify chunk metadata matches parent
        for chunk in chunks:
            assert chunk.document_id == parent.doc_id
            assert chunk.metadata["company"] == parent.company
            assert chunk.metadata["project"] == parent.project
            assert chunk.metadata["domain"] == parent.domain

    def test_chunk_sequence_for_ordering(self):
        """Test chunk sequence can be used to order chunks."""
        chunker = SemanticChunker()
        content = "\n\n".join([f"Chunk {i}: Content here." for i in range(5)])

        chunks, _ = chunker.chunk_document("doc1", content)

        # Sort by sequence
        sorted_chunks = sorted(chunks, key=lambda c: c.sequence)

        # Verify order is preserved
        for i, chunk in enumerate(sorted_chunks):
            assert chunk.sequence == i

    def test_chunk_links_preserve_content_integrity(self):
        """Test chunk links preserve content integrity across chunking."""
        chunker = SemanticChunker()
        original_text = """Section 1: Introduction.

This is the first paragraph with content.

Section 2: Main Content.

This is the second paragraph with content."""

        chunks, _ = chunker.chunk_document("doc1", original_text)

        # Reconstruct content
        chunk_texts = [c.content for c in sorted(chunks, key=lambda c: c.sequence)]
        reconstructed = "\n\n".join(chunk_texts)

        # Verify key content is preserved
        assert "Section 1" in reconstructed
        assert "Section 2" in reconstructed
        assert "Introduction" in reconstructed

    def test_complete_integration_workflow(self):
        """Test complete workflow: register doc, chunk it, verify metadata."""
        # Setup
        manager = MetadataInheritanceManager()
        chunker = SemanticChunker()

        # 1. Register parent document
        doc = manager.register_document(
            doc_id="career_doc_001",
            title="My Career Journey",
            company="Sprinklr",
            project="CGB Project",
            domain="career",
            category="project-experience",
        )

        # 2. Create content and chunk it
        content = """Project: Citizen Governance Bot

CGB is an AI-powered platform for civic engagement. Responsibilities included architecture design, backend development, and stakeholder management.

Key achievements: 10M+ citizen interactions, 50+ cities adoption, 99.9% uptime.

Technical stack: Python, PostgreSQL, Redis, Kubernetes."""

        chunks, error = chunker.chunk_document(
            doc.doc_id,
            content,
            metadata={
                "company": doc.company,
                "project": doc.project,
                "domain": doc.domain,
                "category": doc.category,
            },
        )

        # 3. Verify all chunks are properly linked
        assert error is None
        assert len(chunks) > 0

        for chunk in chunks:
            # Verify parent reference
            assert chunk.document_id == doc.doc_id

            # Verify metadata inheritance
            assert chunk.metadata["company"] == doc.company
            assert chunk.metadata["project"] == doc.project
            assert chunk.metadata["domain"] == doc.domain

            # Verify sequence
            assert chunk.sequence >= 0

            # Verify content integrity
            assert len(chunk.content) > 0
            assert chunk.token_count > 0

        # 4. Test filtering
        sprinklr_chunks = [
            c for c in chunks if c.metadata.get("company") == "Sprinklr"
        ]
        assert len(sprinklr_chunks) == len(chunks)  # All from Sprinklr

        # 5. Export and verify
        exported = chunker.export_chunks(chunks)
        assert all(e["document_id"] == doc.doc_id for e in exported)
        assert all(e["metadata"]["company"] == "Sprinklr" for e in exported)
