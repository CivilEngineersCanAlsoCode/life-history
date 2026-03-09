---

# SANDBOX VERSIONING: EXECUTIVE SUMMARY FOR RESUME BRAIN

## Project Name
Sandbox Versioning (Feature 1 of CRR 2.0 Platform)

## Company & Role Context
American Express | Senior Associate Product Manager | July 2024 - Present

## One-Sentence Description
Designed and delivered a unified simulation environment enabling compliance teams to safely test rule configuration changes against production data before promoting to production, with version control, two-step approval (maker-checker), and atomic promotion.

---

## The Problem Solved

**Legacy Challenge:** The legacy Cadence compliance rules engine had no pre-production testing capability. Any rule change went live immediately, creating existential risk: a single untested rule could misclassify 30M+ customer accounts, triggering AML violations, regulatory penalties, and audit failures. Manual testing (if done at all) happened offline in Excel, took 3-5 days, and had no audit trail. Regulatory audits found no version control, no change log, no evidence of change control—violating AML control requirements.

**Gap:** CRR 2.0 was supposed to replace Cadence but couldn't be certified production-ready without addressing this gap. Regulators expected parity-or-better change control. Compliance teams needed a way to confidently test rules before production.

---

## Key Capabilities Delivered

1. **Sandbox Creation with Scope Management:** Enterprise or Market scope; mutual exclusion enforced (cannot have Enterprise and Market sandboxes simultaneously).

2. **Unified Lifecycle & State Machine:** Draft → In Progress → Testing Completed → Pending Approval 1 → Pending Approval 2 → Implemented/Rejected/Cancelled/Stale. Full audit trail at every state transition.

3. **Simulation on Production Data Copy:** Run rule engine against 30M+ customer accounts and 40+ markets in parallel; deliver results in <5 hours (SLA target: 10M accounts in 5 hours).

4. **Simulation Results & Insights:** Before/after risk distribution visualization, market/legal entity drill-down, customer population impact analysis.

5. **Version Control & Immutable Snapshots:** Configuration locked on Submit; immutable snapshot captures exactly what was tested. Rollback: create new version from any historical snapshot or overwrite Draft.

6. **Two-Step Approval (Maker-Checker):** Two different users must approve; audit trail records both approver identities and approval timestamp. Approver 1 (MLRO) reviews business case; Approver 2 (Manager) reviews operational risks.

7. **Atomic Promotion:** All changes (Rules + Assets + Fundamental Assessment) merged in single database transaction. Full rollback on failure. No partial states.

8. **Enterprise Asset Version Propagation:** Enterprise asset edits automatically cascade to all markets on promotion.

9. **Complete Audit Trail Export (CSV):** All sandbox actions (creation, edits, simulation, approvals) exported with who/what/when/why. Regulatory audit-grade evidence.

10. **Stale State Handling:** If another sandbox promotes while yours is Draft, yours becomes Stale (not deleted). Options: re-base on new config, abandon, or create new version.

---

## Business Impact & Metrics

**Risk Mitigation:** Eliminates production risk from untested rule changes. One prevented incident = [VERIFY: regulatory fine exposure]ne avoided.

**Operational Efficiency:** 
- Reduced cost-per-rule from [VERIFY: legacy cost] to [VERIFY: new cost]
- Time-to-deployment: 14-21 days → 5-7 days
- Simulation time: 3-5 days manual → same-day automated

**Regulatory Compliance:**
- Delivers auditor requirements: version control, pre-production testing, immutable audit trail
- Enables Cadence sunset (CRR proves superior change control)
- Satisfies AML control framework (maker-checker, SOX compliance, audit trail)

**Financial ROI:**
- One-time investment: [VERIFY: actual build cost]
- Year 1 ROI: [VERIFY: %] ([VERIFY: net benefit])
- Year 2+ ROI: [VERIFY: %] ([VERIFY: annual benefit])
- Payback period: <6 months

**North Star Metric:** % of production rule changes deployed with pre-production simulation proof. Target: 95% within 12 months.

---

## Technical Architecture Highlights

**Five Core Components:**

1. **Sandbox Creation & Scope Management**—Enforce mutual exclusion (Enterprise XOR Market); prevent conflicting concurrent changes.

2. **Immutable Snapshots on Submit**—Configuration locked; what gets approved is exactly what was tested. Enables airtight audit evidence.

3. **Simulation Engine with Auto-Scaling**—Horizontal scaling via market partitioning; async job queue with auto-scaling; <5 hour SLA for 30M accounts.

4. **Lifecycle State Machine**—Formal state transitions with logging; two-step approval with enforcement (different users).

5. **Atomic Promotion & Rollback**—Single database transaction (Rules + Assets + FA); rollback on any failure; recoverable via historical snapshots.

**Key Design Decisions:**
- Mutual exclusion prevents silent conflicts (stricter but safer)
- Full production data copy enables accurate population-level impact (slower but audit-defensible)
- Immutable snapshots ensure reproducible audit evidence (friction but compliance-essential)
- Two-step approval with role distinction (Approver 1 = business logic, Approver 2 = operations) adds genuine risk reduction

**Regulatory Controls Built In:**
- Encryption at rest (AES-256) and in transit (TLS)
- Role-based access control (RBAC)
- Automatic data purge (90 days)
- Immutable audit logging (3+ years retention)
- Maker-checker enforcement (two different users, validated at database level)

---

## Execution Highlights

**Scope:** 11 stories, 50 story points, 5 sprints (SAFe framework), delivered by team of 4 engineers + 1 PM.

**Timeline:** Concept to production: 6 months (25 weeks execution + 4 weeks regulatory certification).

**Key Milestones:**
- Sprint 1-2: Core features (sandbox creation, state machine, snapshot, simulation engine, approval UI, atomic promotion)
- Sprint 3: MVP completion (results visualization, version history, audit trail export)
- Sprint 4-5: Hardening, testing, regulatory certification
- Week 29: Go-live with regulatory sign-off

**Notable Decisions:**
- Deferred enterprise asset propagation to Phase 2 (6 weeks post-launch) because asset versioning wasn't complete; half-baked propagation would create technical debt
- Prioritized mutual exclusion design early (prevent silent conflicts) after user testing revealed risk of simultaneous Enterprise/Market testing
- Designed stale state as a visible archive (not deletion) after stakeholder feedback; enables re-base or abandon options

**Challenges Overcome:**
1. Simulation engine complexity was underestimated (8 pts → 13 pts); escalated day 3, re-baselined sprint, used pair programming
2. Two-step approval workflow had edge cases not specified in story (rejection recovery, mutation prevention); conducted rapid design sessions
3. Regulatory review wasn't planned in original timeline (4 weeks of unplanned delay); mitigated by inviting compliance for early iteration (sprint 4)

---

## Stakeholder Management Highlights

**Regulatory Challenge:** Regulators skeptical of pre-production testing as "false confidence." Response: Built narrative around layered controls (simulation + maker-checker + monitoring + rollback), provided audit evidence and regulatory precedent (JPMorgan, Citi models), maintained transparent relationship.

**Engineering Challenge:** Mutual exclusion viewed as bottleneck. Response: Data analysis showed blocking is rare (4 weeks/year), operational workarounds (batch Market rules before Enterprise cycles), monitoring commitment (track blocking monthly).

**Compliance Challenge:** Two-step approval seen as too slow for urgent rule changes. Response: Escalation path (urgent rules bypass standard queue, both approvers pinged simultaneously), data (standard approvals already same-day, second approval adds only 4-6 hours), emergency approval mechanism (manager can authorize if second approver unavailable).

---

## Personal Ownership

**Role:** Senior APM, owning Sandbox Versioning end-to-end.

**Responsibilities:**
1. Problem discovery & validation (8 user interviews, data analysis, case to leadership)
2. Solution design (architecture, detailed PRD, UX wireframes)
3. Cross-functional leadership (negotiated with Regulatory, Engineering, UX)
4. Stakeholder management (addressed pushback, built consensus)
5. Execution oversight (sprint ceremonies, bug triage, burn-down tracking)
6. Launch & adoption (go-live planning, training, adoption monitoring, product iteration)
7. Regulatory certification (worked with Internal Audit, Compliance teams)

**What Fails Without Me:**
- Initial problem validation (research proving this was critical, not theoretical)
- Stakeholder negotiation (navigated competing interests; alternative PM might deprioritize after pushback)
- Design decisions (mutual exclusion, snapshots, stale state came from compliance domain knowledge)
- Regulatory relationships (built trust with Compliance teams; enabled certification)
- Launch execution (stayed engaged through first 8 weeks production; drove adoption)

**Hardest Parts:**
1. Gaining regulatory confidence pre-ship, then shipping without eroding that confidence (psychologically draining but feature was important)
2. Deferring features (enterprise asset propagation) while stakeholders wanted Phase 1 delivery (required discipline; half-baked features create debt)
3. Balancing simplicity (analysts want speed) vs. auditability (regulators want controls) (solved with sequential approval + aggressive SLA + streamlined UI)

---

## Future Roadmap & Strategic Vision

**Strategic Vision:** Make CRR the industry-leading compliance rules engine with the safest, most auditable, fastest rule change process in financial services.

**Sandbox's Role:** Feature 1 of CRR 2.0, establishing the foundation (safe, auditable, fast).

**Phase 2 (Q4 2024 - Q1 2025):** Asset versioning & enterprise propagation, simulation result analytics, rule interaction analysis.

**Phase 3 (Q2-Q3 2025):** Compliance finding-to-rule-change automation, multi-sandbox testing.

**Phase 4+ (Future):** Simulation result prediction (ML), auto-rollback, cross-system change orchestration.

---

## Key Learnings & Reflections

1. **Domain expertise matters:** Compliance domain knowledge was unreplaceable; enabled design decisions other PMs might miss.

2. **Regulatory relationships are capital:** Built relationships with Internal Audit, Compliance teams early; they became advocates, not blockers.

3. **State machines are subtle:** Should have designed the state machine in detail (on paper) before engineering started, not discovered edge cases mid-sprint.

4. **Stakeholder pushback is valuable:** Every objection (engineering, regulatory, compliance) surfaced a real risk; addressed them thoughtfully, not dismissively.

5. **Defer debt, not value:** Deferred enterprise asset propagation because it required upstream work (asset versioning), not because it was low-priority. MVP still delivered 80% of value.

6. **Launch is the beginning, not the end:** Stayed engaged through first 8 weeks production; adoption metrics and early feedback drove product iteration.

---
