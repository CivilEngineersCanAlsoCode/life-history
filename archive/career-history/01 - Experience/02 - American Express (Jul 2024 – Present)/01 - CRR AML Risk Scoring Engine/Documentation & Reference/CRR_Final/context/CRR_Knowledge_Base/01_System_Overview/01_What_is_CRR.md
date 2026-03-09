# CRR System Overview

## What is CRR?

**Customer Risk Rating (CRR)** is an enterprise-wide compliance platform used to calculate and manage risk ratings for customers across multiple markets.

### Core Function
CRR evaluates customer risk based on configurable rules and produces a **risk score from 1-10**:
- **1-3** = Low Risk
- **4-6** = Medium Risk
- **7-9** = High Risk
- **10** = Prohibited

---

## Business Context

### Who Uses CRR?
| User Type | Role | Access Level |
|-----------|------|--------------|
| **CRR Business Users** | Compliance Analysts, Risk Managers | Full edit access to rules, assets, FA |
| **Market Compliance Officers (MCOs)** | Regional Compliance Leads | View-only access to production |

### Where is CRR Used?
- Multiple global markets (India, China, US, etc.)
- Enterprise-level configuration affects all markets
- Market-level configuration is specific to one market

---

## Key Problem Being Solved

### Current State Issues

| Problem | Impact |
|---------|--------|
| **Independent Merges** | Rules and assets can reach production in untested combinations |
| **Partial Logic States** | Production may contain configurations never simulated together |
| **Explainability Gaps** | Cannot trace why a customer's CRR changed |
| **Cross-Market Risk** | Market changes can unintentionally affect other markets |

### CRR 2.0 Solution
- **Unified Sandbox** workflow for all changes
- **Atomic promotions** - all related changes go together
- **Versioning** - every change creates auditable version
- **Simulation** - mandatory testing before production

---

## Core Principles

### 1. Atomicity
A risk decision is not a single rule change or asset change. It is a **coordinated set of changes** that includes:
- Rule updates
- Asset updates
- Fundamental Assessment updates
- Joint simulation
- Single approval
- Single promotion

### 2. Versioning
- Every edit creates a new version
- Old versions are archived, never deleted
- Complete audit trail maintained

### 3. Auditability
- Every change is tracked with:
  - Who made it
  - When it was made
  - What was changed
  - Why (justification comments)

### 4. Sandbox-First
- No direct production edits
- All changes go through sandbox
- Simulation required before approval
- Two-level approval for production promotion

---

## System Components Overview

| Component | Purpose |
|-----------|---------|
| **Risk Framework** | Categories, Elements, Rulesets, Rules |
| **Asset Manager** | Reusable lists/values for rules |
| **Fundamental Assessment (FA)** | Pre-scored attributes (Countries, Industries, etc.) |
| **Sandbox** | Editing workspace with versioning |
| **Reporting** | Risk distribution dashboards |
| **Alerts** | Configurable notifications |

---

*Next: See `02_Risk_Framework/` for detailed hierarchy documentation.*
