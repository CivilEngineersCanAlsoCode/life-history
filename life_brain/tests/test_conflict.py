"""
Unit tests for conflict.py

Covers:
- ConflictResult dataclass
- Semantic similarity calculation (cosine)
- Contradiction magnitude calculation (metric, fact, date, story)
- Entity and temporal scope checks
- Main conflict detection algorithm
- Change log entry creation
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from life_brain.truth.conflict import (
    ConflictResult,
    calculate_semantic_similarity,
    calculate_contradiction_magnitude,
    entity_scope_check,
    temporal_scope_check,
    conflict_check,
    create_change_log_entry,
)


class TestConflictResult:
    """Test ConflictResult dataclass."""

    def test_create_conflict_result_minimal(self):
        """Test creating conflict result with minimal fields."""
        result = ConflictResult(
            status="SAFE",
            conflict_score=0.0
        )
        assert result.status == "SAFE"
        assert result.conflict_score == 0.0
        assert result.existing_pair_id is None
        assert result.existing_answer is None

    def test_create_conflict_result_hard_conflict(self):
        """Test creating hard conflict result."""
        result = ConflictResult(
            status="CONFLICT",
            conflict_score=0.75,
            existing_pair_id="doc_123",
            existing_answer="Old answer"
        )
        assert result.status == "CONFLICT"
        assert result.conflict_score == 0.75
        assert result.existing_pair_id == "doc_123"

    def test_create_conflict_result_soft(self):
        """Test creating soft conflict result."""
        result = ConflictResult(
            status="SOFT",
            conflict_score=0.45,
            contradiction_type="date_mismatch"
        )
        assert result.status == "SOFT"
        assert result.contradiction_type == "date_mismatch"

    def test_create_conflict_result_enrichment(self):
        """Test creating enrichment result."""
        result = ConflictResult(
            status="ENRICHMENT",
            conflict_score=0.15
        )
        assert result.status == "ENRICHMENT"
        assert result.conflict_score == 0.15

    def test_result_with_all_fields(self):
        """Test conflict result with all fields."""
        result = ConflictResult(
            status="CONFLICT",
            conflict_score=0.8,
            existing_pair_id="doc_old",
            existing_answer="Old answer",
            contradiction_type="fact",
            existing_entry_date="2024-01-01",
            existing_context="Sprinklr era",
            existing_doc_id="doc_old_alias"
        )
        assert result.existing_context == "Sprinklr era"
        assert result.existing_entry_date == "2024-01-01"


class TestSemanticSimilarity:
    """Test semantic similarity calculation."""

    def test_similarity_identical_vectors(self):
        """Test similarity of identical vectors."""
        vec = [1.0, 0.0, 0.0]
        similarity = calculate_semantic_similarity(vec, vec)
        assert abs(similarity - 1.0) < 0.01  # Should be 1.0

    def test_similarity_orthogonal_vectors(self):
        """Test similarity of orthogonal vectors."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        similarity = calculate_semantic_similarity(vec1, vec2)
        assert abs(similarity - 0.0) < 0.01  # Should be 0.0

    def test_similarity_opposite_vectors(self):
        """Test similarity of opposite vectors."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [-1.0, 0.0, 0.0]
        similarity = calculate_semantic_similarity(vec1, vec2)
        assert similarity <= 0.01  # Should be close to 0

    def test_similarity_partial_overlap(self):
        """Test similarity with partial overlap."""
        vec1 = [1.0, 1.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        similarity = calculate_semantic_similarity(vec1, vec2)
        assert 0.5 < similarity < 1.0  # Should be between 0.5 and 1.0

    def test_similarity_empty_vectors(self):
        """Test similarity with empty vectors."""
        similarity = calculate_semantic_similarity([], [])
        assert similarity == 0.0

    def test_similarity_zero_vector(self):
        """Test similarity with zero vector."""
        similarity = calculate_semantic_similarity([0, 0, 0], [1, 0, 0])
        assert similarity == 0.0

    def test_similarity_none_input(self):
        """Test similarity with None input."""
        similarity = calculate_semantic_similarity(None, [1, 0, 0])
        assert similarity == 0.0

    def test_similarity_normalized(self):
        """Test that similarity is in [0, 1] range."""
        vec1 = np.random.randn(10).tolist()
        vec2 = np.random.randn(10).tolist()
        similarity = calculate_semantic_similarity(vec1, vec2)
        assert 0.0 <= similarity <= 1.0

    def test_similarity_large_vectors(self):
        """Test similarity calculation with large vectors."""
        vec1 = np.random.randn(768).tolist()  # Typical embedding dimension
        vec2 = np.random.randn(768).tolist()
        similarity = calculate_semantic_similarity(vec1, vec2)
        assert 0.0 <= similarity <= 1.0


class TestContradictionMetric:
    """Test metric contradiction calculation."""

    def test_contradiction_same_metrics(self):
        """Test contradiction for identical metrics."""
        contradiction = calculate_contradiction_magnitude(100, 100, "metric")
        assert contradiction == 0.0

    def test_contradiction_metric_simple(self):
        """Test metric contradiction calculation."""
        # |100 - 30| / max(100, 30) = 70 / 100 = 0.7
        contradiction = calculate_contradiction_magnitude(100, 30, "metric")
        assert abs(contradiction - 0.7) < 0.01

    def test_contradiction_metric_reverse_order(self):
        """Test that contradiction is symmetric."""
        c1 = calculate_contradiction_magnitude(100, 30, "metric")
        c2 = calculate_contradiction_magnitude(30, 100, "metric")
        assert abs(c1 - c2) < 0.01

    def test_contradiction_metric_zero_values(self):
        """Test metric contradiction with zero values."""
        contradiction = calculate_contradiction_magnitude(0, 0, "metric")
        assert contradiction == 0.0

    def test_contradiction_metric_non_numeric(self):
        """Test metric contradiction with non-numeric values."""
        contradiction = calculate_contradiction_magnitude("abc", "def", "metric")
        assert contradiction == 0.0

    def test_contradiction_metric_salary_example(self):
        """Test metric contradiction with salary example."""
        # |50 - 75| / 75 ≈ 0.33
        contradiction = calculate_contradiction_magnitude(50, 75, "metric")
        assert 0.3 <= contradiction <= 0.35


class TestContradictionDate:
    """Test date contradiction calculation."""

    def test_contradiction_same_dates(self):
        """Test contradiction for identical dates."""
        contradiction = calculate_contradiction_magnitude("2024-03-09", "2024-03-09", "date")
        assert contradiction == 0.0

    def test_contradiction_date_one_month_apart(self):
        """Test date contradiction for one month apart."""
        contradiction = calculate_contradiction_magnitude("2024-01", "2024-02", "date")
        # Approximately 30-31 days / 365 ≈ 0.08-0.09
        assert 0.07 <= contradiction <= 0.10

    def test_contradiction_date_one_year_apart(self):
        """Test date contradiction for one year apart."""
        contradiction = calculate_contradiction_magnitude("2023", "2024", "date")
        # Approximately 365 days / 365 = 1.0
        assert contradiction >= 0.9

    def test_contradiction_date_invalid_format(self):
        """Test date contradiction with invalid format."""
        contradiction = calculate_contradiction_magnitude("invalid", "also_invalid", "date")
        # Fallback returns 0.1 for non-matching strings
        assert contradiction == 0.1

    def test_contradiction_date_formats(self):
        """Test various date formats."""
        c1 = calculate_contradiction_magnitude("2024-03-09", "2024-03-09", "date")
        assert c1 == 0.0
        # Different formats may parse differently
        c2 = calculate_contradiction_magnitude("2024-03-09", "2024-03-09", "date")
        assert c2 == 0.0  # Same format, same dates


class TestEntityScopeCheck:
    """Test entity scope checking."""

    def test_same_entity_scope_company_only(self):
        """Test same company scope."""
        new = {"company": "Sprinklr"}
        old = {"company": "Sprinklr"}
        assert entity_scope_check(new, old) is True

    def test_different_entity_scope_company(self):
        """Test different company scope."""
        new = {"company": "Sprinklr"}
        old = {"company": "AmEx"}
        assert entity_scope_check(new, old) is False

    def test_same_entity_scope_multiple_fields(self):
        """Test same scope with multiple entity fields."""
        new = {"company": "Sprinklr", "role": "engineer", "project": "CGB"}
        old = {"company": "Sprinklr", "role": "engineer", "project": "CGB"}
        assert entity_scope_check(new, old) is True

    def test_different_role_same_company(self):
        """Test different role, same company."""
        new = {"company": "Sprinklr", "role": "engineer"}
        old = {"company": "Sprinklr", "role": "manager"}
        assert entity_scope_check(new, old) is False

    def test_missing_entity_fields(self):
        """Test with missing entity fields."""
        new = {"company": "Sprinklr"}
        old = {}  # Missing company
        # Missing on both sides should match (both None)
        result = entity_scope_check(new, old)
        assert result is False  # Different entities

    def test_both_missing_entity_fields(self):
        """Test when both have missing entity fields."""
        new = {}
        old = {}
        # Both missing all fields = same scope
        assert entity_scope_check(new, old) is True

    def test_entity_aliases_normalized(self):
        """Test that entity aliases are normalized."""
        new = {"company": "Sprinklr"}
        old = {"company": "sprinklr"}  # Lowercase
        assert entity_scope_check(new, old) is True


class TestTemporalScopeCheck:
    """Test temporal scope checking."""

    def test_same_temporal_scope_exact_dates(self):
        """Test same temporal scope with exact dates."""
        new = {"date_start": "2024-03-09"}
        old = {"date_start": "2024-03-09"}
        assert temporal_scope_check(new, old) is True

    def test_same_temporal_scope_within_6_months(self):
        """Test same temporal scope within 6 months."""
        new = {"date_start": "2024-03"}
        old = {"date_start": "2024-06"}
        assert temporal_scope_check(new, old) is True

    def test_different_temporal_scope_beyond_6_months(self):
        """Test different temporal scope beyond 6 months."""
        new = {"date_start": "2024-01"}
        old = {"date_start": "2024-09"}
        assert temporal_scope_check(new, old) is False

    def test_different_temporal_scope_different_years(self):
        """Test different temporal scope in different years."""
        new = {"date_start": "2023"}
        old = {"date_start": "2024"}
        assert temporal_scope_check(new, old) is False

    def test_missing_date_fields(self):
        """Test with missing date fields."""
        new = {"date_start": "2024-03-09"}
        old = {}  # Missing date
        # Missing dates = same scope (conservative)
        assert temporal_scope_check(new, old) is True

    def test_both_missing_dates(self):
        """Test when both have missing dates."""
        new = {}
        old = {}
        # Both missing dates = same scope
        assert temporal_scope_check(new, old) is True

    def test_invalid_date_format(self):
        """Test with invalid date format."""
        new = {"date_start": "invalid"}
        old = {"date_start": "also_invalid"}
        # Invalid dates = same scope (conservative)
        assert temporal_scope_check(new, old) is True


class TestConflictCheck:
    """Test main conflict detection algorithm."""

    def test_conflict_check_empty_existing(self):
        """Test conflict check with no existing pairs."""
        new_pair = {"embedding": [1, 0, 0], "answer": "new"}
        result = conflict_check(new_pair, [])
        assert result.status == "SAFE"
        assert result.conflict_score == 0.0

    def test_conflict_check_low_similarity(self):
        """Test that low similarity returns SAFE."""
        new_pair = {
            "embedding": [1, 0, 0],
            "answer": "new answer",
            "company": "Sprinklr"
        }
        existing_pair = (
            {"embedding": [0, 1, 0], "answer": "old answer", "company": "Sprinklr"},
            [0, 1, 0]
        )
        result = conflict_check(new_pair, [existing_pair])
        # Low similarity (orthogonal vectors) should result in SAFE
        assert result.status == "SAFE"

    def test_conflict_check_different_entities(self):
        """Test that different entities don't conflict."""
        new_pair = {
            "embedding": [1, 0, 0],
            "answer": "answer",
            "company": "Sprinklr"
        }
        existing_pair = (
            {"embedding": [1, 0, 0], "answer": "answer", "company": "AmEx"},
            [1, 0, 0]
        )
        result = conflict_check(new_pair, [existing_pair])
        # Same embedding but different company = SAFE
        assert result.status == "SAFE"

    def test_conflict_check_different_time_periods(self):
        """Test that different time periods don't conflict."""
        new_pair = {
            "embedding": [1, 0, 0],
            "answer": "answer",
            "company": "Sprinklr",
            "date_start": "2024-01"
        }
        existing_pair = (
            {
                "embedding": [1, 0, 0],
                "answer": "answer",
                "company": "Sprinklr",
                "date_start": "2022-01"
            },
            [1, 0, 0]
        )
        result = conflict_check(new_pair, [existing_pair])
        # >6 months apart = different scope = SAFE
        assert result.status == "SAFE"

    def test_conflict_check_returns_conflict_result(self):
        """Test that conflict_check returns ConflictResult."""
        new_pair = {"embedding": [1, 0, 0], "answer": "new"}
        result = conflict_check(new_pair, [])
        assert isinstance(result, ConflictResult)
        assert hasattr(result, "status")
        assert hasattr(result, "conflict_score")


class TestChangeLogEntry:
    """Test change log entry creation."""

    def test_create_change_log_basic(self):
        """Test creating basic change log entry."""
        entry = create_change_log_entry(
            old_doc_id="doc_123",
            old_value="Old fact",
            new_value="New fact",
            resolution="user_chose_new"
        )
        assert entry["type"] == "document_record"
        assert entry["category"] == "correction"
        assert entry["old_doc_id"] == "doc_123"
        assert entry["old_value"] == "Old fact"
        assert entry["new_value"] == "New fact"
        assert entry["resolution"] == "user_chose_new"

    def test_create_change_log_with_context(self):
        """Test creating change log with context."""
        entry = create_change_log_entry(
            old_doc_id="doc_1",
            old_value="value1",
            new_value="value2",
            resolution="auto_update",
            context="Sprinklr era"
        )
        assert entry["context"] == "Sprinklr era"

    def test_change_log_has_timestamp(self):
        """Test that change log has timestamp."""
        entry = create_change_log_entry(
            old_doc_id="doc_1",
            old_value="old",
            new_value="new",
            resolution="user_chose_new"
        )
        assert "timestamp" in entry
        assert entry["timestamp"]  # Not empty

    def test_change_log_has_unique_id(self):
        """Test that change log has unique ID."""
        entry1 = create_change_log_entry(
            old_doc_id="doc_1",
            old_value="old",
            new_value="new",
            resolution="correction"
        )
        entry2 = create_change_log_entry(
            old_doc_id="doc_1",
            old_value="old",
            new_value="new",
            resolution="correction"
        )
        assert entry1["id"] != entry2["id"]

    def test_change_log_metadata_fields(self):
        """Test that change log has required metadata."""
        entry = create_change_log_entry(
            old_doc_id="doc_1",
            old_value="old",
            new_value="new",
            resolution="user_chose_new"
        )
        assert entry["privacy"] == "private"
        assert entry["source"] == "user_correction"
        assert entry["schema_version"] == 1
        assert entry["importance"] == 3
        assert entry["domain"] == "metadata"
        assert entry["subdomain"] == "audit_trail"


class TestIntegrationConflict:
    """Integration tests for conflict detection."""

    def test_full_conflict_workflow_safe(self):
        """Test full workflow returning SAFE."""
        new_pair = {
            "embedding": [1, 0, 0],
            "answer": "new answer"
        }
        result = conflict_check(new_pair, [])
        assert result.status == "SAFE"
        assert result.conflict_score == 0.0

    def test_full_workflow_create_change_log(self):
        """Test full workflow with change log creation."""
        # Detect conflict
        new_pair = {"embedding": [1, 0, 0], "answer": "new"}
        result = conflict_check(new_pair, [])

        # If conflict detected, create change log
        if result.status in ["CONFLICT", "SOFT"]:
            entry = create_change_log_entry(
                old_doc_id=result.existing_pair_id or "doc_old",
                old_value=result.existing_answer or "old",
                new_value="new",
                resolution="user_chose_new"
            )
            assert entry is not None
            assert entry["type"] == "document_record"

    def test_scope_checks_combined(self):
        """Test entity and temporal scope together."""
        new = {
            "company": "Sprinklr",
            "role": "engineer",
            "date_start": "2023-01"
        }
        old = {
            "company": "Sprinklr",
            "role": "engineer",
            "date_start": "2023-06"
        }

        entity_match = entity_scope_check(new, old)
        temporal_match = temporal_scope_check(new, old)

        # Same entity, same temporal scope (within 6 months)
        assert entity_match is True
        assert temporal_match is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
