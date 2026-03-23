#!/usr/bin/env python3
"""
query-lifeos.py — Semantic search over lifeos_vectors
======================================================
Usage:
  python3 query_lifeos.py "What did Satvik achieve at Sprinklr?"
  python3 query_lifeos.py "Satvik's mentors" --top 5
  python3 query_lifeos.py "CRR Modernization" --domain career --company "American Express"
"""

import argparse
import sys
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

MONGO_URI = "mongodb://localhost:27017/?directConnection=true"
BGE_MODEL = "BAAI/bge-base-en-v1.5"
BGE_PREFIX = "Represent this sentence: "

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(BGE_MODEL)
    return _model

def search(query: str, top_k: int = 5, domain: str = None, company: str = None) -> list:
    vec = get_model().encode(BGE_PREFIX + query, normalize_embeddings=True).tolist()

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": vec,
                "path": "embedding",
                "numCandidates": top_k * 4,
                "limit": top_k * 2
            }
        },
        {"$addFields": {"score": {"$meta": "vectorSearchScore"}}},
    ]

    # Post-filter by metadata if provided
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

def main():
    parser = argparse.ArgumentParser(description="Query lifeos_vectors semantic search")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--top", type=int, default=5, help="Number of results (default: 5)")
    parser.add_argument("--domain", type=str, default=None, help="Filter: career/achievement/personal/mentorship/education")
    parser.add_argument("--company", type=str, default=None, help="Filter: Sprinklr/American Express/etc")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    results = search(args.query, top_k=args.top, domain=args.domain, company=args.company)

    if args.json:
        import json
        print(json.dumps(results, indent=2, default=str))
        return

    print(f"\n🔍 Query: {args.query}")
    print(f"📊 Results: {len(results)}\n")
    print("="*70)

    for i, r in enumerate(results):
        score = r.get("score", 0)
        print(f"\n[{i+1}] Score: {score:.4f} | {r.get('domain','?')} | {r.get('company','?')} | {r.get('event_date','?')}")
        print(f"  Q: {r['question']}")
        print(f"  A: {r['answer']}")
        print(f"  Tags: {', '.join(r.get('tags', []))}")

if __name__ == "__main__":
    main()
