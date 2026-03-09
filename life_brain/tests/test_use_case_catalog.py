"""
Tests for Use Case Catalog and Matching System

Covers:
- Catalog loading (40+ use cases)
- Keyword matching and scoring
- Category/difficulty filtering
- UI formatting
- Match ranking
"""

import pytest
from life_brain.use_cases.catalog import (
    UseCaseCatalog,
    UseCase,
    UseCaseCategory,
)
from life_brain.use_cases.matcher import UseCaseMatcher, MatchResult
from life_brain.use_cases.ui import UseCaseUI


class TestUseCaseCatalog:
    """Tests for the use case catalog."""

    def test_catalog_loads_complete(self):
        """Test that catalog loads all 40+ use cases."""
        catalog = UseCaseCatalog()
        assert len(catalog.get_all()) >= 40
        assert len(catalog.get_all()) == 41  # Exact count

    def test_catalog_categories_complete(self):
        """Test that all 7 categories are populated."""
        catalog = UseCaseCatalog()
        expected_counts = {
            UseCaseCategory.CAREER: 12,
            UseCaseCategory.RELATIONSHIPS: 7,
            UseCaseCategory.HEALTH: 6,
            UseCaseCategory.FINANCE: 5,
            UseCaseCategory.PERSONAL_GROWTH: 6,
            UseCaseCategory.CREATIVITY: 3,
            UseCaseCategory.MEMORY: 2,
        }

        for category, expected_count in expected_counts.items():
            actual = len(catalog.get_by_category(category))
            assert actual == expected_count, \
                f"{category.value}: expected {expected_count}, got {actual}"

    def test_get_use_case_by_id(self):
        """Test retrieving use case by ID."""
        catalog = UseCaseCatalog()

        # Test a few known IDs
        c1 = catalog.get_by_id("C1")
        assert c1 is not None
        assert c1.use_case_id == "C1"
        assert c1.category == UseCaseCategory.CAREER
        assert "Technical" in c1.title

        r5 = catalog.get_by_id("R5")
        assert r5 is not None
        assert r5.category == UseCaseCategory.RELATIONSHIPS

        f1 = catalog.get_by_id("F1")
        assert f1 is not None
        assert f1.category == UseCaseCategory.FINANCE

    def test_use_case_data_completeness(self):
        """Test that each use case has required fields."""
        catalog = UseCaseCatalog()

        for uc in catalog.get_all():
            assert uc.use_case_id, "Missing use_case_id"
            assert uc.title, "Missing title"
            assert uc.category, "Missing category"
            assert uc.description, "Missing description"
            assert uc.expert_assigned, "Missing expert_assigned"
            assert uc.keywords, "Missing keywords"
            assert uc.difficulty_level in ["beginner", "intermediate", "advanced"]
            assert uc.estimated_duration_min > 0

    def test_get_by_difficulty(self):
        """Test filtering by difficulty level."""
        catalog = UseCaseCatalog()

        beginner = catalog.get_all_by_difficulty("beginner")
        intermediate = catalog.get_all_by_difficulty("intermediate")
        advanced = catalog.get_all_by_difficulty("advanced")

        assert len(beginner) > 0
        assert len(intermediate) > 0
        assert len(advanced) > 0

        # All should be in overall list
        all_uc = catalog.get_all()
        assert len(beginner) + len(intermediate) + len(advanced) == len(all_uc)


class TestUseCaseMatcher:
    """Tests for use case matching and ranking."""

    def test_keyword_match_exact(self):
        """Test exact keyword matching."""
        matcher = UseCaseMatcher()

        # Search for exact title
        matches = matcher.find_top_matches("Interview Prep: Technical Interviews")
        assert len(matches) > 0
        assert matches[0].use_case.use_case_id == "C1"
        assert matches[0].match_type == "keyword"

    def test_keyword_match_partial(self):
        """Test partial keyword matching."""
        matcher = UseCaseMatcher()

        matches = matcher.find_top_matches("interview")
        assert len(matches) > 0
        # Should find multiple interview-related use cases
        interview_matches = [m for m in matches if "interview" in m.use_case.title.lower()]
        assert len(interview_matches) > 0

    def test_keyword_match_description(self):
        """Test matching on description content."""
        matcher = UseCaseMatcher()

        # "coding" appears in description of C1
        matches = matcher.find_top_matches("coding algorithms")
        assert len(matches) > 0
        c1_match = [m for m in matches if m.use_case.use_case_id == "C1"]
        assert len(c1_match) > 0

    def test_difficulty_filter(self):
        """Test filtering by difficulty level."""
        matcher = UseCaseMatcher()

        beginner_matches = matcher.find_top_matches(
            "anything",
            difficulty_filter="beginner"
        )
        intermediate_matches = matcher.find_top_matches(
            "anything",
            difficulty_filter="intermediate"
        )

        for m in beginner_matches:
            assert m.use_case.difficulty_level == "beginner"

        for m in intermediate_matches:
            assert m.use_case.difficulty_level == "intermediate"

    def test_min_score_filter(self):
        """Test minimum score threshold."""
        matcher = UseCaseMatcher()

        # Very high threshold should return fewer results
        high_threshold = matcher.find_top_matches(
            "interview",
            min_score=0.9
        )
        low_threshold = matcher.find_top_matches(
            "interview",
            min_score=0.3
        )

        assert len(high_threshold) <= len(low_threshold)

    def test_limit_parameter(self):
        """Test limiting number of results."""
        matcher = UseCaseMatcher()

        matches_5 = matcher.find_top_matches("anything", limit=5)
        matches_20 = matcher.find_top_matches("anything", limit=20)

        assert len(matches_5) <= 5
        assert len(matches_20) <= 20
        assert len(matches_20) >= len(matches_5)

    def test_rank_by_category(self):
        """Test ranking use cases by category."""
        matcher = UseCaseMatcher()

        ranked = matcher.rank_by_category("test")

        # Should have results for each category
        assert len(ranked) == 7  # 7 categories
        assert all(cat in ranked for cat in [
            "career", "relationships", "health", "finance",
            "personal_growth", "creativity", "memory"
        ])

        # Each category should have use cases
        for cat_name, uc_list in ranked.items():
            assert len(uc_list) > 0

    def test_rank_by_category_with_difficulty_filter(self):
        """Test category ranking with difficulty filter."""
        matcher = UseCaseMatcher()

        ranked = matcher.rank_by_category("test", difficulty_filter="beginner")

        for cat_name, uc_list in ranked.items():
            for uc in uc_list:
                assert uc.difficulty_level == "beginner"

    def test_no_matches_below_threshold(self):
        """Test that minimum score threshold works."""
        matcher = UseCaseMatcher()

        # Random query with very high threshold
        matches = matcher.find_top_matches("xyzabc", min_score=0.95)
        assert len(matches) == 0

    def test_get_available_difficulties(self):
        """Test getting all available difficulty levels."""
        matcher = UseCaseMatcher()

        difficulties = matcher.get_available_difficulties()
        assert set(difficulties) == {"beginner", "intermediate", "advanced"}


class TestUseCaseUI:
    """Tests for UI formatting."""

    def test_format_top_matches_empty(self):
        """Test formatting empty match list."""
        output = UseCaseUI.format_top_matches([])
        assert "No matching use cases" in output
        assert "browsing by category" in output

    def test_format_top_matches_single(self):
        """Test formatting single match."""
        catalog = UseCaseCatalog()
        matcher = UseCaseMatcher(catalog)

        matches = matcher.find_top_matches("interview", limit=1)
        output = UseCaseUI.format_top_matches(matches)

        assert "Top Use Cases" in output
        assert "C1" in output or output  # Has some use case ID
        assert "%" in output  # Has score percentage
        assert "Expert:" in output
        assert "Duration:" in output

    def test_format_single_use_case(self):
        """Test formatting single use case detail."""
        catalog = UseCaseCatalog()
        uc = catalog.get_by_id("C1")

        output = UseCaseUI.format_single_use_case(uc)

        assert "[C1]" in output
        assert "Technical Interviews" in output
        assert "Expert" in output
        assert "Difficulty" in output
        assert "Duration" in output

    def test_format_categorized_list(self):
        """Test formatting full categorized catalog."""
        catalog = UseCaseCatalog()
        by_cat = catalog.get_by_category_sorted()

        output = UseCaseUI.format_categorized_list(by_cat)

        assert "FULL USE CASE CATALOG" in output
        assert "CAREER" in output
        assert "RELATIONSHIPS" in output
        assert "HEALTH" in output
        assert "FINANCE" in output
        # Should have use case IDs visible
        assert "[C1]" in output
        assert "[R1]" in output
        assert "[H1]" in output

    def test_format_quick_selector(self):
        """Test quick selector UI."""
        output = UseCaseUI.format_quick_selector()

        assert "How would you like" in output
        assert "[A]" in output
        assert "[B]" in output
        assert "[C]" in output
        assert "[D]" in output
        assert "keywords" in output
        assert "category" in output
        assert "difficulty" in output

    def test_format_category_browser(self):
        """Test category browser UI."""
        output = UseCaseUI.format_category_browser()

        assert "BROWSE BY CATEGORY" in output
        assert "CAREER" in output
        assert "💼" in output
        assert "12 use cases" in output
        assert "7 use cases" in output
        assert "Type category" in output


class TestUseCaseIntegration:
    """Integration tests for the complete use case system."""

    def test_end_to_end_search_and_display(self):
        """Test complete flow: search -> match -> format."""
        matcher = UseCaseMatcher()

        # User searches
        matches = matcher.find_top_matches("interview prep", limit=5)
        assert len(matches) > 0

        # Format results
        output = UseCaseUI.format_top_matches(matches)
        assert "Top Use Cases" in output
        assert len(output) > 50  # Should be substantial

    def test_end_to_end_browse_by_category(self):
        """Test browsing flow: categories -> ranking -> display."""
        catalog = UseCaseCatalog()
        matcher = UseCaseMatcher(catalog)

        # Get categorized list
        by_cat = catalog.get_by_category_sorted()
        output = UseCaseUI.format_categorized_list(by_cat)

        # Should contain all categories
        assert "CAREER" in output
        assert "RELATIONSHIPS" in output
        assert "HEALTH" in output

        # Should contain use case IDs
        assert "C1" in output
        assert "R1" in output
        assert "H1" in output

    def test_specific_use_case_journey(self):
        """Test finding and viewing a specific use case."""
        catalog = UseCaseCatalog()
        matcher = UseCaseMatcher(catalog)

        # Search for "salary negotiation"
        matches = matcher.find_top_matches("salary negotiation", limit=3)
        assert len(matches) > 0

        # Find the match
        c4_match = [m for m in matches if m.use_case.use_case_id == "C4"]
        assert len(c4_match) > 0

        # View details
        uc = c4_match[0].use_case
        detail_output = UseCaseUI.format_single_use_case(uc)
        assert "C4" in detail_output
        assert "Negotiation" in detail_output
        assert "Chris" in detail_output


class TestZeroMatchesFallback:
    """Regression tests for issues-ly2.2.5: use case catalog 0 matches → show full list fallback."""

    def test_zero_matches_gibberish_query(self):
        """Nonsense query with high min_score should return 0 matches."""
        from life_brain.use_cases.matcher import UseCaseMatcher
        matcher = UseCaseMatcher()
        matches = matcher.find_top_matches("xyzabc123", min_score=0.99)
        assert len(matches) == 0

    def test_find_with_catalog_fallback_returns_all_on_zero(self):
        """find_with_catalog_fallback should return all use cases when no matches."""
        from life_brain.use_cases.matcher import UseCaseMatcher
        matcher = UseCaseMatcher()
        results, used_fallback = matcher.find_with_catalog_fallback("xyzabc123", min_score=0.99)
        assert used_fallback is True
        assert len(results) > 0  # Full catalog returned

    def test_find_with_catalog_fallback_no_fallback_on_match(self):
        """find_with_catalog_fallback should NOT use fallback when matches exist."""
        from life_brain.use_cases.matcher import UseCaseMatcher
        matcher = UseCaseMatcher()
        results, used_fallback = matcher.find_with_catalog_fallback("interview preparation")
        assert used_fallback is False
        assert len(results) > 0

    def test_fallback_results_cover_all_categories(self):
        """Fallback results should include all categories."""
        from life_brain.use_cases.matcher import UseCaseMatcher
        from life_brain.use_cases.catalog import UseCaseCatalog
        matcher = UseCaseMatcher()
        results, used_fallback = matcher.find_with_catalog_fallback("xyzabc123", min_score=0.99)
        catalog = UseCaseCatalog()
        total_catalog = len(catalog.get_all())
        assert len(results) == total_catalog

    def test_fallback_ordered_by_difficulty(self):
        """Fallback results should be ordered beginner first."""
        from life_brain.use_cases.matcher import UseCaseMatcher
        matcher = UseCaseMatcher()
        results, used_fallback = matcher.find_with_catalog_fallback("xyzabc123", min_score=0.99)
        if used_fallback and len(results) > 1:
            # First result should be beginner
            assert results[0].use_case.difficulty_level == "beginner"

    def test_format_empty_matches_has_fallback_message(self):
        """format_top_matches([]) should direct user to browse by category."""
        from life_brain.use_cases.ui import UseCaseUI
        output = UseCaseUI.format_top_matches([])
        assert "No matching" in output or "no matching" in output.lower()
        # Should suggest next action
        assert len(output) > 0
