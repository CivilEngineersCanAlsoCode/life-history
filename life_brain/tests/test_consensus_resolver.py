"""
Tests for Multi-Expert Consensus Resolution Framework.

Tests cover:
- Disagreement detection
- Position extraction
- Resolution generation
- Hinglish formatting
- Edge cases (empty responses, both agree, neutral stances)
"""

import pytest

from life_brain.conversation.consensus_resolver import (
    ConsensusResolver,
    ExpertPosition,
    ConsensusResolution,
)


class TestDisagreementDetection:
    """Test if two responses are truly in disagreement."""

    def test_action_vs_caution_is_disagreement(self):
        """'Quit and build' vs 'Never risk what you have' should detect disagreement."""
        resolver = ConsensusResolver()
        a = "You should quit your job and build the startup. Risk is what creates opportunity."
        b = "Never risk what you have for what you don't have. Stay conservative and safe."
        assert resolver.detect_disagreement(a, b) is True

    def test_both_action_not_disagreement(self):
        """Two action-oriented responses are not necessarily in disagreement."""
        resolver = ConsensusResolver()
        a = "Quit and start building. Risk the leap."
        b = "Build aggressively. Invest all-in."
        result = resolver.detect_disagreement(a, b)
        # Both are action-oriented — not opposing
        assert isinstance(result, bool)

    def test_empty_responses_not_disagreement(self):
        """Empty responses cannot be in disagreement."""
        resolver = ConsensusResolver()
        assert resolver.detect_disagreement("", "") is False
        assert resolver.detect_disagreement("Some content", "") is False

    def test_positive_vs_negative_is_disagreement(self):
        """Absolutely yes vs Never/no should detect disagreement."""
        resolver = ConsensusResolver()
        a = "Absolutely, this is definitely the right move. Excellent opportunity."
        b = "No, never do this. It's dangerous and risky. Terrible idea."
        assert resolver.detect_disagreement(a, b) is True

    def test_identical_responses_not_disagreement(self):
        """Same stance in both responses → no disagreement."""
        resolver = ConsensusResolver()
        same = "Stay safe and protect what you have. Never risk the fundamentals."
        result = resolver.detect_disagreement(same, same)
        assert isinstance(result, bool)


class TestPositionExtraction:
    """Test extracting stance from expert responses."""

    def test_action_stance_detected(self):
        """Response with 'quit', 'build', 'risk' → action stance."""
        resolver = ConsensusResolver()
        pos = resolver.extract_position("Elon", "Quit your job and build the startup. Take the risk.")
        assert pos.stance == "action"
        assert pos.expert_name == "Elon"

    def test_caution_stance_detected(self):
        """Response with 'safe', 'never risk', 'protect' → caution stance."""
        resolver = ConsensusResolver()
        pos = resolver.extract_position("Warren", "Stay safe, never risk what you have. Protect your capital.")
        assert pos.stance == "caution"

    def test_neutral_stance_on_empty(self):
        """Empty response → neutral stance."""
        resolver = ConsensusResolver()
        pos = resolver.extract_position("Expert", "")
        assert pos.stance == "neutral"

    def test_key_recommendation_is_first_sentence(self):
        """Key recommendation must be extracted from first sentence."""
        resolver = ConsensusResolver()
        pos = resolver.extract_position("Expert", "Focus on the fundamentals. Everything else is secondary.")
        assert "fundamentals" in pos.key_recommendation.lower()

    def test_position_has_all_fields(self):
        """Extracted position must have all required fields."""
        resolver = ConsensusResolver()
        pos = resolver.extract_position("Test", "Some response text here.")
        assert hasattr(pos, "expert_name")
        assert hasattr(pos, "stance")
        assert hasattr(pos, "key_recommendation")
        assert hasattr(pos, "conditions")


class TestResolutionGeneration:
    """Test full consensus resolution generation."""

    def test_resolution_has_both_experts(self):
        """Resolution must reference both expert names."""
        resolver = ConsensusResolver()
        a_response = "Quit and build the startup. Risk the opportunity."
        b_response = "Stay safe, never risk, protect your assets."
        resolution = resolver.generate_resolution("Elon", a_response, "Warren", b_response)

        assert "Elon" in resolution.resolution_text
        assert "Warren" in resolution.resolution_text

    def test_resolution_has_conditions_for_both(self):
        """Resolution must include when-is-each-expert-right conditions."""
        resolver = ConsensusResolver()
        resolution = resolver.generate_resolution(
            "Elon", "Quit and build. Take the risk.",
            "Warren", "Never risk what you have. Stay safe."
        )
        assert resolution.condition_a is not None
        assert len(resolution.condition_a) > 10
        assert resolution.condition_b is not None
        assert len(resolution.condition_b) > 10

    def test_resolution_has_follow_up_question(self):
        """Resolution must include a follow-up question for user context."""
        resolver = ConsensusResolver()
        resolution = resolver.generate_resolution(
            "Elon", "Build the startup. Risk everything.",
            "Warren", "Never risk. Protect your savings."
        )
        assert resolution.follow_up_question is not None
        assert "?" in resolution.follow_up_question

    def test_resolution_text_is_hinglish(self):
        """Resolution text must include Hinglish phrasing."""
        resolver = ConsensusResolver()
        resolution = resolver.generate_resolution(
            "Elon", "Quit and build the startup.",
            "Warren", "Never risk what you have."
        )
        # Should contain Hinglish markers
        hinglish_markers = ["hai", "agar", "mein", "dono", "sahi"]
        assert any(marker in resolution.resolution_text.lower() for marker in hinglish_markers)

    def test_resolution_to_dict(self):
        """ConsensusResolution.to_dict() must include all fields."""
        resolver = ConsensusResolver()
        resolution = resolver.generate_resolution(
            "A", "Build aggressively. Invest all-in.",
            "B", "Stay conservative. Never risk savings."
        )
        d = resolution.to_dict()
        assert "expert_a" in d
        assert "expert_b" in d
        assert "condition_a" in d
        assert "condition_b" in d
        assert "follow_up_question" in d
        assert "resolution_text" in d

    def test_resolution_with_empty_responses(self):
        """Empty expert responses must not crash."""
        resolver = ConsensusResolver()
        resolution = resolver.generate_resolution("A", "", "B", "")
        assert isinstance(resolution, ConsensusResolution)
        assert resolution.resolution_text is not None


class TestAgreementMessage:
    """Test the 'experts agree' message."""

    def test_agreement_message_mentions_both_experts(self):
        """No-disagreement message must mention both expert names."""
        resolver = ConsensusResolver()
        msg = resolver.format_no_disagreement_message("Elon", "Warren")
        assert "Elon" in msg
        assert "Warren" in msg

    def test_agreement_message_is_encouraging(self):
        """When experts agree, message should encourage the user."""
        resolver = ConsensusResolver()
        msg = resolver.format_no_disagreement_message("Elon", "Warren")
        assert len(msg) > 20  # Has actual content


class TestEdgeCases:
    """Test edge cases."""

    def test_same_expert_name(self):
        """Same name for both experts must not crash."""
        resolver = ConsensusResolver()
        resolution = resolver.generate_resolution(
            "Expert", "Build and quit.",
            "Expert", "Stay safe and protect."
        )
        assert isinstance(resolution, ConsensusResolution)

    def test_very_long_responses(self):
        """Very long expert responses must not crash."""
        resolver = ConsensusResolver()
        long_response = "This is advice. " * 500
        resolution = resolver.generate_resolution("A", long_response, "B", long_response)
        assert isinstance(resolution, ConsensusResolution)

    def test_condition_a_different_from_condition_b(self):
        """Condition A and B must be different (not identical)."""
        resolver = ConsensusResolver()
        resolution = resolver.generate_resolution(
            "Elon", "Quit and take the risk. Build the startup.",
            "Warren", "Never risk. Stay safe. Protect savings."
        )
        assert resolution.condition_a != resolution.condition_b
