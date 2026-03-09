# CRR COMPLETE TABLE SUMMARY

## Purpose
This document provides a consolidated summary of ALL tables in the CRR system, organized by module.

---

# QUICK REFERENCE: ALL TABLES BY MODULE

## Module 1: CRR Core / Risk Assessment (19 Tables)

| # | Table Name | Physical Name | Purpose |
|---|------------|---------------|---------|
| 1 | Risk Assessment | `risk_assess` | Main sandbox/assessment container |
| 2 | Risk Assessment Status | `risk_assess_sta` | Status master (WORKING, SUBMITTED, etc.) |
| 3 | Risk Assessment Status Tracker | `risk_assess_sta_trk` | Status history per assessment |
| 4 | Risk Assessment Configuration Event | `risk_assess_config_event` | Audit events |
| 5 | Risk Assessment Category | `risk_assess_ctgy` | 5 Risk Categories |
| 6 | Risk Assessment Category Element | `risk_assess_ctgy_elem` | Risk Elements under categories |
| 7 | Rule Set | `rule_set` | Rulesets under elements |
| 8 | Risk Rule | `risk_rule` | Individual rules |
| 9 | Ruleset Risk Method | `ruleset_risk_mthd` | Applicability (Entities/Individuals/Intermediaries) |
| 10 | Risk Method | `risk_mthd` | Risk method master |
| 11 | Data Point | `da_pt` | Customer data fields for rules |
| 12 | Data Point Type | `da_pt_type` | Datapoint type (Lookup, String, etc.) |
| 13 | Data Point Group | `da_pt_grp` | Grouping of datapoints |
| 14 | Data Operator | `da_opr` | Operators (IN, EQUALS, etc.) |
| 15 | Evaluation Function | `eval_func` | Functions for evaluating rules |
| 16 | Multiplier Option | `mult_optn` | Multiplier types (Value, FA) |
| 17 | Risk Score Threshold Configuration | `risk_score_threshold_config` | Risk bucket thresholds (Low/Medium/High/Prohibited) |
| 18 | Time Based Element Execution Log | `tm_base_elem_exec_log` | Logs for time-based rule execution |
| 19 | Country | `ctry` | Country reference data |
| 20 | User | `user` | System users |

---

## Module 2: Asset Manager (6 Tables)

| # | Table Name | Physical Name | Purpose |
|---|------------|---------------|---------|
| 1 | Reference Data Asset Source | `refer_da_asset_srce` | Reference tables (Countries, Industries, etc.) |
| 2 | Reference Data Asset | `refer_da_asset` | Asset definitions with versioning |
| 3 | Reference Data Asset Status History | `refer_da_asset_sta_hist` | Asset lifecycle (DRAFT→SANDBOX→PRODUCTION→ARCHIVE) |
| 4 | Reference Data Asset Source Datapoint | `refer_da_asset_srce_da_pt` | Maps datapoints to reference tables |
| 5 | Reference Data Asset Scope Mapping | `refer_da_asset_scope_mapping` | Maps assets to markets |
| 6* | Asset Tag | `asset_tag` | Asset categorization (NOT IN USE currently) |
| 7* | Asset Access | `asset_access` | User/role access to assets |

*Tables marked with * are mentioned in documentation but may not be active yet.

---

## Module 3: Fundamental Assessment (24 Tables)

### 3.1 Gate & Gate Type Tables

| # | Table Name | Physical Name | Purpose |
|---|------------|---------------|---------|
| 1 | IRA Gate Type | `ira_gate_type` | 6 FA gates (GR, IR, PRR, OCCP, ACR, SR) |
| 2 | IRA Gate | `ira_gate` | Gate instances/attributes |

### 3.2 Geography Gate Tables

| # | Table Name | Physical Name | Purpose |
|---|------------|---------------|---------|
| 3 | IRA Country | `ira_ctry` | Countries |
| 4 | IRA Geographic Division | `ira_geo_div` | Geographic divisions |
| 5 | IRA United Nations Geographic Region | `ira_unify_nat_geo_rgn` | UN regions |

### 3.3 Industry Gate Tables

| # | Table Name | Physical Name | Purpose |
|---|------------|---------------|---------|
| 6 | IRA Industry | `ira_indus` | Industries |
| 7 | IRA Industry Type | `ira_indus_type` | Industry types |

### 3.4 Product Gate Tables

| # | Table Name | Physical Name | Purpose |
|---|------------|---------------|---------|
| 8 | IRA Product | `ira_prod` | Products |
| 9 | IRA Product Type | `ira_prod_type` | Product types |
| 10 | Currency | `curr` | Currency reference |

### 3.5 Other Gate Tables

| # | Table Name | Physical Name | Purpose |
|---|------------|---------------|---------|
| 11 | IRA Occupation | `ira_occpt` | Occupations |
| 12 | IRA Acquisition Channel | `ira_acq_chan` | Acquisition channels |
| 13 | IRA Party Type | `ira_pty_type` | Entity/Party types (Structure) |
| 14 | IRA Party Type Group | `ira_pty_type_grp` | Party type groups |
| 15 | IRA Party Type Group Category | `ira_pty_type_grp_ctgy` | Party type group categories |

### 3.6 Question & Assessment Tables

| # | Table Name | Physical Name | Purpose |
|---|------------|---------------|---------|
| 16 | IRA Section | `ira_sect` | Sections within gates |
| 17 | Question Risk Category | `ques_risk_ctgy` | Question risk categories |
| 18 | Assessment Question | `assess_ques` | 10 questions per gate |
| 19 | Assessment Status | `assess_sta` | FA Assessment status |
| 20 | Inherent Risk Assessment | `inhrnt_risk_assess` | Calculated FA scores |
| 21 | IRA Question Response | `ira_ques_resp` | YES/NO answers |
| 22 | Assessment Document Attachment | `assess_doc_attach` | Document attachments |

### 3.7 Override & Tracking Tables

| # | Table Name | Physical Name | Purpose |
|---|------------|---------------|---------|
| 23 | IRA Risk Score Override | `ira_risk_score_ovrrd` | Market-specific overrides |
| 24 | Assessment Status Tracker | `assess_sta_trk` | FA production tracking |

---

# TOTAL TABLE COUNT

| Module | Table Count |
|--------|-------------|
| CRR Core / Risk Assessment | 20 |
| Asset Manager | 5-7 |
| Fundamental Assessment | 24 |
| **TOTAL** | **~50 Tables** |

---

# TABLE RELATIONSHIPS SUMMARY

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           CRR SYSTEM TABLE RELATIONSHIPS                         │
└─────────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────────┐
                              │      user        │
                              └────────┬─────────┘
                                       │ (creat_user_id, lst_updt_user_id)
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         ▼                             ▼                             ▼
┌─────────────────┐           ┌─────────────────┐          ┌─────────────────┐
│   risk_assess   │           │ refer_da_asset  │          │inhrnt_risk_assess│
│  (Sandbox/      │           │    (Assets)     │          │   (FA Scores)   │
│   Assessment)   │           └────────┬────────┘          └────────┬────────┘
└────────┬────────┘                    │                            │
         │                             │                            │
         ▼                             │                            ▼
┌─────────────────┐                    │                   ┌─────────────────┐
│risk_assess_ctgy │                    │                   │ira_risk_score_  │
│   (Categories)  │                    │                   │    ovrrd        │
└────────┬────────┘                    │                   │  (Overrides)    │
         │                             │                   └─────────────────┘
         ▼                             │
┌─────────────────┐                    │
│risk_assess_ctgy_│                    │
│      elem       │                    │
│   (Elements)    │                    │
└────────┬────────┘                    │
         │                             │
         ▼                             │
┌─────────────────┐                    │
│    rule_set     │                    │
│   (Rulesets)    │                    │
└────────┬────────┘                    │
         │                             │
         ▼                             │
┌─────────────────┐                    │
│    risk_rule    │◄───────────────────┘
│     (Rules)     │    (refer_da_asset_id, refer_da_asset_vsn_no)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│      da_pt      │
│  (Datapoints)   │
└─────────────────┘
```

---

# KEY COLUMN PATTERNS

## Audit Columns (Present in most tables)

| Column | Type | Purpose |
|--------|------|---------|
| `creat_ts` | timestamp(6) | Creation timestamp |
| `creat_user_id` | varchar(34) | User who created record |
| `lst_updt_ts` | timestamp(6) | Last update timestamp |
| `lst_updt_user_id` | varchar(34) | User who last updated |

## Versioning Columns

| Column | Type | Purpose |
|--------|------|---------|
| `risk_assess_id` | integer | Assessment identifier |
| `risk_assess_vsn_no` | integer | Assessment version (1, 2, 3...) |
| `refer_da_asset_id` | integer | Asset identifier |
| `refer_da_asset_vsn_no` | smallint | Asset version (1, 2, 3...) |

## Scope/Market Column

| Column | Type | Purpose |
|--------|------|---------|
| `iso_alpha2_ctry_cd` | varchar(2) | Market code (XX=Enterprise, IN=India, etc.) |

---

# STATUS CODE REFERENCE

## Assessment Status (`risk_assess_sta_cd`)

| Code | Name | Description |
|------|------|-------------|
| 1 | WORKING | Being configured |
| 2 | SUBMITTED | Submitted for simulation |
| 3 | SKIPPED | Simulation skipped |
| 4 | SIMULATED | Simulation complete |
| 5 | APPROVAL_1 | First approval |
| 6 | APPROVAL_2 | Second approval |
| 7 | REJECTED | Rejected |
| 8 | MERGED_TO_PROD | Promoted to production |

## Asset Status (`refer_da_asset_sta_id`)

| Status | Description |
|--------|-------------|
| DRAFT | Created but not linked |
| SANDBOX | Linked to rule in sandbox |
| PRODUCTION | Live in production |
| ARCHIVE | Previous version, replaced |
| DELETE | Soft deleted |

## FA Assessment Status (`assess_sta_cd`)

| Code | Name |
|------|------|
| 1 | Draft |
| 2 | Production |
| 3 | Archived |

---

# GATE TYPE CODES (FA)

| Code | Name | Attribute Table |
|------|------|-----------------|
| GR | Geography | `ira_ctry` |
| IR | Industry | `ira_indus` |
| PRR | Product | `ira_prod` |
| OCCP | Occupation | `ira_occpt` |
| ACR | Acquisition Channel | `ira_acq_chan` |
| SR | Structure | `ira_pty_type` |

---

# RISK METHOD CODES (Applicability)

| Code | Name | Description |
|------|------|-------------|
| XX | Enterprise/All | Applies to all |
| I | Individuals | Personal accounts |
| E | Entities | Business accounts |
| M | Intermediaries | Merchants |

---

*This summary consolidates all table information from Data Dictionary, DDL files, and user-provided diagram descriptions.*
