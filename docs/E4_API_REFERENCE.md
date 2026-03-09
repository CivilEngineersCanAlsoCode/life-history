# E4 API Reference for Wave 1 Agents

**Purpose**: Understand exactly what F5.1, F5.2, F5.4 will receive and return.

---

## RetrievedDocument (from E4)

```python
@dataclass
class RetrievedDocument:
    """A document retrieved from vector search."""
    doc_id: str                          # Unique document identifier
    text: str                            # Full document text
    metadata: Dict[str, Any]             # Rich metadata (source, date, author, etc.)
    embedding: Optional[List[float]]     # Vector embedding (typically 1536 dims)
    similarity_score: float              # 0-1, cosine similarity to query
```

### Example RetrievedDocument
```python
RetrievedDocument(
    doc_id="doc_interview_prep_2024",
    text="Behavioral interview prep: STAR method explanation...",
    metadata={
        "source": "internal_notes",
        "date": "2024-03-08",
        "author": "self",
        "category": "career",
        "domain": "interview_prep",
        "type": "guide"
    },
    embedding=[0.123, -0.456, ..., 0.789],  # 1536 dimensions
    similarity_score=0.92
)
```

---

## GroundednessScore (from E4)

```python
@dataclass
class GroundednessScore:
    """Quantitative groundedness assessment."""
    max_similarity: float       # Max cosine similarity (0-1)
    avg_similarity: float       # Average across all docs
    num_supporting_docs: int    # Count of docs supporting answer (0-3)
    coverage: float             # Fraction of query covered (0-1)
    consistency: float          # Agreement across docs (0-1)
    overall_score: float        # Composite score (0-1)
```

### Confidence Level Mapping

| overall_score | confidence_level | output_type |
|---|---|---|
| > 0.85 | HIGH | DIRECT_ANSWER |
| 0.70-0.85 | MEDIUM | QUALIFIED_ANSWER |
| 0.50-0.70 | LOW | UNCERTAIN_ANSWER |
| < 0.50 | INSUFFICIENT | NO_MATCH |

**Critical**: Thresholds are `>` for upper bounds and `>=` for lower bounds.

---

## What F5 Receives from E4

### Input to F5.1 (ConflictDetector)
```python
documents: List[RetrievedDocument]  # Usually 3, max 3
```

Agents should expect:
- 1-3 documents (rarely more)
- Varying similarity scores (0.5-1.0)
- Rich metadata with dates, sources, types
- Real text from career knowledge base

### Input to F5.2 (CredibilityScorer)
```python
doc: RetrievedDocument              # Single document
context: Dict[str, Any]             # Query context (intent, user_profile, etc.)
```

Agents should extract from metadata:
- `date`: Document creation/update date
- `source`: Where document came from (internal_notes, expert, research, etc.)
- `author`: Who wrote it
- `category`: Domain (career, interview, health, finance, etc.)
- `type`: Document type (guide, story, metric, fact, etc.)

### Input to F5.4 (HallucinationPrevention)
```python
answer: str                         # Generated answer text
docs: List[RetrievedDocument]       # Supporting documents (1-3)
context: Dict[str, Any]             # Query context
```

---

## Output Schemas (Required)

### F5.1 Output: ConflictResult

```python
@dataclass
class ConflictResult:
    doc_pair: Tuple[int, int]       # Indices of conflicting docs (e.g., (0, 1))
    conflict_score: float            # 0-1, magnitude of conflict
    conflict_type: ConflictType      # Enum: QUANTITATIVE, QUALITATIVE, SEMANTIC
    severity: str                    # "low" (0.1-0.3), "medium" (0.3-0.6), "high" (0.6+)
    claim1: str                      # First conflicting claim
    claim2: str                      # Second conflicting claim
    explanation: str                 # Human-readable explanation
```

**Algorithm**: `conflict_score = semantic_similarity × contradiction_magnitude`

### F5.2 Output: CredibilityScore

```python
@dataclass
class CredibilityScore:
    doc_id: str                      # Same as RetrievedDocument.doc_id
    credibility: float               # 0-1, overall trustworthiness
    category: str                    # "expert", "verified", "personal", "questionable"
    recency_score: float             # Component (0-1)
    authority_score: float           # Component (0-1)
    accuracy_score: float            # Component (0-1)
    explanation: str                 # Human-readable justification
```

**Formula**: `credibility = (recency × 0.3) + (authority × 0.4) + (accuracy × 0.3)`

### F5.4 Output: ValidationResult

```python
@dataclass
class ValidationResult:
    is_valid: bool                   # Pass all rules?
    passed_rules: List[str]          # Rule names that passed
    violated_rules: List[RuleViolation]  # Rule names that failed
    rejection_reason: Optional[str]  # Why rejected (if is_valid=False)

@dataclass
class RuleViolation:
    rule_name: str                   # E.g., "confidence_floor"
    severity: str                    # "error" or "warning"
    message: str                     # Explanation
```

---

## Integration Points

### How F5.3 Will Call F5.1

```python
from life_brain.truth_engine.conflict_detector import ConflictDetector

detector = ConflictDetector()
conflicts = detector.detect_conflicts(retrieved_docs)  # List[ConflictResult]

for conflict in conflicts:
    if conflict.conflict_score > 0.3:  # Soft conflict threshold
        # Add disclaimer to synthesis
        disclaimer = f"Note: Sources disagree on {conflict.explanation}"
```

### How F5.3 Will Call F5.2

```python
from life_brain.truth_engine.credibility_scorer import CredibilityScorer

scorer = CredibilityScorer()
scores = {doc.doc_id: scorer.score_source(doc) for doc in docs}

# Sort by credibility
ranked = sorted(docs,
    key=lambda d: scores[d.doc_id].credibility,
    reverse=True)

# Prefer highest-credibility sources
best_doc = ranked[0]
```

### How F5.5 Will Wire Everything

```python
def process_with_truth_engine(
    user_query: str,
    retrieved_docs: List[RetrievedDocument],
    answer: str
) -> Dict:
    # Step 1: Detect conflicts
    conflicts = conflict_detector.detect_conflicts(retrieved_docs)

    # Step 2: Score credibility
    credibility_scores = [
        credibility_scorer.score_source(doc)
        for doc in retrieved_docs
    ]

    # Step 3: Validate answer
    validation = hallucination_prevention.validate_answer(
        answer,
        retrieved_docs,
        {
            'conflicts': conflicts,
            'credibility_scores': credibility_scores
        }
    )

    # Step 4: Return result
    return {
        'answer': answer if validation.is_valid else "I don't know",
        'conflicts': conflicts,
        'credibility': credibility_scores,
        'validation': validation
    }
```

---

## Performance Budget

Total E5 latency added to E4 pipeline: **< 500ms**

- F5.1 Conflict Detection: **< 100ms** per 3-doc batch
- F5.2 Credibility Scoring: **< 50ms** per document (multiply by doc count)
- F5.4 Validation Rules: **< 20ms** per answer
- F5.3 Synthesis: **< 150ms**
- **Total**: ~500ms max

Keep algorithms lightweight and avoid:
- Expensive NLP models
- Nested LLM calls
- Fine-tuning operations
- Unoptimized loops

---

## Test Data Available

Sample documents in `tests/fixtures/` (created by prep work):
- `conflict_test_data.json` - Documents with known conflicts
- `credibility_test_data.json` - Sources with different trust levels
- `hallucination_test_data.json` - Known hallucination cases

---

## Import Path Reference

```python
# RetrievedDocument, GroundednessScore
from life_brain.truth_engine.groundedness import RetrievedDocument, GroundednessScore

# Enums
from life_brain.truth_engine.groundedness import ConfidenceLevel, OutputType

# Your implementations (create these)
from life_brain.truth_engine.conflict_detector import ConflictDetector, ConflictResult
from life_brain.truth_engine.credibility_scorer import CredibilityScorer, CredibilityScore
from life_brain.truth_engine.hallucination_prevention import HallucinationPrevention, ValidationResult
```

---

**Ready to implement? Use this as your north star.**
