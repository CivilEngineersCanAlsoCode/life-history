"""
Completeness and Excellence (CE) check for query-response validation.

Validates that responses fully address the original query by:
- Analyzing query intent and expected coverage
- Identifying missing concepts from the original query
- Scoring response completeness (0.0-1.0)
- Tracking what information is absent
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re


class CompletenessLevel(Enum):
    """Completeness scoring levels."""

    INCOMPLETE = "incomplete"  # <0.5: missing major components
    PARTIAL = "partial"  # 0.5-0.75: covers most but misses some aspects
    SUBSTANTIAL = "substantial"  # 0.75-0.9: very complete, minor gaps
    COMPLETE = "complete"  # >0.9: fully addresses query


@dataclass
class MissingComponent:
    """Tracked missing element from query."""

    component_type: str  # "concept", "example", "detail", "clarification"
    description: str  # What's missing
    priority: int  # 1-5, 5=critical
    relevance_score: float  # 0-1, how important to the query
    found_in_response: bool = False


@dataclass
class CompletenessCheck:
    """Completeness check result."""

    check_id: str
    query: str
    response: str
    completeness_score: float  # 0-1
    completeness_level: CompletenessLevel
    missing_components: List[MissingComponent] = field(default_factory=list)
    coverage_areas: Dict[str, float] = field(default_factory=dict)  # Area -> coverage %
    suggestions: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "check_id": self.check_id,
            "query": self.query,
            "response": self.response,
            "completeness_score": self.completeness_score,
            "completeness_level": self.completeness_level.value,
            "missing_components": [
                {
                    "component_type": m.component_type,
                    "description": m.description,
                    "priority": m.priority,
                    "relevance_score": m.relevance_score,
                    "found_in_response": m.found_in_response,
                }
                for m in self.missing_components
            ],
            "coverage_areas": self.coverage_areas,
            "suggestions": self.suggestions,
            "created_at": self.created_at,
        }


class CompletenessValidator:
    """Validate query-response completeness."""

    # Key question indicators in queries
    QUESTION_TYPES = {
        "what": ["what", "which", "what's", "what is"],
        "why": ["why", "reason", "cause", "because"],
        "how": ["how", "way", "method", "approach"],
        "when": ["when", "time", "schedule", "timing"],
        "where": ["where", "location", "place", "site"],
        "who": ["who", "person", "people", "person"],
        "how_much": ["how much", "amount", "quantity", "number"],
        "decision": ["should", "decide", "choice", "option"],
    }

    # Expected response components
    RESPONSE_COMPONENTS = {
        "direct_answer": ["yes", "no", "true", "false"],
        "explanation": ["because", "reason", "since", "due to"],
        "evidence": ["example", "evidence", "data", "research"],
        "detail": ["specifically", "specifically", "detail", "particular"],
        "context": ["context", "background", "situation", "scenario"],
        "recommendation": ["recommend", "suggest", "advise", "propose"],
    }

    def __init__(self):
        """Initialize completeness validator."""
        self.checks: Dict[str, CompletenessCheck] = {}
        self.check_history: List[CompletenessCheck] = []

    def check_completeness(
        self,
        query: str,
        response: str,
        check_id: str = "",
    ) -> Tuple[Optional[CompletenessCheck], Optional[str]]:
        """
        Check if response fully addresses query.

        Args:
            query: Original question/query
            response: Response to validate
            check_id: Optional check ID

        Returns:
            (CompletenessCheck, error if any)
        """
        if not query or not query.strip():
            return None, "Empty query"

        if not response or not response.strip():
            return None, "Empty response"

        if not check_id:
            check_id = f"ce_{len(self.checks):04d}"

        # Analyze query intent
        query_intent = self._analyze_query_intent(query)

        # Extract response components
        response_components = self._extract_response_components(response)

        # Identify missing components
        missing = self._identify_missing_components(
            query, response, query_intent, response_components
        )

        # Calculate coverage areas
        coverage_areas = self._calculate_coverage_areas(
            query_intent, response_components
        )

        # Calculate completeness score
        completeness_score = self._calculate_completeness_score(
            missing, coverage_areas, response
        )

        # Determine completeness level
        completeness_level = self._determine_completeness_level(completeness_score)

        # Generate suggestions
        suggestions = self._generate_suggestions(missing, coverage_areas)

        check = CompletenessCheck(
            check_id=check_id,
            query=query,
            response=response,
            completeness_score=completeness_score,
            completeness_level=completeness_level,
            missing_components=missing,
            coverage_areas=coverage_areas,
            suggestions=suggestions,
        )

        self.checks[check_id] = check
        self.check_history.append(check)

        return check, None

    def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze what the query is asking for."""
        query_lower = query.lower()
        intent = {
            "question_types": [],
            "key_terms": [],
            "expected_components": [],
            "complexity": "simple",
        }

        # Identify question types
        for qtype, keywords in self.QUESTION_TYPES.items():
            if any(kw in query_lower for kw in keywords):
                intent["question_types"].append(qtype)

        # Extract key terms (4+ chars, not stop words)
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at",
            "to", "for", "of", "with", "by", "from", "is", "are", "be",
            "do", "does", "did", "can", "could", "would", "should",
        }
        words = re.findall(r"\b\w+\b", query_lower)
        intent["key_terms"] = [
            w for w in words if w not in stop_words and len(w) > 3
        ][:8]

        # Determine expected components
        if "why" in intent["question_types"]:
            intent["expected_components"].extend(["explanation", "evidence"])
        if "how" in intent["question_types"]:
            intent["expected_components"].extend(["detail", "recommendation"])
        if "what" in intent["question_types"]:
            intent["expected_components"].extend(["direct_answer", "explanation"])

        # Assess complexity
        if len(intent["question_types"]) > 1 or len(intent["key_terms"]) > 5:
            intent["complexity"] = "complex"

        return intent

    def _extract_response_components(self, response: str) -> Dict[str, List[str]]:
        """Extract components present in response."""
        response_lower = response.lower()
        components = {comp: [] for comp in self.RESPONSE_COMPONENTS.keys()}

        # Check for each component type
        for comp_type, keywords in self.RESPONSE_COMPONENTS.items():
            found = []
            for keyword in keywords:
                if keyword in response_lower:
                    found.append(keyword)
            if found:
                components[comp_type] = found

        # If response has substantial content without explicit markers, mark as present
        if len(response) > 150:
            # Mark explanation as present if not already
            if not components["explanation"]:
                components["explanation"] = ["implicit"]
            # Mark detail as present if not already
            if not components["detail"]:
                components["detail"] = ["implicit"]

        return components

    def _identify_missing_components(
        self,
        query: str,
        response: str,
        query_intent: Dict[str, Any],
        response_components: Dict[str, List[str]],
    ) -> List[MissingComponent]:
        """Identify what's missing from the response."""
        missing = []
        query_lower = query.lower()
        response_lower = response.lower()

        # Only flag critical missing components for pure decision questions
        # "how should" is a "how" question, not a decision
        # Only "should i" or "should we" without "how" are decision questions
        question_types = query_intent.get("question_types", [])
        is_pure_decision = (
            "decision" in question_types
            and "how" not in question_types
            and "what" not in question_types
        )

        if is_pure_decision:
            if not response_components.get("direct_answer"):
                missing.append(
                    MissingComponent(
                        component_type="direct_answer",
                        description="Missing yes/no or clear decision",
                        priority=5,
                        relevance_score=0.9,
                    )
                )

        # Check for key term coverage only if many key terms expected
        key_terms = query_intent.get("key_terms", [])
        if len(key_terms) >= 4:  # Only for complex queries
            covered_terms = sum(1 for term in key_terms if term in response_lower)
            if covered_terms < len(key_terms) * 0.5:  # Less than 50% coverage
                missing.append(
                    MissingComponent(
                        component_type="concept",
                        description=f"Only {covered_terms}/{len(key_terms)} key concepts addressed",
                        priority=2,
                        relevance_score=0.5,
                    )
                )

        # Check for extreme brevity
        if len(response.strip()) < 50:  # Very short response
            missing.append(
                MissingComponent(
                    component_type="detail",
                    description="Response is too brief",
                    priority=3,
                    relevance_score=0.6,
                )
            )

        # Check for excessive vagueness
        vague_terms = ["maybe", "perhaps", "might", "could be", "possibly", "probably"]
        vague_count = sum(response_lower.count(term) for term in vague_terms)
        if vague_count > 3:  # More than 3 vague terms
            missing.append(
                MissingComponent(
                    component_type="clarification",
                    description="Response contains excessive uncertainty/vagueness",
                    priority=2,
                    relevance_score=0.4,
                )
            )

        return missing

    def _calculate_coverage_areas(
        self, query_intent: Dict[str, Any], response_components: Dict[str, List[str]]
    ) -> Dict[str, float]:
        """Calculate coverage for each area."""
        coverage = {}

        # Component coverage - only for components that are actually expected
        components_expected = query_intent.get("expected_components", [])
        if len(components_expected) > 0:
            components_found = sum(
                1
                for comp in components_expected
                if response_components.get(comp)
            )
            coverage["components"] = (
                components_found / len(components_expected)
                if len(components_expected) > 0
                else 1.0
            )
        else:
            coverage["components"] = 1.0  # If no components expected, full coverage

        # Question type handling
        question_types = query_intent.get("question_types", [])
        if len(question_types) > 0:
            coverage["question_types"] = min(1.0, len(question_types) / 3)
        else:
            coverage["question_types"] = 0.8  # Default if no question type detected

        # Overall presence of any substantial response
        components_present = sum(1 for v in response_components.values() if v)
        coverage["response_substance"] = min(
            1.0, components_present / 3
        )  # Expecting at least 3 types

        return coverage

    def _calculate_completeness_score(
        self, missing: List[MissingComponent], coverage_areas: Dict[str, float], response: str
    ) -> float:
        """Calculate overall completeness score (0-1)."""
        # Start with response length baseline
        response_length = len(response.strip())
        if response_length < 50:
            base_score = 0.3
        elif response_length < 100:
            base_score = 0.5
        elif response_length < 200:
            base_score = 0.7
        else:
            base_score = 0.85

        # Critical missing components (priority 5) are heavily penalized
        critical_missing = [m for m in missing if m.priority >= 5]
        for component in critical_missing:
            base_score -= 0.2

        # Other missing components have smaller impact
        other_missing = [m for m in missing if m.priority < 5]
        for component in other_missing:
            deduction = (component.priority / 5.0) * 0.05  # Max 0.05 per component
            base_score -= deduction

        # Adjust by coverage areas (gentler adjustment)
        if coverage_areas:
            avg_coverage = sum(coverage_areas.values()) / len(coverage_areas)
            base_score += (avg_coverage - 1.0) * 0.1  # Small adjustment

        # Bonus for addressing multiple aspects
        if len(missing) == 0 and response_length > 150:
            base_score = min(1.0, base_score + 0.1)

        return max(0.0, min(1.0, base_score))

    def _determine_completeness_level(self, score: float) -> CompletenessLevel:
        """Map score to completeness level."""
        if score < 0.5:
            return CompletenessLevel.INCOMPLETE
        elif score < 0.75:
            return CompletenessLevel.PARTIAL
        elif score < 0.9:
            return CompletenessLevel.SUBSTANTIAL
        else:
            return CompletenessLevel.COMPLETE

    def _generate_suggestions(
        self, missing: List[MissingComponent], coverage_areas: Dict[str, float]
    ) -> List[str]:
        """Generate suggestions for improvement."""
        suggestions = []

        # Prioritize by criticality
        critical_missing = [m for m in missing if m.priority >= 4]
        if critical_missing:
            for m in critical_missing:
                suggestions.append(f"Add {m.description.lower()}")

        # Coverage feedback
        weak_areas = [
            area for area, coverage in coverage_areas.items() if coverage < 0.7
        ]
        if weak_areas:
            suggestions.append(
                f"Improve coverage in: {', '.join(weak_areas)}"
            )

        # General improvements
        if len(missing) > 3:
            suggestions.append("Provide more comprehensive coverage of all query aspects")
        elif len(missing) > 0:
            suggestions.append("Address remaining gaps for a complete response")

        return suggestions

    def get_check(self, check_id: str) -> Optional[CompletenessCheck]:
        """Get specific completeness check."""
        return self.checks.get(check_id)

    def get_checks_by_level(
        self, level: CompletenessLevel
    ) -> List[CompletenessCheck]:
        """Get all checks at a specific completeness level."""
        return [
            check
            for check in self.check_history
            if check.completeness_level == level
        ]

    def batch_check(
        self, query_response_pairs: List[Tuple[str, str]]
    ) -> Tuple[List[CompletenessCheck], Optional[str]]:
        """Check completeness for multiple query-response pairs."""
        checks = []
        for query, response in query_response_pairs:
            check, error = self.check_completeness(query, response)
            if check:
                checks.append(check)
        return checks, None

    def export_check(self, check_id: str) -> Optional[Dict[str, Any]]:
        """Export single check."""
        check = self.get_check(check_id)
        if not check:
            return None
        return check.to_dict()

    def export_all_checks(self) -> List[Dict[str, Any]]:
        """Export all checks."""
        return [check.to_dict() for check in self.check_history]

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about completeness checks."""
        if not self.check_history:
            return {
                "total_checks": 0,
                "avg_completeness": 0.0,
                "by_level": {},
                "common_missing": [],
            }

        total_completeness = sum(c.completeness_score for c in self.check_history)
        avg_completeness = (
            total_completeness / len(self.check_history)
            if self.check_history
            else 0.0
        )

        # Count by level
        by_level = {}
        for level in CompletenessLevel:
            count = sum(
                1 for c in self.check_history if c.completeness_level == level
            )
            by_level[level.value] = count

        # Most common missing components
        all_missing = []
        for check in self.check_history:
            all_missing.extend([m.component_type for m in check.missing_components])
        common_missing = list(
            set(all_missing)
        ) if all_missing else []

        return {
            "total_checks": len(self.check_history),
            "avg_completeness": avg_completeness,
            "by_level": by_level,
            "common_missing": common_missing,
        }
