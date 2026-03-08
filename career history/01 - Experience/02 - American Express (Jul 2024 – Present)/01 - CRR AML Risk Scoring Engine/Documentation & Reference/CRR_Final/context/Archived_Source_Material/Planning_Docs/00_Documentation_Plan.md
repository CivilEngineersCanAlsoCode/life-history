# Asset Manager Journey - Complete Stage Definition
## Granular Breakdown of Every Step

---

## 🎯 Purpose

This document defines **every stage** of the Asset Manager journey in the most granular way possible. No edge cases here - just the journey definition.

**Starting Point:** Completely blank CRR system (no production, no sandbox, no assets)
**End Point:** Mature system with Enterprise + multiple markets in production

---

# PHASE A: FIRST ENTERPRISE SETUP (Day Zero)

## A.1: User Logs Into Blank CRR System
- User opens CRR application
- Dashboard shows empty state
- No assessments exist
- No production data

## A.2: User Sees "Create New Assessment" Option
- Only one option available: "Create Assessment"
- User clicks to start

## A.3: User Selects Scope for First Assessment
- Dropdown shows available scopes
- **Only "Enterprise (XX)" is enabled**
- All market options (IN, BE, AU, etc.) are **disabled/greyed out**
- System enforces: First assessment MUST be Enterprise

## A.4: Enterprise Sandbox is Created
- User selects "Enterprise (XX)"
- System creates: **Sandbox ID: 1, Version: 1, Scope: XX**
- Status: **WORKING** (Draft)
- Sandbox is empty - no rules, no assets, no FA configuration

## A.5: User Lands on Sandbox Dashboard
- Sees empty sandbox
- Configuration Selector shows options: Rules, Assets, Fundamental Assessment
- User can now start building configuration

---

# PHASE B: FIRST ASSET CREATION

## B.1: User Navigates to Asset Manager
- From Configuration Selector, user clicks "Assets"
- Empty asset list displayed
- "Add New Asset" button visible

## B.2: User Clicks "Add New Asset"
- Modal/form opens for asset creation
- All fields shown together in single form

## B.3: User Enters Asset Name
- User types: "High_Risk_Countries"
- System validates: Name must be unique across all assets

## B.4: User Enters Description (MANDATORY)
- User types: "List of countries classified as high risk for AML purposes"
- This field is **REQUIRED** - cannot skip

## B.5: User Selects Reference Data Table
- Dropdown shows available reference tables
- User selects: "Countries"
- This determines what values are VALID for this asset

## B.6: User Uploads Values File
- File upload field in same form
- User clicks "Upload File" / "Choose File"
- File picker opens
- Accepts: CSV, Excel formats
- User selects: "high_risk_countries.csv"

## B.7: System Validates File Format (Before Save)
- Check: Is it CSV/Excel?
- Check: Does it have correct columns?
- Check: Is file size within limits?

## B.8: System Validates Each Value Against Reference Table
- For each row in uploaded file:
  - Is "Iran" in Countries reference table? ✓
  - Is "North Korea" in Countries reference table? ✓
  - Is "Syria" in Countries reference table? ✓
  - (continues for all rows)

## B.9: Validation Result Shown
- All values are valid
- System shows: "X values validated successfully"
- User can now save the complete asset

## B.10: User Clicks Save (Atomic Creation)
- **SINGLE SAVE OPERATION** - creates asset with ALL information together:
  - Name: "High_Risk_Countries"
  - Description: "List of countries..." (mandatory)
  - Reference Table: "Countries"
  - Values: [Iran, North Korea, Syria, Yemen, ...]
- **Asset ID assigned** (e.g., A001)
- **Version: 1** (first version)
- **Status: DRAFT** (not linked to any rule yet)
  - Values: [Iran, North Korea, Syria, Yemen, ...]
- **Asset ID assigned** (e.g., A001)
- **Version: 1** (first version)
- **Status: DRAFT** (not linked to any rule yet)

## B.11: Asset Creation Complete
- Asset A001 Version 1 now exists with all values
- Status: **DRAFT**
- Ready to be used in rules

---

# PHASE C: CREATING ADDITIONAL ASSETS

## C.1: User Creates Second Asset
- Repeats B.1 to B.11 for "Low_Risk_Occupations"
- Reference Table: "Occupations"
- Values: [Teacher, Doctor, Engineer, ...]
- Status: DRAFT

## C.2: User Creates Third Asset
- "Sanctioned_Entities"
- Reference Table: "Entity_Names"
- Values: [Entity1, Entity2, ...]
- Status: DRAFT

## C.3: Multiple DRAFT Assets Exist
- Asset A001: High_Risk_Countries (DRAFT)
- Asset A002: Low_Risk_Occupations (DRAFT)
- Asset A003: Sanctioned_Entities (DRAFT)
- None linked to rules yet

---

# PHASE D: BUILDING RULE FRAMEWORK

## D.1: User Navigates to Rules
- From Configuration Selector, clicks "Rules"
- Empty rule framework displayed

## D.2: User Creates Risk Category
- Creates: "Geographic Risk"
- Creates: "Customer Risk"
- Creates: "Products & Services Risk"
- (follows CRR framework structure)

## D.3: User Creates Risk Element
- Inside "Geographic Risk", creates: "Country of Residence"
- Risk Element ID assigned

## D.4: User Creates Ruleset
- Inside "Country of Residence", creates: "Ruleset 1"
- Ruleset is empty - no rules yet

## D.5: User Opens Ruleset for Editing
- Sees empty ruleset
- "Add Rule" button visible

---

# PHASE E: LINKING ASSET TO RULE (Critical Stage)

## E.1: User Clicks "Add Rule"
- Rule creation form opens
- Form fields in specific order (see below)

## E.2: User Enters Rule Description
- First field: Rule Description (text)
- User types: "Flag customers from high-risk countries"
- Describes what this rule does

## E.3: User Selects Multiplier Type
- Dropdown with two options:
  - **Value** (static number)
  - **Fundamental Assessment** (dynamic from FA gate)
- User selects: "Fundamental Assessment"

## E.4: User Sets Up Multiplier
- **If "Value" was selected:** User enters a number (e.g., 3.0)
- **If "Fundamental Assessment" was selected:** User sees dropdown of 6 FA gates
  - Geography
  - Industry
  - Product
  - Structure
  - Occupation
  - Acquisition Channel
- User selects: "Geography"

## E.5: User Selects Datapoint
- Dropdown shows available datapoints from customer data schema
- User selects: "Nationality_of_Account_Holder"
- **Behind the scenes:** System looks up this datapoint's linked Reference Data Table
  - Nationality_of_Account_Holder → Reference Table: "Countries"

## E.6: User Selects Operator
- For asset-type values, operators are:
  - **INCLUDES** (customer value is in the asset list)
  - **EXCLUDES** (customer value is NOT in the asset list)
- User selects: "INCLUDES"

## E.7: User Selects Value (Asset)
- Because Datapoint's Reference Table is "Countries"...
- **System filters asset dropdown to show ONLY assets with Reference Table = "Countries"**
- User sees filtered list:
  - High_Risk_Countries (Reference: Countries) ✓
  - Low_Risk_Countries (Reference: Countries) ✓
  - ~~Sanctioned_Entities (Reference: Entities)~~ NOT SHOWN
  - ~~High_Risk_Occupations (Reference: Occupations)~~ NOT SHOWN

> **Key Point:** Asset dropdown is filtered based on datapoint's reference table.
> This ensures user cannot accidentally link an "Occupations" asset to a "Country" datapoint.

## E.8: User Selects the Asset
- User selects: "High_Risk_Countries"
- This links the rule to Asset A001

## E.9: User Saves the Rule
- Rule is saved with:
  - Description: "Flag customers from high-risk countries"
  - Multiplier Type: Fundamental Assessment → Geography
  - Datapoint: Nationality_of_Account_Holder
  - Operator: INCLUDES
  - Value: Asset A001 (High_Risk_Countries)
- **CRITICAL MOMENT:** Asset A001 status changes!

## E.10: Asset Status Transition: DRAFT → SANDBOX
- Asset A001 was: DRAFT
- Asset A001 is now: **SANDBOX**
- Reason: It is now linked to a rule in an active sandbox

## E.11: Asset-Rule Association Recorded
- System records: Rule R001 uses Asset A001 V1
- This association is tracked for impact analysis

---

## 📋 OPEN QUESTION: Which Assets Should User See in the Dropdown?

When user is selecting an asset to link to a rule, which assets should appear in the dropdown?

### Assets That Could Be Shown:

| Asset Type | Example | Should Show? | Pros | Cons |
|------------|---------|--------------|------|------|
| **Own sandbox's DRAFT assets** | Assets I created in my current sandbox | ✅ YES | My assets, I should use them | None |
| **Own sandbox's SANDBOX assets** | Assets already linked to other rules | ✅ YES | Already using in this sandbox | None |
| **Enterprise PRODUCTION assets** | Assets currently live in Enterprise | ✅ YES | Standard assets everyone uses | May need copy if editing |
| **Other market's PRODUCTION assets** | India's asset that's in production | ⚠️ MAYBE | Promote reuse | Could cause confusion about ownership |
| **Other market's SANDBOX assets** | India's work-in-progress asset | ❌ NO | - | Unstable, may change or be deleted |
| **ARCHIVED assets** | Old versions | ❌ NO | - | Not current, should use latest |

### Recommended Rule:
> **Show: DRAFT (own) + SANDBOX (own) + PRODUCTION (any scope)**
> 
> **Hide: Other scope's SANDBOX + ARCHIVED**

This balances reuse with stability - user can use any finalized (PRODUCTION) asset but not work-in-progress from other sandboxes.

---

# PHASE F: USING ASSET IN MULTIPLE RULES

## F.1: User Creates Another Rule Using Same Asset
- Creates Rule R002 in different Ruleset
- Also uses "High_Risk_Countries" asset
- Asset A001 now linked to: R001, R002

## F.2: User Creates Rule Using Different Asset
- Creates Rule R003
- Uses "Low_Risk_Occupations" asset
- Asset A002 status: DRAFT → **SANDBOX**

## F.3: User Creates Complex Rule with Multiple Assets
- Creates Rule R004 with conditions:
  - Customer_Jurisdiction IN High_Risk_Countries (A001)
  - AND Customer_Occupation NOT IN Low_Risk_Occupations (A002)
- Single rule references multiple assets

## F.4: Asset Usage Summary at This Point
- A001: SANDBOX, used in R001, R002, R004
- A002: SANDBOX, used in R003, R004
- A003: DRAFT (still not used in any rule)

---

# PHASE G: CONFIGURING MARKET LEVEL SETTINGS

## G.1: User Navigates to Ruleset Listing Page
- Sees list of rulesets created

## G.2: User Clicks "Market Settings" Button
- Modal opens for market-level configuration

## G.3: User Configures Applicability
- Options: Entities, Individuals, Intermediaries
- User selects: "Individuals"
- This applies to ALL rulesets in this Risk Element

## G.4: User Configures Default Multiplier
- Input: Numerical value
- User enters: 1.0
- This is fallback when no ruleset returns TRUE

## G.5: User Configures Weighting
- Input: Numerical value
- User enters: 2.0
- This is used in risk calculation formula

## G.6: User Saves Market Settings
- Settings applied to all rulesets in Risk Element
- Cannot be customized per-ruleset

---

# PHASE H: CONFIGURING FUNDAMENTAL ASSESSMENT

## H.1: User Navigates to Fundamental Assessment
- From Configuration Selector, clicks "Fundamental Assessment"
- Sees 6 FA gates listed

## H.2: User Expands Geography Gate
- Sees list of countries/attributes
- Each has current scores

## H.3: User Selects an Attribute (e.g., Venezuela)
- Opens Questionnaire screen
- Sees 10 questions with Yes/No answers

## H.4: User Answers Questions
- Q1: Is this OFAC prohibited? → Yes
- Q2: Is this FATF high-risk? → Yes
- (provides justification for each answer)

## H.5: User Clicks Calculate
- System calculates FA score based on highest YES question
- New Score: 10 (based on Q1 being YES)

## H.6: Current Score vs New Score
- Current Score: (from production/legacy - if any)
- New Score: 10 (what user just configured)
- Simulation will use New Score

## H.7: User Configures Market Override (Optional)
- Clicks "Update Override"
- Selects market: India
- Sets override score: 8
- This overrides Enterprise score for India specifically

---

# PHASE I: SANDBOX SUBMISSION FOR SIMULATION

## I.1: User Completes All Configuration
- Rules: Configured with assets
- Assets: Values uploaded, linked to rules
- FA: Questions answered
- Market Settings: Defaults configured

## I.2: User Clicks "Submit for Simulation"
- Confirmation modal appears
- Shows summary: X rules, Y assets, Z FA changes

## I.3: User Adds Submission Comment
- User types: "Initial Enterprise configuration for AML risk scoring"

## I.4: User Confirms Submission
- Clicks "Submit"

## I.5: System Captures Snapshot
- CRITICAL: System freezes current state
- Records exactly which asset VERSIONS are being used
- Configuration becomes immutable for this simulation

## I.6: Sandbox Status Changes
- Status: WORKING → **IN_PROGRESS (Simulation Running)**
- User cannot edit sandbox during simulation

## I.7: Asset States During Simulation
- Assets remain: SANDBOX status
- Values are frozen (snapshot taken)
- User cannot edit asset values during simulation

---

# PHASE J: SIMULATION EXECUTION

## J.1: Simulation Job Starts
- System reads snapshot configuration
- Identifies all rules and referenced assets

## J.2: Simulation Accesses Customer Data
- Runs against FULL customer population (not sample)
- Each customer evaluated against rules

## J.3: Simulation Uses Snapshot Versions
- Even if asset was edited after submit, simulation uses SUBMIT-time version
- Snapshot ensures consistency

## J.4: Simulation Calculates Risk Scores
- For each customer:
  - Evaluate rule conditions
  - Look up FA multipliers
  - Calculate risk score

## J.5: Simulation Generates Results
- Comparison: Before vs After
- Shows: How many customers moved to High Risk, Medium Risk, etc.

## J.6: Simulation Completes
- Status: IN_PROGRESS → **TESTING_COMPLETED**
- Results available for review

---

# PHASE K: REVIEW AND APPROVAL

## K.1: User Reviews Simulation Results
- Opens results dashboard
- Sees impact analysis:
  - "10,000 customers moved to High Risk"
  - "5,000 customers moved to Medium Risk"

## K.2: User Decides to Proceed
- Results look acceptable
- Clicks "Implement"

## K.3: Sandbox Status Changes
- Status: TESTING_COMPLETED → **PENDING_APPROVAL_1**
- Waiting for first approver

## K.4: First Approver Reviews
- Different user (maker-checker)
- Reviews configuration and results
- Clicks "Approve"

## K.5: Sandbox Status Changes
- Status: PENDING_APPROVAL_1 → **PENDING_APPROVAL_2**
- Waiting for second approver

## K.6: Second Approver Reviews
- Another different user
- Final review
- Clicks "Approve and Implement"

---

# PHASE L: PROMOTION TO PRODUCTION (Major Milestone)

## L.1: Promotion Transaction Starts
- System begins atomic promotion
- All-or-nothing: Rules + Assets + FA together

## L.2: Rules Moved to Production
- All sandbox rules become production rules
- Enterprise production now has active rules

## L.3: Assets Status Transition: SANDBOX → PRODUCTION
- A001: SANDBOX → **PRODUCTION**
- A002: SANDBOX → **PRODUCTION**
- A003: Remains DRAFT (was never linked to any rule)

## L.4: FA Configuration Activated
- New Scores become Current Scores
- FA multipliers now active for scoring

## L.5: Sandbox Status Final
- Status: PENDING_APPROVAL_2 → **IMPLEMENTED**
- Sandbox becomes historical record

## L.6: Enterprise Production is ACTIVE
- System now actively scoring customers
- Using promoted rules, assets, FA configuration

## L.7: System State After Promotion
```
PRODUCTION:
├── Enterprise: ACTIVE
│   ├── Rules: R001, R002, R003, R004
│   ├── Assets: A001 (PRODUCTION), A002 (PRODUCTION)
│   └── FA: Configured
│
SANDBOX:
└── (none - Enterprise sandbox was promoted)

DRAFT ASSETS:
└── A003 (never used, still DRAFT)
```

---

# PHASE M: POST-PROMOTION - NEW SAND SANDBOX OPTIONS

## M.1: User Returns to Dashboard
- Sees Enterprise is in Production
- "Create New Assessment" button available

## M.2: User Clicks "Create New Assessment"
- Scope dropdown opens
- NOW different options available:
  - Enterprise (XX): ✓ Enabled
  - India (IN): ✓ Enabled
  - Belgium (BE): ✓ Enabled
  - (all markets enabled)

## M.3: Why Are Markets Now Enabled?
- Because Enterprise production exists
- Markets can now be "layered" on top of Enterprise
- Markets inherit Enterprise as baseline

---

# PHASE N: CREATING FIRST MARKET SANDBOX

## N.1: User Selects India (IN)
- User wants to create India-specific configuration
- Selects "India (IN)" from scope dropdown

## N.2: India Sandbox Created
- Sandbox ID: 2, Version: 1, Scope: IN
- Status: WORKING

## N.3: India Inherits Enterprise Baseline
- System copies Enterprise production rules as starting point
- India sees all Enterprise rules
- India can add/modify/remove locally

## N.4: Mutual Exclusion Check
- Now that India sandbox exists:
  - Can user create Enterprise sandbox? **NO** (blocked)
  - Can user create Belgium sandbox? **YES** (markets don't block each other)

---

# PHASE O: MARKET USING ENTERPRISE ASSETS

## O.1: India Views Available Assets
- India opens Asset Manager
- Sees assets from Enterprise PRODUCTION:
  - A001: High_Risk_Countries (PRODUCTION)
  - A002: Low_Risk_Occupations (PRODUCTION)

## O.2: India Creates a New Rule
- Creates India-specific rule
- Wants to use "High_Risk_Countries"

## O.3: India Selects Enterprise Asset in Rule
- Selects "High_Risk_Countries" from dropdown
- Rule references: Asset A001

## O.4: Asset Reference Recorded
- System records: India rule uses Enterprise asset A001
- A001 status: Still PRODUCTION (India is just referencing it)

## O.5: India Saves Rule
- Rule saved successfully
- Asset A001 is now used by:
  - Enterprise production rules
  - India sandbox rules

---

# PHASE P: MARKET WANTS TO EDIT ENTERPRISE ASSET

## P.1: India Wants to Add "Pakistan" to High_Risk_Countries
- User opens A001 for editing
- Wants to add a new value

## P.2: System Blocks Direct Edit
- Modal appears: "This asset is owned by Enterprise"
- Explanation: "Direct edit would affect Enterprise production"

## P.3: System Offers Copy Option
- Button: "Create Copy for India"
- This will create independent India version

## P.4: User Clicks "Create Copy for India"
- System creates new asset:
  - Asset ID: A004
  - Name: High_Risk_Countries_IN
  - Version: 1
  - Status: DRAFT
  - Values: [copied from A001]

## P.5: User Edits the Copy
- User adds "Pakistan" to A004
- Saves changes

## P.6: User Updates Rule to Use Copy
- India rule now references A004 (India copy)
- Not A001 (Enterprise original)

## P.7: Current Asset State
- A001 (Enterprise original): PRODUCTION, used by Enterprise
- A004 (India copy): SANDBOX, used by India

---

# PHASE Q: MULTIPLE MARKET SANDBOXES

## Q.1: User Creates Belgium Sandbox
- Sandbox ID: 3, Version: 1, Scope: BE
- Status: WORKING
- Allowed because: India sandbox (market) doesn't block Belgium sandbox (market)

## Q.2: Belgium Views Available Assets
- Sees A001 (Enterprise PRODUCTION)
- Does NOT see A004 (India's SANDBOX copy) - or does it see but can't edit?

## Q.3: Belgium Uses Enterprise Asset
- Creates rule using A001 (High_Risk_Countries)
- References the Enterprise PRODUCTION asset directly

## Q.4: Belgium Wants to Edit A001
- Same situation as India
- System blocks and offers copy
- Belgium creates A005: High_Risk_Countries_BE

## Q.5: Current Asset Landscape
- A001: Enterprise original (PRODUCTION)
- A004: India copy (SANDBOX)
- A005: Belgium copy (SANDBOX)

---

# PHASE R: MARKET PROMOTION

## R.1: India Submits Sandbox for Simulation
- India configuration complete
- Clicks "Submit for Simulation"

## R.2: India Simulation Runs
- Uses snapshot of India sandbox
- Includes India's copy A004

## R.3: India Approvals Complete
- First and second approver approve

## R.4: India Promotes to Production
- India rules: Active in India production
- A004: SANDBOX → **PRODUCTION**
- India sandbox: IMPLEMENTED

## R.5: Current Production State
```
PRODUCTION:
├── Enterprise: ACTIVE
│   ├── Rules: R001-R004
│   └── Assets: A001, A002 (PRODUCTION)
│
├── India: ACTIVE
│   ├── Rules: Enterprise inherited + India specific
│   └── Assets: A004 (India copy, PRODUCTION)
│
SANDBOX:
├── Belgium (IN_PROGRESS)
│   └── Using A001 (Enterprise) and A005 (Belgium copy)
```

---

# PHASE S: ENTERPRISE UPDATES ASSET (After Markets Exist)

## S.1: All Market Sandboxes Must Be Cleared
- For Enterprise to make changes, no market sandboxes can exist
- Belgium sandbox must be promoted or cancelled first

## S.2: Belgium Promotes or Cancels
- Belgium completes their work
- All sandboxes cleared

## S.3: Enterprise Creates New Sandbox
- Now allowed (no market sandboxes exist)
- Sandbox ID: 4, Version: 1, Scope: XX

## S.4: Enterprise Edits A001 (High_Risk_Countries)
- Adds "Cuba" to the list
- Creates A001 V2

## S.5: Enterprise Promotes
- A001 V2 becomes PRODUCTION
- A001 V1 becomes ARCHIVED

## S.6: Automatic Version Switch
- ALL scopes using A001 now use V2
- Enterprise: Uses A001 V2
- Belgium (if they were using A001): Uses A001 V2
- India: Still uses A004 (their copy - unaffected)

---

# PHASE T: ASSET VERSIONING IN PRODUCTION

## T.1: Only One PRODUCTION Version Exists
- A001 V1: ARCHIVED
- A001 V2: PRODUCTION
- Cannot have both in PRODUCTION

## T.2: Rules Auto-Switch to Latest Version
- No manual update needed
- Rules reference Asset ID, system resolves to PRODUCTION version

## T.3: Historical Snapshots Preserved
- Old simulation results still show V1 values
- Audit trail maintained

---

# PHASE U: MATURE SYSTEM STATE

## U.1: Multiple Markets in Production
- Enterprise: Active
- India: Active
- Belgium: Active
- Germany: Active

## U.2: Complex Asset Landscape - Four Types of Assets

> **Important Context:** There is ONE compliance team (CRR Business Users / Compliance Analysts) that manages configuration for ALL markets. The same person who configures India also configures Australia. There are no separate "owners" and "users" - all are just users of assets.

In a mature system, there are **4 types of assets**:

| Type | Description | Example | Scope |
|------|-------------|---------|-------|
| **1. Enterprise Originals** | Created at Enterprise scope, used by all markets | High_Risk_Countries (A001) | Enterprise |
| **2. Market-Specific Copies** | Copied from Enterprise by a market for customization | High_Risk_Countries_IN (A004) - copied from A001 | India only |
| **3. Market-Independent Assets** | Created entirely at market level, specific to their needs | India_Local_Watchlist (A010) | India only |
| **4. Cross-Market Shared Assets** | Created at one market level but used by multiple markets | APAC_Regional_Risk_List (A015) - used by India AND Australia | Multiple markets |

### Type 4: Cross-Market Sharing - Important Behavior

**Scenario:**
- Asset "APAC_Regional_Risk_List" is in PRODUCTION
- India uses this asset in their rules
- Australia also uses this same asset in their rules
- Both markets are just "users" of this asset

**Key Rule: How to Update a Cross-Market Asset?**

Since this asset is used by MULTIPLE markets:
- Changing it affects India AND Australia
- We need to calculate impact on BOTH markets
- **Therefore: Updates MUST go through Enterprise sandbox**

**Why Enterprise sandbox?**
- Enterprise sandbox runs simulation against ALL markets
- Can calculate impact of asset change across India + Australia together
- Ensures no market is surprised by a change they didn't know about
- Version updates for ALL markets simultaneously

**Update Flow for Type 4 Assets:**
```
1. Asset A015 is in PRODUCTION (used by India, Australia)
2. Compliance team wants to add new value to A015
3. They create ENTERPRISE sandbox (not India or Australia sandbox)
4. Edit A015 in Enterprise sandbox → Creates A015 V2
5. Run Enterprise simulation → Shows impact on India AND Australia
6. Promote Enterprise sandbox → A015 V2 becomes PRODUCTION
7. Both India and Australia now use A015 V2 automatically
```

**Type 4 behaves EXACTLY like Type 1 (Enterprise Originals):**
- Cannot be edited in market-level sandboxes
- Must be updated via Enterprise sandbox
- Changes apply to all markets that use it

## U.3: Ongoing Operations
- New sandboxes created as needed
- Assets versioned over time
- Mutual exclusion enforced for Enterprise changes
- Cross-market assets treated like Enterprise assets for update purposes

---

## 📋 OPEN QUESTION: Which Assets Should Be Editable in Asset List?

When user opens Asset Manager and sees list of assets, which should have "Edit" button enabled?

### Editability Decision Matrix:

| Asset Status | Asset Owner | Your Current Sandbox Scope | Edit Enabled? | Reason |
|--------------|-------------|---------------------------|---------------|--------|
| **DRAFT** | You (same sandbox) | Same | ✅ YES | You created it, you can edit |
| **DRAFT** | Someone else (same sandbox) | Same | ✅ YES | Same team, same sandbox |
| **DRAFT** | Different sandbox | Any | ⚠️ DEPENDS | If you link it first, you can edit; otherwise read-only |
| **SANDBOX** | Your sandbox | Your sandbox | ✅ YES | Actively working on it |
| **SANDBOX** | Other market's sandbox | Your sandbox | ❌ NO | Their work-in-progress |
| **PRODUCTION** | Enterprise | Enterprise sandbox | ✅ YES | Create new version |
| **PRODUCTION** | Enterprise | Market sandbox | ❌ NO (Copy offered) | Would affect Enterprise, must copy |
| **PRODUCTION** | My market | My market sandbox | ✅ YES | Create new version |
| **PRODUCTION** | Other market | My market sandbox | ❌ NO (Copy offered) | Would affect them, must copy |
| **ARCHIVED** | Any | Any | ❌ NO | Historical record only |

### Visual Summary:

```
CAN EDIT (Edit button enabled):
├── DRAFT in MY sandbox
├── SANDBOX in MY sandbox  
└── MY OWN PRODUCTION assets (when I have sandbox)

CANNOT EDIT DIRECTLY (Copy button shown instead):
├── Enterprise PRODUCTION (when in Market sandbox)
└── Other Market's PRODUCTION

COMPLETELY READ-ONLY (No edit, no copy):
├── Other sandbox's SANDBOX assets
└── ARCHIVED assets
```

### Key Principle:
> **Edit = You're the owner or you're in the owning scope's sandbox**
> 
> **Copy = You want to customize someone else's PRODUCTION asset**
> 
> **Read-only = Work-in-progress by others OR archived

---

# SUMMARY: ALL STAGES IN ORDER

| # | Phase | Key Actions |
|---|-------|-------------|
| A | First Enterprise Setup | Login, create first sandbox (Enterprise only) |
| B | First Asset Creation | Create asset, upload values, DRAFT status |
| C | Additional Assets | Create multiple assets, all DRAFT |
| D | Rule Framework | Create categories, elements, rulesets |
| E | Link Asset to Rule | DRAFT → SANDBOX transition |
| F | Multiple Rule Links | Asset used in multiple rules |
| G | Market Level Settings | Applicability, default multiplier, weighting |
| H | Fundamental Assessment | Questions, scores, overrides |
| I | Submit for Simulation | Snapshot captured, cannot edit |
| J | Simulation Execution | Run against full population |
| K | Review and Approval | Two-level approval |
| L | Promote to Production | SANDBOX → PRODUCTION, assets active |
| M | New Sandbox Options | Markets now available |
| N | First Market Sandbox | India created, inherits Enterprise |
| O | Market Uses Enterprise Asset | Reference without copy |
| P | Market Edits Enterprise Asset | Copy-on-write triggered |
| Q | Multiple Markets | Belgium, Germany sandboxes |
| R | Market Promotion | India goes to production |
| S | Enterprise Updates | Mutual exclusion, version bump |
| T | Asset Versioning | Single active version rule |
| U | Mature State | Complex multi-market operations |

---

**Total: 21 Phases, 100+ Granular Steps**

Each phase can now be expanded with edge cases in separate documents.
