---
# UNIFIED SANDBOX JOURNEY: COMPREHENSIVE PRODUCT ANSWERS (ALL 15 QUESTIONS)

## Context & Feature Overview
**Official Name:** Unified Sandbox Journey (Feature 1 in CRR 2.0)  
**Definition:** Consolidates ALL CRR configuration changes (Rules, Assets, Fundamental Assessment) into a single, version-controlled sandbox workflow. Users create sandboxes with Enterprise or Market scope, make edits in Draft state, submit for simulation against production data, review results, obtain two-step approvals, and promote changes atomically to production—with full rollback capability.  
**Scope:** 11 user stories, 50 story points, 5 sprints (26.1.1-26.1.5)  
**Regulatory Drivers:** BRD 12.8 (sandbox/simulation), BRD 12.10 (maker-checker approval), BRD 12.12 (real-time rescoring at onboarding)  
**Users:** Compliance analysts/managers (the compliance team), MLRO/MCO view-only access

---

## Q1. Problem Definition (Clarity Test)

The CRR platform powered risk-decisioning across 40+ markets and 30M+ daily transactions, yet operated without version control, simulation, or atomic changes. Compliance analysts had no sandbox to test configuration changes before production promotion. Changes flowed directly to production—irreversible without manual IT intervention. A single misconfigured rule could shift risk classifications for millions of customers, triggering regulatory exposure: false positives in AML monitoring, missed SAR filings. BRD 12.10 mandated maker-checker governance; BRD 12.8 required sandbox/simulation; BRD 12.12 required real-time rescoring. The platform's migration from Cadence to GCIP on GCP cloud created a modernization window to embed these controls natively.

**Pain point manifestation:** Analysts feared configuration changes. No simulation meant no preview of impact. No version history meant no trace of why rules behaved differently. Single-actor changes risked harm. MLRO teams couldn't validate alignment with risk appetite.

**Regulatory/Competitive Driver:** GCIP on GCP cloud enabled stateless sandbox architecture. Regulatory momentum around transaction monitoring (BRD 12.8, 12.10) demanded proof of controlled, auditable change management.

**North Star:** All CRR configuration changes flow through Unified Sandbox with zero production incidents from misconfigured rules post-launch.

---

## Q2. Customer & Persona Depth

**Primary Users:** Compliance Analysts and Compliance Managers (the compliance team) across 40+ markets. Secondary Users: MLRO and MCO teams (view-only access to sandbox results, BRD 12.9.4).

**What They Accomplish & Pain Points:**
- Analysts: update risk rules in response to regulatory guidance or incidents. Struggle because no sandbox, no version history, no simulation, no audit trail.
- Managers: oversee analysts and ensure BRD 12.10 compliance (maker-checker). Currently a manual, error-prone process.

**Success Metrics:**
- Analysts: time-to-implement (current baseline [VERIFY]), confidence in test results, rollback speed, audit trail completeness.
- Managers: zero single-actor changes reaching production, cycle time to approval, audit export speed for exams.

**Adjacent Team Relationships:** Analysts depend on IT for rollbacks. MLRO currently has no sandbox visibility. GCP platform owns infrastructure. Close coordination required on API stability and simulation SLA.

**"Done" Definition:** One-click sandbox creation, drag-drop edits, instant simulation preview, two-click approval chain, automated promotion with rollback, exportable audit trail—all within CRR UI.

---

## Q3. Discovery & Validation

**Validation Approach:** Interviewed the compliance team across 3 markets. Observed: rule changes emailed to IT (no automation), IT applies changes without simulation (black-box promotion), audit gaps, post-incident root cause revealing single-actor configuration errors. Reviewed BRD 12.8, 12.10, 12.12 and mapped to compliance gaps. Regulatory impact assessment concluded: sandbox is not nice-to-have—it's mandatory.

**Actual vs. Stated Needs:** Stated: "We need a sandbox." Actual: "We need confidence that changes won't break production AND proof of approval for audits." Users didn't ask for atomic promotion; that emerged as the engineering solution to prevent partial failures.

**Product-Market Fit Testing:** Low-fidelity Figma prototype (sandbox creation, draft editing, submit, simulation, approval chain). Walked through with the compliance team and MLRO reps. Surfaced confusion about "what gets simulated" and "when is rollback possible"—refined AC accordingly. No rejection of overall design.

**Key Assumptions Tested:**
- Assumption 1: GCP can provide production data copy for simulation in <SLA>. [VERIFY: confirm SLA]
- Assumption 2: Two-step approval integrates with existing identity systems. ✓ Confirmed.
- Assumption 3: Rules, Assets, FA can be versioned atomically. ✓ Confirmed (no dependency breakage).

---

## Q4. Solution Architecture & Trade-offs

**End-to-End Workflow:**
1. Create sandbox (Enterprise or Market scope, mutual exclusion enforced).
2. Edit Rules, Assets, or FA sub-tabs (edits accumulate in Draft state).
3. Submit for Simulation (modal requires change summary + justification, creates immutable version snapshot).
4. Simulation executes on GCP using production data copy; rescores customer population; real-time progress tracking with cancellation.
5. Review results (customer cohort deltas, risk score distributions).
6. Two-step approval: User A approves, User B approves (different users, BRD 12.10 maker-checker).
7. Atomic promotion: merges all changes (Rules + Assets + FA) in single transaction. Enterprise assets propagate to markets.
8. Full rollback: select prior version, create new version from baseline (immutable states) or overwrite Draft uncommitted changes.

**Why Mutual Exclusion?** Enterprise and Market sandboxes cannot coexist. Prevents race conditions (e.g., both updating same asset). Trade-off: analysts must serialize work. Benefit: zero merge conflicts, zero rollback complexity.

**Why Atomic Promotion?** Rules, Assets, FA are interdependent. All-or-nothing semantics ensures no partial state corruption. Technical & regulatory benefit: clear audit trail of before/after states.

**Key Trade-offs:**
| Trade-off | Benefit | Cost | Mitigation |
|-----------|---------|------|-----------|
| Mutual exclusion | Conflict prevention | Serialized workflows | Sprint scheduling |
| Simulation on production copy | Real impact forecast | Data masking complexity, latency | [VERIFY: SLA] |
| Full rollback capability | Recovery from mistakes | Maintain version history indefinitely | Archive after [VERIFY: retention policy] |
| Two-step approval | BRD 12.10 compliance, reduced errors | Approval cycle time | Optimized UI, escalation paths |

---

## Q5. Metrics & North Star

**North Star:** 100% of CRR configuration changes flow through Unified Sandbox with zero production incidents from misconfigured rules post-launch.

**90-Day Success Metrics:**
- Adoption rate: [VERIFY: target %, baseline %]
- Cycle time (request to promotion): [VERIFY: baseline to target]
- Approval turnaround: [VERIFY: baseline to target]
- Quality: zero post-launch incidents from misconfigured rules
- Audit: 100% of actions logged with who/what/when/why

**Leading Indicators of PMF:**
- Analysts proactively create sandboxes for experimental changes
- Simulation results reviewed before approval (not rubber-stamped)
- Rollback used in response to production issues
- MLRO teams provide meaningful approvals/rejections

**Regulatory Compliance Metrics:**
- Audit trail completeness: every change has justification, two approvals, timestamp, status
- Maker-checker adherence: 100% of promoted changes have two distinct approvers
- Simulation audit: every promoted change has recorded simulation results

**Success Curve:**
- Week 1-2: Early adopters ([VERIFY: baseline] → 30%)
- Week 3-4: Expansion ([VERIFY: baseline] → 60%)
- Month 2: Muscle memory ([VERIFY: baseline] → 90%, approval cycle time decreases)
- Month 3: Steady state (90%+ adoption, analysts onboarded with sandbox as standard)

---

## Q6. AI/ML Depth (When Relevant)

**ML Component:** Sandbox Versioning itself is not ML/AI. But Fundamental Assessment (one config type within sandbox) can incorporate ML models for risk scoring. Sandbox provides governance mechanism to test FA changes safely.

**Versioning & ML Interaction:**
- FA changes can include: new feature engineering, retrained model weights, updated calibration thresholds
- Simulation must include new ML model artifacts (versioned)
- Reproducible inference required: same input → same output across simulations and production
- Model explainability required for audit trails (why did risk score change?)

**ML-Specific Risks:**
- Model drift: if training data is stale, simulation results unreliable. Mitigation: embed model retraining schedules.
- Inference reproducibility: non-determinism breaks testing. Mitigation: enforce deterministic inference, version all dependencies.
- Explainability gaps: MLRO teams need to understand risk score deltas. Mitigation: include feature attribution (SHAP) or risk decomposition in simulation results.

**ML Quality Metrics:**
- Post-simulation: compare simulated scores vs. actual production scores (for past sandbox promotions)
- Model performance on holdout test set
- Fairness metrics: are risk scores equitable across demographics?

**Governance for ML:** Standard ML governance (model cards, bias audits, feature attribution) must be embedded in approval workflows. Audit trail logs not just "rule updated" but "model version X→Y, expected performance delta Z."

**Phased Approach:**
- Phase 1 (current): Rules and assets (deterministic)
- Phase 2 (future): Fundamental Assessment with simple ML features (supervised monitoring)
- Phase 3 (future): Complex ensemble models (advanced monitoring)

---

## Q7. Scalability & Reliability

**Scaling Across 40+ Markets, 30M+ Transactions:**
- Stateless architecture on GCP: horizontal scaling
- Sandbox creation: lightweight metadata, no persistent state
- Config edits: stored as deltas, not full rewrites
- Simulation: asynchronous, distributed across markets
- Rollback: instantaneous version load from metadata store
- [VERIFY: confirm GCP concurrency limits and simulation SLA]

**Reliability Requirements:**
- [VERIFY] 99.99% uptime (sandbox creation/promotion)
- Simulation SLA: [VERIFY: target, likely <5 min] or timeout
- Rollback: 100% success rate
- Version history: immutable
- Audit trail: tamper-proof

**Simulation Job Failures:** Retry (re-executes against same data snapshot), Cancel (reverts to Draft), Timeout (auto-failure notification). User never blocked indefinitely.

**Disaster Recovery:**
- Metadata replicated across [VERIFY: region count, likely 3+] regions
- Production data copy is ephemeral (deleted post-simulation)
- Failover to replica on primary region failure
- Version history never lost

**Atomic Promotion Safety:**
- Database transactions with Serializable isolation
- Pre-commit validation: schema, referential integrity, rollback scenario test
- All-or-nothing: if any component fails, entire transaction aborts
- Zero partial promotions

**Concurrency Control:**
- Mutual exclusion prevents Enterprise/Market sandbox coexistence
- Pessimistic locking: only one user edits sandbox at a time
- User B sees "locked by User A" with wait estimate and force-unlock option

---

## Q8. Monetization & Business Impact

**Direct Monetization:** None. Internal enabler for CRR modernization, customer onboarding (BRR 12.12), regulatory compliance.

**Business Impact of Failure:**
- 6-month delay → CRR stays on Cadence (legacy, high-risk), configuration changes slow, onboarding delayed, regulatory audit gaps
- Fine exposure: [VERIFY: regulatory fine estimate]
- Onboarding delay cost: [VERIFY: customer acquisition impact]
- Feature is critical path for GCIP migration and compliance

**Build Cost vs. ROI:**
- Cost: 50 story points ([VERIFY: labor cost]) = [VERIFY] likely $100k-300k
- ROI: (a) avoided regulatory fines ([VERIFY: estimate, likely multiples of cost]), (b) customer acquisition acceleration ([VERIFY: customer lifetime value × onboarding speed improvement]), (c) operational efficiency (reduced IT rollback tickets = [VERIFY: labor savings])
- [VERIFY] Total ROI likely positive within 12 months

**Competitive Differentiation:**
- Most financial services have sandboxes; ours differentiates on: (a) unified scope (all config types), (b) atomic promotion (all-or-nothing), (c) mutual exclusion (conflict prevention), (d) production data copy simulation (realistic), (e) full version history with point-in-time rollback
- Translates to: faster rule updates responding to fraud trends, stronger compliance posture (attracts regulated customers), lower IT overhead

**Customer Lifetime Value Impact:**
- Faster rule updates → better fraud detection → lower customer fraud loss
- Faster onboarding → faster revenue realization
- Compliance proof → customer trust and retention
- [VERIFY: estimate churn reduction or fraud loss reduction]

**Executive Messaging:** "Sandbox is non-negotiable regulatory requirement (BRD 12.8, 12.10, 12.12). Build it or face audit findings. Secondary benefit: faster onboarding and lower IT overhead. ROI strongly positive within 12 months."

---

## Q9. Stakeholder Management

**Key Stakeholders & Priorities:**
- Compliance analysts (the compliance team): ease of use, simulation speed, clear approval workflows
- Compliance managers: audit trail quality, approval audit, zero single-actor changes
- MLRO teams: visibility into risk score changes, meaningful approval power, audit export for exams
- GCP platform team: API stability, simulation SLA, data masking
- Compliance/Risk leadership: regulatory proof, zero incidents, on-time delivery

**Managing Conflicting Priorities:**
- Conflict 1: Analysts want fast simulation; GCP warns about SLA risk. Resolution: phase capacity increases; Phase 1 SLA [VERIFY: target]; Phase 2 optimize queries.
- Conflict 2: MLRO wants approval authority; analysts worry about delays. Resolution: escalation path—if pending >4 hours, MCO expedites.
- Conflict 3: Audit trail completeness vs. backend performance. Resolution: async logging (don't block promotion on audit write; retry if necessary).

**Securing Buy-In from Skeptics:**
- "Why mutual exclusion?" → Prototype merge scenario; show conflicts; explain atomic promotion requires serial consistency.
- "Simulation too slow?" → Show BRD 12.8 regulatory requirement; explain risk of untested promotions; prototype showing acceptable latency.
- "Two-step approval slows us down?" → Show approval cycle time acceptable ([VERIFY: target <2 hours]); emphasize regulatory requirement and risk reduction; offer expedited path for urgent changes.

**Scope Management:** Boundary: sandbox owns UI, workflow, promotion orchestration. Does not own: simulation job scheduling (GCP), data masking (data governance), identity/authorization (platform). When requests surface: classify as core vs. nice-to-have vs. dependency-delegate. Document in issue threads. Monthly refinement review backlog and reprioritize.

**Communication to Non-Technical Stakeholders:**
- Analogy: "Mutual exclusion is like a hardware lock—only one person at a time, safer."
- Before/after: "Before: rule changes go directly to production with no rollback. After: tested, two-person approval, instant rollback."
- Outcome focus: "Means faster rule updates and lower risk of customer harm."

---

## Q10. Execution & Delivery

**Sprint Breakdown (50 story points, 5 sprints):**
- **26.1.1 ([VERIFY] 8 pts):** Backend APIs + creation UI
- **26.1.2 ([VERIFY] 9 pts):** Lifecycle state management + detail view + sub-navigation
- **26.1.3 ([VERIFY] 14 pts):** Versioning + simulation workflow + progress tracking
- **26.1.4 ([VERIFY] 10 pts):** Two-step approval + atomic promotion
- **26.1.5 ([VERIFY] 9 pts):** Rollback + audit trail export

**Delivery Approach:** SAFe/PI planning, bi-weekly sprints.

**Milestones:**
- Sprint 26.1.1 complete: backend APIs ready for QA integration testing
- Sprint 26.1.2 complete: analysts can create sandboxes and navigate detail view
- Sprint 26.1.3 complete: end-to-end workflow functional (create → edit → submit → simulate → review)
- Sprint 26.1.4 complete: approval workflow integrated, atomic promotion tested
- Sprint 26.1.5 complete: rollback, audit trail export, production-ready

**Technical Risk Management:**
- Risk 1: GCP API latency. Mitigation: early spike on simulation latency; if SLA unmet, escalate to GCP team for optimization.
- Risk 2: Atomic promotion failures. Mitigation: design review, comprehensive test suite covering rollback scenarios.
- Risk 3: Approval workflow complexity. Mitigation: low-fidelity prototype with workflows team.
- Risk 4: UI lock contention under concurrency. Mitigation: load test with [VERIFY: target user count]; profile locking impact.

**UAT & Go-Live:**
- UAT: Week 1 of Sprint 26.1.6. Scripted test cases covering all workflows. Duration: 2 weeks.
- Soft launch: the compliance team only, 1 week. Monitor adoption, incident rate, approval turnaround.
- Hard launch: all markets after no issues.

**Training & Change Management:**
- Recorded walkthroughs (2 x 5 min each)
- In-person office hours (2 sessions for time zone coverage across 40+ markets)
- FAQ document
- Roll out 1 week before soft launch
- Email + in-app notifications on launch

**Quality Gates:**
- Code review pass rate: 100%
- Unit test coverage: >80%
- Integration test pass rate: 100%
- UAT pass rate: 100%
- Zero critical/high severity bugs within 2 weeks post-launch

---

## Q11. Competition & Differentiation

**Competitor Approaches:**
- Typical competitor: sandboxes created per rule/asset (fragmented), simulation on synthetic/mock data (not realistic), single-step approval (error-prone), rollback requires IT escalation (slow), limited version history
- Example: Competitor X allows rule changes in sandbox, simulates against mock data, no approval workflow—leaving compliance gaps

**Unified Sandbox Differentiation:**
1. **Unified scope:** All CRR config types (Rules, Assets, FA) editable in one sandbox, not fragmented. Prevents partial inconsistencies.
2. **Atomic promotion:** All changes commit or rollback together—no partial state. Competitors have no rollback or manual/risky rollback.
3. **Mutual exclusion:** Enterprise and Market sandboxes cannot coexist, preventing merge conflicts. Competitors allow concurrent sandboxes with reconciliation burden.
4. **Production data copy simulation:** Runs on masked real production data, not synthetic. Results reflect actual customer population behavior.
5. **Full version history with point-in-time rollback:** Rollback from any version, not just immediate prior. Competitors typically offer limited history.

**Customer/Compliance Messaging:**
- For analysts: "One place for all CRR changes. Edit rules, assets, FA simultaneously. Simulate results. Get two approvals. Promote atomically. Rollback instantly to any prior version."
- For compliance leadership: "Regulatory compliance built-in. Every change: justified, two-user approval, simulated, fully auditable. BRD 12.8, 12.10, 12.12 automatic."
- For executives: "Reduces regulatory fine risk, accelerates onboarding, cuts IT overhead. Competitive differentiation in regulated markets."

**Competitive Threats to Monitor:**
- Threat 1: Competitors accelerate sandbox adoption. Mitigation: sandbox is table-stakes; focus on launch speed and quality.
- Threat 2: Competitors build advanced approval workflows (conditional, escalation). Mitigation: two-step approval meets BRD 12.10; add advanced logic in Phase 2 if competitive pressure emerges.
- Threat 3: Competitors offer simulation-as-a-service. Mitigation: this is infrastructure; escalate GCP optimization if needed.

**Market Positioning:** American Express positions as the regulatory gold standard in financial risk decisioning. Unified Sandbox reinforces: "We take compliance seriously. We build tools that prevent mistakes, not recover from them. We trust analysts with powerful automation, but verify with two-step approval." Positions AXP as the risk platform for highly regulated segments (corporate banking, PEPs, sanctions).

---

## Q12. UX & Product Thinking

**Key UX Principles:**
1. **Clarity of state:** Sandbox state (Draft, Submitted, Approved, Promoted, Rejected) always visible. "Where am I in the workflow?" answered instantly.
2. **Progressive disclosure:** Initial view shows creation button only. After creation, progressively reveal edit tabs, submit button, approval status. Reduce cognitive load.
3. **Prevention of loss:** Exit-blocking modals for unsaved changes. "You have unsaved edits in Rules. Save or discard?"
4. **Audit transparency:** Every action logged and visible in timeline. Users understand history and verify compliance.
5. **Error prevention:** Before Submit, modal summarizes changes and requires justification. "Are you sure?" before crossing the Rubicon.

**Design for Low-Technical-Fluency Analysts:**
- Domain-specific language: "Submit for Simulation" not "commit"; "Asset 'US Market Default' not found" not "ReferenceError"
- Visual affordances: button states (disabled Submit if no changes), color coding (Green=Approved, Yellow=Pending, Red=Rejected), icons
- Progressive disclosure: novice analysts see simple workflows; experienced analysts see advanced options (cancel simulation, rollback to specific version)

**Error Scenarios & Edge Cases:**
- Edge case 1: User submits, leaves without reviewing results. Modal: "Simulation completed. Results pending. Leave anyway?"
- Edge case 2: User approves, then realizes error. Transition: Approved → Rejected (allow rework).
- Edge case 3: Two users create Enterprise sandboxes simultaneously. Message: "Enterprise sandbox exists. Wait or delete theirs."
- Edge case 4: Simulation times out. Retry button visible.

**Approval Workflow Efficiency:**
- Pre-approval: show first approver and alternate (parallel preparation)
- Approval summary: show only essential info (what changed, why, simulation results delta)
- Rejection shortcuts: re-edit in Draft without full rework
- Escalation: if pending >4 hours, auto-notify manager
- Together: [VERIFY] reduce approval cycle to <2 hours

**Audit Trail Usability:**
- Export CSV: Timestamp | User | Action | Object (Rules/Assets/FA) | Details | Justification | Approval Status
- Timeline view: action sequence on sandbox detail screen
- Example: "2024-01-15 10:00 - Alice created sandbox. 10:15 - Alice edited Rules. 10:30 - Bob submitted. 11:00 - Simulation complete. 11:10 - Charlie approved. 11:20 - Dave approved. 11:25 - Promoted."

**Simulation Results Simplification:**
- Dashboard view: aggregate metrics (X% moved Medium→High, avg delta +2.5)
- Sortable table: affected customer cohorts (filter by delta magnitude)
- Drill-down: click cohort to see individual customers
- Export: results CSV for advanced analysis

---

## Q13. Failure Mode Analysis

**Top 3 Failure Modes:**

**Failure Mode 1: Simulation Timeout/Failure**
- Impact: analyst cannot review results; approval becomes a guess. BRD 12.8 (simulation capability) unmet.
- Mitigation:
  - Set SLA [VERIFY: target <5 min]; monitor latency trends; escalate to GCP if SLA breached
  - Allow retry (non-blocking)
  - Allow proceeding with prior simulation data or skipping for expedited changes (rare, approval comment required)
  - Alert monitoring: if >X% of simulations fail per week, page on-call engineer
  - Test coverage: load test with [VERIFY: customer population size]; verify SLA

**Failure Mode 2: Atomic Promotion Partial Failure**
- Impact: inconsistent state; customer scoring broken. BRD 12.10 (atomic change) violated.
- Mitigation:
  - Pre-promotion validation: schema, referential integrity, rollback scenario test
  - Transaction rollback: Serializable isolation; any component failure → entire transaction aborts
  - Post-promotion verification: smoke test (rescore samples); if fail, auto-trigger rollback
  - Communication: if rollback occurs, user sees "Promotion failed. Rolled back. Contact support with code X."
  - Alert monitoring: zero tolerance for partial promotions

**Failure Mode 3: Approver Rubber-Stamps Risky Changes**
- Impact: bad config reaches production; two-step approval defeats itself.
- Mitigation:
  - Rejection workflow: Approver can revoke approval (Approved → Draft for rework)
  - Comment section: "I approve but with concerns about X" visible to second approver
  - Escalation: complex changes require both Approver and Manager sign-off
  - Training: emphasize approval is decision-making on risk, not rubber-stamp
  - Monitoring: if same approver pair consistently approves without reviewing, escalate to management

**Secondary Failure Modes:**
- Failure Mode 4: User deletes sandbox by mistake. Mitigation: soft delete, allow undelete within 24 hours.
- Failure Mode 5: Concurrent edits within sandbox. Mitigation: pessimistic locking, "locked by User A" message.
- Failure Mode 6: Audit trail corrupted/incomplete. Mitigation: database constraints (append-only), backup to S3 weekly.
- Failure Mode 7: Simulation results don't match production after promotion. Mitigation: post-promotion reconciliation job (24 hours), alert if delta >threshold.

**Rollback Failure Handling:**
- Rollback should succeed 100%—critical recovery mechanism
- Design: Rollback loads prior version from history (metadata operation, not recompute)
- If rollback fails: database corruption, system-level failure
- Mitigation: (a) version history replicated across regions, (b) weekly integrity checks (checksum), (c) alert: if any rollback fails, page entire on-call team
- SLA: 100% success rate

**Failure Testing:** Chaos engineering in staging. Inject failures: kill GCP connection, trigger constraint violations, slow queries, network partitions. Observe graceful degradation and user error messaging. Run weekly. Pre-launch: comprehensive failure scenario test matrix in UAT.

---

## Q14. Product Strategy & Future Vision

**Year 2 Roadmap:**

**Year 2 Phase 1 (Q1-Q2):** Advanced Approval Workflows
- Current: two-step approval (User A, User B)
- Future: conditional approval based on risk (low-risk = single approver, high-risk = three), risk-based escalation (>100k customers affected = auto-escalate to MCO), approval SLA enforcement (>X hours pending = escalate to manager)

**Year 2 Phase 2 (Q3-Q4):** Simulation Analytics
- Current: basic summary (X% moved to High risk)
- Future: ML models predicting approval cycle time, identifying high-risk rule changes early, recommending approval alternatives

**Year 2 Phase 3 (Year 2+):** Cross-Platform Simulation
- Current: sandbox isolated to CRR
- Future: when analyst updates CRR rules impacting fraud detection, simulation includes fraud impact (e.g., "This rule change reduces fraud detection accuracy by 2%")

**Relationship to CRR 2.0:** Sandbox is Feature 1. Downstream features depend on it:
- Feature 2 (ML-powered FA) requires sandbox versioning for model updates
- Feature 3 (Real-time rescoring at onboarding, BRD 12.12) requires sandbox-tested rules
- Feature 4 (Audit reporting) consumes sandbox audit trail

**Vision for Sandbox 2.0:** From "configuration change management" to "risk experimentation platform."
- Analyst creates sandbox to A/B test two rule sets against production customer population, comparing outcomes
- Requires: (a) multi-version comparison (results side-by-side), (b) statistical significance testing, (c) impact estimation (fraud loss vs. bad actor prevention)
- Year 3+ vision, dependent on FA maturity and analytics infrastructure

**Product-Market Fit Evolution:**
- Month 1: adoption rate (% using sandbox)
- Month 3: approval cycle time stability (approaching target SLA)
- Month 6: advanced features adoption (% using rollback, % using audit export)
- Month 12: user satisfaction (NPS [VERIFY: target 50+])
- Year 2: expansion to adjacent use cases (e.g., sandbox for Asset management)

**Strategic Long-Term Risks:**
- Risk 1: Approval bottleneck (cycle time >tolerance). Mitigation: monitor SLA; add parallel approval or escalation paths if breached.
- Risk 2: Simulation irrelevance (approvals rubber-stamped). Mitigation: training, culture shift, highlight cases where simulation prevented incidents.
- Risk 3: Technical debt (latency increase, reliability decrease). Mitigation: allocate 20% team capacity to debt; monitor SLA trends; refresh queries annually.

**Positioning for Future Regulatory Changes:** Current drivers: BRD 12.8, 12.10, 12.12. Likely future drivers: real-time impact reporting, federated approval, explainability. Sandbox design is extensible: audit trail format allows future fields (jurisdiction, attribution), approval workflow allows future steps, simulation results allow enrichment (explainability scores). Forward-thinking prevents future rewrites.

---

## Q15. Personal Ownership Filter

**My Contribution (End-to-End):**
- **Discovery:** 6+ interviews with the compliance team across 3 markets. Shadowed real rule change incident requiring IT rollback. Reviewed regulatory requirements (BRD 12.8, 12.10, 12.12) and mapped to technical solutions.
- **User Story Writing:** Authored all 11 stories with detailed AC covering state transitions, error scenarios, edge cases, regulatory compliance proof points.
- **Design Collaboration:** Led design reviews with backend/frontend engineers. Challenged assumptions. Ensured AC was testable.
- **Prototype Testing:** Facilitated low-fidelity prototype walkthroughs with analysts and MLRO teams. Feedback directly informed AC refinement.
- **Scope Management:** Pushed back on scope creep. Justified Phase 2 roadmap.
- **Regulatory Alignment:** Reviewed each story's AC against BRD requirements to ensure audit trail and maker-checker were non-negotiable.

**Biggest Challenge & Resolution:**
- Challenge: Balancing regulatory rigor (maker-checker is non-negotiable) with UX (approvals can slow updates).
- Engineers initially resisted two-step approval, fearing bottlenecks.
- My response: (a) user research showing typical cycle time <2 hours (acceptable), (b) proposed escalation path for urgent changes (fast-track approval), (c) prototype showing approval UI is dead simple (two checkboxes, comment, click Approve).
- Outcome: Shifted narrative from "approval is burden" to "approval is control we can optimize." Engineers bought in.

**Decision Most Proud Of:** Mutual exclusion constraint.
- Not intuitive—seems like limitation.
- Actually brilliant: prevents concurrent Enterprise/Market sandboxes, eliminating merge conflicts entirely. Makes atomic promotion feasible, eliminates rollback complexity.
- Engineers initially disliked (maximizing parallelization). Once I explained conflict scenarios and showed serialization is acceptable (analysts can schedule work), they agreed it's the right call.
- Subtle design choice that dramatically simplifies system and eliminates whole classes of bugs.

**Hindsight & Learnings:**
1. Would have started GCP SLA negotiation earlier (Month 2 instead of Month 4). Would have surfaced simulation latency concerns earlier, allowing more optimization time.
2. Would have run longer pilot with the compliance team (4 weeks instead of 1 week). More pilot time would have caught workflow nuances and reduced post-launch friction.

**Product Philosophy Reflected in Feature:**
- Core belief: constraints are features. Mutual exclusion, atomic promotion, two-step approval—these are constraints that prevent harm.
- I design for "safe complexity"—systems that are complex enough to be powerful, but constrained enough to be safe.
- Sandbox Versioning achieves this: analysts have flexibility (edit all config types), within safety rails (approval, simulation, rollback). No single actor can break production.
- This is product design in regulated domains: maximize capability within compliance constraints.

**Credit to Others:**
- The Director of Compliance and team: patience in user research and prototype feedback
- GCP platform team: committing to simulation SLA, building robust APIs
- Backend engineers: thoughtful atomic promotion design
- Frontend engineers: intuitive state management and approval UX
- Compliance/risk leadership: clarifying regulatory requirements, making sandbox non-optional
- Quality team: comprehensive UAT planning
- My role: orchestration and advocacy

---

## EXECUTIVE SUMMARY

The **Unified Sandbox Journey** is the foundational control mechanism for CRR 2.0, mandatory for BRD 12.8 (sandbox/simulation), BRD 12.10 (maker-checker approval), and BRD 12.12 (real-time rescoring). It consolidates all CRR configuration changes into a single, version-controlled, simulation-tested, two-step-approved, atomically-promoted workflow with full rollback capability.

**Key Success Factors:**
1. Mutual exclusion (conflict prevention) + Atomic promotion (all-or-nothing) = zero merge/rollback complexity
2. Production data copy simulation = realistic impact forecasting
3. Two-step approval from different users = BRD 12.10 compliance embedded
4. Full version history + point-in-time rollback = instant recovery from mistakes
5. Complete audit trail export = regulatory exam proof

**Stakeholder Alignment:** Analysts (ease of use, simulation speed), managers (audit quality, zero single-actor changes), MLRO (approval authority), leadership (regulatory proof, zero incidents). Clear trade-off management and escalation paths resolve conflicts.

**Delivery:** 11 stories, 50 points, 5 sprints (26.1.1-26.1.5). SAFe/PI planning, bi-weekly sprints. Risk mitigation on GCP SLA, atomic promotion failure scenarios, approval workflow complexity. UAT + soft/hard launch gates.

**Business Case:** Internal enabler for CRR modernization, customer onboarding acceleration, regulatory compliance. ROI strongly positive within 12 months (avoided fines >> build cost).

**Competitive Differentiation:** Unified scope, atomic promotion, mutual exclusion, production data copy simulation, point-in-time rollback. Positions AXP as regulatory gold standard in risk decisioning.

---
