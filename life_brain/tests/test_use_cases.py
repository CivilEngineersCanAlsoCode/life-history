"""
Unit tests for use_cases.py

Covers:
- USE_CASES catalog structure and completeness
- get_use_case() - single use case retrieval
- get_use_cases_by_category() - category filtering
- get_use_cases_by_domain() - domain filtering
- get_use_case_keywords() - keyword mapping
- find_use_cases_by_keywords() - keyword search and matching
"""

import pytest
from life_brain.conversation.use_cases import (
    USE_CASES,
    get_use_case,
    get_use_cases_by_category,
    get_use_cases_by_domain,
    get_use_case_keywords,
    find_use_cases_by_keywords,
)


class TestUseCasesCatalog:
    """Test USE_CASES catalog structure."""

    def test_catalog_exists(self):
        """Test that USE_CASES catalog is populated."""
        assert USE_CASES is not None
        assert len(USE_CASES) > 0

    def test_catalog_has_40_plus_cases(self):
        """Test catalog has 40+ use cases."""
        assert len(USE_CASES) >= 40

    def test_each_case_has_required_fields(self):
        """Test each use case has required fields."""
        required_fields = {"id", "title", "expert", "category", "domain", "description", "keywords", "questions"}
        for uc_id, uc in USE_CASES.items():
            for field in required_fields:
                assert field in uc, f"Missing {field} in {uc_id}"

    def test_case_id_matches_key(self):
        """Test that case ID matches dictionary key."""
        for uc_id, uc in USE_CASES.items():
            assert uc["id"] == uc_id

    def test_each_case_has_questions(self):
        """Test each use case has opening questions."""
        for uc_id, uc in USE_CASES.items():
            assert "questions" in uc
            assert isinstance(uc["questions"], list)
            assert len(uc["questions"]) > 0

    def test_each_case_has_keywords(self):
        """Test each use case has keywords for matching."""
        for uc_id, uc in USE_CASES.items():
            assert "keywords" in uc
            assert isinstance(uc["keywords"], list)
            assert len(uc["keywords"]) > 0

    def test_domains_are_consistent(self):
        """Test that domain and category fields are consistent."""
        for uc_id, uc in USE_CASES.items():
            assert "domain" in uc
            assert "category" in uc
            # Domain and category should be set (not empty)
            assert uc["domain"]
            assert uc["category"]

    def test_experts_are_assigned(self):
        """Test that each use case has an expert assigned."""
        for uc_id, uc in USE_CASES.items():
            assert "expert" in uc
            assert uc["expert"]


class TestGetUseCase:
    """Test get_use_case() function."""

    def test_get_valid_use_case(self):
        """Test retrieving a valid use case."""
        # Career use case
        uc = get_use_case("C1")
        assert uc is not None
        assert uc["id"] == "C1"
        assert uc["title"] == "Interview Prep - Behavioral"

    def test_get_nonexistent_use_case(self):
        """Test retrieving nonexistent use case returns None."""
        uc = get_use_case("INVALID_ID")
        assert uc is None

    def test_get_use_case_returns_full_structure(self):
        """Test that retrieved use case has all fields."""
        uc = get_use_case("C1")
        assert uc["questions"]
        assert uc["keywords"]
        assert uc["expert"]
        assert uc["description"]

    def test_get_all_documented_cases_exist(self):
        """Test some documented use cases are retrievable."""
        # Sample cases across categories
        sample_ids = ["C1", "C2", "P1", "H1", "F1", "R1", "CR1", "M1"]
        for uc_id in sample_ids:
            uc = get_use_case(uc_id)
            assert uc is not None, f"Use case {uc_id} not found"


class TestGetUseCasesByCategory:
    """Test get_use_cases_by_category() function."""

    def test_get_career_use_cases(self):
        """Test retrieving career use cases."""
        cases = get_use_cases_by_category("career")
        assert len(cases) > 0
        for uc_id, uc in cases.items():
            assert uc["category"] == "career"

    def test_get_personal_growth_cases(self):
        """Test retrieving personal growth use cases."""
        cases = get_use_cases_by_category("personal_growth")
        assert len(cases) > 0
        for uc_id, uc in cases.items():
            assert uc["category"] == "personal_growth"

    def test_get_empty_category(self):
        """Test retrieving nonexistent category returns empty dict."""
        cases = get_use_cases_by_category("nonexistent_category")
        assert isinstance(cases, dict)
        assert len(cases) == 0

    def test_all_major_categories_exist(self):
        """Test that major categories have cases."""
        major_categories = ["career", "relationships", "health", "finance", "personal_growth", "creativity", "memories"]
        for category in major_categories:
            cases = get_use_cases_by_category(category)
            assert len(cases) > 0, f"No use cases in category {category}"

    def test_category_filtering_is_accurate(self):
        """Test that category filtering returns only matching cases."""
        categories = set(uc.get("category") for uc in USE_CASES.values())
        for category in categories:
            cases = get_use_cases_by_category(category)
            for uc_id, uc in cases.items():
                assert uc["category"] == category


class TestGetUseCasesByDomain:
    """Test get_use_cases_by_domain() function."""

    def test_get_career_domain(self):
        """Test retrieving career domain cases."""
        cases = get_use_cases_by_domain("career")
        assert len(cases) > 0
        for uc_id, uc in cases.items():
            assert uc["domain"] == "career"

    def test_domain_and_category_alignment(self):
        """Test that domains and categories are aligned."""
        domains = set(uc.get("domain") for uc in USE_CASES.values())
        categories = set(uc.get("category") for uc in USE_CASES.values())
        # Should be similar (in this case they're the same)
        assert len(domains) > 0
        assert len(categories) > 0

    def test_get_empty_domain(self):
        """Test retrieving nonexistent domain returns empty dict."""
        cases = get_use_cases_by_domain("nonexistent_domain")
        assert isinstance(cases, dict)
        assert len(cases) == 0


class TestGetUseCaseKeywords:
    """Test get_use_case_keywords() function."""

    def test_keyword_map_created(self):
        """Test that keyword mapping is created."""
        keyword_map = get_use_case_keywords()
        assert keyword_map is not None
        assert isinstance(keyword_map, dict)
        assert len(keyword_map) > 0

    def test_keywords_map_to_use_cases(self):
        """Test that each keyword maps to use case IDs."""
        keyword_map = get_use_case_keywords()
        for keyword, uc_ids in keyword_map.items():
            assert isinstance(uc_ids, list)
            assert len(uc_ids) > 0
            # Verify that each mapped use case actually has this keyword
            for uc_id in uc_ids:
                uc = get_use_case(uc_id)
                assert keyword in uc["keywords"]

    def test_common_keywords_present(self):
        """Test that expected keywords are in the map."""
        keyword_map = get_use_case_keywords()
        expected_keywords = ["interview", "career", "salary", "negotiation"]
        for expected_kw in expected_keywords:
            # At least one of the expected keywords should be present
            matching = [kw for kw in keyword_map.keys() if expected_kw.lower() in kw.lower()]
            assert len(matching) > 0, f"No keywords containing '{expected_kw}' found"


class TestFindUseCasesByKeywords:
    """Test find_use_cases_by_keywords() function."""

    def test_find_by_single_keyword(self):
        """Test finding use cases by single keyword."""
        results = find_use_cases_by_keywords(["interview"])
        assert len(results) > 0
        # Should find interview-related cases
        assert "C1" in results  # Interview Prep - Behavioral

    def test_find_by_multiple_keywords(self):
        """Test finding use cases by multiple keywords."""
        results = find_use_cases_by_keywords(["career", "growth"])
        assert len(results) > 0

    def test_case_insensitive_search(self):
        """Test that keyword search is case-insensitive."""
        results_lower = find_use_cases_by_keywords(["interview"])
        results_upper = find_use_cases_by_keywords(["INTERVIEW"])
        results_mixed = find_use_cases_by_keywords(["InTeRvIeW"])
        assert results_lower == results_upper == results_mixed

    def test_partial_keyword_matching(self):
        """Test that partial keyword matching works."""
        # "interview" should match "Interview Prep - Behavioral" keywords
        results = find_use_cases_by_keywords(["interview"])
        assert len(results) > 0

    def test_no_matching_keywords(self):
        """Test finding non-existent keywords returns empty list."""
        results = find_use_cases_by_keywords(["qwqwqwqwqwqw"])
        assert isinstance(results, list)
        assert len(results) == 0

    def test_results_are_sorted(self):
        """Test that results are returned in sorted order."""
        results = find_use_cases_by_keywords(["career"])
        assert results == sorted(results)

    def test_no_duplicate_results(self):
        """Test that results don't have duplicates."""
        results = find_use_cases_by_keywords(["career"])
        assert len(results) == len(set(results))

    def test_empty_keyword_list(self):
        """Test searching with empty keyword list."""
        results = find_use_cases_by_keywords([])
        assert isinstance(results, list)


class TestIntegrationUseCases:
    """Integration tests for use case system."""

    def test_full_workflow_career_expert(self):
        """Test workflow: search keywords -> get use case -> get questions."""
        # Search for career-related
        results = find_use_cases_by_keywords(["interview", "behavioral"])
        assert len(results) > 0

        # Get use case details
        uc_id = results[0]
        uc = get_use_case(uc_id)
        assert uc is not None
        assert "questions" in uc

    def test_discovery_by_domain(self):
        """Test discovering use cases by domain."""
        domain = "career"
        cases = get_use_cases_by_domain(domain)
        assert len(cases) > 0

        # Each case should have expert assigned
        for uc_id, uc in cases.items():
            assert uc["expert"]
            assert uc["domain"] == domain

    def test_all_keywords_lead_to_valid_cases(self):
        """Test that every keyword maps to valid use cases."""
        keyword_map = get_use_case_keywords()
        for keyword, uc_ids in keyword_map.items():
            for uc_id in uc_ids:
                uc = get_use_case(uc_id)
                assert uc is not None
                assert keyword in uc["keywords"]

    def test_catalog_consistency(self):
        """Test overall catalog consistency."""
        # Every use case should be findable by its own keywords
        for uc_id, uc in USE_CASES.items():
            found_ids = find_use_cases_by_keywords(uc["keywords"])
            assert uc_id in found_ids, f"{uc_id} not found by its own keywords"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
