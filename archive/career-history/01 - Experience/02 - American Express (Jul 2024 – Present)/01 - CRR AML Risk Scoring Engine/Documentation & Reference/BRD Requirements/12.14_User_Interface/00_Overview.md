# BRD 12.14 — User Interface / Experience

## Status
Yes (Incremental improvements)

## Target Timeline
Incremental improvements ongoing

## Bead Reference
career-context-vfj

## Business Requirement
Render CRR framework on UI.

## Purpose
Review framework with cross-market scanning.

## Expected Outcome
Enhanced UX for review and updates.

## Confirmed Details (from 12.3 Coaching)

### CRR Application — 6 Tabs:
| Tab | Purpose | Status |
|-----|---------|--------|
| **CRR** | Production read-only view of current framework | Built (12.14.1) |
| **Sandbox** | Customization workspace for rules/configuration | Built (12.3) |
| **Asset Manager** | View/edit data point configurations | Built (12.6) |
| **Fundamental Assessment** | View/edit FA gate configurations | Built (12.6) |
| **Reporting** | Reports and dashboards | Not Built (12.13) |
| **Alerts** | Notifications for significant events | Not Started (12.20) |

### UX Design Process:
- 20+ UX sessions conducted with designer (Mamta)
- User-centered design approach with business stakeholders (Charu, Heidi, Tahnee, Tejas)
- Incremental improvements ongoing based on user feedback

### Key UI Capabilities:
- **CRR tab** renders production framework (Categories → Elements → Weightings → Market overrides)
- **Market-specific view** allows selecting a market and comparing enterprise vs market deviations
- **Configuration Switcher** dropdown in sandbox to switch between Rules ↔ Assets ↔ FA editing
- **Export button** for framework download (PDF/spreadsheet)

## Sub-Requirements

| Sub-Req | Title | Status | Coaching Notes |
|---------|-------|--------|----------------|
| 12.14.1 | Framework Rendering | Yes | CRR tab — production read-only view of Categories, Elements, Weightings, Overrides |
| 12.14.2 | Market-Specific View | Yes | Enterprise vs Market comparison, side-by-side/overlay, cross-market scanning |
| 12.14.3 | Framework Download | Yes | PDF/spreadsheet download of framework views |
| 12.14.4 | Permission-Based View | Yes | Role-based visibility — fine-grained permissions pending 12.21 (IAM) |
| 12.14.5 | Customization Request UI | Yes | Maps to 12.2 Change Request — digitizing SharePoint CRR Customization Form |

## Interview Notes
- All 5 sub-requirements built and operational
- UI/UX is a strength of the POA implementation — 20+ design sessions
- CRR tab provides the read-only production view; Sandbox tab provides the editing workspace
