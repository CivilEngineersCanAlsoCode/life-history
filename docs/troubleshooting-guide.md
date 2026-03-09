# Troubleshooting Guide — Life Brain

Common issues aur unke fixes. Pehle yahan dekho — 90% problems yahi list mein hain.

---

## 1. ChromaDB Issues

### "Collection not found" / "No collection configured"

**Symptom:** Search ya ingestion karte time error: `Collection 'life_brain' not found`

**Fix:**
```python
from life_brain.db.chromadb_init import initialize_collection

# Collection pehli baar initialize karo
collection = initialize_collection(
    db_path="./career_context.db",
    collection_name="life_brain",
    reset=False,
)
```

**Root cause:** `career_context.db` file missing hai ya corrupt ho gayi.

---

### "Connection error" during ingestion

**Symptom:** `ConnectionError: Failed to connect to ChromaDB`

**Fix:**
1. Check karo ki `career_context.db` file exist karti hai: `ls -la career_context.db`
2. File permissions check karo: `chmod 644 career_context.db`
3. Agar file corrupt lag rahi hai, backup se restore karo (see Section 6)

---

### Ingestion very slow (> 10 sec per document)

**Symptom:** `ingest_with_retry()` har document pe 10+ seconds le raha hai

**Root cause:** Embedding model pehli baar download ho rahi hai (~80MB)

**Fix:** Pehli baar slow hoga — normal hai. Baad mein fast ho jaayega (cached model).

```bash
# Confirm model download completed
ls ~/.cache/huggingface/hub/
```

---

## 2. Search Issues

### Search returns 0 results

**Symptom:** `collection.query()` returns empty list

**Diagnosis steps:**

```python
# Step 1: Check collection has documents
result = collection.get(limit=5)
print(f"Total docs in collection: {len(result['ids'])}")

# Step 2: Check if query text is too specific
# Try a shorter, more generic query first

# Step 3: Check metadata filters — too strict = 0 results
candidates, p1, p2 = two_pass_conflict_search(
    collection=collection,
    query_text="career",       # Very generic
    query_embedding=None,
    atom_type="story",
    metadata_filters={},       # No filters — start broad
)
print(f"Without filters: {p1} results")
```

---

### Wrong documents being returned

**Symptom:** Search query "salary metric at Sprinklr" return karta hai unrelated documents

**Root cause:** Missing or incorrect metadata — atom_type, company, category fields

**Fix:** Document re-ingest karo with correct metadata:
```python
# Check existing metadata
doc = collection.get(ids=["your_doc_id"], include=["metadatas"])
print(doc["metadatas"])

# Re-ingest with corrected metadata using upsert (same doc_id)
collection.upsert(
    ids=["your_doc_id"],
    documents=["original text"],
    metadatas=[{"atom_type": "metric", "company": "Sprinklr", ...}],
)
```

---

### Two-Pass search not using structural pass

**Symptom:** `pass2_count` always 0 even for metric queries

**Common causes:**
1. `atom_type` is not `"metric"` or `"fact"` — structural pass only runs for these
2. `metadata_filters` is empty `{}` — needs at least one filter key
3. Metadata filter keys must be `company`, `category`, or `doc_type` — others are ignored

```python
# Correct usage for structural pass
candidates, p1, p2 = two_pass_conflict_search(
    collection=collection,
    query_text="revenue",
    query_embedding=None,
    atom_type="metric",                  # ✓ triggers structural pass
    metadata_filters={"company": "Sprinklr"},  # ✓ at least one filter
)
```

---

## 3. Ingestion Issues

### "Validation failed: missing required fields"

**Symptom:** `document_validator.py` rejects document

**Fix:** Ensure all required metadata fields are present:

```python
# Minimum required metadata
metadata = {
    "atom_type": "fact",       # Required
    "domain": "career",        # Required
    "date": "2024-01-15",     # Required (YYYY-MM-DD)
    "company": "Amex",        # Required for career atoms
}
```

See `docs/configuration-guide.md` section 4 for full required fields list.

---

### Document ends up in deadletter queue

**Symptom:** `result["status"] == "deadletter"` after `ingest_with_retry()`

**Meaning:** Document failed 3 retries (max) — transient errors nahi the, validation/conflict issue hai

**Fix:**
```python
from life_brain.db.retry_manager import RetryManager

retry_mgr = RetryManager()
deadletter = retry_mgr.get_deadletter_items()

for item in deadletter:
    print(f"Doc: {item['doc_id']}, Error: {item['error']}")
    # Fix the issue in the original document, then retry manually
```

---

### Privacy field accidentally not set

**Symptom:** Sensitive document ends up in `public` level

**Fix:** Always explicitly set privacy. Default is `private` but double-check:

```python
metadata = {
    "privacy": "private",    # Always set explicitly
    ...
}
```

---

## 4. Session Issues

### Session not resuming (starts fresh every time)

**Symptom:** `SessionResumer` says "first time meeting" even after previous sessions

**Fix:** Check session state directory exists and is writable:

```python
import os
session_dir = "./sessions"
os.makedirs(session_dir, exist_ok=True)
print(f"Session dir writable: {os.access(session_dir, os.W_OK)}")
```

---

### "AttributeError: 'states' object" or similar

**Symptom:** `schema.sessions.clear()` type errors

**Fix:** Correct attribute name is `states` not `sessions`:
```python
schema.states.clear()   # ✓ Correct
# schema.sessions.clear()  # ✗ Wrong
```

---

## 5. Expert Panel Issues

### Panel timeout too fast — not all experts respond

**Symptom:** Only 1-2 experts respond before timeout

**Fix:** Increase timeout in `panel_router()`:

```python
session, result = router.panel_router(
    use_case_id="C1",
    question="Your question here",
    expert_names=["Elon", "Reid", "Naval"],
    timeout_seconds=30.0,    # Default might be too short; increase
)
```

---

### ConsensusResolver not detecting disagreement

**Symptom:** `detect_disagreement()` returns `False` when experts clearly disagree

**Root cause:** Responses don't contain the exact keywords the detector looks for

**Lookup keywords:**
- **Action**: quit, leave, start, build, risk, invest, go all-in
- **Caution**: stay, keep, protect, safe, don't risk, never risk, conservative
- **Positive**: yes, absolutely, definitely, always, strong, great, excellent
- **Negative**: no, never, avoid, risky, dangerous, terrible, bad

**Fix:** Disagreement detection is keyword-based — if responses use different phrasing (e.g., "proceed cautiously" vs "take the leap"), it may not trigger. Future improvement: LLM-based stance detection.

---

## 6. Backup & Restore

### Export before any risky operation

```python
from life_brain.db.data_exporter import DataExporter

exporter = DataExporter(collection=collection)
success, error = exporter.export_to_file(f"./backups/backup_{today}.json")
if not success:
    print(f"Backup failed: {error}")
    # Do NOT proceed with risky operation
```

### Restore from backup

```python
import json

exporter = DataExporter(collection=collection)

with open("./backups/backup_2026-03-09.json") as f:
    backup_data = json.load(f)

result = exporter.import_from_dict(backup_data)
print(f"Restored {result.successful}/{result.attempted} documents")

if result.failed > 0:
    print(f"Failed: {result.failed}")
    for err in result.errors[:5]:    # Show first 5 errors
        print(f"  - {err}")
```

---

## 7. Staleness Detection

### is_stale() always returns True

**Symptom:** All documents marked stale even recent ones

**Fix:** Check `date` field format in metadata — must be `YYYY-MM-DD`:

```python
# ✓ Correct
metadata["date"] = "2024-03-09"

# ✗ Wrong (will parse as stale or fail)
metadata["date"] = "March 9, 2024"
metadata["date"] = "09/03/2024"
metadata["date"] = 1709942400  # Unix timestamp
```

---

### is_stale() always returns False

**Symptom:** Old documents not being flagged

**Fix:** Check `domain` field — expiry windows vary by domain:

```python
from life_brain.truth_engine.staleness_detector import EXPIRY_DAYS_BY_DOMAIN
print(EXPIRY_DAYS_BY_DOMAIN)
# finance=365, health=180, career=730, etc.

# Document with missing domain defaults to... check:
detector = StalenessDetector(collection=None)
print(detector.get_expiry_config("career"))   # 730
print(detector.get_expiry_config("unknown"))  # Falls back to default
```

---

## 8. Test Failures

### Running the full test suite

```bash
# Run all tests
python -m pytest life_brain/tests/ -q

# Run specific module tests
python -m pytest life_brain/tests/test_consensus_resolver.py -v

# Run with output (print statements)
python -m pytest life_brain/tests/ -s -q
```

### Common test import errors

**"ImportError: No module named 'life_brain'"**

```bash
# Run from repo root
cd /path/to/Career-context
python -m pytest life_brain/tests/ -q
```

**"ModuleNotFoundError: No module named 'chromadb'"**

```bash
pip install chromadb sentence-transformers
```

---

## 9. Quick Diagnostics Script

Saari cheez ek saath check karne ke liye:

```python
"""Quick health check for Life Brain system."""

def health_check():
    print("=== Life Brain Health Check ===\n")

    # 1. ChromaDB
    try:
        from life_brain.db.chromadb_init import initialize_collection
        col = initialize_collection("./career_context.db", "life_brain")
        count = len(col.get(limit=1)["ids"])
        print(f"✓ ChromaDB: connected, ~{count}+ docs")
    except Exception as e:
        print(f"✗ ChromaDB: {e}")

    # 2. Session
    try:
        from life_brain.conversation.session_state import SessionStateSchema
        schema = SessionStateSchema()
        print("✓ Session state: OK")
    except Exception as e:
        print(f"✗ Session state: {e}")

    # 3. Experts
    try:
        from life_brain.conversation.experts import ExpertRoster
        roster = ExpertRoster()
        experts = roster.get_all()
        print(f"✓ Expert roster: {len(experts)} experts loaded")
    except Exception as e:
        print(f"✗ Expert roster: {e}")

    # 4. Consensus
    try:
        from life_brain.conversation.consensus_resolver import ConsensusResolver
        resolver = ConsensusResolver()
        result = resolver.detect_disagreement("Build and risk.", "Stay safe.")
        print(f"✓ Consensus resolver: OK (disagreement detected: {result})")
    except Exception as e:
        print(f"✗ Consensus resolver: {e}")

    print("\nHealth check complete.")

health_check()
```

---

## 10. Getting Help

Agar yeh guide mein solution nahi mila:

1. **Test logs dekho**: `python -m pytest life_brain/tests/ -v --tb=long`
2. **Debug logging on karo**: `LOG_LEVEL=DEBUG python your_script.py`
3. **Backup pehle lo** (section 6) before trying fixes
4. **Beads issue banao**: `bd create --title="Bug: <description>" --type=bug --priority=1`
