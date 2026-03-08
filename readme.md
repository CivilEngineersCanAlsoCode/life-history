# Life Brain — AI Second Brain & Vector Database

Satvik Jain ka personal knowledge base — career history, life experiences, relationships, goals, beliefs, aur har cheez jo ek complete AI replica banana ke liye chahiye. Yeh repo raw documents store karta hai, aur ChromaDB vector database me atomic knowledge units ke roop me indexed hota hai.

## Vision

Ek aisa AI brain banana hai jo:
- Meri poori life history jaanta ho — career, relationships, health, finance, beliefs, memories, sab kuch
- Koi bhi question poocho, instant relevant answer de — with proper context
- Interview prep se le ke life decisions tak, 260+ use cases support kare
- Privacy-aware ho — kaunsa data kahan expose ho, controlled rahe
- Time ke saath evolve kare — naye fields, naye domains, bina purana data tode

---

## Repository Structure

```
career history/
├── 00 - Identity & Resume/
│   ├── Interview Prep/          # STAR stories, resume brain index
│   ├── Resume & Portfolio/      # PDF resume, HTML portfolio
│   └── performance-review/      # Year-end reviews
├── 01 - Experience/
│   ├── 01 - Sprinklr (Apr 2022 – Jul 2024)/
│   │   ├── CGB (Citizen Governance Bot)/
│   │   ├── Use Case Hub/
│   │   └── Walmart Spark Driver Support/
│   └── 02 - American Express (Jul 2024 – Present)/
│       ├── 01 - CRR AML Risk Scoring Engine/
│       ├── 02 - Asset Manager/
│       ├── 03 - Advanced Rule Configurations/
│       ├── 04 - Sandbox Versioning/
│       └── 05 - Model Builder/
└── 02 - Resources & Learning/
```

---

## ChromaDB Architecture

### Collection Strategy

**One primary collection: `life_brain`**

Multiple collections mat banao. Reasons:
- Sabse valuable queries cross-domain hoti hain: "What have I learned about leadership?" touches career + personal growth + relationships
- ChromaDB metadata filtering se "virtual collections" ban jati hain without actual separation
- Schema evolution ek jagah manage hoti hai
- Personal scale pe ek collection 100K+ docs handle karta hai

**When to add a NEW collection (rare):**

| Trigger | Example | Why separate? |
|---------|---------|---------------|
| Different data modality | Image embeddings, audio transcripts | Different embedding model needed |
| Extreme volume (100K+ in one type) | 20 years of daily journals | Performance optimization |
| Different access control | Shared family collection vs private thoughts | Security boundary |

### Document Format

Har document = ONE atomic knowledge unit. Text khud self-contained hoga — metadata ke bina bhi samajh aaye:

```
# GOOD (self-contained, embedding-friendly):
"At American Express (Jul 2024-Present), as Senior Associate PM on the
CRR AML Risk Scoring Engine project, I modernized a 12-year-old legacy
system called Cadence. The core problem was that AML investigators spent
12-15 minutes per case because risk data was scattered across 6 different
tools. We consolidated this into a single unified interface, reducing
investigation time to under 4 minutes."

# BAD (depends on metadata to make sense):
"Reduced time from 12-15 minutes to under 4 minutes. Modernized the
legacy system."
```

**Rule: Text = source of truth (readable standalone). Metadata = index (enables filtering & linking).**

### Document ID Strategy

Format: `{domain}_{subdomain}_{YYYYMMDD}_{short_slug}_{4char_hash}`

Examples:
- `career_project_20240715_crr-aml-problem_a3f2`
- `health_mental_20250308_anxiety-trigger-work_b7e1`
- `relationships_family_20230101_papa-career-advice_c9d4`

---

## Metadata Schema (47 Fields)

260 use cases ke thorough analysis ke baad, 47 fields identify hue — 3 tiers me organized:

### TIER 1: Core Fields (24 fields — har document pe apply hote hain)

```python
metadata = {
    # ──── WHAT (Content Classification) ────
    "domain":         str,   # REQUIRED — life area (see Domain Taxonomy)
    "subdomain":      str,   # REQUIRED — specific area within domain
    "type":           str,   # REQUIRED — knowledge unit type (see Type Taxonomy)
    "tags":           str,   # comma-separated flexible tags — catch-all for anything not in structured fields

    # ──── WHEN (Temporal) ────
    "date":           str,   # ISO "YYYY-MM-DD" — exact date if known
    "date_start":     str,   # period start "YYYY-MM"
    "date_end":       str,   # period end "YYYY-MM" or "present"
    "life_phase":     str,   # "early_childhood" | "school" | "college" | "sprinklr_era" | "amex_era" | ...

    # ──── WHO (People & Organizations) ────
    "people":         str,   # comma-separated names involved
    "relationships":  str,   # comma-separated relation types: "mentor,manager,friend"
    "organization":   str,   # company, school, community, group
    "role":           str,   # your role in this context

    # ──── WHERE (Location & Context) ────
    "location":       str,   # city, country, or specific place
    "country":        str,   # country name (for travel, visa, cultural entries)
    "context":        str,   # "work" | "personal" | "social" | "travel" | "health" | "legal" | "financial" | "emergency"

    # ──── CAREER-SPECIFIC ────
    "company":        str,   # "sprinklr" | "amex" | ...
    "project":        str,   # project name slug: "crr_aml" | "use_case_hub" | ...
    "category":       str,   # "problem_definition" | "solution_architecture" | "stakeholder_mgmt" | "metric" | ...

    # ──── META (About the entry itself) ────
    "importance":     int,   # REQUIRED — 1-5 (1=trivial, 5=life-defining)
    "emotion":        str,   # primary emotion: "pride" | "regret" | "joy" | "anxiety" | "anger" | "gratitude" | ...
    "sentiment":      str,   # "positive" | "negative" | "neutral" | "mixed"
    "privacy":        str,   # REQUIRED — "public" | "private" | "confidential" | "secret"
    "confidence":     str,   # "verified" | "approximate" | "uncertain" | "subjective"
    "source":         str,   # REQUIRED — "interview" | "diary" | "memory" | "document" | "reflection" | "conversation" | "medical_record" | "financial_record"

    # ──── SCHEMA ────
    "schema_version": int,   # REQUIRED — starts at 1, increment on schema changes
}
```

**Required fields (har document pe mandatory):** `domain`, `subdomain`, `type`, `importance`, `privacy`, `source`, `schema_version`

### TIER 2: Extended Fields (23 fields — cross-domain, high value)

Yeh fields multiple domains me kaam aate hain. Jab relevant ho tab use karo:

```python
extended_metadata = {
    # ──── STATUS & OUTCOME ────
    "status":              str,   # "active" | "completed" | "abandoned" | "in_progress" | "paused" | "dropped" | "pending" | "resolved"
                                  # UC: 53,67,69,80,124,131-140,162,183,217,231,259
    "outcome":             str,   # free text — what resulted from this event/decision
                                  # UC: 34,62,64,68,70,111-120,136,165,173,179,193,221,225,249
    "resolution_status":   str,   # "resolved" | "ongoing" | "escalated" | "dropped" | "unresolved"
                                  # UC: 12,173,183,187,221,239
    "follow_up_status":    str,   # "pending" | "done" | "dropped" | "not_needed"
                                  # UC: 5,13,25,259

    # ──── QUANTITATIVE ────
    "monetary_value":      float, # any numeric value (salary, price, investment, etc.)
                                  # UC: 3,61-75,129,182,184,185,189,190,194,224
    "currency":            str,   # "INR" | "USD" | "EUR" | ...
                                  # UC: 61-75,129,182,184,190
    "rating":              int,   # 1-5 star rating for reviews
                                  # UC: 77,82,127,129,174,201-210,211-219
    "energy_level":        int,   # 1-5 (how energetic/drained)
                                  # UC: 29,50,56,115,123,130
    "severity":            int,   # 1-5 (for health, crisis, conflict)
                                  # UC: 41,51,225,239

    # ──── CONTENT REFERENCE ────
    "title":               str,   # book/movie/course/song/show/game name
                                  # UC: 77,81,82,86,211-214,219
    "author_creator":      str,   # author/director/creator name
                                  # UC: 77,81,86,212,213,219
    "medium":              str,   # "book" | "course" | "podcast" | "video" | "movie" | "tv_show" | "music" | "game" | "article"
                                  # UC: 77,82,86,211-214,219,238
    "platform":            str,   # "LinkedIn" | "Twitter" | "Udemy" | "Netflix" | "YouTube" | ...
                                  # UC: 82,166,214,231-240

    # ──── TRIGGERS & PATTERNS ────
    "trigger":             str,   # what caused this event/emotion
                                  # UC: 45,49,55,94,103,104,105,141,160,257
    "pattern_id":          str,   # unique ID to link recurring patterns across entries
                                  # UC: 23,101,147,196
    "related_id":          str,   # document ID of a related entry (for linking conflicts, contradictions, follow-ups)
                                  # UC: 140,147,249

    # ──── TEMPORAL EXTRAS ────
    "duration":            str,   # "3 months" | "45 minutes" | "2 years"
                                  # UC: 44,51,57,60,122,125,217,226
    "frequency":           str,   # "daily" | "weekly" | "monthly" | "yearly" | "one_time" | "sporadic"
                                  # UC: 69,125,195
    "expiry_date":         str,   # ISO "YYYY-MM-DD" — for documents, warranties, subscriptions, policies
                                  # UC: 181,182,184,185,188
    "time_of_day":         str,   # "early_morning" | "morning" | "afternoon" | "evening" | "night"
                                  # UC: 50,115,121,123,130,257

    # ──── ITEMS & EVENTS ────
    "item":                str,   # physical object: gift, product, vehicle, document
                                  # UC: 24,68,129,185,189,194,204,216
    "event_name":          str,   # conference/event/gathering name
                                  # UC: 13,32,85,174,218,238
    "environment":         str,   # "office" | "home" | "cafe" | "gym" | "outdoors" | "transit"
                                  # UC: 123,130
}
```

### TIER 3: Domain-Specific Fields (use `tags` until volume justifies promotion)

Yeh fields specific domains ke liye hain. Initially `tags` field me store karo as comma-separated values. Jab kisi field ki volume badhe aur filtering zaroori ho, tab promote karo to a proper metadata field via schema evolution.

```
HEALTH:       symptom, body_part, medication, dosage, side_effect, medical_procedure, sleep_quality, care_type
FINANCIAL:    transaction_type, asset_type, interest_rate, income_source
LEGAL:        document_type, physical_location, counterparty, policy_number, visa_type
DECISIONS:    decision_method, alternative_chosen, alternative_rejected, risk_level, stress_level
RELATIONSHIPS: relationship_status, last_contact_date, recurring_date, reliability_score
ENTERTAINMENT: genre, artist, preference_level
TRAVEL:       venue_name, venue_type, cuisine, trip_type, transport_mode
DIGITAL:      username, url, account_status, visibility
COMMUNICATION: communication_channel, audience_size, feedback_from, feedback_type
FAMILY:       generation, milestone_type, beneficiary
PERSONAL:     effectiveness, change_direction, stance, topic
```

**Promotion rule:** Jab kisi tag ka count 20+ entries ho aur tum usse frequently filter karte ho → promote to proper metadata field + backfill.

---

## Domain Taxonomy (20 domains)

| Domain | Subdomains | UC Range |
|--------|-----------|----------|
| `career` | job_search, project, skill, achievement, failure, negotiation, networking | 1-20 |
| `relationships` | family, friendship, romantic, professional, lost_touch, mentor | 21-40 |
| `health` | physical, mental, habits, medical, fitness, sleep, diet, substance | 41-60 |
| `finance` | income, expense, investment, loan, insurance, tax, subscription, goal | 61-75 |
| `education` | school, college, certification, self_learning, book, course, conference | 76-90 |
| `personal_growth` | lesson, realization, habit_change, therapy, bias, value, fear, coping | 91-110 |
| `decisions` | major_life, career_move, relationship, financial, ethical, risk | 111-120 |
| `daily_life` | routine, diary, observation, mood, gratitude, productivity, cooking, shopping | 121-130 |
| `goals` | short_term, long_term, abandoned, achieved, evolving, resolution, bucket_list | 131-140 |
| `beliefs` | values, philosophy, religion, politics, worldview, ethics, spirituality | 141-150 |
| `memories` | milestone, travel, event, celebration, childhood, sensory, turning_point | 151-160 |
| `creativity` | writing, ideas, side_project, art, innovation, content, analogy | 161-170 |
| `communication` | writing_style, presentation, conversation, speaking, feedback, persuasion | 171-180 |
| `legal` | document, contract, dispute, insurance, warranty, visa, property, vehicle | 181-190 |
| `family` | tree, recipe, parenting, inheritance, tradition, generational, elder_care | 191-200 |
| `travel` | trip, restaurant, hotel, packing, local_tips, commute, relocation, culture | 201-210 |
| `entertainment` | movie, music, book, game, food, fashion, hobby, sport, art | 211-220 |
| `emergency` | crisis, medical_emergency, financial_crisis, mental_crisis, backup, support | 221-230 |
| `social_digital` | online_presence, digital_footprint, community, volunteering, harassment | 231-240 |
| `ai_meta` | twin, faq, journaling, dashboard, coaching, simulation, forecasting, legacy | 241-260 |

## Type Taxonomy (18 types)

| Type | Description | Example |
|------|-------------|---------|
| `fact` | Verifiable statement | "I joined Amex in July 2024" |
| `event` | Something that happened | "Got Leadership Award in Q1 2025" |
| `qa_pair` | Interview Q&A or self-reflection Q&A | 15-question template answers |
| `star_story` | Structured STAR narrative | Situation-Task-Action-Result story |
| `metric` | Quantifiable data point | "85% time reduction" |
| `decision` | Choice made + rationale | "Chose Amex over Google because..." |
| `lesson` | Insight gained from experience | "Never ship without user testing" |
| `reflection` | Diary-style personal thought | Daily journal entry analysis |
| `preference` | Like/dislike/opinion | "Love spicy food, hate mushrooms" |
| `goal` | Aspiration with status | "Become a PM director by 30" |
| `relationship_note` | Info about a person in your life | "Papa always says 'plan before act'" |
| `habit` | Recurring behavior pattern | "Morning coffee + reading = peak focus" |
| `belief` | Held conviction or value | "Integrity > success" |
| `diary_entry` | Daily log entry | "Today felt overwhelmed by..." |
| `dream` | Aspiration or literal dream | "Want to start a SaaS company" |
| `regret` | Something you wish was different | "Should have negotiated harder at X" |
| `review` | Rating + opinion of something | "This course was 4/5, great for..." |
| `document_record` | Administrative/legal record | "Passport expires 2028-03-15" |

---

## Privacy & Access Layers

```
public       → Shareable with anyone (resume facts, portfolio, published work)
private      → Personal but not sensitive (daily diary, preferences, routines)
confidential → Sensitive (salary, health details, relationship issues, performance reviews)
secret       → Never expose via API without explicit auth (fears, regrets, confessions, passwords)
```

Future API banate waqt: `privacy` field se control karo ki kaunsa data kis context me accessible hai.
- Interview prep bot → sirf `public` + `private` career data
- Personal coaching bot → `public` + `private` + `confidential`
- Full access → explicit auth required, includes `secret`

---

## Schema Evolution Strategy

### Adding a New Field

```
Step 1: Schema version bump (e.g., 1 → 2)
Step 2: New docs get the new field
Step 3: Old docs have field = None (ChromaDB handles missing fields)
Step 4: Run backfill script → LLM reads each old doc's text → infers field value → updates metadata
Step 5: Update schema_version on backfilled docs
```

### Backfill Script Pattern

```python
def backfill_new_field(collection, field_name, prompt_template, llm_client):
    """Retroactively populate a new metadata field on old documents."""
    CURRENT_VERSION = 2  # update per migration

    docs = collection.get(
        where={"schema_version": {"$lt": CURRENT_VERSION}},
        include=["documents", "metadatas"]
    )

    for doc_id, text, meta in zip(docs["ids"], docs["documents"], docs["metadatas"]):
        # LLM infers the new field from existing text
        value = llm_client.infer(prompt_template.format(text=text))

        collection.update(
            ids=[doc_id],
            metadatas=[{**meta, field_name: value, "schema_version": CURRENT_VERSION}]
        )
```

**Key insight:** Since every document is self-contained text, you can ALWAYS retroactively extract new metadata from existing content using an LLM. Text IS your source of truth. Metadata is just an index.

### Decision Tree: What to Do When You Want to Track Something New

```
"I want to track something new"
    │
    ├── Is it a new DIMENSION of classification?
    │   (e.g., "energy_level", "stress_level", "effectiveness")
    │   → Add new metadata field + backfill old docs
    │
    ├── Is it a new AREA of life?
    │   (e.g., "spirituality", "parenting", "crypto")
    │   → Add new domain/subdomain value — no schema change needed (just strings)
    │
    ├── Is it fundamentally different DATA?
    │   (e.g., voice memos, photos, medical scans)
    │   → New collection (different embedding model/strategy)
    │
    └── Is it just a new TAG?
        (e.g., "stoicism", "morning_routine", "delhi_memories")
        → Add to tags field, no schema change
```

---

## Data Ingestion Flow

### Interview-Style Cleanup (Primary Method)

Phase 1: Identity & Background (verify resume facts)
Phase 2: Sprinklr Projects (one by one, 15 questions each)
Phase 3: AmEx Projects (one by one, 15 questions each)
Phase 4: Cross-cutting themes (skills, learnings, patterns)
Phase 5: Personal life domains (relationships, health, goals, etc.)

Process per question:
1. Claude poochega ek question
2. Tum answer doge (Hinglish me)
3. Claude verify karega + cleanup karega
4. Atomic knowledge units me todega
5. ChromaDB me store karega with proper metadata
6. Next question

### Chunking Rules

1. **One atomic unit per document** — ek fact, ek story, ek Q&A pair
2. **Self-contained text** — bina metadata ke bhi readable
3. **300-1500 characters ideal** — too short = no context, too long = diluted embedding
4. **Duplicate detection** — same fact multiple jagah ho toh best version rakho, baaki delete
5. **Cross-reference via metadata** — related entries ko `related_id` ya `pattern_id` se link karo

---

## Query Patterns (260 Use Cases Coverage)

### Career & Professional (UC 1-20)

| Query | ChromaDB Filter | Semantic Search |
|-------|----------------|-----------------|
| "Tell me about a conflict you handled" (UC 1,12) | `domain=career, type=star_story` | + semantic: "conflict resolution" |
| "Resume for this JD" (UC 2,6) | `domain=career, type IN [fact,metric,star_story]` | + semantic: JD text |
| "Salary history" (UC 3,63) | `domain IN [career,finance], tags CONTAINS salary` | + semantic: "compensation offer" |
| "Last 6 months achievements" (UC 4,11) | `domain=career, type=metric, date_start >= 2025-09` | + semantic: "achievement impact" |
| "Pending items with manager" (UC 5) | `domain=career, follow_up_status=pending, people CONTAINS manager_name` | |
| "Skills I have" (UC 7,88) | `domain IN [career,education], category=skill` | |
| "Career transitions" (UC 8,19) | `domain=career, type=event, tags CONTAINS role_change` | |
| "LinkedIn post ideas" (UC 9,166) | `domain IN [career,creativity], importance >= 3` | + semantic: "insight story" |
| "Conference contacts" (UC 13) | `domain=career, event_name != null, people != null` | |

### Relationships & Social (UC 21-40)

| Query | ChromaDB Filter |
|-------|----------------|
| "Mom birthday gift history" (UC 21,24) | `domain=relationships, people CONTAINS mom, item != null` |
| "Relationship with X over time" (UC 22,37) | `people CONTAINS X, date sorted` |
| "Recurring conflicts with partner" (UC 23) | `domain=relationships, pattern_id != null, sentiment=negative` |
| "Lost touch friends" (UC 25) | `domain=relationships, subdomain=lost_touch` |
| "Family dynamics" (UC 26) | `domain=relationships, subdomain=family` |
| "Who helped in crisis" (UC 28,230) | `domain IN [relationships,emergency], tags CONTAINS help` |
| "High energy friendships" (UC 29) | `domain=relationships, energy_level >= 4` |
| "Mentors" (UC 40) | `domain=relationships, relationships CONTAINS mentor, importance >= 4` |

### Health & Wellness (UC 41-60)

| Query | ChromaDB Filter |
|-------|----------------|
| "Headache history" (UC 41) | `domain=health, tags CONTAINS headache` |
| "Medical summary" (UC 42) | `domain=health, subdomain=medical` |
| "Anxiety triggers" (UC 45,49) | `domain=health, subdomain=mental, trigger != null` |
| "Medications taken" (UC 47) | `domain=health, tags CONTAINS medication` |
| "Fitness routines" (UC 48) | `domain=health, subdomain=fitness` |
| "Energy patterns" (UC 50) | `domain IN [health,daily_life], energy_level != null, time_of_day != null` |
| "Burnout signs" (UC 56) | `domain=health, tags CONTAINS burnout` |
| "Wellness experiments" (UC 57) | `domain=health, type=experiment, outcome != null` |

### Financial (UC 61-75)

| Query | ChromaDB Filter |
|-------|----------------|
| "Investment returns" (UC 62) | `domain=finance, subdomain=investment, monetary_value != null` |
| "Salary progression" (UC 63) | `domain IN [career,finance], tags CONTAINS salary, date sorted` |
| "Financial mistakes" (UC 64) | `domain=finance, type=lesson, sentiment=negative` |
| "Active loans" (UC 67) | `domain=finance, subdomain=loan, status=active` |
| "Subscriptions" (UC 69) | `domain=finance, subdomain=subscription, status=active` |
| "Negotiation wins" (UC 70) | `domain IN [career,finance], type=decision, tags CONTAINS negotiation, outcome != null` |

### Education & Learning (UC 76-90)

| Query | ChromaDB Filter |
|-------|----------------|
| "Book recommendations" (UC 77,213) | `type=review, medium=book, rating >= 4` |
| "Course reviews" (UC 82) | `type=review, medium=course, platform != null` |
| "Conference notes" (UC 85) | `domain=education, event_name != null` |
| "Skills learned" (UC 88) | `domain IN [education,career], category=skill, duration != null` |
| "My stance on topic X" (UC 90) | `domain IN [beliefs,education], tags CONTAINS topic_x` |

### Personal Growth (UC 91-110)

| Query | ChromaDB Filter |
|-------|----------------|
| "My strengths evidence" (UC 91) | `domain=personal_growth, sentiment=positive, type IN [lesson,reflection]` |
| "How I changed" (UC 92) | `domain=personal_growth, life_phase != null` + sort by date |
| "Emotional patterns" (UC 94) | `domain=personal_growth, emotion != null, trigger != null` |
| "Fears" (UC 96) | `domain=personal_growth, subdomain=fear` |
| "Coping mechanisms" (UC 100) | `domain=personal_growth, subdomain=coping, tags CONTAINS effectiveness` |
| "Therapy notes" (UC 110) | `domain=personal_growth, subdomain=therapy, source=conversation` |

### Decisions (UC 111-120)

| Query | ChromaDB Filter |
|-------|----------------|
| "Best/worst decisions" (UC 111) | `domain=decisions, type=decision, importance >= 4` |
| "Regrets" (UC 112) | `type=regret` |
| "Opportunity costs" (UC 113) | `domain=decisions, tags CONTAINS alternative` |
| "Risk tolerance" (UC 116) | `domain=decisions, tags CONTAINS risk, outcome != null` |
| "Decision frameworks used" (UC 120) | `domain=decisions, tags CONTAINS framework` |

### Daily Life & Productivity (UC 121-130)

| Query | ChromaDB Filter |
|-------|----------------|
| "Best morning routine" (UC 121) | `domain=daily_life, time_of_day=morning, type=habit` |
| "Productivity conditions" (UC 123,130) | `domain=daily_life, energy_level != null, environment != null` |
| "Tool reviews" (UC 124) | `domain=daily_life, type=review, item != null` |
| "Recipes" (UC 127) | `domain=daily_life, subdomain=cooking, type=review` |

### Goals (UC 131-140)

| Query | ChromaDB Filter |
|-------|----------------|
| "All goals" (UC 131-132) | `type=goal` |
| "Achieved goals" (UC 131,135) | `type=goal, status=completed` |
| "Abandoned goals lessons" (UC 139) | `type=goal, status=abandoned` |
| "New year resolutions" (UC 133) | `type=goal, tags CONTAINS resolution` |
| "Bucket list" (UC 135) | `type=goal, subdomain=bucket_list` |

### Beliefs & Values (UC 141-150)

| Query | ChromaDB Filter |
|-------|----------------|
| "Belief changes" (UC 141) | `type=belief, trigger != null` |
| "Political views" (UC 142) | `domain=beliefs, subdomain=politics` |
| "Ethical dilemmas" (UC 143) | `domain=beliefs, subdomain=ethics, type=decision` |
| "Influence map" (UC 148) | `domain=beliefs, people != null, importance >= 4` |
| "Life purpose" (UC 150) | `domain=beliefs, subdomain=philosophy, tags CONTAINS purpose` |

### Memories (UC 151-160)

| Query | ChromaDB Filter |
|-------|----------------|
| "Childhood memories" (UC 152) | `domain=memories, life_phase IN [early_childhood,childhood,school]` |
| "Travel memories" (UC 153) | `domain=memories, subdomain=travel, location != null` |
| "Turning points" (UC 157) | `domain=memories, subdomain=turning_point, importance >= 4` |
| "Proud moments" (UC 156) | `domain=memories, emotion=pride` |
| "Sensory memories" (UC 158) | `domain=memories, subdomain=sensory, tags CONTAINS smell/sound/taste` |

### Creativity (UC 161-170)

| Query | ChromaDB Filter |
|-------|----------------|
| "Ideas archive" (UC 161) | `domain=creativity, subdomain=ideas` |
| "Creative projects" (UC 162) | `domain=creativity, subdomain=side_project, status != null` |
| "Problem solving methods" (UC 169) | `domain=creativity, subdomain=innovation, outcome != null` |
| "Business ideas" (UC 168) | `domain=creativity, subdomain=ideas, tags CONTAINS business` |

### Communication (UC 171-180)

| Query | ChromaDB Filter |
|-------|----------------|
| "Public speaking" (UC 174,238) | `domain=communication, subdomain=speaking, event_name != null` |
| "Feedback received" (UC 178) | `domain=communication, subdomain=feedback, people != null` |
| "Difficult conversations" (UC 173) | `domain=communication, subdomain=conversation, resolution_status != null` |

### Legal & Administrative (UC 181-190)

| Query | ChromaDB Filter |
|-------|----------------|
| "Passport/document expiry" (UC 181) | `domain=legal, type=document_record, expiry_date != null` |
| "Insurance policies" (UC 184) | `domain=legal, subdomain=insurance` |
| "Visa history" (UC 188) | `domain=legal, subdomain=visa, country != null` |
| "Warranty tracking" (UC 185) | `domain=legal, subdomain=warranty, expiry_date != null, item != null` |
| "Address history" (UC 186) | `domain=legal, subdomain=property, location != null, date_start != null` |

### Family & Legacy (UC 191-200)

| Query | ChromaDB Filter |
|-------|----------------|
| "Family tree" (UC 191) | `domain=family, subdomain=tree, type=relationship_note` |
| "Family recipes" (UC 192) | `domain=family, subdomain=recipe` |
| "Parenting lessons" (UC 193) | `domain=family, subdomain=parenting, type=lesson` |
| "Family traditions" (UC 195) | `domain=family, subdomain=tradition, frequency != null` |
| "Family stories" (UC 200) | `domain=family, type IN [event,reflection], people != null` |

### Travel & Places (UC 201-210)

| Query | ChromaDB Filter |
|-------|----------------|
| "Trip reviews" (UC 201) | `domain=travel, subdomain=trip, rating != null` |
| "Restaurant reviews" (UC 202) | `domain=travel, subdomain=restaurant, rating != null, location != null` |
| "Local tips for city X" (UC 205) | `domain=travel, subdomain=local_tips, location CONTAINS X` |
| "Travel buddies" (UC 206) | `domain=travel, people != null, rating != null` |

### Entertainment (UC 211-220)

| Query | ChromaDB Filter |
|-------|----------------|
| "Movie recommendations" (UC 211) | `type=review, medium=movie, rating >= 4` |
| "Music for moods" (UC 212) | `type=preference, medium=music, emotion != null` |
| "Hobbies tried" (UC 217) | `domain=entertainment, subdomain=hobby, status != null` |
| "Food preferences" (UC 215) | `domain=entertainment, subdomain=food, type=preference` |

### Emergency & Crisis (UC 221-230)

| Query | ChromaDB Filter |
|-------|----------------|
| "Crisis playbook" (UC 221) | `domain=emergency, outcome != null` |
| "Emergency contacts" (UC 222) | `domain=emergency, type=document_record, people != null` |
| "Medical emergencies" (UC 225) | `domain=emergency, subdomain=medical_emergency, severity != null` |
| "Support system" (UC 230) | `domain=emergency, subdomain=support, people != null, importance >= 4` |

### Social & Digital (UC 231-240)

| Query | ChromaDB Filter |
|-------|----------------|
| "Online accounts" (UC 231) | `domain=social_digital, type=document_record, platform != null` |
| "Community involvement" (UC 236) | `domain=social_digital, subdomain=community, organization != null` |
| "Volunteering" (UC 237) | `domain=social_digital, subdomain=volunteering` |

### AI Replica & Meta (UC 241-260)

These are **consumption patterns** — they query data stored via the other 19 domains:

| Use Case | How It Works |
|----------|-------------|
| AI Twin (UC 241) | Aggregate `domain=communication` + `domain=career` + personality patterns |
| Personal FAQ (UC 242) | `type IN [fact,qa_pair], privacy IN [public,private]` |
| Journaling Prompts (UC 243) | Analyze gaps in recent `type=diary_entry` + suggest based on patterns |
| Life Dashboard (UC 244) | Aggregate all domains, group by `date_start`, compute trends |
| Coaching Bot (UC 247) | Full semantic search across all domains with `privacy` filtering |
| What-If Simulation (UC 249) | `type=decision` + `outcome` + `related_id` chain analysis |
| Growth Visualizer (UC 255) | Compare `type=metric` entries across time periods |
| Emotional Forecast (UC 257) | Pattern match `emotion` + `trigger` + `time_of_day` + calendar |
| Legacy Planning (UC 260) | `domain=social_digital` + `domain=legal` + `privacy=secret` planning docs |

---

## Technical Setup

### Prerequisites

```bash
pip install chromadb anthropic  # or openai for embeddings
```

### ChromaDB Initialization

```python
import chromadb
from chromadb.config import Settings

# Persistent storage
client = chromadb.PersistentClient(path="./life_brain_db")

# Create collection with cosine similarity (best for text embeddings)
collection = client.get_or_create_collection(
    name="life_brain",
    metadata={"hnsw:space": "cosine"}
)
```

### Adding a Document

```python
def add_to_life_brain(collection, doc_id, text, metadata):
    """Add one atomic knowledge unit to the life brain."""

    # Validate required fields
    required = ["domain", "subdomain", "type", "importance", "privacy", "source", "schema_version"]
    for field in required:
        assert field in metadata, f"Missing required field: {field}"

    # Validate enums
    assert metadata["privacy"] in ["public", "private", "confidential", "secret"]
    assert metadata["importance"] in [1, 2, 3, 4, 5]
    assert metadata["confidence"] in ["verified", "approximate", "uncertain", "subjective"] if "confidence" in metadata else True

    collection.upsert(
        ids=[doc_id],
        documents=[text],
        metadatas=[metadata]
    )

# Example usage
add_to_life_brain(
    collection,
    doc_id="career_project_20240715_crr-aml-problem_a3f2",
    text="""At American Express (Jul 2024-Present), as Senior Associate PM on the
    CRR AML Risk Scoring Engine project, I modernized a 12-year-old legacy system
    called Cadence. The core problem was that AML investigators spent 12-15 minutes
    per case because risk data was scattered across 6 different tools. We consolidated
    this into a single unified interface, reducing investigation time to under 4 minutes.""",
    metadata={
        "domain": "career",
        "subdomain": "project",
        "type": "qa_pair",
        "tags": "legacy_modernization,aml,risk_scoring,cadence",
        "date_start": "2024-07",
        "date_end": "present",
        "life_phase": "amex_era",
        "organization": "American Express",
        "role": "Senior Associate PM",
        "context": "work",
        "company": "amex",
        "project": "crr_aml",
        "category": "problem_definition",
        "importance": 5,
        "emotion": "pride",
        "sentiment": "positive",
        "privacy": "public",
        "confidence": "verified",
        "source": "interview",
        "schema_version": 1,
    }
)
```

### Querying

```python
def query_life_brain(collection, query_text, filters=None, n_results=10):
    """Semantic search with optional metadata filtering."""
    kwargs = {
        "query_texts": [query_text],
        "n_results": n_results,
        "include": ["documents", "metadatas", "distances"]
    }
    if filters:
        kwargs["where"] = filters

    return collection.query(**kwargs)

# Example: Interview prep for system design
results = query_life_brain(
    collection,
    query_text="Tell me about a system you designed from scratch",
    filters={
        "$and": [
            {"domain": "career"},
            {"type": {"$in": ["qa_pair", "star_story"]}},
            {"category": "solution_architecture"},
            {"privacy": {"$in": ["public", "private"]}}
        ]
    }
)

# Example: Anxiety triggers
results = query_life_brain(
    collection,
    query_text="What situations make me anxious?",
    filters={
        "$and": [
            {"domain": {"$in": ["health", "personal_growth"]}},
            {"emotion": "anxiety"}
        ]
    }
)

# Example: Life-defining decisions
results = query_life_brain(
    collection,
    query_text="major life decisions and their outcomes",
    filters={
        "$and": [
            {"type": "decision"},
            {"importance": {"$gte": 4}}
        ]
    }
)
```

---

## 260 Use Cases (Complete List)

### 1. Career & Professional (UC 1-20)
1. Interview Prep — "Tell me about a time you handled conflict" → instant STAR story retrieval
2. Resume Tailoring — Job description paste karo, relevant experiences auto-match
3. Salary Negotiation — Past offers, counteroffers, what worked, what didn't
4. Performance Review Prep — "Last 6 months me meri top achievements kya hain?"
5. 1:1 Meeting Prep — Past conversations with manager, pending topics, feedback received
6. Job Application Screening — "Kya mera experience match karta hai is JD se?"
7. Skill Gap Analysis — "Mujhe kya aata hai vs kya chahiye next role ke liye?"
8. Career Path Simulation — "Jab bhi maine role switch kiya, kya pattern tha?"
9. LinkedIn/Portfolio Content — Life experiences se engaging posts generate karo
10. Reference Request Prep — "X manager ke saath mera kya experience tha, kya bolenge mere baare me?"
11. Promotion Case Building — Auto-compile impact metrics, leadership examples, scope expansion
12. Workplace Conflict Resolution — "Pehle jab similar situation aayi thi, kya kiya tha?"
13. Networking Follow-up — "Iss conference me kisse mila tha, kya discuss kiya tha?"
14. Mentoring Others — "Jab main iss stage pe tha, mujhe kya help mili thi?"
15. Exit Interview Prep — "Iss company me meri journey ka honest summary kya hai?"
16. Work Anniversary Reflection — "1 year ho gaya, kya kya badla?"
17. Side Project Ideas — Past interests + skills + problems noticed → idea generation
18. Freelance Proposal Writing — Relevant past work auto-curate for proposals
19. Onboarding at New Job — "Pehle new jobs me mujhe kya mistakes kiye the, kya seekha?"
20. Managing Up — "Iss type ke manager ke saath kya strategy kaam karti hai mere liye?"

### 2. Relationships & Social (UC 21-40)
21. Birthday/Anniversary Reminders with Context — "Mom ko kya gift diya tha pichle saal? Kya pasand aaya?"
22. Relationship Health Check — "X ke saath last 6 months me interactions kaisi rahi?"
23. Conflict Pattern Recognition — "Partner ke saath baar baar same argument kyun hota hai?"
24. Gift Ideas — "Y ko kya pasand hai? Past me kya appreciate kiya unhone?"
25. Reconnecting with Lost Friends — "Z se last kab baat hui? Kya context tha?"
26. Understanding Family Dynamics — "Papa aur chacha ke beech kya history hai?"
27. Apology Prep — "Maine kya galat kiya tha? Kaise hurt hua tha wo?"
28. Who to Call for Help — "Jab pehle financial trouble aayi thi, kisne help kiya tha?"
29. Friend Compatibility — "Kinke saath mera energy level high rehta hai?"
30. Social Circle Mapping — "Mere life ke different phases me kaun kaun close tha?"
31. Breakup Processing — "Iss relationship me kya achha tha, kya toxic tha?"
32. Wedding/Event Planning — "Kisko invite karna hai? Kiska kya relation hai?"
33. Grief Processing — "Iss insaan ke saare memories ek jagah"
34. Parenting Decisions — "Mere parents ne kya kiya tha iss situation me? Kya effect hua mujh pe?"
35. Trust Assessment — "Iss insaan ne past me kitni baar promise toda?"
36. Conversation Starters — "X se milne wala hun, last time kya discuss kiya tha?"
37. Relationship Timeline — "Hamari friendship ki journey kya rahi hai year by year?"
38. Boundaries Documentation — "Kisne meri boundaries cross ki hain aur kab?"
39. Gratitude Practice — "Kiske liye grateful hun aur kyun?"
40. Mentors & Influences — "Kisne meri life me sabse zyada impact kiya?"

### 3. Health & Wellness (UC 41-60)
41. Symptom History — "Yeh headache pattern pehle bhi hua tha kya? Kab?"
42. Doctor Visit Prep — "Meri medical history ka summary de do"
43. Diet Pattern Analysis — "Jab healthy feel kiya, kya kha raha tha?"
44. Sleep Pattern Correlation — "Jab sleep kharab thi, life me kya chal raha tha?"
45. Mental Health Tracking — "Anxiety episodes ka pattern kya hai? Triggers kya hain?"
46. Therapy Session Prep — "Last session me kya discuss kiya tha? Kya homework mila tha?"
47. Medication History — "Kaunsi medicine kab li? Kya side effects the?"
48. Fitness Journey — "6 months pehle kya routine tha jab sabse fit feel kiya?"
49. Stress Trigger Mapping — "Kaunse situations mujhe consistently stress dete hain?"
50. Energy Level Patterns — "Hafte me kaunse din mera energy high rehta hai?"
51. Injury/Surgery Records — "Knee injury kab hui thi? Recovery me kitna time laga?"
52. Allergy & Intolerance Log — "Kya kya khane se problem hoti hai?"
53. Habit Formation Insights — "Pehle kaunsi habits successfully banayi? Kaise?"
54. Substance Use Tracking — "Caffeine/alcohol consumption patterns over time"
55. Emotional Eating Patterns — "Stress me kya cravings aati hain?"
56. Burnout Early Warning — "Pichli baar burnout hone se pehle kya signs the?"
57. Wellness Experiment Log — "Meditation try kiya tha 3 months — kya result aaya?"
58. Body Changes Timeline — "Weight/fitness changes with life events correlation"
59. Preventive Care Schedule — "Last dental checkup kab tha? Eye exam?"
60. Recovery Patterns — "Bimaar hone ke baad kya routine se jaldi theek hota hun?"

### 4. Financial (UC 61-75)
61. Spending Pattern Analysis — "Paise kahan jaate hain unconsciously?"
62. Investment Decision History — "Pehle kaunse investments kiye? Kya return aaya?"
63. Salary Progression — "Meri earning journey kya rahi hai year by year?"
64. Financial Mistake Learning — "Kaunsi financial galtiyan ki hain? Kya seekha?"
65. Tax Prep — "Iss year ke deductible expenses kya hain?"
66. Insurance Claim History — "Kab kab claim kiya? Kya process tha?"
67. Loan/EMI Tracking — "Kaunse loans liye? Kab khatam hue?"
68. Big Purchase Decision Support — "Pehle jab car/house liya tha, kya factors consider kiye?"
69. Subscription Audit — "Kya kya subscribe hai? Kya actually use karta hun?"
70. Negotiation Playbook — "Pehle jab negotiate kiya — rent, salary, deal — kya tactics kaam kiye?"
71. Emergency Fund Planning — "Past emergencies me kitna paisa laga?"
72. Generosity Log — "Kisne mujhe financially help kiya? Maine kisko?"
73. Side Income History — "Kya kya try kiya extra earn karne ke liye?"
74. Financial Goal Tracking — "5 saal pehle kya goals the? Kitne achieve hue?"
75. Rent/Housing History — "Kahan kahan raha? Kitna rent tha? Kya experience tha?"

### 5. Education & Learning (UC 76-90)
76. Learning Style Discovery — "Kaunse subjects me naturally achha tha? Kaise padha?"
77. Course/Book Recommendations — "Maine kya padha hai, kya pasand aaya, kya nahi"
78. Knowledge Gap Identification — "Kya kya seekhna chahta tha par kabhi seekha nahi?"
79. Study Strategy Optimization — "Exams me kab best perform kiya? Kya strategy thi?"
80. Certification Planning — "Kaunse certifications kiye? Kaunse pending hain?"
81. Book Notes Retrieval — "Us book me kya key insight thi?"
82. Tutorial/Course Review — "Yeh course achha tha ya time waste?"
83. Teacher/Professor Impact — "Kaunse teachers ne influence kiya? Kya seekhaya?"
84. Academic Achievement Timeline — "School se le ke ab tak ki academic journey"
85. Conference/Workshop Notes — "Us event me kya interesting tha?"
86. Podcast/Video Insights — "Kisi podcast me suni thi ek achhi baat... kya thi?"
87. Research Interest Mapping — "Kya topics me mera interest evolve hua time ke saath?"
88. Skill Acquisition Log — "Kaunsi skills seekhi? Kitna time laga? Kaise seekhi?"
89. Language Learning Journey — "Languages kab start ki? Kahan tak pahuncha?"
90. Debate/Argument Prep — "Iss topic pe meri knowledge aur stance kya hai?"

### 6. Personal Growth & Psychology (UC 91-110)
91. Self-Awareness Mapping — "Meri core strengths aur weaknesses kya hain based on evidence?"
92. Personality Evolution — "5 saal pehle kaisa tha vs ab? Kya badla?"
93. Cognitive Bias Detection — "Kya main baar baar same thinking mistake karta hun?"
94. Emotional Pattern Recognition — "Kaunsi situations me consistently kaunsa emotion aata hai?"
95. Values Clarification — "Mere actions se kya values reflect hoti hain vs kya claim karta hun?"
96. Fear Inventory — "Kya kya darr hai? Kab se? Kya basis hai?"
97. Comfort Zone Map — "Kya kya tha jo pehle uncomfortable tha par ab normal hai?"
98. Limiting Belief Identification — "Kaunsi beliefs mujhe rok rahi hain? Evidence kya hai?"
99. Peak Experience Analysis — "Life me kab sabse alive feel kiya? Common factors kya the?"
100. Coping Mechanism Inventory — "Stress me kya karta hun? Kya healthy hai kya nahi?"
101. Attachment Style Evidence — "Relationships me mera pattern kya hai?"
102. Communication Style Analysis — "Kaise communicate karta hun? Kya feedback aaya hai?"
103. Anger Trigger Map — "Kya cheezein mujhe trigger karti hain? Kyun?"
104. Procrastination Patterns — "Kya kaam taalte hain? Kab nahi taalte? Difference kya hai?"
105. Motivation Pattern — "Kya mujhe motivate karta hai consistently?"
106. Resilience Evidence — "Mushkil waqt me kaise recover kiya hai?"
107. Gratitude Journal Insights — "Long term me kis cheez ke liye sabse zyada grateful hun?"
108. Shadow Work — "Kya cheezein suppress karta hun? Kya patterns ignore karta hun?"
109. Life Philosophy Evolution — "Meri worldview kaise badli hai over the years?"
110. Therapy Insights Archive — "Therapist ne kya key observations diye?"

### 7. Decision Making (UC 111-120)
111. Decision Quality Audit — "Mere best decisions kaunse the? Worst? Kya common tha?"
112. Regret Analysis — "Kya regrets hain? Kya seekha unse?"
113. Opportunity Cost Tracking — "Jab X choose kiya Y ke upar, kya hua?"
114. Gut vs Logic Analysis — "Kab gut feeling follow ki? Kab logic? Kya better raha?"
115. Decision Fatigue Patterns — "Kab poor decisions karta hun? Time of day, stress level?"
116. Risk Tolerance Profile — "Kitna risk liya life me? Kya outcome aaya?"
117. Sunk Cost Fallacy Detection — "Kahan pe sirf isliye tika raha kyunki already invest kiya tha?"
118. Consensus vs Solo Decisions — "Kab doosron ki suni? Kab khud decide kiya? Kya better raha?"
119. Speed vs Quality Tradeoff — "Jab jaldi decide kiya vs soch ke — kya pattern hai?"
120. Decision Framework Library — "Kaunse frameworks use kiye hain past me decision ke liye?"

### 8. Daily Life & Productivity (UC 121-130)
121. Routine Optimization — "Kaunsi morning routine sabse productive feel karwa rahi thi?"
122. Time Audit — "Mera time kahan jaata hai actually?"
123. Productivity Pattern — "Kaunse din/time/environment me best kaam hota hai?"
124. Tool/App Review — "Kaunse tools try kiye? Kya tika? Kya chhoda?"
125. Errand/Task Patterns — "Recurring tasks ko kaise optimize kar sakta hun?"
126. Commute History — "Kahan se kahan travel kiya daily? Kya impact tha?"
127. Cooking/Meal Log — "Kya achha bana tha? Recipe kya thi?"
128. Home Improvement Log — "Ghar me kya kya fix/improve kiya? Kaise?"
129. Shopping Decisions — "Kaunse products liye? Review kya hai?"
130. Peak Performance Conditions — "Jab best kaam kiya, conditions kya thi? Music? Caffeine? Silence?"

### 9. Goals & Aspirations (UC 131-140)
131. Goal Archaeology — "10 saal pehle kya goals the? Kitne achieve kiye?"
132. Goal Setting Pattern — "Kaunse type ke goals achieve hote hain, kaunse nahi?"
133. New Year Resolution Audit — "Har saal kya resolve kiya? Kya hua?"
134. Dream Job Evolution — "Bachpan se le ke ab tak dream job kaise badla?"
135. Bucket List Tracking — "Kya kya karna hai? Kya ho chuka?"
136. Vision Board Evidence — "Manifest kiya tha kuch? Kya actually hua?"
137. 5-Year Plan Comparison — "5 saal pehle kya socha tha? Reality kya hai?"
138. Accountability Partner Data — "Kisne mujhe accountable rakha? Kya kaam kiya?"
139. Abandoned Goals Lessons — "Kya chhoda? Kyun? Kya seekha?"
140. Goal Conflict Detection — "Kya mere goals ek doosre ke against hain?"

### 10. Beliefs, Values & Philosophy (UC 141-150)
141. Belief Change Log — "Kya beliefs badli hain? Kyun? Kya trigger tha?"
142. Political Evolution — "Meri political views kaise evolve hui?"
143. Ethical Dilemma Archive — "Kab moral dilemma aaya? Kya choose kiya? Kyun?"
144. Cultural Identity Mapping — "Kaunse cultural values important hain? Kyun?"
145. Spiritual Journey — "Spirituality ke saath mera relationship kya raha hai over time?"
146. Worldview Debates — "Kaunse topics pe strongly opinionated hun? Evidence kya hai?"
147. Hypocrisy Detection — "Kahan pe meri values aur actions mismatch karte hain?"
148. Influence Map — "Kaunsi books/people/events ne meri soch badli?"
149. Death/Legacy Reflection — "Kya yaad rakha jaana chahta hun? Kya chhodna chahta hun?"
150. Meaning Making — "Life ka purpose kya hai? Yeh answer kaise evolve hua?"

### 11. Memories & Experiences (UC 151-160)
151. Memory Preservation — "Fading memories ko capture karna before they're lost"
152. Childhood Reconstruction — "Bachpan ki yaadein — school, friends, family"
153. Travel Diary — "Kahan gaya? Kya dekha? Kya feel kiya?"
154. First Time Experiences — "Pehli baar kab kya kiya? Kya feel hua?"
155. Embarrassing Moments — "Kya kya embarrassing hua? (Growth ke liye useful)"
156. Proud Moments Timeline — "Kab kab proud feel kiya?"
157. Turning Points — "Life ke kaunse moments ne direction change kiya?"
158. Sensory Memories — "Kaunsi smell/song/taste kya yaad dilati hai?"
159. Cultural Experiences — "Different cultures se kya seekha?"
160. Nostalgic Triggers — "Kya cheezein nostalgia trigger karti hain? Kyun?"

### 12. Creativity & Ideas (UC 161-170)
161. Idea Archive — "Random ideas jo aaye the kisi din — retrieve karo"
162. Creative Project Log — "Kya kya creative kaam kiya? Status kya hai?"
163. Writing Prompts from Life — "Meri experiences se kaunse stories ban sakte hain?"
164. Pattern Connection — "Do unrelated experiences me kya common thread hai?"
165. Innovation Methodology — "Pehle kab creative solution nikala tha? Kaise?"
166. Content Calendar — "Kaunsi life stories share worthy hain?"
167. Analogy Library — "Kaunsi real-life analogies use ki hain explain karne ke liye?"
168. Business Idea Validation — "Past experience se kaunsa business idea make sense karta hai?"
169. Problem Solving Patterns — "Tough problems kaise solve kiye hain historically?"
170. Inspiration Sources — "Kya inspire karta hai mujhe? Pattern kya hai?"

### 13. Communication & Expression (UC 171-180)
171. Writing Style Evolution — "Meri writing kaise badli hai over the years?"
172. Presentation Prep — "Iss topic pe mera real experience kya hai? Stories kya hain?"
173. Difficult Conversation Prep — "Pehle similar conversation kaise handle ki thi?"
174. Public Speaking Notes — "Kaunse talks diye? Kya feedback aaya?"
175. Email/Message Templates — "Iss type ki situation me pehle kya likha tha?"
176. Storytelling Arsenal — "Dinner party ke liye meri best stories kaunsi hain?"
177. Humor Log — "Kaunsi funny incidents hui hain?"
178. Feedback Received Archive — "Logo ne mere baare me kya kaha hai over time?"
179. Persuasion Playbook — "Kab kisi ko successfully convince kiya? Kaise?"
180. Language & Vocabulary — "Kaunse words/phrases main often use karta hun?"

### 14. Legal & Administrative (UC 181-190)
181. Document Locator — "Passport kab expire hota hai? Kahan rakha hai?"
182. Contract History — "Kaunse agreements sign kiye? Key terms kya the?"
183. Dispute Resolution Log — "Kab kab legal/formal dispute hua? Kya hua?"
184. Insurance Details — "Kaunsi policies hain? Coverage kya hai?"
185. Warranty Tracking — "Kaunse products ka warranty abhi valid hai?"
186. Address History — "Kahan kahan raha? Dates kya hain?"
187. Complaint Log — "Kab kab complaint ki? Kya resolution mila?"
188. Visa/Immigration History — "Kaunse countries ke visa liye? Status kya hai?"
189. Vehicle History — "Kaunsi gaadi kab li? Kab bechi? Kya issues aaye?"
190. Property Records — "Real estate transactions ka history"

### 15. Family & Legacy (UC 191-200)
191. Family Tree Knowledge — "Parivar ka itihaas — kaun kahan se aaya?"
192. Family Recipe Archive — "Dadi ki recipe kya thi? Mom kaise banati hai?"
193. Parenting Playbook — "Mere parents ne kya kiya achha/bura? Main kya differently karunga?"
194. Inheritance & Will Planning — "Kya kisko milna chahiye? Kyun?"
195. Family Tradition Log — "Kaunsi traditions hain? Unka kya significance hai?"
196. Generational Pattern Recognition — "Kaunse patterns family me repeat hote hain?"
197. Family Conflict History — "Kaunse unresolved issues hain? Context kya hai?"
198. Children's Milestones — "Bacche ka pehla word, pehla step, pehli achievement"
199. Elder Care Notes — "Parents ki health history, preferences, needs"
200. Family Stories Archive — "Dadaji ki woh kahani jo unhone sunai thi..."

### 16. Travel & Places (UC 201-210)
201. Trip Planning from Experience — "Pehle jab Goa gaya tha, kya achha tha kya nahi?"
202. Restaurant/Cafe Reviews — "Best places kahan khaya? Kya order kiya?"
203. Hotel/Stay Reviews — "Kahan ruka? Kya experience tha?"
204. Packing List Optimization — "Pichli trips me kya bhool gaya tha?"
205. Local Tips Archive — "Har city ke liye insider tips jo discover kiye"
206. Travel Buddy Compatibility — "Kiske saath travel kiya? Kya experience tha?"
207. Migration/Relocation History — "Kab kahan shift hua? Kya challenges aaye?"
208. Commute Optimization — "Different routes/modes try kiye, kya best hai?"
209. Favorite Places Map — "Duniya me kaunsi jagah sabse achhi lagi? Kyun?"
210. Cultural Shock Log — "Naye sheher/desh me kya adjust karna pada?"

### 17. Entertainment & Preferences (UC 211-220)
211. Movie/Show Recommendations — "Mujhe kya pasand hai? Similar kya dekh sakta hun?"
212. Music Mood Mapping — "Kaunsa music kab sunna chahiye based on mood?"
213. Book Reading Journey — "Kya padha? Kya impact hua? Kya recommend karunga?"
214. Game History — "Kaunse games khele? Kya achha laga?"
215. Food Preferences Evolution — "Kya pasand badla hai over time?"
216. Fashion/Style Log — "Kya pehnna comfortable hai? Kya compliments aaye?"
217. Hobby Timeline — "Kaunse hobbies try kiye? Kya tika?"
218. Sports Following — "Kaunsi teams support karta hun? Key moments kya the?"
219. Art Appreciation Log — "Kaunsi art/music/film ne deeply move kiya?"
220. Guilty Pleasures — "Kya secretly enjoy karta hun?"

### 18. Emergency & Crisis (UC 221-230)
221. Crisis Playbook — "Pehle jab emergency aayi, kya kiya? Kya kaam kiya?"
222. Emergency Contacts with Context — "Kis situation me kisko call karna hai?"
223. Disaster Recovery — "Data loss, theft, accident — pehle kaise handle kiya?"
224. Insurance Claim Playbook — "Pehle claim kaise kiya tha? Process kya tha?"
225. Medical Emergency History — "Kab kab hospital jaana pada? Kya hua?"
226. Financial Crisis Survival — "Tight budget wale time me kaise manage kiya?"
227. Mental Health Crisis Protocol — "Darkest moments me kya help kiya?"
228. Backup & Recovery Log — "Important data kahan backed up hai?"
229. Near Miss Archive — "Kab baal baal bacha? Kya lesson mila?"
230. Support System Map — "Crisis me kaun reliable hai? Evidence kya hai?"

### 19. Social & Digital Identity (UC 231-240)
231. Online Presence Audit — "Kahan kahan accounts hain? Kya posted hai?"
232. Digital Footprint Awareness — "Public me kya available hai mere baare me?"
233. Password/Account Recovery — "Kaunse security questions set kiye the?"
234. Social Media Impact Analysis — "Social media ka mujh pe kya effect hai?"
235. Online Reputation Management — "Kya hai jo delete/edit karna chahiye?"
236. Community Involvement Log — "Kaunse communities me active hun/tha?"
237. Volunteering History — "Kya social work kiya? Impact kya tha?"
238. Public Speaking/Appearances — "Kab kab publicly appear hua?"
239. Troll/Harassment Log — "Kab online harassment hua? Kaise handle kiya?"
240. Influence & Following — "Kisko follow karta hun? Kyun?"

### 20. AI Replica & Meta Use Cases (UC 241-260)
241. AI Twin for Meetings — "Meri jagah AI attend kare, meri style me respond kare"
242. Personal FAQ Bot — "Naye log mujhse common questions poochte hain — AI answer kare"
243. Automated Journaling Prompts — "Based on past patterns, aaj kya reflect karna chahiye?"
244. Life Pattern Dashboard — "Meri life ka bird's eye view — trends, patterns, cycles"
245. Time Capsule Creation — "Future self ke liye messages based on current state"
246. Memoir Draft Generation — "Autobiography ka first draft from life data"
247. Coaching Bot — "Meri history jaane wala AI coach jo personalized advice de"
248. Compatibility Matching — "Kya main iss person/role/city ke saath compatible hun based on patterns?"
249. What-If Simulations — "Agar us din woh decision different liya hota toh kya hota?"
250. Deathbed Letter Generator — "Important logo ke liye letters based on relationship history"
251. Daily Briefing — "Aaj kya relevant hai past se? Anniversary, lesson, reminder?"
252. Conversation Simulator — "Iss person se baat karni hai — practice karo mere data se"
253. Argument Strengthener — "Mera stance X hai — mere life se evidence do"
254. Contradiction Detector — "Kya main hypocrite hun? Kahan values vs actions clash?"
255. Growth Visualizer — "5 saal pehle vs aaj — kya kya improve hua quantifiably?"
256. Habit Recommender — "Mere patterns ke basis pe, mujhe kya habit start karni chahiye?"
257. Emotional Weather Forecast — "Based on patterns, iss week stress aane wala hai — prep karo"
258. Life Satisfaction Score — "Different domains me meri satisfaction ka trend kya hai?"
259. Unfinished Business Tracker — "Kya kya incomplete chhoda hai? Kya closure chahiye?"
260. Legacy Planning — "Meri digital presence mere baad kaise managed ho?"

---

## Summary

| Aspect | Decision |
|--------|----------|
| Collections | 1 collection (`life_brain`). New only for different modality/scale/access |
| Metadata fields | 47 fields: 24 core + 23 extended. Domain-specific in `tags` until volume justifies promotion |
| Required fields | 7: domain, subdomain, type, importance, privacy, source, schema_version |
| Schema evolution | Version field + LLM backfill script. Text is source of truth, metadata is index |
| Document format | Self-contained text, one atomic knowledge unit per document, 300-1500 chars |
| Privacy | 4-tier: public → private → confidential → secret |
| Use cases covered | 260 across 20 life domains |
| Chunking | One fact/story/Q&A per doc. Linked via related_id and pattern_id |
| ID format | `{domain}_{subdomain}_{date}_{slug}_{hash}` |
