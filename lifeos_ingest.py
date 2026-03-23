#!/usr/bin/env python3
"""
LifeOS Ingest Pipeline
======================
/ingest command — takes raw career story text and stores it in lifeos_vectors.

Flow:
  raw text → Claude generates Q&A pairs → verify → BGE embed → MongoDB insert

Usage:
  python3 lifeos_ingest.py --text "your story here" --domain career --category A --event-date 2022-04-dd
  python3 lifeos_ingest.py --file story.txt --domain career --category A --event-date 2022-04-dd
"""

import argparse
import json
import subprocess
import sys
import uuid
from datetime import datetime
from typing import Optional

from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

# ── CONFIG ──────────────────────────────────────────────────────────────────
MONGO_URI = "mongodb://localhost:27017/?directConnection=true"
DB_NAME = "linkright"
COLLECTION = "lifeos_vectors"
BGE_MODEL = "BAAI/bge-base-en-v1.5"
RECORDED_DATE = datetime.now().strftime("%Y-%m-%d")

VALID_DOMAINS = ["career", "education", "personal", "achievement", "mentorship", "other"]
VALID_CATEGORIES = ["A", "R"]

# ── EMBEDDING ────────────────────────────────────────────────────────────────
_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading BGE model...", flush=True)
        _model = SentenceTransformer(BGE_MODEL)
    return _model

def embed(text: str) -> list:
    """Embed text using BGE-base-en-v1.5 → 768-dim vector."""
    model = get_model()
    # BGE requires instruction prefix for queries
    prefixed = f"Represent this sentence: {text}"
    vec = model.encode(prefixed, normalize_embeddings=True)
    return vec.tolist()

# ── Q&A GENERATION ───────────────────────────────────────────────────────────
QA_PROMPT_TEMPLATE = """You are helping build a personal career knowledge base for Satvik Jain, an IIT Delhi graduate and Senior Product Manager.

Given the following career story or experience, generate 5-8 Q&A pairs that capture the key knowledge, context, and learnings from this story. These will be used for semantic search later.

Rules:
- Questions should be specific and searchable
- Answers should be complete and self-contained (no pronoun ambiguity — use "Satvik" not "he/I")
- Cover: what happened, what was the impact, what skills were used, what was learned
- Write in English only (even if story has Hindi)
- Each Q&A should be independently useful

Story:
{story}

Domain: {domain}
Event date: {event_date}

Output ONLY valid JSON array, no markdown, no explanation:
[
  {{"question": "...", "answer": "..."}},
  ...
]"""

def generate_qa_pairs(story: str, domain: str, event_date: str) -> list:
    """Use Claude CLI to generate Q&A pairs from raw story text."""
    prompt = QA_PROMPT_TEMPLATE.format(
        story=story.strip(),
        domain=domain,
        event_date=event_date
    )

    print("\nGenerating Q&A pairs via Claude...", flush=True)
    result = subprocess.run(
        ["claude", "--print"],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode != 0:
        raise RuntimeError(f"Claude CLI error: {result.stderr}")

    raw = result.stdout.strip()

    # Extract JSON from response
    start = raw.find("[")
    end = raw.rfind("]") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON array found in Claude response:\n{raw}")

    qa_pairs = json.loads(raw[start:end])
    return qa_pairs

# ── MONGODB ──────────────────────────────────────────────────────────────────
def get_collection():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME][COLLECTION]

def build_document(qa: dict, story: str, domain: str, category: str,
                   event_date: str, company: Optional[str], tags: list,
                   story_id: str) -> dict:
    """Build a MongoDB document from a Q&A pair."""
    embedding = embed(qa["answer"])  # embed answer (the knowledge)

    return {
        "_id": f"lifeos-{story_id}-{uuid.uuid4().hex[:8]}",
        "question": qa["question"],
        "answer": qa["answer"],
        "source_text": story,
        "story_id": story_id,           # all Q&As from same story share this
        "domain": domain,               # career / education / personal / achievement
        "category": category,           # A (clear memory) / R (recall needed)
        "event_date": event_date,       # when it happened (YYYY-MM-DD with dd/mm placeholders)
        "recorded_date": RECORDED_DATE, # when Satvik told us (today)
        "company": company,             # optional: Amex / Sprinklr / IIT Delhi / etc.
        "tags": tags,                   # optional: ["leadership", "AML", "team-building"]
        "embedding": embedding,
        "embedding_model": BGE_MODEL,
        "embedding_dims": 768,
        "version": 1,
        "created_at": datetime.utcnow()
    }

def insert_documents(docs: list) -> int:
    """Insert documents into MongoDB."""
    coll = get_collection()
    result = coll.insert_many(docs)
    return len(result.inserted_ids)

# ── VERIFY LOOP ──────────────────────────────────────────────────────────────
def verify_qa_pairs(qa_pairs: list) -> list:
    """Show Q&A pairs to user, let them edit/remove before inserting."""
    print("\n" + "="*60)
    print("Generated Q&A pairs — review before inserting:")
    print("="*60)

    for i, qa in enumerate(qa_pairs):
        print(f"\n[{i+1}] Q: {qa['question']}")
        print(f"     A: {qa['answer']}")

    print("\n" + "-"*60)
    print("Options: 'all' to accept all | '1,3,5' to keep specific | 'edit' to modify")
    choice = input("Your choice: ").strip().lower()

    if choice == "all":
        return qa_pairs
    elif choice == "edit":
        print("Edit mode not implemented yet — accepting all.")
        return qa_pairs
    else:
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(",")]
            return [qa_pairs[i] for i in indices if 0 <= i < len(qa_pairs)]
        except:
            print("Invalid input — accepting all.")
            return qa_pairs

# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="LifeOS Ingest Pipeline")
    parser.add_argument("--text", type=str, help="Story text directly")
    parser.add_argument("--file", type=str, help="Path to .txt file with story")
    parser.add_argument("--domain", type=str, required=True,
                        choices=VALID_DOMAINS, help="Domain of the story")
    parser.add_argument("--category", type=str, required=True,
                        choices=VALID_CATEGORIES, help="A=clear memory, R=recall needed")
    parser.add_argument("--event-date", type=str, required=True,
                        help="When it happened (YYYY-MM-DD, use dd/mm for unknown)")
    parser.add_argument("--company", type=str, default=None,
                        help="Company/org (optional): Amex, Sprinklr, IIT Delhi, etc.")
    parser.add_argument("--tags", type=str, default="",
                        help="Comma-separated tags (optional): leadership,AML,teamwork")
    parser.add_argument("--no-verify", action="store_true",
                        help="Skip verification, insert directly")

    args = parser.parse_args()

    # Get story text
    if args.text:
        story = args.text
    elif args.file:
        with open(args.file, "r") as f:
            story = f.read()
    else:
        print("Error: provide --text or --file")
        sys.exit(1)

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    story_id = uuid.uuid4().hex[:12]

    print(f"\n📥 Ingesting story...")
    print(f"   Domain: {args.domain} | Category: {args.category}")
    print(f"   Event date: {args.event_date} | Recorded: {RECORDED_DATE}")
    print(f"   Story ID: {story_id}")

    # Generate Q&A pairs
    qa_pairs = generate_qa_pairs(story, args.domain, args.event_date)
    print(f"   Generated {len(qa_pairs)} Q&A pairs")

    # Verify (unless skipped)
    if not args.no_verify:
        qa_pairs = verify_qa_pairs(qa_pairs)

    # Build + embed + insert
    print(f"\nEmbedding {len(qa_pairs)} Q&A pairs with BGE...")
    docs = []
    for i, qa in enumerate(qa_pairs):
        print(f"  Embedding {i+1}/{len(qa_pairs)}...", end="\r", flush=True)
        doc = build_document(
            qa=qa,
            story=story,
            domain=args.domain,
            category=args.category,
            event_date=args.event_date,
            company=args.company,
            tags=tags,
            story_id=story_id
        )
        docs.append(doc)

    count = insert_documents(docs)
    print(f"\n✅ Inserted {count} documents into lifeos_vectors")
    print(f"   Story ID: {story_id} (use this to find all Q&As from this story)")
    print(f"   Total docs in collection: {get_collection().count_documents({})}")


if __name__ == "__main__":
    main()
