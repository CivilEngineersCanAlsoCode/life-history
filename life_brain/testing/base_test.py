"""
Base test classes for Life Brain testing framework.

Provides:
- Common setup/teardown for unit tests
- Shared fixtures and utilities
- Integration test infrastructure
"""

import unittest
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TestConfig:
    """Configuration for test execution."""
    verbose: bool = False
    timeout_seconds: int = 30
    enable_slow_tests: bool = False
    mock_external_services: bool = True


class BaseLifeBrainTest(unittest.TestCase):
    """
    Base class for all Life Brain unit tests.

    Provides:
    - Common setUp/tearDown
    - Standard assertion helpers
    - Mock utilities
    - Test isolation
    """

    test_config = TestConfig()

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_start_time = datetime.now()
        self.test_data = {}
        self.mocks = {}

    def tearDown(self):
        """Clean up after each test method."""
        self.test_data.clear()
        self.mocks.clear()

    def assert_has_keys(self, obj: Dict, keys: list, msg: Optional[str] = None):
        """Assert that dictionary has all required keys."""
        for key in keys:
            self.assertIn(key, obj, msg or f"Missing key: {key}")

    def assert_all_values_not_none(self, obj: Dict, msg: Optional[str] = None):
        """Assert that all dict values are not None."""
        for key, value in obj.items():
            self.assertIsNotNone(value, msg or f"Key {key} has None value")

    def assert_in_range(self, value: float, min_val: float, max_val: float,
                       msg: Optional[str] = None):
        """Assert that numeric value is within range."""
        self.assertGreaterEqual(value, min_val, msg or f"{value} < {min_val}")
        self.assertLessEqual(value, max_val, msg or f"{value} > {max_val}")


class BaseIntegrationTest(BaseLifeBrainTest):
    """
    Base class for integration tests.

    Provides:
    - Full system initialization
    - Database setup/teardown
    - Cross-component testing utilities
    """

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for entire test class."""
        cls.system_initialized = True
        cls.integration_resources = {}

    @classmethod
    def tearDownClass(cls):
        """Clean up after all test methods in class."""
        cls.integration_resources.clear()

    def setUp(self):
        """Set up for each integration test."""
        super().setUp()
        self.integration_state = {}

    def assert_system_state(self, expected_state: Dict[str, Any],
                           msg: Optional[str] = None):
        """Assert system is in expected state."""
        for key, value in expected_state.items():
            actual = self.integration_state.get(key)
            self.assertEqual(actual, value,
                           msg or f"State mismatch for {key}: {actual} != {value}")
