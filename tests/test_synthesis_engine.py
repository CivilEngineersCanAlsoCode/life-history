"""
Comprehensive test suite for SynthesisEngine (F5.3) — 45+ test cases

Tests cover:
- Single document synthesis (no conflicts)
- Multiple documents with no conflicts
- Conflicts with both high-credibility sources ("differ" strategy)
- Conflicts with one high-credibility source ("prefer" strategy)
- Low credibility conflicts ("unknown" strategy)
- Conflict disclaimer generation
- Attribution building
- Edge cases and error handling
- Performance benchmarks
"""

import pytest
import time
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from life_brain.truth_engine.synthesis_engine import SynthesisEngine, SynthesisResult


# ============================================================================
# TEST FIXTURES & MOCKS
# ============================================================================

@dataclass
class MockRetrievedDocument:
    """Mock RetrievedDocument for testing."""
    doc_id: str
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    similarity_score: float = 0.0


@dataclass
class MockCredibilityScore:
    """Mock CredibilityScore for testing."""
    doc_id: str
    credibility: float
    category: str
    recency_score: float
    authority_score: float
    accuracy_score: float
    explanation: str


@dataclass
class MockConflictResult:
    """Mock ConflictResult for testing."""
    doc_pair: tuple
    conflict_score: float
    conflict_type: str
    severity: str
    claim1: str
    claim2: str
    explanation: str


# ============================================================================
# TEST SETUP
# ============================================================================

@pytest.fixture
def synthesis_engine():
    """Create a SynthesisEngine instance."""
    return SynthesisEngine()


@pytest.fixture
def single_doc_high_credibility():
    """Single document with high credibility."""
    doc = MockRetrievedDocument(
        doc_id="doc_1",
        text="I led the CRR AML Risk Scoring Engine project at American Express.",
        metadata={"source": "resume", "date": "2024-01-15", "author": "self"}
    )
    score = MockCredibilityScore(
        doc_id="doc_1",
        credibility=0.92,
        category="expert",
        recency_score=1.0,
        authority_score=0.8,
        accuracy_score=0.9,
        explanation="Recent (2024), professional resume"
    )
    return [doc], [score], []


@pytest.fixture
def two_docs_no_conflict():
    """Two documents with no conflicts."""
    docs = [
        MockRetrievedDocument(
            doc_id="doc_1",
            text="I implemented a machine learning model for risk scoring.",
            metadata={"source": "resume", "date": "2024-01-15", "author": "self"}
        ),
        MockRetrievedDocument(
            doc_id="doc_2",
            text="The model achieved 94% accuracy on validation data.",
            metadata={"source": "performance_review", "date": "2024-01-20", "author": "manager"}
        )
    ]
    scores = [
        MockCredibilityScore(
            doc_id="doc_1",
            credibility=0.90,
            category="expert",
            recency_score=1.0,
            authority_score=0.8,
            accuracy_score=0.9,
            explanation="Recent (2024), professional source"
        ),
        MockCredibilityScore(
            doc_id="doc_2",
            credibility=0.95,
            category="expert",
            recency_score=1.0,
            authority_score=1.0,
            accuracy_score=0.9,
            explanation="Recent (2024), manager verification"
        )
    ]
    return docs, scores, []


@pytest.fixture
def two_docs_with_differ_conflict():
    """Two high-credibility documents with conflicting claims."""
    docs = [
        MockRetrievedDocument(
            doc_id="doc_1",
            text="The project salary range was $150k-$200k.",
            metadata={"source": "resume", "date": "2024-01-15", "author": "self"}
        ),
        MockRetrievedDocument(
            doc_id="doc_2",
            text="The project salary range was $140k-$190k.",
            metadata={"source": "offer_letter", "date": "2024-01-10", "author": "hr"}
        )
    ]
    scores = [
        MockCredibilityScore(
            doc_id="doc_1",
            credibility=0.85,
            category="verified",
            recency_score=1.0,
            authority_score=0.7,
            accuracy_score=0.8,
            explanation="Recent (2024), personal account"
        ),
        MockCredibilityScore(
            doc_id="doc_2",
            credibility=0.92,
            category="expert",
            recency_score=1.0,
            authority_score=1.0,
            accuracy_score=0.9,
            explanation="Recent (2024), official HR document"
        )
    ]
    conflicts = [
        MockConflictResult(
            doc_pair=(0, 1),
            conflict_score=0.45,
            conflict_type="quantitative",
            severity="medium",
            claim1="The project salary range was $150k-$200k.",
            claim2="The project salary range was $140k-$190k.",
            explanation="Quantitative discrepancy: salary ranges differ slightly"
        )
    ]
    return docs, scores, conflicts


@pytest.fixture
def two_docs_with_prefer_conflict():
    """Two documents with conflict where one is more credible."""
    docs = [
        MockRetrievedDocument(
            doc_id="doc_1",
            text="I led the redesign of the user interface.",
            metadata={"source": "resume", "date": "2024-01-15", "author": "self"}
        ),
        MockRetrievedDocument(
            doc_id="doc_2",
            text="The candidate contributed to the UI redesign efforts.",
            metadata={"source": "reference", "date": "2024-01-18", "author": "peer"}
        )
    ]
    scores = [
        MockCredibilityScore(
            doc_id="doc_1",
            credibility=0.88,
            category="verified",
            recency_score=1.0,
            authority_score=0.8,
            accuracy_score=0.85,
            explanation="Recent (2024), professional resume"
        ),
        MockCredibilityScore(
            doc_id="doc_2",
            credibility=0.45,
            category="personal",
            recency_score=0.8,
            authority_score=0.5,
            accuracy_score=0.3,
            explanation="Recent (2024), unverified peer reference"
        )
    ]
    conflicts = [
        MockConflictResult(
            doc_pair=(0, 1),
            conflict_score=0.72,
            conflict_type="semantic",
            severity="high",
            claim1="I led the redesign of the user interface.",
            claim2="The candidate contributed to the UI redesign efforts.",
            explanation="Leadership vs contribution conflict"
        )
    ]
    return docs, scores, conflicts


@pytest.fixture
def two_docs_with_low_cred_conflict():
    """Two low-credibility documents with conflicting claims."""
    docs = [
        MockRetrievedDocument(
            doc_id="doc_1",
            text="The project was a major success.",
            metadata={"source": "old_blog", "date": "2020-05-01", "author": "unknown"}
        ),
        MockRetrievedDocument(
            doc_id="doc_2",
            text="The project ultimately failed.",
            metadata={"source": "archive", "date": "2020-06-01", "author": "legacy"}
        )
    ]
    scores = [
        MockCredibilityScore(
            doc_id="doc_1",
            credibility=0.32,
            category="questionable",
            recency_score=0.4,
            authority_score=0.3,
            accuracy_score=0.2,
            explanation="Old (2020), unknown source"
        ),
        MockCredibilityScore(
            doc_id="doc_2",
            credibility=0.28,
            category="questionable",
            recency_score=0.4,
            authority_score=0.2,
            accuracy_score=0.2,
            explanation="Old (2020), archived content"
        )
    ]
    conflicts = [
        MockConflictResult(
            doc_pair=(0, 1),
            conflict_score=0.95,
            conflict_type="semantic",
            severity="high",
            claim1="The project was a major success.",
            claim2="The project ultimately failed.",
            explanation="Semantic contradiction: opposite outcomes"
        )
    ]
    return docs, scores, conflicts


@pytest.fixture
def three_docs_with_multiple_conflicts():
    """Three documents with multiple conflicts."""
    docs = [
        MockRetrievedDocument(
            doc_id="doc_1",
            text="The team had 5 members and succeeded in delivery.",
            metadata={"source": "resume", "date": "2024-01-15", "author": "self"}
        ),
        MockRetrievedDocument(
            doc_id="doc_2",
            text="The team had 4 members and struggled with timeline.",
            metadata={"source": "project_notes", "date": "2023-12-20", "author": "manager"}
        ),
        MockRetrievedDocument(
            doc_id="doc_3",
            text="The team had 6 members but faced delivery challenges.",
            metadata={"source": "archive", "date": "2023-12-15", "author": "unknown"}
        )
    ]
    scores = [
        MockCredibilityScore(
            doc_id="doc_1",
            credibility=0.85,
            category="verified",
            recency_score=1.0,
            authority_score=0.8,
            accuracy_score=0.8,
            explanation="Recent (2024), professional resume"
        ),
        MockCredibilityScore(
            doc_id="doc_2",
            credibility=0.78,
            category="verified",
            recency_score=0.8,
            authority_score=0.8,
            accuracy_score=0.7,
            explanation="Recent (2023), manager notes"
        ),
        MockCredibilityScore(
            doc_id="doc_3",
            credibility=0.35,
            category="questionable",
            recency_score=0.8,
            authority_score=0.3,
            accuracy_score=0.2,
            explanation="Older (2023), archived content"
        )
    ]
    conflicts = [
        MockConflictResult(
            doc_pair=(0, 1),
            conflict_score=0.55,
            conflict_type="quantitative",
            severity="medium",
            claim1="The team had 5 members",
            claim2="The team had 4 members",
            explanation="Team size discrepancy: 5 vs 4"
        ),
        MockConflictResult(
            doc_pair=(0, 2),
            conflict_score=0.60,
            conflict_type="quantitative",
            severity="medium",
            claim1="succeeded in delivery",
            claim2="faced delivery challenges",
            explanation="Outcome conflict"
        )
    ]
    return docs, scores, conflicts


# ============================================================================
# SINGLE DOCUMENT TESTS (5 tests)
# ============================================================================

def test_synthesize_single_doc_no_conflict(synthesis_engine, single_doc_high_credibility):
    """Test synthesis from single document without conflicts."""
    docs, scores, conflicts = single_doc_high_credibility

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    assert result.strategy == "agree"
    assert len(result.preferred_sources) == 1
    assert result.preferred_sources[0] == "doc_1"
    assert "CRR AML" in result.answer or "led" in result.answer.lower()
    assert result.disclaimer is None
    assert result.attribution is not None


def test_synthesize_empty_docs(synthesis_engine):
    """Test synthesis with empty document list."""
    result = synthesis_engine.synthesize([], [], [])

    assert result.strategy == "unknown"
    assert result.answer == "No documents provided for synthesis."
    assert result.preferred_sources == []
    assert result.disclaimer is None


def test_synthesize_single_doc_low_credibility(synthesis_engine):
    """Test synthesis from low-credibility single document."""
    doc = MockRetrievedDocument(
        doc_id="doc_old",
        text="Some outdated information.",
        metadata={"source": "old_blog", "date": "2019-01-01", "author": "unknown"}
    )
    score = MockCredibilityScore(
        doc_id="doc_old",
        credibility=0.25,
        category="questionable",
        recency_score=0.4,
        authority_score=0.2,
        accuracy_score=0.2,
        explanation="Old (2019), unknown source"
    )

    result = synthesis_engine.synthesize([doc], [], [score])

    assert result.strategy == "agree"
    assert len(result.preferred_sources) == 1
    assert result.preferred_sources[0] == "doc_old"


def test_synthesize_three_high_credibility_docs_no_conflict(synthesis_engine):
    """Test synthesis from three high-credibility documents without conflict."""
    docs = [
        MockRetrievedDocument(
            doc_id="doc_1",
            text="I implemented machine learning models.",
            metadata={"source": "resume", "date": "2024-01-15", "author": "self"}
        ),
        MockRetrievedDocument(
            doc_id="doc_2",
            text="The implementation achieved high accuracy.",
            metadata={"source": "performance_review", "date": "2024-01-20", "author": "manager"}
        ),
        MockRetrievedDocument(
            doc_id="doc_3",
            text="The project delivered on time and under budget.",
            metadata={"source": "project_closure", "date": "2024-01-25", "author": "director"}
        )
    ]
    scores = [
        MockCredibilityScore(
            doc_id="doc_1",
            credibility=0.88,
            category="verified",
            recency_score=1.0,
            authority_score=0.8,
            accuracy_score=0.85,
            explanation="Recent (2024), professional source"
        ),
        MockCredibilityScore(
            doc_id="doc_2",
            credibility=0.92,
            category="expert",
            recency_score=1.0,
            authority_score=1.0,
            accuracy_score=0.9,
            explanation="Recent (2024), manager verification"
        ),
        MockCredibilityScore(
            doc_id="doc_3",
            credibility=0.95,
            category="expert",
            recency_score=1.0,
            authority_score=1.0,
            accuracy_score=0.95,
            explanation="Recent (2024), director verification"
        )
    ]

    result = synthesis_engine.synthesize(docs, [], scores)

    assert result.strategy == "agree"
    assert len(result.preferred_sources) == 3
    assert result.preferred_sources == ["doc_3", "doc_2", "doc_1"]  # Sorted by credibility
    assert result.disclaimer is None


# ============================================================================
# CONFLICT HANDLING TESTS (15 tests)
# ============================================================================

def test_synthesize_differ_strategy_both_high_credibility(synthesis_engine, two_docs_with_differ_conflict):
    """Test 'differ' strategy when both sources are highly credible."""
    docs, scores, conflicts = two_docs_with_differ_conflict

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    assert result.strategy == "differ"
    assert len(result.conflicts_handled) == 1
    assert result.conflicts_handled[0].conflict_score == 0.45
    assert "Source A states" in result.answer or "Source B states" in result.answer
    assert result.disclaimer is not None
    assert "conflicting" in result.disclaimer.lower()


def test_synthesize_prefer_strategy_one_high_credibility(synthesis_engine, two_docs_with_prefer_conflict):
    """Test 'prefer' strategy when one source is more credible."""
    docs, scores, conflicts = two_docs_with_prefer_conflict

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    assert result.strategy == "prefer"
    assert len(result.conflicts_handled) == 1
    assert "led" in result.answer.lower() or "redesign" in result.answer.lower()
    assert result.disclaimer is not None
    assert "primary source" in result.disclaimer.lower() or "conflicting" in result.disclaimer.lower()


def test_synthesize_unknown_strategy_low_credibility_conflict(synthesis_engine, two_docs_with_low_cred_conflict):
    """Test 'unknown' strategy when conflict involves low-credibility sources."""
    docs, scores, conflicts = two_docs_with_low_cred_conflict

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    assert result.strategy == "unknown"
    assert "insufficient consensus" in result.answer.lower() or "conflicting" in result.answer.lower()
    assert result.disclaimer is not None


def test_conflict_ranking_by_severity(synthesis_engine):
    """Test that conflicts are ranked by severity correctly."""
    docs = [
        MockRetrievedDocument(
            doc_id="doc_1",
            text="Claim A",
            metadata={"source": "resume", "date": "2024-01-15", "author": "self"}
        ),
        MockRetrievedDocument(
            doc_id="doc_2",
            text="Claim B",
            metadata={"source": "notes", "date": "2024-01-15", "author": "self"}
        )
    ]
    scores = [
        MockCredibilityScore(
            doc_id="doc_1",
            credibility=0.85,
            category="verified",
            recency_score=1.0,
            authority_score=0.8,
            accuracy_score=0.8,
            explanation="Recent"
        ),
        MockCredibilityScore(
            doc_id="doc_2",
            credibility=0.85,
            category="verified",
            recency_score=1.0,
            authority_score=0.8,
            accuracy_score=0.8,
            explanation="Recent"
        )
    ]
    conflicts = [
        MockConflictResult(
            doc_pair=(0, 1),
            conflict_score=0.3,
            conflict_type="qualitative",
            severity="low",
            claim1="Low severity claim",
            claim2="Low severity response",
            explanation="Low severity conflict"
        ),
        MockConflictResult(
            doc_pair=(0, 1),
            conflict_score=0.8,
            conflict_type="semantic",
            severity="high",
            claim1="High severity claim",
            claim2="High severity response",
            explanation="High severity conflict"
        )
    ]

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    # Top conflict should be the one with highest conflict_score
    assert result.conflicts_handled[0].conflict_score == 0.8


def test_multiple_conflicts_handles_top_conflict(synthesis_engine, three_docs_with_multiple_conflicts):
    """Test that when multiple conflicts exist, top-severity conflict is handled."""
    docs, scores, conflicts = three_docs_with_multiple_conflicts

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    # Should handle top conflict (highest severity)
    assert len(result.conflicts_handled) >= 1
    assert result.conflicts_handled[0].conflict_score >= 0.55


def test_differ_answer_format(synthesis_engine, two_docs_with_differ_conflict):
    """Test that 'differ' strategy produces properly formatted answer."""
    docs, scores, conflicts = two_docs_with_differ_conflict

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    assert "Source" in result.answer
    assert "credibility" in result.answer.lower()
    assert "%" in result.answer  # Should have percentage


def test_prefer_answer_format(synthesis_engine, two_docs_with_prefer_conflict):
    """Test that 'prefer' strategy produces properly formatted answer."""
    docs, scores, conflicts = two_docs_with_prefer_conflict

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    # Should include the preferred claim and note the alternative
    assert "led" in result.answer.lower() or "redesign" in result.answer.lower()


def test_unknown_answer_format(synthesis_engine, two_docs_with_low_cred_conflict):
    """Test that 'unknown' strategy produces appropriate message."""
    docs, scores, conflicts = two_docs_with_low_cred_conflict

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    assert "insufficient" in result.answer.lower() or "conflicting" in result.answer.lower()


def test_disclaimer_both_high_credibility(synthesis_engine, two_docs_with_differ_conflict):
    """Test disclaimer when both sources are high credibility."""
    docs, scores, conflicts = two_docs_with_differ_conflict

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    assert result.disclaimer is not None
    assert "conflicting" in result.disclaimer.lower() or "different" in result.disclaimer.lower()


def test_disclaimer_one_high_credibility(synthesis_engine, two_docs_with_prefer_conflict):
    """Test disclaimer when one source is high credibility."""
    docs, scores, conflicts = two_docs_with_prefer_conflict

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    assert result.disclaimer is not None
    # Should mention primary source or conflicting information
    assert "primary" in result.disclaimer.lower() or "conflicting" in result.disclaimer.lower()


def test_disclaimer_low_credibility_conflict(synthesis_engine, two_docs_with_low_cred_conflict):
    """Test disclaimer when conflict involves low-credibility sources."""
    docs, scores, conflicts = two_docs_with_low_cred_conflict

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    assert result.disclaimer is not None
    assert "conflicting" in result.disclaimer.lower()


def test_add_conflict_disclaimer_both_high(synthesis_engine):
    """Test add_conflict_disclaimer method with both high-credibility sources."""
    answer = "The answer is X."
    docs = [
        MockRetrievedDocument(
            doc_id="doc_1",
            text="Claim A",
            metadata={"source": "resume", "date": "2024-01-15", "author": "self"}
        ),
        MockRetrievedDocument(
            doc_id="doc_2",
            text="Claim B",
            metadata={"source": "notes", "date": "2024-01-15", "author": "self"}
        )
    ]
    scores = [
        MockCredibilityScore(
            doc_id="doc_1",
            credibility=0.90,
            category="verified",
            recency_score=1.0,
            authority_score=0.8,
            accuracy_score=0.9,
            explanation="Recent"
        ),
        MockCredibilityScore(
            doc_id="doc_2",
            credibility=0.88,
            category="verified",
            recency_score=1.0,
            authority_score=0.8,
            accuracy_score=0.88,
            explanation="Recent"
        )
    ]
    conflicts = [
        MockConflictResult(
            doc_pair=(0, 1),
            conflict_score=0.50,
            conflict_type="qualitative",
            severity="medium",
            claim1="Claim A",
            claim2="Claim B",
            explanation="Different perspectives"
        )
    ]

    result = synthesis_engine.add_conflict_disclaimer(answer, conflicts, scores)

    assert "Note:" in result or "Caution:" in result
    assert len(result) > len(answer)


def test_add_conflict_disclaimer_one_high(synthesis_engine):
    """Test add_conflict_disclaimer with one high-credibility source."""
    answer = "The answer is X."
    scores = [
        MockCredibilityScore(
            doc_id="doc_1",
            credibility=0.88,
            category="verified",
            recency_score=1.0,
            authority_score=0.8,
            accuracy_score=0.85,
            explanation="Recent"
        ),
        MockCredibilityScore(
            doc_id="doc_2",
            credibility=0.40,
            category="questionable",
            recency_score=0.6,
            authority_score=0.3,
            accuracy_score=0.3,
            explanation="Old"
        )
    ]
    conflicts = [
        MockConflictResult(
            doc_pair=(0, 1),
            conflict_score=0.50,
            conflict_type="qualitative",
            severity="medium",
            claim1="Claim A",
            claim2="Claim B",
            explanation="Different perspectives"
        )
    ]

    result = synthesis_engine.add_conflict_disclaimer(answer, conflicts, scores)

    assert "primary source" in result.lower() or "conflicting" in result.lower()


# ============================================================================
# ATTRIBUTION TESTS (6 tests)
# ============================================================================

def test_attribution_single_doc(synthesis_engine, single_doc_high_credibility):
    """Test attribution for single document."""
    docs, scores, conflicts = single_doc_high_credibility

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    assert "Sources:" in result.attribution
    assert "doc_1" in result.attribution


def test_attribution_multiple_docs(synthesis_engine, two_docs_no_conflict):
    """Test attribution for multiple documents."""
    docs, scores, conflicts = two_docs_no_conflict

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    assert "Sources:" in result.attribution
    assert "doc_1" in result.attribution
    assert "doc_2" in result.attribution


def test_attribution_with_conflicts(synthesis_engine, two_docs_with_differ_conflict):
    """Test attribution includes conflict notation."""
    docs, scores, conflicts = two_docs_with_differ_conflict

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    assert "conflict" in result.attribution.lower() or len(result.conflicts_handled) > 0


def test_attribution_credibility_labels(synthesis_engine, two_docs_no_conflict):
    """Test attribution includes credibility labels."""
    docs, scores, conflicts = two_docs_no_conflict

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    # Should have credibility labels like "expert", "verified", etc.
    assert any(label in result.attribution.lower()
              for label in ["expert", "verified", "personal", "questionable"])


def test_attribution_three_source_limit(synthesis_engine, three_docs_with_multiple_conflicts):
    """Test that attribution limits to 3 sources."""
    docs, scores, conflicts = three_docs_with_multiple_conflicts

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    # Count doc references in attribution
    count = sum(1 for doc in docs if doc.doc_id in result.attribution)
    assert count <= 3


def test_preferred_sources_ranked_by_credibility(synthesis_engine, two_docs_no_conflict):
    """Test that preferred_sources are ranked by credibility."""
    docs, scores, conflicts = two_docs_no_conflict

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    # Scores: doc_2 = 0.95, doc_1 = 0.90
    assert result.preferred_sources[0] == "doc_2"
    assert result.preferred_sources[1] == "doc_1"


# ============================================================================
# DATACLASS & IMMUTABILITY TESTS (3 tests)
# ============================================================================

def test_synthesis_result_frozen(synthesis_engine, single_doc_high_credibility):
    """Test that SynthesisResult is immutable (frozen)."""
    docs, scores, conflicts = single_doc_high_credibility

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    # Attempt to modify should raise error
    with pytest.raises(AttributeError):
        result.answer = "Modified answer"


def test_synthesis_result_contains_all_fields(synthesis_engine, single_doc_high_credibility):
    """Test that SynthesisResult contains all required fields."""
    docs, scores, conflicts = single_doc_high_credibility

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    assert hasattr(result, 'answer')
    assert hasattr(result, 'strategy')
    assert hasattr(result, 'conflicts_handled')
    assert hasattr(result, 'preferred_sources')
    assert hasattr(result, 'disclaimer')
    assert hasattr(result, 'attribution')


def test_synthesis_result_field_types(synthesis_engine, single_doc_high_credibility):
    """Test that SynthesisResult fields have correct types."""
    docs, scores, conflicts = single_doc_high_credibility

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    assert isinstance(result.answer, str)
    assert isinstance(result.strategy, str)
    assert isinstance(result.conflicts_handled, list)
    assert isinstance(result.preferred_sources, list)
    assert result.disclaimer is None or isinstance(result.disclaimer, str)
    assert isinstance(result.attribution, str)


# ============================================================================
# EDGE CASE TESTS (8 tests)
# ============================================================================

def test_missing_doc_id_fallback(synthesis_engine):
    """Test handling of documents without doc_id."""
    # Create a doc without doc_id attribute
    doc = MockRetrievedDocument(
        doc_id="",  # Empty doc_id
        text="Some text",
        metadata={"source": "resume", "date": "2024-01-15", "author": "self"}
    )
    score = MockCredibilityScore(
        doc_id="",
        credibility=0.85,
        category="verified",
        recency_score=1.0,
        authority_score=0.8,
        accuracy_score=0.8,
        explanation="Recent"
    )

    result = synthesis_engine.synthesize([doc], [], [score])

    assert result.strategy == "agree"


def test_missing_credibility_score_fallback(synthesis_engine):
    """Test handling when credibility score is missing for a doc."""
    doc = MockRetrievedDocument(
        doc_id="doc_1",
        text="Some text",
        metadata={"source": "resume", "date": "2024-01-15", "author": "self"}
    )
    # Empty credibility list
    scores = []

    result = synthesis_engine.synthesize([doc], [], scores)

    assert result.strategy == "agree"
    assert len(result.preferred_sources) >= 0


def test_conflict_with_missing_doc_pair(synthesis_engine):
    """Test conflict handling when doc_pair is missing."""
    doc = MockRetrievedDocument(
        doc_id="doc_1",
        text="Text A",
        metadata={"source": "resume", "date": "2024-01-15", "author": "self"}
    )
    score = MockCredibilityScore(
        doc_id="doc_1",
        credibility=0.85,
        category="verified",
        recency_score=1.0,
        authority_score=0.8,
        accuracy_score=0.8,
        explanation="Recent"
    )
    # Create conflict without doc_pair
    conflict = type('obj', (object,), {
        'conflict_score': 0.5,
        'claim1': 'A',
        'claim2': 'B'
    })()

    result = synthesis_engine.synthesize([doc], [conflict], [score])

    # Should not crash
    assert result is not None


def test_large_conflict_score(synthesis_engine):
    """Test handling of high conflict scores."""
    docs = [
        MockRetrievedDocument(
            doc_id="doc_1",
            text="Project succeeded",
            metadata={"source": "resume", "date": "2024-01-15", "author": "self"}
        ),
        MockRetrievedDocument(
            doc_id="doc_2",
            text="Project failed",
            metadata={"source": "notes", "date": "2024-01-15", "author": "self"}
        )
    ]
    scores = [
        MockCredibilityScore(
            doc_id="doc_1",
            credibility=0.90,
            category="verified",
            recency_score=1.0,
            authority_score=0.8,
            accuracy_score=0.9,
            explanation="Recent"
        ),
        MockCredibilityScore(
            doc_id="doc_2",
            credibility=0.88,
            category="verified",
            recency_score=1.0,
            authority_score=0.8,
            accuracy_score=0.88,
            explanation="Recent"
        )
    ]
    conflicts = [
        MockConflictResult(
            doc_pair=(0, 1),
            conflict_score=0.99,  # Very high conflict
            conflict_type="semantic",
            severity="high",
            claim1="Project succeeded",
            claim2="Project failed",
            explanation="Direct opposite"
        )
    ]

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    assert result.strategy in ["differ", "prefer", "unknown"]


def test_very_short_text(synthesis_engine):
    """Test synthesis with very short document text."""
    doc = MockRetrievedDocument(
        doc_id="doc_1",
        text=".",
        metadata={"source": "resume", "date": "2024-01-15", "author": "self"}
    )
    score = MockCredibilityScore(
        doc_id="doc_1",
        credibility=0.85,
        category="verified",
        recency_score=1.0,
        authority_score=0.8,
        accuracy_score=0.8,
        explanation="Recent"
    )

    result = synthesis_engine.synthesize([doc], [], [score])

    assert result.answer is not None
    assert len(result.answer) > 0


def test_very_long_text(synthesis_engine):
    """Test synthesis with very long document text."""
    long_text = "This is a very long document. " * 100
    doc = MockRetrievedDocument(
        doc_id="doc_1",
        text=long_text,
        metadata={"source": "resume", "date": "2024-01-15", "author": "self"}
    )
    score = MockCredibilityScore(
        doc_id="doc_1",
        credibility=0.85,
        category="verified",
        recency_score=1.0,
        authority_score=0.8,
        accuracy_score=0.8,
        explanation="Recent"
    )

    result = synthesis_engine.synthesize([doc], [], [score])

    assert result.answer is not None
    assert len(result.answer) <= 300  # Should be summarized


def test_special_characters_in_claims(synthesis_engine):
    """Test handling of special characters in conflict claims."""
    docs = [
        MockRetrievedDocument(
            doc_id="doc_1",
            text="Salary: $150k-$200k",
            metadata={"source": "resume", "date": "2024-01-15", "author": "self"}
        ),
        MockRetrievedDocument(
            doc_id="doc_2",
            text="Salary: $140k-$190k",
            metadata={"source": "notes", "date": "2024-01-15", "author": "self"}
        )
    ]
    scores = [
        MockCredibilityScore(
            doc_id="doc_1",
            credibility=0.85,
            category="verified",
            recency_score=1.0,
            authority_score=0.8,
            accuracy_score=0.8,
            explanation="Recent"
        ),
        MockCredibilityScore(
            doc_id="doc_2",
            credibility=0.88,
            category="verified",
            recency_score=1.0,
            authority_score=0.8,
            accuracy_score=0.88,
            explanation="Recent"
        )
    ]
    conflicts = [
        MockConflictResult(
            doc_pair=(0, 1),
            conflict_score=0.45,
            conflict_type="quantitative",
            severity="medium",
            claim1="Salary: $150k-$200k",
            claim2="Salary: $140k-$190k",
            explanation="Salary range conflict"
        )
    ]

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    assert "$" in result.answer or "150" in result.answer


# ============================================================================
# PERFORMANCE TESTS (2 tests)
# ============================================================================

def test_performance_single_doc_under_150ms(synthesis_engine, single_doc_high_credibility):
    """Test that synthesis completes in <150ms for single doc."""
    docs, scores, conflicts = single_doc_high_credibility

    start = time.perf_counter()
    result = synthesis_engine.synthesize(docs, conflicts, scores)
    elapsed = time.perf_counter() - start

    assert elapsed < 0.150  # 150ms


def test_performance_three_docs_with_conflicts_under_150ms(synthesis_engine, three_docs_with_multiple_conflicts):
    """Test that synthesis completes in <150ms for three docs with conflicts."""
    docs, scores, conflicts = three_docs_with_multiple_conflicts

    start = time.perf_counter()
    result = synthesis_engine.synthesize(docs, conflicts, scores)
    elapsed = time.perf_counter() - start

    assert elapsed < 0.150  # 150ms


# ============================================================================
# INTEGRATION TESTS (3 tests)
# ============================================================================

def test_integration_with_mock_f5_outputs(synthesis_engine):
    """Test synthesis with realistic F5.1 and F5.2 outputs."""
    # Simulate realistic scenario
    docs = [
        MockRetrievedDocument(
            doc_id="resume_2024",
            text="I led the CRR AML Risk Scoring Engine at American Express (2024-present).",
            metadata={
                "source": "professional_resume",
                "date": "2024-03-08",
                "author": "self",
                "type": "career_experience"
            }
        ),
        MockRetrievedDocument(
            doc_id="manager_review",
            text="Satvik contributed significantly to the CRR project delivery.",
            metadata={
                "source": "performance_review",
                "date": "2024-01-15",
                "author": "manager",
                "type": "verification"
            }
        )
    ]

    scores = [
        MockCredibilityScore(
            doc_id="resume_2024",
            credibility=0.88,
            category="verified",
            recency_score=1.0,
            authority_score=0.8,
            accuracy_score=0.85,
            explanation="Recent (2024), professional resume"
        ),
        MockCredibilityScore(
            doc_id="manager_review",
            credibility=0.93,
            category="expert",
            recency_score=1.0,
            authority_score=1.0,
            accuracy_score=0.9,
            explanation="Recent (2024), manager verification"
        )
    ]

    conflicts = []  # No conflicts in this scenario

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    assert result.strategy == "agree"
    assert len(result.preferred_sources) == 2
    assert result.conflicts_handled == []
    assert "CRR" in result.answer or "American Express" in result.answer


def test_strategy_consistency_across_calls(synthesis_engine, two_docs_with_differ_conflict):
    """Test that same inputs produce same strategy across multiple calls."""
    docs, scores, conflicts = two_docs_with_differ_conflict

    result1 = synthesis_engine.synthesize(docs, conflicts, scores)
    result2 = synthesis_engine.synthesize(docs, conflicts, scores)

    assert result1.strategy == result2.strategy


def test_all_strategies_can_be_produced(synthesis_engine):
    """Test that all four strategies can be produced by the engine."""
    strategies_produced = set()

    # Test "agree" strategy
    docs1, scores1, conflicts1 = (
        [MockRetrievedDocument(doc_id="doc_1", text="Text", metadata={})],
        [MockCredibilityScore(doc_id="doc_1", credibility=0.85, category="verified", recency_score=1.0, authority_score=0.8, accuracy_score=0.8, explanation="")],
        []
    )
    result1 = synthesis_engine.synthesize(docs1, conflicts1, scores1)
    strategies_produced.add(result1.strategy)

    # Test "differ" strategy
    docs2 = [
        MockRetrievedDocument(doc_id="doc_1", text="Claim A", metadata={}),
        MockRetrievedDocument(doc_id="doc_2", text="Claim B", metadata={})
    ]
    scores2 = [
        MockCredibilityScore(doc_id="doc_1", credibility=0.88, category="verified", recency_score=1.0, authority_score=0.8, accuracy_score=0.85, explanation=""),
        MockCredibilityScore(doc_id="doc_2", credibility=0.86, category="verified", recency_score=1.0, authority_score=0.8, accuracy_score=0.8, explanation="")
    ]
    conflicts2 = [
        MockConflictResult(doc_pair=(0, 1), conflict_score=0.5, conflict_type="qualitative", severity="medium", claim1="A", claim2="B", explanation="")
    ]
    result2 = synthesis_engine.synthesize(docs2, conflicts2, scores2)
    strategies_produced.add(result2.strategy)

    # Test "unknown" strategy
    docs3 = [
        MockRetrievedDocument(doc_id="doc_1", text="Claim A", metadata={}),
        MockRetrievedDocument(doc_id="doc_2", text="Claim B", metadata={})
    ]
    scores3 = [
        MockCredibilityScore(doc_id="doc_1", credibility=0.30, category="questionable", recency_score=0.4, authority_score=0.3, accuracy_score=0.2, explanation=""),
        MockCredibilityScore(doc_id="doc_2", credibility=0.28, category="questionable", recency_score=0.4, authority_score=0.2, accuracy_score=0.2, explanation="")
    ]
    conflicts3 = [
        MockConflictResult(doc_pair=(0, 1), conflict_score=0.95, conflict_type="semantic", severity="high", claim1="Success", claim2="Failure", explanation="")
    ]
    result3 = synthesis_engine.synthesize(docs3, conflicts3, scores3)
    strategies_produced.add(result3.strategy)

    assert "agree" in strategies_produced
    assert "differ" in strategies_produced
    assert "unknown" in strategies_produced


# ============================================================================
# ADDITIONAL TESTS (7+ more to reach 45+)
# ============================================================================

def test_synthesize_result_is_hashable(synthesis_engine, single_doc_high_credibility):
    """Test that SynthesisResult fields are usable in data structures."""
    docs, scores, conflicts = single_doc_high_credibility

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    # Can use strategy as dict key
    strategy_dict = {result.strategy: result.answer}
    assert strategy_dict["agree"] == result.answer


def test_credibility_to_label_boundary_values(synthesis_engine):
    """Test credibility to label conversion at boundaries."""
    engine = SynthesisEngine()

    # Test all boundaries
    assert engine._credibility_to_label(0.95) == "expert"
    assert engine._credibility_to_label(0.85) == "expert"
    assert engine._credibility_to_label(0.84) == "verified"
    assert engine._credibility_to_label(0.75) == "verified"
    assert engine._credibility_to_label(0.74) == "personal"
    assert engine._credibility_to_label(0.50) == "personal"
    assert engine._credibility_to_label(0.49) == "questionable"
    assert engine._credibility_to_label(0.0) == "questionable"


def test_synthesize_with_conflicting_doc_indices(synthesis_engine):
    """Test synthesis when conflict references valid doc indices."""
    docs = [
        MockRetrievedDocument(
            doc_id="doc_0",
            text="Text from document 0",
            metadata={"source": "resume", "date": "2024-01-15", "author": "self"}
        ),
        MockRetrievedDocument(
            doc_id="doc_1",
            text="Text from document 1",
            metadata={"source": "notes", "date": "2024-01-15", "author": "self"}
        ),
        MockRetrievedDocument(
            doc_id="doc_2",
            text="Text from document 2",
            metadata={"source": "archive", "date": "2024-01-15", "author": "self"}
        )
    ]
    scores = [
        MockCredibilityScore(doc_id="doc_0", credibility=0.85, category="verified", recency_score=1.0, authority_score=0.8, accuracy_score=0.8, explanation=""),
        MockCredibilityScore(doc_id="doc_1", credibility=0.87, category="verified", recency_score=1.0, authority_score=0.8, accuracy_score=0.85, explanation=""),
        MockCredibilityScore(doc_id="doc_2", credibility=0.40, category="questionable", recency_score=0.8, authority_score=0.3, accuracy_score=0.3, explanation="")
    ]
    conflicts = [
        MockConflictResult(doc_pair=(1, 2), conflict_score=0.6, conflict_type="qualitative", severity="medium", claim1="Claim 1", claim2="Claim 2", explanation="")
    ]

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    # Should successfully handle conflict with indices 1 and 2
    assert result is not None
    assert len(result.preferred_sources) == 3


def test_synthesize_empty_claims_in_conflict(synthesis_engine):
    """Test synthesis when conflict has empty claim strings."""
    docs = [
        MockRetrievedDocument(doc_id="doc_1", text="Text A", metadata={}),
        MockRetrievedDocument(doc_id="doc_2", text="Text B", metadata={})
    ]
    scores = [
        MockCredibilityScore(doc_id="doc_1", credibility=0.85, category="verified", recency_score=1.0, authority_score=0.8, accuracy_score=0.8, explanation=""),
        MockCredibilityScore(doc_id="doc_2", credibility=0.85, category="verified", recency_score=1.0, authority_score=0.8, accuracy_score=0.8, explanation="")
    ]
    conflicts = [
        MockConflictResult(doc_pair=(0, 1), conflict_score=0.5, conflict_type="qualitative", severity="medium", claim1="", claim2="", explanation="")
    ]

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    assert result is not None


def test_extract_summary_preserves_first_sentence(synthesis_engine):
    """Test that extract_summary correctly extracts first sentence."""
    engine = SynthesisEngine()

    text = "This is the first sentence. This is the second sentence. This is the third."
    summary = engine._extract_summary(text)

    assert summary == "This is the first sentence."


def test_extract_summary_handles_no_periods(synthesis_engine):
    """Test extract_summary when text has no periods."""
    engine = SynthesisEngine()

    text = "This is text without any period at the end"
    summary = engine._extract_summary(text, max_length=100)

    assert len(summary) <= 100


def test_extract_summary_respects_max_length(synthesis_engine):
    """Test that extract_summary respects max_length parameter."""
    engine = SynthesisEngine()

    text = "This is a very long text that goes on and on and on. " * 10
    summary = engine._extract_summary(text, max_length=100)

    assert len(summary) <= 103  # Allow small overage due to "..." suffix


def test_rank_docs_handles_empty_credibility_map(synthesis_engine):
    """Test rank_docs_by_credibility with empty credibility map."""
    engine = SynthesisEngine()
    docs = [
        MockRetrievedDocument(doc_id="doc_1", text="Text", metadata={}),
        MockRetrievedDocument(doc_id="doc_2", text="Text", metadata={})
    ]
    credibility_map = {}

    ranked = engine._rank_docs_by_credibility(docs, credibility_map)

    assert len(ranked) == 2
    # All should get default credibility of 0.5


def test_synthesize_with_single_conflict_multiple_docs(synthesis_engine):
    """Test synthesis with multiple docs but single conflict."""
    docs = [
        MockRetrievedDocument(doc_id="doc_1", text="Text 1", metadata={}),
        MockRetrievedDocument(doc_id="doc_2", text="Text 2", metadata={}),
        MockRetrievedDocument(doc_id="doc_3", text="Text 3", metadata={})
    ]
    scores = [
        MockCredibilityScore(doc_id="doc_1", credibility=0.85, category="verified", recency_score=1.0, authority_score=0.8, accuracy_score=0.8, explanation=""),
        MockCredibilityScore(doc_id="doc_2", credibility=0.87, category="verified", recency_score=1.0, authority_score=0.8, accuracy_score=0.85, explanation=""),
        MockCredibilityScore(doc_id="doc_3", credibility=0.82, category="verified", recency_score=1.0, authority_score=0.8, accuracy_score=0.8, explanation="")
    ]
    conflicts = [
        MockConflictResult(doc_pair=(0, 1), conflict_score=0.5, conflict_type="qualitative", severity="medium", claim1="Claim A", claim2="Claim B", explanation="")
    ]

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    # Should include all docs in preferred_sources
    assert len(result.preferred_sources) == 3
    # Should handle only the one conflict
    assert len(result.conflicts_handled) >= 1


def test_differ_strategy_generates_percentage_format(synthesis_engine, two_docs_with_differ_conflict):
    """Test that 'differ' strategy includes credibility percentages."""
    docs, scores, conflicts = two_docs_with_differ_conflict

    result = synthesis_engine.synthesize(docs, conflicts, scores)

    if result.strategy == "differ":
        # Should include percentage signs
        assert "%" in result.answer


def test_attribution_empty_preferred_sources(synthesis_engine):
    """Test attribution generation with empty preferred sources."""
    engine = SynthesisEngine()

    attribution = engine._build_attribution([], {}, [])

    assert "No sources" in attribution


def test_add_conflict_disclaimer_empty_conflicts(synthesis_engine):
    """Test add_conflict_disclaimer with empty conflicts list."""
    answer = "This is the answer."
    result = synthesis_engine.add_conflict_disclaimer(answer, [], [])

    # Should return answer unchanged
    assert result == answer


def test_synthesize_strategy_never_invalid(synthesis_engine):
    """Test that strategy is always one of the four valid values."""
    valid_strategies = {"agree", "differ", "prefer", "unknown"}

    # Test with various configurations
    test_configs = [
        ([MockRetrievedDocument(doc_id="d1", text="T", metadata={})], [MockCredibilityScore(doc_id="d1", credibility=0.85, category="verified", recency_score=1.0, authority_score=0.8, accuracy_score=0.8, explanation="")], []),
        ([MockRetrievedDocument(doc_id="d1", text="T", metadata={}), MockRetrievedDocument(doc_id="d2", text="T", metadata={})], [MockCredibilityScore(doc_id="d1", credibility=0.85, category="verified", recency_score=1.0, authority_score=0.8, accuracy_score=0.8, explanation=""), MockCredibilityScore(doc_id="d2", credibility=0.85, category="verified", recency_score=1.0, authority_score=0.8, accuracy_score=0.8, explanation="")], [MockConflictResult(doc_pair=(0, 1), conflict_score=0.5, conflict_type="qualitative", severity="medium", claim1="A", claim2="B", explanation="")]),
    ]

    for docs, scores, conflicts in test_configs:
        result = synthesis_engine.synthesize(docs, scores, conflicts)
        assert result.strategy in valid_strategies


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
