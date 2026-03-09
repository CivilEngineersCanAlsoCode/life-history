"""
Tests for alternative question phrasing storage.

Tests cover:
- Adding phrasings linked to parent
- Retrieving phrasings by parent
- Parent ID lookup from alt doc
- Stable ID generation
- Deduplication
- Removal
- Statistics
- ChromaDB export format
"""

import pytest
from unittest.mock import Mock

from life_brain.core.alt_question_store import (
    AltQuestionStore,
    AltQuestionDocument,
    generate_alt_question_id,
)


class TestGenerateAltQuestionId:
    """Test ID generation."""

    def test_id_starts_with_alt(self):
        doc_id = generate_alt_question_id("parent1", "What did you do?")
        assert doc_id.startswith("alt_")

    def test_id_contains_parent_id(self):
        doc_id = generate_alt_question_id("parent1", "What did you do?")
        assert "parent1" in doc_id

    def test_same_inputs_same_id(self):
        id1 = generate_alt_question_id("p1", "How did the project go?")
        id2 = generate_alt_question_id("p1", "How did the project go?")
        assert id1 == id2

    def test_different_phrasings_different_ids(self):
        id1 = generate_alt_question_id("p1", "How did the project go?")
        id2 = generate_alt_question_id("p1", "What happened with the project?")
        assert id1 != id2

    def test_different_parents_different_ids(self):
        id1 = generate_alt_question_id("p1", "What did you do?")
        id2 = generate_alt_question_id("p2", "What did you do?")
        assert id1 != id2


class TestAltQuestionDocument:
    """Test AltQuestionDocument dataclass."""

    def test_to_chromadb_dict(self):
        doc = AltQuestionDocument(
            doc_id="alt_p1_abc123",
            parent_id="parent_qa_001",
            phrasing="What was your role?",
            metadata={"company": "Google", "domain": "career"},
        )

        d = doc.to_chromadb_dict()
        assert d["id"] == "alt_p1_abc123"
        assert d["document"] == "What was your role?"
        assert d["metadata"]["parent_id"] == "parent_qa_001"
        assert d["metadata"]["doc_type"] == "alt_question"
        assert d["metadata"]["company"] == "Google"

    def test_to_chromadb_dict_preserves_metadata(self):
        doc = AltQuestionDocument(
            doc_id="alt_1",
            parent_id="p1",
            phrasing="phrasing",
            metadata={"key": "value"},
        )
        d = doc.to_chromadb_dict()
        assert d["metadata"]["key"] == "value"


class TestAltQuestionStore:
    """Test AltQuestionStore."""

    def test_add_phrasings_returns_documents(self):
        store = AltQuestionStore()
        docs = store.add_phrasings(
            "parent_001",
            ["How did you handle it?", "What was your approach?"],
        )
        assert len(docs) == 2

    def test_added_docs_have_parent_id(self):
        store = AltQuestionStore()
        docs = store.add_phrasings("p1", ["How so?", "Why?"])
        assert all(d.parent_id == "p1" for d in docs)

    def test_added_docs_have_phrasings(self):
        store = AltQuestionStore()
        docs = store.add_phrasings("p1", ["How so?"])
        assert docs[0].phrasing == "How so?"

    def test_metadata_attached_to_docs(self):
        store = AltQuestionStore()
        docs = store.add_phrasings(
            "p1",
            ["Phrasing?"],
            base_metadata={"company": "Google", "domain": "career"},
        )
        assert docs[0].metadata["company"] == "Google"
        assert docs[0].metadata["domain"] == "career"

    def test_empty_parent_id_raises(self):
        store = AltQuestionStore()
        with pytest.raises(ValueError):
            store.add_phrasings("", ["Phrasing?"])

    def test_empty_phrasings_skipped(self):
        store = AltQuestionStore()
        docs = store.add_phrasings("p1", ["Valid?", "", "  ", "Also valid?"])
        assert len(docs) == 2

    def test_get_phrasings_for_parent(self):
        store = AltQuestionStore()
        store.add_phrasings("p1", ["Phrasing A?", "Phrasing B?"])

        retrieved = store.get_phrasings_for_parent("p1")
        assert len(retrieved) == 2

    def test_get_phrasings_unknown_parent(self):
        store = AltQuestionStore()
        retrieved = store.get_phrasings_for_parent("nonexistent")
        assert retrieved == []

    def test_phrasings_isolated_per_parent(self):
        store = AltQuestionStore()
        store.add_phrasings("p1", ["P1 question?"])
        store.add_phrasings("p2", ["P2 question A?", "P2 question B?"])

        p1_docs = store.get_phrasings_for_parent("p1")
        p2_docs = store.get_phrasings_for_parent("p2")

        assert len(p1_docs) == 1
        assert len(p2_docs) == 2

    def test_get_parent_id(self):
        store = AltQuestionStore()
        docs = store.add_phrasings("parent_xyz", ["Alt phrasing?"])
        alt_doc_id = docs[0].doc_id

        retrieved_parent = store.get_parent_id(alt_doc_id)
        assert retrieved_parent == "parent_xyz"

    def test_get_parent_id_unknown(self):
        store = AltQuestionStore()
        result = store.get_parent_id("nonexistent_id")
        assert result is None

    def test_remove_phrasings_for_parent(self):
        store = AltQuestionStore()
        store.add_phrasings("p1", ["A?", "B?", "C?"])
        removed = store.remove_phrasings_for_parent("p1")

        assert removed == 3
        assert store.get_phrasings_for_parent("p1") == []

    def test_remove_nonexistent_parent(self):
        store = AltQuestionStore()
        removed = store.remove_phrasings_for_parent("does_not_exist")
        assert removed == 0

    def test_statistics_empty(self):
        store = AltQuestionStore()
        stats = store.get_statistics()
        assert stats["total_alt_docs"] == 0
        assert stats["total_parents"] == 0

    def test_statistics_with_data(self):
        store = AltQuestionStore()
        store.add_phrasings("p1", ["A?", "B?"])
        store.add_phrasings("p2", ["C?"])

        stats = store.get_statistics()
        assert stats["total_alt_docs"] == 3
        assert stats["total_parents"] == 2
        assert stats["avg_phrasings_per_parent"] == 1.5

    def test_export_for_parent(self):
        store = AltQuestionStore()
        store.add_phrasings("p1", ["How?", "Why?"])

        exported = store.export_for_parent("p1")
        assert len(exported) == 2
        assert all("id" in d for d in exported)
        assert all("document" in d for d in exported)
        assert all("metadata" in d for d in exported)
        assert all(d["metadata"]["parent_id"] == "p1" for d in exported)

    def test_chromadb_collection_called(self):
        mock_collection = Mock()
        store = AltQuestionStore(collection=mock_collection)
        store.add_phrasings("p1", ["Phrasing?"])

        mock_collection.upsert.assert_called_once()

    def test_deduplication_via_stable_ids(self):
        """Same phrasing for same parent should produce same doc_id."""
        store = AltQuestionStore()
        docs1 = store.add_phrasings("p1", ["Same phrasing?"])
        docs2 = store.add_phrasings("p1", ["Same phrasing?"])

        # Both added but same ID — only 1 unique doc
        all_docs = store.get_phrasings_for_parent("p1")
        assert len(all_docs) == 1  # Deduped by ID in index
