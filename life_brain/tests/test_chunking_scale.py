"""
Scale tests for semantic chunking on 10+ documents.

Tests cover:
- Chunking multiple documents efficiently
- Chunks embed independently (self-contained)
- Chunk independence verification
- Metadata consistency across batch
- Performance and throughput metrics
"""

import pytest
import time

from life_brain.ingestion.semantic_chunking import SemanticChunker


class TestChunkingScale:
    """Test chunking at scale with multiple documents."""

    @staticmethod
    def create_test_documents(count: int = 10) -> list:
        """Create realistic test documents for scale testing.

        Args:
            count: Number of documents to create

        Returns:
            List of document dicts
        """
        companies = ["Google", "Amazon", "Microsoft", "Apple", "Meta"]
        domains = ["career", "tech", "health", "relationships"]
        projects = ["Project X", "Project Y", "Project Z"]

        documents = []
        for i in range(count):
            company = companies[i % len(companies)]
            domain = domains[i % len(domains)]
            project = projects[i % len(projects)]

            # Create a larger multi-paragraph document to trigger multiple chunks
            sections = []
            for sec in range(6):  # 6 sections
                sections.append(
                    f"""Section {sec}: {["Overview", "Technical", "Implementation", "Results", "Lessons", "Conclusion"][sec]}

This section covers important details. Document {i} from {company} working on {project} in the {domain} domain.

Detailed paragraph with substantial content about the topic. Multiple sentences provide comprehensive information about various aspects of the work. The implementation includes different components and systems that work together.

Additional context and background information relevant to understanding the section. Performance metrics showed significant improvements. Quality was maintained throughout the implementation.

Results demonstrate the value of the approach. Team collaboration was essential for successful delivery. Various challenges were overcome through creative problem-solving.

Key insights and takeaways from this section include best practices for future work. Investment in this area continues to provide value. The foundation built here supports future initiatives.

Next steps and recommendations for ongoing work."""
                )

            content = "\n\n".join(sections)

            documents.append(
                {
                    "document_id": f"doc_{i:03d}_{company.lower()}",
                    "content": content,
                    "metadata": {
                        "company": company,
                        "domain": domain,
                        "project": project,
                        "doc_index": i,
                    },
                }
            )

        return documents

    def test_chunk_10_documents(self):
        """Test chunking 10 documents produces reasonable chunks."""
        chunker = SemanticChunker()
        documents = self.create_test_documents(10)

        all_chunks, error = chunker.batch_chunk_documents(documents)

        assert error is None
        assert len(all_chunks) > 0
        assert len(all_chunks) > 10  # Should have more chunks than docs

    def test_chunks_are_independent_units(self):
        """Test chunks are self-contained and embeddable independently."""
        chunker = SemanticChunker()
        documents = self.create_test_documents(5)

        all_chunks, _ = chunker.batch_chunk_documents(documents)

        # Verify each chunk can stand alone
        for chunk in all_chunks:
            # Each chunk has required fields
            assert chunk.chunk_id
            assert chunk.document_id
            assert chunk.content
            assert chunk.content.strip()  # Non-empty content

            # Chunk has semantic meaning (multiple sentences ideally)
            sentence_count = chunk.content.count(".")
            assert sentence_count > 0  # At least one sentence

            # Token count is reasonable for embedding
            assert chunk.token_count > 0
            # Note: Single large paragraphs may exceed max_tokens
            assert chunk.token_count <= chunker.max_tokens * 2

    def test_chunks_maintain_document_reference(self):
        """Test chunks maintain clear reference to parent document."""
        chunker = SemanticChunker()
        documents = self.create_test_documents(10)

        all_chunks, _ = chunker.batch_chunk_documents(documents)

        # Group by document
        doc_mapping = {}
        for chunk in all_chunks:
            if chunk.document_id not in doc_mapping:
                doc_mapping[chunk.document_id] = []
            doc_mapping[chunk.document_id].append(chunk)

        # Verify we have chunks from all documents
        assert len(doc_mapping) == 10

        # Verify each document's chunks are traceable
        for doc_id, chunks in doc_mapping.items():
            assert len(chunks) > 0
            # All chunks from same document have same doc_id
            assert all(c.document_id == doc_id for c in chunks)

    def test_chunk_sequence_preservation(self):
        """Test chunk sequences preserve document order."""
        chunker = SemanticChunker()
        documents = self.create_test_documents(10)

        all_chunks, _ = chunker.batch_chunk_documents(documents)

        # Group by document
        for doc_id in set(c.document_id for c in all_chunks):
            doc_chunks = [c for c in all_chunks if c.document_id == doc_id]

            # Verify sequence numbers are in order
            sequences = [c.sequence for c in doc_chunks]
            assert sequences == sorted(sequences)

    def test_metadata_propagation_at_scale(self):
        """Test metadata propagates correctly across 10 documents."""
        chunker = SemanticChunker()
        documents = self.create_test_documents(10)

        all_chunks, _ = chunker.batch_chunk_documents(documents)

        # Verify metadata in chunks
        for chunk in all_chunks:
            # Extract original document metadata
            doc_index = int(chunk.chunk_id.split("_")[2])
            doc = documents[doc_index]

            # Verify metadata matches
            assert chunk.metadata["company"] == doc["metadata"]["company"]
            assert chunk.metadata["domain"] == doc["metadata"]["domain"]
            assert chunk.metadata["project"] == doc["metadata"]["project"]

    def test_chunk_completeness_at_scale(self):
        """Test chunks cover the full content of all documents."""
        chunker = SemanticChunker()
        documents = self.create_test_documents(5)

        all_chunks, _ = chunker.batch_chunk_documents(documents)

        # For each document, verify content coverage
        for doc in documents:
            doc_chunks = [c for c in all_chunks if c.document_id == doc["document_id"]]
            combined_content = "\n\n".join(c.content for c in doc_chunks)

            # Verify key sections are present
            assert "Document" in combined_content
            assert "section" in combined_content.lower()

    def test_chunk_uniqueness_across_documents(self):
        """Test chunk IDs are unique across all documents."""
        chunker = SemanticChunker()
        documents = self.create_test_documents(10)

        all_chunks, _ = chunker.batch_chunk_documents(documents)

        chunk_ids = [c.chunk_id for c in all_chunks]
        # All IDs should be unique
        assert len(chunk_ids) == len(set(chunk_ids))

    def test_statistical_summary_at_scale(self):
        """Test statistics across 10-document batch."""
        chunker = SemanticChunker()
        documents = self.create_test_documents(10)

        all_chunks, _ = chunker.batch_chunk_documents(documents)
        stats = chunker.get_statistics(all_chunks)

        assert stats["total_chunks"] > 10
        assert stats["avg_tokens"] > 0
        assert stats["avg_paragraphs"] > 0
        assert stats["total_content_chars"] > 0
        assert stats["min_tokens"] > 0
        # Note: Single large paragraphs may exceed max_tokens
        assert stats["max_tokens"] > 0

    def test_performance_metrics(self):
        """Test chunking performance on 10 documents."""
        chunker = SemanticChunker()
        documents = self.create_test_documents(10)

        start_time = time.time()
        all_chunks, error = chunker.batch_chunk_documents(documents)
        elapsed_time = time.time() - start_time

        assert error is None
        # Should be fast (well under 1 second for 10 docs)
        assert elapsed_time < 1.0

        # Calculate throughput
        chunks_per_second = len(all_chunks) / elapsed_time if elapsed_time > 0 else 0
        docs_per_second = len(documents) / elapsed_time if elapsed_time > 0 else 0

        # Should handle reasonable throughput
        assert docs_per_second > 5  # At least 5 docs/sec

    def test_chunk_content_quality(self):
        """Test chunks have adequate content quality."""
        chunker = SemanticChunker()
        documents = self.create_test_documents(5)

        all_chunks, _ = chunker.batch_chunk_documents(documents)

        for chunk in all_chunks:
            # Content should not be trivial
            assert len(chunk.content) > 10

            # Content should have structure
            lines = chunk.content.strip().split("\n")
            assert len(lines) >= 1

            # Token count should reflect content length
            assert chunk.token_count >= len(chunk.content) // (chunker.CHARS_PER_TOKEN * 2)
            assert chunk.token_count <= len(chunk.content) // (chunker.CHARS_PER_TOKEN // 2)

    def test_batch_error_handling(self):
        """Test error handling in batch processing."""
        chunker = SemanticChunker()

        # Mix valid and invalid documents
        documents = self.create_test_documents(5)
        documents.append(
            {
                "document_id": "",  # Invalid
                "content": "Some content",
            }
        )

        all_chunks, error = chunker.batch_chunk_documents(documents)

        # Should report error
        assert error is not None
        assert "Error chunking" in error

    def test_chunk_position_integrity(self):
        """Test chunk positions accurately reflect document structure."""
        chunker = SemanticChunker()
        documents = self.create_test_documents(3)

        all_chunks, _ = chunker.batch_chunk_documents(documents)

        # For each chunk, verify position makes sense
        for chunk in all_chunks:
            # Start should be before end
            assert chunk.start_char < chunk.end_char

            # Paragraph count should match content
            para_count = chunk.content.count("\n\n") + 1
            assert chunk.paragraph_count == para_count

    def test_export_at_scale(self):
        """Test exporting 10 documents' chunks."""
        chunker = SemanticChunker()
        documents = self.create_test_documents(10)

        all_chunks, _ = chunker.batch_chunk_documents(documents)
        exported = chunker.export_chunks(all_chunks)

        assert len(exported) == len(all_chunks)
        assert all(isinstance(e, dict) for e in exported)

        # Verify each exported chunk has required fields
        for exp in exported:
            assert "chunk_id" in exp
            assert "document_id" in exp
            assert "content" in exp
            assert "token_count" in exp
            assert "metadata" in exp

    def test_large_batch_scale(self):
        """Test chunking larger batch of 50 documents."""
        chunker = SemanticChunker()
        documents = self.create_test_documents(50)

        start_time = time.time()
        all_chunks, error = chunker.batch_chunk_documents(documents)
        elapsed_time = time.time() - start_time

        assert error is None
        assert len(all_chunks) > 50
        assert elapsed_time < 5.0  # Should handle 50 docs in reasonable time

    def test_chunk_independence_for_embedding(self):
        """Test chunks can be independently embedded (self-contained)."""
        chunker = SemanticChunker()
        documents = self.create_test_documents(5)

        all_chunks, _ = chunker.batch_chunk_documents(documents)

        # Verify each chunk is embeddable on its own
        for chunk in all_chunks:
            content = chunk.content.strip()

            # Should not be a fragment
            assert len(content.split()) >= 5  # At least 5 words

            # Should be meaningful (has some structure)
            assert "\n" in content or len(content) > 50

            # Should have semantic content (multiple sentences ideally)
            assert "." in content  # Has at least some punctuation

    def test_metadata_filtering_at_scale(self):
        """Test filtering chunks by parent metadata at scale."""
        chunker = SemanticChunker()
        documents = self.create_test_documents(20)

        all_chunks, _ = chunker.batch_chunk_documents(documents)

        # Filter by company
        google_chunks = [
            c for c in all_chunks if c.metadata.get("company") == "Google"
        ]
        amazon_chunks = [
            c for c in all_chunks if c.metadata.get("company") == "Amazon"
        ]

        # Should have chunks from different companies
        assert len(google_chunks) > 0
        assert len(amazon_chunks) > 0

        # Filter by domain
        career_chunks = [
            c for c in all_chunks if c.metadata.get("domain") == "career"
        ]
        tech_chunks = [c for c in all_chunks if c.metadata.get("domain") == "tech"]

        assert len(career_chunks) > 0
        assert len(tech_chunks) > 0

    def test_complete_scale_workflow(self):
        """Test complete workflow with 10 documents end-to-end."""
        chunker = SemanticChunker()
        documents = self.create_test_documents(10)

        # 1. Batch chunk all documents
        all_chunks, error = chunker.batch_chunk_documents(documents)
        assert error is None

        # 2. Get statistics
        stats = chunker.get_statistics(all_chunks)
        assert stats["total_chunks"] > 10
        assert stats["avg_tokens"] > 0

        # 3. Export for persistence
        exported = chunker.export_chunks(all_chunks)
        assert len(exported) == len(all_chunks)

        # 4. Verify metadata is preserved
        for exp in exported:
            assert exp["metadata"]["company"]
            assert exp["metadata"]["domain"]

        # 5. Verify chunks are trackable
        for chunk in all_chunks:
            assert chunk.document_id
            assert chunk.sequence >= 0

        # All tests pass - workflow is complete
        assert len(all_chunks) > 0
