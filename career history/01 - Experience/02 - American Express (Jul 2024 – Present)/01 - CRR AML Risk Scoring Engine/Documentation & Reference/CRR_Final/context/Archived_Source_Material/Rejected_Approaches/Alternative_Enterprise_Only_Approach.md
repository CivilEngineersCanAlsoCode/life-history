# Alternative User Journey: Enterprise-Only Asset Management
## Tradeoff Analysis: Simplified Asset Model

---

## 🎯 The Tradeoff

> **Creation and Editing of assets is ONLY allowed from Enterprise-Level sandbox.**
> 
> **Markets can ONLY link/use existing assets in their rules. No creation, no editing.**

---

## What This Means

| Action | Enterprise Sandbox | Market Sandbox |
|--------|-------------------|----------------|
| **Create new asset** | ✅ YES | ❌ NO |
| **Edit asset values** | ✅ YES | ❌ NO |
| **Create new version** | ✅ YES | ❌ NO |
| **Link asset to rule** | ✅ YES | ✅ YES |
| **View asset values** | ✅ YES | ✅ YES |
| **Copy asset** | ✅ YES | ❌ NO |

---

# REVISED USER JOURNEY

## PHASE A: FIRST ENTERPRISE SETUP (Same as before)

- A.1: User logs into blank CRR system
- A.2: User sees "Create New Assessment" option
- A.3: Only "Enterprise (XX)" is available (first sandbox must be Enterprise)
- A.4: Enterprise Sandbox is created
- A.5: User lands on Sandbox Dashboard

**No change here.**

---

## PHASE B: ASSET CREATION (Enterprise Only)

## B.1: User Navigates to Asset Manager
- From Configuration Selector, clicks "Assets"
- "Add New Asset" button visible

## B.2: User Creates Asset
- Enters Name, Description (mandatory), Reference Table
- Uploads file with values
- Saves asset
- **Asset ID: A001, Version: 1, Status: DRAFT**

## B.3: User Creates More Assets
- Creates A002, A003, A004...
- All in DRAFT status

**Same as before - assets created at Enterprise level.**

---

## PHASE C: LINKING ASSETS TO RULES (Enterprise)

- User creates rules in Enterprise sandbox
- Links assets to rules
- Asset status: DRAFT → SANDBOX
- Configures FA, Market Settings

**Same as before.**

---

## PHASE D: ENTERPRISE PROMOTION

- Simulation runs
- Approval workflow completes
- Enterprise promotes to Production
- Assets: SANDBOX → PRODUCTION
- Now markets can use these assets

**Same as before.**

---

## PHASE E: MARKET SANDBOX CREATION (Simplified!)

## E.1: User Creates India Sandbox
- Enterprise production exists
- User creates India sandbox
- Status: WORKING

## E.2: India Views Available Assets
- Opens Asset Manager
- Sees list of PRODUCTION assets from Enterprise:
  - A001: High_Risk_Countries
  - A002: Low_Risk_Occupations
  - A003: Sanctioned_Entities
  - etc.

## E.3: What India CANNOT Do
- ❌ Cannot click "Add New Asset" (button disabled/hidden in market sandbox)
- ❌ Cannot click "Edit" on any asset (button disabled)
- ❌ Cannot upload new values
- ❌ Cannot create copies

## E.4: What India CAN Do
- ✅ View asset details and values (read-only)
- ✅ Link assets to rules

---

## PHASE F: MARKET LINKS ASSETS TO RULES

## F.1: India Creates a New Rule
- Creates India-specific rule
- Selects Datapoint, Operator

## F.2: India Selects Asset Value
- Asset dropdown shows: A001, A002, A003... (all PRODUCTION assets)
- All assets are available for linking
- Selects "High_Risk_Countries"

## F.3: Rule Saved
- India rule now references Asset A001
- Asset A001 status: Still PRODUCTION (no change)
- India is just "using" the asset, not modifying it

---

## PHASE G: WHAT IF INDIA NEEDS DIFFERENT VALUES?

This is the key scenario. What if India wants "Pakistan" in the High_Risk_Countries list but Enterprise doesn't have it?

## G.1: Old Approach (Current Design)
- India would create a copy: "High_Risk_Countries_IN"
- India edits the copy with Pakistan
- India uses their copy in rules

## G.2: New Approach (Enterprise-Only)
**India CANNOT create their own version.**

**Options:**

### Option 1: Request Enterprise to Add Value
```
1. India identifies need: "We need Pakistan in High_Risk_Countries"
2. India raises request to Enterprise team (same compliance team)
3. Enterprise creates sandbox
4. Enterprise edits A001 → adds Pakistan → A001 V2
5. Enterprise runs simulation (shows impact on ALL markets)
6. Enterprise promotes
7. Now A001 V2 (with Pakistan) is available to everyone
```

**Pros:**
- Consistent values across all markets
- Single source of truth
- Impact calculated globally

**Cons:**
- India cannot have India-specific value
- All markets get Pakistan (even if they don't want it)

### Option 2: Enterprise Creates India-Specific Asset
```
1. India identifies need: "We need APAC-specific high-risk list"
2. Enterprise creates new asset: "APAC_High_Risk_Countries"
3. This asset has Pakistan (and other APAC-specific countries)
4. India uses this asset instead of the generic one
```

**Pros:**
- India gets what they need
- Managed centrally

**Cons:**
- More assets to manage at Enterprise level
- Enterprise team must understand all market needs

---

## PHASE H: MARKET PROMOTION (Simplified)

## H.1: India Submits for Simulation
- India sandbox ready
- Clicks "Submit for Simulation"

## H.2: Simulation Runs
- Uses India's rules
- Uses Enterprise PRODUCTION assets (A001, A002...)
- No India-specific asset versions exist

## H.3: India Promotes
- India rules go to production
- Assets: No status change (they're already PRODUCTION)
- India is just referencing existing assets

---

## PHASE I: ENTERPRISE UPDATES ASSET

## I.1: No Market Sandboxes Exist
- India promoted, Belgium promoted
- All sandboxes cleared

## I.2: Enterprise Creates Sandbox
- Edits A001: Adds "Cuba"
- Creates A001 V2

## I.3: Enterprise Promotes
- A001 V1 → ARCHIVED
- A001 V2 → PRODUCTION
- **All markets automatically use V2**

**Same as current design - single active version rule.**

---

# COMPARISON: Current vs Enterprise-Only

| Aspect | Current Design | Enterprise-Only |
|--------|---------------|-----------------|
| **Asset creation** | Enterprise + Markets | Enterprise only |
| **Asset editing** | Enterprise + Markets (with copy) | Enterprise only |
| **Number of assets** | Can be many (copies per market) | Fewer (centralized) |
| **Complexity** | Higher (copy-on-write, ownership) | Lower |
| **Market flexibility** | High (markets can customize) | Low (must request Enterprise) |
| **Consistency** | Lower (different versions per market) | Higher (single version) |
| **Edge cases** | Many (who can edit what?) | Few (only Enterprise edits) |
| **Impact analysis** | Complex (per-market simulation) | Simpler (Enterprise simulation covers all) |

---

# WHAT EDGE CASES DISAPPEAR?

With Enterprise-Only approach, these edge cases **no longer exist**:

| Edge Case | Why It Disappears |
|-----------|-------------------|
| ❌ Market tries to edit Enterprise asset | Markets can't edit anything |
| ❌ Copy-on-write workflow | No copies allowed |
| ❌ Multiple copies per market | Only one version exists |
| ❌ "Who owns this asset?" | Enterprise owns everything |
| ❌ Cross-market asset sharing | All assets are Enterprise assets |
| ❌ Market creates asset, Enterprise uses it | Markets don't create assets |
| ❌ DRAFT asset visible to other markets | Only Enterprise has DRAFT |
| ❌ SANDBOX asset from other market | Markets don't have SANDBOX assets |

---

# WHAT EDGE CASES REMAIN?

| Edge Case | Still Exists? | Reason |
|-----------|---------------|--------|
| ✅ Concurrent editing (two users, same asset) | Yes | Enterprise users can still conflict |
| ✅ Edit during simulation | Yes | Enterprise simulation running |
| ✅ Rollback to old version | Yes | Version management still needed |
| ✅ Asset used in multiple rules | Yes | Reference tracking still needed |
| ✅ Delete asset in use | Yes | Still need to check references |
| ✅ Orphaned assets | Yes | Unused assets can exist |
| ✅ Version archival | Yes | Old versions still archived |

---

# NEW WORKFLOW: Market Needs Special Values

```
┌─────────────────────────────────────────────────────────────────┐
│  India needs "Pakistan" in High_Risk_Countries                  │
│                                                                  │
│  Current Design:                                                 │
│  ├── India creates copy "High_Risk_Countries_IN"                │
│  ├── India adds Pakistan                                         │
│  ├── India uses their copy                                      │
│  └── Enterprise original unchanged                               │
│                                                                  │
│  Enterprise-Only Design:                                         │
│  ├── India requests Enterprise to add Pakistan                  │
│  │   └── Option A: Add to main list (affects all)               │
│  │   └── Option B: Create new APAC-specific list                │
│  ├── Enterprise decides and creates/edits                       │
│  └── All markets get consistent asset                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

# PROS OF ENTERPRISE-ONLY APPROACH

| Pro | Explanation |
|-----|-------------|
| ✅ **Massive simplification** | 50%+ of edge cases disappear |
| ✅ **Single source of truth** | No confusion about which asset to use |
| ✅ **Consistent compliance** | All markets use same vetted values |
| ✅ **Easier auditing** | All assets managed centrally |
| ✅ **Fewer database tables** | No need for ownership tracking, copy lineage |
| ✅ **Simpler UI** | Markets see read-only asset list |
| ✅ **Faster impact analysis** | Always Enterprise-level simulation |

---

# CONS OF ENTERPRISE-ONLY APPROACH

| Con | Explanation |
|-----|-------------|
| ❌ **Reduced market flexibility** | Markets can't customize for local needs |
| ❌ **Enterprise bottleneck** | All asset changes go through Enterprise |
| ❌ **Slower turnaround** | Market can't quickly add a value they need |
| ❌ **May not fit all scenarios** | Some markets have unique regulatory requirements |
| ❌ **Enterprise workload increases** | Must handle all market requests |

---

# RECOMMENDATION

**If regulatory/compliance requirements are similar across markets:**
→ Enterprise-Only is a GREAT choice. Simplifies everything.

**If markets have significantly different local requirements:**
→ Current design (with copy-on-write) provides needed flexibility.

**Middle Ground:**
→ Enterprise-Only for CREATION, but allow Markets to REQUEST edits through a formal workflow. Enterprise reviews and implements.

---

# SUMMARY

| Design | Complexity | Flexibility | Best For |
|--------|------------|-------------|----------|
| Current (Markets can copy/edit) | High | High | Diverse regulatory requirements |
| Enterprise-Only | Low | Low | Centralized compliance, similar markets |
| Hybrid (Request workflow) | Medium | Medium | Central control with market input |

---

*Document End*
