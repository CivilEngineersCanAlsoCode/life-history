---

# SANDBOX VERSIONING PROJECT OVERVIEW

**Company:** American Express  
**Role:** Senior Associate Product Manager  
**Timeline:** July 2024 - Present  
**Feature:** Sandbox Versioning (Feature 1 of CRR 2.0 Platform)

---

## What Is Sandbox Versioning?

Sandbox Versioning is a unified simulation environment that enables compliance teams to safely test rule configuration changes (Rules, Assets, Fundamental Assessment) against a production data copy before promoting to production. It includes full version control, two-step approval with audit trail, and atomic promotion with rollback capability.

---

## Why It Matters

**The Problem:** The legacy Cadence system had zero pre-production testing capability. Any rule change went live immediately, risking incorrect risk ratings for millions of customers. No version control, no audit trail, no rollback mechanism. Regulatory audits found critical gaps in change control.

**The Solution:** Sandbox Versioning delivers:
- Pre-production testing against 30M+ customer accounts in <5 hours
- Immutable version control and audit trail
- Two-step approval (maker-checker) with formal audit evidence
- Atomic promotion of all changes (Rules + Assets + FA) with full rollback on failure
- Complete compliance defensibility for regulatory audits

**The Impact:**
- **Risk:** Eliminates production risk from untested rule changes
- **Efficiency:** Reduced time-to-deployment from [VERIFY: legacy time] to [VERIFY: new time]; cost-per-rule from [VERIFY: legacy cost] to $2K
- **Compliance:** Delivers auditor requirements; enables Cadence sunset; satisfies AML control framework
- **ROI:** Year 1: [VERIFY: ROI %] ([VERIFY: net benefit]); Year 2+: [VERIFY: ROI %] ([VERIFY: annual value]); Payback: [VERIFY: estimate]

---

## Core Capabilities

1. **Sandbox Creation:** Users select Enterprise or Market scope; mutual exclusion enforced to prevent conflicting concurrent changes
2. **Configuration Snapshots:** Configuration locked on Submit; immutable snapshot captures exactly what was tested
3. **Simulation Engine:** Runs rule evaluation against 30M+ accounts, 40+ markets in parallel; delivers results in <5 hours
4. **Simulation Results:** Before/after risk distribution, market/entity drill-down, customer population impact
5. **Lifecycle & Approval:** Formal state machine (Draft → In Progress → Testing Completed → Pending Approval 1/2 → Implemented/Rejected/Stale); two-step approval enforces maker-checker
6. **Version Control & Rollback:** Full audit trail; ability to rollback to any historical version
7. **Atomic Promotion:** All changes deployed in single database transaction; full rollback on any failure
8. **Enterprise Asset Propagation:** Enterprise changes automatically cascade to all markets on promotion
9. **Audit Trail Export:** CSV export of all sandbox actions (who/what/when/why) for regulatory evidence
10. **Stale State Handling:** Sandboxes that are superseded by other promotions transition to Stale (not deleted); users can re-base, abandon, or create new version

---

## Users & Their Benefits

**Compliance Analysts (Simulation Runners)**
- Before: 3-5 days manual Excel-based testing; no confidence in results
- After: Same-day automated simulation; objective evidence of rule correctness
- Benefit: Faster iteration, higher confidence, reduced manual toil

**MLRO Teams (Compliance Officers, Approver 1)**
- Before: Can't confidently approve rule changes without manual verification
- After: Pre-production simulation proves rule works; formal approval workflow
- Benefit: Faster rule deployment (5-7 days vs. 2-3 weeks); audit trail for regulatory defense

**Compliance Managers (Operational Risk, Approver 2)**
- Before: Approve based on faith, not evidence; no rollback if something goes wrong
- After: Two-step approval; proof of pre-production testing; atomic rollback capability
- Benefit: Production stability; audit-grade defensibility; rollback confidence

---

## Technical Architecture

**Five Core Components:**

1. **Sandbox Creation & Scope Management**
   - Create sandbox with Enterprise (affects all markets) or Market-specific (single country) scope
   - Enforce mutual exclusion: if Enterprise active, block all Market creations (vice versa)
   - Prevents silent conflicts from concurrent overlapping changes

2. **Immutable Snapshots & Draft State**
   - On creation, capture immutable snapshot of current production config
   - Analysts edit only in Draft state; once submitted, configuration becomes immutable
   - Enables precise version control and audit trail ("exactly this config was tested")

3. **Simulation Engine with Auto-Scaling**
   - Run rule evaluation against production data copy (30M+ accounts, 40+ markets)
   - Horizontal scaling via market partitioning; async job queue with auto-scaling
   - Real-time progress tracking (% complete, ETA); cancellation at any point
   - SLA: 99.5% completion rate within 5 hours

4. **Lifecycle State Machine & Two-Step Approval**
   - Formal state transitions: Draft → In Progress → Testing Completed → Pending Approval 1 → Pending Approval 2 → Implemented/Rejected/Cancelled/Stale
   - Every transition logged with timestamp, user ID, reason
   - Two-step approval enforces maker-checker: Approver 1 and Approver 2 must be different people
   - Approver 1 (MLRO): "Does this rule fix the compliance finding?" 
   - Approver 2 (Manager): "Are there operational risks or rule interactions?"

5. **Atomic Promotion & Rollback**
   - On approval, execute atomic database transaction: all changes (Rules + Assets + FA) merged simultaneously
   - If transaction fails, entire promotion rolls back (no partial states)
   - Rollback capability: create new sandbox from any historical snapshot and re-test

---

## Design Decisions & Trade-offs

**1. Mutual Exclusion (Enterprise XOR Market) vs. Parallel Testing**
- Chosen: Mutual exclusion (Enterprise and Market cannot be active simultaneously)
- Alternative: Allow parallel sandboxes with conflict resolution engine
- Why: User testing revealed that simultaneous testing by different teams creates silent conflicts post-promotion. Mutual exclusion is stricter but prevents catastrophic audit/compliance issues. Operational cost is low (MLRO can sequence changes).

**2. Production Data Copy vs. Sample Subset**
- Chosen: Full production copy (30M+ accounts, 40+ markets)
- Alternative: Representative sample (1M accounts) to speed simulation
- Why: Regulators want proof that rules were tested against the *exact population* they'll affect in production. Tail effects, geographic clustering, temporal patterns may not show in samples. Also, MLRO asks "how many customers will move from Low to Medium risk?" — requires accurate population counts. Longer simulation time (5 hours) is acceptable; regulatory defensibility is non-negotiable.

**3. Immutable Snapshots on Submit vs. Live Configuration References**
- Chosen: Immutable snapshots on Submit (what gets approved is exactly what was tested)
- Alternative: Reference live Draft configuration (approver sees current state even if analyst edits after submission)
- Why: If analyst continues editing Draft after approver starts reviewing, approver is reviewing a moving target. Can't prove "this exact configuration was tested." Immutable snapshots create airtight audit evidence. Trade-off: if analyst wants to incorporate Approval 1 feedback before Approval 2, they must cancel and re-submit.

**4. State Machine Complexity**
- Chosen: 9-state machine (Draft, In Progress, Testing Completed, Pending Approval 1, Pending Approval 2, Implemented, Rejected, Cancelled, Stale)
- Why: Every state corresponds to a real operational phase with distinct user responsibilities and audit trail requirements. More complex internally, but users see simplified view (3 prominent states).

---

## Regulatory & Compliance Controls

**Data Privacy:**
- Encryption at rest (AES-256), in transit (TLS)
- Role-based access control (RBAC); only MLRO and approvers can view sandbox
- Automatic data purge after 90 days
- Audit logging of all data access (3+ year retention)

**Regulatory Audit Trail (AML/SOX):**
- Immutable ledger: every sandbox action (creation, edit, simulation, approval) logged with who/what/when/why
- Maker-checker enforcement: two different users must approve; validated at database level
- Evidence collection: simulation results and approval records attached to promotion
- CSV export: audit-grade evidence exportable for regulatory review

**Change Management:**
- Mutual exclusion is a documented control (prevents conflicting concurrent changes)
- Atomic promotion is a documented control (prevents partial production states)
- Stale state handling is documented (prevents silent supersession of prior tests)

---

## Execution Summary

**Scope:** 11 stories, 50 story points, 5 sprints  
**Team:** 4 senior engineers + 1 PM  
**Timeline:** 25 weeks execution + 4 weeks regulatory certification  
**Delivery:** Week 29 with regulatory sign-off  

**Key Milestones:**
- Sprint 1-2 (10 weeks): Core features (sandbox creation, state machine, snapshots, simulation, approval UI, atomic promotion)
- Sprint 3 (5 weeks): MVP completion (results visualization, version history, audit trail export)
- Sprint 4-5 (10 weeks): Hardening, testing, edge cases, regulatory certification

**Notable Decisions:**
- Deferred enterprise asset propagation to Phase 2 (asset versioning wasn't complete; half-baked propagation would create debt)
- Prioritized mutual exclusion after user testing revealed risk of concurrent Enterprise/Market testing
- Designed stale state as archive (not deletion) based on stakeholder feedback

**Challenges Overcome:**
- Simulation engine complexity underestimated (8 pts → 13 pts); escalated, re-baselined, used pair programming
- Two-step approval had undiscovered edge cases (rejection recovery, mutation prevention); rapid design sessions mid-sprint
- Regulatory review not planned in original timeline (4 weeks unplanned); mitigated with early compliance involvement

---

## Business Impact & Metrics

**North Star Metric:** % of production rule changes deployed with pre-production simulation proof  
Target: 95% within 12 months

**Leading Indicators (daily/weekly):**
- Sandbox creation rate (target: 3-5 per week)
- Time-to-Testing-Completed (target: <1 day)
- Approval velocity (target: >80% approved within 24 hours)
- Simulation completion rate (target: >99%)
- Sandbox re-test rate (target: 1.5-2.5 iterations)

**Lagging Indicators (monthly/quarterly):**
- % of rules with simulation proof (north star)
- Production incidents related to rules (target: zero)
- Regulatory audit findings on change control (target: zero)
- Time-to-deployment (target: 5-7 days, down from 14-21)
- Cost-per-rule (target: [VERIFY: target cost], down from [VERIFY: legacy cost])

**Financial ROI:**
- One-time investment: [VERIFY: actual build cost]
- Annual operations: [VERIFY: annual ops cost]
- Annual benefits: [VERIFY: annual benefits]
- Year 1 ROI: [VERIFY: %] ([VERIFY: net benefit])
- Year 2+ ROI: [VERIFY: %] ([VERIFY: annual value])
- Payback period: <6 months

---

## Future Roadmap

**Phase 2 (Q4 2024 - Q1 2025):**
- Asset versioning & enterprise propagation
- Simulation result analytics (comparison to historical rules)
- Rule interaction analysis (experimental)

**Phase 3 (Q2-Q3 2025):**
- Compliance finding-to-rule-change automation
- Multi-sandbox testing (batch related changes)

**Phase 4+ (Future):**
- Simulation result prediction (ML)
- Auto-rollback on production monitoring anomalies
- Cross-system change orchestration

---

## Key Learning Points for Future PMs

1. **Domain expertise is irreplaceable.** Compliance domain knowledge enabled design decisions (mutual exclusion, stale state handling) that other PMs might miss.

2. **Regulatory relationships are strategic assets.** Built relationships early; regulators became advocates, not blockers.

3. **State machines are subtle.** Design in detail on paper before engineering; avoid discovering edge cases mid-sprint.

4. **Pushback reveals real risks.** Every stakeholder objection (engineering, regulatory, compliance) surfaced a genuine risk; address thoughtfully, not dismissively.

5. **Defer debt, not value.** Deferred enterprise asset propagation because it required upstream work, not because it was low-priority. MVP still delivered 80% of value.

6. **Launch is the beginning.** Stayed engaged through first 8 weeks production; adoption metrics and early feedback drove product iteration and confidence.

7. **Communicate trade-offs transparently.** Two-step approval is slower; explain why (genuine risk reduction, auditor requirement, not bureaucratic checkbox).

---
