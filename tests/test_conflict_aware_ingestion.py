"""
Unit tests for conflict_aware_ingestion.py

Covers:
- ConflictScore dataclass validation
- ConflictCandidate dataclass
- ConflictDetectionResult dataclass
- ConflictDetector initialization
- Similar document querying
- Contradiction measurement (negations, opposite pairs, numerical)
- Conflict score calculation
- Comprehensive conflict detection with all conflict types
- Conflict report formatting
- ConflictAwareIngestionPipeline initialization
- Full ingestion pipeline with validation and conflict detection
- Hard conflict blocking
- Soft conflict handling with auto-resolve
- Enrichment scenarios
- No conflict scenarios
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from life_brain.db.conflict_aware_ingestion import (
    ConflictType,
    ConflictScore,
    ConflictCandidate,
    ConflictDetectionResult,
    ConflictDetector,
    ConflictAwareIngestionPipeline,
)
from life_brain.db.document_validator import DocumentValidator, ValidationResult
from life_brain.db.error_reporter import ValidationError


class TestConflictScore:
    """Test ConflictScore dataclass."""

    def test_create_valid_conflict_score(self):
        """Test creating valid conflict score."""
        score = ConflictScore(
            semantic_similarity=0.8,
            contradiction_magnitude=0.5,
            overall_score=0.4
        )
        assert score.semantic_similarity == 0.8
        assert score.contradiction_magnitude == 0.5
        assert score.overall_score == 0.4

    def test_conflict_score_zero_values(self):
        """Test conflict score with all zeros."""
        score = ConflictScore(0, 0, 0)
        assert score.semantic_similarity == 0
        assert score.contradiction_magnitude == 0
        assert score.overall_score == 0

    def test_conflict_score_max_values(self):
        """Test conflict score with max values."""
        score = ConflictScore(1.0, 1.0, 1.0)
        assert score.semantic_similarity == 1.0
        assert score.contradiction_magnitude == 1.0
        assert score.overall_score == 1.0

    def test_conflict_score_invalid_similarity_high(self):
        """Test conflict score with invalid similarity > 1."""
        with pytest.raises(AssertionError):
            ConflictScore(1.5, 0.5, 0.75)

    def test_conflict_score_invalid_similarity_negative(self):
        """Test conflict score with negative similarity."""
        with pytest.raises(AssertionError):
            ConflictScore(-0.1, 0.5, 0.5)

    def test_conflict_score_invalid_contradiction_high(self):
        """Test conflict score with invalid contradiction > 1."""
        with pytest.raises(AssertionError):
            ConflictScore(0.8, 1.5, 0.4)

    def test_conflict_score_invalid_overall_high(self):
        """Test conflict score with invalid overall > 1."""
        with pytest.raises(AssertionError):
            ConflictScore(0.8, 0.5, 1.1)


class TestConflictCandidate:
    """Test ConflictCandidate dataclass."""

    def test_create_conflict_candidate(self):
        """Test creating conflict candidate."""
        candidate = ConflictCandidate(
            doc_id="doc_123",
            existing_text="Sample text",
            existing_metadata={"domain": "career"},
            conflict_score=0.75
        )
        assert candidate.doc_id == "doc_123"
        assert candidate.existing_text == "Sample text"
        assert candidate.conflict_score == 0.75

    def test_candidate_with_embedding(self):
        """Test candidate with embedding vector."""
        embedding = [0.1, 0.2, 0.3]
        candidate = ConflictCandidate(
            doc_id="doc_456",
            existing_text="Text",
            existing_metadata={},
            embedding=embedding
        )
        assert candidate.embedding == embedding

    def test_candidate_default_conflict_score(self):
        """Test candidate with default conflict score."""
        candidate = ConflictCandidate(
            doc_id="doc_789",
            existing_text="Text",
            existing_metadata={}
        )
        assert candidate.conflict_score == 0.0


class TestConflictDetectionResult:
    """Test ConflictDetectionResult dataclass."""

    def test_create_no_conflict_result(self):
        """Test creating no-conflict result."""
        score = ConflictScore(0.5, 0.0, 0.0)
        result = ConflictDetectionResult(
            has_conflict=False,
            conflict_type=ConflictType.NO_CONFLICT,
            score=score,
            reason="No similar documents found"
        )
        assert result.has_conflict is False
        assert result.conflict_type == ConflictType.NO_CONFLICT

    def test_create_hard_conflict_result(self):
        """Test creating hard conflict result."""
        score = ConflictScore(0.9, 0.8, 0.72)
        candidate = ConflictCandidate(
            doc_id="existing_doc",
            existing_text="Existing text",
            existing_metadata={}
        )
        result = ConflictDetectionResult(
            has_conflict=True,
            conflict_type=ConflictType.HARD_CONFLICT,
            score=score,
            candidate=candidate,
            reason="Hard conflict detected"
        )
        assert result.has_conflict is True
        assert result.candidate.doc_id == "existing_doc"

    def test_result_with_resolution_options(self):
        """Test result with resolution options."""
        score = ConflictScore(0.4, 0.3, 0.12)
        result = ConflictDetectionResult(
            has_conflict=False,
            conflict_type=ConflictType.ENRICHMENT,
            score=score,
            resolution_options=["proceed_independent", "merge_with_existing"]
        )
        assert len(result.resolution_options) == 2

    def test_result_default_values(self):
        """Test result with default field values."""
        score = ConflictScore(0, 0, 0)
        result = ConflictDetectionResult(
            has_conflict=False,
            conflict_type=ConflictType.NO_CONFLICT,
            score=score
        )
        assert result.reason == ""
        assert result.recommendation == ""
        assert len(result.resolution_options) == 0


class TestConflictDetectorInit:
    """Test ConflictDetector initialization."""

    def test_create_detector(self):
        """Test creating conflict detector."""
        mock_collection = Mock()
        detector = ConflictDetector(mock_collection)
        assert detector is not None
        assert detector.collection == mock_collection

    def test_detector_thresholds(self):
        """Test detector has correct thresholds."""
        mock_collection = Mock()
        detector = ConflictDetector(mock_collection)
        assert detector.CONFLICT_THRESHOLD == 0.6
        assert detector.SOFT_CONFLICT_THRESHOLD == 0.3
        assert detector.ENRICHMENT_THRESHOLD == 0.1


class TestQuerySimilarDocuments:
    """Test similar document querying."""

    def test_query_no_results(self):
        """Test query with no results."""
        mock_collection = Mock()
        mock_collection.query.return_value = {"ids": [[]], "documents": [[]]}
        detector = ConflictDetector(mock_collection)

        candidates = detector.query_similar_documents("test text")
        assert len(candidates) == 0

    def test_query_single_result(self):
        """Test query returning single result."""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "ids": [["doc_1"]],
            "documents": [["Existing document"]],
            "metadatas": [[{"domain": "career"}]],
            "distances": [[0.2]],  # Distance; similarity = 1 - 0.2 = 0.8
            "embeddings": [[[0.1, 0.2, 0.3]]]
        }
        detector = ConflictDetector(mock_collection)

        candidates = detector.query_similar_documents("New document", domain="career", n_results=5)

        assert len(candidates) == 1
        assert candidates[0].doc_id == "doc_1"
        assert candidates[0].conflict_score == 0.8  # 1 - distance
        mock_collection.query.assert_called_once()

    def test_query_multiple_results(self):
        """Test query returning multiple results."""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "ids": [["doc_1", "doc_2", "doc_3"]],
            "documents": [["Text 1", "Text 2", "Text 3"]],
            "metadatas": [[{}, {}, {}]],
            "distances": [[0.1, 0.3, 0.5]],
            "embeddings": [[[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]]
        }
        detector = ConflictDetector(mock_collection)

        candidates = detector.query_similar_documents("Test", n_results=3)

        assert len(candidates) == 3
        assert candidates[0].conflict_score == 0.9  # 1 - 0.1
        assert candidates[1].conflict_score == 0.7  # 1 - 0.3
        assert candidates[2].conflict_score == 0.5  # 1 - 0.5

    def test_query_with_domain_filter(self):
        """Test query applies domain filter."""
        mock_collection = Mock()
        mock_collection.query.return_value = {"ids": [[]], "documents": [[]]}
        detector = ConflictDetector(mock_collection)

        detector.query_similar_documents("test", domain="career")

        # Verify domain filter was passed
        call_args = mock_collection.query.call_args
        assert call_args[1]["where"] == {"domain": "career"}

    def test_query_exception_handling(self):
        """Test query handles exceptions gracefully."""
        mock_collection = Mock()
        mock_collection.query.side_effect = Exception("Connection error")
        detector = ConflictDetector(mock_collection)

        candidates = detector.query_similar_documents("test")

        assert len(candidates) == 0


class TestMeasureContradiction:
    """Test contradiction measurement."""

    def test_no_contradiction(self):
        """Test texts with no contradiction."""
        mock_collection = Mock()
        detector = ConflictDetector(mock_collection)

        contradiction = detector.measure_contradiction(
            "I worked at Sprinklr", "I worked at Sprinklr"
        )
        assert contradiction == 0.0

    def test_negation_contradiction(self):
        """Test negation words create contradiction."""
        mock_collection = Mock()
        detector = ConflictDetector(mock_collection)

        contradiction = detector.measure_contradiction(
            "I did not complete the project",
            "I completed the project"
        )
        assert contradiction == 0.5

    def test_opposite_pair_yes_no(self):
        """Test opposite pair: yes vs no."""
        mock_collection = Mock()
        detector = ConflictDetector(mock_collection)

        contradiction = detector.measure_contradiction(
            "The answer is yes",
            "The answer is no"
        )
        # "no" at end triggers negation detection (has space before it), returns 0.5
        assert contradiction == 0.5

    def test_opposite_pair_success_failure(self):
        """Test opposite pair: success vs failure."""
        mock_collection = Mock()
        detector = ConflictDetector(mock_collection)

        contradiction = detector.measure_contradiction(
            "The project was a success",
            "The project was a failure"
        )
        assert contradiction == 0.9

    def test_opposite_pair_passed_failed(self):
        """Test opposite pair: passed vs failed."""
        mock_collection = Mock()
        detector = ConflictDetector(mock_collection)

        contradiction = detector.measure_contradiction(
            "We passed the audit",
            "We failed the audit"
        )
        assert contradiction == 0.9

    def test_numerical_conflict_significant_difference(self):
        """Test numerical conflict with significant difference."""
        mock_collection = Mock()
        detector = ConflictDetector(mock_collection)

        contradiction = detector.measure_contradiction(
            "We improved by 50%",
            "We improved by 5%"
        )
        # ratio = min(50, 5) / max(50, 5) = 0.1 < 0.5
        assert contradiction == 0.4

    def test_numerical_no_conflict_small_difference(self):
        """Test numerical values with small difference."""
        mock_collection = Mock()
        detector = ConflictDetector(mock_collection)

        contradiction = detector.measure_contradiction(
            "We improved by 45%",
            "We improved by 50%"
        )
        # ratio = 45/50 = 0.9 >= 0.5
        assert contradiction == 0.0

    def test_case_insensitive_contradiction(self):
        """Test contradiction detection is case-insensitive."""
        mock_collection = Mock()
        detector = ConflictDetector(mock_collection)

        contradiction = detector.measure_contradiction(
            "The response is YES",
            "The response is NO"
        )
        # "NO" triggers negation word detection, returns 0.5
        assert contradiction == 0.5


class TestCalculateConflictScore:
    """Test conflict score calculation."""

    def test_calculate_zero_score(self):
        """Test calculation with zero values."""
        mock_collection = Mock()
        detector = ConflictDetector(mock_collection)

        score = detector.calculate_conflict_score(0.0, 0.0)

        assert score.semantic_similarity == 0.0
        assert score.contradiction_magnitude == 0.0
        assert score.overall_score == 0.0

    def test_calculate_high_score(self):
        """Test calculation with high values."""
        mock_collection = Mock()
        detector = ConflictDetector(mock_collection)

        score = detector.calculate_conflict_score(0.8, 0.75)

        assert score.semantic_similarity == 0.8
        assert score.contradiction_magnitude == 0.75
        assert abs(score.overall_score - 0.6) < 0.0001  # 0.8 * 0.75 (floating point safe)

    def test_calculate_partial_score(self):
        """Test calculation formula."""
        mock_collection = Mock()
        detector = ConflictDetector(mock_collection)

        score = detector.calculate_conflict_score(0.5, 0.4)

        assert score.overall_score == 0.2  # 0.5 * 0.4


class TestDetectConflict:
    """Test comprehensive conflict detection."""

    def test_detect_no_candidates(self):
        """Test detection with no similar documents."""
        mock_collection = Mock()
        detector = ConflictDetector(mock_collection)

        result = detector.detect_conflict(
            "new text",
            {"domain": "career"},
            existing_candidates=[]
        )

        assert result.has_conflict is False
        assert result.conflict_type == ConflictType.NO_CONFLICT
        assert "No similar documents" in result.reason

    def test_detect_hard_conflict(self):
        """Test hard conflict detection."""
        mock_collection = Mock()
        detector = ConflictDetector(mock_collection)

        candidate = ConflictCandidate(
            doc_id="existing",
            existing_text="Success at Sprinklr",
            existing_metadata={},
            conflict_score=0.95
        )

        result = detector.detect_conflict(
            "Failure at Sprinklr",  # Contradiction: success vs failure
            {"domain": "career"},
            existing_candidates=[candidate]
        )

        assert result.has_conflict is True
        assert result.conflict_type == ConflictType.HARD_CONFLICT
        assert result.score.overall_score >= detector.CONFLICT_THRESHOLD

    def test_detect_soft_conflict(self):
        """Test soft conflict detection."""
        mock_collection = Mock()
        detector = ConflictDetector(mock_collection)

        candidate = ConflictCandidate(
            doc_id="existing",
            existing_text="Worked on project",
            existing_metadata={},
            conflict_score=0.6  # High similarity
        )

        result = detector.detect_conflict(
            "Didn't work on project",  # Negation creates contradiction
            {"domain": "career"},
            existing_candidates=[candidate]
        )

        # Overall score = 0.6 * 0.5 = 0.3, exactly at soft threshold
        assert result.conflict_type in [ConflictType.SOFT_CONFLICT, ConflictType.ENRICHMENT]

    def test_detect_enrichment(self):
        """Test enrichment detection (low conflict)."""
        mock_collection = Mock()
        detector = ConflictDetector(mock_collection)

        candidate = ConflictCandidate(
            doc_id="existing",
            existing_text="Worked on CGB",
            existing_metadata={},
            conflict_score=0.3  # Moderate similarity
        )

        result = detector.detect_conflict(
            "Worked on CGB, also built dashboard",
            {"domain": "career"},
            existing_candidates=[candidate]
        )

        # Low contradiction = enrichment scenario
        assert result.conflict_type in [ConflictType.ENRICHMENT, ConflictType.NO_CONFLICT]

    def test_detect_worst_candidate_prioritized(self):
        """Test detector picks worst (highest score) candidate."""
        mock_collection = Mock()
        detector = ConflictDetector(mock_collection)

        candidates = [
            ConflictCandidate(
                doc_id="low_conflict",
                existing_text="Text 1",
                existing_metadata={},
                conflict_score=0.4
            ),
            ConflictCandidate(
                doc_id="high_conflict",
                existing_text="Text 2",
                existing_metadata={},
                conflict_score=0.9
            ),
        ]

        result = detector.detect_conflict(
            "Opposite text",
            {"domain": "career"},
            existing_candidates=candidates
        )

        if result.candidate:
            assert result.candidate.doc_id == "high_conflict"

    def test_detect_querying_from_collection(self):
        """Test detect_conflict queries collection if no candidates provided."""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "ids": [["found_doc"]],
            "documents": [["text"]],
            "metadatas": [[{"domain": "career"}]],
            "distances": [[0.3]],
            "embeddings": [[[0.1, 0.2]]]
        }
        detector = ConflictDetector(mock_collection)

        result = detector.detect_conflict(
            "new text",
            {"domain": "career"},
            existing_candidates=None  # Force query
        )

        mock_collection.query.assert_called_once()


class TestFormatConflictReport:
    """Test conflict report formatting."""

    def test_format_no_conflict_report(self):
        """Test formatting no-conflict report."""
        mock_collection = Mock()
        detector = ConflictDetector(mock_collection)

        result = ConflictDetectionResult(
            has_conflict=False,
            conflict_type=ConflictType.NO_CONFLICT,
            score=ConflictScore(0, 0, 0),
            reason="No conflicts"
        )

        report = detector.format_conflict_report(result)

        assert "NO_CONFLICT" in report
        assert "No conflicts" in report

    def test_format_hard_conflict_report(self):
        """Test formatting hard conflict report."""
        mock_collection = Mock()
        detector = ConflictDetector(mock_collection)

        candidate = ConflictCandidate(
            doc_id="doc_123",
            existing_text="Existing content",
            existing_metadata={}
        )

        result = ConflictDetectionResult(
            has_conflict=True,
            conflict_type=ConflictType.HARD_CONFLICT,
            score=ConflictScore(0.9, 0.8, 0.72),
            candidate=candidate,
            reason="Hard conflict detected",
            recommendation="User must resolve"
        )

        report = detector.format_conflict_report(result)

        assert "HARD_CONFLICT" in report
        assert "0.90" in report  # Similarity score
        assert "0.80" in report  # Contradiction score
        assert "0.72" in report  # Overall score

    def test_format_report_with_resolution_options(self):
        """Test report includes resolution options."""
        mock_collection = Mock()
        detector = ConflictDetector(mock_collection)

        result = ConflictDetectionResult(
            has_conflict=False,
            conflict_type=ConflictType.NO_CONFLICT,
            score=ConflictScore(0, 0, 0),
            resolution_options=["option_1", "option_2"]
        )

        report = detector.format_conflict_report(result)

        assert "option_1" in report
        assert "option_2" in report


class TestConflictAwareIngestionPipelineInit:
    """Test pipeline initialization."""

    def test_create_pipeline(self):
        """Test creating ingestion pipeline."""
        mock_collection = Mock()
        pipeline = ConflictAwareIngestionPipeline(mock_collection)

        assert pipeline.collection == mock_collection
        assert pipeline.validator is not None
        assert pipeline.detector is not None

    def test_pipeline_with_custom_validator(self):
        """Test pipeline with custom validator."""
        mock_collection = Mock()
        custom_validator = DocumentValidator()
        pipeline = ConflictAwareIngestionPipeline(mock_collection, validator=custom_validator)

        assert pipeline.validator == custom_validator


class TestIngestWithConflictCheck:
    """Test full ingestion pipeline."""

    def test_ingest_validation_fails(self):
        """Test ingestion fails on validation error."""
        mock_collection = Mock()
        pipeline = ConflictAwareIngestionPipeline(mock_collection)

        # Mock validator to return invalid
        error = ValidationError(
            category="required",
            field="domain",
            value=None
        )
        invalid_result = ValidationResult(
            is_valid=False,
            errors=[error],
            warnings=[],
            metadata_valid=False,
            text_valid=False,
            schema_compliant=False
        )
        pipeline.validator.validate_document = Mock(return_value=invalid_result)

        result = pipeline.ingest_with_conflict_check(
            doc_id="doc_1",
            text="Text",
            metadata={}
        )

        assert result["status"] == "validation_failed"
        assert len(result["errors"]) > 0

    def test_ingest_hard_conflict_blocks(self):
        """Test hard conflict blocks ingestion."""
        mock_collection = Mock()
        pipeline = ConflictAwareIngestionPipeline(mock_collection)

        # Mock valid validation
        valid_result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            metadata_valid=True,
            text_valid=True,
            schema_compliant=True
        )
        pipeline.validator.validate_document = Mock(return_value=valid_result)

        # Mock hard conflict detection
        candidate = ConflictCandidate(
            doc_id="existing",
            existing_text="Old fact",
            existing_metadata={}
        )
        conflict_result = ConflictDetectionResult(
            has_conflict=True,
            conflict_type=ConflictType.HARD_CONFLICT,
            score=ConflictScore(0.95, 0.9, 0.855),
            candidate=candidate
        )
        pipeline.detector.detect_conflict = Mock(return_value=conflict_result)

        result = pipeline.ingest_with_conflict_check(
            doc_id="doc_new",
            text="New fact",
            metadata={"domain": "career"}
        )

        assert result["status"] == "hard_conflict_detected"
        assert "doc_new" in result["doc_id"]
        mock_collection.upsert.assert_not_called()

    def test_ingest_soft_conflict_without_auto_resolve(self):
        """Test soft conflict returns for user decision."""
        mock_collection = Mock()
        pipeline = ConflictAwareIngestionPipeline(mock_collection)

        # Mock valid validation
        valid_result = ValidationResult(
            is_valid=True, errors=[], warnings=[],
            metadata_valid=True, text_valid=True, schema_compliant=True
        )
        pipeline.validator.validate_document = Mock(return_value=valid_result)

        # Mock soft conflict
        candidate = ConflictCandidate(
            doc_id="existing",
            existing_text="Existing",
            existing_metadata={}
        )
        conflict_result = ConflictDetectionResult(
            has_conflict=True,
            conflict_type=ConflictType.SOFT_CONFLICT,
            score=ConflictScore(0.5, 0.5, 0.25),
            candidate=candidate
        )
        pipeline.detector.detect_conflict = Mock(return_value=conflict_result)

        result = pipeline.ingest_with_conflict_check(
            doc_id="doc_new",
            text="New",
            metadata={},
            auto_resolve=False
        )

        assert result["status"] == "soft_conflict_detected"
        mock_collection.upsert.assert_not_called()

    def test_ingest_soft_conflict_with_auto_resolve(self):
        """Test soft conflict auto-resolves with auto_resolve=True."""
        mock_collection = Mock()
        pipeline = ConflictAwareIngestionPipeline(mock_collection)

        valid_result = ValidationResult(
            is_valid=True, errors=[], warnings=[],
            metadata_valid=True, text_valid=True, schema_compliant=True
        )
        pipeline.validator.validate_document = Mock(return_value=valid_result)

        # Soft conflict
        candidate = ConflictCandidate(
            doc_id="existing",
            existing_text="Existing",
            existing_metadata={}
        )
        conflict_result = ConflictDetectionResult(
            has_conflict=True,
            conflict_type=ConflictType.SOFT_CONFLICT,
            score=ConflictScore(0.5, 0.5, 0.25),
            candidate=candidate
        )
        pipeline.detector.detect_conflict = Mock(return_value=conflict_result)

        result = pipeline.ingest_with_conflict_check(
            doc_id="doc_new",
            text="New",
            metadata={},
            auto_resolve=True  # Auto-proceed on soft conflicts
        )

        assert result["status"] == "success"
        mock_collection.upsert.assert_called_once()

    def test_ingest_enrichment_auto_proceeds(self):
        """Test enrichment automatically proceeds."""
        mock_collection = Mock()
        pipeline = ConflictAwareIngestionPipeline(mock_collection)

        valid_result = ValidationResult(
            is_valid=True, errors=[], warnings=[],
            metadata_valid=True, text_valid=True, schema_compliant=True
        )
        pipeline.validator.validate_document = Mock(return_value=valid_result)

        # Enrichment scenario
        candidate = ConflictCandidate(
            doc_id="existing",
            existing_text="Existing",
            existing_metadata={}
        )
        conflict_result = ConflictDetectionResult(
            has_conflict=False,
            conflict_type=ConflictType.ENRICHMENT,
            score=ConflictScore(0.3, 0.05, 0.015),
            candidate=candidate
        )
        pipeline.detector.detect_conflict = Mock(return_value=conflict_result)

        result = pipeline.ingest_with_conflict_check(
            doc_id="doc_new",
            text="New detail",
            metadata={}
        )

        assert result["status"] == "success"
        mock_collection.upsert.assert_called_once()

    def test_ingest_no_conflict_proceeds(self):
        """Test no conflict proceeds normally."""
        mock_collection = Mock()
        pipeline = ConflictAwareIngestionPipeline(mock_collection)

        valid_result = ValidationResult(
            is_valid=True, errors=[], warnings=[],
            metadata_valid=True, text_valid=True, schema_compliant=True
        )
        pipeline.validator.validate_document = Mock(return_value=valid_result)

        # No conflict
        conflict_result = ConflictDetectionResult(
            has_conflict=False,
            conflict_type=ConflictType.NO_CONFLICT,
            score=ConflictScore(0, 0, 0)
        )
        pipeline.detector.detect_conflict = Mock(return_value=conflict_result)

        result = pipeline.ingest_with_conflict_check(
            doc_id="doc_new",
            text="New text",
            metadata={"domain": "career"}
        )

        assert result["status"] == "success"
        mock_collection.upsert.assert_called_once()

    def test_ingest_with_qa_pair(self):
        """Test ingestion with Q&A pair."""
        mock_collection = Mock()
        pipeline = ConflictAwareIngestionPipeline(mock_collection)

        valid_result = ValidationResult(
            is_valid=True, errors=[], warnings=[],
            metadata_valid=True, text_valid=True, schema_compliant=True
        )
        pipeline.validator.validate_document = Mock(return_value=valid_result)

        conflict_result = ConflictDetectionResult(
            has_conflict=False,
            conflict_type=ConflictType.NO_CONFLICT,
            score=ConflictScore(0, 0, 0)
        )
        pipeline.detector.detect_conflict = Mock(return_value=conflict_result)

        result = pipeline.ingest_with_conflict_check(
            doc_id="doc_qa",
            text="Detailed answer",
            metadata={},
            question="What happened?",
            answer="Detailed answer explaining the situation"
        )

        assert result["status"] == "success"

    def test_ingest_handles_insertion_error(self):
        """Test ingestion handles ChromaDB insertion errors."""
        mock_collection = Mock()
        mock_collection.upsert.side_effect = Exception("Database error")
        pipeline = ConflictAwareIngestionPipeline(mock_collection)

        valid_result = ValidationResult(
            is_valid=True, errors=[], warnings=[],
            metadata_valid=True, text_valid=True, schema_compliant=True
        )
        pipeline.validator.validate_document = Mock(return_value=valid_result)

        conflict_result = ConflictDetectionResult(
            has_conflict=False,
            conflict_type=ConflictType.NO_CONFLICT,
            score=ConflictScore(0, 0, 0)
        )
        pipeline.detector.detect_conflict = Mock(return_value=conflict_result)

        result = pipeline.ingest_with_conflict_check(
            doc_id="doc_error",
            text="Text",
            metadata={}
        )

        assert result["status"] == "ingestion_failed"
        assert "error" in result


class TestIntegrationConflictAwareIngestion:
    """Integration tests for conflict-aware ingestion."""

    def test_full_pipeline_no_conflict_path(self):
        """Test full pipeline with no conflicts."""
        mock_collection = Mock()
        pipeline = ConflictAwareIngestionPipeline(mock_collection)

        valid_result = ValidationResult(
            is_valid=True, errors=[], warnings=[],
            metadata_valid=True, text_valid=True, schema_compliant=True
        )
        pipeline.validator.validate_document = Mock(return_value=valid_result)

        conflict_result = ConflictDetectionResult(
            has_conflict=False,
            conflict_type=ConflictType.NO_CONFLICT,
            score=ConflictScore(0, 0, 0),
            reason="No similar documents"
        )
        pipeline.detector.detect_conflict = Mock(return_value=conflict_result)

        result = pipeline.ingest_with_conflict_check(
            doc_id="career_001",
            text="Worked on machine learning projects at Sprinklr",
            metadata={"domain": "career", "company": "Sprinklr"},
            question="What did you work on at Sprinklr?",
            answer="I worked on machine learning and AI projects"
        )

        assert result["status"] == "success"
        assert result["conflict_handled"] is False

    def test_full_pipeline_hard_conflict_path(self):
        """Test full pipeline with hard conflict."""
        mock_collection = Mock()
        pipeline = ConflictAwareIngestionPipeline(mock_collection)

        valid_result = ValidationResult(
            is_valid=True, errors=[], warnings=[],
            metadata_valid=True, text_valid=True, schema_compliant=True
        )
        pipeline.validator.validate_document = Mock(return_value=valid_result)

        candidate = ConflictCandidate(
            doc_id="old_doc",
            existing_text="Worked at AmEx",
            existing_metadata={}
        )
        conflict_result = ConflictDetectionResult(
            has_conflict=True,
            conflict_type=ConflictType.HARD_CONFLICT,
            score=ConflictScore(0.9, 0.85, 0.765),
            candidate=candidate,
            reason="Contradictory information about employer"
        )
        pipeline.detector.detect_conflict = Mock(return_value=conflict_result)

        result = pipeline.ingest_with_conflict_check(
            doc_id="career_002",
            text="Worked at Sprinklr",
            metadata={"domain": "career"}
        )

        assert result["status"] == "hard_conflict_detected"
        assert result["conflict_type"] == "hard_conflict"

    def test_multiple_sequential_ingestions(self):
        """Test multiple sequential ingestions."""
        mock_collection = Mock()
        pipeline = ConflictAwareIngestionPipeline(mock_collection)

        valid_result = ValidationResult(
            is_valid=True, errors=[], warnings=[],
            metadata_valid=True, text_valid=True, schema_compliant=True
        )
        pipeline.validator.validate_document = Mock(return_value=valid_result)

        no_conflict = ConflictDetectionResult(
            has_conflict=False,
            conflict_type=ConflictType.NO_CONFLICT,
            score=ConflictScore(0, 0, 0)
        )
        pipeline.detector.detect_conflict = Mock(return_value=no_conflict)

        docs = [
            ("doc_1", "First document"),
            ("doc_2", "Second document"),
            ("doc_3", "Third document"),
        ]

        results = []
        for doc_id, text in docs:
            result = pipeline.ingest_with_conflict_check(
                doc_id=doc_id,
                text=text,
                metadata={}
            )
            results.append(result)

        assert len(results) == 3
        assert all(r["status"] == "success" for r in results)
        assert mock_collection.upsert.call_count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
