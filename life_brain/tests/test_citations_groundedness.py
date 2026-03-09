"""
Test suite for Citations & Groundedness Scoring

Tests boundary conditions at 0.85 (HIGH), 0.70 (MEDIUM), 0.50 (LOW) thresholds.

Coverage:
- issues-085: Test boundary conditions at 0.85, 0.70, 0.50 thresholds
- issues-8gh: Format with citations (select_top_documents)
- issues-s1z: Implement format_attribution() with source and confidence
"""

import pytest
from typing import List
from life_brain.truth.groundedness import (
    GroundednessScore,
    GroundednessCalculator,
    OutputGenerator,
    SynthesisLimiter,
    RetrievedDocument,
    ConfidenceLevel,
    OutputType,
)


class TestBoundaryConditions:
    """Test confidence/output mapping at critical thresholds."""

    def test_high_confidence_boundary_0_85(self):
        """Test HIGH confidence at exactly 0.85 threshold."""
        score = GroundednessScore(
            max_similarity=0.90,
            avg_similarity=0.85,
            num_supporting_docs=3,
            coverage=0.95,
            consistency=0.90,
            overall_score=0.85,
        )

        # At 0.85, should still be HIGH (> 0.85 is required, so 0.85 is MEDIUM)
        assert score.confidence_level() == ConfidenceLevel.MEDIUM
        assert score.output_type() == OutputType.QUALIFIED_ANSWER

    def test_high_confidence_above_0_85(self):
        """Test HIGH confidence above 0.85."""
        score = GroundednessScore(
            max_similarity=0.95,
            avg_similarity=0.90,
            num_supporting_docs=3,
            coverage=1.0,
            consistency=1.0,
            overall_score=0.86,
        )

        assert score.confidence_level() == ConfidenceLevel.HIGH
        assert score.output_type() == OutputType.DIRECT_ANSWER

    def test_medium_confidence_boundary_0_70(self):
        """Test MEDIUM confidence at exactly 0.70 threshold."""
        score = GroundednessScore(
            max_similarity=0.75,
            avg_similarity=0.70,
            num_supporting_docs=2,
            coverage=0.80,
            consistency=0.85,
            overall_score=0.70,
        )

        # At 0.70, should be LOW (> 0.70 is required for MEDIUM)
        assert score.confidence_level() == ConfidenceLevel.LOW
        assert score.output_type() == OutputType.UNCERTAIN_ANSWER

    def test_medium_confidence_above_0_70(self):
        """Test MEDIUM confidence above 0.70."""
        score = GroundednessScore(
            max_similarity=0.80,
            avg_similarity=0.75,
            num_supporting_docs=2,
            coverage=0.85,
            consistency=0.90,
            overall_score=0.75,
        )

        assert score.confidence_level() == ConfidenceLevel.MEDIUM
        assert score.output_type() == OutputType.QUALIFIED_ANSWER

    def test_low_confidence_boundary_0_50(self):
        """Test LOW confidence at exactly 0.50 threshold."""
        score = GroundednessScore(
            max_similarity=0.60,
            avg_similarity=0.50,
            num_supporting_docs=1,
            coverage=0.50,
            consistency=0.60,
            overall_score=0.50,
        )

        # At 0.50, should be INSUFFICIENT (< 0.50 is INSUFFICIENT, exactly 0.50 is LOW)
        assert score.confidence_level() == ConfidenceLevel.LOW
        assert score.output_type() == OutputType.UNCERTAIN_ANSWER

    def test_low_confidence_below_0_50(self):
        """Test INSUFFICIENT confidence below 0.50."""
        score = GroundednessScore(
            max_similarity=0.40,
            avg_similarity=0.35,
            num_supporting_docs=0,
            coverage=0.30,
            consistency=0.50,
            overall_score=0.35,
        )

        assert score.confidence_level() == ConfidenceLevel.INSUFFICIENT
        assert score.output_type() == OutputType.NO_MATCH

    def test_all_boundary_transitions(self):
        """Test all boundary transitions are correct."""
        thresholds = [
            (0.49, ConfidenceLevel.INSUFFICIENT, OutputType.NO_MATCH),
            (0.50, ConfidenceLevel.LOW, OutputType.UNCERTAIN_ANSWER),
            (0.60, ConfidenceLevel.LOW, OutputType.UNCERTAIN_ANSWER),
            (0.69, ConfidenceLevel.LOW, OutputType.UNCERTAIN_ANSWER),
            (0.70, ConfidenceLevel.LOW, OutputType.UNCERTAIN_ANSWER),
            (0.71, ConfidenceLevel.MEDIUM, OutputType.QUALIFIED_ANSWER),
            (0.80, ConfidenceLevel.MEDIUM, OutputType.QUALIFIED_ANSWER),
            (0.85, ConfidenceLevel.MEDIUM, OutputType.QUALIFIED_ANSWER),
            (0.86, ConfidenceLevel.HIGH, OutputType.DIRECT_ANSWER),
            (0.95, ConfidenceLevel.HIGH, OutputType.DIRECT_ANSWER),
        ]

        for score_value, expected_confidence, expected_output_type in thresholds:
            score = GroundednessScore(
                max_similarity=score_value,
                avg_similarity=score_value,
                num_supporting_docs=3,
                coverage=score_value,
                consistency=score_value,
                overall_score=score_value,
            )
            assert score.confidence_level() == expected_confidence, \
                f"Failed at score {score_value}: expected {expected_confidence.value}"
            assert score.output_type() == expected_output_type, \
                f"Failed at score {score_value}: expected {expected_output_type.value}"


class TestSelectTopDocuments:
    """Test select_top_documents() limiting to max 3."""

    def create_documents(self, count: int, scores: List[float]) -> List[RetrievedDocument]:
        """Helper to create test documents."""
        docs = []
        for i in range(count):
            doc = RetrievedDocument(
                doc_id=f"doc_{i}",
                text=f"Document {i}",
                metadata={"index": i},
                similarity_score=scores[i] if i < len(scores) else 0.0,
            )
            docs.append(doc)
        return docs

    def test_select_empty_list(self):
        """Test selecting from empty list."""
        docs = self.create_documents(0, [])
        selected = SynthesisLimiter.select_top_documents(docs)
        assert selected == []

    def test_select_single_document(self):
        """Test selecting from single document."""
        docs = self.create_documents(1, [0.95])
        selected = SynthesisLimiter.select_top_documents(docs)
        assert len(selected) == 1
        assert selected[0].doc_id == "doc_0"
        assert selected[0].similarity_score == 0.95

    def test_select_top_3_from_3(self):
        """Test selecting all 3 documents when exactly 3."""
        docs = self.create_documents(3, [0.95, 0.85, 0.75])
        selected = SynthesisLimiter.select_top_documents(docs, max_docs=3)
        assert len(selected) == 3
        assert [d.similarity_score for d in selected] == [0.95, 0.85, 0.75]

    def test_select_top_3_from_5(self):
        """Test selecting top 3 from 5 documents."""
        docs = self.create_documents(5, [0.95, 0.70, 0.85, 0.60, 0.90])
        selected = SynthesisLimiter.select_top_documents(docs, max_docs=3)
        assert len(selected) == 3
        # Should be sorted by similarity descending
        scores = [d.similarity_score for d in selected]
        assert scores == [0.95, 0.90, 0.85]

    def test_select_top_3_from_10(self):
        """Test selecting top 3 from 10 documents."""
        docs = self.create_documents(
            10,
            [0.95, 0.70, 0.85, 0.60, 0.90, 0.55, 0.88, 0.50, 0.92, 0.65]
        )
        selected = SynthesisLimiter.select_top_documents(docs, max_docs=3)
        assert len(selected) == 3
        scores = [d.similarity_score for d in selected]
        assert scores == [0.95, 0.92, 0.90]

    def test_select_respects_max_docs_limit(self):
        """Test that max_docs parameter is respected."""
        docs = self.create_documents(10, [i * 0.1 for i in range(10, 0, -1)])

        # Test with different max_docs values
        for max_docs in [1, 2, 3, 5]:
            selected = SynthesisLimiter.select_top_documents(docs, max_docs=max_docs)
            assert len(selected) <= max_docs
            assert len(selected) == min(max_docs, len(docs))


class TestFormatAttribution:
    """Test format_attribution() with source and confidence."""

    def create_docs_with_scores(self, scores: List[float]) -> List[RetrievedDocument]:
        """Helper to create test documents."""
        return [
            RetrievedDocument(
                doc_id=f"doc_{i}",
                text=f"Content {i}",
                metadata={"source": f"source_{i}"},
                similarity_score=score,
            )
            for i, score in enumerate(scores)
        ]

    def test_no_attribution_below_0_50(self):
        """Test no attribution added for score < 0.50."""
        answer = "This is an answer."
        docs = self.create_docs_with_scores([0.40])
        groundedness = GroundednessScore(
            max_similarity=0.40,
            avg_similarity=0.40,
            num_supporting_docs=1,
            coverage=0.40,
            consistency=0.50,
            overall_score=0.40,
        )

        result = OutputGenerator.format_attribution(answer, docs, groundedness)
        assert result == answer
        assert "(Source:" not in result

    def test_attribution_at_0_50(self):
        """Test attribution added at exactly 0.50."""
        answer = "This is an answer."
        docs = self.create_docs_with_scores([0.80, 0.70])
        groundedness = GroundednessScore(
            max_similarity=0.80,
            avg_similarity=0.75,
            num_supporting_docs=2,
            coverage=0.80,
            consistency=0.85,
            overall_score=0.50,
        )

        result = OutputGenerator.format_attribution(answer, docs, groundedness)
        assert answer in result
        assert "(Source:" in result
        assert "doc_0" in result
        assert "doc_1" in result
        assert "50%" in result

    def test_attribution_single_document(self):
        """Test attribution format with single document."""
        answer = "Career advice answer."
        docs = self.create_docs_with_scores([0.92])
        groundedness = GroundednessScore(
            max_similarity=0.92,
            avg_similarity=0.92,
            num_supporting_docs=1,
            coverage=0.95,
            consistency=1.0,
            overall_score=0.92,
        )

        result = OutputGenerator.format_attribution(answer, docs, groundedness)
        assert "doc_0" in result
        assert "92%" in result
        assert "92%" in result  # Groundedness score

    def test_attribution_multiple_documents(self):
        """Test attribution format with multiple documents."""
        answer = "Complex answer with multiple sources."
        docs = self.create_docs_with_scores([0.95, 0.88, 0.82, 0.75])
        groundedness = GroundednessScore(
            max_similarity=0.95,
            avg_similarity=0.90,
            num_supporting_docs=4,
            coverage=1.0,
            consistency=0.95,
            overall_score=0.88,
        )

        result = OutputGenerator.format_attribution(answer, docs, groundedness)

        # Should limit to top 3 documents
        assert "doc_0" in result
        assert "doc_1" in result
        assert "doc_2" in result
        assert "doc_3" not in result  # 4th doc should not appear

        # Check confidence percentage
        assert "88%" in result

    def test_attribution_format_syntax(self):
        """Test attribution follows correct syntax."""
        answer = "Test answer"
        docs = self.create_docs_with_scores([0.85, 0.75])
        groundedness = GroundednessScore(
            max_similarity=0.85,
            avg_similarity=0.80,
            num_supporting_docs=2,
            coverage=0.90,
            consistency=0.92,
            overall_score=0.75,
        )

        result = OutputGenerator.format_attribution(answer, docs, groundedness)

        # Should have format: answer + "\n\n(Source: doc_0 (85%), doc_1 (75%), confidence: 75%)"
        assert result.startswith(answer)
        assert "\n\n(Source:" in result
        assert ", confidence:" in result
        assert result.endswith(")")

    def test_attribution_high_confidence(self):
        """Test attribution with high confidence score."""
        answer = "High confidence answer."
        docs = self.create_docs_with_scores([0.98, 0.96, 0.94])
        groundedness = GroundednessScore(
            max_similarity=0.98,
            avg_similarity=0.96,
            num_supporting_docs=3,
            coverage=1.0,
            consistency=0.99,
            overall_score=0.96,
        )

        result = OutputGenerator.format_attribution(answer, docs, groundedness)
        assert "96%" in result  # Groundedness confidence
        assert "98%" in result  # First doc
        assert "96%" in result  # Second doc


class TestSelectAndAttributionIntegration:
    """Test integration between select_top_documents and format_attribution."""

    def test_workflow_many_docs_to_citation(self):
        """Test workflow: retrieve many docs -> select top 3 -> add citation."""
        # Simulate retrieval of 10 documents
        docs = [
            RetrievedDocument(
                doc_id=f"doc_{i}",
                text=f"Document {i} content",
                metadata={"date": f"2026-01-{i:02d}"},
                similarity_score=0.95 - (i * 0.05),  # Descending scores
            )
            for i in range(10)
        ]

        # Step 1: Select top 3
        selected = SynthesisLimiter.select_top_documents(docs, max_docs=3)
        assert len(selected) == 3
        assert selected[0].doc_id == "doc_0"
        assert selected[1].doc_id == "doc_1"
        assert selected[2].doc_id == "doc_2"

        # Step 2: Calculate groundedness on selected docs
        groundedness = GroundednessScore(
            max_similarity=selected[0].similarity_score,
            avg_similarity=sum(d.similarity_score for d in selected) / len(selected),
            num_supporting_docs=len(selected),
            coverage=0.85,
            consistency=0.90,
            overall_score=0.82,
        )

        # Step 3: Format with attribution
        answer = "Based on retrieved information, here is the answer."
        result = OutputGenerator.format_attribution(answer, selected, groundedness)

        assert "doc_0" in result
        assert "doc_1" in result
        assert "doc_2" in result
        assert "doc_3" not in result  # Beyond top 3
        assert "82%" in result

    def test_low_score_no_docs_no_citation(self):
        """Test that no docs with low score results in no citation."""
        docs = [
            RetrievedDocument(
                doc_id=f"doc_{i}",
                text=f"Document {i}",
                metadata={},
                similarity_score=0.30,
            )
            for i in range(3)
        ]

        selected = SynthesisLimiter.select_top_documents(docs, max_docs=3)
        assert len(selected) == 3  # Documents are selected

        groundedness = GroundednessScore(
            max_similarity=0.30,
            avg_similarity=0.30,
            num_supporting_docs=3,
            coverage=0.20,
            consistency=0.30,
            overall_score=0.30,  # Below 0.50 threshold
        )

        answer = "Low confidence answer."
        result = OutputGenerator.format_attribution(answer, selected, groundedness)

        # No citation should be added
        assert result == answer


class TestSynthesisLimitValidation:
    """Test synthesis limit validation."""

    def test_validate_synthesis_within_limits(self):
        """Test validation passes when within limits."""
        docs = [
            RetrievedDocument(
                doc_id=f"doc_{i}",
                text=f"Content {i}",
                metadata={},
                similarity_score=0.90,
            )
            for i in range(3)
        ]

        answer = "Answer synthesized from documents."
        is_valid, error = SynthesisLimiter.validate_synthesis(docs, answer)
        assert is_valid
        assert error is None

    def test_validate_synthesis_exceeds_limit(self):
        """Test validation fails when exceeding max docs."""
        docs = [
            RetrievedDocument(
                doc_id=f"doc_{i}",
                text=f"Content {i}",
                metadata={},
                similarity_score=0.90,
            )
            for i in range(5)  # More than max of 3
        ]

        answer = "Answer with too many sources."
        is_valid, error = SynthesisLimiter.validate_synthesis(docs, answer)
        assert not is_valid
        assert "Synthesis limit exceeded" in error
        assert "5 documents" in error

    def test_validate_synthesis_hallucination_detection(self):
        """Test hallucination detection: long answer with no documents."""
        docs = []
        answer = "This is a very long answer that was not supported by any documents. " * 5

        is_valid, error = SynthesisLimiter.validate_synthesis(docs, answer)
        assert not is_valid
        assert "hallucination" in error.lower() or "supporting documents" in error.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
