# CRR Complete Journey: From Zero to Production
## A Non-Technical Guide for Product Managers

---

## Document Purpose

This document explains the **complete lifecycle** of CRR (Customer Risk Rating) from a completely blank system to a mature state with:
- Enterprise production running
- Multiple market sandboxes active
- Assets being created, versioned, and reused

**Written for:** Non-technical Product Managers who need to understand every step, edge case, and decision point.

**Tone:** Over-explaining. Every concept will be broken down thoroughly.

---

# PART 1: UNDERSTANDING THE STARTING POINT

## 1.1 What Does "Blank State" Mean?

Imagine you just installed the CRR system for the first time at American Express. What do you see?

**Answer: Nothing.** 

- No rules configured
- No assets created
- No production assessment running
- No sandboxes exist

This is your "Day Zero" state. Everything needs to be built from scratch.

---

## 1.2 The First Constraint: Enterprise Must Come First

Here's an important rule baked into the system:

> **The FIRST sandbox you create MUST be "Enterprise" scope.**

**Why?**

Think of it like building a house:
- Enterprise = Foundation of the house
- Markets (India, Belgium, etc.) = Rooms built ON TOP of the foundation

You cannot build rooms before you have a foundation. Similarly:
- You cannot create a "India" sandbox if there's no Enterprise production yet
- Enterprise rules become the "default" that all markets inherit

---

## 1.3 What is an "Assessment" vs "Sandbox"?

Before we proceed, let's clarify these terms:

| Term | What It Means |
|------|---------------|
| **Assessment** | A complete risk scoring configuration (rules + assets + fundamental assessment) |
| **Sandbox** | A "draft" or "testing" version of an assessment. Changes happen here before going "live" |
| **Production** | The "live" version that actively scores real customers |

**Analogy:**
- Sandbox = Your draft document in Google Docs
- Production = The published document that clients can see

---

# PART 2: THE HAPPY PATH - BUILDING FROM ZERO

Let me walk you through the complete happy path (everything goes smoothly, no errors).

---

## Step 1: Create Enterprise Sandbox

**Where are we?** Blank system, nothing exists.

**What happens?**
1. CRR Business User clicks "Create New Sandbox"
2. System shows dropdown: "Select Scope"
3. **Only "Enterprise (XX)" is available** (markets are disabled because no production exists yet)
4. User selects "Enterprise"
5. System creates: **Sandbox Enterprise Version 1**

**What exists now?**
```
┌─────────────────────────────┐
│  Sandbox: Enterprise V1     │
│  Status: WORKING (Draft)    │
│  Contents: Empty            │
└─────────────────────────────┘

Production: NOTHING (does not exist yet)
```

---

## Step 2: Build the Risk Framework Structure

Now the user needs to build the actual risk structure. Remember the hierarchy:

```
Risk Framework (Enterprise)
└── Risk Categories (5 total)
    └── Risk Elements
        └── Rulesets
            └── Rules
```

**What the user does:**
1. Creates Risk Category: "Customer Risk"
2. Creates Risk Category: "Geographic Risk"
3. Creates Risk Category: "Transaction Risk"
4. Creates Risk Category: "Products & Services Risk"
5. Creates Risk Category: "ARFs & HROs"

Then, inside each category, creates Risk Elements. For example:
- Customer Risk → "Income Level"
- Customer Risk → "Occupation Type"
- Geographic Risk → "Country of Residence"

---

## Step 3: Now We Need Assets! (This is Important)

Here's where it gets interesting.

The user wants to create a rule like:
> "If customer's country is in HIGH_RISK_COUNTRIES list, then score = High"

**Problem:** There's no "HIGH_RISK_COUNTRIES" list yet!

**Solution:** User must first CREATE an Asset.

---

## Step 3a: Creating the First Asset

**Where does user go?**
In the Sandbox, user clicks on the "Configuration Selector" dropdown and switches from "Rules" to "Assets".

**What user does:**
1. Clicks "Add New Asset" button
2. A modal (popup form) appears:
   - **Asset Name:** "High_Risk_Countries"
   - **Reference Data Table:** "Countries" (dropdown selection)
   - **Description:** "List of countries classified as high risk for AML"
3. User uploads CSV or manually adds values:
   - Iran
   - North Korea
   - Syria
   - (etc.)
4. Clicks "Save"

**What happens in the system?**

```
Asset Created:
├── Asset ID: A001
├── Version: 1 (first version ever)
├── Status: DRAFT
├── Values: [Iran, North Korea, Syria, ...]
├── Reference Table: Countries
└── Used By: NOTHING (not linked to any rule yet)
```

**Important:** The status is "DRAFT" because no rule is using it yet.

---

## Step 3b: What is an Asset, Really? (Technical Explanation for Non-Technical People)

Let me over-explain this because it's crucial.

### First, Understand Reference Data Table (Master List)

Before we talk about Assets, you need to understand Reference Data Tables.

**Reference Data Table = Master List of ALL Valid Values**

Think of American Express having a master list of all 200+ countries where they operate. This is the "Countries" reference data table. It contains EVERY valid country that can ever be used in CRR rules.

**Purpose of Reference Data Table:**
- It's NOT for storing risk data
- It's ONLY for **VALIDATION** - to ensure users cannot create invalid values
- Think of it like a dropdown menu source - you can only pick values that exist in this list

```
Reference Data Table: "Countries" (Master List)
├── India
├── USA
├── Germany
├── Belgium
├── Iran
├── North Korea
├── Syria
├── ... (200+ countries)
└── Every country where Amex operates
```

---

### Now, What is an Asset?

**An Asset is a CENTRALIZED LIST created inside the CRR platform.**

It is:
- **NOT a file** (it's not an Excel file or CSV that you upload and store)
- **NOT pointing to rows** in the reference table
- It IS a **named list** that contains a SUBSET of values from a reference table

**Key Concept:** The Asset STORES its own values, but those values are VALIDATED against the Reference Data Table to ensure they're legitimate.

**Example:**

```
Asset: "High_Risk_Countries"
├── Asset ID: A001
├── Version: 1
├── Reference Table Used: "Countries" (for validation only)
├── Values STORED IN THIS ASSET:
│   ├── Iran
│   ├── North Korea
│   ├── Syria
│   └── Afghanistan
└── This list is stored centrally in the CRR database
```

**How Values Are Added (Important!):**

Users do NOT type values one by one. Instead:
1. User prepares a CSV or Excel file with list of values
2. User uploads this file through the Asset Manager
3. System reads the file, extracts values
4. System VALIDATES each value against the Reference Data Table
5. If all values are valid → File is accepted, values are stored in the Asset
6. If any value is invalid → File is REJECTED with error message

```
Example:

User uploads: high_risk_countries.csv
├── Row 1: Iran        → ✅ Valid (exists in Countries reference table)
├── Row 2: North Korea → ✅ Valid
├── Row 3: Narnia      → ❌ INVALID (does not exist in reference table)
└── RESULT: Upload REJECTED - "Narnia is not a valid country"
```

**After successful upload:**
- The file itself is NOT stored
- Only the VALUES from the file are stored in the Asset's centralized list
- The Asset becomes the single source of truth for those values

---

### How Does a Rule Use an Asset?

When a rule says:
> "Customer_Jurisdiction IN High_Risk_Countries"

The system:
1. Looks up Asset "High_Risk_Countries" (Asset ID: A001)
2. Fetches the VALUES stored in this asset: [Iran, North Korea, Syria, Afghanistan]
3. Checks if customer's jurisdiction matches any of those values

The rule is essentially saying: "Go to the centralized location where Asset A001's values are stored, fetch the list, and check if customer's country is in that list."

---

### Why Version Matters

If you later add "Pakistan" to the list, we don't want to mess up old records. So:
- Version 1 = [Iran, North Korea, Syria, Afghanistan]
- Version 2 = [Iran, North Korea, Syria, Afghanistan, Pakistan]

Old simulation results used V1, new ones use V2. This is **traceability**.

---

## Step 4: Create a Rule That Uses the Asset

Now user goes back to "Rules" in the Configuration Selector.

### 4a: Basic Rule Creation

**What user does:**
1. Navigate to: Geographic Risk → Country of Residence → Ruleset 1
2. Click "Add Rule"
3. Configure the rule condition:
   - **Datapoint:** "Customer_Jurisdiction" (a field from customer data)
   - **Operator:** "IN" (meaning "is one of")
   - **Value:** Select Asset → "High_Risk_Countries"

### 4b: Selecting Multiplier Type (Important!)

After setting up the rule condition, user must configure the **Multiplier**. The ruleset screen has a dropdown for **Multiplier Type**:

| Multiplier Type | What It Does |
|-----------------|--------------|
| **Value** | User enters a static numerical value (e.g., 2.0, 5.0) |
| **Fundamental Assessment** | Multiplier is dynamically fetched from FA table |

**If user selects "Value":**
```
Multiplier Type: Value
Multiplier: 3.0 (static number entered by user)

Calculation: Rule Logic × Weighting × 3.0
```

**If user selects "Fundamental Assessment":**
```
Multiplier Type: Fundamental Assessment
├── Dropdown shows: 6 FA Gates
│   ├── Geography
│   ├── Industry
│   ├── Product
│   ├── Structure
│   ├── Occupation
│   └── Acquisition Channel
│
└── User selects: "Geography"
```

**What this means:** 
> "When this rule evaluates, look at the customer's country (from their data), go to the Geography FA table, find that country's FA score, and use that as the multiplier."

**Example with FA Multiplier:**
```
Customer: Juan from Venezuela
Rule: Customer_Jurisdiction IN High_Risk_Countries → TRUE
Multiplier Type: Fundamental Assessment → Geography
System looks up: Venezuela in Geography FA table → Score 10

Calculation: TRUE × Weighting × 10 = Risk contribution
```

### 4c: Rule Logic with AND/OR

Rules can have **multiple conditions** combined using logical operators:

| Operator | Meaning |
|----------|---------|
| **AND** | Both conditions must be true |
| **OR** | Either condition can be true |
| **( )** | Parentheses for complex logic grouping |

**Simple AND Example:**
```
Condition 1: Customer_Jurisdiction IN High_Risk_Countries
    AND
Condition 2: Customer_Product IN High_Value_Products
```
*(Both must be true for rule to fire)*

**Complex Logic with Parentheses:**
```
(Condition 1 OR Condition 2) AND Condition 3
```

**Note:** Most of the time, business users only use AND conditions. OR and parentheses are used for more complex scenarios.

### 4d: Market Level Settings (Ruleset Listing Page)

On the **Ruleset Listing Page**, there is a **[Market Settings]** button. When clicked, it opens a modal to configure settings that apply to **ALL rulesets** in that Risk Element.

**Market Level Settings Modal:**

| Setting | Description |
|---------|-------------|
| **Applicability** | Which customer type this ruleset applies to |
| **Default Multiplier** | Fallback multiplier when NO ruleset returns true |
| **Weighting** | The weight used in risk calculation |

**Applicability Options:**

| Value | Meaning |
|-------|---------|
| **Entities** | Legal entities / Corporate accounts |
| **Individuals** | Individual customers / Personal accounts |
| **Intermediaries** | Payment merchants (check industry definition for exact scope) |

**Default Multiplier - The Fallback Mechanism:**

```
Normal Scenario (at least one ruleset returns TRUE):
└── Calculation: Multiplier × Weighting

Fallback Scenario (NO ruleset returns TRUE):
└── Calculation: DEFAULT MULTIPLIER × Weighting
```

*Why do we need this?* Even if no specific rule triggers, we still need to maintain some minimum risk score. The Default Multiplier ensures there's always a baseline.

**Important Constraints:**
- Market Settings are applied to **ALL rulesets** in the Risk Element at once
- You **CANNOT** set different Applicability per ruleset
- You **CANNOT** set different Default Multiplier per ruleset
- You **CANNOT** set different Weighting per ruleset
- These are shared/common settings across all rulesets in that Risk Element

4. Save the rule

**What happens in the system?**

```
Rule Created:
├── Rule ID: R001
├── Logic: Customer_Jurisdiction IN A001 (Asset ID for High_Risk_Countries)
├── Multiplier Type: Fundamental Assessment → Geography
├── Weighting: (from Market Settings)
└── Logical Operator: AND (if multiple conditions)

Asset A001 Status Change:
├── OLD Status: DRAFT
└── NEW Status: SANDBOX (because now it's being used in a sandbox)
```

**This is critical:** The moment you link an asset to a rule, its status changes from DRAFT to SANDBOX.

---

## Step 5: Create More Assets and Rules

User repeats this process many times:

| Asset Created | Used In Rulesets |
|---------------|-----------------|
| High_Risk_Countries (A001 V1) | RS001, RS005 |
| Low_Risk_Occupations (A002 V1) | RS002 |
| Sanctioned_Entities (A003 V1) | RS003, RS007, RS012 |
| High_Value_Products (A004 V1) | RS004 |

### Important: Rulesets Can Contain Multiple Conditions

A Ruleset is NOT just one simple rule. It can contain **multiple conditions** combined using logical operators (AND, OR).

**Example of a Single Ruleset with Multiple Conditions:**

```
Ruleset: RS001 (High Risk Geographic Profile)
│
├── Condition 1: Customer_Jurisdiction IN High_Risk_Countries (A001)
│       AND
├── Condition 2: Customer_Occupation NOT IN Low_Risk_Occupations (A002)
│       AND
├── Condition 3: Customer_Name IN Sanctioned_Entities (A003)
│
└── If ALL conditions are TRUE → Customer is flagged High Risk
```

**In this single ruleset (RS001), we are using THREE different assets:**
- A001 (High_Risk_Countries)
- A002 (Low_Risk_Occupations)
- A003 (Sanctioned_Entities)

**The logical structure looks like:**
```
(Datapoint1 Operator1 Asset1) AND (Datapoint2 Operator2 Asset2) AND (Datapoint3 Operator3 Asset3)
```

### Summary of Asset Usage Patterns

| Pattern | Example |
|---------|---------|
| Same asset in MULTIPLE rulesets | A003 used in RS003, RS007, RS012 |
| MULTIPLE assets in SAME ruleset | RS001 uses A001, A002, A003 together |
| Same asset in MULTIPLE rules within one ruleset | A001 used in 2 different conditions in RS001 |

**Key Point:** This is why asset changes have such wide impact - one asset update can affect multiple rulesets across the entire framework!

### Current State After Step 5

- All assets are Version 1 (first time being created)
- All assets are now status "SANDBOX" (linked to rules)
- Some assets are reused heavily across multiple rulesets

---

## Step 5b: Understanding Fundamental Assessment (FA) - The Multiplier System

Before we submit for simulation, you need to understand Fundamental Assessment. This is a critical part of how CRR calculates risk scores.

### What is Fundamental Assessment?

Fundamental Assessment (FA) is a **structured process to calculate the inherent risk of certain customer attributes**. Unlike rules which check data against conditions, FA provides **multipliers** that amplify or reduce the risk score based on attribute characteristics.

**The Key Formula:**
```
Risk Score = (Rule Logic Result) × Weight × MULTIPLIER
                                          ↑
                                    This comes from FA!
```

### The 6 Fundamental Assessment Gates

FA is organized into **6 gates**. Think of these as 6 categories of inherent risk:

| Gate # | Gate Name | Example Attributes |
|--------|-----------|-------------------|
| 1 | **Geography** | Countries: Lesotho, Venezuela, Spain, Germany, etc. |
| 2 | **Industry** | Casinos, Hotels, Restaurants, Money Services, etc. |
| 3 | **Product** | Corp CPC, Corp CTL, Consumer Cards, etc. |
| 4 | **Structure** | Business types, Legal structures |
| 5 | **Occupation** | High-risk occupations, Politically Exposed Persons |
| 6 | **Acquisition Channel** | How customer was acquired (direct, broker, etc.) |

> **⚠️ IMPORTANT CLARIFICATION:**
> 
> The **Geography gate** in Fundamental Assessment refers to the **country of the ACCOUNT HOLDER** (the customer's nationality/residence). 
> 
> This is **DIFFERENT** from the **Geography Risk Category** inside the CRR Rules Framework, which evaluates geographic risk factors in rules.
> 
> This is a common source of confusion, so keep this distinction in mind.

### Inside Each Gate: Attributes and Questions

**Structure:**
```
FA Gate (e.g., Geography)
└── Attribute (e.g., "Venezuela")
    └── 10 Questions (ranked by priority)
        ├── Q1 (Rank 10): Is this an OFAC prohibited country?
        ├── Q2 (Rank 9): Is this a FATF high-risk jurisdiction?
        ├── Q3 (Rank 8): Is this on the Thomson Reuters high-risk list?
        ├── Q4 (Rank 7): Does this country have weak AML laws?
        ├── ... 
        └── Q10 (Rank 1): Is there any minor concern?
```

### How FA Scoring Works (This is Important!)

**The Question-Answer Process:**

1. Business users configure each attribute by answering 10 questions with **YES or NO**
2. These answers are based on **third-party data** (e.g., Thomson Reuters surveys, FATF reports)
3. Each question has a **rank** (and corresponding score):
   - Question 1 (highest priority) = Score 10
   - Question 2 = Score 9
   - Question 3 = Score 8
   - ...and so on down to Score 1

**Calculating the FA Score:**

The **FA Score = Score of the HIGHEST RANKED question that was answered YES**

```
Example: Configuring FA for "Venezuela" (Geography Gate)

Q1 (Rank 10): Is this OFAC prohibited? → YES ✓
Q2 (Rank 9): Is this FATF high-risk? → YES ✓
Q3 (Rank 8): Thomson Reuters high-risk? → YES ✓
Q4 (Rank 7): Weak AML laws? → NO
...

FA Score = 10 (because Q1 is the highest-ranked YES)
```

```
Another Example: Configuring FA for "Germany" (Geography Gate)

Q1 (Rank 10): Is this OFAC prohibited? → NO
Q2 (Rank 9): Is this FATF high-risk? → NO
Q3 (Rank 8): Thomson Reuters high-risk? → NO
Q4 (Rank 7): Weak AML laws? → NO
Q5 (Rank 6): Tax haven? → NO
Q6 (Rank 5): Any privacy concerns? → YES ✓
...

FA Score = 5 (because Q6 is the highest-ranked YES)
```

### How FA Score Becomes a Multiplier

When a CRR rule evaluates a customer, the FA score is dynamically fetched based on the customer's attributes:

```
Customer A:
- Account Holder Country = Venezuela
- Product = Corp CPC

Rule RS001 evaluates:
- Condition: Customer_Jurisdiction IN High_Risk_Countries → TRUE
- Weight: Fixed at 2.0
- Multiplier: Fetched from FA table for "Venezuela" → 10

Final Score Contribution = TRUE × 2.0 × 10 = 20 points
```

```
Customer B:
- Account Holder Country = Spain  
- Product = Corp CPC

Same Rule RS001 evaluates:
- Condition: Customer_Jurisdiction IN High_Risk_Countries → TRUE
  (Spain is also in High_Risk_Countries list)
- Weight: Fixed at 2.0
- Multiplier: Fetched from FA table for "Spain" → 7
  (Spain has lower FA score than Venezuela because fewer high-risk questions answered YES)

Final Score Contribution = TRUE × 2.0 × 7 = 14 points
```

```
Customer C:
- Account Holder Country = Germany  
- Product = Corp CPC

Same Rule RS001 evaluates:
- Condition: Customer_Jurisdiction IN High_Risk_Countries → TRUE
  (Germany is also in High_Risk_Countries list)
- Weight: Fixed at 2.0
- Multiplier: Fetched from FA table for "Germany" → 5
  (Germany has even lower FA score - only minor concerns)

Final Score Contribution = TRUE × 2.0 × 5 = 10 points
```

**Key Point:** The SAME ruleset and SAME rule logic produces DIFFERENT risk scores for different customers based on their account holder country's FA scores!

**The multiplier is DYNAMICALLY picked from the FA attributes table based on the customer's data.**

(Note: FA Overrides also matter - if a market has set an override for a particular attribute, the override score is used instead of the default.)

### FA Navigation Hierarchy (How to Access FA Configuration)

Here's the complete navigation flow when accessing Fundamental Assessment:

```
Configuration Selector Dropdown (inside Sandbox)
└── Select "Fundamental Assessment"
    │
    └── Assessment Types (The 6 FA Gates)
        ├── Geography
        ├── Industry
        ├── Product
        ├── Structure
        ├── Occupation
        └── Acquisition Channel
            │
            └── Attributes (specific items in that gate)
                ├── (For Geography) Venezuela, Germany, India, etc.
                ├── (For Industry) Casinos, Hotels, Money Services, etc.
                │
                └── Questionnaire Screen (for selected attribute)
                    ├── 10 Questions with Yes/No answers
                    ├── Justification required for each answer
                    ├── [Calculate] button
                    └── [Update Override] button
```

### Answering Questions vs Setting Overrides

There are TWO different workflows on the Questionnaire screen:

| Action | What It Does | Justification Required? |
|--------|--------------|------------------------|
| **Answering Questions** | Set Yes/No for each of the 10 questions | ✅ YES - Must provide reason for each answer |
| **Setting Override** | Set a market-specific override score | ❌ NO - Can directly set override value |

**Answering Questions:**
1. Navigate to: FA → Assessment Type → Attribute → Questionnaire
2. For each question, select YES or NO
3. **Must provide justification** for why that answer was chosen
4. Click **[Calculate]** to compute the new FA score
5. New score appears in the "New Score" column

**Setting Overrides:**
1. On the Questionnaire screen, click **[Update Override]** button
2. Select the Center/Market (e.g., India)
3. Enter the override score directly (no reason required)
4. Save the override (timestamp recorded)

### FA Overrides (Market-Specific Adjustments)

Sometimes markets have **local requirements** that differ from Enterprise scoring.

**Example Problem:**
- Enterprise FA score for "Casinos" (Industry) = 6
- But India wants Casinos scored as 8 (because gambling is more restricted in India)
- USA wants Casinos scored as 3 (because it's regulated but legal)

**Solution: FA Overrides**

```
Industry: Casinos
├── Enterprise FA Score: 6 (default from questionnaire)
├── Override for India: 8 (higher risk - set directly)
└── Override for USA: 3 (lower risk - set directly)
```

### FA Score Range

| Value | Meaning |
|-------|---------|
| **1** | Lowest possible score (minimum risk) |
| **10** | Highest possible score (maximum risk) |
| **0** | ❌ NOT ALLOWED - Score can NEVER be zero |

### Current Score vs New Score (Critical Concept!)

In the FA management screen, you see two columns. Understanding these is crucial:

| Column | What It Contains | When It's Used |
|--------|------------------|----------------|
| **Current Score** | FA score currently active in PRODUCTION | Used for PRODUCTION scoring |
| **New Score** | FA score you've configured in sandbox | Used for SIMULATION scoring |

**How They Work in Simulation:**

```
When simulation runs:
├── SANDBOX configuration uses: NEW SCORE
├── PRODUCTION baseline uses: CURRENT SCORE
│
└── Comparison Report Shows:
    ├── "With Current Score (Production): X customers at High Risk"
    ├── "With New Score (Sandbox): Y customers at High Risk"  
    └── "Change: +Z customers moved to High Risk"
```

**What Happens on Promotion to Production:**

```
Before Promotion:
├── Current Score: 6
└── New Score: 8

After Promotion to Production:
├── Current Score: 8 (New Score becomes Current Score!)
└── New Score: 8 (same as Current until next change)
```

**Initial Platform State:**
When you first access the platform, both Current Score and New Score already have values configured (migrated from legacy system). They will be the same until someone makes a change in sandbox.

### The Calculate Button Workflow

The **[Calculate]** button is located on the **Questionnaire screen** (not on the main FA screen).

**Workflow:**
1. User changes answers to questions (Yes/No)
2. User provides justification for changes
3. User clicks **[Calculate]**
4. System computes new FA score based on highest-ranked YES question
5. New score is stored in the **New Score** column
6. New Score will be used when simulation runs

```
Before clicking Calculate:
├── Current Score: 6
└── New Score: 6 (unchanged)

User changes Q2 from NO to YES (Q2 has rank 9)

After clicking Calculate:
├── Current Score: 6 (unchanged - still in production)
└── New Score: 9 (recalculated based on new answers)
```

### Important FA Constraints

| Rule | Description |
|------|-------------|
| **Enterprise Only** | FA questions can ONLY be edited in Enterprise sandbox |
| **Full Population Testing** | Simulation runs on FULL customer population (not a sample!) |
| **Justification for Q&A** | Every question answer change requires a written reason |
| **No Justification for Override** | Overrides can be set directly without providing reason |
| **Calculate Required** | Must click "Calculate" after changing answers to update New Score |
| **Score Range** | Minimum = 1, Maximum = 10, Zero is NOT allowed |

### FA Values Are Already Configured (Initial Setup)

Unlike Rules and Assets which start blank, **FA framework already exists** with:
- All 6 gates defined
- All attributes listed under each gate
- Questions configured (migrated from legacy system)
- Both Current Score and New Score populated (initially same values)

Business only needs to update answers or add overrides as needed.

---

## Step 6: Submit for Simulation

User is happy with the configuration. Now they want to TEST it.

**What user does:**
1. Clicks "Submit for Simulation"
2. A confirmation modal appears showing:
   - **Rules Changed:** 15
   - **Assets Added:** 4
   - **Fundamental Assessment:** (configured if any)
3. User writes a comment: "Initial Enterprise configuration for AML risk scoring"
4. Clicks "Submit"

**What happens in the system?**

```
Sandbox Enterprise:
├── Version: 1
├── Status: WORKING → IN_PROGRESS (simulation running)
│
├── Snapshot Captured:
│   ├── Rules: R001, R002, R003... (all frozen)
│   ├── Asset Versions Used:
│   │   ├── A001 V1
│   │   ├── A002 V1
│   │   ├── A003 V1
│   │   └── A004 V1
│   └── Configuration: Immutable (cannot be changed now)
```

**CRITICAL:** Once you submit, a "snapshot" is taken. This snapshot:
- Records EXACTLY which asset versions were used
- Freezes the configuration for testing
- Cannot be edited until simulation completes

---

## Step 7: Simulation Runs

The system runs the simulation against the **FULL customer population** for that market (not a sample!).

**What happens?**
1. Simulation engine reads the sandbox configuration
2. Applies rules to test customers
3. Calculates risk scores
4. Generates comparison report (before vs after)

**During this time:**
- Sandbox status: "IN_PROGRESS"
- All editing is DISABLED
- User can only wait and watch progress

**After completion:**
- Sandbox status: "TESTING_COMPLETED"
- Results available for review

---

## Step 8: Review Results and Approve

User reviews the simulation results.

**What user sees:**
- "10,000 customers moved from Low Risk to Medium Risk"
- "500 customers moved to High Risk"
- Detailed breakdown by rule

**User decision:** Results look good, proceed to approval.

**What happens:**
1. User clicks "Implement"
2. Status changes: TESTING_COMPLETED → PENDING_APPROVAL_1
3. First approver reviews and clicks "Approve"
4. Status changes: PENDING_APPROVAL_1 → PENDING_APPROVAL_2
5. Second approver (different person) reviews and clicks "Approve"

---

## Step 9: Promote to Production (THE BIG MOMENT)

This is the moment of truth!

**What user does:**
- Second approver clicks "Approve and Implement"

**What happens in the system (ATOMIC TRANSACTION):**

```
┌─────────────────────────────────────────────────────────────────┐
│                    ATOMIC PROMOTION                              │
│                                                                  │
│  The following happens as ONE operation:                        │
│  (If ANY step fails, EVERYTHING rolls back)                     │
│                                                                  │
│  1. All Rules from Sandbox → Production                         │
│  2. All Assets from Sandbox → Production                        │
│  3. All FA config from Sandbox → Production                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Asset Status Changes:**

| Asset | Before | After |
|-------|--------|-------|
| A001 V1 | SANDBOX | PRODUCTION |
| A002 V1 | SANDBOX | PRODUCTION |
| A003 V1 | SANDBOX | PRODUCTION |
| A004 V1 | SANDBOX | PRODUCTION |

**System State After Promotion:**

```
┌─────────────────────────────────┐
│  PRODUCTION: Enterprise         │
│  Status: ACTIVE                 │
│  Assets: A001-A004 (all V1)     │
│  Rules: RS001-RS015             │
│  Actively scoring customers!    │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│  Sandbox: Enterprise V1         │
│  Status: IMPLEMENTED            │
│  (Historical record)            │
└─────────────────────────────────┘
```

---

# PART 3: NOW THINGS GET INTERESTING - MARKETS ENTER

We now have a production Enterprise assessment. What happens next?

---

## Step 10: Market Sandboxes Become Available

Remember earlier we said "Only Enterprise" was available? Now things change.

**System State:**
```
Production: Enterprise EXISTS ✓

Available Sandbox Options:
├── Enterprise: ✅ AVAILABLE (can create to make changes to Enterprise production)
└── Markets:
    ├── India (IN): ✅ AVAILABLE
    ├── Belgium (BE): ✅ AVAILABLE
    └── Germany (GE): ✅ AVAILABLE
```

### The Sandbox Mutual Exclusion Rule (Important!)

Here's a critical rule about sandbox coexistence:

> **Enterprise SANDBOX and Market SANDBOX cannot exist at the same time.**

**Why?** If both exist simultaneously:
- If Enterprise sandbox goes to Production → All market sandboxes become STALE
- If Market sandbox goes to Production → Enterprise changes may be incompatible
- This creates a messy refresh situation that's hard to manage

**The Decision:** To avoid this complexity, we enforce mutual exclusion at the SANDBOX level.

| Current State | Can Create Enterprise Sandbox? | Can Create Market Sandbox? |
|---------------|-------------------------------|---------------------------|
| No sandboxes exist | ✅ YES | ✅ YES |
| Enterprise SANDBOX exists | ✅ (already exists) | ❌ NO - Blocked |
| Any Market SANDBOX exists | ❌ NO - Blocked | ✅ YES (other markets OK) |
| Only Enterprise PRODUCTION exists (no sandbox) | ✅ YES | ✅ YES |

**Key Clarification:**
- Enterprise **PRODUCTION** existing does NOT block anything
- It's the Enterprise **SANDBOX** that blocks Market sandboxes (and vice versa)
- User can always create an Enterprise sandbox to make changes to Enterprise production
- But they cannot have Enterprise sandbox AND Market sandbox active simultaneously



---

## Step 11: Create India Sandbox

User wants to create India-specific rules.

**What user does:**
1. Click "Create New Sandbox"
2. Select "India (IN)"
3. System creates sandbox

**What happens?**
```
System copies Enterprise Production as baseline:
├── All Enterprise rules copied (but scoped to XX)
├── All assets available (pointing to same production assets)
└── India sandbox starts with Enterprise configuration as foundation

Sandbox India V1 Created:
├── Status: WORKING (Draft)
├── Baseline: Enterprise Production
└── Changes: None yet
```

**Important concept: The India sandbox doesn't DUPLICATE the assets. It REFERENCES them.**

---

## Step 12: India Wants to Use Existing Enterprise Asset

**Scenario:** India wants to use "High_Risk_Countries" asset in a new India-specific rule.

**What user does:**
1. Creates new Risk Element under "Geographic Risk" (India scope)
2. Creates new Ruleset "RS_IN_001"
3. Creates rule: "Customer_Jurisdiction IN High_Risk_Countries"

**What happens in system?**

```
Asset A001 (High_Risk_Countries):
├── Status: PRODUCTION (unchanged)
├── Version: 1 (unchanged)
└── Used By:
    ├── Enterprise Rules: RS001, RS005
    └── India Sandbox Rules: RS_IN_001 (NEW!)
```

The same asset (A001 V1) is now being used by:
- Enterprise production
- India sandbox

**This is called ASSET REUSE. It's powerful but needs careful handling.**

---

## Step 13: India Wants to EDIT the Asset (EDGE CASE!)

Here's where it gets tricky.

**Scenario:** India wants to ADD "Pakistan" to the High_Risk_Countries list.

**User tries to:**
1. Go to Assets in India sandbox
2. Find "High_Risk_Countries"
3. Click "Edit"

**What happens?**

```
┌─────────────────────────────────────────────────────────────────┐
│                         BLOCKED!                                │
│                                                                  │
│  ⚠️ This asset is used in Enterprise Production.                │
│                                                                  │
│  You cannot directly edit this asset because changes would      │
│  affect Enterprise rules.                                       │
│                                                                  │
│  Options:                                                        │
│  [Create a Copy for India]    [Cancel]                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Why is this blocked?**

Because if India edits "High_Risk_Countries", it would ALSO change what Enterprise sees. Enterprise didn't ask for that change!

---

## Step 14: Copy-on-Write Workflow (The Solution)

**What happens when user clicks "Create a Copy for India":**

1. System creates new asset:
   ```
   Original Asset (unchanged):
   ├── Asset ID: A001
   ├── Name: High_Risk_Countries
   ├── Version: 1
   ├── Status: PRODUCTION
   └── Values: [Iran, North Korea, Syria]
   
   NEW Copy Created:
   ├── Asset ID: A005 (new ID!)
   ├── Name: High_Risk_Countries_IN (auto-suffixed)
   ├── Version: 1 (fresh version for this new asset)
   ├── Status: DRAFT (brand new)
   └── Values: [Iran, North Korea, Syria] (copied from original)
   ```

2. User can now edit A005:
   - Add "Pakistan" to the list
   - Save changes

3. A005 becomes:
   ```
   Asset A005 (High_Risk_Countries_IN):
   ├── Version: 1
   ├── Status: SANDBOX (used in India sandbox)
   └── Values: [Iran, North Korea, Syria, Pakistan]
   ```

4. India's rule now points to A005 instead of A001:
   ```
   Rule RS_IN_001:
   └── Customer_Jurisdiction IN A005 (India's copy)
   ```

**Result:**
- Enterprise uses A001 with [Iran, North Korea, Syria]
- India uses A005 with [Iran, North Korea, Syria, Pakistan]
- Both are happy, no conflicts!

---

## Step 15: India Creates Brand New Asset

**Scenario:** India needs an asset that doesn't exist: "India_Specific_Suspicious_Occupations"

**What user does:**
1. Go to Assets
2. Click "Add New Asset"
3. Create:
   ```
   Asset ID: A006
   Name: India_Suspicious_Occupations
   Reference Table: Occupations
   Values: [Money Changer, Jeweller, ...]
   Status: DRAFT
   Version: 1
   ```

**Key point:** This asset is DRAFT because no rule uses it yet.

**User then:**
1. Creates rule using this asset
2. Asset status changes: DRAFT → SANDBOX

**Important:** This asset (A006) is ONLY used in India sandbox. It doesn't affect Enterprise at all.

---

## Step 16: India Submits for Simulation

**What happens on submit?**

```
India Sandbox V1 Snapshot:
├── Rules Added: 5 (India-specific)
├── Rules Modified: 3 (localised Enterprise rules)
├── Assets Used:
│   ├── A001 V1 (Enterprise - referenced for some rules)
│   ├── A005 V1 (India copy of High_Risk_Countries)
│   └── A006 V1 (India new asset)
└── Status: IN_PROGRESS
```

**The snapshot records EXACTLY which asset versions India is using.**

---

## Step 17: Meanwhile, Belgium Also Creates Sandbox

At the same time, Belgium team creates their sandbox.

**System State:**
```
Active Sandboxes:
├── India V1 (IN_PROGRESS - simulation running)
└── Belgium V1 (WORKING - just created)

Production:
└── Enterprise (ACTIVE)
```

**Key insight:** Multiple market sandboxes can exist simultaneously!

---

## Step 18: Belgium Wants to Use High_Risk_Countries Too

**Belgium does:**
1. Creates rule using A001 (High_Risk_Countries)

**What happens?**

```
Asset A001 (High_Risk_Countries):
├── Status: PRODUCTION
└── Used By:
    ├── Enterprise Production: RS001, RS005
    ├── India Sandbox: (not anymore, India uses A005 copy)
    └── Belgium Sandbox: RS_BE_001 (NEW!)
```

**Belgium can use A001 directly because:**
- A001 is in PRODUCTION status
- Belgium hasn't EDITED it
- Belgium is just REFERENCING it

---

## Step 19: Belgium Wants to Edit High_Risk_Countries

**Same scenario as India:**
1. Belgium tries to edit A001
2. System blocks: "This asset is used in Enterprise Production"
3. Belgium clicks "Create Copy"
4. System creates A007: "High_Risk_Countries_BE"

Now we have:
```
Asset A001: High_Risk_Countries (Enterprise)
   └── Values: [Iran, North Korea, Syria]
   
Asset A005: High_Risk_Countries_IN (India)
   └── Values: [Iran, North Korea, Syria, Pakistan]
   
Asset A007: High_Risk_Countries_BE (Belgium)
   └── Values: [Iran, North Korea, Syria, Belarus]
```

**Each market has their own copy with their own customizations!**

---

# PART 4: MAJOR EDGE CASES AND HOW THEY'RE HANDLED

Now let's look at all the tricky scenarios.

---

## EDGE CASE 1: Asset Used in Multiple Market Sandboxes

**Scenario:**
- India creates A006 (India_Suspicious_Occupations)
- India's sandbox is promoted to Production
- Now A006 is in PRODUCTION
- Belgium wants to use A006 in their rules

**What happens when Belgium creates a rule using A006?**

| Action | System Response |
|--------|-----------------|
| Belgium selects A006 in rule | ✅ ALLOWED (A006 is visible to all) |
| Belgium tries to EDIT A006 | ❌ BLOCKED - "Asset used in India Production" |
| Belgium clicks "Create Copy" | ✅ Creates A008: India_Suspicious_Occupations_BE |

**Key Rule:** Any asset in PRODUCTION that's used by another market cannot be directly edited by anyone except in Enterprise sandbox.

---

## EDGE CASE 2: Concurrent Editing (Two Users, Same Asset)

**Scenario:**
- User A opens asset A005 for editing at 10:00 AM (sees Version 1)
- User B opens same asset A005 at 10:01 AM (sees Version 1)
- User B saves changes at 10:05 AM (creates Version 2)
- User A tries to save at 10:10 AM

**What happens?**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONFLICT DETECTED!                            │
│                                                                  │
│  The asset has been modified by another user.                   │
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │ YOUR CHANGES    │    │ CURRENT STATE   │                     │
│  ├─────────────────┤    ├─────────────────┤                     │
│  │ Added: Pakistan │    │ Added: Myanmar  │                     │
│  │ (from V1)       │    │ (now V2)        │                     │
│  └─────────────────┘    └─────────────────┘                     │
│                                                                  │
│  [MERGE]    [OVERWRITE]    [RELOAD]                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Options explained:**
- **MERGE:** Combine both changes: [Pakistan + Myanmar]
- **OVERWRITE:** Keep only your changes, discard User B's changes
- **RELOAD:** Discard your changes, see latest version

**Technical Implementation:** This uses "Optimistic Locking" via a `version_no` column.

---

## EDGE CASE 3: Enterprise Updates Asset After Market Has Already Promoted

**Important Context:** Remember, Enterprise sandbox and Market sandbox CANNOT exist simultaneously. So this scenario happens in a SEQUENTIAL manner.

**Scenario:**
1. Enterprise Production has A001 V1 (High_Risk_Countries)
2. India creates sandbox (no Enterprise sandbox can exist now)
3. India uses A001 V1 in their rules
4. India promotes to Production → India Production now references A001 V1
5. India sandbox is now gone (promoted)
6. Time passes...
7. Enterprise creates new sandbox (allowed now, no market sandboxes exist)
8. Enterprise edits A001 → creates A001 V2
9. Enterprise promotes to Production

**What happens on Enterprise promotion?**

```
Asset Version Changes:
├── A001 V1: PRODUCTION → ARCHIVED (old version archived)
└── A001 V2: SANDBOX → PRODUCTION (new version becomes active)

Rule Updates (Automatic):
├── Enterprise Rules using A001: Now use V2 ✓
├── India Rules using A001: Now use V2 ✓  (Automatic!)
└── Belgium Rules using A001: Now use V2 ✓ (Automatic!)
```

**Key Rule: LATEST VERSION IS ALWAYS USED EVERYWHERE**

> When Enterprise promotes a new asset version to production:
> 1. Old version (V1) → **ARCHIVED**
> 2. New version (V2) → **PRODUCTION**
> 3. **ALL rules across ALL scopes** automatically use the latest version
> 4. There is NO scenario where India uses V1 while Enterprise uses V2

**Why this design?**

```
❌ IMPOSSIBLE: Split Version Scenario
├── Enterprise uses: A001 V2
└── India uses: A001 V1
    └── THIS CANNOT HAPPEN!

✅ ACTUAL: Single Version for All
├── Enterprise uses: A001 V2
├── India uses: A001 V2 (same!)
└── Belgium uses: A001 V2 (same!)
```

**Implication for Markets:**
- When Enterprise updates an asset, market productions automatically get the updated values
- Markets don't need to manually "pull" or "sync" - it's automatic
- If a market needs DIFFERENT values than Enterprise, they must create their OWN COPY of the asset

## EDGE CASE 4: Asset Becomes Orphaned

**Scenario:**
1. User creates asset A008 in sandbox
2. User links it to rule RS_010
3. Later, user deletes rule RS_010
4. Now A008 is not used by anything

**What happens?**

```
Asset A008:
├── Status: SANDBOX (was linked to a rule)
├── Used By: NOTHING (rule was deleted)
└── Fate: Becomes "orphaned"
```

**System behavior:**
- Asset remains in SANDBOX status (doesn't auto-delete)
- After 90 days of being unused → auto-marked as ARCHIVED
- Archived assets hidden from default search (but still exist)

---

## EDGE CASE 5: Sandbox Hits Version Limit (10 Versions)

**Scenario:**
1. User creates sandbox, makes changes, submits (V1)
2. Simulation fails, creates V2
3. This repeats... V3, V4, V5... V10
4. User tries to create V11

**What happens?**

```
┌─────────────────────────────────────────────────────────────────┐
│                    VERSION LIMIT REACHED                        │
│                                                                  │
│  This sandbox has reached the maximum of 10 versions.           │
│                                                                  │
│  To continue working, you must:                                 │
│  [Archive This Sandbox and Start New]                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**What happens on archive:**
1. Old sandbox → Read-only historical record
2. New sandbox created → V1
3. **All asset versions CARRY OVER to new sandbox**
4. User continues from where they left off

---

## EDGE CASE 6: Rollback to Old Sandbox Version

**Scenario (within same sandbox):**
1. User creates Market sandbox V1
2. User makes changes, submits for simulation → V2 created
3. User makes more changes, submits → V3 created
4. Simulation results for V3 are bad
5. User wants to rollback to V2 (or even V1)

**What happens?**

```
┌─────────────────────────────────────────────────────────────────┐
│                    ROLLBACK CONFIRMATION                        │
│                                                                  │
│  You are about to rollback to Version 2.                        │
│                                                                  │
│  This will discard all changes made in Version 3.               │
│  This action cannot be undone.                                  │
│                                                                  │
│  [Rollback to V2]    [Cancel]                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Allowed:** User can rollback to any previous version within the same sandbox.

**Note:** This is different from the "STALE" concept. STALE happens when the underlying PRODUCTION baseline changes. Rollback within a sandbox is just going back to a previous attempt within the same baseline.

---

## EDGE CASE 7: Simulation Queue Delay

**Scenario:**
1. User submits Market sandbox at 10:00 AM
2. System is busy, simulation enters queue
3. At 12:00 PM, user's simulation finally runs

**Question:** Does simulation use 10:00 AM state or 12:00 PM state?

**Answer:** 10:00 AM state (SUBMIT time)

**Why?** Configuration is COPIED at submit time, not when job starts. This ensures consistency.

**Note:** Since Enterprise sandbox cannot exist while Market sandbox exists, there is no scenario where Enterprise updates production while a market simulation is in queue. The mutual exclusion rule prevents this complexity.

---

## EDGE CASE 8: Enterprise Deletes Risk Category That Markets Have Overridden

**Important Clarification First:**
- **Risk Category** (e.g., "Geographic Risk") = Organizational grouping for RULES in the CRR framework
- **FA Gate** (e.g., "Geography") = Fundamental Assessment gate for ACCOUNT HOLDER'S country

These are DIFFERENT concepts. This edge case is about **Risk Categories** (rule organization), NOT FA gates.

**Scenario:**
1. Enterprise has "Customer Risk" category with rules about customer types
2. India created localised rule overrides in "Customer Risk" category
3. Enterprise wants to DELETE "Customer Risk" category entirely

**What happens?**

```
┌─────────────────────────────────────────────────────────────────┐
│                    DELETION BLOCKED                             │
│                                                                  │
│  You cannot delete "Customer Risk" category because:            │
│                                                                  │
│  Markets with localisations in this category:                   │
│  - India: 5 rule overrides                                      │
│  - Belgium: 3 rule overrides                                    │
│                                                                  │
│  Please coordinate with markets before deleting.                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Enterprise cannot force-delete.** They must work with markets first.

---

## EDGE CASE 9: Draft Asset Gets Promoted Before Being Used

**Important Context:** Remember, Enterprise sandbox and Market sandbox CANNOT exist simultaneously.

**Valid Scenario (Sequential):**
1. India creates sandbox
2. User A creates asset A010 in India sandbox (status: DRAFT)
3. User A hasn't linked A010 to any rule yet
4. India sandbox gets promoted to Production (without using A010)
5. A010 status is still DRAFT (unused assets don't automatically get promoted)
6. Time passes...
7. Enterprise creates sandbox (allowed now, no market sandboxes)
8. Enterprise user sees A010 (it's visible globally) and uses it in Enterprise rules
9. Enterprise promotes to Production
10. A010 is now PRODUCTION status!

**What happens when India creates new sandbox?**

```
User A in India creates sandbox:
├── Sees A010 but can't edit it directly
├── Reason: "Asset is in Enterprise Production"
└── Must create a copy to make India-specific changes
```

**Key Learning:** 
- Assets are globally visible once created
- Any scope can use a DRAFT asset if they link it to their rules
- Whoever promotes first "claims" the asset to their production
- Other scopes must create copies to customize

---

## EDGE CASE 10: Asset Version Explosion

**Scenario:**
Over 3 months, an asset is edited 100+ times across various sandboxes.

**What happens in UI?**

```
Version Dropdown:
├── Shows: Last 10 versions only
├── Link: "View All 127 Versions →"
└── Full history accessible, just not in dropdown
```

**No hard limit** on versions, but UI is optimized for usability.

---

# PART 5: COMPLETE SYSTEM STATE DIAGRAM

After all the above scenarios, here's what a mature system looks like:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PRODUCTION                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Enterprise Assessment                                                   │
│  ├── Rules: RS001-RS050                                                  │
│  ├── Assets: A001 V2, A002 V1, A003 V3, A004 V1                         │
│  └── Status: ACTIVE (scoring 50M customers daily)                        │
│                                                                          │
│  India Assessment (extends Enterprise)                                   │
│  ├── Inherited: All Enterprise rules                                    │
│  ├── Overrides: RS_IN_001 to RS_IN_010                                  │
│  ├── Assets: A005 V3 (India copy), A006 V2 (India-only)                 │
│  └── Status: ACTIVE                                                      │
│                                                                          │
│  Belgium Assessment (extends Enterprise)                                 │
│  ├── Inherited: All Enterprise rules                                    │
│  ├── Overrides: RS_BE_001 to RS_BE_005                                  │
│  ├── Assets: A007 V1 (Belgium copy)                                     │
│  └── Status: ACTIVE                                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                           SANDBOXES                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Germany Sandbox V2 (Status: WORKING)                                   │
│  ├── Creating new overrides                                              │
│  ├── Using: A001 V2 (Enterprise), A010 V1 (Germany-only, DRAFT)         │
│  └── Not yet submitted for simulation                                   │
│                                                                          │
│  Spain Sandbox V1 (Status: TESTING_COMPLETED)                           │
│  ├── Simulation complete, awaiting approval                             │
│  ├── Assets: A011 V1 (Spain-only)                                       │
│  └── Next: Approver review                                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                        ASSET INVENTORY                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ID    │ Name                        │ Status     │ Versions │ Used By  │
│  ──────┼─────────────────────────────┼────────────┼──────────┼──────────│
│  A001  │ High_Risk_Countries         │ PRODUCTION │ V1, V2   │ ENT, BE  │
│  A002  │ Low_Risk_Occupations        │ PRODUCTION │ V1       │ ENT      │
│  A003  │ Sanctioned_Entities         │ PRODUCTION │ V1-V3    │ ENT      │
│  A004  │ High_Value_Products         │ PRODUCTION │ V1       │ ENT      │
│  A005  │ High_Risk_Countries_IN      │ PRODUCTION │ V1-V3    │ IN       │
│  A006  │ India_Suspicious_Occupations│ PRODUCTION │ V1-V2    │ IN       │
│  A007  │ High_Risk_Countries_BE      │ PRODUCTION │ V1       │ BE       │
│  A010  │ Germany_Local_List          │ DRAFT      │ V1       │ GE (sbx) │
│  A011  │ Spain_Custom_Products       │ SANDBOX    │ V1       │ ES (sbx) │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# PART 6: SUMMARY OF KEY RULES

## Asset Status Transitions

```
DRAFT ──────► SANDBOX ──────► PRODUCTION ──────► ARCHIVED
  │              │                  │
  │              │                  └── When newer version promoted
  │              │
  │              └── When linked to ruleset in sandbox
  │
  └── Newly created, not linked anywhere
```

### Critical Rule: Single Active Version

> **Only ONE version of an asset can be in PRODUCTION status at any time.**

When a new version is promoted:
1. Old version (Vn) → ARCHIVED
2. New version (Vn+1) → PRODUCTION
3. **ALL rules across ALL scopes** automatically use the new version

**There is NO scenario where Enterprise uses V2 while India uses V1 for the same asset!**

If a market needs different values, they must create their **OWN COPY** of the asset.

## Editability Rules (Quick Reference)

| Asset Status | Your Sandbox Type | Editable? | Why? |
|--------------|-------------------|-----------|------|
| DRAFT | Any | ✅ YES | Not used anywhere yet |
| SANDBOX | Your market only | ✅ YES | Your sandbox, your rules |
| SANDBOX | Other markets | ❌ NO | Would affect them |
| PRODUCTION | Your market only | ✅ YES | Create new version |
| PRODUCTION | Multiple markets | ❌ NO | Create copy |
| PRODUCTION | Enterprise | ❌ NO | Create copy |

## Sandbox Scope Rules

| Scenario | Enterprise Sandbox | Market Sandboxes |
|----------|-------------------|------------------|
| No production exists | ✅ Only option | ❌ Not available |
| Enterprise production exists | ✅ Available | ✅ Available |
| Enterprise sandbox active | ✅ (is active) | ❌ Blocked |
| Market sandbox active | ❌ Blocked | ✅ Other markets OK |

---

# APPENDIX: Frequently Confused Concepts

## "Linking" vs "Copying" an Asset

| Action | What It Means |
|--------|---------------|
| **Linking** | Rule points to existing asset. No duplication. |
| **Copying** | Creates new asset with same values. Independent thereafter. |

## "Version" Meanings

| Context | What "Version" Means |
|---------|---------------------|
| Asset Version | V1, V2, V3 of same asset (edit history) |
| Sandbox Version | V1-V10 of sandbox (simulation attempts) |
| Production Version | P1, P2... (each promotion creates new production version) |

---

*Document End*

*This guide should help you understand every step from zero to a fully operational CRR system.*
