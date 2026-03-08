# Wave 1 Integration Contract

**Purpose**: Define exact integration points between F5.1, F5.2, F5.4 and F5.3, F5.5

**Date**: 2026-03-08
**Status**: Ready for agent implementation

---

## Module Responsibilities

### F5.1: ConflictDetector (AzureCove)
**Input**: List[RetrievedDocument] (1-3 docs)
**Output**: List[ConflictResult]
**Latency**: < 100ms per batch

**Public Interface**:
```python
from life_brain.truth_engine.conflict_detector import ConflictDetector, ConflictResult

detector = ConflictDetector()
conflicts = detector.detect_conflicts(docs)  # List[ConflictResult]
```

**Exact Dataclass** (from skeleton_modules.py):
```python
@dataclass
class ConflictResult:
    doc_pair: Tuple[int, int]       # (0, 1), (0, 2), or (1, 2)
    conflict_score: float            # 0-1
    conflict_type: ConflictType      # QUANTITATIVE, QUALITATIVE, SEMANTIC
    severity: str                    # "low", "medium", "high"
    claim1: str                      # Text from doc at index doc_pair[0]
    claim2: str                      # Text from doc at index doc_pair[1]
    explanation: str                 # Why they conflict
```

**Test Data Available**:
`tests/fixtures/conflict_test_data.json` — 5 real scenarios with expected outputs

---

### F5.2: CredibilityScorer (SwiftGlacier)
**Input**: RetrievedDocument + optional context
**Output**: CredibilityScore
**Latency**: < 50ms per document

**Public Interface**:
```python
from life_brain.truth_engine.credibility_scorer import CredibilityScorer, CredibilityScore

scorer = CredibilityScorer()
score = scorer.score_source(doc, context=None)  # Single CredibilityScore
scores = [scorer.score_source(doc) for doc in docs]  # List[CredibilityScore]
ranked = scorer.rank_by_credibility(docs)  # Sorted by credibility
```

**Exact Dataclass**:
```python
@dataclass
class CredibilityScore:
    doc_id: str                      # Same as RetrievedDocument.doc_id
    credibility: float               # 0-1
    category: str                    # "expert", "verified", "personal", "questionable"
    recency_score: float             # Component 0-1
    authority_score: float           # Component 0-1
    accuracy_score: float            # Component 0-1
    explanation: str                 # Human readable
```

**Scoring Formula** (EXACT):
```
credibility = (recency × 0.3) + (authority × 0.4) + (accuracy × 0.3)
```

**Test Data Available**:
`tests/fixtures/credibility_test_data.json` — 7 scenarios with scoring examples

---

### F5.4: HallucinationPrevention (AmberFinch)
**Input**: answer (str), docs (List[RetrievedDocument]), context (Dict)
**Output**: ValidationResult
**Latency**: < 20ms per answer

**Public Interface**:
```python
from life_brain.truth_engine.hallucination_prevention import (
    HallucinationPrevention, ValidationResult, RuleViolation
)

validator = HallucinationPrevention()
result = validator.validate_answer(answer, docs, context)  # ValidationResult
```

**Exact Dataclass**:
```python
@dataclass
class ValidationResult:
    is_valid: bool                   # True if all rules pass
    passed_rules: List[str]          # ["synthesis_limits", "confidence_floor", ...]
    violated_rules: List[RuleViolation]  # [RuleViolation(...), ...]
    rejection_reason: Optional[str]  # If is_valid=False

@dataclass
class RuleViolation:
    rule_name: str                   # "confidence_floor", "date_integrity", etc.
    severity: str                    # "error" (fail) or "warning" (alert)
    message: str                     # Detailed explanation
```

**Five Rules** (in order):
1. **Synthesis Limits**: Max 3 docs, no synthesis across contradictions
2. **Confidence Floor**: groundedness >= 0.50
3. **Date Integrity**: Don't use old docs for recent questions (>365 days)
4. **Authority Matching**: Document type matches question type
5. **Factuality Checks**: Numeric consistency ±10%, date alignment, names verified

**Test Data Available**:
`tests/fixtures/hallucination_test_data.json` — 7 test cases with expected pass/fail

---

## How F5.3 (Synthesis) Will Call F5.1 + F5.2

```python
from life_brain.truth_engine.conflict_detector import ConflictDetector
from life_brain.truth_engine.credibility_scorer import CredibilityScorer

# After retrieval from E4
docs: List[RetrievedDocument] = [...]  # 1-3 docs

# Step 1: Detect conflicts
detector = ConflictDetector()
conflicts = detector.detect_conflicts(docs)

# Step 2: Score credibility
scorer = CredibilityScorer()
credibility_scores = [scorer.score_source(doc) for doc in docs]

# Step 3: Rank by credibility
ranked_docs = scorer.rank_by_credibility(docs)

# Step 4: Synthesis decision
if conflicts:  # If conflicts detected
    if any(c.conflict_score > 0.3 for c in conflicts):
        # Present multiple perspectives
        answer = synthesize_conflicting_perspectives(ranked_docs, conflicts)
    else:
        # Safe to synthesize
        answer = synthesize_single_answer(ranked_docs)
else:
    # No conflicts, synthesize freely
    answer = synthesize_single_answer(ranked_docs)
```

---

## How F5.5 (Integration) Will Call All Three

```python
from life_brain.truth_engine.conflict_detector import ConflictDetector
from life_brain.truth_engine.credibility_scorer import CredibilityScorer
from life_brain.truth_engine.hallucination_prevention import HallucinationPrevention

def process_with_truth_engine(
    user_query: str,
    retrieved_docs: List[RetrievedDocument],
    generated_answer: str,
    groundedness_score: float
) -> Dict:
    """
    Full E5 pipeline: detect → score → validate → output.
    """
    # Step 1: Conflict detection
    detector = ConflictDetector()
    conflicts = detector.detect_conflicts(retrieved_docs)

    # Step 2: Credibility scoring
    scorer = CredibilityScorer()
    credibility_scores = [
        scorer.score_source(doc)
        for doc in retrieved_docs
    ]

    # Step 3: Hallucination validation
    validator = HallucinationPrevention()
    validation = validator.validate_answer(
        generated_answer,
        retrieved_docs,
        {
            'groundedness_score': groundedness_score,
            'conflicts': conflicts,
            'credibility_scores': credibility_scores,
            'user_query': user_query
        }
    )

    # Step 4: Output decision
    if validation.is_valid:
        final_answer = generated_answer
        confidence = "high" if groundedness_score > 0.85 else "medium"
    else:
        final_answer = f"I don't have enough information: {validation.rejection_reason}"
        confidence = "low"

    return {
        'answer': final_answer,
        'confidence': confidence,
        'conflicts': conflicts,
        'credibility_scores': credibility_scores,
        'validation': validation,
        'groundedness': groundedness_score,
        'sources': [
            {'doc_id': d.doc_id, 'similarity': d.similarity_score}
            for d in retrieved_docs
        ]
    }
```

---

## Critical Design Decisions

### Dataclass Immutability
- All output dataclasses MUST be frozen (`@dataclass(frozen=True)`)
- This prevents F5.3/F5.5 from accidentally modifying them

### No Side Effects
- ConflictDetector, CredibilityScorer, HallucinationPrevention should be stateless
- Initialize once, reuse many times
- No database writes, API calls, or external state changes

### Error Handling
- If algorithm fails (e.g., NLP error), return sensible defaults:
  - ConflictDetector: return empty list (no conflicts detected)
  - CredibilityScorer: return middle-ground score (0.5)
  - HallucinationPrevention: return is_valid=True (don't block answers)

### Logging
- Use Python's `logging` module (not print)
- Log at INFO level for key decisions, DEBUG for algorithmic steps
- Example: `logger.info(f"Detected {len(conflicts)} conflicts")`

---

## Test Validation Checklist

Before F5.3/F5.5 agents start, ALL of these must pass:

**F5.1 Tests** (40+ cases):
- [ ] Detects all 5 conflict_test_data scenarios correctly
- [ ] Conflict scores match expected ±0.05
- [ ] Conflict types classified correctly
- [ ] Empty input returns []
- [ ] Single doc returns []
- [ ] Edge cases handled (special chars, dates, numbers)

**F5.2 Tests** (35+ cases):
- [ ] Scores all 7 credibility_test_data scenarios correctly
- [ ] Recent docs score higher than old (same authority)
- [ ] Expert > personal > unknown
- [ ] Verified > unverified
- [ ] rank_by_credibility() sorts descending
- [ ] Explanations are human-readable

**F5.4 Tests** (50+ cases):
- [ ] All 5 rules implemented
- [ ] test_cases from hallucination_test_data.json pass
- [ ] Low groundedness (< 0.50) fails validation
- [ ] High groundedness (> 0.85) passes all rules
- [ ] Numeric tolerance (±10%) applied correctly
- [ ] Date integrity checked

---

## Performance Targets

| Component | Target | Test | Pass Criteria |
|-----------|--------|------|---------------|
| F5.1 | < 100ms/batch | 3 docs, 100 trials | 95th percentile < 100ms |
| F5.2 | < 50ms/doc | Single doc, 100 trials | 95th percentile < 50ms |
| F5.4 | < 20ms/answer | Single answer, 100 trials | 95th percentile < 20ms |
| Total E5 | < 500ms | Full pipeline, 50 trials | 95th percentile < 500ms |

**Measurement Method**:
```python
import time
start = time.perf_counter()
# ... call function ...
elapsed = time.perf_counter() - start
print(f"Elapsed: {elapsed*1000:.1f}ms")
```

---

## File Locations

| File | Purpose |
|------|---------|
| `life_brain/truth_engine/skeleton_modules.py` | Exact dataclasses & signatures |
| `life_brain/truth_engine/E4_API_REFERENCE.md` | E4 input/output reference |
| `tests/fixtures/conflict_test_data.json` | 5 test scenarios for F5.1 |
| `tests/fixtures/credibility_test_data.json` | 7 test scenarios for F5.2 |
| `tests/fixtures/hallucination_test_data.json` | 7 test scenarios for F5.4 |

---

## Next Steps (for F5.3 & F5.5 agents)

1. Wait for Wave 1 agents to complete and push code
2. Run integration test suite: `pytest tests/test_e5_integration.py`
3. Implement F5.3 using ConflictResult + CredibilityScore outputs
4. Implement F5.5 by wiring all components and running E4 regression tests
5. All 48 E4 tests must still pass after E5 integration

---

**Contract Version**: 1.0
**Status**: READY FOR IMPLEMENTATION
**Last Updated**: 2026-03-08
