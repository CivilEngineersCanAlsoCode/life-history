# CRR AML Risk Scoring Engine - Project Overview & Index

## Quick Summary

**Project:** Customer Risk Rating (CRR) - Modernizing the AML (Anti-Money Laundering) Risk Scoring Engine  
**Company:** American Express  
**Role:** Senior Associate Product Manager  
**Timeline:** Jul 2024 – Present  
**Team Size:** 18-person scrum team  
**Status:** Phase 1 delivered, Phase 2 in progress (Jul 2024 – Present)

**Achievement:** Won Amex Leadership Award + 6000 Blue Rewards for delivery excellence

## The Challenge

**Legacy System:** Cadence (12+ years old)
- Non-scalable monolithic architecture
- Poor explainability—couldn't explain risk scores to regulators or analysts
- Performance bottleneck at scale (30M+ daily transactions)
- Long development cycles for compliance updates (weeks to deploy rule changes across 40+ markets)
- Alert fatigue and manual workarounds by compliance analysts

**Scale & Scope:**
- 30 million daily transactions across 40+ markets globally
- Sub-2-second real-time risk scoring requirement at customer onboarding
- Must support FATF standards and local AML/KYC regulations across 40+ jurisdictions
- 50+ compliance analysts and investigators rely on system daily

## The Solution: CRR on GCIP Platform

**New Platform:** GCIP (Global Compliance Intelligence Platform)  
**Architecture:** Five-dimension risk scoring framework (Customer, Geography, Transaction, Product, Events)  
**Score Output:** 1-10 scale mapping to Low/Medium/High/Very High risk categories

### 10 Rally Capabilities (7 Delivered in Phase 1)

| # | Capability | Rally ID | Status |
|---|-----------|----------|--------|
| 1 | CRR Framework & Configurability | C140525 | 17/26 features Done |
| 2 | Centralized Data Management (Asset Manager + FA) | C140527 | 4/9 features Done |
| 3 | Governance and Authorization | C140528 | 2/2 features Done |
| 4 | Sandbox and Change Validation | C140529 | 6/19 features Done |
| 5 | Reporting and Notifications | C140530 | 0/3 features Done |
| 6 | Audit and Compliance Management | C140531 | 2/6 features Done |
| 7 | Customer Level Risk Scoring | C145274 | 11/32 features Done |
| 8 | AI/ML Based Scoring (Phase 2) | C150874 | Funnel |
| 9 | Integration with AML Ecosystem (Phase 2) | C150875 | Funnel |
| 10 | Entity Obligor & Onboarding API (Phase 2) | C150876 | Funnel |

## Business Impact

| Metric | Impact |
|--------|--------|
| **Regulatory Risk Mitigation** | [VERIFY: estimated regulatory risk avoided] |
| **Operational Efficiency** | [VERIFY: annual analyst productivity savings] |
| **Market Expansion** | Unlocked 5 high-compliance jurisdictions |
| **Onboarding Velocity** | [VERIFY] 8% improvement in customer activation completion rates |
| **Project ROI** | [VERIFY] Breakeven in <2 months post-launch |

## How We Delivered Phase 1

**Key Strategies:**
1. Ruthless prioritization: 10 Rally capabilities scoped, 7 delivered in Phase 1 (CRR Framework & Configurability, Centralized Data Management, Governance & Authorization, Sandbox & Change Validation, Reporting & Notifications, Audit & Compliance Management, Customer Level Risk Scoring)
2. Aggressive risk-taking: staged launches within quarterly SAFe PI cycles
3. Parallel work streams: 2 scrum teams (Rule Configuration ~12 members, Rule Execution ~6 members) with independent delivery paths
4. Analyst-in-the-loop: monthly beta testing vs. annual gates
5. Escalated decision-making: weekly steering meetings for unblocking
6. Feature flagging: deploy incomplete features, enable/disable without re-deployment

## User Research Insights

**20+ UX Sessions** with compliance analysts, managers, and MLRO officers revealed:

- The main issues identified were lack of scalability, inefficient system, and legacy architecture — Cadence couldn't handle 30M+ daily transactions efficiently, rule changes took weeks to deploy, and the monolithic design created operational bottlenecks
- Analysts wanted to customize rules for market-specific risks
- Time-to-investigation target: reduce from 12-15 minutes to <4 minutes
- Analysts valued control over full automation
- Trust in new system built through parallel runs and transparent scoring explanations

## Key Metrics & KPIs

### North Star Metric
**Time-to-Investigation:** Median time from risk alert to analyst initiating investigation
- Cadence baseline: 12-15 minutes
- CRR target: <4 minutes
- Driver: Explainable scores enable faster triage

### Performance Metrics (Delivered)
- Scoring latency: <2 seconds at 99th percentile (from 3-5 seconds)
- System uptime: 99.5%+ (critical for analyst reliance)
- Task completion rate: 94% (from 65% in early prototypes)
- Score interpretation error rate: 2% (from 18% in Cadence)

### Business Metrics (Post-Launch Targets)
- False positive rate: 25% reduction
- Regulatory audit findings: Fewer compliance gaps than Cadence
- Analyst productivity: Cases investigated per analyst per week
- Time-to-understand-a-score: [VERIFY] 42 seconds (from 3.2 minutes in Cadence)

## Project Governance

**Framework:** SAFe (Scaled Agile) with quarterly PI (Program Increment) Planning
**Team Structure:** 2 scrum teams (18 total)
- Rule Configuration Team: ~12 members (frontend, backend, UX designer, UX researcher, QA)
- Rule Execution Team: ~6 members (backend engineers, data engineers, QA)
- Product & Leadership: 2 product managers, 1 tech lead, scrum master

## Regulatory & Compliance Context

**Standards & Frameworks:**
- FATF (Financial Action Task Force) standards
- AML/KYC compliance requirements
- GDPR, CCPA, and local privacy regulations
- Consent order risk mitigation

**Key Stakeholders:**
- MLRO (Money Laundering Reporting Officer) - regulatory authority
- Chief Compliance Officer - executive sponsor
- Compliance analysts - primary users (50+)
- Legal & Regulatory Affairs - rule review and approval
- Data Governance - Point of Assessment data quality

## Architecture Decisions

### Why Rules-Based Over ML?
- Regulatory requirement for explainability and auditability
- Analysts wanted control, not black-box automation
- FATF standards demand traceable scoring logic
- ML models planned for Phase 2 after analyst trust is established

### Why GCIP Over Alternatives?
- **vs. Lift-and-shift Cadence:** Would perpetuate technical debt; didn't solve explainability problem
- **vs. Third-party platforms (SAS, FICO):** Couldn't support 40-market customization + integration with proprietary Amex systems
- **vs. Build proprietary:** Would have taken longer; GCIP offered vendor support and long-term strategic partnership

### Key Technical Decisions
- Stateless scoring services for horizontal scalability
- Aggressive caching for Point of Assessment data retrieval
- Rules compiled at deployment vs. runtime interpretation
- Daily delta scores + monthly full customer rescoring
- Strict multi-tenant data isolation with row-level security

## Known Challenges & Mitigations

| Challenge | Mitigation |
|-----------|-----------|
| Scoring regression (false negatives) | 2-month parallel runs with detailed comparison analysis |
| Data quality issues | Data quality task force + reconciliation dashboard |
| Analyst adoption/resistance | Transparent communication + escalation path for disputed scores |
| Legal review bottleneck | Playbook with templates + parallel review process |
| Integration failures | Dedicated engineers embedded with downstream teams |
| Organizational fear of change | Parallel runs proving CRR more defensible in audits |

## Files in This Project Folder

### Template Answers (Interview Prep)
- `/Template Answers CRR/` folder containing:
  - 15 individual template answer files (01-15) for behavioral interview questions
  - `Answer to all 15 Combined CRR.md` - all answers in narrative format
  - `Template Answers CRR.md` - index of all template answers

### Documentation
- `CRR Resume Brain.md` - Comprehensive brain dump and knowledge base
- `CRR AML Engine.md` - This overview and index file

## Interview-Ready Key Takeaways

### Problem Definition
Legacy AML system was 12+ years old, non-scalable, couldn't explain scores to regulators, and created alert fatigue for 50+ analysts. Risk included regulatory penalties, inability to enter new markets, and operational inefficiency. This was an existential problem requiring urgent modernization.

### Customer Insight
The main issues discovered through UX research were lack of scalability, inefficient system, and legacy architecture. Cadence couldn't scale to handle growing transaction volumes, rule changes required weeks of deployment effort across 40+ markets, and the monolithic design created operational bottlenecks for compliance teams.

### Solution Innovation
Built configurable risk scoring framework on GCIP platform across 10 Rally capabilities — 7 delivered in Phase 1 including CRR Framework & Configurability, Centralized Data Management (Asset Manager for centralized list management + data point configuration), Sandbox & Change Validation (copy-on-write sandbox architecture), and Customer Level Risk Scoring. Rules-based approach (not ML) to ensure regulatory explainability.

### Execution Excellence
Delivered Phase 1 (7 of 10 Rally capabilities) through ruthless prioritization (10 Rally capabilities scoped, 7 delivered in Phase 1 with 3 deferred to Phase 2), parallel work streams, and aggressive risk-taking. Maintained quality through parallel runs, regression testing, and escalated decision-making.

### Business Impact
[VERIFY: regulatory penalties avoided], [VERIFY: operational savings], [VERIFY: market entries and onboarding improvement % improvement in onboarding completion rates. Breakeven in <2 months post-launch.

### Stakeholder Management
Built organizational confidence through parallel runs comparing CRR vs. Cadence scoring, transparent risk communication, and escalation paths for disputed scores. Overcame resistance by proving CRR more defensible in regulatory audits.

### Personal Leadership
As Senior APM, personally owned vision, discovery, prioritization, and end-to-end execution. Drove ruthless prioritization of 10 Rally capabilities for phased delivery.

## Phase 2 & Future Vision

**Next 6-12 Months:**
- Behavioral ML models for anomaly detection
- Network analysis identifying customer relationship risk
- Product-specific risk scoring (card/loan/payment level)
- Advanced reporting and audit dashboards

**Long-Term Vision:**
- GCIP as industry-leading compliance platform
- CRR as reference architecture for enterprise AML
- Compliance capabilities as strategic competitive advantage (not cost center)
- Full consolidation of 15+ legacy compliance point solutions into unified GCIP platform

## Contact & Links

- **Project Location:** `/sessions/peaceful-dazzling-goldberg/mnt/Resume Brain/02 - American Express (Jul 2024 – Present)/01 - CRR AML Risk Scoring Engine/`
- **Template Answers:** See `/Template Answers CRR/` folder
- **Knowledge Base:** `CRR Resume Brain.md`
- **Interview Prep:** Start with `Answer to all 15 Combined CRR.md` for narrative overview, then drill into individual template answers as needed

---

**Last Updated:** 2026-03-04  
**Project Status:** Delivered, in-production, Phase 2 planning underway
