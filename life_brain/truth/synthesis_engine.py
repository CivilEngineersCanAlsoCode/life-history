"""
Multi-Perspective Synthesis Engine — F5.3

Synthesizes answers from multiple documents considering:
1. Conflicts between sources (from F5.1)
2. Credibility scores (from F5.2)
3. Strategy selection (agree, differ, prefer, unknown)
4. Disclaimer generation for conflicts
5. Source attribution with confidence

Algorithm:
1. Receive docs, conflicts, credibility_scores
2. Rank docs by credibility (descending)
3. Check if conflicts exist:
   - No conflicts: synthesize from highest-credibility source
   - Conflicts: rank by severity and apply strategy:
     * Both high-credibility: "differ" (present both)
     * One high-credibility: "prefer" (note conflict)
     * Low credibility conflict: "unknown" (insufficient consensus)
4. Add disclaimers and attribution
5. Return SynthesisResult
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# DATACLASSES
# ============================================================================

@dataclass(frozen=True)
class SynthesisResult:
    """Result of multi-perspective synthesis."""

    answer: str                        # Generated answer text
    strategy: str                      # "agree", "differ", "prefer", "unknown"
    conflicts_handled: List[Any]       # List of ConflictResult objects handled
    preferred_sources: List[str]       # doc_ids ranked by credibility (highest first)
    disclaimer: Optional[str]          # Added if conflicts exist
    attribution: str                   # Source citations with confidence


class SynthesisEngine:
    """
    Synthesize answers from multiple documents considering conflicts and credibility.

    Strategies:
    - "agree": All sources agree or no conflicts detected
    - "differ": Sources disagree and both are highly credible (present both)
    - "prefer": Sources disagree but one is more credible (prefer high, note conflict)
    - "unknown": Insufficient consensus or low credibility conflict
    """

    # Credibility thresholds for strategy selection
    HIGH_CREDIBILITY_THRESHOLD = 0.75
    MEDIUM_CREDIBILITY_THRESHOLD = 0.50

    def __init__(self):
        """Initialize the SynthesisEngine."""
        pass

    def synthesize(
        self,
        docs: List[Any],
        conflicts: List[Any],
        credibility_scores: List[Any]
    ) -> SynthesisResult:
        """
        Synthesize answer from multiple documents with conflict awareness.

        Args:
            docs: List of RetrievedDocument objects (1-3)
            conflicts: List of ConflictResult from F5.1 (may be empty)
            credibility_scores: List of CredibilityScore from F5.2 (one per doc)

        Returns:
            SynthesisResult with answer, strategy, conflicts, sources, disclaimer, attribution

        Algorithm:
        1. Build credibility map (doc_id -> CredibilityScore)
        2. Rank documents by credibility
        3. Check for conflicts:
           - No conflicts: synthesize single answer from top source
           - Conflicts exist:
             * Filter conflicts by severity
             * Apply strategy based on credibility of conflicting sources
             * Generate answer and disclaimer accordingly
        4. Build attribution with source citations
        5. Return SynthesisResult
        """
        if not docs:
            return SynthesisResult(
                answer="No documents provided for synthesis.",
                strategy="unknown",
                conflicts_handled=[],
                preferred_sources=[],
                disclaimer=None,
                attribution="No sources available."
            )

        # Step 1: Build credibility map
        credibility_map = self._build_credibility_map(docs, credibility_scores)

        # Step 2: Rank documents by credibility
        ranked_doc_ids = self._rank_docs_by_credibility(docs, credibility_map)

        # Step 3: Determine strategy and synthesis
        if not conflicts:
            # No conflicts: synthesize from top source
            strategy = "agree"
            answer = self._synthesize_single_answer(docs, ranked_doc_ids)
            conflicts_handled = []
            disclaimer = None
        else:
            # Conflicts exist: apply strategy
            strategy, answer, conflicts_handled, disclaimer = self._handle_conflicts(
                docs, conflicts, ranked_doc_ids, credibility_map
            )

        # Step 4: Build attribution
        attribution = self._build_attribution(
            ranked_doc_ids, credibility_map, conflicts_handled
        )

        # Step 5: Return result
        return SynthesisResult(
            answer=answer,
            strategy=strategy,
            conflicts_handled=conflicts_handled,
            preferred_sources=ranked_doc_ids,
            disclaimer=disclaimer,
            attribution=attribution
        )

    def add_conflict_disclaimer(
        self,
        answer: str,
        conflicts: List[Any],
        credibility_scores: List[Any]
    ) -> str:
        """
        Add a disclaimer to answer if conflicts are present.

        Args:
            answer: Generated answer text
            conflicts: List of ConflictResult objects
            credibility_scores: List of CredibilityScore objects

        Returns:
            Answer with disclaimer appended if needed

        Disclaimer templates:
        - Both high credibility: "Multiple sources have different perspectives on this."
        - One high credibility: "Primary source indicates X; conflicting information exists."
        - Low credibility conflict: "Multiple conflicting sources with low credibility."
        """
        if not conflicts:
            return answer

        # Build credibility map
        credibility_map = {cs.doc_id: cs for cs in credibility_scores}

        # Analyze conflict credibilities
        high_cred_count = 0
        low_cred_count = 0

        for conflict in conflicts:
            # Get doc indices from conflict
            if hasattr(conflict, 'doc_pair'):
                doc_indices = conflict.doc_pair
                # Count high credibility sources in this conflict
                for idx in doc_indices:
                    if idx < len(credibility_scores):
                        score = credibility_scores[idx].credibility
                        if score >= self.HIGH_CREDIBILITY_THRESHOLD:
                            high_cred_count += 1
                        else:
                            low_cred_count += 1

        # Generate disclaimer based on credibility profile
        if high_cred_count >= 2:
            disclaimer = (
                "\nNote: Multiple sources have different perspectives on this. "
                "Consider consulting the original sources for complete context."
            )
        elif high_cred_count == 1:
            disclaimer = (
                "\nNote: This answer is based on a primary source; "
                "however, some conflicting information exists in other sources."
            )
        else:
            disclaimer = (
                "\nCaution: Multiple conflicting sources with lower credibility. "
                "This answer reflects the best available information."
            )

        return answer + disclaimer

    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================

    def _build_credibility_map(
        self,
        docs: List[Any],
        credibility_scores: List[Any]
    ) -> Dict[str, float]:
        """
        Build mapping from doc_id to credibility score.

        Args:
            docs: List of RetrievedDocument objects
            credibility_scores: List of CredibilityScore objects

        Returns:
            Dictionary mapping doc_id -> credibility (0-1)
        """
        credibility_map = {}

        # Map by position first (fallback if doc_id mismatch)
        for i, (doc, score) in enumerate(zip(docs, credibility_scores)):
            if hasattr(score, 'doc_id') and score.doc_id:
                credibility_map[score.doc_id] = score.credibility
            elif hasattr(doc, 'doc_id'):
                credibility_map[doc.doc_id] = score.credibility if hasattr(score, 'credibility') else 0.5

        return credibility_map

    def _rank_docs_by_credibility(
        self,
        docs: List[Any],
        credibility_map: Dict[str, float]
    ) -> List[str]:
        """
        Rank documents by credibility score (highest first).

        Args:
            docs: List of RetrievedDocument objects
            credibility_map: Mapping of doc_id -> credibility

        Returns:
            List of doc_ids sorted by credibility (descending)
        """
        doc_ids_with_scores = []

        for doc in docs:
            doc_id = doc.doc_id if hasattr(doc, 'doc_id') else str(id(doc))
            credibility = credibility_map.get(doc_id, 0.5)
            doc_ids_with_scores.append((doc_id, credibility))

        # Sort by credibility descending
        doc_ids_with_scores.sort(key=lambda x: x[1], reverse=True)
        return [doc_id for doc_id, _ in doc_ids_with_scores]

    def _synthesize_single_answer(
        self,
        docs: List[Any],
        ranked_doc_ids: List[str]
    ) -> str:
        """
        Synthesize answer from single top-credibility source.

        Args:
            docs: List of RetrievedDocument objects
            ranked_doc_ids: List of doc_ids ranked by credibility

        Returns:
            Synthesized answer text
        """
        if not ranked_doc_ids or not docs:
            return "Unable to synthesize answer from provided documents."

        # Find the top-ranked document
        top_doc_id = ranked_doc_ids[0]
        top_doc = None

        for doc in docs:
            if hasattr(doc, 'doc_id') and doc.doc_id == top_doc_id:
                top_doc = doc
                break

        if not top_doc:
            # Fallback: use first doc
            top_doc = docs[0]

        # Extract text from document
        text = top_doc.text if hasattr(top_doc, 'text') else str(top_doc)

        # Return first sentence or chunk (simplified synthesis)
        return self._extract_summary(text)

    def _handle_conflicts(
        self,
        docs: List[Any],
        conflicts: List[Any],
        ranked_doc_ids: List[str],
        credibility_map: Dict[str, float]
    ) -> Tuple[str, str, List[Any], Optional[str]]:
        """
        Handle conflicts and determine synthesis strategy.

        Args:
            docs: List of RetrievedDocument objects
            conflicts: List of ConflictResult objects
            ranked_doc_ids: List of doc_ids ranked by credibility
            credibility_map: Mapping of doc_id -> credibility

        Returns:
            Tuple of (strategy, answer, conflicts_handled, disclaimer)

        Strategy selection:
        - "differ": Both sources high credibility (>0.75) → present both
        - "prefer": One high credibility → prefer high, note conflict
        - "unknown": Low credibility conflict → insufficient consensus
        """
        # Sort conflicts by severity (highest first)
        sorted_conflicts = self._sort_conflicts_by_severity(conflicts)

        if not sorted_conflicts:
            strategy = "agree"
            answer = self._synthesize_single_answer(docs, ranked_doc_ids)
            return strategy, answer, [], None

        # Analyze top conflict
        top_conflict = sorted_conflicts[0]
        conflicts_handled = [top_conflict]

        # Get credibility of conflicting sources
        credibility_1 = self._get_conflict_credibility(docs, top_conflict, 0, credibility_map)
        credibility_2 = self._get_conflict_credibility(docs, top_conflict, 1, credibility_map)

        logger.debug(
            f"Conflict analysis: credibility_1={credibility_1:.2f}, "
            f"credibility_2={credibility_2:.2f}"
        )

        # Determine strategy
        if credibility_1 >= self.HIGH_CREDIBILITY_THRESHOLD and \
           credibility_2 >= self.HIGH_CREDIBILITY_THRESHOLD:
            # Both high credibility: present both perspectives
            strategy = "differ"
            answer = self._synthesize_differ_answer(
                docs, top_conflict, ranked_doc_ids, credibility_map
            )
            disclaimer = (
                "Sources have conflicting information on this topic. "
                "Both perspectives are from credible sources."
            )

        elif credibility_1 >= self.HIGH_CREDIBILITY_THRESHOLD or \
             credibility_2 >= self.HIGH_CREDIBILITY_THRESHOLD:
            # One high credibility: prefer high, note conflict
            strategy = "prefer"
            answer = self._synthesize_prefer_answer(
                docs, top_conflict, ranked_doc_ids, credibility_map
            )
            disclaimer = (
                "Primary source provides this answer; "
                "however, some sources present conflicting information."
            )

        else:
            # Low credibility conflict: insufficient consensus
            strategy = "unknown"
            answer = (
                "Multiple conflicting sources exist on this topic, "
                "but with insufficient credibility to provide a definitive answer."
            )
            disclaimer = (
                "The available sources contain conflicting information. "
                "Please consult additional sources for a complete picture."
            )

        return strategy, answer, conflicts_handled, disclaimer

    def _synthesize_differ_answer(
        self,
        docs: List[Any],
        conflict: Any,
        ranked_doc_ids: List[str],
        credibility_map: Dict[str, float]
    ) -> str:
        """
        Synthesize answer presenting both conflicting perspectives.

        Args:
            docs: List of RetrievedDocument objects
            conflict: ConflictResult object
            ranked_doc_ids: List of doc_ids ranked by credibility
            credibility_map: Mapping of doc_id -> credibility

        Returns:
            Answer text presenting both perspectives
        """
        if not hasattr(conflict, 'claim1') or not hasattr(conflict, 'claim2'):
            return "Conflicting information exists between sources."

        credibility_1 = self._get_conflict_credibility(docs, conflict, 0, credibility_map)
        credibility_2 = self._get_conflict_credibility(docs, conflict, 1, credibility_map)

        answer = (
            f"Sources provide different perspectives: "
            f"Source A states '{conflict.claim1}' (credibility: {credibility_1:.0%}), "
            f"while Source B states '{conflict.claim2}' (credibility: {credibility_2:.0%})."
        )

        return answer

    def _synthesize_prefer_answer(
        self,
        docs: List[Any],
        conflict: Any,
        ranked_doc_ids: List[str],
        credibility_map: Dict[str, float]
    ) -> str:
        """
        Synthesize answer preferring higher-credibility source.

        Args:
            docs: List of RetrievedDocument objects
            conflict: ConflictResult object
            ranked_doc_ids: List of doc_ids ranked by credibility
            credibility_map: Mapping of doc_id -> credibility

        Returns:
            Answer text preferring higher-credibility source
        """
        if not hasattr(conflict, 'claim1') or not hasattr(conflict, 'claim2'):
            return "Primary source indicates a particular perspective."

        credibility_1 = self._get_conflict_credibility(docs, conflict, 0, credibility_map)
        credibility_2 = self._get_conflict_credibility(docs, conflict, 1, credibility_map)

        # Determine which is more credible
        if credibility_1 >= credibility_2:
            preferred_claim = conflict.claim1
            alternative_claim = conflict.claim2
            preferred_cred = credibility_1
        else:
            preferred_claim = conflict.claim2
            alternative_claim = conflict.claim1
            preferred_cred = credibility_2

        answer = (
            f"{preferred_claim} "
            f"(primary source: {preferred_cred:.0%} credibility) — "
            f"though some sources suggest '{alternative_claim}'."
        )

        return answer

    def _build_attribution(
        self,
        ranked_doc_ids: List[str],
        credibility_map: Dict[str, float],
        conflicts_handled: List[Any]
    ) -> str:
        """
        Build attribution string with source citations and confidence.

        Args:
            ranked_doc_ids: List of doc_ids ranked by credibility
            credibility_map: Mapping of doc_id -> credibility
            conflicts_handled: List of ConflictResult objects handled

        Returns:
            Attribution string
        """
        if not ranked_doc_ids:
            return "No sources cited."

        citations = []

        for doc_id in ranked_doc_ids[:3]:  # Max 3 sources
            credibility = credibility_map.get(doc_id, 0.5)
            confidence_label = self._credibility_to_label(credibility)
            citations.append(f"{doc_id} ({confidence_label})")

        attribution = "Sources: " + ", ".join(citations)

        if conflicts_handled:
            attribution += f" (with {len(conflicts_handled)} conflict(s) noted)"

        return attribution

    def _sort_conflicts_by_severity(self, conflicts: List[Any]) -> List[Any]:
        """
        Sort conflicts by severity (highest first).

        Args:
            conflicts: List of ConflictResult objects

        Returns:
            Sorted list of ConflictResult objects
        """
        if not conflicts:
            return []

        def get_severity_score(conflict: Any) -> float:
            """Get numeric score for severity sorting."""
            if hasattr(conflict, 'conflict_score'):
                return conflict.conflict_score
            elif isinstance(conflict, dict) and 'conflict_score' in conflict:
                return conflict['conflict_score']
            return 0.0

        sorted_conflicts = sorted(conflicts, key=get_severity_score, reverse=True)
        return sorted_conflicts

    def _get_conflict_credibility(
        self,
        docs: List[Any],
        conflict: Any,
        conflict_index: int,
        credibility_map: Dict[str, float]
    ) -> float:
        """
        Get credibility score for a source involved in a conflict.

        Args:
            docs: List of RetrievedDocument objects
            conflict: ConflictResult object with doc_pair
            conflict_index: Which source in conflict (0 or 1)
            credibility_map: Mapping of doc_id -> credibility

        Returns:
            Credibility score (0-1)
        """
        if not hasattr(conflict, 'doc_pair'):
            return 0.5  # Default fallback

        doc_index = conflict.doc_pair[conflict_index]

        if 0 <= doc_index < len(docs):
            doc = docs[doc_index]
            doc_id = doc.doc_id if hasattr(doc, 'doc_id') else str(id(doc))
            return credibility_map.get(doc_id, 0.5)

        return 0.5  # Default fallback

    def _credibility_to_label(self, credibility: float) -> str:
        """
        Convert credibility score to human-readable label.

        Args:
            credibility: Credibility score (0-1)

        Returns:
            Label like "high", "medium", "low"
        """
        if credibility >= 0.85:
            return "expert"
        elif credibility >= 0.75:
            return "verified"
        elif credibility >= 0.50:
            return "personal"
        else:
            return "questionable"

    def _extract_summary(self, text: str, max_length: int = 200) -> str:
        """
        Extract summary from document text.

        Args:
            text: Full document text
            max_length: Maximum length of summary

        Returns:
            Summary text
        """
        if not text:
            return "No text available."

        # Take first sentence
        sentences = text.split('.')
        if sentences:
            summary = sentences[0].strip()
            if summary:
                return summary + "."

        # Fallback: truncate
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text
