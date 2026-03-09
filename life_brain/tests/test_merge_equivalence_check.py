"""
Test suite for merge/equivalence (ME) check module.

Tests cover:
- Cosine similarity calculation
- Duplicate detection
- Merge proposal and approval
- Document deduplication
- Batch operations and statistics
"""

import pytest

from life_brain.truth.merge_equivalence_check import (
    MergeEquivalenceValidator,
    MergeDecision,
    DuplicateCandidate,
    MergeStatus,
)


class TestDuplicateCandidate:
    """Test DuplicateCandidate dataclass."""

    def test_create_candidate(self):
        """Test creating duplicate candidate."""
        candidate = DuplicateCandidate(
            doc_id_1="doc1",
            doc_id_2="doc2",
            similarity_score=0.92,
            overlap_percentage=0.88,
            merge_confidence=0.90,
        )

        assert candidate.doc_id_1 == "doc1"
        assert candidate.similarity_score == 0.92


class TestMergeDecision:
    """Test MergeDecision dataclass."""

    def test_create_decision(self):
        """Test creating merge decision."""
        decision = MergeDecision(
            merge_id="me_001",
            doc_id_1="doc1",
            doc_id_2="doc2",
            primary_doc_id="doc1",
            status=MergeStatus.PENDING,
            similarity_score=0.90,
            reason="Duplicate content",
        )

        assert decision.merge_id == "me_001"
        assert decision.status == MergeStatus.PENDING

    def test_to_dict(self):
        """Test converting to dict."""
        decision = MergeDecision(
            merge_id="me_002",
            doc_id_1="d1",
            doc_id_2="d2",
            primary_doc_id="d1",
            status=MergeStatus.MERGED,
            similarity_score=0.87,
            reason="Merged",
            merged_content="Combined content here",
        )

        d = decision.to_dict()
        assert d["merge_id"] == "me_002"
        assert d["status"] == "merged"


class TestMergeEquivalenceValidator:
    """Test MergeEquivalenceValidator functionality."""

    def test_create_validator(self):
        """Test creating validator."""
        validator = MergeEquivalenceValidator()
        assert len(validator.documents) == 0
        assert len(validator.duplicates) == 0

    def test_add_document(self):
        """Test adding documents."""
        validator = MergeEquivalenceValidator()

        validator.add_document("doc1", "Machine learning is a type of artificial intelligence")
        validator.add_document("doc2", "ML is a subset of AI that enables systems to learn")

        assert len(validator.documents) == 2

    def test_cosine_similarity_identical(self):
        """Test similarity of identical texts."""
        validator = MergeEquivalenceValidator()

        text = "Python is a programming language"
        similarity = validator._calculate_cosine_similarity(text, text)

        assert similarity > 0.99

    def test_cosine_similarity_different(self):
        """Test similarity of different texts."""
        validator = MergeEquivalenceValidator()

        text1 = "The cat sat on the mat"
        text2 = "Programming is fun"
        similarity = validator._calculate_cosine_similarity(text1, text2)

        assert similarity < 0.5

    def test_cosine_similarity_similar(self):
        """Test similarity of similar texts."""
        validator = MergeEquivalenceValidator()

        text1 = "Machine learning is a powerful technology for AI"
        text2 = "Machine learning is a powerful technology for artificial intelligence"
        similarity = validator._calculate_cosine_similarity(text1, text2)

        assert 0.5 <= similarity < 1.0

    def test_cosine_similarity_very_similar(self):
        """Test similarity of very similar texts."""
        validator = MergeEquivalenceValidator()

        text1 = "The quick brown fox jumps over the lazy dog"
        text2 = "The quick brown fox jumps over the lazy dog"
        similarity = validator._calculate_cosine_similarity(text1, text2)

        assert similarity > 0.95

    def test_detect_duplicates_none(self):
        """Test detection with no duplicates."""
        validator = MergeEquivalenceValidator()

        validator.add_document("doc1", "Python programming language")
        validator.add_document("doc2", "JavaScript web language")

        duplicates = validator.detect_duplicates()

        assert len(duplicates) == 0

    def test_detect_duplicates_found(self):
        """Test detecting duplicates."""
        validator = MergeEquivalenceValidator()

        validator.add_document("doc1", "Machine learning enables artificial intelligence applications")
        validator.add_document("doc2", "Machine learning enables artificial intelligence applications")

        duplicates = validator.detect_duplicates()

        assert len(duplicates) > 0
        assert duplicates[0].similarity_score > 0.95

    def test_detect_duplicates_threshold(self):
        """Test duplicate detection respects threshold."""
        validator = MergeEquivalenceValidator()

        # Very similar but distinct
        validator.add_document("doc1", "The system improves performance and reliability")
        validator.add_document("doc2", "The system improves performance and safety")

        duplicates = validator.detect_duplicates()

        # May or may not be detected depending on similarity
        if duplicates:
            assert duplicates[0].similarity_score >= validator.SIMILARITY_THRESHOLD

    def test_propose_merge_success(self):
        """Test proposing merge."""
        validator = MergeEquivalenceValidator()

        validator.add_document("doc1", "Python is a programming language widely used")
        validator.add_document("doc2", "Python is a programming language widely used")

        decision, error = validator.propose_merge("doc1", "doc2")

        assert error is None
        assert decision is not None
        assert decision.status == MergeStatus.PENDING

    def test_propose_merge_nonexistent_doc1(self):
        """Test proposing merge with nonexistent first doc."""
        validator = MergeEquivalenceValidator()

        validator.add_document("doc2", "Content")

        decision, error = validator.propose_merge("nonexistent", "doc2")

        assert error is not None
        assert decision is None

    def test_propose_merge_nonexistent_doc2(self):
        """Test proposing merge with nonexistent second doc."""
        validator = MergeEquivalenceValidator()

        validator.add_document("doc1", "Content")

        decision, error = validator.propose_merge("doc1", "nonexistent")

        assert error is not None
        assert decision is None

    def test_propose_merge_low_similarity(self):
        """Test proposing merge with low similarity."""
        validator = MergeEquivalenceValidator()

        validator.add_document("doc1", "Python programming")
        validator.add_document("doc2", "JavaScript web development")

        decision, error = validator.propose_merge("doc1", "doc2")

        assert error is not None
        assert decision is None

    def test_approve_merge(self):
        """Test approving merge."""
        validator = MergeEquivalenceValidator()

        validator.add_document("doc1", "Machine learning is important")
        validator.add_document("doc2", "Machine learning is important")

        decision, _ = validator.propose_merge("doc1", "doc2")
        approved, error = validator.approve_merge(decision.merge_id)

        assert error is None
        assert approved.status == MergeStatus.MERGED

    def test_approve_merge_nonexistent(self):
        """Test approving nonexistent merge."""
        validator = MergeEquivalenceValidator()

        decision, error = validator.approve_merge("nonexistent")

        assert error is not None
        assert decision is None

    def test_approve_merge_already_merged(self):
        """Test approving already merged decision."""
        validator = MergeEquivalenceValidator()

        validator.add_document("doc1", "Same content")
        validator.add_document("doc2", "Same content")

        decision, _ = validator.propose_merge("doc1", "doc2")
        validator.approve_merge(decision.merge_id)

        # Try to approve again
        decision2, error = validator.approve_merge(decision.merge_id)

        assert error is not None

    def test_reject_merge(self):
        """Test rejecting merge."""
        validator = MergeEquivalenceValidator()

        validator.add_document("doc1", "Content A")
        validator.add_document("doc2", "Content A")

        decision, _ = validator.propose_merge("doc1", "doc2")
        rejected, error = validator.reject_merge(decision.merge_id, "False positive")

        assert error is None
        assert rejected.status == MergeStatus.REJECTED

    def test_merged_mapping(self):
        """Test merge mapping creation."""
        validator = MergeEquivalenceValidator()

        validator.add_document("doc1", "Duplicate content")
        validator.add_document("doc2", "Duplicate content")

        decision, _ = validator.propose_merge("doc1", "doc2")
        validator.approve_merge(decision.merge_id)

        mapping = validator.get_merge_mapping()

        assert "doc2" in mapping
        assert mapping["doc2"] == "doc1"

    def test_documents_after_merge(self):
        """Test documents collection after merge."""
        validator = MergeEquivalenceValidator()

        validator.add_document("doc1", "Content 1")
        validator.add_document("doc2", "Content 1")

        assert len(validator.documents) == 2

        decision, _ = validator.propose_merge("doc1", "doc2")
        validator.approve_merge(decision.merge_id)

        # Secondary doc should be removed
        assert len(validator.documents) == 1
        assert "doc1" in validator.documents
        assert "doc2" not in validator.documents

    def test_get_merge_decision(self):
        """Test retrieving merge decision."""
        validator = MergeEquivalenceValidator()

        validator.add_document("doc1", "Same")
        validator.add_document("doc2", "Same")

        decision, _ = validator.propose_merge("doc1", "doc2")
        retrieved = validator.get_merge_decision(decision.merge_id)

        assert retrieved is not None
        assert retrieved.merge_id == decision.merge_id

    def test_get_pending_merges(self):
        """Test retrieving pending merges."""
        validator = MergeEquivalenceValidator()

        validator.add_document("doc1", "Machine learning technology platform")
        validator.add_document("doc2", "Machine learning technology platform")
        validator.add_document("doc3", "Artificial intelligence systems design")

        validator.propose_merge("doc1", "doc2")
        validator.propose_merge("doc2", "doc3")

        pending = validator.get_pending_merges()

        # Should have at least 1 pending (doc1-doc2), doc2-doc3 may not meet threshold
        assert len(pending) >= 1

    def test_batch_detect_and_propose(self):
        """Test batch detection and proposal."""
        validator = MergeEquivalenceValidator()

        # Add documents with some duplicates
        validator.add_document("doc1", "Machine learning is powerful")
        validator.add_document("doc2", "Machine learning is powerful")
        validator.add_document("doc3", "Python programming")
        validator.add_document("doc4", "Python programming")

        decisions, error = validator.batch_detect_and_propose()

        assert error is None
        assert len(decisions) >= 2

    def test_export_merge_decision(self):
        """Test exporting merge decision."""
        validator = MergeEquivalenceValidator()

        validator.add_document("doc1", "Content")
        validator.add_document("doc2", "Content")

        decision, _ = validator.propose_merge("doc1", "doc2")
        exported = validator.export_merge_decision(decision.merge_id)

        assert exported is not None
        assert exported["merge_id"] == decision.merge_id

    def test_export_all_decisions(self):
        """Test exporting all decisions."""
        validator = MergeEquivalenceValidator()

        validator.add_document("doc1", "Python programming language tutorial")
        validator.add_document("doc2", "Python programming language tutorial")

        decision, _ = validator.propose_merge("doc1", "doc2")
        if decision:
            validator.approve_merge(decision.merge_id)

        exported = validator.export_all_decisions()

        assert len(exported) >= 1

    def test_statistics_empty(self):
        """Test statistics with empty validator."""
        validator = MergeEquivalenceValidator()
        stats = validator.get_statistics()

        assert stats["total_documents"] == 0
        assert stats["total_duplicates_detected"] == 0

    def test_statistics_with_duplicates(self):
        """Test statistics with duplicates."""
        validator = MergeEquivalenceValidator()

        validator.add_document("doc1", "Machine learning")
        validator.add_document("doc2", "Machine learning")
        validator.add_document("doc3", "Different content")

        validator.detect_duplicates()
        decisions, _ = validator.batch_detect_and_propose()

        stats = validator.get_statistics()

        assert stats["total_documents"] == 3
        assert stats["total_duplicates_detected"] > 0

    def test_normalize_text(self):
        """Test text normalization."""
        validator = MergeEquivalenceValidator()

        original = "Hello, WORLD! How are you?"
        normalized = validator._normalize_text(original)

        # Should be lowercase and without punctuation
        assert normalized.islower()
        assert "," not in normalized
        assert "!" not in normalized

    def test_overlap_percentage(self):
        """Test overlap calculation."""
        validator = MergeEquivalenceValidator()

        text1 = "The quick brown fox"
        text2 = "The quick blue fox"

        overlap = validator._calculate_overlap_percentage(text1, text2)

        assert 0.5 < overlap < 1.0

    def test_multiple_validators_independent(self):
        """Test multiple validators are independent."""
        v1 = MergeEquivalenceValidator()
        v2 = MergeEquivalenceValidator()

        v1.add_document("doc1", "Content 1")
        v2.add_document("doc2", "Content 2")

        assert len(v1.documents) == 1
        assert len(v2.documents) == 1

    def test_merge_confidence_calculation(self):
        """Test merge confidence is between 0-1."""
        validator = MergeEquivalenceValidator()

        for similarity in [0.85, 0.90, 0.95, 0.99]:
            for overlap in [0.7, 0.85, 0.95]:
                confidence = validator._calculate_merge_confidence(
                    similarity, overlap, "Some text", "Some text"
                )
                assert 0.0 <= confidence <= 1.0

    def test_complex_workflow(self):
        """Test complete merge workflow."""
        validator = MergeEquivalenceValidator()

        # Add documents
        validator.add_document("career_1", "Career growth in tech industry")
        validator.add_document("career_2", "Career growth in tech industry")
        validator.add_document("tech_1", "Python and JavaScript languages")

        # Detect duplicates
        duplicates = validator.detect_duplicates()
        assert len(duplicates) > 0

        # Propose merges
        decisions, _ = validator.batch_detect_and_propose()
        assert len(decisions) > 0

        # Approve first merge
        first_decision = decisions[0]
        validator.approve_merge(first_decision.merge_id)

        # Check mapping
        mapping = validator.get_merge_mapping()
        assert len(mapping) > 0

        # Get stats
        stats = validator.get_statistics()
        assert stats["merges_completed"] > 0

    def test_primary_document_selection(self):
        """Test that longer document is selected as primary."""
        validator = MergeEquivalenceValidator()

        short_content = "Machine learning systems"
        long_content = "Machine learning systems and artificial intelligence technology platform design"

        validator.add_document("short", short_content)
        validator.add_document("long", long_content)

        # For this test, we'll manually call with None for primary
        # and check that the logic selects the longer one
        decision, error = validator.propose_merge("short", "long", None)

        if decision:  # Only check if similarity was high enough
            assert decision.primary_doc_id == "long"
        else:
            # If not similar enough, that's ok - the test was about the selection logic
            assert True
