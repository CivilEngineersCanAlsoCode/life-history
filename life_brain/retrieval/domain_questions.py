"""
Domain-specific question templates.

Pre-built question templates for different life domains with specialized
prompts optimized for each area (career, relationships, health, learning).
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Domain(Enum):
    """Life domains."""

    CAREER = "career"
    RELATIONSHIPS = "relationships"
    HEALTH = "health"
    LEARNING = "learning"
    PERSONAL_GROWTH = "personal_growth"
    FINANCE = "finance"
    PROJECTS = "projects"


@dataclass
class QuestionTemplate:
    """Single question template."""

    template_id: str
    domain: Domain
    category: str  # "impact", "metrics", "feelings", etc.
    template_text: str  # With {placeholder} for customization
    follow_ups: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    expertise_areas: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "template_id": self.template_id,
            "domain": self.domain.value,
            "category": self.category,
            "template_text": self.template_text,
            "follow_ups": self.follow_ups,
            "keywords": self.keywords,
            "expertise_areas": self.expertise_areas,
        }


@dataclass
class SpecializedQuestion:
    """Question specialized from template."""

    question_id: str
    template_id: str
    domain: Domain
    original_template: str
    specialized_text: str
    context: str  # "What this is about"
    parameters: Dict[str, str] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "question_id": self.question_id,
            "template_id": self.template_id,
            "domain": self.domain.value,
            "specialized_text": self.specialized_text,
            "context": self.context,
            "parameters": self.parameters,
            "created_at": self.created_at,
        }


class DomainQuestions:
    """Manage domain-specific question templates."""

    # Career questions
    CAREER_TEMPLATES = [
        QuestionTemplate(
            template_id="career_impact_1",
            domain=Domain.CAREER,
            category="impact",
            template_text="What is the real impact of {role/project}? How does it affect {stakeholders}?",
            follow_ups=[
                "Who benefits most?",
                "What would break if this disappeared?",
                "How is success measured?",
            ],
            keywords=["impact", "stakeholders", "value", "outcomes"],
            expertise_areas=["strategy", "leadership"],
        ),
        QuestionTemplate(
            template_id="career_metrics_1",
            domain=Domain.CAREER,
            category="metrics",
            template_text="What are the key metrics for {role/project}? How do we measure success?",
            follow_ups=[
                "What's the baseline?",
                "What's the target?",
                "How do we track progress?",
            ],
            keywords=["metrics", "measurement", "OKR", "success"],
            expertise_areas=["systems", "execution"],
        ),
        QuestionTemplate(
            template_id="career_growth_1",
            domain=Domain.CAREER,
            category="growth",
            template_text="How can I grow from {current_position} into {target_position}? What skills matter?",
            follow_ups=[
                "What's missing?",
                "How long would this take?",
                "Who can help me?",
            ],
            keywords=["growth", "development", "skills", "career path"],
            expertise_areas=["interviews", "scale"],
        ),
    ]

    # Relationship questions
    RELATIONSHIP_TEMPLATES = [
        QuestionTemplate(
            template_id="relationship_feelings_1",
            domain=Domain.RELATIONSHIPS,
            category="feelings",
            template_text="How do you feel about {situation}? What emotions come up?",
            follow_ups=[
                "Why do you feel this way?",
                "What would help?",
                "Have you shared this?",
            ],
            keywords=["emotions", "feelings", "vulnerability", "connection"],
            expertise_areas=["vulnerability", "relationships"],
        ),
        QuestionTemplate(
            template_id="relationship_conflict_1",
            domain=Domain.RELATIONSHIPS,
            category="conflict",
            template_text="What's the core issue in {conflict}? What does each person need?",
            follow_ups=[
                "What's their perspective?",
                "Where's the common ground?",
                "What could bridge the gap?",
            ],
            keywords=["conflict", "resolution", "empathy", "needs"],
            expertise_areas=["negotiation", "relationships"],
        ),
        QuestionTemplate(
            template_id="relationship_communication_1",
            domain=Domain.RELATIONSHIPS,
            category="communication",
            template_text="How can you express {concern/feeling} to {person} without blame?",
            follow_ups=[
                "What's your core fear?",
                "What do you want from them?",
                "How can you show vulnerability?",
            ],
            keywords=["communication", "honesty", "vulnerability", "dialogue"],
            expertise_areas=["negotiation", "relationships"],
        ),
    ]

    # Health questions
    HEALTH_TEMPLATES = [
        QuestionTemplate(
            template_id="health_energy_1",
            domain=Domain.HEALTH,
            category="energy",
            template_text="What affects your energy levels? When do you feel {most/least} energized?",
            follow_ups=[
                "What's the pattern?",
                "What helps recovery?",
                "What drains you?",
            ],
            keywords=["energy", "vitality", "recovery", "patterns"],
            expertise_areas=["science", "wellness"],
        ),
        QuestionTemplate(
            template_id="health_habits_1",
            domain=Domain.HEALTH,
            category="habits",
            template_text="What one habit would most improve your {health area}? Why haven't you started?",
            follow_ups=[
                "What's the blocker?",
                "How would you make it easy?",
                "Who can help?",
            ],
            keywords=["habits", "behavior", "change", "sustainability"],
            expertise_areas=["science", "systems"],
        ),
        QuestionTemplate(
            template_id="health_balance_1",
            domain=Domain.HEALTH,
            category="balance",
            template_text="How balanced is your {sleep/exercise/diet/stress}? What's ideal?",
            follow_ups=[
                "What's off?",
                "What would fix it?",
                "What's the first step?",
            ],
            keywords=["balance", "wellness", "holistic", "integration"],
            expertise_areas=["science", "systems"],
        ),
    ]

    # Learning questions
    LEARNING_TEMPLATES = [
        QuestionTemplate(
            template_id="learning_why_1",
            domain=Domain.LEARNING,
            category="purpose",
            template_text="Why do you want to learn {skill}? How would you use it?",
            follow_ups=[
                "What's the real goal?",
                "Who needs this skill?",
                "What happens if you don't learn it?",
            ],
            keywords=["purpose", "motivation", "application", "context"],
            expertise_areas=["first_principles", "learning"],
        ),
        QuestionTemplate(
            template_id="learning_approach_1",
            domain=Domain.LEARNING,
            category="strategy",
            template_text="What's the best way to learn {skill}? How would you approach it?",
            follow_ups=[
                "What fundamentals matter?",
                "How would you practice?",
                "How would you know you've learned it?",
            ],
            keywords=["learning", "strategy", "fundamentals", "mastery"],
            expertise_areas=["first_principles", "science"],
        ),
        QuestionTemplate(
            template_id="learning_challenge_1",
            domain=Domain.LEARNING,
            category="obstacles",
            template_text="What's the hardest part of learning {skill}? How do you overcome it?",
            follow_ups=[
                "What's the blocker?",
                "How have you solved similar problems?",
                "Who could help?",
            ],
            keywords=["challenge", "obstacles", "persistence", "support"],
            expertise_areas=["first_principles", "challenge"],
        ),
    ]

    # Personal growth questions
    GROWTH_TEMPLATES = [
        QuestionTemplate(
            template_id="growth_values_1",
            domain=Domain.PERSONAL_GROWTH,
            category="values",
            template_text="What are your core values? How aligned is your life with them?",
            follow_ups=[
                "Which value is most neglected?",
                "What would living them look like?",
                "What's one change you'd make?",
            ],
            keywords=["values", "purpose", "alignment", "integrity"],
            expertise_areas=["ethics", "consciousness"],
        ),
        QuestionTemplate(
            template_id="growth_identity_1",
            domain=Domain.PERSONAL_GROWTH,
            category="identity",
            template_text="Who are you becoming? Is that who you want to be?",
            follow_ups=[
                "What identity are you building?",
                "What would change it?",
                "What's holding you back?",
            ],
            keywords=["identity", "self", "becoming", "evolution"],
            expertise_areas=["vulnerability", "consciousness"],
        ),
        QuestionTemplate(
            template_id="growth_challenge_1",
            domain=Domain.PERSONAL_GROWTH,
            category="challenge",
            template_text="What's your biggest limitation right now? How could you transcend it?",
            follow_ups=[
                "Where does this come from?",
                "What's the first step?",
                "Who do you need to become?",
            ],
            keywords=["limitation", "growth", "transcendence", "potential"],
            expertise_areas=["consciousness", "inspiration"],
        ),
    ]

    # Finance questions
    FINANCE_TEMPLATES = [
        QuestionTemplate(
            template_id="finance_goal_1",
            domain=Domain.FINANCE,
            category="goals",
            template_text="What's your financial goal for {timeframe}? What does financial freedom mean to you?",
            follow_ups=[
                "What's the number?",
                "How would you get there?",
                "What's the first step?",
            ],
            keywords=["goals", "wealth", "freedom", "independence"],
            expertise_areas=["value", "scale"],
        ),
        QuestionTemplate(
            template_id="finance_leverage_1",
            domain=Domain.FINANCE,
            category="leverage",
            template_text="Where's your leverage? How can you earn more without trading time?",
            follow_ups=[
                "What could you build?",
                "What skills have leverage?",
                "How long would it take?",
            ],
            keywords=["leverage", "passive income", "multiplication", "optionality"],
            expertise_areas=["optionality", "scale"],
        ),
    ]

    # Projects questions
    PROJECT_TEMPLATES = [
        QuestionTemplate(
            template_id="project_problem_1",
            domain=Domain.PROJECTS,
            category="problem",
            template_text="What problem does {project} solve? For whom? How urgent?",
            follow_ups=[
                "Who's the user?",
                "Why do they care?",
                "What would they pay?",
            ],
            keywords=["problem", "user", "value", "market"],
            expertise_areas=["scale", "strategy"],
        ),
        QuestionTemplate(
            template_id="project_execution_1",
            domain=Domain.PROJECTS,
            category="execution",
            template_text="What's the MVP? What's the minimum to test the idea?",
            follow_ups=[
                "What can you do in a week?",
                "Who's your first user?",
                "How do you measure success?",
            ],
            keywords=["MVP", "execution", "validation", "iteration"],
            expertise_areas=["systems", "execution"],
        ),
    ]

    def __init__(self):
        """Initialize with all templates."""
        self.templates: Dict[str, QuestionTemplate] = {}
        self.specialized_questions: Dict[str, SpecializedQuestion] = {}
        self.specialization_history: List[SpecializedQuestion] = []
        self._load_templates()

    def _load_templates(self) -> None:
        """Load all templates."""
        all_templates = (
            self.CAREER_TEMPLATES
            + self.RELATIONSHIP_TEMPLATES
            + self.HEALTH_TEMPLATES
            + self.LEARNING_TEMPLATES
            + self.GROWTH_TEMPLATES
            + self.FINANCE_TEMPLATES
            + self.PROJECT_TEMPLATES
        )

        for template in all_templates:
            self.templates[template.template_id] = template

    def get_template(self, template_id: str) -> Optional[QuestionTemplate]:
        """Get specific template."""
        return self.templates.get(template_id)

    def get_templates_by_domain(self, domain: Domain) -> List[QuestionTemplate]:
        """Get all templates for a domain."""
        return [
            t for t in self.templates.values() if t.domain == domain
        ]

    def get_templates_by_category(
        self, domain: Domain, category: str
    ) -> List[QuestionTemplate]:
        """Get templates for specific domain and category."""
        return [
            t for t in self.templates.values()
            if t.domain == domain and t.category == category
        ]

    def specialize_template(
        self,
        template_id: str,
        parameters: Dict[str, str],
        context: str = "",
    ) -> Tuple[Optional[SpecializedQuestion], Optional[str]]:
        """Specialize a template with parameters."""
        template = self.get_template(template_id)
        if not template:
            return None, f"Template {template_id} not found"

        # Substitute parameters
        specialized_text = template.template_text
        for key, value in parameters.items():
            specialized_text = specialized_text.replace(f"{{{key}}}", value)

        question_id = f"q_{len(self.specialized_questions):04d}"

        question = SpecializedQuestion(
            question_id=question_id,
            template_id=template_id,
            domain=template.domain,
            original_template=template.template_text,
            specialized_text=specialized_text,
            context=context,
            parameters=parameters,
        )

        self.specialized_questions[question_id] = question
        self.specialization_history.append(question)

        return question, None

    def get_domain_overview(self, domain: Domain) -> Dict[str, Any]:
        """Get overview of all templates for a domain."""
        templates = self.get_templates_by_domain(domain)

        categories = {}
        for template in templates:
            if template.category not in categories:
                categories[template.category] = []
            categories[template.category].append(template)

        return {
            "domain": domain.value,
            "total_templates": len(templates),
            "categories": {
                cat: len(templates_list)
                for cat, templates_list in categories.items()
            },
            "templates": [t.to_dict() for t in templates],
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about templates and usage."""
        domains_count = {}
        for template in self.templates.values():
            domain = template.domain.value
            domains_count[domain] = domains_count.get(domain, 0) + 1

        return {
            "total_templates": len(self.templates),
            "total_domains": len(set(t.domain for t in self.templates.values())),
            "by_domain": domains_count,
            "specialized_count": len(self.specialization_history),
        }

    def export_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Export single template."""
        template = self.get_template(template_id)
        if not template:
            return None
        return template.to_dict()

    def export_all_templates(self) -> List[Dict[str, Any]]:
        """Export all templates."""
        return [t.to_dict() for t in self.templates.values()]

    def export_specialized(
        self, question_id: str
    ) -> Optional[Dict[str, Any]]:
        """Export specialized question."""
        question = self.specialized_questions.get(question_id)
        if not question:
            return None
        return question.to_dict()

    def batch_specialize(
        self,
        template_ids: List[str],
        parameter_sets: List[Dict[str, str]],
    ) -> Tuple[List[SpecializedQuestion], Optional[str]]:
        """Specialize multiple templates."""
        if len(template_ids) != len(parameter_sets):
            return [], "Mismatched template and parameter counts"

        questions = []
        for template_id, params in zip(template_ids, parameter_sets):
            question, error = self.specialize_template(template_id, params)
            if question:
                questions.append(question)

        return questions, None
