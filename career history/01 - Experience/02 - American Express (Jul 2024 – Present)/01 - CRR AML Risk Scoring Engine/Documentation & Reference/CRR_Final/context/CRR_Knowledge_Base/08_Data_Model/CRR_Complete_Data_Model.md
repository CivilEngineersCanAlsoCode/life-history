# CRR Complete Data Model Documentation

## Document Purpose
This document provides a comprehensive reference for the CRR (Customer Risk Rating) database schema, covering all tables related to Risk Assessments, Assets, Rules, and Fundamental Assessments.

---

# PART 1: DATA MODEL OVERVIEW

## 1.1 High-Level Entity Relationship

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     CRR DATA MODEL OVERVIEW                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘

                                    ┌─────────────────────┐
                                    │    risk_assess      │
                                    │  (Assessment/Sandbox)│
                                    └──────────┬──────────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
                    ▼                          ▼                          ▼
        ┌───────────────────┐      ┌───────────────────┐      ┌───────────────────┐
        │risk_assess_sta_trk│      │ risk_assess_ctgy  │      │risk_assess_config │
        │  (Status Tracking)│      │ (Risk Categories) │      │     _event        │
        └───────────────────┘      └─────────┬─────────┘      └───────────────────┘
                                             │
                                             ▼
                                   ┌───────────────────┐
                                   │risk_assess_ctgy_  │
                                   │      elem         │
                                   │ (Risk Elements)   │
                                   └─────────┬─────────┘
                                             │
                                             ▼
                                   ┌───────────────────┐
                                   │     rule_set      │
                                   │   (Rulesets)      │
                                   └─────────┬─────────┘
                                             │
                                             ▼
                                   ┌───────────────────┐
                                   │    risk_rule      │◄─────────────┐
                                   │     (Rules)       │              │
                                   └───────────────────┘              │
                                             │                        │
                                             │ links to               │
                                             ▼                        │
        ┌───────────────────────────────────────────────────────────────────────────────┐
        │                              ASSET MANAGER TABLES                              │
        └───────────────────────────────────────────────────────────────────────────────┘
                    │                          │                          │
                    ▼                          ▼                          ▼
        ┌───────────────────┐      ┌───────────────────┐      ┌───────────────────┐
        │refer_da_asset_srce│      │  refer_da_asset   │      │refer_da_asset_sta │
        │ (Reference Table) │◄─────│     (Assets)      │─────▶│     _hist         │
        └───────────────────┘      └───────────────────┘      │ (Status History)  │
                    │                        │                └───────────────────┘
                    ▼                        ▼
        ┌───────────────────┐      ┌───────────────────┐
        │refer_da_asset_    │      │refer_da_asset_    │
        │   srce_da_pt      │      │  scope_mapping    │
        │(Datapoint Mapping)│      │ (Market Mapping)  │
        └───────────────────┘      └───────────────────┘
```

---

## 1.2 Table Categories

| Category | Tables | Purpose |
|----------|--------|---------|
| **Assessment/Sandbox** | `risk_assess`, `risk_assess_sta_trk`, `risk_assess_config_event` | Manage sandbox lifecycle and assessment versions |
| **Risk Framework** | `risk_assess_ctgy`, `risk_assess_ctgy_elem`, `rule_set`, `risk_rule`, `ruleset_risk_mthd` | Define risk categories, elements, rulesets, and rules |
| **Asset Manager** | `refer_da_asset_srce`, `refer_da_asset`, `refer_da_asset_sta_hist`, `refer_da_asset_srce_da_pt`, `refer_da_asset_scope_mapping` | Manage centralized assets and their lifecycle |
| **User Management** | `user` | Store user information |

---

# PART 2: ASSESSMENT/SANDBOX TABLES

## 2.1 `risk_assess` (Main Assessment Table)

**Purpose:** Stores all assessments (sandboxes). Each row represents a sandbox version for a specific market scope.

### Table Structure

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `risk_assess_id` | integer | NOT NULL | Unique identifier for the assessment |
| `risk_assess_vsn_no` | integer | NOT NULL | Version number of the assessment |
| `iso_alpha2_ctry_cd` | varchar(2) | NOT NULL | Market scope code (XX = Enterprise, IN = India, etc.) |
| `risk_assess_nm` | varchar(100) | NOT NULL | Assessment name |
| `risk_assess_ds` | varchar(500) | NULL | Assessment description |
| `act_in` | boolean | NOT NULL | Is this the active/current version? TRUE/FALSE |
| `hist_ts` | timestamp | NULL | Timestamp when this became historical (promoted) |
| `merge_prod_risk_assess_id` | integer | NULL | ID of the production assessment this was merged into |
| `merge_prod_risk_assess_vsn_no` | integer | NULL | Version of the production assessment |
| `srce_risk_assess_id` | integer | NULL | Source/parent assessment ID (NULL for first assessment) |
| `srce_risk_assess_vsn_no` | integer | NULL | Source/parent assessment version |
| `creat_ts` | timestamp(6) | NOT NULL | Creation timestamp |
| `creat_user_id` | varchar(34) | NOT NULL | User who created this assessment |
| `lst_updt_ts` | timestamp(6) | NULL | Last update timestamp |
| `lst_updt_user_id` | varchar(34) | NULL | User who last updated |

### Primary Key
`(risk_assess_id, risk_assess_vsn_no)`

### Key Business Rules

| Rule | Description |
|------|-------------|
| **First Assessment** | When creating first Enterprise assessment, `srce_risk_assess_id` and `srce_risk_assess_vsn_no` are NULL |
| **Sandbox Creation** | New sandbox creates new `risk_assess_id` with `risk_assess_vsn_no = 1` |
| **Version Increment** | When editing existing assessment, new version is created with incremented `risk_assess_vsn_no` |
| **Active Flag** | Only ONE assessment per scope can have `act_in = TRUE` at a time |
| **Promotion** | When promoted, `hist_ts` is set, `act_in` becomes FALSE, and `merge_prod_risk_assess_id/vsn_no` are populated |

### Example Data

**Scenario: First Enterprise Assessment Created**
```
risk_assess_id=1, risk_assess_vsn_no=1, iso_alpha2_ctry_cd='XX', act_in=TRUE
srce_risk_assess_id=NULL, srce_risk_assess_vsn_no=NULL
```

**Scenario: After Promotion to Production**
```
risk_assess_id=1, risk_assess_vsn_no=1, iso_alpha2_ctry_cd='XX', act_in=TRUE
hist_ts='2026-01-15T11:52:26', merge_prod_risk_assess_id=1, merge_prod_risk_assess_vsn_no=1
```

---

## 2.2 `risk_assess_sta_trk` (Assessment Status Tracking)

**Purpose:** Tracks the lifecycle status of each assessment version through various states.

### Table Structure

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `risk_assess_id` | integer | NOT NULL | Assessment ID |
| `risk_assess_vsn_no` | integer | NOT NULL | Assessment version |
| `risk_assess_sta_cd` | smallint | NOT NULL | Status code |
| `sta_cmnt_tx` | varchar(500) | NULL | Status comment/reason |
| `creat_user_id` | varchar(34) | NOT NULL | User who set this status |
| `creat_ts` | timestamp(6) | NOT NULL | When status was set |

### Primary Key
`(risk_assess_id, risk_assess_vsn_no, risk_assess_sta_cd)`

### Status Codes

| Code | Status Name | Description |
|------|-------------|-------------|
| 1 | WORKING | Initial draft state, being configured |
| 2 | SUBMITTED | Submitted for simulation |
| 3 | SKIPPED | Simulation skipped |
| 4 | SIMULATED | Simulation completed |
| 5 | APPROVAL_1 | First approval received |
| 6 | APPROVAL_2 | Second approval received |
| 7 | REJECTED | Assessment rejected |
| 8 | MERGED_TO_PROD | Successfully merged to production |

### Example Data - Full Lifecycle

```
risk_assess_id | risk_assess_vsn_no | risk_assess_sta_cd | sta_cmnt_tx              | creat_ts
---------------|--------------------|--------------------|--------------------------|-------------------------
1              | 1                  | 1                  | Default status, Version 1 | 2026-01-15T08:52:26
1              | 1                  | 3                  | skipped                   | 2026-01-15T10:54:26
1              | 1                  | 5                  | approval 1                | 2026-01-15T11:55:26
1              | 1                  | 6                  | approval 2                | 2026-01-15T11:52:26
1              | 1                  | 8                  | merged to prod            | 2026-01-15T11:52:26
```

---

## 2.3 `risk_assess_config_event` (Configuration Events)

**Purpose:** Logs configuration events that occur during the assessment lifecycle.

### Table Structure

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `risk_assess_config_event_id` | uuid | NOT NULL | Unique event identifier |
| `event_nm` | varchar(50) | NOT NULL | Event name |
| `risk_assess_id` | integer | NOT NULL | Assessment ID |
| `risk_assess_vsn_no` | integer | NOT NULL | Assessment version |
| `risk_assess_sta_cd` | smallint | NOT NULL | Current status code |
| `event_sta_nm` | varchar(15) | NULL | Event status name |
| `creat_ts` | timestamp(6) | NOT NULL | Event timestamp |
| `creat_user_id` | varchar(34) | NOT NULL | User who triggered event |
| `lst_updt_ts` | timestamp(6) | NULL | Last update timestamp |
| `lst_updt_user_id` | varchar(34) | NULL | Last update user |

### Primary Key
`(risk_assess_config_event_id)`

### Foreign Key
References `risk_assess_sta_trk(risk_assess_id, risk_assess_vsn_no, risk_assess_sta_cd)`

---

# PART 3: RISK FRAMEWORK TABLES

## 3.1 `risk_assess_ctgy` (Risk Categories)

**Purpose:** Stores risk categories within an assessment. CRR has 5 standard categories.

### Table Structure

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `risk_assess_id` | integer | NOT NULL | Parent assessment ID |
| `risk_assess_vsn_no` | integer | NOT NULL | Parent assessment version |
| `risk_ctgy_id` | integer | NOT NULL | Category identifier |
| `risk_ctgy_nm` | varchar(100) | NOT NULL | Category name |
| `risk_assess_ctgy_ds` | varchar(500) | NULL | Category description |
| `creat_ts` | timestamp(6) | NOT NULL | Creation timestamp |
| `creat_user_id` | varchar(34) | NOT NULL | Created by user |
| `lst_updt_ts` | timestamp(6) | NULL | Last update timestamp |
| `lst_updt_user_id` | varchar(34) | NULL | Last update user |

### Primary Key
`(risk_assess_id, risk_assess_vsn_no, risk_ctgy_id)`

### Standard Categories

| risk_ctgy_id | risk_ctgy_nm |
|-------------|--------------|
| 1 | Customer Risk |
| 2 | Geographic Risk |
| 3 | Transaction Risk |
| 4 | Products & Services Risk |
| 5 | ARFs & HROs |

---

## 3.2 `risk_assess_ctgy_elem` (Risk Elements)

**Purpose:** Stores risk elements within each category.

### Table Structure

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `risk_assess_id` | integer | NOT NULL | Parent assessment ID |
| `risk_assess_vsn_no` | integer | NOT NULL | Parent assessment version |
| `iso_alpha2_ctry_cd` | varchar(2) | NOT NULL | Market scope |
| `risk_elem_id` | integer | NOT NULL | Element identifier |
| `risk_ctgy_id` | integer | NOT NULL | Parent category ID |
| `risk_elem_nm` | varchar(100) | NOT NULL | Element name |
| `risk_assess_elem_ds` | varchar(500) | NULL | Element description |
| `tm_base_in` | boolean | NOT NULL | Is time-based evaluation enabled? |
| `min_max_mult_eval_cd` | varchar(3) | NOT NULL | MIN or MAX evaluation code |
| `prohibited_in` | boolean | NOT NULL | Is prohibited flag enabled? |
| `tm_base_run_intvl_day_ct` | integer | NULL | Time interval in days |
| `creat_ts` | timestamp(6) | NOT NULL | Creation timestamp |
| `creat_user_id` | varchar(34) | NOT NULL | Created by user |
| `lst_updt_ts` | timestamp(6) | NULL | Last update timestamp |
| `lst_updt_user_id` | varchar(34) | NULL | Last update user |

### Primary Key
`(risk_assess_id, risk_assess_vsn_no, risk_elem_id)`

---

## 3.3 `rule_set` (Rulesets)

**Purpose:** Stores rulesets within each risk element.

### Table Structure

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `risk_assess_id` | integer | NOT NULL | Parent assessment ID |
| `risk_assess_vsn_no` | integer | NOT NULL | Parent assessment version |
| `iso_alpha2_ctry_cd` | varchar(2) | NOT NULL | Market scope |
| `risk_elem_id` | integer | NOT NULL | Parent element ID |
| `rule_set_id` | integer | NOT NULL | Ruleset identifier |
| `rule_set_ds` | varchar(500) | NULL | Ruleset description |
| `mult_da_pt_id` | integer | NULL | Multiplier datapoint ID (if FA-based) |
| `dflt_mult_no` | decimal | NOT NULL | Default multiplier value |
| `dflt_wt_no` | decimal | NOT NULL | Default weighting |
| `ruleset_mult_no` | decimal | NULL | Ruleset multiplier |
| `mult_optn_id` | integer | NULL | Multiplier option ID |
| `rule_set_cond_tx` | varchar(1000) | NULL | Condition expression text |
| `creat_ts` | timestamp(6) | NOT NULL | Creation timestamp |
| `creat_user_id` | varchar(34) | NOT NULL | Created by user |
| `lst_updt_ts` | timestamp(6) | NULL | Last update timestamp |
| `lst_updt_user_id` | varchar(34) | NULL | Last update user |

### Primary Key
`(risk_assess_id, risk_assess_vsn_no, risk_elem_id, rule_set_id)`

---

## 3.4 `risk_rule` (Rules)

**Purpose:** Stores individual rules within rulesets. **This table links to Assets.**

### Table Structure

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `risk_assess_id` | integer | NOT NULL | Parent assessment ID |
| `risk_assess_vsn_no` | integer | NOT NULL | Parent assessment version |
| `iso_alpha2_ctry_cd` | varchar(2) | NOT NULL | Market scope |
| `risk_elem_id` | integer | NOT NULL | Parent element ID |
| `rule_set_id` | integer | NOT NULL | Parent ruleset ID |
| `rule_id` | integer | NOT NULL | Rule identifier |
| `rule_seq_no` | smallint | NOT NULL | Rule sequence number |
| `da_pt_id` | integer | NOT NULL | Datapoint ID to evaluate |
| `da_opr_id` | integer | NOT NULL | Operator ID (IN, NOT IN, EQUALS, etc.) |
| `da_pt_val` | varchar(500) | NULL | Static value (if not using asset) |
| `refer_da_asset_id` | integer | NULL | **Asset ID (FK to refer_da_asset)** |
| `refer_da_asset_vsn_no` | smallint | NULL | **Asset version number** |
| `creat_ts` | timestamp(6) | NOT NULL | Creation timestamp |
| `creat_user_id` | varchar(34) | NOT NULL | Created by user |
| `lst_updt_ts` | timestamp(6) | NULL | Last update timestamp |
| `lst_updt_user_id` | varchar(34) | NULL | Last update user |

### Primary Key
`(risk_assess_id, risk_assess_vsn_no, risk_elem_id, rule_set_id, rule_id)`

### Foreign Key to Asset
`(refer_da_asset_id, refer_da_asset_vsn_no)` → `refer_da_asset(refer_da_asset_id, refer_da_asset_vsn_no)`

### Example Data

**Rule using Asset A1, Version 1:**
```
risk_assess_id=1, risk_assess_vsn_no=1, rule_id=1
da_pt_id=3, da_opr_id=2, da_pt_val=NULL
refer_da_asset_id=1, refer_da_asset_vsn_no=1
```

**Rule using Asset A1, Version 2 (after edit):**
```
risk_assess_id=2, risk_assess_vsn_no=1, rule_id=1
da_pt_id=3, da_opr_id=2, da_pt_val=NULL
refer_da_asset_id=1, refer_da_asset_vsn_no=2
```

---

## 3.5 `ruleset_risk_mthd` (Ruleset Risk Methods/Applicability)

**Purpose:** Defines which customer types a ruleset applies to.

### Table Structure

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `risk_assess_id` | integer | NOT NULL | Parent assessment ID |
| `risk_assess_vsn_no` | integer | NOT NULL | Parent assessment version |
| `iso_alpha2_ctry_cd` | varchar(2) | NOT NULL | Market scope |
| `risk_elem_id` | integer | NOT NULL | Parent element ID |
| `rule_set_id` | integer | NOT NULL | Parent ruleset ID |
| `risk_mthd_cd` | varchar(2) | NOT NULL | Risk method/applicability code |
| `creat_ts` | timestamp(6) | NOT NULL | Creation timestamp |
| `creat_user_id` | varchar(34) | NULL | Created by user |
| `lst_updt_ts` | timestamp(6) | NULL | Last update timestamp |
| `lst_updt_user_id` | varchar(34) | NULL | Last update user |

### Primary Key
`(risk_assess_id, risk_assess_vsn_no, risk_elem_id, rule_set_id, risk_mthd_cd)`

### Risk Method Codes

| Code | Meaning |
|------|---------|
| XX | Enterprise/All |
| I | Individuals |
| E | Entities |
| M | Intermediaries (Merchants) |

### Example Data

```
risk_assess_id | rule_set_id | risk_mthd_cd
---------------|-------------|-------------
1              | 1           | XX
1              | 1           | I
1              | 1           | E
1              | 1           | M
```

---

# PART 4: ASSET MANAGER TABLES

## 4.1 `refer_da_asset_srce` (Reference Data Source/Tables)

**Purpose:** Stores the master reference data tables (e.g., Countries, Industries, Products). Assets are linked to these tables for validation.

### Table Structure

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `refer_da_asset_srce_id` | integer | NOT NULL | Unique source ID |
| `refer_da_srce_nm` | varchar(30) | NOT NULL | Source table name |
| `refer_da_srce_disp_nm` | varchar(50) | NOT NULL | Display name for UI |
| `refer_da_srce_ds` | varchar(200) | NOT NULL | Description |
| `refer_da_srce_attr_nm` | varchar(30) | NOT NULL | Attribute name in source |

### Primary Key
`(refer_da_asset_srce_id)`

### Example Data

| refer_da_asset_srce_id | refer_da_srce_nm | refer_da_srce_disp_nm | refer_da_srce_ds |
|------------------------|------------------|----------------------|------------------|
| 1 | COUNTRIES | Countries | List of all countries |
| 2 | INDUSTRIES | Industries | Industry classifications |
| 3 | PRODUCTS | Products | Product types |
| 4 | OCCUPATIONS | Occupations | Occupation types |

---

## 4.2 `refer_da_asset` (Assets - Main Table)

**Purpose:** Stores asset definitions. Each asset has an ID and version. Asset data is stored as JSON.

### Table Structure

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `refer_da_asset_id` | integer | NOT NULL | Unique asset ID |
| `refer_da_asset_vsn_no` | smallint | NOT NULL | Version number |
| `refer_da_asset_nm` | varchar(30) | NOT NULL | Asset name |
| `refer_asset_da` | json | NOT NULL | Asset data (values stored as JSON) |
| `refer_asset_da_hash_tx` | varchar(4000) | NOT NULL | Hash of asset data (for change detection) |
| `refer_da_asset_srce_id` | integer | NOT NULL | FK to reference table |
| `refer_da_asset_ds` | varchar(200) | NULL | Asset description |
| `creat_user_id` | varchar(34) | NOT NULL | Created by user |
| `creat_ts` | timestamp(6) | NOT NULL | Creation timestamp |
| `lst_updt_user_id` | varchar(34) | NULL | Last update user |
| `lst_updt_ts` | timestamp(6) | NULL | Last update timestamp |

### Primary Key
`(refer_da_asset_id, refer_da_asset_vsn_no)`

### Foreign Key
`(refer_da_asset_srce_id)` → `refer_da_asset_srce(refer_da_asset_srce_id)`

### JSON Data Structure

```json
{
  "list": ["Iran", "North Korea", "Syria"],
  "filename": "High_Risk_Countries"
}
```

### Example Data

**Asset Version 1:**
```
refer_da_asset_id=1, refer_da_asset_vsn_no=1
refer_da_asset_nm='Asset 1'
refer_asset_da='{"list":["1","2"],"filename":"Asset1"}'
refer_asset_da_hash_tx='878278631'
refer_da_asset_srce_id=1
```

**Asset Version 2 (after edit with new value added):**
```
refer_da_asset_id=1, refer_da_asset_vsn_no=2
refer_da_asset_nm='Asset 1'
refer_asset_da='{"list":["1","2","3"],"filename":"Asset1"}'
refer_asset_da_hash_tx='988278631'
refer_da_asset_srce_id=1
```

---

## 4.3 `refer_da_asset_sta_hist` (Asset Status History)

**Purpose:** Tracks the lifecycle status of each asset version.

### Table Structure

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `refer_da_asset_id` | integer | NOT NULL | Asset ID |
| `refer_da_asset_vsn_no` | smallint | NOT NULL | Asset version |
| `sta_updt_ts` | timestamp(6) | NOT NULL | Status update timestamp |
| `refer_da_asset_sta_id` | varchar(30) | NOT NULL | Status code |
| `sta_updt_cmnt_tx` | varchar(500) | NULL | Status comment |
| `creat_user_id` | varchar(34) | NOT NULL | User who updated status |

### Primary Key
`(refer_da_asset_id, refer_da_asset_vsn_no, sta_updt_ts)`

### Status Values

| Status | Description |
|--------|-------------|
| **DRAFT** | Asset created but not linked to any rule |
| **SANDBOX** | Asset linked to rule in sandbox |
| **PRODUCTION** | Asset promoted to production |
| **ARCHIVE** | Previous version archived after new version promoted |
| **DELETE** | Asset marked for deletion (soft delete) |

### Example Data - Full Asset Lifecycle

```
refer_da_asset_id | refer_da_asset_vsn_no | sta_updt_ts              | refer_da_asset_sta_id
------------------|----------------------|--------------------------|----------------------
1                 | 1                    | 2026-01-15T09:52:26      | DRAFT
1                 | 1                    | 2026-01-15T10:52:26      | SANDBOX
1                 | 1                    | 2026-01-15T11:52:26      | PRODUCTION
1                 | 2                    | 2026-01-15T13:52:26      | SANDBOX
1                 | 2                    | 2026-01-15T14:52:26      | PRODUCTION
1                 | 1                    | 2026-01-15T14:52:26      | ARCHIVE
```

---

## 4.4 `refer_da_asset_srce_da_pt` (Datapoint to Reference Table Mapping)

**Purpose:** Maps which datapoints can use which reference tables. Used to filter asset dropdown in rule creation.

### Table Structure

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `da_pt_id` | integer | NOT NULL | Datapoint ID |
| `refer_da_asset_srce_id` | integer | NOT NULL | Reference table ID |

### Primary Key
`(da_pt_id)`

### Foreign Key
`(refer_da_asset_srce_id)` → `refer_da_asset_srce(refer_da_asset_srce_id)`

### Purpose
When user selects a datapoint in rule creation, system looks up this table to find the corresponding reference table, then filters assets to show only those linked to that reference table.

---

## 4.5 `refer_da_asset_scope_mapping` (Asset to Market Mapping)

**Purpose:** Tracks which markets/scopes an asset is linked to.

### Table Structure

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `refer_da_asset_id` | integer | NOT NULL | Asset ID |
| `iso_alpha2_ctry_cd` | varchar(2) | NOT NULL | Market scope code |

### Primary Key
`(refer_da_asset_id, iso_alpha2_ctry_cd)`

### Example Data

```
refer_da_asset_id | iso_alpha2_ctry_cd
------------------|-------------------
1                 | XX  (Enterprise)
1                 | IN  (India)
1                 | CN  (China)
```

### Usage
- When an asset is linked to a rule in a scope, an entry is added here
- Used to track cross-market asset usage
- Helps determine if asset is "shared" (multiple scopes)

---

# PART 5: FUNDAMENTAL ASSESSMENT (FA) TABLES

## 5.1 FA Tables Overview

The Fundamental Assessment module has 22 tables organized into the following groups:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        FUNDAMENTAL ASSESSMENT TABLE HIERARCHY                           │
└─────────────────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │  ira_gate_type  │
                              │   (6 Gates)     │
                              └────────┬────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │    ira_gate     │
                              │ (Gate Instances)│
                              └────────┬────────┘
                                       │
         ┌─────────────┬───────────────┼───────────────┬─────────────┬─────────────┐
         ▼             ▼               ▼               ▼             ▼             ▼
   ┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐
   │ ira_ctry │  │ira_indus │  │  ira_prod    │  │ira_occpt│  │ira_acq_  │  │ira_pty_  │
   │(Countries│  │(Industry)│  │  (Product)   │  │(Occupat)│  │  chan    │  │  type    │
   │   GR)    │  │   (IR)   │  │    (PRR)     │  │ (OCCP)  │  │  (ACR)   │  │  (SR)    │
   └──────────┘  └──────────┘  └──────────────┘  └─────────┘  └──────────┘  └──────────┘
         │             │               │               │             │             │
         └─────────────┴───────────────┼───────────────┴─────────────┴─────────────┘
                                       ▼
                            ┌─────────────────────┐
                            │  inhrnt_risk_assess │
                            │  (FA Assessments)   │
                            └──────────┬──────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
            ┌──────────────┐  ┌───────────────┐  ┌────────────────────┐
            │ira_ques_resp │  │assess_doc_    │  │ira_risk_score_ovrrd│
            │(Q&A Answers) │  │   attach      │  │   (Overrides)      │
            └──────────────┘  └───────────────┘  └────────────────────┘
```

---

## 5.2 Gate Type & Gate Tables

### `ira_gate_type` (FA Gate Types - The 6 Gates)

**Purpose:** Defines the 6 Fundamental Assessment gate types.

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `gate_type_cd` | varchar(6) | NOT NULL | Gate type code (PK) |
| `gate_type_nm` | varchar(35) | NOT NULL | Gate type name |
| `gate_type_ds` | varchar(500) | NOT NULL | Gate description |

**The 6 FA Gates:**

| gate_type_cd | gate_type_nm | Description |
|--------------|--------------|-------------|
| **GR** | Geography | Country/Geographic risk |
| **IR** | Industry | Industry/Sector risk |
| **PRR** | Product | Product type risk |
| **OCCP** | Occupation | Occupation risk |
| **ACR** | Acquisition Channel | How customer was acquired |
| **SR** | Structure | Entity structure risk |

---

### `ira_gate` (FA Gate Instances)

**Purpose:** Maps gate types to specific gate codes (attributes).

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `gate_type_cd` | varchar(6) | NOT NULL | Gate type code (FK) |
| `gate_cd` | varchar(10) | NOT NULL | Specific gate code |

**Primary Key:** `(gate_type_cd, gate_cd)`

**Foreign Key:** `gate_type_cd` → `ira_gate_type(gate_type_cd)`

---

## 5.3 Attribute Tables (One Per Gate)

### `ira_ctry` (Countries - Geography Gate)

**Purpose:** Stores country attributes for Geography FA gate.

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `ira_ctry_cd` | varchar(2) | NOT NULL | ISO 2-letter country code (PK) |
| `ctry_full_nm` | varchar(70) | NOT NULL | Full country name |
| `ira_unify_nat_geo_rgn_cd` | varchar(3) | NULL | UN geographic region code |
| `ira_geo_div_cd` | varchar(4) | NULL | Geographic division code |
| `act_ctry_in` | boolean | NOT NULL | Is country active? |
| `strng_reg_envir_in` | boolean | NOT NULL | Strong regulatory environment? |
| `creat_user_id` | varchar(34) | NOT NULL | Created by user |
| `creat_ts` | timestamp(6) | NOT NULL | Creation timestamp |
| `lst_updt_ts` | timestamp(6) | NULL | Last update timestamp |
| `lst_updt_user_id` | varchar(34) | NULL | Last update user |

**Supporting Tables:**
- `ira_geo_div` - Geographic divisions
- `ira_unify_nat_geo_rgn` - UN geographic regions

---

### `ira_indus` (Industries - Industry Gate)

**Purpose:** Stores industry attributes for Industry FA gate.

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `ira_indus_cd` | varchar(10) | NOT NULL | Industry code (PK) |
| `indus_nm` | varchar(50) | NOT NULL | Industry name |
| `cash_intensive_bus_in` | boolean | NOT NULL | Is this a cash-intensive business? |
| `ira_indus_type_cd` | varchar(10) | NOT NULL | Industry type code (FK) |
| `creat_user_id` | varchar(34) | NOT NULL | Created by user |
| `creat_ts` | timestamp(6) | NOT NULL | Creation timestamp |
| `lst_updt_ts` | timestamp(6) | NULL | Last update timestamp |
| `lst_updt_user_id` | varchar(34) | NULL | Last update user |

**Supporting Table:** `ira_indus_type` - Industry type categories

---

### `ira_prod` (Products - Product Gate)

**Purpose:** Stores product attributes for Product FA gate.

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `ira_prod_cd` | varchar(10) | NOT NULL | Product code (PK) |
| `prod_nm` | varchar(80) | NOT NULL | Product name |
| `ira_prod_type_cd` | varchar(10) | NOT NULL | Product type code (FK) |
| `iso_alpha3_curr_cd` | varchar(3) | NOT NULL | Currency code |
| `stat_in` | boolean | NOT NULL | Status indicator |
| `creat_user_id` | varchar(34) | NOT NULL | Created by user |
| `creat_ts` | timestamp(6) | NOT NULL | Creation timestamp |
| `lst_updt_ts` | timestamp(6) | NULL | Last update timestamp |
| `lst_updt_user_id` | varchar(34) | NULL | Last update user |

**Supporting Tables:**
- `ira_prod_type` - Product type categories
- `curr` - Currency reference

---

### `ira_occpt` (Occupations - Occupation Gate)

**Purpose:** Stores occupation attributes for Occupation FA gate.

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `ira_occpt_cd` | varchar(10) | NOT NULL | Occupation code (PK) |
| `occpt_nm` | varchar(50) | NOT NULL | Occupation name |
| `creat_user_id` | varchar(34) | NOT NULL | Created by user |
| `creat_ts` | timestamp(6) | NOT NULL | Creation timestamp |
| `lst_updt_ts` | timestamp(6) | NULL | Last update timestamp |
| `lst_updt_user_id` | varchar(34) | NULL | Last update user |

---

### `ira_acq_chan` (Acquisition Channels - Acquisition Channel Gate)

**Purpose:** Stores acquisition channel attributes.

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `ira_acq_chan_cd` | varchar(6) | NOT NULL | Acquisition channel code (PK) |
| `parnt_ira_acq_chan_cd` | varchar(6) | NULL | Parent channel (for hierarchy) |
| `chan_nm` | varchar(30) | NOT NULL | Channel name |
| `creat_user_id` | varchar(34) | NOT NULL | Created by user |
| `creat_ts` | timestamp(6) | NOT NULL | Creation timestamp |
| `lst_updt_ts` | timestamp(6) | NULL | Last update timestamp |
| `lst_updt_user_id` | varchar(34) | NULL | Last update user |

---

### `ira_pty_type` (Party/Entity Types - Structure Gate)

**Purpose:** Stores party/entity type attributes for Structure FA gate.

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `ira_pty_type_cd` | varchar(6) | NOT NULL | Party type code (PK) |
| `pty_type_nm` | varchar(60) | NOT NULL | Party type name |
| `parnt_ira_pty_type_cd` | varchar(6) | NOT NULL | Parent type (for hierarchy) |
| `ira_type_grp_cd` | varchar(6) | NOT NULL | Type group code (FK) |
| `creat_user_id` | varchar(34) | NOT NULL | Created by user |
| `creat_ts` | timestamp(6) | NOT NULL | Creation timestamp |
| `lst_updt_ts` | timestamp(6) | NULL | Last update timestamp |
| `lst_updt_user_id` | varchar(34) | NULL | Last update user |

**Supporting Tables:**
- `ira_pty_type_grp` - Party type groups
- `ira_pty_type_grp_ctgy` - Party type group categories

---

## 5.4 Question & Assessment Tables

### `ira_sect` (FA Sections)

**Purpose:** Sections within each gate for organizing questions.

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `gate_type_cd` | varchar(6) | NOT NULL | Gate type code (FK) |
| `ira_sect_cd` | varchar(4) | NOT NULL | Section code |
| `sect_nm` | varchar(100) | NOT NULL | Section name |
| `sect_ord_no` | smallint | NOT NULL | Section display order |

**Primary Key:** `(gate_type_cd, ira_sect_cd)`

---

### `ques_risk_ctgy` (Question Risk Categories)

**Purpose:** Categories to classify questions by risk.

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `ques_risk_ctgy_cd` | varchar(4) | NOT NULL | Risk category code (PK) |
| `ques_risk_ctgy_nm` | varchar(40) | NOT NULL | Risk category name |

---

### `assess_ques` (Assessment Questions)

**Purpose:** Stores the 10 questions for each FA gate. Questions are ranked by priority.

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `assess_ques_id` | smallint | NOT NULL | Question ID (PK) |
| `ira_sect_cd` | varchar(4) | NOT NULL | Section code |
| `gate_type_cd` | varchar(6) | NOT NULL | Gate type code |
| `disp_seq_no` | integer | NOT NULL | Display sequence/rank (1-10) |
| `dflt_ans_cd` | varchar(3) | NOT NULL | Default answer (YES/NO) |
| `ques_risk_ctgy_cd` | varchar(4) | NOT NULL | Risk category code |
| `assess_ques_tx` | varchar(1000) | NOT NULL | Question text |
| `ques_del_in` | boolean | NOT NULL | Is question deleted? |
| `creat_ts` | timestamp(6) | NOT NULL | Creation timestamp |
| `creat_user_id` | varchar(34) | NOT NULL | Created by user |
| `lst_updt_ts` | timestamp(6) | NULL | Last update timestamp |
| `lst_updt_user_id` | varchar(34) | NULL | Last update user |

**Key:** `disp_seq_no` is the rank (1 = lowest priority/score, 10 = highest priority/score)

---

### `assess_sta` (Assessment Status)

**Purpose:** Status codes for FA assessments.

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `assess_sta_cd` | varchar(3) | NOT NULL | Status code (PK) |
| `assess_sta_nm` | varchar(30) | NOT NULL | Status name |

**Status Codes:**
| Code | Name |
|------|------|
| 1 | Draft |
| 2 | Production |
| 3 | Archived |

---

### `inhrnt_risk_assess` (Inherent Risk Assessment - FA Scores)

**Purpose:** Stores the calculated FA scores for each attribute.

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `ira_id` | integer | NOT NULL | Assessment ID (PK) |
| `gate_type_cd` | varchar(6) | NOT NULL | Gate type code |
| `gate_cd` | varchar(10) | NOT NULL | Specific gate/attribute code |
| `assess_sta_cd` | varchar(3) | NOT NULL | Assessment status |
| `assess_ts` | timestamp(6) | NOT NULL | Assessment timestamp |
| `prod_impl_id` | integer | NULL | Production implementation ID |
| `risk_score_calc_no` | integer | NULL | **Calculated risk score (1-10)** |
| `corruption_risk_score_no` | integer | NULL | Corruption risk score |
| `creat_user_id` | varchar(34) | NOT NULL | Created by user |
| `creat_ts` | timestamp(6) | NOT NULL | Creation timestamp |
| `lst_updt_ts` | timestamp(6) | NULL | Last update timestamp |
| `lst_updt_user_id` | varchar(34) | NULL | Last update user |

**Key Field:** `risk_score_calc_no` - This is the FA score (1-10) calculated based on question answers.

---

### `ira_ques_resp` (Question Responses)

**Purpose:** Stores YES/NO answers to questions for each assessment.

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `ira_id` | integer | NOT NULL | Assessment ID (FK) |
| `assess_ques_id` | smallint | NOT NULL | Question ID (FK) |
| `assess_ans_cd` | varchar(3) | NOT NULL | Answer (YES/NO) |
| `ans_cmnt_tx` | varchar(1000) | NOT NULL | Justification/comment for answer |

**Primary Key:** `(ira_id, assess_ques_id)`

---

### `assess_doc_attach` (Document Attachments)

**Purpose:** Stores document attachments for question justifications.

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `doc_attach_id` | integer | NOT NULL | Attachment ID (PK) |
| `doc_attach_link_tx` | text | NOT NULL | Document link |
| `creat_user_id` | varchar(34) | NOT NULL | Created by user |
| `creat_ts` | timestamp(6) | NOT NULL | Creation timestamp |
| `ira_id` | integer | NOT NULL | Assessment ID |
| `assess_ques_id` | smallint | NOT NULL | Question ID |

---

## 5.5 Override Tables

### `ira_risk_score_ovrrd` (FA Score Overrides)

**Purpose:** Stores market-specific override scores for FA attributes.

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `gate_type_cd` | varchar(6) | NOT NULL | Gate type code |
| `gate_cd` | varchar(10) | NOT NULL | Specific gate/attribute code |
| `ira_ctry_cd` | varchar(2) | NOT NULL | Market code for override |
| `assess_sta_cd` | varchar(3) | NOT NULL | Assessment status |
| `prod_impl_id` | integer | NULL | Production implementation ID |
| `risk_score_ovrrd_no` | integer | NOT NULL | **Override score (1-10)** |
| `creat_user_id` | varchar(34) | NOT NULL | Created by user |
| `creat_ts` | timestamp(6) | NOT NULL | Creation timestamp |
| `lst_updt_ts` | timestamp(6) | NULL | Last update timestamp |
| `lst_updt_user_id` | varchar(34) | NULL | Last update user |

**Primary Key:** `(gate_type_cd, gate_cd, ira_ctry_cd)`

**Example:**
```
gate_type_cd='IR', gate_cd='CASINO', ira_ctry_cd='IN', risk_score_ovrrd_no=8
(India overrides Casino industry score to 8 instead of Enterprise default)
```

---

## 5.6 Status Tracking Tables

### `assess_sta_trk` (Assessment Status Tracking)

**Purpose:** Tracks when FA assessments were promoted to production.

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `prod_impl_id` | integer | NOT NULL | Production implementation ID (PK) |
| `creat_user_id` | varchar(34) | NOT NULL | User who promoted |
| `creat_ts` | timestamp(6) | NOT NULL | Promotion timestamp |

---

## 5.7 Complete FA Table List

| # | Table Name | Purpose | Count |
|---|------------|---------|-------|
| 1 | `ira_gate_type` | 6 FA gate types | 6 rows |
| 2 | `ira_gate` | Gate instances (attribute mapping) | Many |
| 3 | `ira_ctry` | Countries (Geography) | ~200 |
| 4 | `ira_geo_div` | Geographic divisions | Reference |
| 5 | `ira_unify_nat_geo_rgn` | UN regions | Reference |
| 6 | `ira_indus` | Industries | Many |
| 7 | `ira_indus_type` | Industry types | Reference |
| 8 | `ira_prod` | Products | Many |
| 9 | `ira_prod_type` | Product types | Reference |
| 10 | `curr` | Currencies | Reference |
| 11 | `ira_occpt` | Occupations | Many |
| 12 | `ira_acq_chan` | Acquisition channels | Many |
| 13 | `ira_pty_type` | Party/entity types | Many |
| 14 | `ira_pty_type_grp` | Party type groups | Reference |
| 15 | `ira_pty_type_grp_ctgy` | Party type categories | Reference |
| 16 | `ira_sect` | FA sections | ~6 per gate |
| 17 | `ques_risk_ctgy` | Question risk categories | Reference |
| 18 | `assess_ques` | Assessment questions | 10 per gate |
| 19 | `assess_sta` | Assessment status | 3 values |
| 20 | `inhrnt_risk_assess` | Calculated FA scores | Many |
| 21 | `ira_ques_resp` | Question answers | Many |
| 22 | `assess_doc_attach` | Document attachments | Many |
| 23 | `ira_risk_score_ovrrd` | Market overrides | Many |
| 24 | `assess_sta_trk` | Production tracking | Audit |

---

# PART 6: USER MANAGEMENT

## 5.1 `user` (User Table)

**Purpose:** Stores user information for the CRR system.

### Table Structure

| Column Name | Data Type | Nullable | Description |
|-------------|-----------|----------|-------------|
| `emp_cntrct_no` | varchar(11) | NOT NULL | Employee contract number (PK) |
| `user_full_nm` | varchar(180) | NOT NULL | Full name |
| `user_first_nm` | varchar(60) | NOT NULL | First name |
| `user_lst_nm` | varchar(60) | NOT NULL | Last name |
| `ads_id` | varchar(50) | NOT NULL | Active Directory ID |
| `email_ad_tx` | varchar(255) | NOT NULL | Email address |
| `creat_ts` | timestamp(6) | NOT NULL | Creation timestamp |
| `creat_user_id` | varchar(34) | NOT NULL | Created by user |
| `lst_updt_ts` | timestamp(6) | NULL | Last update timestamp |
| `lst_updt_user_id` | varchar(34) | NULL | Last update user |

### Primary Key
`(emp_cntrct_no)`

---

# PART 6: DATA FLOW SCENARIOS

## 6.1 Scenario: First Enterprise Assessment with New Asset

```
Step 1: User creates Enterprise assessment
   → risk_assess: INSERT (risk_assess_id=1, vsn=1, scope=XX)
   → risk_assess_sta_trk: INSERT (status=1/WORKING)

Step 2: User creates asset
   → refer_da_asset: INSERT (asset_id=1, vsn=1)
   → refer_da_asset_sta_hist: INSERT (status=DRAFT)

Step 3: User creates rule and links asset
   → risk_assess_ctgy: INSERT (category)
   → risk_assess_ctgy_elem: INSERT (element)
   → rule_set: INSERT (ruleset)
   → risk_rule: INSERT (refer_da_asset_id=1, refer_da_asset_vsn_no=1)
   → refer_da_asset_sta_hist: INSERT (status=SANDBOX)
   → refer_da_asset_scope_mapping: INSERT (asset_id=1, scope=XX)

Step 4: User submits and merges to production
   → risk_assess_sta_trk: INSERT (status=3/SKIPPED, 5/APPROVAL1, 6/APPROVAL2, 8/MERGED)
   → risk_assess: UPDATE (hist_ts set, merge IDs set)
   → refer_da_asset_sta_hist: INSERT (status=PRODUCTION)
```

## 6.2 Scenario: Edit Asset in Existing Assessment

```
Step 1: User creates new sandbox (assessment version)
   → risk_assess: INSERT (risk_assess_id=2, vsn=1, scope=XX)
   → risk_rule: COPY from production with same asset references

Step 2: User edits asset
   → refer_da_asset: INSERT (asset_id=1, vsn=2, new data)
   → refer_da_asset_sta_hist: INSERT (asset_id=1, vsn=2, status=SANDBOX)

Step 3: User updates rule to use new asset version
   → risk_rule: UPDATE (refer_da_asset_vsn_no=2)

Step 4: User merges to production
   → risk_assess: UPDATE (new version active)
   → refer_da_asset_sta_hist: INSERT (asset_id=1, vsn=2, status=PRODUCTION)
   → refer_da_asset_sta_hist: INSERT (asset_id=1, vsn=1, status=ARCHIVE)
```

---

# PART 7: KEY RELATIONSHIPS SUMMARY

## 7.1 Table Relationships Diagram

```
user ────────────────┐
                     │ creat_user_id / lst_updt_user_id (used in all tables)
                     │
                     ▼
risk_assess ◄────────┤ (1:N)
     │               │
     │ (1:N)         │
     ▼               │
risk_assess_sta_trk ─┤
     │               │
     │ (1:N)         │
     ▼               │
risk_assess_ctgy ────┤
     │               │
     │ (1:N)         │
     ▼               │
risk_assess_ctgy_elem┤
     │               │
     │ (1:N)         │
     ▼               │
rule_set ────────────┤
     │               │
     │ (1:N)         │
     ▼               │
risk_rule ───────────┤
     │               │
     │ (N:1)         │
     ▼               │
refer_da_asset ──────┤
     │               │
     │ (1:N)         │
     ▼               │
refer_da_asset_sta_hist
     │
     │ (N:1)
     ▼
refer_da_asset_srce ◄── refer_da_asset_srce_da_pt (N:1)
```

---

# PART 8: OPEN QUESTIONS & ACTION ITEMS

From the source documents, the following action items were noted:

| # | Item | Status |
|---|------|--------|
| 1 | Remove `crnt_refer_da_asset_sta_id` from `crnt_refer_da_asset` table | Pending |
| 2 | Check for `merge_prod_risk_assess_id` and `merge_prod_risk_assess_vsn_no` usage | Clarified |
| 3 | How to show and notify user for assets used in other markets in an XX assessment | Design Decision Needed |
| 4 | Add DELETE status for asset | ✅ Added in status values |

---

*This data model documentation is based on analysis of CSV data flows, DDL files, and the Data Dictionary from the CRR project.*
