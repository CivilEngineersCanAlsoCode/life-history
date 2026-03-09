# Life Brain API Reference

Complete API documentation for all Life Brain modules.

## Table of Contents

1. [Data Ingestion](#data-ingestion)
2. [Validation & Conflict Detection](#validation--conflict-detection)
3. [Truth & Grounding Engine](#truth--grounding-engine)
4. [Retrieval & Search](#retrieval--search)
5. [Session Management](#session-management)
6. [Intent Detection](#intent-detection)
7. [Framework & Utilities](#framework--utilities)

---

## Data Ingestion

### `life_brain.db.ingestion`

Core document ingestion pipeline.

#### `IngestionManager`

```python
from life_brain.db.ingestion import IngestionManager

manager = IngestionManager(chroma_client, validator)
```

**Methods:**

- `ingest_documents(documents: List[Dict]) -> IngestionResult`
  - Ingest multiple documents with conflict detection
  - Args: `documents` - List of document dicts with text and metadata
  - Returns: Result with success/failure counts and conflicts

- `ingest_single(document: Dict) -> bool`
  - Ingest single document
  - Returns: True if successful

- `ingest_batch(documents: List[Dict], batch_size: int = 100) -> BatchIngestionResult`
  - Ingest large batches with progress tracking
  - Args: `batch_size` - Docs per batch
  - Returns: Batch results with metrics

#### `IngestionValidator`

```python
from life_brain.db.ingestion import IngestionValidator

validator = IngestionValidator()
validation_result = validator.validate(document)
```

**Methods:**

- `validate(document: Dict) -> ValidationResult`
  - Validate document structure and content
  - Returns: ValidationResult with errors list

- `validate_metadata(metadata: Dict) -> bool`
  - Validate metadata against 47-field schema
  - Raises: ValueError if validation fails

---

## Validation & Conflict Detection

### `life_brain.truth_engine.conflict`

Conflict detection and scoring.

#### `ConflictDetector`

```python
from life_brain.truth_engine.conflict import ConflictDetector

detector = ConflictDetector(threshold=0.3)
result = detector.detect_conflict(existing_doc, new_doc)
```

**Methods:**

- `detect_conflict(existing: Dict, new: Dict) -> ConflictResult`
  - Detect if two documents represent conflicting information
  - Returns: ConflictResult with score and category
  - Categories: "enrichment" (<0.1), "soft" (0.1-0.3), "hard" (>0.3)

- `calculate_conflict_score(doc1: Dict, doc2: Dict) -> float`
  - Calculate numeric conflict score (0-1)
  - Returns: Confidence-weighted conflict score

#### `ConflictResult`

```python
@dataclass
class ConflictResult:
    has_conflict: bool
    conflict_score: float  # 0-1
    category: str  # "enrichment", "soft", "hard"
    reasoning: str
    resolution_options: List[str]
```

---

## Truth & Grounding Engine

### `life_brain.truth_engine.groundedness`

Groundedness scoring and retrieval validation.

#### `GroundednessScorer`

```python
from life_brain.truth_engine.groundedness import GroundednessScorer

scorer = GroundednessScorer()
score = scorer.score_synthesis(answer, retrieved_docs, context)
```

**Methods:**

- `score_synthesis(answer: str, retrieved_docs: List[RetrievedDocument], context: Optional[Dict]) -> float`
  - Score how well answer is grounded in retrieved documents
  - Returns: Groundedness score (0-1)

- `score_document_relevance(doc: RetrievedDocument, query: str) -> float`
  - Score how relevant a document is to query
  - Returns: Relevance score (0-1)

- `validate_citations(answer: str, retrieved_docs: List[RetrievedDocument]) -> CitationValidation`
  - Validate that claims are properly supported
  - Returns: CitationValidation with issues list

#### `RetrievedDocument`

```python
@dataclass
class RetrievedDocument:
    doc_id: str
    text: str
    metadata: Dict[str, Any]
    similarity_score: float  # 0-1
```

---

## Retrieval & Search

### `life_brain.retrieval.alt_question_retrieval`

Multi-angle semantic search.

#### `AltQuestionRetrieval`

```python
from life_brain.retrieval import AltQuestionRetrieval

retriever = AltQuestionRetrieval(chroma_client, embedder)
results = retriever.search_by_query("What projects have you led?")
```

**Methods:**

- `search_by_query(query: str, top_k: int = 5, min_similarity: float = 0.5) -> List[Dict]`
  - Search across all question angles
  - Returns: Results ranked by relevance

- `search_by_angle(query: str, angle: SearchAngle, top_k: int = 5) -> List[MultiAngleSearchResult]`
  - Search focusing on specific angle (behavioral, metric, impact, etc.)
  - Returns: Results for that angle

- `search_all_angles(query: str, top_k: int = 3) -> Dict[str, List]`
  - Search same query across all angles
  - Returns: Dict mapping angle names to results

- `suggest_related_questions(answer_id: str) -> List[str]`
  - Get alternative phrasings for an answer
  - Returns: List of related questions

#### `SearchAngle`

```python
class SearchAngle(Enum):
    BEHAVIORAL = "behavioral"  # "What did you do in situation X?"
    METRIC_FOCUSED = "metric"  # "What metrics improved?"
    IMPACT_FOCUSED = "impact"  # "What was the business impact?"
    PROCESS_FOCUSED = "process"  # "How did you approach this?"
    LEARNING_FOCUSED = "learning"  # "What did you learn?"
```

#### `MultiAngleSearchSession`

```python
session = MultiAngleSearchSession(retriever)
result = session.search_with_suggestions("My accomplishments")
angle_results = session.explore_angle(SearchAngle.METRIC_FOCUSED)
```

**Methods:**

- `search_with_suggestions(query: str) -> Dict`
  - Search with AI-suggested angle recommendations
  - Returns: Primary results + suggested angles

- `explore_angle(angle: SearchAngle, top_k: int = 5) -> List`
  - Switch focus to different angle
  - Returns: Results for that angle

---

## Session Management

### `life_brain.session.session_manager`

Cross-turn state and context management.

#### `SessionManager`

```python
from life_brain.session.session_manager import SessionManager

manager = SessionManager()
session = manager.create_session(user_id="user_123")
```

**Methods:**

- `create_session(user_id: str, metadata: Optional[Dict] = None) -> Session`
  - Create new conversation session
  - Returns: Session object

- `resume_session(session_id: str) -> Optional[Session]`
  - Resume previous session
  - Returns: Session if found, None otherwise

- `save_session(session: Session) -> bool`
  - Persist session state
  - Returns: True if successful

- `get_session_context(session_id: str) -> Dict`
  - Get rich context for session
  - Returns: Context dict with history, state, metadata

#### `Session`

```python
@dataclass
class Session:
    session_id: str
    user_id: str
    created_at: str
    metadata: Dict[str, Any]  # User preferences, language, etc.
    context: Dict[str, Any]  # Shared state
    conversation_history: List[Dict]  # Messages
```

---

## Intent Detection

### `life_brain.intent.detector`

Intent detection for mode gate and use case routing.

#### `IntentDetector`

```python
from life_brain.intent.detector import IntentDetector

detector = IntentDetector()
intent = detector.detect_intent("I want to prepare for an interview")
```

**Methods:**

- `detect_intent(message: str) -> IntentResult`
  - Detect user intent from message
  - Returns: IntentResult with detected intent + confidence

- `detect_mode(message: str) -> ModeResult`
  - Detect conversation mode (small talk vs guided)
  - Returns: ModeResult with mode + confidence

- `match_use_cases(message: str, top_k: int = 10) -> List[UseCaseMatch]`
  - Find matching use cases
  - Returns: Top K use cases by relevance

#### `IntentResult`

```python
@dataclass
class IntentResult:
    intent: str  # e.g., "interview_prep", "career_planning"
    confidence: float  # 0-1
    keywords: List[str]  # Matched keywords
    mode: str  # "small_talk" or "guided"
```

---

## Framework & Utilities

### `life_brain.logging_framework`

Unified logging with performance tracking.

#### `LifeBrainLogger`

```python
from life_brain.logging_framework import (
    get_logger,
    set_log_level,
    LogLevel,
    log_execution_time,
    PerformanceMonitor,
)

logger = get_logger("my_module")
set_log_level(LogLevel.DEBUG)
```

**Functions:**

- `get_logger(module_name: str) -> logging.Logger`
  - Get logger for module
  - Returns: Logger instance

- `set_log_level(level: LogLevel) -> None`
  - Set global log level
  - Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

- `@log_execution_time(level=LogLevel.INFO)`
  - Decorator for automatic execution time logging
  - Logs function entry, exit, and any exceptions

#### `PerformanceMonitor`

```python
monitor = PerformanceMonitor("batch_ingestion")
monitor.record(0.5, "operation_1")
monitor.record(0.3, "operation_2")
monitor.log_report()
```

**Methods:**

- `record(duration: float, operation: str) -> None`
  - Record operation duration

- `report() -> Dict`
  - Get performance statistics
  - Returns: min, max, avg times, etc.

- `log_report() -> None`
  - Log report to logger

### `life_brain.monitoring_dashboard`

Real-time operation monitoring.

#### `MonitoringDashboard`

```python
from life_brain.monitoring_dashboard import get_dashboard, record_batch

dashboard = get_dashboard()
dashboard.record_batch(
    batch_id="batch_001",
    operation="ingestion",
    total_docs=100,
    successful_docs=95,
    failed_docs=5,
    duration_seconds=10.0,
)

status = dashboard.get_health_status()
print(dashboard.format_text_report())
```

**Methods:**

- `record_batch(batch_id, operation, total_docs, successful_docs, failed_docs, errors, duration) -> BatchMetric`
  - Record batch operation metrics

- `get_dashboard() -> Dict`
  - Get full dashboard state

- `get_health_status() -> Dict`
  - Get system health (healthy/warning/degraded/critical)

- `get_error_report() -> Dict`
  - Get detailed error breakdown

- `format_text_report() -> str`
  - Get human-readable dashboard report

### `life_brain.testing`

Testing framework utilities.

#### Test Base Classes

```python
from life_brain.testing import (
    BaseLifeBrainTest,
    BaseIntegrationTest,
    mock_retrieved_document,
    MockChromaDB,
    assert_valid_document,
)

class TestMyModule(BaseLifeBrainTest):
    def test_something(self):
        doc = mock_retrieved_document()
        assert_valid_document(doc)
```

**Classes:**

- `BaseLifeBrainTest`: Base test class with common setup/teardown
- `BaseIntegrationTest`: Integration test infrastructure

**Fixtures:**

- `mock_retrieved_document()` - Mock ChromaDB document
- `mock_metadata_dict()` - Mock metadata
- `sample_documents()` - Sample test documents
- `MockChromaDB` - Mock database
- `MockLLM` - Mock language model

**Assertions:**

- `assert_valid_document(doc)` - Validate document structure
- `assert_valid_metadata(metadata)` - Validate metadata
- `assert_similarity_in_range(score)` - Validate similarity score

---

## Error Handling

All modules follow consistent error handling:

```python
try:
    result = manager.ingest_documents(docs)
except ValidationError as e:
    print(f"Validation failed: {e.errors}")
except ConflictError as e:
    print(f"Conflict detected: {e.conflicts}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

---

## Configuration

Global configuration in `life_brain/config.py`:

```python
from life_brain.config import Config

config = Config()
config.set("chroma_path", "/path/to/data")
config.set("embedder_model", "sentence-transformers/all-MiniLM-L6-v2")
```

---

## Best Practices

1. **Always validate before ingesting**: Use `IngestionValidator` before adding documents
2. **Monitor performance**: Use `@log_execution_time` on critical paths
3. **Handle conflicts gracefully**: Check for conflicts and offer resolution options
4. **Use sessions**: Maintain session context for multi-turn conversations
5. **Log strategically**: Use `LogLevel.DEBUG` for development, `INFO` for production
6. **Test thoroughly**: Extend `BaseLifeBrainTest` for consistent testing

---

## Examples

### Complete Ingestion Workflow

```python
from life_brain.db.ingestion import IngestionManager, IngestionValidator
from life_brain.truth_engine.conflict import ConflictDetector
from life_brain.logging_framework import get_logger

logger = get_logger("ingestion_workflow")

validator = IngestionValidator()
detector = ConflictDetector()
manager = IngestionManager(chroma_client, validator)

# Validate document
doc = {"text": "...", "metadata": {...}}
if not validator.validate(doc):
    logger.warning(f"Validation failed for {doc['id']}")
    sys.exit(1)

# Check for conflicts
existing_doc = manager.get_similar_doc(doc)
if existing_doc:
    conflict = detector.detect_conflict(existing_doc, doc)
    if conflict.has_conflict:
        logger.info(f"Conflict detected: {conflict.reasoning}")

# Ingest
result = manager.ingest_documents([doc])
logger.info(f"Ingestion complete: {result.success_count} successful")
```

### Multi-Angle Search Workflow

```python
from life_brain.retrieval import AltQuestionRetrieval, MultiAngleSearchSession

retriever = AltQuestionRetrieval(chroma_client, embedder)
session = MultiAngleSearchSession(retriever)

# Get suggestions
result = session.search_with_suggestions("Tell me about your projects")
print(f"Suggested angles: {result['suggested_angles']}")

# Explore metric angle
metrics_results = session.explore_angle(SearchAngle.METRIC_FOCUSED)
print(f"Found {len(metrics_results)} metric-focused results")
```

---

**Last Updated:** March 2026
**Status:** Complete & Production-Ready
