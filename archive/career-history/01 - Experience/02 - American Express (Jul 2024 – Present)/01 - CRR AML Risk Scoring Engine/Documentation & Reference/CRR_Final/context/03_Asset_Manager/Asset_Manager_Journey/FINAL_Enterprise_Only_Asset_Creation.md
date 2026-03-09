# FINAL APPROACH: Enterprise-Only Asset Creation
## Simplest Possible Asset Manager Architecture

---

## 🎯 The Final Rule

| Action | Enterprise Sandbox | Market Sandbox |
|--------|-------------------|----------------|
| **Create new asset** | ✅ YES | ❌ NO |
| **Edit asset** | ✅ YES | ❌ NO |
| **Link asset to rule** | ✅ YES | ✅ YES |
| **View asset** | ✅ YES | ✅ YES |

> **One Simple Principle:**
> 
> **All assets are created and edited at Enterprise level.**
> **Markets can only LINK/USE existing PRODUCTION assets.**

---

## Why This Works

### Single Team Context:
- Same compliance team manages ALL markets
- No separate "owners" - everyone is on same team
- Central asset management makes sense

### Removed Complexity:
- ❌ No market-level asset creation
- ❌ No "who owns this asset?" confusion
- ❌ No cross-market sharing logic
- ❌ No asset promotion from market to enterprise
- ❌ No copy-on-write

### Kept Flexibility:
- ✅ Enterprise can create market-specific assets (e.g., "APAC_Watchlist")
- ✅ Markets can use any PRODUCTION asset
- ✅ Same team creates what markets need

---

# SIMPLIFIED USER JOURNEY

## PHASE A: ENTERPRISE CREATES ALL ASSETS

```
STEP 1: User creates Enterprise sandbox

STEP 2: User creates assets for ALL needs:
        
        Global Assets (used by everyone):
        ├── A001: High_Risk_Countries
        ├── A002: Low_Risk_Occupations
        └── A003: Sanctioned_Entities
        
        Regional Assets (for specific markets):
        ├── A004: APAC_Regional_Watchlist (for India, Australia)
        ├── A005: EU_Regulatory_List (for Belgium, Germany)
        └── A006: India_Local_Watchlist (for India only)

STEP 3: User links some assets to Enterprise rules

STEP 4: User promotes Enterprise sandbox
        All assets: DRAFT → SANDBOX → PRODUCTION
```

**Key Point:** Even "India-specific" assets like A006 are created at Enterprise level.

---

## PHASE B: MARKET USES ASSETS

```
STEP 5: User creates India sandbox

STEP 6: User opens Asset Manager in India sandbox

        ┌──────────────────────────────────────────────┐
        │  ASSET LIST (India Sandbox View)             │
        ├──────────────────────────────────────────────┤
        │                                              │
        │  AVAILABLE ASSETS (Read-Only):               │
        │  ├── A001: High_Risk_Countries    [View]     │
        │  ├── A002: Low_Risk_Occupations   [View]     │
        │  ├── A003: Sanctioned_Entities    [View]     │
        │  ├── A004: APAC_Regional_Watchlist[View]     │
        │  ├── A005: EU_Regulatory_List     [View]     │
        │  └── A006: India_Local_Watchlist  [View]     │
        │                                              │
        │  [+ Add New Asset] ← BUTTON NOT VISIBLE      │
        │                      (hidden in market)      │
        │                                              │
        └──────────────────────────────────────────────┘

STEP 7: User creates India rules, links A001, A004, A006

STEP 8: User promotes India sandbox
        Assets: No status change (already PRODUCTION)
        India rules: Now using these assets
```

---

## PHASE C: MARKET NEEDS NEW ASSET

**Scenario:** India needs a new asset "India_PEP_List" that doesn't exist.

### ✅ NEW RULE: Enterprise Sandbox Can Coexist with Market Sandboxes

```
STEP 1: User identifies need in India sandbox work
        "We need a PEP list for India"

STEP 2: User CANNOT create asset in India sandbox
        No "Add New Asset" button visible

STEP 3: User creates Enterprise sandbox
        ✅ ALLOWED - No need to cancel India sandbox!
        
        Enterprise sandbox = ONLY for asset creation/editing
        Market sandbox = Continues working in parallel

STEP 4: In Enterprise sandbox:
        User creates A007: India_PEP_List
        User promotes Enterprise sandbox

STEP 5: A007 is now PRODUCTION

STEP 6: Back in India sandbox:
        User refreshes asset list
        Can now see and use A007
```

**Key Change from Original Design:**
| Scenario | OLD Rule | NEW Rule |
|----------|----------|----------|
| India sandbox exists, want to create asset | ❌ Must cancel India sandbox first | ✅ Create Enterprise sandbox in parallel |
| Enterprise sandbox exists, want India work | ❌ Must wait for Enterprise | ✅ Create India sandbox in parallel |

**Why This Works:**
- Enterprise sandbox = Asset creation/editing ONLY
- Market sandbox = Rule configuration ONLY
- They don't conflict because they work on different things

**Workflow Visualization:**

```
India sandbox (WORKING)
├── User realizes: "Need India_PEP_List"
│
├── User creates Enterprise sandbox (NO NEED TO CANCEL!)
│   ├── Creates A007: India_PEP_List
│   └── Promotes Enterprise
│
├── A007: PRODUCTION ✓
│
└── User continues India sandbox work
    └── Links A007 to India rules
```

---

## PHASE D: ENTERPRISE UPDATES ASSET (Coexistence Allowed)

```
Current State:
├── India sandbox: WORKING (active)
├── Belgium sandbox: WORKING (active)
│
├── India uses: A001, A004, A006
├── Belgium uses: A001, A005

User wants to add "Cuba" to A001 (High_Risk_Countries)

STEP 1: User creates Enterprise sandbox
        ✅ ALLOWED - India and Belgium sandboxes still active!

STEP 2: Edit A001 → Creates A001 V2

STEP 3: Enterprise simulation runs
        Shows impact on: All markets (using current production config)

STEP 4: Promote Enterprise sandbox
        A001 V1 → ARCHIVED
        A001 V2 → PRODUCTION
        
STEP 5: India and Belgium sandboxes get notification:
        "Asset A001 has been updated to V2"
        Their next simulation will use V2
```

---

## UPDATED SANDBOX COEXISTENCE RULES

| Sandbox Type | Can Coexist With |
|--------------|------------------|
| Enterprise | ✅ Market sandboxes (any) |
| Market (India) | ✅ Enterprise + Other markets |
| Market (Belgium) | ✅ Enterprise + Other markets |

### Only ONE Enterprise Sandbox at a Time

| Existing | Can Create? |
|----------|-------------|
| Enterprise sandbox exists | ❌ Cannot create another Enterprise |
| Market sandboxes exist | ✅ Can create Enterprise |
| Enterprise + Markets exist | ✅ Valid state |

---

## WHAT HAPPENS WHEN ENTERPRISE UPDATES ASSET DURING MARKET WORK?

```
Timeline:
├── T1: India sandbox created, using A001 V1
├── T2: Enterprise sandbox created (parallel)
├── T3: Enterprise edits A001 → V2
├── T4: Enterprise promotes → A001 V2 is PRODUCTION
├── T5: India sandbox still open

What does India see?

Option A (Simpler): India continues using V1 snapshot
├── India's current work based on V1
├── When India submits for simulation, uses V1
├── When India promotes, system warns about stale asset
└── India can refresh to get V2

Option B (Recommended): India auto-sees V2
├── India's asset list shows V2 immediately
├── Rules automatically reference V2
├── Simulation uses V2
└── No action needed from India
```

**Recommendation: Option B** - Markets always see latest PRODUCTION version.

---

# ASSET VISIBILITY IN MARKET SANDBOX

## What User Sees:

| Asset Status | Visible in Market? | Can Link? | Can Edit? |
|--------------|-------------------|-----------|-----------|
| PRODUCTION | ✅ YES | ✅ YES | ❌ NO |
| ARCHIVED | ❌ NO | ❌ NO | ❌ NO |
| DRAFT (Enterprise) | ❌ NO | ❌ NO | ❌ NO |
| SANDBOX (Enterprise) | ❌ NO | ❌ NO | ❌ NO |

## Summary:
**Markets only see PRODUCTION assets. That's it.**

---

# UI/UX IN MARKET SANDBOX

## Asset Manager View:

```
┌─────────────────────────────────────────────────────────┐
│  ASSET MANAGER                                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ℹ️ Assets can only be created in Enterprise sandbox.    │
│     You can VIEW and LINK existing assets here.         │
│                                                          │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  Search: [________________] [🔍]                        │
│                                                          │
│  │ Name                      │ Reference │ Values │     │
│  ├───────────────────────────┼───────────┼────────┤     │
│  │ High_Risk_Countries       │ Countries │ 45     │[👁]│
│  │ Low_Risk_Occupations      │ Occupations│ 120   │[👁]│
│  │ Sanctioned_Entities       │ Entities  │ 2,340  │[👁]│
│  │ APAC_Regional_Watchlist   │ Countries │ 12     │[👁]│
│  │ India_Local_Watchlist     │ Countries │ 8      │[👁]│
│                                                          │
│  [👁] = View Details (Read-Only)                        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Key UI Elements:**
- No "Add New Asset" button
- Info message explaining assets are Enterprise-level
- Only "View" action available (not Edit)

---

# NAMING CONVENTION FOR REGIONAL ASSETS

Since all assets are created at Enterprise, use clear naming:

| Asset Name | Purpose | Intended Markets |
|------------|---------|------------------|
| High_Risk_Countries | Global list | All |
| Low_Risk_Occupations | Global list | All |
| APAC_Regional_Watchlist | APAC region | India, Australia, etc. |
| EU_Regulatory_List | EU region | Belgium, Germany, etc. |
| India_Local_Watchlist | India specific | India only |
| Australia_PEP_List | Australia specific | Australia only |

**Convention:**
- `[Region]_[Purpose]` for regional assets
- `[Market]_[Purpose]` for market-specific assets
- No prefix for global assets

---

# EDGE CASES - WHAT REMAINS

| Edge Case | Handling |
|-----------|----------|
| Concurrent edit (Enterprise) | Optimistic locking, conflict resolution |
| Edit during simulation | New version created, simulation uses snapshot |
| Delete asset in use | Blocked, show references |
| Orphaned asset | Auto-archive after 90 days |
| Rollback to old version | Enterprise sandbox required |

# EDGE CASES - ELIMINATED

| Edge Case | Gone Because |
|-----------|--------------|
| Copy-on-write | No copies |
| Market creates asset | Not allowed |
| Which market owns asset? | All assets are Enterprise |
| Cross-market sharing rules | Not needed - all are shared |
| Asset classification logic | No classification - all Enterprise |
| Market-to-Enterprise promotion | Not needed |

---

# COMPARISON - ALL APPROACHES

| Approach | Complexity | Flexibility | Edge Cases |
|----------|------------|-------------|------------|
| Original (copies allowed) | 🔴🔴🔴🔴🔴 | HIGH | Many |
| Hybrid (markets create) | 🟡🟡 | MEDIUM | Some |
| **Enterprise-Only (FINAL)** | 🟢 | LOW | Few |

---

# FINAL SUMMARY

```
┌─────────────────────────────────────────────────────────┐
│                                                          │
│  ASSET CREATION: ENTERPRISE ONLY                        │
│  ├── All assets created in Enterprise sandbox          │
│  ├── Market sandboxes: View + Link only                │
│  └── No copies, no market-level creation                │
│                                                          │
│  ASSET EDITING: ENTERPRISE ONLY                         │
│  ├── All edits in Enterprise sandbox                   │
│  ├── Enterprise simulation = all-market impact          │
│  └── Single version for everyone                        │
│                                                          │
│  MARKET SANDBOXES:                                      │
│  ├── View PRODUCTION assets                             │
│  ├── Link assets to rules                               │
│  └── That's it. Nothing else.                           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## One-Liner:
> **"Create at Enterprise. Use everywhere."**

---

*Document End - FINAL APPROACH*
