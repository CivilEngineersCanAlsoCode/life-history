# Hybrid Approach: Enterprise + Market Asset Creation
## Simplified Architecture with Flexibility

---

## 🎯 The Hybrid Model

| Scope | Create New Asset | Edit Enterprise Asset | Edit Own Asset | Share with Other Markets |
|-------|-----------------|----------------------|----------------|-------------------------|
| **Enterprise** | ✅ YES | ✅ YES | ✅ YES | ✅ (all markets) |
| **Market** | ✅ YES (new only) | ❌ NO | ✅ YES (own only) | ✅ YES |

**Key Rules:**
1. Enterprise creates "global" assets used everywhere
2. Markets CANNOT edit Enterprise assets (read-only for them)
3. Markets CAN create NEW assets for regional/local needs
4. Market-created assets CAN be shared with other markets

---

## What This Simplifies

### REMOVED Complexity:
- ❌ No copy-on-write for Enterprise assets
- ❌ No "copies" of Enterprise assets per market
- ❌ No confusion about "original vs copy"

### KEPT Flexibility:
- ✅ Markets can create regional assets
- ✅ Markets can share with neighboring markets
- ✅ Enterprise controls global assets

---

# SIMPLIFIED USER JOURNEY

## PHASE A: ENTERPRISE ASSET CREATION

```
Day 1: Enterprise sandbox created
       ↓
Day 2: Enterprise creates global assets
       - A001: High_Risk_Countries (global list)
       - A002: Low_Risk_Occupations (global list)
       - A003: Sanctioned_Entities (global list)
       ↓
Day 3: Enterprise links to rules, simulates, promotes
       ↓
Day 4: Enterprise PRODUCTION active
       Assets A001, A002, A003 = PRODUCTION status
```

---

## PHASE B: MARKET USES ENTERPRISE ASSETS (Read-Only)

```
Day 5: India sandbox created
       ↓
India opens Asset Manager:
       
       ┌──────────────────────────────────────────────┐
       │  ASSET LIST (India Sandbox View)             │
       ├──────────────────────────────────────────────┤
       │                                              │
       │  ENTERPRISE ASSETS (Read-Only):              │
       │  ├── A001: High_Risk_Countries    [View]     │
       │  ├── A002: Low_Risk_Occupations   [View]     │
       │  └── A003: Sanctioned_Entities    [View]     │
       │                                              │
       │  [+ Add New Asset] ← India CAN create new    │
       │                                              │
       └──────────────────────────────────────────────┘

India creates rule:
       - Uses A001 (Enterprise asset)
       - Read-only reference, no copy needed
```

**Key Difference from Current Design:**
- India sees [View] button, NOT [Edit] or [Copy]
- India cannot modify Enterprise assets in any way
- India can only USE them in rules

---

## PHASE C: MARKET CREATES NEW ASSET (Regional Needs)

**Scenario:** India needs an APAC-specific watchlist that Enterprise doesn't have.

```
Day 6: India clicks [+ Add New Asset]
       ↓
India creates:
       - Asset Name: "APAC_Regional_Watchlist"
       - Description: "Countries with APAC-specific risks"
       - Reference Table: Countries
       - Values: [Pakistan, Myanmar, Cambodia, Laos]
       ↓
Asset Created:
       - Asset ID: A004
       - Version: 1
       - Status: DRAFT
       - Scope: INDIA (market-level)
```

---

## PHASE D: MARKET LINKS OWN ASSET TO RULES

```
India creates rule:
       - Datapoint: Customer_Jurisdiction
       - Operator: INCLUDES
       - Value: A004 (APAC_Regional_Watchlist) ← India's own asset
       ↓
A004 Status: DRAFT → SANDBOX
```

---

## PHASE E: MARKET PROMOTES TO PRODUCTION

```
Day 7: India submits for simulation
       Uses: A001, A002 (Enterprise) + A004 (India's own)
       ↓
Day 8: India promotes to production
       ↓
Asset States:
       - A001, A002, A003: PRODUCTION (Enterprise) - unchanged
       - A004: PRODUCTION (India-created, India-owned)
```

---

## PHASE F: ANOTHER MARKET WANTS TO USE INDIA'S ASSET

**Scenario:** Australia has similar APAC regulations and wants to use A004.

```
Day 9: Australia sandbox created
       ↓
Australia opens Asset Manager:
       
       ┌──────────────────────────────────────────────┐
       │  ASSET LIST (Australia Sandbox View)         │
       ├──────────────────────────────────────────────┤
       │                                              │
       │  ENTERPRISE ASSETS (Read-Only):              │
       │  ├── A001: High_Risk_Countries    [View]     │
       │  ├── A002: Low_Risk_Occupations   [View]     │
       │  └── A003: Sanctioned_Entities    [View]     │
       │                                              │
       │  MARKET ASSETS (Shareable):                  │
       │  └── A004: APAC_Regional_Watchlist [View]    │
       │           (Created by: India)                │
       │           Status: PRODUCTION                 │
       │                                              │
       │  [+ Add New Asset]                           │
       │                                              │
       └──────────────────────────────────────────────┘

Australia creates rule:
       - Uses A004 (India's asset)
       - Read-only reference
       - No copy, no edit
```

**What Australia CAN do:**
- ✅ View A004 values
- ✅ Link A004 to their rules
- ✅ Use A004 in simulation

**What Australia CANNOT do:**
- ❌ Edit A004 (it's India's asset)
- ❌ Copy A004 (no copies in this model)

---

## PHASE G: UPDATING MARKET-CREATED ASSETS

### Who Can Edit A004 (APAC_Regional_Watchlist)?

| Actor | Can Edit? | Reason |
|-------|-----------|--------|
| Enterprise | ❌ NO | Not the creator scope |
| India | ✅ YES | Creator scope |
| Australia | ❌ NO | Just a user |

### Update Flow:

```
Scenario: Need to add "Vietnam" to A004

Step 1: India creates new sandbox
        (No Enterprise sandbox can exist - mutual exclusion)
        
Step 2: India edits A004
        Adds: Vietnam
        Creates: A004 V2
        
Step 3: India runs simulation
        Shows impact on: India rules using A004
        
Step 4: India promotes
        A004 V1 → ARCHIVED
        A004 V2 → PRODUCTION
        
Step 5: Australia (using A004) automatically gets V2
        (Single active version rule)
```

**Important:** India's simulation only shows impact on INDIA.
Australia's impact is not calculated until Australia runs their own simulation.

---

## KEY ARCHITECTURAL DECISION: Impact Calculation for Shared Assets

### Problem:
- A004 is used by India AND Australia
- India updates A004
- India's simulation only shows India impact
- Australia doesn't know about the change until later

### ✅ SELECTED: Option 3 - Enterprise Treatment for Shared Assets

> **Rule: If an asset is used by 2+ markets, it is treated like an Enterprise asset.**
> 
> **Updates MUST go through Enterprise sandbox.**
> **Enterprise simulation shows impact on ALL markets.**

---

## How Option 3 Works in Detail:

### STEP 1: Asset Starts as Market-Level

```
Day 1: India creates A004 (APAC_Regional_Watchlist)
       - Created by: India
       - Used by: India only
       - Status: PRODUCTION (after India promotes)
       - Classification: MARKET-LEVEL ASSET ✓
       
       → India can edit this asset in India sandbox
```

### STEP 2: Another Market Links the Asset

```
Day 10: Australia creates sandbox
        Australia links A004 to their rules
        Australia promotes
        
        Now A004 is used by:
        - India (1)
        - Australia (2)
        
        Total users: 2+ markets
        
        ⚠️ SYSTEM AUTOMATICALLY RECLASSIFIES:
        A004 is now: ENTERPRISE-LEVEL ASSET
```

### STEP 3: Editing Rules Change

```
BEFORE (Single Market Usage):
├── India creates sandbox
├── India edits A004
├── India simulates (India impact only)
└── India promotes

AFTER (2+ Market Usage):
├── India CANNOT create sandbox that edits A004 (blocked!)
├── Must create ENTERPRISE sandbox
├── Enterprise edits A004
├── Enterprise simulates (India + Australia impact)
└── Enterprise promotes
```

### User Experience When Market Tries to Edit Shared Asset:

```
┌─────────────────────────────────────────────────────────────────┐
│  Cannot Edit This Asset                                         │
│                                                                  │
│  "APAC_Regional_Watchlist" is used by multiple markets:         │
│  - India                                                        │
│  - Australia                                                    │
│                                                                  │
│  Assets used by 2+ markets can only be edited through an       │
│  Enterprise sandbox to ensure impact is calculated for all      │
│  affected markets.                                               │
│                                                                  │
│  [Create Enterprise Sandbox]    [Cancel]                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Updated Asset Classification Logic:

| Condition | Classification | Who Can Edit? |
|-----------|----------------|---------------|
| Created by Enterprise | ENTERPRISE-LEVEL | Enterprise only |
| Created by Market, used by 1 market | MARKET-LEVEL | Creator market |
| Created by Market, used by 2+ markets | **PROMOTED TO ENTERPRISE-LEVEL** | Enterprise only |

---

## Visual Flow: Asset Lifecycle with Option 3

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Asset A004 Created by India                                    │
│  ├── Status: MARKET-LEVEL                                       │
│  ├── Users: India only                                          │
│  └── India can edit ✓                                           │
│                                                                  │
│          ↓ (Australia links to their rules)                     │
│                                                                  │
│  Asset A004 Used by Multiple Markets                            │
│  ├── Status: PROMOTED TO ENTERPRISE-LEVEL                       │
│  ├── Users: India, Australia                                    │
│  └── Only Enterprise can edit ✓                                 │
│                                                                  │
│          ↓ (To update A004 now)                                 │
│                                                                  │
│  Enterprise sandbox required                                    │
│  ├── Enterprise edits A004 → Creates V2                        │
│  ├── Enterprise simulation shows impact on                      │
│  │   ├── India rules                                            │
│  │   └── Australia rules                                        │
│  └── Enterprise promotes → All markets get V2                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## What Happens to Mutual Exclusion?

With Option 3, the mutual exclusion logic expands:

| Situation | Can Create India Sandbox? | Can Create Enterprise Sandbox? |
|-----------|--------------------------|-------------------------------|
| No sandboxes exist | ✅ YES | ✅ YES |
| India sandbox exists | ✅ (already exists) | ❌ NO (blocked) |
| Enterprise sandbox exists | ❌ NO | ✅ (already exists) |
| India wants to edit MARKET-LEVEL asset A005 | ✅ Create India sandbox | N/A |
| India wants to edit ENTERPRISE-LEVEL asset A004 | ❌ BLOCKED | ✅ Must create Enterprise |

---

## Edge Case: What If All Markets Stop Using the Asset?

```
Scenario:
- A004 used by India + Australia (ENTERPRISE-LEVEL)
- Australia removes A004 from all their rules
- Now only India uses A004

Question: Does A004 go back to MARKET-LEVEL?

Answer: Once promoted to ENTERPRISE-LEVEL, it STAYS Enterprise-level.
        This prevents flip-flopping and confusion.
        Classification is "high water mark" - only goes up, never down.
```

---

### Recommendation (SELECTED):
**Option 3 is chosen as the final design.**

---

## WHAT IF AUSTRALIA NEEDS DIFFERENT VALUES?

**Scenario:** India has A004 with [Pakistan, Myanmar, Cambodia, Laos]
Australia wants [Pakistan, Myanmar, Cambodia, Laos, **Indonesia**]

### In This Model:

```
Australia CANNOT edit A004 (not the creator)
Australia CANNOT copy A004 (no copies allowed)

Australia's Options:

Option A: Request India to add Indonesia
          - India adds Indonesia to A004
          - But then India also gets Indonesia (may not want it)
          
Option B: Australia creates own asset
          - Creates A005: "Australia_Regional_Watchlist"
          - Values: [Pakistan, Myanmar, Cambodia, Laos, Indonesia]
          - Uses A005 instead of A004
          - Duplicates most values, but Australia controls it
```

**Tradeoff:** Less flexibility than copy-on-write, but MUCH simpler system.

---

# COMPLETE ASSET VISIBILITY & EDITABILITY MATRIX

## What User Sees in Asset Manager:

| Asset Type | Your Scope | Visible? | Can Link? | Can Edit? |
|------------|-----------|----------|-----------|-----------|
| Enterprise PRODUCTION | Any | ✅ YES | ✅ YES | ❌ NO |
| Enterprise DRAFT/SANDBOX | Enterprise | ✅ YES | ✅ YES | ✅ YES |
| Enterprise DRAFT/SANDBOX | Market | ❌ NO | ❌ NO | ❌ NO |
| Own Market PRODUCTION | Same Market | ✅ YES | ✅ YES | ✅ YES (new version) |
| Own Market DRAFT/SANDBOX | Same Market | ✅ YES | ✅ YES | ✅ YES |
| Other Market PRODUCTION | Your Market | ✅ YES | ✅ YES | ❌ NO |
| Other Market DRAFT/SANDBOX | Your Market | ❌ NO | ❌ NO | ❌ NO |

## Summary:
- **Enterprise PRODUCTION:** Everyone can use, nobody (except Enterprise) edits
- **Your own assets:** Full control
- **Other market's PRODUCTION:** Can use, cannot edit
- **Anyone's DRAFT/SANDBOX:** Not visible outside their scope

---

# EDGE CASES IN THIS MODEL

## Edge Cases That EXIST:

| Edge Case | Description | Handling |
|-----------|-------------|----------|
| India edits asset used by Australia | Version auto-update | Australia gets new version automatically |
| Two markets create similar assets | Duplication | Allowed - each market controls their own |
| Concurrent edit (same market) | Two users edit same asset | Optimistic locking conflict resolution |
| Delete asset in use | Asset used in rules | Block deletion, show references |
| Orphaned assets | Asset not used anywhere | Auto-archive after 90 days |

## Edge Cases That DON'T EXIST:

| Edge Case | Why It's Gone |
|-----------|--------------|
| Copy-on-write decision | No copies allowed |
| Copy naming conflicts | No copies |
| Copy vs original confusion | No copies |
| Who can edit Enterprise asset? | Only Enterprise |
| Multiple copies per market | No copies |

---

# PROS AND CONS

## PROS:

| Benefit | Explanation |
|---------|-------------|
| ✅ **Simpler than current** | No copy-on-write logic |
| ✅ **Market flexibility** | Markets can create regional assets |
| ✅ **Clear ownership** | Creator scope owns the asset |
| ✅ **Sharing without complexity** | Other markets can use, not edit |
| ✅ **Enterprise protected** | No one can modify Enterprise assets |

## CONS:

| Drawback | Explanation |
|----------|-------------|
| ❌ **No customization of Enterprise** | Markets can't have their version of Enterprise asset |
| ❌ **Duplication possible** | If Australia needs slightly different values, must create new asset |
| ❌ **Shared asset updates** | When India updates, Australia may not know immediately |

---

# FINAL SUMMARY

## This Hybrid Model:

```
┌─────────────────────────────────────────────────────────┐
│                                                          │
│  ENTERPRISE ASSETS                                       │
│  ├── Created by: Enterprise only                        │
│  ├── Edited by: Enterprise only                         │
│  └── Used by: Everyone                                   │
│                                                          │
│  MARKET ASSETS                                           │
│  ├── Created by: Any market                             │
│  ├── Edited by: Creator market only                     │
│  └── Used by: Any market (read-only)                    │
│                                                          │
│  NO COPIES ALLOWED                                       │
│  ├── No "High_Risk_Countries_IN"                        │
│  └── Markets create NEW assets if they need different   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Complexity Score:
- Current Design (with copies): 🔴🔴🔴🔴🔴 (High)
- Enterprise-Only: 🟢 (Low)
- **This Hybrid Model:** 🟡🟡 (Medium-Low)

---

*Document End*
