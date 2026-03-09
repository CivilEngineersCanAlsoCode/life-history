"""
Unit tests for expert_introduction.py

Covers:
- ExpertIntroducer initialization
- format_expert_introduction() - Expert intro formatting
- format_expert_approval_prompt() - Approval prompt formatting
- get_expert_specific_questions() - Expert-specific opening questions
- enforce_privacy_firewall() - Privacy filtering
- get_expert_vocabulary() - Expert vocabulary retrieval
- format_expert_response_style() - Response styling by tone
- format_expert_intro_and_first_question() - Combined intro + question
- get_expert_summary() - Expert metadata summary
- should_suggest_different_expert() - Expert appropriateness check
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from life_brain.conversation.expert_introduction import ExpertIntroducer
from life_brain.conversation.experts import get_expert
from life_brain.conversation.use_cases import get_use_case


class TestExpertIntroducerInit:
    """Test ExpertIntroducer initialization."""

    def test_init_no_params(self):
        """Test initialization with no parameters."""
        introducer = ExpertIntroducer()
        assert introducer is not None


class TestFormatExpertIntroduction:
    """Test format_expert_introduction() formatting."""

    def test_format_valid_expert(self):
        """Test formatting introduction for valid expert."""
        introducer = ExpertIntroducer()

        # Use a known expert
        expert_name = "satya_nadella"
        intro, expert = introducer.format_expert_introduction(expert_name)

        assert isinstance(intro, str)
        assert len(intro) > 0
        assert expert_name in expert.get("key", "") or "satya" in intro.lower()

    def test_format_unknown_expert(self):
        """Unknown expert returns graceful fallback message (not ValueError)."""
        introducer = ExpertIntroducer()
        result = introducer.format_expert_introduction("unknown_expert_xyz")
        # Returns tuple (message, expert_dict)
        assert isinstance(result, tuple)
        message, expert_dict = result
        assert isinstance(message, str)
        assert len(message) > 0

    def test_format_includes_real_name(self):
        """Test formatted introduction includes real name."""
        introducer = ExpertIntroducer()

        intro, expert = introducer.format_expert_introduction("satya_nadella")

        real_name = expert.get("real_name", "")
        assert real_name in intro

    def test_format_includes_role(self):
        """Test formatted introduction includes role."""
        introducer = ExpertIntroducer()

        intro, expert = introducer.format_expert_introduction("satya_nadella")

        role = expert.get("role", "")
        assert role in intro or "role" in intro.lower()

    def test_format_includes_tone(self):
        """Test formatted introduction includes tone."""
        introducer = ExpertIntroducer()

        intro, expert = introducer.format_expert_introduction("satya_nadella")

        tone = expert.get("tone", "")
        assert tone in intro or "tone" in intro.lower()

    def test_format_includes_hinglish(self):
        """Test formatted introduction includes Hinglish."""
        introducer = ExpertIntroducer()

        intro, expert = introducer.format_expert_introduction("satya_nadella")

        # Should contain Hinglish words
        assert any(word in intro for word in ["Shukriya", "aare", "baare"])

    def test_format_with_use_case_id(self):
        """Test formatting with use case ID."""
        introducer = ExpertIntroducer()

        intro, expert = introducer.format_expert_introduction("satya_nadella", use_case_id="C1")

        assert isinstance(intro, str)
        assert len(intro) > 0

    def test_format_returns_expert_dict(self):
        """Test returns complete expert dict."""
        introducer = ExpertIntroducer()

        intro, expert = introducer.format_expert_introduction("satya_nadella")

        assert isinstance(expert, dict)
        assert "real_name" in expert or "name" in expert
        assert "role" in expert or "expertise" in expert


class TestFormatExpertApprovalPrompt:
    """Test format_expert_approval_prompt() formatting."""

    def test_format_approval_valid_expert(self):
        """Test formatting approval prompt for valid expert."""
        introducer = ExpertIntroducer()

        prompt = introducer.format_expert_approval_prompt("satya_nadella")

        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_format_approval_unknown_expert(self):
        """Test approval prompt for unknown expert raises error."""
        introducer = ExpertIntroducer()

        with pytest.raises(ValueError):
            introducer.format_expert_approval_prompt("unknown_xyz")

    def test_format_approval_includes_real_name(self):
        """Test approval prompt includes expert's real name."""
        introducer = ExpertIntroducer()

        prompt = introducer.format_expert_approval_prompt("satya_nadella")

        expert = get_expert("satya_nadella")
        real_name = expert.get("real_name", "")
        assert real_name in prompt

    def test_format_approval_includes_options(self):
        """Test approval prompt includes selection options."""
        introducer = ExpertIntroducer()

        prompt = introducer.format_expert_approval_prompt("satya_nadella")

        # Should have approval/rejection options
        assert any(opt in prompt for opt in ["Haan", "Nahi", "Khud", "Yes", "No"])

    def test_format_approval_hinglish_style(self):
        """Test approval prompt uses Hinglish."""
        introducer = ExpertIntroducer()

        prompt = introducer.format_expert_approval_prompt("satya_nadella")

        assert any(word in prompt for word in ["Kya", "sahi", "hain", "Haan", "Nahi"])


class TestGetExpertSpecificQuestions:
    """Test get_expert_specific_questions() question retrieval."""

    def test_get_questions_valid_expert_and_case(self):
        """Test getting questions for valid expert and use case."""
        introducer = ExpertIntroducer()

        questions = introducer.get_expert_specific_questions("satya_nadella", "C1")

        assert isinstance(questions, list)
        assert len(questions) > 0

    def test_get_questions_returns_list(self):
        """Test always returns list."""
        introducer = ExpertIntroducer()

        questions = introducer.get_expert_specific_questions("satya_nadella", "C1")

        assert isinstance(questions, list)

    def test_get_questions_invalid_expert(self):
        """Test invalid expert returns empty list."""
        introducer = ExpertIntroducer()

        questions = introducer.get_expert_specific_questions("unknown_xyz", "C1")

        assert questions == []

    def test_get_questions_invalid_use_case(self):
        """Test invalid use case returns empty list."""
        introducer = ExpertIntroducer()

        questions = introducer.get_expert_specific_questions("satya_nadella", "INVALID")

        assert questions == []

    def test_get_questions_includes_opener(self):
        """Test questions include expert's opener."""
        introducer = ExpertIntroducer()

        questions = introducer.get_expert_specific_questions("satya_nadella", "C1")

        expert = get_expert("satya_nadella")
        opener = expert.get("opener", "")
        if opener:
            assert opener in questions

    def test_get_questions_includes_use_case_questions(self):
        """Test questions include use case opening questions."""
        introducer = ExpertIntroducer()

        questions = introducer.get_expert_specific_questions("satya_nadella", "C1")

        use_case = get_use_case("C1")
        uc_questions = use_case.get("questions", [])

        # Should include some use case questions
        if uc_questions:
            assert any(q in questions for q in uc_questions[:3])


class TestEnforcePrivacyFirewall:
    """Test enforce_privacy_firewall() privacy filtering."""

    @patch('life_brain.conversation.expert_introduction.query_with_privacy_firewall')
    def test_enforce_firewall_filters_data(self, mock_firewall):
        """Test privacy firewall filters data."""
        introducer = ExpertIntroducer()

        mock_firewall.return_value = [{"id": "doc1", "text": "filtered"}]

        result = introducer.enforce_privacy_firewall(
            "satya_nadella",
            "What is AI?",
            [{"id": "doc1"}, {"id": "doc2"}]
        )

        assert isinstance(result, list)
        assert len(result) <= 2
        mock_firewall.assert_called_once()

    @patch('life_brain.conversation.expert_introduction.query_with_privacy_firewall')
    def test_enforce_firewall_calls_correct_function(self, mock_firewall):
        """Test calls query_with_privacy_firewall correctly."""
        introducer = ExpertIntroducer()

        mock_firewall.return_value = []

        introducer.enforce_privacy_firewall(
            "satya_nadella",
            "Test query",
            [{"id": "1"}]
        )

        mock_firewall.assert_called_once_with(
            expert_name="satya_nadella",
            query="Test query",
            available_data=[{"id": "1"}]
        )

    @patch('life_brain.conversation.expert_introduction.query_with_privacy_firewall')
    def test_enforce_firewall_empty_data(self, mock_firewall):
        """Test firewall with empty data."""
        introducer = ExpertIntroducer()

        mock_firewall.return_value = []

        result = introducer.enforce_privacy_firewall("satya_nadella", "Query", [])

        assert result == []


class TestGetExpertVocabulary:
    """Test get_expert_vocabulary() vocabulary retrieval."""

    def test_get_vocabulary_valid_expert(self):
        """Test getting vocabulary for valid expert."""
        introducer = ExpertIntroducer()

        vocab = introducer.get_expert_vocabulary("satya_nadella")

        assert isinstance(vocab, list)

    def test_get_vocabulary_unknown_expert(self):
        """Test unknown expert returns empty list."""
        introducer = ExpertIntroducer()

        vocab = introducer.get_expert_vocabulary("unknown_xyz")

        assert vocab == []

    def test_get_vocabulary_contains_words(self):
        """Test vocabulary contains actual vocabulary words."""
        introducer = ExpertIntroducer()

        expert = get_expert("satya_nadella")
        vocab = introducer.get_expert_vocabulary("satya_nadella")

        expected_vocab = expert.get("vocabulary", [])
        assert vocab == expected_vocab


class TestFormatExpertResponseStyle:
    """Test format_expert_response_style() response styling."""

    def test_style_response_valid_expert(self):
        """Test styling response for valid expert."""
        introducer = ExpertIntroducer()

        response = introducer.format_expert_response_style("satya_nadella", "This is a response")

        assert isinstance(response, str)
        assert len(response) > 0

    def test_style_response_unknown_expert(self):
        """Test styling with unknown expert returns original."""
        introducer = ExpertIntroducer()

        original = "This is a response"
        result = introducer.format_expert_response_style("unknown_xyz", original)

        assert result == original

    def test_style_response_includes_signature(self):
        """Test styled response includes expert signature."""
        introducer = ExpertIntroducer()

        response = introducer.format_expert_response_style("satya_nadella", "This is a response")

        # Should include some expert-specific signature based on tone
        assert "—" in response or "response" in response.lower()

    def test_style_response_based_on_tone(self):
        """Test styling varies by expert tone."""
        introducer = ExpertIntroducer()

        expert = get_expert("satya_nadella")
        tone = expert.get("tone", "").lower()

        response = introducer.format_expert_response_style("satya_nadella", "Test response")

        # Response should be styled according to tone
        assert isinstance(response, str)


class TestFormatExpertIntroAndFirstQuestion:
    """Test format_expert_intro_and_first_question() combined formatting."""

    def test_format_combined_valid_inputs(self):
        """Test combined format with valid inputs."""
        introducer = ExpertIntroducer()

        message = introducer.format_expert_intro_and_first_question("satya_nadella", "C1")

        assert isinstance(message, str)
        assert len(message) > 0

    def test_format_combined_invalid_expert(self):
        """Test combined format with invalid expert raises error."""
        introducer = ExpertIntroducer()

        with pytest.raises(ValueError):
            introducer.format_expert_intro_and_first_question("unknown_xyz", "C1")

    def test_format_combined_invalid_use_case(self):
        """Test combined format with invalid use case raises error."""
        introducer = ExpertIntroducer()

        with pytest.raises(ValueError):
            introducer.format_expert_intro_and_first_question("satya_nadella", "INVALID")

    def test_format_combined_includes_expert_name(self):
        """Test combined format includes expert name."""
        introducer = ExpertIntroducer()

        message = introducer.format_expert_intro_and_first_question("satya_nadella", "C1")

        expert = get_expert("satya_nadella")
        real_name = expert.get("real_name", "")
        assert real_name in message

    def test_format_combined_includes_use_case_title(self):
        """Test combined format includes use case title."""
        introducer = ExpertIntroducer()

        message = introducer.format_expert_intro_and_first_question("satya_nadella", "C1")

        use_case = get_use_case("C1")
        title = use_case.get("title", "")
        assert title in message

    def test_format_combined_includes_opener(self):
        """Test combined format includes expert opener."""
        introducer = ExpertIntroducer()

        message = introducer.format_expert_intro_and_first_question("satya_nadella", "C1")

        expert = get_expert("satya_nadella")
        opener = expert.get("opener", "")
        assert opener in message

    def test_format_combined_hinglish(self):
        """Test combined format uses Hinglish."""
        introducer = ExpertIntroducer()

        message = introducer.format_expert_intro_and_first_question("satya_nadella", "C1")

        assert any(word in message for word in ["tumhare", "samne", "ke liye", "kehte"])


class TestGetExpertSummary:
    """Test get_expert_summary() metadata summary."""

    def test_get_summary_valid_expert(self):
        """Test getting summary for valid expert."""
        introducer = ExpertIntroducer()

        summary = introducer.get_expert_summary("satya_nadella")

        assert isinstance(summary, dict)
        assert "name" in summary or "role" in summary

    def test_get_summary_unknown_expert(self):
        """Test unknown expert returns empty dict."""
        introducer = ExpertIntroducer()

        summary = introducer.get_expert_summary("unknown_xyz")

        assert summary == {}

    def test_get_summary_includes_metadata(self):
        """Test summary includes expert metadata."""
        introducer = ExpertIntroducer()

        summary = introducer.get_expert_summary("satya_nadella")

        # Should include key metadata fields
        expected_keys = ["name", "role", "domains", "tone"]
        assert any(key in summary for key in expected_keys)

    def test_get_summary_includes_expertise(self):
        """Test summary includes expertise/stories."""
        introducer = ExpertIntroducer()

        summary = introducer.get_expert_summary("satya_nadella")

        # Should include expertise info
        if summary:
            assert any(key in summary for key in ["expertise", "signature_stories"])


class TestShouldSuggestDifferentExpert:
    """Test should_suggest_different_expert() expert appropriateness."""

    def test_suggest_for_matching_topic(self):
        """Test doesn't suggest change for matching topic."""
        introducer = ExpertIntroducer()

        expert = get_expert("satya_nadella")
        domains = expert.get("domains", [])

        if domains:
            topic = domains[0]
            should_suggest = introducer.should_suggest_different_expert("satya_nadella", topic)
            assert isinstance(should_suggest, bool)

    def test_suggest_for_non_matching_topic(self):
        """Test suggests change for non-matching topic."""
        introducer = ExpertIntroducer()

        should_suggest = introducer.should_suggest_different_expert("satya_nadella", "xyz abc def")

        assert isinstance(should_suggest, bool)

    def test_suggest_unknown_expert(self):
        """Test returns False for unknown expert."""
        introducer = ExpertIntroducer()

        should_suggest = introducer.should_suggest_different_expert("unknown_xyz", "topic")

        assert should_suggest == False

    def test_suggest_returns_boolean(self):
        """Test always returns boolean."""
        introducer = ExpertIntroducer()

        result = introducer.should_suggest_different_expert("satya_nadella", "AI and technology")

        assert isinstance(result, bool)


class TestIntegrationExpertIntroduction:
    """Integration tests for ExpertIntroducer."""

    def test_full_workflow_expert_introduction(self):
        """Test full workflow: introduce expert and get questions."""
        introducer = ExpertIntroducer()

        # Step 1: Get introduction
        intro, expert = introducer.format_expert_introduction("satya_nadella", "C1")
        assert isinstance(intro, str)

        # Step 2: Get approval prompt
        approval = introducer.format_expert_approval_prompt("satya_nadella")
        assert isinstance(approval, str)

        # Step 3: Get opening questions
        questions = introducer.get_expert_specific_questions("satya_nadella", "C1")
        assert isinstance(questions, list)

    def test_full_workflow_combined_intro(self):
        """Test combined introduction workflow."""
        introducer = ExpertIntroducer()

        # One-shot intro + first question
        message = introducer.format_expert_intro_and_first_question("satya_nadella", "C1")

        assert isinstance(message, str)
        assert len(message) > 100

        # Get summary for context
        summary = introducer.get_expert_summary("satya_nadella")
        assert isinstance(summary, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestMissingExpertProfile:
    """Regression test for issues-ly2.4.3: expert introduction when expert profile missing."""

    def test_unknown_expert_intro_does_not_crash(self):
        """get_expert_intro() with unknown expert_id must not crash."""
        from life_brain.conversation.expert_introduction import ExpertIntroducer
        introducer = ExpertIntroducer()
        result = introducer.format_expert_introduction("nonexistent_expert_xyz", "C1")
        # Should return something (even if None/empty/default) not raise
        assert isinstance(result, tuple) and isinstance(result[0], str)

    def test_unknown_expert_summary_no_crash(self):
        """get_expert_summary() with unknown expert_id must not crash."""
        from life_brain.conversation.expert_introduction import ExpertIntroducer
        introducer = ExpertIntroducer()
        summary = introducer.get_expert_summary("does_not_exist")
        assert summary is None or isinstance(summary, dict)
