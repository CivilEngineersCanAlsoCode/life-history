# Asset Manager - Project Overview

## Quick Facts

| Dimension | Details |
|-----------|---------|
| **Project** | Asset Manager — centralized lifecycle management for AML/CFT risk policy lists |
| **Company** | American Express |
| **Role** | Senior Associate Product Manager |
| **Timeline** | Jul 2024 – Present |
| **Status** | Delivered; in production across 40+ markets |
| **Impact** | [VERIFY: time-to-update before vs after]; [VERIFY: annual value]; [VERIFY: active users]; [VERIFY: assets prosets promoted; zero incidents |

---

## The Problem

Reference data lists (Industry, Geography, Company Structure, Acquisition Channel, Notable Lists) used to configure AML/CFT risk rules across 40+ markets were managed manually outside the CRR platform:

- **Time to update:** [VERIFY] 26 days average (formal BRD → Engineering queue → development → testing → deployment)
- **Audit trail:** None (regulatory compliance gap)
- **Consistency:** Different markets operated different versions of the same list
- **Scale:** 30M+ daily transactions scored against these lists
- **Risk:** A single inconsistency could propagate across 40 markets and millions of transactions

**Root cause:** Compliance analysts owned the business logic but lacked operational control.

---

## The Solution

Asset Manager is a sandbox-driven lifecycle management system with these core capabilities:

### Architecture
- **Sandbox-first:** All asset operations occur in sandboxes (Enterprise or Market level) before production promotion
- **Hierarchical ownership:** Enterprise defines shared assets (5 core types: Acquisition Channel, Industry, Geography, Company Structure, Product); markets inherit with copy-on-write option
- **Versioning:** Immutable versions; changes create new versions; enables audit clarity
- **Copy-on-write workflow:** Market teams can customize shared assets for local regulatory requirements without affecting enterprise versions

### Key Features Delivered
1. **Asset creation** within sandbox context with reference data validation (pattern matching, fuzzy matching)
2. **State transitions:** Draft → Sandbox → Production with automatic usage metadata tracking
3. **Shared asset visibility:** All assets visible everywhere (Enterprise + Market sandboxes) with visual indicators
4. **Copy-on-write customization:** Shared assets can be forked locally; automated divergence detection flags stale copies
5. **Enterprise propagation:** Updates to enterprise assets automatically propagate to dependent market sandboxes on promotion
6. **Excel export:** Two-sheet format (Values + References) for audit validation against external sources
7. **Read-only view:** Compliance analysts can view assets without edit capability
8. **Complete audit trail:** Who/what/when/why for every change; 15-minute undo window for promotions

---

## Key Innovation: Copy-on-Write

The copy-on-write architecture was the breakthrough that enabled both enterprise governance and market flexibility:

**Traditional approaches:**
- Full enterprise control: Too restrictive; markets need local customization for regulatory differences
- Full market autonomy: Creates duplicates and inconsistency across 40+ markets

**Copy-on-write solution:**
1. Enterprise defines reference assets (e.g., Geography list with all ISO countries)
2. Market inherits asset automatically
3. When market analyst edits a shared asset, system creates a local copy (fork)
4. Enterprise version remains unchanged
5. Automated divergence detection helps analysts decide: merge updates, keep local, or deprecate

This solved the core tension: market autonomy + enterprise consistency.

---

## Discovery & Validation

**User Research:** 20+ sessions with compliance analysts, MLRO leads, CRR administrators across US, UK, Asia-Pacific

**Key Findings:**
- Current cycle time: 26 days average
- Backlog: [VERIFY] 80+ asset-related feature requests pending over 18 months
- Pain points: Loss of agency, inconsistency, audit gaps, Engineering bottleneck
- Copy-on-write insight: [VERIFY] 8 of 8 compliance analysts said market customization is essential for regulatory compliance

**Validation:**
- [VERIFY] 94% would switch to self-service if available
- [VERIFY] 89% cited audit trails as must-have
- [VERIFY] 78% adoption within 30 minutes of launch (post-delivery)

---

## Execution & Delivery

**SAFe PI Cadence:** 5 sprints, 40 story points

**Sprint Breakdown:**
- **Sprints 1-2:** Core CRUD + sandbox context (foundational engine)
- **Sprint 3:** Audit trail + state transitions
- **Sprint 4:** Copy-on-write workflow + visual indicators
- **Sprint 5:** Excel export + read-only view

**Major Challenge:** Copy-on-write complexity
- Initially estimated as one-sprint feature during planning
- Sprint 3 implementation revealed complex distributed versioning problem
- Required deeper database schema changes than anticipated
- **Decision made:** Extended PI by one sprint (mid-PI re-plan) to deliver properly
- **Outcome:** Preserved quality over deadline; gained stakeholder trust

**UX Challenge:** Copy-on-write comprehension
- UAT revealed [VERIFY] 40% of analysts didn't understand copy-on-write concept
- Initial SUS score: [VERIFY] 68 (below 70 threshold)
- **Actions:** Renamed feature to "Create Local Copy", added visual decision helper, improved UI
- **Result:** SUS improved to [VERIFY] 81 (excellent); [VERIFY] 78% adoption in first 30 minutes post-launch

---

## Metrics & Impact

### Time-to-Asset-Update (North Star)
| Metric | Baseline | Target | Actual |
|--------|----------|--------|--------|
| Time-to-update (days) | [VERIFY] 26 | <8 (80% of updates) | [VERIFY] 3.2 |
| Improvement | — | 69% | [VERIFY] **84%** |

### Adoption & Usage
- Active users (week 2): [VERIFY] 87 compliance analysts
- Assets created in sandbox: [VERIFY] 1,200+
- Assets promoted to production: [VERIFY] 400+
- Production incidents: [VERIFY] 0
- User satisfaction: [VERIFY] 4.3/5 stars

### Business Impact
| Dimension | Value |
|-----------|-------|
| **Annual time savings** | [VERIFY: annual time savings in dollar value] |
| **Risk mitigation** | [VERIFY: risk mitigation value estimate] |
| **Total annual value** | [VERIFY: total annual value] |
| **Delivery cost** | [VERIFY: delivery cost] |
| **ROI** | [VERIFY] 2.7x (year one) |
| **Payback period** | [VERIFY] 4.4 months |

### Operational Improvements
| Metric | Baseline | Post-Launch | Improvement |
|--------|----------|-------------|-------------|
| BRD tickets to Engineering | [VERIFY] 40/month | [VERIFY] 2/month | [VERIFY] 95% ↓ |
| Consistency drift (markets) | Unmeasured | <5% | N/A |
| Audit findings | [VERIFY] 2 per cycle | [VERIFY] 0 | [VERIFY] 100% ↓ |

---

## What I Own & Drive

**Full product leadership:**
1. **Strategy & Vision:** Articulated problem statement, secured executive buy-in, defined success metrics
2. **Discovery & Validation:** Conducted 20+ user research sessions, synthesized findings, validated solution approach
3. **Design Direction:** Iterated on design with UX designer and user feedback, pushed for quality
4. **Roadmap Prioritization:** Weighted scoring framework (regulatory risk 40%, user pain 30%, effort 20%, dependency 10%)
5. **Stakeholder Management:** Regional sessions, negotiation, continuous engagement
6. **Delivery Accountability:** 5-sprint SAFe cadence, mid-PI re-planning, risk management

**Critical decisions I made:**
- **Copy-on-write architecture:** Synthesized competing stakeholder needs (market autonomy vs. enterprise governance)
- **Phased delivery:** Sequenced complexity (CRUD π1, copy-on-write π2, audit export π3)
- **Mid-PI re-plan:** Extended timeline for copy-on-write quality despite deadline pressure
- **UX redesign:** Pushed for iteration when SUS score [VERIFY] failed, despite time impact
- **Validation approach:** Shipped as suggestions-only to prevent false positives until tuning completed

**What fails without me:**
- Copy-on-write wouldn't exist (required synthesis of competing interests)
- Stakeholder alignment wouldn't hold (requires continuous regional engagement)
- Product quality wouldn't survive roadmap pressure (requires principled advocacy)

---

## Hardest Parts

### Challenge 1: Copy-on-Write Complexity
- Initially underestimated as simple "fork" operation
- Mid-implementation discovered complex distributed versioning requirements
- Required consistency guarantees across 40+ market sandboxes
- **Decision:** Extend PI by 1 sprint rather than ship broken feature
- **Learning:** Technical spike in Sprint 0 would have caught this

### Challenge 2: UX Comprehension
- UAT revealed users didn't understand copy-on-write despite explanation
- SUS score of 68 was wake-up call
- **Resolution:** Pushed for design iteration; renamed feature; added visual helpers
- **Learning:** Domain experts ≠ SaaS power users; don't assume product literacy

### Challenge 3: Stakeholder Communication
- Market teams surprised by launch (hadn't been involved early)
- Created expectation misalignment and initial resistance
- **Resolution:** Hosted 4 regional sessions explaining roadmap, benefits, launch timeline
- **Learning:** Involve stakeholders earlier; early communication cheaper than late resistance

---

## Post-Launch Roadmap

**Phase 2 (Next PI):**
- Role-based access control (Approver, Reviewer roles)
- External data integrations (SWIFT, ISO, Refinitiv OFAC)
- Auto-population of assets from official sources

**Phase 3 (PI+2):**
- Asset templates (Country List, Person List, Product List patterns)
- Bulk import for legacy system migration
- Onboard 10+ new markets

**Year 2 Vision:**
- Asset usage analytics (which assets drive risk score changes?)
- Asset effectiveness metrics (do assets drive high SAR counts?)
- Predictive recommendations (ML models for asset values)
- Auto-rules generation (define thresholds, rules auto-generate)

---

## Why This Matters

Asset Manager unblocked downstream roadmap items that depended on self-serve asset management:
- Automated rules generation
- Market-level alert customization
- Third-party risk integrations

[VERIFY] This capability enabled CRR's expansion from 8 markets to 40+ markets in 18 months. The manual asset management model couldn't have scaled.

More broadly, Asset Manager represents a strategic shift: compliance teams now own and control risk thresholds in real-time instead of waiting weeks for Engineering cycles. This is a foundational capability enabling CRR's evolution toward a self-serve risk intelligence platform.

---

## Contact & Next Steps

For questions about Asset Manager, specific use cases, or technical architecture details, refer to the full resume brain document or template answers (15 core questions).

**Key interview talking points:**
1. Problem clarity: 26-day cycle time, audit gaps, inconsistency risk across 40+ markets
2. Innovation: Copy-on-write architecture (market autonomy + enterprise governance)
3. Validation: 20+ research sessions proved market teams needed customization
4. Execution: 5-sprint delivery, mid-PI re-plan for quality, UX iteration under pressure
5. Impact: [VERIFY: % time reduction], [VERIFY: annual value], [VERIFY: active users], [VERIFY: incidents]

---
