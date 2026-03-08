"""
Intent Detection System — Detect user intent from keywords and context.

Implements:
- detect_intent(): Match user input to 40+ use cases with confidence scoring
- mode_gate_ui(): Show Small Talk vs Guided mode selection buttons
- Continuous detection: Run intent detection within any conversation context
"""

from life_brain.intent.detector import IntentDetector
from life_brain.intent.mode_gate import mode_gate_ui, format_mode_buttons

__all__ = [
    "IntentDetector",
    "mode_gate_ui",
    "format_mode_buttons",
]
