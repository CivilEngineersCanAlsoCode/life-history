# 🎯 CRR COMPLETE USER JOURNEY DOCUMENTATION - MASTER META-PROMPT

## VERSION 2.0 - COMPREHENSIVE INTEGRATED EDITION

> **This is the MASTER PROMPT that governs the creation of all CRR User Journey documentation.**
> **It must be ultra-specific, granular, and leave no room for ambiguity.**

---

# PART 0: EXECUTION MODEL & GOVERNANCE

## 0.1 How This Documentation Will Be Generated

> **CRITICAL EXECUTION RULES:**

| Rule # | Rule Description |
|--------|------------------|
| 1 | This documentation will be generated **ONE SECTION AT A TIME** |
| 2 | Each section = **ONE markdown file** |
| 3 | Each section = **ONE response from the system** |
| 4 | System **MUST WAIT** for user permission before moving to next section |
| 5 | Do **NOT** combine multiple sections in one response |
| 6 | Current section **MUST BE 100% COMPLETE** before asking to proceed |
| 7 | Each section must follow the **SECTION TEMPLATE** defined in Part 7 |
| 8 | Each section must include **QA TEST CASES** as defined in Part 8 |
| 9 | Do **NOT** shorten or summarize - **MORE DETAIL IS ALWAYS BETTER** |
| 10 | If in doubt, **OVER-EXPLAIN** rather than under-explain |

## 0.2 What "Complete" Means for Each Section

A section is considered **COMPLETE** only when ALL of the following are true:

- [ ] All screens/views on that tab are documented
- [ ] Both user type perspectives are covered (where applicable)
- [ ] Every possible user action is listed
- [ ] Every action has preconditions, steps, and postconditions
- [ ] Multi-user scenarios are included (if applicable)
- [ ] At least 5 edge cases are covered with resolutions
- [ ] QA Test Cases are provided:
  - [ ] At least 10 positive test cases
  - [ ] At least 5 negative test cases
  - [ ] At least 3 boundary test cases
- [ ] System state changes are clearly documented with Before/After
- [ ] Examples are provided for every major concept
- [ ] No undefined behavior exists

---

# PART 1: SYSTEM CONTEXT & UNDERSTANDING

## 1.1 What is CRR?

CRR (Customer Risk Rating) is an **Anti-Money Laundering (AML) risk scoring platform** used by American Express globally. It:

- Assigns risk scores to customers based on configurable rules
- Uses a framework of Risk Categories, Risk Elements, Rulesets, and Rules
- Supports multiple markets (India, China, Belgium, USA, etc.)
- Allows testing changes in sandbox before going live to production
- Provides reporting and alerting capabilities

## 1.2 User Types (ONLY 2 TYPES)

There are **EXACTLY TWO** types of users in the CRR system:

### User Type 1: VIEWER (Read-Only User)

| Attribute | Description |
|-----------|-------------|
| **Who They Are** | Market Compliance Officers |
| **What They Do** | View the current production configuration for their market |
| **Access Level** | READ-ONLY across all tabs |
| **Cannot Do** | Create sandboxes, edit rules, create assets, modify FA |
| **Primary Use Case** | Understanding how their market's risk framework is configured |
| **Tabs They Access** | CRR Tab (view), Assets Tab (view), FA Tab (view), Reporting Tab (view), Alerts Tab (limited) |

### User Type 2: EDITOR (Full Access User)

| Attribute | Description |
|-----------|-------------|
| **Who They Are** | CRR Business Users, Compliance Analysts, Risk Managers |
| **What They Do** | Create sandboxes, edit configuration, promote changes to production |
| **Access Level** | FULL ACCESS across all tabs |
| **Can Do** | Create/edit sandboxes, create/edit assets, modify FA, configure alerts |
| **Primary Use Case** | Modifying the risk framework and testing changes before production |
| **Tabs They Access** | All tabs with full permissions |

---

## 1.3 Application Tab Structure (6 TABS)

The CRR application is divided into **6 main tabs**. Each tab has a specific purpose:

### TAB 1: CRR (Production View Dashboard)

| Aspect | Details |
|--------|---------|
| **Purpose** | View-only screen showing current PRODUCTION configuration |
| **Who Uses It** | VIEWERS (Market Compliance Officers) |
| **What It Shows** | How the risk framework is set up in production for their market |
| **Key Elements** | Risk Categories → Risk Elements → Rulesets → Rules hierarchy |
| **Editing Allowed?** | ❌ NO - View only |
| **Sandbox Content Shown?** | ❌ NO - Only PRODUCTION |

### TAB 2: SANDBOX (Editing Workspace)

| Aspect | Details |
|--------|---------|
| **Purpose** | Where actual EDITING and CONFIGURATION happens |
| **Who Uses It** | EDITORS only |
| **What It Shows** | List of sandboxes, sandbox creation, sandbox editing |
| **Key Elements** | Sandbox listing, Create Sandbox, Edit Sandbox, Promote Sandbox |
| **Editing Allowed?** | ✅ YES - Full editing inside sandboxes |
| **Types of Sandboxes** | Enterprise Sandbox, Market Sandbox |

### TAB 3: ASSETS (Production Asset Dashboard)

| Aspect | Details |
|--------|---------|
| **Purpose** | View-only dashboard showing PRODUCTION assets only |
| **Who Uses It** | VIEWERS and EDITORS |
| **What It Shows** | All assets that are currently in PRODUCTION status |
| **Key Elements** | Asset listing, Asset details, Asset usage (which rules use it) |
| **Editing Allowed?** | ❌ NO - View only in this tab (editing happens inside Sandbox) |
| **Draft/Sandbox Assets Shown?** | ❌ NO - Only PRODUCTION assets |

### TAB 4: FUNDAMENTAL ASSESSMENTS (Production FA Dashboard)

| Aspect | Details |
|--------|---------|
| **Purpose** | View-only dashboard showing PRODUCTION FA scores |
| **Who Uses It** | VIEWERS and EDITORS |
| **What It Shows** | FA scores currently used in production for different attributes |
| **Key Elements** | 6 FA Gates, Attributes, Current Scores |
| **Editing Allowed?** | ❌ NO - View only in this tab (editing happens inside Sandbox) |
| **New Scores Shown?** | ❌ NO - Only Current (Production) scores |

### TAB 5: REPORTING (Production Scoring Dashboard)

| Aspect | Details |
|--------|---------|
| **Purpose** | Production scoring dashboard showing risk distribution |
| **Who Uses It** | VIEWERS and EDITORS |
| **What It Shows** | Risk distribution across Center, Product, Legal Entity, Risk Score |
| **Key Metrics** | Customers, Accounts (3 sub-metrics), Risk buckets |
| **Editing Allowed?** | ❌ NO - View only |

**DETAILED REPORTING STRUCTURE:**

#### 5.1 Primary Dimensions
The report shows distribution across:
- **Center** (Market/Region - e.g., India, China, USA)
- **Product** (Product types)
- **Legal Entity** (Legal entity classifications)
- **Risk Score** (1-10 scale)

#### 5.2 Customer Metrics
- Total number of customers per segment

#### 5.3 Account Metrics (3 Columns)
| Column | Metric | Description |
|--------|--------|-------------|
| Column 1 | **Number of Independent Accounts** | Accounts not part of any hierarchy |
| Column 2 | **Number of Hierarchical Accounts** | Accounts that are part of a hierarchy |
| Column 3 | **Number of Hierarchies** | Total distinct hierarchies |

#### 5.4 Risk Distribution Buckets
| Risk Bucket | Score Range | Description |
|-------------|-------------|-------------|
| **Low Risk** | 1, 2, 3 | Minimal concern |
| **Medium Risk** | 4, 5, 6 | Moderate concern |
| **High Risk** | 7, 8, 9 | Elevated concern |
| **Prohibited** | 10 | Maximum risk - prohibited status |

> **Note:** Score of 10 is specifically called "PROHIBITED" not just "High Risk"

### TAB 6: ALERTS (Alert Configuration)

| Aspect | Details |
|--------|---------|
| **Purpose** | Configure alerts for specific situations |
| **Who Uses It** | EDITORS primarily (VIEWERS can view alerts) |
| **What It Shows** | Alert rules, triggered alerts, alert history |
| **Key Use Cases** | Sudden increase in risk rating, spike in customers/accounts |
| **Editing Allowed?** | ✅ YES for EDITORS to configure alerts |

**ALERT TYPES:**
- Sudden increase in risk rating for a market
- Spike in number of customers in a particular market
- Spike in number of accounts in a particular market
- Movement of customers between risk buckets
- Other configurable thresholds

---

# PART 2: SYSTEM STATES (EVOLUTION TIMELINE)

The CRR system evolves through distinct states. Documentation must cover ALL states.

## 2.1 State Timeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CRR SYSTEM STATE EVOLUTION                           │
└─────────────────────────────────────────────────────────────────────────────┘

DAY 0                    DAY 1-7                   DAY 8-30                
┌──────────┐             ┌──────────┐              ┌──────────┐             
│  NULL    │────────────▶│ENTERPRISE│─────────────▶│  FIRST   │
│  STATE   │             │ SETUP    │              │  MARKET  │
│          │             │          │              │          │
│ Nothing  │             │ First    │              │ First    │
│ exists   │             │ sandbox  │              │ market   │
│          │             │ created  │              │ goes     │
│          │             │ and      │              │ live     │
│          │             │ promoted │              │          │
└──────────┘             └──────────┘              └──────────┘             
                                                        │
                                                        ▼
DAY 90+                  DAY 30-90                     
┌──────────┐             ┌──────────┐             
│  MATURE  │◀────────────│  MULTI   │◀────────────┘
│  STATE   │             │  MARKET  │             
│          │             │          │             
│ Multiple │             │ Multiple │             
│ markets, │             │ markets  │             
│ active   │             │ being    │             
│ users,   │             │ set up   │             
│ full ops │             │          │             
└──────────┘             └──────────┘             
```

## 2.2 State Definitions

### STATE 1: NULL STATE (Day 0)

| Aspect | Description |
|--------|-------------|
| **What Exists** | NOTHING - Blank system |
| **Production** | Does not exist |
| **Sandboxes** | None |
| **Assets** | None |
| **Rules** | None |
| **FA** | Pre-configured (migrated from legacy) |
| **What User Sees** | Empty dashboards, disabled buttons |
| **First Action Required** | Create Enterprise Sandbox |

**Constraints in Null State:**
- Cannot create Market Sandbox (no Enterprise production exists)
- Cannot create assets (no sandbox exists)
- Cannot configure rules (no sandbox exists)
- Can only view empty dashboards

### STATE 2: ENTERPRISE SETUP (Day 1-7)

| Aspect | Description |
|--------|-------------|
| **What Exists** | First Enterprise Sandbox created |
| **Production** | Still does not exist |
| **Sandboxes** | 1 Enterprise Sandbox (WORKING status) |
| **Assets** | Being created inside sandbox |
| **Rules** | Being configured inside sandbox |
| **FA** | Can be modified inside sandbox |
| **What User Does** | Configure entire risk framework |
| **End Goal** | Promote Enterprise Sandbox to create first Production |

**Activities in This State:**
1. Create risk categories
2. Create risk elements
3. Create rulesets
4. Create rules
5. Create assets for rules
6. Configure FA scores
7. Submit for simulation
8. Review impact analysis
9. Get approval
10. Promote to production

### STATE 3: FIRST MARKET LAUNCH (Day 8-30)

| Aspect | Description |
|--------|-------------|
| **What Exists** | Enterprise Production + First Market Sandbox |
| **Production** | Enterprise Production is LIVE |
| **Sandboxes** | Can create Market Sandboxes now |
| **Assets** | Enterprise assets are now PRODUCTION status |
| **Rules** | Enterprise rules are now PRODUCTION status |
| **FA** | Enterprise FA scores are now Current Score |
| **What User Does** | Create first Market Sandbox and customize for market |

**What Changes for Markets:**
- Markets inherit Enterprise production as base
- Markets can customize (add/modify rules for their market)
- Markets can create market-specific assets
- Markets can set FA overrides

### STATE 4: MULTI-MARKET EXPANSION (Day 30-90)

| Aspect | Description |
|--------|-------------|
| **What Exists** | Enterprise Production + Multiple Market Productions |
| **Markets Active** | 2+ markets (e.g., India + China) |
| **Concurrent Work** | Multiple sandboxes can coexist |
| **Asset Sharing** | Assets can be used across markets |
| **Complexity** | Multi-user scenarios become relevant |

**Coexistence Rules:**
| Scenario | Allowed? |
|----------|----------|
| Enterprise Sandbox + India Sandbox | ✅ YES |
| Enterprise Sandbox + India Sandbox + China Sandbox | ✅ YES |
| 2 Enterprise Sandboxes simultaneously | ❌ NO (only 1 at a time) |
| India Sandbox + China Sandbox | ✅ YES |

### STATE 5: MATURE PRODUCTION STATE (Day 90+)

| Aspect | Description |
|--------|-------------|
| **What Exists** | Full production across Enterprise + all markets |
| **Assets** | 10+ assets in PRODUCTION, versioned |
| **Markets** | 3+ markets actively customized |
| **Sandboxes** | Multiple active simultaneously |
| **Users** | Multiple concurrent users |
| **FA** | Scores + Overrides configured |
| **Reporting** | Full risk distribution available |
| **Alerts** | Configured and triggering |

**This is the state where ALL operations must work flawlessly!**

---

# PART 3: CORE CRR COMPONENTS

## 3.1 Risk Framework Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RISK FRAMEWORK HIERARCHY                             │
└─────────────────────────────────────────────────────────────────────────────┘

LEVEL 1: RISK FRAMEWORK (Container)
│
├── LEVEL 2: RISK CATEGORIES (5 total)
│   │
│   ├── Customer Risk
│   │   │
│   │   └── LEVEL 3: RISK ELEMENTS
│   │       │
│   │       ├── Income Level
│   │       │   │
│   │       │   └── LEVEL 4: RULESETS
│   │       │       │
│   │       │       ├── Ruleset 1: High Income Check
│   │       │       │   │
│   │       │       │   └── LEVEL 5: RULES (with conditions)
│   │       │       │       ├── Rule 1: IF income > 100k AND...
│   │       │       │       └── Rule 2: IF income < 10k AND...
│   │       │       │
│   │       │       └── Ruleset 2: Income Source Check
│   │       │           └── Rules...
│   │       │
│   │       ├── Occupation Type
│   │       │   └── Rulesets → Rules
│   │       │
│   │       └── ... more elements
│   │
│   ├── Geographic Risk
│   │   └── Risk Elements → Rulesets → Rules
│   │
│   ├── Transaction Risk
│   │   └── Risk Elements → Rulesets → Rules
│   │
│   ├── Products & Services Risk
│   │   └── Risk Elements → Rulesets → Rules
│   │
│   └── ARFs & HROs
│       └── Risk Elements → Rulesets → Rules
│
└── Each level has configuration options
```

## 3.2 Rule Structure (CRITICAL DETAIL)

### Rule Creation Form Fields (IN THIS ORDER)

When creating a rule, the form fields appear in this EXACT order:

| Field # | Field Name | Description | Options/Validation |
|---------|------------|-------------|-------------------|
| 1 | **Description** | Human-readable description of what the rule does | Free text, required |
| 2 | **Multiplier Type** | How the multiplier value is determined | Dropdown: "Value" OR "Fundamental Assessment" |
| 3a | **Multiplier Value** | (If Multiplier Type = Value) Static number | Decimal (e.g., 2.0, 3.5) |
| 3b | **FA Gate Selection** | (If Multiplier Type = FA) Which FA gate to use | Dropdown: Geography, Industry, Product, Structure, Occupation, Acquisition Channel |
| 4 | **Datapoint** | The customer data field to check | Dropdown from available datapoints |
| 5 | **Operator** | How to compare datapoint with value | IN, NOT IN, EQUALS, NOT EQUALS, GREATER THAN, LESS THAN |
| 6 | **Asset/Value Selection** | What to compare against | Asset dropdown (filtered by datapoint's reference table) |

**Important:** Asset dropdown is **FILTERED** based on the selected datapoint's reference table. Only assets that match the reference table are shown.

### Rule Logical Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| **AND** | Both conditions must be true | Condition1 AND Condition2 |
| **OR** | Either condition can be true | Condition1 OR Condition2 |
| **( )** | Grouping for complex logic | (Cond1 OR Cond2) AND Cond3 |

### Market Level Settings

These settings apply to **ALL rulesets** in a Risk Element:

| Setting | Description | Options |
|---------|-------------|---------|
| **Applicability** | Which customer type this applies to | Entities, Individuals, Intermediaries |
| **Default Multiplier** | Fallback when no ruleset matches | Numeric value |
| **Weighting** | Weight in overall score calculation | Numeric value |

---

## 3.3 Asset Lifecycle

### Asset States

```
┌─────────┐     ┌─────────┐     ┌────────────┐     ┌──────────┐
│  DRAFT  │────▶│ SANDBOX │────▶│ PRODUCTION │────▶│ ARCHIVED │
└─────────┘     └─────────┘     └────────────┘     └──────────┘
     │               │                │                  │
     │               │                │                  │
   Created       Linked to        Sandbox            New version
   but not       a rule in        promoted           promoted
   linked        sandbox                             replaces
```

### Asset State Definitions

| State | When | Visibility |
|-------|------|------------|
| **DRAFT** | Asset created but not linked to any rule | Only in creating sandbox |
| **SANDBOX** | Asset linked to rule inside sandbox | Only in that sandbox |
| **PRODUCTION** | Sandbox promoted, asset is live | Visible everywhere |
| **ARCHIVED** | New version promoted, old version archived | Version history only |

### Asset Visibility Rules

| Context | DRAFT | SANDBOX | PRODUCTION | ARCHIVED |
|---------|-------|---------|------------|----------|
| CRR Tab (Production View) | ❌ | ❌ | ✅ | ❌ |
| Assets Tab (Dashboard) | ❌ | ❌ | ✅ | ❌ |
| Enterprise Sandbox | ✅ | ✅ | ✅ | Version history |
| Market Sandbox | ❌ | ❌ | ✅ | ❌ |

### Asset Creation Rules

| Rule | Description |
|------|-------------|
| **Enterprise Only** | Assets can ONLY be created/edited inside Enterprise Sandbox |
| **Market Linking** | Market Sandboxes can only LINK existing PRODUCTION assets |
| **Quick Asset** | Special feature for markets to create assets (uses hidden Enterprise sandbox) |
| **Unique Names** | Asset names must be unique within the system |
| **Reference Table** | Each asset is linked to a specific reference data table |

---

## 3.4 Fundamental Assessment (FA)

### The 6 FA Gates

| Gate # | Gate Name | Example Attributes | What It Measures |
|--------|-----------|-------------------|------------------|
| 1 | **Geography** | Countries (Venezuela, Germany, India) | Risk of account holder's country |
| 2 | **Industry** | Casinos, Hotels, Money Services | Risk of customer's industry |
| 3 | **Product** | Corp CPC, Corp CTL, Consumer Cards | Risk of product type |
| 4 | **Structure** | Business types, Legal structures | Risk of entity structure |
| 5 | **Occupation** | PEP, High-risk occupations | Risk of customer's occupation |
| 6 | **Acquisition Channel** | Direct, Broker, Online | Risk of how customer was acquired |

### FA Score Calculation

Each attribute has **10 questions** ranked by priority:
- Question 1 (Rank 10) = Highest priority
- Question 10 (Rank 1) = Lowest priority

**FA Score = Score of the HIGHEST RANKED question answered YES**

```
Example: Venezuela

Q1 (Rank 10): OFAC prohibited? → YES ✓
Q2 (Rank 9): FATF high-risk? → YES ✓
Q3 (Rank 8): Thomson Reuters list? → YES ✓
Q4 (Rank 7): Weak AML laws? → NO
...

FA Score = 10 (highest YES is Q1 with rank 10)
```

### Current Score vs New Score

| Column | What It Contains | Used For |
|--------|------------------|----------|
| **Current Score** | Score currently in PRODUCTION | Production scoring |
| **New Score** | Score configured in sandbox | Simulation scoring |

After promotion: New Score → becomes → Current Score

### FA Overrides

Markets can override Enterprise FA scores:

```
Industry: Casinos
├── Enterprise FA Score: 6
├── India Override: 8 (gambling more restricted)
└── USA Override: 3 (regulated but legal)
```

### FA Score Range

| Value | Meaning |
|-------|---------|
| **1** | Lowest risk |
| **10** | Highest risk (PROHIBITED) |
| **0** | ❌ NOT ALLOWED - Never zero |

---

## 3.5 Sandbox Types & Lifecycle

### Enterprise Sandbox

| Aspect | Description |
|--------|-------------|
| **Scope** | Affects ALL markets globally |
| **Can Create** | Assets, Rules, FA changes |
| **Maximum Active** | Only 1 at a time |
| **Coexistence** | CAN coexist with Market Sandboxes |
| **Promotion Effect** | All changes go to Enterprise Production |

### Market Sandbox

| Aspect | Description |
|--------|-------------|
| **Scope** | Affects ONLY that specific market |
| **Can Create** | Market-specific rules, FA overrides |
| **Cannot Create** | Assets (must link existing PRODUCTION assets) |
| **Maximum Active** | Multiple can coexist |
| **Coexistence** | CAN coexist with Enterprise + other Markets |
| **Promotion Effect** | Changes apply only to that market |

### Sandbox Lifecycle

```
┌──────────┐     ┌───────────┐     ┌──────────┐     ┌──────────┐
│ CREATED  │────▶│  WORKING  │────▶│SUBMITTED │────▶│ APPROVED │
└──────────┘     └───────────┘     └──────────┘     └──────────┘
                       │                                  │
                       │                                  ▼
                       │                          ┌──────────┐
                       │                          │ PROMOTED │
                       │                          └──────────┘
                       │                                  │
                       ▼                                  ▼
                 ┌──────────┐                     ┌──────────┐
                 │ REJECTED │                     │ DELETED  │
                 └──────────┘                     │(sandbox) │
                       │                          └──────────┘
                       ▼
                 ┌──────────┐
                 │ DELETED  │
                 └──────────┘
```

---

# PART 4: SECTION-BY-SECTION BREAKDOWN

## Overview of All Sections

| Section # | Section Name | Output File | Coverage |
|-----------|--------------|-------------|----------|
| 0 | Foundation | `CRR_Journey_00_Foundation.md` | System overview, users, states |
| 1 | CRR Tab | `CRR_Journey_01_CRR_Tab.md` | Production view dashboard |
| 2 | Sandbox Tab | `CRR_Journey_02_Sandbox_Tab.md` | Sandbox management |
| 3 | Assets Tab | `CRR_Journey_03_Assets_Tab.md` | Asset dashboard |
| 4 | FA Tab | `CRR_Journey_04_FA_Tab.md` | Fundamental Assessment |
| 5 | Reporting Tab | `CRR_Journey_05_Reporting_Tab.md` | Scoring dashboard |
| 6 | Alerts Tab | `CRR_Journey_06_Alerts_Tab.md` | Alert configuration |
| 7 | Inside Sandbox | `CRR_Journey_07_Inside_Sandbox.md` | Editing operations inside sandbox |
| 8 | Cross-Tab Scenarios | `CRR_Journey_08_Cross_Tab_Scenarios.md` | Multi-user, cross-tab flows |
| 9 | Edge Cases | `CRR_Journey_09_Edge_Cases.md` | All edge cases with resolutions |
| 10 | QA Master | `CRR_Journey_10_QA_Master.md` | Consolidated test cases |
| 11 | Design Decisions | `CRR_Journey_11_Design_Decisions.md` | Rationale for design choices |

---

## SECTION 0: FOUNDATION

**Output File:** `CRR_Journey_00_Foundation.md`

### What This Section Covers:
1. Complete system overview
2. User types (Viewer vs Editor) - detailed
3. Application tab structure - detailed
4. System states (Null → Mature) - detailed
5. Navigation hierarchy
6. Terminology glossary
7. Prerequisites for using the system

### Detailed Breakdown:

#### 0.1 System Overview
- What is CRR?
- What problem does it solve?
- Who uses it?
- High-level architecture

#### 0.2 User Types Deep Dive
- Viewer: Complete profile, permissions, use cases
- Editor: Complete profile, permissions, use cases
- Permission matrix: Tab × User Type
- Login/Authentication flow

#### 0.3 Tab Structure Deep Dive
- Tab 1: CRR - Complete description
- Tab 2: Sandbox - Complete description
- Tab 3: Assets - Complete description
- Tab 4: Fundamental Assessments - Complete description
- Tab 5: Reporting - Complete description (with all metrics)
- Tab 6: Alerts - Complete description

#### 0.4 System States Deep Dive
- Null State: What exists, constraints, first action
- Enterprise Setup: Activities, goals, end state
- First Market: Changes, market customization
- Multi-Market: Coexistence, concurrent work
- Mature State: Full operations, all features active

#### 0.5 Navigation Hierarchy
- Tab navigation
- Within-tab navigation
- Breadcrumbs
- Context switching (sandbox vs production)

#### 0.6 Terminology Glossary
- All CRR-specific terms defined
- Examples for each term

#### 0.7 QA Test Cases for Foundation
- System access tests
- Permission verification tests
- Navigation tests

---

## SECTION 1: TAB 1 - CRR (Production View Dashboard)

**Output File:** `CRR_Journey_01_CRR_Tab.md`

### What This Section Covers:
1. What the CRR Tab shows
2. Viewer perspective (Market Compliance Officers)
3. What configuration is visible
4. How to navigate the risk framework
5. What CANNOT be done (editing disabled)
6. Comparison with Sandbox view

### Detailed Breakdown:

#### 1.1 Tab Overview
- Purpose: View-only production configuration
- Primary users: Viewers (Market Compliance Officers)
- What they see: Current production setup for their market

#### 1.2 Screen Layout
- Header section
- Navigation panel
- Main content area
- Footer/Status area

#### 1.3 What Configuration Is Visible
- Risk Categories (5 total)
- Risk Elements under each category
- Rulesets under each element
- Rules under each ruleset
- Rule details (conditions, multipliers, etc.)

#### 1.4 Navigation Flow
- Clicking on Risk Category
- Drilling down to Risk Element
- Viewing Rulesets
- Viewing individual Rules
- Back navigation

#### 1.5 Data Displayed for Each Level
- Category level: Name, count of elements
- Element level: Name, count of rulesets
- Ruleset level: Name, count of rules, settings
- Rule level: Full configuration details

#### 1.6 What Is Disabled/Hidden
- All edit buttons
- Create buttons
- Delete buttons
- Sandbox-related actions

#### 1.7 Market-Specific View
- How market filtering works
- What India Viewer sees vs China Viewer

#### 1.8 QA Test Cases
- Positive: View each level successfully
- Negative: Attempt to edit (should fail)
- Boundary: Large number of rules display

---

## SECTION 2: TAB 2 - SANDBOX

**Output File:** `CRR_Journey_02_Sandbox_Tab.md`

### What This Section Covers:
1. Sandbox listing screen
2. Create Enterprise Sandbox
3. Create Market Sandbox
4. Edit Sandbox (go inside)
5. Delete/Reject Sandbox
6. Promote Sandbox to Production
7. Sandbox coexistence rules
8. Sandbox lifecycle states
9. All edge cases

### Detailed Breakdown:

#### 2.1 Sandbox Listing Screen
- What Viewer sees (read-only list)
- What Editor sees (with action buttons)
- Columns: Name, Scope, Status, Created By, Date
- Filtering options
- Sorting options

#### 2.2 Create Enterprise Sandbox
- Preconditions (no existing Enterprise sandbox)
- Step-by-step flow
- Form fields
- Validation rules
- Post-creation state

#### 2.3 Create Market Sandbox
- Preconditions (Enterprise production must exist)
- Step-by-step flow
- Market selection
- Form fields
- Validation rules
- Post-creation state

#### 2.4 Edit Sandbox (Go Inside)
- Clicking on sandbox row
- What opens (sandbox editing environment)
- Context switch indicator
- Available actions inside

#### 2.5 Submit Sandbox for Simulation
- Preconditions
- Submission flow
- Simulation execution
- Viewing results

#### 2.6 Approve/Reject Sandbox
- Approval workflow
- Rejection reasons
- What happens to changes on rejection

#### 2.7 Promote Sandbox to Production
- Preconditions (approved)
- Promotion confirmation
- Impact on production
- Post-promotion state
- Sandbox deletion after promotion

#### 2.8 Delete Sandbox
- When allowed
- Confirmation dialog
- Impact on contents
- Audit trail

#### 2.9 Coexistence Rules
- Enterprise + Market: Allowed
- Enterprise + Enterprise: NOT Allowed
- Market + Market: Allowed
- During promotion: Locking behavior

#### 2.10 Edge Cases
- Create sandbox when one exists
- Delete sandbox while user inside
- Promote while simulation running
- Reject after partial changes
- Network failure during promotion

#### 2.11 QA Test Cases
- All create scenarios
- All delete scenarios
- All promote scenarios
- Permission tests
- Concurrent user tests

---

## SECTION 3: TAB 3 - ASSETS

**Output File:** `CRR_Journey_03_Assets_Tab.md`

### What This Section Covers:
1. Asset listing dashboard (production only)
2. Asset detail view
3. Asset usage (which rules use it)
4. Asset version history
5. What CANNOT be done from this tab
6. How assets are created (inside Sandbox)
7. Quick Asset feature

### Detailed Breakdown:

#### 3.1 Asset Listing Dashboard
- Only PRODUCTION assets shown
- Columns: Name, Description, Reference Table, Used By Count, Version
- Filtering options
- Sorting options
- Search functionality

#### 3.2 Asset Detail View
- Clicking on asset row
- Name, Description
- Reference Table
- Values in the asset
- Usage list (rules using this asset)
- Version history

#### 3.3 Asset Usage
- Which rulesets use this asset
- Which rules specifically
- Impact analysis preview

#### 3.4 Version History
- All versions listed
- Current (PRODUCTION) version highlighted
- ARCHIVED versions shown
- Version comparison (if applicable)

#### 3.5 What Is Disabled
- Create Asset button (use Sandbox)
- Edit Asset button (use Sandbox)
- Delete Asset button (use Sandbox)

#### 3.6 How Assets Are Created (Reference)
- Must go to Sandbox Tab
- Open or create Enterprise Sandbox
- Create asset inside sandbox
- Promote to make it PRODUCTION

#### 3.7 Quick Asset Feature
- What it is
- When it appears (Market Sandbox)
- How it works (hidden Enterprise sandbox)
- Limitations

#### 3.8 Edge Cases
- Asset with many rules (display)
- Asset with archived versions
- Asset in multiple sandboxes

#### 3.9 QA Test Cases
- View asset list
- View asset details
- View usage
- View versions
- Attempt edit (should be disabled)

---

## SECTION 4: TAB 4 - FUNDAMENTAL ASSESSMENTS

**Output File:** `CRR_Journey_04_FA_Tab.md`

### What This Section Covers:
1. FA overview dashboard (production scores only)
2. The 6 Gates
3. Attributes under each gate
4. Current Scores (production)
5. What CANNOT be done from this tab
6. How FA is edited (inside Sandbox)

### Detailed Breakdown:

#### 4.1 FA Overview Dashboard
- Only Current (PRODUCTION) scores shown
- Navigation: Gate → Attribute → Questionnaire
- No editing allowed from this tab

#### 4.2 The 6 Gates Landing Screen
- List of 6 gates
- Count of attributes in each
- Click to drill down

#### 4.3 Attributes List
- Under each gate
- Attribute name
- Current Score displayed
- Click to see questionnaire

#### 4.4 Questionnaire View (Read-Only)
- 10 questions shown
- Current answers (YES/NO)
- Calculated score shown
- All fields disabled

#### 4.5 Overrides View
- Market-specific overrides displayed
- Override history
- No editing allowed

#### 4.6 Score Range Display
- 1-10 scale visualization
- Color coding (Low/Medium/High/Prohibited)
- Current score highlighted

#### 4.7 What Is Disabled
- Answer editing
- Calculate button
- Override setting

#### 4.8 How FA Is Edited (Reference)
- Must go to Sandbox Tab
- Open Enterprise Sandbox
- Navigate to FA inside sandbox
- Edit answers, recalculate
- Promote to update Current Score

#### 4.9 Edge Cases
- Attribute with many overrides
- Gate with many attributes
- Display of score = 10 (Prohibited)

#### 4.10 QA Test Cases
- View all gates
- View attributes
- View questionnaire
- Attempt edit (disabled)

---

## SECTION 5: TAB 5 - REPORTING

**Output File:** `CRR_Journey_05_Reporting_Tab.md`

### What This Section Covers:
1. Production Scoring Dashboard
2. Risk distribution metrics
3. Dimensions: Center, Product, Legal Entity, Risk Score
4. Customer metrics
5. Account metrics (3 types)
6. Risk buckets (Low/Medium/High/Prohibited)
7. Export functionality

### Detailed Breakdown:

#### 5.1 Dashboard Overview
- Purpose: Production scoring visibility
- Users: Viewers and Editors
- Data: Real-time production metrics

#### 5.2 Primary Dimensions

**5.2.1 Center (Market/Region)**
- India, China, USA, Belgium, etc.
- Filter by center
- Center-wise distribution

**5.2.2 Product**
- Product types
- Filter by product
- Product-wise distribution

**5.2.3 Legal Entity**
- Legal entity classifications
- Filter by legal entity
- Entity-wise distribution

**5.2.4 Risk Score**
- 1-10 scale
- Score-wise distribution
- Trend over time (if applicable)

#### 5.3 Customer Metrics
- Total customers per segment
- Customer count by risk bucket
- Customer movement analysis

#### 5.4 Account Metrics (3 Columns)

| Column | Metric | Definition |
|--------|--------|------------|
| 1 | **Independent Accounts** | Accounts NOT part of any hierarchy |
| 2 | **Hierarchical Accounts** | Accounts that ARE part of a hierarchy |
| 3 | **Hierarchies** | Count of distinct hierarchies |

#### 5.5 Risk Distribution Buckets

| Bucket | Score Range | Color | Description |
|--------|-------------|-------|-------------|
| **Low Risk** | 1, 2, 3 | Green | Minimal risk |
| **Medium Risk** | 4, 5, 6 | Yellow | Moderate risk |
| **High Risk** | 7, 8, 9 | Orange | Elevated risk |
| **Prohibited** | 10 | Red | Maximum - Prohibited status |

#### 5.6 Report Table Structure

```
┌────────────┬──────────┬──────────┬─────────────────────────────────┬─────────────────────────────────┐
│            │          │          │          CUSTOMERS               │           ACCOUNTS              │
│  CENTER    │ PRODUCT  │  LEGAL   ├─────┬────────┬────────┬─────────┼───────────┬────────────┬────────┤
│            │          │  ENTITY  │ LOW │ MEDIUM │  HIGH  │PROHIBIT │INDEPENDENT│HIERARCHICAL│HIERARCH│
├────────────┼──────────┼──────────┼─────┼────────┼────────┼─────────┼───────────┼────────────┼────────┤
│ India      │ CPC      │ Corp     │ 500 │  200   │   50   │   10    │    300    │    400     │   50   │
│ India      │ CTL      │ Corp     │ 300 │  150   │   30   │    5    │    200    │    250     │   30   │
│ China      │ CPC      │ SME      │ 800 │  300   │   80   │   15    │    500    │    600     │   80   │
│ ...        │ ...      │ ...      │ ... │  ...   │  ...   │  ...    │    ...    │    ...     │  ...   │
└────────────┴──────────┴──────────┴─────┴────────┴────────┴─────────┴───────────┴────────────┴────────┘
```

#### 5.7 Filtering Options
- By Center
- By Product
- By Legal Entity
- By Risk Bucket
- Date range

#### 5.8 Export Functionality
- Export to Excel
- Export to PDF
- Select columns to export
- Select filters to apply

#### 5.9 Edge Cases
- Large data volumes
- Empty segments
- All customers in one bucket

#### 5.10 QA Test Cases
- View full report
- Apply each filter
- Export report
- Verify calculations

---

## SECTION 6: TAB 6 - ALERTS

**Output File:** `CRR_Journey_06_Alerts_Tab.md`

### What This Section Covers:
1. Alert listing screen
2. Alert types
3. Alert configuration (Editors only)
4. Alert triggers
5. Alert management
6. Notification delivery

### Detailed Breakdown:

#### 6.1 Alert Listing Screen
- Active alerts
- Triggered alerts history
- Alert status (Active/Triggered/Dismissed)

#### 6.2 Alert Types

| Alert Type | Trigger Condition | Example |
|------------|-------------------|---------|
| **Risk Rating Spike** | Sudden increase in avg risk rating | Market avg went from 4.5 to 6.2 |
| **Customer Count Spike** | Sudden increase in customers | 20% increase in India customers |
| **Account Count Spike** | Sudden increase in accounts | 15% increase in accounts |
| **Bucket Movement** | Large movement between risk buckets | 100 customers moved to High Risk |
| **Threshold Breach** | Configurable threshold crossed | >500 customers in Prohibited |

#### 6.3 Alert Configuration (Editors Only)

**Configuration Form:**
| Field | Description | Example |
|-------|-------------|---------|
| Alert Name | Human-readable name | "India High Risk Spike" |
| Alert Type | Type from dropdown | Risk Rating Spike |
| Scope | Market/Product/etc | India |
| Threshold | Trigger value | 10% increase |
| Time Window | Comparison period | Last 7 days |
| Recipients | Who gets notified | email@amex.com |

#### 6.4 Alert Triggers
- How alerts are evaluated
- Frequency of evaluation
- What triggers notification

#### 6.5 Alert Management
- View triggered alerts
- Acknowledge alert
- Dismiss alert
- Alert history

#### 6.6 Viewer vs Editor Permissions
- Viewer: Can see triggered alerts only
- Editor: Can configure + see + manage alerts

#### 6.7 Edge Cases
- Multiple alerts triggering simultaneously
- False positive handling
- Alert configuration conflicts

#### 6.8 QA Test Cases
- Configure new alert
- Trigger alert (test mode)
- Acknowledge alert
- View history

---

## SECTION 7: INSIDE SANDBOX (Editing Operations)

**Output File:** `CRR_Journey_07_Inside_Sandbox.md`

### What This Section Covers:
1. Entering a sandbox (context switch)
2. Rule configuration inside sandbox
3. Asset creation inside sandbox
4. FA modification inside sandbox
5. Simulation submission
6. Exiting sandbox

### Detailed Breakdown:

*[Extensive coverage of all editing operations within sandbox environment]*

---

## SECTION 8: CROSS-TAB SCENARIOS

**Output File:** `CRR_Journey_08_Cross_Tab_Scenarios.md`

### What This Section Covers:
1. Complete user journeys (end-to-end)
2. Multi-user concurrent scenarios
3. Cross-tab dependencies
4. Race condition handling

### Detailed Breakdown:

*[Extensive coverage of cross-tab flows and multi-user scenarios]*

---

## SECTION 9: EDGE CASES (Comprehensive)

**Output File:** `CRR_Journey_09_Edge_Cases.md`

### What This Section Covers:
1. All edge cases not covered in individual sections
2. Naughty user scenarios
3. System failure scenarios
4. Race conditions
5. Resolution for each edge case

### Categories of Edge Cases:

#### 9.1 Simultaneous Operations
- Two users editing same rule
- Link + Unlink same asset
- Delete + Link same asset
- Create + Delete same sandbox

#### 9.2 State Transition Conflicts
- Promotion during simulation
- Rejection during editing
- Deletion during viewing

#### 9.3 Data Integrity
- Orphan assets
- Circular dependencies
- Invalid references

#### 9.4 Session & Timing
- Session timeout during edit
- Network failure during promotion
- Long-running simulation timeout

#### 9.5 Permission Edge Cases
- Viewer attempting edit
- Editor losing permissions mid-session
- Role change during active sandbox

---

## SECTION 10: QA MASTER (Consolidated Test Cases)

**Output File:** `CRR_Journey_10_QA_Master.md`

### What This Section Covers:
1. Complete test case repository
2. Organized by tab
3. Organized by operation
4. Regression test suite
5. Integration test scenarios

---

## SECTION 11: DESIGN DECISIONS

**Output File:** `CRR_Journey_11_Design_Decisions.md`

### What This Section Covers:
1. Why Enterprise-Only asset creation
2. Why Quick Asset via hidden sandbox
3. Why sandbox coexistence allowed
4. Version management strategy
5. Conflict resolution approach
6. Performance considerations
7. Security considerations

---

# PART 5: MULTI-USER SCENARIOS FORMAT

For all multi-user scenarios, use this time-sequence table format:

```
| Time | User A (Role) | User B (Role) | System State | Notes |
|------|---------------|---------------|--------------|-------|
| T1   | Action        | -             | State        | ...   |
| T2   | -             | Action        | State        | ...   |
| T3   | Reaction      | Sees result   | State        | ...   |
```

---

# PART 6: EDGE CASE DOCUMENTATION FORMAT

For all edge cases, use this format:

```
### Edge Case [#]: [Name]

**Scenario:**
[Describe the exact steps that create this edge case]

**System Behavior:**
[What should the system do]

**User Experience:**
[What the user sees/experiences]

**Resolution:**
[How the situation is resolved]

**Prevention:**
[How to prevent this in the future]

**Test Case:**
| Test ID | Steps | Expected Result |
|---------|-------|-----------------|
| TC_EC_# | ...   | ...             |
```

---

# PART 7: SECTION TEMPLATE (MANDATORY)

Every section document **MUST** follow this template:

```markdown
# CRR User Journey: [SECTION NAME]

## Document Metadata
| Attribute | Value |
|-----------|-------|
| Section # | [#] |
| Version | 1.0 |
| Last Updated | [Date] |
| Author | CRR Documentation AI |

---

## 1. Overview
[Brief description - 2-3 paragraphs]

### 1.1 Purpose of This Section
[What this section covers]

### 1.2 Who Should Read This
[Target audience]

### 1.3 Prerequisites
[What reader should know before reading this]

---

## 2. Screen/Tab Description

### 2.1 What VIEWER Sees
[Complete description of read-only view]

[Include ASCII diagram of screen layout]

### 2.2 What EDITOR Sees
[Complete description of editable view]

[Include ASCII diagram of screen layout with action buttons]

### 2.3 Navigation
[How to get to this tab]

### 2.4 Screen Elements
[List all UI elements: buttons, tables, filters, etc.]

---

## 3. All Possible Operations

| # | Operation | Who Can Do | Results In |
|---|-----------|------------|------------|
| 1 | [Action]  | Viewer/Editor | [State change] |
| 2 | [Action]  | Editor only | [State change] |
| ... | ... | ... | ... |

---

## 4. Detailed User Flows

### 4.1 [Operation 1 Name]

**Preconditions:**
- [Condition 1]
- [Condition 2]

**Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]
...

**Postconditions:**
- [Result 1]
- [Result 2]

**System State Change:**
| Before | After |
|--------|-------|
| [State] | [New State] |

**Example:**
[Concrete example with sample data]

---

### 4.2 [Operation 2 Name]
[Same structure as 4.1]

---

## 5. Multi-User Scenarios

### 5.1 [Scenario Name]

| Time | User A | User B | System State |
|------|--------|--------|--------------|
| T1   | ...    | ...    | ...          |

**Expected Behavior:**
[What should happen]

---

## 6. Edge Cases

### 6.1 [Edge Case 1]
[Full edge case documentation as per format]

### 6.2 [Edge Case 2]
[Full edge case documentation]

...

---

## 7. QA Test Cases

### 7.1 Positive Test Cases

| Test ID | Test Case Name | Preconditions | Steps | Expected Result | Priority |
|---------|----------------|---------------|-------|-----------------|----------|
| POS_001 | ... | ... | ... | ... | High |
| POS_002 | ... | ... | ... | ... | Medium |
| ... | ... | ... | ... | ... | ... |

### 7.2 Negative Test Cases

| Test ID | Test Case Name | Preconditions | Steps | Expected Result | Priority |
|---------|----------------|---------------|-------|-----------------|----------|
| NEG_001 | ... | ... | ... | ... | High |
| ... | ... | ... | ... | ... | ... |

### 7.3 Boundary Test Cases

| Test ID | Test Case Name | Boundary Condition | Steps | Expected Result | Priority |
|---------|----------------|-------------------|-------|-----------------|----------|
| BND_001 | ... | ... | ... | ... | High |
| ... | ... | ... | ... | ... | ... |

### 7.4 Integration Test Cases

| Test ID | Test Case Name | Cross-Tab Flow | Steps | Expected Result | Priority |
|---------|----------------|----------------|-------|-----------------|----------|
| INT_001 | ... | ... | ... | ... | High |
| ... | ... | ... | ... | ... | ... |

---

## 8. Summary

### 8.1 Key Takeaways
[Bullet points of most important things to remember]

### 8.2 Common Mistakes
[What users often get wrong]

### 8.3 Best Practices
[Recommended approaches]

---

## 9. Related Sections
[Links to other sections that relate to this one]

---
```

---

# PART 8: QA TEST CASE REQUIREMENTS

## Minimum Test Cases Per Section

| Category | Minimum Count | Priority Distribution |
|----------|---------------|----------------------|
| Positive Tests | 10+ | 3 High, 4 Medium, 3 Low |
| Negative Tests | 5+ | 2 High, 2 Medium, 1 Low |
| Boundary Tests | 3+ | 1 High, 1 Medium, 1 Low |
| Integration Tests | 3+ | As applicable |

## Test Case Attributes

Every test case **MUST** include:
- Test ID (unique)
- Test Case Name (descriptive)
- Preconditions (what must be true before test)
- Steps (numbered, specific)
- Expected Result (precise, verifiable)
- Priority (High/Medium/Low)

---

# PART 9: VALIDATION CHECKLIST (PER SECTION)

Before marking a section complete, verify ALL items:

### Coverage Checklist
- [ ] All screens on the tab are documented
- [ ] Both VIEWER and EDITOR perspectives covered
- [ ] Every UI element described
- [ ] Every possible action listed
- [ ] Navigation flow documented

### Flow Checklist
- [ ] Every operation has preconditions
- [ ] Every operation has numbered steps
- [ ] Every operation has postconditions
- [ ] State changes documented with Before/After
- [ ] Examples provided

### Multi-User Checklist
- [ ] Concurrent access scenarios covered
- [ ] Time-sequence tables used
- [ ] Lock/conflict handling documented

### Edge Case Checklist
- [ ] At least 5 edge cases documented
- [ ] Each has scenario description
- [ ] Each has system behavior
- [ ] Each has resolution

### QA Checklist
- [ ] 10+ positive test cases
- [ ] 5+ negative test cases
- [ ] 3+ boundary test cases
- [ ] All test cases have required attributes

### Quality Checklist
- [ ] No technical jargon unexplained
- [ ] All terms defined or linked to glossary
- [ ] ASCII diagrams for complex layouts
- [ ] Examples use realistic data

---

# PART 10: EXECUTION WORKFLOW

```
┌──────────────────────────────────────────────────────────────────────┐
│  USER SAYS: "Start" or "Begin"                                        │
└──────────────────────┬───────────────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  EXECUTE SECTION 0: Foundation                                        │
│  Create file: Asset_Manager_Journey/CRR_Journey_00_Foundation.md      │
│  Follow template, include all subsections                             │
│  Complete validation checklist                                        │
└──────────────────────┬───────────────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  NOTIFY USER: "Section 0 complete. Review and say 'Next' to proceed" │
└──────────────────────┬───────────────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  WAIT FOR USER PERMISSION                                             │
│  Do NOT proceed until user explicitly says to continue                │
└──────────────────────┬───────────────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  EXECUTE SECTION 1: CRR Tab                                           │
│  Create file: Asset_Manager_Journey/CRR_Journey_01_CRR_Tab.md         │
│  Follow template, include all subsections                             │
│  Complete validation checklist                                        │
└──────────────────────┬───────────────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  NOTIFY USER: "Section 1 complete. Review and say 'Next' to proceed" │
└──────────────────────┬───────────────────────────────────────────────┘
                       ▼
                     ... [REPEAT FOR ALL SECTIONS] ...
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  ALL 12 SECTIONS COMPLETE                                             │
│  Notify user of completion                                            │
│  Provide summary of all created files                                 │
└──────────────────────────────────────────────────────────────────────┘
```

---

# PART 11: GUARDRAILS

## DO (REQUIRED BEHAVIORS):

- ✅ Complete ONE section fully before asking to proceed
- ✅ Follow the section template EXACTLY
- ✅ Include ALL required test cases
- ✅ Show BOTH Viewer and Editor perspectives
- ✅ Use ASCII diagrams for UI layouts
- ✅ Provide CONCRETE examples with sample data
- ✅ Document EVERY edge case with resolution
- ✅ Use time-sequence tables for multi-user scenarios
- ✅ Make the document LONGER, not shorter
- ✅ Over-explain rather than under-explain
- ✅ Link related sections at the end of each section

## DON'T (PROHIBITED BEHAVIORS):

- ❌ Combine multiple sections in one response
- ❌ Skip any subsection in the template
- ❌ Use less than minimum test cases
- ❌ Leave edge cases without resolution
- ❌ Assume user knows CRR terminology
- ❌ Use technical jargon without explanation
- ❌ Proceed to next section without user permission
- ❌ Shorten or summarize to save space
- ❌ Use generic examples instead of CRR-specific ones
- ❌ Omit any validation checklist item

---

# PART 12: REFERENCE FILES

| File Path | What It Contains | Use For |
|-----------|------------------|---------|
| `context/CRR_Zero_to_Production_Journey.md` | Existing journey doc | Structure reference |
| `context/Asset_Manager_Journey/*.md` | Asset Manager docs | Asset details |
| `context/CRR_Product_Requirements_Document.md` | PRD | Requirements |
| `Backlog/12.8_Sandbox_-_Simulation_functionality/` | Sandbox specs | Sandbox details |
| `Backlog/12.1_CRR_Structure_and_Setup/` | Structure specs | Framework details |
| `Backlog/12.5_Configurability/` | Config specs | Rule/FA config |
| `Backlog/12.6_Centralized_lists__Fundamental_AssessmentsNotable_Lists/` | FA/Asset specs | FA details |
| `Backlog/12.13_Reporting__Dashboards/` | Reporting specs | Report details |
| `Backlog/12.20_Notifications/` | Alert specs | Alert details |

---

# READY TO BEGIN?

When user says "Start", "Begin", or gives explicit permission:

1. Begin with **SECTION 0: FOUNDATION**
2. Create file `CRR_Journey_00_Foundation.md` in the Asset_Manager_Journey folder
3. Follow the template in Part 7
4. Complete all validation items in Part 9
5. Include all required test cases from Part 8
6. Notify user when complete
7. **WAIT** for user to say "Next" before proceeding to Section 1

---

*This meta-prompt is comprehensive, detailed, and designed to produce high-quality, QA-friendly documentation for the entire CRR platform.*

**Document Length Target:** 10,000-15,000 words MINIMUM across all sections
**Each Section:** 1,000-2,000 words
**Quality Standard:** Enterprise-grade, production-ready documentation
