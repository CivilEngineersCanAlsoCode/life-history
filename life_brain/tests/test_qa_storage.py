"""
Test suite for Q&A storage module.

Tests cover:
- Q&A pair creation and management
- Context metadata handling
- Indexing and retrieval
- Search functionality
- Batch operations
- Statistics and exports
"""

import pytest

from life_brain.storage.qa_storage import (
    QAStorage,
    QAPair,
    ContextMetadata,
    QASource,
    QACategory,
)


class TestContextMetadata:
    """Test ContextMetadata dataclass."""

    def test_create_metadata(self):
        """Test creating context metadata."""
        context = ContextMetadata(
            company="TechCorp",
            project="Project X",
            role="Engineer",
            date="2024-01-15",
        )

        assert context.company == "TechCorp"
        assert context.project == "Project X"


class TestQAPair:
    """Test QAPair dataclass."""

    def test_create_qa_pair(self):
        """Test creating Q&A pair."""
        context = ContextMetadata(company="Tech Inc")
        qa = QAPair(
            qa_id="qa_001",
            question="What is Python?",
            answer="Python is a programming language",
            context=context,
            source=QASource.DOCUMENTATION,
            category=QACategory.KNOWLEDGE,
        )

        assert qa.question == "What is Python?"
        assert qa.source == QASource.DOCUMENTATION

    def test_to_dict(self):
        """Test converting Q&A to dict."""
        context = ContextMetadata(company="ABC Corp", project="Project Y")
        qa = QAPair(
            qa_id="qa_002",
            question="How does it work?",
            answer="It works like this...",
            context=context,
            source=QASource.EXPERIENCE,
            category=QACategory.TECHNICAL,
            tags=["python", "backend"],
        )

        d = qa.to_dict()
        assert d["qa_id"] == "qa_002"
        assert d["source"] == "experience"


class TestQAStorage:
    """Test QAStorage functionality."""

    def test_create_storage(self):
        """Test creating Q&A storage."""
        storage = QAStorage()
        assert len(storage.qa_pairs) == 0

    def test_create_qa_pair(self):
        """Test creating Q&A pair."""
        storage = QAStorage()
        context = ContextMetadata(company="TechCorp", project="API")
        qa, error = storage.create_qa_pair(
            question="What is REST?",
            answer="REST is an architectural style",
            context=context,
            source=QASource.DOCUMENTATION,
            category=QACategory.KNOWLEDGE,
        )

        assert error is None
        assert qa is not None
        assert qa.question == "What is REST?"

    def test_create_qa_empty_question(self):
        """Test creating Q&A with empty question."""
        storage = QAStorage()
        context = ContextMetadata()
        qa, error = storage.create_qa_pair(
            question="",
            answer="An answer",
            context=context,
            source=QASource.RESEARCH,
            category=QACategory.KNOWLEDGE,
        )

        assert error is not None
        assert qa is None

    def test_create_qa_empty_answer(self):
        """Test creating Q&A with empty answer."""
        storage = QAStorage()
        context = ContextMetadata()
        qa, error = storage.create_qa_pair(
            question="A question",
            answer="",
            context=context,
            source=QASource.RESEARCH,
            category=QACategory.KNOWLEDGE,
        )

        assert error is not None
        assert qa is None

    def test_get_qa_pair(self):
        """Test retrieving Q&A pair."""
        storage = QAStorage()
        context = ContextMetadata(company="Tech")
        qa, _ = storage.create_qa_pair(
            "Q1", "A1", context, QASource.EXPERIENCE, QACategory.TECHNICAL
        )

        retrieved = storage.get_qa_pair(qa.qa_id)
        assert retrieved is not None
        assert retrieved.question == "Q1"

    def test_get_nonexistent_qa_pair(self):
        """Test retrieving nonexistent Q&A pair."""
        storage = QAStorage()
        qa = storage.get_qa_pair("nonexistent")
        assert qa is None

    def test_get_by_company(self):
        """Test retrieving Q&A pairs by company."""
        storage = QAStorage()
        context1 = ContextMetadata(company="CompanyA")
        context2 = ContextMetadata(company="CompanyB")

        storage.create_qa_pair(
            "Q1", "A1", context1, QASource.RESEARCH, QACategory.KNOWLEDGE
        )
        storage.create_qa_pair(
            "Q2", "A2", context2, QASource.RESEARCH, QACategory.KNOWLEDGE
        )

        company_a_qa = storage.get_by_company("CompanyA")
        assert len(company_a_qa) == 1

    def test_get_by_project(self):
        """Test retrieving Q&A pairs by project."""
        storage = QAStorage()
        context1 = ContextMetadata(project="ProjectX")
        context2 = ContextMetadata(project="ProjectY")

        storage.create_qa_pair(
            "Q1", "A1", context1, QASource.RESEARCH, QACategory.KNOWLEDGE
        )
        storage.create_qa_pair(
            "Q2", "A2", context2, QASource.RESEARCH, QACategory.KNOWLEDGE
        )

        project_x = storage.get_by_project("ProjectX")
        assert len(project_x) == 1

    def test_get_by_tag(self):
        """Test retrieving Q&A pairs by tag."""
        storage = QAStorage()
        context = ContextMetadata()

        storage.create_qa_pair(
            "Q1", "A1", context, QASource.RESEARCH, QACategory.KNOWLEDGE,
            tags=["python", "backend"]
        )
        storage.create_qa_pair(
            "Q2", "A2", context, QASource.RESEARCH, QACategory.KNOWLEDGE,
            tags=["python", "frontend"]
        )

        python_qa = storage.get_by_tag("python")
        assert len(python_qa) == 2

    def test_get_by_category(self):
        """Test retrieving Q&A pairs by category."""
        storage = QAStorage()
        context = ContextMetadata()

        storage.create_qa_pair(
            "Q1", "A1", context, QASource.RESEARCH, QACategory.TECHNICAL
        )
        storage.create_qa_pair(
            "Q2", "A2", context, QASource.RESEARCH, QACategory.BEHAVIORAL
        )

        technical = storage.get_by_category(QACategory.TECHNICAL)
        assert len(technical) == 1

    def test_get_by_source(self):
        """Test retrieving Q&A pairs by source."""
        storage = QAStorage()
        context = ContextMetadata()

        storage.create_qa_pair(
            "Q1", "A1", context, QASource.INTERVIEW, QACategory.KNOWLEDGE
        )
        storage.create_qa_pair(
            "Q2", "A2", context, QASource.RESEARCH, QACategory.KNOWLEDGE
        )

        interviews = storage.get_by_source(QASource.INTERVIEW)
        assert len(interviews) == 1

    def test_search_by_keyword(self):
        """Test searching Q&A by keyword."""
        storage = QAStorage()
        context = ContextMetadata()

        storage.create_qa_pair(
            "What is Python?", "Python is a language",
            context, QASource.RESEARCH, QACategory.KNOWLEDGE
        )
        storage.create_qa_pair(
            "What is Java?", "Java is also a language",
            context, QASource.RESEARCH, QACategory.KNOWLEDGE
        )

        results = storage.search_by_keyword("Python")
        assert len(results) == 1

    def test_search_by_context(self):
        """Test searching Q&A by context."""
        storage = QAStorage()
        context1 = ContextMetadata(company="TechCorp", project="API")
        context2 = ContextMetadata(company="TechCorp", project="Web")

        storage.create_qa_pair(
            "Q1", "A1", context1, QASource.RESEARCH, QACategory.KNOWLEDGE
        )
        storage.create_qa_pair(
            "Q2", "A2", context2, QASource.RESEARCH, QACategory.KNOWLEDGE
        )

        api_qa = storage.search_by_context(project="API")
        assert len(api_qa) == 1

    def test_update_qa_pair(self):
        """Test updating Q&A pair."""
        storage = QAStorage()
        context = ContextMetadata()
        qa, _ = storage.create_qa_pair(
            "Original Q", "Original A",
            context, QASource.RESEARCH, QACategory.KNOWLEDGE
        )

        updated, error = storage.update_qa_pair(
            qa.qa_id, question="Updated Q"
        )

        assert error is None
        assert updated.question == "Updated Q"
        assert updated.version == 2

    def test_update_nonexistent_qa_pair(self):
        """Test updating nonexistent Q&A pair."""
        storage = QAStorage()
        qa, error = storage.update_qa_pair("nonexistent", question="New")

        assert error is not None
        assert qa is None

    def test_batch_create(self):
        """Test batch creating Q&A pairs."""
        storage = QAStorage()
        data = [
            {
                "question": "Q1",
                "answer": "A1",
                "company": "Corp1",
                "category": "TECHNICAL",
                "source": "RESEARCH",
            },
            {
                "question": "Q2",
                "answer": "A2",
                "company": "Corp2",
                "category": "KNOWLEDGE",
                "source": "DOCUMENTATION",
            },
        ]

        created, error = storage.batch_create(data)

        assert error is None
        assert len(created) == 2

    def test_export_qa_pair(self):
        """Test exporting Q&A pair."""
        storage = QAStorage()
        context = ContextMetadata(company="Test")
        qa, _ = storage.create_qa_pair(
            "Q", "A", context, QASource.RESEARCH, QACategory.KNOWLEDGE
        )

        exported = storage.export_qa_pair(qa.qa_id)
        assert exported is not None
        assert exported["question"] == "Q"

    def test_export_nonexistent_qa_pair(self):
        """Test exporting nonexistent Q&A pair."""
        storage = QAStorage()
        exported = storage.export_qa_pair("nonexistent")
        assert exported is None

    def test_export_all_qa_pairs(self):
        """Test exporting all Q&A pairs."""
        storage = QAStorage()
        context = ContextMetadata()

        storage.create_qa_pair(
            "Q1", "A1", context, QASource.RESEARCH, QACategory.KNOWLEDGE
        )
        storage.create_qa_pair(
            "Q2", "A2", context, QASource.RESEARCH, QACategory.KNOWLEDGE
        )

        exported = storage.export_all_qa_pairs()
        assert len(exported) == 2

    def test_statistics_empty(self):
        """Test statistics with no Q&A pairs."""
        storage = QAStorage()
        stats = storage.get_statistics()

        assert stats["total_qa_pairs"] == 0

    def test_statistics_with_qa_pairs(self):
        """Test statistics with Q&A pairs."""
        storage = QAStorage()
        context1 = ContextMetadata(company="Corp1", project="P1")
        context2 = ContextMetadata(company="Corp1", project="P2")

        storage.create_qa_pair(
            "Q1", "A1", context1, QASource.RESEARCH, QACategory.TECHNICAL
        )
        storage.create_qa_pair(
            "Q2", "A2", context2, QASource.EXPERIENCE, QACategory.KNOWLEDGE
        )

        stats = storage.get_statistics()
        assert stats["total_qa_pairs"] == 2
        assert stats["unique_projects"] == 2

    def test_context_tree(self):
        """Test getting Q&A organized by context."""
        storage = QAStorage()
        context = ContextMetadata(company="Corp", project="Project1")

        storage.create_qa_pair(
            "Q1", "A1", context, QASource.RESEARCH, QACategory.KNOWLEDGE
        )

        tree = storage.get_qa_by_context_tree()
        assert "Corp" in tree
        assert "Project1" in tree["Corp"]

    def test_custom_qa_id(self):
        """Test creating Q&A with custom ID."""
        storage = QAStorage()
        context = ContextMetadata()
        qa, _ = storage.create_qa_pair(
            "Q", "A", context, QASource.RESEARCH, QACategory.KNOWLEDGE,
            qa_id="custom_123"
        )

        assert qa.qa_id == "custom_123"

    def test_multiple_storage_independent(self):
        """Test multiple storage instances are independent."""
        s1 = QAStorage()
        s2 = QAStorage()

        context = ContextMetadata()
        s1.create_qa_pair(
            "Q1", "A1", context, QASource.RESEARCH, QACategory.KNOWLEDGE
        )
        s2.create_qa_pair(
            "Q2", "A2", context, QASource.RESEARCH, QACategory.KNOWLEDGE
        )

        assert len(s1.qa_pairs) == 1
        assert len(s2.qa_pairs) == 1

    def test_qa_with_multiple_tags(self):
        """Test Q&A with multiple tags."""
        storage = QAStorage()
        context = ContextMetadata()

        qa, _ = storage.create_qa_pair(
            "Q", "A", context, QASource.RESEARCH, QACategory.TECHNICAL,
            tags=["python", "backend", "api", "rest"]
        )

        for tag in ["python", "backend", "api"]:
            results = storage.get_by_tag(tag)
            assert len(results) >= 1

    def test_keyword_search_case_insensitive(self):
        """Test keyword search is case-insensitive."""
        storage = QAStorage()
        context = ContextMetadata()

        storage.create_qa_pair(
            "What is Python?", "Python is great",
            context, QASource.RESEARCH, QACategory.KNOWLEDGE
        )

        results1 = storage.search_by_keyword("python")
        results2 = storage.search_by_keyword("PYTHON")

        assert len(results1) == len(results2)

    def test_context_search_multiple_criteria(self):
        """Test context search with multiple criteria."""
        storage = QAStorage()
        context = ContextMetadata(
            company="TechCorp",
            project="ProjectX",
            role="Engineer"
        )

        storage.create_qa_pair(
            "Q", "A", context, QASource.RESEARCH, QACategory.KNOWLEDGE
        )

        results = storage.search_by_context(
            company="TechCorp",
            project="ProjectX"
        )

        assert len(results) >= 1

    def test_qa_confidence_score(self):
        """Test Q&A confidence score."""
        storage = QAStorage()
        context = ContextMetadata()

        qa, _ = storage.create_qa_pair(
            "Q", "A", context, QASource.RESEARCH, QACategory.KNOWLEDGE,
        )

        assert 0.0 <= qa.confidence <= 1.0

    def test_complete_workflow(self):
        """Test complete Q&A storage workflow."""
        storage = QAStorage()

        # Create Q&A pairs
        context = ContextMetadata(company="TechCorp", project="API")
        qa1, _ = storage.create_qa_pair(
            "What is REST?", "REST is an architecture",
            context, QASource.DOCUMENTATION, QACategory.TECHNICAL,
            tags=["api", "architecture"]
        )

        # Retrieve by context
        api_qa = storage.get_by_project("API")
        assert len(api_qa) >= 1

        # Search by keyword
        results = storage.search_by_keyword("REST")
        assert len(results) >= 1

        # Get statistics
        stats = storage.get_statistics()
        assert stats["total_qa_pairs"] >= 1

        # Export
        exported = storage.export_qa_pair(qa1.qa_id)
        assert exported is not None
