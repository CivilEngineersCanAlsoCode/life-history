"""
Use Case UI — Display formatted use case results.

Provides templates for showing top-10 matches and full categorized catalog.
"""

from typing import List, Dict
from .use_case_catalog import UseCase, UseCaseCategory
from .use_case_matcher import MatchResult, UseCaseMatcher


class UseCaseUI:
    """Format use case results for display."""

    @staticmethod
    def format_top_matches(
        matches: List[MatchResult],
        title: str = "Top Use Cases for You"
    ) -> str:
        """
        Format top-10 matches as a ranked list with scores.

        Shows:
        - Rank (1-10)
        - Use case ID + title
        - Expert assigned
        - Match score as progress bar
        - Difficulty level
        """
        if not matches:
            return "❌ No matching use cases found. Try browsing by category."

        lines = [f"\n{title}", "=" * 60]

        for idx, match in enumerate(matches, 1):
            uc = match.use_case
            score_pct = int(match.match_score * 100)
            bar_filled = int(score_pct / 10)
            bar_empty = 10 - bar_filled
            progress_bar = "█" * bar_filled + "░" * bar_empty

            difficulty_emoji = {
                "beginner": "🟢",
                "intermediate": "🟡",
                "advanced": "🔴",
            }.get(uc.difficulty_level, "⚪")

            lines.append(f"\n{idx:2d}. [{uc.use_case_id}] {uc.title}")
            lines.append(f"    Expert: {uc.expert_assigned} | {difficulty_emoji} {uc.difficulty_level.title()}")
            lines.append(f"    Match: {progress_bar} {score_pct}%")
            lines.append(f"    Duration: ~{uc.estimated_duration_min} min")

        lines.append("\n" + "=" * 60)
        lines.append("Select by ID (e.g., 'C1') or browse by category")

        return "\n".join(lines)

    @staticmethod
    def format_single_use_case(uc: UseCase) -> str:
        """Format a single use case for detailed view."""
        difficulty_emoji = {
            "beginner": "🟢",
            "intermediate": "🟡",
            "advanced": "🔴",
        }.get(uc.difficulty_level, "⚪")

        return f"""
╭─────────────────────────────────────────────────────╮
│ [{uc.use_case_id}] {uc.title:<40} │
├─────────────────────────────────────────────────────┤
│ Expert Assigned: {uc.expert_assigned:<35} │
│ Difficulty:     {difficulty_emoji} {uc.difficulty_level.title():<35} │
│ Duration:       ~{uc.estimated_duration_min} minutes{' ' * 29} │
├─────────────────────────────────────────────────────┤
│                                                     │
│ {uc.description[:50]}                │
│ {uc.description[50:100]}  │
│ {uc.description[100:]}  │
│                                                     │
╰─────────────────────────────────────────────────────╯
"""

    @staticmethod
    def format_categorized_list(
        by_category: Dict[str, List[UseCase]]
    ) -> str:
        """
        Format full categorized use case list for browsing.

        Shows all 40+ use cases organized by category.
        """
        lines = [
            "\n📚 FULL USE CASE CATALOG",
            "=" * 70,
            ""
        ]

        category_emoji = {
            "career": "💼",
            "relationships": "💕",
            "health": "🏥",
            "finance": "💰",
            "personal_growth": "🌱",
            "creativity": "🎨",
            "memory": "📖",
        }

        for category_key, use_cases in sorted(by_category.items()):
            emoji = category_emoji.get(category_key, "📌")
            category_title = category_key.replace("_", " ").title()

            lines.append(f"\n{emoji} {category_title.upper()} ({len(use_cases)} use cases)")
            lines.append("-" * 70)

            for uc in use_cases:
                difficulty_emoji = {
                    "beginner": "🟢",
                    "intermediate": "🟡",
                    "advanced": "🔴",
                }.get(uc.difficulty_level, "⚪")

                lines.append(
                    f"  [{uc.use_case_id}] {uc.title:<45} {difficulty_emoji} "
                    f"({uc.estimated_duration_min}m)"
                )

        lines.append("\n" + "=" * 70)
        lines.append("Select by ID (e.g., 'C1', 'R2', 'H5') to start a use case")

        return "\n".join(lines)

    @staticmethod
    def format_quick_selector() -> str:
        """
        Quick selector UI for user to choose input method.

        Shows options:
        [A] Search by keywords
        [B] Browse by category
        [C] Filter by difficulty
        """
        return """
╭─────────────────────────────────────────────────────╮
│ How would you like to find a use case?              │
├─────────────────────────────────────────────────────┤
│                                                     │
│ [A] Search with keywords (e.g., "interview prep")   │
│ [B] Browse by category (career, health, finance...) │
│ [C] Filter by difficulty (beginner to advanced)     │
│ [D] See all 40+ use cases                          │
│                                                     │
╰─────────────────────────────────────────────────────╯
"""

    @staticmethod
    def format_category_browser() -> str:
        """Display categories for user to choose from."""
        categories = [
            ("💼", "CAREER", "12 use cases"),
            ("💕", "RELATIONSHIPS", "7 use cases"),
            ("🏥", "HEALTH", "6 use cases"),
            ("💰", "FINANCE", "5 use cases"),
            ("🌱", "PERSONAL GROWTH", "6 use cases"),
            ("🎨", "CREATIVITY", "3 use cases"),
            ("📖", "MEMORY", "2 use cases"),
        ]

        lines = [
            "\n📚 BROWSE BY CATEGORY",
            "=" * 50,
            ""
        ]

        for emoji, category, count in categories:
            lines.append(f"{emoji} {category:<20} {count:>12}")

        lines.append("\n" + "=" * 50)
        lines.append("Type category name or emoji to explore")

        return "\n".join(lines)
