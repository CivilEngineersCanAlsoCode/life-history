# E4 Merge Verification Checklist

**Purpose**: Gate for code review before merging agent work to main/dev
**Status**: Pre-work for CopperBear, CyanFalcon, PearlLantern completion
**Date**: 2026-03-08

---

## Pre-Merge Requirements

### ✅ Code Quality

- [ ] **Linting**: No PEP 8 violations
  ```bash
  python -m flake8 life_brain/intent/ life_brain/conversation/ life_brain/truth_engine/ --max-line-length=120 --extend-ignore=E203,W503
  ```

- [ ] **Type Hints**: Full coverage on new functions
  ```bash
  python -m mypy life_brain/ --ignore-missing-imports --no-error-summary 2>/dev/null | grep -c "error:" | grep "^0$"
  ```

- [ ] **No unused imports**: Clean imports
  ```bash
  python -m pylint --disable=all --enable=unused-import life_brain/**/*.py
  ```

### ✅ Test Coverage

- [ ] **Unit Tests Pass**: All agent-specific tests pass
  ```bash
  python -m pytest tests/test_citations_groundedness.py -v
  python -m pytest tests/test_citations_intent_integration.py -v
  python -m pytest tests/test_intent_monitor.py -v
  python -m pytest tests/test_mode_selector.py -v
  ```

- [ ] **Integration Tests Pass**: E4 full integration tests pass
  ```bash
  python -m pytest tests/test_e4_full_integration.py -v
  ```

- [ ] **Coverage ≥ 95%**: New code has high coverage
  ```bash
  python -m pytest --cov=life_brain --cov-report=term-missing tests/ | grep TOTAL | awk '{print $NF}'
  ```

- [ ] **No flaky tests**: Run test suite 3x, all pass consistently
  ```bash
  for i in {1..3}; do python -m pytest tests/ -q || exit 1; done
  ```

### ✅ Documentation

- [ ] **Module docstrings**: All classes/functions documented
  - Check: `grep -r "^def " life_brain/ | grep -v "def __" | wc -l` vs `grep -r "\"\"\"" life_brain/ | wc -l`

- [ ] **Type annotations**: All parameters and returns annotated
  ```bash
  grep -r "def " life_brain/ | grep -v ": " | grep -v "__" | head -5
  # Should return 0 matches for uncorrected code
  ```

- [ ] **Example usage**: Each module has usage examples in docstrings or README

- [ ] **Changelog updated**: CHANGELOG.md or release notes mention feature

---

## Functionality Verification

### ✅ CopperBear (Intent Detection)

**Deliverables**:
- `detect_intent()` - Detects user intent with confidence score
- `mode_gate_ui()` - Shows mode selection buttons
- Continuous detection within small talk
- Keyword matching to 40+ use cases

**Verification**:
- [ ] Intent detection works with 40+ use case keywords
- [ ] Confidence scores range 0-1
- [ ] Mode selection UI displays correctly
- [ ] Can detect intent shifts (small_talk → guided)
- [ ] Integration test passes with real intents
- [ ] Fallback to "general" mode for unknown intents

**Test Commands**:
```bash
pytest tests/test_intent_monitor.py::TestIntentMonitor -v
pytest tests/test_e4_full_integration.py::TestE4FullIntegration::test_career_question_full_flow -v
```

### ✅ CyanFalcon (Citations & Groundedness)

**Deliverables**:
- `select_top_documents()` - Returns top 3 by relevance
- `format_attribution()` - Formats citations with source + confidence
- Boundary condition testing at 0.85, 0.70, 0.50

**Verification**:
- [ ] select_top_documents() returns exactly 3 docs (or fewer if fewer available)
- [ ] Documents sorted by relevance score (descending)
- [ ] format_attribution() creates proper citation format: `(Source: doc (XX%), confidence: YY%)`
- [ ] No citations added for scores < 0.50
- [ ] Citations added for scores ≥ 0.50
- [ ] Boundary tests pass at 0.49, 0.50, 0.70, 0.71, 0.85, 0.86

**Test Commands**:
```bash
pytest tests/test_citations_groundedness.py::TestBoundaryConditions -v
pytest tests/test_citations_groundedness.py::TestSelectTopDocuments -v
pytest tests/test_citations_groundedness.py::TestFormatAttribution -v
pytest tests/test_e4_full_integration.py::TestThresholdBoundaries -v
```

### ✅ PearlLantern (Monitoring & Mode Selection)

**Deliverables**:
- `intent_monitor.py` - Detects intent shifts
- `mode_selector.py` - Displays mode options + handles selection
- Session continuity tracking

**Verification**:
- [ ] Intent shift detection works (small_talk ↔ guided)
- [ ] Mode selector renders in 4 styles (MENU, BUTTONS, INLINE, MODAL)
- [ ] Bilingual support (English + Hinglish)
- [ ] Input handling: A/B, full text, Hinglish variations
- [ ] Session analytics tracked correctly
- [ ] No duplicate prompts for same mode

**Test Commands**:
```bash
pytest tests/test_intent_monitor.py -v
pytest tests/test_mode_selector.py -v
pytest tests/test_integration_intent_and_mode.py -v
```

---

## Architecture Verification

### ✅ Data Flow Integrity

- [ ] **Intent → Citations**: Intent output schema matches citation input schema
  - Intent confidence flows to groundedness calculator
  - Use case ID used for document filtering

- [ ] **Citations → Mode Selection**: Citation output feeds into mode display
  - High confidence answers show citations prominently
  - Low confidence answers show uncertain tone

- [ ] **Mode Monitoring**: Monitor detects shifts based on intent confidence
  - Confidence delta (prev vs current) computed correctly
  - Prompts only on significant shifts (e.g., delta > 0.3)

### ✅ Integration Points

- [ ] **No circular dependencies**: Modules don't import each other in circles
  ```bash
  python -c "import networkx; print('OK')" 2>&1 | grep -q ImportError || echo "Dependencies OK"
  ```

- [ ] **Shared interfaces**: Mock signatures match real signatures
  - Test mocks should match actual function signatures
  - Return types consistent across modules

- [ ] **Error propagation**: Errors bubble up cleanly
  - No silent failures in module composition
  - Logging enabled for debugging

---

## Performance Verification

### ✅ Speed Benchmarks

- [ ] **Intent detection < 100ms**: Fast keyword matching
- [ ] **Document selection < 50ms**: Quick top-3 sort
- [ ] **Groundedness calc < 150ms**: Multi-dimensional scoring
- [ ] **Citation formatting < 30ms**: String assembly
- [ ] **Mode selection < 20ms**: Enum rendering

**Benchmark Command**:
```bash
python -m pytest tests/ --durations=10 -v | tail -15
```

### ✅ Memory Usage

- [ ] **No memory leaks**: Session objects cleaned up properly
- [ ] **Reasonable state size**: Monitor/selector instances < 1MB each
- [ ] **Batch operations work**: Can handle 100+ documents without issue

---

## Git & Commit Quality

### ✅ Git History

- [ ] **Clean commit history**: Logical, atomic commits
  ```bash
  git log --oneline origin/dev..HEAD | head -5
  ```

- [ ] **Good commit messages**: Descriptive, follow convention
  - Format: `TYPE: Brief description`
  - Include issue numbers: `Closes #123`

- [ ] **No merge commits**: Fast-forward or rebase preferred
  ```bash
  git log --oneline --graph --all | head -10 | grep -i merge || echo "No merges (good)"
  ```

- [ ] **Signed commits** (optional but recommended):
  ```bash
  git log --show-signature HEAD | head -5
  ```

### ✅ File Organization

- [ ] **Files in correct locations**:
  - Intent: `life_brain/intent/detector.py`, `mode_gate.py`
  - Citations: `life_brain/truth_engine/groundedness.py`
  - Monitoring: `life_brain/conversation/intent_monitor.py`, `mode_selector.py`

- [ ] **Tests co-located**:
  - All tests in `tests/` directory
  - Naming: `test_*.py`

- [ ] **No debug files**: No `*.pyc`, `__pycache__`, `.pytest_cache` in commits
  ```bash
  git status | grep -E "\.pyc|__pycache__|\.pytest_cache" && echo "FAIL: Debug files found" || echo "OK"
  ```

---

## Integration Testing (Final Gate)

### ✅ End-to-End Scenarios

Run the complete E4 integration suite:

```bash
python -m pytest tests/test_e4_full_integration.py -v --tb=short
```

**Must Pass**:
1. `test_career_question_full_flow` - Typical use case
2. `test_low_confidence_query_no_citations` - Graceful degradation
3. `test_intent_shift_from_small_talk_to_guided` - Mode switching
4. `test_multi_turn_conversation_same_mode` - Session continuity
5. `test_boundary_condition_exactly_0_50` - Critical threshold
6. `test_full_pipeline_with_mode_options` - All modules together
7. `test_graceful_handling_no_documents` - Error handling
8. All `TestThresholdBoundaries` tests pass

### ✅ Cross-Agent Compatibility

- [ ] CopperBear output compatible with CyanFalcon input
- [ ] CyanFalcon output compatible with PearlLantern input
- [ ] No data transformation issues
- [ ] Version compatibility (if applicable)

---

## Code Review Sign-Off

### ✅ Reviewer Checklist

- [ ] **Functionality**: Does it do what it claims?
- [ ] **Code quality**: Is it clean, readable, maintainable?
- [ ] **Tests**: Are they comprehensive and passing?
- [ ] **Documentation**: Is it clear and complete?
- [ ] **Performance**: Is it reasonably fast?
- [ ] **Security**: Are there no obvious vulnerabilities?
- [ ] **Architecture**: Does it fit the system design?

---

## Pre-Merge Automated Checks

```bash
#!/bin/bash
# Run this before merging
set -e

echo "=== Running Pre-Merge Checks ==="

echo "1. Linting..."
python -m flake8 life_brain/ --max-line-length=120 --extend-ignore=E203,W503

echo "2. Type Checking..."
python -m mypy life_brain/ --ignore-missing-imports 2>&1 | grep -c "error" | grep "^0$" || true

echo "3. Unit Tests..."
python -m pytest tests/test_citations_groundedness.py tests/test_intent_monitor.py tests/test_mode_selector.py -v

echo "4. Integration Tests..."
python -m pytest tests/test_e4_full_integration.py -v

echo "5. Coverage..."
python -m pytest --cov=life_brain --cov-report=term-missing tests/ | tail -5

echo "=== All checks passed! Ready to merge ==="
```

---

## Post-Merge

- [ ] Verify PR merged to dev branch
- [ ] Close related beads issues with commit hash
- [ ] Deploy to staging (if applicable)
- [ ] Monitor logs for errors
- [ ] Document any breaking changes

---

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Author (CopperBear) | Agent | - | - |
| Author (CyanFalcon) | Agent | - | - |
| Author (PearlLantern) | Agent | - | - |
| Reviewer | TurquoisePond | - | - |
| QA Lead | - | - | - |

---

**Last Updated**: 2026-03-08
**Version**: 1.0
**Status**: Draft (awaiting agent completion)
