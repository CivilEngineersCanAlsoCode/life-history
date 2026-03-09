# Fundamental Assessment (FA) Overview

## What is Fundamental Assessment?

**Fundamental Assessment (FA)** is a system for pre-scoring customer attributes based on inherent risk characteristics. FA scores are used as multipliers in CRR rules.

---

## The 6 FA Gates

| Gate Code | Gate Name | What It Scores |
|-----------|-----------|----------------|
| **GR** | Geography | Countries and geographic regions |
| **IR** | Industry | Industry/sector classifications |
| **PRR** | Product | Product types and services |
| **OCCP** | Occupation | Customer occupations |
| **ACR** | Acquisition Channel | How customer was acquired |
| **SR** | Structure | Entity/legal structure type |

---

## FA Scoring Mechanism

### Question-Based Scoring

Each FA attribute (e.g., a specific country) is scored based on **10 questions** ranked by priority.

```
Questions (Ranked 1-10 by Priority):
┌────┬──────────────────────────────────────────────────────────┬─────────┐
│ Rank│ Question                                                 │ Answer  │
├────┼──────────────────────────────────────────────────────────┼─────────┤
│ 10 │ Is this a sanctioned country?                            │ NO      │
│  9 │ Is this on FATF blacklist?                                │ NO      │
│  8 │ Is this a known tax haven?                                │ YES ←── │
│  7 │ Does this have weak AML regulations?                      │ YES     │
│  6 │ Is this an emerging market?                               │ YES     │
│  5 │ Does this have political instability?                     │ NO      │
│  4 │ Limited correspondent banking?                            │ NO      │
│  3 │ High corruption index?                                    │ YES     │
│  2 │ Limited regulatory enforcement?                           │ NO      │
│  1 │ Other minor concerns?                                     │ YES     │
└────┴──────────────────────────────────────────────────────────┴─────────┘

SCORE = Highest ranked question with "YES" answer = 8
```

### Score Calculation Rule
> **FA Score = Rank of the highest-ranked question answered "YES"**

| If Highest YES is at Rank | Score |
|---------------------------|-------|
| Rank 10 | 10 (Prohibited) |
| Rank 8 | 8 |
| Rank 5 | 5 |
| No YES answers | 1 (Lowest risk) |

---

## Score Ranges

| Score | Risk Level | Business Action |
|-------|------------|-----------------|
| 1-3 | Low | Standard processing |
| 4-6 | Medium | Enhanced monitoring |
| 7-9 | High | Enhanced due diligence |
| 10 | Prohibited | Cannot onboard |

---

## FA in Rules

### FA as Multiplier

When creating a rule with FA-based multiplier:

```
Rule: If Customer_Country IN High_Risk_Countries THEN use FA(GR) score

Example:
- Customer country = Iran
- Iran's FA(GR) score = 10
- Rule contribution = 10x (multiplier)
```

### Current Score vs New Score

| Term | Meaning |
|------|---------|
| **Current Score** | FA score from last promoted production |
| **New Score** | FA score being edited in current sandbox |

The **New Score** becomes **Current Score** after sandbox promotion.

---

## FA Overrides

### What is an Override?

A market can **override** the Enterprise FA score for a specific attribute.

### Example
| Attribute | Gate | Enterprise Score | India Override |
|-----------|------|------------------|----------------|
| Casino | Industry (IR) | 6 | 8 |
| Online Gaming | Industry (IR) | 5 | 7 |

**Why?** India considers these industries higher risk than Enterprise baseline.

### Override Rules
- Override applies only to the market that sets it
- Enterprise score remains unchanged for other markets
- Override score is used in that market's calculations

---

## FA Workflow

### Editing FA Scores

1. User opens Sandbox → Fundamental Assessment tab
2. Selects gate (e.g., Geography)
3. Selects attribute (e.g., Iran)
4. Answers the 10 questions
5. System calculates new score
6. New score is visible but not yet active
7. On sandbox promotion, new scores become current

### FA Score Change Without Rule Change

If ONLY FA scores change (no rule logic changes):
- Simulation **can be skipped**
- Still requires two-level approval

---

## FA Tables Reference

| Table | Purpose |
|-------|---------|
| `ira_gate_type` | 6 gate types |
| `ira_gate` | Gate instances |
| `inhrnt_risk_assess` | Calculated scores |
| `ira_ques_resp` | Question answers |
| `ira_risk_score_ovrrd` | Market overrides |

*For full schema, see `08_Data_Model/CRR_Complete_Data_Model.md`*

---

*Next: See `02_FA_Gates_Detail.md` for each gate's attributes.*
*Next: See `03_FA_Override_Rules.md` for override configuration.*
