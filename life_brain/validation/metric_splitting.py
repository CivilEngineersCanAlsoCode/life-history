"""
Metric splitting for extracting quantitative values from text.

Extracts and separates key metrics (e.g., "marks: 100", "impact: 50%") from
unstructured text and provides structured access to metric names and values.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re


class MetricType(Enum):
    """Type of metric value."""

    PERCENTAGE = "percentage"  # 0-100%
    SCORE = "score"  # Numeric score
    COUNT = "count"  # Integer count
    RATIO = "ratio"  # Ratio like 1:2
    BOOLEAN = "boolean"  # True/False
    CATEGORICAL = "categorical"  # Text value
    CURRENCY = "currency"  # Money
    DURATION = "duration"  # Time duration


@dataclass
class MetricValue:
    """Extracted metric with value and type."""

    metric_name: str
    raw_value: str  # Original text value
    parsed_value: Any  # Parsed/normalized value
    metric_type: MetricType
    unit: str = ""  # Unit (%, $, sec, etc)
    confidence: float = 1.0  # 0-1, confidence in extraction


@dataclass
class SplitMetric:
    """Complete split metric with metadata."""

    metric_id: str
    metric: MetricValue
    source_text: str  # Original sentence
    context: str  # Broader context
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_id": self.metric_id,
            "name": self.metric.metric_name,
            "raw_value": self.metric.raw_value,
            "parsed_value": self.metric.parsed_value,
            "type": self.metric.metric_type.value,
            "unit": self.metric.unit,
            "confidence": self.metric.confidence,
            "source_text": self.source_text,
            "created_at": self.created_at,
        }


class MetricSplitter:
    """Extract and split metrics from text."""

    # Common metric patterns - ordered by specificity (most specific first)
    METRIC_PATTERNS = {
        "duration": r"(time|duration)[\s:]*(\d+)\s*(hours|minutes|seconds|days|months|years)",
        "currency": r"(price|cost|salary|revenue)[\s:]*\$?\s*(\d+(?:,\d{3})*(?:\.\d+)?)",
        "ratio": r"(\w+)[\s:]*(\d+)\s*:\s*(\d+)",
        "percentage": r"(\w+)[\s:]*(\d+(?:\.\d+)?)\s*%",
        "marks": r"(marks|points|score|rating)[\s:]*(\d+(?:\.\d+)?)",
        "count": r"(count|total|number|amount)[\s:]*(\d+)(?!\s*[:/])",
        "score": r"(\w+)[\s:]*(\d+(?:\.\d+)?)\s*/\s*(\d+)",
    }

    def __init__(self):
        """Initialize metric splitter."""
        self.metrics: Dict[str, SplitMetric] = {}
        self.metric_history: List[SplitMetric] = []

    def split_metrics(
        self, text: str, context: str = ""
    ) -> Tuple[List[SplitMetric], Optional[str]]:
        """
        Extract metrics from text.

        Args:
            text: Text to extract metrics from
            context: Broader context for categorization

        Returns:
            (List of split metrics, error if any)
        """
        if not text or not text.strip():
            return [], "Empty text"

        metrics = []

        # Split into sentences
        sentences = self._split_sentences(text)

        for sentence in sentences:
            # Try to extract metrics from each sentence
            extracted = self._extract_metrics_from_sentence(sentence)

            for metric_value in extracted:
                metric_id = f"met_{len(self.metrics):04d}"
                split_metric = SplitMetric(
                    metric_id=metric_id,
                    metric=metric_value,
                    source_text=sentence,
                    context=context,
                )

                self.metrics[metric_id] = split_metric
                self.metric_history.append(split_metric)
                metrics.append(split_metric)

        return metrics, None

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r"[.!?]+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _extract_metrics_from_sentence(self, sentence: str) -> List[MetricValue]:
        """Extract all metrics from a sentence."""
        metrics = []
        sentence_lower = sentence.lower()

        # Try each pattern
        for pattern_type, pattern in self.METRIC_PATTERNS.items():
            matches = re.finditer(pattern, sentence, re.IGNORECASE)

            for match in matches:
                metric_value = self._create_metric_from_match(
                    match, pattern_type, sentence
                )
                if metric_value:
                    metrics.append(metric_value)

        return metrics

    def _create_metric_from_match(
        self, match: re.Match, pattern_type: str, sentence: str
    ) -> Optional[MetricValue]:
        """Create metric from regex match."""
        try:
            if pattern_type == "percentage":
                name = match.group(1)
                value = float(match.group(2))
                return MetricValue(
                    metric_name=name,
                    raw_value=match.group(0),
                    parsed_value=min(100.0, max(0.0, value)),
                    metric_type=MetricType.PERCENTAGE,
                    unit="%",
                    confidence=0.95,
                )

            elif pattern_type == "score":
                name = match.group(1)
                value = float(match.group(2))
                max_val = float(match.group(3)) if match.group(3) else 10
                return MetricValue(
                    metric_name=name,
                    raw_value=match.group(0),
                    parsed_value=value,
                    metric_type=MetricType.SCORE,
                    unit=f"/{max_val}",
                    confidence=0.90,
                )

            elif pattern_type == "marks":
                name = match.group(1)
                value = float(match.group(2))
                return MetricValue(
                    metric_name=name,
                    raw_value=match.group(0),
                    parsed_value=value,
                    metric_type=MetricType.SCORE,
                    unit="",
                    confidence=0.92,
                )

            elif pattern_type == "ratio":
                name = match.group(1)
                val1 = int(match.group(2))
                val2 = int(match.group(3))
                return MetricValue(
                    metric_name=name,
                    raw_value=match.group(0),
                    parsed_value=(val1, val2),
                    metric_type=MetricType.RATIO,
                    unit="",
                    confidence=0.88,
                )

            elif pattern_type == "currency":
                name = match.group(1)
                value_str = match.group(2).replace(",", "")
                value = float(value_str)
                return MetricValue(
                    metric_name=name,
                    raw_value=match.group(0),
                    parsed_value=value,
                    metric_type=MetricType.CURRENCY,
                    unit="$",
                    confidence=0.93,
                )

            elif pattern_type == "count":
                name = match.group(1)
                value = int(match.group(2))
                return MetricValue(
                    metric_name=name,
                    raw_value=match.group(0),
                    parsed_value=value,
                    metric_type=MetricType.COUNT,
                    unit="",
                    confidence=0.94,
                )

            elif pattern_type == "duration":
                name = match.group(1)
                value = int(match.group(2))
                unit = match.group(3).lower()
                return MetricValue(
                    metric_name=name,
                    raw_value=match.group(0),
                    parsed_value=value,
                    metric_type=MetricType.DURATION,
                    unit=unit[0],  # First letter as unit
                    confidence=0.89,
                )

        except (ValueError, IndexError):
            return None

        return None

    def get_metric(self, metric_id: str) -> Optional[SplitMetric]:
        """Get specific metric."""
        return self.metrics.get(metric_id)

    def get_metrics_by_name(self, name: str) -> List[SplitMetric]:
        """Get all metrics with specific name."""
        name_lower = name.lower()
        return [
            m
            for m in self.metric_history
            if m.metric.metric_name.lower() == name_lower
        ]

    def get_metrics_by_type(self, metric_type: MetricType) -> List[SplitMetric]:
        """Get all metrics of a specific type."""
        return [
            m for m in self.metric_history if m.metric.metric_type == metric_type
        ]

    def get_metric_values(self) -> Dict[str, Any]:
        """Get all metrics as key-value pairs."""
        result = {}
        for metric in self.metric_history:
            key = metric.metric.metric_name
            if key in result:
                # Handle duplicates - store as list
                if not isinstance(result[key], list):
                    result[key] = [result[key]]
                result[key].append(metric.metric.parsed_value)
            else:
                result[key] = metric.metric.parsed_value
        return result

    def batch_split(
        self, texts: List[str], context: str = ""
    ) -> Tuple[List[SplitMetric], Optional[str]]:
        """Batch split metrics from multiple texts."""
        all_metrics = []
        for text in texts:
            metrics, _ = self.split_metrics(text, context)
            all_metrics.extend(metrics)
        return all_metrics, None

    def export_metric(self, metric_id: str) -> Optional[Dict[str, Any]]:
        """Export single metric."""
        metric = self.get_metric(metric_id)
        if not metric:
            return None
        return metric.to_dict()

    def export_all_metrics(self) -> List[Dict[str, Any]]:
        """Export all metrics."""
        return [m.to_dict() for m in self.metric_history]

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about extracted metrics."""
        if not self.metric_history:
            return {
                "total_metrics": 0,
                "by_type": {},
                "avg_confidence": 0.0,
            }

        type_counts = {}
        for metric in self.metric_history:
            mtype = metric.metric.metric_type.value
            type_counts[mtype] = type_counts.get(mtype, 0) + 1

        avg_confidence = (
            sum(m.metric.confidence for m in self.metric_history)
            / len(self.metric_history)
        )

        return {
            "total_metrics": len(self.metric_history),
            "by_type": type_counts,
            "avg_confidence": avg_confidence,
            "unique_names": len(set(m.metric.metric_name for m in self.metric_history)),
        }
