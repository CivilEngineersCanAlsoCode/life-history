"""
Test suite for completeness and excellence (CE) check module.

Tests cover:
- Completeness score calculation
- Missing component identification
- Coverage area analysis
- Query intent analysis
- Response component extraction
- Batch operations and statistics
"""

import pytest

from life_brain.truth.completeness_check import (
    CompletenessValidator,
    CompletenessCheck,
    MissingComponent,
    CompletenessLevel,
)


class TestMissingComponent:
    """Test MissingComponent dataclass."""

    def test_create_missing_component(self):
        """Test creating missing component."""
        missing = MissingComponent(
            component_type="concept",
            description="Missing key concept",
            priority=3,
            relevance_score=0.7,
        )

        assert missing.component_type == "concept"
        assert missing.priority == 3

    def test_missing_component_default_found(self):
        """Test missing component default found value."""
        missing = MissingComponent(
            component_type="detail",
            description="Test",
            priority=2,
            relevance_score=0.5,
        )

        assert missing.found_in_response is False


class TestCompletenessCheck:
    """Test CompletenessCheck dataclass."""

    def test_create_check(self):
        """Test creating completeness check."""
        check = CompletenessCheck(
            check_id="ce_001",
            query="How do I improve my skills?",
            response="Practice regularly and learn from mistakes.",
            completeness_score=0.8,
            completeness_level=CompletenessLevel.SUBSTANTIAL,
        )

        assert check.check_id == "ce_001"
        assert check.completeness_score == 0.8

    def test_to_dict(self):
        """Test converting to dict."""
        check = CompletenessCheck(
            check_id="ce_002",
            query="What's the best approach?",
            response="The best approach depends on your context.",
            completeness_score=0.7,
            completeness_level=CompletenessLevel.PARTIAL,
            suggestions=["Add more examples"],
        )

        d = check.to_dict()
        assert d["check_id"] == "ce_002"
        assert d["completeness_level"] == "partial"
        assert len(d["suggestions"]) == 1


class TestCompletenessValidator:
    """Test CompletenessValidator functionality."""

    def test_create_validator(self):
        """Test creating validator."""
        validator = CompletenessValidator()
        assert len(validator.checks) == 0
        assert len(validator.check_history) == 0

    def test_check_completeness_complete(self):
        """Test completely addressing query."""
        validator = CompletenessValidator()

        check, error = validator.check_completeness(
            query="What are the benefits of exercise?",
            response="Exercise has numerous benefits: it improves cardiovascular health, increases strength, boosts mental health by releasing endorphins, helps with weight management, and improves sleep quality. Regular exercise also reduces risk of chronic diseases.",
        )

        assert error is None
        assert check is not None
        assert check.completeness_score > 0.75

    def test_check_completeness_incomplete(self):
        """Test incomplete response."""
        validator = CompletenessValidator()

        check, error = validator.check_completeness(
            query="What should I do about my career concerns?",
            response="Think about it.",
        )

        assert error is None
        assert check.completeness_score < 0.7

    def test_check_completeness_partial(self):
        """Test partially complete response."""
        validator = CompletenessValidator()

        check, error = validator.check_completeness(
            query="How should I approach this project?",
            response="You should start by defining the project scope and requirements, then create a timeline. Make sure to communicate with stakeholders.",
        )

        assert error is None
        assert check.completeness_level in [
            CompletenessLevel.PARTIAL,
            CompletenessLevel.SUBSTANTIAL,
        ]

    def test_check_completeness_empty_query(self):
        """Test with empty query."""
        validator = CompletenessValidator()

        check, error = validator.check_completeness(query="", response="Some response")

        assert error == "Empty query"
        assert check is None

    def test_check_completeness_empty_response(self):
        """Test with empty response."""
        validator = CompletenessValidator()

        check, error = validator.check_completeness(
            query="What is your name?", response=""
        )

        assert error == "Empty response"
        assert check is None

    def test_check_completeness_both_empty(self):
        """Test with both empty."""
        validator = CompletenessValidator()

        check, error = validator.check_completeness(query="", response="")

        assert error == "Empty query"
        assert check is None

    def test_check_id_auto_generated(self):
        """Test auto-generated check ID."""
        validator = CompletenessValidator()

        check1, _ = validator.check_completeness(
            query="Q1", response="A comprehensive response to the query."
        )
        check2, _ = validator.check_completeness(
            query="Q2", response="Another comprehensive response."
        )

        assert check1.check_id == "ce_0000"
        assert check2.check_id == "ce_0001"

    def test_check_id_custom(self):
        """Test custom check ID."""
        validator = CompletenessValidator()

        check, _ = validator.check_completeness(
            query="Question", response="Response text here.", check_id="custom_ce_001"
        )

        assert check.check_id == "custom_ce_001"

    def test_why_question_completeness(self):
        """Test completeness for why questions."""
        validator = CompletenessValidator()

        check, _ = validator.check_completeness(
            query="Why should I invest in education?",
            response="Education provides knowledge, improves job prospects, increases earning potential, and enables personal growth. It's an investment in your future.",
        )

        # Should identify explanation/evidence components
        assert check.missing_components is not None

    def test_how_question_completeness(self):
        """Test completeness for how questions."""
        validator = CompletenessValidator()

        check, _ = validator.check_completeness(
            query="How can I improve my productivity?",
            response="To improve productivity, you can: set clear goals, break tasks into smaller steps, eliminate distractions, take regular breaks, and track your progress.",
        )

        assert check.completeness_score > 0.6

    def test_what_question_completeness(self):
        """Test completeness for what questions."""
        validator = CompletenessValidator()

        check, _ = validator.check_completeness(
            query="What are the main challenges?",
            response="The main challenges are time management, resource constraints, and technical limitations.",
        )

        assert check is not None

    def test_decision_question_completeness(self):
        """Test completeness for decision questions."""
        validator = CompletenessValidator()

        check, _ = validator.check_completeness(
            query="Should I accept this job offer?",
            response="Yes, because the offer provides good salary, growth opportunities, and aligns with your career goals.",
        )

        assert check.completeness_level != CompletenessLevel.INCOMPLETE

    def test_missing_components_identified(self):
        """Test that missing components are identified."""
        validator = CompletenessValidator()

        check, _ = validator.check_completeness(
            query="What should I do about this serious problem?",
            response="It's complicated.",
        )

        assert len(check.missing_components) > 0

    def test_missing_components_not_identified_for_complete(self):
        """Test few missing components for complete responses."""
        validator = CompletenessValidator()

        check, _ = validator.check_completeness(
            query="What is 2 + 2?",
            response="2 + 2 equals 4. This is basic arithmetic where two quantities of 2 are combined to get 4.",
        )

        # Complete response should have few or no major missing components
        critical_missing = [m for m in check.missing_components if m.priority >= 4]
        assert len(critical_missing) == 0 or check.completeness_score > 0.8

    def test_coverage_areas_calculated(self):
        """Test coverage areas are calculated."""
        validator = CompletenessValidator()

        check, _ = validator.check_completeness(
            query="Why and how should I learn programming?",
            response="You should learn programming because it's in high demand and enables you to build things. Start by learning Python or JavaScript basics.",
        )

        assert len(check.coverage_areas) > 0
        assert all(0 <= v <= 1 for v in check.coverage_areas.values())

    def test_suggestions_generated(self):
        """Test suggestions are generated for incomplete responses."""
        validator = CompletenessValidator()

        check, _ = validator.check_completeness(
            query="How do I handle conflict in relationships?",
            response="Listen to the other person.",
        )

        assert len(check.suggestions) > 0

    def test_suggestions_minimal_for_complete(self):
        """Test fewer suggestions for complete responses."""
        validator = CompletenessValidator()

        check, _ = validator.check_completeness(
            query="What is water?",
            response="Water is a transparent, odorless liquid that is essential for all living organisms. It covers about 71% of Earth's surface and is composed of hydrogen and oxygen (H2O). Water is used for drinking, agriculture, industry, and recreation. It exists in three states: solid (ice), liquid (water), and gas (steam).",
        )

        assert len(check.suggestions) <= 2 or check.completeness_score > 0.85

    def test_completeness_level_incomplete(self):
        """Test incomplete level."""
        validator = CompletenessValidator()

        check, _ = validator.check_completeness(
            query="Explain quantum computing", response="It's complex."
        )

        assert check.completeness_level == CompletenessLevel.INCOMPLETE

    def test_completeness_level_partial(self):
        """Test partial level."""
        validator = CompletenessValidator()

        check, _ = validator.check_completeness(
            query="Explain photosynthesis",
            response="Photosynthesis is a process where plants convert sunlight into chemical energy.",
        )

        assert check.completeness_level in [
            CompletenessLevel.PARTIAL,
            CompletenessLevel.INCOMPLETE,
        ]

    def test_completeness_level_substantial(self):
        """Test substantial level."""
        validator = CompletenessValidator()

        check, _ = validator.check_completeness(
            query="What is machine learning?",
            response="Machine learning is a subset of artificial intelligence where systems learn from data without being explicitly programmed. It includes supervised learning for predictions, unsupervised learning for pattern discovery, and reinforcement learning for decision-making. Applications include image recognition, natural language processing, and recommendation systems.",
        )

        assert check.completeness_level in [
            CompletenessLevel.SUBSTANTIAL,
            CompletenessLevel.COMPLETE,
        ]

    def test_completeness_level_complete(self):
        """Test complete level."""
        validator = CompletenessValidator()

        check, _ = validator.check_completeness(
            query="Define cloud computing and its benefits",
            response="Cloud computing is the delivery of computing services over the internet including servers, storage, databases, and software. Benefits include cost savings through pay-as-you-go pricing, scalability to handle varying workloads, accessibility from anywhere, automatic updates and maintenance, disaster recovery capabilities, and flexibility in choosing services. Examples include AWS, Azure, and Google Cloud.",
        )

        assert check.completeness_level == CompletenessLevel.COMPLETE

    def test_get_check(self):
        """Test retrieving specific check."""
        validator = CompletenessValidator()

        validator.check_completeness(
            query="Test", response="Response text.", check_id="test_ce_001"
        )

        check = validator.get_check("test_ce_001")
        assert check is not None
        assert check.check_id == "test_ce_001"

    def test_get_nonexistent_check(self):
        """Test retrieving nonexistent check."""
        validator = CompletenessValidator()
        check = validator.get_check("nonexistent")
        assert check is None

    def test_get_checks_by_level_incomplete(self):
        """Test getting incomplete level checks."""
        validator = CompletenessValidator()

        validator.check_completeness("Q1", "A")
        validator.check_completeness("Q2", "A comprehensive response with many details.")

        incomplete_checks = validator.get_checks_by_level(CompletenessLevel.INCOMPLETE)
        assert len(incomplete_checks) > 0

    def test_batch_check(self):
        """Test batch checking."""
        validator = CompletenessValidator()

        pairs = [
            ("Question 1", "Response 1"),
            ("Question 2", "Response 2"),
            ("Question 3", "Response 3"),
        ]

        checks, error = validator.batch_check(pairs)

        assert error is None
        assert len(checks) == 3

    def test_batch_check_empty(self):
        """Test batch with empty pairs."""
        validator = CompletenessValidator()

        checks, error = validator.batch_check([])

        assert error is None
        assert len(checks) == 0

    def test_export_check(self):
        """Test exporting single check."""
        validator = CompletenessValidator()

        validator.check_completeness(
            query="Q", response="Response.", check_id="exp_001"
        )

        exported = validator.export_check("exp_001")
        assert exported is not None
        assert exported["check_id"] == "exp_001"

    def test_export_nonexistent(self):
        """Test exporting nonexistent check."""
        validator = CompletenessValidator()
        exported = validator.export_check("nonexistent")
        assert exported is None

    def test_export_all_checks(self):
        """Test exporting all checks."""
        validator = CompletenessValidator()

        validator.check_completeness("Q1", "Response 1")
        validator.check_completeness("Q2", "Response 2")

        exported = validator.export_all_checks()
        assert len(exported) == 2

    def test_statistics_empty(self):
        """Test statistics with no checks."""
        validator = CompletenessValidator()
        stats = validator.get_statistics()

        assert stats["total_checks"] == 0
        assert stats["avg_completeness"] == 0.0

    def test_statistics_with_checks(self):
        """Test statistics with multiple checks."""
        validator = CompletenessValidator()

        validator.check_completeness("Q1", "A")
        validator.check_completeness("Q2", "A comprehensive response.")
        validator.check_completeness(
            "Q3", "An extensive and detailed response with all components."
        )

        stats = validator.get_statistics()
        assert stats["total_checks"] == 3
        assert stats["avg_completeness"] > 0

    def test_multiple_validators_independent(self):
        """Test multiple validators are independent."""
        v1 = CompletenessValidator()
        v2 = CompletenessValidator()

        v1.check_completeness("Q1", "R1")
        v2.check_completeness("Q2", "R2")

        assert len(v1.check_history) == 1
        assert len(v2.check_history) == 1

    def test_completeness_with_examples(self):
        """Test completeness improves with examples."""
        validator = CompletenessValidator()

        check_no_examples, _ = validator.check_completeness(
            query="What are design patterns?",
            response="Design patterns are reusable solutions to common programming problems.",
        )

        check_with_examples, _ = validator.check_completeness(
            query="What are design patterns?",
            response="Design patterns are reusable solutions to common programming problems. Examples include Singleton, Factory, Observer, and Strategy patterns. Each addresses a specific type of problem.",
        )

        assert check_with_examples.completeness_score > check_no_examples.completeness_score

    def test_vague_language_detection(self):
        """Test detection of vague language."""
        validator = CompletenessValidator()

        check, _ = validator.check_completeness(
            query="What should I do?",
            response="Maybe you could possibly try something like this, perhaps, if it might work.",
        )

        # Should identify vagueness
        vague_missing = [
            m
            for m in check.missing_components
            if "uncertainty" in m.description or "vagueness" in m.description
        ]
        assert len(vague_missing) > 0 or check.completeness_score < 0.7

    def test_complex_multi_part_query(self):
        """Test completeness for complex multi-part query."""
        validator = CompletenessValidator()

        check, _ = validator.check_completeness(
            query="What are the benefits, challenges, and best practices for remote work?",
            response="Benefits include flexibility, cost savings, and productivity. Challenges include isolation, communication gaps, and distractions. Best practices: set clear boundaries, use communication tools, maintain regular check-ins, and provide proper equipment.",
        )

        assert check.completeness_level != CompletenessLevel.INCOMPLETE

    def test_confidence_scoring_bounds(self):
        """Test completeness score is always 0-1."""
        validator = CompletenessValidator()

        for i in range(5):
            check, _ = validator.check_completeness(
                query=f"Question {i}",
                response=f"Response {i}" * (i + 1),
            )
            assert 0.0 <= check.completeness_score <= 1.0

    def test_workflow_complete(self):
        """Test complete workflow."""
        validator = CompletenessValidator()

        # Check completeness
        check, error = validator.check_completeness(
            query="How do I improve productivity?",
            response="Productivity can be improved through: goal setting, time blocking, eliminating distractions, regular breaks, and tracking progress. Each method has been proven to increase output.",
        )

        assert error is None
        assert check.completeness_score > 0.6

        # Get check
        retrieved = validator.get_check(check.check_id)
        assert retrieved is not None

        # Export
        exported = validator.export_check(check.check_id)
        assert exported["completeness_level"] in [
            "partial",
            "substantial",
            "complete",
        ]

        # Stats
        stats = validator.get_statistics()
        assert stats["total_checks"] == 1
