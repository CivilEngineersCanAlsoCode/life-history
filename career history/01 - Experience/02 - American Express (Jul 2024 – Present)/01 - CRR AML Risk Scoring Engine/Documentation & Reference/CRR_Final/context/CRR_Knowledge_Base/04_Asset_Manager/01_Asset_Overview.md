# Asset Manager Overview

## What is an Asset?

An **Asset** is a reusable list of values that can be used in multiple rules across the CRR system.

### Asset Characteristics
| Attribute | Description |
|-----------|-------------|
| **Content** | List of values from a reference data table |
| **Format** | Stored as JSON in database |
| **Versioning** | Every edit creates new immutable version |
| **Linkage** | Linked to exactly one reference data table |
| **Usage** | Can be used in multiple rules across markets |

### Example Assets
| Asset Name | Reference Table | Values |
|------------|-----------------|--------|
| High_Risk_Countries | Countries | Iran, North Korea, Syria, Cuba |
| Cash_Intensive_Industries | Industries | Casino, Money Services, Jewelry |
| Prohibited_Occupations | Occupations | Arms Dealer, Unlicensed Broker |
| Sensitive_Products | Products | Private Banking, Correspondent Banking |

---

## Asset Lifecycle States

```
┌────────────┐     Link to rule     ┌────────────┐    Promote     ┌────────────┐
│   DRAFT    │ ─────────────────▶   │  SANDBOX   │ ──────────────▶│ PRODUCTION │
└────────────┘                      └────────────┘                └────────────┘
     │                                    │                              │
     │ Delete                             │ Edit                         │ Edit
     ▼                                    ▼                              ▼
┌────────────┐                      ┌────────────┐                ┌────────────┐
│  DELETED   │                      │  V2 in     │                │ V2 created │
└────────────┘                      │  Sandbox   │                │ in Sandbox │
                                    └────────────┘                └────────────┘
                                                                        │
                                                                        │ Old version
                                                                        ▼
                                                                  ┌────────────┐
                                                                  │  ARCHIVED  │
                                                                  └────────────┘
```

### State Definitions

| State | When? | What Can User Do? |
|-------|-------|-------------------|
| **DRAFT** | Asset created but not linked to any rule | Edit, Delete |
| **SANDBOX** | Asset linked to rule in active sandbox | Edit (creates new version) |
| **PRODUCTION** | Asset promoted with sandbox | Read-only; Edit creates V2 |
| **ARCHIVED** | Old version replaced by newer | Read-only; Retained for audit |
| **DELETED** | Soft-deleted, not in use | Cannot be recovered |

---

## Asset Versioning

### Version Creation Rules

| Trigger | Action |
|---------|--------|
| Create new asset | V1 created in DRAFT |
| Link DRAFT to rule | V1 moves to SANDBOX |
| Edit SANDBOX asset (before submit) | V1 updated inline |
| Submit sandbox | V1 frozen |
| Edit after submit | V2 created |
| Promote to production | V(sandbox) → PRODUCTION |
| Old production version | V(old) → ARCHIVED |

### Example Version History
```
Asset: High_Risk_Countries

Version | State      | Content                       | Date
--------|------------|-------------------------------|------------
V1      | ARCHIVED   | [Iran, North Korea]           | 2024-01-01
V2      | ARCHIVED   | [Iran, North Korea, Syria]    | 2024-06-15
V3      | PRODUCTION | [Iran, NK, Syria, Cuba]       | 2025-01-20
V4      | SANDBOX    | [Iran, NK, Syria, Cuba, Yemen]| 2025-01-24
```

---

## Enterprise-Only Asset Creation (FINAL Decision)

### Key Rule
> **Assets can ONLY be created at the Enterprise level.**
> Market sandboxes can USE existing assets but cannot CREATE new ones.

### Rationale
1. Single source of truth for asset definitions
2. Prevents duplicate assets across markets
3. Ensures consistent values for cross-market rules
4. Simplifies governance and audit

### How Markets Use Assets

| Action | Enterprise Sandbox | Market Sandbox |
|--------|-------------------|----------------|
| Create new asset | ✅ Yes | ❌ No |
| Edit existing asset | ✅ Yes | ⚠️ Only if market-exclusive |
| Use asset in rule | ✅ Yes | ✅ Yes (from Production) |
| View all assets | ✅ Yes | ✅ Yes |

### Market-Exclusive Asset
An asset is **market-exclusive** if:
- It is ONLY used by rules in ONE market
- No other market's rules reference it
- In this case, that market CAN edit it

---

## Quick Asset Feature

When creating a rule and the needed asset doesn't exist:

### Flow
1. User is creating/editing rule
2. User selects datapoint (e.g., Customer_Country)
3. Asset dropdown shows available assets
4. User clicks **"+ Create Quick Asset"**
5. Modal opens with:
   - Asset Name (required)
   - Description (optional)
   - Reference Table (auto-set based on datapoint)
   - Values (multi-select from reference table)
6. User saves
7. New asset immediately available in dropdown
8. Asset created in DRAFT state
9. When rule is saved, asset moves to SANDBOX

### Quick Asset Rules
- Quick Asset inherits reference table from selected datapoint
- Only values valid in that reference table can be added
- Quick Asset follows normal versioning after creation

---

## Cross-Market Asset Usage

### Scenario
Asset "High_Risk_Countries" is used by:
- Enterprise rules
- India market rules
- China market rules

### What Happens When Asset Needs Update?

| Who Needs to Update? | What Must They Do? |
|---------------------|-------------------|
| Any market | Create Enterprise sandbox |
| Enterprise | Edit asset in Enterprise sandbox |
| All markets | Wait for Enterprise promotion |

### Why?
- Asset used by 2+ markets is treated as Enterprise asset
- Prevents one market from breaking another market's rules
- Ensures coordinated testing and promotion

---

*Next: See `02_Asset_Visibility_Rules.md` for visibility by sandbox type.*
*Next: See `03_Asset_Editing_Rules.md` for editing permissions.*
