"""
Test suite for alternative question storage.

Tests cover:
- Question storage and retrieval
- ChromaDB integration
- Batch operations
- Search functionality
- Statistics tracking
"""

import pytest
from unittest.mock import Mock, MagicMock

from life_brain.retrieval.alt_question_storage import (
    StoredQuestion,
    AltQuestionStorage,
)


class TestStoredQuestion:
    """Test StoredQuestion dataclass."""

    def test_create_question(self):
        """Test creating stored question."""
        q = StoredQuestion(
            question_id="q_001",
            question_text="What have you learned?",
            angle="learning",
            parent_doc_id="doc_001",
            answer_id="ans_001",
        )

        assert q.question_id == "q_001"
        assert q.angle == "learning"

    def test_to_chroma_format(self):
        """Test converting to ChromaDB format."""
        q = StoredQuestion(
            question_id="q_001",
            question_text="What have you learned?",
            angle="learning",
            parent_doc_id="doc_001",
            answer_id="ans_001",
            metadata={"custom": "value"},
        )

        q_id, q_text, q_metadata = q.to_chroma_format()

        assert q_id == "q_001"
        assert q_text == "What have you learned?"
        assert q_metadata["angle"] == "learning"
        assert q_metadata["custom"] == "value"


class TestAltQuestionStorage:
    """Test AltQuestionStorage."""

    def test_create_storage(self):
        """Test creating storage."""
        mock_client = Mock()
        mock_embedder = Mock()

        storage = AltQuestionStorage(mock_client, mock_embedder)

        assert storage.client is mock_client
        assert storage.embedder is mock_embedder

    def test_store_question(self):
        """Test storing a single question."""
        mock_client = Mock()
        mock_embedder = Mock()
        mock_embedder.encode.return_value = [[0.1, 0.2, 0.3]]

        storage = AltQuestionStorage(mock_client, mock_embedder)

        q = storage.store_question(
            question_text="What have you done?",
            angle="behavioral",
            parent_doc_id="doc_001",
            answer_id="ans_001",
        )

        assert q.question_text == "What have you done?"
        assert q.angle == "behavioral"
        assert q.parent_doc_id == "doc_001"

    def test_store_question_batch(self):
        """Test storing multiple questions."""
        mock_client = Mock()
        mock_embedder = Mock()
        mock_embedder.encode.return_value = [[0.1, 0.2, 0.3]]

        storage = AltQuestionStorage(mock_client, mock_embedder)

        questions_by_angle = {
            "behavioral": "What did you do?",
            "metric": "What metrics improved?",
            "impact": "What was the impact?",
        }

        stored = storage.store_question_batch(
            parent_doc_id="doc_001",
            answer_id="ans_001",
            questions_by_angle=questions_by_angle,
        )

        assert len(stored) == 3
        assert all(q.parent_doc_id == "doc_001" for q in stored)

    def test_retrieve_questions_for_answer(self):
        """Test retrieving questions for answer."""
        mock_client = Mock()
        mock_embedder = Mock()
        mock_embedder.encode.return_value = [[0.1, 0.2, 0.3]]

        storage = AltQuestionStorage(mock_client, mock_embedder)

        # Store questions for two answers
        storage.store_question("Q1", "angle1", "doc1", "ans_001")
        storage.store_question("Q2", "angle2", "doc1", "ans_001")
        storage.store_question("Q3", "angle1", "doc1", "ans_002")

        # Retrieve for ans_001
        questions = storage.retrieve_questions_for_answer("ans_001")
        assert len(questions) == 2

    def test_retrieve_questions_by_angle(self):
        """Test retrieving questions by angle."""
        mock_client = Mock()
        mock_embedder = Mock()
        mock_embedder.encode.return_value = [[0.1, 0.2, 0.3]]

        storage = AltQuestionStorage(mock_client, mock_embedder)

        storage.store_question("Q1", "behavioral", "doc1", "ans_001")
        storage.store_question("Q2", "behavioral", "doc1", "ans_002")
        storage.store_question("Q3", "metric", "doc1", "ans_001")

        behavioral = storage.retrieve_questions_by_angle("behavioral")
        assert len(behavioral) == 2

    def test_retrieve_questions_for_parent(self):
        """Test retrieving questions for parent document."""
        mock_client = Mock()
        mock_embedder = Mock()
        mock_embedder.encode.return_value = [[0.1, 0.2, 0.3]]

        storage = AltQuestionStorage(mock_client, mock_embedder)

        storage.store_question("Q1", "angle1", "doc_001", "ans_001")
        storage.store_question("Q2", "angle2", "doc_001", "ans_002")
        storage.store_question("Q3", "angle1", "doc_002", "ans_003")

        doc_001_questions = storage.retrieve_questions_for_parent("doc_001")
        assert len(doc_001_questions) == 2

    def test_delete_questions_for_answer(self):
        """Test deleting questions for answer."""
        mock_client = Mock()
        mock_embedder = Mock()
        mock_embedder.encode.return_value = [[0.1, 0.2, 0.3]]

        storage = AltQuestionStorage(mock_client, mock_embedder)

        storage.store_question("Q1", "angle1", "doc1", "ans_001")
        storage.store_question("Q2", "angle2", "doc1", "ans_001")
        storage.store_question("Q3", "angle1", "doc1", "ans_002")

        deleted = storage.delete_questions_for_answer("ans_001")
        assert deleted == 2

        remaining = storage.retrieve_questions_for_answer("ans_001")
        assert len(remaining) == 0

    def test_get_statistics_empty(self):
        """Test statistics on empty storage."""
        mock_client = Mock()
        mock_embedder = Mock()

        storage = AltQuestionStorage(mock_client, mock_embedder)
        stats = storage.get_statistics()

        assert stats["total_questions"] == 0
        assert stats["total_answers"] == 0

    def test_get_statistics_populated(self):
        """Test statistics on populated storage."""
        mock_client = Mock()
        mock_embedder = Mock()
        mock_embedder.encode.return_value = [[0.1, 0.2, 0.3]]

        storage = AltQuestionStorage(mock_client, mock_embedder)

        storage.store_question("Q1", "behavioral", "doc1", "ans_001")
        storage.store_question("Q2", "metric", "doc1", "ans_001")
        storage.store_question("Q3", "behavioral", "doc2", "ans_002")

        stats = storage.get_statistics()

        assert stats["total_questions"] == 3
        assert stats["total_answers"] == 2
        assert stats["total_documents"] == 2
        assert "behavioral" in stats["angles_used"]

    def test_export_questions(self):
        """Test exporting questions."""
        mock_client = Mock()
        mock_embedder = Mock()
        mock_embedder.encode.return_value = [[0.1, 0.2, 0.3]]

        storage = AltQuestionStorage(mock_client, mock_embedder)

        storage.store_question("Q1", "behavioral", "doc1", "ans_001")
        storage.store_question("Q2", "metric", "doc1", "ans_002")

        exported = storage.export_questions()

        assert len(exported) == 2
        assert all("question_id" in q for q in exported)
        assert all("angle" in q for q in exported)


class TestAltQuestionStorageIntegration:
    """Integration tests for question storage."""

    def test_full_storage_workflow(self):
        """Test complete storage workflow."""
        mock_client = Mock()
        mock_embedder = Mock()
        mock_embedder.encode.return_value = [[0.1, 0.2, 0.3]]

        storage = AltQuestionStorage(mock_client, mock_embedder)

        # Store questions
        questions_by_angle = {
            "behavioral": "What did you do?",
            "metric": "What metrics improved?",
            "impact": "What was the impact?",
        }

        stored = storage.store_question_batch(
            parent_doc_id="doc_001",
            answer_id="ans_001",
            questions_by_angle=questions_by_angle,
        )

        assert len(stored) == 3

        # Retrieve by answer
        retrieved = storage.retrieve_questions_for_answer("ans_001")
        assert len(retrieved) == 3

        # Get stats
        stats = storage.get_statistics()
        assert stats["total_questions"] == 3
        assert stats["total_answers"] == 1

    def test_multi_answer_storage(self):
        """Test storing questions for multiple answers."""
        mock_client = Mock()
        mock_embedder = Mock()
        mock_embedder.encode.return_value = [[0.1, 0.2, 0.3]]

        storage = AltQuestionStorage(mock_client, mock_embedder)

        # Store for answer 1
        storage.store_question_batch(
            parent_doc_id="doc_001",
            answer_id="ans_001",
            questions_by_angle={
                "behavioral": "Q1",
                "metric": "Q2",
            },
        )

        # Store for answer 2
        storage.store_question_batch(
            parent_doc_id="doc_001",
            answer_id="ans_002",
            questions_by_angle={
                "behavioral": "Q3",
                "impact": "Q4",
            },
        )

        stats = storage.get_statistics()
        assert stats["total_questions"] == 4
        assert stats["total_answers"] == 2

    def test_angle_coverage(self):
        """Test coverage of different angles."""
        mock_client = Mock()
        mock_embedder = Mock()
        mock_embedder.encode.return_value = [[0.1, 0.2, 0.3]]

        storage = AltQuestionStorage(mock_client, mock_embedder)

        angles = ["behavioral", "metric", "impact", "process", "learning"]
        for i, angle in enumerate(angles):
            storage.store_question(
                f"Question {i}",
                angle,
                "doc_001",
                f"ans_{i:03d}",
            )

        stats = storage.get_statistics()
        assert len(stats["angles_used"]) == 5
        assert set(stats["angles_used"]) == set(angles)
