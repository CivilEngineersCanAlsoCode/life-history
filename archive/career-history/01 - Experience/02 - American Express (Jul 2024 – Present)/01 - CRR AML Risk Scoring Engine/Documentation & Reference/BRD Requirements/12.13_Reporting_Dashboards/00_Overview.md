# BRD 12.13 — Reporting / Dashboards

## Status
Not Built

## Target Timeline
Core Reporting Team

## Bead Reference
career-context-3z5

## Business Requirement
Generate reports/dashboards.

## Purpose
Reports with CRR framework data and risk distribution.

## Expected Outcome
Comprehensive review and analysis for regulatory context.

## Confirmed Details (from Coaching + CRR Reporting Excel)

### CRR-Specific Reports (R9-R17):
| Report | Description | Maps to BRD |
|--------|-------------|-------------|
| R9 | Market-level Production vs Sandbox risk distribution comparison | 12.9.5, 12.13.3 |
| R10 | Product-wise Production vs Sandbox comparison | 12.9.5, 12.13.3 |
| R11 | Data quality report (fill rates, data freshness) | 12.17.3, 12.18.1 |
| R12 | Risk element trigger details (which rules fired for which customers) | 12.13.1 |
| R13 | FA/Centralized Lists/Notable Lists changes (who, when, what changed) | 12.13.2, 12.7 |
| R14 | Audit trail for all risk point changes per customer | 12.7, 12.15.1 |
| R15 | Implementation tracker (sandbox status, approval pipeline) | 12.13.1 |
| R16 | Scoring matrix report (complete framework snapshot) | 12.13.1 |
| R17 | Raw data extract for downstream consumption | 12.17.4 |

### Architecture:
- **GCIP** = source of truth for CRR data and framework
- **LUMI** = reporting/analytics platform for additional stakeholders
- Data flows: GCIP → BigQuery → LUMI for reporting consumption
- 48 metrics defined across CRR and DAM ownership

### Key Insight:
- R9/R10 are sandbox simulation result reports — partially covered by 12.9 (sandbox analysis UI)
- R11 data quality is a cross-cutting concern spanning 12.17 (Data) and 12.18 (Performance)
- Reporting is owned by a separate Core Reporting Team, not the CRR product team directly

## Sub-Requirements

| Sub-Req | Title | Status | Coaching Notes |
|---------|-------|--------|----------------|
| 12.13.1 | Framework Scoring Matrix Report | Not Built | Maps to R12, R15, R16 — framework snapshot + trigger details + implementation tracker |
| 12.13.2 | Reference Data Report | Not Built | Maps to R13 — FA/Lists/Notable Lists changes with audit trail |
| 12.13.3 | Risk Distribution Dashboard | Not Built | Maps to R9, R10 — Market/Product-wise risk distribution comparison |
| 12.13.4 | Download Capability | Not Built | Excel/PDF download for all reports — cross-ref with 12.14.3 |
| 12.13.5 | Permission-Based Access | Not Built | Depends on 12.21 (IAM) |
