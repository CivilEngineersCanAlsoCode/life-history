# E5: Truth & Grounding Engine — Implementation Plan

**Status**: Pre-Planning (Identified as P0 blocker after E4)
**Priority**: P0 - Foundation for all retrieval
**Date**: 2026-03-08

---

## Executive Summary

**E5** is the critical foundation for preventing hallucinations in the career knowledge base system. It builds on E4 (Intent Detection → Citations) to add:

1. **Conflict Detection**: Identify contradictions in retrieved documents
2. **Source Credibility**: Score document trustworthiness
3. **Multi-perspective Synthesis**: Combine viewpoints safely
4. **Hallucination Prevention**: Hard rules before generation

This epic **blocks all downstream conversation features** (F4, F6) until complete.

---

## Current State (E4 Complete)

### ✅ What E4 Gives Us

1. **Intent Detection** (CopperBear)
   - User intent with confidence 0-1
   - Use case categorization (career, interview, projects, etc.)

2. **Citations & Groundedness** (CyanFalcon)
   - Groundedness score (0-1)
   - Top 3 documents selected by relevance
   - Citation formatting with source + confidence
   - Boundary conditions: 0.50 (add citations), 0.85 (high confidence)

3. **Mode Monitoring** (PearlLantern)
   - Intent shift detection
   - Mode selection UI (small_talk ↔ guided)
   - Session continuity tracking

### ⚠️ What E4 Does NOT Do

- ❌ Detect conflicts between documents
- ❌ Assess source trustworthiness
- ❌ Handle multiple contradictory perspectives
- ❌ Prevent synthesis of conflicting information
- ❌ Score fact vs. opinion

---

## E5 Requirements

### E5.1: Conflict Detection Engine

**Goal**: Identify when retrieved documents contradict each other

**Inputs**:
- Top 3 documents (from CyanFalcon)
- User intent/use case
- Historical facts (if available)

**Outputs**:
- Conflict score (0-1) for each document pair
- Conflict type (quantitative, qualitative, semantic)
- Severity (low, medium, high)

**Algorithm**:
```
For each document pair (D1, D2):
  1. Extract claims from both
  2. Compute semantic similarity of claims
  3. If claims similar but contradictory → flag conflict
  4. Score: similarity × contradiction_magnitude
  5. Categorize by type

Example:
- D1: "Backend engineer salary $150k-200k"
- D2: "Backend engineer salary $120k-180k"
- Overlap: YES
- Contradiction: Quantitative (ranges overlap but boundaries differ)
- Severity: LOW (ranges overlap significantly)
```

**Success Criteria**:
- [ ] Detects 80%+ of obvious contradictions
- [ ] Classifies conflict type correctly
- [ ] Scores severity appropriately
- [ ] Runs in < 200ms for 3 documents

### E5.2: Source Credibility Scoring

**Goal**: Assess trustworthiness of each source

**Inputs**:
- Document metadata (source, date, author, category)
- Document type (personal, research, official, archive)
- Update recency
- Historical accuracy (if available)

**Outputs**:
- Credibility score (0-1) per document
- Credibility category (expert, verified, personal, questionable)
- Explanation (why is this trustworthy?)

**Scoring Framework**:
```
Credibility = (recency × 0.3) + (authority × 0.4) + (accuracy × 0.3)

Recency (0-1):
- < 3 months: 1.0
- 3-6 months: 0.8
- 6-12 months: 0.6
- > 12 months: 0.4

Authority (0-1):
- Official/researched: 1.0
- Professional/verified: 0.8
- Personal/expert: 0.7
- Community/archive: 0.5
- Unknown: 0.3

Accuracy (0-1):
- Verified fact: 1.0
- Corroborated (2+ sources): 0.9
- Single source: 0.7
- Potentially outdated: 0.5
- Contradicted by other sources: 0.2
```

**Success Criteria**:
- [ ] Scores documents by credibility
- [ ] Expert sources rank higher than archive
- [ ] Recent documents prefer over old
- [ ] Documented scoring rationale

### E5.3: Multi-Perspective Synthesis

**Goal**: Combine conflicting viewpoints safely without hallucinating

**Inputs**:
- Conflicting documents with credibility scores
- Conflict type and severity
- User intent

**Outputs**:
- Synthesis strategy (agree, differ, unknown)
- Combined answer with disclaimers
- Attribution to each perspective

**Synthesis Rules**:
```
IF conflicts detected:
  1. Rank by credibility score
  2. IF high_credibility_conflict:
       → Present both perspectives
       → Example: "Some sources say X (expert source), others say Y (research-based)"
  3. ELIF low_credibility_conflict:
       → Favor high-credibility source
       → Note: "Primary source indicates X; conflicting information exists but less verified"
  4. IF majority_agreement:
       → Present as consensus
       → Note uncertainty percentages
```

**Success Criteria**:
- [ ] Never synthesizes contradictions as single fact
- [ ] Attributes conflicting claims to sources
- [ ] Handles 3+ conflicting documents
- [ ] Clear disclaimers when uncertainty

### E5.4: Hallucination Prevention Rules

**Goal**: Hard rules to prevent impossible/false outputs

**Prevention Strategies**:

1. **Synthesis Limits** (from E4)
   - [ ] Max 3 documents per answer (already implemented)
   - [ ] No synthesis across contradictory sources

2. **Confidence Floor**
   - [ ] If groundedness < 0.50 → "I don't know"
   - [ ] If conflict detected + low credibility → "Multiple sources disagree; insufficient evidence"

3. **Date Integrity**
   - [ ] Don't cite facts from documents older than confidence threshold
   - [ ] Example: "Career advice from 2020" vs "2024 market trends"

4. **Authority Matching**
   - [ ] Match document authority to question type
   - [ ] Example: Career guidance question → require "personal experience" or "expert" source

5. **Factuality Checks**
   - [ ] Numeric facts must be consistent across sources (±10%)
   - [ ] Dates must align with known events
   - [ ] Names/titles must be verified

**Success Criteria**:
- [ ] Prevents 95%+ of obvious hallucinations
- [ ] Clear logging of rules violated
- [ ] Human-understandable rejection reasons

### E5.5: Query Decomposition (Already Implemented)

**Status**: Already complete from earlier session
- Complex questions broken into sub-questions
- Each sub-question answered independently
- Results synthesized safely

---

## Dependency Analysis

### ✅ E5 Depends On (Satisfied by E4)

- Intent detection with confidence scores ✅
- Top 3 documents selected ✅
- Groundedness scoring ✅
- Document metadata available ✅

### ⚠️ E5 Blocks (Must Complete Before)

- **F4**: Conversation Features
  - F4.1: Mode Gate Orchestration (ready but needs truth engine)
  - F4.2-4.5: One-by-one Q&A, Expert intro, Panels

- **F6**: Session Continuity
  - Needs truth engine to maintain consistency across turns

- **F7**: Production Testing
  - Needs truth engine for quality validation

---

## Implementation Strategy

### Phase 1: Conflict Detection (2-3 days)

**Files to Create**:
- `life_brain/truth_engine/conflict_detector.py`
- `tests/test_conflict_detection.py`

**Key Functions**:
```python
class ConflictDetector:
    def detect_conflicts(docs: List[RetrievedDocument]) -> List[ConflictResult]:
        """Compare all document pairs for contradictions."""

    def score_conflict(claim1, claim2) -> float:
        """Compute conflict score 0-1."""

    def categorize_conflict(conflict) -> ConflictType:
        """Classify as quantitative, qualitative, semantic."""
```

**Tests**:
- [ ] Same fact, different values (quantitative)
- [ ] Same claim, different framing (semantic)
- [ ] Complementary facts (no conflict)
- [ ] Direct contradictions (high conflict)

### Phase 2: Source Credibility (1-2 days)

**Files to Create**:
- `life_brain/truth_engine/credibility_scorer.py`
- `tests/test_credibility_scoring.py`

**Key Functions**:
```python
class CredibilityScorer:
    def score_source(doc: RetrievedDocument, context: Dict) -> CredibilityScore:
        """Compute credibility 0-1."""

    def rank_by_credibility(docs: List[RetrievedDocument]) -> List[RetrievedDocument]:
        """Sort by credibility descending."""

    def get_credibility_explanation(doc: RetrievedDocument) -> str:
        """Human-readable justification."""
```

**Tests**:
- [ ] Recent documents score higher than old
- [ ] Expert sources score higher than personal
- [ ] Verified facts score higher than unverified

### Phase 3: Synthesis Rules (1-2 days)

**Files to Create**:
- `life_brain/truth_engine/synthesis_engine.py`
- `tests/test_synthesis_engine.py`

**Key Functions**:
```python
class SynthesisEngine:
    def synthesize_conflicting_docs(docs: List[RetrievedDocument],
                                   conflicts: List[ConflictResult]) -> SynthesisResult:
        """Combine perspectives safely."""

    def add_conflict_disclaimer(answer: str, conflicts: List[ConflictResult]) -> str:
        """Append disclaimer about disagreements."""
```

**Tests**:
- [ ] Disagreements presented as alternatives
- [ ] Disclaimers added when conflicts
- [ ] High-credibility sources preferred

### Phase 4: Hallucination Prevention (1 day)

**Files to Create**:
- `life_brain/truth_engine/hallucination_prevention.py`
- `tests/test_hallucination_prevention.py`

**Key Functions**:
```python
class HallucinationPrevention:
    def validate_answer(answer: str, docs: List[RetrievedDocument]) -> ValidationResult:
        """Check answer against 5 prevention rules."""

    def get_rejection_reason(violation: Rule) -> str:
        """Human-understandable why we can't answer."""
```

**Tests**:
- [ ] Low groundedness → "I don't know"
- [ ] Conflicting sources → disclaimer
- [ ] Old information → date warning
- [ ] Numeric inconsistency → rejection
- [ ] Authority mismatch → rejection

### Phase 5: Integration with E4 (1 day)

**Files to Modify**:
- `life_brain/truth_engine/groundedness.py` (update OutputGenerator)
- `tests/test_e4_e5_integration.py` (new integration tests)

**Integration Points**:
```
Current Flow (E4):
Intent → Docs → Groundedness Score → Format Attribution

New Flow (E4+E5):
Intent → Docs → [NEW] Conflict Detection → [NEW] Credibility Score
         → [NEW] Synthesis + Disclaimers → [NEW] Hallucination Check
         → Groundedness Score → Format Attribution
```

---

## Prep Work (Can Start Now)

While agents finish E4, we can prep:

### 1. Data Structure Design ✅ (In Progress)
- `ConflictResult` dataclass
- `CredibilityScore` dataclass
- `SynthesisResult` dataclass
- `ValidationResult` dataclass

### 2. Test Fixtures
- Create dataset of conflicting documents for testing
- Create dataset of different source types
- Create dataset of hallucination examples

### 3. Algorithm Research
- Semantic similarity algorithms for conflict detection
- Credibility scoring models
- Synthesis strategies

### 4. Documentation
- E5 requirements specification ← **We're doing this now**
- Module architecture diagram
- Integration points

---

## Timeline & Dependencies

```
Timeline:
Current: 2026-03-08
├─ E4 Complete: 2026-03-08 (waiting for CopperBear)
├─ E5 Phase 1-5: 2026-03-08 to 2026-03-15 (5-7 days)
├─ E5 Integration Tests: 2026-03-15
├─ E5 Complete: 2026-03-16
└─ F4/F6 Can Start: 2026-03-16

Dependencies Graph:
E1 (Data Ingestion) ✅ → E4 (Intent/Citations) ⏳ → E5 (Truth Engine) 🔜
                                                   → F4 (Conversation) 🔜
                                                   → F6 (Sessions) 🔜
```

---

## Success Criteria

- [ ] Conflict detection catches 90%+ of contradictions
- [ ] Credibility scoring differentiates sources meaningfully
- [ ] Synthesis combines perspectives without hallucinating
- [ ] 100% of E5.4 hallucination rules implemented
- [ ] All 40+ E4 integration tests still pass with E5
- [ ] E5 adds < 500ms latency to end-to-end flow
- [ ] Documentation complete
- [ ] 100+ unit tests across E5 modules
- [ ] Zero hallucination false negatives in manual testing

---

## Risk & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Conflict detection misses subtle contradictions | High | Medium | Extensive test dataset, manual validation |
| Credibility scoring is too aggressive | Medium | Medium | Tuning thresholds, expert review |
| Synthesis adds too much latency | Low | High | Optimize semantic similarity, cache results |
| Hallucination rules too strict | Medium | Low | User feedback loop, adjustable thresholds |

---

## Questions for Design Review

1. **Conflict Detection**: Should we use semantic similarity or keyword-based approach first?
2. **Credibility**: How do we source the metadata (date, author, category)?
3. **Synthesis**: Should we show conflicting sources to user, or synthesize internally?
4. **Prevention**: Should hallucination rules be hard gates or soft warnings?
5. **Performance**: Are we okay with 200-300ms additional latency for truth engine?

---

## Next Steps (After E4 Complete)

1. [ ] Review this plan with team
2. [ ] Address design questions
3. [ ] Create ConflictDetector module
4. [ ] Create test fixtures
5. [ ] Iterate through 5 phases
6. [ ] Integrate with E4
7. [ ] Deploy to production

---

**Owner**: TurquoisePond (Coordinator)
**Status**: Ready for implementation queue
**Last Updated**: 2026-03-08
