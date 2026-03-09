# Configuration Guide — Life Brain

Yeh guide batati hai ki system ko kaise configure karein: ChromaDB settings, domain setup,
expert rosters, environment variables, aur atom type schemas.

---

## 1. Environment Variables

System automatically works with defaults. Override karna ho toh `.env` file banao root mein:

```bash
# ChromaDB
CHROMA_DB_PATH=./career_context.db     # Default: ./career_context.db
CHROMA_COLLECTION_NAME=life_brain      # Default: life_brain

# Embedding
EMBEDDING_MODEL=all-MiniLM-L6-v2       # Default: all-MiniLM-L6-v2 (free, local)

# Logging
LOG_LEVEL=INFO                          # DEBUG / INFO / WARNING / ERROR
LOG_FILE=./life_brain.log              # Optional: file output

# Session
SESSION_STATE_DIR=./sessions           # Where session JSONs are saved
MAX_SESSION_AGE_DAYS=30               # Sessions older than this get cleaned up
```

---

## 2. ChromaDB Collection Setup

### Default Configuration

```python
from life_brain.db.chromadb_init import initialize_collection

collection = initialize_collection(
    db_path="./career_context.db",      # Persistent storage path
    collection_name="life_brain",       # Collection name
    reset=False,                        # True = wipe and recreate
)
```

### When to Reset

```python
# CAUTION: Reset deletes ALL data. Use only during initial setup.
collection = initialize_collection(db_path="./test.db", reset=True)
```

---

## 3. Atom Type Schema

Har document ek `atom_type` field zaroori hai. Ye types supported hain:

| Type | Use For | Example |
|------|---------|---------|
| `fact` | Verified facts about your life | "Sprinklr join kiya April 2022 mein" |
| `metric` | Quantitative achievements | "CGB reached 94% CSAT in Q3 2023" |
| `story` | STAR-format experiences | "Walmart Spark Driver Support launch story" |
| `decision` | Major life/career decisions | "American Express accept kiya July 2024" |
| `lesson` | What you learned from something | "Never skip user research, even under deadline" |
| `belief` | Personal values and principles | "Feedback loop wali culture best hoti hai" |
| `memory` | Episodic memories | "First day at Sprinklr office" |
| `goal` | Future aspirations | "PM role at product-led company in 3 years" |

### Required Metadata Fields

```python
{
    "atom_type": "metric",              # REQUIRED
    "domain": "career",                 # REQUIRED: career/finance/health/relationships/
                                        #   personal_growth/memory/creativity
    "company": "Sprinklr",             # For career atoms
    "project": "CGB",                  # For project-specific atoms
    "category": "product_metrics",     # Subcategory for filtering
    "date": "2023-09-15",             # ISO format YYYY-MM-DD
    "confidence": 0.95,                # 0.0–1.0, how certain are you?
    "source": "confluence_export",     # Where this data came from
    "privacy": "private",             # private / team / public
}
```

---

## 4. Domain Configuration

### Available Domains

| Domain | Description | Expiry Window |
|--------|-------------|--------------|
| `career` | Work experience, projects, achievements | 730 days (2 years) |
| `finance` | Money, investments, savings, spending | 365 days (1 year) |
| `health` | Physical and mental wellness | 180 days (6 months) |
| `relationships` | People, friendships, family | 365 days (1 year) |
| `personal_growth` | Learnings, beliefs, values, identity | 1825 days (5 years) |
| `memory` | Episodic memories and stories | 1825 days (5 years) |
| `creativity` | Creative projects, writing, ideas | 730 days (2 years) |

### Custom Expiry Override

```python
from life_brain.truth_engine.staleness_detector import StalenessDetector, EXPIRY_DAYS_BY_DOMAIN

# Check current config
print(EXPIRY_DAYS_BY_DOMAIN)
# {'finance': 365, 'health': 180, 'career': 730, ...}

# Detector uses domain from doc metadata automatically
detector = StalenessDetector(collection=your_collection)
result = detector.check_collection_for_stale()
print(f"Stale docs: {result.stale_count} / {result.total_checked}")
```

---

## 5. Expert Roster Configuration

Default experts load ho jaate hain automatically. Custom expert add karna ho:

```python
from life_brain.conversation.experts import Expert, ExpertRoster

roster = ExpertRoster()

# Available experts (pre-configured)
all_experts = roster.get_all()
for expert in all_experts:
    print(f"{expert.name} — {expert.domain}")

# Get by domain
career_experts = roster.get_by_domain("career")
relationship_experts = roster.get_by_domain("relationships")
```

### Expert Domain Mapping

| Domain | Default Experts |
|--------|----------------|
| Career | Elon Musk, Reid Hoffman, Naval Ravikant |
| Finance | Warren Buffett, Charlie Munger, Ray Dalio |
| Relationships | Esther Perel, Brene Brown |
| Health | Andrew Huberman, Peter Attia |
| Product | Paul Graham, Julie Zhuo, Marty Cagan |

---

## 6. Conversational Mode Configuration

Question delivery mode use case ID se auto-detect hoti hai:

```python
from life_brain.conversation.conversational_framing import ConversationalFramer, QuestionMode

framer = ConversationalFramer()

# Check mode for any use case
print(framer.get_mode("C1"))   # STRUCTURED (career)
print(framer.get_mode("R2"))   # CONVERSATIONAL (relationships)
print(framer.get_mode("P2"))   # HYBRID (goals/habits)

# Render a question
output = framer.render_question(
    use_case_id="C1",
    question_text="Biggest achievement in last 12 months? Numbers ke saath.",
    question_index=2,    # 0-based
    total_questions=8,
)
print(output)
# "Q3 of 8 — Theek hai, ab next — Biggest achievement..."
```

---

## 7. Ingestion Configuration

### Batch Settings

```python
from life_brain.db.ingestion_wrapper import ResilientIngestion

ingestion = ResilientIngestion(
    collection=collection,
    max_retries=3,          # Attempts before deadletter (default: 3)
    initial_delay=1.0,      # First retry wait in seconds (default: 1.0)
    max_delay=60.0,         # Max backoff cap (default: 60.0)
)

result = ingestion.ingest_with_retry(
    doc_id="unique_id_001",
    text="Document content here.",
    metadata={"atom_type": "fact", "domain": "career", ...},
)
print(result["status"])  # "success" / "failed" / "deadletter"
```

### Chunking Settings

```python
from life_brain.db.chunking import SemanticChunker

chunker = SemanticChunker(
    min_tokens=50,      # Minimum tokens per chunk (default: 50)
    max_tokens=500,     # Maximum tokens per chunk (default: 500)
)
chunks = chunker.chunk_document(long_text)
```

---

## 8. Two-Pass Conflict Search

Conflict detection zyada accurate hota hai two-pass search se:

```python
from life_brain.truth_engine.two_pass_conflict_search import two_pass_conflict_search

candidates, pass1_count, pass2_count = two_pass_conflict_search(
    collection=collection,
    query_text="revenue growth Q3 2023",
    query_embedding=None,           # Optional pre-computed embedding
    atom_type="metric",             # METRIC/FACT → Pass 2 runs; others → Pass 1 only
    metadata_filters={
        "company": "Sprinklr",
        "category": "product_metrics",
    },
    semantic_top_k=5,               # Pass 1: top-k by similarity (default: 5)
    structural_limit=100,           # Pass 2: max structural results (default: 100)
)

print(f"Total candidates: {len(candidates)}")
print(f"Semantic: {pass1_count}, Structural: {pass2_count}")
```

---

## 9. Export / Backup Configuration

```python
from life_brain.db.data_exporter import DataExporter

exporter = DataExporter(collection=collection)

# Full backup
result, error = exporter.export_all()
exporter.export_to_file("./backups/life_brain_backup.json")

# Domain-specific export
career_result, _ = exporter.export_by_domain("career")

# Restore from backup
import_result = exporter.import_from_dict(result.to_dict())
print(f"Restored: {import_result.successful}/{import_result.attempted}")
print(f"Success rate: {import_result.success_rate:.1%}")
```

---

## 10. Privacy Levels

| Level | Meaning | Who Sees It |
|-------|---------|-------------|
| `private` | Only you | Never shared with any AI/external system |
| `team` | Work context | Can be used for work-related queries |
| `public` | Safe to share | Can appear in any output |

Default for all ingested documents: `private`. Explicitly set `privacy` in metadata to override.
