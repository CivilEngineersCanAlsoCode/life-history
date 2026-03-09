# BRD 12.12 — Integration with AML Ecosystem

## Status
Not Built

## Target Timeline
26.3

## Bead Reference
career-context-54w

## Business Requirement
Make CRR available to consuming apps.

## Purpose
Holistic CRR view across AML ecosystem.

## Expected Outcome
Customer risk rating available to all consuming applications.

## Coaching Context

### CRR in the AML Ecosystem:
- CRR (Customer Risk Rating) is a **foundational input** to the broader AML/KYC ecosystem
- **Final Customer Risk Score** = MAX(Pure Customer Score, Max Hierarchy Customer Score) — this is what gets consumed downstream
- Downstream consumers use CRR to determine investigation priority, due diligence level, monitoring intensity

### Integration Architecture (from High Level Architecture):
- **GCP-based:** GCIP (CRR) → PubSub → Downstream systems
- **DAM (Lumi Project gfccodl)** handles data ingestion from source systems
- **CRR (Lumi Project gcipamlcrr)** handles rule configuration and scoring
- **BigQuery** serves as the data warehouse for cross-system analytics

### Key Integration Points:
```
Source Systems → DAM → CRR Scoring Engine → Final Risk Score
                                              ↓
                                    KYC, AML, TM, EDD, Anomaly Index
                                              ↑
                                    Alert disposition data (feedback loop)
```

### Critical Gap — Real-Time Scoring:
- Currently **only daily batch at 7pm MST** — no real-time scoring API exists
- 12.12.3 requires **sub-2 second** real-time scoring at onboarding — major architecture gap
- This maps to 12.18.1 Report 5 (Real-Time Onboarding Performance)

## Sub-Requirements

| Sub-Req | Title | Status | Coaching Notes |
|---------|-------|--------|----------------|
| 12.12.1 | Downstream System Integration | Not Built | Final Customer Risk Score → KYC, AML, TM, EDD, Anomaly Index |
| 12.12.2 | Override Feedback Loop | Not Built | Bidirectional: if downstream overrides CRR → must feed back with details |
| 12.12.3 | Real-Time Onboarding Integration | Not Built | Sub-2 second SLA; currently only daily batch exists — MAJOR GAP |
| 12.12.4 | Alert Data Integration | Not Built | Post-disposition alert data feeds back into CRR scoring (EDD, SAR, Sanctions) |
| 12.12.5 | Future Enhancement Flexibility | Not Built | Architecture must accommodate evolving integration needs |

## Interview Notes
- All 5 sub-requirements Not Built — Target 26.3
- Real-time onboarding scoring (12.12.3) is the most architecturally significant gap
- Override feedback loop (12.12.2) connects to 12.4.3 (Manual Risk Rating Override) — external system overrides must be consumed
- Integration via GCP PubSub aligns with existing sandbox simulation communication pattern
