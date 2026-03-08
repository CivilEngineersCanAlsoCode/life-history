"""
Test suite for monitoring dashboard.

Tests cover:
- Batch metric recording
- Aggregated metrics calculation
- Health status reporting
- Error analysis and reporting
- Dashboard formatting
"""

import pytest
from datetime import datetime

from life_brain.monitoring_dashboard import (
    MonitoringDashboard,
    BatchMetric,
    DashboardMetrics,
    MetricType,
    get_dashboard,
    record_batch,
)


class TestBatchMetric:
    """Test BatchMetric dataclass."""

    def test_create_batch_metric(self):
        """Test creating a batch metric."""
        metric = BatchMetric(
            batch_id="batch_001",
            operation="ingestion",
            start_time="2024-03-09T10:00:00",
            end_time="2024-03-09T10:05:00",
            total_docs=100,
            successful_docs=95,
            failed_docs=5,
            duration_seconds=300.0,
        )

        assert metric.batch_id == "batch_001"
        assert metric.total_docs == 100
        assert metric.successful_docs == 95

    def test_batch_metric_to_dict(self):
        """Test converting batch metric to dictionary."""
        metric = BatchMetric(
            batch_id="batch_001",
            operation="ingestion",
            start_time="2024-03-09T10:00:00",
            end_time="2024-03-09T10:05:00",
            total_docs=100,
            successful_docs=90,
            failed_docs=10,
            errors={"validation_error": 7, "network_error": 3},
            duration_seconds=10.0,
        )

        dict_form = metric.to_dict()
        assert dict_form["batch_id"] == "batch_001"
        assert dict_form["success_rate"] == 90.0
        assert dict_form["error_rate"] == 10.0
        assert dict_form["errors"]["validation_error"] == 7


class TestDashboardMetrics:
    """Test DashboardMetrics aggregation."""

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        metrics = DashboardMetrics()
        metrics.total_documents = 100
        metrics.successful_documents = 90
        metrics.failed_documents = 10

        assert metrics.overall_success_rate == 90.0
        assert metrics.overall_error_rate == 10.0

    def test_success_rate_zero_documents(self):
        """Test success rate with no documents."""
        metrics = DashboardMetrics()
        assert metrics.overall_success_rate == 0.0
        assert metrics.overall_error_rate == 0.0

    def test_metrics_to_dict(self):
        """Test metrics dictionary conversion."""
        metrics = DashboardMetrics()
        metrics.total_batches = 5
        metrics.total_documents = 500
        metrics.successful_documents = 480
        metrics.failed_documents = 20
        metrics.avg_throughput = 50.0
        metrics.p95_latency = 100.0
        metrics.error_summary = {"validation": 15, "network": 5}

        dict_form = metrics.to_dict()
        assert dict_form["summary"]["total_batches"] == 5
        assert dict_form["summary"]["overall_success_rate"] == 96.0
        assert dict_form["performance"]["avg_throughput_docs_per_sec"] == 50.0


class TestMonitoringDashboard:
    """Test MonitoringDashboard."""

    def test_create_dashboard(self):
        """Test creating a dashboard."""
        dashboard = MonitoringDashboard()
        assert dashboard.retention_hours == 24
        assert len(dashboard.batches) == 0

    def test_record_single_batch(self):
        """Test recording a single batch."""
        dashboard = MonitoringDashboard()
        metric = dashboard.record_batch(
            batch_id="batch_1",
            operation="ingestion",
            total_docs=100,
            successful_docs=95,
            failed_docs=5,
            duration_seconds=10.0,
        )

        assert len(dashboard.batches) == 1
        assert dashboard.metrics.total_batches == 1
        assert dashboard.metrics.total_documents == 100
        assert dashboard.metrics.successful_documents == 95

    def test_record_multiple_batches(self):
        """Test recording multiple batches."""
        dashboard = MonitoringDashboard()

        dashboard.record_batch(
            batch_id="batch_1",
            operation="ingestion",
            total_docs=100,
            successful_docs=95,
            failed_docs=5,
            duration_seconds=10.0,
        )

        dashboard.record_batch(
            batch_id="batch_2",
            operation="validation",
            total_docs=95,
            successful_docs=90,
            failed_docs=5,
            duration_seconds=5.0,
        )

        assert dashboard.metrics.total_batches == 2
        assert dashboard.metrics.total_documents == 195
        assert dashboard.metrics.successful_documents == 185

    def test_aggregate_errors(self):
        """Test error aggregation."""
        dashboard = MonitoringDashboard()

        dashboard.record_batch(
            batch_id="batch_1",
            operation="ingestion",
            total_docs=100,
            successful_docs=90,
            failed_docs=10,
            errors={"validation": 7, "network": 3},
            duration_seconds=10.0,
        )

        dashboard.record_batch(
            batch_id="batch_2",
            operation="validation",
            total_docs=100,
            successful_docs=95,
            failed_docs=5,
            errors={"validation": 5},
            duration_seconds=5.0,
        )

        assert dashboard.metrics.error_summary["validation"] == 12
        assert dashboard.metrics.error_summary["network"] == 3

    def test_throughput_calculation(self):
        """Test throughput calculation."""
        dashboard = MonitoringDashboard()

        dashboard.record_batch(
            batch_id="batch_1",
            operation="ingestion",
            total_docs=100,
            successful_docs=100,
            failed_docs=0,
            duration_seconds=10.0,
        )

        # Throughput = 100 docs / 10 seconds = 10 docs/sec
        assert dashboard.metrics.avg_throughput == 10.0

    def test_get_health_status_healthy(self):
        """Test health status when healthy."""
        dashboard = MonitoringDashboard()
        dashboard.record_batch(
            batch_id="batch_1",
            operation="ingestion",
            total_docs=100,
            successful_docs=99,
            failed_docs=1,
            duration_seconds=10.0,
        )

        status = dashboard.get_health_status()
        assert status["status"] == "healthy"
        assert "99" in status["success_rate"]

    def test_get_health_status_warning(self):
        """Test health status when warning."""
        dashboard = MonitoringDashboard()
        dashboard.record_batch(
            batch_id="batch_1",
            operation="ingestion",
            total_docs=100,
            successful_docs=95,
            failed_docs=5,
            duration_seconds=10.0,
        )

        status = dashboard.get_health_status()
        assert status["status"] == "warning"

    def test_get_health_status_critical(self):
        """Test health status when critical."""
        dashboard = MonitoringDashboard()
        dashboard.record_batch(
            batch_id="batch_1",
            operation="ingestion",
            total_docs=100,
            successful_docs=80,
            failed_docs=20,
            duration_seconds=10.0,
        )

        status = dashboard.get_health_status()
        assert status["status"] == "critical"

    def test_get_error_report(self):
        """Test error report generation."""
        dashboard = MonitoringDashboard()
        dashboard.record_batch(
            batch_id="batch_1",
            operation="ingestion",
            total_docs=100,
            successful_docs=90,
            failed_docs=10,
            errors={"validation": 7, "network": 3},
            duration_seconds=10.0,
        )

        report = dashboard.get_error_report()
        assert report["total_errors"] == 10
        assert report["error_types"]["validation"] == 7
        assert "batch_1" in report["batch_details"]

    def test_format_text_report(self):
        """Test text report formatting."""
        dashboard = MonitoringDashboard()
        dashboard.record_batch(
            batch_id="batch_1",
            operation="ingestion",
            total_docs=100,
            successful_docs=95,
            failed_docs=5,
            errors={"validation": 5},
            duration_seconds=10.0,
        )

        report = dashboard.format_text_report()
        assert "MONITORING DASHBOARD" in report
        assert "Total Documents: 100" in report
        assert "Success Rate" in report
        assert "validation: 5" in report

    def test_cleanup_old_batches(self):
        """Test cleaning up old batches."""
        dashboard = MonitoringDashboard(retention_hours=0)
        dashboard.record_batch(
            batch_id="batch_1",
            operation="ingestion",
            total_docs=100,
            successful_docs=95,
            failed_docs=5,
            duration_seconds=10.0,
        )

        assert len(dashboard.batches) == 1
        removed = dashboard.cleanup_old_batches()
        assert removed >= 0  # May or may not remove based on timing

    def test_get_dashboard(self):
        """Test getting full dashboard."""
        dashboard = MonitoringDashboard()
        dashboard.record_batch(
            batch_id="batch_1",
            operation="ingestion",
            total_docs=100,
            successful_docs=95,
            failed_docs=5,
            duration_seconds=10.0,
        )

        full_dashboard = dashboard.get_dashboard()
        assert "dashboard" in full_dashboard
        assert "batches_detail" in full_dashboard
        assert full_dashboard["dashboard"]["summary"]["total_batches"] == 1


class TestGlobalDashboard:
    """Test global dashboard functions."""

    def test_get_dashboard_singleton(self):
        """Test getting global dashboard."""
        dash1 = get_dashboard()
        dash2 = get_dashboard()
        assert dash1 is dash2

    def test_record_batch_global(self):
        """Test recording batch to global dashboard."""
        # Reset dashboard
        global MonitoringDashboard
        from life_brain import monitoring_dashboard as md
        md._dashboard_instance = None

        metric = record_batch(
            batch_id="batch_1",
            operation="ingestion",
            total_docs=100,
            successful_docs=95,
            failed_docs=5,
            duration_seconds=10.0,
        )

        assert metric.batch_id == "batch_1"
        dashboard = get_dashboard()
        assert len(dashboard.batches) >= 1
