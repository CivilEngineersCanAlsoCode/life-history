"""
Mock objects for Life Brain testing — ChromaDB, LLM, embeddings, etc.

Provides:
- MockChromaDB for database testing
- MockEmbedding for vector operations
- MockLLM for language model testing
- MockSession for session testing
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import random
import uuid


@dataclass
class MockEmbedding:
    """Mock embedding vector."""
    vector: List[float] = field(default_factory=lambda: [random.random() for _ in range(384)])
    model: str = "mock-embedding-model"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "vector": self.vector,
            "model": self.model,
            "dimension": len(self.vector),
        }


class MockChromaDB:
    """Mock ChromaDB for testing without database."""

    def __init__(self):
        self.collections = {}
        self.documents = {}

    def create_collection(self, name: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a mock collection."""
        collection_id = str(uuid.uuid4())
        self.collections[name] = {
            "id": collection_id,
            "name": name,
            "metadata": metadata or {},
            "docs": [],
        }
        return self.collections[name]

    def get_collection(self, name: str) -> Optional[Dict[str, Any]]:
        """Get collection by name."""
        return self.collections.get(name)

    def add(self, collection_name: str, doc_ids: List[str], embeddings: List[List[float]],
            documents: List[str], metadatas: List[Dict]) -> Dict[str, Any]:
        """Add documents to collection (mock)."""
        if collection_name not in self.collections:
            self.create_collection(collection_name)

        collection = self.collections[collection_name]
        for doc_id, embedding, text, metadata in zip(doc_ids, embeddings, documents, metadatas):
            doc = {
                "id": doc_id,
                "embedding": embedding,
                "text": text,
                "metadata": metadata,
            }
            self.documents[doc_id] = doc
            collection["docs"].append(doc_id)

        return {
            "status": "success",
            "count": len(doc_ids),
            "collection": collection_name,
        }

    def query(self, collection_name: str, query_embeddings: List[List[float]],
             n_results: int = 3) -> Dict[str, Any]:
        """Query collection (mock)."""
        collection = self.get_collection(collection_name)
        if not collection:
            return {"results": [], "error": f"Collection {collection_name} not found"}

        # Return top n results based on random scores
        results = []
        for doc_id in collection["docs"][:n_results]:
            doc = self.documents.get(doc_id)
            if doc:
                results.append({
                    "id": doc_id,
                    "distance": random.random(),
                    "text": doc["text"],
                    "metadata": doc["metadata"],
                })

        return {"results": results, "count": len(results)}

    def delete_collection(self, name: str) -> Dict[str, Any]:
        """Delete collection (mock)."""
        if name in self.collections:
            del self.collections[name]
            return {"status": "success", "collection": name}
        return {"status": "error", "message": f"Collection {name} not found"}


class MockLLM:
    """Mock Language Model for testing."""

    def __init__(self, response_template: str = "Mock LLM response"):
        self.response_template = response_template
        self.call_count = 0
        self.last_prompt = None

    def generate(self, prompt: str, temperature: float = 0.7,
                max_tokens: int = 256) -> str:
        """Generate text (mock)."""
        self.call_count += 1
        self.last_prompt = prompt
        return f"{self.response_template} [Call #{self.call_count}]"

    def embed_query(self, text: str) -> List[float]:
        """Embed query (mock)."""
        return [random.random() for _ in range(384)]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents (mock)."""
        return [[random.random() for _ in range(384)] for _ in texts]

    def get_call_count(self) -> int:
        """Get number of times LLM was called."""
        return self.call_count


class MockSession:
    """Mock session manager for testing."""

    def __init__(self, session_id: str = "test_session"):
        self.session_id = session_id
        self.state = {}
        self.context = {}
        self.history = []

    def set_state(self, key: str, value: Any) -> None:
        """Set session state."""
        self.state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get session state."""
        return self.state.get(key, default)

    def add_to_history(self, role: str, content: str) -> None:
        """Add message to history."""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": str(random.random()),
        })

    def get_history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self.history.copy()

    def clear_history(self) -> None:
        """Clear history."""
        self.history.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "state": self.state.copy(),
            "context": self.context.copy(),
            "history": self.history.copy(),
        }
