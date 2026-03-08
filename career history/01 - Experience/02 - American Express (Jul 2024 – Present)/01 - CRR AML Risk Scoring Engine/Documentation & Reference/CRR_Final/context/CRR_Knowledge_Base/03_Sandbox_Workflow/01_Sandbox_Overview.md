# Sandbox Workflow Overview

## What is a Sandbox?

A **Sandbox** is a versioned workspace where all configuration changes are made before being promoted to production. It ensures:
- All changes are tested together
- No untested combinations reach production
- Complete audit trail exists

---

## Sandbox Types

### Enterprise Sandbox
| Attribute | Value |
|-----------|-------|
| **Scope** | All markets globally |
| **Asset Visibility** | All assets |
| **Asset Editability** | All assets (with versioning) |
| **Rule Editability** | All rules across all markets |
| **Maximum Count** | Only ONE can exist at a time |
| **Use Case** | Enterprise-wide configuration changes |

### Market Sandbox
| Attribute | Value |
|-----------|-------|
| **Scope** | Single market only (e.g., India) |
| **Asset Visibility** | All assets (production + draft) |
| **Asset Editability** | Draft assets OR market-exclusive assets |
| **Rule Editability** | Only rules for that market |
| **Maximum Count** | Multiple can coexist (different markets) |
| **Use Case** | Market-specific configuration changes |

---

## Coexistence Rules

```
┌────────────────────────────────────────────────────────────────┐
│                    SANDBOX COEXISTENCE MATRIX                   │
├────────────────────┬─────────────────┬─────────────────────────┤
│ Active Sandbox     │ Enterprise      │ Market Sandboxes        │
├────────────────────┼─────────────────┼─────────────────────────┤
│ None               │ ✅ Can create   │ ✅ Can create any       │
│ Enterprise exists  │ ✅ (is active)  │ ✅ Markets CAN coexist  │
│ Market(s) exist    │ ✅ Can create   │ ✅ Other markets OK     │
└────────────────────┴─────────────────┴─────────────────────────┘
```

**Key Decision**: Enterprise and Market sandboxes **CAN coexist** (as per final design decision).

---

## Sandbox Lifecycle States

```
                    ┌─────────────────┐
                    │     CREATED     │ ← User creates sandbox
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
         ┌─────────│     WORKING     │←────────┐
         │         └────────┬────────┘         │
         │                  │                  │
         │ Delete           │ Submit           │ Reject
         │                  ▼                  │
         │         ┌─────────────────┐         │
         │         │   SUBMITTED     │         │
         │         └────────┬────────┘         │
         │                  │                  │
         │                  │ Simulate         │
         │                  ▼                  │
         │         ┌─────────────────┐         │
         │         │   SIMULATED     │─────────┤
         │         └────────┬────────┘         │
         │                  │                  │
         │                  │ Approve 1        │
         │                  ▼                  │
         │         ┌─────────────────┐         │
         │         │   APPROVAL_1    │─────────┤
         │         └────────┬────────┘         │
         │                  │                  │
         │                  │ Approve 2        │
         │                  ▼                  │
         │         ┌─────────────────┐         │
         │         │   APPROVAL_2    │─────────┘
         │         └────────┬────────┘
         │                  │
         │                  │ Promote
         │                  ▼
         │         ┌─────────────────┐
         └────────▶│    PROMOTED     │
                   │  (MERGED_PROD)  │
                   └─────────────────┘
```

### Status Definitions

| Status | Code | What Can User Do? |
|--------|------|-------------------|
| **WORKING** | 1 | Edit rules, assets, FA; Submit or Delete |
| **SUBMITTED** | 2 | Wait for simulation; Cannot edit |
| **SIMULATED** | 4 | View results; Request approval or modify |
| **APPROVAL_1** | 5 | Wait for second approval |
| **APPROVAL_2** | 6 | Promote to production or reject |
| **REJECTED** | 7 | Modify and resubmit |
| **PROMOTED** | 8 | Sandbox closed; Changes in production |

---

## Simulation Skip Rule

| Condition | Simulation Requirement |
|-----------|------------------------|
| Rules changed | ✅ Simulation mandatory |
| Only FA scores changed | ⏭️ Simulation can be skipped |
| Only assets changed (no rule logic change) | Depends on business rule |

---

## Approval Requirements

### Two-Person Rule
- **Approval 1** and **Approval 2** must be by **different users**
- Same user cannot approve both levels
- Approver cannot be the person who made the changes

### Approval Information Required
- Justification text (why these changes are needed)
- Reference to any compliance tickets
- Business impact assessment

---

## What Happens on Promotion?

When a sandbox is promoted to production:

1. **Assessment Table**
   - Old production version: `act_in = FALSE`, `hist_ts` set
   - New production version: `act_in = TRUE`

2. **Asset Table**
   - Sandbox assets: Status → PRODUCTION
   - Old production asset versions: Status → ARCHIVE

3. **Rules Table**
   - New rules copied to production assessment
   - Asset references updated to production versions

---

*Next: See `02_Sandbox_Operations.md` for detailed operation flows.*
