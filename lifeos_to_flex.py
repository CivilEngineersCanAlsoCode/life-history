#!/usr/bin/env python3
"""
lifeos-to-flex.py — Query lifeos_vectors → LinkedIn post ideas
==============================================================
Queries LifeOS for career achievements/stories and suggests
LinkedIn post angles for the Flex module.

Usage:
  python3 lifeos_to_flex.py                        # random top story
  python3 lifeos_to_flex.py "leadership lessons"   # topic-based
  python3 lifeos_to_flex.py --domain achievement   # filter by domain
  python3 lifeos_to_flex.py --company Sprinklr     # filter by company
"""

import argparse
import json
import random
import subprocess
import sys
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

MONGO_URI = "mongodb://localhost:27017/?directConnection=true"
BGE_MODEL = "BAAI/bge-base-en-v1.5"
BGE_PREFIX = "Represent this sentence: "

FLEX_PROMPT = """You are a LinkedIn content strategist for Satvik Jain, an IIT Delhi graduate and Senior Product Manager building LinkRight.

Based on these career stories/facts from his personal knowledge base, suggest 3 LinkedIn post angles.

For each angle provide:
1. Hook (first line that stops the scroll)
2. Core message (what's the lesson/insight)
3. Post type (story | insight | achievement | lesson | thread)
4. Best format (single post | carousel | thread)

Career facts:
{facts}

Rules:
- Posts must be authentic — based ONLY on the provided facts
- Satvik's audience: PMs, founders, job seekers, IIT/top college grads
- Tone: direct, honest, slightly vulnerable — NOT corporate
- Each angle must be genuinely different

Output JSON:
[
  {{
    "hook": "...",
    "core_message": "...",
    "type": "...",
    "format": "...",
    "source_question": "..."
  }}
]"""

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(BGE_MODEL)
    return _model

def search(query: str, top_k: int = 8, domain: str = None, company: str = None) -> list:
    vec = get_model().encode(BGE_PREFIX + query, normalize_embeddings=True).tolist()
    pipeline = [
        {"$vectorSearch": {
            "index": "vector_index",
            "queryVector": vec,
            "path": "embedding",
            "numCandidates": top_k * 4,
            "limit": top_k * 2
        }},
        {"$addFields": {"score": {"$meta": "vectorSearchScore"}}},
    ]
    match = {}
    if domain:
        match["domain"] = domain
    if company:
        match["company"] = {"$regex": company, "$options": "i"}
    if match:
        pipeline.append({"$match": match})
    pipeline.append({"$limit": top_k})
    pipeline.append({"$project": {"embedding": 0}})

    client = MongoClient(MONGO_URI)
    results = list(client["linkright"]["lifeos_vectors"].aggregate(pipeline))
    client.close()
    return results

def random_story(domain: str = None, company: str = None) -> list:
    """Pick a random story slug and return all its Q&As."""
    client = MongoClient(MONGO_URI)
    coll = client["linkright"]["lifeos_vectors"]
    match = {}
    if domain:
        match["domain"] = domain
    if company:
        match["company"] = {"$regex": company, "$options": "i"}
    slugs = coll.distinct("story_slug", match)
    if not slugs:
        return []
    slug = random.choice(slugs)
    docs = list(coll.find({"story_slug": slug}, {"embedding": 0}))
    client.close()
    return docs

def generate_post_ideas(facts: list) -> list:
    facts_text = "\n".join([
        f"- Q: {f['question']}\n  A: {f['answer']}"
        for f in facts[:6]
    ])
    prompt = FLEX_PROMPT.format(facts=facts_text)
    result = subprocess.run(
        ["claude", "--print"], input=prompt,
        capture_output=True, text=True, timeout=90
    )
    if result.returncode != 0:
        raise RuntimeError(f"Claude error: {result.stderr[:200]}")
    raw = result.stdout.strip()
    start, end = raw.find("["), raw.rfind("]") + 1
    if start == -1:
        return []
    return json.loads(raw[start:end])

def main():
    parser = argparse.ArgumentParser(description="LifeOS → Flex LinkedIn post ideas")
    parser.add_argument("topic", nargs="?", default=None, help="Topic to search (optional)")
    parser.add_argument("--domain", type=str, default=None)
    parser.add_argument("--company", type=str, default=None)
    parser.add_argument("--top", type=int, default=6)
    args = parser.parse_args()

    print("\n🧠 LifeOS → Flex LinkedIn Ideas\n")

    get_model()

    if args.topic:
        print(f"🔍 Topic: {args.topic}")
        facts = search(args.topic, top_k=args.top, domain=args.domain, company=args.company)
    else:
        print("🎲 Random story mode")
        facts = random_story(domain=args.domain, company=args.company)

    if not facts:
        print("❌ No facts found")
        sys.exit(1)

    print(f"📊 Using {len(facts)} facts from lifeos_vectors\n")
    for f in facts[:3]:
        print(f"  • {f['question'][:70]}")
    print(f"  ... +{max(0, len(facts)-3)} more\n")

    print("⚡ Generating LinkedIn post ideas...")
    ideas = generate_post_ideas(facts)

    print(f"\n{'='*60}")
    print(f"💡 {len(ideas)} POST IDEAS")
    print(f"{'='*60}\n")

    for i, idea in enumerate(ideas):
        print(f"[{i+1}] {idea.get('type','?').upper()} | {idea.get('format','?')}")
        print(f"  🪝 Hook: {idea.get('hook','')}")
        print(f"  💬 Message: {idea.get('core_message','')[:120]}")
        print(f"  📌 Source: {idea.get('source_question','')[:60]}")
        print()

if __name__ == "__main__":
    main()
