"""
Nugget identification for atomic fact extraction.

Identifies and extracts atomic facts (nuggets) from text by extracting
subject-predicate pairs that represent standalone, verifiable claims.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re


class NuggetType(Enum):
    """Type of nugget/atomic fact."""

    DEFINITION = "definition"  # X is/are Y
    PROPERTY = "property"  # X has/have Y
    ACTION = "action"  # X did/does Y
    RELATIONSHIP = "relationship"  # X relates to Y
    ATTRIBUTE = "attribute"  # X is adjective
    QUANTITY = "quantity"  # X has number Y
    TEMPORAL = "temporal"  # X happens at time Y


@dataclass
class SubjectPredicatePair:
    """Subject-predicate atomic fact."""

    subject: str  # The entity/topic
    predicate: str  # The claim about the subject
    nugget_type: NuggetType
    confidence: float  # 0-1, confidence in extraction
    source_sentence: str  # Original sentence
    keywords: List[str] = field(default_factory=list)


@dataclass
class IdentifiedNugget:
    """Identified nugget with metadata."""

    nugget_id: str
    subject_predicate: SubjectPredicatePair
    context: str  # Broader context from the document
    importance_score: float  # 0-1, how important this fact is
    related_nuggets: List[str] = field(default_factory=list)  # IDs of related nuggets
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "nugget_id": self.nugget_id,
            "subject": self.subject_predicate.subject,
            "predicate": self.subject_predicate.predicate,
            "type": self.subject_predicate.nugget_type.value,
            "confidence": self.subject_predicate.confidence,
            "importance_score": self.importance_score,
            "context": self.context,
            "keywords": self.subject_predicate.keywords,
            "created_at": self.created_at,
        }


class NuggetIdentifier:
    """Identify atomic facts (nuggets) from text."""

    # Verb patterns for different nugget types
    DEFINITION_VERBS = ["is", "are", "was", "were", "being", "be"]
    PROPERTY_VERBS = ["has", "have", "had", "having", "owns", "contains"]
    ACTION_VERBS = [
        "did", "does", "do", "made", "makes", "created", "creates", "built",
        "wrote", "writes", "developed", "develops", "implemented", "implements"
    ]
    RELATIONSHIP_VERBS = [
        "relates", "connected", "associated", "linked", "refers", "belongs"
    ]

    # Stop words that shouldn't be subjects
    STOP_SUBJECTS = {
        "the", "a", "an", "this", "that", "these", "those", "it", "they"
    }

    def __init__(self):
        """Initialize nugget identifier."""
        self.nuggets: Dict[str, IdentifiedNugget] = {}
        self.nugget_history: List[IdentifiedNugget] = []

    def identify_nuggets(self, text: str, context: str = "") -> Tuple[List[IdentifiedNugget], Optional[str]]:
        """
        Identify atomic facts from text.

        Args:
            text: Text to extract nuggets from
            context: Broader context for importance scoring

        Returns:
            (List of identified nuggets, error if any)
        """
        if not text or not text.strip():
            return [], "Empty text"

        nuggets = []

        # Split into sentences
        sentences = self._split_sentences(text)

        for sentence in sentences:
            # Extract subject-predicate pairs
            pairs = self._extract_subject_predicate_pairs(sentence)

            for pair in pairs:
                importance = self._calculate_importance(pair, context)

                nugget_id = f"nug_{len(self.nuggets):04d}"
                nugget = IdentifiedNugget(
                    nugget_id=nugget_id,
                    subject_predicate=pair,
                    context=context,
                    importance_score=importance,
                )

                self.nuggets[nugget_id] = nugget
                self.nugget_history.append(nugget)
                nuggets.append(nugget)

        # Link related nuggets
        self._link_related_nuggets(nuggets)

        return nuggets, None

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting on punctuation
        sentences = re.split(r"[.!?]+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _extract_subject_predicate_pairs(self, sentence: str) -> List[SubjectPredicatePair]:
        """Extract subject-predicate pairs from a sentence."""
        pairs = []
        sentence_lower = sentence.lower()

        # Try to identify subject and predicate
        # Pattern: [Subject] [Verb] [Predicate]

        # Try different verb patterns
        for nugget_type, verbs in [
            (NuggetType.DEFINITION, self.DEFINITION_VERBS),
            (NuggetType.PROPERTY, self.PROPERTY_VERBS),
            (NuggetType.ACTION, self.ACTION_VERBS),
            (NuggetType.RELATIONSHIP, self.RELATIONSHIP_VERBS),
        ]:
            for verb in verbs:
                # Look for verb in sentence
                pattern = rf"\b{verb}\b"
                if re.search(pattern, sentence_lower, re.IGNORECASE):
                    # Try to split around the verb
                    parts = re.split(pattern, sentence, flags=re.IGNORECASE)
                    if len(parts) >= 2:
                        subject = parts[0].strip()
                        predicate = " ".join(parts[1:]).strip()

                        # Clean up subject and predicate
                        subject = self._clean_subject(subject)
                        predicate = self._clean_predicate(predicate)

                        if subject and predicate:
                            # Calculate confidence
                            confidence = self._calculate_extraction_confidence(
                                subject, predicate, verb, nugget_type
                            )

                            # Extract keywords
                            keywords = self._extract_keywords(predicate)

                            pair = SubjectPredicatePair(
                                subject=subject,
                                predicate=predicate,
                                nugget_type=nugget_type,
                                confidence=confidence,
                                source_sentence=sentence,
                                keywords=keywords,
                            )
                            pairs.append(pair)
                            break  # Found a pattern, move to next sentence

        return pairs

    def _clean_subject(self, subject: str) -> str:
        """Clean extracted subject."""
        subject = subject.strip()

        # Remove leading articles
        subject = re.sub(r"^(the|a|an|this|that|these|those)\s+", "", subject, flags=re.IGNORECASE)

        # Remove trailing punctuation
        subject = subject.rstrip(",.;:\"'")

        # Capitalize first letter
        if subject:
            subject = subject[0].upper() + subject[1:] if len(subject) > 1 else subject.upper()

        return subject

    def _clean_predicate(self, predicate: str) -> str:
        """Clean extracted predicate."""
        predicate = predicate.strip()

        # Remove trailing punctuation
        predicate = predicate.rstrip(",.;:\"'")

        return predicate

    def _calculate_extraction_confidence(
        self, subject: str, predicate: str, verb: str, nugget_type: NuggetType
    ) -> float:
        """Calculate confidence in the extraction."""
        confidence = 0.7  # Base confidence

        # Boost for longer, more specific subject
        if len(subject) > 5:
            confidence += 0.1

        # Boost for longer predicate with detail
        if len(predicate) > 15:
            confidence += 0.1

        # Boost for less ambiguous verb types
        if nugget_type == NuggetType.DEFINITION:
            confidence += 0.05

        # Cap at 1.0
        return min(1.0, confidence)

    def _extract_keywords(self, predicate: str) -> List[str]:
        """Extract keywords from predicate."""
        words = predicate.split()
        # Take meaningful words (4+ chars)
        keywords = [w.lower() for w in words if len(w) > 3 and not w.startswith("'")]
        return keywords[:5]  # Top 5

    def _calculate_importance(self, pair: SubjectPredicatePair, context: str) -> float:
        """Calculate importance score of a nugget."""
        importance = pair.confidence * 0.5

        # Boost if subject appears in context
        if context and pair.subject.lower() in context.lower():
            importance += 0.2

        # Boost for action and definition types (more informative)
        if pair.nugget_type in [NuggetType.ACTION, NuggetType.DEFINITION]:
            importance += 0.1

        # Boost for longer predicates (more specific)
        if len(pair.predicate) > 20:
            importance += 0.1

        return min(1.0, importance)

    def _link_related_nuggets(self, nuggets: List[IdentifiedNugget]) -> None:
        """Link related nuggets based on shared subjects/keywords."""
        for i, nugget1 in enumerate(nuggets):
            for nugget2 in nuggets[i + 1 :]:
                if self._are_related(nugget1, nugget2):
                    nugget1.related_nuggets.append(nugget2.nugget_id)
                    nugget2.related_nuggets.append(nugget1.nugget_id)

    def _are_related(self, nugget1: IdentifiedNugget, nugget2: IdentifiedNugget) -> bool:
        """Check if two nuggets are related."""
        # Related if same subject
        if nugget1.subject_predicate.subject.lower() == nugget2.subject_predicate.subject.lower():
            return True

        # Related if shared keywords
        keys1 = set(nugget1.subject_predicate.keywords)
        keys2 = set(nugget2.subject_predicate.keywords)
        if len(keys1 & keys2) > 0:
            return True

        return False

    def get_nugget(self, nugget_id: str) -> Optional[IdentifiedNugget]:
        """Get specific nugget."""
        return self.nuggets.get(nugget_id)

    def get_nuggets_by_subject(self, subject: str) -> List[IdentifiedNugget]:
        """Get all nuggets about a subject."""
        subject_lower = subject.lower()
        return [
            nugget
            for nugget in self.nugget_history
            if nugget.subject_predicate.subject.lower() == subject_lower
        ]

    def get_nuggets_by_type(self, nugget_type: NuggetType) -> List[IdentifiedNugget]:
        """Get all nuggets of a specific type."""
        return [
            nugget
            for nugget in self.nugget_history
            if nugget.subject_predicate.nugget_type == nugget_type
        ]

    def get_top_nuggets(self, top_n: int = 10) -> List[IdentifiedNugget]:
        """Get top N nuggets by importance."""
        sorted_nuggets = sorted(
            self.nugget_history, key=lambda n: n.importance_score, reverse=True
        )
        return sorted_nuggets[:top_n]

    def batch_identify(self, texts: List[str], context: str = "") -> Tuple[List[IdentifiedNugget], Optional[str]]:
        """Batch identify nuggets from multiple texts."""
        all_nuggets = []
        for text in texts:
            nuggets, error = self.identify_nuggets(text, context)
            all_nuggets.extend(nuggets)
        return all_nuggets, None

    def export_nugget(self, nugget_id: str) -> Optional[Dict[str, Any]]:
        """Export single nugget."""
        nugget = self.get_nugget(nugget_id)
        if not nugget:
            return None
        return nugget.to_dict()

    def export_all_nuggets(self) -> List[Dict[str, Any]]:
        """Export all nuggets."""
        return [nugget.to_dict() for nugget in self.nugget_history]

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about identified nuggets."""
        if not self.nugget_history:
            return {
                "total_nuggets": 0,
                "by_type": {},
                "avg_importance": 0.0,
                "avg_confidence": 0.0,
            }

        type_counts = {}
        for nugget in self.nugget_history:
            ntype = nugget.subject_predicate.nugget_type.value
            type_counts[ntype] = type_counts.get(ntype, 0) + 1

        avg_importance = (
            sum(n.importance_score for n in self.nugget_history) / len(self.nugget_history)
        )
        avg_confidence = (
            sum(n.subject_predicate.confidence for n in self.nugget_history)
            / len(self.nugget_history)
        )

        return {
            "total_nuggets": len(self.nugget_history),
            "by_type": type_counts,
            "avg_importance": avg_importance,
            "avg_confidence": avg_confidence,
            "unique_subjects": len(set(n.subject_predicate.subject for n in self.nugget_history)),
        }
