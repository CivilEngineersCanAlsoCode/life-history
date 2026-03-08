# CRR Application UI Structure

## Overview

The CRR application has **6 main tabs** accessible from the top navigation.

```
┌──────┬─────────┬────────┬──────────────────────┬───────────┬────────┐
│ CRR  │ Sandbox │ Assets │ Fundamental          │ Reporting │ Alerts │
│      │         │        │ Assessments          │           │        │
└──────┴─────────┴────────┴──────────────────────┴───────────┴────────┘
  Tab 1   Tab 2    Tab 3          Tab 4             Tab 5      Tab 6
```

---

## Tab 1: CRR (Production View Dashboard)

### Purpose
View-only dashboard showing the PRODUCTION risk framework for user's market.

### Access
| User Type | Access |
|-----------|--------|
| Viewer | ✅ Their assigned market |
| Editor | ✅ All markets |

### Content
- Risk framework hierarchy (Categories → Elements → Rulesets → Rules)
- All shown in PRODUCTION state
- Market selector dropdown (for Editors)

### Actions Available
- View hierarchy
- Expand/collapse nodes
- Export configuration
- **No editing** (editing happens in Sandbox tab)

---

## Tab 2: Sandbox (Editing Workspace)

### Purpose
Workspace where Editors create, manage, and edit sandboxes.

### Access
| User Type | Access |
|-----------|--------|
| Viewer | ❌ No access |
| Editor | ✅ Full access |

### Content
- List of active sandboxes (user's own)
- Sandbox creation button
- Inside sandbox:
  - Risk framework (editable)
  - Asset access (editable)
  - FA access (editable)
  - Simulation controls
  - Submit/Approve buttons

### Sandbox List View
| Column | Description |
|--------|-------------|
| Sandbox Name | User-defined name |
| Scope | Enterprise or Market name |
| Status | WORKING / SUBMITTED / SIMULATED / APPROVED |
| Created | Timestamp |
| Actions | Open, Delete, Submit |

### Inside Sandbox View
- Same hierarchy as CRR tab but **editable**
- Plus Asset Manager panel
- Plus FA panel
- Simulation button
- Submit button

---

## Tab 3: Assets (Production Asset Dashboard)

### Purpose
View-only dashboard showing PRODUCTION assets.

### Access
| User Type | Access |
|-----------|--------|
| Viewer | ✅ View only |
| Editor | ✅ View; Edit inside Sandbox |

### Content
- Table of all PRODUCTION assets
- Columns:
  - Asset Name
  - Reference Table
  - Description
  - Version
  - Last Updated
  - Actions (View, Download)

### Filter Options
- By Reference Table
- By Scope (Enterprise / Market)
- By Risk Category (where used)

### Actions Available
- View asset details (read-only)
- Download asset as CSV/Excel
- **No direct editing** (editing happens inside Sandbox)

---

## Tab 4: Fundamental Assessments (Production FA Dashboard)

### Purpose
View-only dashboard showing PRODUCTION FA scores.

### Access
| User Type | Access |
|-----------|--------|
| Viewer | ✅ View only (their market) |
| Editor | ✅ View; Edit inside Sandbox |

### Content
- FA Gate selector (6 gates)
- List of attributes for selected gate
- Current FA score per attribute
- Override indicator (if market has override)

### Filter Options
- By Gate (GR, IR, PRR, OCCP, ACR, SR)
- By Score Range (1-3, 4-6, 7-9, 10)
- By Market (for overrides)

### Actions Available
- View attribute details
- View question answers
- Export scores
- **No direct editing** (editing happens inside Sandbox)

---

## Tab 5: Reporting (Production Scoring Dashboard)

### Purpose
Analytics dashboard showing risk distribution and metrics.

### Access
| User Type | Access |
|-----------|--------|
| Viewer | ✅ View only |
| Editor | ✅ View only |

### Content

#### Customer Metrics
- Total customers in scope

#### Account Metrics (3 columns)
| Column | Description |
|--------|-------------|
| Independent Accounts | Standalone accounts |
| Hierarchical Accounts | Accounts in a hierarchy |
| Hierarchies | Number of account hierarchies |

#### Risk Distribution Buckets
| Bucket | Score Range | Count | Percentage |
|--------|-------------|-------|------------|
| Low | 1-3 | X | X% |
| Medium | 4-6 | X | X% |
| High | 7-9 | X | X% |
| Prohibited | 10 | X | X% |

### Filter Options
- By Center
- By Product
- By Legal Entity
- Date range

---

## Tab 6: Alerts (Alert Configuration)

### Purpose
Configure and view alerts for specific risk situations.

### Access
| User Type | Access |
|-----------|--------|
| Viewer | ✅ View triggered alerts only |
| Editor | ✅ Configure + View alerts |

### Alert Types
- Risk rating spike (customer score increased by X)
- Customer count spike in risk bucket
- Account count spike
- New prohibited customers

### Alert Configuration (Editor only)
- Alert name
- Trigger condition
- Threshold
- Recipients (email)
- Frequency

### Alert View
- List of triggered alerts
- Alert details
- Resolution status

---

## Navigation Flow

```
                           ┌─────────────────┐
                           │   User Login    │
                           └────────┬────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
              ┌─────────┐    ┌───────────┐   ┌───────────┐
              │ Viewer  │    │  Editor   │   │  Editor   │
              │  MCO    │    │ (Market)  │   │(Enterprise│
              └────┬────┘    └─────┬─────┘   └─────┬─────┘
                   │               │               │
                   ▼               ▼               ▼
              ┌────────────────────────────────────────────────┐
              │                 Tab Navigation                  │
              ├────────┬─────────┬────────┬─────┬─────┬────────┤
              │  CRR   │ Sandbox │ Assets │ FA  │Report│ Alerts │
              └────────┴─────────┴────────┴─────┴─────┴────────┘
```

---

*For detailed screen mockups, see `06_Design_Assets/`.*
