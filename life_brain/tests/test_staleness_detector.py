"""
Tests for staleness detection and auto-expiry.

Tests cover:
- Expiry date computation by domain
- is_stale() logic
- Collection-level staleness check
- Review prompt formatting
- User response handling
- Edge cases (no collection, empty docs, missing dates)
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from life_brain.truth.staleness_detector import (
    StalenessDetector,
    StaleDocument,
    StalenessCheckResult,
    EXPIRY_DAYS_BY_DOMAIN,
    DEFAULT_EXPIRY_DAYS,
)


class TestExpiryComputation:
    """Test domain-based expiry date computation."""

    def test_finance_expiry_is_365_days(self):
        """Finance domain → 365 days expiry."""
        detector = StalenessDetector()
        stored = datetime(2024, 1, 1).isoformat()
        expiry = detector.compute_expiry_date("finance", stored)
        expiry_dt = datetime.fromisoformat(expiry)
        assert (expiry_dt - datetime(2024, 1, 1)).days == 365

    def test_health_expiry_is_180_days(self):
        """Health domain → 180 days expiry."""
        detector = StalenessDetector()
        stored = datetime(2024, 1, 1).isoformat()
        expiry = detector.compute_expiry_date("health", stored)
        expiry_dt = datetime.fromisoformat(expiry)
        assert (expiry_dt - datetime(2024, 1, 1)).days == 180

    def test_career_expiry_is_730_days(self):
        """Career domain → 730 days (2 years) expiry."""
        detector = StalenessDetector()
        stored = datetime(2024, 1, 1).isoformat()
        expiry = detector.compute_expiry_date("career", stored)
        expiry_dt = datetime.fromisoformat(expiry)
        assert (expiry_dt - datetime(2024, 1, 1)).days == 730

    def test_personal_growth_expiry_is_5_years(self):
        """Personal growth domain → 1825 days (5 years)."""
        detector = StalenessDetector()
        stored = datetime(2020, 1, 1).isoformat()
        expiry = detector.compute_expiry_date("personal_growth", stored)
        expiry_dt = datetime.fromisoformat(expiry)
        assert (expiry_dt - datetime(2020, 1, 1)).days == 1825

    def test_unknown_domain_uses_default(self):
        """Unknown domain uses DEFAULT_EXPIRY_DAYS."""
        detector = StalenessDetector()
        stored = datetime(2024, 1, 1).isoformat()
        expiry = detector.compute_expiry_date("nonexistent_domain", stored)
        expiry_dt = datetime.fromisoformat(expiry)
        assert (expiry_dt - datetime(2024, 1, 1)).days == DEFAULT_EXPIRY_DAYS

    def test_invalid_stored_at_does_not_crash(self):
        """Invalid stored_at date must not crash — defaults to now."""
        detector = StalenessDetector()
        expiry = detector.compute_expiry_date("career", "not-a-date")
        assert isinstance(expiry, str)
        assert len(expiry) > 0

    def test_all_configured_domains_have_expiry(self):
        """All domains in EXPIRY_DAYS_BY_DOMAIN must produce valid expiry."""
        detector = StalenessDetector()
        stored = datetime(2023, 6, 1).isoformat()
        for domain in EXPIRY_DAYS_BY_DOMAIN:
            expiry = detector.compute_expiry_date(domain, stored)
            assert isinstance(expiry, str)
            assert len(expiry) > 0


class TestIsStale:
    """Test individual staleness check logic."""

    def test_past_expiry_is_stale(self):
        """Document expired 10 days ago must be stale."""
        detector = StalenessDetector()
        past = (datetime.now() - timedelta(days=10)).isoformat()
        stale, days_overdue = detector.is_stale(past)
        assert stale is True
        assert days_overdue >= 10

    def test_future_expiry_not_stale(self):
        """Document expiring in 30 days is not stale."""
        detector = StalenessDetector()
        future = (datetime.now() + timedelta(days=30)).isoformat()
        stale, days_overdue = detector.is_stale(future)
        assert stale is False
        assert days_overdue == 0

    def test_exact_expiry_today_is_stale(self):
        """Document expiring exactly today (yesterday 23:59:59) is stale."""
        detector = StalenessDetector()
        yesterday = (datetime.now() - timedelta(seconds=1)).isoformat()
        stale, _ = detector.is_stale(yesterday)
        assert stale is True

    def test_custom_reference_date(self):
        """Staleness check with custom reference date."""
        detector = StalenessDetector()
        expiry = datetime(2025, 1, 1).isoformat()
        reference = datetime(2025, 6, 1).isoformat()  # 5 months after expiry
        stale, days_overdue = detector.is_stale(expiry, reference)
        assert stale is True
        assert days_overdue == (datetime(2025, 6, 1) - datetime(2025, 1, 1)).days

    def test_invalid_expiry_not_stale(self):
        """Invalid expiry date must not crash — returns not stale."""
        detector = StalenessDetector()
        stale, days = detector.is_stale("not-a-date")
        assert stale is False
        assert days == 0


class TestCollectionStalenessCheck:
    """Test full collection staleness scan."""

    def test_no_collection_returns_empty_result(self):
        """No collection → returns result with 0 docs checked."""
        detector = StalenessDetector(collection=None)
        result = detector.check_collection_for_stale()
        assert result.total_checked == 0
        assert result.stale_count == 0
        assert isinstance(result, StalenessCheckResult)

    def test_all_fresh_docs_no_stale(self):
        """All documents with future expiry → 0 stale."""
        mock_collection = Mock()
        future = (datetime.now() + timedelta(days=365)).isoformat()
        mock_collection.get.return_value = {
            "ids": ["doc1", "doc2"],
            "documents": ["Content 1", "Content 2"],
            "metadatas": [
                {"domain": "career", "expiry_date": future, "date": "2024-01-01"},
                {"domain": "finance", "expiry_date": future, "date": "2024-01-01"},
            ],
        }

        detector = StalenessDetector(collection=mock_collection)
        result = detector.check_collection_for_stale()

        assert result.total_checked == 2
        assert result.stale_count == 0

    def test_expired_docs_detected(self):
        """Documents with past expiry → flagged as stale."""
        mock_collection = Mock()
        past = (datetime.now() - timedelta(days=100)).isoformat()
        mock_collection.get.return_value = {
            "ids": ["doc1"],
            "documents": ["My salary is 15 lakh."],
            "metadatas": [
                {"domain": "finance", "expiry_date": past, "date": "2022-01-01"},
            ],
        }

        detector = StalenessDetector(collection=mock_collection)
        result = detector.check_collection_for_stale()

        assert result.stale_count == 1
        assert result.stale_documents[0].doc_id == "doc1"
        assert result.stale_documents[0].domain == "finance"
        assert result.stale_documents[0].days_overdue >= 100

    def test_mixed_fresh_and_stale(self):
        """Mix of fresh and stale docs → correct counts."""
        mock_collection = Mock()
        past = (datetime.now() - timedelta(days=50)).isoformat()
        future = (datetime.now() + timedelta(days=200)).isoformat()
        mock_collection.get.return_value = {
            "ids": ["old_doc", "new_doc"],
            "documents": ["Old info", "New info"],
            "metadatas": [
                {"domain": "finance", "expiry_date": past},
                {"domain": "career", "expiry_date": future},
            ],
        }

        detector = StalenessDetector(collection=mock_collection)
        result = detector.check_collection_for_stale()

        assert result.stale_count == 1
        assert result.by_domain.get("finance", 0) == 1

    def test_collection_error_returns_empty(self):
        """ChromaDB error during check → returns empty result, not crash."""
        mock_collection = Mock()
        mock_collection.get.side_effect = Exception("ChromaDB connection error")

        detector = StalenessDetector(collection=mock_collection)
        result = detector.check_collection_for_stale()

        assert result.total_checked == 0
        assert result.stale_count == 0

    def test_docs_without_expiry_date_computed_from_stored_at(self):
        """Docs without expiry_date get expiry computed from stored date."""
        mock_collection = Mock()
        old_date = "2020-01-01"  # 4+ years ago — should be stale for finance (365d)
        mock_collection.get.return_value = {
            "ids": ["doc_no_expiry"],
            "documents": ["Savings: 5 lakh rupees"],
            "metadatas": [
                {"domain": "finance", "date": old_date},  # No expiry_date
            ],
        }

        detector = StalenessDetector(collection=mock_collection)
        result = detector.check_collection_for_stale()

        assert result.stale_count == 1


class TestReviewPrompt:
    """Test review prompt formatting."""

    def test_empty_stale_list_returns_positive_message(self):
        """No stale docs → positive 'all up-to-date' message."""
        detector = StalenessDetector()
        prompt = detector.format_review_prompt([])
        assert "up-to-date" in prompt.lower() or "✅" in prompt

    def test_stale_docs_show_in_prompt(self):
        """Stale documents appear in prompt with year and preview."""
        detector = StalenessDetector()
        stale = [
            StaleDocument(
                doc_id="d1",
                domain="finance",
                content_preview="Salary 15 lakh per year",
                stored_at="2022-06-15T00:00:00",
                expiry_date="2023-06-15T00:00:00",
                days_overdue=300,
            )
        ]
        prompt = detector.format_review_prompt(stale)
        assert "2022" in prompt
        assert "Salary" in prompt
        assert "Still valid" in prompt or "[S]" in prompt

    def test_prompt_shows_max_5_docs(self):
        """Review prompt shows at most 5 stale documents."""
        detector = StalenessDetector()
        stale = [
            StaleDocument(
                doc_id=f"d{i}",
                domain="finance",
                content_preview=f"Content {i}",
                stored_at="2020-01-01T00:00:00",
                expiry_date="2021-01-01T00:00:00",
                days_overdue=500,
            )
            for i in range(10)
        ]
        prompt = detector.format_review_prompt(stale)
        # Only 5 shown
        assert prompt.count("📋") <= 5


class TestUserResponseHandling:
    """Test user review response processing."""

    def test_still_valid_resets_expiry(self):
        """Response 'still_valid' → reset expiry action."""
        detector = StalenessDetector()
        result = detector.handle_user_response("doc1", "still_valid")
        assert result["action"] == "reset_expiry"
        assert result["status"] == "ok"

    def test_s_shorthand_works(self):
        """'s' shorthand for still_valid → reset expiry."""
        detector = StalenessDetector()
        result = detector.handle_user_response("doc1", "s")
        assert result["action"] == "reset_expiry"

    def test_update_with_new_value(self):
        """Response 'update' with new_value → update_content action."""
        detector = StalenessDetector()
        result = detector.handle_user_response("doc1", "update", new_value="Salary 25 lakh")
        assert result["action"] == "update_content"
        assert result["new_value"] == "Salary 25 lakh"
        assert result["status"] == "ok"

    def test_delete_archives_not_hard_deletes(self):
        """Response 'delete' → archive action (soft delete)."""
        detector = StalenessDetector()
        result = detector.handle_user_response("doc1", "delete")
        assert result["action"] == "archive"
        assert "archived" in result["message"].lower() or "soft" in result["message"].lower()

    def test_unknown_response_returns_error(self):
        """Unknown response → error status."""
        detector = StalenessDetector()
        result = detector.handle_user_response("doc1", "random_input")
        assert result["status"] == "error"

    def test_result_always_has_doc_id(self):
        """All response types must include doc_id in result."""
        detector = StalenessDetector()
        for response in ["still_valid", "update", "delete", "unknown"]:
            result = detector.handle_user_response("test_doc", response)
            assert result["doc_id"] == "test_doc"


class TestExpiryConfig:
    """Test expiry configuration."""

    def test_get_expiry_config_returns_all_domains(self):
        """get_expiry_config must return all configured domains."""
        detector = StalenessDetector()
        config = detector.get_expiry_config()
        assert "finance" in config
        assert "health" in config
        assert "career" in config
        assert "relationships" in config

    def test_expiry_config_values_are_ints(self):
        """All expiry values must be integers (days)."""
        detector = StalenessDetector()
        config = detector.get_expiry_config()
        for domain, days in config.items():
            assert isinstance(days, int), f"Domain '{domain}' expiry is not int: {days}"
            assert days > 0
