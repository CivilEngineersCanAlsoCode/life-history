"""
Custom assertion helpers for Life Brain testing.

Provides:
- Document validation assertions
- Metadata validation assertions
- Similarity score assertions
- Result structure assertions
"""

from typing import Dict, Any, List, Optional
from life_brain.truth.groundedness import RetrievedDocument


def assert_valid_document(doc: Dict[str, Any], strict: bool = True) -> bool:
    """
    Assert that document has valid structure.

    Args:
        doc: Document to validate
        strict: If True, require all fields; if False, allow partial fields

    Returns:
        True if valid

    Raises:
        AssertionError if invalid
    """
    if strict:
        required_fields = ["id", "text", "metadata"]
        for field in required_fields:
            assert field in doc, f"Document missing required field: {field}"

    assert isinstance(doc.get("text", ""), str), "Document text must be string"
    assert len(doc.get("text", "").strip()) > 0, "Document text cannot be empty"

    if "metadata" in doc:
        assert isinstance(doc["metadata"], dict), "Document metadata must be dict"

    return True


def assert_valid_metadata(metadata: Dict[str, Any], strict: bool = False) -> bool:
    """
    Assert that metadata has valid structure.

    Args:
        metadata: Metadata dictionary to validate
        strict: If True, require all 47 standard fields

    Returns:
        True if valid

    Raises:
        AssertionError if invalid
    """
    if strict:
        required_fields = [
            "domain",
            "subdomain",
            "doc_type",
            "source",
            "created_at",
        ]
        for field in required_fields:
            assert field in metadata, f"Metadata missing required field: {field}"

    # Validate field types if present
    if "domain" in metadata:
        assert isinstance(metadata["domain"], str), "domain must be string"

    if "confidence" in metadata:
        assert isinstance(metadata["confidence"], (int, float)), \
            "confidence must be numeric"
        assert 0.0 <= metadata["confidence"] <= 1.0, \
            "confidence must be between 0 and 1"

    return True


def assert_similarity_in_range(similarity: float, min_val: float = 0.0,
                              max_val: float = 1.0, msg: Optional[str] = None) -> bool:
    """
    Assert that similarity score is in valid range.

    Args:
        similarity: Similarity score to check
        min_val: Minimum valid value (default: 0.0)
        max_val: Maximum valid value (default: 1.0)
        msg: Optional custom message

    Returns:
        True if valid

    Raises:
        AssertionError if invalid
    """
    assert isinstance(similarity, (int, float)), \
        msg or f"Similarity must be numeric, got {type(similarity)}"

    assert min_val <= similarity <= max_val, \
        msg or f"Similarity {similarity} not in range [{min_val}, {max_val}]"

    return True


def assert_retrieved_documents_valid(docs: List[RetrievedDocument]) -> bool:
    """
    Assert that retrieved documents list is valid.

    Args:
        docs: List of retrieved documents

    Returns:
        True if valid

    Raises:
        AssertionError if invalid
    """
    assert isinstance(docs, list), "Documents must be a list"

    for i, doc in enumerate(docs):
        assert hasattr(doc, "doc_id"), f"Doc {i} missing doc_id"
        assert hasattr(doc, "text"), f"Doc {i} missing text"
        assert hasattr(doc, "similarity_score"), f"Doc {i} missing similarity_score"

        assert isinstance(doc.doc_id, str), f"Doc {i} doc_id must be string"
        assert isinstance(doc.text, str), f"Doc {i} text must be string"
        assert_similarity_in_range(doc.similarity_score)

    return True


def assert_conflict_result_valid(result: Dict[str, Any]) -> bool:
    """
    Assert that conflict detection result is valid.

    Args:
        result: Conflict detection result

    Returns:
        True if valid

    Raises:
        AssertionError if invalid
    """
    required_fields = [
        "has_conflict",
        "conflict_score",
        "category",
    ]

    for field in required_fields:
        assert field in result, f"Result missing field: {field}"

    assert isinstance(result["has_conflict"], bool), \
        "has_conflict must be boolean"

    assert_similarity_in_range(result["conflict_score"])

    valid_categories = ["enrichment", "soft", "hard"]
    assert result["category"] in valid_categories, \
        f"Invalid category: {result['category']}"

    return True


def assert_session_valid(session: Dict[str, Any]) -> bool:
    """
    Assert that session object is valid.

    Args:
        session: Session dictionary

    Returns:
        True if valid

    Raises:
        AssertionError if invalid
    """
    required_fields = ["session_id", "user_id", "created_at"]

    for field in required_fields:
        assert field in session, f"Session missing field: {field}"

    assert isinstance(session.get("session_id"), str), \
        "session_id must be string"

    if "metadata" in session:
        assert isinstance(session["metadata"], dict), \
            "metadata must be dict"

    return True
