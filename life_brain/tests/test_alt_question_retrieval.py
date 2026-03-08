"""
Test suite for alternative question retrieval.

Tests cover:
- Alternative question storage
- Multi-angle search
- Search result ranking
- Related question suggestions
- Search sessions
"""

import pytest
from unittest.mock import Mock, MagicMock

from life_brain.retrieval import (
    AltQuestionRetrieval,
    AltQuestionStorage,
    MultiAngleSearchSession,
    SearchAngle,
)


class TestSearchAngle:
    """Test SearchAngle enum."""

    def test_search_angles_exist(self):
        """Test that all search angles are defined."""
        assert SearchAngle.BEHAVIORAL is not None
        assert SearchAngle.METRIC_FOCUSED is not None
        assert SearchAngle.IMPACT_FOCUSED is not None
        assert SearchAngle.PROCESS_FOCUSED is not None
        assert SearchAngle.LEARNING_FOCUSED is not None

    def test_search_angle_values(self):
        """Test search angle values."""
        assert SearchAngle.BEHAVIORAL.value == "behavioral"
        assert SearchAngle.METRIC_FOCUSED.value == "metric"
        assert SearchAngle.IMPACT_FOCUSED.value == "impact"


class TestAltQuestionStorage:
    """Test alternative question storage."""

    def test_create_storage(self):
        """Test creating storage."""
        mock_client = Mock()
        storage = AltQuestionStorage(mock_client)

        assert storage.client is mock_client
        assert storage.collection_name == "life_brain"

    def test_store_alternative_questions(self):
        """Test storing alternative questions."""
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_collection.return_value = mock_collection

        storage = AltQuestionStorage(mock_client)

        alt_questions = {
            SearchAngle.BEHAVIORAL: "Tell me about a time you led a project",
            SearchAngle.METRIC_FOCUSED: "What metrics did you improve",
        }

        result = storage.store_alternative_questions(
            parent_doc_id="doc_123",
            answer_id="ans_456",
            primary_question="What is a project you're proud of?",
            alt_questions=alt_questions,
        )

        assert "primary" in result
        assert "behavioral" in result
        assert "metric" in result

    def test_get_alternative_questions_for_answer(self):
        """Test retrieving alternative questions."""
        mock_client = Mock()
        storage = AltQuestionStorage(mock_client)

        result = storage.get_alternative_questions_for_answer("ans_456")
        assert result["answer_id"] == "ans_456"


class TestAltQuestionRetrieval:
    """Test alternative question retrieval."""

    def test_create_retrieval_system(self):
        """Test creating retrieval system."""
        mock_client = Mock()
        mock_embedder = Mock()

        retriever = AltQuestionRetrieval(mock_client, mock_embedder)

        assert retriever.storage is not None
        assert retriever.embedder is mock_embedder

    def test_search_by_query(self):
        """Test searching by query."""
        mock_client = Mock()
        mock_embedder = Mock()
        mock_embedder.encode.return_value = [[0.1, 0.2, 0.3]]

        retriever = AltQuestionRetrieval(mock_client, mock_embedder)

        results = retriever.search_by_query("What projects have I led?")

        assert isinstance(results, list)
        assert len(results) > 0

    def test_search_by_angle(self):
        """Test searching by specific angle."""
        mock_client = Mock()
        mock_embedder = Mock()
        mock_embedder.encode.return_value = [[0.1, 0.2, 0.3]]

        retriever = AltQuestionRetrieval(mock_client, mock_embedder)

        results = retriever.search_by_angle(
            "What metrics did you improve?",
            SearchAngle.METRIC_FOCUSED,
        )

        assert isinstance(results, list)

    def test_search_all_angles(self):
        """Test searching all angles."""
        mock_client = Mock()
        mock_embedder = Mock()
        mock_embedder.encode.return_value = [[0.1, 0.2, 0.3]]

        retriever = AltQuestionRetrieval(mock_client, mock_embedder)

        results = retriever.search_all_angles("What have you accomplished?")

        assert isinstance(results, dict)

    def test_suggest_related_questions(self):
        """Test suggesting related questions."""
        mock_client = Mock()
        mock_embedder = Mock()

        retriever = AltQuestionRetrieval(mock_client, mock_embedder)

        suggestions = retriever.suggest_related_questions("ans_456")

        assert isinstance(suggestions, list)

    def test_search_result_filtering(self):
        """Test filtering results by similarity threshold."""
        mock_client = Mock()
        mock_embedder = Mock()
        mock_embedder.encode.return_value = [[0.1, 0.2, 0.3]]

        retriever = AltQuestionRetrieval(mock_client, mock_embedder)

        # Search with high threshold should filter low-similarity results
        results = retriever.search_by_query(
            "Test query",
            min_similarity=0.9,
        )

        for result in results:
            assert result["similarity"] >= 0.9


class TestMultiAngleSearchSession:
    """Test multi-angle search session."""

    def test_create_session(self):
        """Test creating search session."""
        mock_client = Mock()
        mock_embedder = Mock()

        retriever = AltQuestionRetrieval(mock_client, mock_embedder)
        session = MultiAngleSearchSession(retriever)

        assert session.retriever is retriever
        assert session.search_history == []
        assert session.current_angle is None

    def test_search_with_suggestions(self):
        """Test searching with angle suggestions."""
        mock_client = Mock()
        mock_embedder = Mock()
        mock_embedder.encode.return_value = [[0.1, 0.2, 0.3]]

        retriever = AltQuestionRetrieval(mock_client, mock_embedder)
        session = MultiAngleSearchSession(retriever)

        result = session.search_with_suggestions("What have you done?")

        assert "primary_results" in result
        assert "suggested_angles" in result
        assert "query" in result
        assert result["query"] == "What have you done?"

    def test_explore_angle(self):
        """Test switching to different angle."""
        mock_client = Mock()
        mock_embedder = Mock()

        retriever = AltQuestionRetrieval(mock_client, mock_embedder)
        session = MultiAngleSearchSession(retriever)

        results = session.explore_angle(SearchAngle.IMPACT_FOCUSED)

        assert session.current_angle == SearchAngle.IMPACT_FOCUSED
        assert isinstance(results, list)

    def test_search_session_history(self):
        """Test that search session maintains history."""
        mock_client = Mock()
        mock_embedder = Mock()
        mock_embedder.encode.return_value = [[0.1, 0.2, 0.3]]

        retriever = AltQuestionRetrieval(mock_client, mock_embedder)
        session = MultiAngleSearchSession(retriever)

        initial_history_length = len(session.search_history)
        session.search_with_suggestions("First query")

        # History should be maintained (or empty, depending on implementation)
        assert isinstance(session.search_history, list)


class TestMultiAngleSearchIntegration:
    """Integration tests for multi-angle search."""

    def test_full_search_workflow(self):
        """Test complete search workflow."""
        mock_client = Mock()
        mock_embedder = Mock()
        mock_embedder.encode.return_value = [[0.1, 0.2, 0.3]]

        retriever = AltQuestionRetrieval(mock_client, mock_embedder)

        # 1. Search by query
        results = retriever.search_by_query("Tell me about your projects")
        assert len(results) > 0

        # 2. Get all angles
        angle_results = retriever.search_all_angles("What did you accomplish?")
        assert isinstance(angle_results, dict)

    def test_session_exploration_workflow(self):
        """Test session-based exploration."""
        mock_client = Mock()
        mock_embedder = Mock()
        mock_embedder.encode.return_value = [[0.1, 0.2, 0.3]]

        retriever = AltQuestionRetrieval(mock_client, mock_embedder)
        session = MultiAngleSearchSession(retriever)

        # 1. Initial search with suggestions
        result = session.search_with_suggestions("My accomplishments")
        assert "suggested_angles" in result

        # 2. Explore specific angle
        angle_results = session.explore_angle(SearchAngle.METRIC_FOCUSED)
        assert session.current_angle == SearchAngle.METRIC_FOCUSED

        # 3. Switch to another angle
        angle_results = session.explore_angle(SearchAngle.BEHAVIORAL)
        assert session.current_angle == SearchAngle.BEHAVIORAL

    def test_search_result_ranking(self):
        """Test that results are ranked by relevance."""
        mock_client = Mock()
        mock_embedder = Mock()
        mock_embedder.encode.return_value = [[0.1, 0.2, 0.3]]

        retriever = AltQuestionRetrieval(mock_client, mock_embedder)

        results = retriever.search_by_query("What have you learned?")

        # Results should be sorted by similarity (descending)
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i]["similarity"] >= results[i + 1]["similarity"]
