"""
Testing framework for Life Brain — unit test templates, mocking utilities, and helpers.

This module provides:
- Base test classes with common setup/teardown
- Mock fixtures for ChromaDB, LLM, and external services
- Assertion helpers for common patterns
- Test data generators
"""

from life_brain.testing.base_test import (
    BaseLifeBrainTest,
    BaseIntegrationTest,
)
from life_brain.testing.fixtures import (
    mock_chroma_collection,
    mock_retrieved_document,
    mock_metadata_dict,
    sample_documents,
)
from life_brain.testing.mocks import (
    MockChromaDB,
    MockEmbedding,
    MockLLM,
    MockSession,
)
from life_brain.testing.assertions import (
    assert_valid_document,
    assert_valid_metadata,
    assert_similarity_in_range,
)

__all__ = [
    # Base test classes
    "BaseLifeBrainTest",
    "BaseIntegrationTest",
    # Fixtures
    "mock_chroma_collection",
    "mock_retrieved_document",
    "mock_metadata_dict",
    "sample_documents",
    # Mocks
    "MockChromaDB",
    "MockEmbedding",
    "MockLLM",
    "MockSession",
    # Assertions
    "assert_valid_document",
    "assert_valid_metadata",
    "assert_similarity_in_range",
]
