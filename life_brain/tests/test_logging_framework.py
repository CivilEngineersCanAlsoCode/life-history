"""
Test suite for logging framework.

Tests cover:
- Logger initialization and configuration
- Log levels (debug, info, warning, error)
- Execution time tracking
- Performance monitoring
- Structured logging
"""

import pytest
import logging
import tempfile
from pathlib import Path

from life_brain.logging_framework import (
    LifeBrainLogger,
    LogLevel,
    log_execution_time,
    PerformanceMonitor,
    get_logger,
    set_log_level,
)


class TestLifeBrainLogger:
    """Test LifeBrainLogger singleton."""

    def test_singleton_pattern(self):
        """Test that LifeBrainLogger is a singleton."""
        logger1 = LifeBrainLogger()
        logger2 = LifeBrainLogger()
        assert logger1 is logger2

    def test_get_logger(self):
        """Test getting a logger for a module."""
        logger = LifeBrainLogger()
        module_logger = logger.get_logger("test_module")
        assert module_logger is not None
        assert "life_brain.test_module" in module_logger.name

    def test_set_level(self):
        """Test setting log level."""
        logger = LifeBrainLogger()
        logger.set_level(LogLevel.DEBUG)
        assert logger.log_level == LogLevel.DEBUG

    def test_add_file_handler(self):
        """Test adding file handler."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = LifeBrainLogger()
            logger.add_file_handler(str(log_file))
            assert log_file.exists()


class TestLogLevel:
    """Test LogLevel enum."""

    def test_log_level_values(self):
        """Test log level enum values."""
        assert LogLevel.DEBUG.value == logging.DEBUG
        assert LogLevel.INFO.value == logging.INFO
        assert LogLevel.WARNING.value == logging.WARNING
        assert LogLevel.ERROR.value == logging.ERROR
        assert LogLevel.CRITICAL.value == logging.CRITICAL


class TestLogExecutionTime:
    """Test execution time logging decorator."""

    def test_decorator_logs_execution(self):
        """Test that decorator logs execution time."""
        @log_execution_time(LogLevel.INFO)
        def test_function():
            return "result"

        result = test_function()
        assert result == "result"

    def test_decorator_logs_errors(self):
        """Test that decorator logs errors."""
        @log_execution_time(LogLevel.INFO)
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()

    def test_decorator_preserves_function_metadata(self):
        """Test that decorator preserves function name and docstring."""
        @log_execution_time(LogLevel.INFO)
        def documented_function():
            """Function documentation."""
            return "result"

        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "Function documentation."


class TestPerformanceMonitor:
    """Test PerformanceMonitor."""

    def test_create_monitor(self):
        """Test creating a monitor."""
        monitor = PerformanceMonitor("test_monitor")
        assert monitor.name == "test_monitor"
        assert monitor.measurements == []

    def test_record_measurement(self):
        """Test recording a measurement."""
        monitor = PerformanceMonitor("test")
        monitor.record(0.5, "operation_1")
        monitor.record(0.3, "operation_2")

        assert len(monitor.measurements) == 2
        assert monitor.measurements[0]["duration"] == 0.5
        assert monitor.measurements[1]["duration"] == 0.3

    def test_report_generation(self):
        """Test generating performance report."""
        monitor = PerformanceMonitor("test")
        monitor.record(0.5, "op1")
        monitor.record(0.3, "op2")

        report = monitor.report()
        assert report["monitor"] == "test"
        assert report["total_measurements"] == 2
        assert report["avg_time"] == 0.4
        assert report["min_time"] == 0.3
        assert report["max_time"] == 0.5

    def test_report_empty_monitor(self):
        """Test report on empty monitor."""
        monitor = PerformanceMonitor("empty")
        report = monitor.report()
        assert "error" in report


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_get_logger(self):
        """Test get_logger function."""
        logger = get_logger("test_module")
        assert logger is not None
        assert "life_brain.test_module" in logger.name

    def test_set_log_level(self):
        """Test set_log_level function."""
        set_log_level(LogLevel.DEBUG)
        logger = LifeBrainLogger()
        assert logger.log_level == LogLevel.DEBUG

        set_log_level(LogLevel.ERROR)
        assert logger.log_level == LogLevel.ERROR


class TestLoggingIntegration:
    """Integration tests for logging framework."""

    def test_full_logging_workflow(self):
        """Test complete logging workflow."""
        logger = LifeBrainLogger()
        logger.set_level(LogLevel.DEBUG)

        @log_execution_time(LogLevel.DEBUG)
        def complex_operation():
            monitor = PerformanceMonitor("workflow")
            monitor.record(0.1, "step_1")
            monitor.record(0.2, "step_2")
            monitor.log_report()
            return True

        result = complex_operation()
        assert result is True

    def test_multiple_loggers(self):
        """Test using multiple loggers."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        assert logger1 != logger2
        assert "module1" in logger1.name
        assert "module2" in logger2.name

    def test_logger_isolation(self):
        """Test that loggers for different modules are isolated."""
        logger_a = get_logger("module_a")
        logger_b = get_logger("module_b")

        assert logger_a.name != logger_b.name
        assert "module_a" in logger_a.name
        assert "module_b" in logger_b.name
