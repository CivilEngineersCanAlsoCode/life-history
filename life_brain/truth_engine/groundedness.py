"""
Groundedness Scoring & Anti-Hallucination Protocol — E5.4 & E5.5

Implements:
- Groundedness score formula (0-1)
- Output decision rules based on groundedness
- Attribution format with source citing
- Synthesis limits (max 3 vectors per output)
- Query decomposition for complex questions
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import math

logger = logging.getLogger(__name__)


class ConfidenceLevel(str, Enum):
    """Confidence level of an answer based on groundedness."""
    HIGH = "high"  # > 0.85
    MEDIUM = "medium"  # 0.70-0.85
    LOW = "low"  # 0.50-0.70
    INSUFFICIENT = "insufficient"  # < 0.50


class OutputType(str, Enum):
    """Type of output to generate based on groundedness."""
    DIRECT_ANSWER = "direct_answer"  # Groundedness > 0.85
    QUALIFIED_ANSWER = "qualified_answer"  # 0.70-0.85
    UNCERTAIN_ANSWER = "uncertain_answer"  # 0.50-0.70
    NO_MATCH = "no_match"  # < 0.50


@dataclass
class RetrievedDocument:
    """A document retrieved from vector search."""

    doc_id: str
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    similarity_score: float = 0.0  # 0-1, cosine similarity


@dataclass
class GroundednessScore:
    """Quantitative groundedness assessment."""

    max_similarity: float  # Max cosine similarity of retrieved docs (0-1)
    avg_similarity: float  # Average similarity across retrieved docs
    num_supporting_docs: int  # How many docs support the answer (0-3+)
    coverage: float  # Fraction of query covered by retrieved docs (0-1)
    consistency: float  # How consistent are the retrieved docs (0-1)
    overall_score: float  # 0-1, composite groundedness

    def confidence_level(self) -> ConfidenceLevel:
        """Map score to confidence level."""
        if self.overall_score > 0.85:
            return ConfidenceLevel.HIGH
        elif self.overall_score > 0.70:
            return ConfidenceLevel.MEDIUM
        elif self.overall_score >= 0.50:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.INSUFFICIENT

    def output_type(self) -> OutputType:
        """Determine what type of output to generate."""
        if self.overall_score > 0.85:
            return OutputType.DIRECT_ANSWER
        elif self.overall_score > 0.70:
            return OutputType.QUALIFIED_ANSWER
        elif self.overall_score >= 0.50:
            return OutputType.UNCERTAIN_ANSWER
        else:
            return OutputType.NO_MATCH


class GroundednessCalculator:
    """Calculate groundedness of answers against retrieved documents."""

    # Weighting for groundedness components
    WEIGHTS = {
        "max_similarity": 0.40,  # Primary: best match similarity
        "avg_similarity": 0.20,  # Secondary: average quality
        "num_docs": 0.20,  # Tertiary: support breadth (1, 2, or 3+ docs)
        "consistency": 0.20,  # Tertiary: doc agreement
    }

    def __init__(self, query_threshold: float = 0.75):
        """
        Initialize calculator.

        Args:
            query_threshold: Minimum similarity to consider a doc relevant (0-1)
        """
        self.query_threshold = query_threshold

    def calculate_max_similarity(self, documents: List[RetrievedDocument]) -> float:
        """Get max similarity from retrieved documents."""
        if not documents:
            return 0.0
        return max(doc.similarity_score for doc in documents)

    def calculate_avg_similarity(self, documents: List[RetrievedDocument]) -> float:
        """Get average similarity across relevant documents."""
        relevant = [d for d in documents if d.similarity_score >= self.query_threshold]
        if not relevant:
            return 0.0
        return sum(d.similarity_score for d in relevant) / len(relevant)

    def count_supporting_documents(self, documents: List[RetrievedDocument]) -> int:
        """Count documents that support the query (above threshold)."""
        return len([d for d in documents if d.similarity_score >= self.query_threshold])

    def calculate_coverage(
        self,
        query_keywords: List[str],
        documents: List[RetrievedDocument],
    ) -> float:
        """
        Estimate what fraction of query is covered by retrieved documents.

        Args:
            query_keywords: Key terms from the query
            documents: Retrieved documents

        Returns:
            Coverage score (0-1)
        """
        if not query_keywords or not documents:
            return 0.0

        doc_text = " ".join(d.text.lower() for d in documents)
        covered_keywords = sum(1 for kw in query_keywords if kw.lower() in doc_text)
        return covered_keywords / len(query_keywords)

    def calculate_consistency(self, documents: List[RetrievedDocument]) -> float:
        """
        Measure consistency/agreement across documents.

        Heuristic: If docs contradict, consistency is low.
        If they agree, consistency is high.

        Args:
            documents: Retrieved documents

        Returns:
            Consistency score (0-1)
        """
        if len(documents) < 2:
            return 1.0  # Single doc is "consistent with itself"

        # Simple heuristic: look for contradictory signals
        docs_lower = [d.text.lower() for d in documents]

        contradiction_patterns = [
            ("yes", "no"),
            ("true", "false"),
            ("success", "failure"),
            ("supported", "rejected"),
        ]

        contradictions_found = 0
        for positive, negative in contradiction_patterns:
            has_positive = any(positive in d for d in docs_lower)
            has_negative = any(negative in d for d in docs_lower)
            if has_positive and has_negative:
                contradictions_found += 1

        # Consistency = 1 - (contradictions / total patterns)
        consistency = 1.0 - (contradictions_found / len(contradiction_patterns))
        return max(0.0, min(1.0, consistency))

    def calculate_groundedness(
        self,
        documents: List[RetrievedDocument],
        query_keywords: Optional[List[str]] = None,
    ) -> GroundednessScore:
        """
        Calculate comprehensive groundedness score.

        Args:
            documents: Retrieved documents (max 3 for synthesis)
            query_keywords: Key terms from query (for coverage calculation)

        Returns:
            GroundednessScore with component breakdown
        """
        # Component 1: Maximum similarity
        max_sim = self.calculate_max_similarity(documents)

        # Component 2: Average similarity
        avg_sim = self.calculate_avg_similarity(documents)

        # Component 3: Number of supporting documents
        num_supporting = min(self.count_supporting_documents(documents), 3)  # Cap at 3
        num_score = num_supporting / 3.0  # Normalize to 0-1

        # Component 4: Coverage
        coverage = self.calculate_coverage(query_keywords or [], documents)

        # Component 5: Consistency
        consistency = self.calculate_consistency(documents)

        # Composite score using weighted components
        overall_score = (
            self.WEIGHTS["max_similarity"] * max_sim +
            self.WEIGHTS["avg_similarity"] * avg_sim +
            self.WEIGHTS["num_docs"] * num_score +
            self.WEIGHTS["consistency"] * consistency
        )

        # Apply coverage as modifier (if coverage is low, reduce overall score)
        if coverage < 0.5:
            overall_score *= (0.5 + coverage)  # Reduce by up to 50%

        return GroundednessScore(
            max_similarity=max_sim,
            avg_similarity=avg_sim,
            num_supporting_docs=num_supporting,
            coverage=coverage,
            consistency=consistency,
            overall_score=min(1.0, max(0.0, overall_score)),
        )


class OutputGenerator:
    """Generate outputs with appropriate confidence indicators based on groundedness."""

    PROMPTS = {
        OutputType.DIRECT_ANSWER: (
            "Provide a direct, confident answer based on the retrieved information.",
            ""
        ),
        OutputType.QUALIFIED_ANSWER: (
            "Provide an answer with a brief confidence qualification.",
            " — Yeh meri understanding hai, confirm karo."
        ),
        OutputType.UNCERTAIN_ANSWER: (
            "Provide an answer but indicate uncertainty.",
            " — Mujhe kuch related pata hai, lekin poora confident nahi hun:"
        ),
        OutputType.NO_MATCH: (
            "Politely indicate insufficient grounded information.",
            " — Mere paas is baare mein enough verified information nahi hai. Kya tum mujhe yeh batana chahoge?"
        ),
    }

    @staticmethod
    def format_attribution(
        answer: str,
        documents: List[RetrievedDocument],
        groundedness: GroundednessScore,
    ) -> str:
        """
        Format answer with source attribution.

        Args:
            answer: Generated answer text
            documents: Supporting documents
            groundedness: Groundedness score

        Returns:
            Formatted answer with attribution
        """
        if groundedness.overall_score < 0.50:
            return answer  # No attribution for low-confidence

        # Build source citation
        source_docs = [(d.doc_id, d.similarity_score) for d in documents[:3]]
        source_str = ", ".join(f"{doc_id} ({score:.0%})" for doc_id, score in source_docs)

        attribution = f"\n\n(Source: {source_str}, confidence: {groundedness.overall_score:.0%})"
        return answer + attribution

    @staticmethod
    def generate_output(
        answer: str,
        groundedness: GroundednessScore,
        documents: List[RetrievedDocument],
        language: str = "hinglish",
    ) -> Dict[str, Any]:
        """
        Generate final output with appropriate confidence indicators.

        Args:
            answer: Base answer text
            groundedness: Groundedness score
            documents: Supporting documents
            language: Output language ("english" or "hinglish")

        Returns:
            Dict with output, confidence, and metadata
        """
        output_type = groundedness.output_type()
        confidence = groundedness.confidence_level()

        prompt_prefix, prompt_suffix = OutputGenerator.PROMPTS[output_type]

        # Generate confidence-qualified output
        if output_type == OutputType.DIRECT_ANSWER:
            final_answer = answer
        elif output_type == OutputType.QUALIFIED_ANSWER:
            final_answer = answer + prompt_suffix
        elif output_type == OutputType.UNCERTAIN_ANSWER:
            final_answer = answer + prompt_suffix
        else:  # NO_MATCH
            final_answer = prompt_suffix

        # Add attribution
        final_answer = OutputGenerator.format_attribution(answer, documents, groundedness)

        return {
            "output": final_answer,
            "output_type": output_type.value,
            "confidence_level": confidence.value,
            "groundedness_score": groundedness.overall_score,
            "groundedness_breakdown": {
                "max_similarity": round(groundedness.max_similarity, 2),
                "avg_similarity": round(groundedness.avg_similarity, 2),
                "num_supporting_docs": groundedness.num_supporting_docs,
                "coverage": round(groundedness.coverage, 2),
                "consistency": round(groundedness.consistency, 2),
            },
            "source_documents": [
                {
                    "doc_id": d.doc_id,
                    "similarity": round(d.similarity_score, 2),
                }
                for d in documents[:3]
            ],
        }


class SynthesisLimiter:
    """Enforce synthesis limits to prevent hallucination."""

    MAX_DOCUMENTS_PER_OUTPUT = 3
    MAX_RETRIEVAL_RESULTS = 10

    @staticmethod
    def select_top_documents(
        documents: List[RetrievedDocument],
        max_docs: int = MAX_DOCUMENTS_PER_OUTPUT,
    ) -> List[RetrievedDocument]:
        """
        Select top N documents by relevance.

        Args:
            documents: Retrieved documents
            max_docs: Maximum documents to include

        Returns:
            Top N documents sorted by similarity
        """
        sorted_docs = sorted(documents, key=lambda d: d.similarity_score, reverse=True)
        selected = sorted_docs[:max_docs]

        logger.debug(
            f"Selected {len(selected)}/{len(documents)} documents for synthesis "
            f"(similarities: {[f'{d.similarity_score:.2f}' for d in selected]})"
        )

        return selected

    @staticmethod
    def validate_synthesis(
        documents: List[RetrievedDocument],
        answer: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that synthesis doesn't exceed limits.

        Args:
            documents: Documents used for synthesis
            answer: Generated answer

        Returns:
            Tuple of (is_valid, error_message_or_none)
        """
        if len(documents) > SynthesisLimiter.MAX_DOCUMENTS_PER_OUTPUT:
            error = (
                f"Synthesis limit exceeded: {len(documents)} documents "
                f"(max {SynthesisLimiter.MAX_DOCUMENTS_PER_OUTPUT})"
            )
            return False, error

        # Check for hallucination signals
        if not documents and len(answer) > 50:
            return False, "Non-trivial answer with no supporting documents"

        return True, None

    @staticmethod
    def format_synthesis_report(
        documents: List[RetrievedDocument],
        groundedness: GroundednessScore,
    ) -> str:
        """
        Format a report of the synthesis process.

        Args:
            documents: Documents used
            groundedness: Groundedness score

        Returns:
            Formatted report
        """
        report = f"""
╔═══════════════════════════════════════════════════════════════════╗
║                  SYNTHESIS REPORT                                 ║
╚═══════════════════════════════════════════════════════════════════╝

📊 Groundedness Score: {groundedness.overall_score:.2f}
   Confidence: {groundedness.confidence_level().value.upper()}

📚 Documents Used: {len(documents)}/{SynthesisLimiter.MAX_DOCUMENTS_PER_OUTPUT} (limit)

📈 Similarity Scores:
"""
        for i, doc in enumerate(documents, 1):
            report += f"   {i}. {doc.doc_id:<30} {doc.similarity_score:.2%}\n"

        report += f"""
🎯 Coverage: {groundedness.coverage:.0%}
🤝 Consistency: {groundedness.consistency:.2f}
"""
        return report.strip()
