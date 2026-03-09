"""
Expert Context Manager — Maintain expert state and enforce access rules.

Handles:
- Loading expert profile at session start
- Maintaining expert context across turns
- Enforcing domain-specific data access (privacy firewall)
- Tracking conversation history within expert lens
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime

from .expert_roster import ExpertRoster, Expert


@dataclass
class ExpertContext:
    """Maintains expert context throughout a session."""

    expert: Expert
    session_start_ts: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    user_profile: Optional[Dict[str, Any]] = None  # What expert knows about user
    session_data_domains: List[str] = field(default_factory=list)  # Domains accessed this session

    def add_turn(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a conversation turn."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        })

    def get_recent_history(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history for context window."""
        return self.conversation_history[-limit:]

    def is_domain_accessible(self, domain: str) -> bool:
        """Check if expert can access this data domain."""
        return domain in self.expert.data_access_domains

    def track_domain_access(self, domain: str):
        """Track that expert accessed a domain this session."""
        if domain not in self.session_data_domains:
            self.session_data_domains.append(domain)


class ExpertContextManager:
    """Manages expert selection, loading, and context throughout session."""

    def __init__(self):
        """Initialize with expert roster."""
        self.roster = ExpertRoster()
        self.current_context: Optional[ExpertContext] = None

    def load_expert(self, expert_name: str) -> Optional[ExpertContext]:
        """
        Load expert and initialize session context.

        This is called when user selects an expert or when a use case
        automatically assigns an expert.

        Args:
            expert_name: Name of expert (e.g., "Satya", "Richard")

        Returns:
            ExpertContext if expert found, None otherwise
        """
        expert = self.roster.get_by_name(expert_name)
        if not expert:
            return None

        self.current_context = ExpertContext(expert=expert)
        return self.current_context

    def get_expert_greeting(self) -> str:
        """
        Get expert's opening statement for session.

        Format:
        "[Expert Name], The [Title]"
        "[Bio]"
        ""
        "[Opening statement]"
        """
        if not self.current_context:
            return ""

        e = self.current_context.expert
        return f"""
✨ {e.name}, The {e.title}

{e.bio}

{e.conversation_starter}
"""

    def get_speaking_style_instructions(self) -> str:
        """
        Get instructions for how expert should speak in this session.

        Includes style, phrases, and approach.
        """
        if not self.current_context:
            return ""

        e = self.current_context.expert
        phrases = ", ".join(f'"{p}"' for p in e.favorite_phrases[:3])

        return f"""
Speaking Style: {e.speaking_style}

Signature Phrases: {phrases}

Approach: Focus on {e.domain.value}. Share stories when relevant. Use examples.
"""

    def enforce_data_access(
        self,
        requested_domain: str
    ) -> tuple[bool, Optional[str]]:
        """
        Check if expert can access requested data domain.

        Implements privacy firewall:
        - Warren can only access finance data
        - Esther can only access relationship data
        - Some experts can access multiple domains
        - etc.

        Returns:
            (is_allowed, message)
        """
        if not self.current_context:
            return False, "No expert loaded"

        expert = self.current_context.expert
        is_allowed = requested_domain in expert.data_access_domains

        if is_allowed:
            self.current_context.track_domain_access(requested_domain)
            return True, None
        else:
            denial_msg = (
                f"{expert.name} specializes in {expert.domain.value}, "
                f"not {requested_domain}. Would you like to switch experts?"
            )
            return False, denial_msg

    def get_context_for_llm(self) -> Dict[str, Any]:
        """
        Get expert context formatted for LLM prompt.

        Includes expert profile, conversation history, and style instructions.
        """
        if not self.current_context:
            return {}

        ctx = self.current_context
        e = ctx.expert

        return {
            "expert_name": e.name,
            "expert_title": e.title,
            "expert_philosophy": e.philosophy,
            "speaking_style": e.speaking_style,
            "favorite_phrases": e.favorite_phrases,
            "domain_expertise": e.domain_expertise,
            "recent_history": ctx.get_recent_history(10),
            "user_profile": ctx.user_profile or {},
            "conversation_sample": e.conversation_sample,
        }

    def get_expert_summary(self) -> str:
        """Get brief summary of current expert for display."""
        if not self.current_context:
            return "No expert loaded"

        e = self.current_context.expert
        return f"🎭 {e.name}, {e.title} — {e.domain.value.title()}"

    def switch_expert(self, new_expert_name: str) -> Optional[str]:
        """
        Switch to a different expert mid-session.

        Returns greeting message if successful, error message otherwise.
        """
        new_context = self.load_expert(new_expert_name)
        if not new_context:
            return f"Expert {new_expert_name} not found."

        # Preserve some context
        new_context.user_profile = self.current_context.user_profile if self.current_context else None

        self.current_context = new_context
        return self.get_expert_greeting()

    def can_help_with_use_case(self, use_case_id: str) -> bool:
        """Check if current expert can help with use case."""
        if not self.current_context:
            return False

        return use_case_id in self.current_context.expert.accessible_use_cases

    def get_expert_signature_story(self, story_index: int = 0) -> Optional[str]:
        """
        Get a signature story from the expert.

        Useful for illustrating approach or making a point.
        """
        if not self.current_context:
            return None

        expert = self.current_context.expert
        if story_index >= len(expert.signature_stories):
            return None

        story = expert.signature_stories[story_index]
        return f"""
📖 {story.title}

{story.summary}

💡 Lesson: {story.lesson}
"""

    def get_all_experts_list(self) -> List[str]:
        """Get list of all available experts for display."""
        return [e.name for e in self.roster.get_all()]

    def get_expert_selector_ui(self) -> str:
        """
        Format expert selector for user.

        Shows all 16 experts with their domains.
        """
        lines = [
            "\n🎭 SELECT YOUR EXPERT GUIDE",
            "=" * 60,
            ""
        ]

        # Group by domain
        by_domain = {}
        for expert in self.roster.get_all():
            domain = expert.domain.value.replace("_", " ").title()
            if domain not in by_domain:
                by_domain[domain] = []
            by_domain[domain].append(expert)

        for domain in sorted(by_domain.keys()):
            lines.append(f"\n{domain.upper()}")
            for expert in by_domain[domain]:
                lines.append(f"  • {expert.name:<15} — {expert.title}")

        lines.append("\n" + "=" * 60)
        lines.append("Type expert name to select (e.g., 'Satya', 'Richard', 'Warren')")

        return "\n".join(lines)
