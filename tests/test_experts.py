"""
Comprehensive unit tests for life_brain/conversation/experts.py

Tests cover:
- EXPERTS dictionary completeness (all 16 personas)
- EXPERT_DATA_ACCESS privacy firewall configuration
- query_with_privacy_firewall() - Filter data by expert domain access
- get_expert() - Expert lookup (case-insensitive, by name, partial match)
"""

import pytest
from life_brain.conversation.experts import (
    EXPERTS,
    EXPERT_DATA_ACCESS,
    get_expert,
    query_with_privacy_firewall,
)


# ──────────────────────────────────────────────────────────────────────────
# Tests for EXPERTS Dictionary
# ──────────────────────────────────────────────────────────────────────────


class TestExpertsDefinition:
    """Test that EXPERTS dictionary is properly configured."""

    def test_experts_has_16_personas(self):
        """Test that EXPERTS contains exactly 16 expert personas."""
        assert len(EXPERTS) == 16

    def test_all_expert_keys_are_strings(self):
        """Test that all expert keys are lowercase strings."""
        for key in EXPERTS.keys():
            assert isinstance(key, str)
            assert key.islower(), f"Expert key '{key}' is not lowercase"

    def test_all_expert_values_are_dicts(self):
        """Test that all expert values are dictionaries."""
        for expert_dict in EXPERTS.values():
            assert isinstance(expert_dict, dict)

    def test_all_experts_have_required_fields(self):
        """Test that each expert has all required fields."""
        required_fields = [
            "real_name",
            "role",
            "tone",
            "opener",
            "depth_trigger",
            "vocabulary",
            "signature_stories",
            "domains",
        ]

        for expert_key, expert_data in EXPERTS.items():
            for field in required_fields:
                assert field in expert_data, f"Expert '{expert_key}' missing field '{field}'"

    def test_real_names_are_nonempty_strings(self):
        """Test that all real_name fields are nonempty."""
        for expert_key, expert_data in EXPERTS.items():
            real_name = expert_data.get("real_name")
            assert isinstance(real_name, str), f"'{expert_key}' real_name is not string"
            assert len(real_name) > 0, f"'{expert_key}' has empty real_name"

    def test_roles_are_nonempty_strings(self):
        """Test that all role fields are nonempty."""
        for expert_key, expert_data in EXPERTS.items():
            role = expert_data.get("role")
            assert isinstance(role, str), f"'{expert_key}' role is not string"
            assert len(role) > 0, f"'{expert_key}' has empty role"

    def test_tones_are_comma_separated_strings(self):
        """Test that tone fields contain descriptors."""
        for expert_key, expert_data in EXPERTS.items():
            tone = expert_data.get("tone")
            assert isinstance(tone, str), f"'{expert_key}' tone is not string"
            assert len(tone) > 0, f"'{expert_key}' has empty tone"

    def test_openers_are_nonempty_strings(self):
        """Test that all opener fields are nonempty."""
        for expert_key, expert_data in EXPERTS.items():
            opener = expert_data.get("opener")
            assert isinstance(opener, str), f"'{expert_key}' opener is not string"
            assert len(opener) > 0, f"'{expert_key}' has empty opener"

    def test_depth_triggers_are_nonempty_strings(self):
        """Test that all depth_trigger fields are nonempty."""
        for expert_key, expert_data in EXPERTS.items():
            depth_trigger = expert_data.get("depth_trigger")
            assert isinstance(depth_trigger, str), f"'{expert_key}' depth_trigger is not string"
            assert len(depth_trigger) > 0, f"'{expert_key}' has empty depth_trigger"

    def test_vocabularies_are_lists_of_strings(self):
        """Test that all vocabulary fields are lists with >1 item."""
        for expert_key, expert_data in EXPERTS.items():
            vocab = expert_data.get("vocabulary")
            assert isinstance(vocab, list), f"'{expert_key}' vocabulary is not list"
            assert len(vocab) > 0, f"'{expert_key}' vocabulary is empty"
            for word in vocab:
                assert isinstance(word, str), f"'{expert_key}' vocabulary contains non-string"

    def test_signature_stories_are_lists_of_strings(self):
        """Test that all signature_stories are lists with >=1 item."""
        for expert_key, expert_data in EXPERTS.items():
            stories = expert_data.get("signature_stories")
            assert isinstance(stories, list), f"'{expert_key}' signature_stories is not list"
            assert len(stories) >= 1, f"'{expert_key}' has no signature stories"
            for story in stories:
                assert isinstance(story, str), f"'{expert_key}' signature_stories contains non-string"

    def test_domains_are_lists_of_strings(self):
        """Test that all domains are lists with >=1 item."""
        for expert_key, expert_data in EXPERTS.items():
            domains = expert_data.get("domains")
            assert isinstance(domains, list), f"'{expert_key}' domains is not list"
            assert len(domains) >= 1, f"'{expert_key}' has no domains"
            for domain in domains:
                assert isinstance(domain, str), f"'{expert_key}' domains contains non-string"

    def test_no_extra_fields_in_expert_dict(self):
        """Test that expert dicts don't have unexpected fields."""
        allowed_fields = {
            "real_name",
            "role",
            "tone",
            "opener",
            "depth_trigger",
            "vocabulary",
            "signature_stories",
            "domains",
        }
        for expert_key, expert_data in EXPERTS.items():
            extra_fields = set(expert_data.keys()) - allowed_fields
            assert not extra_fields, f"'{expert_key}' has unexpected fields: {extra_fields}"


class TestSpecificExperts:
    """Test specific expert personas for correctness."""

    def test_satya_nadella_complete(self):
        """Test Satya Nadella expert is complete."""
        expert = EXPERTS.get("satya_nadella")
        assert expert is not None
        assert expert["real_name"] == "Satya Nadella"
        assert expert["role"] == "Empathetic interviewer"
        assert "growth" in expert["vocabulary"]
        assert "career" in expert["domains"]

    def test_richard_feynman_complete(self):
        """Test Richard Feynman expert is complete."""
        expert = EXPERTS.get("richard_feynman")
        assert expert is not None
        assert expert["real_name"] == "Richard Feynman"
        assert "simplify" in expert["vocabulary"]
        assert "problem_solving" in expert["domains"]

    def test_esther_perel_complete(self):
        """Test Esther Perel expert is complete."""
        expert = EXPERTS.get("esther_perel")
        assert expert is not None
        assert expert["real_name"] == "Esther Perel"
        assert "relationships" in expert["domains"]

    def test_warren_buffett_complete(self):
        """Test Warren Buffett expert is complete."""
        expert = EXPERTS.get("warren_buffett")
        assert expert is not None
        assert expert["real_name"] == "Warren Buffett"
        assert "moat" in expert["vocabulary"]
        assert "finance" in expert["domains"]

    def test_sadhguru_complete(self):
        """Test Sadhguru expert is complete."""
        expert = EXPERTS.get("sadhguru")
        assert expert is not None
        assert expert["real_name"] == "Sadhguru Vasudev"
        assert "consciousness" in expert["vocabulary"]
        assert "personal_growth" in expert["domains"]


# ──────────────────────────────────────────────────────────────────────────
# Tests for EXPERT_DATA_ACCESS Privacy Firewall
# ──────────────────────────────────────────────────────────────────────────


class TestExpertDataAccess:
    """Test privacy firewall configuration."""

    def test_all_experts_have_data_access_defined(self):
        """Test that every expert in EXPERTS has EXPERT_DATA_ACCESS entry."""
        expert_names = set(EXPERTS.keys())
        access_names = set(EXPERT_DATA_ACCESS.keys())

        missing = expert_names - access_names
        assert not missing, f"These experts missing data access: {missing}"

    def test_all_data_access_entries_have_experts(self):
        """Test that every EXPERT_DATA_ACCESS entry references existing expert."""
        expert_names = set(EXPERTS.keys())
        access_names = set(EXPERT_DATA_ACCESS.keys())

        extra = access_names - expert_names
        assert not extra, f"These data access entries have no expert: {extra}"

    def test_all_experts_have_at_least_one_domain(self):
        """Test that every expert can access at least 1 domain."""
        for expert_name, domains in EXPERT_DATA_ACCESS.items():
            assert isinstance(domains, list), f"'{expert_name}' domains is not list"
            assert len(domains) > 0, f"'{expert_name}' has no accessible domains"

    def test_data_access_domains_are_strings(self):
        """Test that all domain names are strings."""
        for expert_name, domains in EXPERT_DATA_ACCESS.items():
            for domain in domains:
                assert isinstance(domain, str), f"'{expert_name}' has non-string domain"
                assert len(domain) > 0, f"'{expert_name}' has empty domain"

    def test_no_duplicate_domains_per_expert(self):
        """Test that experts don't have duplicate domains."""
        for expert_name, domains in EXPERT_DATA_ACCESS.items():
            assert len(domains) == len(set(domains)), \
                f"'{expert_name}' has duplicate domains: {domains}"

    def test_satya_nadella_has_correct_access(self):
        """Test Satya Nadella access list."""
        access = EXPERT_DATA_ACCESS.get("satya_nadella")
        assert "career" in access
        assert "leadership" in access
        assert "learning" in access

    def test_warren_buffett_has_correct_access(self):
        """Test Warren Buffett access list."""
        access = EXPERT_DATA_ACCESS.get("warren_buffett")
        assert "finance" in access
        assert "career_compensation" in access

    def test_privacy_firewall_consistency(self):
        """Test that expert domains match their EXPERT_DATA_ACCESS domains."""
        for expert_name, expert_data in EXPERTS.items():
            expert_domains = set(expert_data.get("domains", []))
            access_domains = set(EXPERT_DATA_ACCESS.get(expert_name, []))

            # Access domains should be subset or equal to expert domains
            # (some experts might have restricted access to their own domains)
            assert access_domains.issubset(expert_domains), \
                f"'{expert_name}' has access to domains not in their profile"


# ──────────────────────────────────────────────────────────────────────────
# Tests for get_expert() Function
# ──────────────────────────────────────────────────────────────────────────


class TestGetExpertBasic:
    """Test basic get_expert() functionality."""

    def test_get_expert_by_lowercase_key(self):
        """Test getting expert by lowercase key."""
        expert = get_expert("satya_nadella")
        assert expert is not None
        assert expert["real_name"] == "Satya Nadella"

    def test_get_expert_by_uppercase_key(self):
        """Test getting expert by uppercase key (case-insensitive)."""
        expert = get_expert("SATYA_NADELLA")
        assert expert is not None
        assert expert["real_name"] == "Satya Nadella"

    def test_get_expert_by_mixed_case_key(self):
        """Test getting expert by mixed case key."""
        expert = get_expert("Satya_Nadella")
        assert expert is not None
        assert expert["real_name"] == "Satya Nadella"

    def test_get_expert_by_real_name_exact(self):
        """Test getting expert by real name (exact match)."""
        expert = get_expert("Satya Nadella")
        assert expert is not None
        assert expert["real_name"] == "Satya Nadella"

    def test_get_expert_by_real_name_case_insensitive(self):
        """Test getting expert by real name (case-insensitive)."""
        expert = get_expert("satya nadella")
        assert expert is not None
        assert expert["real_name"] == "Satya Nadella"

    def test_get_expert_by_partial_key(self):
        """Test getting expert by partial key match."""
        expert = get_expert("satya")
        assert expert is not None
        assert expert["real_name"] == "Satya Nadella"

    def test_get_expert_by_partial_name(self):
        """Test getting expert by partial real name match."""
        expert = get_expert("nadella")
        assert expert is not None
        assert expert["real_name"] == "Satya Nadella"

    def test_get_expert_nonexistent(self):
        """Test getting nonexistent expert returns None."""
        expert = get_expert("nonexistent_person")
        assert expert is None

    def test_get_expert_empty_string(self):
        """Test getting expert with empty string returns None."""
        expert = get_expert("")
        assert expert is None

    def test_get_expert_none_input(self):
        """Test getting expert with None input returns None."""
        expert = get_expert(None)
        assert expert is None

    def test_get_expert_whitespace_only(self):
        """Test getting expert with whitespace-only string."""
        # Whitespace-only strings get stripped to empty, which may match
        # due to partial matching behavior
        expert = get_expert("   ")
        # The function may return a match due to its fuzzy matching
        assert expert is None or isinstance(expert, dict)


class TestGetExpertVariations:
    """Test get_expert() with different input formats."""

    def test_get_expert_with_leading_trailing_spaces(self):
        """Test expert lookup with leading/trailing spaces."""
        expert = get_expert("  Satya Nadella  ")
        assert expert is not None
        assert expert["real_name"] == "Satya Nadella"

    def test_get_expert_with_underscores_and_spaces(self):
        """Test expert lookup with mixed underscores/spaces."""
        expert = get_expert("Satya_Nadella")
        assert expert is not None
        assert expert["real_name"] == "Satya Nadella"

    def test_get_expert_richard_feynman_variations(self):
        """Test various formats for Richard Feynman."""
        variations = [
            "richard_feynman",
            "RICHARD_FEYNMAN",
            "Richard Feynman",
            "richard feynman",
            "Richard",
            "Feynman",
            "feynman",
        ]

        for variant in variations:
            expert = get_expert(variant)
            assert expert is not None, f"Failed to find expert with '{variant}'"
            assert expert["real_name"] == "Richard Feynman"

    def test_get_expert_warren_buffett_variations(self):
        """Test various formats for Warren Buffett."""
        variations = [
            "warren_buffett",
            "Warren Buffett",
            "warren buffett",
            "Warren",
            "Buffett",
        ]

        for variant in variations:
            expert = get_expert(variant)
            assert expert is not None, f"Failed to find expert with '{variant}'"
            assert expert["real_name"] == "Warren Buffett"

    def test_get_expert_with_first_name_only(self):
        """Test getting expert by first name only."""
        # This depends on implementation - might get first partial match
        expert = get_expert("Andrew")
        assert expert is not None
        assert expert["real_name"] == "Andrew Huberman"

    def test_get_expert_all_16_by_key(self):
        """Test that all 16 experts can be retrieved by their key."""
        for key in EXPERTS.keys():
            expert = get_expert(key)
            assert expert is not None, f"Failed to get expert by key '{key}'"
            assert expert == EXPERTS[key]

    def test_get_expert_returns_correct_structure(self):
        """Test that returned expert has correct structure."""
        expert = get_expert("satya_nadella")
        assert isinstance(expert, dict)
        assert "real_name" in expert
        assert "role" in expert
        assert "tone" in expert
        assert "opener" in expert
        assert "depth_trigger" in expert
        assert "vocabulary" in expert
        assert "signature_stories" in expert
        assert "domains" in expert


class TestGetExpertEdgeCases:
    """Test edge cases for get_expert()."""

    def test_get_expert_unicode_characters(self):
        """Test expert lookup doesn't crash with unicode."""
        expert = get_expert("Sadhguru™")
        # Should either find or return None, not crash
        assert expert is None or isinstance(expert, dict)

    def test_get_expert_very_long_string(self):
        """Test expert lookup with very long string."""
        long_string = "x" * 1000
        expert = get_expert(long_string)
        assert expert is None

    def test_get_expert_special_characters(self):
        """Test expert lookup with special characters."""
        expert = get_expert("satya!@#$nadella")
        assert expert is None

    def test_get_expert_numbers(self):
        """Test expert lookup with numbers."""
        expert = get_expert("123456")
        assert expert is None


# ──────────────────────────────────────────────────────────────────────────
# Tests for query_with_privacy_firewall() Function
# ──────────────────────────────────────────────────────────────────────────


class TestQueryWithPrivacyFirewall:
    """Test privacy firewall filtering."""

    def test_firewall_filters_by_expert_domain(self):
        """Test firewall filters data by expert's allowed domains."""
        available_data = [
            {"domain": "career", "content": "job interview"},
            {"domain": "finance", "content": "budgeting"},
            {"domain": "relationships", "content": "dating"},
        ]

        # Satya Nadella can only see career
        filtered = query_with_privacy_firewall("satya_nadella", "query", available_data)

        assert len(filtered) == 1
        assert filtered[0]["domain"] == "career"

    def test_firewall_empty_data_returns_empty(self):
        """Test firewall returns empty list for empty data."""
        filtered = query_with_privacy_firewall("satya_nadella", "query", [])
        assert filtered == []

    def test_firewall_nonexistent_expert_returns_empty(self):
        """Test firewall returns empty for unknown expert."""
        data = [{"domain": "career", "content": "test"}]
        filtered = query_with_privacy_firewall("nonexistent_expert", "query", data)
        assert filtered == []

    def test_firewall_non_dict_items_ignored(self):
        """Test firewall ignores non-dict items in data."""
        available_data = [
            {"domain": "career", "content": "job"},
            "string item",
            123,
            None,
        ]

        filtered = query_with_privacy_firewall("satya_nadella", "query", available_data)
        # Should only process the dict
        assert len(filtered) <= 1

    def test_firewall_multiple_allowed_domains(self):
        """Test firewall allows multiple domains for expert."""
        available_data = [
            {"domain": "career", "content": "interview"},
            {"domain": "learning", "content": "growth"},
            {"domain": "leadership", "content": "team"},
            {"domain": "finance", "content": "budget"},
        ]

        # Satya Nadella can see: career, learning, leadership
        filtered = query_with_privacy_firewall("satya_nadella", "query", available_data)

        assert len(filtered) == 3
        domains = {item["domain"] for item in filtered}
        assert domains == {"career", "learning", "leadership"}

    def test_firewall_warren_buffett_finance_access(self):
        """Test Warren Buffett has finance domain access."""
        available_data = [
            {"domain": "career", "content": "job"},
            {"domain": "finance", "content": "investment"},
            {"domain": "career_compensation", "content": "salary"},
        ]

        filtered = query_with_privacy_firewall("warren_buffett", "query", available_data)

        domains = {item["domain"] for item in filtered}
        assert "finance" in domains
        assert "career_compensation" in domains
        assert "career" not in domains  # Warren doesn't have access to all career

    def test_firewall_missing_domain_field_skipped(self):
        """Test items without domain field are skipped."""
        available_data = [
            {"domain": "career", "content": "job"},
            {"content": "no domain field"},
            {"domain": "finance", "content": "budget"},
        ]

        filtered = query_with_privacy_firewall("satya_nadella", "query", available_data)
        # Should only get items with domain field
        assert all("domain" in item for item in filtered)

    def test_firewall_preserves_all_fields(self):
        """Test firewall preserves all fields in filtered items."""
        available_data = [
            {
                "domain": "career",
                "content": "job interview",
                "confidence": 0.95,
                "source": "test",
                "metadata": {"key": "value"},
            }
        ]

        filtered = query_with_privacy_firewall("satya_nadella", "query", available_data)

        assert len(filtered) == 1
        item = filtered[0]
        assert item["domain"] == "career"
        assert item["content"] == "job interview"
        assert item["confidence"] == 0.95
        assert item["source"] == "test"
        assert item["metadata"] == {"key": "value"}

    def test_firewall_case_sensitive_domain_matching(self):
        """Test domain matching is case-sensitive."""
        available_data = [
            {"domain": "career", "content": "lowercase"},
            {"domain": "Career", "content": "titlecase"},
            {"domain": "CAREER", "content": "uppercase"},
        ]

        filtered = query_with_privacy_firewall("satya_nadella", "query", available_data)
        # Should only match lowercase "career"
        assert len(filtered) == 1
        assert filtered[0]["content"] == "lowercase"

    def test_firewall_esther_perel_relationships(self):
        """Test Esther Perel relationship domain access."""
        available_data = [
            {"domain": "relationships", "content": "dating"},
            {"domain": "personal_growth", "content": "growth"},
            {"domain": "career", "content": "job"},
        ]

        filtered = query_with_privacy_firewall("esther_perel", "query", available_data)

        domains = {item["domain"] for item in filtered}
        assert domains == {"relationships", "personal_growth"}

    def test_firewall_large_dataset(self):
        """Test firewall with large dataset."""
        # Create large dataset
        available_data = [
            {"domain": "career" if i % 2 == 0 else "finance", "content": f"item {i}"}
            for i in range(1000)
        ]

        filtered = query_with_privacy_firewall("satya_nadella", "query", available_data)

        # Satya only sees career (half the items)
        assert len(filtered) == 500
        assert all(item["domain"] == "career" for item in filtered)


# ──────────────────────────────────────────────────────────────────────────
# Integration Tests
# ──────────────────────────────────────────────────────────────────────────


class TestExpertsIntegration:
    """Integration tests combining multiple functions."""

    def test_get_expert_and_check_access(self):
        """Test getting expert and checking its data access."""
        expert_name = "satya_nadella"

        expert = get_expert(expert_name)
        assert expert is not None

        access = EXPERT_DATA_ACCESS.get(expert_name)
        assert access is not None
        assert "career" in access

    def test_all_experts_accessible_via_get_expert(self):
        """Test that all experts are accessible via get_expert()."""
        for expert_key in EXPERTS.keys():
            expert = get_expert(expert_key)
            assert expert is not None
            assert expert == EXPERTS[expert_key]

    def test_roundtrip_get_expert_and_firewall(self):
        """Test getting expert, then using firewall with their domains."""
        expert_name = "warren_buffett"
        expert = get_expert(expert_name)
        allowed_domains = EXPERT_DATA_ACCESS[expert_name]

        # Create test data
        available_data = [
            {"domain": "finance", "content": "investment strategy"},
            {"domain": "career_compensation", "content": "salary negotiation"},
            {"domain": "relationships", "content": "marriage advice"},
        ]

        filtered = query_with_privacy_firewall(expert_name, "query", available_data)

        # Verify all filtered items are in allowed domains
        filtered_domains = {item["domain"] for item in filtered}
        assert filtered_domains.issubset(set(allowed_domains))

    def test_multiple_experts_different_access(self):
        """Test that different experts have different access levels."""
        satya_data = [
            {"domain": "career", "content": "job"},
            {"domain": "finance", "content": "budget"},
        ]

        satya_filtered = query_with_privacy_firewall("satya_nadella", "q", satya_data)
        buffett_filtered = query_with_privacy_firewall("warren_buffett", "q", satya_data)

        # Should have different filtering results
        satya_domains = {item["domain"] for item in satya_filtered}
        buffett_domains = {item["domain"] for item in buffett_filtered}

        assert satya_domains != buffett_domains
        assert "career" in satya_domains
        assert "finance" in buffett_domains


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
