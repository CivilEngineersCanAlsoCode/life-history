"""
Adversarial mode for exploring opposing expert perspectives.

Routes questions to experts with opposing viewpoints, exposing trade-offs
and forcing deeper thinking through principled disagreement.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from life_brain.conversation.panel_router import (
    PanelRouter,
    ExpertResponse,
    PanelRole,
    PanelSession,
)
from life_brain.conversation.expert_roster import ExpertDomain


class OpposingPerspective(Enum):
    """Opposing perspective categories."""

    GROWTH_VS_STABILITY = "growth_vs_stability"  # Risk vs Safety
    DETAIL_VS_BIGPICTURE = "detail_vs_bigpicture"  # Deep dive vs Overview
    ACTION_VS_REFLECTION = "action_vs_reflection"  # Do vs Think
    SHORT_TERM_VS_LONG_TERM = "short_term_vs_long_term"  # Now vs Future
    INDIVIDUAL_VS_COLLECTIVE = "individual_vs_collective"  # Self vs Group
    LOGIC_VS_EMOTION = "logic_vs_emotion"  # Rational vs Feelings
    TRADITION_VS_INNOVATION = "tradition_vs_innovation"  # Status quo vs New
    FREEDOM_VS_STRUCTURE = "freedom_vs_structure"  # Autonomy vs Systems


@dataclass
class AdversarialPosition:
    """One side of an adversarial debate."""

    position_name: str  # "Pro", "Con", "Cautious", "Bold", etc.
    experts: List[str]  # Expert names taking this position
    perspective: str  # Description of this perspective
    key_arguments: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "position_name": self.position_name,
            "experts": self.experts,
            "perspective": self.perspective,
            "key_arguments": self.key_arguments,
            "risks": self.risks,
            "benefits": self.benefits,
        }


@dataclass
class AdversarialDebate:
    """Complete adversarial debate with multiple perspectives."""

    session_id: str
    question: str
    perspective_type: OpposingPerspective
    positions: List[AdversarialPosition] = field(default_factory=list)
    responses: Dict[str, ExpertResponse] = field(default_factory=dict)
    synthesis: str = ""
    common_ground: List[str] = field(default_factory=list)
    key_tradeoffs: List[str] = field(default_factory=list)
    recommended_approach: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "question": self.question,
            "perspective_type": self.perspective_type.value,
            "positions": [p.to_dict() for p in self.positions],
            "responses": {k: v.to_dict() for k, v in self.responses.items()},
            "synthesis": self.synthesis,
            "common_ground": self.common_ground,
            "key_tradeoffs": self.key_tradeoffs,
            "recommended_approach": self.recommended_approach,
            "created_at": self.created_at,
        }


class AdversarialMode:
    """Explore questions through opposing expert perspectives."""

    # Opposing expert pairings
    OPPOSING_PAIRS = {
        OpposingPerspective.GROWTH_VS_STABILITY: {
            "growth": ["Jeff", "Naval", "Reed"],  # Scaler, Optioneer, Connector
            "stability": ["Narayana", "Warren", "Andy"],  # Ethical, Value, Systems
        },
        OpposingPerspective.DETAIL_VS_BIGPICTURE: {
            "detail": ["Richard", "Andrew", "Chris"],  # Explainer, Scientist, Negotiator
            "bigpicture": ["Jeff", "Indra", "APJ"],  # Scaler, Strategist, Visionary
        },
        OpposingPerspective.ACTION_VS_REFLECTION: {
            "action": ["Satya", "Jeff", "Reed"],  # Interviewer, Scaler, Connector
            "reflection": ["Sadhguru", "Brené", "Esther"],  # Consciousness, Vulnerability, Relationships
        },
        OpposingPerspective.SHORT_TERM_VS_LONG_TERM: {
            "short_term": ["Chris", "Andy"],  # Negotiator, Systems
            "long_term": ["Warren", "Narayana", "Indra"],  # Value, Ethical, Strategist
        },
        OpposingPerspective.INDIVIDUAL_VS_COLLECTIVE: {
            "individual": ["Naval", "Brené"],  # Optioneer, Vulnerability
            "collective": ["Reed", "Indra", "Andy"],  # Connector, Strategist, Systems
        },
        OpposingPerspective.LOGIC_VS_EMOTION: {
            "logic": ["Richard", "Warren", "Charlie"],  # Explainer, Value, Inverter
            "emotion": ["Esther", "Brené", "Sadhguru"],  # Relationships, Vulnerability, Consciousness
        },
        OpposingPerspective.TRADITION_VS_INNOVATION: {
            "tradition": ["Narayana", "Warren"],  # Ethical, Value
            "innovation": ["Jeff", "Reed", "Naval"],  # Scaler, Connector, Optioneer
        },
        OpposingPerspective.FREEDOM_VS_STRUCTURE: {
            "freedom": ["Naval", "Brené"],  # Optioneer, Vulnerability
            "structure": ["Andy", "Narayana"],  # Systems, Ethical
        },
    }

    def __init__(self, panel_router: Optional[PanelRouter] = None):
        """Initialize adversarial mode."""
        self.router = panel_router or PanelRouter()
        self.debates: Dict[str, AdversarialDebate] = {}
        self.debate_history: List[AdversarialDebate] = []

    def debate_question(
        self,
        session_id: str,
        question: str,
        perspective_type: OpposingPerspective = OpposingPerspective.GROWTH_VS_STABILITY,
        context: str = "",
    ) -> Tuple[AdversarialDebate, Optional[str]]:
        """
        Debate question through opposing perspectives.

        Args:
            session_id: Unique session ID
            question: Question to debate
            perspective_type: Type of opposing perspectives
            context: Additional context

        Returns:
            (AdversarialDebate, error if any)
        """
        if not question or not question.strip():
            return None, "Empty question"

        if perspective_type not in self.OPPOSING_PAIRS:
            return None, f"Unknown perspective type: {perspective_type}"

        # Get opposing experts
        pair_info = self.OPPOSING_PAIRS[perspective_type]

        # Create debate object
        debate = AdversarialDebate(
            session_id=session_id,
            question=question,
            perspective_type=perspective_type,
        )

        # Create positions
        for position_name, expert_names in pair_info.items():
            position = AdversarialPosition(
                position_name=position_name.replace("_", " ").title(),
                experts=expert_names,
                perspective=f"The {position_name.replace('_', ' ')} perspective",
            )
            debate.positions.append(position)

        # Get responses from each expert
        all_experts = []
        for pos in debate.positions:
            all_experts.extend(pos.experts[:2])  # Take top 2 from each side

        # Route to panel to get responses
        panel_session, error = self.router.panel_router(
            session_id=session_id,
            question_text=question,
            expert_names=all_experts,
            context=context,
            category="adversarial",
        )

        if error:
            return None, error

        # Extract responses
        debate.responses = panel_session.responses

        # Analyze debate
        self._analyze_debate(debate)

        # Store
        self.debates[session_id] = debate
        self.debate_history.append(debate)

        return debate, None

    def _analyze_debate(self, debate: AdversarialDebate) -> None:
        """Analyze debate for synthesis, tradeoffs, common ground."""
        if not debate.responses:
            return

        # Extract positions from responses
        for position in debate.positions:
            position.key_arguments = self._extract_arguments(
                debate.responses, position.experts
            )
            position.risks = self._extract_risks(debate.responses, position.experts)
            position.benefits = self._extract_benefits(
                debate.responses, position.experts
            )

        # Find common ground
        all_insights = []
        for resp in debate.responses.values():
            all_insights.extend(resp.key_insights)

        # Common insights
        insight_counts = {}
        for insight in all_insights:
            insight_counts[insight] = insight_counts.get(insight, 0) + 1

        debate.common_ground = [
            insight for insight, count in insight_counts.items() if count > 1
        ]

        # Identify key tradeoffs
        debate.key_tradeoffs = self._extract_tradeoffs(debate)

        # Synthesize
        debate.synthesis = self._synthesize_perspectives(debate)

        # Recommend approach
        debate.recommended_approach = self._recommend_approach(debate)

    def _extract_arguments(
        self, responses: Dict[str, ExpertResponse], expert_names: List[str]
    ) -> List[str]:
        """Extract key arguments from expert side."""
        arguments = []

        for name in expert_names:
            if name in responses:
                arguments.extend(responses[name].key_insights[:2])

        return list(set(arguments))  # Remove duplicates

    def _extract_risks(
        self, responses: Dict[str, ExpertResponse], expert_names: List[str]
    ) -> List[str]:
        """Extract risks mentioned by experts."""
        risks = []

        for name in expert_names:
            if name in responses:
                # Simulate risk extraction
                resp = responses[name]
                if "risk" in resp.response_text.lower() or "danger" in resp.response_text.lower():
                    risks.extend(resp.key_insights)

        return list(set(risks))

    def _extract_benefits(
        self, responses: Dict[str, ExpertResponse], expert_names: List[str]
    ) -> List[str]:
        """Extract benefits mentioned by experts."""
        benefits = []

        for name in expert_names:
            if name in responses:
                resp = responses[name]
                if "benefit" in resp.response_text.lower() or "advantage" in resp.response_text.lower():
                    benefits.extend(resp.key_insights)

        return list(set(benefits))

    def _extract_tradeoffs(self, debate: AdversarialDebate) -> List[str]:
        """Extract key tradeoffs between positions."""
        tradeoffs = []

        if len(debate.positions) >= 2:
            pos1_benefits = debate.positions[0].benefits
            pos2_benefits = debate.positions[1].benefits

            pos1_risks = debate.positions[0].risks
            pos2_risks = debate.positions[1].risks

            # Tradeoff: what one gains, other might lose
            if pos1_benefits and pos2_risks:
                tradeoffs.append(
                    f"{debate.positions[0].position_name} gains {pos1_benefits[0] if pos1_benefits else 'advantages'} but risks {pos2_risks[0] if pos2_risks else 'downsides'}"
                )

        return tradeoffs

    def _synthesize_perspectives(self, debate: AdversarialDebate) -> str:
        """Synthesize opposing perspectives."""
        if len(debate.positions) < 2:
            return "Single perspective identified."

        pos1 = debate.positions[0].position_name
        pos2 = debate.positions[1].position_name

        synthesis = f"{pos1} and {pos2} perspectives offer complementary insights. "
        synthesis += f"Neither is purely right - the optimal path likely requires elements of both. "
        synthesis += f"The key is understanding when each applies."

        return synthesis

    def _recommend_approach(self, debate: AdversarialDebate) -> str:
        """Recommend balanced approach."""
        if not debate.common_ground:
            return "Consider hybrid approach incorporating both perspectives' strengths."

        common = debate.common_ground[0] if debate.common_ground else "core principle"
        recommendation = f"Start from the common ground: {common}. "
        recommendation += f"Then apply context-specific judgment on which perspective to emphasize."

        return recommendation

    def get_debate(self, session_id: str) -> Optional[AdversarialDebate]:
        """Get specific debate."""
        return self.debates.get(session_id)

    def export_debate(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export debate."""
        debate = self.debates.get(session_id)
        if not debate:
            return None
        return debate.to_dict()

    def export_all_debates(self) -> List[Dict[str, Any]]:
        """Export all debates."""
        return [d.to_dict() for d in self.debate_history]

    def get_debate_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get debate summary."""
        debate = self.debates.get(session_id)
        if not debate:
            return None

        return {
            "session_id": session_id,
            "question": debate.question,
            "perspective_type": debate.perspective_type.value,
            "position_count": len(debate.positions),
            "expert_count": sum(len(p.experts) for p in debate.positions),
            "common_ground": debate.common_ground,
            "key_tradeoffs": debate.key_tradeoffs,
            "synthesis": debate.synthesis,
        }

    def get_debate_statistics(self) -> Dict[str, Any]:
        """Get statistics about debates."""
        if not self.debate_history:
            return {
                "total_debates": 0,
                "by_perspective": {},
                "avg_positions": 0,
                "avg_common_ground": 0,
            }

        by_perspective = {}
        total_positions = 0
        total_common_ground = 0

        for debate in self.debate_history:
            persp = debate.perspective_type.value
            by_perspective[persp] = by_perspective.get(persp, 0) + 1
            total_positions += len(debate.positions)
            total_common_ground += len(debate.common_ground)

        return {
            "total_debates": len(self.debate_history),
            "by_perspective": by_perspective,
            "avg_positions": (
                total_positions / len(self.debate_history)
                if self.debate_history
                else 0
            ),
            "avg_common_ground": (
                total_common_ground / len(self.debate_history)
                if self.debate_history
                else 0
            ),
        }

    def compare_positions(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Compare positions in a debate."""
        debate = self.debates.get(session_id)
        if not debate or len(debate.positions) < 2:
            return None

        pos1 = debate.positions[0]
        pos2 = debate.positions[1]

        return {
            "position1": pos1.position_name,
            "position2": pos2.position_name,
            "arguments1": pos1.key_arguments,
            "arguments2": pos2.key_arguments,
            "risks1": pos1.risks,
            "risks2": pos2.risks,
            "benefits1": pos1.benefits,
            "benefits2": pos2.benefits,
            "common_ground": debate.common_ground,
            "tradeoffs": debate.key_tradeoffs,
        }
