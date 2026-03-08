# E5: Truth & Grounding Engine — Beads Planning & Breakdown

**Date**: 2026-03-08
**Status**: ✅ Fully planned in beads, ready for agent execution
**Epic ID**: issues-666
**Total Features**: 5 (F5.1 → F5.5)
**Total Tasks**: 42+ tasks (detailed in beads)

---

## 🎯 E5 Overview

**Mission**: Prevent hallucinations in the career knowledge base system by detecting conflicts, scoring credibility, synthesizing safely, and validating outputs.

**Scope**:
- Identifies contradictions in retrieved documents
- Assesses source trustworthiness
- Safely combines conflicting viewpoints
- Enforces hard rules against hallucinations
- Integrates with E4 pipeline

**Impact**: Unblocks F4 (Conversation Features) and F6 (Session Continuity)

---

## 📊 Beads Structure

### Epic: E5 (issues-666)
```
E5: Truth & Grounding Engine — P0
│
├─ F5.1 (issues-eky) — P0 ← READY NOW
│  └─ Conflict Detection Engine
│     • Detect contradictions
│     • Categorize conflict types
│     • Score severity (0-1)
│
├─ F5.2 (issues-i99) — P0 ← READY NOW
│  └─ Source Credibility Scoring
│     • Recency + Authority + Accuracy
│     • Ranking & explanation
│     • Credibility categories
│
├─ F5.4 (issues-xpd) — P0 ← READY NOW
│  └─ Hallucination Prevention Rules
│     • Synthesis limits
│     • Confidence floor
│     • Date integrity
│     • Authority matching
│     • Factuality checks
│
├─ F5.3 (issues-way) — P1 ◐ BLOCKED BY: F5.1, F5.2
│  └─ Multi-Perspective Synthesis
│     • Conflict-aware synthesis
│     • Disclaimer generation
│     • Attribution formatting
│
└─ F5.5 (issues-uqn) — P1 ◐ BLOCKED BY: F5.1, F5.2, F5.3, F5.4
   └─ E4 Integration & Production Testing
      • Wire all components
      • End-to-end tests (20+)
      • Performance validation
      • Deployment checklist
```

---

## 🔄 Execution Timeline

### Phase 1: Parallel Execution (Wave 1) — ~2-3 days

**3 agents start immediately**:

```
Agent 1: F5.1 (Conflict Detection)
  ├─ T5.1.1: ConflictDetector class
  ├─ T5.1.2: Scoring algorithm
  ├─ T5.1.3: Conflict categorization
  ├─ T5.1.4: Edge cases
  ├─ T5.1.5: 40+ test cases
  └─ T5.1.6: Documentation
  ⏱️  Est: 2-3 days

Agent 2: F5.2 (Credibility Scoring)
  ├─ T5.2.1: CredibilityScorer class
  ├─ T5.2.2: Scoring formula (recency+authority+accuracy)
  ├─ T5.2.3: Ranking & explanation
  ├─ T5.2.4: Edge cases
  ├─ T5.2.5: 35+ test cases
  └─ T5.2.6: Documentation
  ⏱️  Est: 2-3 days

Agent 3: F5.4 (Hallucination Prevention)
  ├─ T5.4.1: HallucinationPrevention class
  ├─ T5.4.2-4.6: 5 validation rules
  ├─ T5.4.7: 50+ test cases
  └─ T5.4.8: Documentation
  ⏱️  Est: 2-3 days
```

**Status**: 🟢 **All 3 agents can start immediately (no blockers)**

---

### Phase 2: Sequential Execution (Wave 2) — ~2 days

**After Phase 1 completes, 2 more agents start**:

```
Agent 4: F5.3 (Multi-Perspective Synthesis)
  ├─ WAITS FOR: F5.1 output schema + F5.2 credibility ranking
  ├─ T5.3.1: SynthesisEngine class
  ├─ T5.3.2: Strategy selection
  ├─ T5.3.3: Conflict-aware generation
  ├─ T5.3.4: Disclaimer generation
  ├─ T5.3.5: Attribution formatting
  ├─ T5.3.6: 45+ test cases
  └─ T5.3.7: Documentation
  ⏱️  Est: 1-2 days

Agent 5: F5.5 (E4 Integration)
  ├─ WAITS FOR: All F5.1-F5.4 complete
  ├─ T5.5.1-5.4: Wire components to groundedness.py
  ├─ T5.5.5: 20+ integration tests
  ├─ T5.5.6: Performance benchmarking
  ├─ T5.5.7: Production validation
  └─ T5.5.8: Deployment checklist
  ⏱️  Est: 1 day
```

**Status**: 🟠 **Blocked until Phase 1 complete**

---

## 📈 Critical Path & Dependencies

```
F5.1 ────────────┐
                 ├─→ F5.3 ──┐
F5.2 ────────────┤          │
                 │          ├─→ F5.5
F5.4 ────────────┘          │
                            │
                            ↓
                      (Integration)
```

**Critical Path** (longest time to completion):
- F5.1 (2-3 days) → F5.3 (1-2 days) → F5.5 (1 day) = **5-7 days total**

**Non-critical**:
- F5.2 (2-3 days) - runs in parallel with F5.1
- F5.4 (2-3 days) - runs in parallel with F5.1

---

## 🎯 Success Criteria Per Feature

### F5.1: Conflict Detection
- ✅ Detects 90%+ of actual contradictions
- ✅ Classifies conflict type (quantitative/qualitative/semantic)
- ✅ Scores severity correctly (0-1 range)
- ✅ <100ms per 3-document batch
- ✅ 40+ test cases pass
- ✅ Handles edge cases (overlapping ranges, different framing)

### F5.2: Credibility Scoring
- ✅ Scores documents 0-1 meaningfully
- ✅ Expert sources > personal > unknown
- ✅ Recent > old (same authority)
- ✅ Verified > unverified
- ✅ <50ms per document
- ✅ 35+ test cases pass
- ✅ Explanation is human-readable

### F5.4: Hallucination Prevention
- ✅ All 5 rules implemented
- ✅ 95%+ rule effectiveness
- ✅ Rules are applied in order
- ✅ Rejection reasons are clear
- ✅ <20ms for validation
- ✅ 50+ test cases pass

### F5.3: Synthesis
- ✅ Never synthesizes contradictions as fact
- ✅ Presents disagreements as alternatives
- ✅ Disclaimers added when conflicts
- ✅ High-credibility sources preferred
- ✅ Attribution is correct
- ✅ 45+ test cases pass

### F5.5: Integration
- ✅ E4 tests still pass (48/48)
- ✅ No data loss in pipeline
- ✅ <500ms added latency total
- ✅ 20+ end-to-end integration tests pass
- ✅ Deployment checklist complete
- ✅ Production data validated

---

## 📊 Metrics & Quality Gates

### Code Quality (All Features)
```
✓ Type hints: 100% coverage
✓ Docstrings: All public functions
✓ Linting: 0 PEP 8 violations
✓ Logging: DEBUG/INFO structured logs
✓ Error handling: Comprehensive
```

### Test Coverage (All Features)
```
✓ Unit tests: 170+ (40+35+50+45)
✓ Integration tests: 20+
✓ Edge case coverage: Comprehensive
✓ Pass rate: 100%
✓ Coverage %: >95% per feature
```

### Performance
```
F5.1: Conflict detection      <100ms per batch (3 docs)
F5.2: Credibility scoring      <50ms per doc
F5.3: Synthesis engine        <150ms
F5.4: Hallucination validation <20ms
───────────────────────────────────────
Total added latency:          <500ms (target)
```

### Documentation
```
✓ API reference per feature
✓ Algorithm explanation (markdown)
✓ Integration points defined
✓ Test documentation
✓ Deployment checklist
✓ Migration guide for E4 users
```

---

## 🚀 Wave 1 Readiness (Start Now!)

### F5.1, F5.2, F5.4 Status: 🟢 READY

**Why these can start immediately**:
- No dependencies on each other
- Clear, isolated interfaces
- Test data available (career docs)
- Success criteria well-defined
- Algorithms documented

**What each agent needs**:
- **F5.1 Agent**:
  - Input: Retrieved documents (3+)
  - Output: ConflictResult dataclass
  - Tests: 40 test cases (exact match, test files exist)
  - Deliverable: conflict_detector.py module

- **F5.2 Agent**:
  - Input: Document metadata
  - Output: CredibilityScore dataclass
  - Tests: 35 test cases
  - Deliverable: credibility_scorer.py module

- **F5.4 Agent**:
  - Input: Answer, supporting documents, context
  - Output: ValidationResult dataclass
  - Tests: 50 test cases
  - Deliverable: hallucination_prevention.py module

---

## 🔧 Agent Handoff Details

### For Each Wave 1 Agent

**You will receive**:
1. Beads issue with full task breakdown
2. File reservations (no conflicts)
3. MCP agent mail contact info
4. Integration points (how your output feeds to F5.3/F5.5)
5. Test dataset (career knowledge base docs)

**You will deliver**:
1. Production module (type hints, docstrings, logging)
2. Test suite (100% pass rate)
3. Documentation (API, algorithm, examples)
4. Git commit with clear message
5. Completion report

**You will coordinate**:
- Report ready status when complete
- Share output schema with next wave
- Verify integration points
- Participate in end-to-end tests

---

## ⚠️ Risk Mitigation

### High Risk: Semantic Similarity Performance
**Risk**: ConflictDetector slow on large document sets
**Mitigation**:
- Batch operations from start
- Cache similarity computations
- Benchmark at <100ms target
- Start with exact keyword matching, add semantic later if needed

### High Risk: Conflict Detection Accuracy
**Risk**: Misses contradictions or has false positives
**Mitigation**:
- 40+ test cases with real career data
- Manual validation on sample conflicts
- Review algorithm with domain expert
- Iterative tuning if needed

### Medium Risk: Integration Complexity
**Risk**: F5.5 struggles to wire components
**Mitigation**:
- Clear interfaces per F5.1-F5.4
- Isolated, independent modules
- E4 regression tests (48 must still pass)
- Integration tests written alongside

### Medium Risk: Hallucination Rules Too Strict
**Risk**: Rules reject valid answers
**Mitigation**:
- Start permissive (fewer rules)
- Add rules incrementally
- Validate with real career Q&A
- User feedback loop

---

## 📋 Beads Issue IDs

| Feature | ID | Status | Priority | Blocked By |
|---------|----|---------|-----------|----|
| E5 (Epic) | issues-666 | open | P0 | - |
| F5.1 | issues-eky | open | P0 | - |
| F5.2 | issues-i99 | open | P0 | - |
| F5.4 | issues-xpd | open | P0 | - |
| F5.3 | issues-way | open | P1 | F5.1, F5.2 |
| F5.5 | issues-uqn | open | P1 | F5.1, F5.2, F5.3, F5.4 |

**View in beads**:
```bash
bd ready                    # See F5.1, F5.2, F5.4
bd blocked                  # See F5.3, F5.5 waiting
bd show issues-666          # Full E5 structure
```

---

## 🎯 Next Immediate Steps

1. ✅ **E5 planned in beads** (just completed)
2. ⏭️ **Spawn Wave 1 agents** (3 agents for F5.1, F5.2, F5.4)
3. ⏭️ **Agents claim issues** (`bd update <id> --status=in_progress`)
4. ⏭️ **Build & test independently**
5. ⏭️ **Complete Wave 1** (~2-3 days)
6. ⏭️ **Spawn Wave 2 agents** (F5.3, F5.5)
7. ⏭️ **Integration & testing** (~2 days)
8. ⏭️ **Merge to main**
9. ⏭️ **Deploy to production** ✅

---

## 📞 Coordination

**Wave 1 Agents** (F5.1, F5.2, F5.4):
- Work independently (no coordination needed)
- Report status via agent mail
- Share output schemas when complete
- Prepare for Wave 2 integration

**Wave 2 Agents** (F5.3, F5.5):
- Wait for Wave 1 completion
- Receive output schemas
- Verify integration points
- Complete end-to-end testing

**All Agents**:
- File reservations prevent conflicts
- MCP agent mail auto-syncs progress
- Messages persist to git
- Contact approvals auto-approved

---

## 🏁 Success

**When all 5 features complete**:
- ✅ 170+ tests passing
- ✅ <500ms added latency
- ✅ Hallucination detection working
- ✅ Conflict handling robust
- ✅ E4 tests still pass
- ✅ Production ready
- ✅ F4 & F6 can start

**Timeline**: 5-7 days from start to production

---

**Status**: 🟢 **READY TO EXECUTE**

All planning complete. Ready to spawn agents.

---

**Owner**: TurquoisePond (Coordinator)
**Created**: 2026-03-08
**Last Updated**: 2026-03-08
