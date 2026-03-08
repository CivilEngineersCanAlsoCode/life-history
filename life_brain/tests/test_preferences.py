"""
Test suite for preferences system.

Tests cover:
- Preference creation and validation
- Language, style, and expert preferences
- Preference updates
- Statistics and distribution
"""

import pytest
from datetime import datetime

from life_brain.session.preferences import (
    UserPreferences,
    PreferencesSystem,
    Language,
    CommunicationStyle,
    ExpertDomain,
)


class TestUserPreferences:
    """Test UserPreferences dataclass."""

    def test_create_preferences(self):
        """Test creating user preferences."""
        prefs = UserPreferences(user_id="user_001")

        assert prefs.user_id == "user_001"
        assert prefs.language == Language.HINGLISH
        assert prefs.communication_style == CommunicationStyle.CONVERSATIONAL

    def test_to_dict(self):
        """Test converting to dictionary."""
        prefs = UserPreferences(
            user_id="user_001",
            language=Language.ENGLISH,
            communication_style=CommunicationStyle.FORMAL,
            detail_level=7,
        )

        prefs_dict = prefs.to_dict()
        assert prefs_dict["user_id"] == "user_001"
        assert prefs_dict["language"] == "english"
        assert prefs_dict["detail_level"] == 7

    def test_validate_valid(self):
        """Test validating valid preferences."""
        prefs = UserPreferences(user_id="user_001", detail_level=5)

        is_valid, errors = prefs.validate()
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_detail_level_bounds(self):
        """Test detail level validation."""
        # Too low
        prefs1 = UserPreferences(user_id="user_001", detail_level=0)
        is_valid1, _ = prefs1.validate()
        assert is_valid1 is False

        # Too high
        prefs2 = UserPreferences(user_id="user_001", detail_level=11)
        is_valid2, _ = prefs2.validate()
        assert is_valid2 is False


class TestPreferencesSystem:
    """Test PreferencesSystem."""

    def test_create_system(self):
        """Test creating preferences system."""
        system = PreferencesSystem()
        assert len(system.preferences) == 0

    def test_preferences_system_create(self):
        """Test creating user preferences."""
        system = PreferencesSystem()

        prefs = system.preferences_system(
            user_id="user_001",
            language="english",
            communication_style="formal",
            detail_level=8,
        )

        assert prefs.user_id == "user_001"
        assert prefs.language == Language.ENGLISH
        assert prefs.detail_level == 8

    def test_preferences_system_with_experts(self):
        """Test creating preferences with experts."""
        system = PreferencesSystem()

        prefs = system.preferences_system(
            user_id="user_001",
            preferred_experts=["product", "data"],
        )

        assert ExpertDomain.PRODUCT in prefs.preferred_experts
        assert ExpertDomain.DATA in prefs.preferred_experts

    def test_get_preferences(self):
        """Test retrieving preferences."""
        system = PreferencesSystem()

        system.preferences_system("user_001", language="english")
        prefs = system.get_preferences("user_001")

        assert prefs is not None
        assert prefs.language == Language.ENGLISH

    def test_update_preference(self):
        """Test updating preferences."""
        system = PreferencesSystem()

        system.preferences_system("user_001", detail_level=5)
        success, error = system.update_preference(
            "user_001",
            detail_level=8,
            language="english",
        )

        assert success is True
        prefs = system.get_preferences("user_001")
        assert prefs.detail_level == 8
        assert prefs.language == Language.ENGLISH

    def test_update_nonexistent_user(self):
        """Test updating nonexistent user."""
        system = PreferencesSystem()

        success, error = system.update_preference("nonexistent", detail_level=5)
        assert success is False
        assert "not found" in error

    def test_update_with_custom_field(self):
        """Test updating with custom fields."""
        system = PreferencesSystem()

        system.preferences_system("user_001")
        system.update_preference(
            "user_001",
            custom_theme="dark_blue",
            custom_font_size=14,
        )

        prefs = system.get_preferences("user_001")
        assert prefs.custom_fields["custom_theme"] == "dark_blue"
        assert prefs.custom_fields["custom_font_size"] == 14

    def test_preference_history(self):
        """Test preference change history."""
        system = PreferencesSystem()

        system.preferences_system("user_001", language="hinglish")
        system.update_preference("user_001", language="english")
        system.update_preference("user_001", detail_level=8)

        history = system.get_preference_history("user_001")
        assert len(history) >= 3

    def test_export_preferences(self):
        """Test exporting preferences."""
        system = PreferencesSystem()

        system.preferences_system("user_001", language="english", detail_level=7)
        exported = system.export_preferences("user_001")

        assert exported is not None
        assert exported["user_id"] == "user_001"
        assert exported["language"] == "english"

    def test_language_distribution(self):
        """Test language distribution."""
        system = PreferencesSystem()

        system.preferences_system("user_001", language="english")
        system.preferences_system("user_002", language="hinglish")
        system.preferences_system("user_003", language="hinglish")

        dist = system.get_language_distribution()
        assert dist["english"] == 1
        assert dist["hinglish"] == 2

    def test_style_distribution(self):
        """Test communication style distribution."""
        system = PreferencesSystem()

        system.preferences_system("user_001", communication_style="formal")
        system.preferences_system("user_002", communication_style="formal")
        system.preferences_system("user_003", communication_style="concise")

        dist = system.get_style_distribution()
        assert dist["formal"] == 2
        assert dist["concise"] == 1

    def test_expert_popularity(self):
        """Test expert domain popularity."""
        system = PreferencesSystem()

        system.preferences_system("user_001", preferred_experts=["product", "data"])
        system.preferences_system("user_002", preferred_experts=["product"])
        system.preferences_system("user_003", preferred_experts=["career"])

        popularity = system.get_expert_popularity()
        assert popularity["product"] == 2
        assert popularity["data"] == 1
        assert popularity["career"] == 1

    def test_get_statistics(self):
        """Test getting statistics."""
        system = PreferencesSystem()

        # Add multiple users
        for i in range(3):
            system.preferences_system(
                f"user_{i:03d}",
                language="english" if i % 2 == 0 else "hinglish",
                communication_style="formal" if i % 2 == 0 else "conversational",
                detail_level=5 + i,
            )

        stats = system.get_statistics()
        assert stats["total_users"] == 3
        assert "english" in stats["languages"]
        assert stats["avg_detail_level"] > 0

    def test_export_all_preferences(self):
        """Test exporting all preferences."""
        system = PreferencesSystem()

        for i in range(3):
            system.preferences_system(f"user_{i}")

        exported = system.export_all_preferences()
        assert len(exported) == 3
        assert all("user_id" in e for e in exported)

    def test_preferences_persistence(self):
        """Test preferences persist across operations."""
        system = PreferencesSystem()

        prefs1 = system.preferences_system(
            "user_001",
            language="english",
            detail_level=7,
        )

        # Update
        system.update_preference("user_001", detail_level=9)

        # Retrieve again
        prefs2 = system.get_preferences("user_001")

        assert prefs2.detail_level == 9
        assert prefs2.language == Language.ENGLISH

    def test_multiple_users_independent(self):
        """Test multiple users have independent preferences."""
        system = PreferencesSystem()

        system.preferences_system("user_001", language="english", detail_level=5)
        system.preferences_system("user_002", language="hinglish", detail_level=9)

        prefs1 = system.get_preferences("user_001")
        prefs2 = system.get_preferences("user_002")

        assert prefs1.language == Language.ENGLISH
        assert prefs2.language == Language.HINGLISH
        assert prefs1.detail_level == 5
        assert prefs2.detail_level == 9

    def test_invalid_language(self):
        """Test invalid language raises error."""
        system = PreferencesSystem()

        with pytest.raises(ValueError, match="Invalid language"):
            system.preferences_system("user_001", language="klingon")

    def test_invalid_style(self):
        """Test invalid style raises error."""
        system = PreferencesSystem()

        with pytest.raises(ValueError, match="Invalid communication_style"):
            system.preferences_system(
                "user_001",
                communication_style="aggressively_sarcastic",
            )

    def test_invalid_expert(self):
        """Test invalid expert raises error."""
        system = PreferencesSystem()

        with pytest.raises(ValueError, match="Invalid expert"):
            system.preferences_system(
                "user_001",
                preferred_experts=["product", "invalid"],
            )

    def test_complex_preferences_workflow(self):
        """Test complex workflow with multiple users."""
        system = PreferencesSystem()

        # Create diverse users
        users = [
            ("user_pm", "english", "formal", ["product"], 8),
            ("user_eng", "hinglish", "conversational", ["engineering", "data"], 6),
            ("user_career", "english", "detailed", ["career"], 9),
        ]

        for user_id, lang, style, experts, detail in users:
            system.preferences_system(
                user_id,
                language=lang,
                communication_style=style,
                preferred_experts=experts,
                detail_level=detail,
            )

        # Verify statistics
        stats = system.get_statistics()
        assert stats["total_users"] == 3
        assert stats["avg_detail_level"] == (8 + 6 + 9) / 3

        # Update one user
        system.update_preference("user_pm", detail_level=10)
        updated = system.get_preferences("user_pm")
        assert updated.detail_level == 10

        # Verify others unchanged
        assert system.get_preferences("user_eng").detail_level == 6
