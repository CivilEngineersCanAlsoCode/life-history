"""
User preferences system for personalization.

Stores and manages user preferences including language, expert preferences,
communication style, and other customization settings.
"""

from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Language(Enum):
    """Supported languages."""
    ENGLISH = "english"
    HINGLISH = "hinglish"  # Hindi-English mix
    HINDI = "hindi"


class CommunicationStyle(Enum):
    """Communication style preferences."""
    FORMAL = "formal"  # Professional, structured
    CONVERSATIONAL = "conversational"  # Friendly, casual
    CONCISE = "concise"  # Brief, to-the-point
    DETAILED = "detailed"  # Comprehensive, thorough
    DIRECT = "direct"  # Straight answers


class ExpertDomain(Enum):
    """Expert domains available."""
    PRODUCT = "product"  # Product management
    ENGINEERING = "engineering"  # Software engineering
    DATA = "data"  # Data science
    CAREER = "career"  # Career development
    LIFE = "life"  # Life philosophy


@dataclass
class UserPreferences:
    """User preferences configuration."""

    user_id: str
    language: Language = Language.HINGLISH
    communication_style: CommunicationStyle = CommunicationStyle.CONVERSATIONAL
    preferred_experts: List[ExpertDomain] = field(
        default_factory=lambda: [ExpertDomain.CAREER]
    )
    time_zone: str = "UTC"  # e.g., "Asia/Kolkata"
    detail_level: int = 5  # 1-10 scale, how detailed responses should be
    auto_save: bool = True  # Auto-save session state
    track_commitments: bool = True  # Track promises and deadlines
    sentiment_analysis: bool = True  # Enable sentiment tracking
    session_history: int = 10  # Keep last N sessions
    dark_mode: bool = False  # UI theme preference
    quick_answers: bool = True  # Prefer short responses first
    show_sources: bool = True  # Show source documents
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "language": self.language.value,
            "communication_style": self.communication_style.value,
            "preferred_experts": [e.value for e in self.preferred_experts],
            "time_zone": self.time_zone,
            "detail_level": self.detail_level,
            "auto_save": self.auto_save,
            "track_commitments": self.track_commitments,
            "sentiment_analysis": self.sentiment_analysis,
            "session_history": self.session_history,
            "dark_mode": self.dark_mode,
            "quick_answers": self.quick_answers,
            "show_sources": self.show_sources,
            "custom_fields": self.custom_fields,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate preferences."""
        errors = []

        if not self.user_id or not self.user_id.strip():
            errors.append("user_id is required")

        if not 1 <= self.detail_level <= 10:
            errors.append("detail_level must be 1-10")

        if self.session_history < 1:
            errors.append("session_history must be >= 1")

        if not isinstance(self.language, Language):
            errors.append("language must be valid Language enum")

        if not isinstance(self.communication_style, CommunicationStyle):
            errors.append("communication_style must be valid CommunicationStyle enum")

        return len(errors) == 0, errors


class PreferencesSystem:
    """Manage user preferences."""

    def __init__(self):
        """Initialize preferences system."""
        self.preferences: Dict[str, UserPreferences] = {}  # user_id -> UserPreferences
        self.preference_history: Dict[str, List[Dict[str, Any]]] = {}  # user_id -> history

    def preferences_system(
        self,
        user_id: str,
        language: str = "hinglish",
        communication_style: str = "conversational",
        preferred_experts: Optional[List[str]] = None,
        time_zone: str = "UTC",
        detail_level: int = 5,
        auto_save: bool = True,
        track_commitments: bool = True,
        sentiment_analysis: bool = True,
        session_history: int = 10,
        dark_mode: bool = False,
        quick_answers: bool = True,
        show_sources: bool = True,
        **custom_fields,
    ) -> UserPreferences:
        """
        Create or update user preferences.

        Args:
            user_id: User ID
            language: Language preference (english, hinglish, hindi)
            communication_style: Style preference
            preferred_experts: List of expert domains
            time_zone: User's timezone
            detail_level: Response detail (1-10)
            auto_save: Auto-save sessions
            track_commitments: Track promises
            sentiment_analysis: Analyze mood
            session_history: Sessions to keep
            dark_mode: Dark UI theme
            quick_answers: Prefer concise first
            show_sources: Show document sources
            **custom_fields: Custom preference fields

        Returns:
            UserPreferences object
        """
        # Convert string to enums
        try:
            lang_enum = Language[language.upper()]
        except KeyError:
            raise ValueError(f"Invalid language: {language}")

        try:
            style_enum = CommunicationStyle[communication_style.upper()]
        except KeyError:
            raise ValueError(f"Invalid communication_style: {communication_style}")

        # Convert expert domains
        expert_enums = []
        if preferred_experts:
            for expert in preferred_experts:
                try:
                    expert_enums.append(ExpertDomain[expert.upper()])
                except KeyError:
                    raise ValueError(f"Invalid expert domain: {expert}")

        # Create preferences
        prefs = UserPreferences(
            user_id=user_id,
            language=lang_enum,
            communication_style=style_enum,
            preferred_experts=expert_enums or [ExpertDomain.CAREER],
            time_zone=time_zone,
            detail_level=detail_level,
            auto_save=auto_save,
            track_commitments=track_commitments,
            sentiment_analysis=sentiment_analysis,
            session_history=session_history,
            dark_mode=dark_mode,
            quick_answers=quick_answers,
            show_sources=show_sources,
            custom_fields=custom_fields,
        )

        # Validate
        is_valid, errors = prefs.validate()
        if not is_valid:
            raise ValueError(f"Invalid preferences: {errors}")

        # Store preferences
        self.preferences[user_id] = prefs

        # Track history
        if user_id not in self.preference_history:
            self.preference_history[user_id] = []

        self.preference_history[user_id].append({
            "timestamp": datetime.now().isoformat(),
            "changes": "created",
            "values": prefs.to_dict(),
        })

        return prefs

    def get_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Get user preferences."""
        return self.preferences.get(user_id)

    def update_preference(
        self,
        user_id: str,
        **updates,
    ) -> Tuple[bool, Optional[str]]:
        """
        Update specific preferences.

        Args:
            user_id: User ID
            **updates: Preference fields to update

        Returns:
            (success, error_message)
        """
        if user_id not in self.preferences:
            return False, f"User {user_id} not found"

        prefs = self.preferences[user_id]

        # Track changes
        changes = []

        # Handle enum conversions
        if "language" in updates:
            try:
                prefs.language = Language[updates["language"].upper()]
                changes.append(f"language: {updates['language']}")
            except KeyError:
                return False, f"Invalid language: {updates['language']}"

        if "communication_style" in updates:
            try:
                prefs.communication_style = CommunicationStyle[
                    updates["communication_style"].upper()
                ]
                changes.append(f"communication_style: {updates['communication_style']}")
            except KeyError:
                return False, f"Invalid style: {updates['communication_style']}"

        if "preferred_experts" in updates:
            try:
                prefs.preferred_experts = [
                    ExpertDomain[e.upper()] for e in updates["preferred_experts"]
                ]
                changes.append(f"preferred_experts: updated")
            except KeyError as e:
                return False, f"Invalid expert: {e}"

        # Handle other fields
        for key in ["time_zone", "detail_level", "session_history", "auto_save",
                    "track_commitments", "sentiment_analysis", "dark_mode",
                    "quick_answers", "show_sources"]:
            if key in updates:
                setattr(prefs, key, updates[key])
                changes.append(f"{key}: {updates[key]}")

        # Handle custom fields
        for key, value in updates.items():
            if key not in prefs.__dataclass_fields__:
                prefs.custom_fields[key] = value
                changes.append(f"custom {key}: {value}")

        # Update timestamp
        prefs.updated_at = datetime.now().isoformat()

        # Record in history
        self.preference_history[user_id].append({
            "timestamp": datetime.now().isoformat(),
            "changes": ", ".join(changes),
            "values": prefs.to_dict(),
        })

        return True, None

    def get_preference_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get preference change history."""
        return self.preference_history.get(user_id, [])

    def export_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Export user preferences."""
        prefs = self.get_preferences(user_id)
        if not prefs:
            return None
        return prefs.to_dict()

    def get_all_users_count(self) -> int:
        """Get total number of users."""
        return len(self.preferences)

    def get_language_distribution(self) -> Dict[str, int]:
        """Get distribution of language preferences."""
        dist = {}
        for prefs in self.preferences.values():
            lang = prefs.language.value
            dist[lang] = dist.get(lang, 0) + 1
        return dist

    def get_style_distribution(self) -> Dict[str, int]:
        """Get distribution of communication styles."""
        dist = {}
        for prefs in self.preferences.values():
            style = prefs.communication_style.value
            dist[style] = dist.get(style, 0) + 1
        return dist

    def get_expert_popularity(self) -> Dict[str, int]:
        """Get popularity of expert domains."""
        popularity = {}
        for prefs in self.preferences.values():
            for expert in prefs.preferred_experts:
                domain = expert.value
                popularity[domain] = popularity.get(domain, 0) + 1
        return popularity

    def get_statistics(self) -> Dict[str, Any]:
        """Get preferences statistics."""
        if not self.preferences:
            return {
                "total_users": 0,
                "languages": {},
                "styles": {},
                "experts": {},
                "avg_detail_level": 0,
            }

        detail_levels = [p.detail_level for p in self.preferences.values()]
        avg_detail = sum(detail_levels) / len(detail_levels) if detail_levels else 0

        return {
            "total_users": len(self.preferences),
            "languages": self.get_language_distribution(),
            "styles": self.get_style_distribution(),
            "experts": self.get_expert_popularity(),
            "avg_detail_level": avg_detail,
        }

    def export_all_preferences(self) -> List[Dict[str, Any]]:
        """Export all user preferences."""
        return [p.to_dict() for p in self.preferences.values()]
