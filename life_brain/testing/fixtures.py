"""
Test fixtures for Life Brain — reusable test data and mock objects.

Provides:
- Standard test documents
- Mock metadata dictionaries
- ChromaDB collection mocks
- Common test scenarios
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import random
import string


def mock_metadata_dict(
    domain: str = "career",
    subdomain: str = "project",
    confidence: float = 0.9,
    **kwargs
) -> Dict[str, Any]:
    """Generate a mock metadata dictionary."""
    metadata = {
        # TIER 1: Core fields
        "domain": domain,
        "subdomain": subdomain,
        "doc_type": "fact",
        "source": "resume",
        "author": "self",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        # Confidence and authority
        "confidence": confidence,
        "authority": "personal",
        # Content markers
        "contains_metric": False,
        "contains_date": False,
        "contains_name": False,
        # Privacy and accessibility
        "is_public": True,
        "is_sensitive": False,
    }
    # Add any additional kwargs
    metadata.update(kwargs)
    return metadata


def mock_retrieved_document(
    doc_id: Optional[str] = None,
    text: Optional[str] = None,
    similarity_score: float = 0.85,
    metadata: Optional[Dict] = None,
):
    """Generate a mock retrieved document."""
    from life_brain.truth_engine.groundedness import RetrievedDocument

    if doc_id is None:
        doc_id = f"doc_{''.join(random.choices(string.ascii_lowercase, k=6))}"

    if text is None:
        text = "This is sample document text for testing purposes."

    if metadata is None:
        metadata = mock_metadata_dict()

    return RetrievedDocument(
        doc_id=doc_id,
        text=text,
        metadata=metadata,
        similarity_score=similarity_score,
    )


def mock_chroma_collection(num_docs: int = 5) -> Dict[str, Any]:
    """Generate mock ChromaDB collection."""
    return {
        "name": "test_collection",
        "count": num_docs,
        "documents": [
            mock_retrieved_document(
                doc_id=f"doc_{i}",
                text=f"Test document {i}: Sample content.",
                similarity_score=0.9 - (i * 0.05),
            )
            for i in range(num_docs)
        ],
    }


def sample_documents() -> List[Dict[str, Any]]:
    """Generate sample documents for testing."""
    return [
        {
            "id": "career_project_20240715_crr-aml_a3f2",
            "text": (
                "At American Express (Jul 2024-Present), as Senior Associate PM "
                "on the CRR AML Risk Scoring Engine project, I modernized a "
                "12-year-old legacy system. The core problem was that AML "
                "investigators spent 12-15 minutes per case because risk data "
                "was scattered across 6 different tools. We consolidated this "
                "into a single unified interface, reducing investigation time "
                "to under 4 minutes."
            ),
            "metadata": mock_metadata_dict(
                domain="career",
                subdomain="project",
                company="American Express",
                project="CRR AML Risk Scoring Engine",
                role="Senior Associate PM",
                impact_metric="4x faster investigation (12-15m → 4m)",
            ),
        },
        {
            "id": "career_skill_20250101_python-async_b7e1",
            "text": (
                "Mastered Python async/await patterns for handling concurrent "
                "database operations. This enabled batch processing of 10K+ "
                "documents with 95%+ success rate and proper error recovery."
            ),
            "metadata": mock_metadata_dict(
                domain="career",
                subdomain="skill",
                skill="Python async/await",
                proficiency="advanced",
            ),
        },
        {
            "id": "health_mental_20250308_anxiety-work_c9d4",
            "text": (
                "When facing high-pressure deadlines at work, I experience "
                "anxiety peaks. Effective strategies: structured planning, "
                "25-min focused work sprints, meditation breaks."
            ),
            "metadata": mock_metadata_dict(
                domain="health",
                subdomain="mental",
                is_sensitive=True,
                is_public=False,
            ),
        },
    ]


@dataclass
class MockSession:
    """Mock user session for testing."""
    session_id: str = field(default_factory=lambda: f"sess_{''.join(random.choices(string.ascii_lowercase, k=8))}")
    user_id: str = "test_user"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "metadata": self.metadata,
            "context": self.context,
        }
