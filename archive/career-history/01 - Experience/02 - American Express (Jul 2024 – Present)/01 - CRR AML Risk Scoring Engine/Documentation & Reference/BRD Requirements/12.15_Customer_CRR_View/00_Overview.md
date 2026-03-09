# BRD 12.15 — Customer Level CRR View / Report

## Status
Not Built

## Target Timeline
2027

## Bead Reference
career-context-xp6

## Business Requirement
Provide customer risk rating with contributing factors.

## Purpose
Visibility into factors and tracking changes.

## Expected Outcome
Reduced research time for risk rating investigation.

## Coaching Context (from 12.4 Scoring)

### Connection to Risk Scoring Architecture:
- **Final Customer Risk Score** = MAX(Pure Customer Score, Max Hierarchy Customer Score) — this is the ONLY score exposed downstream
- Account-level scoring is being **decommissioned** — customer-level is the strategic direction
- Manual overrides (12.4.3) are **permanent** and customer-level — these must be visible in the factor contribution view
- **Obligor ID** used as legal entity identifier

### What This BRD Would Enable:
- Currently, users can see the aggregate risk distribution (via sandbox results dashboard)
- This BRD adds **individual customer transparency** — drill into WHY a specific customer got a specific score
- Critical for FIU/MCO investigation workflows — reduces research time
- Maps to CRR Report **R14**: Audit trail for all risk point changes per customer

### Pre-requisites:
- DAM output (customer-level scored data) must be available — Target 26.3
- Rule Execution Team scoring must capture factor-level contribution data
- 12.7 audit trail provides the who/when tracking

## Sub-Requirements

| Sub-Req | Title | Status |
|---------|-------|--------|
| 12.15.1 | Customer Risk Rating Change Audit | Not Built |
| 12.15.2 | Customer Factor Contribution View | Not Built |
| 12.15.3 | Risk Rating Change History Report | Not Built |

## Interview Notes
- All 3 sub-requirements Not Built — Target 2027
- Depends on scoring data being available at customer-factor level (DAM + Rule Execution Team)
- Key user value: reduces investigation time for FIU/MCO when reviewing customer risk ratings
