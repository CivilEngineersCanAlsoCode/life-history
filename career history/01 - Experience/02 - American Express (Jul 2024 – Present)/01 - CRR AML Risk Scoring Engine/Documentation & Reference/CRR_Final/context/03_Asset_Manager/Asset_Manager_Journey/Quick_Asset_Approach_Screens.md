# Creative Approach 1: Quick Asset in Market Sandbox
## Detailed Screen-by-Screen Breakdown

---

## Core Concept

> **User sees:** Create asset in Market sandbox
> **System does:** Creates asset in hidden mini-Enterprise sandbox → auto-promotes

**Result:** User never leaves their Market sandbox, but assets are properly managed at Enterprise level.

---

# SCREEN 1: VIEW ONLY ASSET SCREEN (Dashboard - No Sandbox Active)

## When User Sees This:
- User is on Dashboard (no sandbox open)
- User clicks "View Assets" from navigation

## What User Sees:

```
┌─────────────────────────────────────────────────────────────────┐
│  ASSET MANAGER                                      [Not in Sandbox]│
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ℹ️ Viewing production assets. To create or edit, open a sandbox.│
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  Search: [_______________________] [🔍]     Filter: [All ▼]     │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Name                    │ Type      │ Values │ Last Updated ││
│  ├─────────────────────────┼───────────┼────────┼──────────────┤│
│  │ High_Risk_Countries     │ Countries │ 45     │ 23-Jan-2026  ││
│  │ Low_Risk_Occupations    │ Occupations│ 120   │ 20-Jan-2026  ││
│  │ Sanctioned_Entities     │ Entities  │ 2,340  │ 15-Jan-2026  ││
│  │ APAC_Regional_Watchlist │ Countries │ 12     │ 22-Jan-2026  ││
│  │ India_PEP_List          │ Persons   │ 500    │ 21-Jan-2026  ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Actions per row: [👁 View] [📥 Export]                         │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  [+ Create Asset] ← DISABLED (greyed out)                       │
│  Tooltip: "Open a sandbox to create assets"                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## What's Available:

| Element | State | Action |
|---------|-------|--------|
| Asset List | Shows PRODUCTION assets only | - |
| View Button | ✅ Enabled | Opens asset detail modal |
| Export Button | ✅ Enabled | Downloads CSV |
| Create Button | ❌ Disabled (greyed) | Shows tooltip |
| Edit | ❌ Not shown | - |

---

# SCREEN 2: ENTERPRISE SANDBOX ASSET LISTING

## When User Sees This:
- User is inside Enterprise sandbox
- User clicks "Assets" in Configuration Selector

## What User Sees:

```
┌─────────────────────────────────────────────────────────────────┐
│  SANDBOX: Enterprise (XX) v1               Status: WORKING      │
├─────────────────────────────────────────────────────────────────┤
│  [Rules]    [Assets ✓]    [Fundamental Assessment]              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  ASSET MANAGER                               [Enterprise Sandbox]│
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [+ Create New Asset]    [📥 Export All]                        │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  Search: [_______________________] [🔍]     Filter: [All ▼]     │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Name                    │ Status     │ Version │ Actions    ││
│  ├─────────────────────────┼────────────┼─────────┼────────────┤│
│  │ High_Risk_Countries     │ PRODUCTION │ V2      │ 👁 ✏️ 📥   ││
│  │ Low_Risk_Occupations    │ PRODUCTION │ V1      │ 👁 ✏️ 📥   ││
│  │ Sanctioned_Entities     │ PRODUCTION │ V3      │ 👁 ✏️ 📥   ││
│  │ New_Draft_Asset         │ DRAFT      │ V1      │ 👁 ✏️ 📥 🗑││
│  │ Sandbox_Work_Asset      │ SANDBOX    │ V1      │ 👁 ✏️ 📥 🗑││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Legend:                                                        │
│  • PRODUCTION = Live in production                              │
│  • SANDBOX = Modified in this sandbox (not yet promoted)        │
│  • DRAFT = Created but not linked to any rule                   │
│                                                                  │
│  Actions: 👁 View   ✏️ Edit   📥 Export   🗑 Delete             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## What's Available:

| Element | State | Action |
|---------|-------|--------|
| Asset List | Shows ALL statuses (PRODUCTION + SANDBOX + DRAFT) | - |
| Create Button | ✅ Enabled | Opens create form |
| View Button | ✅ Enabled | Opens detail modal |
| Edit Button | ✅ Enabled | Opens edit form (creates new version for PRODUCTION) |
| Export Button | ✅ Enabled | Downloads CSV |
| Delete Button | ✅ Enabled for DRAFT/SANDBOX | Only if not used in rules |

## Status Column Behavior:

| Status | Meaning |Can Edit? | Can Delete? |
|--------|---------|----------|-------------|
| PRODUCTION | Already live | ✅ YES (creates V+1) | ❌ NO |
| SANDBOX | Edited in this sandbox | ✅ YES | ✅ YES (if not in rule) |
| DRAFT | Created, not in rule | ✅ YES | ✅ YES |

---

# SCREEN 3: MARKET SANDBOX ASSET LISTING (with Quick Asset!)

## When User Sees This:
- User is inside Market sandbox (e.g., India)
- User clicks "Assets" in Configuration Selector

## What User Sees:

```
┌─────────────────────────────────────────────────────────────────┐
│  SANDBOX: India (IN) v1                     Status: WORKING     │
├─────────────────────────────────────────────────────────────────┤
│  [Rules]    [Assets ✓]    [Fundamental Assessment]              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  ASSET MANAGER                                    [India Sandbox]│
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [+ Quick Asset]    [📥 Export All]                             │
│   ↑                                                              │
│   This is the magic button!                                     │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  ℹ️ You can VIEW and LINK assets to your rules here.            │
│     Need a new asset? Use "Quick Asset" above.                  │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  Search: [_______________________] [🔍]     Filter: [All ▼]     │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Name                    │ Type       │ Values │ Actions     ││
│  ├─────────────────────────┼────────────┼────────┼─────────────┤│
│  │ High_Risk_Countries     │ Countries  │ 45     │ 👁 📥       ││
│  │ Low_Risk_Occupations    │ Occupations│ 120    │ 👁 📥       ││
│  │ Sanctioned_Entities     │ Entities   │ 2,340  │ 👁 📥       ││
│  │ APAC_Regional_Watchlist │ Countries  │ 12     │ 👁 📥       ││
│  │ India_PEP_List          │ Persons    │ 500    │ 👁 📥       ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Actions: 👁 View   📥 Export                                   │
│  (No Edit button - assets are read-only in Market sandbox)     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## What's Available:

| Element | State | Action |
|---------|-------|--------|
| Asset List | Shows PRODUCTION assets only | - |
| **Quick Asset Button** | ✅ Enabled | **Opens Quick Asset wizard** |
| View Button | ✅ Enabled | Opens detail modal |
| Export Button | ✅ Enabled | Downloads CSV |
| Edit Button | ❌ Not shown | - |
| Delete Button | ❌ Not shown | - |

## Key Differences from Enterprise:

| Feature | Enterprise Sandbox | Market Sandbox |
|---------|-------------------|----------------|
| Create button | "Create New Asset" | "Quick Asset" |
| Edit button | ✅ Shown | ❌ Not shown |
| Delete button | ✅ Shown (for DRAFT/SANDBOX) | ❌ Not shown |
| Assets shown | ALL (PRODUCTION + SANDBOX + DRAFT) | PRODUCTION only |
| Status column | ✅ Shown | ❌ Not shown (all are PRODUCTION) |

---

# SCREEN 4: QUICK ASSET WIZARD (Market Sandbox Special Feature)

## When User Clicks "Quick Asset":

```
┌─────────────────────────────────────────────────────────────────┐
│  QUICK ASSET CREATION                                    [X]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ⚡ Create a new asset quickly without leaving your sandbox.    │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  Asset Name *                                                    │
│  [India_Special_Watchlist_________________]                     │
│                                                                  │
│  Description *                                                   │
│  [Special watchlist for India compliance___]                    │
│  [requirements and local regulations_______]                    │
│                                                                  │
│  Reference Data Table *                                         │
│  [Countries                              ▼]                     │
│                                                                  │
│  Upload Values *                                                 │
│  [Choose File]  india_watchlist.csv                             │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  Preview (first 5 values):                                      │
│  ├── Pakistan ✓                                                 │
│  ├── Afghanistan ✓                                              │
│  ├── Bangladesh ✓                                               │
│  └── (3 of 8 shown)                                             │
│                                                                  │
│  ✓ All 8 values validated against Countries table              │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  ℹ️ This asset will be published immediately.                   │
│     You can use it in your rules right away.                    │
│                                                                  │
│  [Cancel]                           [Create & Publish Asset]   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## What Happens Behind the Scenes:

```
User clicks [Create & Publish Asset]
        ↓
System (hidden from user):
        1. Creates temporary Enterprise sandbox
        2. Creates asset in that sandbox
        3. Auto-approves (or uses pre-approval for quick assets)
        4. Promotes Enterprise sandbox
        5. Closes temporary sandbox
        ↓
Result:
        - Asset is now PRODUCTION
        - User sees success message
        - Asset appears in list immediately
        ↓
User continues working in India sandbox
        - Can now link new asset to rules
```

## Success Message:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  ✅ Asset Created Successfully!                                │
│                                                                  │
│  "India_Special_Watchlist" is now ready to use.                │
│                                                                  │
│  [Use in Rules]          [Close]                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

# SCREEN 5: ASSET DETAIL VIEW (Same Everywhere)

## Modal that opens when clicking "View":

```
┌─────────────────────────────────────────────────────────────────┐
│  ASSET DETAILS                                           [X]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─ BASIC INFORMATION ─────────────────────────────────────────┐│
│  │                                                              ││
│  │  Name:           High_Risk_Countries                        ││
│  │  Description:    List of countries classified as high risk  ││
│  │                  for AML purposes                           ││
│  │  Reference Table: Countries                                  ││
│  │  Status:         PRODUCTION                                  ││
│  │  Version:        V2                                          ││
│  │  Last Modified:  23-Jan-2026 by John Smith                  ││
│  │                                                              ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─ VALUES (45 total) ────────────────────────────── [📥 Export]│
│  │                                                              ││
│  │  Search values: [_______________] [🔍]                      ││
│  │                                                              ││
│  │  ┌────────────────────────────────────────────────────────┐ ││
│  │  │ Iran                                                    │ ││
│  │  │ North Korea                                             │ ││
│  │  │ Syria                                                   │ ││
│  │  │ Yemen                                                   │ ││
│  │  │ Venezuela                                               │ ││
│  │  │ Cuba                                                    │ ││
│  │  │ Myanmar                                                 │ ││
│  │  │ ... (showing 7 of 45)              [Load More]         │ ││
│  │  └────────────────────────────────────────────────────────┘ ││
│  │                                                              ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─ USAGE (Where is this asset used?) ─────────────────────────┐│
│  │                                                              ││
│  │  Markets using this asset:                                  ││
│  │  ├── Enterprise: 3 rules                                    ││
│  │  ├── India: 2 rules                                         ││
│  │  ├── Belgium: 1 rule                                        ││
│  │  └── Australia: 1 rule                                      ││
│  │                                                              ││
│  │  [View Detailed Usage]                                      ││
│  │                                                              ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─ VERSION HISTORY ───────────────────────────────────────────┐│
│  │                                                              ││
│  │  V2 (Current) - 23-Jan-2026 - Added Cuba, Myanmar          ││
│  │  V1 (Archived) - 15-Jan-2026 - Initial version              ││
│  │                                                              ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  [Close]                                                        │
│                     ↑                                           │
│  (Edit button shown only in Enterprise sandbox)                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

# SUMMARY: QUICK REFERENCE

## Button Visibility Matrix:

| Button | Dashboard | Enterprise Sandbox | Market Sandbox |
|--------|-----------|-------------------|----------------|
| Create Asset | ❌ Disabled | ✅ "Create New Asset" | ✅ "Quick Asset" |
| Edit | ❌ Hidden | ✅ Shown | ❌ Hidden |
| Delete | ❌ Hidden | ✅ (for DRAFT/SANDBOX) | ❌ Hidden |
| View | ✅ Shown | ✅ Shown | ✅ Shown |
| Export | ✅ Shown | ✅ Shown | ✅ Shown |

## Assets Shown Matrix:

| Asset Status | Dashboard | Enterprise Sandbox | Market Sandbox |
|--------------|-----------|-------------------|----------------|
| PRODUCTION | ✅ | ✅ | ✅ |
| SANDBOX | ❌ | ✅ | ❌ |
| DRAFT | ❌ | ✅ | ❌ |
| ARCHIVED | ❌ | ❌ | ❌ |

---

# EDGE CASE: QUICK ASSET INTERRUPTION

## What if Quick Asset fails?

```
User clicks [Create & Publish Asset]
        ↓
System creating hidden Enterprise sandbox...
        ↓
ERROR: Validation fails OR system error
        ↓
User sees:

┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  ❌ Asset Creation Failed                                       │
│                                                                  │
│  Error: Some values are not valid against Countries table.     │
│                                                                  │
│  Invalid values:                                                │
│  - "Narnia" (not found in Countries)                           │
│  - "Westeros" (not found in Countries)                         │
│                                                                  │
│  [Fix and Retry]          [Cancel]                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Hidden Enterprise sandbox is automatically cleaned up.
User stays in India sandbox, can fix and retry.
```

---

*Document Complete*
