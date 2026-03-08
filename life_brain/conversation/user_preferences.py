"""
User preferences and personalization settings.

Persists: language preference, expert preferences, conversation style,
response format, and custom settings. Improves with repeated use.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
import os

logger = logging.getLogger(__name__)


# Valid values for enumerated preferences
VALID_LANGUAGES = {"english", "hinglish", "hindi"}
VALID_STYLES = {"concise", "detailed", "conversational"}
VALID_FORMATS = {"plain", "markdown", "bullets"}
VALID_EXPERTS = {"career", "mental_health", "technical", "finance", "health"}


@dataclass
class UserPreferences:
    """User preferences and personalization settings."""

    # Core preferences
    language: str = "hinglish"           # "english", "hinglish", "hindi"
    conversation_style: str = "conversational"  # "concise", "detailed", "conversational"
    response_format: str = "plain"       # "plain", "markdown", "bullets"

    # Expert preferences
    preferred_experts: List[str] = field(default_factory=list)  # e.g. ["career", "mental_health"]
    blocked_experts: List[str] = field(default_factory=list)

    # Personalization
    custom_settings: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    update_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "language": self.language,
            "conversation_style": self.conversation_style,
            "response_format": self.response_format,
            "preferred_experts": self.preferred_experts,
            "blocked_experts": self.blocked_experts,
            "custom_settings": self.custom_settings,
            "last_updated": self.last_updated,
            "update_count": self.update_count,
        }


class UserPreferenceManager:
    """Manage and persist user preferences."""

    def __init__(self, storage_path: Optional[str] = None):
        self._preferences: UserPreferences = UserPreferences()
        self._storage_path: Optional[str] = storage_path
        self._last_save_error: Optional[str] = None

    @property
    def preferences(self) -> UserPreferences:
        return self._preferences

    def set_language(self, language: str) -> None:
        """Set language preference.

        Args:
            language: One of "english", "hinglish", "hindi"

        Raises:
            ValueError: If language not valid
        """
        lang = language.lower().strip()
        if lang not in VALID_LANGUAGES:
            raise ValueError(f"Invalid language '{language}'. Valid: {VALID_LANGUAGES}")
        self._preferences.language = lang
        self._bump_update()

    def set_conversation_style(self, style: str) -> None:
        """Set conversation style.

        Args:
            style: One of "concise", "detailed", "conversational"
        """
        s = style.lower().strip()
        if s not in VALID_STYLES:
            raise ValueError(f"Invalid style '{style}'. Valid: {VALID_STYLES}")
        self._preferences.conversation_style = s
        self._bump_update()

    def set_response_format(self, fmt: str) -> None:
        """Set response format.

        Args:
            fmt: One of "plain", "markdown", "bullets"
        """
        f = fmt.lower().strip()
        if f not in VALID_FORMATS:
            raise ValueError(f"Invalid format '{fmt}'. Valid: {VALID_FORMATS}")
        self._preferences.response_format = f
        self._bump_update()

    def add_preferred_expert(self, expert: str) -> None:
        """Add an expert to preferred list."""
        e = expert.lower().strip()
        if e not in VALID_EXPERTS:
            raise ValueError(f"Invalid expert '{expert}'. Valid: {VALID_EXPERTS}")
        if e not in self._preferences.preferred_experts:
            self._preferences.preferred_experts.append(e)
            self._bump_update()

    def remove_preferred_expert(self, expert: str) -> None:
        """Remove an expert from preferred list."""
        e = expert.lower().strip()
        if e in self._preferences.preferred_experts:
            self._preferences.preferred_experts.remove(e)
            self._bump_update()

    def block_expert(self, expert: str) -> None:
        """Block an expert from being suggested."""
        e = expert.lower().strip()
        if e not in VALID_EXPERTS:
            raise ValueError(f"Invalid expert '{expert}'. Valid: {VALID_EXPERTS}")
        if e not in self._preferences.blocked_experts:
            self._preferences.blocked_experts.append(e)
            # Remove from preferred if present
            if e in self._preferences.preferred_experts:
                self._preferences.preferred_experts.remove(e)
            self._bump_update()

    def set_custom(self, key: str, value: Any) -> None:
        """Set a custom preference."""
        if not key or not key.strip():
            raise ValueError("key cannot be empty")
        self._preferences.custom_settings[key] = value
        self._bump_update()

    def get_custom(self, key: str, default: Any = None) -> Any:
        """Get a custom preference."""
        return self._preferences.custom_settings.get(key, default)

    def update_from_dict(self, data: Dict[str, Any]) -> List[str]:
        """Bulk update preferences from a dictionary.

        Args:
            data: Dict with preference keys/values

        Returns:
            List of keys that were successfully updated
        """
        updated = []
        setters = {
            "language": self.set_language,
            "conversation_style": self.set_conversation_style,
            "response_format": self.set_response_format,
        }
        for key, fn in setters.items():
            if key in data:
                try:
                    fn(data[key])
                    updated.append(key)
                except ValueError:
                    pass

        if "preferred_experts" in data:
            for expert in data["preferred_experts"]:
                try:
                    self.add_preferred_expert(expert)
                    updated.append(f"preferred_experts:{expert}")
                except ValueError:
                    pass

        if "custom_settings" in data:
            for k, v in data["custom_settings"].items():
                try:
                    self.set_custom(k, v)
                    updated.append(f"custom:{k}")
                except ValueError:
                    pass

        return updated

    def export(self) -> Dict[str, Any]:
        """Export preferences as dict."""
        return self._preferences.to_dict()

    def reset(self) -> None:
        """Reset to defaults."""
        self._preferences = UserPreferences()

    def save_to_disk(self) -> bool:
        """Persist preferences to disk if storage_path is set.

        Returns:
            True if saved successfully (or no path configured), False on error.
        """
        if not self._storage_path:
            return True
        try:
            with open(self._storage_path, "w") as f:
                json.dump(self.export(), f, indent=2)
            self._last_save_error = None
            return True
        except (IOError, OSError) as e:
            self._last_save_error = str(e)
            logger.error(f"Preferences auto-save failed: {e}")
            return False

    def _bump_update(self) -> None:
        """Increment update counter and update timestamp."""
        self._preferences.update_count += 1
        self._preferences.last_updated = datetime.now().isoformat()
        self.save_to_disk()
