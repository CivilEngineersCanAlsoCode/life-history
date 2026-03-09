# CRR Roles & Permissions

## User Types

CRR has **exactly 2 user types** with distinct access levels.

---

## User Type 1: Viewer (Market Compliance Officer)

### Profile
| Attribute | Value |
|-----------|-------|
| **Role Title** | Market Compliance Officer (MCO) |
| **Scope** | Single assigned market (e.g., India only) |
| **Access Level** | Read-only |
| **Primary Goal** | View production configuration for compliance/audit |

### Permissions Matrix

| Action | CRR Tab | Sandbox Tab | Assets Tab | FA Tab | Reporting | Alerts |
|--------|---------|-------------|------------|--------|-----------|--------|
| View | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Edit | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Create | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Delete | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Export | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |

### What Viewer CAN Do
- View PRODUCTION configuration for their market
- View risk framework hierarchy (categories, elements, rulesets, rules)
- View PRODUCTION assets (read-only)
- View FA scores and overrides (read-only)
- View reporting dashboards
- View triggered alerts
- Export data for audit purposes

### What Viewer CANNOT Do
- Access Sandbox tab
- Edit any configuration
- Create sandboxes
- Create or edit assets
- Create or edit rules
- Modify FA scores
- Approve any changes

---

## User Type 2: Editor (CRR Business User)

### Profile
| Attribute | Value |
|-----------|-------|
| **Role Title** | CRR Business User (Compliance Analyst, Risk Manager) |
| **Scope** | Enterprise-wide OR Market-specific (configurable) |
| **Access Level** | Full edit access |
| **Primary Goal** | Configure and maintain CRR rules, assets, and FA |

### Permissions Matrix

| Action | CRR Tab | Sandbox Tab | Assets Tab | FA Tab | Reporting | Alerts |
|--------|---------|-------------|------------|--------|-----------|--------|
| View | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Create | ❌* | ✅ | ✅** | ✅** | ❌ | ✅ |
| Edit | ❌* | ✅ | ✅** | ✅** | ❌ | ✅ |
| Delete | ❌* | ✅ | ✅** | ❌ | ❌ | ✅ |
| Submit | N/A | ✅ | N/A | N/A | N/A | N/A |
| Approve | N/A | ✅ | N/A | N/A | N/A | N/A |
| Promote | N/A | ✅ | N/A | N/A | N/A | N/A |

*CRR Tab is read-only; editing happens in Sandbox Tab
**Asset/FA editing happens inside Sandbox

### What Editor CAN Do
- View all production configuration
- Create Enterprise or Market sandboxes
- Edit rules, rulesets, elements within sandbox
- Create new assets (Enterprise sandbox only)
- Edit assets (with versioning)
- Edit FA scores and answers
- Run simulations
- Submit for approval
- Approve other users' sandboxes
- Promote approved sandboxes to production
- Configure alerts

### What Editor CANNOT Do
- Approve their own submissions (two-person rule)
- Edit production directly (must use sandbox)
- Delete production data

---

## Two-Person Rule

For sandbox promotion:
- **Submitter** cannot be **Approver 1**
- **Approver 1** cannot be **Approver 2**
- Minimum 2 different people required for production promotion

```
User A (Submitter) ──▶ Submit
User B (Approver)  ──▶ Approve 1
User C (Approver)  ──▶ Approve 2 ──▶ Promote
```

---

## Tab Access Summary

| Tab | Viewer | Editor |
|-----|--------|--------|
| **Tab 1: CRR** | View production for their market | View production for all markets |
| **Tab 2: Sandbox** | ❌ No access | Full access |
| **Tab 3: Assets** | View production assets | View + Edit (in sandbox) |
| **Tab 4: FA** | View production FA | View + Edit (in sandbox) |
| **Tab 5: Reporting** | View reports | View reports |
| **Tab 6: Alerts** | View triggered alerts | Configure + View alerts |

---

## Scope-Based Access

### Enterprise Scope Editor
- Can create Enterprise sandboxes
- Can view/edit all market configurations
- Can create assets (Enterprise-only rule)

### Market Scope Editor
- Can create sandboxes for their market only
- Can edit market-specific rules only
- Cannot create new assets
- Can use existing production assets

---

*For detailed tab functionality, see `07_UI_Structure/`.*
