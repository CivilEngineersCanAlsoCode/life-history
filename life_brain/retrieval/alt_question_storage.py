"""
Alternative question storage — persist question phrasings in ChromaDB.

Stores each alternative question as a separate document enabling:
- Direct search across all question angles
- Individual question relevance scoring
- Related question discovery
- Question clustering by topic
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class StoredQuestion:
    """A stored question document."""
    question_id: str
    question_text: str
    angle: str
    parent_doc_id: str
    answer_id: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = None
    stored_at: str = None

    def __post_init__(self):
        """Initialize defaults."""
        if self.metadata is None:
            self.metadata = {}
        if self.stored_at is None:
            self.stored_at = datetime.now().isoformat()

    def to_chroma_format(self) -> Tuple[str, str, Dict[str, Any]]:
        """Convert to ChromaDB storage format."""
        return (
            self.question_id,
            self.question_text,
            {
                "angle": self.angle,
                "parent_doc_id": self.parent_doc_id,
                "answer_id": self.answer_id,
                "question_type": "alternative",
                **self.metadata,
            }
        )


class AltQuestionStorage:
    """Store and manage alternative questions in ChromaDB."""

    def __init__(self, chroma_client: Any, embedder: Any, collection_name: str = "life_brain"):
        """
        Initialize storage.

        Args:
            chroma_client: ChromaDB client
            embedder: Embedding model
            collection_name: ChromaDB collection name
        """
        self.client = chroma_client
        self.embedder = embedder
        self.collection_name = collection_name
        self.collection = None
        self.stored_questions: Dict[str, StoredQuestion] = {}

    def get_collection(self):
        """Get or create ChromaDB collection."""
        if self.collection is None:
            try:
                self.collection = self.client.get_collection(self.collection_name)
            except Exception:
                self.collection = self.client.create_collection(self.collection_name)
        return self.collection

    def store_question(
        self,
        question_text: str,
        angle: str,
        parent_doc_id: str,
        answer_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StoredQuestion:
        """
        Store a single question.

        Args:
            question_text: Question phrasing
            angle: Search angle (behavioral, metric, etc.)
            parent_doc_id: Parent document ID
            answer_id: Associated answer ID
            metadata: Additional metadata

        Returns:
            StoredQuestion object
        """
        question_id = f"{parent_doc_id}_q_{angle}_{uuid.uuid4().hex[:8]}"

        # Generate embedding
        try:
            embedding = self.embedder.encode([question_text])[0]
        except Exception:
            embedding = None

        # Create stored question
        stored_q = StoredQuestion(
            question_id=question_id,
            question_text=question_text,
            angle=angle,
            parent_doc_id=parent_doc_id,
            answer_id=answer_id,
            embedding=embedding,
            metadata=metadata or {},
        )

        # Store locally
        self.stored_questions[question_id] = stored_q

        # Store in ChromaDB
        collection = self.get_collection()
        q_id, q_text, q_metadata = stored_q.to_chroma_format()

        try:
            if embedding:
                collection.add(
                    ids=[q_id],
                    documents=[q_text],
                    metadatas=[q_metadata],
                    embeddings=[embedding],
                )
            else:
                collection.add(
                    ids=[q_id],
                    documents=[q_text],
                    metadatas=[q_metadata],
                )
        except Exception:
            pass  # Silently fail if storage not available

        return stored_q

    def store_question_batch(
        self,
        parent_doc_id: str,
        answer_id: str,
        questions_by_angle: Dict[str, str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[StoredQuestion]:
        """
        Store multiple questions for an answer.

        Args:
            parent_doc_id: Parent document ID
            answer_id: Answer ID
            questions_by_angle: Dict mapping angle → question text
            metadata: Additional metadata

        Returns:
            List of StoredQuestion objects
        """
        stored_questions = []

        for angle, question_text in questions_by_angle.items():
            stored_q = self.store_question(
                question_text=question_text,
                angle=angle,
                parent_doc_id=parent_doc_id,
                answer_id=answer_id,
                metadata=metadata,
            )
            stored_questions.append(stored_q)

        return stored_questions

    def retrieve_questions_for_answer(
        self,
        answer_id: str,
    ) -> List[StoredQuestion]:
        """
        Retrieve all questions for an answer.

        Args:
            answer_id: Answer ID

        Returns:
            List of StoredQuestion objects
        """
        matching = []
        for q in self.stored_questions.values():
            if q.answer_id == answer_id:
                matching.append(q)
        return matching

    def retrieve_questions_by_angle(
        self,
        angle: str,
    ) -> List[StoredQuestion]:
        """
        Retrieve all questions for an angle.

        Args:
            angle: Search angle

        Returns:
            List of StoredQuestion objects
        """
        matching = []
        for q in self.stored_questions.values():
            if q.angle == angle:
                matching.append(q)
        return matching

    def retrieve_questions_for_parent(
        self,
        parent_doc_id: str,
    ) -> List[StoredQuestion]:
        """
        Retrieve all questions for a parent document.

        Args:
            parent_doc_id: Parent document ID

        Returns:
            List of StoredQuestion objects
        """
        matching = []
        for q in self.stored_questions.values():
            if q.parent_doc_id == parent_doc_id:
                matching.append(q)
        return matching

    def search_questions(
        self,
        query: str,
        top_k: int = 5,
        angle_filter: Optional[str] = None,
    ) -> List[Tuple[StoredQuestion, float]]:
        """
        Search questions by semantic similarity.

        Args:
            query: Search query
            top_k: Number of results
            angle_filter: Optional angle to filter by

        Returns:
            List of (StoredQuestion, similarity) tuples
        """
        # Would normally query ChromaDB
        # For now, return empty (would be implemented with actual search)
        return []

    def delete_questions_for_answer(
        self,
        answer_id: str,
    ) -> int:
        """
        Delete all questions for an answer.

        Args:
            answer_id: Answer ID

        Returns:
            Number of questions deleted
        """
        to_delete = []
        for q_id, q in self.stored_questions.items():
            if q.answer_id == answer_id:
                to_delete.append(q_id)

        for q_id in to_delete:
            del self.stored_questions[q_id]

        return len(to_delete)

    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics."""
        if not self.stored_questions:
            return {
                "total_questions": 0,
                "total_answers": 0,
                "total_documents": 0,
                "angles_used": [],
            }

        # Calculate stats
        answers = set(q.answer_id for q in self.stored_questions.values())
        docs = set(q.parent_doc_id for q in self.stored_questions.values())
        angles = set(q.angle for q in self.stored_questions.values())

        return {
            "total_questions": len(self.stored_questions),
            "total_answers": len(answers),
            "total_documents": len(docs),
            "angles_used": list(angles),
            "avg_questions_per_answer": len(self.stored_questions) / max(len(answers), 1),
        }

    def export_questions(self) -> List[Dict[str, Any]]:
        """Export all stored questions."""
        return [
            {
                "question_id": q.question_id,
                "question": q.question_text,
                "angle": q.angle,
                "parent_doc_id": q.parent_doc_id,
                "answer_id": q.answer_id,
                "stored_at": q.stored_at,
                "metadata": q.metadata,
            }
            for q in self.stored_questions.values()
        ]
