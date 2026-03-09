# Knowledge Organization Guide

How to name, tag, and maintain knowledge in the Life Brain system.
Follow these conventions so search always works well.

---

## 1. Naming Conventions

### Files

```
Format: [YYYY-MM-DD]-[type]-[subject].md
Examples:
  2024-03-09-star-cgb-launch.md
  2024-01-15-metrics-aml-risk-engine.md
  2023-09-01-decision-amex-offer.md
```

### Document IDs (ChromaDB)

```
Format: [company_short]-[project]-[type]-[YYYYMM]-[seq]
Examples:
  spr-cgb-metric-202309-001    → Sprinklr CGB metric Sept 2023 first entry
  amx-aml-story-202407-003    → Amex AML STAR story July 2024 third entry
  personal-finance-fact-202401-001
```

**Company short codes:**
- `spr` → Sprinklr
- `amx` → American Express
- `pers` → Personal (non-work)

---

## 2. Metadata Tagging Schema

Every document **must** have these fields:

```python
{
    # REQUIRED — always set these
    "atom_type": str,     # fact|metric|story|decision|lesson|belief|memory|goal
    "domain": str,        # career|finance|health|relationships|personal_growth|memory|creativity
    "date": str,          # YYYY-MM-DD (most specific date possible)
    "privacy": str,       # private|team|public

    # REQUIRED for career atoms
    "company": str,       # "Sprinklr" | "American Express" | etc (canonical name)
    "project": str,       # Project name (e.g., "CGB", "AML Risk Scoring Engine")

    # RECOMMENDED — improves search precision
    "category": str,      # Subcategory within domain (see table below)
    "confidence": float,  # 0.0-1.0 (how certain are you this is accurate?)
    "source": str,        # Where you got this: confluence|memory|document|interview

    # OPTIONAL
    "role": str,          # Your role when this happened (PM|Engineer|etc)
    "tags": str,          # Comma-separated: "leadership,conflict,milestone"
}
```

### Category Values by Domain

| Domain | Valid Categories |
|--------|----------------|
| career | product_metrics, team_metrics, technical, process, leadership, stakeholder, growth |
| finance | income, savings, investment, expense, tax, property |
| health | fitness, nutrition, sleep, mental_health, medical |
| relationships | romantic, friendship, family, professional, conflict |
| personal_growth | habit, belief, learning, identity, values |
| memory | childhood, travel, milestone, relationship_moment |
| creativity | writing, design, music, side_project |

---

## 3. Atom Type Guidelines

Choose the right atom type — it determines how search ranks and conflict-checks:

| Atom Type | Use When | Example |
|-----------|---------|---------|
| `fact` | Verifiable statement about what happened | "CGB launched in September 2023" |
| `metric` | Quantitative measurement with number | "CGB CSAT reached 94% in Q3 2023" |
| `story` | STAR-format experience narrative | "Led CGB launch with 3-person team in 6 weeks" |
| `decision` | A choice you made with context | "Chose to accept Amex offer over startup option" |
| `lesson` | Something you learned from an experience | "Always involve ops in product launch planning" |
| `belief` | Core principle or value | "Feedback loops are the most important team habit" |
| `memory` | Episodic personal memory | "First day at Sprinklr — overwhelmed but excited" |
| `goal` | Future aspiration with timeline | "PM role at product-led company by 2027" |

---

## 4. Search Best Practices

### What works well

```python
# Specific + domain filtered
search("CGB CSAT metrics", domain="career", company="Sprinklr")

# Role + company
search("leadership challenges at American Express")

# Type-specific
search("salary decisions", atom_type="decision")

# Time-bounded
search("Q3 2023 achievements")
```

### What to avoid

```python
# Too vague — will return everything
search("work")
search("good stuff")

# Typos in company names — use canonical names
search("amrican express metrics")   # ✗ Will miss results
search("American Express metrics")  # ✓
```

### Expanding searches when results are poor

1. Remove one filter at a time (start with `company`, then `domain`)
2. Try alternate phrasings: "leadership" vs "management" vs "team lead"
3. Use Life Brain's alt phrasing: `alt_question_store.get_alternatives("your query")`
4. Use two-pass search for metrics — it finds structural matches too

---

## 5. Privacy Guidelines

| Level | Rule | Example |
|-------|------|---------|
| `private` | Never share with any AI/external service | Personal health data, family conflicts, financial details |
| `team` | OK for work queries, not personal | Project architectures, team dynamics |
| `public` | Safe in any context | Publicly known achievements, general career timeline |

**Default everything to `private`.** Upgrade deliberately.

**Never store:**
- Passwords, tokens, API keys
- Others' private information without consent
- Health diagnoses with names attached

---

## 6. Confidence Levels

| Score | Meaning | Use When |
|-------|---------|---------|
| 0.95–1.0 | Verified, documented | You have written proof (document, email) |
| 0.8–0.94 | High confidence | Strong memory + corroborating details |
| 0.6–0.79 | Medium confidence | General memory, no documentation |
| 0.4–0.59 | Low confidence | Vague recollection or second-hand |
| < 0.4 | Uncertain | Tag as needs_verification = true |

---

## 7. Maintenance Schedule

### Weekly
- [ ] Process passive capture queue: `engine.get_weekly_review()`
- [ ] Add new facts from week's significant events

### Monthly
- [ ] Update metric snapshots for active projects
- [ ] Review staleness alerts (finance domain: 365-day window)
- [ ] Archive completed goals (update status to "achieved" or "abandoned")

### Quarterly
- [ ] Full backup: `exporter.export_to_file("backup_YYYYQQ.json")`
- [ ] Review `health` domain atoms (180-day expiry)
- [ ] Update STAR stories with latest metrics

### Annually
- [ ] Career domain review (730-day expiry window for career atoms)
- [ ] Update identity/belief atoms — do they still reflect who you are?
- [ ] Review and prune obsolete facts (tech stack knowledge, old contacts)

---

## 8. Folder Structure Reference

```
context/                    ← READ-ONLY reference templates (this folder)
├── ORGANIZATION.md         ← This file
├── interview-prep/
│   ├── behavioral-questions.md
│   ├── star-story-checklist.md
│   └── technical-questions-index.md  (add as needed)
└── templates/
    ├── project-analysis-15q.md
    ├── metrics-tracking.md
    └── stakeholder-analysis.md       (add as needed)

docs/                       ← System documentation
├── configuration-guide.md
├── troubleshooting-guide.md
└── noob-onboarding.md

career history/             ← Your actual career content (edit freely)
life_brain/                 ← System code (edit only via code contributions)
```

---

## 9. Quick Reference: What to Add After Key Events

| Event | What to Add | Atom Type | Domain |
|-------|-------------|-----------|--------|
| Got promoted | Announcement + new responsibilities | fact | career |
| Project shipped | Launch metrics, team, timeline | metric + story | career |
| Job offer received | Offer details, decision factors | decision | career |
| Had difficult 1:1 | What was said, what you decided | lesson | career |
| Investment made | Amount, vehicle, thesis | fact | finance |
| Had health insight | What changed in your routine | lesson | health |
| Relationship milestone | What happened, what it meant | memory | relationships |
| Learned something big | What, how, application | lesson | personal_growth |
| Made a big decision | Options considered, why you chose | decision | personal_growth |
