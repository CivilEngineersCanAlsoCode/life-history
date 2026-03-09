"""
Multi-Expert Consensus Resolution Framework.

When two experts disagree, generates a context-based resolution that empowers
the user to decide rather than leaving them in paralysis.

Format:
  'Dono valid hain — alag alag contexts ke liye.
   [Expert A] sahi hai agar: [condition A optimal]
   [Expert B] sahi hai agar: [condition B optimal]
   Tumhari situation mein: [follow-up question]'
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import re
import logging

logger = logging.getLogger(__name__)


# Keywords that indicate opposing positions
OPPOSING_KEYWORDS = {
    "action": ["quit", "leave", "start", "build", "risk", "invest", "go all-in"],
    "caution": ["stay", "keep", "protect", "safe", "don't risk", "never risk", "conservative"],
    "positive": ["yes", "absolutely", "definitely", "always", "strong", "great", "excellent"],
    "negative": ["no", "never", "avoid", "risky", "dangerous", "terrible", "bad"],
}


@dataclass
class ExpertPosition:
    """Extracted position from an expert response."""

    expert_name: str
    stance: str          # "action" | "caution" | "positive" | "negative" | "neutral"
    key_recommendation: str   # Core recommendation in 1 sentence
    conditions: List[str] = field(default_factory=list)   # When this advice is best
    response_text: str = ""


@dataclass
class ConsensusResolution:
    """Consensus resolution output for user."""

    expert_a: str
    expert_b: str
    condition_a: str    # When Expert A is right
    condition_b: str    # When Expert B is right
    follow_up_question: str  # Question to identify user's situation
    resolution_text: str    # Full Hinglish formatted resolution

    def to_dict(self) -> Dict[str, Any]:
        return {
            "expert_a": self.expert_a,
            "expert_b": self.expert_b,
            "condition_a": self.condition_a,
            "condition_b": self.condition_b,
            "follow_up_question": self.follow_up_question,
            "resolution_text": self.resolution_text,
        }


class ConsensusResolver:
    """Detects expert disagreement and generates context-based resolutions."""

    def detect_disagreement(
        self,
        response_a: str,
        response_b: str,
    ) -> bool:
        """
        Detect if two expert responses are in genuine disagreement.

        Args:
            response_a: First expert's response text
            response_b: Second expert's response text

        Returns:
            True if responses appear to recommend opposing actions
        """
        if not response_a or not response_b:
            return False

        a_lower = response_a.lower()
        b_lower = response_b.lower()

        # Check for opposing stance keywords
        a_action = any(kw in a_lower for kw in OPPOSING_KEYWORDS["action"])
        a_caution = any(kw in a_lower for kw in OPPOSING_KEYWORDS["caution"])
        b_action = any(kw in b_lower for kw in OPPOSING_KEYWORDS["action"])
        b_caution = any(kw in b_lower for kw in OPPOSING_KEYWORDS["caution"])

        # Disagreement: A is action-oriented, B is cautious (or vice versa)
        if (a_action and b_caution) or (a_caution and b_action):
            return True

        # Check positive vs negative stance
        a_positive = any(kw in a_lower for kw in OPPOSING_KEYWORDS["positive"])
        b_negative = any(kw in b_lower for kw in OPPOSING_KEYWORDS["negative"])
        b_positive = any(kw in b_lower for kw in OPPOSING_KEYWORDS["positive"])
        a_negative = any(kw in a_lower for kw in OPPOSING_KEYWORDS["negative"])

        if (a_positive and b_negative) or (a_negative and b_positive):
            return True

        return False

    def extract_position(self, expert_name: str, response_text: str) -> ExpertPosition:
        """
        Extract core position from expert response.

        Args:
            expert_name: Expert's name
            response_text: Expert's response

        Returns:
            ExpertPosition with stance and key recommendation
        """
        if not response_text:
            return ExpertPosition(
                expert_name=expert_name,
                stance="neutral",
                key_recommendation="No clear recommendation.",
            )

        lower = response_text.lower()

        # Determine stance
        action_score = sum(1 for kw in OPPOSING_KEYWORDS["action"] if kw in lower)
        caution_score = sum(1 for kw in OPPOSING_KEYWORDS["caution"] if kw in lower)
        positive_score = sum(1 for kw in OPPOSING_KEYWORDS["positive"] if kw in lower)
        negative_score = sum(1 for kw in OPPOSING_KEYWORDS["negative"] if kw in lower)

        if action_score > caution_score:
            stance = "action"
        elif caution_score > action_score:
            stance = "caution"
        elif positive_score > negative_score:
            stance = "positive"
        elif negative_score > positive_score:
            stance = "negative"
        else:
            stance = "neutral"

        # Extract key recommendation: first sentence
        sentences = re.split(r"[.!?]", response_text)
        key_rec = sentences[0].strip() if sentences else response_text[:100]

        return ExpertPosition(
            expert_name=expert_name,
            stance=stance,
            key_recommendation=key_rec or response_text[:100],
            response_text=response_text,
        )

    def generate_resolution(
        self,
        expert_a_name: str,
        expert_a_response: str,
        expert_b_name: str,
        expert_b_response: str,
        context: str = "",
    ) -> ConsensusResolution:
        """
        Generate context-based consensus resolution.

        Args:
            expert_a_name: First expert's name
            expert_a_response: First expert's response
            expert_b_name: Second expert's name
            expert_b_response: Second expert's response
            context: Topic/question context

        Returns:
            ConsensusResolution with formatted Hinglish output
        """
        pos_a = self.extract_position(expert_a_name, expert_a_response)
        pos_b = self.extract_position(expert_b_name, expert_b_response)

        # Generate conditions based on stances
        condition_a, condition_b = self._generate_conditions(pos_a, pos_b, context)
        follow_up = self._generate_follow_up(pos_a, pos_b, context)

        resolution_text = f"""Dono valid hain — alag alag contexts ke liye.

**{expert_a_name}** sahi hai agar: {condition_a}

**{expert_b_name}** sahi hai agar: {condition_b}

Tumhari situation mein: {follow_up}"""

        return ConsensusResolution(
            expert_a=expert_a_name,
            expert_b=expert_b_name,
            condition_a=condition_a,
            condition_b=condition_b,
            follow_up_question=follow_up,
            resolution_text=resolution_text.strip(),
        )

    def _generate_conditions(
        self,
        pos_a: ExpertPosition,
        pos_b: ExpertPosition,
        context: str,
    ) -> Tuple[str, str]:
        """Generate when-is-each-expert-right conditions."""
        # Action vs Caution pattern
        if pos_a.stance == "action" and pos_b.stance == "caution":
            return (
                "tumhare paas strong runway hai, backup plan clear hai, aur calculated risk uthane ki capacity hai",
                "current situation mein stability zyada zaroori hai, dependents hain, ya safety net weak hai",
            )
        elif pos_a.stance == "caution" and pos_b.stance == "action":
            return (
                "abhi stability zyada zaroori hai — resources limited hain, dependencies hain",
                "tumhare paas resources aur conviction dono hain — high-risk high-reward moment hai",
            )
        elif pos_a.stance == "positive" and pos_b.stance == "negative":
            return (
                "context aur conditions tumhare favor mein hain — strong fundamentals hain",
                "risks clearly outweigh benefits hain, ya timing sahi nahi hai",
            )
        elif pos_a.stance == "negative" and pos_b.stance == "positive":
            return (
                "current execution ya timing mein issues hain jo pehle fix karne chahiye",
                "tumne risks properly assess kar liye hain aur upside clearly better hai",
            )
        else:
            return (
                f"tumhara specific situation {pos_a.key_recommendation[:50]} wali direction mein hai",
                f"tumhara specific situation {pos_b.key_recommendation[:50]} wali direction mein fit karta hai",
            )

    def _generate_follow_up(
        self,
        pos_a: ExpertPosition,
        pos_b: ExpertPosition,
        context: str,
    ) -> str:
        """Generate a follow-up question to identify user's situation."""
        if pos_a.stance in ("action", "positive") or pos_b.stance in ("action", "positive"):
            return "Abhi tumhare paas runway kitna hai — financially aur emotionally? 6 months se zyada ya kam?"
        elif pos_a.stance in ("caution", "negative") or pos_b.stance in ("caution", "negative"):
            return "Is decision mein sabse bada risk kya hai jo tumhe rok raha hai? Concrete ho sake toh batao."
        else:
            return "Tumhari current situation mein sabse important constraint kya hai — time, money, ya energy?"

    def format_no_disagreement_message(
        self,
        expert_a_name: str,
        expert_b_name: str,
    ) -> str:
        """Message when experts actually agree."""
        return (
            f"Interesting — **{expert_a_name}** aur **{expert_b_name}** dono ek hi direction mein soch rahe hain. "
            f"Is alignment ko seriously lo — jab do alag experts agree karein toh usually signal strong hota hai."
        )
