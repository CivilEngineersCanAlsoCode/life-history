Plan: Life Brain — Intelligent Life Capture & Expert Conversation OS
                                                                                                             
 Context                                                

 Ek complete "Life OS" banana hai jisme:
 - Conversational capture (structured + casual)
 - Truth-first philosophy: conflicting information block hoti hai until resolved
 - Anti-hallucination: har output grounded in vector DB, ya denial
 - Famous expert personas jo real-life legends ki tarah baat karein
 - Multi-expert panel sessions
 - MECE extraction pipeline
 - Session continuity + emotional intelligence
 - Sabhi .agents/workflows/sync-life.md mein documented

 ---
 Complete Architecture

 User Message
     ↓
 [Intent Detector] ─── even in small talk → suggest expert
     ↓
 [Mode Gate] → Small Talk / Guided
     │
     ├─ Small Talk → [Passive Capture] → confidence: 0.6 → Review Queue
     │
     └─ Guided → [Use Case Selector (Top 10 + Full List)]
                     ↓
               [Expert Roster] → user confirms introduction
                     ↓
               [Single Expert OR Multi-Expert Panel]
                     ↓
               [One-by-One Focused Q&A + Depth Probing]
                     ↓
               [MECE Extraction Pipeline]
                     ↓
               ┌────────────────────────────┐
               │  TRUTH ENGINE              │
               │  Conflict Detection →      │
               │  Block / Clarify / Update  │
               └────────────────────────────┘
                     ↓ (only if clean)
               [Groundedness Check]
                     ↓
               [ChromaDB Commit]

 ---
 Layer 0: Truth Engine (Conflict Detection)

 Core Philosophy: "Ek bhi galat memory poori retrieval ko poison kar sakti hai."

 Pre-Insert Conflict Check

 Before inserting any new Q&A pair:

 def conflict_check(new_pair: QAPair, collection: ChromaDB) -> ConflictResult:
     # Step 1: Find semantically similar existing pairs
     candidates = collection.query(
         query_texts=[new_pair.question + " " + new_pair.answer],
         n_results=5,
         where={"domain": new_pair.metadata.domain}
     )

     for candidate in candidates:
         sem_sim = candidate.cosine_similarity  # from query results
         contradiction = measure_contradiction(new_pair, candidate)
         conflict_score = sem_sim * contradiction.magnitude

         if conflict_score > CONFLICT_THRESHOLD:
             return ConflictResult(status="CONFLICT", existing=candidate, score=conflict_score)

     return ConflictResult(status="SAFE")

 Quantitative Conflict Formula

 Conflict Score = Semantic_Similarity × Contradiction_Magnitude

 Semantic_Similarity = cosine_sim(embed(new_pair), embed(existing_pair))
   # Threshold: > 0.75 means "about the same thing"

 Contradiction_Magnitude = based on atom type:
   ├─ METRIC (numerical): |new_val - old_val| / max(new_val, old_val)
   │    e.g., marks 100 vs 30 → |100-30|/100 = 0.70
   ├─ FACT (boolean/status): LLM binary → 0.0 or 1.0
   │    e.g., "I led project" vs "I supported project" → 1.0
   ├─ DATE: date_diff_days / 365  (normalized to 0-1)
   └─ STORY: semantic_divergence score from LLM (0-1)

 Decision Matrix:
   conflict_score > 0.6  → HARD CONFLICT → block, ask user
   0.3 < score ≤ 0.6     → SOFT CONFLICT → warn, ask user
   0.1 < score ≤ 0.3     → ENRICHMENT   → auto-update existing (new info adds detail)
   score ≤ 0.1           → SAFE          → insert freely

 Conflict Resolution Protocol

 System: "Ruko ek second —

 Tumne pehle kaha tha:
   📌 [existing_pair.answer] (stored on [existing_pair.date])

 Abhi tum bol rahe ho:
   📝 [new_pair.answer]

 Yeh dono aapas mein contradict karte hain. Kya sahi hai?"

 Options:
   A) Purani baat sahi hai → discard new entry
   B) Nayi baat sahi hai → update purani, create change_log entry
   C) Dono alag contexts mein sahi hain → add context_qualifier to both
      (User specifies: "marks 100 = semester 1", "marks 30 = semester 2")
   D) Verify karna hai baad mein → flag both as unverified, add to review queue

 Change Log (Audit Trail)

 Every correction creates a document_record type entry:
 {
     "type": "document_record",
     "category": "correction",
     "old_doc_id": "career_edu_2020_marks_a3f2",
     "old_value": "marks: 100",
     "new_value": "marks: 30",
     "resolution": "user_confirmed_new",
     "date": "2024-03-08",
     "context": "semester 2 result"
 }

 ---
 Layer 0B: Anti-Hallucination Protocol

 Core Rule: "Jo DB mein nahi hai, wo bolenge nahi."

 Groundedness Score Formula

 Groundedness = max(cosine_sim(query_embed, doc_embed_i)) over retrieved docs

 Output Decision:
   Groundedness > 0.85  → HIGH confidence
                           Output: "[Answer] (source: {doc_id})"

   0.70 < G ≤ 0.85      → MEDIUM confidence
                           Output: "[Answer] — yeh meri understanding hai, confirm karo."

   0.50 < G ≤ 0.70      → LOW confidence
                           Output: "Mujhe kuch related pata hai, lekin poora confident nahi hun:
                                   [Answer] — kya yeh sahi hai?"

   G ≤ 0.50             → NO MATCH
                           Output: "Mere paas is baare mein enough verified information
                                   nahi hai. Kya tum mujhe yeh batana chahoge?"

 Synthesis Limit

 - Max 3 vectors combine karo for one output
 - Har vector ko cite karo: (source: doc_1, doc_2, doc_3)
 3 vectors required → don't synthesize, ask for narrower question

 Attribution Format

 "Tumhara Sprinklr salary approximately ₹X tha.
 (Yeh information [career_compensation_2022_sprinklr_b4c1] se hai, confidence: 0.92)"

 ---
 Layer 1: Mode Gate + Intent Detection

 Entry Point

 System: "Kya chal raha hai?"

 Auto-detect from message:
 - Keywords → use case matching (even in small talk)
 - No keywords → show mode menu:
   [A] Bas baatein (Free talk)
   [B] Kuch record karna hai (Guided)

 Small Talk Intent Detection

 Even in casual mode, continuously detect intent:

 def detect_intent_from_small_talk(message: str) -> SuggestionResult:
     matches = match_use_cases(message, top_n=3)

     if matches[0].confidence > 0.7:
         # Proactively suggest
         expert = get_expert_for_use_case(matches[0])
         return SuggestionResult(
             message=f"Sunta hun. Lagta hai {expert.name} ({expert.role}) is maamle mein kafi helpful ho
 sakte hain. Kya main unhe introduce karun?",
             expert=expert,
             use_case=matches[0]
         )
     # else: continue small talk without interruption

 Key: Suggestion sirf ek baar. Agar user ignore kare → mat baar baar poochho.

 ---
 Layer 2: Use Case Catalog (40+ Use Cases)

 Selection Flow

 User ne context diya → Top 10 show karo (ranked by semantic match)
 User ne context nahi diya → Full categorized list show karo

 Display:
 "Tumhare baaton ke hisaab se, yeh sabse relevant lag raha hai:

 1. 🎯 [C1] Interview Prep - Behavioral  (Interviewer: Satya)   ▓▓▓▓▓▓▓▓░░ 92%
 2. 💼 [C11] Leadership Story Capture   (Coach: Narayana)       ▓▓▓▓▓▓▓░░░ 87%
 3. 🧠 [C7] Career Planning & Pivots   (Strategist: Indra)      ▓▓▓▓▓▓░░░░ 81%
 ...10 results...

 [📋 Sabhi use cases dikhao]"

 Full Use Case List

 🎯 CAREER

 ┌─────┬─────────────────────────────┬─────────────────────────────┬────────────────────────────────────┐
 │ ID  │          Use Case           │           Expert            │              Persona               │
 ├─────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────────┤
 │ C1  │ Interview Prep - Behavioral │ Satya (Satya Nadella)       │ Empathetic, growth mindset         │
 │     │                             │                             │ interviewer                        │
 ├─────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────────┤
 │ C2  │ Interview Prep - Technical  │ Richard (Feynman)           │ Simplify, first-principles         │
 ├─────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────────┤
 │ C3  │ Interview Prep - System     │ Jeff (Bezos)                │ Scale, working backwards           │
 │     │ Design                      │                             │                                    │
 ├─────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────────┤
 │ C4  │ Resume Crafting             │ Indra (Indra Nooyi)         │ Strategic positioning              │
 ├─────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────────┤
 │ C5  │ Salary Negotiation          │ Chris (Chris Voss)          │ FBI negotiator                     │
 ├─────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────────┤
 │ C6  │ Performance Review Prep     │ Andy (Andy Grove)           │ OKRs, direct feedback              │
 ├─────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────────┤
 │ C7  │ Career Planning & Pivots    │ Naval (Naval Ravikant)      │ Optionality, leverage              │
 ├─────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────────┤
 │ C8  │ Job Search Strategy         │ Reed (Reid Hoffman)         │ LinkedIn, network leverage         │
 ├─────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────────┤
 │ C9  │ Project Documentation       │ Narayana (N.R. Narayana     │ Ethics + execution                 │
 │     │                             │ Murthy)                     │                                    │
 ├─────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────────┤
 │ C10 │ Learning & Skill Dev        │ Richard (Feynman)           │ Feynman technique                  │
 ├─────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────────┤
 │ C11 │ Leadership Stories          │ APJ (A.P.J. Abdul Kalam)    │ Inspiring, values                  │
 ├─────┼─────────────────────────────┼─────────────────────────────┼────────────────────────────────────┤
 │ C12 │ Team/Manager Dynamics       │ Andy (Andy Grove)           │ Management by OKR                  │
 └─────┴─────────────────────────────┴─────────────────────────────┴────────────────────────────────────┘

 💛 RELATIONSHIPS

 ┌─────┬─────────────────────────┬─────────────────────────────┬──────────────────────────────┐
 │ ID  │        Use Case         │           Expert            │           Persona            │
 ├─────┼─────────────────────────┼─────────────────────────────┼──────────────────────────────┤
 │ R1  │ Conflict Resolution     │ Esther (Esther Perel)       │ Psychoanalytic, European wit │
 ├─────┼─────────────────────────┼─────────────────────────────┼──────────────────────────────┤
 │ R2  │ Difficult Conversations │ Chris (Chris Voss)          │ Tactical empathy             │
 ├─────┼─────────────────────────┼─────────────────────────────┼──────────────────────────────┤
 │ R3  │ Romantic Relationship   │ Devdutt (Devdutt Pattanaik) │ Indian mythology lens        │
 ├─────┼─────────────────────────┼─────────────────────────────┼──────────────────────────────┤
 │ R4  │ Family Issues           │ Ratan (Ratan Tata)          │ Humble, family values        │
 ├─────┼─────────────────────────┼─────────────────────────────┼──────────────────────────────┤
 │ R5  │ Friendship Dynamics     │ Brené (Brené Brown)         │ Vulnerability + courage      │
 ├─────┼─────────────────────────┼─────────────────────────────┼──────────────────────────────┤
 │ R6  │ Professional Networking │ Reid (Reid Hoffman)         │ Strategic connections        │
 ├─────┼─────────────────────────┼─────────────────────────────┼──────────────────────────────┤
 │ R7  │ Boundaries & Saying No  │ Brené (Brené Brown)         │ Assertiveness + warmth       │
 └─────┴─────────────────────────┴─────────────────────────────┴──────────────────────────────┘

 💪 HEALTH

 ┌─────┬────────────────────┬─────────────────────┬──────────────────────────┐
 │ ID  │      Use Case      │       Expert        │         Persona          │
 ├─────┼────────────────────┼─────────────────────┼──────────────────────────┤
 │ H1  │ Fitness Planning   │ Andrew (Huberman)   │ Neuroscience + protocols │
 ├─────┼────────────────────┼─────────────────────┼──────────────────────────┤
 │ H2  │ Mental Wellness    │ Brené (Brené Brown) │ Research-backed empathy  │
 ├─────┼────────────────────┼─────────────────────┼──────────────────────────┤
 │ H3  │ Sleep Optimization │ Andrew (Huberman)   │ Circadian science        │
 ├─────┼────────────────────┼─────────────────────┼──────────────────────────┤
 │ H4  │ Nutrition          │ Andrew (Huberman)   │ Evidence-based           │
 ├─────┼────────────────────┼─────────────────────┼──────────────────────────┤
 │ H5  │ Energy Management  │ Sadhguru (Sadhguru) │ Inner engineering        │
 ├─────┼────────────────────┼─────────────────────┼──────────────────────────┤
 │ H6  │ Medical Tracking   │ Andrew (Huberman)   │ Systematic tracking      │
 └─────┴────────────────────┴─────────────────────┴──────────────────────────┘

 💰 FINANCE

 ┌─────┬───────────────────────┬───────────────────────┬──────────────────────────┐
 │ ID  │       Use Case        │        Expert         │         Persona          │
 ├─────┼───────────────────────┼───────────────────────┼──────────────────────────┤
 │ F1  │ Budgeting             │ Warren (Buffett)      │ Live below means, frugal │
 ├─────┼───────────────────────┼───────────────────────┼──────────────────────────┤
 │ F2  │ Investment Strategy   │ Warren (Buffett)      │ Long-term, value         │
 ├─────┼───────────────────────┼───────────────────────┼──────────────────────────┤
 │ F3  │ Salary & Compensation │ Charlie (Munger)      │ Opportunity cost         │
 ├─────┼───────────────────────┼───────────────────────┼──────────────────────────┤
 │ F4  │ Big Purchases         │ Charlie (Munger)      │ Inversion, second-order  │
 ├─────┼───────────────────────┼───────────────────────┼──────────────────────────┤
 │ F5  │ Financial Goals       │ Rakesh (Jhunjhunwala) │ Indian market wisdom     │
 └─────┴───────────────────────┴───────────────────────┴──────────────────────────┘

 🧠 PERSONAL GROWTH

 ┌─────┬──────────────────────┬─────────────────────┬─────────────────────────────┐
 │ ID  │       Use Case       │       Expert        │           Persona           │
 ├─────┼──────────────────────┼─────────────────────┼─────────────────────────────┤
 │ P1  │ Habit Building       │ Andrew (Huberman)   │ Dopamine + routine          │
 ├─────┼──────────────────────┼─────────────────────┼─────────────────────────────┤
 │ P2  │ Goal Setting         │ Elon (Musk)         │ First principles, moonshots │
 ├─────┼──────────────────────┼─────────────────────┼─────────────────────────────┤
 │ P3  │ Journaling           │ Brené (Brené Brown) │ Reflection + growth         │
 ├─────┼──────────────────────┼─────────────────────┼─────────────────────────────┤
 │ P4  │ Learning Plans       │ Richard (Feynman)   │ Simplify to mastery         │
 ├─────┼──────────────────────┼─────────────────────┼─────────────────────────────┤
 │ P5  │ Identity & Values    │ Sadhguru            │ Inner clarity               │
 ├─────┼──────────────────────┼─────────────────────┼─────────────────────────────┤
 │ P6  │ Major Life Decisions │ Charlie (Munger)    │ Mental models               │
 └─────┴──────────────────────┴─────────────────────┴─────────────────────────────┘

 🎨 CREATIVITY

 ┌─────┬───────────────────────────┬──────────────────┬─────────────────────────────┐
 │ ID  │         Use Case          │      Expert      │           Persona           │
 ├─────┼───────────────────────────┼──────────────────┼─────────────────────────────┤
 │ CR1 │ Idea Generation           │ Steve (Jobs)     │ Intersection of arts + tech │
 ├─────┼───────────────────────────┼──────────────────┼─────────────────────────────┤
 │ CR2 │ Writing                   │ Naval (Ravikant) │ Aphoristic, clear           │
 ├─────┼───────────────────────────┼──────────────────┼─────────────────────────────┤
 │ CR3 │ Personal Project Planning │ Jeff (Bezos)     │ Working backwards + PR/FAQ  │
 └─────┴───────────────────────────┴──────────────────┴─────────────────────────────┘

 📚 MEMORIES

 ┌─────┬────────────────┬─────────────────────┬────────────────────────────────────┐
 │ ID  │    Use Case    │       Expert        │              Persona               │
 ├─────┼────────────────┼─────────────────────┼────────────────────────────────────┤
 │ M1  │ Memory Capture │ APJ (Kalam)         │ Turning points, moments of grace   │
 ├─────┼────────────────┼─────────────────────┼────────────────────────────────────┤
 │ M2  │ Life Review    │ Sadhguru            │ Pattern recognition, consciousness │
 ├─────┼────────────────┼─────────────────────┼────────────────────────────────────┤
 │ M3  │ People Notes   │ Devdutt (Pattanaik) │ Relationships as stories           │
 └─────┴────────────────┴─────────────────────┴────────────────────────────────────┘

 ---
 Layer 3: Expert Introduction Protocol

 Introduction Script

 System (before loading any expert):

 "Main tumhe [Expert Name] se milwana chahta hun.

 [Expert Name] ek [domain] expert hain — [one-liner about their style].
 Real life mein, [brief bio: why they're famous, what they stand for].

 Kya tum [Name] ke saath is topic pe baat karna chahoge?"

 [Haan, bilkul] → Load persona
 [Koi aur chahiye] → Show alternatives in same domain
 [Khud handle karo] → System proceeds without persona

 Example:
 "Main tumhe Warren se milwana chahta hun.

 Warren ek finance aur investment expert hain — patient, long-term, folksy wisdom.
 Real life mein Warren Buffett ek legendary investor hain jo 60+ saalon se compounding ka
 power demonstrate kar rahe hain. Unka mantra: "Be greedy when others are fearful."

 Kya tum Warren ke saath apni financial strategy pe baat karna chahoge?"

 ---
 Layer 4: Multi-Expert Panel

 Panel Formation

 User: "Career change karna chahta hun par family ka pressure hai."
 System: "Yeh decision career aur relationships dono ko touch karta hai.
          Main tumhe [Naval] (career strategy) aur [Esther] (family dynamics) dono se
          milwata hun — ek panel mein. Theek hai?"

 [Yes] → Panel session starts

 Panel Conversation Format

 Sequential Format (default):
 User Q → Naval responds (career angle) → Esther responds (relationship angle)

 Debate Format (opt-in):
 User: "Kya mujhe startup join karni chahiye?"
 Elon: "Regretting not taking the shot is worse than failing. Jump."
 Warren: "Never risk what you have and need for what you don't have and don't need."
 System: "Dono perspectives sun lo — ab tum decide karo."

 Panel Rules:
 - Each expert stays in their domain
 - Privacy firewall: Esther sirf relationship data access kare, Warren sirf financial
 - Max 3 experts in one panel (cognitive load)
 - Clear speaker labels: [Warren]: / [Esther]:

 ---
 Layer 5: MECE Extraction Pipeline

 Nuggets FIRST, Q&A SECOND:

 Raw Answer
     ↓
 A: Nugget Identification
    (one subject + one predicate = one nugget,
     metrics ALWAYS separate nuggets)
     ↓
 B: ME Check (cosine_sim > 0.85 → merge)
     ↓
 C: Q&A Generation
    (primary Q + 2-3 alt phrasings in tags)
     ↓
 D: CE Check (LLM: "koi info miss toh nahi?")
     ↓
 E: Metadata Assignment (inherited + per-pair + dynamic extension)
     ↓
 F: TRUTH ENGINE (conflict check before insert)
     ↓
 G: Groundedness Verify (for outputs back to user)

 5 Atom Types: FACT | STORY | METRIC | DECISION | LESSON

 ---
 Layer 6: Dynamic Metadata Extension

 3-Tier Fallback:
 Tier 1: Existing 47 fields → map karo
 Tier 2: tags field → overflow bucket
 Tier 3: extra_metadata: {} → novel key:value pairs

 Auto-Promotion: When extra_metadata key appears 20+ times → create beads issue for schema promotion

 ---
 Layer 7: Passive Small Talk Capture

 Confidence: 0.6 for small talk extractions
 Review queue: weekly prompt "Yeh baatein confirm karo?"
 User confirms → confidence: 0.9, insert formally

 ---
 Brainstormed Additional Features

 1. Accountability Partner Mode

 Expert tracks commitments made in past sessions:
 Warren: "Pichli session mein tumne kaha tha ki March tak emergency fund build karoge.
          3 months ho gaye — kya hua?"

 2. Expert Disagreement (Adversarial Mode)

 Two experts deliberately disagree to give robust perspective:
 Elon vs Warren on "Should I quit my job for a startup?"
 User gets adversarial input → makes more informed decision

 3. Sentiment Tracking Across Sessions

 # Track emotion tags over time
 trend = analyze_emotion_trend(last_10_sessions)
 if trend.dominant == "stressed" and trend.increasing:
     suggest_use_case("H2: Mental Wellness", expert="Brené")

 4. First-Person Biography Generator

 After sufficient sessions, auto-generate:
 - Career arc narrative
 - Top 5 STAR stories
 - Leadership philosophy (derived from decisions)
 - Life values (derived from reflections + goals)
 Format: interview-ready paragraphs

 5. Time Machine Mode

 Expert answers as themselves at different life points:
 "Warren 1960 mein kya karte agar unke paas ₹10 lakh hote?"
 vs
 "Warren 2024 mein kya karte?"
 → Historical context + modern application

 6. Cross-Domain Pattern Insight

 After 15+ sessions:
 System: "Maine notice kiya hai — tumhara career mein control freakery
          aur relationships mein micromanagement tendency common hai.
          Kya tum isko explore karna chahoge?"
 Creates star_story type entry with pattern_id linking both domains.

 7. Privacy Firewall per Expert

 expert_data_access = {
     "Warren": ["finance", "career_compensation"],
     "Esther": ["relationships", "personal_growth"],
     "APJ": ["career", "identity", "goals"],
     "Sadhguru": ["health", "personal_growth", "beliefs"]
 }
 # Expert cannot "see" outside their domain

 8. Expert Signature Stories

 Each persona has 2-3 signature stories/quotes from real person:
 warren_signatures = [
     "See's Candies story — pricing power aur moat",
     "Missing Amazon/Google — 'Too Hard' pile",
     "Newspaper test — kya tum comfortable hoge agar yeh front page pe hota?"
 ]
 # Warren naturally references these in conversation for authenticity

 9. Knowledge Completeness Dashboard

 For each use case, show what % of standard questions are answered:
 Interview Prep (C1):
   Problem Definition    ████████░░ 80%
   STAR Stories         ████░░░░░░ 40%
   Metrics & Impact     ██████████ 100%
   Failure Stories      ██░░░░░░░░ 20%

 "Failure Stories pe focus karo — interview mein zaroor poochhenge."

 ---
 Workflow File: .agents/workflows/sync-life.md

 Will contain:
 1. Session Entry + Mode Gate Protocol
 2. Full Use Case Catalog (40+ entries)
 3. Context Matching Algorithm (embedding-based)
 4. Expert Roster (16 personas with full descriptions)
 5. Introduction Script Templates
 6. Panel Formation Rules
 7. One-by-One Question Banks per Use Case
 8. MECE Extraction Protocol (complete algorithm)
 9. Truth Engine Protocol (conflict detection + resolution)
 10. Groundedness Formula + Output Decision Rules
 11. Dynamic Metadata Extension (3-tier)
 12. Small Talk Passive Capture Rules
 13. Session State Schema
 14. Privacy Firewall Definitions
 15. Accountability Tracking

 ---
 Beads Issues to Create

 New Epics:

 E4: Conversational System (blocks all others) P0

 ┌───────┬───────────────────────────────────────┬──────────┐
 │ Issue │                 Title                 │ Priority │
 ├───────┼───────────────────────────────────────┼──────────┤
 │ F4.1  │ Mode Gate + Intent Detection          │ P1       │
 ├───────┼───────────────────────────────────────┼──────────┤
 │ F4.2  │ Use Case Catalog + Top 10 Matching    │ P1       │
 ├───────┼───────────────────────────────────────┼──────────┤
 │ F4.3  │ Expert Roster (16 personas with bios) │ P1       │
 ├───────┼───────────────────────────────────────┼──────────┤
 │ F4.4  │ Expert Introduction Protocol          │ P1       │
 ├───────┼───────────────────────────────────────┼──────────┤
 │ F4.5  │ One-by-One Question Flow Engine       │ P1       │
 ├───────┼───────────────────────────────────────┼──────────┤
 │ F4.6  │ Multi-Expert Panel System             │ P2       │
 ├───────┼───────────────────────────────────────┼──────────┤
 │ F4.7  │ Session Continuity + State Tracking   │ P2       │
 ├───────┼───────────────────────────────────────┼──────────┤
 │ F4.8  │ Small Talk Passive Capture            │ P3       │
 ├───────┼───────────────────────────────────────┼──────────┤
 │ F4.9  │ Accountability Partner Mode           │ P3       │
 ├───────┼───────────────────────────────────────┼──────────┤
 │ F4.10 │ Write sync-life.md workflow file      │ P1       │
 └───────┴───────────────────────────────────────┴──────────┘

 E5: Truth & Grounding Engine P0

 ┌───────┬───────────────────────────────────────────────┬──────────┐
 │ Issue │                     Title                     │ Priority │
 ├───────┼───────────────────────────────────────────────┼──────────┤
 │ F5.1  │ Conflict Detection Algorithm (quantitative)   │ P1       │
 ├───────┼───────────────────────────────────────────────┼──────────┤
 │ F5.2  │ Conflict Resolution UX (block/clarify/update) │ P1       │
 ├───────┼───────────────────────────────────────────────┼──────────┤
 │ F5.3  │ Change Log + Audit Trail                      │ P2       │
 ├───────┼───────────────────────────────────────────────┼──────────┤
 │ F5.4  │ Groundedness Score Formula + Output Rules     │ P1       │
 ├───────┼───────────────────────────────────────────────┼──────────┤
 │ F5.5  │ Synthesis Limit + Attribution Format          │ P2       │
 └───────┴───────────────────────────────────────────────┴──────────┘

 E0: Knowledge Extraction Strategy P1 (depends on E4)

 ┌───────┬───────────────────────────────────────────────┬──────────┐
 │ Issue │                     Title                     │ Priority │
 ├───────┼───────────────────────────────────────────────┼──────────┤
 │ F0.1  │ Interview session format + conversation guide │ P1       │
 ├───────┼───────────────────────────────────────────────┼──────────┤
 │ F0.2  │ Atomic knowledge extraction (nuggets first)   │ P1       │
 ├───────┼───────────────────────────────────────────────┼──────────┤
 │ F0.3  │ MECE validation algorithm (ME + CE checks)    │ P1       │
 ├───────┼───────────────────────────────────────────────┼──────────┤
 │ F0.4  │ Q&A pair generator + question templates       │ P1       │
 ├───────┼───────────────────────────────────────────────┼──────────┤
 │ F0.5  │ Metadata auto-assignment + dynamic extension  │ P2       │
 └───────┴───────────────────────────────────────────────┴──────────┘

 ---
 Implementation Order

 E5 (Truth Engine) → defines what "valid data" looks like
     ↓ parallel with ↓
 E4 (Conversational System) → defines how data enters
     ↓
 E0 (Extraction Pipeline) → how raw answers become Q&A atoms
     ↓
 E1 (ChromaDB) → F1.1 schema → F1.2 ingestion
     ↓
 E2 (Organize existing knowledge) → retroactively apply pipeline
     ↓
 E3 (Context directory) → reference templates

 ---
 Verification

 - User messages "nervous about interview" → system suggests Satya (Interviewer persona) within 2 messages
 - User types conflicting info → conflict_score calculated, blocked with clear explanation
 - Expert introduced with proper bio before conversation starts
 - Multi-expert panel shows clear [Name]: labels, respects privacy firewall
 - LLM output with groundedness < 0.50 results in "mere paas yeh info nahi hai"
 - 1 raw answer (5 sentences) → 3-5 MECE pairs, 0 conflicts, all grounded