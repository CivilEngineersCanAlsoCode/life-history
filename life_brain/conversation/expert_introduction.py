"""
Expert Introduction Protocol — Introduce experts with context and privacy.

Implements:
- Expert bio and credibility establishment
- Privacy firewall enforcement
- Introduction approval flow
- Hinglish conversation styling
"""

from typing import Dict, Any, Optional, Tuple
import logging

from life_brain.conversation.experts import get_expert, query_with_privacy_firewall
from life_brain.conversation.use_cases import get_use_case

logger = logging.getLogger(__name__)


class ExpertIntroducer:
    """Manages expert introduction and approval flows."""

    def __init__(self):
        pass

    def format_expert_introduction(
        self,
        expert_name: str,
        use_case_id: Optional[str] = None,
        context: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Format expert introduction for user.

        Args:
            expert_name: Expert key (e.g., 'satya_nadella')
            use_case_id: Use case context (e.g., 'C1')
            context: Additional context

        Returns:
            Tuple of (introduction_text, expert_dict)
        """
        expert = get_expert(expert_name)
        if not expert:
            return f"Expert '{expert_name}' ka profile available nahi hai.", {}

        real_name = expert.get("real_name", expert_name)
        role = expert.get("role", "Expert")
        tone = expert.get("tone", "thoughtful")
        opener = expert.get("opener", "Let's begin.")

        # Build introduction
        intro = f"""Shukriya! Main tumhe {real_name} se introduce karte hoon.

**{real_name}** — {role}
Tone: {tone}

{real_name} is baare mein sochte hain:
"""

        # Add context about this person
        signature_stories = expert.get("signature_stories", [])
        if signature_stories:
            intro += f"\n📖 Famous kai: {signature_stories[0]}\n"

        intro += f"""
---

"{opener}"

---

Kya main aage badh jau?"""

        logger.info(f"Formatted introduction for {real_name}")
        return (intro, expert)

    def format_expert_approval_prompt(
        self,
        expert_name: str,
        use_case_id: Optional[str] = None
    ) -> str:
        """
        Format approval prompt for expert.

        Returns:
            Hinglish approval prompt
        """
        expert = get_expert(expert_name)
        if not expert:
            raise ValueError(f"Unknown expert: {expert_name}")

        real_name = expert.get("real_name", expert_name)

        prompt = f"""Kya {real_name} sahi hain is topic ke liye?

[Haan] — Bilkul, introduction do
[Nahi] — Kohaaz expert chahiye
[Khud] — Mujhe guide karo (without expert)"""

        return prompt.strip()

    def get_expert_specific_questions(
        self,
        expert_name: str,
        use_case_id: str
    ) -> list:
        """
        Get opening questions from expert's style.

        Args:
            expert_name: Expert key
            use_case_id: Use case for context

        Returns:
            List of expert-specific opening questions
        """
        expert = get_expert(expert_name)
        use_case = get_use_case(use_case_id)

        if not expert or not use_case:
            return []

        questions = []

        # Add expert's signature opener
        opener = expert.get("opener")
        if opener:
            questions.append(opener)

        # Add depth trigger as second question
        depth_trigger = expert.get("depth_trigger")
        if depth_trigger:
            questions.append(depth_trigger)

        # Add use case questions if available
        use_case_questions = use_case.get("questions", [])
        if isinstance(use_case_questions, list):
            questions.extend(use_case_questions[:3])
        else:
            questions.append(use_case_questions)

        logger.debug(f"Prepared {len(questions)} questions for {expert_name}")
        return questions

    def enforce_privacy_firewall(
        self,
        expert_name: str,
        query: str,
        available_data: list
    ) -> list:
        """
        Filter data to only what expert can see.

        Args:
            expert_name: Expert key
            query: User query
            available_data: All retrieved data

        Returns:
            Filtered data only for this expert's domains
        """
        filtered = query_with_privacy_firewall(
            expert_name=expert_name,
            query=query,
            available_data=available_data
        )

        logger.debug(f"Privacy firewall applied for {expert_name}: {len(available_data)} → {len(filtered)} items")
        return filtered

    def get_expert_vocabulary(self, expert_name: str) -> list:
        """
        Get expert's signature vocabulary for response styling.

        Args:
            expert_name: Expert key

        Returns:
            List of vocabulary words this expert uses
        """
        expert = get_expert(expert_name)
        if not expert:
            return []

        return expert.get("vocabulary", [])

    def format_expert_response_style(
        self,
        expert_name: str,
        response_text: str
    ) -> str:
        """
        Style response according to expert's tone.

        Args:
            expert_name: Expert key
            response_text: Base response text

        Returns:
            Styled response
        """
        expert = get_expert(expert_name)
        if not expert:
            return response_text

        tone = expert.get("tone", "thoughtful").lower()
        real_name = expert.get("real_name", "Expert")

        # Add expert signature based on tone
        if "empathetic" in tone:
            response_text += "\n\n— Samajhta hun teri feeling ko."
        elif "direct" in tone:
            response_text += "\n\n— Seedha sach: ye important hai."
        elif "wise" in tone or "acerbic" in tone:
            response_text += "\n\n— Socho is baare mein."
        elif "scientific" in tone:
            response_text += "\n\n— Evidence ke basis pe dekhte hain."
        elif "strategic" in tone:
            response_text += "\n\n— Long-term mein socho."

        return response_text.strip()

    def format_expert_intro_and_first_question(
        self,
        expert_name: str,
        use_case_id: str
    ) -> str:
        """
        All-in-one: Format expert intro + first question.

        Args:
            expert_name: Expert key
            use_case_id: Use case

        Returns:
            Complete intro + first question in Hinglish
        """
        expert = get_expert(expert_name)
        use_case = get_use_case(use_case_id)

        if not expert or not use_case:
            raise ValueError("Invalid expert or use case")

        real_name = expert.get("real_name")
        role = expert.get("role")
        opener = expert.get("opener")
        use_case_title = use_case.get("title", "Conversation")

        message = f"""🎤 **{real_name}** tumhare samne {use_case_title} ke liye.

**Role**: {role}
**Specialty**: {use_case_title}

{real_name} kehte hain:
"{opener}"

---
Shuru karenge?"""

        return message.strip()

    def get_expert_summary(self, expert_name: str) -> Dict[str, Any]:
        """
        Get summary of expert for context.

        Returns:
            Dict with expert metadata
        """
        expert = get_expert(expert_name)
        if not expert:
            return {}

        return {
            "name": expert.get("real_name"),
            "role": expert.get("role"),
            "domains": expert.get("domains", []),
            "tone": expert.get("tone"),
            "expertise": expert.get("signature_stories", [])[:2],
        }

    def should_suggest_different_expert(
        self,
        expert_name: str,
        user_topic: str
    ) -> bool:
        """
        Check if expert is appropriate for topic.

        Args:
            expert_name: Expert key
            user_topic: User's topic of interest

        Returns:
            True if different expert would be better
        """
        expert = get_expert(expert_name)
        if not expert:
            return False

        # Simple heuristic: check if any keyword matches expert domain
        topic_lower = user_topic.lower()
        domains = expert.get("domains", [])

        # If no keyword match and expert very specialized, suggest change
        domain_keywords = " ".join(domains).lower()
        has_keyword_match = any(word in topic_lower for word in domains)

        return not has_keyword_match and len(domains) <= 2
