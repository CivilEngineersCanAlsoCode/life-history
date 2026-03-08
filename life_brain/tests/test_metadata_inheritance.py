"""
Test suite for metadata inheritance module.

Tests cover:
- Document registration
- Chunk creation with inherited metadata
- Metadata override
- Batch operations
- Retrieval and filtering
- Statistics and exports
"""

import pytest

from life_brain.storage.metadata_inheritance import (
    MetadataInheritanceManager,
    DocumentMetadata,
    ChunkMetadata,
)


class TestDocumentMetadata:
    """Test DocumentMetadata dataclass."""

    def test_create_metadata(self):
        """Test creating document metadata."""
        metadata = DocumentMetadata(
            doc_id="doc1",
            title="Test Doc",
            company="TechCorp",
            project="ProjectX",
        )

        assert metadata.doc_id == "doc1"
        assert metadata.company == "TechCorp"

    def test_to_dict(self):
        """Test converting to dict."""
        metadata = DocumentMetadata(
            doc_id="doc2",
            title="Another Doc",
            domain="career",
            tags=["python", "backend"],
        )

        d = metadata.to_dict()
        assert d["doc_id"] == "doc2"
        assert d["domain"] == "career"


class TestChunkMetadata:
    """Test ChunkMetadata dataclass."""

    def test_create_chunk_metadata(self):
        """Test creating chunk metadata."""
        chunk = ChunkMetadata(
            chunk_id="chunk1",
            parent_doc_id="doc1",
            sequence=0,
            company="Corp",
        )

        assert chunk.parent_doc_id == "doc1"
        assert chunk.sequence == 0

    def test_to_dict(self):
        """Test converting chunk to dict."""
        chunk = ChunkMetadata(
            chunk_id="chunk2",
            parent_doc_id="doc2",
            sequence=1,
            domain="health",
        )

        d = chunk.to_dict()
        assert d["chunk_id"] == "chunk2"
        assert d["domain"] == "health"


class TestMetadataInheritanceManager:
    """Test MetadataInheritanceManager functionality."""

    def test_create_manager(self):
        """Test creating manager."""
        manager = MetadataInheritanceManager()
        assert len(manager.parent_documents) == 0

    def test_register_document(self):
        """Test registering document."""
        manager = MetadataInheritanceManager()
        doc = manager.register_document(
            doc_id="doc1",
            title="My Document",
            company="TechCorp",
            project="API",
            domain="career",
        )

        assert doc.doc_id == "doc1"
        assert doc.company == "TechCorp"

    def test_create_chunk_with_inherited_metadata(self):
        """Test creating chunk with inherited metadata."""
        manager = MetadataInheritanceManager()
        manager.register_document(
            "doc1", "Doc Title", company="Corp", project="Proj", domain="tech"
        )

        chunk_meta, error = manager.create_chunk(
            "doc1", "Chunk content here", sequence=0
        )

        assert error is None
        assert chunk_meta is not None
        assert chunk_meta.company == "Corp"
        assert chunk_meta.project == "Proj"
        assert chunk_meta.domain == "tech"

    def test_create_chunk_nonexistent_document(self):
        """Test creating chunk for nonexistent document."""
        manager = MetadataInheritanceManager()
        chunk_meta, error = manager.create_chunk(
            "nonexistent", "Content", sequence=0
        )

        assert error is not None
        assert chunk_meta is None

    def test_chunk_metadata_override(self):
        """Test overriding chunk metadata."""
        manager = MetadataInheritanceManager()
        manager.register_document("doc1", "Doc", company="Corp", project="Proj")

        chunk_meta, _ = manager.create_chunk(
            "doc1",
            "Content",
            sequence=0,
            override_metadata={"domain": "health"}  # Override
        )

        assert chunk_meta.domain == "health"

    def test_custom_chunk_id(self):
        """Test creating chunk with custom ID."""
        manager = MetadataInheritanceManager()
        manager.register_document("doc1", "Doc")

        chunk_meta, _ = manager.create_chunk(
            "doc1", "Content", sequence=0, chunk_id="custom_123"
        )

        assert chunk_meta.chunk_id == "custom_123"

    def test_batch_create_chunks(self):
        """Test batch creating chunks."""
        manager = MetadataInheritanceManager()
        manager.register_document("doc1", "Doc", company="Corp", project="Proj")

        chunks, error = manager.batch_create_chunks(
            "doc1",
            ["Content 1", "Content 2", "Content 3"],
            chunk_type="text"
        )

        assert error is None
        assert len(chunks) == 3
        assert all(c.company == "Corp" for c in chunks)

    def test_get_chunk(self):
        """Test retrieving chunk."""
        manager = MetadataInheritanceManager()
        manager.register_document("doc1", "Doc")
        chunk_meta, _ = manager.create_chunk("doc1", "Test content", sequence=0)

        retrieved = manager.get_chunk(chunk_meta.chunk_id)
        assert retrieved is not None
        content, metadata = retrieved
        assert content == "Test content"

    def test_get_nonexistent_chunk(self):
        """Test retrieving nonexistent chunk."""
        manager = MetadataInheritanceManager()
        chunk = manager.get_chunk("nonexistent")
        assert chunk is None

    def test_get_chunks_for_document(self):
        """Test retrieving chunks for a document."""
        manager = MetadataInheritanceManager()
        manager.register_document("doc1", "Doc1")
        manager.register_document("doc2", "Doc2")

        manager.batch_create_chunks("doc1", ["C1", "C2"])
        manager.batch_create_chunks("doc2", ["C3"])

        doc1_chunks = manager.get_chunks_for_document("doc1")
        assert len(doc1_chunks) == 2

    def test_get_chunks_by_domain(self):
        """Test retrieving chunks by domain."""
        manager = MetadataInheritanceManager()
        manager.register_document("doc1", "Doc", domain="career")
        manager.register_document("doc2", "Doc", domain="health")

        manager.batch_create_chunks("doc1", ["C1"])
        manager.batch_create_chunks("doc2", ["C2"])

        career_chunks = manager.get_chunks_by_domain("career")
        assert len(career_chunks) == 1

    def test_get_chunks_by_project(self):
        """Test retrieving chunks by project."""
        manager = MetadataInheritanceManager()
        manager.register_document("doc1", "Doc", project="ProjectA")
        manager.register_document("doc2", "Doc", project="ProjectB")

        manager.batch_create_chunks("doc1", ["C1"])
        manager.batch_create_chunks("doc2", ["C2"])

        proj_a = manager.get_chunks_by_project("ProjectA")
        assert len(proj_a) == 1

    def test_get_chunks_by_company(self):
        """Test retrieving chunks by company."""
        manager = MetadataInheritanceManager()
        manager.register_document("doc1", "Doc", company="CompanyA")
        manager.register_document("doc2", "Doc", company="CompanyB")

        manager.batch_create_chunks("doc1", ["C1"])
        manager.batch_create_chunks("doc2", ["C2"])

        comp_a = manager.get_chunks_by_company("CompanyA")
        assert len(comp_a) == 1

    def test_get_chunks_by_tag(self):
        """Test retrieving chunks by tag."""
        manager = MetadataInheritanceManager()
        manager.register_document("doc1", "Doc", tags=["python", "backend"])

        manager.batch_create_chunks("doc1", ["C1", "C2"])

        python_chunks = manager.get_chunks_by_tag("python")
        assert len(python_chunks) == 2

    def test_update_chunk_metadata(self):
        """Test updating chunk metadata."""
        manager = MetadataInheritanceManager()
        manager.register_document("doc1", "Doc")
        chunk_meta, _ = manager.create_chunk("doc1", "Content", sequence=0)

        updated, error = manager.update_chunk_metadata(
            chunk_meta.chunk_id, confidence=0.9
        )

        assert error is None
        assert updated.confidence == 0.9

    def test_update_nonexistent_chunk(self):
        """Test updating nonexistent chunk."""
        manager = MetadataInheritanceManager()
        updated, error = manager.update_chunk_metadata("nonexistent", confidence=0.8)

        assert error is not None
        assert updated is None

    def test_export_chunk(self):
        """Test exporting chunk."""
        manager = MetadataInheritanceManager()
        manager.register_document("doc1", "Doc")
        chunk_meta, _ = manager.create_chunk("doc1", "Content", sequence=0)

        exported = manager.export_chunk(chunk_meta.chunk_id)
        assert exported is not None
        assert exported["chunk_id"] == chunk_meta.chunk_id

    def test_export_nonexistent_chunk(self):
        """Test exporting nonexistent chunk."""
        manager = MetadataInheritanceManager()
        exported = manager.export_chunk("nonexistent")
        assert exported is None

    def test_export_all_chunks_for_document(self):
        """Test exporting all chunks for document."""
        manager = MetadataInheritanceManager()
        manager.register_document("doc1", "Doc")
        manager.batch_create_chunks("doc1", ["C1", "C2", "C3"])

        exported = manager.export_all_chunks_for_document("doc1")
        assert len(exported) == 3

    def test_statistics_empty(self):
        """Test statistics with no chunks."""
        manager = MetadataInheritanceManager()
        stats = manager.get_statistics()

        assert stats["total_chunks"] == 0

    def test_statistics_with_chunks(self):
        """Test statistics with chunks."""
        manager = MetadataInheritanceManager()
        manager.register_document("doc1", "Doc", company="Corp", domain="career")
        manager.batch_create_chunks("doc1", ["C1", "C2"])

        stats = manager.get_statistics()
        assert stats["total_chunks"] == 2
        assert stats["total_documents"] == 1

    def test_inheritance_map(self):
        """Test getting inheritance map."""
        manager = MetadataInheritanceManager()
        manager.register_document("doc1", "Doc1")
        manager.batch_create_chunks("doc1", ["C1", "C2"])

        mapping = manager.get_inheritance_map()
        assert "doc1" in mapping
        assert mapping["doc1"]["chunk_count"] == 2

    def test_multiple_managers_independent(self):
        """Test multiple managers are independent."""
        m1 = MetadataInheritanceManager()
        m2 = MetadataInheritanceManager()

        m1.register_document("doc1", "Doc1")
        m2.register_document("doc2", "Doc2")

        assert len(m1.parent_documents) == 1
        assert len(m2.parent_documents) == 1

    def test_token_counting(self):
        """Test token counting."""
        manager = MetadataInheritanceManager()
        manager.register_document("doc1", "Doc")

        # Estimate: 4 chars per token
        long_content = "x" * 100
        chunk_meta, _ = manager.create_chunk("doc1", long_content, sequence=0)

        assert chunk_meta.token_count > 0
        assert chunk_meta.char_count == 100

    def test_chunk_type_tracking(self):
        """Test chunk type is tracked."""
        manager = MetadataInheritanceManager()
        manager.register_document("doc1", "Doc")

        chunk_meta, _ = manager.create_chunk(
            "doc1", "Code here", sequence=0, chunk_type="code"
        )

        assert chunk_meta.chunk_type == "code"

    def test_chunk_sequence_ordering(self):
        """Test chunks maintain sequence."""
        manager = MetadataInheritanceManager()
        manager.register_document("doc1", "Doc")

        for i in range(5):
            chunk_meta, _ = manager.create_chunk(
                "doc1", f"Content {i}", sequence=i
            )

        chunks = manager.get_chunks_for_document("doc1")
        sequences = [c[1].sequence for c in chunks]
        assert sequences == sorted(sequences)

    def test_complex_metadata_inheritance(self):
        """Test complex metadata inheritance scenario."""
        manager = MetadataInheritanceManager()

        # Register document with full metadata
        manager.register_document(
            doc_id="doc1",
            title="Complex Document",
            company="TechCorp",
            project="Project Alpha",
            domain="career",
            category="interview",
            tags=["python", "backend", "api"],
        )

        # Create chunks - should inherit all metadata
        chunk_meta, _ = manager.create_chunk("doc1", "Content", sequence=0)

        assert chunk_meta.company == "TechCorp"
        assert chunk_meta.project == "Project Alpha"
        assert chunk_meta.domain == "career"
        assert chunk_meta.category == "interview"
        assert "python" in chunk_meta.tags

    def test_complete_workflow(self):
        """Test complete metadata inheritance workflow."""
        manager = MetadataInheritanceManager()

        # Register documents
        manager.register_document("doc1", "Doc1", company="Corp1", domain="tech")
        manager.register_document("doc2", "Doc2", company="Corp2", domain="health")

        # Create chunks
        manager.batch_create_chunks("doc1", ["C1", "C2", "C3"])
        manager.batch_create_chunks("doc2", ["C4", "C5"])

        # Retrieve by context
        tech_chunks = manager.get_chunks_by_domain("tech")
        assert len(tech_chunks) == 3

        corp1_chunks = manager.get_chunks_by_company("Corp1")
        assert len(corp1_chunks) == 3

        # Get statistics
        stats = manager.get_statistics()
        assert stats["total_chunks"] == 5
        assert stats["total_documents"] == 2

        # Export data
        mapping = manager.get_inheritance_map()
        assert len(mapping) == 2


class TestNullParentDocIdBug:
    """Regression tests for issues-beu: metadata inheritance fails when parent doc_id is null.

    Bug: create_chunk() with None parent_doc_id silently passed to dict.get(None)
    and produced confusing error. register_document() with None doc_id stored bad state.
    Fix: explicit null checks with clear error messages before processing.
    """

    def test_create_chunk_null_parent_doc_id_returns_error(self):
        """create_chunk() with None parent_doc_id should return error, not crash."""
        manager = MetadataInheritanceManager()
        chunk, error = manager.create_chunk(
            parent_doc_id=None, chunk_content="some text", sequence=0
        )
        assert chunk is None
        assert error is not None
        assert "null" in error.lower() or "empty" in error.lower()

    def test_create_chunk_empty_parent_doc_id_returns_error(self):
        """create_chunk() with empty string parent_doc_id should return error."""
        manager = MetadataInheritanceManager()
        chunk, error = manager.create_chunk(
            parent_doc_id="", chunk_content="some text", sequence=0
        )
        assert chunk is None
        assert error is not None

    def test_register_document_null_doc_id_raises(self):
        """register_document() with None doc_id should raise ValueError."""
        manager = MetadataInheritanceManager()
        with pytest.raises(ValueError):
            manager.register_document(doc_id=None, title="Test Doc")

    def test_register_document_empty_doc_id_raises(self):
        """register_document() with empty string doc_id should raise ValueError."""
        manager = MetadataInheritanceManager()
        with pytest.raises(ValueError):
            manager.register_document(doc_id="", title="Test Doc")

    def test_valid_doc_id_still_works(self):
        """Normal (non-null) doc_id must still work after guard added."""
        manager = MetadataInheritanceManager()
        manager.register_document("doc1", "My Doc", company="Acme")
        chunk, error = manager.create_chunk("doc1", "chunk content", sequence=0)
        assert error is None
        assert chunk is not None
        assert chunk.company == "Acme"
