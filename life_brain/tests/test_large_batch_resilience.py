"""
Large-scale batch testing with 1000+ documents - resilience and progress reporting.

Tests cover:
- Processing 1000+ documents
- Progress tracking at scale
- Resilience and retry handling
- Throughput metrics
- Error handling and deadletter queue
- End-to-end workflow
"""

import pytest
import time
from typing import Dict, List, Any

from life_brain.core.semantic_chunking import SemanticChunker
from life_brain.core.batch_metrics import BatchProgressTracker, BatchReporter


class TestLargeBatchProcessing:
    """Test processing large batches (1000+ documents)."""

    @staticmethod
    def create_large_batch(document_count: int = 1000) -> List[Dict[str, Any]]:
        """Create a large batch of documents for testing.

        Args:
            document_count: Number of documents to create

        Returns:
            List of document dictionaries
        """
        companies = ["Google", "Amazon", "Microsoft", "Apple", "Meta", "Netflix", "Tesla", "Uber"]
        domains = ["career", "tech", "health", "relationships", "finance"]
        projects = ["Project A", "Project B", "Project C", "Project D", "Project E"]

        documents = []
        for i in range(document_count):
            company = companies[i % len(companies)]
            domain = domains[i % len(domains)]
            project = projects[i % len(projects)]

            # Create document with multiple sections
            sections = []
            for sec in range(3):
                sections.append(
                    f"""Section {sec}: Details

This is section {sec} of document {i}. Content from {company} working on {project} in {domain}.

Key points include various aspects. Implementation details are provided. Results show success metrics.

Additional information relevant to context. Quality metrics indicate good performance. Future plans include expansion."""
                )

            content = "\n\n".join(sections)

            documents.append(
                {
                    "document_id": f"large_doc_{i:05d}_{company.lower()}",
                    "content": content,
                    "metadata": {
                        "company": company,
                        "domain": domain,
                        "project": project,
                        "batch_index": i,
                    },
                }
            )

        return documents

    def test_chunk_1000_documents(self):
        """Test chunking 1000 documents."""
        chunker = SemanticChunker()
        documents = self.create_large_batch(1000)

        start_time = time.time()
        all_chunks, error = chunker.batch_chunk_documents(documents)
        elapsed = time.time() - start_time

        assert error is None
        assert len(all_chunks) >= 1000  # At least 1 chunk per doc
        assert elapsed < 30  # Should complete in reasonable time

    def test_progress_tracking_large_batch(self):
        """Test progress tracking during large batch processing."""
        tracker = BatchProgressTracker("large_batch_001", total=100)

        # Simulate processing
        for i in range(100):
            if i % 3 == 0:
                tracker.record_success()
            elif i % 3 == 1:
                tracker.record_retry_scheduled("TemporaryError")
            else:
                tracker.record_failed_first_try("ValidationError")

        batch = tracker.complete()

        assert batch.successful > 0
        assert batch.in_retry_queue > 0
        assert batch.failed_first_try > 0
        assert batch.total_documents == 100
        assert batch.duration_seconds > 0

    def test_resilience_retry_handling(self):
        """Test retry queue and deadletter handling."""
        tracker = BatchProgressTracker("resilience_test", total=50)

        # Simulate errors and retries
        for i in range(20):
            tracker.record_failed_first_try("TemporaryError")

        for i in range(15):
            tracker.record_retry_scheduled("ConflictError")

        for i in range(10):
            tracker.record_success()

        for i in range(5):
            tracker.record_deadlettered("PermanentError")

        batch = tracker.complete()

        assert batch.failed_first_try == 20
        assert batch.in_retry_queue == 15
        assert batch.successful == 10
        assert batch.deadlettered == 5
        assert batch.total_documents == 50

    def test_progress_reports_1000_documents(self):
        """Test progress reporting for 1000 documents."""
        tracker = BatchProgressTracker("scale_test_1000", total=1000)

        # Simulate processing
        success_count = 950
        retry_count = 30
        deadletter_count = 20

        for i in range(success_count):
            tracker.record_success()

        for i in range(retry_count):
            tracker.record_retry_scheduled("TemporaryError")

        for i in range(deadletter_count):
            tracker.record_deadlettered("ValidationError")

        batch = tracker.complete()

        assert batch.successful == success_count
        assert batch.in_retry_queue == retry_count
        assert batch.deadlettered == deadletter_count

        # Verify statistics
        assert abs(batch.get_success_rate() - 95.0) < 0.1
        assert batch.duration_seconds > 0

    def test_throughput_metrics_large_batch(self):
        """Test throughput calculations on large batch."""
        tracker = BatchProgressTracker("throughput_test", total=10000)

        # Simulate processing 10000 docs
        for i in range(10000):
            tracker.record_success()

        batch = tracker.complete()

        throughput = batch.get_throughput()
        assert throughput > 0  # Should have some throughput

    def test_error_aggregation_large_batch(self):
        """Test error aggregation across many error types."""
        tracker = BatchProgressTracker("error_agg", total=200)

        error_types = [
            "ValidationError",
            "ConflictError",
            "TemporaryError",
            "FormatError",
            "DuplicateError",
        ]

        # Distribute errors
        for i, error_type in enumerate(error_types * 10):  # 50 of each
            if i % 2 == 0:
                tracker.record_deadlettered(error_type)
            else:
                tracker.record_retry_scheduled(error_type)

        batch = tracker.complete()

        # Verify all error types are tracked
        for error_type in error_types:
            assert error_type in batch.errors_by_type
            assert batch.errors_by_type[error_type] > 0

    def test_batch_reporter_generates_report(self):
        """Test report generation for large batch."""
        tracker = BatchProgressTracker("report_test", total=500)

        # Process batch
        for i in range(475):
            tracker.record_success()

        for i in range(15):
            tracker.record_deadlettered("ValidationError")

        for i in range(10):
            tracker.record_retry_scheduled("ConflictError")

        batch = tracker.complete()

        # Generate text report
        report = BatchReporter.format_text_report(batch)
        assert "BATCH INGESTION REPORT" in report
        assert "500" in report  # Total docs
        assert "475" in report  # Successful
        assert "Deadlettered" in report

        # Generate JSON report
        json_report = BatchReporter.export_json(batch)
        assert "batch_id" in json_report
        assert "successful" in json_report

    def test_chunk_then_track_workflow(self):
        """Test end-to-end workflow: chunk documents and track progress."""
        chunker = SemanticChunker()
        documents = self.create_large_batch(100)  # Smaller for speed

        # Create progress tracker
        tracker = BatchProgressTracker("e2e_workflow", total=len(documents))

        # Process documents
        all_chunks, error = chunker.batch_chunk_documents(documents)
        assert error is None

        # Simulate tracking
        for i, doc in enumerate(documents):
            if i % 50 == 0:
                tracker.record_success()
            elif i % 50 == 25:
                tracker.record_retry_scheduled("ChunkingError")
            else:
                tracker.record_success()

        batch = tracker.complete()

        # Verify workflow
        assert batch.successful > 0
        assert len(all_chunks) >= len(documents)  # At least 1 chunk per doc
        assert batch.total_documents == len(documents)

    def test_batch_with_metadata_filtering(self):
        """Test filtering chunks by company in large batch."""
        chunker = SemanticChunker()
        documents = self.create_large_batch(200)

        all_chunks, _ = chunker.batch_chunk_documents(documents)

        # Filter by company
        google_chunks = [c for c in all_chunks if c.metadata.get("company") == "Google"]
        amazon_chunks = [c for c in all_chunks if c.metadata.get("company") == "Amazon"]

        # Verify filtering works at scale
        assert len(google_chunks) > 0
        assert len(amazon_chunks) > 0
        assert all(c.metadata["company"] == "Google" for c in google_chunks)
        assert all(c.metadata["company"] == "Amazon" for c in amazon_chunks)

    def test_batch_statistics_1000_docs(self):
        """Test statistics generation on 1000+ documents."""
        chunker = SemanticChunker()
        documents = self.create_large_batch(1000)

        all_chunks, _ = chunker.batch_chunk_documents(documents)
        stats = chunker.get_statistics(all_chunks)

        assert stats["total_chunks"] >= 1000
        assert stats["avg_tokens"] > 0
        assert stats["total_content_chars"] > 0
        assert "max_tokens" in stats
        assert "min_tokens" in stats

    def test_resilience_with_mixed_errors(self):
        """Test resilience with multiple error types."""
        tracker = BatchProgressTracker("mixed_errors", total=1000)

        # Simulate realistic error distribution
        success = 920  # 92% success
        temporary = 50  # 5% temporary errors (will retry)
        permanent = 20  # 2% permanent errors (deadletter)
        validation = 10  # 1% validation errors

        for i in range(success):
            tracker.record_success()

        for i in range(temporary):
            tracker.record_retry_scheduled("TemporaryError")

        for i in range(permanent):
            tracker.record_deadlettered("PermanentError")

        for i in range(validation):
            tracker.record_failed_first_try("ValidationError")

        batch = tracker.complete()

        # Verify distribution
        assert batch.successful == success
        assert batch.in_retry_queue == temporary
        assert batch.deadlettered == permanent
        assert batch.failed_first_try == validation
        assert abs(batch.get_success_rate() - 92.0) < 0.1

    def test_parallel_batch_simulation(self):
        """Test tracking multiple batches in parallel."""
        batches = [
            BatchProgressTracker(f"batch_{i}", total=100) for i in range(5)
        ]

        # Process each batch
        for batch_tracker in batches:
            for i in range(100):
                if i % 5 == 0:
                    batch_tracker.record_deadlettered("Error")
                else:
                    batch_tracker.record_success()

        # Complete all
        completed_batches = [bt.complete() for bt in batches]

        # Verify all completed
        assert len(completed_batches) == 5
        for batch in completed_batches:
            assert batch.total_documents == 100
            assert batch.successful > 0
            assert batch.deadlettered > 0

    def test_large_batch_chunk_independence(self):
        """Test chunk independence at large scale."""
        chunker = SemanticChunker()
        documents = self.create_large_batch(500)

        all_chunks, _ = chunker.batch_chunk_documents(documents)

        # Verify chunks are independent units
        for chunk in all_chunks:
            assert chunk.chunk_id  # Has ID
            assert chunk.document_id  # References parent
            assert chunk.content  # Has content
            assert chunk.token_count > 0  # Can be embedded
            assert chunk.metadata  # Has metadata

    def test_complete_large_batch_workflow(self):
        """Test complete workflow with large batch end-to-end."""
        # 1. Create large batch
        chunker = SemanticChunker()
        documents = self.create_large_batch(200)

        # 2. Create progress tracker
        tracker = BatchProgressTracker("complete_workflow_200docs", total=len(documents))

        # 3. Chunk documents
        start_time = time.time()
        all_chunks, error = chunker.batch_chunk_documents(documents)
        chunking_time = time.time() - start_time

        assert error is None

        # 4. Track progress (simulate)
        successful = 0
        for i in range(len(documents)):
            if i % 10 == 0:
                tracker.record_deadlettered("SampleError")
            elif i % 5 == 0:
                tracker.record_retry_scheduled("TemporaryError")
            else:
                tracker.record_success()
                successful += 1

        batch = tracker.complete()

        # 5. Verify statistics
        assert batch.total_documents == len(documents)
        assert batch.successful > 0
        assert batch.deadlettered > 0
        assert batch.in_retry_queue > 0

        # 6. Get statistics
        stats = chunker.get_statistics(all_chunks)
        assert stats["total_chunks"] >= len(documents)  # At least 1 chunk per doc

        # 7. Generate report
        report = BatchReporter.format_text_report(batch)
        assert "BATCH INGESTION REPORT" in report
        assert str(len(documents)) in report

        # 8. Verify timing
        assert chunking_time < 30  # Should be reasonably fast

        # All checks pass
        assert len(all_chunks) > 0
        assert batch.duration_seconds > 0
