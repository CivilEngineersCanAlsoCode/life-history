# CRR Risk Framework Hierarchy

## Overview

The CRR risk framework is organized as a hierarchical tree structure that defines how customer risk is calculated.

```
Risk Framework (Enterprise or Market scoped)
  └── Risk Categories (5 total)
        └── Risk Elements (multiple per category)
              └── Rulesets (multiple per element)
                    └── Rules (multiple per ruleset)
```

---

## Hierarchy Levels

### Level 1: Risk Framework
- **Scope**: Enterprise (global) or Market-specific
- **Purpose**: Container for all risk configuration
- **Key Attribute**: `iso_alpha2_ctry_cd` (XX = Enterprise, IN = India, etc.)

### Level 2: Risk Categories
CRR has **5 standard categories**:

| # | Category Name | Description |
|---|---------------|-------------|
| 1 | **Customer Risk** | Customer-specific attributes like source of wealth, occupation |
| 2 | **Geographic Risk** | Location-based risk (country of residence, business, transactions) |
| 3 | **Transaction Risk** | Transaction patterns, volumes, and behaviors |
| 4 | **Products & Services Risk** | Risk associated with specific products held |
| 5 | **ARFs & HROs** | Additional Risk Factors and High Risk Organizations |

### Level 3: Risk Elements
- Specific dimensions of risk within a category
- Each element has:
  - Name and description
  - Time-based evaluation flag
  - MIN/MAX multiplier evaluation logic
  - Prohibited flag (can trigger score of 10)

### Level 4: Rulesets
- Collection of rules with shared configuration
- Each ruleset has:
  - Description
  - Default multiplier and weighting
  - Applicability (Entities/Individuals/Intermediaries)
  - Condition logic

### Level 5: Rules
- Individual conditions that evaluate customer data
- Each rule has:
  - Datapoint (what customer field to check)
  - Operator (how to compare)
  - Value/Asset (what to compare against)

---

## Visual Hierarchy Example

```
Risk Framework: India (IN)
│
├── Customer Risk
│   ├── Source of Wealth
│   │   ├── Ruleset: High-Value Source Check
│   │   │   ├── Rule: IF Source_of_Wealth IN ["Inheritance", "Lottery"] THEN 2.0x
│   │   │   └── Rule: IF Source_of_Wealth IN ["Business Income"] THEN 1.0x
│   │   │
│   │   └── Ruleset: Unexplained Wealth
│   │       └── Rule: IF Wealth_vs_Income_Ratio > 10 THEN 3.0x
│   │
│   └── Length of Relationship
│       └── Ruleset: New Customer Risk
│           └── Rule: IF Relationship_Months < 6 THEN 1.5x
│
├── Geographic Risk
│   ├── Country of Residence
│   │   └── Ruleset: High Risk Countries
│   │       └── Rule: IF Residence_Country IN [High_Risk_Countries_Asset] THEN FA_Score
│   │
│   └── Country of Business
│       └── ...
│
├── Transaction Risk
│   └── ...
│
├── Products & Services Risk
│   └── ...
│
└── ARFs & HROs
    └── ...
```

---

## Key Relationships

### One-to-Many Relationships
```
1 Risk Assessment → Many Categories
1 Category → Many Elements
1 Element → Many Rulesets
1 Ruleset → Many Rules
```

### Many-to-One Relationships
```
Many Rules → 1 Asset (reused across rules)
Many Rules → 1 Datapoint (same field evaluated differently)
```

---

## Inheritance Model

### Enterprise → Market
1. **Enterprise configuration** sets the baseline
2. **Market configuration** can:
   - Add new market-specific rules
   - Override Enterprise settings
   - Disable Enterprise rules for that market

### What Can Markets Do?
| Action | Allowed? |
|--------|----------|
| Add new rulesets | ✅ Yes |
| Add new rules to existing rulesets | ✅ Yes |
| Disable Enterprise rules | ✅ Yes (via toggle) |
| Edit Enterprise rules | ❌ No (create market override) |
| Delete Enterprise rules | ❌ No |

---

*Next: See `02_Risk_Elements.md` for element-level details.*
*Next: See `03_Rulesets.md` for ruleset configuration.*
*Next: See `04_Rules.md` for rule structure and operators.*
