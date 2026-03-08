# 🔄 Sandbox Refresh Functionality - Architectural Design

## Document Purpose
This document explains how to implement the **Refresh** functionality when Enterprise and Market sandboxes coexist. Written for non-technical stakeholders with over-simplified explanations.

---

# 📚 PART 1: UNDERSTANDING THE PROBLEM

## 1.1 The Coexistence Scenario

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SANDBOX COEXISTENCE SCENARIO                             │
└─────────────────────────────────────────────────────────────────────────────────┘

        PRODUCTION (Live Rules)
        ═══════════════════════
              │
              │ Enterprise Sandbox Created
              ▼
    ┌─────────────────────┐     ┌─────────────────────┐
    │  ENTERPRISE SANDBOX │     │   MARKET SANDBOX    │
    │    (Scope: XX)      │     │   (Scope: India)    │
    │                     │     │                     │
    │  - Rule A (Ent)     │     │  - Rule A (Ent) ◄───┼── OVERLAPPING!
    │  - Rule B (Ent)     │     │  - Rule C (India)   │
    │  - Rule D (Ent)     │     │  - Rule D (Ent) ◄───┼── OVERLAPPING!
    └─────────────────────┘     └─────────────────────┘
              │
              │ Enterprise promoted to Production
              ▼
        PRODUCTION (Updated!)
        ═══════════════════════
        Rule A changed! ───────────► Market Sandbox is now STALE!
        Rule D changed! ───────────► Market Sandbox is now STALE!
```

## 1.2 What Makes a Sandbox "STALE"?

Think of it like a **Word Document Analogy**:

| Situation | Analogy |
|-----------|---------|
| You're editing a document | You have Market Sandbox open |
| Someone else saves changes to the same document | Enterprise Sandbox gets promoted |
| Your copy is now outdated | Your Market Sandbox is now STALE |
| You need to "refresh" to see their changes | You need to REFRESH the sandbox |

### Technical Definition of STALE:
A sandbox becomes STALE when **ANY rule it inherited from Production** has been updated in Production after the sandbox was created.

---

# 📚 PART 2: THE SOLUTION ARCHITECTURE

## 2.1 High-Level Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           REFRESH FUNCTIONALITY FLOW                             │
└─────────────────────────────────────────────────────────────────────────────────┘

   ┌────────────────┐
   │ Market Sandbox │
   │   (Working)    │
   └───────┬────────┘
           │
           │ (1) Enterprise Sandbox promoted
           ▼
   ┌────────────────┐
   │ Market Sandbox │
   │   (STALE)      │◄── UI shows "STALE" badge, buttons disabled
   └───────┬────────┘
           │
           │ (2) User clicks REFRESH button
           ▼
   ┌────────────────────────────────────────────────────────────────────┐
   │                    REFRESH PROCESS                                  │
   │                                                                     │
   │  Step A: Identify which Enterprise rules were changed in Prod      │
   │  Step B: For each changed rule, check if user modified it locally  │
   │  Step C: If NOT modified → Pull latest from Production             │
   │  Step D: If MODIFIED → Keep user's version (don't overwrite)       │
   │  Step E: Update sandbox metadata to mark as "FRESH"                │
   │                                                                     │
   └───────┬────────────────────────────────────────────────────────────┘
           │
           │ (3) Refresh complete
           ▼
   ┌────────────────┐
   │ Market Sandbox │
   │   (Working)    │◄── User can continue editing
   └────────────────┘
```

## 2.2 The Golden Rule: User Changes Are Never Lost

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    WHAT HAPPENS TO DIFFERENT RULE TYPES                          │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┬─────────────────────┬───────────────────────────────────┐
│ Rule Type            │ User Action         │ What Refresh Does                 │
├──────────────────────┼─────────────────────┼───────────────────────────────────┤
│ Enterprise Rule A    │ User edited it      │ ✅ KEEP user's version            │
│ Enterprise Rule B    │ User deleted it     │ ✅ KEEP deleted (stays deleted)   │
│ Enterprise Rule C    │ No changes          │ ✅ PULL latest from Production    │
│ Market-specific Rule │ User created new    │ ✅ KEEP as-is (not affected)      │
└──────────────────────┴─────────────────────┴───────────────────────────────────┘
```

---

# 📚 PART 3: DATABASE DESIGN

## 3.1 New Table: `sandbox_stale_tracker`

This new table tracks when a sandbox becomes stale and what rules caused it.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    TABLE: sandbox_stale_tracker                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┬───────────────┬─────────────────────────────────────┐
│ Column                  │ Type          │ Purpose                             │
├─────────────────────────┼───────────────┼─────────────────────────────────────┤
│ stale_tracker_id        │ integer (PK)  │ Unique identifier                   │
│ affected_risk_assess_id │ integer       │ The sandbox that became stale       │
│ affected_risk_assess_vsn│ integer       │ Version of the affected sandbox     │
│ triggering_risk_assess_id│ integer      │ Enterprise sandbox that was promoted│
│ stale_detected_ts       │ timestamp     │ When staleness was detected         │
│ is_stale                │ boolean       │ TRUE = still stale, FALSE = refreshed│
│ refreshed_ts            │ timestamp     │ When refresh was performed          │
│ refreshed_user_id       │ varchar       │ Who performed the refresh           │
└─────────────────────────┴───────────────┴─────────────────────────────────────┘
```

## 3.2 New Table: `sandbox_stale_rules`

Tracks exactly which rules caused the staleness.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    TABLE: sandbox_stale_rules                                    │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┬───────────────┬─────────────────────────────────────┐
│ Column                  │ Type          │ Purpose                             │
├─────────────────────────┼───────────────┼─────────────────────────────────────┤
│ stale_tracker_id        │ integer (FK)  │ Links to stale_tracker              │
│ stale_rule_id           │ integer       │ The rule that changed in Production │
│ prod_rule_version       │ integer       │ New version in production           │
│ sandbox_rule_version    │ integer       │ Version sandbox had at creation     │
│ user_modified           │ boolean       │ Did user modify this rule locally?  │
│ refresh_action          │ varchar       │ PULLED / KEPT_USER_VERSION          │
└─────────────────────────┴───────────────┴─────────────────────────────────────┘
```

## 3.3 New Column: `risk_assess` Table

Add one new column to existing table:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    ADD TO TABLE: risk_assess                                     │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┬───────────────┬─────────────────────────────────────┐
│ New Column              │ Type          │ Purpose                             │
├─────────────────────────┼───────────────┼─────────────────────────────────────┤
│ is_stale                │ boolean       │ TRUE = sandbox is stale             │
│                         │ DEFAULT FALSE │ FALSE = sandbox is fresh            │
└─────────────────────────┴───────────────┴─────────────────────────────────────┘
```

---

# 📚 PART 4: THE REFRESH ALGORITHM

## 4.1 Step-by-Step Process

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         REFRESH ALGORITHM (Simplified)                           │
└─────────────────────────────────────────────────────────────────────────────────┘

STEP 1: GET STALE RULES
═══════════════════════
→ Find all entries in sandbox_stale_rules for this sandbox
→ This gives us the list of Enterprise rules that changed

STEP 2: FOR EACH STALE RULE, CHECK USER MODIFICATIONS
══════════════════════════════════════════════════════
→ Compare sandbox version of rule with its "creation snapshot"
→ If different = User modified it
→ If same = User never touched it

STEP 3: DECIDE ACTION FOR EACH RULE
════════════════════════════════════
IF user_modified = TRUE:
    → Action = KEEP user's version
    → Log: "Kept user's modified version of Rule X"
    
IF user_modified = FALSE:
    → Action = PULL from Production
    → Copy latest production rule into sandbox
    → Log: "Pulled latest version of Rule Y from Production"

STEP 4: MARK SANDBOX AS FRESH
══════════════════════════════
→ Set risk_assess.is_stale = FALSE
→ Update sandbox_stale_tracker.is_stale = FALSE
→ Set refreshed_ts = NOW()
```

## 4.2 Visual Example

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              REFRESH EXAMPLE                                     │
└─────────────────────────────────────────────────────────────────────────────────┘

BEFORE REFRESH:
───────────────
Production Rules:           Market Sandbox Rules:
├── Rule A (v3) ──────►     ├── Rule A (v1) ← STALE! User edited
├── Rule B (v2) ──────►     ├── Rule B (v1) ← STALE! No user edits
├── Rule C (v1)             ├── Rule C (v1) ← Not affected
└── Rule D (v2) ──────►     ├── Rule D (-)  ← STALE! User deleted
                            └── Rule E (new)← User created

AFTER REFRESH:
──────────────
Production Rules:           Market Sandbox Rules:
├── Rule A (v3)             ├── Rule A (v1) ← KEPT (user edited)
├── Rule B (v2)             ├── Rule B (v2) ← PULLED (no user edits)
├── Rule C (v1)             ├── Rule C (v1) ← No change needed
└── Rule D (v2)             ├── Rule D (-)  ← KEPT deleted
                            └── Rule E (new)← KEPT (user created)
```

---

# 📚 PART 5: UI/UX DESIGN

## 5.1 Stale State UI

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              STALE STATE SCREEN                                  │
│─────────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │ ⚠️ SANDBOX STALE - REFRESH REQUIRED                                        │ │
│  │                                                                            │ │
│  │ This sandbox has become stale because Enterprise rules were updated       │ │
│  │ in Production on January 24, 2026 at 5:30 PM.                              │ │
│  │                                                                            │ │
│  │ Affected Rules: 3 rules need attention                                     │ │
│  │ Your Changes: All your edits will be preserved                             │ │
│  │                                                                            │ │
│  │              ┌──────────────────────┐                                      │ │
│  │              │   🔄 REFRESH NOW     │                                      │ │
│  │              └──────────────────────┘                                      │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │ DISABLED ACTIONS:                                                          │ │
│  │ ❌ Edit Rules        ❌ Edit Assets       ❌ Edit FA Scores                 │ │
│  │ ❌ Submit Sandbox    ❌ Cancel Sandbox                                      │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 5.2 Refresh Preview Screen

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          REFRESH PREVIEW SCREEN                                  │
│─────────────────────────────────────────────────────────────────────────────────│
│                                                                                  │
│  The following actions will be taken:                                            │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                            │ │
│  │  ✅ WILL BE UPDATED FROM PRODUCTION:                                       │ │
│  │     • Rule B: High Risk Countries (you haven't modified this)              │ │
│  │     • Rule F: Transaction Limits (you haven't modified this)               │ │
│  │                                                                            │ │
│  │  🔒 YOUR CHANGES WILL BE PRESERVED:                                        │ │
│  │     • Rule A: Customer Type (you edited this)                              │ │
│  │     • Rule D: Geographic Risk (you deleted this)                           │ │
│  │     • Rule E: India Special (you created this)                             │ │
│  │                                                                            │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
│                    ┌─────────────────┐    ┌─────────────────┐                   │
│                    │     Cancel      │    │ Confirm Refresh │                   │
│                    └─────────────────┘    └─────────────────┘                   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

# 📚 PART 6: API DESIGN

## 6.1 New API Endpoints

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              NEW API ENDPOINTS                                   │
└─────────────────────────────────────────────────────────────────────────────────┘

1. CHECK STALENESS
   ────────────────
   GET /api/sandbox/{sandboxId}/staleness-status
   
   Response:
   {
     "isStale": true,
     "staleSince": "2026-01-24T17:30:00",
     "triggeringPromotion": {
       "promotedSandboxId": 5,
       "promotedAt": "2026-01-24T17:25:00",
       "promotedBy": "john.doe"
     },
     "affectedRulesCount": 3
   }

2. GET REFRESH PREVIEW
   ────────────────────
   GET /api/sandbox/{sandboxId}/refresh-preview
   
   Response:
   {
     "rulesToUpdate": [
       {"ruleId": 2, "ruleName": "High Risk Countries", "action": "PULL"},
       {"ruleId": 6, "ruleName": "Transaction Limits", "action": "PULL"}
     ],
     "rulesToPreserve": [
       {"ruleId": 1, "ruleName": "Customer Type", "reason": "USER_EDITED"},
       {"ruleId": 4, "ruleName": "Geographic Risk", "reason": "USER_DELETED"}
     ]
   }

3. EXECUTE REFRESH
   ────────────────
   POST /api/sandbox/{sandboxId}/refresh
   
   Response:
   {
     "success": true,
     "refreshedAt": "2026-01-24T17:35:00",
     "rulesUpdated": 2,
     "rulesPreserved": 2,
     "sandboxStatus": "WORKING"
   }
```

---

# 📚 PART 7: EVENT TRIGGERS

## 7.1 When to Mark Sandbox as STALE

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           STALENESS TRIGGER FLOW                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

TRIGGER: Enterprise Sandbox Promoted to Production
═════════════════════════════════════════════════

                    Enterprise Sandbox
                    Promoted (Status=8)
                           │
                           ▼
               ┌───────────────────────┐
               │ BACKGROUND JOB STARTS │
               └───────────┬───────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │ Find all active       │
               │ Market Sandboxes      │
               │ (status = WORKING)    │
               └───────────┬───────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
    ┌─────────────────┐       ┌─────────────────┐
    │ India Sandbox   │       │ China Sandbox   │
    └────────┬────────┘       └────────┬────────┘
             │                         │
             ▼                         ▼
    ┌─────────────────┐       ┌─────────────────┐
    │ Check for       │       │ Check for       │
    │ overlapping     │       │ overlapping     │
    │ rules           │       │ rules           │
    └────────┬────────┘       └────────┬────────┘
             │                         │
             ▼                         ▼
       Has overlaps?             Has overlaps?
             │                         │
        YES  │                    NO   │
             ▼                         ▼
    ┌─────────────────┐       ┌─────────────────┐
    │ Mark as STALE   │       │ No action       │
    │ Create tracker  │       │ (stays fresh)   │
    │ record          │       │                 │
    └─────────────────┘       └─────────────────┘
```

---

# 📚 PART 8: IMPLEMENTATION SUMMARY

## 8.1 Components to Build

| # | Component | Type | Purpose |
|---|-----------|------|---------|
| 1 | `sandbox_stale_tracker` | Database Table | Track stale sandboxes |
| 2 | `sandbox_stale_rules` | Database Table | Track affected rules |
| 3 | `is_stale` column | Database Column | Quick staleness check |
| 4 | StalenessDetectionJob | Background Service | Runs after promotion |
| 5 | RefreshService | Backend Service | Executes refresh logic |
| 6 | StalenessController | API Controller | Exposes 3 endpoints |
| 7 | StaleNotificationBanner | UI Component | Shows stale warning |
| 8 | RefreshPreviewModal | UI Component | Shows what will happen |

## 8.2 Edge Cases Handled

| Edge Case | How It's Handled |
|-----------|------------------|
| User deleted a rule | Deletion is preserved (not restored) |
| User created new rule | Not affected by refresh |
| Multiple promotions before refresh | All changes accumulated |
| User partially edited | Keeps user's version |
| Asset changes only | Asset refreshed similarly |

---

## Summary

Ye architecture ensure karti hai ki:
1. **User ka kaam kabhi lost nahi hota** - jo bhi changes user ne kiye, woh safe hain
2. **System automatically detect karta hai** - jab bhi Enterprise promote hota hai
3. **Clear UI feedback** - user ko pata chalta hai kya stale hai aur kya update hoga
4. **Audit trail** - sab kuch tracked hai database mein

