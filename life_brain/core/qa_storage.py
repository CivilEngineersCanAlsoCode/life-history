"""
Q&A pair storage with rich contextual metadata.

Manages storage and retrieval of question-answer pairs with complete context:
company, project, role, date, source, tags, categories, and confidence scores.
"""

from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class QASource(Enum):
    """Source of Q&A pair."""

    INTERVIEW = "interview"  # Interview or conversation
    DOCUMENTATION = "documentation"  # From docs or guides
    EXPERIENCE = "experience"  # Personal experience/STAR story
    RESEARCH = "research"  # Research or learning
    FEEDBACK = "feedback"  # From feedback or reviews
    BRAINSTORM = "brainstorm"  # Generated or ideated


class QACategory(Enum):
    """Category of Q&A."""

    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SITUATIONAL = "situational"
    KNOWLEDGE = "knowledge"
    SKILL = "skill"
    PROCESS = "process"
    STRATEGY = "strategy"


@dataclass
class ContextMetadata:
    """Context information for Q&A."""

    company: str = ""  # Company name
    project: str = ""  # Project name
    role: str = ""  # Role/position
    date: str = ""  # Date of Q&A
    source_url: str = ""  # URL or source location
    author: str = ""  # Who created this Q&A
    department: str = ""  # Department/team


@dataclass
class QAPair:
    """Question-Answer pair with metadata."""

    qa_id: str
    question: str
    answer: str
    context: ContextMetadata
    source: QASource
    category: QACategory
    tags: List[str] = field(default_factory=list)
    confidence: float = 1.0  # 0-1, confidence in accuracy
    difficulty: float = 0.5  # 0-1, difficulty level
    usefulness: float = 0.5  # 0-1, how useful this is
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "qa_id": self.qa_id,
            "question": self.question,
            "answer": self.answer,
            "company": self.context.company,
            "project": self.context.project,
            "role": self.context.role,
            "date": self.context.date,
            "source": self.source.value,
            "category": self.category.value,
            "tags": self.tags,
            "confidence": self.confidence,
            "difficulty": self.difficulty,
            "usefulness": self.usefulness,
            "created_at": self.created_at,
        }


class QAStorage:
    """Store and manage Q&A pairs."""

    def __init__(self):
        """Initialize Q&A storage."""
        self.qa_pairs: Dict[str, QAPair] = {}
        self.qa_history: List[QAPair] = []
        # Index for fast lookups
        self.by_company: Dict[str, List[str]] = {}  # company -> [qa_ids]
        self.by_project: Dict[str, List[str]] = {}  # project -> [qa_ids]
        self.by_tag: Dict[str, List[str]] = {}  # tag -> [qa_ids]
        self.by_category: Dict[QACategory, List[str]] = {}  # category -> [qa_ids]

    def create_qa_pair(
        self,
        question: str,
        answer: str,
        context: ContextMetadata,
        source: QASource,
        category: QACategory,
        tags: List[str] = None,
        qa_id: str = "",
    ) -> Tuple[Optional[QAPair], Optional[str]]:
        """
        Create and store Q&A pair.

        Args:
            question: The question
            answer: The answer
            context: Contextual metadata
            source: Source of this Q&A
            category: Category of Q&A
            tags: Optional tags
            qa_id: Optional custom QA ID

        Returns:
            (QAPair, error if any)
        """
        if not question or not question.strip():
            return None, "Empty question"

        if not answer or not answer.strip():
            return None, "Empty answer"

        if not qa_id:
            qa_id = f"qa_{len(self.qa_pairs):05d}"

        qa_pair = QAPair(
            qa_id=qa_id,
            question=question,
            answer=answer,
            context=context,
            source=source,
            category=category,
            tags=tags or [],
        )

        self.qa_pairs[qa_id] = qa_pair
        self.qa_history.append(qa_pair)

        # Update indices
        self._update_indices(qa_pair)

        return qa_pair, None

    def _update_indices(self, qa_pair: QAPair) -> None:
        """Update lookup indices."""
        qa_id = qa_pair.qa_id

        if qa_pair.context.company:
            if qa_pair.context.company not in self.by_company:
                self.by_company[qa_pair.context.company] = []
            if qa_id not in self.by_company[qa_pair.context.company]:
                self.by_company[qa_pair.context.company].append(qa_id)

        if qa_pair.context.project:
            if qa_pair.context.project not in self.by_project:
                self.by_project[qa_pair.context.project] = []
            if qa_id not in self.by_project[qa_pair.context.project]:
                self.by_project[qa_pair.context.project].append(qa_id)

        for tag in qa_pair.tags:
            if tag not in self.by_tag:
                self.by_tag[tag] = []
            if qa_id not in self.by_tag[tag]:
                self.by_tag[tag].append(qa_id)

        category = qa_pair.category
        if category not in self.by_category:
            self.by_category[category] = []
        if qa_id not in self.by_category[category]:
            self.by_category[category].append(qa_id)

    def get_qa_pair(self, qa_id: str) -> Optional[QAPair]:
        """Get specific Q&A pair."""
        return self.qa_pairs.get(qa_id)

    def get_by_company(self, company: str) -> List[QAPair]:
        """Get all Q&A pairs for a company."""
        qa_ids = self.by_company.get(company, [])
        return [self.qa_pairs[qa_id] for qa_id in qa_ids if qa_id in self.qa_pairs]

    def get_by_project(self, project: str) -> List[QAPair]:
        """Get all Q&A pairs for a project."""
        qa_ids = self.by_project.get(project, [])
        return [self.qa_pairs[qa_id] for qa_id in qa_ids if qa_id in self.qa_pairs]

    def get_by_tag(self, tag: str) -> List[QAPair]:
        """Get all Q&A pairs with a tag."""
        qa_ids = self.by_tag.get(tag, [])
        return [self.qa_pairs[qa_id] for qa_id in qa_ids if qa_id in self.qa_pairs]

    def get_by_category(self, category: QACategory) -> List[QAPair]:
        """Get all Q&A pairs in a category."""
        qa_ids = self.by_category.get(category, [])
        return [self.qa_pairs[qa_id] for qa_id in qa_ids if qa_id in self.qa_pairs]

    def get_by_source(self, source: QASource) -> List[QAPair]:
        """Get all Q&A pairs from a source."""
        return [qa for qa in self.qa_history if qa.source == source]

    def search_by_keyword(self, keyword: str) -> List[QAPair]:
        """Search Q&A pairs by keyword in question or answer."""
        keyword_lower = keyword.lower()
        results = []
        for qa in self.qa_history:
            if (keyword_lower in qa.question.lower() or
                keyword_lower in qa.answer.lower()):
                results.append(qa)
        return results

    def search_by_context(
        self,
        company: str = "",
        project: str = "",
        role: str = "",
    ) -> List[QAPair]:
        """Search Q&A pairs by context criteria."""
        results = self.qa_history

        if company:
            results = [qa for qa in results if qa.context.company == company]

        if project:
            results = [qa for qa in results if qa.context.project == project]

        if role:
            results = [qa for qa in results if qa.context.role == role]

        return results

    def update_qa_pair(
        self,
        qa_id: str,
        question: Optional[str] = None,
        answer: Optional[str] = None,
        tags: Optional[List[str]] = None,
        usefulness: Optional[float] = None,
    ) -> Tuple[Optional[QAPair], Optional[str]]:
        """Update existing Q&A pair."""
        qa_pair = self.qa_pairs.get(qa_id)
        if not qa_pair:
            return None, f"Q&A pair {qa_id} not found"

        if question:
            qa_pair.question = question

        if answer:
            qa_pair.answer = answer

        if tags is not None:
            qa_pair.tags = tags

        if usefulness is not None:
            qa_pair.usefulness = min(1.0, max(0.0, usefulness))

        qa_pair.updated_at = datetime.now().isoformat()
        qa_pair.version += 1

        return qa_pair, None

    def batch_create(
        self, qa_data: List[Dict[str, Any]]
    ) -> Tuple[List[QAPair], Optional[str]]:
        """Create multiple Q&A pairs."""
        created = []
        for item in qa_data:
            context = ContextMetadata(
                company=item.get("company", ""),
                project=item.get("project", ""),
                role=item.get("role", ""),
                date=item.get("date", ""),
            )
            qa_pair, error = self.create_qa_pair(
                question=item.get("question", ""),
                answer=item.get("answer", ""),
                context=context,
                source=QASource[item.get("source", "RESEARCH").upper()],
                category=QACategory[item.get("category", "KNOWLEDGE").upper()],
                tags=item.get("tags", []),
            )
            if qa_pair:
                created.append(qa_pair)

        return created, None

    def export_qa_pair(self, qa_id: str) -> Optional[Dict[str, Any]]:
        """Export single Q&A pair."""
        qa_pair = self.get_qa_pair(qa_id)
        if not qa_pair:
            return None
        return qa_pair.to_dict()

    def export_all_qa_pairs(self) -> List[Dict[str, Any]]:
        """Export all Q&A pairs."""
        return [qa.to_dict() for qa in self.qa_history]

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about Q&A storage."""
        if not self.qa_history:
            return {
                "total_qa_pairs": 0,
                "by_company": {},
                "by_category": {},
                "by_source": {},
                "avg_confidence": 0.0,
            }

        company_counts = {}
        for company in self.by_company:
            company_counts[company] = len(self.by_company[company])

        category_counts = {}
        for category in self.by_category:
            category_counts[category.value] = len(self.by_category[category])

        source_counts = {}
        for qa in self.qa_history:
            source = qa.source.value
            source_counts[source] = source_counts.get(source, 0) + 1

        avg_confidence = sum(qa.confidence for qa in self.qa_history) / len(self.qa_history)

        return {
            "total_qa_pairs": len(self.qa_history),
            "by_company": company_counts,
            "by_category": category_counts,
            "by_source": source_counts,
            "avg_confidence": avg_confidence,
            "unique_projects": len(self.by_project),
            "unique_tags": len(self.by_tag),
        }

    def get_qa_by_context_tree(self) -> Dict[str, Dict[str, List[str]]]:
        """Get Q&A organized by company -> project."""
        tree = {}
        for qa_id, qa_pair in self.qa_pairs.items():
            company = qa_pair.context.company or "Uncategorized"
            project = qa_pair.context.project or "General"

            if company not in tree:
                tree[company] = {}
            if project not in tree[company]:
                tree[company][project] = []

            tree[company][project].append(qa_id)

        return tree
