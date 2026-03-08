"""
Conflict-Aware Ingestion Pipeline — Truth Engine integration for insertions.

Implements:
- Pre-insertion conflict checking
- Conflict scoring and categorization
- User-driven resolution workflow
- Change logging and audit trails
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import chromadb

from life_brain.db.document_validator import DocumentValidator, ValidationResult
from life_brain.db.error_reporter import ValidationError

logger = logging.getLogger(__name__)


class ConflictType(str, Enum):
    """Type of conflict detected."""
    NO_CONFLICT = "no_conflict"
    SOFT_CONFLICT = "soft_conflict"
    HARD_CONFLICT = "hard_conflict"
    ENRICHMENT = "enrichment"


@dataclass
class ConflictScore:
    """Quantitative conflict assessment."""

    semantic_similarity: float  # 0-1, cosine similarity of embeddings
    contradiction_magnitude: float  # 0-1, how much they contradict
    overall_score: float  # 0-1, semantic_sim * contradiction_mag

    def __post_init__(self):
        """Validate scores are in range."""
        assert 0 <= self.semantic_similarity <= 1.0
        assert 0 <= self.contradiction_magnitude <= 1.0
        assert 0 <= self.overall_score <= 1.0


@dataclass
class ConflictCandidate:
    """An existing document that may conflict with new one."""

    doc_id: str
    existing_text: str
    existing_metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    conflict_score: float = 0.0


@dataclass
class ConflictDetectionResult:
    """Result of conflict detection."""

    has_conflict: bool
    conflict_type: ConflictType
    score: ConflictScore
    candidate: Optional[ConflictCandidate] = None
    reason: str = ""
    recommendation: str = ""
    resolution_options: List[str] = field(default_factory=list)


class ConflictDetector:
    """Detects conflicts between new and existing documents."""

    # Thresholds for conflict categorization
    CONFLICT_THRESHOLD = 0.6  # Hard conflict
    SOFT_CONFLICT_THRESHOLD = 0.3  # Soft conflict
    ENRICHMENT_THRESHOLD = 0.1  # Enrichment (new info adds detail)

    def __init__(self, collection: chromadb.Collection):
        """
        Initialize conflict detector.

        Args:
            collection: ChromaDB collection to query for conflicts
        """
        self.collection = collection

    def query_similar_documents(
        self,
        text: str,
        domain: Optional[str] = None,
        n_results: int = 5,
    ) -> List[ConflictCandidate]:
        """
        Query collection for semantically similar documents.

        Args:
            text: New document text to query with
            domain: Optional domain filter
            n_results: Number of similar documents to retrieve

        Returns:
            List of ConflictCandidate objects
        """
        try:
            where_filter = None
            if domain:
                where_filter = {"domain": domain}

            results = self.collection.query(
                query_texts=[text],
                n_results=n_results,
                where=where_filter,
                include=["embeddings", "metadatas", "documents", "distances"]
            )

            candidates = []
            if results and results.get("ids") and len(results["ids"]) > 0:
                for i, doc_id in enumerate(results["ids"][0]):
                    # Convert distance to similarity (cosine distance → similarity)
                    distance = results.get("distances", [[]])[0][i] if results.get("distances") else 0
                    similarity = 1 - distance  # Convert distance to similarity

                    candidate = ConflictCandidate(
                        doc_id=doc_id,
                        existing_text=results.get("documents", [[]])[0][i] if results.get("documents") else "",
                        existing_metadata=results.get("metadatas", [[]])[0][i] if results.get("metadatas") else {},
                        embedding=results.get("embeddings", [[]])[0][i] if results.get("embeddings") else None,
                        conflict_score=similarity,
                    )
                    candidates.append(candidate)

            logger.debug(f"Found {len(candidates)} similar documents for conflict check")
            return candidates

        except Exception as e:
            logger.warning(f"Error querying similar documents: {e}")
            return []

    def measure_contradiction(
        self,
        new_text: str,
        existing_text: str,
    ) -> float:
        """
        Measure how much new and existing documents contradict.

        Simple heuristic: check for negations, opposite claims, etc.

        Args:
            new_text: New document text
            existing_text: Existing document text

        Returns:
            Contradiction magnitude (0-1)
        """
        new_lower = new_text.lower()
        existing_lower = existing_text.lower()

        # Check for explicit contradictions
        negation_words = ["not", "no", "never", "doesn't", "didn't", "won't", "cannot", "can't"]
        new_has_negation = any(f" {word} " in f" {new_lower} " for word in negation_words)
        existing_has_negation = any(f" {word} " in f" {existing_lower} " for word in negation_words)

        # If one has negation and other doesn't, could be contradiction
        if new_has_negation != existing_has_negation:
            return 0.5

        # Exact opposite phrases indicate strong contradiction
        opposite_pairs = [
            ("yes", "no"),
            ("true", "false"),
            ("success", "failure"),
            ("passed", "failed"),
        ]

        for positive, negative in opposite_pairs:
            if positive in new_lower and negative in existing_lower:
                return 0.9
            if negative in new_lower and positive in existing_lower:
                return 0.9

        # Numerical conflicts (example: different metrics)
        import re
        new_numbers = re.findall(r'\d+', new_text)
        existing_numbers = re.findall(r'\d+', existing_text)

        if new_numbers and existing_numbers:
            # Simple heuristic: if ranges don't overlap significantly, might contradict
            new_max = max(int(n) for n in new_numbers)
            existing_max = max(int(n) for n in existing_numbers)
            if new_max > 0 and existing_max > 0:
                ratio = min(new_max, existing_max) / max(new_max, existing_max)
                if ratio < 0.5:  # Significant difference
                    return 0.4

        # Default: no obvious contradiction
        return 0.0

    def calculate_conflict_score(
        self,
        semantic_similarity: float,
        contradiction_magnitude: float,
    ) -> ConflictScore:
        """
        Calculate overall conflict score.

        Formula: conflict_score = semantic_similarity * contradiction_magnitude

        Args:
            semantic_similarity: Cosine similarity (0-1)
            contradiction_magnitude: Contradiction level (0-1)

        Returns:
            ConflictScore object
        """
        overall_score = semantic_similarity * contradiction_magnitude
        return ConflictScore(
            semantic_similarity=semantic_similarity,
            contradiction_magnitude=contradiction_magnitude,
            overall_score=overall_score,
        )

    def detect_conflict(
        self,
        new_text: str,
        new_metadata: Dict[str, Any],
        existing_candidates: Optional[List[ConflictCandidate]] = None,
    ) -> ConflictDetectionResult:
        """
        Comprehensive conflict detection for new document.

        Args:
            new_text: New document text
            new_metadata: New document metadata
            existing_candidates: Optional pre-fetched candidates (avoids re-querying)

        Returns:
            ConflictDetectionResult with findings and recommendations
        """
        # Fetch similar documents if not provided
        if existing_candidates is None:
            domain = new_metadata.get("domain")
            existing_candidates = self.query_similar_documents(new_text, domain=domain)

        if not existing_candidates:
            logger.debug("No similar documents found, no conflict possible")
            return ConflictDetectionResult(
                has_conflict=False,
                conflict_type=ConflictType.NO_CONFLICT,
                score=ConflictScore(0, 0, 0),
                reason="No similar documents in database",
            )

        # Check each candidate for conflicts
        highest_conflict_type = ConflictType.NO_CONFLICT
        highest_score: Optional[ConflictScore] = None
        worst_candidate: Optional[ConflictCandidate] = None

        for candidate in existing_candidates:
            # Measure contradiction
            contradiction = self.measure_contradiction(new_text, candidate.existing_text)

            # Calculate overall score
            score = self.calculate_conflict_score(
                semantic_similarity=candidate.conflict_score,
                contradiction_magnitude=contradiction,
            )

            logger.debug(
                f"Checking candidate {candidate.doc_id}: "
                f"similarity={score.semantic_similarity:.2f}, "
                f"contradiction={score.contradiction_magnitude:.2f}, "
                f"overall={score.overall_score:.2f}"
            )

            # Categorize conflict
            if score.overall_score >= self.CONFLICT_THRESHOLD:
                if score.overall_score > (highest_score.overall_score if highest_score else 0):
                    highest_conflict_type = ConflictType.HARD_CONFLICT
                    highest_score = score
                    worst_candidate = candidate

            elif score.overall_score >= self.SOFT_CONFLICT_THRESHOLD:
                if highest_conflict_type != ConflictType.HARD_CONFLICT:
                    if score.overall_score > (highest_score.overall_score if highest_score else 0):
                        highest_conflict_type = ConflictType.SOFT_CONFLICT
                        highest_score = score
                        worst_candidate = candidate

            elif score.overall_score >= self.ENRICHMENT_THRESHOLD:
                if highest_conflict_type == ConflictType.NO_CONFLICT:
                    highest_conflict_type = ConflictType.ENRICHMENT
                    highest_score = score
                    worst_candidate = candidate

        # Prepare result
        has_conflict = highest_conflict_type in [ConflictType.HARD_CONFLICT, ConflictType.SOFT_CONFLICT]

        if not highest_score:
            highest_score = ConflictScore(0, 0, 0)

        result = ConflictDetectionResult(
            has_conflict=has_conflict,
            conflict_type=highest_conflict_type,
            score=highest_score,
            candidate=worst_candidate,
        )

        # Add details based on conflict type
        if highest_conflict_type == ConflictType.NO_CONFLICT:
            result.reason = "No conflicts detected"
            result.recommendation = "Proceed with ingestion"
            result.resolution_options = ["proceed"]

        elif highest_conflict_type == ConflictType.ENRICHMENT:
            result.reason = f"New info may enrich existing document {worst_candidate.doc_id}"
            result.recommendation = "Consider updating existing document with new info"
            result.resolution_options = ["proceed_independent", "merge_with_existing"]

        elif highest_conflict_type == ConflictType.SOFT_CONFLICT:
            result.reason = f"Soft conflict with {worst_candidate.doc_id} (score: {highest_score.overall_score:.2f})"
            result.recommendation = "Review and clarify which version is correct"
            result.resolution_options = [
                "accept_new",  # Discard existing, use new
                "accept_existing",  # Discard new, keep existing
                "add_context",  # Add context to distinguish (e.g., "in Q1" vs "in Q2")
            ]

        elif highest_conflict_type == ConflictType.HARD_CONFLICT:
            result.reason = f"Hard conflict with {worst_candidate.doc_id} (score: {highest_score.overall_score:.2f})"
            result.recommendation = "BLOCK: Cannot proceed. User must resolve conflict."
            result.resolution_options = [
                "ask_user_which_is_correct",
                "add_context_to_both",
                "manual_review",
            ]

        logger.info(f"Conflict detection result: {result.conflict_type.value} — {result.reason}")
        return result

    def format_conflict_report(self, result: ConflictDetectionResult) -> str:
        """Format conflict detection result as readable report."""
        report = f"""
╔═══════════════════════════════════════════════════════════════════╗
║              CONFLICT DETECTION REPORT                            ║
╚═══════════════════════════════════════════════════════════════════╝

Status: {result.conflict_type.value.upper()}

Similarity Score:     {result.score.semantic_similarity:.2f}
Contradiction:        {result.score.contradiction_magnitude:.2f}
Overall Conflict:     {result.score.overall_score:.2f}

Reason: {result.reason}

Recommendation: {result.recommendation}

Resolution Options:
"""
        for i, option in enumerate(result.resolution_options, 1):
            report += f"  {i}. {option}\n"

        if result.candidate:
            report += f"""
Conflicting Document: {result.candidate.doc_id}
Existing: {result.candidate.existing_text[:100]}...
"""
        return report.strip()


class ConflictAwareIngestionPipeline:
    """End-to-end ingestion with conflict detection and resolution."""

    def __init__(
        self,
        collection: chromadb.Collection,
        validator: Optional[DocumentValidator] = None,
    ):
        """
        Initialize pipeline.

        Args:
            collection: ChromaDB collection
            validator: Optional DocumentValidator (creates if not provided)
        """
        self.collection = collection
        self.validator = validator or DocumentValidator()
        self.detector = ConflictDetector(collection)

    def ingest_with_conflict_check(
        self,
        doc_id: str,
        text: str,
        metadata: Dict[str, Any],
        question: Optional[str] = None,
        answer: Optional[str] = None,
        auto_resolve: bool = False,
    ) -> Dict[str, Any]:
        """
        Full ingestion pipeline: validate, detect conflict, resolve.

        Args:
            doc_id: Document ID
            text: Document text
            metadata: Document metadata
            question: Optional question for Q&A pairs
            answer: Optional answer for Q&A pairs
            auto_resolve: If True, auto-proceed on non-hard conflicts

        Returns:
            Dict with ingestion status and details
        """
        # Step 1: Validation
        val_result = self.validator.validate_document(
            metadata=metadata,
            text=text,
            question=question,
            answer=answer,
        )

        if not val_result.is_valid:
            logger.warning(f"Validation failed for {doc_id}")
            return {
                "status": "validation_failed",
                "doc_id": doc_id,
                "errors": [
                    {
                        "field": e.field,
                        "message": e.message,
                        "suggestion": e.suggestion,
                    }
                    for e in val_result.errors
                ],
            }

        # Step 2: Conflict detection
        conflict_result = self.detector.detect_conflict(new_text=text, new_metadata=metadata)

        if conflict_result.has_conflict:
            logger.warning(f"Conflict detected for {doc_id}: {conflict_result.conflict_type.value}")

            if conflict_result.conflict_type == ConflictType.HARD_CONFLICT:
                # Block hard conflicts
                return {
                    "status": "hard_conflict_detected",
                    "doc_id": doc_id,
                    "conflict_type": conflict_result.conflict_type.value,
                    "conflicting_doc": conflict_result.candidate.doc_id if conflict_result.candidate else None,
                    "score": conflict_result.score.overall_score,
                    "report": self.detector.format_conflict_report(conflict_result),
                    "recommendation": conflict_result.recommendation,
                    "resolution_options": conflict_result.resolution_options,
                }

            elif not auto_resolve:
                # Return conflict for user decision
                return {
                    "status": "soft_conflict_detected",
                    "doc_id": doc_id,
                    "conflict_type": conflict_result.conflict_type.value,
                    "conflicting_doc": conflict_result.candidate.doc_id if conflict_result.candidate else None,
                    "score": conflict_result.score.overall_score,
                    "report": self.detector.format_conflict_report(conflict_result),
                    "recommendation": conflict_result.recommendation,
                    "resolution_options": conflict_result.resolution_options,
                }

        # Step 3: Insert (if no hard conflict or auto-resolved)
        try:
            self.collection.upsert(
                ids=[doc_id],
                metadatas=[metadata],
                documents=[text],
            )
            logger.info(f"Successfully ingested: {doc_id}")
            return {
                "status": "success",
                "doc_id": doc_id,
                "conflict_handled": conflict_result.conflict_type != ConflictType.NO_CONFLICT,
            }

        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            return {
                "status": "ingestion_failed",
                "doc_id": doc_id,
                "error": str(e),
            }
