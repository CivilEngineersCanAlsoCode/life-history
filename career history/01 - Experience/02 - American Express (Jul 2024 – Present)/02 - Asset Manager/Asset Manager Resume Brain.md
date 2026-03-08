# Asset Manager - Resume Brain & Interview Prep

## Executive Summary

**Project:** Asset Manager — a centralized, sandbox-driven lifecycle management system for reusable AML/CFT risk policy lists across 40+ markets
**Role:** Senior Associate Product Manager
**Impact:** Reduced time-to-asset-update from [VERIFY: before] to [VERIFY: after]; [VERIFY: annual value]; [VERIFY: active usersrs, 400+ assets promoted, zero production incidents
**Key Innovation:** Copy-on-write architecture enabling enterprise consistency with market-level customization

---

## The Problem

Before Asset Manager existed, reference data lists (Industry, Geography, Company Structure, Acquisition Channel, Notable Lists) were managed manually outside the CRR platform:
- Each update required formal change requests routed through Engineering
- Average cycle time: [VERIFY] 26 days
- No audit trail of who changed what, when, and why (compliance gap)
- Inconsistency: different markets operated different versions of the same list
- Risk: 30M+ daily transactions scored against inconsistent thresholds

The core tension: Compliance analysts owned the business logic but lacked operational control.

---

## Discovery & Validation

Conducted 20+ user research sessions with compliance teams across US, UK, Asia-Pacific regions:
- Tracked time-to-close metrics: [VERIFY] 26 days average
- Analyzed 18 months of backlog: [VERIFY] 80+ asset-related feature requests pending
- Interviewed compliance analysts, MLRO leads, CRR administrators
- Ran contextual inquiry sessions observing asset change requests
- Storyboarded proposed workflows, iterated with users

**Key insight from research:** Market teams needed to customize enterprise assets for local regulatory requirements (e.g., UK JMLSE vs. US guidance on Industry definitions). This wasn't in initial product vision but proved essential.

**Validation results:**
- [VERIFY] 94% of analysts would switch to self-service if available
- [VERIFY] 89% cited audit trails as must-have
- Copy-on-write architecture validated with [VERIFY] 8 of 8 compliance analysts

---

## The Solution

### Core Architecture
- **Sandbox-first design:** All assets live in sandboxes (Enterprise or Market) before promotion to production
- **Hierarchical ownership:** Enterprise defines shared assets (5 core types); markets inherit with copy-on-write option
- **Versioning:** Immutable asset versions; changes create new versions; provides audit clarity
- **State transitions:** Draft → Sandbox → Production with usage metadata tracking

### Key Capabilities Delivered
1. **Asset creation within sandbox context** with reference data validation
2. **Automatic state transitions** with visual status indicators
3. **Copy-on-write workflow** enabling market customization without breaking enterprise synchronization
4. **Enterprise version propagation** automatically updating all markets on promotion
5. **Excel export** (two-sheet Values + References format) for audit validation
6. **Read-only compliance analyst view** for non-editing stakeholders
7. **Complete audit trail** with who/what/when/why; 15-minute undo window for promotions

### Copy-on-Write: The Key Innovation
When a compliance analyst edits a shared enterprise asset in their market sandbox:
1. System creates a local copy (fork) instead of modifying enterprise version
2. Local copy maintains version lineage to original
3. Automated divergence detection flags when local copy differs from enterprise
4. Analysts can merge updates back or keep local version separate

This solved the core tension: market autonomy + enterprise governance.

---

## Execution & Delivery

**SAFe PI Cadence:** 5 sprints, 40 story points

Sprint breakdown:
- **Sprints 1-2:** Core CRUD + sandbox context management (foundational engine)
- **Sprint 3:** Audit trail + state transitions (Draft → Sandbox → Production)
- **Sprint 4:** Copy-on-write workflow + visual indicators
- **Sprint 5:** Excel export + read-only view

**Major execution challenge:** Copy-on-write complexity
- Initially estimated as one-sprint feature
- During Sprint 3 implementation, engineers discovered complex distributed versioning problem
- Consistency guarantees across 40+ market sandboxes required deeper schema changes
- **Decision:** Extend PI by one sprint, re-plan at midpoint (risky but necessary)
- **Outcome:** Delivered copy-on-write properly; gained stakeholder trust by choosing quality over deadline

**UX iteration challenge:**
- UAT revealed analysts struggled with copy-on-write UI (SUS score [VERIFY] 68, below 70 threshold)
- Primary friction: confusion about when to create local copy vs. edit enterprise asset
- Remediation: Added visual decision helper ("Is this market-specific?"), renamed feature to "Create Local Copy"
- Post-iteration SUS: [VERIFY] 81 (excellent)

**Validation challenges:**
- Pattern-matching validation engine had [VERIFY] 8% false-positive rate in UAT
- Shipped as "suggestions only" mode (doesn't block, advises analysts)
- Post-launch tuning brought false-positive rate to [VERIFY] <1%

---

## Key Metrics

### North Star
**Time-to-Asset-Update (TTAU)**
- Baseline: [VERIFY] 26 days
- Target: [VERIFY] <8 hours for 80% of updates
- Actual (2 months post-launch): [VERIFY] 3.2 days average (84% improvement)

### Leading Indicators
- Sandbox adoption: [VERIFY] >90% (analysts testing before production)
- Audit completeness: [VERIFY] 100% (all changes documented)
- Copy-on-write usage: [VERIFY] >70% (market customization adoption)
- User session frequency: [VERIFY] >85% return weekly

### Lagging Indicators
- Manual workaround reduction: [VERIFY] 40/month → 2/month (95% reduction)
- Consistency score: [VERIFY] <5% drift across market versions
- Compliance audit findings: [VERIFY] eliminated (target 0, achieved in first audit cycle)

### Business Impact
- **Value created:** [VERIFY: total annual value]
- **Delivery cost:** [VERIFY: delivery cost]
- **ROI:** [VERIFY] 2.7x year one; payback in 4.4 months
- **Adoption:** [VERIFY] 87 active users week 2, 400+ assets promoted to production
- **Reliability:** [VERIFY] Zero production incidents, 99.95% uptime SLA

---

## Stakeholder Management

**Market teams:** Initially feared losing autonomy to enterprise governance
- **Resolution:** Socialized copy-on-write architecture through 4 regional sessions
- **Key message:** Market customization preserved while enabling consistency
- **Outcome:** Turned skeptics into co-designers

**MLRO compliance:** Wanted formal approval workflows for asset promotion
- **Initial proposal:** Add "Pending Approval" state with routing (adds latency)
- **Resolution:** Compliance validation checklist embedded in promotion flow; self-validation + audit trail
- **Outcome:** Governance maintained without bottleneck

**Engineering team:** Resisted aggressive timeline for copy-on-write
- **Resolution:** Phased delivery (CRUD π1, copy-on-write PI2, audit export PI3)
- **Outcome:** Reduced complexity per sprint; delivered safely

---

## Key Trade-offs & Decisions

**Sandbox-first vs. direct editing:**
- Trade-off: Added latency/complexity but prevented production errors
- Decision: Chosen for safety; one list error scoring 30M transactions too risky

**Enterprise control vs. market autonomy:**
- Trade-off: Copy-on-write balances both; some markets wanted full independence
- Decision: Enforced enterprise reference assets (5 core types) to prevent 40+ divergent definitions

**Immutable versions vs. edit flexibility:**
- Trade-off: Can't edit promoted versions; changes create new versions
- Decision: Chosen for audit clarity; always pinpoint which version was live

**Phased delivery vs. big-bang:**
- Trade-off: Scope creep if features added late; trust damage if deadlines missed
- Decision: Phased (CRUD → copy-on-write → audit export) allowed validation between phases

**Full external data integration vs. minimal validation:**
- Trade-off: External integration (ISO, SWIFT, OFAC data) adds complexity
- Decision: Shipped batch validation + manual override; full integration in PI2

---

## Technical Depth

### Architecture
- **Microservice:** Golang backend, DynamoDB + Postgres, React SPA frontend
- **Event-driven sync:** SQS + Lambda for asset propagation across market sandboxes
- **Versioning:** Immutable asset versions with dependency tracking
- **Audit logging:** Tamper-evident logs with SOX compliance

### Scalability
- Tested to [VERIFY] 10K+ assets; 500 concurrent edits
- Event-driven promotion now sub-second regardless of market count
- Multi-region deployment with automated failover

### Data integrity
- Optimistic locking for concurrent edits
- Pre-delete dependency checks (hard block if rules reference asset)
- Soft-delete with orphan detection
- 15-minute undo window for accidental promotions

---

## Failure Modes & Mitigations

| Failure Mode | Mitigation |
|---|---|
| Asset corruption (e.g., empty list) | Pre-promotion validation, 15-min undo window |
| Copy-on-write divergence | Automated divergence detection, "Last Updated" flag |
| Accidental asset deletion | Hard block on deletion if rules reference asset |
| Orphaned assets | Usage analytics, flag >90 days unused |
| UI confusion (copy-on-write) | Renamed feature, visual decision helper |
| Validation false positives | Tuned pattern matching to <1% false-positive rate |
| Sync latency across 40+ markets | Event-driven architecture, now sub-second |

---

## Post-Launch Roadmap

### Phase 2 (Next PI)
- Role-based access control: Approver, Reviewer roles
- External data integrations: SWIFT, ISO, sanctions list providers
- Pre-population of geography/industry assets from official sources

### Phase 3 (PI+2)
- Asset templates: Country List, Person List, Product List patterns
- Bulk import: Migration from legacy spreadsheet-based systems
- Onboard 10+ new markets

### Year 2 Vision
- Asset usage analytics: Which assets drive most risk score changes?
- Asset effectiveness metrics: Do high-SAR assets actually identify illicit activity?
- Predictive recommendations: ML models suggesting asset values based on SAR patterns
- Auto-rules generation: "Define asset thresholds, rules auto-generate"

---

## What I Own & Drive

**Full product leadership:**
- Strategy & vision (articulated problem + secured resources)
- Discovery & validation (20+ research sessions, synthesis)
- Design direction (iterated with UX designer + users)
- Roadmap prioritization (weighted scoring framework)
- Stakeholder management (regional sessions, negotiation)
- Delivery accountability (5-sprint SAFe cadence, mid-PI re-planning)

**Critical decisions I made:**
1. **Copy-on-write hybrid model:** Balanced market autonomy + enterprise consistency
2. **Phased delivery:** Reduced complexity, validated between phases
3. **Mid-PI re-plan:** Extended timeline for copy-on-write quality
4. **UX redesign:** Pushed for iteration despite time pressure ([VERIFY] SUS 68 → 81)
5. **Validation mode:** Shipped as suggestions-only to prevent false positives

**What fails without me:**
- Copy-on-write wouldn't exist (required synthesis of competing stakeholder needs)
- Stakeholder alignment wouldn't hold (requires continuous engagement)
- Product quality standards wouldn't survive roadmap pressure

---

## Hardest Parts

### Challenge 1: Copy-on-Write Complexity
- Initially thought it was simple "fork" operation
- Mid-implementation discovered distributed versioning, consistency challenges
- Forced difficult decision: extend timeline or ship broken feature
- **Resolution:** Extended PI by 1 sprint; explained to leadership why quality mattered more than deadline
- **Learning:** Technical spike in Sprint 0 would have caught this; future projects prioritize architectural validation

### Challenge 2: UX Comprehension Failure
- UAT revealed 40% of analysts didn't understand copy-on-write despite explanation
- Initial SUS score of [VERIFY] 68 (below acceptable threshold) was wake-up call
- **Resolution:** Pushed Engineering for design iteration (unpopular); renamed feature; added visual helpers
- **Learning:** Domain experts ≠ SaaS power users; assumed too much product literacy

### Challenge 3: Stakeholder Expectations
- Market teams surprised by Asset Manager launch; hadn't been involved in discovery
- Created expectation misalignment, initial resistance
- **Resolution:** Hosted 4 regional "state of the asset" sessions explaining roadmap, benefits, launch timeline
- **Learning:** Early communication is cheaper than late resistance; involve stakeholders earlier in discovery

---

## Interview Preparation Reminders

**Strong opening:** "I led Asset Manager, a self-serve lifecycle management system for AML/CFT risk reference data. The problem: list updates took 26 days and required Engineering because there was no governance structure. We delivered a platform reducing time-to-update to same-day with full audit trails. Key innovation was copy-on-write architecture enabling market customization without breaking enterprise consistency."

**Core narrative arc:**
1. Problem (26-day cycle, audit gaps, inconsistency)
2. Validation (20+ research sessions, market teams needed copy-on-write)
3. Solution (sandbox-first, copy-on-write, state transitions, audit trails)
4. Execution (5-sprint delivery, mid-PI re-plan for copy-on-write quality)
5. Impact ([VERIFY: % time reduction], [VERIFY: annual value], [VERIFY: incidents])

**Anticipated tough questions:**
- "Why did you choose copy-on-write?" → User research proved market teams needed local customization while maintaining enterprise consistency; hybrid model was only option satisfying both
- "What would you do differently?" → Longer technical spike in Sprint 0 for copy-on-write; earlier stakeholder communication with market teams
- "How did you handle the SUS score failure?" → Took it seriously; pushed for design iteration despite time pressure; renamed feature + added visual helpers; SUS improved to 81
- "What failed without you?" → Copy-on-write wouldn't exist (required synthesis of competing interests); stakeholder alignment wouldn't hold without continuous engagement; product quality wouldn't survive roadmap pressure

**Quantified impact to emphasize:**
- TTAU: [VERIFY] 26 days → 3.2 days (84% improvement)
- Manual workarounds: [VERIFY] 40/month → 2/month (95% reduction)
- Business value: [VERIFY: annual value], [VERIFY: ROI]
- Adoption: [VERIFY] 87 users week 2, 400+ assets promoted
- Reliability: [VERIFY] 99.95% uptime, zero production incidents

---
