#!/usr/bin/env python3
"""
crr_ingest.py — Ingest Amex CRR Modernization stories into lifeos_vectors
"""
import json, subprocess, sys, uuid
from datetime import datetime
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

MONGO_URI = "mongodb://localhost:27017/?directConnection=true"
BGE_MODEL  = "BAAI/bge-base-en-v1.5"
BGE_PREFIX = "Represent this sentence: "
RECORDED_DATE = "2026-03-24"

STORIES = [
  {
    "story_id": "amex-crr-problem",
    "story_slug": "amex-crr-problem",
    "company": "American Express",
    "domain": "career",
    "event_date": "2024-08-dd",
    "tags": ["amex","crr","aml","product-strategy","modernization"],
    "text": """
Satvik joined American Express in August 2024 as Senior Associate PM (APM).
His main product: CRR (Customer Risk Rating) — an Anti-Money Laundering (AML) risk scoring engine.

The product had 4 major problems:
1. Speed — scoring was slow and batch-based
2. UI/UX — interface was outdated and hard to use
3. Configurability — business rules were hardcoded, hard to change
4. Audit/Reporting — poor audit trail for regulatory compliance

The tech stack involved legacy Python/PySpark on Mainframe being migrated to:
- BigQuery (cloud data layer)
- Kotlin (new front-end app)
- Event-based triggers (real-time scoring)

Satvik was given ownership of this 3-year modernization roadmap spanning 7 PIs (PI 24.5 through PI 26.1).
He led 18 developers directly and built direct visibility with the Director.
"""
  },
  {
    "story_id": "amex-crr-pivots",
    "story_slug": "amex-crr-pivots",
    "company": "American Express",
    "domain": "career",
    "event_date": "2024-mm-dd",
    "tags": ["amex","crr","strategic-pivot","product-strategy","pi-planning"],
    "text": """
Satvik led CRR through 3 major strategic pivots during his tenure:

Pivot 1 (PI 25.2): Original plan was to build the full platform logic layer first.
Satvik changed direction to lift-and-shift the POD (Proof of Delivery) first to show early value.
This reduced risk and gave stakeholders something tangible quickly.

Pivot 2 (PI 25.5): An AML regulatory audit created a compliance dependency.
The full CRR platform launch was pushed to 2028 to accommodate regulatory requirements.
Satvik communicated this delay upward and replanned the roadmap accordingly.

Pivot 3 (PI 26.2): A data quality crisis was discovered — the underlying data feeding CRR was unreliable.
Satvik made the bold call to pause CRR feature development entirely and redirect the team to fix the data layer first.
This pivot required presenting the decision to VP-level leadership and getting buy-in.
Current focus: data standardisation, derivation, translation, categorisation across 1,100+ datapoints and 34 product portfolios.
"""
  },
  {
    "story_id": "amex-vp-pie-chart",
    "story_slug": "amex-vp-pie-chart",
    "company": "American Express",
    "domain": "achievement",
    "event_date": "2025-mm-dd",
    "tags": ["amex","crr","vp","strategic-visibility","workload","leadership"],
    "text": """
Satvik created a strategic workload analysis showing that CRR consumed 55.8% of his team's total PI capacity.
He sent this pie chart directly to VP Gregory A. Liss as evidence that the product needed dedicated senior PM support.
The message was direct: the product's complexity and cross-team dependencies warranted a dedicated hire.

Result: VP Gregory A. Liss hired a new Senior PM specifically for CRR.
The Senior PM joined in June 2025, validating Satvik's analysis.
This demonstrated Satvik's ability to use data to influence executive decisions and advocate for his team.
"""
  },
  {
    "story_id": "amex-data-standardisation",
    "story_slug": "amex-data-standardisation",
    "company": "American Express",
    "domain": "career",
    "event_date": "2026-mm-dd",
    "tags": ["amex","data-strategy","standardisation","crr","pi-26"],
    "text": """
After Pivot 3, Satvik's current work (PI 26.2+) is entirely focused on data quality and standardisation.
He is leading the translation, standardisation, derivation, and categorisation of 1,100+ datapoints
across 34 product portfolios within American Express.

Key responsibilities:
- Defining data standards and schemas for AML risk signals
- Working with data engineers on BigQuery migration
- Presenting the data standardisation roadmap to new VP Kai
- Building alignment across 34 product teams on data definitions

This work is the foundation for any future CRR platform rebuild — garbage in, garbage out.
Satvik's insight: fixing the data layer is more valuable than shipping features on bad data.
"""
  },
  {
    "story_id": "amex-leadership-in-action",
    "story_slug": "amex-leadership-in-action",
    "company": "American Express",
    "domain": "achievement",
    "event_date": "2025-mm-dd",
    "tags": ["amex","award","leadership","recognition","g3l2"],
    "text": """
Satvik received the Leadership in Action Award at American Express — a recognition for demonstrating
exceptional leadership beyond his role level.

Other recognitions at Amex:
- G3L2 performance rating (top tier)
- G1L2 rating in 2025
- Multiple Blue Rewards from VP and Director level
- RTE/Agile Champions appreciation for backlog quality across 7 PIs

The Leadership in Action Award specifically called out:
- Taking full ownership of CRR from his manager Anuj Kathwariya
- Leading 18 developers solo across 10 sprints
- Building direct visibility with the Director level

His manager Anuj Kathwariya was described as kind but a heavy micromanager.
Satvik learned Rally, SAFe, and user story writing from scratch under Anuj in his first months.
"""
  },
  {
    "story_id": "amex-evan-ai-workfusion",
    "story_slug": "amex-evan-ai-workfusion",
    "company": "American Express",
    "domain": "achievement",
    "event_date": "2025-mm-dd",
    "tags": ["amex","ai","workfusion","evan-ai","demo","vp","financial-screening"],
    "text": """
Satvik led the integration of Evan AI (by Workfusion) into the Amex AML workflow.
Evan AI is used for financial screening — specifically negative news and media triage for AML compliance.
The integration automated the review of adverse media and negative news about entities under AML review.

Satvik gave a live AI demo to the VP of AI at American Express.
The demo showcased how Evan AI reduced manual review time for negative news screening
and improved consistency in AML risk decisions.

This made Satvik one of the few APMs at Amex with hands-on AI integration experience
at the VP-visibility level. It also fed his personal interest in AI product management.
"""
  },
]

QA_PROMPT = """You are processing career stories for Satvik Jain's LifeOS knowledge base.

Generate 8-10 atomic Q&A pairs from this career story.
Rules:
- Simple specific Q → single clear A (1-3 sentences max)
- Always say "Satvik" not "he/I"
- English only
- Each Q must be narrow and answerable from the text alone
- Focus on: achievements, decisions, metrics, people, outcomes

Story:
{text}

Output ONLY valid JSON array:
[{{"question": "...", "answer": "..."}}]"""

def generate_qa(text):
    result = subprocess.run(
        ["claude","--print"],
        input=QA_PROMPT.format(text=text.strip()),
        capture_output=True, text=True, timeout=90
    )
    raw = result.stdout.strip()
    start, end = raw.find("["), raw.rfind("]")+1
    return json.loads(raw[start:end])

def main():
    print("Loading BGE model...")
    model = SentenceTransformer(BGE_MODEL)

    client = MongoClient(MONGO_URI)
    coll = client["linkright"]["lifeos_vectors"]
    total_inserted = 0

    for story in STORIES:
        print(f"\n→ {story['story_slug']}")
        pairs = generate_qa(story["text"])
        print(f"  {len(pairs)} Q&A pairs generated")

        docs = []
        sid = uuid.uuid4().hex[:12]
        for qa in pairs:
            vec = model.encode(BGE_PREFIX + qa["answer"], normalize_embeddings=True).tolist()
            docs.append({
                "_id": f"lifeos-{sid}-{uuid.uuid4().hex[:8]}",
                "question":        qa["question"],
                "answer":          qa["answer"],
                "story_id":        sid,
                "story_slug":      story["story_slug"],
                "domain":          story["domain"],
                "category":        "A",
                "event_date":      story["event_date"],
                "recorded_date":   RECORDED_DATE,
                "company":         story["company"],
                "tags":            story["tags"],
                "embedding":       vec,
                "embedding_model": BGE_MODEL,
                "embedding_dims":  768,
                "verified":        True,
                "source":          "batch",
                "version":         1,
                "created_at":      datetime.utcnow(),
            })
        result = coll.insert_many(docs)
        total_inserted += len(result.inserted_ids)
        print(f"  ✅ Inserted {len(result.inserted_ids)} vectors")

    total = coll.count_documents({})
    client.close()
    print(f"\n✅ Total new vectors: {total_inserted}")
    print(f"   Grand total in lifeos_vectors: {total}")

if __name__ == "__main__":
    main()
