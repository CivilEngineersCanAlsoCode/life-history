# CRR Glossary

## Core Terms

### Assessment / Sandbox
The workspace where configuration changes are made. An assessment is a versioned container that holds all changes before they are promoted to production.

### Risk Framework
The hierarchical structure of risk configuration: Categories → Elements → Rulesets → Rules.

---

## Risk Hierarchy Terms

### Risk Category
Top-level grouping of risk. CRR has 5 standard categories:
1. **Customer Risk** - Customer-specific attributes
2. **Geographic Risk** - Location-based risk
3. **Transaction Risk** - Transaction patterns and behavior
4. **Products & Services Risk** - Product-specific risk
5. **ARFs & HROs** - Additional Risk Factors & High Risk Organizations

### Risk Element
A specific dimension of risk within a category. Examples:
- Under Customer Risk: "Source of Wealth", "Length of Relationship"
- Under Geographic Risk: "Country of Residence", "Country of Business"

### Ruleset
A collection of rules under an element that share the same weighting and multiplier logic.

### Rule
A single condition that evaluates customer data. Structure:
```
[Datapoint] [Operator] [Value/Asset]
Example: Customer_Country IN High_Risk_Countries
```

---

## Asset Terms

### Asset
A reusable list of values that can be used in multiple rules. Examples:
- "High Risk Countries" = [Iran, North Korea, Syria]
- "Cash Intensive Industries" = [Casino, Money Services, Jewelry]

### Reference Data Table
Master list of all valid values for a datapoint. Assets must contain values from their linked reference table.

### Asset Version
Every edit to an asset creates a new immutable version. Format: Asset_Name V1, V2, V3, etc.

---

## State Terms

### Draft
- For Assets: Created but not linked to any rule
- Fully editable and deletable

### Sandbox State
- For Assets: Linked to a rule in a sandbox
- Editable only within the sandbox that owns it

### Production State
- For Assets: Promoted to live production
- Read-only, cannot be directly edited
- Editing creates new version in sandbox

### Archived State
- Previous version replaced by newer version
- Retained for audit purposes
- Never deleted

---

## Sandbox Terms

### Enterprise Sandbox
- Scope: All markets
- Can edit: All assets, all rules
- Only ONE can exist at a time

### Market Sandbox
- Scope: Single market (e.g., India only)
- Can edit: Market-specific rules and assets
- Multiple market sandboxes can coexist

### Promotion / Merge
The process of moving sandbox changes to production after simulation and approval.

### Simulation
Mandatory testing of sandbox changes against sample customer data before approval.

---

## Fundamental Assessment Terms

### FA Gate
One of 6 pre-scored attribute categories:
| Code | Name |
|------|------|
| GR | Geography |
| IR | Industry |
| PRR | Product |
| OCCP | Occupation |
| ACR | Acquisition Channel |
| SR | Structure |

### FA Score
A pre-calculated risk score (1-10) for each attribute in an FA gate.

### FA Override
Market-specific override of an FA score (e.g., India gives "Casino" industry a score of 8 instead of Enterprise default of 6).

---

## User Terms

### CRR Business User
- Compliance Analyst or Risk Manager
- Full access to create, edit, simulate, and promote

### Market Compliance Officer (MCO)
- Regional compliance lead
- View-only access to production configuration
- Cannot edit anything

---

## Technical Terms

### Datapoint
A customer attribute field that can be evaluated in rules. Examples:
- Customer_Country
- Product_Type
- Industry_Code
- Transaction_Amount

### Operator
Logical comparison used in rules:
| Type | Operators |
|------|-----------|
| Numeric | >, <, =, >=, <= |
| List/Asset | IN, NOT IN |
| Boolean | TRUE, FALSE |
| String | EQUALS, CONTAINS |

### Multiplier
A factor that amplifies or dampens the risk contribution of a ruleset.
- **Value-based**: Static number (e.g., 2.0)
- **FA-based**: Uses FA score as multiplier

---

## Status Codes Quick Reference

### Assessment Status Codes
| Code | Name |
|------|------|
| 1 | WORKING |
| 2 | SUBMITTED |
| 3 | SKIPPED |
| 4 | SIMULATED |
| 5 | APPROVAL_1 |
| 6 | APPROVAL_2 |
| 7 | REJECTED |
| 8 | MERGED_TO_PROD |

### Asset Status Codes
| Status | Meaning |
|--------|---------|
| DRAFT | Not linked anywhere |
| SANDBOX | In use in sandbox |
| PRODUCTION | Live in production |
| ARCHIVE | Old version, replaced |
| DELETE | Soft deleted |

---

*This glossary is a living document. Update as new terms are introduced.*
