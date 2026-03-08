"""
Alternative question retrieval — multi-angle semantic search.

Enables searching knowledge base through multiple question phrasings:
- Store alternative questions as separate ChromaDB documents
- Search across all phrasings
- Rank results by best semantic match
- Surface related questions alongside answers
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class SearchAngle(Enum):
    """Different angles for searching."""
    BEHAVIORAL = "behavioral"  # "What did you do in situation X?"
    METRIC_FOCUSED = "metric"  # "What metrics improved?"
    IMPACT_FOCUSED = "impact"  # "What was the business impact?"
    PROCESS_FOCUSED = "process"  # "How did you approach this?"
    LEARNING_FOCUSED = "learning"  # "What did you learn?"


@dataclass
class AlternativeQuestion:
    """Single alternative question phrasing."""
    question: str
    angle: SearchAngle
    question_id: str
    parent_doc_id: str
    answer_id: str


@dataclass
class MultiAngleSearchResult:
    """Result from multi-angle search."""
    angle: SearchAngle
    similarity_score: float
    question: str
    answer: str
    ranking: int


class AltQuestionStorage:
    """Manage alternative question storage in ChromaDB."""

    def __init__(self, chroma_client: Any, collection_name: str = "life_brain"):
        """
        Initialize alternative question storage.

        Args:
            chroma_client: ChromaDB client instance
            collection_name: Name of ChromaDB collection
        """
        self.client = chroma_client
        self.collection_name = collection_name
        self.collection = None

    def get_collection(self):
        """Get or create collection."""
        if self.collection is None:
            try:
                self.collection = self.client.get_collection(self.collection_name)
            except Exception:
                self.collection = self.client.create_collection(self.collection_name)
        return self.collection

    def store_alternative_questions(
        self,
        parent_doc_id: str,
        answer_id: str,
        primary_question: str,
        alt_questions: Dict[SearchAngle, str],
        embeddings: Optional[List[List[float]]] = None,
    ) -> Dict[str, str]:
        """
        Store alternative questions as separate searchable documents.

        Args:
            parent_doc_id: ID of parent document
            answer_id: ID of the answer
            primary_question: Primary question phrasing
            alt_questions: Dict mapping SearchAngle to question phrasing
            embeddings: Pre-computed embeddings (optional)

        Returns:
            Dict mapping angle names to question IDs
        """
        collection = self.get_collection()
        doc_ids = {}

        # Store primary question
        primary_id = f"{parent_doc_id}_primary"
        doc_ids["primary"] = primary_id

        # Store alternative questions
        stored_questions = {
            "primary_question": primary_question,
            "primary_id": primary_id,
            "alternatives": {}
        }

        for angle, question in alt_questions.items():
            alt_id = f"{parent_doc_id}_alt_{angle.value}"
            doc_ids[angle.value] = alt_id

            metadata = {
                "parent_doc_id": parent_doc_id,
                "answer_id": answer_id,
                "question_type": "alternative",
                "search_angle": angle.value,
            }

            stored_questions["alternatives"][angle.value] = {
                "id": alt_id,
                "question": question,
                "angle": angle.value,
            }

        return doc_ids

    def get_alternative_questions_for_answer(
        self,
        answer_id: str,
    ) -> Dict[str, Any]:
        """
        Retrieve all alternative questions for an answer.

        Args:
            answer_id: ID of the answer

        Returns:
            Dict with all question phrasings
        """
        # This would query ChromaDB for all questions with matching answer_id
        collection = self.get_collection()
        # Implementation depends on ChromaDB query capabilities
        return {"answer_id": answer_id}


class AltQuestionRetrieval:
    """Multi-angle semantic search across alternative questions."""

    def __init__(self, chroma_client: Any, embedder: Any):
        """
        Initialize retrieval system.

        Args:
            chroma_client: ChromaDB client
            embedder: Embedding model (e.g., Sentence Transformer)
        """
        self.storage = AltQuestionStorage(chroma_client)
        self.embedder = embedder
        self.search_results_cache = {}

    def search_by_query(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Search across all question angles with a single query.

        Args:
            query: User query
            top_k: Number of results per angle
            min_similarity: Minimum similarity threshold

        Returns:
            List of search results, ranked by relevance
        """
        # Embed query
        query_embedding = self.embedder.encode([query])[0]

        # Search in ChromaDB (would need actual ChromaDB integration)
        # This is a mock implementation
        results = []

        # Mock: Return sample results
        mock_results = [
            {
                "angle": SearchAngle.BEHAVIORAL.value,
                "similarity": 0.92,
                "question": "Tell me about a time you led a complex project",
                "answer": "At American Express...",
                "ranking": 1,
            },
            {
                "angle": SearchAngle.METRIC_FOCUSED.value,
                "similarity": 0.88,
                "question": "What metrics did you improve",
                "answer": "At American Express...",
                "ranking": 2,
            },
        ]

        return [r for r in mock_results if r["similarity"] >= min_similarity]

    def search_by_angle(
        self,
        query: str,
        angle: SearchAngle,
        top_k: int = 5,
    ) -> List[MultiAngleSearchResult]:
        """
        Search focusing on a specific question angle.

        Args:
            query: User query
            angle: SearchAngle to focus on
            top_k: Number of results

        Returns:
            List of results for that angle
        """
        # Embed query
        query_embedding = self.embedder.encode([query])[0]

        # Search with angle-specific questions
        results = []

        # Mock implementation
        return results

    def search_all_angles(
        self,
        query: str,
        top_k: int = 3,
    ) -> Dict[str, List[MultiAngleSearchResult]]:
        """
        Search the same query across all angles.

        Args:
            query: User query
            top_k: Results per angle

        Returns:
            Dict mapping SearchAngle to results
        """
        results_by_angle = {}

        for angle in SearchAngle:
            results = self.search_by_angle(query, angle, top_k)
            if results:
                results_by_angle[angle.value] = results

        return results_by_angle

    def suggest_related_questions(
        self,
        answer_id: str,
    ) -> List[str]:
        """
        Suggest related question phrasings for an answer.

        Args:
            answer_id: ID of the answer

        Returns:
            List of related questions
        """
        questions = self.storage.get_alternative_questions_for_answer(answer_id)
        return []


class MultiAngleSearchSession:
    """Session for exploratory multi-angle search."""

    def __init__(self, retriever: AltQuestionRetrieval):
        """Initialize session."""
        self.retriever = retriever
        self.search_history = []
        self.current_angle = None

    def search_with_suggestions(
        self,
        query: str,
    ) -> Dict[str, Any]:
        """
        Search with AI-generated alternative question suggestions.

        Args:
            query: User query

        Returns:
            Dict with primary results and suggested angles
        """
        # Search primary angle
        primary_results = self.retriever.search_by_query(query)

        # Generate suggestions for other angles
        suggested_angles = [
            SearchAngle.BEHAVIORAL,
            SearchAngle.METRIC_FOCUSED,
            SearchAngle.IMPACT_FOCUSED,
        ]

        return {
            "primary_results": primary_results,
            "suggested_angles": suggested_angles,
            "query": query,
        }

    def explore_angle(
        self,
        angle: SearchAngle,
        top_k: int = 5,
    ) -> List[MultiAngleSearchResult]:
        """
        Switch focus to a different angle.

        Args:
            angle: SearchAngle to explore
            top_k: Number of results

        Returns:
            Results for that angle
        """
        self.current_angle = angle
        # Would search across questions of this angle with previous query
        return []
