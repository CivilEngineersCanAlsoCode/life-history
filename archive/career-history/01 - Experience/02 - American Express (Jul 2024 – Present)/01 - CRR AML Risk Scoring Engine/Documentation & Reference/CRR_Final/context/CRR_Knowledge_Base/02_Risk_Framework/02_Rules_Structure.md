# Rule Structure & Creation

## Rule Components

A CRR rule is composed of the following components in **order of creation**:

```
1. Description → 2. Multiplier Type → 3. Multiplier Value/FA Gate → 4. Datapoint → 5. Operator → 6. Value/Asset
```

---

## Component Details

### 1. Rule Description
- Free text description of what the rule does
- Used for audit and documentation
- Example: "Flag customers in high-risk countries"

### 2. Multiplier Type
| Type | Description |
|------|-------------|
| **Value** | Static numeric multiplier |
| **FA (Fundamental Assessment)** | Uses pre-scored FA gate value as multiplier |

### 3. Multiplier Value / FA Gate Selection
- If **Value**: Enter numeric value (e.g., 1.5, 2.0, 3.0)
- If **FA**: Select one of 6 FA gates (GR, IR, PRR, OCCP, ACR, SR)

### 4. Datapoint
Customer attribute to evaluate. Examples:
- `Customer_Country`
- `Product_Type`
- `Industry_Code`
- `Transaction_Amount`
- `Source_of_Wealth`

**Key**: Datapoint selection determines which reference table (and thus which assets) are available.

### 5. Operator
| Datapoint Type | Available Operators |
|----------------|---------------------|
| **Numeric** | `>`, `<`, `=`, `>=`, `<=`, `BETWEEN` |
| **List/Asset** | `IN`, `NOT IN`, `INCLUDES`, `EXCLUDES` |
| **Boolean** | `TRUE`, `FALSE` |
| **String** | `EQUALS`, `CONTAINS`, `STARTS WITH` |

### 6. Value or Asset Selection
- **Static Value**: Direct entry (e.g., "100000", "true")
- **Asset**: Select from available assets linked to the datapoint's reference table

---

## Rule Creation Order (UI Flow)

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Enter Rule Description                                  │
│         "Flag high-risk country of residence"                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Select Multiplier Type                                  │
│         (○) Value   (●) FA                                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: Select FA Gate (if FA selected)                         │
│         [ Geography (GR) ▼ ]                                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: Select Datapoint                                        │
│         [ Customer_Country ▼ ]                                  │
│         → This filters available assets to "Countries" table     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: Select Operator                                         │
│         [ IN ▼ ]                                                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: Select Asset or Enter Value                             │
│         [ High_Risk_Countries_V2 ▼ ]                            │
│         (Only shows assets linked to Countries reference table)  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Rule Logic Composition

### Logical Operators
Rules within a ruleset can be combined using:
- **AND** - All conditions must be true
- **OR** - Any condition must be true
- **Parentheses** - For grouping complex logic

### Example Complex Rule
```
(Customer_Country IN High_Risk_Countries)
AND
(
  (Transaction_Amount > 100000)
  OR
  (Product_Type IN Cash_Intensive_Products)
)
```

---

## Multiplier Evaluation

### Value-based Multiplier
```
IF rule matches THEN apply multiplier directly
Example: IF Country IN High_Risk THEN 2.0x
```

### FA-based Multiplier
```
IF rule matches THEN use FA score as multiplier
Example: IF Country IN High_Risk THEN FA(GR) score of that country
```

### Element Evaluation Mode
| Mode | Behavior |
|------|----------|
| **MAX** | Use highest matching ruleset multiplier |
| **MIN** | Use lowest matching ruleset multiplier |

---

## Rule Applicability

Rules can be configured to apply to specific customer types:

| Code | Customer Type |
|------|---------------|
| **I** | Individuals (personal accounts) |
| **E** | Entities (business accounts) |
| **M** | Intermediaries (merchants) |
| **XX** | All customer types |

---

## Quick Asset Feature

When creating a rule and the needed asset doesn't exist:
1. User can click "Create Quick Asset"
2. Enter asset name and values
3. Asset is immediately available for selection
4. Asset is created in DRAFT state, moves to SANDBOX when rule is saved

---

*Next: See `04_Asset_Manager/` for asset management details.*
