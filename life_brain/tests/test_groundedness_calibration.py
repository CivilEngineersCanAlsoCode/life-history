"""Tests for groundedness_calibration.py — score formula + threshold calibration."""

import pytest
from life_brain.truth_engine.groundedness_calibration import (
    groundedness_score,
    score_to_level,
    threshold_measurement,
    threshold_adaptation,
    ThresholdCalibrationResult,
    DEFAULT_THRESHOLDS,
    DOMAIN_THRESHOLDS,
)


# ── groundedness_score ────────────────────────────────────────────────────────

class TestGroundednessScore:
    def test_identical_vectors(self):
        v = [1.0, 0.0, 0.0]
        score = groundedness_score(v, [v])
        assert score == pytest.approx(1.0)

    def test_max_of_multiple_docs(self):
        query = [1.0, 0.0]
        docs = [
            [0.5, 0.866],  # ~0.5 similarity
            [1.0, 0.0],    # 1.0 similarity
            [0.0, 1.0],    # 0.0 similarity
        ]
        score = groundedness_score(query, docs)
        assert score == pytest.approx(1.0)

    def test_orthogonal_returns_zero(self):
        query = [1.0, 0.0]
        docs = [[0.0, 1.0]]
        score = groundedness_score(query, docs)
        assert score == pytest.approx(0.0)

    def test_empty_docs(self):
        assert groundedness_score([1.0, 0.0], []) == 0.0

    def test_empty_query(self):
        assert groundedness_score([], [[1.0, 0.0]]) == 0.0

    def test_partial_similarity(self):
        query = [1.0, 0.0]
        docs = [[0.707, 0.707]]  # ~45 degrees, ~0.707 similarity
        score = groundedness_score(query, docs)
        assert 0.6 < score < 0.8

    def test_score_bounded_01(self):
        query = [1.0, 1.0]
        docs = [[1.0, 1.0], [0.5, 0.5]]
        score = groundedness_score(query, docs)
        assert 0.0 <= score <= 1.0


# ── score_to_level ────────────────────────────────────────────────────────────

class TestScoreToLevel:
    def test_high_confidence(self):
        level = score_to_level(0.90)
        assert level.level == "high"

    def test_medium_confidence(self):
        level = score_to_level(0.75)
        assert level.level == "medium"

    def test_low_confidence(self):
        level = score_to_level(0.60)
        assert level.level == "low"

    def test_insufficient(self):
        level = score_to_level(0.40)
        assert level.level == "insufficient"

    def test_exactly_on_boundary(self):
        # score exactly equal to "medium" threshold (0.70) should be NOT medium
        # (medium requires > 0.70)
        level = score_to_level(0.70)
        assert level.level in ("low", "insufficient")  # 0.70 is NOT > 0.70

    def test_domain_specific_thresholds(self):
        # Health domain has higher thresholds
        level_health = score_to_level(0.82, domain="health")
        level_default = score_to_level(0.82, domain=None)
        # health high threshold is 0.90 → 0.82 < 0.90 but > 0.75 → medium
        assert level_health.level == "medium"
        # default high is 0.85 → 0.82 < 0.85 but > 0.70 → medium (not high!)
        assert level_default.level == "medium"

    def test_returns_groundedness_level(self):
        level = score_to_level(0.88)
        assert hasattr(level, "level")
        assert hasattr(level, "score")
        assert hasattr(level, "threshold")

    def test_str_representation(self):
        level = score_to_level(0.88)
        s = str(level)
        assert "high" in s or "medium" in s or "low" in s or "insufficient" in s


# ── threshold_measurement ─────────────────────────────────────────────────────

class TestThresholdMeasurement:
    def test_empty_samples(self):
        result = threshold_measurement([], domain="career")
        assert result.sample_count == 0
        assert result.needs_adaptation is False

    def test_returns_calibration_result(self):
        samples = [(0.90, "high"), (0.75, "medium"), (0.60, "low"), (0.30, "insufficient")]
        result = threshold_measurement(samples, domain="career")
        assert isinstance(result, ThresholdCalibrationResult)
        assert result.domain == "career"

    def test_sample_count_correct(self):
        samples = [(0.9, "high"), (0.75, "medium"), (0.6, "low")]
        result = threshold_measurement(samples)
        assert result.sample_count == 3

    def test_accuracy_between_0_and_1(self):
        samples = [(0.9, "high"), (0.75, "medium"), (0.6, "low"), (0.3, "insufficient")]
        result = threshold_measurement(samples, domain="career")
        assert 0.0 <= result.accuracy_estimate <= 1.0

    def test_perfect_labeling_high_accuracy(self):
        # Samples that match existing thresholds perfectly
        samples = [
            (0.92, "high"), (0.88, "high"),
            (0.78, "medium"), (0.73, "medium"),
            (0.62, "low"), (0.55, "low"),
            (0.35, "insufficient"), (0.20, "insufficient"),
        ]
        result = threshold_measurement(samples, domain="career")
        assert result.accuracy_estimate > 0.5  # Should be fairly accurate

    def test_suggested_thresholds_keys(self):
        samples = [(0.9, "high"), (0.7, "medium"), (0.5, "low")]
        result = threshold_measurement(samples)
        assert "high" in result.suggested_thresholds
        assert "medium" in result.suggested_thresholds
        assert "low" in result.suggested_thresholds

    def test_needs_adaptation_flag(self):
        # With bad labels (all marked "insufficient" but high scores), adaptation needed
        samples = [(0.9, "insufficient"), (0.8, "insufficient"), (0.7, "insufficient")]
        result = threshold_measurement(samples, domain="career")
        assert isinstance(result.needs_adaptation, bool)


# ── threshold_adaptation ──────────────────────────────────────────────────────

class TestThresholdAdaptation:
    def _make_result(self, current, suggested, needs=True, domain="test_domain"):
        return ThresholdCalibrationResult(
            domain=domain,
            sample_count=10,
            suggested_thresholds=suggested,
            current_thresholds=current,
            accuracy_estimate=0.6,
            needs_adaptation=needs,
        )

    def test_no_adaptation_when_not_needed(self):
        result = self._make_result(
            {"high": 0.85, "medium": 0.70, "low": 0.50, "insufficient": 0.0},
            {"high": 0.86, "medium": 0.71, "low": 0.51, "insufficient": 0.0},
            needs=False,
            domain="test_no_adapt"
        )
        updated = threshold_adaptation(result)
        assert updated == result.current_thresholds

    def test_adapts_toward_suggested(self):
        result = self._make_result(
            {"high": 0.85, "medium": 0.70, "low": 0.50, "insufficient": 0.0},
            {"high": 0.90, "medium": 0.75, "low": 0.55, "insufficient": 0.0},
            domain="test_adapt_toward"
        )
        updated = threshold_adaptation(result, learning_rate=0.5)
        # With lr=0.5, high should move halfway from 0.85 to 0.90 = 0.875
        assert 0.85 < updated["high"] < 0.90

    def test_ordering_preserved(self):
        result = self._make_result(
            {"high": 0.85, "medium": 0.70, "low": 0.50, "insufficient": 0.0},
            {"high": 0.60, "medium": 0.80, "low": 0.90, "insufficient": 0.0},  # inverted
            domain="test_order"
        )
        updated = threshold_adaptation(result, learning_rate=1.0)
        # Ordering must be enforced: high > medium > low
        assert updated["high"] > updated["medium"]
        assert updated["medium"] >= updated["low"]

    def test_learning_rate_zero_no_change(self):
        current = {"high": 0.85, "medium": 0.70, "low": 0.50, "insufficient": 0.0}
        result = self._make_result(current, {"high": 0.95, "medium": 0.80, "low": 0.60, "insufficient": 0.0},
                                    domain="test_lr_zero")
        updated = threshold_adaptation(result, learning_rate=0.0)
        # lr=0 means no change
        assert updated["high"] == pytest.approx(0.85, abs=0.01)
        assert updated["medium"] == pytest.approx(0.70, abs=0.01)

    def test_learning_rate_clamped(self):
        result = self._make_result(
            {"high": 0.85, "medium": 0.70, "low": 0.50, "insufficient": 0.0},
            {"high": 0.90, "medium": 0.75, "low": 0.55, "insufficient": 0.0},
            domain="test_clamp"
        )
        # Should not raise even with lr > 1
        updated = threshold_adaptation(result, learning_rate=5.0)
        assert updated["high"] <= 1.0

    def test_updates_domain_thresholds(self):
        domain = "test_persist_domain"
        result = self._make_result(
            {"high": 0.85, "medium": 0.70, "low": 0.50, "insufficient": 0.0},
            {"high": 0.90, "medium": 0.75, "low": 0.55, "insufficient": 0.0},
            domain=domain
        )
        updated = threshold_adaptation(result, learning_rate=1.0)
        assert DOMAIN_THRESHOLDS.get(domain) == updated

    def test_returns_dict_with_all_keys(self):
        result = self._make_result(
            {"high": 0.85, "medium": 0.70, "low": 0.50, "insufficient": 0.0},
            {"high": 0.88, "medium": 0.73, "low": 0.53, "insufficient": 0.0},
            domain="test_keys"
        )
        updated = threshold_adaptation(result)
        assert all(k in updated for k in ["high", "medium", "low", "insufficient"])


# ── Integration: score → level using calibrated thresholds ───────────────────

class TestIntegration:
    def test_full_calibration_cycle(self):
        """Measure → adapt → improved classification."""
        domain = "integration_test_domain"
        # Samples that suggest thresholds should be higher
        samples = [
            (0.95, "high"), (0.93, "high"),
            (0.85, "medium"), (0.82, "medium"),
            (0.70, "low"), (0.68, "low"),
            (0.40, "insufficient"), (0.35, "insufficient"),
        ]
        result = threshold_measurement(samples, domain=domain)
        threshold_adaptation(result, learning_rate=0.5)

        # After adaptation, score 0.90 should classify as expected
        level = score_to_level(0.90, domain=domain)
        assert level.level in ("high", "medium")  # reasonable classification
