# Asset Manager - Complete User Journey
## From Blank System to Production (Step by Step)

---

# PART 1: PERMISSION MATRIX

## Who Can Do What?

### Quick Summary Table:

| Action | Enterprise Sandbox | Market Sandbox | No Sandbox (Dashboard) |
|--------|-------------------|----------------|----------------------|
| **Create Asset** | ✅ YES | ❌ NO | ❌ NO |
| **Edit Asset** | ✅ YES (own scope assets) | ❌ NO | ❌ NO |
| **View Asset List** | ✅ YES | ✅ YES | ✅ YES |
| **View Asset Details** | ✅ YES | ✅ YES | ✅ YES |
| **Export Asset** | ✅ YES | ✅ YES | ✅ YES |
| **Link to Rule** | ✅ YES | ✅ YES | N/A |
| **Delete Asset** | ✅ YES (with restrictions) | ❌ NO | ❌ NO |

### Detailed Permission Rules:

**1. CREATE Permission:**
- ✅ Only allowed in **Enterprise Sandbox**
- ❌ Not allowed in Market Sandbox
- ❌ Not allowed when no sandbox is active

**2. EDIT Permission:**
- ✅ Only allowed in **Enterprise Sandbox**
- ❌ Not allowed in Market Sandbox
- ❌ Not allowed when no sandbox is active
- Additional rule: Can only edit PRODUCTION assets (creates new version)

**3. VIEW/EXPORT Permission:**
- ✅ Always allowed, regardless of sandbox state
- Can view from dashboard, any sandbox, anywhere
- Export = download asset values as CSV

**4. DELETE Permission:**
- ✅ Only in Enterprise Sandbox
- ❌ Blocked if asset is used by any rule (anywhere)
- Must remove all rule references first

---

# PART 2: WHAT USER SEES IN EACH STATE

## State 1: No Sandbox Active (Dashboard View)

```
┌─────────────────────────────────────────────────────────────────┐
│  CRR DASHBOARD                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Quick Links:                                                   │
│  ├── [View Assessments]                                         │
│  ├── [View Assets] ← Can view PRODUCTION assets                │
│  └── [Create New Assessment]                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

When user clicks "View Assets":

┌─────────────────────────────────────────────────────────────────┐
│  ASSET MANAGER (Read-Only Mode)                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ℹ️ You are viewing PRODUCTION assets.                          │
│     To create or edit, start an Enterprise sandbox.             │
│                                                                  │
│  ────────────────────────────────────────────────────────────   │
│                                                                  │
│  │ Name                   │ Ref Table  │ Values │ Actions │     │
│  ├────────────────────────┼────────────┼────────┼─────────┤     │
│  │ High_Risk_Countries    │ Countries  │ 45     │ 👁 📥  │     │
│  │ Low_Risk_Occupations   │ Occupations│ 120    │ 👁 📥  │     │
│  │ Sanctioned_Entities    │ Entities   │ 2,340  │ 👁 📥  │     │
│                                                                  │
│  👁 = View Details    📥 = Export CSV                           │
│                                                                  │
│  [+ Create Asset] ← BUTTON DISABLED (no sandbox)               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## State 2: Enterprise Sandbox Active

```
┌─────────────────────────────────────────────────────────────────┐
│  SANDBOX: Enterprise (XX) - Version 1                          │
│  Status: WORKING                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Configuration Selector:                                        │
│  ├── [Rules]                                                    │
│  ├── [Assets] ← Full access                                     │
│  └── [Fundamental Assessment]                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

When user clicks "Assets":

┌─────────────────────────────────────────────────────────────────┐
│  ASSET MANAGER (Enterprise Sandbox)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [+ Create New Asset] ← ENABLED                                 │
│                                                                  │
│  ────────────────────────────────────────────────────────────   │
│                                                                  │
│  │ Name                   │ Status     │ Values │ Actions │     │
│  ├────────────────────────┼────────────┼────────┼─────────┤     │
│  │ High_Risk_Countries    │ PRODUCTION │ 45     │ 👁 ✏️ 📥│     │
│  │ Low_Risk_Occupations   │ PRODUCTION │ 120    │ 👁 ✏️ 📥│     │
│  │ New_Asset_Draft        │ DRAFT      │ 10     │ 👁 ✏️ 📥│     │
│  │ Another_Asset          │ SANDBOX    │ 25     │ 👁 ✏️ 📥│     │
│                                                                  │
│  👁 = View    ✏️ = Edit    📥 = Export                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Status meanings:
- PRODUCTION: Already live in production (editing creates V2)
- SANDBOX: Created/edited in current sandbox (not yet promoted)
- DRAFT: Created but not linked to any rule yet
```

---

## State 3: Market Sandbox Active

```
┌─────────────────────────────────────────────────────────────────┐
│  SANDBOX: India (IN) - Version 1                                │
│  Status: WORKING                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Configuration Selector:                                        │
│  ├── [Rules]                                                    │
│  ├── [Assets] ← View + Link only                               │
│  └── [Fundamental Assessment]                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

When user clicks "Assets":

┌─────────────────────────────────────────────────────────────────┐
│  ASSET MANAGER (India Sandbox - Read Only)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ℹ️ Assets can only be created/edited in Enterprise sandbox.    │
│     You can VIEW and LINK assets to your rules here.           │
│                                                                  │
│  ────────────────────────────────────────────────────────────   │
│                                                                  │
│  │ Name                   │ Status     │ Values │ Actions │     │
│  ├────────────────────────┼────────────┼────────┼─────────┤     │
│  │ High_Risk_Countries    │ PRODUCTION │ 45     │ 👁 📥  │     │
│  │ Low_Risk_Occupations   │ PRODUCTION │ 120    │ 👁 📥  │     │
│  │ APAC_Regional_List     │ PRODUCTION │ 12     │ 👁 📥  │     │
│                                                                  │
│  👁 = View    📥 = Export                                       │
│  (No Edit button - assets are read-only in Market sandbox)     │
│                                                                  │
│  [+ Create Asset] ← BUTTON NOT VISIBLE                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Key difference from Enterprise:
- No "Edit" button (✏️ not shown)
- No "Create Asset" button
- Only PRODUCTION assets visible (no DRAFT/SANDBOX from Enterprise)
```

---

# PART 3: COMPLETE USER JOURNEY

## Starting Point: Completely Blank System
- No production exists
- No sandbox exists  
- No assets exist

---

## JOURNEY STEP 1: First Login

```
User logs into CRR
        ↓
Dashboard shows:
        - No assessments
        - "View Assets" shows empty list
        - "Create New Assessment" available
```

---

## JOURNEY STEP 2: Create First Enterprise Sandbox

```
User clicks "Create New Assessment"
        ↓
Scope selector shows:
        - Enterprise (XX) ✓ (only option enabled)
        - India (IN) ✗ (disabled - no production yet)
        - Belgium (BE) ✗ (disabled)
        ↓
User selects Enterprise
        ↓
Enterprise Sandbox created:
        - Sandbox ID: 1
        - Version: 1
        - Status: WORKING
```

---

## JOURNEY STEP 3: Navigate to Assets

```
User clicks "Assets" in Configuration Selector
        ↓
Asset Manager opens:
        - Empty list (no assets exist)
        - [+ Create New Asset] button visible and enabled
```

---

## JOURNEY STEP 4: Create First Asset

```
User clicks [+ Create New Asset]
        ↓
Asset Creation Form opens:

┌─────────────────────────────────────────────────────────────────┐
│  CREATE NEW ASSET                                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Asset Name: [High_Risk_Countries________________]              │
│                                                                  │
│  Description: [List of countries classified as high___________] │
│               [risk for AML purposes______________________]     │
│               (REQUIRED)                                        │
│                                                                  │
│  Reference Data Table: [Countries ▼]                            │
│                                                                  │
│  Upload Values: [Choose File] high_risk_countries.csv          │
│                                                                  │
│  ────────────────────────────────────────────────────────────   │
│                                                                  │
│  Preview (first 5 values):                                      │
│  ├── Iran ✓                                                     │
│  ├── North Korea ✓                                              │
│  ├── Syria ✓                                                    │
│  ├── Yemen ✓                                                    │
│  └── Venezuela ✓                                                │
│                                                                  │
│  Validation: ✓ All 45 values valid against Countries table     │
│                                                                  │
│  [Cancel]                              [Save Asset]             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

User clicks [Save Asset]
        ↓
Asset Created:
        - Asset ID: A001
        - Version: 1
        - Status: DRAFT (not linked to any rule yet)
```

---

## JOURNEY STEP 5: Create More Assets

```
User repeats Step 4 for:
        - A002: Low_Risk_Occupations (Reference: Occupations)
        - A003: Sanctioned_Entities (Reference: Entities)
        - A004: APAC_Regional_Watchlist (Reference: Countries)
        
All assets are DRAFT status
```

---

## JOURNEY STEP 6: Build Rules (Link Assets)

```
User navigates to Rules → Creates Ruleset → Adds Rule
        ↓
Rule Creation Form:

        Description: [Flag high-risk country customers__________]
        
        Multiplier Type: [Fundamental Assessment ▼]
        FA Gate: [Geography ▼]
        
        Datapoint: [Customer_Jurisdiction ▼]
        Operator: [INCLUDES ▼]
        Value: [High_Risk_Countries ▼]  ← Asset dropdown
               └── Shows: A001, A002, A003, A004 (all available)
        
User selects A001 (High_Risk_Countries)
User clicks [Save Rule]
        ↓
CRITICAL CHANGE:
        Asset A001 status: DRAFT → SANDBOX
        (Because it's now linked to a rule in this sandbox)
```

---

## JOURNEY STEP 7: Complete Configuration

```
User completes:
        ├── More rules (linking more assets)
        ├── Fundamental Assessment configuration
        └── Market Level Settings

Assets now:
        - A001: SANDBOX (linked to rules)
        - A002: SANDBOX (linked to rules)
        - A003: SANDBOX (linked to rules)
        - A004: DRAFT (not linked to any rule)
```

---

## JOURNEY STEP 8: Submit for Simulation

```
User clicks "Submit for Simulation"
        ↓
System captures SNAPSHOT:
        - All rules frozen
        - All assets frozen (current versions)
        - FA configuration frozen
        ↓
Sandbox Status: WORKING → IN_PROGRESS
        ↓
Simulation runs against full customer population
```

---

## JOURNEY STEP 9: Review Results & Approve

```
Simulation completes
        ↓
Results shown:
        - X customers moved to High Risk
        - Y customers moved to Medium Risk
        ↓
User clicks "Implement"
        ↓
Sandbox Status: TESTING_COMPLETED → PENDING_APPROVAL_1
        ↓
First Approver approves
        ↓
Sandbox Status: PENDING_APPROVAL_1 → PENDING_APPROVAL_2
        ↓
Second Approver approves
```

---

## JOURNEY STEP 10: Promote to Production (MAJOR MILESTONE)

```
User clicks "Approve and Implement"
        ↓
PROMOTION TRANSACTION (Atomic):
        
        1. Rules → Production
        2. Assets → Production
           - A001: SANDBOX → PRODUCTION
           - A002: SANDBOX → PRODUCTION  
           - A003: SANDBOX → PRODUCTION
           - A004: DRAFT (stays DRAFT - not linked to any rule)
        3. FA → Production
        
        ↓
Sandbox Status: PENDING_APPROVAL_2 → IMPLEMENTED
        ↓
ENTERPRISE IS NOW IN PRODUCTION ✓
```

---

## JOURNEY STEP 11: Market Sandboxes Now Available

```
User goes to Dashboard
User clicks "Create New Assessment"
        ↓
Scope selector now shows:
        - Enterprise (XX) ✓ (enabled)
        - India (IN) ✓ (NOW ENABLED!)
        - Belgium (BE) ✓ (NOW ENABLED!)
        - Germany (DE) ✓ (NOW ENABLED!)
        
Why? Because Enterprise Production now exists.
Markets can now "layer" on top of Enterprise.
```

---

## JOURNEY STEP 12: Create India Sandbox

```
User selects India (IN)
        ↓
India Sandbox created:
        - Inherits Enterprise rules as baseline
        - Can add/modify India-specific rules
        ↓
User navigates to Assets:
        - Sees PRODUCTION assets only (A001, A002, A003)
        - A004 is DRAFT, NOT visible to India
        - NO "Create" or "Edit" buttons
        - Can only View and Export
```

---

## JOURNEY STEP 13: India Links Assets to Rules

```
User creates India-specific rule
        ↓
In rule value dropdown:
        - Sees A001, A002, A003 (PRODUCTION assets)
        - Can select and link to India rules
        ↓
User selects A001 for India rule
        ↓
Asset A001 is now referenced by:
        - Enterprise rules
        - India rules
        
(No status change - A001 is already PRODUCTION)
```

---

## JOURNEY STEP 14: India Needs New Asset

```
While working in India sandbox:
        "We need India_PEP_List asset"
        ↓
User CANNOT create in India sandbox
        ↓
User creates Enterprise Sandbox (PARALLEL allowed!)
        - India sandbox stays active
        - Enterprise sandbox created for asset work only
        ↓
In Enterprise sandbox:
        User creates A005: India_PEP_List
        User promotes Enterprise sandbox
        ↓
A005: PRODUCTION ✓
        ↓
Back in India sandbox:
        User refreshes asset list
        Now sees A005
        Links A005 to India rules
```

---

## JOURNEY STEP 15: India Promotes

```
India completes configuration
India submits for simulation
Simulation runs (uses India rules + assets)
Approvers approve
India promotes
        ↓
INDIA IS NOW IN PRODUCTION ✓

System state:
├── Enterprise: PRODUCTION (active)
├── India: PRODUCTION (active, layered on Enterprise)
└── Assets: A001, A002, A003, A005 (all PRODUCTION)
```

---

# PART 4: SANDBOX LIFECYCLE IMPACT ON ASSETS

## Scenario A: Sandbox PROMOTED

```
What happens to assets?

Assets in SANDBOX status:
        └── Change to PRODUCTION status

Assets in DRAFT status (linked to rules):
        └── Change to PRODUCTION status

Assets in DRAFT status (NOT linked to rules):
        └── Stay DRAFT (not part of promotion)

Assets already in PRODUCTION:
        └── No change

Database Tables Updated:
        - refer_da_asset_sta_hist: New status record added
        - refer_da_asset: version marked as PRODUCTION
```

---

## Scenario B: Sandbox REJECTED

```
What happens to assets?

All changes are DISCARDED:
        - New assets created in this sandbox → DELETED (or marked ORPHAN)
        - New versions of existing assets → DISCARDED
        - PRODUCTION assets referenced → No change

User must start fresh sandbox if they want to try again.
```

---

## Scenario C: Sandbox DELETED (Before Promotion)

```
Same as REJECTED:
        - Work is discarded
        - DRAFT assets may become orphaned
        - PRODUCTION assets unaffected
```

---

## Scenario D: Enterprise Updates Asset (While Markets in Production)

```
Current state:
        - A001 V1: PRODUCTION (used by India, Belgium)
        
Enterprise updates A001 → V2:

1. Enterprise sandbox created
2. A001 edited → A001 V2 created
3. Enterprise promotes

Result:
        - A001 V1: ARCHIVED
        - A001 V2: PRODUCTION
        - India: Now uses A001 V2 (automatic)
        - Belgium: Now uses A001 V2 (automatic)
        
Database:
        - refer_da_asset_sta_hist: V1 marked ARCHIVED
        - refer_da_asset_sta_hist: V2 marked PRODUCTION
        - Rules automatically resolve to V2 (latest PRODUCTION)
```

---

# PART 5: ASSET VIEW SCREEN DETAILS

## What to Show in Asset List:

| Field | Always Show | Enterprise Only |
|-------|-------------|-----------------|
| Asset Name | ✓ | ✓ |
| Description | ✓ | ✓ |
| Reference Table | ✓ | ✓ |
| Value Count | ✓ | ✓ |
| Status | ✓ | ✓ |
| Version | Enterprise view | ✓ |
| Last Modified | ✓ | ✓ |
| Modified By | ✓ | ✓ |
| Used In Rules Count | ✓ | ✓ |

## What to Show in Asset Detail View:

```
┌─────────────────────────────────────────────────────────────────┐
│  ASSET DETAILS: High_Risk_Countries                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  BASIC INFO                                                     │
│  ├── Name: High_Risk_Countries                                  │
│  ├── Description: List of countries classified as high risk    │
│  ├── Reference Table: Countries                                 │
│  ├── Status: PRODUCTION                                         │
│  ├── Current Version: V2                                        │
│  └── Last Modified: 2026-01-23 by John Smith                   │
│                                                                  │
│  ────────────────────────────────────────────────────────────   │
│                                                                  │
│  VALUES (45 total)                                [Export CSV]  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Iran                                                       │ │
│  │ North Korea                                                │ │
│  │ Syria                                                      │ │
│  │ Yemen                                                      │ │
│  │ Venezuela                                                  │ │
│  │ Cuba                                                       │ │
│  │ ... (showing 6 of 45)                                     │ │
│  │                                              [Load More]   │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ────────────────────────────────────────────────────────────   │
│                                                                  │
│  USAGE (Where is this asset used?)                              │
│  ├── Enterprise:                                                │
│  │   └── Rule: RS_ENT_001 "High risk country check"           │
│  ├── India:                                                     │
│  │   └── Rule: RS_IND_001 "India jurisdiction check"           │
│  └── Belgium:                                                   │
│      └── Rule: RS_BE_001 "EU compliance check"                 │
│                                                                  │
│  ────────────────────────────────────────────────────────────   │
│                                                                  │
│  VERSION HISTORY                                                │
│  ├── V2 (Current) - 2026-01-23 - Added Cuba                   │
│  └── V1 (Archived) - 2026-01-15 - Initial version              │
│                                                                  │
│  [Close]                           [Edit] ← Only in Enterprise │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

# PART 6: EDGE CASES SUMMARY

| # | Edge Case | Handling |
|---|-----------|----------|
| 1 | Create asset in Market sandbox | BLOCKED - no create button |
| 2 | Edit asset in Market sandbox | BLOCKED - no edit button |
| 3 | Delete asset used in rules | BLOCKED - show rule references |
| 4 | Two users edit same asset | Optimistic locking - conflict resolution |
| 5 | Edit during simulation | Creates new version - simulation uses snapshot |
| 6 | Orphaned asset (not used) | Auto-archive after 90 days |
| 7 | Sandbox rejected | Assets discarded, PRODUCTION unaffected |
| 8 | Enterprise updates asset used by markets | All markets auto-get new version |
| 9 | Asset with invalid values | Validation fails on upload - cannot save |
| 10 | Large asset (10,000+ values) | Paginated view, performance optimization |

---

# SUMMARY

## One-Page Reference:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  ASSET PERMISSIONS                                              │
│  ├── CREATE: Enterprise sandbox only                           │
│  ├── EDIT: Enterprise sandbox only                             │
│  ├── VIEW: Anywhere (always allowed)                           │
│  ├── EXPORT: Anywhere (always allowed)                         │
│  └── DELETE: Enterprise sandbox (if not in use)                │
│                                                                  │
│  WHAT MARKETS SEE                                               │
│  ├── Only PRODUCTION assets                                     │
│  ├── No DRAFT or SANDBOX assets from Enterprise                │
│  └── Read-only (view + export only)                            │
│                                                                  │
│  SANDBOX COEXISTENCE                                            │
│  ├── Enterprise + Market sandboxes: ✅ Allowed                 │
│  ├── Multiple Market sandboxes: ✅ Allowed                     │
│  └── Multiple Enterprise sandboxes: ❌ Not allowed             │
│                                                                  │
│  VERSION RULE                                                   │
│  ├── Only ONE version can be PRODUCTION                        │
│  ├── Old version → ARCHIVED                                     │
│  └── All markets auto-use latest PRODUCTION                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

*Document Complete*
