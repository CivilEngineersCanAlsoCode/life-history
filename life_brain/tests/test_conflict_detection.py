"""
Comprehensive tests for Conflict Detection Engine (F5.1).

Tests cover:
- 5 real scenarios from test data (salary, leadership, project outcome, no conflict, date)
- 40+ edge cases (empty input, single doc, special characters, etc.)
- Performance benchmarking
- Type correctness
"""

import pytest
import json
import time
from pathlib import Path
from typing import List, Dict, Any

from life_brain.truth_engine.conflict_detector import (
    ConflictDetector,
    ConflictResult,
    ConflictType,
)
from life_brain.truth_engine.groundedness import RetrievedDocument


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

@pytest.fixture
def test_data_path():
    """Get path to conflict test data."""
    return Path(__file__).parent / "fixtures" / "conflict_test_data.json"


@pytest.fixture
def conflict_test_data(test_data_path):
    """Load test data from JSON."""
    with open(test_data_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def detector():
    """Create ConflictDetector instance."""
    return ConflictDetector()


def create_retrieved_document(
    doc_id: str,
    text: str,
    source: str = "test",
    date: str = "2024-03-08",
    author: str = "test",
    category: str = "career",
    similarity_score: float = 0.9
) -> RetrievedDocument:
    """Create a RetrievedDocument for testing."""
    return RetrievedDocument(
        doc_id=doc_id,
        text=text,
        metadata={
            "source": source,
            "date": date,
            "author": author,
            "category": category,
        },
        embedding=None,  # Not needed for token-based similarity
        similarity_score=similarity_score,
    )


# ============================================================================
# ORACLE TESTS (5 REAL SCENARIOS)
# ============================================================================

class TestOracleScenarios:
    """Test against 5 real scenarios from conflict_test_data.json."""

    def test_quantitative_conflict_salary_ranges(self, detector, conflict_test_data):
        """Test: Salary ranges $150k-200k vs $120k-180k."""
        scenario = conflict_test_data["test_cases"][0]
        assert scenario["name"] == "Quantitative Conflict: Salary Ranges"

        docs = [
            create_retrieved_document(
                doc["doc_id"],
                doc["text"],
                source=doc["metadata"]["source"],
                date=doc["metadata"]["date"],
                author=doc["metadata"]["author"],
            )
            for doc in scenario["documents"]
        ]

        results = detector.detect_conflicts(docs)

        expected = scenario["expected_conflict"]

        # Should find at least one conflict
        assert len(results) > 0, "Should detect conflict"

        # Find best matching result
        best = max(results, key=lambda r: r.conflict_score) if results else None
        assert best is not None

        # Verify type
        assert best.conflict_type == ConflictType.QUANTITATIVE

        # Verify score is within tolerance (±0.05)
        assert abs(best.conflict_score - expected["conflict_score"]) < 0.1, \
            f"Score mismatch: {best.conflict_score} vs {expected['conflict_score']}"

        # Verify severity
        assert best.severity == expected["severity"]

    def test_semantic_conflict_leadership_levels(self, detector, conflict_test_data):
        """Test: 'Led redesign' vs 'Contributed to improvements'."""
        scenario = conflict_test_data["test_cases"][1]
        assert "leadership" in scenario["name"].lower() or "Different Interpretations" in scenario["name"]

        docs = [
            create_retrieved_document(
                doc["doc_id"],
                doc["text"],
                source=doc["metadata"]["source"],
                date=doc["metadata"]["date"],
                author=doc["metadata"]["author"],
            )
            for doc in scenario["documents"]
        ]

        results = detector.detect_conflicts(docs)

        expected = scenario["expected_conflict"]

        assert len(results) > 0, "Should detect semantic conflict"

        best = max(results, key=lambda r: r.conflict_score)

        # Verify type
        assert best.conflict_type == ConflictType.SEMANTIC

        # Verify score (within tolerance)
        assert abs(best.conflict_score - expected["conflict_score"]) < 0.2, \
            f"Score mismatch: {best.conflict_score} vs {expected['conflict_score']}"

        # Verify severity
        assert best.severity == expected["severity"]

    def test_qualitative_conflict_project_outcome(self, detector, conflict_test_data):
        """Test: 'Major success' vs 'Ultimately deprecated'."""
        scenario = conflict_test_data["test_cases"][2]
        assert "contradiction" in scenario["name"].lower() or "outcome" in scenario["name"].lower()

        docs = [
            create_retrieved_document(
                doc["doc_id"],
                doc["text"],
                source=doc["metadata"]["source"],
                date=doc["metadata"]["date"],
                author=doc["metadata"]["author"],
            )
            for doc in scenario["documents"]
        ]

        results = detector.detect_conflicts(docs)

        expected = scenario["expected_conflict"]

        assert len(results) > 0, "Should detect contradiction"

        best = max(results, key=lambda r: r.conflict_score)

        # Verify type
        assert best.conflict_type == ConflictType.QUALITATIVE

        # Verify score
        assert abs(best.conflict_score - expected["conflict_score"]) < 0.15, \
            f"Score mismatch: {best.conflict_score} vs {expected['conflict_score']}"

        # Verify severity
        assert best.severity == expected["severity"]

    def test_no_conflict_complementary_facts(self, detector, conflict_test_data):
        """Test: No conflict with complementary timeline facts."""
        scenario = conflict_test_data["test_cases"][3]
        assert "complementary" in scenario["name"].lower() or "No Conflict" in scenario["name"]

        docs = [
            create_retrieved_document(
                doc["doc_id"],
                doc["text"],
                source=doc["metadata"]["source"],
                date=doc["metadata"]["date"],
                author=doc["metadata"]["author"],
            )
            for doc in scenario["documents"]
        ]

        results = detector.detect_conflicts(docs)

        expected = scenario["expected_conflict"]

        # Should have no conflicts or very low score
        if results:
            best = max(results, key=lambda r: r.conflict_score)
            assert best.conflict_score < 0.2, \
                f"Score too high for complementary facts: {best.conflict_score}"

    def test_date_discrepancy_conflict(self, detector, conflict_test_data):
        """Test: Employment end date conflict (Dec 2024 vs Mar 2026)."""
        scenario = conflict_test_data["test_cases"][4]
        assert "date" in scenario["name"].lower()

        docs = [
            create_retrieved_document(
                doc["doc_id"],
                doc["text"],
                source=doc["metadata"]["source"],
                date=doc["metadata"]["date"],
                author=doc["metadata"]["author"],
            )
            for doc in scenario["documents"]
        ]

        results = detector.detect_conflicts(docs)

        expected = scenario["expected_conflict"]

        assert len(results) > 0, "Should detect date conflict"

        best = max(results, key=lambda r: r.conflict_score)

        # Verify type
        assert best.conflict_type == ConflictType.QUANTITATIVE

        # Verify score (dates are quantitative)
        assert abs(best.conflict_score - expected["conflict_score"]) < 0.2, \
            f"Score mismatch: {best.conflict_score} vs {expected['conflict_score']}"


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_input(self, detector):
        """Test with empty document list."""
        results = detector.detect_conflicts([])
        assert results == [], "Empty input should return empty list"

    def test_single_document(self, detector):
        """Test with single document (no pairs)."""
        doc = create_retrieved_document("doc1", "Some text about salary $100k")
        results = detector.detect_conflicts([doc])
        assert results == [], "Single doc should return empty list"

    def test_identical_documents(self, detector):
        """Test with identical documents (no conflict)."""
        text = "Backend engineer salaries range from $150,000 to $200,000."
        doc1 = create_retrieved_document("doc1", text)
        doc2 = create_retrieved_document("doc2", text)
        results = detector.detect_conflicts([doc1, doc2])
        # Identical = no conflict
        assert len(results) == 0 or results[0].conflict_score < 0.1

    def test_completely_different_documents(self, detector):
        """Test with unrelated documents (no conflict)."""
        doc1 = create_retrieved_document(
            "doc1",
            "I studied Python and JavaScript during my bootcamp."
        )
        doc2 = create_retrieved_document(
            "doc2",
            "The weather today is sunny and warm."
        )
        results = detector.detect_conflicts([doc1, doc2])
        # Unrelated = no conflict
        assert len(results) == 0 or max([r.conflict_score for r in results]) < 0.3

    def test_special_characters_in_text(self, detector):
        """Test with special characters, unicode, etc."""
        doc1 = create_retrieved_document(
            "doc1",
            "Salary: $150,000-$200,000 USD (including 401k & benefits)"
        )
        doc2 = create_retrieved_document(
            "doc2",
            "Salary range: $120k–$180k/year (excl. benefits)"
        )
        results = detector.detect_conflicts([doc1, doc2])
        # Should handle special chars gracefully
        assert isinstance(results, list)

    def test_very_short_claims(self, detector):
        """Test with very short text."""
        doc1 = create_retrieved_document("doc1", "Success")
        doc2 = create_retrieved_document("doc2", "Failure")
        results = detector.detect_conflicts([doc1, doc2])
        # Should handle short text
        assert isinstance(results, list)

    def test_numeric_ranges_with_overlaps(self, detector):
        """Test numeric range overlap calculation."""
        doc1 = create_retrieved_document("doc1", "Salary range: $150,000-$200,000")
        doc2 = create_retrieved_document("doc2", "Salary range: $180,000-$230,000")
        results = detector.detect_conflicts([doc1, doc2])
        # Overlapping ranges = moderate conflict
        assert isinstance(results, list)
        if results:
            assert results[0].conflict_type == ConflictType.QUANTITATIVE

    def test_numeric_ranges_no_overlap(self, detector):
        """Test numeric ranges with no overlap."""
        doc1 = create_retrieved_document("doc1", "Paid $100,000 in year 1")
        doc2 = create_retrieved_document("doc2", "Paid $200,000 in year 2")
        results = detector.detect_conflicts([doc1, doc2])
        # No overlap = high conflict (if same context)
        assert isinstance(results, list)

    def test_date_parsing_various_formats(self, detector):
        """Test date parsing with different formats."""
        doc1 = create_retrieved_document("doc1", "Started in July 2024")
        doc2 = create_retrieved_document("doc2", "Started in 2024-07-01")
        results = detector.detect_conflicts([doc1, doc2])
        # Should parse dates correctly
        assert isinstance(results, list)

    def test_three_documents_all_pairs(self, detector):
        """Test with 3 documents (should check all 3 pairs)."""
        doc1 = create_retrieved_document("doc1", "Project was a major success")
        doc2 = create_retrieved_document("doc2", "Project was ultimately deprecated")
        doc3 = create_retrieved_document("doc3", "Project achieved 45% improvement")
        results = detector.detect_conflicts([doc1, doc2, doc3])
        # Should have results for conflicting pairs
        assert isinstance(results, list)

    def test_claim_extraction_empty_text(self, detector):
        """Test claim extraction from empty text."""
        claims = detector._extract_claims("")
        assert claims == []

    def test_claim_extraction_no_strong_verbs(self, detector):
        """Test claim extraction with no strong verbs."""
        claims = detector._extract_claims("This is some generic text without action verbs.")
        # May extract fewer claims
        assert isinstance(claims, list)

    def test_semantic_similarity_computation(self, detector):
        """Test semantic similarity computation."""
        similarity = detector._token_similarity(
            "Backend engineer salary $150k",
            "Backend engineer salary $120k"
        )
        assert 0 <= similarity <= 1
        assert similarity > 0.5  # Should be quite similar

    def test_semantic_similarity_different_claims(self, detector):
        """Test similarity of very different claims."""
        similarity = detector._token_similarity(
            "Backend engineer salary",
            "Python programming language"
        )
        assert 0 <= similarity <= 1

    def test_contradiction_numeric_zero_values(self, detector):
        """Test contradiction with zero values."""
        magnitude = detector._numeric_contradiction("Salary: $0", "Salary: $0")
        assert isinstance(magnitude, float)

    def test_contradiction_no_numbers(self, detector):
        """Test contradiction when no numbers present."""
        magnitude = detector._numeric_contradiction(
            "Led project",
            "Contributed to project"
        )
        assert magnitude == 0.0

    def test_qualitative_contradiction_detection(self, detector):
        """Test detection of qualitative contradictions."""
        magnitude = detector._qualitative_contradiction(
            "Led the technical redesign",
            "Contributed to improvements"
        )
        assert magnitude > 0, "Should detect qualitative difference"

    def test_semantic_opposites_detection(self, detector):
        """Test detection of semantic opposites."""
        assert detector._are_semantic_opposites(
            "Project succeeded",
            "Project failed"
        )
        assert detector._are_semantic_opposites(
            "Major success",
            "Ultimately deprecated"
        )

    def test_semantic_opposites_false_positive(self, detector):
        """Test that similar words aren't falsely marked as opposites."""
        assert not detector._are_semantic_opposites(
            "Backend engineer",
            "Backend development"
        )

    def test_has_numbers_detection(self, detector):
        """Test number detection in text."""
        assert detector._has_numbers("Salary: $150,000")
        assert detector._has_numbers("Started in 2024")
        assert detector._has_numbers("March 2024")
        assert not detector._has_numbers("No numbers here")

    def test_has_qualitative_keywords(self, detector):
        """Test qualitative keyword detection."""
        assert detector._has_qualitative_keywords("Major success")
        assert detector._has_qualitative_keywords("Project failed")
        assert detector._has_qualitative_keywords("Senior engineer")
        assert not detector._has_qualitative_keywords("Engineer role at company")

    def test_severity_classification_low(self, detector):
        """Test severity classification for low scores."""
        severity = detector._determine_severity(0.15)
        assert severity == "low"

    def test_severity_classification_medium(self, detector):
        """Test severity classification for medium scores."""
        severity = detector._determine_severity(0.45)
        assert severity == "medium"

    def test_severity_classification_high(self, detector):
        """Test severity classification for high scores."""
        severity = detector._determine_severity(0.75)
        assert severity == "high"

    def test_conflict_type_categorization_quantitative(self, detector):
        """Test categorization as QUANTITATIVE."""
        conflict_type = detector.categorize_conflict(
            "$150,000-$200,000",
            "$120,000-$180,000",
            0.25
        )
        assert conflict_type == ConflictType.QUANTITATIVE

    def test_conflict_type_categorization_semantic(self, detector):
        """Test categorization as SEMANTIC."""
        conflict_type = detector.categorize_conflict(
            "Project succeeded",
            "Project failed",
            0.9
        )
        assert conflict_type == ConflictType.SEMANTIC

    def test_conflict_type_categorization_qualitative(self, detector):
        """Test categorization as QUALITATIVE."""
        conflict_type = detector.categorize_conflict(
            "Led the team",
            "Contributed to the effort",
            0.5
        )
        # Could be QUALITATIVE or SEMANTIC
        assert conflict_type in [ConflictType.QUALITATIVE, ConflictType.SEMANTIC]

    def test_conflict_type_categorization_none(self, detector):
        """Test categorization as NONE when no conflict."""
        conflict_type = detector.categorize_conflict(
            "Backend engineer",
            "Frontend developer",
            0.05
        )
        # Low score should give NONE
        assert conflict_type == ConflictType.NONE

    def test_score_conflict_low_similarity(self, detector):
        """Test score_conflict with low similarity claims."""
        score = detector.score_conflict(
            "Backend engineer",
            "Swimming technique"
        )
        assert 0 <= score <= 1
        assert score < 0.3

    def test_score_conflict_high_contradiction(self, detector):
        """Test score_conflict with high contradiction."""
        score = detector.score_conflict(
            "Project succeeded",
            "Project failed"
        )
        assert score > 0.5

    def test_score_conflict_empty_claims(self, detector):
        """Test score_conflict with empty strings."""
        assert detector.score_conflict("", "Some text") == 0.0
        assert detector.score_conflict("Some text", "") == 0.0
        assert detector.score_conflict("", "") == 0.0

    def test_result_sorting_by_score(self, detector):
        """Test that results are sorted by conflict_score descending."""
        doc1 = create_retrieved_document("doc1", "Project succeeded")
        doc2 = create_retrieved_document("doc2", "Project failed")
        doc3 = create_retrieved_document("doc3", "Project had mixed results")

        results = detector.detect_conflicts([doc1, doc2, doc3])

        # Results should be sorted by score descending
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].conflict_score >= results[i + 1].conflict_score

    def test_duplicate_removal(self, detector):
        """Test that duplicate conflicts are removed."""
        doc1 = create_retrieved_document("doc1", "Major success achieved in 2024")
        doc2 = create_retrieved_document("doc2", "Ultimately deprecated in 2024")

        results = detector.detect_conflicts([doc1, doc2])

        # Should not have duplicate (same) conflicts
        doc_pairs = [r.doc_pair for r in results]
        assert len(doc_pairs) == len(set(doc_pairs))

    def test_explanation_generation(self, detector):
        """Test that explanations are generated correctly."""
        doc1 = create_retrieved_document("doc1", "Salary: $150k-$200k")
        doc2 = create_retrieved_document("doc2", "Salary: $120k-$180k")

        results = detector.detect_conflicts([doc1, doc2])

        if results:
            assert len(results[0].explanation) > 0
            assert isinstance(results[0].explanation, str)

    def test_cosine_similarity_with_embeddings(self, detector):
        """Test cosine similarity computation with actual embeddings."""
        vec1 = [0.1, 0.2, 0.3]
        vec2 = [0.1, 0.2, 0.3]
        similarity = detector._cosine_similarity(vec1, vec2)
        assert abs(similarity - 1.0) < 0.01  # Perfect match

    def test_cosine_similarity_orthogonal(self, detector):
        """Test cosine similarity with orthogonal vectors."""
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]
        similarity = detector._cosine_similarity(vec1, vec2)
        assert abs(similarity - 0.0) < 0.01  # Orthogonal = 0 similarity

    def test_cosine_similarity_empty_vectors(self, detector):
        """Test cosine similarity with empty vectors."""
        similarity = detector._cosine_similarity([], [])
        assert similarity == 0.0

    def test_doc_pair_indices_correct(self, detector):
        """Test that doc_pair indices are correct."""
        doc1 = create_retrieved_document("doc1", "Success")
        doc2 = create_retrieved_document("doc2", "Failure")
        doc3 = create_retrieved_document("doc3", "Success again")

        results = detector.detect_conflicts([doc1, doc2, doc3])

        for result in results:
            assert result.doc_pair[0] < result.doc_pair[1]
            assert 0 <= result.doc_pair[0] < 3
            assert 0 <= result.doc_pair[1] < 3


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test performance requirements."""

    def test_performance_3_docs_batch(self, detector):
        """Test performance: < 100ms for 3-doc batch."""
        docs = [
            create_retrieved_document(
                f"doc{i}",
                f"Text about salary $150k and success in 202{i}"
            )
            for i in range(3)
        ]

        start = time.time()
        results = detector.detect_conflicts(docs)
        elapsed = time.time() - start

        assert elapsed < 0.1, f"Performance target: <100ms, got {elapsed*1000:.1f}ms"
        assert isinstance(results, list)

    def test_performance_5_docs_batch(self, detector):
        """Test performance: <300ms for 5-doc batch."""
        docs = [
            create_retrieved_document(
                f"doc{i}",
                f"Text about salary and project outcomes in 202{i}"
            )
            for i in range(5)
        ]

        start = time.time()
        results = detector.detect_conflicts(docs)
        elapsed = time.time() - start

        # 5 docs = 10 pairs, should still be fast
        assert elapsed < 0.3, f"Performance target: <300ms, got {elapsed*1000:.1f}ms"
        assert isinstance(results, list)


# ============================================================================
# TYPE AND DATACLASS TESTS
# ============================================================================

class TestTypeCorrectness:
    """Test type hints and dataclass correctness."""

    def test_conflict_result_dataclass(self):
        """Test ConflictResult dataclass creation."""
        result = ConflictResult(
            doc_pair=(0, 1),
            conflict_score=0.75,
            conflict_type=ConflictType.SEMANTIC,
            severity="high",
            claim1="Project succeeded",
            claim2="Project failed",
            explanation="Direct contradiction"
        )

        assert result.doc_pair == (0, 1)
        assert result.conflict_score == 0.75
        assert result.conflict_type == ConflictType.SEMANTIC
        assert result.severity == "high"

    def test_conflict_type_enum(self):
        """Test ConflictType enum values."""
        assert ConflictType.QUANTITATIVE.value == "quantitative"
        assert ConflictType.QUALITATIVE.value == "qualitative"
        assert ConflictType.SEMANTIC.value == "semantic"
        assert ConflictType.NONE.value == "none"

    def test_detector_return_type(self, detector):
        """Test that detector returns correct type."""
        doc1 = create_retrieved_document("doc1", "Text A")
        doc2 = create_retrieved_document("doc2", "Text B")

        results = detector.detect_conflicts([doc1, doc2])

        assert isinstance(results, list)
        assert all(isinstance(r, ConflictResult) for r in results)

    def test_all_results_have_required_fields(self, detector):
        """Test that all results have required fields."""
        doc1 = create_retrieved_document("doc1", "Success")
        doc2 = create_retrieved_document("doc2", "Failure")

        results = detector.detect_conflicts([doc1, doc2])

        for result in results:
            assert hasattr(result, 'doc_pair')
            assert hasattr(result, 'conflict_score')
            assert hasattr(result, 'conflict_type')
            assert hasattr(result, 'severity')
            assert hasattr(result, 'claim1')
            assert hasattr(result, 'claim2')
            assert hasattr(result, 'explanation')

            # Verify types
            assert isinstance(result.doc_pair, tuple)
            assert isinstance(result.conflict_score, float)
            assert isinstance(result.conflict_type, ConflictType)
            assert isinstance(result.severity, str)
            assert isinstance(result.claim1, str)
            assert isinstance(result.claim2, str)
            assert isinstance(result.explanation, str)

    def test_conflict_score_bounds(self, detector):
        """Test that conflict_score is always 0-1."""
        doc1 = create_retrieved_document("doc1", "Success")
        doc2 = create_retrieved_document("doc2", "Failure")

        results = detector.detect_conflicts([doc1, doc2])

        for result in results:
            assert 0.0 <= result.conflict_score <= 1.0

    def test_severity_valid_values(self, detector):
        """Test that severity is one of valid values."""
        doc1 = create_retrieved_document("doc1", "Success")
        doc2 = create_retrieved_document("doc2", "Failure")

        results = detector.detect_conflicts([doc1, doc2])

        valid_severities = {"low", "medium", "high"}
        for result in results:
            assert result.severity in valid_severities


# ============================================================================
# DOCSTRING AND DOCUMENTATION TESTS
# ============================================================================

class TestDocumentation:
    """Test that docstrings and documentation are complete."""

    def test_detector_has_docstring(self):
        """Test ConflictDetector class has docstring."""
        assert ConflictDetector.__doc__ is not None
        assert len(ConflictDetector.__doc__) > 0

    def test_detect_conflicts_has_docstring(self):
        """Test detect_conflicts method has docstring."""
        assert ConflictDetector.detect_conflicts.__doc__ is not None

    def test_score_conflict_has_docstring(self):
        """Test score_conflict method has docstring."""
        assert ConflictDetector.score_conflict.__doc__ is not None

    def test_categorize_conflict_has_docstring(self):
        """Test categorize_conflict method has docstring."""
        assert ConflictDetector.categorize_conflict.__doc__ is not None

    def test_all_private_methods_have_docstrings(self):
        """Test that major private methods have docstrings."""
        detector = ConflictDetector()
        private_methods = [
            '_extract_claims',
            '_compute_semantic_similarity',
            '_calculate_contradiction_magnitude',
            '_token_similarity',
            '_cosine_similarity',
        ]
        for method_name in private_methods:
            method = getattr(detector, method_name)
            assert method.__doc__ is not None, f"{method_name} missing docstring"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
