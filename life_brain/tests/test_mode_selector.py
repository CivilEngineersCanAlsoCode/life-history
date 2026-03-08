"""Simple tests for Mode Selector."""
import pytest
from life_brain.conversation.mode_selector import ModeSelector, ModeUIStyle, handle_mode_selection
from life_brain.conversation.mode_gate import Mode

class TestModeSelector:
    def test_init(self):
        selector = ModeSelector()
        assert selector.style == ModeUIStyle.MENU
        assert len(selector.selection_history) == 0

    def test_handle_selection_a(self):
        selector = ModeSelector()
        result = selector.handle_selection("A")
        assert result is not None
        mode, _ = result
        assert mode == Mode.SMALL_TALK

    def test_handle_selection_b(self):
        selector = ModeSelector()
        result = selector.handle_selection("B")
        assert result is not None
        mode, _ = result
        assert mode == Mode.GUIDED

    def test_handle_selection_hinglish(self):
        selector = ModeSelector()
        result = selector.handle_selection("bas baatein")
        assert result is not None
        mode, _ = result
        assert mode == Mode.SMALL_TALK

    def test_render_menu_style(self):
        selector = ModeSelector(style=ModeUIStyle.MENU)
        output = selector.render_mode_selection()
        assert "[A]" in output
        assert "[B]" in output

    def test_render_button_style(self):
        selector = ModeSelector(style=ModeUIStyle.BUTTONS)
        output = selector.render_mode_selection()
        assert "SMALL TALK" in output
        assert "GUIDED" in output

    def test_selection_history(self):
        selector = ModeSelector()
        selector.handle_selection("A")
        selector.handle_selection("B")
        assert len(selector.selection_history) == 2

    def test_format_confirmation(self):
        selector = ModeSelector()
        msg = selector.format_mode_confirmation(Mode.SMALL_TALK)
        assert "baatein" in msg.lower()

    def test_helper_function(self):
        result = handle_mode_selection("A")
        assert result is not None
        mode, _ = result
        assert mode == Mode.SMALL_TALK
