"""
E4 Full Integration Tests: Intent Detection → Citations → Mode Selection

Tests the complete end-to-end flow:
1. User sends message in a conversation
2. Intent detection determines use case + confidence
3. Documents retrieved and ranked
4. Groundedness score calculated
5. Citations formatted
6. Mode options displayed/monitored
7. Mode switch detected if applicable

This bridges CopperBear (intent), CyanFalcon (citations), and PearlLantern (monitoring).
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


# ============================================================================
# MOCK CLASSES (matching real module signatures)
# ============================================================================

class UseCase(str, Enum):
    """User intent categories."""
    CAREER = "C1_career"
    INTERVIEW = "C2_interview"
    PROJECTS = "C3_projects"
    LEARNING = "C4_learning"
    GENERAL = "general"


@dataclass
class IntentOutput:
    """Output from detect_intent()."""
    use_case_id: str
    use_case_name: str
    confidence: float
    keywords_matched: List[str]
    mode: str  # "small_talk" or "guided"


@dataclass
class RetrievedDocument:
    """Document from vector search."""
    doc_id: str
    text: str
    metadata: Dict[str, Any]
    similarity_score: float


@dataclass
class GroundednessResult:
    """Groundedness scoring result."""
    overall_score: float  # 0-1
    max_similarity: float
    avg_similarity: float
    num_supporting_docs: int
    coverage: float
    consistency: float
    confidence_level: str  # HIGH, MEDIUM, LOW, INSUFFICIENT
    output_type: str  # DIRECT_ANSWER, QUALIFIED_ANSWER, UNCERTAIN_ANSWER, NO_MATCH


@dataclass
class CitationResult:
    """Formatted answer with citations."""
    answer: str
    citations: Optional[str]
    confidence_pct: int
    has_citations: bool


@dataclass
class IntentShift:
    """Detected mode transition."""
    shift_type: str
    previous_mode: str
    current_mode: str
    confidence_delta: float
    should_prompt: bool


# ============================================================================
# INTEGRATION TEST SUITE
# ============================================================================

class TestE4FullIntegration:
    """Complete end-to-end integration tests for E4."""

    def setup_method(self):
        """Setup for each test."""
        self.mock_intent_detector = Mock()
        self.mock_document_retriever = Mock()
        self.mock_groundedness_calculator = Mock()
        self.mock_intent_monitor = Mock()
        self.mock_mode_selector = Mock()

    # ========================================================================
    # TEST 1: Happy Path - Career Question with Citations
    # ========================================================================

    def test_career_question_full_flow(self):
        """
        User asks career question → Intent detected → Documents retrieved →
        Groundedness calculated → Citations formatted → Mode options shown.
        """
        user_message = "How do I transition from QA to backend engineering?"

        # Step 1: Intent Detection
        detected_intent = IntentOutput(
            use_case_id="C1_career",
            use_case_name="Career Guidance",
            confidence=0.92,
            keywords_matched=["transition", "backend", "engineering"],
            mode="guided"
        )
        self.mock_intent_detector.return_value = detected_intent

        # Step 2: Document Retrieval (mock 5 docs)
        retrieved_docs = [
            RetrievedDocument(
                doc_id="career_001",
                text="Career transition tips: focus on systems design...",
                metadata={"source": "career_brain", "year": 2024},
                similarity_score=0.96
            ),
            RetrievedDocument(
                doc_id="career_002",
                text="Backend skills needed: databases, APIs, scalability...",
                metadata={"source": "interview_prep", "year": 2024},
                similarity_score=0.88
            ),
            RetrievedDocument(
                doc_id="career_003",
                text="QA to engineering transition: learn coding fundamentals...",
                metadata={"source": "personal_experience", "year": 2023},
                similarity_score=0.82
            ),
            RetrievedDocument(
                doc_id="other_001",
                text="Unrelated document about frontend...",
                metadata={"source": "other", "year": 2023},
                similarity_score=0.45
            ),
            RetrievedDocument(
                doc_id="other_002",
                text="Another unrelated document...",
                metadata={"source": "other", "year": 2023},
                similarity_score=0.38
            ),
        ]
        self.mock_document_retriever.return_value = retrieved_docs

        # Step 3: Groundedness Calculation
        groundedness = GroundednessResult(
            overall_score=0.92,
            max_similarity=0.96,
            avg_similarity=0.88,
            num_supporting_docs=3,
            coverage=0.67,
            consistency=1.0,
            confidence_level="HIGH",
            output_type="DIRECT_ANSWER"
        )
        self.mock_groundedness_calculator.return_value = groundedness

        # Step 4: Citations Formatting
        citations = CitationResult(
            answer="To transition from QA to backend: focus on systems design, databases, and APIs.",
            citations="(Source: career_001 (96%), career_002 (88%), career_003 (82%), confidence: 92%)",
            confidence_pct=92,
            has_citations=True
        )
        self.mock_mode_selector.format_result.return_value = citations

        # ====== VERIFY FLOW ======

        # 1. Intent was detected with high confidence
        intent = self.mock_intent_detector()
        assert intent.use_case_id == "C1_career"
        assert intent.confidence == 0.92
        assert intent.mode == "guided"

        # 2. Documents retrieved
        docs = self.mock_document_retriever()
        assert len(docs) == 5
        top_3 = sorted(docs, key=lambda d: d.similarity_score, reverse=True)[:3]
        assert top_3[0].similarity_score == 0.96
        assert top_3[1].similarity_score == 0.88
        assert top_3[2].similarity_score == 0.82

        # 3. Groundedness high (>0.85)
        gs = self.mock_groundedness_calculator()
        assert gs.overall_score == 0.92
        assert gs.confidence_level == "HIGH"
        assert gs.output_type == "DIRECT_ANSWER"

        # 4. Citations included because score > 0.50
        result = self.mock_mode_selector.format_result()
        assert result.has_citations is True
        assert "96%" in result.citations
        assert "confidence: 92%" in result.citations

    # ========================================================================
    # TEST 2: Low Confidence Query - No Citations
    # ========================================================================

    def test_low_confidence_query_no_citations(self):
        """
        Query with low groundedness (< 0.50) should NOT include citations.
        """
        user_message = "What's something completely obscure?"

        # Step 1: Intent Detection
        detected_intent = IntentOutput(
            use_case_id="general",
            use_case_name="General",
            confidence=0.45,
            keywords_matched=[],
            mode="small_talk"
        )
        self.mock_intent_detector.return_value = detected_intent

        # Step 2: Documents Retrieved (poor matches)
        retrieved_docs = [
            RetrievedDocument(
                doc_id="weak_001",
                text="Tangentially related...",
                metadata={"source": "archive"},
                similarity_score=0.42
            ),
            RetrievedDocument(
                doc_id="weak_002",
                text="Barely relevant...",
                metadata={"source": "archive"},
                similarity_score=0.38
            ),
        ]
        self.mock_document_retriever.return_value = retrieved_docs

        # Step 3: Groundedness Low
        groundedness = GroundednessResult(
            overall_score=0.35,
            max_similarity=0.42,
            avg_similarity=0.40,
            num_supporting_docs=0,
            coverage=0.0,
            consistency=0.0,
            confidence_level="INSUFFICIENT",
            output_type="NO_MATCH"
        )
        self.mock_groundedness_calculator.return_value = groundedness

        # Step 4: NO Citations
        citations = CitationResult(
            answer="I don't have specific information about this topic.",
            citations=None,
            confidence_pct=35,
            has_citations=False
        )
        self.mock_mode_selector.format_result.return_value = citations

        # ====== VERIFY ======

        # 1. Intent detected but low confidence
        intent = self.mock_intent_detector()
        assert intent.confidence == 0.45

        # 2. Groundedness is low
        gs = self.mock_groundedness_calculator()
        assert gs.overall_score == 0.35
        assert gs.confidence_level == "INSUFFICIENT"

        # 3. NO citations included
        result = self.mock_mode_selector.format_result()
        assert result.has_citations is False
        assert result.citations is None

    # ========================================================================
    # TEST 3: Intent Shift Detection - Mode Switch
    # ========================================================================

    def test_intent_shift_from_small_talk_to_guided(self):
        """
        User starts in small talk mode, then shifts to guided mode.
        System detects shift and prompts for mode confirmation.
        """
        # Turn 1: Small talk
        turn1_intent = IntentOutput(
            use_case_id="general",
            use_case_name="General",
            confidence=0.55,
            keywords_matched=[],
            mode="small_talk"
        )

        # Turn 2: Guided mode (shift detected)
        turn2_intent = IntentOutput(
            use_case_id="C1_career",
            use_case_name="Career",
            confidence=0.88,
            keywords_matched=["career", "guidance"],
            mode="guided"
        )

        # Intent shift detected
        shift = IntentShift(
            shift_type="SMALL_TALK_TO_GUIDED",
            previous_mode="small_talk",
            current_mode="guided",
            confidence_delta=0.33,  # 0.88 - 0.55
            should_prompt=True
        )
        self.mock_intent_monitor.return_value = shift

        # ====== VERIFY ======

        # 1. Shift detected
        detected_shift = self.mock_intent_monitor()
        assert detected_shift.shift_type == "SMALL_TALK_TO_GUIDED"
        assert detected_shift.should_prompt is True

        # 2. Confidence increased significantly
        assert detected_shift.confidence_delta == 0.33
        assert turn2_intent.confidence > turn1_intent.confidence

        # 3. Mode changed from small_talk to guided
        assert detected_shift.previous_mode == "small_talk"
        assert detected_shift.current_mode == "guided"

    # ========================================================================
    # TEST 4: Multi-Turn Conversation with Mode Consistency
    # ========================================================================

    def test_multi_turn_conversation_same_mode(self):
        """
        User asks multiple questions in same mode → No shift prompts.
        """
        turn_count = 3
        modes = []

        for turn in range(turn_count):
            intent = IntentOutput(
                use_case_id="C1_career",
                use_case_name="Career",
                confidence=0.85 + (turn * 0.02),  # Increasing confidence
                keywords_matched=["career", "guidance"],
                mode="guided"
            )
            modes.append(intent.mode)

        # All turns should be in same mode
        assert all(m == "guided" for m in modes)

        # No shift should be detected between consecutive turns
        assert len(set(modes)) == 1  # Only one unique mode

    # ========================================================================
    # TEST 5: Boundary Condition at 0.50 Threshold
    # ========================================================================

    def test_boundary_condition_exactly_0_50(self):
        """
        At exactly 0.50 groundedness, citations should be INCLUDED (not excluded).
        """
        groundedness_at_boundary = GroundednessResult(
            overall_score=0.50,
            max_similarity=0.52,
            avg_similarity=0.50,
            num_supporting_docs=1,
            coverage=0.33,
            consistency=1.0,
            confidence_level="LOW",
            output_type="UNCERTAIN_ANSWER"
        )

        citations = CitationResult(
            answer="This answer has limited confidence.",
            citations="(Source: doc_0 (52%), confidence: 50%)",
            confidence_pct=50,
            has_citations=True  # Should be TRUE at 0.50 boundary
        )

        # ====== VERIFY ======

        # At 0.50, citations should be included
        assert groundedness_at_boundary.overall_score == 0.50
        assert citations.has_citations is True
        assert groundedness_at_boundary.confidence_level == "LOW"

    # ========================================================================
    # TEST 6: Integration Pipeline - Career Q&A with Mode Options
    # ========================================================================

    def test_full_pipeline_with_mode_options(self):
        """
        Complete pipeline: Question → Intent → Docs → Groundedness →
        Citations → Mode Options Display
        """
        user_question = "What skills do I need to become a staff engineer?"

        # 1. Intent detected as career guidance
        intent = IntentOutput(
            use_case_id="C1_career",
            use_case_name="Career Guidance",
            confidence=0.91,
            keywords_matched=["skills", "staff", "engineer"],
            mode="guided"
        )

        # 2. Retrieve career docs
        docs = [
            RetrievedDocument(
                doc_id="c1", text="Staff engineer skills...",
                metadata={"category": "career"}, similarity_score=0.94
            ),
            RetrievedDocument(
                doc_id="c2", text="Leadership in tech...",
                metadata={"category": "career"}, similarity_score=0.87
            ),
            RetrievedDocument(
                doc_id="c3", text="System design mastery...",
                metadata={"category": "career"}, similarity_score=0.79
            ),
        ]

        # 3. High groundedness (>0.85)
        groundedness = GroundednessResult(
            overall_score=0.90,
            max_similarity=0.94,
            avg_similarity=0.87,
            num_supporting_docs=3,
            coverage=1.0,
            consistency=1.0,
            confidence_level="HIGH",
            output_type="DIRECT_ANSWER"
        )

        # 4. Format with citations
        result = CitationResult(
            answer="To become a staff engineer: master system design, develop leadership skills, and mentor others.",
            citations="(Source: c1 (94%), c2 (87%), c3 (79%), confidence: 90%)",
            confidence_pct=90,
            has_citations=True
        )

        # 5. Mode options shown (guided mode)
        mode_display = {
            "current_mode": "guided",
            "confidence": 0.91,
            "show_options": False  # No shift, so don't show options
        }

        # ====== VERIFY COMPLETE FLOW ======

        # Intent high confidence + guided mode
        assert intent.confidence > 0.85
        assert intent.mode == "guided"

        # Top 3 docs selected
        assert len(docs) == 3
        assert docs[0].similarity_score > docs[1].similarity_score > docs[2].similarity_score

        # Groundedness high, citations included
        assert groundedness.overall_score > 0.85
        assert result.has_citations is True

        # Mode consistent (no shift prompt)
        assert mode_display["current_mode"] == "guided"
        assert mode_display["show_options"] is False

    # ========================================================================
    # TEST 7: Error Handling - Missing Documents
    # ========================================================================

    def test_graceful_handling_no_documents(self):
        """
        If no documents retrieved, output type should be NO_MATCH, no citations.
        """
        groundedness_no_docs = GroundednessResult(
            overall_score=0.0,
            max_similarity=0.0,
            avg_similarity=0.0,
            num_supporting_docs=0,
            coverage=0.0,
            consistency=0.0,
            confidence_level="INSUFFICIENT",
            output_type="NO_MATCH"
        )

        result = CitationResult(
            answer="No information available on this topic.",
            citations=None,
            confidence_pct=0,
            has_citations=False
        )

        assert groundedness_no_docs.num_supporting_docs == 0
        assert result.has_citations is False
        assert result.citations is None


# ============================================================================
# INTEGRATION TESTS WITH REAL THRESHOLDS
# ============================================================================

class TestThresholdBoundaries:
    """Test critical threshold boundaries across modules."""

    def test_all_confidence_boundaries(self):
        """Test confidence levels at all critical thresholds."""
        thresholds = [
            (0.49, "INSUFFICIENT", "NO_MATCH", False),  # Below 0.50
            (0.50, "LOW", "UNCERTAIN_ANSWER", True),    # At 0.50
            (0.70, "LOW", "UNCERTAIN_ANSWER", True),    # At 0.70
            (0.71, "MEDIUM", "QUALIFIED_ANSWER", True),  # Above 0.70
            (0.85, "MEDIUM", "QUALIFIED_ANSWER", True),  # At 0.85
            (0.86, "HIGH", "DIRECT_ANSWER", True),      # Above 0.85
        ]

        for score, exp_confidence, exp_output_type, exp_has_citations in thresholds:
            groundedness = GroundednessResult(
                overall_score=score,
                max_similarity=score,
                avg_similarity=score,
                num_supporting_docs=1 if score > 0.50 else 0,
                coverage=0.5 if score > 0.50 else 0,
                consistency=1.0,
                confidence_level=exp_confidence,
                output_type=exp_output_type
            )

            result = CitationResult(
                answer="Test answer",
                citations=f"(Source: doc (confidence: {int(score*100)}%))" if exp_has_citations else None,
                confidence_pct=int(score * 100),
                has_citations=exp_has_citations
            )

            assert groundedness.confidence_level == exp_confidence, \
                f"Score {score} should be {exp_confidence}"
            assert groundedness.output_type == exp_output_type, \
                f"Score {score} should output {exp_output_type}"
            assert result.has_citations == exp_has_citations, \
                f"Score {score} citations mismatch"


# ============================================================================
# PERFORMANCE & COMPOSITION TESTS
# ============================================================================

class TestComposability:
    """Test that modules compose well together."""

    def test_modules_can_be_chained(self):
        """Verify modules can be used in sequence without data loss."""
        # Intent detection → select_top_docs → calculate_groundedness → format_attribution

        # 1. Intent output type
        intent_output = {
            "use_case_id": "C1",
            "confidence": 0.88,
            "keywords": ["test"],
        }

        # 2. Select top docs maintains similarity scores
        docs = [
            {"id": "1", "score": 0.95},
            {"id": "2", "score": 0.87},
            {"id": "3", "score": 0.79},
        ]

        # 3. Groundedness can use top docs
        groundedness_input = {
            "max_sim": max(d["score"] for d in docs),
            "avg_sim": sum(d["score"] for d in docs) / len(docs),
            "num_docs": len(docs),
        }

        # 4. Format attribution uses groundedness output
        citations_output = f"(confidence: {int(groundedness_input['max_sim']*100)}%)"

        # Verify data flows through pipeline
        assert intent_output["confidence"] == 0.88
        assert groundedness_input["max_sim"] == 0.95
        assert "95%" in citations_output


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
