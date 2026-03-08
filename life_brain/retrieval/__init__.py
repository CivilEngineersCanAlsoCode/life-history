"""
Retrieval module — semantic search and alternative question retrieval.

Provides:
- Multi-angle semantic search across alternative question phrasings
- Answer retrieval with related question suggestions
- Exploratory search sessions
"""

from life_brain.retrieval.alt_question_retrieval import (
    AltQuestionRetrieval,
    AltQuestionStorage,
    MultiAngleSearchSession,
    MultiAngleSearchResult,
    AlternativeQuestion,
    SearchAngle,
)

__all__ = [
    "AltQuestionRetrieval",
    "AltQuestionStorage",
    "MultiAngleSearchSession",
    "MultiAngleSearchResult",
    "AlternativeQuestion",
    "SearchAngle",
]
