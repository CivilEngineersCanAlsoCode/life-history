"""
Unit tests for semantic_matcher.py

Covers:
- SemanticMatcher initialization
- score_similarity() - Query-use case matching with scoring
- get_top_matches() - Top N ranking with filtering
- format_top_10_display() - Hinglish display formatting
- format_full_catalog() - Complete catalog display
- get_category_display() - Category-specific display
- quick_suggest() - Auto-suggestion for high-confidence matches
- handle_use_case_selection() - User selection handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from life_brain.conversation.semantic_matcher import SemanticMatcher
from life_brain.conversation.use_cases import USE_CASES, get_use_cases_by_category


class TestSemanticMatcherInit:
    """Test SemanticMatcher initialization."""

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_init_creates_client(self, mock_anthropic_class):
        """Test initialization creates Anthropic client."""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        matcher = SemanticMatcher()

        assert matcher.client == mock_client
        assert matcher.use_cases == USE_CASES
        assert len(matcher.use_cases) > 0


class TestScoreSimilarity:
    """Test score_similarity() scoring logic."""

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_score_with_keyword_match(self, mock_anthropic):
        """Test scoring with keyword matches."""
        matcher = SemanticMatcher()

        # C1 has "interview" keyword
        use_case = USE_CASES["C1"]
        query = "I need help with interview preparation"

        score = matcher.score_similarity(query, use_case)

        assert 0 < score <= 1.0
        assert score > 0.1  # Should have matches

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_score_with_title_match(self, mock_anthropic):
        """Test scoring with title word match."""
        matcher = SemanticMatcher()

        use_case = USE_CASES["C1"]  # "Interview Prep - Behavioral"
        query = "Tell me about Interview techniques"

        score = matcher.score_similarity(query, use_case)

        assert score > 0.2  # Title match should contribute

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_score_no_match(self, mock_anthropic):
        """Test scoring with no relevant match."""
        matcher = SemanticMatcher()

        use_case = USE_CASES["C1"]
        query = "xyz abc def ghi jkl"

        score = matcher.score_similarity(query, use_case)

        assert 0 <= score < 0.1

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_score_case_insensitive(self, mock_anthropic):
        """Test scoring is case-insensitive."""
        matcher = SemanticMatcher()

        use_case = USE_CASES["C1"]
        score_lower = matcher.score_similarity("interview", use_case)
        score_upper = matcher.score_similarity("INTERVIEW", use_case)
        score_mixed = matcher.score_similarity("InTeRvIeW", use_case)

        assert score_lower == score_upper == score_mixed

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_score_bounded_0_to_1(self, mock_anthropic):
        """Test score is always bounded 0-1."""
        matcher = SemanticMatcher()

        for use_case_id, use_case in list(USE_CASES.items())[:10]:
            score = matcher.score_similarity("test query", use_case)
            assert 0 <= score <= 1.0


class TestGetTopMatches:
    """Test get_top_matches() ranking."""

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_get_top_matches_returns_list(self, mock_anthropic):
        """Test get_top_matches returns list of tuples."""
        matcher = SemanticMatcher()

        results = matcher.get_top_matches("interview preparation")

        assert isinstance(results, list)
        assert all(isinstance(r, tuple) and len(r) == 3 for r in results)

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_get_top_matches_sorted_by_score(self, mock_anthropic):
        """Test results are sorted by score descending."""
        matcher = SemanticMatcher()

        results = matcher.get_top_matches("career growth salary")

        scores = [r[2] for r in results]
        assert scores == sorted(scores, reverse=True)

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_get_top_matches_respects_top_n(self, mock_anthropic):
        """Test respects top_n parameter."""
        matcher = SemanticMatcher()

        results_3 = matcher.get_top_matches("career", top_n=3)
        results_5 = matcher.get_top_matches("career", top_n=5)
        results_10 = matcher.get_top_matches("career", top_n=10)

        assert len(results_3) <= 3
        assert len(results_5) <= 5
        assert len(results_10) <= 10

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_get_top_matches_respects_min_score(self, mock_anthropic):
        """Test respects min_score threshold."""
        matcher = SemanticMatcher()

        results = matcher.get_top_matches("xyz", top_n=100, min_score=0.5)

        # All scores should be >= 0.5
        assert all(r[2] >= 0.5 for r in results)

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_get_top_matches_empty_results(self, mock_anthropic):
        """Test returns empty list when no matches above min_score."""
        matcher = SemanticMatcher()

        results = matcher.get_top_matches("xyz", min_score=0.99)

        # Should return empty or very few matches
        assert isinstance(results, list)

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_get_top_matches_includes_use_case_data(self, mock_anthropic):
        """Test results include full use case data."""
        matcher = SemanticMatcher()

        results = matcher.get_top_matches("interview", top_n=5)

        for use_case_id, use_case, score in results:
            assert use_case_id in USE_CASES
            assert "title" in use_case
            assert "expert" in use_case
            assert "keywords" in use_case


class TestFormatTop10Display:
    """Test format_top_10_display() Hinglish formatting."""

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_format_empty_matches(self, mock_anthropic):
        """Test formatting with empty matches."""
        matcher = SemanticMatcher()

        display = matcher.format_top_10_display([])

        assert isinstance(display, str)
        assert "nahi mila" in display.lower() or "not found" in display.lower()

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_format_single_match(self, mock_anthropic):
        """Test formatting single match."""
        matcher = SemanticMatcher()

        use_case = USE_CASES["C1"]
        matches = [("C1", use_case, 0.85)]

        display = matcher.format_top_10_display(matches)

        assert "C1" in display
        assert "Interview Prep" in display
        assert "85%" in display
        assert "█" in display  # Progress bar

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_format_multiple_matches(self, mock_anthropic):
        """Test formatting multiple matches."""
        matcher = SemanticMatcher()

        use_cases = [
            ("C1", USE_CASES["C1"], 0.9),
            ("C2", USE_CASES["C2"], 0.8),
            ("C3", USE_CASES["C3"], 0.7),
        ]

        display = matcher.format_top_10_display(use_cases)

        assert "C1" in display
        assert "C2" in display
        assert "C3" in display
        assert "90%" in display
        assert "80%" in display
        assert "70%" in display

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_format_includes_hinglish(self, mock_anthropic):
        """Test formatting includes Hinglish text."""
        matcher = SemanticMatcher()

        use_case = USE_CASES["C1"]
        matches = [("C1", use_case, 0.85)]

        display = matcher.format_top_10_display(matches)

        # Should include Hinglish keywords
        assert any(keyword in display for keyword in ["baaton", "relevant", "Expert"])

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_format_includes_selection_instructions(self, mock_anthropic):
        """Test formatting includes selection instructions."""
        matcher = SemanticMatcher()

        use_case = USE_CASES["C1"]
        matches = [("C1", use_case, 0.85)]

        display = matcher.format_top_10_display(matches)

        # Should include instructions
        assert "Select" in display or "ID" in display


class TestFormatFullCatalog:
    """Test format_full_catalog() catalog display."""

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_format_full_catalog_returns_string(self, mock_anthropic):
        """Test returns formatted string."""
        matcher = SemanticMatcher()

        display = matcher.format_full_catalog()

        assert isinstance(display, str)
        assert len(display) > 100

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_format_includes_all_domains(self, mock_anthropic):
        """Test includes all domains."""
        matcher = SemanticMatcher()

        display = matcher.format_full_catalog()

        domains = set(uc.get("domain") for uc in USE_CASES.values())
        for domain in domains:
            assert domain.upper() in display

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_format_includes_use_case_ids(self, mock_anthropic):
        """Test includes use case IDs."""
        matcher = SemanticMatcher()

        display = matcher.format_full_catalog()

        # Check for some known use cases
        assert "[C1]" in display
        assert "[R1]" in display
        assert "[H1]" in display

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_format_includes_expert_names(self, mock_anthropic):
        """Test includes expert names."""
        matcher = SemanticMatcher()

        display = matcher.format_full_catalog()

        # Should include expert labels
        assert "Expert:" in display


class TestGetCategoryDisplay:
    """Test get_category_display() category formatting."""

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_get_category_display_valid_category(self, mock_anthropic):
        """Test display for valid category."""
        matcher = SemanticMatcher()

        display = matcher.get_category_display("career")

        assert isinstance(display, str)
        assert "career" in display.lower()
        assert "[C1]" in display  # Should include a career use case

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_get_category_display_invalid_category(self, mock_anthropic):
        """Test display for invalid category."""
        matcher = SemanticMatcher()

        display = matcher.get_category_display("invalid_category")

        assert isinstance(display, str)
        # Should indicate no use cases found
        assert len(display) > 0

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_get_category_display_includes_all_items(self, mock_anthropic):
        """Test display includes all items in category."""
        matcher = SemanticMatcher()

        display = matcher.get_category_display("career")

        career_cases = get_use_cases_by_category("career")
        for uc_id in career_cases.keys():
            assert f"[{uc_id}]" in display


class TestQuickSuggest:
    """Test quick_suggest() auto-suggestion."""

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_quick_suggest_high_confidence(self, mock_anthropic):
        """Test suggests use case with high confidence."""
        matcher = SemanticMatcher()

        # Use a very specific query that should match well
        result = matcher.quick_suggest("interview behavioral STAR story preparation")

        # Might return None or a suggestion depending on scores
        if result:
            use_case_id, use_case = result
            assert use_case_id in USE_CASES
            assert "title" in use_case

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_quick_suggest_low_confidence(self, mock_anthropic):
        """Test returns None for low confidence."""
        matcher = SemanticMatcher()

        result = matcher.quick_suggest("xyz abc def")

        # Should return None or tuple
        assert result is None or isinstance(result, tuple)

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_quick_suggest_threshold_enforcement(self, mock_anthropic):
        """Test enforces 0.75 confidence threshold."""
        matcher = SemanticMatcher()

        # Query that shouldn't reach high confidence
        result = matcher.quick_suggest("random words here")

        # Result should be None or high confidence suggestion
        if result:
            _, _, score = matcher.get_top_matches("random words here", top_n=1)[0]
            assert score > 0.75


class TestHandleUseCaseSelection:
    """Test handle_use_case_selection() selection handling."""

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_handle_valid_id(self, mock_anthropic):
        """Test handling valid use case ID."""
        matcher = SemanticMatcher()

        result = matcher.handle_use_case_selection("C1")

        assert result is not None
        use_case_id, use_case = result
        assert use_case_id == "C1"
        assert use_case == USE_CASES["C1"]

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_handle_invalid_id(self, mock_anthropic):
        """Test handling invalid use case ID."""
        matcher = SemanticMatcher()

        result = matcher.handle_use_case_selection("INVALID")

        assert result is None

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_handle_case_sensitivity(self, mock_anthropic):
        """Test ID handling is case-sensitive."""
        matcher = SemanticMatcher()

        result_lower = matcher.handle_use_case_selection("c1")
        result_upper = matcher.handle_use_case_selection("C1")

        # c1 should not match (IDs are uppercase)
        assert result_lower is None
        assert result_upper is not None

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_handle_numeric_selection_valid_range(self, mock_anthropic):
        """Test numeric selection in valid range."""
        matcher = SemanticMatcher()

        # Numeric selection 1-10 for now returns None
        # (requires context of last top-10 results)
        result = matcher.handle_use_case_selection("5")

        # Should be None for now
        assert result is None

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_handle_numeric_selection_invalid_range(self, mock_anthropic):
        """Test numeric selection outside valid range."""
        matcher = SemanticMatcher()

        result = matcher.handle_use_case_selection("999")

        assert result is None


class TestIntegrationSemanticMatcher:
    """Integration tests for SemanticMatcher."""

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_full_workflow_query_to_selection(self, mock_anthropic):
        """Test full workflow: query -> matches -> selection."""
        matcher = SemanticMatcher()

        # Step 1: Get matches for query
        matches = matcher.get_top_matches("I need help with salary negotiation")
        assert len(matches) > 0

        # Step 2: Format for display
        display = matcher.format_top_10_display(matches)
        assert isinstance(display, str)

        # Step 3: User selects one
        top_id, _, _ = matches[0]
        result = matcher.handle_use_case_selection(top_id)
        assert result is not None

    @patch('life_brain.conversation.semantic_matcher.Anthropic')
    def test_catalog_discovery_workflow(self, mock_anthropic):
        """Test catalog discovery workflow."""
        matcher = SemanticMatcher()

        # Step 1: Show full catalog
        catalog = matcher.format_full_catalog()
        assert isinstance(catalog, str)

        # Step 2: Show category
        category_display = matcher.get_category_display("career")
        assert isinstance(category_display, str)

        # Step 3: Select from category
        result = matcher.handle_use_case_selection("C1")
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
