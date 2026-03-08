"""
Groundedness score formula + threshold calibration.

groundedness_score(): max cosine similarity between query and retrieved docs.
threshold_measurement(): compute optimal thresholds per domain.
threshold_adaptation(): update HIGH/MEDIUM/LOW boundaries from feedback.
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


# ── Default thresholds ────────────────────────────────────────────────────────

DEFAULT_THRESHOLDS: Dict[str, float] = {
    "high": 0.85,        # cite source confidently
    "medium": 0.70,      # caveat: "confirm karo"
    "low": 0.50,         # flag uncertainty
    "insufficient": 0.0, # no match, do not answer
}

# Per-domain threshold overrides (start from defaults)
DOMAIN_THRESHOLDS: Dict[str, Dict[str, float]] = {
    "career": {"high": 0.85, "medium": 0.70, "low": 0.50, "insufficient": 0.0},
    "finance": {"high": 0.88, "medium": 0.72, "low": 0.52, "insufficient": 0.0},
    "health": {"high": 0.90, "medium": 0.75, "low": 0.55, "insufficient": 0.0},
    "relationships": {"high": 0.80, "medium": 0.65, "low": 0.45, "insufficient": 0.0},
}


@dataclass
class GroundednessLevel:
    """Named confidence level for a groundedness score."""
    level: str          # "high", "medium", "low", "insufficient"
    score: float        # raw score (0-1)
    threshold: float    # boundary used

    def __str__(self) -> str:
        return f"{self.level} ({self.score:.3f})"


@dataclass
class ThresholdCalibrationResult:
    """Result of threshold_measurement() for a domain."""
    domain: str
    sample_count: int
    suggested_thresholds: Dict[str, float]
    current_thresholds: Dict[str, float]
    accuracy_estimate: float        # 0-1, how well current thresholds separate levels
    needs_adaptation: bool


# ── Core formula ─────────────────────────────────────────────────────────────

def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm1 * norm2)))


def groundedness_score(
    query_embed: List[float],
    doc_embeds: List[List[float]],
) -> float:
    """
    Compute groundedness score for a query against retrieved documents.

    Formula: max(cosine_sim(query, doc_i)) across all retrieved docs.

    Args:
        query_embed: Query embedding vector.
        doc_embeds: List of document embedding vectors.

    Returns:
        Groundedness score (0-1). 0 if no docs provided.
    """
    if not doc_embeds or not query_embed:
        return 0.0

    return max(_cosine_similarity(query_embed, doc) for doc in doc_embeds)


def score_to_level(
    score: float,
    domain: Optional[str] = None,
) -> GroundednessLevel:
    """
    Map a groundedness score to a named confidence level.

    Thresholds (per domain if available):
        > 0.85 → high      (cite source)
        > 0.70 → medium    (caveat)
        > 0.50 → low       (flag uncertainty)
        ≤ 0.50 → insufficient (do not answer)

    Args:
        score: Groundedness score (0-1).
        domain: Optional domain for domain-specific thresholds.

    Returns:
        GroundednessLevel with level name and threshold used.
    """
    thresholds = DOMAIN_THRESHOLDS.get(domain or "", DEFAULT_THRESHOLDS)

    if score > thresholds["high"]:
        return GroundednessLevel("high", score, thresholds["high"])
    elif score > thresholds["medium"]:
        return GroundednessLevel("medium", score, thresholds["medium"])
    elif score > thresholds["low"]:
        return GroundednessLevel("low", score, thresholds["low"])
    else:
        return GroundednessLevel("insufficient", score, thresholds["low"])


# ── Threshold calibration ─────────────────────────────────────────────────────

def threshold_measurement(
    scored_samples: List[Tuple[float, str]],
    domain: str = "",
) -> ThresholdCalibrationResult:
    """
    Measure optimal groundedness thresholds for a domain.

    Analyzes a labeled sample set to find natural score breakpoints.

    Args:
        scored_samples: List of (score, actual_quality) pairs where
            actual_quality is "high", "medium", "low", or "insufficient".
        domain: Domain name for domain-specific tuning.

    Returns:
        ThresholdCalibrationResult with suggested thresholds.
    """
    current = DOMAIN_THRESHOLDS.get(domain, DEFAULT_THRESHOLDS.copy())

    if not scored_samples:
        return ThresholdCalibrationResult(
            domain=domain,
            sample_count=0,
            suggested_thresholds=current.copy(),
            current_thresholds=current.copy(),
            accuracy_estimate=0.0,
            needs_adaptation=False,
        )

    # Group scores by actual quality
    groups: Dict[str, List[float]] = {"high": [], "medium": [], "low": [], "insufficient": []}
    for score, quality in scored_samples:
        if quality in groups:
            groups[quality].append(score)

    # Compute mean score per group
    group_means: Dict[str, float] = {}
    for level, scores in groups.items():
        if scores:
            group_means[level] = sum(scores) / len(scores)

    # Suggest thresholds as midpoints between group means
    suggested = current.copy()
    levels = ["high", "medium", "low"]
    ordered_means = [(lvl, group_means.get(lvl, current[lvl])) for lvl in levels]
    ordered_means.sort(key=lambda x: x[1], reverse=True)

    for i in range(len(ordered_means) - 1):
        upper_level = ordered_means[i][0]
        upper_mean = ordered_means[i][1]
        lower_mean = ordered_means[i + 1][1]
        midpoint = (upper_mean + lower_mean) / 2
        suggested[upper_level] = round(midpoint, 3)

    # Estimate accuracy: fraction of samples classified correctly by current thresholds
    correct = 0
    for score, quality in scored_samples:
        predicted = score_to_level(score, domain).level
        if predicted == quality:
            correct += 1
    accuracy = correct / len(scored_samples) if scored_samples else 0.0

    # Needs adaptation if accuracy < 80% or thresholds differ significantly
    needs_adaptation = accuracy < 0.80 or any(
        abs(suggested.get(k, 0) - current.get(k, 0)) > 0.05
        for k in ["high", "medium", "low"]
    )

    return ThresholdCalibrationResult(
        domain=domain,
        sample_count=len(scored_samples),
        suggested_thresholds=suggested,
        current_thresholds=current.copy(),
        accuracy_estimate=round(accuracy, 3),
        needs_adaptation=needs_adaptation,
    )


def threshold_adaptation(
    result: ThresholdCalibrationResult,
    learning_rate: float = 0.3,
) -> Dict[str, float]:
    """
    Adapt groundedness thresholds based on calibration measurement.

    Uses exponential moving average:
        new_threshold = current + learning_rate * (suggested - current)

    Args:
        result: ThresholdCalibrationResult from threshold_measurement().
        learning_rate: How aggressively to move toward suggested (0-1).
            0 = no change, 1 = fully adopt suggested, 0.3 = conservative.

    Returns:
        Updated threshold dict. Also updates DOMAIN_THRESHOLDS in place.
    """
    if not result.needs_adaptation:
        return result.current_thresholds.copy()

    lr = max(0.0, min(1.0, learning_rate))
    current = result.current_thresholds
    suggested = result.suggested_thresholds

    updated: Dict[str, float] = {}
    for key in ["high", "medium", "low"]:
        cur = current.get(key, DEFAULT_THRESHOLDS[key])
        sug = suggested.get(key, cur)
        new_val = cur + lr * (sug - cur)
        updated[key] = round(new_val, 4)
    updated["insufficient"] = 0.0

    # Enforce strict ordering: high > medium > low > 0
    min_gap = 0.01
    # Ensure high >= medium >= low, with gaps
    if updated["high"] <= updated["medium"]:
        updated["high"] = updated["medium"] + min_gap
    if updated["medium"] <= updated["low"]:
        updated["medium"] = updated["low"] + min_gap
    # Re-check high > medium after fixing medium
    if updated["high"] <= updated["medium"]:
        updated["high"] = updated["medium"] + min_gap

    # Persist to DOMAIN_THRESHOLDS
    DOMAIN_THRESHOLDS[result.domain] = updated

    return updated
