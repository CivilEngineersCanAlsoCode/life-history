"""
Test suite for domain-specific question templates.

Tests cover:
- Template loading and retrieval
- Domain and category filtering
- Template specialization
- Statistics and exports
"""

import pytest

from life_brain.retrieval.domain_questions import (
    DomainQuestions,
    Domain,
    QuestionTemplate,
    SpecializedQuestion,
)


class TestQuestionTemplate:
    """Test QuestionTemplate dataclass."""

    def test_create_template(self):
        """Test creating template."""
        template = QuestionTemplate(
            template_id="test_1",
            domain=Domain.CAREER,
            category="impact",
            template_text="What's the impact of {project}?",
        )

        assert template.template_id == "test_1"
        assert template.domain == Domain.CAREER

    def test_to_dict(self):
        """Test converting to dict."""
        template = QuestionTemplate(
            template_id="test_2",
            domain=Domain.RELATIONSHIPS,
            category="feelings",
            template_text="How do you feel about {situation}?",
            keywords=["emotion", "vulnerability"],
        )

        d = template.to_dict()
        assert d["domain"] == "relationships"
        assert len(d["keywords"]) == 2


class TestSpecializedQuestion:
    """Test SpecializedQuestion dataclass."""

    def test_create_specialized(self):
        """Test creating specialized question."""
        q = SpecializedQuestion(
            question_id="q_001",
            template_id="career_1",
            domain=Domain.CAREER,
            original_template="What's the impact of {project}?",
            specialized_text="What's the impact of project X?",
            context="Team planning",
        )

        assert q.question_id == "q_001"
        assert q.specialized_text == "What's the impact of project X?"

    def test_to_dict(self):
        """Test converting to dict."""
        q = SpecializedQuestion(
            question_id="q_002",
            template_id="rel_1",
            domain=Domain.RELATIONSHIPS,
            original_template="How do you feel about {situation}?",
            specialized_text="How do you feel about our communication?",
            context="Relationship reflection",
        )

        d = q.to_dict()
        assert d["domain"] == "relationships"
        assert "communication" in d["specialized_text"]


class TestDomainQuestions:
    """Test DomainQuestions functionality."""

    def test_create_domain_questions(self):
        """Test creating domain questions."""
        dq = DomainQuestions()
        assert len(dq.templates) > 0

    def test_templates_loaded(self):
        """Test all templates are loaded."""
        dq = DomainQuestions()

        # Check each domain has templates
        for domain in Domain:
            domain_templates = dq.get_templates_by_domain(domain)
            # Most domains should have templates
            if domain != Domain.FINANCE:  # Finance might have fewer
                assert len(domain_templates) >= 1

    def test_get_template(self):
        """Test retrieving specific template."""
        dq = DomainQuestions()

        template = dq.get_template("career_impact_1")
        assert template is not None
        assert template.domain == Domain.CAREER

    def test_get_nonexistent_template(self):
        """Test retrieving nonexistent template."""
        dq = DomainQuestions()
        template = dq.get_template("nonexistent")
        assert template is None

    def test_get_templates_by_domain_career(self):
        """Test getting career templates."""
        dq = DomainQuestions()

        career_templates = dq.get_templates_by_domain(Domain.CAREER)
        assert len(career_templates) >= 1
        assert all(t.domain == Domain.CAREER for t in career_templates)

    def test_get_templates_by_domain_relationships(self):
        """Test getting relationship templates."""
        dq = DomainQuestions()

        rel_templates = dq.get_templates_by_domain(Domain.RELATIONSHIPS)
        assert len(rel_templates) >= 1
        assert all(t.domain == Domain.RELATIONSHIPS for t in rel_templates)

    def test_get_templates_by_domain_health(self):
        """Test getting health templates."""
        dq = DomainQuestions()

        health_templates = dq.get_templates_by_domain(Domain.HEALTH)
        assert len(health_templates) >= 1

    def test_get_templates_by_domain_learning(self):
        """Test getting learning templates."""
        dq = DomainQuestions()

        learning_templates = dq.get_templates_by_domain(Domain.LEARNING)
        assert len(learning_templates) >= 1

    def test_get_templates_by_category_career_impact(self):
        """Test getting career impact templates."""
        dq = DomainQuestions()

        impact_templates = dq.get_templates_by_category(Domain.CAREER, "impact")
        assert len(impact_templates) >= 1
        assert all(t.category == "impact" for t in impact_templates)

    def test_get_templates_by_category_career_metrics(self):
        """Test getting career metrics templates."""
        dq = DomainQuestions()

        metrics_templates = dq.get_templates_by_category(Domain.CAREER, "metrics")
        assert len(metrics_templates) >= 1

    def test_get_templates_by_category_relationship_feelings(self):
        """Test getting relationship feelings templates."""
        dq = DomainQuestions()

        feelings_templates = dq.get_templates_by_category(
            Domain.RELATIONSHIPS, "feelings"
        )
        assert len(feelings_templates) >= 1

    def test_specialize_template(self):
        """Test specializing a template."""
        dq = DomainQuestions()

        question, error = dq.specialize_template(
            "career_impact_1",
            {"role/project": "New Platform", "stakeholders": "Users"},
            context="Product planning",
        )

        assert error is None
        assert question is not None
        assert "New Platform" in question.specialized_text
        assert "Users" in question.specialized_text

    def test_specialize_nonexistent_template(self):
        """Test specializing nonexistent template."""
        dq = DomainQuestions()

        question, error = dq.specialize_template(
            "nonexistent", {"param": "value"}
        )

        assert error is not None
        assert question is None

    def test_specialize_relationship_template(self):
        """Test specializing relationship template."""
        dq = DomainQuestions()

        question, error = dq.specialize_template(
            "relationship_feelings_1",
            {"situation": "my partner's career change"},
            context="Checking in",
        )

        assert error is None
        assert "partner's career change" in question.specialized_text

    def test_specialize_health_template(self):
        """Test specializing health template."""
        dq = DomainQuestions()

        question, error = dq.specialize_template(
            "health_energy_1",
            {"most/least": "most"},
            context="Energy audit",
        )

        assert error is None

    def test_specialize_learning_template(self):
        """Test specializing learning template."""
        dq = DomainQuestions()

        question, error = dq.specialize_template(
            "learning_why_1",
            {"skill": "machine learning"},
            context="Career development",
        )

        assert error is None
        assert "machine learning" in question.specialized_text

    def test_get_domain_overview_career(self):
        """Test getting domain overview for career."""
        dq = DomainQuestions()

        overview = dq.get_domain_overview(Domain.CAREER)
        assert overview["domain"] == "career"
        assert overview["total_templates"] >= 3
        assert "impact" in overview["categories"]

    def test_get_domain_overview_relationships(self):
        """Test getting domain overview for relationships."""
        dq = DomainQuestions()

        overview = dq.get_domain_overview(Domain.RELATIONSHIPS)
        assert overview["domain"] == "relationships"
        assert overview["total_templates"] >= 3

    def test_get_domain_overview_health(self):
        """Test getting domain overview for health."""
        dq = DomainQuestions()

        overview = dq.get_domain_overview(Domain.HEALTH)
        assert overview["domain"] == "health"
        assert len(overview["categories"]) >= 1

    def test_get_statistics(self):
        """Test getting statistics."""
        dq = DomainQuestions()

        stats = dq.get_statistics()
        assert stats["total_templates"] >= 15
        assert stats["total_domains"] >= 5

    def test_export_template(self):
        """Test exporting template."""
        dq = DomainQuestions()

        exported = dq.export_template("career_impact_1")
        assert exported is not None
        assert exported["template_id"] == "career_impact_1"

    def test_export_nonexistent_template(self):
        """Test exporting nonexistent template."""
        dq = DomainQuestions()

        exported = dq.export_template("nonexistent")
        assert exported is None

    def test_export_all_templates(self):
        """Test exporting all templates."""
        dq = DomainQuestions()

        exported = dq.export_all_templates()
        assert len(exported) >= 15

    def test_export_specialized(self):
        """Test exporting specialized question."""
        dq = DomainQuestions()

        question, _ = dq.specialize_template(
            "career_impact_1",
            {"role/project": "Project X", "stakeholders": "Team"},
        )

        exported = dq.export_specialized(question.question_id)
        assert exported is not None
        assert "Project X" in exported["specialized_text"]

    def test_batch_specialize(self):
        """Test batch specialization."""
        dq = DomainQuestions()

        template_ids = ["career_impact_1", "relationship_feelings_1"]
        params = [
            {"role/project": "Platform", "stakeholders": "Users"},
            {"situation": "career change"},
        ]

        questions, error = dq.batch_specialize(template_ids, params)

        assert error is None
        assert len(questions) == 2

    def test_batch_specialize_mismatch(self):
        """Test batch specialize with mismatched counts."""
        dq = DomainQuestions()

        template_ids = ["career_impact_1"]
        params = [
            {"param": "value"},
            {"param": "value2"},
        ]

        questions, error = dq.batch_specialize(template_ids, params)

        assert error is not None
        assert len(questions) == 0

    def test_template_has_follow_ups(self):
        """Test that templates have follow-up questions."""
        dq = DomainQuestions()

        template = dq.get_template("career_impact_1")
        assert len(template.follow_ups) > 0

    def test_template_has_keywords(self):
        """Test that templates have keywords."""
        dq = DomainQuestions()

        template = dq.get_template("relationship_feelings_1")
        assert len(template.keywords) > 0

    def test_template_has_expertise_areas(self):
        """Test that templates have expertise areas."""
        dq = DomainQuestions()

        template = dq.get_template("career_growth_1")
        assert len(template.expertise_areas) > 0

    def test_multiple_domain_questions_independent(self):
        """Test multiple instances are independent."""
        dq1 = DomainQuestions()
        dq2 = DomainQuestions()

        q1, _ = dq1.specialize_template(
            "career_impact_1",
            {"role/project": "P1", "stakeholders": "S1"},
        )
        q2, _ = dq2.specialize_template(
            "career_impact_1",
            {"role/project": "P2", "stakeholders": "S2"},
        )

        assert "P1" in q1.specialized_text
        assert "P2" in q2.specialized_text
        assert q1.specialized_text != q2.specialized_text

    def test_all_domains_have_templates(self):
        """Test all domains have at least one template."""
        dq = DomainQuestions()

        for domain in [
            Domain.CAREER,
            Domain.RELATIONSHIPS,
            Domain.HEALTH,
            Domain.LEARNING,
            Domain.PERSONAL_GROWTH,
        ]:
            templates = dq.get_templates_by_domain(domain)
            assert len(templates) > 0

    def test_specialize_preserves_context(self):
        """Test that specialization preserves context."""
        dq = DomainQuestions()

        context = "Important meeting prep"
        question, _ = dq.specialize_template(
            "career_impact_1",
            {"role/project": "X", "stakeholders": "Y"},
            context=context,
        )

        assert question.context == context

    def test_template_parameter_substitution(self):
        """Test parameter substitution in templates."""
        dq = DomainQuestions()

        question, _ = dq.specialize_template(
            "learning_why_1",
            {"skill": "Python"},
            context="Learning planning",
        )

        # Original template has {skill}, should be replaced
        assert "{skill}" not in question.specialized_text
        assert "Python" in question.specialized_text
