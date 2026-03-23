#!/usr/bin/env python3
"""
ingest-diary.py — Process daily diary → Q&A pairs → lifeos_vectors
===================================================================
Chronicler runs this at 7:30 PM IST daily.

Usage:
  python3 ingest_diary.py ~/personal-diary/2026-03-23.md
  python3 ingest_diary.py ~/personal-diary/2026-03-23.md --dry-run
"""

import argparse
import json
import re
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path

from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

MONGO_URI = "mongodb://localhost:27017/?directConnection=true"
BGE_MODEL = "BAAI/bge-base-en-v1.5"
BGE_PREFIX = "Represent this sentence: "
RECORDED_DATE = datetime.now().strftime("%Y-%m-%d")

QA_PROMPT = """You are processing Satvik Jain's personal diary entry for his LifeOS knowledge base.

From this diary entry, extract 5-8 Q&A pairs capturing meaningful facts, reflections, decisions, and experiences.

RULES:
1. Simple specific question → single clear answer
2. Always say "Satvik" not "he/I"
3. English only in Q&A (diary may be Hinglish)
4. Focus on: decisions made, people mentioned, work events, personal growth, goals, feelings
5. Skip trivial/routine details (e.g. "Satvik woke up at 7am" unless important)
6. Category A = clear memory (Satvik explicitly stated), R = inferred/uncertain

Diary entry date: {date}
Diary entry:
{text}

Output ONLY valid JSON:
[
  {{"question": "...", "answer": "...", "category": "A", "domain": "career|personal|health|achievement|other"}}
]"""

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(BGE_MODEL)
    return _model

def embed(text: str) -> list:
    return get_model().encode(BGE_PREFIX + text, normalize_embeddings=True).tolist()

def extract_date_from_filename(path: str) -> str:
    match = re.search(r"(\d{4}-\d{2}-\d{2})", path)
    return match.group(1) if match else RECORDED_DATE

def generate_qa(diary_text: str, date: str) -> list:
    prompt = QA_PROMPT.format(date=date, text=diary_text.strip())
    result = subprocess.run(
        ["claude", "--print"], input=prompt,
        capture_output=True, text=True, timeout=90
    )
    if result.returncode != 0:
        raise RuntimeError(f"Claude error: {result.stderr[:200]}")
    raw = result.stdout.strip()
    start, end = raw.find("["), raw.rfind("]") + 1
    if start == -1:
        raise ValueError(f"No JSON in response")
    return json.loads(raw[start:end])

def main():
    parser = argparse.ArgumentParser(description="Ingest diary into lifeos_vectors")
    parser.add_argument("diary_file", type=str, help="Path to diary .md file")
    parser.add_argument("--dry-run", action="store_true", help="Show Q&A without inserting")
    args = parser.parse_args()

    path = Path(args.diary_file).expanduser()
    if not path.exists():
        print(f"❌ File not found: {path}")
        sys.exit(1)

    diary_text = path.read_text()
    event_date = extract_date_from_filename(str(path))
    story_id = uuid.uuid4().hex[:12]

    print(f"\n📔 Diary: {path.name}")
    print(f"   Date: {event_date} | Story ID: {story_id}")
    print(f"   Length: {len(diary_text)} chars\n")

    qa_pairs = generate_qa(diary_text, event_date)
    print(f"✅ {len(qa_pairs)} Q&A pairs generated\n")

    for i, qa in enumerate(qa_pairs):
        print(f"[{i+1}] ({qa.get('domain','?')}/{qa.get('category','A')})")
        print(f"  Q: {qa['question']}")
        print(f"  A: {qa['answer'][:100]}...")
        print()

    if args.dry_run:
        print("[DRY RUN — not inserting]")
        return

    print("Embedding + inserting...")
    get_model()

    docs = []
    for qa in qa_pairs:
        vec = embed(qa["answer"])
        docs.append({
            "_id": f"lifeos-{story_id}-{uuid.uuid4().hex[:8]}",
            "question": qa["question"],
            "answer": qa["answer"],
            "story_id": story_id,
            "story_slug": f"diary-{event_date}",
            "domain": qa.get("domain", "personal"),
            "category": qa.get("category", "A"),
            "event_date": event_date,
            "recorded_date": RECORDED_DATE,
            "company": None,
            "tags": ["diary", "daily-entry"],
            "embedding": vec,
            "embedding_model": BGE_MODEL,
            "embedding_dims": 768,
            "verified": True,
            "source": "diary",
            "version": 1,
            "created_at": datetime.utcnow()
        })

    client = MongoClient(MONGO_URI)
    coll = client["linkright"]["lifeos_vectors"]
    result = coll.insert_many(docs)
    total = coll.count_documents({})
    client.close()

    print(f"\n✅ Inserted {len(result.inserted_ids)} vectors")
    print(f"   Total in lifeos_vectors: {total}")

if __name__ == "__main__":
    main()
