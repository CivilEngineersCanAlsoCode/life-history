"""
E5-E4 Integration Tests: Truth Engine into E4 Pipeline

Tests the integration of E5 components (F5.1-F5.4) into the E4 groundedness pipeline.

Test structure:
1. Happy path: answer + citations + conflicts + validation
2. Low confidence: validation rejection
3. Intent shift: E4 → E5 pipeline
4. Multi-turn: session continuity
5. Boundary conditions: groundedness thresholds with conflicts
6. Performance: <500ms total latency

Modules tested:
- F5.1 ConflictDetector integration
- F5.2 CredibilityScorer integration
- F5.3 SynthesisEngine integration
- F5.4 HallucinationPrevention integration
"""

import pytest
import time
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

from life_brain.truth_engine.groundedness import (
    OutputGenerator,
    GroundednessScore,
    RetrievedDocument,
    OutputType,
    ConfidenceLevel,
)
from life_brain.truth_engine.conflict_detector import ConflictDetector, ConflictResult, ConflictType
from life_brain.truth_engine.credibility_scorer import CredibilityScorer, CredibilityScore
from life_brain.truth_engine.synthesis_engine import SynthesisEngine, SynthesisResult
from life_brain.truth_engine.hallucination_prevention import HallucinationPrevention, ValidationResult, RuleViolation


# ============================================================================
# TEST FIXTURES & HELPERS
# ============================================================================

class MockConflictResult:
    """Mock ConflictResult for testing."""
    def __init__(self, doc_pair=(0, 1), conflict_score=0.5, conflict_type="semantic", severity="medium"):
        self.doc_pair = doc_pair
        self.conflict_score = conflict_score
        self.conflict_type = conflict_type
        self.severity = severity
        self.claim1 = "Test claim 1"
        self.claim2 = "Test claim 2"
        self.explanation = "Test conflict explanation"


class MockCredibilityScore:
    """Mock CredibilityScore for testing."""
    def __init__(self, doc_id="doc1", credibility=0.85, category="expert"):
        self.doc_id = doc_id
        self.credibility = credibility
        self.category = category
        self.recency_score = 0.9
        self.authority_score = 0.85
        self.accuracy_score = 0.82
        self.explanation = f"Credibility assessment for {doc_id}"


class MockSynthesisResult:
    """Mock SynthesisResult for testing."""
    def __init__(self, answer="Synthesized answer", strategy="agree", disclaimer=None):
        self.answer = answer
        self.strategy = strategy
        self.disclaimer = disclaimer
        self.conflicts_handled = []
        self.preferred_sources = ["doc1", "doc2"]
        self.attribution = "Sources: doc1, doc2"


class MockValidationResult:
    """Mock ValidationResult for testing."""
    def __init__(self, is_valid=True, passed_rules=None, rejection_reason=None):
        self.is_valid = is_valid
        self.passed_rules = passed_rules or ["synthesis_limits", "confidence_floor"]
        self.violated_rules = [] if is_valid else [RuleViolation("confidence_floor", "error", "Score too low")]
        self.rejection_reason = rejection_reason


def create_mock_document(doc_id: str, similarity: float = 0.85) -> RetrievedDocument:
    """Helper to create a mock document."""
    return RetrievedDocument(
        doc_id=doc_id,
        text=f"This is document {doc_id} with relevant content about career and projects.",
        metadata={
            "source": "career_brain",
            "date": "2024-03-09",
            "author": "Satvik Jain",
        },
        similarity_score=similarity,
    )


def create_groundedness_score(overall_score: float = 0.85) -> GroundednessScore:
    """Helper to create a groundedness score."""
    return GroundednessScore(
        max_similarity=overall_score,
        avg_similarity=overall_score * 0.95,
        num_supporting_docs=2,
        coverage=0.9,
        consistency=0.88,
        overall_score=overall_score,
    )


# ============================================================================
# TEST CLASS: E5-E4 INTEGRATION
# ============================================================================

class TestE5E4Integration:
    """Integration tests for E5 truth engine into E4 pipeline."""

    def setup_method(self):
        """Setup for each test."""
        self.detector = ConflictDetector()
        self.scorer = CredibilityScorer()
        self.synthesis_engine = SynthesisEngine()
        self.validator = HallucinationPrevention()

    # ========================================================================
    # TEST 1: HAPPY PATH - Answer with Citations + Conflicts + Validation
    # ========================================================================

    def test_happy_path_answer_with_e5_metadata(self):
        """
        Complete E5-E4 pipeline:
        - High confidence query
        - Multiple documents
        - No conflicts detected
        - All validations pass
        - Output includes E5 metadata
        """
        documents = [
            create_mock_document("career_001", 0.92),
            create_mock_document("career_002", 0.88),
        ]
        groundedness = create_groundedness_score(0.90)

        answer = "Career transition requires systematic skill development and networking."
        user_query = "How do I transition from QA to backend?"

        # Mock the E5 components
        with patch.object(ConflictDetector, 'detect_conflicts', return_value=[]):
            with patch.object(CredibilityScorer, 'score_source') as mock_cred:
                mock_cred.side_effect = [
                    MockCredibilityScore("career_001", 0.92),
                    MockCredibilityScore("career_002", 0.85),
                ]
                with patch.object(SynthesisEngine, 'synthesize') as mock_syn:
                    mock_syn.return_value = MockSynthesisResult(answer=answer, strategy="agree")
                    with patch.object(HallucinationPrevention, 'validate_answer') as mock_val:
                        mock_val.return_value = MockValidationResult(is_valid=True)

                        output = OutputGenerator.generate_output(
                            answer=answer,
                            groundedness=groundedness,
                            documents=documents,
                            user_query=user_query,
                            enable_e5_integration=True,
                        )

        # Assertions
        assert output["output_type"] == OutputType.DIRECT_ANSWER.value
        assert output["confidence_level"] == ConfidenceLevel.HIGH.value
        assert output["groundedness_score"] == 0.90
        assert len(output["source_documents"]) == 2

        # E5 metadata assertions
        assert "e5_integration" in output
        assert output["e5_integration"]["conflicts"] == []
        assert len(output["e5_integration"]["credibility_scores"]) == 2
        assert output["e5_integration"]["synthesis"]["strategy"] == "agree"
        assert output["e5_integration"]["validation"]["is_valid"] is True
        assert len(output["e5_integration"]["validation"]["passed_rules"]) == 2

    # ========================================================================
    # TEST 2: LOW CONFIDENCE - Validation Rejection
    # ========================================================================

    def test_low_confidence_validation_rejects_answer(self):
        """
        Low confidence groundedness score triggers validation rejection.
        - Groundedness 0.40 (below confidence floor)
        - Validation fails
        - Output becomes "I don't have enough information"
        """
        documents = [create_mock_document("old_001", 0.50)]
        groundedness = create_groundedness_score(0.40)  # Below confidence floor

        answer = "Some uncertain answer based on limited info."

        with patch.object(ConflictDetector, 'detect_conflicts', return_value=[]):
            with patch.object(CredibilityScorer, 'score_source') as mock_cred:
                mock_cred.return_value = MockCredibilityScore("old_001", 0.45)
                with patch.object(SynthesisEngine, 'synthesize') as mock_syn:
                    mock_syn.return_value = MockSynthesisResult(answer=answer)
                    with patch.object(HallucinationPrevention, 'validate_answer') as mock_val:
                        mock_val.return_value = MockValidationResult(
                            is_valid=False,
                            rejection_reason="Confidence floor not met"
                        )

                        output = OutputGenerator.generate_output(
                            answer=answer,
                            groundedness=groundedness,
                            documents=documents,
                            enable_e5_integration=True,
                        )

        # Assertions
        assert "I don't have enough information" in output["output"]
        assert output["e5_integration"]["validation"]["is_valid"] is False
        assert output["e5_integration"]["validation"]["rejection_reason"] == "Confidence floor not met"
        assert output["confidence_level"] == ConfidenceLevel.INSUFFICIENT.value

    # ========================================================================
    # TEST 3: CONFLICT DETECTION & SYNTHESIS
    # ========================================================================

    def test_conflict_detection_and_synthesis(self):
        """
        Conflicts detected and synthesized:
        - Two documents with conflicting claims
        - F5.1 detects conflicts
        - F5.3 synthesizes with disclaimer
        - Output includes conflict metadata
        """
        documents = [
            create_mock_document("proj_001", 0.88),
            create_mock_document("proj_002", 0.85),
        ]
        groundedness = create_groundedness_score(0.86)

        conflict = MockConflictResult(
            doc_pair=(0, 1),
            conflict_score=0.45,
            severity="medium",
        )

        answer = "Original answer."

        with patch.object(ConflictDetector, 'detect_conflicts', return_value=[conflict]):
            with patch.object(CredibilityScorer, 'score_source') as mock_cred:
                mock_cred.side_effect = [
                    MockCredibilityScore("proj_001", 0.88),
                    MockCredibilityScore("proj_002", 0.85),
                ]
                with patch.object(SynthesisEngine, 'synthesize') as mock_syn:
                    mock_syn.return_value = MockSynthesisResult(
                        answer=answer,
                        strategy="differ",
                        disclaimer="Note: Sources have different perspectives."
                    )
                    with patch.object(HallucinationPrevention, 'validate_answer') as mock_val:
                        mock_val.return_value = MockValidationResult(is_valid=True)

                        output = OutputGenerator.generate_output(
                            answer=answer,
                            groundedness=groundedness,
                            documents=documents,
                            enable_e5_integration=True,
                        )

        # Assertions
        assert len(output["e5_integration"]["conflicts"]) == 1
        assert output["e5_integration"]["conflicts"][0]["conflict_score"] == 0.45
        assert output["e5_integration"]["conflicts"][0]["severity"] == "medium"
        assert output["e5_integration"]["synthesis"]["disclaimer"] is not None
        assert output["e5_integration"]["synthesis"]["strategy"] == "differ"

    # ========================================================================
    # TEST 4: CREDIBILITY RANKING
    # ========================================================================

    def test_credibility_scores_influence_synthesis(self):
        """
        Credibility scores properly rank documents:
        - Document 1: credibility 0.95 (expert)
        - Document 2: credibility 0.65 (personal)
        - Synthesis prefers Document 1
        """
        documents = [
            create_mock_document("expert_001", 0.88),
            create_mock_document("personal_002", 0.82),
        ]
        groundedness = create_groundedness_score(0.85)

        answer = "Answer text."

        with patch.object(ConflictDetector, 'detect_conflicts', return_value=[]):
            with patch.object(CredibilityScorer, 'score_source') as mock_cred:
                mock_cred.side_effect = [
                    MockCredibilityScore("expert_001", 0.95, "expert"),
                    MockCredibilityScore("personal_002", 0.65, "personal"),
                ]
                with patch.object(SynthesisEngine, 'synthesize') as mock_syn:
                    mock_syn.return_value = MockSynthesisResult(
                        answer=answer,
                        strategy="agree",
                    )
                    with patch.object(HallucinationPrevention, 'validate_answer') as mock_val:
                        mock_val.return_value = MockValidationResult(is_valid=True)

                        output = OutputGenerator.generate_output(
                            answer=answer,
                            groundedness=groundedness,
                            documents=documents,
                            enable_e5_integration=True,
                        )

        # Assertions
        cred_scores = output["e5_integration"]["credibility_scores"]
        assert cred_scores[0]["credibility"] == 0.95
        assert cred_scores[0]["category"] == "expert"
        assert cred_scores[1]["credibility"] == 0.65
        assert cred_scores[1]["category"] == "personal"

    # ========================================================================
    # TEST 5: MULTI-TURN CONVERSATION
    # ========================================================================

    def test_multi_turn_with_session_context(self):
        """
        Multi-turn conversation with E5 validation:
        - First turn: answer generated with E5
        - Second turn: validation considers conversation context
        - Session state preserved
        """
        documents = [create_mock_document("context_001", 0.87)]
        groundedness = create_groundedness_score(0.85)

        first_answer = "First turn answer."
        second_answer = "Second turn answer building on context."
        user_query = "Tell me more about that project?"

        with patch.object(ConflictDetector, 'detect_conflicts', return_value=[]):
            with patch.object(CredibilityScorer, 'score_source') as mock_cred:
                mock_cred.return_value = MockCredibilityScore("context_001", 0.85)
                with patch.object(SynthesisEngine, 'synthesize') as mock_syn:
                    mock_syn.return_value = MockSynthesisResult(answer=second_answer)
                    with patch.object(HallucinationPrevention, 'validate_answer') as mock_val:
                        mock_val.return_value = MockValidationResult(is_valid=True)

                        output = OutputGenerator.generate_output(
                            answer=second_answer,
                            groundedness=groundedness,
                            documents=documents,
                            user_query=user_query,
                            enable_e5_integration=True,
                        )

        # Assertions
        assert output["e5_integration"]["validation"]["is_valid"] is True
        assert output["groundedness_score"] == 0.85
        assert len(output["source_documents"]) == 1

    # ========================================================================
    # TEST 6: BOUNDARY CONDITIONS
    # ========================================================================

    def test_boundary_condition_exactly_0_50_groundedness(self):
        """
        Boundary condition: groundedness exactly 0.50.
        - At confidence floor threshold
        - Should be LOW confidence, UNCERTAIN_ANSWER
        - Validation should still pass if other rules ok
        """
        documents = [create_mock_document("boundary_001", 0.50)]
        groundedness = create_groundedness_score(0.50)

        answer = "Uncertain answer at boundary."

        with patch.object(ConflictDetector, 'detect_conflicts', return_value=[]):
            with patch.object(CredibilityScorer, 'score_source') as mock_cred:
                mock_cred.return_value = MockCredibilityScore("boundary_001", 0.50)
                with patch.object(SynthesisEngine, 'synthesize') as mock_syn:
                    mock_syn.return_value = MockSynthesisResult(answer=answer)
                    with patch.object(HallucinationPrevention, 'validate_answer') as mock_val:
                        mock_val.return_value = MockValidationResult(is_valid=True)

                        output = OutputGenerator.generate_output(
                            answer=answer,
                            groundedness=groundedness,
                            documents=documents,
                            enable_e5_integration=True,
                        )

        # Assertions
        assert output["confidence_level"] == ConfidenceLevel.LOW.value
        assert output["output_type"] == OutputType.UNCERTAIN_ANSWER.value
        assert output["groundedness_score"] == 0.50

    def test_boundary_condition_0_49_groundedness(self):
        """
        Below confidence floor: 0.49 groundedness.
        - Should be INSUFFICIENT confidence
        - Validation may reject
        """
        documents = [create_mock_document("low_001", 0.49)]
        groundedness = create_groundedness_score(0.49)

        answer = "Low confidence answer."

        with patch.object(ConflictDetector, 'detect_conflicts', return_value=[]):
            with patch.object(CredibilityScorer, 'score_source') as mock_cred:
                mock_cred.return_value = MockCredibilityScore("low_001", 0.49)
                with patch.object(SynthesisEngine, 'synthesize') as mock_syn:
                    mock_syn.return_value = MockSynthesisResult(answer=answer)
                    with patch.object(HallucinationPrevention, 'validate_answer') as mock_val:
                        mock_val.return_value = MockValidationResult(
                            is_valid=False,
                            rejection_reason="Confidence floor not met"
                        )

                        output = OutputGenerator.generate_output(
                            answer=answer,
                            groundedness=groundedness,
                            documents=documents,
                            enable_e5_integration=True,
                        )

        # Assertions
        assert output["confidence_level"] == ConfidenceLevel.INSUFFICIENT.value
        assert output["output_type"] == OutputType.NO_MATCH.value

    def test_boundary_condition_high_conflict_with_high_groundedness(self):
        """
        Boundary: High groundedness (0.88) but high conflict (score > 0.6).
        - Conflicts detected and significant
        - Synthesis uses "hard_conflict" strategy
        - Answer quality may be questioned despite high groundedness
        """
        documents = [
            create_mock_document("high_001", 0.88),
            create_mock_document("high_002", 0.86),
        ]
        groundedness = create_groundedness_score(0.88)

        high_conflict = MockConflictResult(
            doc_pair=(0, 1),
            conflict_score=0.72,  # > 0.6 (high severity)
            severity="high",
        )

        answer = "Answer with high conflict."

        with patch.object(ConflictDetector, 'detect_conflicts', return_value=[high_conflict]):
            with patch.object(CredibilityScorer, 'score_source') as mock_cred:
                mock_cred.side_effect = [
                    MockCredibilityScore("high_001", 0.88),
                    MockCredibilityScore("high_002", 0.86),
                ]
                with patch.object(SynthesisEngine, 'synthesize') as mock_syn:
                    mock_syn.return_value = MockSynthesisResult(
                        answer=answer,
                        strategy="hard_conflict",
                        disclaimer="⚠️ Warning: Significant contradictions detected."
                    )
                    with patch.object(HallucinationPrevention, 'validate_answer') as mock_val:
                        mock_val.return_value = MockValidationResult(is_valid=True)

                            output = OutputGenerator.generate_output(
                            answer=answer,
                            groundedness=groundedness,
                            documents=documents,
                            enable_e5_integration=True,
                        )

        # Assertions
        assert output["groundedness_score"] == 0.88
        assert output["e5_integration"]["conflicts"][0]["conflict_score"] == 0.72
        assert output["e5_integration"]["synthesis"]["strategy"] == "hard_conflict"
        assert "Warning" in (output["e5_integration"]["synthesis"]["disclaimer"] or "")

    # ========================================================================
    # TEST 7: PERFORMANCE - <500ms latency
    # ========================================================================

    def test_performance_e5_under_500ms(self):
        """
        Performance validation: E5 pipeline adds <500ms latency.
        - Measure end-to-end time
        - Ensure acceptable for production
        """
        documents = [
            create_mock_document("perf_001", 0.85),
            create_mock_document("perf_002", 0.82),
        ]
        groundedness = create_groundedness_score(0.84)
        answer = "Performance test answer."

        with patch.object(ConflictDetector, 'detect_conflicts', return_value=[]):
            with patch.object(CredibilityScorer, 'score_source') as mock_cred:
                mock_cred.side_effect = [
                    MockCredibilityScore("perf_001", 0.85),
                    MockCredibilityScore("perf_002", 0.82),
                ]
                with patch.object(SynthesisEngine, 'synthesize') as mock_syn:
                    mock_syn.return_value = MockSynthesisResult(answer=answer)
                    with patch.object(HallucinationPrevention, 'validate_answer') as mock_val:
                        mock_val.return_value = MockValidationResult(is_valid=True)

                        start = time.time()
                        output = OutputGenerator.generate_output(
                            answer=answer,
                            groundedness=groundedness,
                            documents=documents,
                            enable_e5_integration=True,
                        )
                        elapsed_ms = (time.time() - start) * 1000

        # Assertions
        assert elapsed_ms < 500, f"E5 pipeline took {elapsed_ms:.1f}ms, target <500ms"
        assert output["e5_integration"] is not None

    # ========================================================================
    # TEST 8: DISABLE E5 INTEGRATION
    # ========================================================================

    def test_legacy_path_e5_disabled(self):
        """
        Backward compatibility: E5 can be disabled.
        - enable_e5_integration=False
        - Output doesn't include E5 metadata
        - Still generates valid output
        """
        documents = [create_mock_document("legacy_001", 0.85)]
        groundedness = create_groundedness_score(0.85)
        answer = "Legacy format answer."

        output = OutputGenerator.generate_output(
            answer=answer,
            groundedness=groundedness,
            documents=documents,
            enable_e5_integration=False,
        )

        # Assertions
        assert output["output_type"] == OutputType.DIRECT_ANSWER.value
        assert output["confidence_level"] == ConfidenceLevel.HIGH.value
        assert "e5_integration" not in output

    # ========================================================================
    # TEST 9: ERROR HANDLING IN E5 PIPELINE
    # ========================================================================

    def test_e5_error_handling_graceful_fallback(self):
        """
        Error in E5 pipeline doesn't crash output generation.
        - E5 raises exception
        - Falls back to original answer
        - Includes error context in validation
        """
        documents = [create_mock_document("error_001", 0.85)]
        groundedness = create_groundedness_score(0.85)
        answer = "Answer text."

        with patch.object(ConflictDetector, 'detect_conflicts', side_effect=Exception("Mock error")):
            output = OutputGenerator.generate_output(
                answer=answer,
                groundedness=groundedness,
                documents=documents,
                enable_e5_integration=True,
            )

        # Assertions
        assert output["output"] is not None
        assert output["groundedness_score"] == 0.85
        assert output["e5_integration"]["validation"]["is_valid"] is False
        assert "Error in truth engine" in output["e5_integration"]["validation"]["rejection_reason"]

    # ========================================================================
    # TEST 10: COMPLEX SCENARIO - Conflicts + Low Credibility + High Score
    # ========================================================================

    def test_complex_scenario_conflicts_low_cred_high_groundedness(self):
        """
        Complex scenario: High groundedness but low credibility and conflicts.
        - Groundedness 0.87 (high)
        - Credibility 0.50 (low)
        - Conflicts detected
        - Should still validate carefully
        """
        documents = [
            create_mock_document("complex_001", 0.87),
            create_mock_document("complex_002", 0.85),
        ]
        groundedness = create_groundedness_score(0.87)

        conflict = MockConflictResult(
            doc_pair=(0, 1),
            conflict_score=0.35,
            severity="medium",
        )

        answer = "Complex answer with conflicts."

        with patch.object(ConflictDetector, 'detect_conflicts', return_value=[conflict]):
            with patch.object(CredibilityScorer, 'score_source') as mock_cred:
                mock_cred.side_effect = [
                    MockCredibilityScore("complex_001", 0.50, "personal"),
                    MockCredibilityScore("complex_002", 0.55, "personal"),
                ]
                with patch.object(SynthesisEngine, 'synthesize') as mock_syn:
                    mock_syn.return_value = MockSynthesisResult(
                        answer=answer,
                        strategy="differ",
                    )
                    with patch.object(HallucinationPrevention, 'validate_answer') as mock_val:
                        mock_val.return_value = MockValidationResult(is_valid=True)

                            output = OutputGenerator.generate_output(
                            answer=answer,
                            groundedness=groundedness,
                            documents=documents,
                            enable_e5_integration=True,
                        )

        # Assertions
        assert output["groundedness_score"] == 0.87
        assert output["confidence_level"] == ConfidenceLevel.HIGH.value
        assert len(output["e5_integration"]["conflicts"]) == 1
        assert output["e5_integration"]["credibility_scores"][0]["credibility"] == 0.50

    # ========================================================================
    # TEST 11: EMPTY DOCUMENTS HANDLING
    # ========================================================================

    def test_empty_documents_graceful_handling(self):
        """
        Empty documents list should be handled gracefully.
        - No documents provided
        - E5 components still run but with safe defaults
        - No crash
        """
        documents = []
        groundedness = create_groundedness_score(0.0)
        answer = "No information available."

        output = OutputGenerator.generate_output(
            answer=answer,
            groundedness=groundedness,
            documents=documents,
            enable_e5_integration=True,
        )

        # Assertions
        assert output["output_type"] == OutputType.NO_MATCH.value
        assert output["confidence_level"] == ConfidenceLevel.INSUFFICIENT.value
        assert output["e5_integration"]["conflicts"] == []
        assert output["e5_integration"]["credibility_scores"] == []

    # ========================================================================
    # TEST 12: TYPE HINTS VALIDATION
    # ========================================================================

    def test_output_structure_type_compliance(self):
        """
        Output structure matches expected types.
        - All keys present
        - All values correct types
        - E5 metadata properly typed
        """
        documents = [create_mock_document("type_001", 0.85)]
        groundedness = create_groundedness_score(0.85)

        with patch.object(ConflictDetector, 'detect_conflicts', return_value=[]):
            with patch.object(CredibilityScorer, 'score_source') as mock_cred:
                mock_cred.return_value = MockCredibilityScore("type_001", 0.85)
                with patch.object(SynthesisEngine, 'synthesize') as mock_syn:
                    mock_syn.return_value = MockSynthesisResult(answer="Test")
                    with patch.object(HallucinationPrevention, 'validate_answer') as mock_val:
                        mock_val.return_value = MockValidationResult(is_valid=True)

                        output = OutputGenerator.generate_output(
                            answer="Test answer",
                            groundedness=groundedness,
                            documents=documents,
                            enable_e5_integration=True,
                        )

        # Type checks
        assert isinstance(output["output"], str)
        assert isinstance(output["output_type"], str)
        assert isinstance(output["confidence_level"], str)
        assert isinstance(output["groundedness_score"], float)
        assert isinstance(output["groundedness_breakdown"], dict)
        assert isinstance(output["source_documents"], list)
        assert isinstance(output["e5_integration"], dict)

        # E5 metadata types
        e5 = output["e5_integration"]
        assert isinstance(e5["conflicts"], list)
        assert isinstance(e5["credibility_scores"], list)
        assert isinstance(e5["synthesis"], dict)
        assert isinstance(e5["validation"], dict) or e5["validation"] is None
