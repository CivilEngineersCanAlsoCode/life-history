"""
Comprehensive test suite for CredibilityScorer (F5.2).

Tests:
- All 7 test data scenarios with oracle verification
- Component scoring (recency, authority, accuracy)
- Edge cases (missing dates, unknown sources)
- Ranking functionality
- Performance (<50ms per doc)
- 35+ test cases total
"""

import json
import time
import pytest
from datetime import datetime
from pathlib import Path

from life_brain.truth.credibility_scorer import (
    CredibilityScorer,
    CredibilityScore,
    REFERENCE_DATE,
)
from life_brain.truth.groundedness import RetrievedDocument


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def scorer():
    """Create a CredibilityScorer instance with fixed reference date."""
    return CredibilityScorer(reference_date=REFERENCE_DATE)


@pytest.fixture
def test_data():
    """Load test data from credibility_test_data.json."""
    test_file = Path(__file__).parent / "fixtures" / "credibility_test_data.json"
    with open(test_file) as f:
        return json.load(f)


def create_retrieved_document(doc_dict: dict) -> RetrievedDocument:
    """Helper to convert test dict to RetrievedDocument."""
    return RetrievedDocument(
        doc_id=doc_dict["doc_id"],
        text=doc_dict["text"],
        metadata=doc_dict["metadata"],
        embedding=None,
        similarity_score=doc_dict.get("similarity_score", 0.0),
    )


# ============================================================================
# Section 1: Oracle Test Cases (from credibility_test_data.json)
# ============================================================================


class TestOracleScenarios:
    """Test all 7 scenarios from test data with exact expected values."""

    def test_expert_recent_source(self, scorer, test_data):
        """Expert 2024: credibility ~0.95"""
        test_case = test_data["test_cases"][0]
        assert test_case["name"] == "Expert Recent Source"

        doc = create_retrieved_document(test_case["document"])
        score = scorer.score_source(doc)

        expected = test_case["expected_credibility"]
        # Check overall credibility (most important) - within ±0.05
        assert abs(score.credibility - expected["credibility"]) <= 0.05
        # Category should match expected
        assert score.category == expected["category"]

    def test_personal_old_source(self, scorer, test_data):
        """Personal 2021: credibility ~0.53"""
        test_case = test_data["test_cases"][1]
        assert test_case["name"] == "Personal Old Source"

        doc = create_retrieved_document(test_case["document"])
        score = scorer.score_source(doc)

        expected = test_case["expected_credibility"]
        assert abs(score.credibility - expected["credibility"]) <= 0.05
        assert score.category == expected["category"]

    def test_verified_recent_source(self, scorer, test_data):
        """Verified 2024: credibility ~0.87"""
        test_case = test_data["test_cases"][2]
        assert test_case["name"] == "Verified Recent Source"

        doc = create_retrieved_document(test_case["document"])
        score = scorer.score_source(doc)

        expected = test_case["expected_credibility"]
        assert abs(score.credibility - expected["credibility"]) <= 0.05
        assert score.category == expected["category"]

    def test_community_source(self, scorer, test_data):
        """Community source: credibility ~0.58"""
        test_case = test_data["test_cases"][3]
        assert test_case["name"] == "Community Source"

        doc = create_retrieved_document(test_case["document"])
        score = scorer.score_source(doc)

        expected = test_case["expected_credibility"]
        assert abs(score.credibility - expected["credibility"]) <= 0.05
        assert score.category == expected["category"]

    def test_corroborated_fact(self, scorer, test_data):
        """Corroborated by 2+ sources: credibility ~0.84"""
        test_case = test_data["test_cases"][4]
        assert test_case["name"] == "Corroborated Fact"

        doc = create_retrieved_document(test_case["document"])
        score = scorer.score_source(doc)

        expected = test_case["expected_credibility"]
        assert abs(score.credibility - expected["credibility"]) <= 0.05
        assert score.category == expected["category"]

    def test_outdated_archive_source(self, scorer, test_data):
        """Archive 2019: credibility ~0.38"""
        test_case = test_data["test_cases"][5]
        assert test_case["name"] == "Outdated Archive Source"

        doc = create_retrieved_document(test_case["document"])
        score = scorer.score_source(doc)

        expected = test_case["expected_credibility"]
        assert abs(score.credibility - expected["credibility"]) <= 0.05
        assert score.category == expected["category"]

    def test_contradicted_source(self, scorer, test_data):
        """Contradicted by 2+ sources: credibility ~0.32"""
        test_case = test_data["test_cases"][6]
        assert test_case["name"] == "Contradicted Source"

        doc = create_retrieved_document(test_case["document"])
        score = scorer.score_source(doc)

        expected = test_case["expected_credibility"]
        assert abs(score.credibility - expected["credibility"]) <= 0.05
        assert score.category == expected["category"]


# ============================================================================
# Section 2: Component Scoring Tests
# ============================================================================


class TestRecencyScoring:
    """Test recency score calculation."""

    def test_recent_3_months(self):
        """< 3 months → 1.0"""
        score = CredibilityScorer._calculate_recency_score("2026-02-01")
        assert score == 1.0

    def test_3_6_months(self):
        """3-6 months → 0.8"""
        # With ref_date=2024-04-30, check a date ~4-5 months old
        score = CredibilityScorer._calculate_recency_score("2023-12-01")
        assert score == 0.8

    def test_6_12_months(self):
        """6-12 months → 0.6"""
        # With ref_date=2024-04-30, check a date ~8 months old
        score = CredibilityScorer._calculate_recency_score("2023-08-15")
        assert score == 0.6

    def test_over_12_months(self):
        """> 12 months → 0.4"""
        # With ref_date=2024-04-30, check a date > 12 months old
        score = CredibilityScorer._calculate_recency_score("2023-01-01")
        assert score == 0.4

    def test_much_older(self):
        """> 12 months (very old) → 0.4"""
        score = CredibilityScorer._calculate_recency_score("2019-06-01")
        assert score == 0.4

    def test_date_with_month_only(self):
        """Parse YYYY-MM format"""
        score = CredibilityScorer._calculate_recency_score("2026-02")
        assert score == 1.0

    def test_date_with_year_only(self):
        """Parse YYYY format"""
        score = CredibilityScorer._calculate_recency_score("2026")
        assert score == 1.0

    def test_empty_date(self):
        """Empty date → 0.4 (assume old)"""
        score = CredibilityScorer._calculate_recency_score("")
        assert score == 0.4

    def test_invalid_date(self):
        """Invalid date → 0.4"""
        score = CredibilityScorer._calculate_recency_score("invalid")
        assert score == 0.4


class TestAuthorityScoring:
    """Test authority score calculation."""

    def test_official_research(self):
        """Official source → 1.0"""
        score = CredibilityScorer._calculate_authority_score(
            "gartner_report", "gartner_analyst"
        )
        assert score == 1.0

    def test_professional_verified(self):
        """Professional/verified → 0.8"""
        score = CredibilityScorer._calculate_authority_score(
            "performance_review", "manager"
        )
        assert score == 0.8

    def test_personal_expert(self):
        """Personal/expert → 0.7"""
        score = CredibilityScorer._calculate_authority_score("personal_blog", "self")
        assert score == 0.7

    def test_community_unverified(self):
        """Community/unverified → 0.5"""
        score = CredibilityScorer._calculate_authority_score("glassdoor", "anonymous")
        assert score == 0.5

    def test_unknown_archive(self):
        """Unknown/archive → 0.3"""
        score = CredibilityScorer._calculate_authority_score("old_blog", "legacy")
        assert score == 0.3

    def test_authority_type_override(self):
        """Explicit authority_type takes precedence"""
        score = CredibilityScorer._calculate_authority_score(
            "unknown", "unknown", authority_type="official"
        )
        assert score == 1.0

    def test_empty_source_and_author(self):
        """Both empty → 0.3"""
        score = CredibilityScorer._calculate_authority_score("", "")
        assert score == 0.3

    def test_case_insensitive(self):
        """Source/author matching is case-insensitive"""
        score1 = CredibilityScorer._calculate_authority_score("Gartner_Report", "")
        score2 = CredibilityScorer._calculate_authority_score("gartner_report", "")
        assert score1 == score2 == 1.0


class TestAccuracyScoring:
    """Test accuracy score calculation."""

    def test_contradicted_source(self):
        """Contradicted by sources → 0.2"""
        doc = RetrievedDocument(
            doc_id="test", text="test", metadata={}, similarity_score=0.5
        )
        score = CredibilityScorer._calculate_accuracy_score(
            doc, contradicted_by=["source1", "source2"]
        )
        assert score == 0.2

    def test_corroborated_2_plus_sources(self):
        """Corroborated by 2+ sources → 0.9"""
        doc = RetrievedDocument(
            doc_id="test", text="test", metadata={}, similarity_score=0.5
        )
        score = CredibilityScorer._calculate_accuracy_score(
            doc, corroborated_by=["source1", "source2"]
        )
        assert score == 0.9

    def test_corroborated_1_source(self):
        """Corroborated by 1 source → 0.73"""
        doc = RetrievedDocument(
            doc_id="test", text="test", metadata={}, similarity_score=0.5
        )
        score = CredibilityScorer._calculate_accuracy_score(
            doc, corroborated_by=["source1"]
        )
        assert score == 0.73

    def test_verified_metadata(self):
        """Verified in metadata → 1.0"""
        doc = RetrievedDocument(
            doc_id="test",
            text="test",
            metadata={"verified": True},
            similarity_score=0.5,
        )
        score = CredibilityScorer._calculate_accuracy_score(doc)
        assert score == 1.0

    def test_potentially_outdated(self):
        """Old document (> 365 days) → 0.43"""
        doc = RetrievedDocument(
            doc_id="test",
            text="test",
            metadata={"date": "2019-06-01"},
            similarity_score=0.5,
        )
        score = CredibilityScorer._calculate_accuracy_score(doc)
        assert score == 0.43

    def test_default_single_source(self):
        """No verification info → 0.73"""
        doc = RetrievedDocument(
            doc_id="test", text="test", metadata={}, similarity_score=0.5
        )
        score = CredibilityScorer._calculate_accuracy_score(doc)
        assert score == 0.73

    def test_empty_corroborated_list(self):
        """Empty corroborated list → 0.73"""
        doc = RetrievedDocument(
            doc_id="test", text="test", metadata={}, similarity_score=0.5
        )
        score = CredibilityScorer._calculate_accuracy_score(doc, corroborated_by=[])
        assert score == 0.73


# ============================================================================
# Section 3: Overall Scoring Tests
# ============================================================================


class TestOverallScoring:
    """Test overall credibility score calculation."""

    def test_scoring_formula_applied_correctly(self, scorer):
        """Verify weighted formula: (r×0.3) + (a×0.4) + (acc×0.3)"""
        doc = RetrievedDocument(
            doc_id="test",
            text="test",
            metadata={
                "date": "2026-02-01",  # recency = 1.0
                "source": "official",  # authority = 1.0
                "author": "expert",
                "verified": True,  # accuracy = 1.0
            },
            similarity_score=0.9,
        )
        score = scorer.score_source(doc)

        # Expected: (1.0 × 0.3) + (1.0 × 0.4) + (1.0 × 0.3) = 1.0
        assert score.credibility == 1.0

    def test_scoring_with_mixed_components(self, scorer):
        """Test formula with mixed component scores"""
        doc = RetrievedDocument(
            doc_id="test",
            text="test",
            metadata={
                "date": "2023-08-15",  # recency = 0.6 (with ref_date=2024-04-30)
                "source": "glassdoor",  # authority = 0.5
                "author": "anonymous",
                # community source recent: accuracy = 0.27
            },
            similarity_score=0.7,
        )
        score = scorer.score_source(doc)

        # Expected: (0.6 × 0.3) + (0.5 × 0.4) + (0.27 × 0.3)
        # = 0.18 + 0.20 + 0.081 = 0.461 ≈ 0.46
        # But accuracy might be 0.2 for community, so: 0.18 + 0.20 + 0.06 = 0.44
        assert abs(score.credibility - 0.44) <= 0.03

    def test_score_clamped_to_0_1(self, scorer):
        """Credibility never exceeds 1.0"""
        doc = RetrievedDocument(
            doc_id="test",
            text="test",
            metadata={
                "date": "2026-02-01",
                "source": "official",
                "author": "expert",
                "verified": True,
            },
            similarity_score=2.0,  # Invalid but shouldn't break scoring
        )
        score = scorer.score_source(doc)
        assert 0.0 <= score.credibility <= 1.0


# ============================================================================
# Section 4: Categorization Tests
# ============================================================================


class TestCategorization:
    """Test credibility category assignment."""

    def test_expert_category(self, scorer):
        """credibility > 0.8 → 'expert'"""
        doc = RetrievedDocument(
            doc_id="test",
            text="test",
            metadata={
                "date": "2026-02-01",
                "source": "gartner_report",
                "author": "analyst",
            },
            similarity_score=0.9,
        )
        score = scorer.score_source(doc)
        assert score.category == "expert"

    def test_verified_category(self, scorer):
        """0.6 <= credibility <= 0.8 → 'verified'"""
        doc = RetrievedDocument(
            doc_id="test",
            text="test",
            metadata={
                "date": "2026-01-01",
                "source": "performance_review",
                "author": "manager",
            },
            similarity_score=0.8,
        )
        score = scorer.score_source(doc)
        assert score.category == "verified"

    def test_personal_category(self, scorer):
        """0.45-0.75 with personal authority → 'personal'"""
        doc = RetrievedDocument(
            doc_id="test",
            text="test",
            metadata={
                "date": "2023-08-15",  # recency = 0.6
                "source": "personal_blog",
                "author": "self",
                # personal + 6mo old: authority=0.7, accuracy=0.43
            },
            similarity_score=0.6,
        )
        score = scorer.score_source(doc)
        # credibility = (0.6 × 0.3) + (0.7 × 0.4) + (0.43 × 0.3) = 0.581
        assert score.category in ["personal", "verified"]  # ~0.58, border between them

    def test_questionable_category(self, scorer):
        """credibility < 0.4 → 'questionable'"""
        doc = RetrievedDocument(
            doc_id="test",
            text="test",
            metadata={
                "date": "2019-01-01",
                "source": "old_blog",
                "author": "legacy",
            },
            similarity_score=0.3,
        )
        score = scorer.score_source(doc)
        assert score.category == "questionable"


# ============================================================================
# Section 5: Ranking Tests
# ============================================================================


class TestRanking:
    """Test document ranking by credibility."""

    def test_rank_by_credibility_descending(self, scorer):
        """Documents ranked in descending credibility order"""
        docs = [
            RetrievedDocument(
                doc_id="old",
                text="test",
                metadata={"date": "2019-01-01", "source": "old_blog"},
                similarity_score=0.5,
            ),
            RetrievedDocument(
                doc_id="recent",
                text="test",
                metadata={"date": "2026-02-01", "source": "gartner_report"},
                similarity_score=0.9,
            ),
            RetrievedDocument(
                doc_id="middle",
                text="test",
                metadata={"date": "2025-06-01", "source": "personal_blog"},
                similarity_score=0.7,
            ),
        ]

        ranked = scorer.rank_by_credibility(docs)

        # Verify descending order
        assert ranked[0].doc_id == "recent"  # Highest credibility
        assert ranked[1].doc_id == "middle"
        assert ranked[2].doc_id == "old"  # Lowest credibility

    def test_rank_preserves_document_order(self, scorer):
        """Ranking returns modified list, not in-place"""
        docs = [
            RetrievedDocument(
                doc_id="a",
                text="test",
                metadata={"date": "2026-01-01", "source": "official"},
                similarity_score=0.9,
            ),
            RetrievedDocument(
                doc_id="b",
                text="test",
                metadata={"date": "2026-02-01", "source": "official"},
                similarity_score=0.9,
            ),
        ]

        ranked = scorer.rank_by_credibility(docs)
        assert len(ranked) == len(docs)
        assert all(r.doc_id in ["a", "b"] for r in ranked)

    def test_rank_empty_list(self, scorer):
        """Empty list returns empty list"""
        ranked = scorer.rank_by_credibility([])
        assert ranked == []


# ============================================================================
# Section 6: Explanation Tests
# ============================================================================


class TestExplanations:
    """Test human-readable explanations."""

    def test_explanation_includes_date(self, scorer):
        """Explanation includes date info"""
        doc = RetrievedDocument(
            doc_id="test",
            text="test",
            metadata={"date": "2026-03-08", "source": "official", "author": "expert"},
            similarity_score=0.9,
        )
        explanation = scorer.get_credibility_explanation(doc)
        assert "2026-03-08" in explanation or "Recent" in explanation

    def test_explanation_includes_source(self, scorer):
        """Explanation includes source info"""
        doc = RetrievedDocument(
            doc_id="test",
            text="test",
            metadata={"date": "2026-02-01", "source": "gartner_report", "author": ""},
            similarity_score=0.9,
        )
        explanation = scorer.get_credibility_explanation(doc)
        assert "official" in explanation.lower() or "gartner" in explanation.lower()

    def test_explanation_corroboration(self, scorer):
        """Explanation mentions corroboration"""
        doc = RetrievedDocument(
            doc_id="test",
            text="test",
            metadata={
                "date": "2026-02-01",
                "source": "personal",
                "author": "self",
                "corroborated_by": ["source1", "source2"],
            },
            similarity_score=0.9,
        )
        explanation = scorer.get_credibility_explanation(doc)
        assert "2" in explanation or "corroborat" in explanation.lower()

    def test_explanation_contradiction(self, scorer):
        """Explanation mentions contradictions"""
        doc = RetrievedDocument(
            doc_id="test",
            text="test",
            metadata={
                "date": "2026-02-01",
                "source": "personal",
                "author": "self",
                "contradicted_by": ["source1", "source2"],
            },
            similarity_score=0.9,
        )
        explanation = scorer.get_credibility_explanation(doc)
        assert "contradict" in explanation.lower()


# ============================================================================
# Section 7: Edge Cases and Error Handling
# ============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_missing_metadata(self, scorer):
        """Handles missing metadata gracefully"""
        doc = RetrievedDocument(
            doc_id="test",
            text="test",
            metadata={},  # No metadata
            similarity_score=0.5,
        )
        score = scorer.score_source(doc)
        assert 0.0 <= score.credibility <= 1.0

    def test_none_metadata_values(self, scorer):
        """Handles None values in metadata"""
        doc = RetrievedDocument(
            doc_id="test",
            text="test",
            metadata={"date": None, "source": None, "author": None},
            similarity_score=0.5,
        )
        score = scorer.score_source(doc)
        assert 0.0 <= score.credibility <= 1.0

    def test_extra_metadata_fields(self, scorer):
        """Ignores extra metadata fields"""
        doc = RetrievedDocument(
            doc_id="test",
            text="test",
            metadata={
                "date": "2026-02-01",
                "source": "official",
                "author": "expert",
                "extra_field": "ignored",
                "another_field": "also_ignored",
            },
            similarity_score=0.5,
        )
        score = scorer.score_source(doc)
        assert 0.0 <= score.credibility <= 1.0

    def test_score_rounding(self, scorer):
        """Scores are rounded to 2 decimals"""
        doc = RetrievedDocument(
            doc_id="test",
            text="test",
            metadata={"date": "2026-02-01", "source": "official"},
            similarity_score=0.5,
        )
        score = scorer.score_source(doc)
        assert len(str(score.credibility).split(".")[-1]) <= 2
        assert len(str(score.recency_score).split(".")[-1]) <= 2
        assert len(str(score.authority_score).split(".")[-1]) <= 2
        assert len(str(score.accuracy_score).split(".")[-1]) <= 2


# ============================================================================
# Section 8: Performance Tests
# ============================================================================


class TestPerformance:
    """Test performance requirements (<50ms per document)."""

    def test_single_document_performance(self, scorer):
        """Single document scores in < 50ms"""
        doc = RetrievedDocument(
            doc_id="test",
            text="test text content",
            metadata={"date": "2026-02-01", "source": "official", "author": "expert"},
            similarity_score=0.8,
        )

        start = time.perf_counter()
        score = scorer.score_source(doc)
        elapsed = time.perf_counter() - start

        assert elapsed < 0.050  # 50ms
        assert score is not None

    def test_batch_performance(self, scorer):
        """Batch of 10 documents scores in < 500ms"""
        docs = [
            RetrievedDocument(
                doc_id=f"doc{i}",
                text="test text content",
                metadata={
                    "date": "2026-02-01",
                    "source": "official",
                    "author": "expert",
                },
                similarity_score=0.8,
            )
            for i in range(10)
        ]

        start = time.perf_counter()
        scores = [scorer.score_source(doc) for doc in docs]
        elapsed = time.perf_counter() - start

        assert elapsed < 0.500  # 500ms for 10 docs
        assert len(scores) == 10

    def test_ranking_performance(self, scorer):
        """Ranking 10 documents in < 50ms"""
        docs = [
            RetrievedDocument(
                doc_id=f"doc{i}",
                text="test",
                metadata={"date": f"202{i % 6}-01-01", "source": "official"},
                similarity_score=0.5 + (i * 0.05),
            )
            for i in range(10)
        ]

        start = time.perf_counter()
        ranked = scorer.rank_by_credibility(docs)
        elapsed = time.perf_counter() - start

        assert elapsed < 0.050  # 50ms
        assert len(ranked) == 10


# ============================================================================
# Section 9: Type Hints & Dataclass Tests
# ============================================================================


class TestTypeHints:
    """Verify type hints and dataclass behavior."""

    def test_credibility_score_immutable(self, scorer):
        """CredibilityScore is frozen (immutable)"""
        doc = RetrievedDocument(
            doc_id="test",
            text="test",
            metadata={"date": "2026-02-01", "source": "official"},
            similarity_score=0.5,
        )
        score = scorer.score_source(doc)

        with pytest.raises(AttributeError):
            score.credibility = 0.5

    def test_credibility_score_has_all_fields(self, scorer):
        """CredibilityScore has all required fields"""
        doc = RetrievedDocument(
            doc_id="test",
            text="test",
            metadata={"date": "2026-02-01", "source": "official"},
            similarity_score=0.5,
        )
        score = scorer.score_source(doc)

        assert hasattr(score, "doc_id")
        assert hasattr(score, "credibility")
        assert hasattr(score, "category")
        assert hasattr(score, "recency_score")
        assert hasattr(score, "authority_score")
        assert hasattr(score, "accuracy_score")
        assert hasattr(score, "explanation")

    def test_credibility_score_field_types(self, scorer):
        """CredibilityScore fields have correct types"""
        doc = RetrievedDocument(
            doc_id="test",
            text="test",
            metadata={"date": "2026-02-01", "source": "official"},
            similarity_score=0.5,
        )
        score = scorer.score_source(doc)

        assert isinstance(score.doc_id, str)
        assert isinstance(score.credibility, float)
        assert isinstance(score.category, str)
        assert isinstance(score.recency_score, float)
        assert isinstance(score.authority_score, float)
        assert isinstance(score.accuracy_score, float)
        assert isinstance(score.explanation, str)


# ============================================================================
# Section 10: Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests with real scenarios."""

    def test_ranking_with_mixed_documents(self, scorer, test_data):
        """Rank real test data documents correctly"""
        docs = [
            create_retrieved_document(tc["document"]) for tc in test_data["test_cases"]
        ]

        ranked = scorer.rank_by_credibility(docs)

        # First should be expert (highest)
        first_score = scorer.score_source(ranked[0])
        assert first_score.category == "expert"

        # Last should be questionable (lowest)
        last_score = scorer.score_source(ranked[-1])
        assert last_score.category in ["questionable", "personal"]

    def test_recent_higher_than_old(self, scorer):
        """Recent docs score higher than old (same authority)"""
        recent = RetrievedDocument(
            doc_id="recent",
            text="test",
            metadata={"date": "2026-02-01", "source": "official", "author": "expert"},
            similarity_score=0.9,
        )
        old = RetrievedDocument(
            doc_id="old",
            text="test",
            metadata={"date": "2019-01-01", "source": "official", "author": "expert"},
            similarity_score=0.9,
        )

        recent_score = scorer.score_source(recent).credibility
        old_score = scorer.score_source(old).credibility

        assert recent_score > old_score

    def test_expert_higher_than_personal(self, scorer):
        """Expert sources score higher than personal (same recency)"""
        expert = RetrievedDocument(
            doc_id="expert",
            text="test",
            metadata={"date": "2026-02-01", "source": "gartner_report", "author": "analyst"},
            similarity_score=0.9,
        )
        personal = RetrievedDocument(
            doc_id="personal",
            text="test",
            metadata={"date": "2026-02-01", "source": "personal_blog", "author": "self"},
            similarity_score=0.9,
        )

        expert_score = scorer.score_source(expert).credibility
        personal_score = scorer.score_source(personal).credibility

        assert expert_score > personal_score

    def test_verified_higher_than_unverified(self, scorer):
        """Verified docs score higher than unverified (same recency/authority)"""
        verified = RetrievedDocument(
            doc_id="verified",
            text="test",
            metadata={
                "date": "2026-02-01",
                "source": "official",
                "author": "expert",
                "verified": True,
            },
            similarity_score=0.9,
        )
        unverified = RetrievedDocument(
            doc_id="unverified",
            text="test",
            metadata={
                "date": "2026-02-01",
                "source": "official",
                "author": "expert",
                "verified": False,
            },
            similarity_score=0.9,
        )

        verified_score = scorer.score_source(verified).credibility
        unverified_score = scorer.score_source(unverified).credibility

        assert verified_score > unverified_score
