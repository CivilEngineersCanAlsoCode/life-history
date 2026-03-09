# BRD 12.17 — Data Considerations

## Status
Not Built

## Target Timeline
26.3

## Bead Reference
career-context-bxf

## Business Requirement
Solve data challenges for CRR integrity.

## Purpose
Ensure data accurate and exhaustive.

## Expected Outcome
High confidence that risk rating reflects true customer risk.

## Coaching Context

### Data Architecture in CRR 2.0:
- **DAM (Data Attribute Manager)** = data ingestion layer; manages data points used by CRR rules
- **GCIP** = CRR application platform (source of truth for framework)
- **LUMI** = reporting/analytics platform for additional stakeholders
- **BigQuery** = data warehouse connecting GCIP → LUMI
- **Cloud SQL** = stores rule configurations in CRR application

### Data Flow:
```
Source Systems → DAM (ingestion) → Rule Execution Team (scoring) → GCIP (results)
                                                                  → BigQuery → LUMI (reporting)
```

### Key Data Concepts from Coaching:
- **Data points** are pre-defined in CRR — users select from existing list, cannot create new ones
- Asset Manager expanded from 5 data points (Cadence) to ALL data points (POA)
- **Time-based flag** on risk elements indicates data that changes monthly (e.g., transaction patterns)
- **3 ratio rule types** (Income Type/Count/Transaction Ratio) have data point combination constraints
- Data quality directly impacts scoring accuracy — CRR Report **R11** tracks data quality metrics

### LUMI Integration:
- LUMI provides reporting access to stakeholders outside GCIP
- Both population data (12.17.4) and framework data (12.17.5) must flow to LUMI
- 48 metrics defined across CRR and DAM ownership in reporting requirements

## Sub-Requirements

| Sub-Req | Title | Status | Coaching Notes |
|---------|-------|--------|----------------|
| 12.17.1 | Data Mapping Resolution | Not Built | DAM handles data mapping; POA solutioning must resolve current mapping issues |
| 12.17.2 | Current Data Usage | Not Built | Asset Manager expanded to all data points in POA; daily delta + monthly batch rescoring |
| 12.17.3 | Data Quality for Calculations | Not Built | Maps to CRR Report R11; fill rates and data freshness tracking |
| 12.17.4 | Full Population Data to LUMI | Not Built | GCIP → BigQuery → LUMI pipeline; account-level granularity with history |
| 12.17.5 | Framework Data to LUMI | Not Built | Framework config + version history must flow to LUMI for audit/analysis |
| 12.17.6 | Legal Hold Data | Not Built | Records excluded from purge must be available for CRR scoring |

## Interview Notes
- All 6 sub-requirements Not Built — Target 26.3
- Data quality is a pre-requisite for 12.19 (AI/ML) — must be solved first
- DAM integration ready in E2 environment; full pipeline Target 26.3
- 48 metrics across CRR/DAM ownership defined in CRR Reporting requirements
