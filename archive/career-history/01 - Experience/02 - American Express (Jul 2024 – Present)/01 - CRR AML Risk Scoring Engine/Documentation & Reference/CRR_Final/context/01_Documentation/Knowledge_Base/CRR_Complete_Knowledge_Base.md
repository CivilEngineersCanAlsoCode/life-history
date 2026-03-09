# Customer Risk Rating (CRR) 2.0 - Complete Knowledge Base

---

## Document Information

| Field | Value |
|-------|-------|
| **Product** | Customer Risk Rating (CRR) Modernization Platform |
| **Document Type** | Complete Product Knowledge Base |
| **Version** | 1.0 |
| **Last Updated** | January 2026 |
| **Owner** | CRR Product Team - American Express |
| **Status** | Active Development (PI 26.1) |

---

# TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [Product Vision & Problem Statement](#2-product-vision--problem-statement)
3. [System Architecture](#3-system-architecture)
4. [User Personas & Journeys](#4-user-personas--journeys)
5. [Asset Manager Lifecycle](#5-asset-manager-lifecycle)
6. [Sandbox Workflow](#6-sandbox-workflow)
7. [Localisation Flow](#7-localisation-flow)
8. [Edge Cases & Conflict Resolution](#8-edge-cases--conflict-resolution)
9. [Technical Data Model](#9-technical-data-model)
10. [Feature Breakdown](#10-feature-breakdown)
11. [User Stories](#11-user-stories)
12. [Non-Functional Requirements](#12-non-functional-requirements)
13. [Decision Log & Open Questions](#13-decision-log--open-questions)
14. [Glossary](#14-glossary)

---

# 1. EXECUTIVE SUMMARY

## 1.1 What is CRR?

Customer Risk Rating (CRR) is a **hierarchical, deterministic risk-scoring engine** used for Anti-Money Laundering (AML) and related risk assessments at American Express. It evaluates customer risk based on configurable rules that analyze customer attributes, geographic factors, transaction patterns, and product usage.

## 1.2 The Modernization Initiative (CRR 2.0)

The CRR 2.0 platform is a comprehensive modernization initiative to transform how American Express configures, tests, and deploys AML risk scoring logic across global markets.

### Key Transformation Goals

| Goal | Description |
|------|-------------|
| **Unified Sandbox** | Consolidate all CRR configuration (Rules, Assets, Fundamental Assessment) into a single sandbox workflow |
| **Atomic Promotion** | Ensure version-controlled promotion to production with full rollback capability |
| **Complete Audit Trail** | Provide full lineage from change creation through production implementation |
| **Cross-Market Governance** | Enable centralized asset management with copy-on-write protection |

### Current Problems Being Addressed

| Problem | Business Impact |
|---------|-----------------|
| **Independent Merges** | Rules and assets can reach production in untested combinations |
| **Partial Logic States** | Production may contain configurations never simulated together |
| **Explainability Gaps** | Cannot trace why a customer's CRR changed for audit purposes |
| **Cross-Market Risk** | Market-specific changes can inadvertently affect other markets |
| **Manual Asset Management** | File-based CSV uploads lead to duplication and inconsistency |

---

# 2. PRODUCT VISION & PROBLEM STATEMENT

## 2.1 Vision Statement

> Create a unified, auditable, and atomic CRR configuration platform where every risk decision is tested as a complete change set before reaching production, with full traceability and cross-market governance.

## 2.2 Target Outcomes

1. **Zero Untested Production States** - All configuration combinations are simulated before deployment
2. **Complete Audit Lineage** - Every change traceable from creation to production
3. **Simplified Governance** - Clear Enterprise vs Market scope boundaries
4. **Reduced Manual Work** - Centralized asset management eliminates file duplication

## 2.3 Key Insight: Atomic Risk Decisions

The CRR system fundamentally operates on **risk decisions**, not isolated configuration changes. A valid risk decision often requires:

- Coordinated asset updates
- Coordinated rule updates
- Joint simulation
- Single approval
- Single promotion

The current UI and workflow do not enforce or even encourage this atomicity. **CRR 2.0 changes this.**

---

# 3. SYSTEM ARCHITECTURE

## 3.1 CRR Hierarchy Model

The CRR system is structured as a hierarchical tree:

```
Risk Framework (Enterprise/Market scoped)
  └── Risk Categories (5 total)
        ├── Customer
        ├── Geography  
        ├── Transactions
        ├── Products & Services
        └── ARFs & HROs
              └── Risk Elements (specific risk dimensions)
                    └── Rulesets (executable risk logic units)
                          └── Rules (Datapoint + Operator + Value/Asset)
```

### Component Definitions

| Component | Description |
|-----------|-------------|
| **Risk Framework** | Top-level container scoped by market/center (e.g., India, Belgium, Enterprise) |
| **Risk Categories** | Logical groupings of risk sources (5 categories) |
| **Risk Elements** | Specific dimensions of risk within a category |
| **Rulesets** | Executable risk logic units with weighting and multipliers |
| **Rules** | Atomic logic expressions: Datapoint → Operator → Value |

## 3.2 Rule Logic Model

### Rule Structure
Each rule within a ruleset is defined as:
- **Datapoint** - Customer attribute (jurisdiction, occupation, product type)
- **Operator** - Logical operator constrained by datapoint type
- **Value** - Static value or Asset (reusable list)

```
Example: Customer_Jurisdiction IN High_Risk_Countries
```

### Operators by Datapoint Type

| Datapoint Type | Available Operators |
|----------------|---------------------|
| Numeric | Greater than, Less than, Equals |
| Asset (list/array) | Includes, Excludes |
| Boolean | True, False |
| String | Equals, Contains |

### Rule Logic Composition
- Rules can be combined using **AND / OR**
- Nesting is supported
- Rule evaluation is deterministic, static, and context-aware for entity type

### Ruleset Impact Formula
```
Ruleset Impact = Rule Logic × Weight × Multiplier
```

## 3.3 Scope Model

The scope model determines where configurations are applied:

| Scope Code | Meaning | Example |
|------------|---------|---------|
| `XX` | Enterprise (Global) | Common rules for all markets |
| `IN` | India Market | India-specific localizations |
| `BE` | Belgium Market | Belgium-specific localizations |
| `GE` | Germany Market | Germany-specific localizations |

### Scope Execution Priority
```
When running assessment for Belgium:
1. Check for BE-scoped risk elements → Use if found
2. If not found → Use XX-scoped risk elements

Localised rules ALWAYS take precedence over enterprise
```

## 3.4 Reference Data & Assets

### Reference Data Tables
- Master list of valid values for all datapoints
- Each datapoint points to exactly one reference data table
- A single reference data table can be shared across multiple datapoints
- Reference data tables enforce **global validity constraints**

Example:
```
Reference Table: Product_Type
↳ Datapoints using it:
   - Product
   - Secondary Product
   - Jurisdiction Product
```

### Asset Definition

An **Asset** is:
- A named, versioned list of values validated against a reference data table
- Values validated at creation time against reference data table
- Can contain one or more values (always treated as list)
- Used as **Values** in rule logic

| Property | Description |
|----------|-------------|
| **Structure** | Array of values (even single values are treated as lists) |
| **Validation** | Values validated at creation against reference data tables |
| **Reuse** | Can be used across rules, rulesets, elements, categories, and markets |
| **Scale** | ~100 assets today, scaling to ~1000+ |

### Asset Reuse Model
Assets are reused extensively:
- Across rules
- Across rulesets
- Across risk elements
- Across risk categories
- Across markets

---

# 4. USER PERSONAS & JOURNEYS

## 4.1 Primary Personas

| Persona | Role | Permissions | Primary Goals |
|---------|------|-------------|---------------|
| **CRR Business User** | Compliance Analyst/Manager | Full configuration authority | Create/edit rules, assets, FA; run simulations; promote to production |
| **Market Compliance Officer** | Regional Compliance Lead | View-only access | Reference production configuration; export for auditors; understand market-specific rules |

## 4.2 Persona Capabilities Matrix

| Capability | CRR Business User | Market Compliance Officer |
|------------|-------------------|---------------------------|
| Create/Edit Sandbox | ✅ | ❌ |
| Run Simulation | ✅ | ❌ |
| Approve Changes | ✅ | ❌ |
| Promote to Production | ✅ | ❌ |
| View Production Config | ✅ | ✅ |
| Export Assets/Reports | ✅ | ✅ |
| Create/Edit Assets | ✅ | ❌ |
| View Market-Specific Data | All Markets | Assigned Markets Only |

## 4.3 Market Compliance Officer Journey

### Available Screens (View-Only)
1. **CRR Screen** - View rules
2. **Assets Screen** - View assets linked to rulesets
3. **Fundamental Assessment Screen** - View gates and overrides

### CRR Screen Navigation
- **Primary Dropdown**: Select market (e.g., India, Belgium, Germany)
- **Secondary Dropdown**: Filter scope
  - **All**: Shows all rules for market
  - **Market**: Shows only market-specific (localized) rules
  - **Enterprise**: Shows only enterprise-scoped rules

### Assets Screen Navigation
- Primary and secondary dropdowns available
- Shows only assets linked to rulesets visible for selected market/scope
- All assets presented in read-only mode

### Fundamental Assessment Screen
- Shows only gates linked to visible rulesets
- Shows only overrides for user's assigned center/market
- Does NOT show overrides for other centers

## 4.4 CRR Business User Journey

### Standalone Asset Manager
- Full visibility across all markets (no primary/secondary dropdown)
- **Plus Asset** button to create new assets
- New assets created in Draft status (editable and deletable)
- Existing assets in Sandbox/Production status: view and export only
- **Must go to Sandbox to edit non-Draft assets**

### Fundamental Assessment
- Full visibility of all gates and overrides
- Configuration changes happen within Sandbox

### Sandbox Workflow (New Unified Experience)
**Configuration Selector Dropdown:**
- Rules (default)
- Assets
- Fundamental Assessment

User can switch between configuration types without leaving sandbox context.

---

# 5. ASSET MANAGER LIFECYCLE

## 5.1 Asset Status Flow

```
DRAFT ──────► SANDBOX ──────► PRODUCTION ──────► DEPRECATED/ARCHIVED
  │              │                  │
  │              │                  └── When newer version promoted
  │              │
  │              └── When linked to ruleset in sandbox
  │
  └── Newly created, not linked anywhere
```

### Status Definitions

| Status | Meaning |
|--------|---------|
| **Draft** | Newly created, not linked to any rule/sandbox. Fully editable and deletable. |
| **Sandbox** | Linked to one or more sandbox rulesets. Subject to sandbox state editability rules. |
| **Production** | Actively used in latest CRR production version. Limited editability. |
| **Archived** | Previously used in production, now replaced by newer version. Read-only. |

## 5.2 Editability Matrix

| Sandbox Type | Asset Status | Used By | Editable? | Action |
|--------------|--------------|---------|-----------|--------|
| Enterprise | Any | Any | ✅ YES | Versioning |
| Market | DRAFT | - | ✅ YES | Inline update |
| Market | SANDBOX/PROD | This market only | ✅ YES | Versioning |
| Market | SANDBOX/PROD | Multiple markets | ❌ NO | Must Copy |
| Market | SANDBOX/PROD | Enterprise | ❌ NO | Must Copy |
| Any (non-Draft state) | Any | - | ❌ NO | View only |

### Key Editability Rules

1. **In Enterprise Sandbox**: All assets editable with versioning
2. **In Market Sandbox**: 
   - Draft assets: Editable inline
   - Assets used only in THIS sandbox: Editable with versioning
   - Assets used in OTHER markets/Enterprise/Production: Blocked → Prompt to create copy

## 5.3 Versioning Semantics

```
Production: A1 V1
    │
    ▼ User edits in sandbox (FIRST time)
Sandbox: A1 V2 created (once)
    │
    ▼ User makes more changes (before submit)
Sandbox: A1 V2 updated INLINE (no new version)
    │
    ▼ User submits for simulation
Sandbox: A1 V2 FROZEN, mapped to sandbox version
    │
    ▼ Next edit after submit
Sandbox: A1 V3 created
```

**Key Rules:**
- First edit in sandbox creates new version
- Subsequent edits before submit update inline (same version)
- Submit freezes current version
- Next edit after submit creates new version

## 5.4 Copy-on-Write Workflow

When user attempts to edit a shared (cross-market/enterprise) asset:

1. **System blocks editing**
2. **Modal displays**: "This asset is used in [Market A, Market B, Enterprise]. Would you like to create a copy?"
3. **Copy creation**:
   - Default name: `{OriginalName}_copy`
   - List Name field disabled (same reference table)
   - Real-time duplicate name validation
   - Save disabled until unique name entered
4. **New copy created in Draft status**
5. **Original asset unchanged**

## 5.5 Asset Export

Two-sheet Excel workbook:
- **Filename**: `{AssetName}_v{version}.xlsx`
- **Sheet 1 (Values)**: Single column with all asset values (no header)
- **Sheet 2 (References)**: Where-used metadata with columns:
  - Scope
  - Status
  - Risk Category
  - Risk Element
  - Ruleset
  - Rule

---

# 6. SANDBOX WORKFLOW

## 6.1 Sandbox Types

| Type | Scope | Asset Visibility | Asset Editability |
|------|-------|------------------|-------------------|
| **Enterprise** | All markets | All assets | All assets (with versioning) |
| **Market** | Single market | All assets | Draft assets OR assets used only in this market |

### Mutual Exclusion Rules

| Active Sandbox | Enterprise Option | Market Options |
|----------------|-------------------|----------------|
| None | ✅ Enabled | ✅ Enabled |
| Enterprise | ✅ (exists) | ❌ Disabled |
| Any Market | ❌ Disabled | ✅ Other markets enabled |

**Enterprise and Market sandboxes cannot coexist.**

## 6.2 Sandbox Lifecycle States

```
                    ┌─────────────┐
                    │   WORKING   │ ← Sandbox Draft (edits allowed)
                    └──────┬──────┘
                           │ Submit (comment mandatory)
                    ┌──────▼──────┐
                    │ SUBMISSION  │
                    │ IN PROGRESS │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
        Cancel ────►│ IN_PROGRESS │ (Simulation running)
           │        └──────┬──────┘
           │               │
    ┌──────▼──────┐ ┌──────▼──────┐
    │  CANCELLED  │ │ TESTING     │
    │             │ │ COMPLETED   │
    └──────┬──────┘ └──────┬──────┘
           │               │
           │        ┌──────▼──────┐
           │        │ View Results│
           │        └──┬───────┬──┘
           │       No  │       │ Yes (Implement)
           │    ┌──────▼───┐   │
           │    │ CREATE   │   │
           │    │ NEW VER  │   │
           │    │ or       │   │
           │    │ ROLLBACK │   │
           │    └──────┬───┘   │
           │           │       │
           └───────────┴───────┤
                               │
                    ┌──────────▼──────────┐
                    │ PENDING_APPROVAL_1  │
                    └──────────┬──────────┘
                      Reject   │   Approve
                    ┌──────────┼──────────┐
                    │          │          │
             ┌──────▼──────┐   │   ┌──────▼──────────┐
             │  REJECTED   │   │   │PENDING_APPROVAL_2│
             └──────┬──────┘   │   └──────┬──────────┘
                    │          │   Reject │   Approve
                    │          │   ┌──────┼──────┐
                    └──────────┴───►      │      │
                                   ┌──────▼──┐ ┌─▼──────────┐
                                   │REJECTED │ │ PRODUCTION │
                                   └─────────┘ │  (Merged)  │
                                               └────────────┘
```

### State Editability

| State | Editable? |
|-------|-----------|
| WORKING (Draft) | ✅ YES |
| SUBMISSION IN PROGRESS | ❌ NO |
| IN_PROGRESS (Simulation) | ❌ NO |
| CANCELLED | ❌ NO |
| TESTING COMPLETED | ❌ NO |
| PENDING APPROVAL 1 | ❌ NO |
| PENDING APPROVAL 2 | ❌ NO |
| REJECTED | ❌ NO |
| PRODUCTION | ❌ NO |

**Assets follow sandbox editability state exactly.**

## 6.3 Key Rules

- **Version Cap**: Maximum 10 versions per sandbox
- **After Cap**: Must archive/delete sandbox and create new
- **Comments**: Mandatory at each state transition
- **History**: All transitions logged with ECN, Username, Timestamp, Version, Status, Comments

## 6.4 Unified Configuration Experience

### Configuration Selector in Sandbox UI
Options:
- Rules (default)
- Assets
- Fundamental Assessment

### Switching views does NOT exit sandbox context

### Unified Change Summary (Before Simulation)
Displays all changes grouped by type:
- Rule changes
- Asset changes
- Fundamental Assessment changes

### Atomic Promotion
When promoting sandbox to production:
- Rules, Assets, and Fundamental Assessment promoted **together**
- Partial promotion NOT allowed
- Single database transaction
- Full rollback on any failure

## 6.5 Simulation Rules

- **Delta Execution**: Only runs CHANGED risk elements
- **Isolation**: Uses COPIED rules in sandbox (not production at runtime)
- **Scope**: Pulls unchanged rules from production for complete scoring
- **Copy Timestamp**: Configuration copied at SUBMIT time (not job start)

---

# 7. LOCALISATION FLOW

## 7.1 When Market Edits Enterprise Ruleset

When a user in a market sandbox edits an enterprise-scoped ruleset:

```
Enterprise Risk Element (Scope XX)
  └── Ruleset 1 (XX)
  └── Ruleset 2 (XX)
  └── Ruleset 3 (XX)

User in India sandbox clicks EDIT on Ruleset 2
    │
    ▼ System triggers LOCALISATION
    
Creates:
  India Risk Element (Scope IN)
    └── Ruleset 1 (IN) ← Copy
    └── Ruleset 2 (IN) ← Copy + User's edit
    └── Ruleset 3 (IN) ← Copy

Original XX Risk Element UNCHANGED
```

## 7.2 Example Scenario

```
Enterprise (XX) rule: "Income < 5000 = High Risk"
India (IN) wants: "Income < 10000 = High Risk"

When India edits:
1. System COPIES Enterprise rule to India scope
2. Creates new India-scoped rule with edits
3. Now India has 2 rules: Global (XX) + India (IN)
4. System always applies LOCAL (IN) rule first
```

## 7.3 Enterprise Asset Propagation

When Enterprise sandbox is promoted to production:
- Enterprise assets propagate to ALL markets automatically
- Markets using custom copies are SKIPPED in propagation
- Original market copies remain unchanged

---

# 8. EDGE CASES & CONFLICT RESOLUTION

## 8.1 Resolved Edge Cases (EC1-EC10)

### EC1: Asset Unlinked Mid-Edit (Shared→Exclusive)

**Scenario**: User edits shared asset. While editing, other markets unlink it, making it exclusive to user's market.

**Resolution**: System re-checks ownership at SAVE time. If now exclusive, allows inline update (no copy needed).

---

### EC2: Asset Status Change Mid-Edit (SANDBOX→DRAFT)

**Scenario**: User edits SANDBOX status asset. Colleague removes all rules using it, reverting to DRAFT.

**Resolution**: System detects DRAFT status at save. Allows inline update (DRAFT is flexible).

---

### EC3: Multi-Sandbox Split (Shared Asset, Different Versions)

**Scenario**: Raj (India) edits Asset A1 → V2. Sarah (Belgium) also uses A1 in her sandbox.

**Resolution**: 
- Raj's sandbox links to V2
- Sarah's sandbox stays on V1
- Each sandbox tracks own version via `sandbox_component_map`

---

### EC4: Concurrent Edit Detection

**Scenario**: Two users edit same asset simultaneously.

**Resolution**: Optimistic locking via `version_no`:
```
User X opens at T1 (version_no = 5)
User Y opens at T2 (version_no = 5)
User Y saves at T3 → Success (version_no = 6)
User X saves at T4 → FAILS (version mismatch)
```

Conflict UI shows:
- Your changes
- Current state (other user's changes)
- Options: MERGE | OVERWRITE | RELOAD

---

### EC5: Enterprise Edit Impact on Markets

**Scenario**: Enterprise edits global asset. Markets have active sandboxes using it.

**Resolution**:
- NO auto-propagation to active sandboxes
- Manual refresh required by markets
- UI shows "Stale Sandbox" badge
- Warning modal to Enterprise: "This change will mark X sandboxes as STALE"

---

### EC6: Scoring Engine - Copied vs Production

**Scenario**: Simulation runs while Enterprise changes production.

**Resolution**: 
- Uses COPIED rules in sandbox (fully isolated)
- Production changes don't affect running simulation
- Copy made at SUBMIT time (before queue)

---

### EC7: Draft Asset Becomes Production via Different Sandbox

**Scenario**: Raj creates Draft asset. Enterprise promotes same asset to Production.

**Resolution**: 
- Asset status changes to PRODUCTION
- Raj loses edit rights on original
- Must create new version or copy

---

### EC8: Enterprise Attempts Delete of Localized Ruleset

**Scenario**: Enterprise tries to delete "Geography Risk" category. Markets have overrides.

**Resolution**: **BLOCKED**
- System tells Enterprise: "Cannot delete. Markets are using it."
- Enterprise must coordinate with markets first

---

### EC9: Refresh with Conflicting Versions

**Scenario**: Enterprise creates V2. Market created V3 (based on V1). Market refreshes.

**Resolution**: Conflict resolution UI:
- Take Enterprise V2 (lose V3)
- Keep My V3 (ignore Enterprise)
- Manual Merge

---

### EC10: Version Cap + Asset Versions

**Scenario**: Sandbox hits version 10 limit. User needs to continue work.

**Resolution**: 
- Archive old sandbox (read-only for history)
- Create new sandbox
- All asset versions **carry over** to new sandbox
- No work lost

---

## 8.2 Additional Edge Cases (EC11-EC20)

### EC11: Optimistic Locking Cascade (Asset Version vs Rule Reference)

**Scenario**: User X updates Asset A1 (V1→V2). User Y edits Rule R1 that references A1.

**Resolution**: **NO Auto-Update**
- Rule R1 continues pointing to V1
- Badge shown: "Underlying asset has newer version"
- User must explicitly click "Update Reference"

---

### EC12: Orphan Asset Accumulation

**Scenario**: After 1 year, 5000+ orphan assets accumulate (unused, status SANDBOX).

**Resolution**: **Auto-Archive (Soft Hide)**
- If asset untouched and unused for 90 days → move to ARCHIVED status
- Hidden from search unless "Include Archived" checkbox selected
- Never auto-delete

---

### EC13: Merge Conflict Resolution Logic

**Scenario**: Two users merge lists. A adds [Apple, Banana], B adds [Carrot, Banana].

**Resolution**: **Set Union**
- Result: [Apple, Banana, Carrot]
- Duplicates removed automatically

---

### EC14: Stale Sandbox + Version Cap Collision

**Scenario**: Sandbox at version 9, needs refresh (stale). Refresh would create version 10 (cap).

**Resolution**: **Forced Archive**
- System prompts: "Sandbox full. Creating NEW refreshed sandbox for you."
- New sandbox created with refreshed baseline

---

### EC15: Enterprise Edit During Active Market Sandboxes

**Scenario**: Enterprise edits asset → Production. Markets IN and BE have active sandboxes using old version.

**Resolution**: **Warning Modal to Enterprise**
- "This change will mark X sandboxes as STALE"
- Markets notified via "Stale" badge
- Markets must refresh manually before promotion

---

### EC16: Simulation Isolation During Queue Delay

**Scenario**: Submit at 12:00. Job runs at 14:00. Production changed at 13:00.

**Resolution**: **Copy on SUBMIT**
- State captured at submit time (12:00)
- Queue delay doesn't affect simulation data

---

### EC17: Copy-on-Write Naming Convention

**Scenario**: Multiple markets copy same asset.

**Resolution**: **Suffix Scoping**
- Auto-name: `{AssetName}_{MarketCode}`
- Example: `Global_List_IN`, `Global_List_BE`
- User can customize name (with duplicate validation)

---

### EC18: Rollback to Stale Production Baseline

**Scenario**: User rolls back to version based on 6-month-old production data.

**Resolution**: **Allow with Warning**
- Rollback permitted
- Sandbox immediately flagged as "STALE"
- User must eventually refresh or acknowledge staleness

---

### EC19: Asset Version Explosion

**Scenario**: Asset accumulates 500+ versions over time.

**Resolution**: **Soft Cap in UI**
- Dropdown shows last 10 versions
- "See All" link to view complete history
- No hard version limit

---

### EC20: FA Gate Deletion with Active Market Overrides

**Scenario**: Enterprise deletes Gate G1. Markets have overrides on G1.

**Resolution**: **Cascade Soft Delete**
- Enterprise delete marks G1 as deleted
- Market overrides auto-marked as **Inactive/Hidden**
- Nothing breaks, just disappears gracefully

---

## 8.3 Concurrent Edit Handling

### Optimistic Locking Implementation

```
User X opens edit at T1 (version_no = 5)
User Y opens edit at T2 (version_no = 5)
User Y saves at T3 → Success (version_no = 6)
User X saves at T4 → FAILS (version mismatch: expected 5, found 6)
```

### Conflict Resolution UI

```
┌─────────────────────────────────────────────────────┐
│            CONFLICT DETECTED                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────┐    ┌─────────────────┐        │
│  │ YOUR CHANGES    │    │ CURRENT STATE   │        │
│  ├─────────────────┤    ├─────────────────┤        │
│  │ Added: [A, B]   │    │ Added: [C, D]   │        │
│  │ Removed: [X]    │    │ Removed: []     │        │
│  └─────────────────┘    └─────────────────┘        │
│                                                     │
│  [MERGE]    [OVERWRITE]    [RELOAD]                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 8.4 Refresh/Rebase Workflow

### Scenario

```
T1: India sandbox created from Production P1
    └── Copies baseline config from P1
    
T2: Enterprise updates production to P2
    └── India sandbox is now STALE
    
T3: India tries to refresh
    └── System compares: India changes vs P1→P2 diff
    └── Detects conflicts
    └── User resolves: Keep Mine / Take Theirs / Manual Merge
```

### Key Behavior
- **Manual Refresh Required**: Markets must explicitly refresh to get enterprise updates
- **No Auto-Propagation**: Prevents surprise breaking changes mid-work
- **UI Indicator**: "Stale sandbox" badge shown when production advanced

---

# 9. TECHNICAL DATA MODEL

## 9.1 Primary Database Tables

| Table | Purpose |
|-------|---------|
| `risk_assess` | Sandbox container (versioned) |
| `sandbox_version` | Tracks each sandbox version (1-10) |
| `sandbox_component_map` | Maps sandbox version → component versions |
| `refer_da_asset` | Asset definitions (versioned) |
| `refer_da_asset_srce` | Asset source types |
| `risk_assess_sta_rel` | Status history (state transitions) |
| `sandbox_audit_comment` | Audit trail with comments |
| `rule_set` | Ruleset definitions |
| `risk_rule` | Individual rules (references assets) |
| `risk_assess_ctgy_elem_rel` | Risk elements |

## 9.2 Key Relationships

```
sandbox_version (1) ──► (N) sandbox_component_map
                              │
                              ├── rule_version
                              ├── asset_version
                              └── fa_version

refer_da_asset (1) ──► (N) asset_versions
                              │
                              └── values (validated against reference table)

risk_rule (N) ──► (1) refer_da_asset (via asset reference)
```

## 9.3 Audit Trail Schema

Every state transition logged with:
- ECN (Employee Corporate Network ID)
- Username
- Timestamp
- Version number
- Status (from → to)
- Comments (mandatory at transitions)

---

# 10. FEATURE BREAKDOWN

## 10.1 Feature 1: Unified Sandbox Journey (F817944)

**Feature Name**: CRR - Unified Sandbox Configuration Experience (UI & Journey Revamp)

### Complete Scope (User's Voice)

> As a Compliance Analyst / Compliance Manager,
> I want to configure, review, simulate, and promote CRR Rules, Assets, and Fundamental Assessment together within a single Sandbox experience,
> so that all risk logic changes are made in one place, tested together, reviewed together, and promoted as one atomic risk decision.

### Key Capabilities
- Create Enterprise or Market-scoped sandboxes
- Navigate between Rules/Assets/FA within sandbox context
- Create immutable version snapshots on simulation submission
- Two-step approval workflow with different approvers
- Atomic promotion with full transaction rollback
- Complete audit trail export

### Benefit to Business
- Eliminates fragmented configuration paths that create partial, untested risk states
- Enforces atomic risk decisions, improving regulatory defensibility
- Reduces operational errors caused by disconnected edits
- Improves explainability during audits by preserving change-set integrity

---

## 10.2 Feature 2: Asset Manager (F817940)

**Feature Name**: CRR - Enable Asset Manager Functionality E2E (Analysis & Build) E2

### Complete Scope (User's Voice)

> As a Compliance Analyst / Compliance Manager,
> I want assets to behave as versioned, governed configuration artifacts that can be reused safely across markets,
> so that changes to asset values do not unintentionally affect other markets or prior risk decisions.

### Key Capabilities
- Create assets within sandbox with reference data validation
- Automatic status transitions (Draft → Sandbox → Production → Archived)
- Visual indicators for shared vs local assets
- Copy-on-write workflow for shared assets in Market sandboxes
- Enterprise asset propagation to all markets on promotion
- Two-sheet Excel export (Values + References)

### Benefit to Business
- Prevents unintended cross-market risk impact
- Enables safe asset reuse at enterprise scale
- Improves audit traceability and lineage
- Reduces rework and configuration errors
- Supports regulator-grade explainability

---

## 10.3 Feature 3: UI Enhancements (F817939)

**Feature Name**: CRR - UI Enhancements & Modifications and Miscellaneous Work in E2

### Description
Incremental UI improvements, defect fixes, and technical debt resolution.

---

# 11. USER STORIES

## 11.1 Feature 1: Unified Sandbox Journey (9 Stories)

### Story 1.1 – Restrict All Configuration Editing to Sandbox Only
**As a** Compliance Analyst/Manager,
**I want** all configuration changes to be restricted to Sandbox only
**so that** no untested or partial changes can reach production.

**Acceptance Criteria:**
- Given I am on CRR, Asset Manager, or FA outside sandbox
- When I view configuration
- Then all configuration is read-only
- And no edit, add, or delete actions are available

---

### Story 1.2 – Add Configuration Selector Inside Sandbox
**As a** Compliance Analyst/Manager,
**I want** a configuration selector inside the Sandbox
**so that** I can switch between Rules, Assets, and FA without leaving sandbox.

**Acceptance Criteria:**
- Given I am inside a sandbox
- When I open configuration selector
- Then I see options for Rules, Assets, and FA
- And switching options does not exit sandbox or reset version

---

### Story 1.3 – Edit Rules Within Sandbox Context
**As a** Compliance Analyst/Manager,
**I want** to edit CRR rules within the sandbox
**so that** rule changes are isolated, testable, and versioned.

**Acceptance Criteria:**
- Given sandbox is in editable state
- When I select Rules from sandbox selector
- Then rule editing actions are enabled
- And all changes saved to sandbox version

---

### Story 1.4 – Edit Assets Within Sandbox Context
**As a** Compliance Analyst/Manager,
**I want** to edit assets within the sandbox
**so that** asset changes are tested together with rule changes.

**Acceptance Criteria:**
- Given sandbox is in editable state
- When I select Assets from sandbox selector
- Then eligible assets are editable
- And asset changes saved to sandbox version

---

### Story 1.5 – Edit Fundamental Assessment Within Sandbox Context
**As a** Compliance Analyst/Manager,
**I want** to edit FA within the sandbox
**so that** changes to multipliers and gates are tested with rules and assets.

**Acceptance Criteria:**
- Given sandbox is in editable state
- When I select FA from sandbox selector
- Then assessment configuration is editable
- And changes scoped to sandbox version

---

### Story 1.6 – Enforce Sandbox State-Based Editability
**As a** Compliance Analyst/Manager,
**I want** configuration editability to follow sandbox state
**so that** approved or running sandboxes cannot be modified.

**Acceptance Criteria:**
- Given sandbox is in non-editable state
- When I view Rules, Assets, or FA
- Then all configuration is read-only
- And edit actions are disabled

---

### Story 1.7 – Show Unified Change Summary Before Simulation
**As a** Compliance Analyst/Manager,
**I want** to see all configuration changes before simulation
**so that** I understand the full impact of what I am testing.

**Acceptance Criteria:**
- Given I initiate sandbox simulation
- When change review screen is shown
- Then rule changes, asset changes, and FA changes are displayed
- And changes grouped by configuration type

---

### Story 1.8 – Run Simulation Using Unified Configuration Set
**As a** Compliance Analyst/Manager,
**I want** simulation to run using rules, assets, and FA from same sandbox version
**so that** results accurately reflect my intended changes.

**Acceptance Criteria:**
- Given sandbox simulation is triggered
- When simulation executes
- Then it uses exact rule, asset, and FA versions from sandbox
- And production configuration is not used

---

### Story 1.9 – Promote Sandbox as Single Atomic Change Set
**As a** Compliance Analyst/Manager,
**I want** to promote rules, assets, and FA together
**so that** production always reflects complete and approved risk decision.

**Acceptance Criteria:**
- Given sandbox is approved
- When I promote to production
- Then rules, assets, and FA promoted together
- And partial promotion not allowed

---

## 11.2 Feature 2: Asset Manager (9 Stories)

### Story 2.1 – Create New Asset in Draft State
**As a** Compliance Analyst/Manager,
**I want** to create new assets in Draft state
**so that** they can be refined before being used.

**Acceptance Criteria:**
- Given I create a new asset
- When asset is saved
- Then its status is Draft
- And it can be edited or deleted

---

### Story 2.2 – Show All Assets for Selection in Sandbox
**As a** Compliance Analyst/Manager,
**I want** to see all assets available for use in sandbox rules
**so that** assets can be reused consistently.

**Acceptance Criteria:**
- Given I am in any sandbox
- When I view assets
- Then all system assets visible for selection

---

### Story 2.3 – Allow Asset Editing Only When Safe
**As a** Compliance Analyst/Manager,
**I want** to edit assets only when they are safe to change
**so that** other markets are not impacted.

**Acceptance Criteria:**
- Given asset is in Draft OR used only in current editable sandbox
- When I edit the asset
- Then editing is allowed

---

### Story 2.4 – Block Editing of Cross-Market or Shared Assets
**As a** Compliance Analyst/Manager,
**I want** editing of shared assets to be blocked
**so that** cross-market risk is prevented.

**Acceptance Criteria:**
- Given asset is used in another market, enterprise, or production
- When I attempt to edit it
- Then editing is blocked

---

### Story 2.5 – Prompt Asset Copy for Cross-Market Edits
**As a** Compliance Analyst/Manager,
**I want** to create a copy of an asset when direct editing is not allowed
**so that** I can safely customize it.

**Acceptance Criteria:**
- Given asset editing is blocked
- When I choose to create a copy
- Then new Draft asset is created
- And original asset remains unchanged

---

### Story 2.6 – Version Asset on Every Edit
**As a** Compliance Analyst/Manager,
**I want** every asset edit to create a new version
**so that** changes are traceable and auditable.

**Acceptance Criteria:**
- Given I edit an asset
- When I save changes
- Then new immutable asset version is created
- And previous versions preserved

---

### Story 2.7 – Align Asset Editability with Sandbox State
**As a** Compliance Analyst/Manager,
**I want** asset editability to follow sandbox state
**so that** frozen sandboxes cannot be altered.

**Acceptance Criteria:**
- Given sandbox is non-editable
- When I view assets inside that sandbox
- Then all asset edits are disabled

---

### Story 2.8 – Manage Asset Lifecycle States
**As a** Compliance Analyst/Manager,
**I want** assets to move through clear lifecycle states
**so that** I understand their usage and impact.

**Acceptance Criteria:**
- Given asset is used in active sandbox → status is Sandbox
- Given asset is used in latest production CRR → status is Production
- Given asset is no longer referenced by production → status is Archived

---

### Story 2.9 – Track Asset Versions Used by Sandbox Versions
**As a** Compliance Analyst/Manager,
**I want** sandbox versions to record asset versions used
**so that** future audits can explain CRR outcomes.

**Acceptance Criteria:**
- Given a sandbox version exists
- When I inspect its metadata
- Then exact asset versions used are recorded

---

# 12. NON-FUNCTIONAL REQUIREMENTS

## 12.1 Performance

| Metric | Target |
|--------|--------|
| Sandbox creation | < 5 seconds |
| Configuration save | < 2 seconds |
| Simulation progress update | ≤ 5 second polling |
| Asset export (1000 values, 50 references) | < 10 seconds |
| Duplicate name validation | < 500ms |
| Atomic promotion (50 rules, 20 assets, 10 FA) | < 30 seconds |

## 12.2 Scalability

| Metric | Capacity |
|--------|----------|
| Concurrent sandboxes | 4 (1 Enterprise + 3 Markets, or 4 Markets) |
| Assets per system | Up to 1,000 |
| Values per asset | Up to 10,000 |
| Ruleset references per asset | Up to 100 |
| Versions per sandbox | Up to 10 (before pagination) |
| Simulation population | Up to 10 million accounts |

## 12.3 Security

- All operations require ADS (Active Directory Services) authentication
- Role-based access control for sandbox operations
- Two-factor approval for production implementation
- Tamper-proof audit logs encrypted at rest
- CSV validation for malicious content

## 12.4 Compliance

- Full lineage from sandbox creation through production
- Track "who/what/when/why" for every change
- Historical snapshots preserved for minimum 7 years
- Exportable audit logs in standard formats

---

# 13. DECISION LOG & OPEN QUESTIONS

## 13.1 Confirmed Decisions

| # | Question | Decision |
|---|----------|----------|
| FQ1 | Do asset versions carry over when sandbox hits version cap? | ✅ YES - carry over to new sandbox |
| FQ2 | How is concurrent edit conflict detected? | Optimistic locking via `version_no` column |
| FQ3 | What happens if asset is unlinked mid-edit? | Re-check on SAVE; if exclusive now, inline update succeeds |
| FQ4 | Do enterprise edits auto-propagate to markets? | ❌ NO - manual refresh required |
| FQ5 | Does simulation use copied or production rules? | Uses COPIED rules in sandbox (isolated) |
| FQ6 | What happens to orphan assets when sandbox archived? | Stay SANDBOX status (orphaned); cleanup after 90 days |
| FQ7 | When asset version changes, should rules auto-update reference? | ❌ NO - user must manually update |
| FQ9 | For asset value lists, is merge = UNION of both sets? | ✅ YES |
| FQ12 | Is sandbox config copied at SUBMIT or JOB_START? | At SUBMIT time |

## 13.2 Open Questions (Require Business Input)

| # | Question | Options |
|---|----------|---------|
| FQ8 | Orphan asset retention period before admin review? | 30 days / 90 days / Never auto-flag |
| FQ10 | Does refresh create new sandbox version? | Yes / No |
| FQ11 | Can stale sandbox merge to production? | Yes / No / With warning |
| FQ13 | Is asset name globally unique or scoped to market? | Global / Market-scoped |
| FQ14 | Allow rollback if resulting config would be stale? | Yes / No / With warning |
| FQ15 | Can enterprise delete FA gate if markets have overrides? | Yes (cascade) / No (block) |

## 13.3 Additional Open Question

> **Do markets need visibility to the question answers that are updated by business in Fundamental Assessment?**

This remains an open question requiring business stakeholder decision.

---

# 14. GLOSSARY

| Term | Definition |
|------|------------|
| **Asset** | Named, versioned list of values validated against reference data |
| **Sandbox** | Isolated environment for testing CRR configuration changes |
| **Copy-on-Write** | Protection mechanism creating local copy instead of modifying shared asset |
| **Atomic Promotion** | All-or-nothing deployment of configuration changes |
| **FA** | Fundamental Assessment - Q&A-based risk evaluation |
| **AML** | Anti-Money Laundering |
| **CRR** | Customer Risk Rating |
| **Ruleset** | Executable risk logic unit with weighting and multipliers |
| **Risk Element** | Specific dimension of risk within a category |
| **Risk Category** | Logical grouping of risk sources (Customer, Geography, Transactions, Products & Services, ARFs & HROs) |
| **Localisation** | Process of creating market-specific copies of enterprise configurations |
| **Stale Sandbox** | Sandbox that is behind current production state |
| **Orphan Asset** | Asset not linked to any active sandbox or production rule |
| **ECN** | Employee Corporate Network ID (used for audit trail) |
| **Reference Data Table** | Master list of valid values for datapoints |
| **Scope** | Context in which configuration applies (Enterprise XX, or Market codes like IN, BE) |

---

# APPENDIX A: Release Scope (PI 26.1)

## In Scope

✅ Enterprise vs Market mutual exclusion  
✅ Unified sandbox configuration (Rules/Assets/FA)  
✅ Immutable version snapshots  
✅ Atomic promotion with rollback  
✅ Asset versioning and lifecycle  
✅ Copy-on-write for shared assets  
✅ Enterprise asset propagation  
✅ Two-sheet asset export  
✅ Read-only standalone Asset Manager  

## Out of Scope

❌ Authorization/permissions management (separate effort)  
❌ Concurrent edit collision detection (minimal user base)  
❌ Multi-market simulation  
❌ Scheduled implementation  
❌ Sandbox templates/cloning  
❌ Advanced conflict resolution UI  
❌ Bulk sandbox operations  
❌ Asset comparison tool  

## Future Enhancements

- Pessimistic locking for Draft edits
- Advanced simulation analytics
- Sandbox diff comparison
- Automated validation rules
- Import from external systems

---

# APPENDIX B: BRD Reference Mapping

| BRD Section | Requirement | PRD Coverage |
|-------------|-------------|--------------|
| 12.8 | Sandbox simulation functionality | Feature 1: Unified Sandbox Journey |
| 12.8.1 | Impact analysis capability | Simulation workflow |
| 12.8.4 | Multiple instances, scope hierarchy | Scope selection, mutual exclusion |
| 12.8.5 | Modification confirmation prompt | Submit confirmation modal |
| 12.8.6 | Progress tracking | Simulation progress UI |
| 12.8.12 | Version control | Version snapshots |
| 12.6 | Reference list management | Feature 2: Asset Manager |
| 12.6.1 | Multi-level list setup | Enterprise/Market asset scope |
| 12.7 | Change tracking | Audit trail requirements |

---

*Document End*

*Last Generated: January 2026*
*Source: CRR_Final/context/*
