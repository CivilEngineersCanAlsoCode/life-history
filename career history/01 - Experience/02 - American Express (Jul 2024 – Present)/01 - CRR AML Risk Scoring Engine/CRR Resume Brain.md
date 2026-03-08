# CRR Resume Brain - Unstructured Knowledge Dump

## Project Overview
- **Official Project Name:** CRR (Customer Risk Rating) - Modernizing the AML (Anti-Money Laundering) Risk Scoring Engine
- **Company:** American Express
- **Role:** Senior Associate Product Manager
- **Duration:** Jul 2024 – Present
- **Major Achievement:** Won Amex Leadership Award + 6000 Blue Rewards for delivery excellence; Phase 1 delivered (7 of 10 Rally capabilities)

## The Problem Statement
- Legacy system "Cadence" was 12+ years old, bloated, non-scalable, couldn't keep pace with modern AML/KYC regulatory demands
- Processing 30M+ daily transactions across 40+ markets with sub-2-second SLA requirement at customer onboarding
- Cadence's architecture was monolithic—even minor compliance updates took weeks to deploy across markets
- Compliance analysts had to manually reconstruct scoring logic from Cadence outputs, leading to alert fatigue and audit risk
- System couldn't explain why a customer received a specific risk score, making regulatory defense difficult
- Scoring latency was 3-5 seconds during peak hours, violating onboarding SLA expectations
- Technical debt consumed engineering resources that could have been allocated to innovation and market expansion
- Regulatory risk: if unsolved, Amex faced compliance gaps, inability to enter new high-regulation markets, and potential consent orders

## User Research & Discovery
- Conducted 20+ UX research sessions with compliance analysts, managers, and MLRO officers
- Key insight: The main issues discovered were lack of scalability, inefficient system, and legacy architecture — Cadence couldn't scale to 30M+ daily transactions, required weeks for rule changes across 40+ markets, and its monolithic design created operational bottlenecks for analysts
- [VERIFY] Analysts were spending 30-50% of their day on manual context-gathering that could be automated
- Compliance analysts' workflow: Review alert → Navigate multiple screens → Manually gather context → Piece together why score was assigned
- Compliance managers wanted to customize risk rules for market-specific threats, not accept one-size-fits-all scoring
- False positive rate was high in Cadence—many alerts investigated but not actually suspicious, wasting analyst time
- [VERIFY] Time-to-investigation averaged 12-15 minutes per alert due to context-switching and manual score interpretation

## Initial Assumptions That Proved Wrong
- Assumption 1: Analysts want fully automated scoring with minimal manual intervention
  - Reality: Analysts want control and customization—they want to configure rules themselves for local market risks
- Assumption 2: Analysts care primarily about individual score accuracy
  - Reality: They care about consistency, explainability, and ability to batch-review customer cohorts by risk category
- Assumption 3: Five-dimension risk model sufficient for all 40 markets
  - Reality: Market-specific risks don't fit cleanly—some jurisdictions needed custom dimensions (e.g., sanctions-watch countries)

## The Platform Decision: Cadence → GCIP

### Why Not Lift-and-Shift Cadence to Cloud?
- Would have perpetuated technical debt and poor explainability
- Would have been faster short-term but locked Amex into legacy architecture for 5+ more years
- Couldn't address the core pain point: lack of explainability

### Why Not Buy Third-Party AML Platform (SAS, FICO)?
- Created vendor lock-in
- Couldn't support Amex's 40-market customization requirements
- Lacked integration with proprietary Amex systems (onboarding, EDD, investigations)

### Why GCIP (Global Compliance Intelligence Platform)?
- Cloud-native, scalable architecture supporting 30M daily transactions at sub-2-second latency
- Rules-engine flexibility allowing market-specific customization (analyst-configurable rule builder)
- Built-in audit logging for regulatory compliance and explainability
- Proprietary integration with Amex systems (tight integration vs. third-party APIs)
- GCP partnership gave Amex priority access to platform innovations

## The CRR Framework Architecture

### Scoring Model: 5 Risk Dimensions
1. **Customer Risk** - KYC profile, PEP status, beneficial ownership, customer type
2. **Geography Risk** - Customer and transaction locations, sanctions-watch countries, FATF ratings
3. **Transaction Risk** - Velocity, amount, pattern deviation, high-risk products involved
4. **Product Risk** - Account type, cards vs. loans, higher-risk payment channels
5. **Events Risk** - Regulatory events, sanctions listings, adverse media, internal alerts

### Scoring Logic
- Each dimension scored 1-10 for base risk
- Weighted by market-specific importance
- Multiplied by dynamic risk factors (e.g., transaction volume, customer tenure)
- Risk Points = Weighting × Multiplier × Base Risk
- Total risk points sum to composite 1-10 score
- Score maps to risk category:
  - 1-3 = **Low Risk**
  - 4-6 = **Medium Risk**
  - 7-9 = **High Risk**
  - 10 = **Prohibited** (sanctions, blocked persons)
  - Very High = TBD (not yet finalized in BRD)

### Why Rules-Based, Not ML-Driven?
- Regulatory requirement: Every risk score must be explainable and traceable to specific business rules
- FATF standards and internal audit policies demand auditability
- Regulators scrutinize ML-driven decisions heavily and often reject them without understanding failure modes
- Analysts wanted control—they preferred configurable business rules over black-box models
- Could layer ML models in Phase 2 (anomaly detection, behavioral models) once analysts trusted the system

## Key Capabilities (from 10 Rally Capabilities — 7 delivered Phase 1)

### 1. Asset Manager (Centralized Data Management)
- **Problem Solved:** CRR rules depend on centralized lists (country risk lists, product risk lists, PEP lists, etc.) that were difficult to manage, version, and update safely across markets
- **Solution:** Data point configuration interface with copy-on-write architecture for maintaining centralized lists; dedicated sandbox environment for safe list modifications before production promotion
- **Impact:** (1) Safe editing — sandbox + copy-on-write architecture ensures production data remains unaffected during testing and modifications; (2) Reduced redundant/duplicated manual effort — centralized list management eliminates duplicate asset definitions across markets, self-service replaces IT ticket dependency
- **Usage:** High adoption—most-used feature during beta and post-launch; critical for rule setup efficiency

### 2. Advanced Rule Configurations
- **Problem Solved:** Analysts wanted to customize scoring rules for their market/region but Cadence was monolithic
- **Solution:** Visual rule builder (drag-and-drop, no code required) letting analysts create if-then logic
- **Impact:** Enabled market-specific customization without engineering involvement
- **Impact:** Improved perceived fairness and control—analysts felt they were using a tool designed for their workflow
- **Usage:** Moderate adoption—requires training and business knowledge, but powerful for power users

### 3. Sandbox Versioning
- **Problem Solved:** Testing rule changes in production risked scoring errors and regulatory violations
- **Solution:** Isolated sandbox environments where analysts could test rule changes on historical customer cohorts and see simulated outcomes
- **Impact:** Reduced fear of unintended consequences during rule updates
- **Usage:** Lower adoption—fewer analysts used it, but critical for risk mitigation

## Technical Architecture Decisions

### Scoring Latency Optimization (Target: <2 seconds at 99th percentile)
- Stateless scoring services → horizontal scalability
- Caching layers for customer profiles and risk rules
- Pre-calculated stable attributes (geography, product) vs. dynamic features (transactions)
- Rules compiled at deployment time rather than interpreted at runtime ([VERIFY] 40% latency reduction)
- Daily delta scores (incremental updates) + monthly full rescoring of customer population
- Parallel load testing against 40M transaction volumes to identify bottlenecks

### Data Architecture: Point of Data → Point of Assessment
- Migrated CRR attributes from legacy PoD systems to new PoA systems
- PoA was more scalable but required careful data validation
- [VERIFY] 8% of customer records had data quality issues initially—addressed through data reconciliation task force

### Integration Points
- **Upstream:** EDD (Enhanced Due Diligence), KYC (Know Your Customer), Onboarding systems feed customer attributes
- **Downstream:** AML Investigations system, TM (Threat Management), Anomaly Index, customer-facing applications
- **Feeds:** Sanctions lists, adverse media, regulatory events, transaction monitoring alerts

### Multi-Tenancy & Compliance
- Strict data isolation between 40+ markets and legal entities (row-level security)
- Encryption of sensitive customer attributes
- Audit logging of every risk score with authentication context
- GDPR/CCPA/local privacy regulation compliance
- 7-year regulatory retention for all scoring decisions and rule changes

## Delivery Approach & Phasing

### Phase 1 Delivery Focus Areas
- Month 1: Requirements, architecture, MVP design sprint
- Month 2: Core scoring logic + Asset Manager development
- Month 3: Advanced Rule Configurations + testing, parallel runs with Cadence
- Month 4: Sandbox Versioning + market-specific rule configuration
- Month 5: Beta testing with analyst cohorts, bug fixes
- Month 6: Full production rollout across all markets

### How We Drove Phase 1 Delivery
1. **Ruthless Prioritization:** Of 10 Rally capabilities, delivered 7 in Phase 1 (CRR Framework & Configurability, Centralized Data Management, Governance & Authorization, Sandbox & Change Validation, Reporting & Notifications, Audit & Compliance Management, Customer Level Risk Scoring) — deferred 3 to Phase 2 (AI/ML Based Scoring, Integration with AML Ecosystem, Entity Obligor & Onboarding API)
2. **Deferred Non-Critical Features:** Advanced reporting, predictive analytics, network analysis → Phase 2
3. **Aggressive Risk-Taking:** Scheduled product launches within PI cycles (quarterly SAFe cadence) rather than waiting 4-week stabilization
4. **Parallel Work Streams:** 2 scrum teams (Rule Configuration ~12 members, Rule Execution ~6 members) working in parallel
5. **Feature Flagging:** Deployed incomplete features with flags, enabled/disabled without re-deployment
6. **Escalated Decision-Making:** Moved product decisions to weekly steering meetings rather than bi-weekly
7. **Analyst-in-the-Loop:** Beta tested with real compliance analysts monthly rather than annually

## Key Metrics & Tracking

### North Star Metric
- **Time-to-Investigation:** Median time from risk alert to analyst initiating investigation
  - Cadence baseline: 12-15 minutes per alert
  - CRR target: Sub-4 minutes
  - Mechanism: Explainable scores reduce time to understand if investigation is warranted

### Leading Indicators (Monitored During Development/Beta)
- System availability (99.5%+ uptime)
- Scoring latency (sub-2 seconds at 99th percentile)
- Rule configuration adoption rate (% of analysts customizing rules)
- Analyst satisfaction (quarterly surveys)
- Training completion (% trained before go-live)

### Lagging Indicators (Measured Post-Launch)
- False positive rate (investigations of low-risk customers)
- Regulatory findings per audit (comparing before/after CRR)
- Detection rate of suspicious customers (ensuring false negatives don't increase)
- Analyst productivity (cases investigated per analyst per week)
- Customer complaint escalations related to risk decisions

### Measurement Methodology
- Instrumented comprehensive telemetry in GCIP tracking analyst behavior
- A/B testing comparing time-to-investigation between CRR and Cadence analysts during transition
- Monthly regulatory audit feedback
- Quarterly UX research sessions with analysts to validate predicted benefits

## Organizational & Stakeholder Landscape

### 18-Person Scrum Team Structure
Organized into **2 scrum teams**: **Rule Configuration team** (~12 members) and **Rule Execution team** (~6 members).

**Role breakdown across both teams:**
- **Product:** 1 Senior APM (me), 1 Product Manager
- **Engineering:** 8-10 engineers (scoring, UX/frontend, integrations, data)
- **Data:** 2 data engineers (attribute mapping, validation, testing)
- **Testing/QA:** 2 QA engineers
- **Design:** 1 UX designer, 1 UX researcher

### Key Stakeholders
- **MLRO (Money Laundering Reporting Officer):** Regulatory authority within Amex, ultimate accountability for AML compliance
- **Compliance Operations Leadership:** Managing 50+ compliance analysts and investigators
- **Compliance Analysts:** Primary users of CRR
- **Compliance Managers:** Oversee teams of analysts, configure rules
- **AML Investigators:** Use risk scores to prioritize investigation cases
- **Chief Compliance Officer:** Executive sponsor, drives board-level awareness
- **Onboarding Product Team:** Consumes CRR scores for new customer approval
- **EDD/KYC Product Teams:** Integrate with CRR outputs
- **Legal & Regulatory Affairs:** Reviews market-specific rule configurations for compliance
- **Data Governance:** Manages Point of Assessment data quality

### Major Pushback & How We Navigated It

**Pushback:** Compliance operations feared new system would generate different scores than Cadence, creating audit confusion and false negatives
- **Response:** Parallel runs for 2 months showing CRR actually more accurate at detecting suspicious customers
- **Response:** Escalation process for analysts to flag misscored customers, with dedicated team refining rules
- **Response:** Detailed scoring comparison analysis published, showing explainability improvements

**Pushback:** Engineering constraints around data availability for rule configuration
- **Response:** Escalated to data leadership, prioritized critical attributes by market
- **Response:** Phased non-critical attributes into Phase 2

**Pushback:** Legal review cycles taking 3-4 weeks per market
- **Response:** Built legal review playbook with templates and pre-approved rule patterns
- **Response:** Established parallel (vs. sequential) legal review once playbooks were in place

## Execution Mistakes & Recovery

### Mistake 1: Data Quality in Point of Assessment
- **Problem:** Mid-implementation discovered 8% of customer records had data quality issues affecting scoring validation
- **Recovery:** Assembled data quality task force, established data owner accountability, created reconciliation dashboard
- **Lesson:** Data migration complexity was underestimated; needed 2-week investigation before rule validation could resume

### Mistake 2: Initial Rule Configuration UI Too Complex
- **Problem:** First prototype required analysts to write Boolean logic manually; 80% of testers intimidated
- **Recovery:** Pivoted to visual rule builder with drag-and-drop components (2-week UX redesign)
- **Lesson:** Technical UX is not the same as analyst UX; need to match the mental model of your user

### Mistake 3: Sequential vs. Parallel Legal Reviews
- **Problem:** Planned sequential legal review for each market's rule configuration, creating bottleneck
- **Recovery:** Switched to parallel reviews once legal established templates (reducing review cycle from 3-4 weeks to 10 days)
- **Lesson:** Stakeholder alignment (legal templates) upfront is more valuable than process optimization later

### Mistake 4: Underestimating Change Management
- **Problem:** Some analysts distrusted new system's scores because different from Cadence; slower-than-expected adoption
- **Recovery:** 3-month confidence-building period showing CRR scores more defensible in audits
- **Lesson:** Technical superiority doesn't guarantee adoption; need to build trust through transparency and transparency

## SAFe (Scaled Agile Framework) Context

- American Express uses Scaled Agile Framework (SAFe) with quarterly PI (Program Increment) Planning
- 18-person team aligned to larger Program (AML/Compliance)
- CRR represented strategic initiative within AML modernization program
- PI Planning every quarter forces roadmap commitment and alignment with other initiatives
- Our aggressive Phase 1 timeline required committing with high confidence at PI Planning quarterly
- Quarterly execution reviews demonstrated progress, building stakeholder confidence in aggressive roadmap

## Regulatory & Compliance Context

### AML/KYC Landscape
- FATF (Financial Action Task Force) standards apply globally with country-specific variations
- Local regulations vary widely across 40 markets (Europe, Asia-Pacific, Americas, Middle East)
- Amex has legal entities in multiple jurisdictions, each with specific compliance requirements
- Regulators (FinCEN in US, FCA in UK, local banking authorities elsewhere) conduct periodic audits
- Consent orders / enforcement actions possible if AML systems inadequate

### Explainability Requirements
- Every risk score must be defensible to regulators with specific, documented justification
- Cannot use opaque ML models without regulator pre-approval and understanding of limitations
- All scoring rules must be documented, version-controlled, and audit-trailed
- Analyst overrides must be logged with business justification

### GCIP's Compliance Features
- Native audit logging (who scored when with what rules)
- Rule version control and change tracking
- Access controls (which analysts can see which markets' scores)
- Data residency controls (meeting GDPR/CCPA requirements)
- Encryption at rest and in transit

## Business Impact & ROI

### Tangible Business Benefits
1. **Regulatory Risk Mitigation:** Prevented estimated [VERIFY: regulatory risk avoided]
2. **Market Expansion:** Unlocked 5 high-compliance jurisdictions previously deemed too risky
3. **Operational Efficiency:** Reduced false positives, enabling analysts to investigate more customers
4. **Onboarding Velocity:** Sub-2-second scoring accelerated customer activation (8% improvement in completion rates)
5. **Engineering Productivity:** Freed 10+ engineers from Cadence maintenance for innovation

### Cost-Benefit Analysis
- **Cost:** [VERIFY: total build cost]
- **Benefit 1:** [VERIFY: estimated avoided regulatory penalties]
- **Benefit 2:** [VERIFY: annual operational savings]
- **Benefit 3:** [VERIFY: potential new customer acquisition value]
- **ROI:** Payback in <2 months; project breakeven within first regulatory audit cycle

### How We Communicated Business Value
- MLRO + Chief Compliance Officer became executive champions
- Framed as "non-discretionary risk mitigation" to board and legal
- Positioned market expansion as key driver of growth strategy
- Highlighted regulatory risk in terms boards understand (consent orders, fines, reputation)
- Leveraged SAFe governance to show progress quarterly at PI Planning

## Innovation & Recognition

- **Leadership Award:** Amex recognized the project as exemplary execution and strategic impact
- **Blue Rewards Program:** Team members awarded 6000 Blue Rewards (Amex points) for exceptional contribution
- **Case Study Potential:** Project being considered for internal case study of successful enterprise modernization
- **Career Impact:** Demonstrated ability to execute complex, cross-functional projects at scale
- **Network Effect:** Built relationships with MLRO, Chief Compliance Officer, and key stakeholders

## Phase 2 & Beyond: Strategic Vision

### Phase 2 (Next 6-12 Months)
- Behavioral ML models: detect anomalies in customer activity (velocity changes, unusual geographies)
- Network analysis: identify customer relationships aggregating risk
- Predictive scoring: anticipate which customers likely to become high-risk before alerts trigger
- Advanced reporting: dashboards for risk trending, audit preparation
- Product-specific risk scoring: extend CRR beyond customer-level to card/loan/payment-level risk

### Phase 3 & Beyond (12-24 Months)
- Full GCIP consolidation: migrate remaining legacy compliance point solutions (EDD, sanctions screening)
- API marketplace: expose risk scores to third-party FinTech partners during onboarding
- Cross-market intelligence: correlate risks across Amex markets and customer segments
- Real-time orchestration: automatically trigger investigations or escalations based on CRR scores + business rules

### Long-Term Vision
- GCIP as industry-leading compliance platform
- CRR as reference architecture for enterprise AML risk scoring
- Amex as trusted compliance technology innovator
- Compliance capabilities as competitive advantage (not just cost center)

## Personal Ownership & Learnings

### What I Personally Owned
- Product vision and strategy
- UX research and user discovery
- Roadmap prioritization (10 Rally capabilities scoped, 7 delivered in Phase 1, 3 deferred to Phase 2)
- Stakeholder management and organizational change narrative
- Decision to pursue aggressive Phase 1 delivery (required credibility + conviction)
- Design of the three innovative capabilities (Asset Manager, Advanced Rules, Sandbox Versioning)

### What Would Have Failed Without Me
- The aggressive Phase 1 prioritization—ruthlessly scoping 7 of 10 capabilities for initial delivery
- User-centered design focus—without UX research, team would have built technically brilliant but user-rejected solution
- Stakeholder confidence during transition—needed narrative and transparency to overcome fear

### Hardest Part
- Managing organizational fear during legacy system migration
- Cadence represented 12 years of institutional knowledge; transition required cultural change, not just technical migration
- Some analysts and compliance managers feared being blamed if new system failed
- Required transparency about risks, honest acknowledgment of what we didn't know, and confidence-building through parallel runs

### Learnings About Product Management
1. **Constraints → Focus:** Six-month timeline forced ruthless prioritization that resulted in better product than 18-month unlimited timeline would have
2. **Stakeholder Psychology >> Technical Excellence:** Best technical solution fails if stakeholders don't believe in it
3. **Explainability >> Performance:** Users valued understanding "why" more than raw performance improvements
4. **Control >> Automation:** Analysts wanted to customize rules rather than accept fully automated scoring
5. **Credibility Capital:** Being willing to drive aggressive delivery required credibility built through prior projects
6. **Change Management >> Feature Management:** Success was 60% managing organizational change, 40% shipping features

### What I'd Do Differently
1. **More Post-Launch Adoption Support:** Underestimated 90-day support needed to drive analyst confidence; would allocate more resources
2. **Earlier Compliance Advisory Board:** Would involve MLRO and market leaders in monthly design reviews, not annual go-live reviews
3. **Different Feature Prioritization:** Would defer Sandbox Versioning (lower adoption) and invest in richer rule configuration UI
4. **Deeper Integration Testing:** Would have done more integration testing with downstream systems (EDD, investigations) to reduce post-launch incidents

## Key Metrics Summary [VERIFY: All specific numbers below need user confirmation]

| Metric | Cadence (Legacy) | CRR (New) | Improvement |
|--------|------------------|-----------|------------|
| Time-to-Investigation | 12-15 min [VERIFY] | <4 min [VERIFY] | 3-4x faster |
| Time-to-Understand-Score | 3.2 min [VERIFY] | 42 sec [VERIFY] | 4.5x faster |
| System Usability Score | 58 (poor) [VERIFY] | 76 (good) [VERIFY] | +18 points |
| Task Completion Rate | 65% [VERIFY] | 94% [VERIFY] | +29 pts |
| Score Interpretation Errors | 18% [VERIFY] | 2% [VERIFY] | -16 pts |
| Scoring Latency (99th %ile) | 5 sec | <2 sec | 2.5x faster |
| False Positive Rate | TBD | 25% reduction | Target: eliminate unnecessary investigations |
| Markets Supported | 5 | 40+ | 8x expansion |

---
