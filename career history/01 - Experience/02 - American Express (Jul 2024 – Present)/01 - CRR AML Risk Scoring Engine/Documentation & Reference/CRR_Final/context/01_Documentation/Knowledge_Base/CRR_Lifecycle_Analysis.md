# CRR Complete Lifecycle Analysis
## Unified Sandbox, Asset Manager & Edge Cases

**Document Version:** 1.0 (Structured Analysis)
**Created:** 2026-01-21
**Purpose:** Consolidate all confirmed understanding, open questions, and edge cases for CRR lifecycle in a structured format for decision making.

---

# PART 1: WHAT I UNDERSTOOD ✅

## 1.1 Core System Architecture

### CRR Hierarchy
```
Risk Framework (Enterprise/Market scoped)
  └── Risk Categories (5 total)
        ├── Customer
        ├── Geography  
        ├── Transactions
        ├── Products & Services
        └── ARFs & HROs
              └── Risk Elements
                    └── Rulesets
                          └── Rules (Datapoint + Operator + Value/Asset)
```

### Scope Model
| Scope Code | Meaning | Example |
|------------|---------|---------|
| `XX` | Enterprise (Global) | Common rules for all markets |
| `IN` | India Market | India-specific localizations |
| `BE` | Belgium Market | Belgium-specific localizations |
| `GE` | Germany Market | Germany-specific localizations |

---

## 1.2 Sandbox Lifecycle (Confirmed)

### State Machine
```
                    ┌─────────────┐
                    │   WORKING   │ ← Sandbox Draft (edits allowed)
                    └──────┬──────┘
                           │ Submit (comment mandatory)
                    ┌──────▼──────┐
                    │ SUBMISSION  │
                    │ IN PROGRESS │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
        Cancel ────►│ IN_PROGRESS │ (Simulation running)
           │        └──────┬──────┘
           │               │
    ┌──────▼──────┐ ┌──────▼──────┐
    │  CANCELLED  │ │ TESTING     │
    │             │ │ COMPLETED   │
    └──────┬──────┘ └──────┬──────┘
           │               │
           │        ┌──────▼──────┐
           │        │ View Results│
           │        └──┬───────┬──┘
           │       No  │       │ Yes (Implement)
           │    ┌──────▼───┐   │
           │    │ CREATE   │   │
           │    │ NEW VER  │   │
           │    │ or       │   │
           │    │ ROLLBACK │   │
           │    └──────┬───┘   │
           │           │       │
           └───────────┴───────┤
                               │
                    ┌──────────▼──────────┐
                    │ PENDING_APPROVAL_1  │
                    └──────────┬──────────┘
                      Reject   │   Approve
                    ┌──────────┼──────────┐
                    │          │          │
             ┌──────▼──────┐   │   ┌──────▼──────────┐
             │  REJECTED   │   │   │PENDING_APPROVAL_2│
             └──────┬──────┘   │   └──────┬──────────┘
                    │          │   Reject │   Approve
                    │          │   ┌──────┼──────┐
                    └──────────┴───►      │      │
                                   ┌──────▼──┐ ┌─▼──────────┐
                                   │REJECTED │ │ PRODUCTION │
                                   └─────────┘ │  (Merged)  │
                                               └────────────┘
```

### Key Rules
- **Version Cap:** Maximum 10 versions per sandbox
- **After Cap:** Must archive/delete sandbox and create new
- **Comments:** Mandatory at each state transition
- **History:** All transitions logged with ECN, Username, Timestamp, Version, Status, Comments

---

## 1.3 Asset Lifecycle (Confirmed)

### Asset Status Flow
```
DRAFT ──────► SANDBOX ──────► PRODUCTION ──────► DEPRECATED
  │              │                  │
  │              │                  └── When newer version promoted
  │              │
  │              └── When linked to ruleset in sandbox
  │
  └── Newly created, not linked anywhere
```

### Editability Matrix ✅
| Sandbox Type | Asset Status | Used By | Editable? | Action |
|--------------|--------------|---------|-----------|--------|
| Enterprise | Any | Any | ✅ YES | Versioning |
| Market | DRAFT | - | ✅ YES | Inline update |
| Market | SANDBOX/PROD | This market only | ✅ YES | Versioning |
| Market | SANDBOX/PROD | Multiple markets | ❌ NO | Must Copy |
| Market | SANDBOX/PROD | Enterprise | ❌ NO | Must Copy |
| Any (non-Draft state) | Any | - | ❌ NO | View only |

### Versioning Semantics ✅
```
Production: A1 V1
    │
    ▼ User edits in sandbox (FIRST time)
Sandbox: A1 V2 created (once)
    │
    ▼ User makes more changes (before submit)
Sandbox: A1 V2 updated INLINE (no new version)
    │
    ▼ User submits for simulation
Sandbox: A1 V2 FROZEN, mapped to sandbox version
    │
    ▼ Next edit after submit
Sandbox: A1 V3 created
```

---

## 1.4 Localisation Flow (Confirmed)

### When Market Edits Enterprise Ruleset
```
Enterprise Risk Element (Scope XX)
  └── Ruleset 1 (XX)
  └── Ruleset 2 (XX)
  └── Ruleset 3 (XX)

User in India sandbox clicks EDIT on Ruleset 2
    │
    ▼ System triggers LOCALISATION
    
Creates:
  India Risk Element (Scope IN)
    └── Ruleset 1 (IN) ← Copy
    └── Ruleset 2 (IN) ← Copy + User's edit
    └── Ruleset 3 (IN) ← Copy

Original XX Risk Element UNCHANGED
```

### Rule Execution Priority
```
If Belgium assessment runs:
  1. Check for BE-scoped risk elements → Use if found
  2. If not found → Use XX-scoped risk elements
  
Localised rules ALWAYS take precedence over enterprise
```

---

## 1.5 Concurrent Edit Handling (Confirmed)

### Optimistic Locking
```
User X opens edit at T1 (version_no = 5)
User Y opens edit at T2 (version_no = 5)
User Y saves at T3 → Success (version_no = 6)
User X saves at T4 → FAILS (version mismatch: expected 5, found 6)
```

### Conflict Resolution UI
```
┌─────────────────────────────────────────────────────┐
│            CONFLICT DETECTED                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────┐    ┌─────────────────┐        │
│  │ YOUR CHANGES    │    │ CURRENT STATE   │        │
│  ├─────────────────┤    ├─────────────────┤        │
│  │ Added: [A, B]   │    │ Added: [C, D]   │        │
│  │ Removed: [X]    │    │ Removed: []     │        │
│  └─────────────────┘    └─────────────────┘        │
│                                                     │
│  [MERGE]    [OVERWRITE]    [RELOAD]                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 1.6 Simulation & Promotion (Confirmed)

### Simulation Rules
- **Delta Execution:** Only runs CHANGED risk elements
- **Isolation:** Uses COPIED rules in sandbox (not production at runtime)
- **Scope:** Pulls unchanged rules from production for complete scoring

### Atomic Promotion
- Rules + Assets + Fundamental Assessment promoted TOGETHER
- Partial promotion NOT allowed
- All components must be approved as one change set

---

## 1.7 Refresh/Rebase (Confirmed)

### Scenario
```
T1: India sandbox created from Production P1
    └── Copies baseline config from P1
    
T2: Enterprise updates production to P2
    └── India sandbox is now STALE
    
T3: India tries to refresh
    └── System compares: India changes vs P1→P2 diff
    └── Detects conflicts
    └── User resolves: Keep Mine / Take Theirs / Manual Merge
```

### Key Behavior
- **Manual Refresh Required:** Markets must explicitly refresh to get enterprise updates
- **No Auto-Propagation:** Prevents surprise breaking changes mid-work
- **UI Indicator:** Stale sandbox badge shown when production advanced

---

# PART 2: CONFIRMED ANSWERS ✅

## From Your Responses (FQ1-FQ6)

### FQ1: Sandbox Version Cap Handling
| Question | Answer |
|----------|--------|
| Do asset versions carry over to new sandbox? | ✅ YES |
| New sandbox base from? | Latest version of each component |
| Archived sandbox accessible? | Yes, read-only for history/rollback |
| Asset status when sandbox archived? | Stays SANDBOX (orphaned) |

### FQ2: Concurrent Edit Conflict Detection
| Question | Answer |
|----------|--------|
| Detection mechanism? | `version_no` column (optimistic locking) |
| Different fields = no conflict? | NO - entire row is atomic unit |
| Show diff? | Yes, side-by-side comparison |
| Resolution options? | Merge / Overwrite / Reload |

### FQ3: Asset Unlinking Mid-Edit Protection
| Question | Answer |
|----------|--------|
| Re-check on SAVE? | ✅ YES |
| If became exclusive? | Edit succeeds as inline update |
| If still shared? | Original BLOCK applies |
| If became DRAFT? | Edit succeeds (DRAFT allows inline) |

### FQ4: Enterprise Edit Impact on Markets
| Question | Answer |
|----------|--------|
| Auto-propagate? | ❌ NO |
| Manual refresh required? | ✅ YES |
| UI indicator? | Stale sandbox badge |

### FQ5: Scoring Engine - Copied vs Production Rules
| Question | Answer |
|----------|--------|
| Which approach? | Uses COPIED rules in sandbox |
| Why? | Fully isolated, production changes don't affect |
| Trade-off? | Storage overhead accepted |

### FQ6: Archive Cleanup & Asset Status
| Question | Answer |
|----------|--------|
| SANDBOX-only assets? | Stay SANDBOX (orphaned) |
| Production assets? | Stay PRODUCTION (immutable) |
| Cleanup? | Nightly job flags orphans >30 days |
| Auto-delete? | ❌ NO - never auto-delete |

---

# PART 3: RESOLVED EDGE CASES ✅

## EC1-EC10: Previously Identified & Resolved

| # | Edge Case | Resolution |
|---|-----------|------------|
| EC1 | Asset unlinked mid-edit (Shared→Exclusive) | Re-check on SAVE; if exclusive now, inline update succeeds |
| EC2 | Asset status change mid-edit (SANDBOX→DRAFT) | Edit succeeds as inline update |
| EC3 | Asset linked to multiple sandboxes | Each sandbox tracks own version via `sandbox_component_map` |
| EC4 | Concurrent edit detection | Optimistic locking via `version_no`; conflict UI with Merge/Overwrite/Reload |
| EC5 | Enterprise edit impact on market rules | Manual refresh required; no auto-propagate |
| EC6 | Scoring engine - copied vs production | Uses copied rules in sandbox (isolated) |
| EC7 | Draft asset becomes PRODUCTION via different sandbox | Original market loses edit rights; must create V2 |
| EC8 | Market localised ruleset deletion by enterprise | BLOCKED - Enterprise cannot delete; coordinate with markets |
| EC9 | Refresh with conflicting asset versions | Conflict resolution UI: Keep Mine / Take Theirs / Merge |
| EC10 | Version cap + asset versions | Carry over to new sandbox; archived sandbox read-only |

---

# PART 4: NEW EDGE CASES DISCOVERED 🔶

## EC11-EC20: Need Your Input

### EC11: Optimistic Locking Cascade Failure
```
Scenario:
- User X edits Asset A1, creates A1 V2
- User Y edits Rule R1 (references A1)
- User X saves A1 V2 successfully
- User Y's Rule R1 still points to A1 V1

QUESTION: Should Rule R1 auto-update to A1 V2?
□ Yes - Rules auto-update to latest asset version in same sandbox
□ No - User must manually update rule reference
```

### EC12: Orphan Asset Accumulation
```
Based on: Orphaned assets stay SANDBOX indefinitely

Risk: After 1 year, 1000+ orphan assets → slow search, storage bloat

QUESTION: Retention policy?
□ Auto-archive after 90 days
□ Require explicit admin action
□ Allow bulk-delete by user
□ Other: _____________
```

### EC13: Merge Conflict Resolution Logic
```
Scenario:
- User X adds values [A, B] to asset
- User Y adds values [C, D] to same asset
- Both choose "Merge"

QUESTION: What's the merge logic?
□ UNION of both sets → [A, B, C, D]
□ User must manually pick each value
□ Need 3-way merge UI like Git
□ Other: _____________
```

### EC14: Stale Sandbox + Version Cap Collision
```
Scenario:
- Sandbox is stale (needs refresh)
- Sandbox is at version 9
- User refreshes → creates version 10
- User finds issues → CANNOT create version 11 (cap hit)

QUESTION: Should refresh count against version cap?
□ Yes - refresh creates new version
□ No - refresh is separate operation
□ Allow 1 extra version after cap for refresh
□ Other: _____________
```

### EC15: Enterprise Edit During Active Market Sandboxes
```
Timeline:
T1: Enterprise edits Asset A1 (V1→V2), merges to production
T2: Market IN has active sandbox using A1 V1 (now stale)
T3: Market BE has active sandbox using A1 V1 (now stale)

QUESTION: Auto-notification?
□ Yes - system notifies IN, BE that they're stale
□ No - users must check manually
□ Block their merge if stale
□ Other: _____________
```

### EC16: Simulation Isolation During Queue Delay
```
Timeline:
T1: User submits sandbox for simulation
T2: Simulation enters queue (2-hour wait)
T3: During queue, enterprise merges new prod version
T4: Simulation actually starts

QUESTION: When is copy made?
□ At SUBMIT time (before queue)
□ At JOB_START time (when simulation runs)
□ Other: _____________
```

### EC17: Copy-On-Write Naming Convention
```
Market A copies "High_Risk_Countries" → ?
Market B copies same → ?
Market C copies same → ?

QUESTION: Naming convention?
□ Auto-append market code: "High_Risk_Countries_IN"
□ User provides custom name
□ Auto-increment: "High_Risk_Countries_2"
□ Other: _____________
```

### EC18: Rollback to Stale Production Baseline
```
Timeline:
T1: Sandbox V1 created from Prod P1
T2: Sandbox V2 created (edits made)
T3: Enterprise updates prod to P2
T4: User rollbacks to V1 (from P1 baseline)
T5: New V3 is based on P1 config, but current prod is P2

QUESTION: Allow rollback to stale config?
□ Yes - with "Stale" warning
□ No - force refresh first
□ Other: _____________
```

### EC19: Asset Version Explosion
```
Scenario:
- User edits asset, doesn't submit for 3 months
- Makes 500+ inline changes to V2
- Finally submits
- Next day, edits again → creates V3

Over time: Asset could have 100+ versions

QUESTION: Version limit per asset?
□ No limit
□ Hard limit (e.g., 50 versions)
□ Consolidate old versions after X time
□ Other: _____________
```

### EC20: FA Gate Deletion with Active Market Overrides
```
Scenario:
- Enterprise sandbox deletes FA Gate G1
- G1 has overrides in IN, BE, GE markets

QUESTION: Allow deletion?
□ Yes - cascade-delete all overrides
□ No - block until markets remove overrides
□ Mark as "DEPRECATED" instead of delete
□ Other: _____________
```

---

# PART 5: OPEN FOLLOW-UP QUESTIONS 🔴

## FQ7-FQ15: Need Your Answers

| # | Question | Options |
|---|----------|---------|
| FQ7 | When asset version changes (V1→V2), should rules auto-update reference? | □ Yes □ No |
| FQ8 | Orphan asset retention period before admin review? | □ 30 days □ 90 days □ Never auto-flag |
| FQ9 | For asset value lists, is merge = UNION of both sets? | □ Yes □ No □ User picks each |
| FQ10 | Does refresh create new sandbox version? | □ Yes □ No |
| FQ11 | Can stale sandbox merge to production? | □ Yes □ No □ With warning |
| FQ12 | Is sandbox config copied at SUBMIT or JOB_START? | □ SUBMIT □ JOB_START |
| FQ13 | Is asset name globally unique or scoped to market? | □ Global □ Market-scoped |
| FQ14 | Allow rollback if resulting config would be stale? | □ Yes □ No □ With warning |
| FQ15 | Can enterprise delete FA gate if markets have overrides? | □ Yes (cascade) □ No (block) |

---

# PART 6: DATABASE TABLES INVOLVED

## Primary Tables

| Table | Purpose |
|-------|---------|
| `risk_assess` | Sandbox container (versioned) |
| `sandbox_version` | Tracks each sandbox version (1-10) |
| `sandbox_component_map` | Maps sandbox version → component versions |
| `refer_da_asset` | Asset definitions (versioned) |
| `refer_da_asset_srce` | Asset source types |
| `risk_assess_sta_rel` | Status history (state transitions) |
| `sandbox_audit_comment` | Audit trail with comments |
| `rule_set` | Ruleset definitions |
| `risk_rule` | Individual rules (references assets) |
| `risk_assess_ctgy_elem_rel` | Risk elements |

---

# PART 7: NEXT STEPS

## Immediate Actions Needed

1. **Answer FQ7-FQ15** - Critical for finalizing edge case handling
2. **Confirm EC11-EC20** - Choose resolution for each new edge case
3. **Review sandbox version cap vs refresh** - This is a potential major issue

## After Confirmation

1. Build 2-page HTML visualization with all scenarios
2. Create detailed database operations for each flow
3. Document API contracts for each operation

---

*Document maintained at: `/Users/satvikjain/Downloads/Projects/CRR_Final/context/CRR_Lifecycle_Analysis.md`*
