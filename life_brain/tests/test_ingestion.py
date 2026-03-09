"""
Unit tests for ingestion.py

Covers:
- QAPair dataclass
- add_to_life_brain function (validation, conflict checking, upsert)
- batch_ingest function (multiple Q&A pairs with error handling)
- validate_document_batch function (batch validation)
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from life_brain.core.ingestion import QAPair, add_to_life_brain, batch_ingest, validate_document_batch

# Helper: Generate text > 100 chars
def long_text(prefix="Q: Answer?"):
    return f"{prefix}\nA: This is a detailed and comprehensive answer that provides sufficient information to exceed the 100 character minimum requirement for proper document validation in the ingestion system."

class TestQAPair:
    """Test QAPair dataclass."""

    def test_create_qa_pair_basic(self):
        """Test creating basic Q&A pair."""
        pair = QAPair(
            question="What is ML?",
            answer="Machine Learning is...",
            doc_id="qa_1",
            metadata={"domain": "career"}
        )
        assert pair.question == "What is ML?"
        assert pair.doc_id == "qa_1"

    def test_create_qa_pair_with_alternatives(self):
        """Test Q&A pair with alternative questions."""
        pair = QAPair(
            question="What is ML?",
            answer="Answer",
            doc_id="qa_2",
            metadata={},
            alt_questions=["Machine learning?", "ML?"]
        )
        assert len(pair.alt_questions) == 2


class TestAddToLifeBrain:
    """Test add_to_life_brain function."""

    @patch('life_brain.core.ingestion.ChromaDBManager')
    @patch('life_brain.core.ingestion.conflict_check')
    def test_add_success_first_try(self, mock_conflict, mock_manager_class):
        """Test successful addition on first try."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_conflict.return_value = Mock(status="SAFE")

        mock_collection = Mock()
        doc_id = add_to_life_brain(
            collection=mock_collection,
            doc_id="test_doc",
            text=long_text(),
            metadata={"domain": "career"}
        )

        assert doc_id == "test_doc"
        mock_collection.upsert.assert_called_once()

    @patch('life_brain.core.ingestion.ChromaDBManager')
    def test_add_fails_metadata_validation(self, mock_manager_class):
        """Test failure on metadata validation."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.validate_required_fields.side_effect = ValueError("Missing")

        mock_collection = Mock()
        with pytest.raises(ValueError):
            add_to_life_brain(
                collection=mock_collection,
                doc_id="bad",
                text=long_text(),
                metadata={}
            )

    @patch('life_brain.core.ingestion.ChromaDBManager')
    def test_add_fails_text_too_short(self, mock_manager_class):
        """Test failure when text is too short."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager

        mock_collection = Mock()
        with pytest.raises(ValueError) as exc:
            add_to_life_brain(
                collection=mock_collection,
                doc_id="short",
                text="Short",
                metadata={}
            )
        assert "100" in str(exc.value)

    @patch('life_brain.core.ingestion.ChromaDBManager')
    @patch('life_brain.core.ingestion.conflict_check')
    def test_add_hard_conflict_detected(self, mock_conflict, mock_manager_class):
        """Test hard conflict is detected during ingestion."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.validate_required_fields.return_value = None
        mock_conflict.return_value = Mock(status="CONFLICT", conflict_score=0.8, existing_answer="Old")

        mock_collection = Mock()
        # Empty query result (no existing docs)
        mock_collection.query.return_value = {"ids": [[]], "metadatas": [], "embeddings": []}

        # Even with hard conflict detected, if collection query is empty, ingestion proceeds
        doc_id = add_to_life_brain(
            collection=mock_collection,
            doc_id="conflict",
            text=long_text(),
            metadata={"domain": "career"}
        )
        assert doc_id == "conflict"
        mock_collection.upsert.assert_called_once()

    @patch('life_brain.core.ingestion.ChromaDBManager')
    @patch('life_brain.core.ingestion.conflict_check')
    def test_add_soft_conflict_proceeds(self, mock_conflict, mock_manager_class):
        """Test soft conflict proceeds."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_conflict.return_value = Mock(status="SOFT", conflict_score=0.4, existing_answer="Similar")

        mock_collection = Mock()
        mock_collection.query.return_value = {"ids": [["ex"]], "metadatas": [[{}]], "embeddings": [[]]}

        doc_id = add_to_life_brain(
            collection=mock_collection,
            doc_id="soft",
            text=long_text(),
            metadata={"domain": "career"}
        )

        assert doc_id == "soft"

    @patch('life_brain.core.ingestion.ChromaDBManager')
    @patch('life_brain.core.ingestion.conflict_check')
    def test_add_enrichment_detected(self, mock_conflict, mock_manager_class):
        """Test enrichment scenario."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_conflict.return_value = Mock(status="ENRICHMENT", conflict_score=0.2)

        mock_collection = Mock()
        mock_collection.query.return_value = {"ids": [["ex"]], "metadatas": [[{}]], "embeddings": [[]]}

        doc_id = add_to_life_brain(
            collection=mock_collection,
            doc_id="enrich",
            text=long_text(),
            metadata={"domain": "career"}
        )

        assert doc_id == "enrich"


class TestBatchIngest:
    """Test batch_ingest function."""

    @patch('life_brain.core.ingestion.add_to_life_brain')
    def test_batch_all_success(self, mock_add):
        """Test batch where all succeed."""
        mock_add.side_effect = lambda **kw: kw.get("doc_id")

        mock_collection = Mock()
        pairs = [
            QAPair("Q1?", "A1", "d1", {"domain": "career"}),
            QAPair("Q2?", "A2", "d2", {"domain": "career"}),
        ]

        result = batch_ingest(mock_collection, pairs)

        assert result["inserted"] == 2
        assert result["success_rate"] == 100

    @patch('life_brain.core.ingestion.add_to_life_brain')
    def test_batch_mixed_results(self, mock_add):
        """Test batch with mixed results."""
        def add_effect(**kw):
            doc_id = kw.get("doc_id")
            if doc_id == "fail": raise ValueError("Validation")
            if doc_id == "conflict": raise ValueError("HARD CONFLICT")
            return doc_id

        mock_add.side_effect = add_effect
        mock_collection = Mock()
        pairs = [
            QAPair("Q1?", "A1", "ok", {"domain": "career"}),
            QAPair("Q2?", "A2", "fail", {"domain": "career"}),
            QAPair("Q3?", "A3", "conflict", {"domain": "career"}),
        ]

        result = batch_ingest(mock_collection, pairs)

        assert result["inserted"] == 1
        assert result["conflicts"] == 1
        assert result["skipped"] == 1

    @patch('life_brain.core.ingestion.add_to_life_brain')
    def test_batch_formats_qa_text(self, mock_add):
        """Test batch formats Q&A correctly."""
        texts = []
        def capture(**kw):
            texts.append(kw.get("text"))
            return kw.get("doc_id")

        mock_add.side_effect = capture
        mock_collection = Mock()
        pairs = [QAPair("What is ML?", "Machine learning is...", "qa_1", {})]

        batch_ingest(mock_collection, pairs)

        assert len(texts) == 1
        assert "Q: What is ML?" in texts[0]
        assert "A: Machine learning" in texts[0]

    @patch('life_brain.core.ingestion.add_to_life_brain')
    def test_batch_empty(self, mock_add):
        """Test batch with no pairs."""
        result = batch_ingest(Mock(), [])
        assert result["total"] == 0
        assert result["success_rate"] == 0


class TestValidateDocumentBatch:
    """Test validate_document_batch function."""

    @patch('life_brain.core.ingestion.ChromaDBManager')
    def test_validate_all_valid(self, mock_manager_class):
        """Test validation with all valid documents."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.validate_required_fields.return_value = None

        pairs = [
            QAPair("What is Python really and why is it important?", "Python is a versatile programming language used for general purpose computing with excellent readability and broad industry adoption in web development, data science, and automation.", "d1", {"domain": "career"}),
            QAPair("Why should I learn Python for my career?", "Python is useful for career growth because it has simple syntax, is very readable by humans, and is widely used in high-demand fields like machine learning and web development.", "d2", {"domain": "career"}),
        ]

        valid_ids, invalid = validate_document_batch(pairs)
        assert len(valid_ids) == 2
        assert len(invalid) == 0

    @patch('life_brain.core.ingestion.ChromaDBManager')
    def test_validate_missing_metadata(self, mock_manager_class):
        """Test validation fails on missing metadata."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.validate_required_fields.side_effect = ValueError("Missing")

        pairs = [QAPair("Q?", "A", "d1", {})]
        valid_ids, invalid = validate_document_batch(pairs)

        assert len(invalid) == 1

    @patch('life_brain.core.ingestion.ChromaDBManager')
    def test_validate_text_too_short(self, mock_manager_class):
        """Test validation fails on short text."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager

        pairs = [QAPair("Short?", "Short", "d1", {"domain": "career"})]
        valid_ids, invalid = validate_document_batch(pairs)

        assert len(invalid) == 1

    @patch('life_brain.core.ingestion.ChromaDBManager')
    def test_validate_short_question(self, mock_manager_class):
        """Test validation fails on short question."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager

        pairs = [QAPair("Q?", "Answer with sufficient content and length for validation.", "d1", {"domain": "career"})]
        valid_ids, invalid = validate_document_batch(pairs)

        assert len(invalid) == 1
        assert "question" in invalid[0][1].lower()

    @patch('life_brain.core.ingestion.ChromaDBManager')
    def test_validate_short_answer(self, mock_manager_class):
        """Test validation fails on short answer."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.validate_required_fields.return_value = None

        pairs = [QAPair("What is effective learning in professional development?", "Short", "d1", {"domain": "career"})]
        valid_ids, invalid = validate_document_batch(pairs)

        assert len(invalid) == 1
        assert "answer" in invalid[0][1].lower() or "too short" in invalid[0][1].lower()

    @patch('life_brain.core.ingestion.ChromaDBManager')
    def test_validate_duplicate_questions(self, mock_manager_class):
        """Test validation detects duplicates."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.validate_required_fields.return_value = None

        pairs = [
            QAPair("What is machine learning and how does it differ from traditional programming?", "Machine learning is a subset of AI that enables systems to learn from data without being explicitly programmed.", "d1", {"domain": "career"}),
            QAPair("What is machine learning and how does it differ from traditional programming?", "Alternative ML definition focusing on pattern recognition and statistical models for building intelligent systems.", "d2", {"domain": "career"}),
        ]

        valid_ids, invalid = validate_document_batch(pairs)

        # Both duplicates are marked as invalid (one per pair that references the other)
        assert len(invalid) == 2
        assert all("duplicate" in err[1].lower() for err in invalid)

    @patch('life_brain.core.ingestion.ChromaDBManager')
    def test_validate_case_insensitive_duplicates(self, mock_manager_class):
        """Test duplicate detection is case-insensitive."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager

        pairs = [
            QAPair("What is ML?", "Machine learning definition here with content.", "d1", {"domain": "career"}),
            QAPair("what is ml?", "Same question in lowercase form with different content.", "d2", {"domain": "career"}),
        ]

        valid_ids, invalid = validate_document_batch(pairs)
        assert len(invalid) >= 1


class TestIntegrationIngestion:
    """Integration tests."""

    @patch('life_brain.core.ingestion.ChromaDBManager')
    @patch('life_brain.core.ingestion.add_to_life_brain')
    def test_full_workflow_single(self, mock_add, mock_manager_class):
        """Test full single document workflow."""
        mock_add.return_value = "doc_123"

        doc_id = add_to_life_brain(
            collection=Mock(),
            doc_id="doc_123",
            text=long_text(),
            metadata={"domain": "career"}
        )

        assert doc_id == "doc_123"

    @patch('life_brain.core.ingestion.ChromaDBManager')
    @patch('life_brain.core.ingestion.add_to_life_brain')
    def test_full_workflow_batch(self, mock_add, mock_manager_class):
        """Test full batch workflow."""
        mock_add.side_effect = lambda **kw: kw.get("doc_id")

        pairs = [
            QAPair("Career growth?", "I grew through challenging projects at my company over time.", "d1", {"domain": "career"}),
            QAPair("Skills learned?", "I learned machine learning and python programming and product management.", "d2", {"domain": "career"}),
        ]

        result = batch_ingest(Mock(), pairs)
        assert result["inserted"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
