"""Simple tests for Intent Monitor."""
import pytest
from life_brain.conversation.intent_monitor import IntentMonitor, IntentShift

class TestIntentMonitor:
    def test_init(self):
        monitor = IntentMonitor()
        assert monitor.previous_mode is None
        assert len(monitor.shift_history) == 0

    def test_small_talk_to_guided(self):
        monitor = IntentMonitor()
        monitor.detect_shift("small_talk", current_confidence=0.5)
        shift_type, _ = monitor.detect_shift("guided", current_use_case_id="C1", current_confidence=0.85)
        assert shift_type == IntentShift.SMALL_TALK_TO_GUIDED

    def test_should_prompt_on_shift(self):
        monitor = IntentMonitor()
        monitor.detect_shift("small_talk", current_confidence=0.5)
        shift_type, _ = monitor.detect_shift("guided", current_use_case_id="C1", current_confidence=0.85)
        assert monitor.should_prompt_mode_switch(shift_type) is True

    def test_analytics(self):
        monitor = IntentMonitor()
        monitor.detect_shift("small_talk", current_confidence=0.5)
        monitor.detect_shift("guided", current_use_case_id="C1", current_confidence=0.85)
        monitor.detect_shift("small_talk", current_confidence=0.6)
        
        analytics = monitor.get_shift_analytics()
        assert analytics["total_shifts"] == 3
        assert analytics["mode_switches_count"] == 2
