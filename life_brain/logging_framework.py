"""
Logging framework for Life Brain — debug/info/warning/error levels across all modules.

Provides:
- Centralized logger configuration
- Performance timing decorators
- Structured logging with context
- Log aggregation and analysis
"""

import logging
import sys
import functools
import time
from typing import Any, Callable, Optional, Dict
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class LifeBrainLogger:
    """Centralized logger for Life Brain modules."""

    _instance = None
    _loggers: Dict[str, logging.Logger] = {}

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize logger framework."""
        if self._initialized:
            return

        self.log_level = LogLevel.INFO
        self.handlers = []
        self._setup_root_logger()
        self._initialized = True

    def _setup_root_logger(self) -> None:
        """Set up root logger with console handler."""
        root_logger = logging.getLogger("life_brain")
        root_logger.setLevel(self.log_level.value)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level.value)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)

        root_logger.addHandler(console_handler)
        self.handlers.append(console_handler)

    def get_logger(self, module_name: str) -> logging.Logger:
        """Get logger for a specific module."""
        logger_name = f"life_brain.{module_name}"

        if logger_name not in self._loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(self.log_level.value)
            self._loggers[logger_name] = logger

        return self._loggers[logger_name]

    def set_level(self, level: LogLevel) -> None:
        """Set global log level."""
        self.log_level = level
        root_logger = logging.getLogger("life_brain")
        root_logger.setLevel(level.value)

        for handler in self.handlers:
            handler.setLevel(level.value)

    def add_file_handler(self, filepath: str, level: LogLevel = LogLevel.INFO) -> None:
        """Add file handler for logging to file."""
        file_handler = logging.FileHandler(filepath)
        file_handler.setLevel(level.value)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)

        root_logger = logging.getLogger("life_brain")
        root_logger.addHandler(file_handler)
        self.handlers.append(file_handler)


def log_execution_time(level: LogLevel = LogLevel.INFO):
    """
    Decorator to log function execution time.

    Usage:
        @log_execution_time(LogLevel.DEBUG)
        def my_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = LifeBrainLogger().get_logger(func.__module__)
            start_time = time.time()

            logger.log(
                level.value,
                f"▶ Starting {func.__name__}",
            )

            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.log(
                    level.value,
                    f"✓ Completed {func.__name__} in {elapsed:.3f}s",
                )
                return result

            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"✗ Failed {func.__name__} after {elapsed:.3f}s: {str(e)}",
                )
                raise

        return wrapper
    return decorator


def log_structured(
    message: str,
    level: LogLevel = LogLevel.INFO,
    **context: Any
) -> Callable:
    """
    Log with structured context.

    Usage:
        log_structured(
            "Document processed",
            level=LogLevel.INFO,
            doc_id="abc123",
            success=True,
            duration=0.5,
        )
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = LifeBrainLogger().get_logger(func.__module__)

            context_str = " | ".join(
                f"{k}={v}" for k, v in context.items()
            )
            full_message = f"{message} [{context_str}]" if context else message

            logger.log(level.value, full_message)
            return func(*args, **kwargs)

        return wrapper
    return decorator


class PerformanceMonitor:
    """Track performance metrics across operations."""

    def __init__(self, name: str):
        self.name = name
        self.measurements = []
        self.logger = LifeBrainLogger().get_logger("performance")

    def record(self, duration: float, operation: str) -> None:
        """Record an operation's duration."""
        self.measurements.append({
            "operation": operation,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
        })

    def report(self) -> Dict[str, Any]:
        """Generate performance report."""
        if not self.measurements:
            return {"error": "No measurements recorded"}

        durations = [m["duration"] for m in self.measurements]
        return {
            "monitor": self.name,
            "total_measurements": len(self.measurements),
            "total_time": sum(durations),
            "avg_time": sum(durations) / len(durations),
            "min_time": min(durations),
            "max_time": max(durations),
            "measurements": self.measurements,
        }

    def log_report(self) -> None:
        """Log performance report."""
        report = self.report()
        if "error" in report:
            self.logger.warning(report["error"])
            return

        self.logger.info(
            f"Performance [{self.name}]: "
            f"avg={report['avg_time']:.3f}s, "
            f"total={report['total_time']:.3f}s, "
            f"count={report['total_measurements']}"
        )


# Module-level convenience functions
def get_logger(module_name: str) -> logging.Logger:
    """Get logger for a module."""
    return LifeBrainLogger().get_logger(module_name)


def set_log_level(level: LogLevel) -> None:
    """Set global log level."""
    LifeBrainLogger().set_level(level)


def add_file_logging(filepath: str) -> None:
    """Add file logging."""
    LifeBrainLogger().add_file_handler(filepath)
