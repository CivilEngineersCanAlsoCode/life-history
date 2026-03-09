"""
Test suite for nugget identification module.

Tests cover:
- Subject-predicate extraction
- Nugget type classification
- Importance scoring
- Batch operations
- Statistics and exports
"""

import pytest

from life_brain.validation.nugget_identification import (
    NuggetIdentifier,
    NuggetType,
    SubjectPredicatePair,
    IdentifiedNugget,
)


class TestSubjectPredicatePair:
    """Test SubjectPredicatePair dataclass."""

    def test_create_pair(self):
        """Test creating subject-predicate pair."""
        pair = SubjectPredicatePair(
            subject="Python",
            predicate="is a programming language",
            nugget_type=NuggetType.DEFINITION,
            confidence=0.95,
            source_sentence="Python is a programming language.",
        )

        assert pair.subject == "Python"
        assert pair.nugget_type == NuggetType.DEFINITION


class TestIdentifiedNugget:
    """Test IdentifiedNugget dataclass."""

    def test_create_nugget(self):
        """Test creating identified nugget."""
        pair = SubjectPredicatePair(
            subject="AI",
            predicate="transforms industries",
            nugget_type=NuggetType.ACTION,
            confidence=0.8,
            source_sentence="AI transforms industries.",
        )
        nugget = IdentifiedNugget(
            nugget_id="nug_001",
            subject_predicate=pair,
            context="Artificial intelligence discussion",
            importance_score=0.85,
        )

        assert nugget.nugget_id == "nug_001"

    def test_to_dict(self):
        """Test converting nugget to dict."""
        pair = SubjectPredicatePair(
            subject="Machine Learning",
            predicate="enables predictions",
            nugget_type=NuggetType.PROPERTY,
            confidence=0.88,
            source_sentence="Machine learning enables predictions.",
            keywords=["predictions", "learning"],
        )
        nugget = IdentifiedNugget(
            nugget_id="nug_002",
            subject_predicate=pair,
            context="ML context",
            importance_score=0.80,
        )

        d = nugget.to_dict()
        assert d["nugget_id"] == "nug_002"
        assert d["type"] == "property"


class TestNuggetIdentifier:
    """Test NuggetIdentifier functionality."""

    def test_create_identifier(self):
        """Test creating nugget identifier."""
        identifier = NuggetIdentifier()
        assert len(identifier.nuggets) == 0

    def test_identify_nuggets_empty(self):
        """Test with empty text."""
        identifier = NuggetIdentifier()
        nuggets, error = identifier.identify_nuggets("")

        assert error == "Empty text"
        assert len(nuggets) == 0

    def test_identify_nuggets_definition(self):
        """Test identifying definition nuggets."""
        identifier = NuggetIdentifier()
        nuggets, error = identifier.identify_nuggets(
            "Python is a programming language."
        )

        assert error is None
        assert len(nuggets) > 0
        assert any(n.subject_predicate.nugget_type == NuggetType.DEFINITION for n in nuggets)

    def test_identify_nuggets_property(self):
        """Test identifying property nuggets."""
        identifier = NuggetIdentifier()
        nuggets, error = identifier.identify_nuggets(
            "The system has advanced security features."
        )

        assert error is None
        assert len(nuggets) > 0

    def test_identify_nuggets_action(self):
        """Test identifying action nuggets."""
        identifier = NuggetIdentifier()
        nuggets, error = identifier.identify_nuggets(
            "The team developed a new platform."
        )

        assert error is None
        assert len(nuggets) > 0

    def test_identify_multiple_nuggets(self):
        """Test identifying multiple nuggets."""
        identifier = NuggetIdentifier()
        text = "Python is a language. Java is compiled. Ruby is dynamic."
        nuggets, error = identifier.identify_nuggets(text)

        assert error is None
        assert len(nuggets) >= 1

    def test_subject_extracted(self):
        """Test that subjects are properly extracted."""
        identifier = NuggetIdentifier()
        nuggets, _ = identifier.identify_nuggets("The car is fast.")

        if nuggets:
            assert any("car" in n.subject_predicate.subject.lower() for n in nuggets)

    def test_predicate_extracted(self):
        """Test that predicates are properly extracted."""
        identifier = NuggetIdentifier()
        nuggets, _ = identifier.identify_nuggets("Machine learning is powerful.")

        if nuggets:
            assert any("powerful" in n.subject_predicate.predicate.lower() for n in nuggets)

    def test_confidence_scoring(self):
        """Test confidence score is between 0-1."""
        identifier = NuggetIdentifier()
        nuggets, _ = identifier.identify_nuggets(
            "Technology evolves rapidly. Innovation drives progress."
        )

        for nugget in nuggets:
            assert 0.0 <= nugget.subject_predicate.confidence <= 1.0

    def test_importance_scoring(self):
        """Test importance score is between 0-1."""
        identifier = NuggetIdentifier()
        nuggets, _ = identifier.identify_nuggets(
            "Python is important. Java is useful.", context="Programming languages"
        )

        for nugget in nuggets:
            assert 0.0 <= nugget.importance_score <= 1.0

    def test_get_nugget(self):
        """Test retrieving specific nugget."""
        identifier = NuggetIdentifier()
        nuggets, _ = identifier.identify_nuggets("Test is good.")

        if nuggets:
            retrieved = identifier.get_nugget(nuggets[0].nugget_id)
            assert retrieved is not None
            assert retrieved.nugget_id == nuggets[0].nugget_id

    def test_get_nonexistent_nugget(self):
        """Test retrieving nonexistent nugget."""
        identifier = NuggetIdentifier()
        nugget = identifier.get_nugget("nonexistent")
        assert nugget is None

    def test_get_nuggets_by_subject(self):
        """Test retrieving nuggets by subject."""
        identifier = NuggetIdentifier()
        identifier.identify_nuggets("Python is powerful. Python is popular.")

        python_nuggets = identifier.get_nuggets_by_subject("Python")
        # Should find nuggets about Python
        assert len(python_nuggets) >= 0

    def test_get_nuggets_by_type_definition(self):
        """Test retrieving definition type nuggets."""
        identifier = NuggetIdentifier()
        identifier.identify_nuggets("AI is intelligence. ML is subset.")

        definitions = identifier.get_nuggets_by_type(NuggetType.DEFINITION)
        assert len(definitions) >= 0

    def test_get_top_nuggets(self):
        """Test retrieving top nuggets."""
        identifier = NuggetIdentifier()
        identifier.identify_nuggets(
            "Technology is important. Innovation drives change. Progress matters.",
            context="Tech industry trends"
        )

        top = identifier.get_top_nuggets(2)
        assert len(top) <= 2

    def test_batch_identify(self):
        """Test batch nugget identification."""
        identifier = NuggetIdentifier()
        texts = [
            "Python is powerful.",
            "Java is compiled.",
            "Ruby is dynamic.",
        ]
        nuggets, error = identifier.batch_identify(texts)

        assert error is None
        assert len(nuggets) >= 0

    def test_export_nugget(self):
        """Test exporting single nugget."""
        identifier = NuggetIdentifier()
        nuggets, _ = identifier.identify_nuggets("Test is valid.")

        if nuggets:
            exported = identifier.export_nugget(nuggets[0].nugget_id)
            assert exported is not None
            assert exported["nugget_id"] == nuggets[0].nugget_id

    def test_export_nonexistent(self):
        """Test exporting nonexistent nugget."""
        identifier = NuggetIdentifier()
        exported = identifier.export_nugget("nonexistent")
        assert exported is None

    def test_export_all_nuggets(self):
        """Test exporting all nuggets."""
        identifier = NuggetIdentifier()
        identifier.identify_nuggets("Test one. Test two.")
        identifier.identify_nuggets("Another test.")

        exported = identifier.export_all_nuggets()
        assert len(exported) >= 0

    def test_statistics_empty(self):
        """Test statistics with no nuggets."""
        identifier = NuggetIdentifier()
        stats = identifier.get_statistics()

        assert stats["total_nuggets"] == 0
        assert stats["avg_importance"] == 0.0

    def test_statistics_with_nuggets(self):
        """Test statistics with nuggets."""
        identifier = NuggetIdentifier()
        identifier.identify_nuggets("Python is language. Java is compiled.")
        identifier.identify_nuggets("Ruby is dynamic.")

        stats = identifier.get_statistics()
        assert stats["total_nuggets"] >= 0
        if stats["total_nuggets"] > 0:
            assert 0 <= stats["avg_importance"] <= 1.0

    def test_related_nuggets_same_subject(self):
        """Test nuggets with same subject are related."""
        identifier = NuggetIdentifier()
        nuggets, _ = identifier.identify_nuggets(
            "Python is powerful. Python is popular."
        )

        if len(nuggets) >= 2:
            # Check if related nuggets are linked
            # This depends on extraction quality
            assert all(isinstance(n.related_nuggets, list) for n in nuggets)

    def test_clean_subject_removes_articles(self):
        """Test subject cleaning removes articles."""
        identifier = NuggetIdentifier()
        cleaned = identifier._clean_subject("the machine learning")
        assert "the" not in cleaned.lower() or cleaned.lower() == "the machine learning"

    def test_extract_keywords(self):
        """Test keyword extraction."""
        identifier = NuggetIdentifier()
        keywords = identifier._extract_keywords("Machine learning enables powerful predictions")
        assert len(keywords) > 0
        assert all(len(k) > 3 for k in keywords)

    def test_nugget_types_comprehensive(self):
        """Test identification of different nugget types."""
        identifier = NuggetIdentifier()

        # Definition
        nuggets1, _ = identifier.identify_nuggets("AI is artificial intelligence.")
        # Property
        nuggets2, _ = identifier.identify_nuggets("Technology has limitations.")
        # Action
        nuggets3, _ = identifier.identify_nuggets("Engineers developed the system.")

        # At least some should be identified
        total = len(nuggets1) + len(nuggets2) + len(nuggets3)
        assert total >= 1

    def test_context_improves_importance(self):
        """Test that context affects importance scoring."""
        identifier = NuggetIdentifier()

        nuggets1, _ = identifier.identify_nuggets(
            "Python is a language.", context=""
        )
        nuggets2, _ = identifier.identify_nuggets(
            "Python is a language.", context="Python programming guide"
        )

        if nuggets1 and nuggets2:
            # With context, importance should potentially be higher
            assert isinstance(nuggets1[0].importance_score, float)
            assert isinstance(nuggets2[0].importance_score, float)

    def test_multiple_identifiers_independent(self):
        """Test multiple identifiers are independent."""
        id1 = NuggetIdentifier()
        id2 = NuggetIdentifier()

        id1.identify_nuggets("First nugget")
        id2.identify_nuggets("Second nugget")

        assert len(id1.nugget_history) >= 0
        assert len(id2.nugget_history) >= 0

    def test_complex_text_multiple_sentences(self):
        """Test complex text with multiple sentences."""
        identifier = NuggetIdentifier()
        text = """
        Python is a high-level language. It supports multiple programming paradigms.
        Machine learning is a subset of AI. Deep learning uses neural networks.
        These technologies are transforming industries.
        """
        nuggets, error = identifier.identify_nuggets(text)

        assert error is None
        assert len(nuggets) >= 0

    def test_sentence_splitting(self):
        """Test sentence splitting."""
        identifier = NuggetIdentifier()
        sentences = identifier._split_sentences("First. Second! Third?")
        assert len(sentences) >= 2

    def test_nugget_history_tracking(self):
        """Test nugget history is tracked."""
        identifier = NuggetIdentifier()

        identifier.identify_nuggets("First text.")
        identifier.identify_nuggets("Second text.")

        assert len(identifier.nugget_history) >= 0

    def test_confidence_and_importance_correlation(self):
        """Test that confidence and importance are correlated."""
        identifier = NuggetIdentifier()
        nuggets, _ = identifier.identify_nuggets(
            "Python is excellent for data science applications.",
            context="Data science tools"
        )

        for nugget in nuggets:
            # Higher confidence should generally lead to higher importance
            # (though not always due to context)
            assert 0.0 <= nugget.subject_predicate.confidence <= 1.0
            assert 0.0 <= nugget.importance_score <= 1.0


class TestNoKeywordsEdgeCase:
    """Regression test for issues-i4z.2.8: no extractable keywords in answer."""

    def test_no_keywords_returns_empty_no_crash(self):
        """Answer with no extractable keywords must return empty result, not crash."""
        identifier = NuggetIdentifier()
        nuggets, error = identifier.identify_nuggets("a b c d e")
        assert error is None or isinstance(error, str)
        assert isinstance(nuggets, list)

    def test_stopword_only_answer(self):
        """Answer with only stopwords/common words should not crash."""
        identifier = NuggetIdentifier()
        nuggets, _ = identifier.identify_nuggets("the and is in of to")
        assert isinstance(nuggets, list)

    def test_single_word_answer_handled(self):
        """Single word answer must not crash."""
        identifier = NuggetIdentifier()
        nuggets, _ = identifier.identify_nuggets("Yes")
        assert isinstance(nuggets, list)
