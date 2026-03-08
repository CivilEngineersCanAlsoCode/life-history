"""
Tests for user preferences and personalization settings.

Tests cover:
- Setting and getting language, style, format preferences
- Expert preference management (add/remove/block)
- Custom settings
- Bulk update from dict
- Validation and error handling
- Export/reset
"""

import pytest

from life_brain.conversation.user_preferences import (
    UserPreferences,
    UserPreferenceManager,
)


class TestUserPreferences:
    """Test UserPreferences dataclass."""

    def test_default_values(self):
        prefs = UserPreferences()
        assert prefs.language == "hinglish"
        assert prefs.conversation_style == "conversational"
        assert prefs.response_format == "plain"
        assert prefs.preferred_experts == []
        assert prefs.blocked_experts == []

    def test_to_dict(self):
        prefs = UserPreferences()
        d = prefs.to_dict()
        assert "language" in d
        assert "conversation_style" in d
        assert "response_format" in d
        assert "preferred_experts" in d
        assert "custom_settings" in d
        assert "update_count" in d


class TestSetLanguage:
    """Test language preference setting."""

    def test_set_english(self):
        mgr = UserPreferenceManager()
        mgr.set_language("english")
        assert mgr.preferences.language == "english"

    def test_set_hinglish(self):
        mgr = UserPreferenceManager()
        mgr.set_language("hinglish")
        assert mgr.preferences.language == "hinglish"

    def test_set_hindi(self):
        mgr = UserPreferenceManager()
        mgr.set_language("hindi")
        assert mgr.preferences.language == "hindi"

    def test_case_insensitive(self):
        mgr = UserPreferenceManager()
        mgr.set_language("English")
        assert mgr.preferences.language == "english"

    def test_invalid_language_raises(self):
        mgr = UserPreferenceManager()
        with pytest.raises(ValueError):
            mgr.set_language("french")

    def test_update_count_increments(self):
        mgr = UserPreferenceManager()
        mgr.set_language("english")
        assert mgr.preferences.update_count == 1


class TestConversationStyle:
    """Test conversation style preference."""

    def test_set_concise(self):
        mgr = UserPreferenceManager()
        mgr.set_conversation_style("concise")
        assert mgr.preferences.conversation_style == "concise"

    def test_set_detailed(self):
        mgr = UserPreferenceManager()
        mgr.set_conversation_style("detailed")
        assert mgr.preferences.conversation_style == "detailed"

    def test_invalid_style_raises(self):
        mgr = UserPreferenceManager()
        with pytest.raises(ValueError):
            mgr.set_conversation_style("casual")


class TestResponseFormat:
    """Test response format preference."""

    def test_set_markdown(self):
        mgr = UserPreferenceManager()
        mgr.set_response_format("markdown")
        assert mgr.preferences.response_format == "markdown"

    def test_set_bullets(self):
        mgr = UserPreferenceManager()
        mgr.set_response_format("bullets")
        assert mgr.preferences.response_format == "bullets"

    def test_invalid_format_raises(self):
        mgr = UserPreferenceManager()
        with pytest.raises(ValueError):
            mgr.set_response_format("html")


class TestExpertPreferences:
    """Test expert preference management."""

    def test_add_preferred_expert(self):
        mgr = UserPreferenceManager()
        mgr.add_preferred_expert("career")
        assert "career" in mgr.preferences.preferred_experts

    def test_add_duplicate_expert_ignored(self):
        mgr = UserPreferenceManager()
        mgr.add_preferred_expert("career")
        mgr.add_preferred_expert("career")
        assert mgr.preferences.preferred_experts.count("career") == 1

    def test_remove_preferred_expert(self):
        mgr = UserPreferenceManager()
        mgr.add_preferred_expert("career")
        mgr.remove_preferred_expert("career")
        assert "career" not in mgr.preferences.preferred_experts

    def test_block_expert(self):
        mgr = UserPreferenceManager()
        mgr.block_expert("mental_health")
        assert "mental_health" in mgr.preferences.blocked_experts

    def test_block_removes_from_preferred(self):
        mgr = UserPreferenceManager()
        mgr.add_preferred_expert("career")
        mgr.block_expert("career")
        assert "career" not in mgr.preferences.preferred_experts
        assert "career" in mgr.preferences.blocked_experts

    def test_invalid_expert_raises(self):
        mgr = UserPreferenceManager()
        with pytest.raises(ValueError):
            mgr.add_preferred_expert("astrology")

    def test_multiple_preferred_experts(self):
        mgr = UserPreferenceManager()
        mgr.add_preferred_expert("career")
        mgr.add_preferred_expert("technical")
        assert len(mgr.preferences.preferred_experts) == 2


class TestCustomSettings:
    """Test custom preference settings."""

    def test_set_and_get_custom(self):
        mgr = UserPreferenceManager()
        mgr.set_custom("greeting", "Hey there!")
        assert mgr.get_custom("greeting") == "Hey there!"

    def test_get_custom_default(self):
        mgr = UserPreferenceManager()
        assert mgr.get_custom("nonexistent", "fallback") == "fallback"

    def test_custom_any_type(self):
        mgr = UserPreferenceManager()
        mgr.set_custom("max_results", 10)
        mgr.set_custom("show_scores", True)
        assert mgr.get_custom("max_results") == 10
        assert mgr.get_custom("show_scores") is True

    def test_empty_key_raises(self):
        mgr = UserPreferenceManager()
        with pytest.raises(ValueError):
            mgr.set_custom("", "value")


class TestBulkUpdate:
    """Test bulk update from dict."""

    def test_update_language(self):
        mgr = UserPreferenceManager()
        updated = mgr.update_from_dict({"language": "english"})
        assert "language" in updated
        assert mgr.preferences.language == "english"

    def test_update_multiple(self):
        mgr = UserPreferenceManager()
        updated = mgr.update_from_dict({
            "language": "english",
            "conversation_style": "concise",
            "response_format": "markdown",
        })
        assert len(updated) == 3

    def test_invalid_values_skipped(self):
        mgr = UserPreferenceManager()
        updated = mgr.update_from_dict({"language": "french"})
        assert "language" not in updated

    def test_update_experts_from_dict(self):
        mgr = UserPreferenceManager()
        mgr.update_from_dict({"preferred_experts": ["career", "technical"]})
        assert "career" in mgr.preferences.preferred_experts

    def test_update_custom_from_dict(self):
        mgr = UserPreferenceManager()
        mgr.update_from_dict({"custom_settings": {"theme": "dark"}})
        assert mgr.get_custom("theme") == "dark"


class TestExportReset:
    """Test export and reset functionality."""

    def test_export_returns_dict(self):
        mgr = UserPreferenceManager()
        exported = mgr.export()
        assert isinstance(exported, dict)
        assert "language" in exported

    def test_reset_clears_preferences(self):
        mgr = UserPreferenceManager()
        mgr.set_language("english")
        mgr.add_preferred_expert("career")
        mgr.reset()
        assert mgr.preferences.language == "hinglish"
        assert mgr.preferences.preferred_experts == []
        assert mgr.preferences.update_count == 0


class TestSaveToDisk:
    """Regression tests for issues-36e: preferences auto-save IOError handling.

    Bug: no storage_path param and no error handling when disk write fails.
    Fix: optional storage_path, save_to_disk() with IOError catch + logger.error().
    """

    def test_no_storage_path_returns_true(self):
        """save_to_disk() with no path configured should return True (no-op)."""
        mgr = UserPreferenceManager()
        result = mgr.save_to_disk()
        assert result is True

    def test_save_to_disk_writes_file(self, tmp_path):
        """save_to_disk() should write valid JSON to configured path."""
        import json
        path = str(tmp_path / "prefs.json")
        mgr = UserPreferenceManager(storage_path=path)
        mgr.set_language("english")

        result = mgr.save_to_disk()

        assert result is True
        with open(path) as f:
            data = json.load(f)
        assert data["language"] == "english"

    def test_save_to_disk_ioerror_returns_false(self, tmp_path):
        """save_to_disk() should return False (not raise) on IOError."""
        bad_path = str(tmp_path / "nonexistent_dir" / "prefs.json")
        mgr = UserPreferenceManager(storage_path=bad_path)

        result = mgr.save_to_disk()

        assert result is False

    def test_save_to_disk_ioerror_stores_error(self, tmp_path):
        """save_to_disk() should store error message on IOError."""
        bad_path = str(tmp_path / "nonexistent_dir" / "prefs.json")
        mgr = UserPreferenceManager(storage_path=bad_path)
        mgr.save_to_disk()

        assert mgr._last_save_error is not None

    def test_bump_update_calls_save(self, tmp_path):
        """_bump_update() (called by set_language etc.) should auto-save to disk."""
        import json
        path = str(tmp_path / "prefs.json")
        mgr = UserPreferenceManager(storage_path=path)

        mgr.set_language("hindi")

        with open(path) as f:
            data = json.load(f)
        assert data["language"] == "hindi"

    def test_successful_save_clears_last_error(self, tmp_path):
        """After a successful save, _last_save_error should be None."""
        path = str(tmp_path / "prefs.json")
        mgr = UserPreferenceManager(storage_path=path)
        mgr._last_save_error = "stale error"

        mgr.save_to_disk()

        assert mgr._last_save_error is None
