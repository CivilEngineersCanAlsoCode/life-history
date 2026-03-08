# CRR 2.0 FEATURES - EXECUTIVE SUMMARY

---

## FEATURE 1: UNIFIED SANDBOX JOURNEY

### Feature Description

The Unified Sandbox Journey consolidates all CRR configuration changes (Rules, Assets, Fundamental Assessment) into a single, version-controlled sandbox workflow where users create sandboxes with Enterprise or Market scope, make edits across all configuration types in Draft state, submit for simulation to test against production data, review results, obtain two-step approvals, and promote changes atomically to production with full rollback capability—ensuring that no partial or untested configurations reach production while maintaining complete audit lineage from sandbox creation through implementation, with mutual exclusion between Enterprise and Market sandboxes preventing conflicting simultaneous changes.

---

### Feature Acceptance Criteria (High-Level)

- ✅ Users can create Enterprise or Market sandboxes with automatic baseline copying from production
- ✅ Enterprise and Market sandboxes cannot coexist simultaneously (mutual exclusion enforced)
- ✅ All configuration types (Rules, Assets, FA) are editable within single sandbox context with sub-navigation
- ✅ Uncommitted changes accumulate in Draft state until Submit creates immutable version snapshot
- ✅ Submit for Simulation displays change summary modal requiring justification before proceeding
- ✅ Simulation runs on production data copy with real-time progress tracking and cancellation capability
- ✅ Simulation results display risk distribution changes with option to rollback or continue to approval
- ✅ Two-step approval workflow requires two different users to approve before implementation
- ✅ Atomic promotion merges all changes (Rules + Assets + FA) in single transaction with full rollback on any failure
- ✅ Enterprise asset version updates automatically propagate to all markets using the asset upon promotion
- ✅ Rollback creates new version from historical baseline (non-editable states) or overwrites uncommitted changes (Draft state)
- ✅ Version history displays all versions with timestamps, users, status, and justification comments
- ✅ Complete audit trail exports showing all actions (edits, submissions, approvals, implementations) with who/what/when/why
- ✅ Rejection transitions sandbox to Rejected state with detailed error comments in rejection field
- ✅ Exit-blocking modals prevent accidental navigation loss when unsaved changes exist

---

### User Story Breakdown

| Story ID | Story Name | What to Achieve | Sprint | Points |
|----------|------------|-----------------|--------|--------|
| **1.1** | Sandbox Data Model and Backend API Foundation | Create database schema for sandboxes with lifecycle states, versioning support, and core CRUD API endpoints (create, read, update, delete sandboxes) | 26.1.1 | 5 |
| **1.2** | Sandbox Creation UI with Scope Selection | Build UI for creating sandboxes with Enterprise/Market dropdown, enforce mutual exclusion (disable markets when Enterprise active, disable Enterprise when Market active), and display blank state when no production exists | 26.1.1 | 3 |
| **1.3** | Sandbox Lifecycle State Management Backend | Implement state transition validation logic ensuring sandboxes progress through correct lifecycle (Draft → In Progress → Testing Completed → Pending Approval → Implemented/Rejected) with business rule enforcement | 26.1.2 | 5 |
| **1.4** | Sandbox Detail View with Sub-Navigation | Create sandbox detail page with dropdown/tabs for Rules/Assets/FA configuration types, maintain sandbox context across navigation, and implement exit-blocking modal for unsaved changes | 26.1.2 | 4 |
| **1.5** | Sandbox Versioning - Create Version and Snapshot Logic | Capture all uncommitted changes (rules, assets, FA) as immutable version snapshot when user submits, link versions to specific component versions, and support version history retrieval | 26.1.3 | 5 |
| **1.6** | Submit for Simulation Workflow with Confirmation Modal | Build submit UI displaying change summary modal (rules/assets/FA modifications), require justification comment, create version on confirm, and trigger simulation API call | 26.1.3 | 5 |
| **1.7** | Simulation Progress Tracking UI with Polling | Display real-time progress updates via polling (every 5 seconds), show progress bar with percentage and estimated time remaining, provide cancel simulation capability, and handle completion/failure notifications | 26.1.3 | 4 |
| **1.8** | Two-Step Approval Workflow Backend and UI | Implement approval process requiring two different users to approve (validate second approver ≠ first approver), support rejection with mandatory comments, and maintain approval audit trail | 26.1.4 | 5 |
| **1.9** | Atomic Promotion to Production with Transaction Rollback | Merge all sandbox changes (rules + assets + FA) in single database transaction, implement full rollback if any component fails, propagate enterprise asset versions to all markets, and transition sandbox to Implemented or Rejected state | 26.1.4 | 5 |
| **1.10** | Rollback Functionality - Create New Version from Historical | Build rollback UI to create new editable version copying historical version's configuration (from non-editable states) or overwrite uncommitted changes with historical config (from Draft state) | 26.1.5 | 5 |
| **1.11** | Complete Audit Trail Export and History View | Create audit trail export to CSV with all sandbox actions (edits, versions, approvals, implementations), display audit history timeline in UI grouped by version, and support filtering by component type | 26.1.5 | 4 |

**Feature 1 Total: 11 stories, 50 points**

---

## FEATURE 2: ASSET MANAGER

### Feature Description

The Asset Manager feature provides centralized, sandbox-driven lifecycle management for reusable risk policy lists (assets) where users create assets within sandbox context with reference data validation, all assets remain visible everywhere with visual indicators distinguishing shared (multi-market) from local (single-market) assets, editability rules enforce Draft assets as globally editable while Sandbox assets require versioning (Enterprise/local) or copy-on-write workflow (Market/shared), Enterprise sandbox edits automatically propagate new asset versions to all markets upon promotion, and users can export assets to two-sheet Excel workbooks (Values + References) for audit and documentation purposes—eliminating file-upload duplication problems and ensuring consistent risk policy enforcement across the enterprise with complete audit trails.

---

### Feature Acceptance Criteria (High-Level)

- ✅ Assets can only be created within sandbox context (not in standalone view) with reference data validation
- ✅ Asset status transitions automatically from Draft → Sandbox when first used in any rule with usage metadata tracking
- ✅ All assets are visible everywhere (Enterprise and Market sandboxes) regardless of status or scope
- ✅ Visual indicators (color accents, not text labels) distinguish shared assets from local assets
- ✅ Draft assets are editable everywhere with changes immediately visible globally (no versioning)
- ✅ Local Sandbox assets (used only in one market) are editable with versioning in their home market
- ✅ Shared Sandbox assets (used in multiple markets or Enterprise) trigger copy-on-write workflow in Market sandboxes
- ✅ All Sandbox assets are editable with versioning in Enterprise sandbox regardless of usage scope
- ✅ Copy-on-write workflow prompts user to create copy with default name "{AssetName}_copy" and real-time duplicate validation
- ✅ Copy creation opens Edit Asset modal with pre-filled fields (name, description, list name disabled, CSV pre-loaded)
- ✅ Duplicate name validation runs on modal open and as user types with inline error and Save button disabled until unique
- ✅ Enterprise asset version updates automatically propagate to all markets using that asset upon sandbox promotion
- ✅ Asset export generates two-sheet Excel: Values sheet (all values) + References sheet (where used with human-readable columns)
- ✅ Asset deletion only allowed for Draft status assets not used in any rules (blocked for Sandbox/Production)
- ✅ Standalone Asset Manager view displays only Production assets filtered by selected market (read-only, Export only)

---

### User Story Breakdown

| Story ID | Story Name | What to Achieve | Sprint | Points |
|----------|------------|-----------------|--------|--------|
| **2.1** | Asset Data Model and Core CRUD APIs | Create database schema for assets with lifecycle status, version tracking, usage metadata tables, and core API endpoints (create, read, update, delete, validate) with reference data validation | 26.1.1 | 5 |
| **2.2** | Asset Creation UI in Sandbox Context | Build asset creation modal within sandbox with form fields (name, description, list name dropdown, CSV upload), real-time duplicate name validation, and reference data validation on save | 26.1.2 | 4 |
| **2.3** | Asset Status Transition from Draft to Sandbox on First Use | Implement automatic status update when asset is first selected in rule, create usage metadata records linking asset to rule/ruleset/market, and support usage retrieval API | 26.1.2 | 5 |
| **2.4** | Asset Visibility - All Assets Visible with Indicators | Build asset list view showing all assets (Draft/Sandbox/Production) with visual color indicators for shared assets, tooltips showing usage details, and consistent display across Enterprise and Market sandboxes | 26.1.3 | 4 |
| **2.5** | Asset Editability Rules - Draft, Local, and Shared | Implement backend editability check API returning editable flag and edit mode (direct/version/copy_required) based on asset status, sandbox scope, and usage metadata (local vs shared detection) | 26.1.3 | 5 |
| **2.6** | Copy-on-Write Workflow with Duplicate Name Validation | Build shared asset edit flow with confirmation modal, open Edit Asset modal pre-filled with "{OriginalName}_copy" default, implement real-time duplicate validation on modal open and as user types, disable Save until unique name entered | 26.1.4 | 5 |
| **2.7** | Enterprise Asset Versioning and Automatic Market Propagation | Implement asset version creation on edit in Enterprise sandbox, capture version in sandbox snapshot, and automatically update all markets' rule references to new version upon atomic promotion with audit logging | 26.1.4 | 5 |
| **2.8** | Asset Export with Two-Sheet Workbook Format | Build export functionality generating Excel with Values sheet (one column, all values) and References sheet (Scope/Status/Risk Category/Element/Ruleset/Rule using human-readable names, not IDs), filename format "{AssetName}_v{version}.xlsx" | 26.1.5 | 4 |
| **2.9** | Standalone Asset Manager Read-Only View | Create standalone Asset Manager tab with market dropdown filter, display only Production assets used in selected market, show Export action only (no Edit/Delete), and implement read-only asset detail view | 26.1.5 | 3 |

**Feature 2 Total: 9 stories, 40 points**

---

## COMBINED SPRINT ALLOCATION

| Sprint | Stories | Total Points | Focus Area |
|--------|---------|--------------|------------|
| **26.1.1** | 1.1, 1.2, 2.1 | 13 | Backend foundations (sandbox + asset data models and APIs), basic sandbox creation UI |
| **26.1.2** | 1.3, 1.4, 2.2, 2.3 | 18 | Lifecycle management, sandbox detail view with sub-nav, asset creation, status transitions |
| **26.1.3** | 1.5, 1.6, 1.7, 2.4, 2.5 | 23 | Versioning, simulation workflow, progress tracking, asset visibility and editability rules |
| **26.1.4** | 1.8, 1.9, 2.6, 2.7 | 20 | Approvals, atomic promotion, copy-on-write workflow, enterprise asset propagation |
| **26.1.5** | 1.10, 1.11, 2.8, 2.9 | 16 | Rollback, audit trail, asset export, standalone read-only view (finishes mid-sprint) |

**Grand Total: 20 stories, 90 points across 5 sprints**

---

**This document is optimized for team review meetings - scan the one-liners to understand scope, then reference full user stories for implementation details.**

**Perfect! I now have complete clarity. Let me write the full feature structures.**

---

# FEATURE 1: UNIFIED SANDBOX JOURNEY

## 1. Description (User Voice Format)

**As a** Compliance Analyst / Manager,  
**I should be able to** create, manage, version, simulate, approve, and promote all CRR configuration changes (Rules, Assets, Fundamental Assessment) within a single, unified Sandbox workflow,  
**so that** all changes are tested together as one atomic risk decision, ensuring no partial or untested configurations reach production, and maintaining full audit lineage from sandbox creation through production implementation.

---

## 2. Benefit to Business

This feature eliminates the critical risk of independent rule and asset promotions that could create untested production states, ensuring that every CRR change is simulated, reviewed, and approved as a complete risk decision before implementation. By consolidating all configuration types (Rules, Assets, Fundamental Assessment) into a single sandbox lifecycle with mutual exclusion between Enterprise and Market scopes, the system prevents conflicting changes, provides clear audit trails, and supports regulatory compliance requirements. Business users gain confidence that production CRR always reflects deliberate, validated risk policies, reducing AML audit risk and manual error while increasing productivity through streamlined change management workflows.

---

## 3. Verbatim Requirement from BRD

**BRD 12.8:** "System should support sandbox simulation functionality providing multiple instances and effective monitoring capabilities."

**BRD 12.8.1:** "System should have the capability to run CRR simulations to analyze the impact of any CRR update to the risk distribution."

**BRD 12.8.2:** "The underlying data used in the simulation/sandbox should a production copy."

**BRD 12.8.3:** "Access to the Sandbox will be controlled by User Access Permissions (should be configurable)."

**BRD 12.8.4:** "Multiple instances should be available for the Business (ability to run 4 instances in parallel). There should be ability to limit the sandbox to > Enterprise > Market/Center specific > Legal Entity > Product"

**BRD 12.8.5:** "At the time of submitting/triggering a sandbox simulation, system should prompt the user to confirm that all the updates being made are in line with the required enhancement/change request (the elements that have been modified should be rendered/highlighted on the UI for easy reference/validation)."

**BRD 12.8.6:** "The system must have the capability to track/display the progress of the simulation exercise. The estimated time to completion must also be displayed."

**BRD 12.8.7:** "System must notify pre-defined set of users on Sandbox completion or if there was an issue encountered in completing the process."

**BRD 12.8.8:** "The system must have capability to allow a simulation exercise to be cancelled at any point. The user will be required to confirm the cancellation."

**BRD 12.8.9:** "All reference data sets that are referenced by the CRR module should be available in the Sandbox environment. In particular (and as example) - Notable Lists, Centralized List/Fundamental Assessments"

**BRD 12.8.10:** "For any sandbox/simulation exercise, the system must be able to display the details of all the components that were modified (element, weight, multiplier etc.,)."

**BRD 12.8.12:** "System must maintain version control of all changes made. This must be available on the Sandbox UI."

**BRD 12.8.13:** "Updates made in the course of a simulation should be on top of the previous changes made (should not override prior updates). System must highlight the updates that are already in flight (in another sandbox) and allow the user to merge the changes (optional)."

**BRD 12.9:** "System should provide the ability for users to review results from simulation exercises for better decision making and analytics."

**BRD 12.7:** "System should be able to keep track of all updates made to the CRR framework and reference lists."

**BRD 12.7.1:** "System must track and make available for viewing any change made to a List / Risk Element / Risk Category - weight and multiplier (add/modify/delete with who/when and any justification)"

**BRD 12.7.2:** "Version history of the CRR module (enterprise level, market/center level and legal entity) must be maintained with a log of all the changes made to the underlying components (Lists/ Risk Element / Risk Category - weight and multiplier) along with user/implementation date details"

---

## 4. User Scenarios / Functional Requirements

### 4.1 Sandbox Creation and Scope Selection

Business users access the Sandbox tab where they can create new sandboxes with Enterprise or Market scope. On initial blank state (no production exists), only Enterprise scope is available in the dropdown. After production exists, users can select either Enterprise or any Market (India, France, Spain, etc.). The system enforces mutual exclusion: if an Enterprise sandbox is active, Market options are disabled; if any Market sandbox is active, Enterprise option is disabled. Users see clear tooltip messages explaining why certain options are unavailable. When creating a sandbox, the system automatically copies the latest production configuration as the baseline, including all rules, assets, and fundamental assessment settings for the selected scope.

### 4.2 Sandbox Lifecycle States

Sandboxes progress through clearly defined states: Draft (editable), In Progress (simulation running), Testing Completed (simulation results available), Pending Approval 1, Pending Approval 2, Rejected, Cancelled, and Stale. Each state has specific allowed actions and UI indicators. Draft state allows full editing of rules, assets, and fundamental assessment. Non-editable states (In Progress through Pending Approval) lock all configuration changes but allow viewing and analysis. The Rejected state includes error comments explaining why implementation failed. Stale state indicates production was updated by another sandbox and requires user action.

### 4.3 Unified Configuration Editing

Within a sandbox, users navigate between Rules, Assets, and Fundamental Assessment using a sub-navigation dropdown or tabs, maintaining sandbox context at all times. All edits across these three configuration types accumulate as uncommitted changes in Draft state. Exit-blocking modals prevent accidental navigation loss when unsaved changes exist. Users can edit rules (add/modify/delete rulesets and rules), edit assets (create new, edit existing based on editability rules), and modify fundamental assessment Q&A and overrides, all within the same sandbox session.

### 4.4 Sandbox Versioning

All edits remain uncommitted until the user clicks "Submit for Simulation," which creates Version 1 as an immutable snapshot of the complete configuration (rules + assets + fundamental assessment). Users cannot see incremental change history within Draft state; all changes are treated as work in progress. After reviewing simulation results, users can click "Create New Version" to start a new draft that builds on the previous version's baseline. The system supports rollback functionality: from non-editable states, rollback creates a new version copying the selected historical version's configuration; from Draft state, rollback overwrites current uncommitted changes with the selected version's configuration. Version history displays all versions with timestamps, user information, and status.

### 4.5 Submit for Simulation Workflow

When users submit a sandbox, the system captures a snapshot of all components (rules, assets, fundamental assessment) and locks the sandbox into "In Progress" state. A confirmation modal displays all modified components (highlighted elements, weights, multipliers, asset changes, FA answer changes) for user validation. The system triggers simulation on a production data copy and displays progress indicators with estimated time to completion. Users can cancel the simulation at any point with confirmation prompt. Upon completion or failure, the system notifies predefined users via email/notification. Simulation results show risk distribution changes, impacted customer counts, and detailed component-level impacts.

### 4.6 Approval Workflow

After simulation completion, the sandbox enters "Testing Completed" state where users can review results and decide to proceed or rollback. The system requires two-step approval by two different users (Pending Approval 1, Pending Approval 2) with audit trail of approver identities and timestamps. Approvers can review simulation results, change summaries, and justification comments before approving or rejecting. Rejection transitions sandbox to "Rejected" state with mandatory comments explaining the decision. Approved sandboxes move to final implementation stage.

### 4.7 Atomic Implementation (Promotion to Production)

When implementation is triggered, the system performs atomic promotion of all components (Rules + Assets + Fundamental Assessment) in a single database transaction. If any component fails to merge (database deadlock, validation error, etc.), the entire transaction is rolled back with NO partial commits. The sandbox transitions to "Rejected" state with detailed error messages in comments field (example: "Implementation failed: Database deadlock on asset table. Please retry or contact support."). Upon successful promotion, all changes become active in production simultaneously, the sandbox is removed from active list, production configuration is updated, and all markets using enterprise assets automatically receive new versions.

### 4.8 Enterprise vs Market Mutual Exclusion

The system strictly enforces that Enterprise and Market sandboxes cannot coexist. When an Enterprise sandbox exists (any state from Draft through Pending Approval), the "Add Risk Assessment" button for all markets is disabled with tooltip: "Cannot create Market sandbox while Enterprise sandbox is active." When any Market sandbox exists, the Enterprise option is disabled with tooltip: "Cannot create Enterprise sandbox while Market sandbox is active." This mutual exclusion eliminates the need for stale detection and conflict resolution between Enterprise and Market changes, simplifying the architecture and ensuring clear change ownership.

### 4.9 Audit and Traceability

The system maintains complete audit logs for all sandbox activities: sandbox creation (user, timestamp, scope, baseline version), all configuration edits (component type, old value, new value, user, timestamp), version creation events (version number, snapshot details, user, timestamp), simulation triggers and results (simulation ID, start time, end time, status, result summary), approval actions (approver user, timestamp, decision, comments), and implementation events (promotion timestamp, success/failure status, error details if failed). All audit data is exportable for regulatory review and includes mandatory justification comments for key actions.

---

## 5. Non-Functional Requirements

**Performance:**  
Sandbox creation must complete within 5 seconds. Configuration edits must save within 2 seconds. Simulation progress must update in real-time (polling interval ≤ 5 seconds). Simulation completion notification must be sent within 1 minute of completion. Atomic implementation transaction must complete within 30 seconds for typical sandbox size (50 rules, 20 assets, 10 FA overrides).

**Security:**  
All sandbox operations require authentication via Active Directory Services (ADS). Role-based access control enforces CRR Business User permissions for sandbox creation and editing. Two-factor approval required for production implementation. All API calls must be authenticated and authorized. Audit logs must be tamper-proof and encrypted at rest.

**Scalability:**  
System must support up to 4 concurrent sandboxes (1 Enterprise + 3 Markets, or 4 Markets) without performance degradation. Simulation must handle population sizes up to 10 million customer accounts within acceptable SLA (example: 5 hours as per BRD 12.18.6). Version history must accommodate up to 10 versions per sandbox without pagination delays.

**Compliance:**  
All changes must maintain full lineage from sandbox creation through production implementation for regulatory audit trails. System must track "who/what/when/why" for every configuration change per BRD 12.7 requirements. Implementation must support regulatory reporting requirements with exportable audit logs in standard formats.

**Audit:**  
Mandatory justification comments required for key actions (version creation, approval, rejection, implementation). Audit trail must link sandbox versions to specific asset versions, rule versions, and FA configurations. System must preserve historical sandbox snapshots for minimum 7 years for regulatory review. All user actions must be logged with ADS ID, timestamp, and action details.

---

## 6. Out of Scope

**Not Included in This Feature:**
- Concurrent edit collision detection within Draft state (deprioritized, minimal user base)
- Multi-market simulation (simulate one sandbox across multiple markets simultaneously)
- Scheduled implementation (promote sandbox at specific date/time)
- Sandbox templates or cloning from historical sandboxes
- Advanced conflict resolution UI for stale sandboxes (not needed due to mutual exclusion)
- Bulk sandbox operations (delete multiple, approve multiple)
- Sandbox sharing or collaboration features (multiple users editing same sandbox)
- Custom approval workflows (fixed two-step approval)
- Sandbox archival and long-term storage policies
- Integration with external change management systems

**Future Enhancements (Post-26.1):**
- Pessimistic locking for Draft edits if user base grows
- Advanced analytics on simulation results (trend analysis, what-if scenarios)
- Sandbox comparison tool (diff between two sandbox versions)
- Automated testing and validation rules for sandbox content

---

## 7. Dependencies

**Feature-Level Dependencies (External Teams):**
- **By Default:** None (placeholder - user to update)

**User Story-Level Dependencies:**
- Backend API team must complete sandbox versioning data model before frontend can display version history
- Simulation engine must be available before Submit workflow can be tested
- Notification service must be configured for simulation completion alerts
- Database team must implement atomic transaction support for promotion logic
- Authentication service must support RBAC for approval workflows

**Internal Dependencies:**
- Asset Manager feature must be completed in parallel to enable asset editing within sandbox
- Fundamental Assessment must support sandbox context for FA override editing
- CRR rule configuration must support sandbox-scoped CRUD operations

---

## 8. Risks

**Technical Risks:**
- Database transaction timeouts during atomic promotion if sandbox contains large number of changes (mitigated by transaction optimization and retry logic)
- Simulation performance degradation with large population sizes (mitigated by background job processing and progress tracking)
- Version history storage growth over time (mitigated by archival policies and database indexing)

**Timeline Risks:**
- Complex versioning logic may require additional refinement cycles (mitigated by thorough discovery and prototyping)
- Integration with simulation engine may reveal unexpected dependencies (mitigated by early API contract validation)

**Operational Risks:**
- Users may create sandbox without proper testing plan, wasting simulation resources (mitigated by training and best practice documentation)
- Approval process may become bottleneck if approvers are unavailable (mitigated by clear SLA definition and escalation paths)
- Failed promotions may require manual intervention if error messages are unclear (mitigated by comprehensive error logging and support runbooks)

---

## 9. Acceptance Criteria (Gherkin Format)

### AC1 - Sandbox Creation with Scope Selection

**Given** a CRR Business User is on the Sandbox list view with no active sandboxes and production exists,  
**When** the user clicks "Add Risk Assessment" and selects "Enterprise" from the scope dropdown,  
**Then** a new Enterprise sandbox is created in Draft state with baseline copied from latest production configuration,  
**And** the Market dropdown options become disabled with tooltip "Cannot create Market sandbox while Enterprise sandbox is active."

### AC2 - Unified Configuration Editing in Draft State

**Given** a CRR Business User has an active sandbox in Draft state,  
**When** the user navigates between Rules, Assets, and Fundamental Assessment tabs within the sandbox,  
**Then** all edits accumulate as uncommitted changes without creating versions,  
**And** exit-blocking modal appears if user attempts to navigate away with unsaved changes.

### AC3 - Submit for Simulation with Version Creation

**Given** a CRR Business User has made edits in Draft sandbox,  
**When** the user clicks "Submit for Simulation" and confirms the change summary,  
**Then** the system creates Version 1 as immutable snapshot of all components (rules + assets + FA),  
**And** sandbox transitions to "In Progress" state,  
**And** simulation is triggered on production data copy.

### AC4 - Simulation Progress Tracking

**Given** a sandbox is in "In Progress" state with simulation running,  
**When** the user views the sandbox detail screen,  
**Then** real-time progress indicator displays current status and estimated time to completion,  
**And** user can click "Cancel Simulation" with confirmation prompt to abort the process.

### AC5 - Simulation Results Review

**Given** simulation has completed successfully,  
**When** the sandbox transitions to "Testing Completed" state,  
**Then** user can view risk distribution changes, impacted customer counts, and component-level details,  
**And** user can choose to "Create New Version" to continue editing or proceed to approval.

### AC6 - Version Rollback from Non-Editable State

**Given** a sandbox is in "Testing Completed" state at Version 2,  
**When** the user clicks "Rollback to Version 1,"  
**Then** the system creates Version 3 as a copy of Version 1's configuration,  
**And** Version 3 opens in Draft state for further editing.

### AC7 - Version Rollback from Draft State

**Given** a sandbox is in Draft state at Version 3 with uncommitted changes,  
**When** the user clicks "Rollback to Version 2,"  
**Then** the system overwrites Version 3's uncommitted changes with Version 2's configuration,  
**And** Version 3 remains in Draft state with all uncommitted changes discarded.

### AC8 - Two-Step Approval Workflow

**Given** a sandbox in "Testing Completed" state,  
**When** the first approver clicks "Approve,"  
**Then** sandbox transitions to "Pending Approval 1" state,  
**When** the second approver (different user) clicks "Approve,"  
**Then** sandbox transitions to "Pending Approval 2" state ready for implementation.

### AC9 - Atomic Promotion to Production

**Given** a sandbox in "Pending Approval 2" state,  
**When** the user clicks "Implement,"  
**Then** the system performs atomic transaction merging all components (rules + assets + FA) to production,  
**And** if any component fails, entire transaction is rolled back with NO partial commits,  
**And** sandbox transitions to "Rejected" state with error details in comments field.

### AC10 - Successful Implementation with Asset Version Propagation

**Given** a sandbox in "Pending Approval 2" state contains updated enterprise asset "Global_Products" v2,  
**When** implementation succeeds,  
**Then** all markets using "Global_Products" automatically reference v2 in their production rulesets,  
**And** previous version v1 is marked as archived in backend but hidden in UI,  
**And** audit log records version upgrade for all affected markets.

### AC11 - Enterprise vs Market Mutual Exclusion Enforcement

**Given** an active India Market sandbox exists in Draft state,  
**When** user attempts to create Enterprise sandbox,  
**Then** "Add Risk Assessment" button for Enterprise is disabled,  
**And** tooltip displays "Cannot create Enterprise sandbox while Market sandbox is active."

### AC12 - Rejection with Error Comments

**Given** atomic promotion fails due to database deadlock on asset table,  
**When** the system rolls back the transaction,  
**Then** sandbox transitions to "Rejected" state,  
**And** comments field is populated with "Implementation failed: Database deadlock on asset table. Please retry or contact support."

### AC13 - Audit Trail Completeness

**Given** a sandbox has progressed from Draft through Implementation,  
**When** user exports audit log,  
**Then** log contains all actions with user ADS ID, timestamp, action type, component details, old/new values, and justification comments,  
**And** log links sandbox version to specific asset versions, rule versions, and FA configurations.

---

# FEATURE 2: ASSET MANAGER

## 1. Description (User Voice Format)

**As a** Compliance Analyst / Manager,  
**I should be able to** create, edit, version, export, and promote Assets within sandbox workflows using centralized list management with reference data validation,  
**so that** reusable risk policy lists (high-risk countries, restricted occupations, etc.) are managed consistently across all markets and rulesets, with full audit lineage, versioning, and copy-on-write protection to prevent unintended cross-market impact.

---

## 2. Benefit to Business

This feature eliminates the current file-upload based asset duplication problem where the same list must be maintained in multiple CSV files across different rules, leading to inconsistency and manual error. By centralizing asset management with automatic reference data validation, business users can create lists once and reuse them across all applicable rules, significantly reducing maintenance effort. The sandbox-driven lifecycle ensures that asset changes are tested and approved before production, while version control provides complete audit trails for regulatory compliance. Copy-on-write protection for shared assets prevents unintended cross-market changes, giving market teams flexibility to customize while maintaining enterprise-wide policy integrity.

---

## 3. Verbatim Requirement from BRD

**BRD 12.6:** "System should have the capability to setup and maintain all reference lists."

**BRD 12.6.1:** "System must have the capability to setup/update these reference lists at the below levels: > Enterprise > Center/Market specific > Legal Entity > Product. For reference, Enterprise level lists at this time > Acquisition Channel, Industry, Geography, Company Structure, Product"

**BRD 12.6.3:** "System should provide the ability to setup Centralized (notable) lists in a user friendly manner (UI/UX to facilitate the update in an efficient manner). Product consideration - to provide options and elicit business feedback on the same."

**BRD 12.6.4:** "Access to setup a new list and/or update the lists will be controlled by User Access Permissions (should be configurable)."

**BRD 12.7.3:** "System must track and make available for viewing any change made to the Fundamental Assessment/Notable List/ reference data (add/modify/delete with who/when and any justification)"

**BRD 12.8.9:** "All reference data sets that are referenced by the CRR module should be available in the Sandbox environment. In particular (and as example) - Notable Lists, Centralized List/Fundamental Assessments"

**BRD 12.13.2:** "System should have the ability to generate a report with all the Fundamental Assessments / Centralized Lists / Notable Lists - This should be available at the following levels - > Enterprise > Center/Market specific > Product > Legal Entity"

---

## 4. User Scenarios / Functional Requirements

### 4.1 Asset Creation in Sandbox

Business users create assets only within sandbox context. User navigates to sandbox, clicks "Assets" sub-navigation, and clicks "Create Asset" button. The system displays asset creation form with fields: Asset Name (required, unique across system), Description (optional), List Name (dropdown of available reference data tables), and CSV file upload. Upon save, asset is created with status "Draft" and is immediately visible and editable in all sandboxes (Enterprise and Market). The system validates CSV values against the selected reference data table, rejecting any invalid values with clear error messages. Draft assets exist in a global pool and are not scoped to any specific sandbox until first used in a rule.

### 4.2 Asset Lifecycle and Status Transitions

Assets progress through four states: Draft (newly created, globally editable), Sandbox (used in at least one rule, subject to editability rules), Production (actively used in production rulesets, read-only outside sandbox), and Archived (previous production version, hidden in UI but stored for audit). The critical transition from Draft to Sandbox occurs automatically when an asset is first selected in any rule's value dropdown. This transition triggers usage metadata updates (tracking which market/ruleset/rule references the asset) and changes editability permissions. When a sandbox containing asset changes is promoted to production, affected assets transition to Production status, and previous versions become Archived.

### 4.3 Asset Visibility Rules

All assets are visible everywhere regardless of status or usage scope. In Enterprise sandbox, users see all assets in the system (Draft, Sandbox, Production). In Market sandbox, users also see all assets but with visual indicators (color accents, not text labels) distinguishing shared assets (used in multiple markets or enterprise) from local assets (used only in this specific market). The standalone Asset Manager view (outside sandbox) displays only Production assets filtered by selected market scope. For example, selecting "Belgium" in market dropdown shows only assets currently used in Belgium's production rulesets. Draft and Sandbox assets never appear in standalone view.

### 4.4 Asset Editability Rules

Editability depends on asset status and sandbox scope. Draft assets are editable everywhere (any user in any sandbox can edit inline with changes immediately visible globally). Sandbox assets have conditional editability: in Enterprise sandbox, all assets are editable with automatic versioning; in Market sandbox, local assets (used only in this market) are editable with versioning, but shared assets (used in multiple markets or enterprise) trigger copy-on-write workflow. Production assets are never directly editable; all edits must occur through sandbox workflow creating new versions. The system enforces these rules by disabling edit buttons or showing appropriate modals based on context.

### 4.5 Copy-on-Write Workflow for Shared Assets

When a user in Market sandbox attempts to edit a shared asset, the system detects shared usage (used in markets: India, France, Spain) and displays confirmation modal: "This asset has been used across multiple markets: [India, France, Spain]. Would you like to create a copy and customize?" with options [Create a Copy] [Cancel]. If user clicks "Create a Copy," the system opens the Edit Asset modal pre-populated with: Asset Name = `{OriginalAssetName}_copy`, Description = copied from original, List Name = same as original (read-only), and original CSV file pre-loaded. Real-time duplicate validation checks if the default name already exists and displays inline error message below Asset Name field: "Asset with this name already exists. Please choose a different name." The Save button remains disabled until the name is unique. User can modify name, description, and upload replacement CSV before saving. Upon successful save, a new asset entity is created with new asset_id in Draft status.

### 4.6 Asset Versioning and Enterprise Propagation

When assets are edited in Enterprise sandbox, the system creates new immutable versions. For example, editing "Global_Products" while in Draft state creates changes that accumulate until Submit for Simulation, which captures the modified asset as part of Version 1 snapshot. Each subsequent edit and submit cycle creates new sandbox versions, each linking to specific asset version snapshots. When Enterprise sandbox is promoted to production, all markets using the enterprise asset automatically receive the new version immediately. For instance, if India Market was using "Global_Products" v1 and Enterprise promotes v2, India's production rulesets instantly reference v2. Previous version v1 is marked Archived in backend, hidden in UI, but retained for audit trail linked to historical sandbox versions.

### 4.7 Asset Export Functionality

Users can export assets to Excel workbooks with standardized format. The export contains two sheets: "Values" sheet lists all asset values in single column, and "References" sheet shows where the asset is used with columns: Scope (label format: "Enterprise" or "India Market"), Status (Draft/Sandbox/Production, never Archived in UI), Risk Category (name like "Product Risk"), Risk Element (name like "Product Type"), Ruleset (description not ID), and Rule (rule logic text not rule ID). Export file naming follows pattern: `{AssetName}_v{version}.xlsx`, for example "High_Risk_Products_v2.xlsx". Each row in References sheet represents one ruleset that uses the asset, showing the ruleset description and associated rule logic text for human readability.

### 4.8 Asset Deletion Rules

Asset deletion is only permitted for assets in Draft status that have never been used in any rule. If user attempts to delete a Sandbox or Production asset, the system blocks the action with error message: "Cannot delete asset. Asset is currently used in rulesets. Remove all rule references before deletion." The system does not provide automatic cascade deletion that would orphan rules. For Draft assets, deletion is immediate and permanent (no soft delete) since they have no production impact. The deletion button is disabled (grayed out) for non-Draft assets in the UI to prevent users from attempting invalid deletions.

### 4.9 Asset Usage Tracking and Metadata

The system maintains comprehensive usage metadata for each asset: list of all rulesets referencing the asset (ruleset_id, iso_alpha2_ctry_cd, rule_id), current status (Draft/Sandbox/Production/Archived), version history (all previous versions with timestamps and creating user), audit trail (creation user/timestamp, all edit events with user/timestamp/justification comments), and sandbox linkages (which sandbox versions include which asset versions). This metadata powers the References sheet in exports, enables smart editability rules, and supports regulatory audit requirements. Usage tracking updates automatically when assets are added to or removed from rules.

### 4.10 Standalone Asset Manager View (Read-Only)

Outside of sandbox context, the Asset Manager tab provides a read-only view of production assets. Users select a market from primary dropdown (e.g., Belgium), and the system displays only assets currently used in Belgium's production rulesets, showing columns: Asset Name, Description, List Name (reference data table), Last Updated (timestamp), and Actions (Export only - no Edit/Delete). The view is filtered by market scope to help Market Compliance Officers understand what lists are active in their market. The "Submit" and "Implement" buttons that existed in the old UI are removed as these actions now occur only through unified sandbox workflow. This view serves as a reference/documentation tool, not an editing interface.

---

## 5. Non-Functional Requirements

**Performance:**  
Asset creation must complete within 3 seconds including reference data validation. Asset edit saves must complete within 2 seconds. Export generation for assets with up to 1000 values and 50 ruleset references must complete within 10 seconds. Asset usage metadata queries must return within 1 second. Duplicate name validation must occur in real-time (≤ 500ms response) as user types.

**Security:**  
All asset operations require CRR Business User role authentication. Asset editing permissions must respect sandbox scope rules (Enterprise vs Market). CSV file uploads must be validated for malicious content (no executable code, SQL injection attempts). Reference data validation must prevent invalid values from entering the system. Audit logs must capture all asset modifications with user identity and timestamp.

**Scalability:**  
System must support up to 1000 assets without performance degradation in listing or search operations. Individual assets must accommodate up to 10,000 values without upload or validation failures. Usage metadata must efficiently handle assets referenced by 100+ rulesets across multiple markets. Version history must support up to 50 versions per asset with fast retrieval.

**Compliance:**  
All asset changes must maintain full audit lineage for regulatory review per BRD 12.7 requirements. System must track "who/what/when/why" for every asset modification. Asset version history must be preserved for minimum 7 years. Export functionality must provide regulator-ready documentation showing asset usage across risk framework. Copy-on-write workflow must prevent unintended cross-market policy changes.

**Audit:**  
Mandatory justification comments required when editing assets in sandbox. Audit trail must link asset versions to sandbox versions and production implementations. System must preserve all historical asset versions (including Archived) for compliance review. Export logs must track who downloaded which assets and when.

---

## 6. Out of Scope

**Not Included in This Feature:**
- Concurrent edit collision detection for Draft assets (deprioritized, minimal user base - handled with generic backend error)
- Asset Manager UI redesign or navigation changes (using existing layout, only adding sandbox integration)
- Inline editing from Asset list view (editing only via modal forms)
- Multi-market simulation for asset impact analysis
- Asset templates or bulk asset creation from spreadsheets
- Advanced search and filtering in Asset list (basic name search only)
- Asset usage analytics and recommendations (which assets are underutilized, etc.)
- Asset comparison tool (diff between two asset versions)
- Automated asset validation rules beyond reference data check
- Asset lifecycle automation (auto-archive old unused assets)

**Future Enhancements (Post-26.1):**
- Optimistic locking for Draft asset concurrent edits if user base grows
- Advanced asset search with filters (status, usage scope, last modified date)
- Asset import from external systems (automated list updates)
- Asset usage heat maps showing which assets are most referenced
- Bulk asset operations (delete multiple Draft assets at once)

---

## 7. Dependencies

**Feature-Level Dependencies (External Teams):**
- **By Default:** None (placeholder - user to update)

**User Story-Level Dependencies:**
- Reference Data Table service must be available for validation logic
- Database team must implement asset versioning schema before versioning features can be built
- Sandbox feature must provide API endpoints for asset scoping and editability checks
- Rule configuration system must trigger asset status transitions when assets are used in rules
- Export service must support Excel workbook generation with multi-sheet format

**Internal Dependencies:**
- Unified Sandbox Journey feature provides the sandbox context where assets are created and edited
- Rule configuration must support asset selection from global asset pool in rule value dropdowns
- Fundamental Assessment may reference assets (out of scope for 26.1 but architecture should allow)

---

## 8. Risks

**Technical Risks:**
- Reference data validation performance may degrade with large asset CSV files (mitigated by async validation with progress indicator)
- Asset version propagation during enterprise promotion may fail if markets have conflicting local changes (mitigated by mutual exclusion rule preventing this scenario)
- Export generation may timeout for assets with hundreds of ruleset references (mitigated by pagination or background job processing)
- Real-time duplicate validation may cause UI lag if asset table grows very large (mitigated by database indexing on asset name)

**Timeline Risks:**
- Copy-on-write workflow UX complexity may require additional design iterations (mitigated by thorough prototyping and user testing)
- Asset lifecycle state transitions have many edge cases that may surface during testing (mitigated by comprehensive test scenarios and QA cycles)

**Operational Risks:**
- Users may create too many Draft assets without cleanup, cluttering the global pool (mitigated by documentation and training on Draft deletion)
- Copy naming conventions may lead to confusion if users create many copies (mitigated by clear naming guidelines and best practices documentation)
- Shared asset detection may not be obvious to users, leading to unexpected copy prompts (mitigated by visual indicators and tooltip explanations)

---

## 9. Acceptance Criteria (Gherkin Format)

### AC1 - Asset Creation in Sandbox Draft State

**Given** a CRR Business User is inside a sandbox in Draft state,  
**When** the user clicks "Assets" sub-nav, then "Create Asset," enters name "High_Risk_Industries," selects list name "Industry_Code," uploads CSV with valid values, and clicks Save,  
**Then** a new asset is created with status "Draft" and is immediately visible in all sandboxes (Enterprise and Market),  
**And** the asset can be selected in rule value dropdowns for any data point linked to "Industry_Code" reference table.

### AC2 - Asset Status Transition from Draft to Sandbox

**Given** an asset "Restricted_Countries" exists in Draft status,  
**When** a user in any sandbox configures a rule and selects "Restricted_Countries" from the asset dropdown as the rule value,  
**Then** the asset status automatically transitions to "Sandbox,"  
**And** usage metadata is updated to track the market/ruleset/rule referencing the asset.

### AC3 - Draft Asset Global Editability

**Given** an asset "New_Products" exists in Draft status,  
**When** User A in India Market sandbox edits the asset adding value "ProductX," and User B in France Market sandbox views the asset,  
**Then** User B immediately sees "ProductX" in the asset values list,  
**And** User B can also edit the asset inline with changes visible to all sandboxes.

### AC4 - Enterprise Sandbox Edits All Assets with Versioning

**Given** a CRR Business User is in Enterprise sandbox Draft state,  
**When** the user edits asset "Global_Products" (Sandbox status) by adding three new values and clicks Save,  
**Then** changes accumulate as uncommitted in the Draft,  
**When** the user clicks "Submit for Simulation,"  
**Then** Version 1 is created capturing the modified "Global_Products" as part of the sandbox snapshot.

### AC5 - Market Sandbox Local Asset Editing

**Given** asset "India_Specific_Industries" (Sandbox status) is used ONLY in India Market rulesets,  
**When** user in India Market sandbox clicks Edit on this asset,  
**Then** Edit Asset modal opens allowing inline editing with versioning,  
**And** no copy prompt appears because asset is local to India.

### AC6 - Market Sandbox Shared Asset Copy-on-Write Prompt

**Given** asset "APAC_Countries" (Sandbox status) is used in India, Singapore, and France Market rulesets,  
**When** user in India Market sandbox clicks Edit on "APAC_Countries,"  
**Then** modal displays "This asset has been used across multiple markets: [India, Singapore, France]. Would you like to create a copy and customize?" with [Create a Copy] [Cancel] buttons.

### AC7 - Copy Creation with Duplicate Name Validation

**Given** user clicked "Create a Copy" for shared asset "APAC_Countries,"  
**When** the Edit Asset modal opens with default name "APAC_Countries_copy," but an asset with this name already exists,  
**Then** inline validation error appears below Asset Name field: "Asset with this name already exists. Please choose a different name,"  
**And** Save button is disabled until user changes the name to a unique value.

### AC8 - Successful Copy Creation with New Asset ID

**Given** user renamed copy to "APAC_Countries_India" (no duplicate),  
**When** user clicks Save,  
**Then** new asset is created with new asset_id, status "Draft," and values copied from original,  
**And** user can now edit this copy inline and select it in India Market rules.

### AC9 - Enterprise Asset Version Automatic Propagation

**Given** India Market production rulesets use "Global_Products" v1,  
**When** Enterprise sandbox containing "Global_Products" v2 is promoted to production,  
**Then** India's production rulesets automatically reference "Global_Products" v2,  
**And** v1 is marked Archived in backend (hidden in UI but retained for audit).

### AC10 - Asset Export with Two-Sheet Workbook

**Given** asset "High_Risk_Products" is used in 3 rulesets across 2 risk elements,  
**When** user clicks Export on this asset,  
**Then** system generates Excel file "High_Risk_Products_v2.xlsx" with two sheets: "Values" (listing all asset values) and "References" (3 rows showing Scope, Status, Risk Category name, Risk Element name, Ruleset description, and Rule logic text).

### AC11 - Asset Deletion Blocked for Sandbox Status

**Given** asset "Active_Products" has status "Sandbox" (used in at least one rule),  
**When** user attempts to delete the asset,  
**Then** deletion is blocked with error message "Cannot delete asset. Asset is currently used in rulesets. Remove all rule references before deletion,"  
**And** Delete button is disabled (grayed out) in the UI.

### AC12 - Draft Asset Deletion Allowed

**Given** asset "Unused_Test_Asset" has status "Draft" and is not referenced by any rules,  
**When** user clicks Delete and confirms,  
**Then** asset is permanently deleted from the system,  
**And** asset no longer appears in any sandbox asset lists.

### AC13 - Standalone Asset Manager Read-Only View

**Given** user navigates to standalone Asset Manager tab (outside sandbox) and selects "Belgium" from market dropdown,  
**When** the page loads,  
**Then** only Production assets currently used in Belgium's production rulesets are displayed,  
**And** Edit and Delete buttons are hidden (only Export action available).

### AC14 - Asset Usage Tracking in Metadata

**Given** asset "Restricted_Occupations" is used in 5 rulesets across India and France markets,  
**When** user views asset details or exports the asset,  
**Then** usage metadata shows all 5 ruleset references with market scope (IN/FR), ruleset descriptions, and rule logic text,  
**And** audit trail shows all historical edits with user ADS ID and timestamps.

### AC15 - Reference Data Validation on Upload

**Given** user uploads CSV file for asset linked to "Country_Code" reference table,  
**When** CSV contains invalid value "INVALID_COUNTRY" not present in reference data,  
**Then** validation error displays "Invalid value detected: INVALID_COUNTRY. Please ensure all values match reference data table Country_Code,"  
**And** asset creation is blocked until CSV is corrected.

---

**Both feature structures are now complete with ALL discovered requirements, edge cases, and business rules incorporated.**

**Ready for next steps:**
1. User Story decomposition with 3-5 point sizing
2. Sprint sequencing for 26.1.1 through 26.1.5
3. User Journey Tree Diagrams

**Please confirm: "Proceed to User Story creation"**

# USER STORIES - FEATURE 1: UNIFIED SANDBOX JOURNEY

---

## STORY 1.1: Sandbox Data Model and Backend API Foundation

**Story Title:** Create Sandbox Data Model and Core CRUD APIs

**Description:**

**As a** Backend Developer,  
**I want to** implement the sandbox data model with all required tables and relationships, and create core CRUD API endpoints,  
**so that** the frontend can create, read, update, and manage sandbox entities with proper state management and audit tracking.

**Verbatim Requirement from BRD:**

BRD 12.8: "System should support sandbox simulation functionality providing multiple instances and effective monitoring capabilities."

**Story Type:** Backend

**Sprint Assignment:** 26.1.1

**Dependencies:**
- **Blocks:** Stories 1.2, 1.3, 1.4 (all frontend and full-stack stories depend on these APIs)
- **Blocked By:** None
- **External:** Database team must provision sandbox schema

**Rally Metadata:** Team = CRR Rule Configuration, Feature = [User to populate], Iteration = 26.1.1

**Acceptance Criteria:**

✓ **Happy Path - Sandbox Entity Creation:**

**Given** the backend receives a POST request to `/api/v1/sandboxes` with payload:
```json
{
  "scope": "Enterprise",
  "iso_alpha2_ctry_cd": "XX",
  "risk_assess_id": 1,
  "risk_assess_vsn_no": 1,
  "creat_user_id": "user123"
}
```
**When** the API processes the request,  
**Then** a new record is created in `sandbox` table with:
- `sandbox_id` (auto-generated integer, primary key)
- `scope` = "Enterprise"
- `iso_alpha2_ctry_cd` = "XX"
- `status` = "Draft"
- `creat_ts` = current timestamp
- `creat_user_id` = "user123"
- `baseline_risk_assess_vsn_no` = latest production version  
**And** response returns 201 Created with `sandbox_id` and full sandbox object.

✓ **Happy Path - Retrieve Sandbox by ID:**

**Given** a sandbox with `sandbox_id` = 100 exists,  
**When** the backend receives GET request to `/api/v1/sandboxes/100`,  
**Then** response returns 200 OK with complete sandbox object including all fields from `sandbox` table,  
**And** response includes related data: current version number, baseline version, created user details.

✓ **Happy Path - Update Sandbox Status:**

**Given** a sandbox with `sandbox_id` = 100 has `status` = "Draft",  
**When** the backend receives PATCH request to `/api/v1/sandboxes/100` with `{"status": "In Progress"}`,  
**Then** the `status` field in `sandbox` table is updated to "In Progress",  
**And** `lst_updt_ts` is updated to current timestamp,  
**And** `lst_updt_user_id` is recorded,  
**And** response returns 200 OK with updated sandbox object.

✗ **Sad Path - Invalid Scope Value:**

**Given** the backend receives POST request with `{"scope": "InvalidScope"}`,  
**When** the API validates the payload,  
**Then** response returns 400 Bad Request with error message "Invalid scope. Must be 'Enterprise' or valid market code",  
**And** no record is created in `sandbox` table.

⚠ **Edge Case - Retrieve Non-Existent Sandbox:**

**Given** no sandbox exists with `sandbox_id` = 999,  
**When** the backend receives GET request to `/api/v1/sandboxes/999`,  
**Then** response returns 404 Not Found with error message "Sandbox not found",  
**And** no exception is thrown.

🔴 **Error Handling - Database Connection Failure:**

**Given** the database is unavailable,  
**When** the backend receives POST request to create sandbox,  
**Then** response returns 503 Service Unavailable with error message "Database connection failed. Please try again later",  
**And** no partial data is committed.

---

## STORY 1.2: Sandbox Creation UI with Scope Selection and Mutual Exclusion

**Story Title:** Build Sandbox Creation UI with Enterprise/Market Dropdown and Mutual Exclusion Logic

**Description:**

**As a** CRR Business User,  
**I want to** create new sandboxes by selecting either Enterprise or Market scope from a dropdown, with automatic disabling of unavailable options based on existing active sandboxes,  
**so that** I can start editing CRR configurations in an isolated sandbox environment while the system prevents conflicting Enterprise and Market sandboxes from coexisting.

**Verbatim Requirement from BRD:**

BRD 12.8.4: "Multiple instances should be available for the Business (ability to run 4 instances in parallel). There should be ability to limit the sandbox to > Enterprise > Market/Center specific > Legal Entity > Product"

**Story Type:** Frontend

**Sprint Assignment:** 26.1.1

**Dependencies:**
- **Blocks:** None
- **Blocked By:** Story 1.1 (requires sandbox CRUD APIs)
- **External:** None

**Rally Metadata:** Team = CRR Rule Configuration, Feature = [User to populate], Iteration = 26.1.1

**Acceptance Criteria:**

✓ **Happy Path - Initial Blank State (No Production):**

**Given** no production configuration exists and user is on Sandbox list page,  
**When** the page loads,  
**Then** the scope dropdown displays only "Enterprise" option,  
**And** "Add Risk Assessment" button is enabled,  
**When** user clicks "Add Risk Assessment," selects "Enterprise," and clicks Create,  
**Then** API call is made to POST `/api/v1/sandboxes` with `scope: "Enterprise"`,  
**And** new sandbox appears in list with status "Draft".

✓ **Happy Path - Enterprise Sandbox Active Disables Markets:**

**Given** an Enterprise sandbox exists with status "Draft",  
**When** user returns to Sandbox list page,  
**Then** scope dropdown displays "Enterprise" (disabled, grayed out) and all market options (India, France, Spain, etc.) are disabled,  
**And** tooltip on disabled market options displays "Cannot create Market sandbox while Enterprise sandbox is active",  
**And** "Add Risk Assessment" button is disabled.

✓ **Happy Path - Market Sandbox Active Disables Enterprise:**

**Given** an India Market sandbox exists with status "Testing Completed",  
**When** user returns to Sandbox list page,  
**Then** scope dropdown displays "Enterprise" (disabled) and other market options (France, Spain, etc.) are enabled,  
**And** India option is disabled (cannot create duplicate market sandbox),  
**And** tooltip on disabled Enterprise option displays "Cannot create Enterprise sandbox while Market sandbox is active".

✓ **Happy Path - Create Market Sandbox After Enterprise Promotion:**

**Given** Enterprise sandbox was promoted to production (no longer active),  
**When** user navigates to Sandbox list page,  
**Then** scope dropdown displays "Enterprise" and all market options (all enabled),  
**When** user selects "India" and clicks Create,  
**Then** API call is made with `scope: "India"`, `iso_alpha2_ctry_cd: "IN"`,  
**And** new India sandbox appears in list.

✗ **Sad Path - API Failure During Creation:**

**Given** user clicks "Add Risk Assessment" and selects "Enterprise",  
**When** API call to POST `/api/v1/sandboxes` fails with 500 error,  
**Then** error toast notification displays "Failed to create sandbox. Please try again",  
**And** no sandbox appears in the list,  
**And** user can retry the creation.

⚠ **Edge Case - Multiple Market Sandboxes Allowed:**

**Given** India Market sandbox exists (status "Draft"),  
**When** user creates France Market sandbox,  
**Then** both sandboxes appear in list (India and France),  
**And** Enterprise option remains disabled,  
**And** user can have up to 3 market sandboxes active simultaneously.

🔴 **Error Handling - Network Timeout:**

**Given** user clicks Create and network request times out,  
**When** timeout occurs after 30 seconds,  
**Then** error message displays "Request timeout. Please check your connection and retry",  
**And** Create button is re-enabled for retry.

---

## STORY 1.3: Sandbox Lifecycle State Management Backend

**Story Title:** Implement Sandbox Status Transitions and State Validation Logic

**Description:**

**As a** Backend Developer,  
**I want to** implement state transition logic that validates allowed status changes and enforces business rules for each sandbox state,  
**so that** sandboxes progress through the correct lifecycle (Draft → In Progress → Testing Completed → Pending Approval → Rejected/Implemented) with proper validation and audit logging.

**Verbatim Requirement from BRD:**

BRD 12.8.5: "At the time of submitting/triggering a sandbox simulation, system should prompt the user to confirm that all the updates being made are in line with the required enhancement/change request (the elements that have been modified should be rendered/highlighted on the UI for easy reference/validation)."

**Story Type:** Backend

**Sprint Assignment:** 26.1.2

**Dependencies:**
- **Blocks:** Stories 1.5, 1.8 (simulation and approval workflows depend on state management)
- **Blocked By:** Story 1.1 (requires sandbox data model)
- **External:** None

**Rally Metadata:** Team = CRR Rule Configuration, Feature = [User to populate], Iteration = 26.1.2

**Acceptance Criteria:**

✓ **Happy Path - Draft to In Progress Transition:**

**Given** sandbox with `sandbox_id` = 100, `status` = "Draft",  
**When** backend receives PATCH `/api/v1/sandboxes/100/status` with `{"status": "In Progress", "user_id": "user123"}`,  
**Then** `status` field updates to "In Progress" in `sandbox` table,  
**And** `lst_updt_ts` and `lst_updt_user_id` are updated,  
**And** audit log entry is created with action = "STATUS_CHANGE", old_value = "Draft", new_value = "In Progress",  
**And** response returns 200 OK.

✓ **Happy Path - In Progress to Testing Completed:**

**Given** sandbox has `status` = "In Progress" and simulation completed successfully,  
**When** backend receives status update to "Testing Completed",  
**Then** status transitions successfully,  
**And** `simulation_complete_ts` field is populated with current timestamp,  
**And** notification is sent to predefined user distribution list.

✗ **Sad Path - Invalid State Transition:**

**Given** sandbox has `status` = "Draft",  
**When** backend receives request to transition directly to "Pending Approval 1" (skipping In Progress and Testing Completed),  
**Then** response returns 400 Bad Request with error message "Invalid state transition. Cannot move from Draft to Pending Approval 1. Must progress through In Progress → Testing Completed first",  
**And** status remains "Draft" in database.

✗ **Sad Path - Transition from Non-Editable State:**

**Given** sandbox has `status` = "Pending Approval 2",  
**When** backend receives request to transition back to "Draft",  
**Then** response returns 400 Bad Request with error message "Cannot revert to Draft from Pending Approval 2. Use Rollback functionality to create new version",  
**And** status remains unchanged.

⚠ **Edge Case - Cancelled to Draft Not Allowed:**

**Given** sandbox has `status` = "Cancelled",  
**When** backend receives request to change status to "Draft",  
**Then** response returns 400 Bad Request with error message "Cancelled sandboxes cannot be reopened. Create new sandbox instead",  
**And** status remains "Cancelled".

⚠ **Edge Case - Rejected Sandbox Can Only Be Resubmitted:**

**Given** sandbox has `status` = "Rejected" with rejection comments,  
**When** backend receives request to change status to "Testing Completed" (without fixing issues),  
**Then** response returns 400 Bad Request,  
**And** allowed transition is only back to "Draft" for editing.

🔴 **Error Handling - Concurrent Status Update:**

**Given** two users attempt to update same sandbox status simultaneously,  
**When** backend processes first request successfully,  
**Then** second request receives 409 Conflict with error message "Sandbox status was modified by another user. Please refresh and retry",  
**And** optimistic locking prevents data corruption.

---

## STORY 1.4: Sandbox Detail View with Sub-Navigation for Rules/Assets/FA

**Story Title:** Create Sandbox Detail UI with Configuration Type Switcher and Exit Blocking

**Description:**

**As a** CRR Business User,  
**I want to** navigate between Rules, Assets, and Fundamental Assessment configuration types within my sandbox using a dropdown or tabs, with automatic exit blocking when I have unsaved changes,  
**so that** I can edit all configuration types in one unified sandbox session without losing work.

**Verbatim Requirement from BRD:**

BRD 12.8.9: "All reference data sets that are referenced by the CRR module should be available in the Sandbox environment. In particular (and as example) - Notable Lists, Centralized List/Fundamental Assessments"

**Story Type:** Frontend

**Sprint Assignment:** 26.1.2

**Dependencies:**
- **Blocks:** None
- **Blocked By:** Story 1.1 (requires sandbox APIs), Story 1.2 (requires sandbox creation)
- **External:** Rule configuration UI, Asset Manager UI, FA UI must support sandbox context parameter

**Rally Metadata:** Team = CRR Rule Configuration, Feature = [User to populate], Iteration = 26.1.2

**Acceptance Criteria:**

✓ **Happy Path - Configuration Type Switcher Displays:**

**Given** user opens sandbox detail page for `sandbox_id` = 100,  
**When** the page loads,  
**Then** a configuration type dropdown displays with options: ["Rules", "Assets", "Fundamental Assessment"],  
**And** default selection is "Rules",  
**And** the Rules configuration UI is displayed in sandbox context (showing only rules within this sandbox scope).

✓ **Happy Path - Switch to Assets View:**

**Given** user is viewing Rules in sandbox detail,  
**When** user selects "Assets" from configuration dropdown,  
**Then** the view switches to Asset Manager UI filtered to sandbox context,  
**And** sandbox_id = 100 is passed as query parameter to Asset API,  
**And** all assets are visible (Draft, Sandbox, Production) with editability rules enforced.

✓ **Happy Path - Switch to Fundamental Assessment:**

**Given** user is viewing Assets in sandbox detail,  
**When** user selects "Fundamental Assessment" from dropdown,  
**Then** FA UI loads with sandbox context (`sandbox_id` = 100, `iso_alpha2_ctry_cd` from sandbox scope),  
**And** FA overrides for the sandbox's market are displayed,  
**And** Calculate button is enabled for editing.

✓ **Happy Path - Exit Blocking Modal on Unsaved Changes:**

**Given** user made edits in Rules view (added new rule, not yet saved),  
**When** user attempts to switch to "Assets" or clicks browser back button,  
**Then** modal appears with message "You have unsaved changes. Do you want to discard them?" with buttons [Stay and Save] [Discard and Leave],  
**When** user clicks [Stay and Save],  
**Then** modal closes and user remains in Rules view,  
**When** user clicks [Discard and Leave],  
**Then** unsaved changes are discarded and view switches to selected configuration type.

✗ **Sad Path - API Failure Loading Assets:**

**Given** user selects "Assets" from dropdown,  
**When** API call to fetch assets fails with 500 error,  
**Then** error message displays "Failed to load assets. Please try again",  
**And** view remains on previous configuration type (Rules),  
**And** user can retry by selecting Assets again.

⚠ **Edge Case - No Unsaved Changes Allows Direct Navigation:**

**Given** user is viewing Rules with no uncommitted edits,  
**When** user switches to "Assets",  
**Then** view switches immediately without exit-blocking modal,  
**And** no data is lost.

⚠ **Edge Case - Exit Blocking on Browser Back:**

**Given** user has unsaved changes in sandbox,  
**When** user clicks browser back button or closes tab,  
**Then** browser native "Leave site?" prompt appears,  
**And** user must confirm before losing changes.

🔴 **Error Handling - Sandbox Not Found:**

**Given** user navigates to sandbox detail page with invalid `sandbox_id` = 999,  
**When** API returns 404 Not Found,  
**Then** error page displays "Sandbox not found or has been deleted",  
**And** user is redirected to Sandbox list page after 3 seconds.

---

## STORY 1.5: Sandbox Versioning - Create Version and Snapshot Logic

**Story Title:** Implement Sandbox Version Creation with Immutable Snapshots on Submit

**Description:**

**As a** Backend Developer,  
**I want to** capture all uncommitted changes (rules, assets, FA) as an immutable version snapshot when user clicks "Submit for Simulation,"  
**so that** every simulation is linked to a specific, traceable configuration version that cannot be altered, supporting audit requirements and rollback functionality.

**Verbatim Requirement from BRD:**

BRD 12.8.12: "System must maintain version control of all changes made. This must be available on the Sandbox UI."

**Story Type:** Backend

**Sprint Assignment:** 26.1.3

**Dependencies:**
- **Blocks:** Story 1.6 (simulation workflow), Story 1.11 (rollback functionality)
- **Blocked By:** Story 1.3 (requires state management), Asset Manager stories for asset versioning
- **External:** Database team must implement `sandbox_version` table schema

**Rally Metadata:** Team = CRR Rule Configuration, Feature = [User to populate], Iteration = 26.1.3

**Acceptance Criteria:**

✓ **Happy Path - Create Version 1 on First Submit:**

**Given** sandbox with `sandbox_id` = 100, `status` = "Draft" with uncommitted rule and asset changes,  
**When** backend receives POST `/api/v1/sandboxes/100/versions` with `{"user_id": "user123", "justification": "Testing geographic risk changes"}`,  
**Then** a new record is created in `sandbox_version` table with:
- `sandbox_id` = 100
- `version_no` = 1
- `creat_ts` = current timestamp
- `creat_user_id` = "user123"
- `justification_comment` = "Testing geographic risk changes"
- `status` = "Submitted"  
**And** all modified rules are captured in `sandbox_rule_snapshot` junction table linking `sandbox_version_id` to `rule_id` with `rule_vsn_no`,  
**And** all modified assets are captured in `sandbox_asset_snapshot` junction table linking `sandbox_version_id` to `asset_id` with `asset_vsn_no`,  
**And** FA override changes are captured in `sandbox_fa_snapshot` table,  
**And** sandbox `status` transitions to "In Progress",  
**And** response returns 201 Created with `version_no` = 1.

✓ **Happy Path - Create Version 2 After Editing Version 1:**

**Given** sandbox has Version 1 (status "Testing Completed") and user clicked "Create New Version" to start editing,  
**When** user makes new edits and clicks Submit,  
**Then** Version 2 is created with:
- `version_no` = 2
- `parent_version_no` = 1 (links to previous version)
- New snapshots of rules/assets/FA at Version 2 state  
**And** Version 1 remains immutable in database,  
**And** response returns version_no = 2.

✓ **Happy Path - Retrieve Version History:**

**Given** sandbox has 3 versions (v1, v2, v3),  
**When** backend receives GET `/api/v1/sandboxes/100/versions`,  
**Then** response returns array of all versions with fields: `version_no`, `creat_ts`, `creat_user_id`, `status`, `justification_comment`, `simulation_result_summary`,  
**And** versions are ordered by `version_no` descending (newest first).

✗ **Sad Path - Missing Justification Comment:**

**Given** user attempts to submit sandbox without providing justification,  
**When** backend receives POST with empty `justification` field,  
**Then** response returns 400 Bad Request with error "Justification comment is required for version creation",  
**And** no version is created.

⚠ **Edge Case - No Changes Detected:**

**Given** sandbox is in Draft state but user made no edits since last version,  
**When** backend receives version creation request,  
**Then** response returns 400 Bad Request with error "No changes detected since last version. Cannot create duplicate version",  
**And** version count remains unchanged.

⚠ **Edge Case - Version Snapshot Includes Deleted Rules:**

**Given** user deleted Rule R-100 from sandbox in Draft state,  
**When** version is created,  
**Then** snapshot records the deletion with `deleted_flag` = true for R-100,  
**And** audit trail shows rule was present in baseline but removed in this version.

🔴 **Error Handling - Snapshot Creation Transaction Rollback:**

**Given** version creation begins and rules are snapshotted successfully but assets snapshot fails,  
**When** database error occurs during asset snapshot,  
**Then** entire transaction is rolled back (rules snapshot also removed),  
**And** response returns 500 Internal Server Error with message "Version creation failed. Please retry",  
**And** sandbox remains in Draft state.

---

## STORY 1.6: Submit for Simulation Workflow with Confirmation Modal

**Story Title:** Build Submit UI with Change Summary Modal and Simulation Trigger

**Description:**

**As a** CRR Business User,  
**I want to** review all my configuration changes in a confirmation modal before submitting for simulation, then trigger the simulation process,  
**so that** I can validate my changes are correct before committing resources to simulation and ensure I haven't missed any important modifications.

**Verbatim Requirement from BRD:**

BRD 12.8.5: "At the time of submitting/triggering a sandbox simulation, system should prompt the user to confirm that all the updates being made are in line with the required enhancement/change request (the elements that have been modified should be rendered/highlighted on the UI for easy reference/validation)."

**Story Type:** Full-Stack

**Sprint Assignment:** 26.1.3

**Dependencies:**
- **Blocks:** Story 1.7 (simulation progress tracking)
- **Blocked By:** Story 1.5 (requires versioning APIs), Story 1.3 (requires state management)
- **External:** Simulation engine team must provide simulation trigger API endpoint

**Rally Metadata:** Team = CRR Rule Configuration, Feature = [User to populate], Iteration = 26.1.3

**Acceptance Criteria:**

✓ **Happy Path - Submit Button Displays in Draft State:**

**Given** sandbox is in "Draft" state with uncommitted changes,  
**When** user is on sandbox detail page,  
**Then** "Submit for Simulation" button is visible and enabled,  
**When** user clicks the button,  
**Then** confirmation modal opens.

✓ **Happy Path - Confirmation Modal Displays Change Summary:**

**Given** user clicked "Submit for Simulation" and sandbox has:
- 5 rule modifications (2 added, 2 edited, 1 deleted)
- 3 asset modifications (1 created, 2 edited)
- 1 FA override change (Geography answer changed Yes→No)  
**When** modal opens,  
**Then** modal displays sections:
- **Rules Changes:** Lists all modified rules with change type indicator (✓ Added, ✏ Edited, ✗ Deleted) and rule identifiers
- **Asset Changes:** Lists modified assets with change type and asset names
- **FA Changes:** Lists FA override changes with old/new values
- Justification comment text area (required field)
- Buttons: [Cancel] [Confirm and Submit]

✓ **Happy Path - Submit with Justification:**

**Given** confirmation modal is open with all changes displayed,  
**When** user enters justification "Testing Q4 regulatory compliance updates" and clicks [Confirm and Submit],  
**Then** API calls are made sequentially:
  1. POST `/api/v1/sandboxes/{id}/versions` with justification → creates Version 1
  2. POST `/api/v1/simulations` with `sandbox_id` and `version_no` → triggers simulation  
**And** modal closes,  
**And** sandbox status updates to "In Progress",  
**And** success toast displays "Simulation submitted successfully. You will be notified upon completion",  
**And** page redirects to simulation progress view.

✗ **Sad Path - Empty Justification Blocks Submit:**

**Given** confirmation modal is open,  
**When** user leaves justification field empty and clicks [Confirm and Submit],  
**Then** inline error message displays below text area "Justification is required",  
**And** [Confirm and Submit] button remains disabled until text is entered.

✗ **Sad Path - Version Creation API Fails:**

**Given** user clicks [Confirm and Submit],  
**When** API call to create version returns 500 error,  
**Then** error toast displays "Failed to create version. Please try again",  
**And** modal remains open for retry,  
**And** no simulation is triggered.

⚠ **Edge Case - No Changes Prevents Submit:**

**Given** sandbox has no uncommitted changes since last version,  
**When** user is on sandbox detail page,  
**Then** "Submit for Simulation" button is disabled (grayed out) with tooltip "No changes to submit. Make edits before submitting".

⚠ **Edge Case - User Cancels Modal:**

**Given** confirmation modal is open,  
**When** user clicks [Cancel] or clicks outside modal (backdrop),  
**Then** modal closes without making any API calls,  
**And** sandbox remains in Draft state,  
**And** no version is created.

🔴 **Error Handling - Simulation Trigger Fails After Version Created:**

**Given** version creation succeeds but simulation trigger API fails,  
**When** POST `/api/v1/simulations` returns 503 Service Unavailable,  
**Then** error toast displays "Simulation could not be triggered. Contact support with Reference ID: [version_id]",  
**And** sandbox status remains "Draft" (version exists but not marked as submitted),  
**And** user can retry submission which will use existing version.

---

## STORY 1.7: Simulation Progress Tracking UI with Polling

**Story Title:** Build Real-Time Simulation Progress View with Status Polling

**Description:**

**As a** CRR Business User,  
**I want to** see real-time progress updates while my simulation is running, including estimated time to completion and ability to cancel,  
**so that** I know the simulation is proceeding and can abort if I realize I made an error.

**Verbatim Requirement from BRD:**

BRD 12.8.6: "The system must have the capability to track/display the progress of the simulation exercise. The estimated time to completion must also be displayed."

BRD 12.8.8: "The system must have capability to allow a simulation exercise to be cancelled at any point. The user will be required to confirm the cancellation."

**Story Type:** Frontend

**Sprint Assignment:** 26.1.3

**Dependencies:**
- **Blocks:** Story 1.8 (approval workflow needs simulation completion)
- **Blocked By:** Story 1.6 (requires simulation submission)
- **External:** Simulation engine must provide progress API endpoint

**Rally Metadata:** Team = CRR Rule Configuration, Feature = [User to populate], Iteration = 26.1.3

**Acceptance Criteria:**

✓ **Happy Path - Progress View Displays After Submit:**

**Given** sandbox transitioned to "In Progress" after submitting simulation,  
**When** user is on sandbox detail page,  
**Then** simulation progress section displays with:
- Progress bar showing percentage complete (initially 0%)
- Status text "Simulation in progress... Processing customer population"
- Estimated time to completion "~4 hours 30 minutes remaining"
- [Cancel Simulation] button enabled

✓ **Happy Path - Real-Time Progress Updates via Polling:**

**Given** simulation is running and progress view is displayed,  
**When** frontend polls GET `/api/v1/simulations/{simulation_id}/progress` every 5 seconds,  
**Then** progress bar updates to reflect current completion percentage (e.g., 15%, 30%, 75%),  
**And** estimated time remaining updates dynamically,  
**And** status text updates through stages: "Processing customer population" → "Calculating risk scores" → "Generating results" → "Finalizing simulation".

✓ **Happy Path - Simulation Completes Successfully:**

**Given** simulation reaches 100% completion,  
**When** final poll returns status "Completed",  
**Then** progress bar shows 100%,  
**And** status text changes to "Simulation completed successfully",  
**And** [Cancel Simulation] button is hidden,  
**And** [View Results] button appears,  
**And** sandbox status updates to "Testing Completed",  
**And** notification is sent to user's email.

✓ **Happy Path - User Cancels Simulation:**

**Given** simulation is at 40% progress,  
**When** user clicks [Cancel Simulation],  
**Then** confirmation modal appears "Are you sure you want to cancel this simulation? Progress will be lost." with [Yes, Cancel] [No, Continue],  
**When** user clicks [Yes, Cancel],  
**Then** API call to DELETE `/api/v1/simulations/{simulation_id}` is made,  
**And** progress view displays "Simulation cancelled by user",  
**And** sandbox status reverts to "Draft",  
**And** no results are generated.

✗ **Sad Path - Simulation Fails with Error:**

**Given** simulation encounters error at 60% progress,  
**When** poll returns status "Failed" with error message "Data validation error: Missing customer records",  
**Then** progress bar turns red,  
**And** status text displays "Simulation failed: Data validation error",  
**And** error details are shown with option to [View Logs] or [Retry],  
**And** sandbox transitions to "Rejected" state with error in comments.

⚠ **Edge Case - User Navigates Away During Simulation:**

**Given** simulation is running and user navigates to another page,  
**When** user returns to sandbox detail page,  
**Then** simulation progress is still displayed with current status (polling resumes),  
**And** no progress is lost.

⚠ **Edge Case - Estimated Time Adjusts Based on Actual Performance:**

**Given** simulation initial estimate was 5 hours but progressing faster than expected,  
**When** system recalculates based on actual throughput,  
**Then** estimated time remaining updates to more accurate value (e.g., 3 hours 15 minutes),  
**And** user sees dynamically adjusted estimate.

🔴 **Error Handling - Polling API Timeout:**

**Given** simulation is running but progress API becomes unresponsive,  
**When** poll request times out after 10 seconds,  
**Then** progress view displays warning "Unable to fetch progress. Simulation may still be running. Will retry in 30 seconds",  
**And** retry logic attempts to reconnect,  
**And** simulation is not cancelled automatically.

---

## STORY 1.8: Two-Step Approval Workflow Backend and UI

**Story Title:** Implement Two-Step Approval Process with Locking and Audit Trail

**Description:**

**As a** CRR Business User,  
**I want to** require two different users to approve a sandbox before it can be implemented to production,  
**so that** no single person can unilaterally push changes to production, ensuring proper oversight and reducing risk of unauthorized changes.

**Verbatim Requirement from BRD:**

BRD 12.8: "System should support sandbox simulation functionality providing multiple instances and effective monitoring capabilities."

BRD 12.7.1: "System must track and make available for viewing any change made to a List / Risk Element / Risk Category - weight and multiplier (add/modify/delete with who/when and any justification)"

**Story Type:** Full-Stack

**Sprint Assignment:** 26.1.4

**Dependencies:**
- **Blocks:** Story 1.9 (atomic promotion requires approval completion)
- **Blocked By:** Story 1.7 (requires simulation completion)
- **External:** None

**Rally Metadata:** Team = CRR Rule Configuration, Feature = [User to populate], Iteration = 26.1.4

**Acceptance Criteria:**

✓ **Happy Path - First Approval Transition:**

**Given** sandbox is in "Testing Completed" state after successful simulation,  
**When** Approver 1 (user_id = "approver1") clicks [Approve] button on sandbox detail page,  
**Then** API call to POST `/api/v1/sandboxes/{id}/approvals` with `{"approver_user_id": "approver1", "decision": "Approved", "comments": "Risk distribution acceptable"}` is made,  
**And** new record created in `sandbox_approval` table with:
- `sandbox_id` = {id}
- `approval_step` = 1
- `approver_user_id` = "approver1"
- `decision` = "Approved"
- `approval_ts` = current timestamp
- `comments` = "Risk distribution acceptable"  
**And** sandbox `status` transitions to "Pending Approval 1",  
**And** success toast displays "Approval 1 recorded. Awaiting second approval",  
**And** audit log entry created.

✓ **Happy Path - Second Approval Transition:**

**Given** sandbox is in "Pending Approval 1" state,  
**When** Approver 2 (user_id = "approver2", different from approver1) clicks [Approve],  
**Then** API validates `approver2` ≠ `approver1`,  
**And** new record created with `approval_step` = 2,  
**And** sandbox `status` transitions to "Pending Approval 2",  
**And** [Implement] button becomes enabled,  
**And** success toast displays "Approval 2 recorded. Ready for implementation".

✗ **Sad Path - Same User Attempts Both Approvals:**

**Given** Approver 1 (user_id = "approver1") provided first approval,  
**When** same user attempts second approval,  
**Then** API returns 400 Bad Request with error "Second approver must be different from first approver",  
**And** no approval record is created,  
**And** sandbox remains in "Pending Approval 1" state,  
**And** UI displays error toast "You cannot provide both approvals. A different user must approve".

✓ **Happy Path - Rejection at First Approval:**

**Given** sandbox is in "Testing Completed" state,  
**When** Approver 1 clicks [Reject] and provides comments "Simulation shows unexpected risk spike in India market. Needs review",  
**Then** API call creates approval record with `decision` = "Rejected",  
**And** sandbox `status` transitions to "Rejected",  
**And** `rejection_comments` field populated with provided text,  
**And** sandbox creator receives notification email,  
**And** sandbox is locked (cannot edit without creating new version).

✓ **Happy Path - Rejection at Second Approval:**

**Given** sandbox is in "Pending Approval 1" state (first approval completed),  
**When** Approver 2 clicks [Reject] with comments "Conflicts with recent regulatory guidance",  
**Then** sandbox transitions to "Rejected" state,  
**And** both approval records (step 1 approved, step 2 rejected) are preserved in `sandbox_approval` table,  
**And** rejection comments are stored.

⚠ **Edge Case - Approval Locking Prevents Concurrent Edits:**

**Given** sandbox is in "Pending Approval 1" state,  
**When** user attempts to edit rules or assets,  
**Then** all edit buttons are disabled with tooltip "Cannot edit sandbox during approval process",  
**And** configuration views are read-only.

⚠ **Edge Case - Approval History Displays:**

**Given** sandbox has progressed through both approvals,  
**When** user views sandbox detail page,  
**Then** approval history section displays:
- Approval 1: [User Name], [Timestamp], Decision: Approved, Comments: [text]
- Approval 2: [User Name], [Timestamp], Decision: Approved, Comments: [text]

🔴 **Error Handling - Approval API Failure:**

**Given** Approver 1 clicks [Approve],  
**When** API call fails with 500 error,  
**Then** error toast displays "Failed to record approval. Please retry",  
**And** sandbox remains in "Testing Completed" state,  
**And** no partial approval is saved,  
**And** user can retry approval action.

---

## STORY 1.9: Atomic Promotion to Production with Transaction Rollback

**Story Title:** Implement Atomic Promotion Logic with Full Transaction Rollback on Failure

**Description:**

**As a** Backend Developer,  
**I want to** promote sandbox changes (rules + assets + FA) to production in a single atomic database transaction with automatic full rollback if any component fails,  
**so that** production never contains partial or inconsistent configurations, maintaining data integrity and preventing untested risk states.

**Verbatim Requirement from BRD:**

BRD 12.8: "System should support sandbox simulation functionality providing multiple instances and effective monitoring capabilities."

BRD 12.7.2: "Version history of the CRR module (enterprise level, market/center level and legal entity) must be maintained with a log of all the changes made to the underlying components (Lists/ Risk Element / Risk Category - weight and multiplier) along with user/implementation date details"

**Story Type:** Backend

**Sprint Assignment:** 26.1.4

**Dependencies:**
- **Blocks:** None (final implementation step)
- **Blocked By:** Story 1.8 (requires approval completion), Asset Manager versioning stories
- **External:** Database team must ensure transaction isolation level supports atomic operations

**Rally Metadata:** Team = CRR Rule Execution, Feature = [User to populate], Iteration = 26.1.4

**Acceptance Criteria:**

✓ **Happy Path - Successful Atomic Promotion:**

**Given** sandbox in "Pending Approval 2" state with:
- 5 rule changes (2 added to `risk_rule` table, 2 updated, 1 deleted)
- 3 asset version updates (assets in `asset` table with new `asset_vsn_no`)
- 1 FA override change (record in `fa_override` table)  
**When** backend receives POST `/api/v1/sandboxes/{id}/implement` with `{"user_id": "implementer1"}`,  
**Then** database transaction begins with isolation level SERIALIZABLE,  
**And** Step 1: All rule changes merged to production `risk_rule` table,  
**And** Step 2: All asset version updates applied (production rules updated to reference new `asset_vsn_no`),  
**And** Step 3: FA override changes merged to production `fa_override` table,  
**And** Step 4: Audit log entries created for all changes with `implement_ts` and `implement_user_id`,  
**And** Step 5: Transaction committed,  
**And** sandbox `status` updated to "Implemented",  
**And** sandbox moved from active list to history,  
**And** response returns 200 OK with message "Implementation successful".

✗ **Sad Path - Asset Merge Fails → Full Rollback:**

**Given** sandbox ready for implementation,  
**When** implementation begins and:
  - Rule merge completes successfully ✅
  - Asset merge encounters database deadlock ❌  
**Then** exception is caught at Step 2,  
**And** entire transaction is rolled back (rule changes reverted),  
**And** NO changes are committed to production,  
**And** sandbox `status` transitions to "Rejected",  
**And** `rejection_comments` populated with "Implementation failed: Database deadlock on asset table. Please retry or contact support. Reference ID: [transaction_id]",  
**And** response returns 500 Internal Server Error,  
**And** notification sent to implementation user and support team.

✗ **Sad Path - FA Override Validation Fails → Full Rollback:**

**Given** implementation reaches Step 3 (FA override merge),  
**When** validation discovers data constraint violation (e.g., invalid country code in override),  
**Then** transaction is rolled back,  
**And** rule and asset changes are reverted,  
**And** sandbox transitions to "Rejected" with error "Implementation failed: FA override validation error. Invalid country code 'XYZ'",  
**And** NO partial data exists in production.

✓ **Happy Path - Enterprise Asset Version Propagates to All Markets:**

**Given** Enterprise sandbox contains updated "Global_Products" asset from v1 to v2,  
**When** implementation succeeds,  
**Then** ALL markets using "Global_Products" in their production rules automatically reference v2,  
**And** update is recorded in audit log: "Asset Global_Products upgraded from v1 to v2 in markets: [IN, FR, ES]",  
**And** v1 is marked with status "Archived" in `asset` table (hidden from UI, retained for audit).

⚠ **Edge Case - Retry After Rejection:**

**Given** sandbox was rejected due to implementation failure (status "Rejected"),  
**When** user fixes underlying issue (e.g., database deadlock resolved by DBA) and clicks [Retry Implementation],  
**Then** API call to POST `/api/v1/sandboxes/{id}/implement` is made again,  
**And** sandbox transitions from "Rejected" back to "Pending Approval 2" momentarily,  
**And** new implementation attempt executes with fresh transaction.

⚠ **Edge Case - Concurrent Implementation Prevention:**

**Given** implementation request is in flight for sandbox A,  
**When** second user attempts to implement same sandbox simultaneously,  
**Then** second request is blocked with 409 Conflict error "Implementation already in progress. Please wait",  
**And** locking mechanism prevents race condition.

🔴 **Error Handling - Transaction Timeout:**

**Given** implementation transaction takes longer than configured timeout (e.g., 60 seconds),  
**When** timeout is reached before commit,  
**Then** transaction is automatically rolled back,  
**And** sandbox transitions to "Rejected" with error "Implementation timeout. Transaction exceeded 60 seconds. Contact support",  
**And** no partial changes remain in production,  
**And** database connection is released properly.

---

## STORY 1.10: Rollback Functionality - Create New Version from Historical Version

**Story Title:** Build Rollback UI and Backend to Copy Historical Version into New Editable Draft

**Description:**

**As a** CRR Business User,  
**I want to** rollback my sandbox to a previous version's configuration when simulation results are unsatisfactory,  
**so that** I can continue editing from a known-good baseline instead of manually reverting all changes.

**Verbatim Requirement from BRD:**

BRD 12.8.12: "System must maintain version control of all changes made. This must be available on the Sandbox UI."

**Story Type:** Full-Stack

**Sprint Assignment:** 26.1.5

**Dependencies:**
- **Blocks:** None
- **Blocked By:** Story 1.5 (requires versioning infrastructure)
- **External:** None

**Rally Metadata:** Team = CRR Rule Configuration, Feature = [User to populate], Iteration = 26.1.5

**Acceptance Criteria:**

✓ **Happy Path - Rollback from Non-Editable State (Testing Completed):**

**Given** sandbox is in "Testing Completed" state at Version 3 with unsatisfactory simulation results,  
**When** user clicks [View Version History], selects Version 1, and clicks [Rollback to This Version],  
**Then** confirmation modal appears "Create new version based on Version 1? Current Version 3 will remain unchanged." with [Create New Version] [Cancel],  
**When** user clicks [Create New Version],  
**Then** API call to POST `/api/v1/sandboxes/{id}/rollback` with `{"target_version_no": 1, "user_id": "user123"}` is made,  
**And** new Version 4 is created with configuration copied from Version 1:
  - All rules from Version 1 snapshot
  - All assets from Version 1 snapshot
  - All FA overrides from Version 1 snapshot  
**And** Version 4 opens in "Draft" state (editable),  
**And** sandbox transitions to "Draft" status,  
**And** success toast displays "Rollback successful. Now editing Version 4 based on Version 1",  
**And** audit log records rollback action with source and target versions.

✓ **Happy Path - Rollback from Draft State (Overwrites Uncommitted Changes):**

**Given** sandbox is in "Draft" state at Version 3 with uncommitted edits (user added 2 new rules but hasn't submitted),  
**When** user clicks [Rollback to Version 2],  
**Then** warning modal appears "This will discard all uncommitted changes in current Draft. Continue?" with [Yes, Rollback] [Cancel],  
**When** user clicks [Yes, Rollback],  
**Then** API call to POST `/api/v1/sandboxes/{id}/rollback-draft` with `{"target_version_no": 2}` is made,  
**And** Version 3's uncommitted changes are discarded,  
**And** Version 3's configuration is overwritten with Version 2's snapshot (rules/assets/FA),  
**And** sandbox remains in "Draft" state at Version 3 (no new version created),  
**And** success toast displays "Rolled back to Version 2. Uncommitted changes discarded".

✓ **Happy Path - Version History Displays All Versions:**

**Given** sandbox has 5 versions (v1 through v5),  
**When** user clicks [View Version History] button on sandbox detail page,  
**Then** modal opens displaying table with columns:
- Version No. (1, 2, 3, 4, 5)
- Created Date/Time
- Created By (user name)
- Status (Submitted, Testing Completed, Rejected, Implemented)
- Justification Comment (excerpt or full text)
- Actions ([View Details] [Rollback])  
**And** current version is highlighted,  
**And** [Rollback] button is enabled for all versions except current.

✗ **Sad Path - Rollback to Current Version Not Allowed:**

**Given** sandbox is at Version 3,  
**When** user attempts to rollback to Version 3 (current version),  
**Then** [Rollback] button is disabled with tooltip "Cannot rollback to current version",  
**And** no API call is made.

⚠ **Edge Case - Rollback Preserves Original Version Numbers:**

**Given** user rolls back from Version 4 to Version 1,  
**When** new Version 5 is created from Version 1 baseline,  
**Then** Version 1, 2, 3, 4 remain unchanged in database and version history,  
**And** Version 5 is marked as "derived from Version 1" in metadata,  
**And** audit trail shows clear lineage: v5 created via rollback from v1.

⚠ **Edge Case - User Cancels Rollback:**

**Given** rollback confirmation modal is displayed,  
**When** user clicks [Cancel],  
**Then** modal closes,  
**And** no API call is made,  
**And** sandbox remains at current version with no changes.

🔴 **Error Handling - Snapshot Retrieval Fails:**

**Given** user initiates rollback to Version 2,  
**When** backend attempts to retrieve Version 2 snapshot but encounters database error,  
**Then** response returns 500 Internal Server Error with message "Failed to retrieve version snapshot. Contact support",  
**And** no new version is created,  
**And** current sandbox state remains unchanged,  
**And** error is logged for support investigation.

---

## STORY 1.11: Complete Audit Trail Export and History View

**Story Title:** Build Audit Trail Export Functionality and History View UI

**Description:**

**As a** CRR Business User and Compliance Officer,  
**I want to** export complete audit logs for any sandbox showing all configuration changes, approvals, and implementation details,  
**so that** I can provide regulatory auditors with comprehensive change documentation and demonstrate proper oversight.

**Verbatim Requirement from BRD:**

BRD 12.7.1: "System must track and make available for viewing any change made to a List / Risk Element / Risk Category - weight and multiplier (add/modify/delete with who/when and any justification)"

BRD 12.7.2: "Version history of the CRR module (enterprise level, market/center level and legal entity) must be maintained with a log of all the changes made to the underlying components (Lists/ Risk Element / Risk Category - weight and multiplier) along with user/implementation date details"

**Story Type:** Full-Stack

**Sprint Assignment:** 26.1.5

**Dependencies:**
- **Blocks:** None
- **Blocked By:** All versioning, approval, and implementation stories (requires audit data)
- **External:** None

**Rally Metadata:** Team = CRR Rule Configuration, Feature = [User to populate], Iteration = 26.1.5

**Acceptance Criteria:**

✓ **Happy Path - Export Complete Audit Log:**

**Given** sandbox has completed full lifecycle (Draft → Testing → Approvals → Implemented),  
**When** user clicks [Export Audit Log] button on sandbox detail page,  
**Then** API call to GET `/api/v1/sandboxes/{id}/audit-log?format=csv` is made,  
**And** CSV file is generated with columns:
- Timestamp (ISO 8601 format)
- User ADS ID
- User Full Name
- Action Type (CREATE_SANDBOX, EDIT_RULE, EDIT_ASSET, SUBMIT_VERSION, APPROVE, REJECT, IMPLEMENT)
- Component Type (Sandbox, Rule, Asset, FA_Override)
- Component ID (rule_id, asset_id, etc.)
- Old Value (JSON or text representation)
- New Value (JSON or text representation)
- Justification Comment
- Version Number  
**And** file downloads with name `Sandbox_{id}_Audit_Log_{timestamp}.csv`,  
**And** all entries are sorted chronologically (oldest first).

✓ **Happy Path - Audit History View in UI:**

**Given** user is on sandbox detail page,  
**When** user clicks [View History] tab,  
**Then** audit history timeline displays showing:
- All version creation events with timestamps and users
- All configuration changes (rules added/edited/deleted, assets modified, FA changes)
- All approval/rejection events with approver names and comments
- Implementation event with success/failure status  
**And** entries are grouped by version,  
**And** expandable sections show detailed change diffs (old value → new value).

✓ **Happy Path - Audit Log Links Sandbox Version to Asset Versions:**

**Given** sandbox Version 2 contains asset "Global_Products" v3,  
**When** audit log is exported,  
**Then** entry shows:
```
Timestamp, user123, John Doe, SNAPSHOT_ASSET, Asset, 456, Global_Products v2, Global_Products v3, "Updated for Q4 compliance", 2
```  
**And** clear link between sandbox version 2 and asset version 3 is documented.

✓ **Happy Path - Filter Audit Log by Component Type:**

**Given** user is viewing audit history in UI,  
**When** user selects filter "Assets Only" from dropdown,  
**Then** timeline shows only asset-related changes (asset creation, edits, version updates),  
**And** rule and FA changes are hidden,  
**And** user can toggle filters on/off.

✗ **Sad Path - Export Fails Due to Large Data Volume:**

**Given** sandbox has 10,000+ audit entries,  
**When** user clicks [Export Audit Log],  
**Then** progress indicator displays "Generating audit log... This may take a few minutes",  
**When** export times out after 2 minutes,  
**Then** error message displays "Audit log too large to export directly. Please contact support to request archived logs",  
**And** no partial CSV is downloaded.

⚠ **Edge Case - Audit Log for Rejected Sandbox:**

**Given** sandbox was rejected during implementation with error "Database deadlock",  
**When** audit log is exported,  
**Then** final entry shows:
```
2025-01-15T10:30:00Z, system, System, IMPLEMENT_FAILED, Sandbox, 100, Pending Approval 2, Rejected, "Implementation failed: Database deadlock on asset table. Reference ID: TXN-12345", NULL
```  
**And** rejection details are captured for post-mortem analysis.

⚠ **Edge Case - Audit Log Shows Rollback Lineage:**

**Given** sandbox Version 4 was created via rollback from Version 1,  
**When** audit log is viewed,  
**Then** entry shows:
```
2025-01-14T14:20:00Z, user456, Jane Smith, ROLLBACK_VERSION, Sandbox, 100, Version 3, Version 4 (from Version 1), "Reverting to stable baseline", 4
```  
**And** lineage is clear that v4 is based on v1.

🔴 **Error Handling - Missing Audit Data:**

**Given** sandbox audit log has gaps due to system failure during historical edits,  
**When** export is requested,  
**Then** export completes with warning banner "Some audit entries may be missing due to system errors. Contact support if complete history is required",  
**And** exported CSV includes disclaimer row at top,  
**And** available entries are still provided.

---

**Total Stories for Feature 1: 11 stories**  
**Estimated Total Points: ~45 points** (within 2 sprint capacity considering Feature 2 in parallel)

---

# USER STORIES - FEATURE 2: ASSET MANAGER

---

## STORY 2.1: Asset Data Model and Core CRUD APIs

**Story Title:** Create Asset Data Model with Versioning and Core API Endpoints

**Description:**

**As a** Backend Developer,  
**I want to** implement the asset data model with lifecycle status fields, version tracking, and usage metadata, plus core CRUD API endpoints,  
**so that** the frontend can create, read, update, and delete assets with proper validation, versioning, and audit trails.

**Verbatim Requirement from BRD:**

BRD 12.6: "System should have the capability to setup and maintain all reference lists."

BRD 12.7.3: "System must track and make available for viewing any change made to the Fundamental Assessment/Notable List/ reference data (add/modify/delete with who/when and any justification)"

**Story Type:** Backend

**Sprint Assignment:** 26.1.1

**Dependencies:**
- **Blocks:** All Asset Manager frontend stories
- **Blocked By:** Story 1.1 (sandbox data model must exist first)
- **External:** Reference Data Table service must be available for validation

**Rally Metadata:** Team = CRR Rule Configuration, Feature = [User to populate], Iteration = 26.1.1

**Acceptance Criteria:**

✓ **Happy Path - Create Asset in Draft Status:**

**Given** backend receives POST `/api/v1/assets` with payload:
```json
{
  "name": "High_Risk_Industries",
  "description": "Industries flagged for enhanced due diligence",
  "list_name": "Industry_Code",
  "values": ["CASINO", "ARMS_DEALER", "CRYPTO_EXCHANGE"],
  "creat_user_id": "user123",
  "sandbox_id": 100
}
```  
**When** the API processes the request,  
**Then** values are validated against `Industry_Code` reference data table,  
**And** if all values are valid, new record created in `asset` table with:
- `asset_id` (auto-generated, primary key)
- `name` = "High_Risk_Industries" (validated for uniqueness)
- `description` = provided text
- `list_name` = "Industry_Code"
- `asset_vsn_no` = 1
- `status` = "Draft"
- `creat_ts` = current timestamp
- `creat_user_id` = "user123"  
**And** values stored in `asset_value` junction table linking `asset_id` to each value,  
**And** response returns 201 Created with complete asset object including `asset_id`.

✓ **Happy Path - Retrieve Asset with Usage Metadata:**

**Given** asset with `asset_id` = 456 exists and is used in 3 rulesets,  
**When** backend receives GET `/api/v1/assets/456?include_usage=true`,  
**Then** response returns 200 OK with asset object plus `usage_metadata` array containing:
```json
{
  "usage_metadata": [
    {
      "iso_alpha2_ctry_cd": "IN",
      "risk_elem_id": 10,
      "ruleset_id": 301,
      "rule_id": 3001,
      "ruleset_ds": "High-risk product screening"
    }
    // ... additional usage entries
  ]
}
```

✓ **Happy Path - Update Asset Creates New Version:**

**Given** asset with `asset_id` = 456, `asset_vsn_no` = 2, `status` = "Sandbox" exists,  
**When** backend receives PATCH `/api/v1/assets/456` with `{"values": ["ADDED_VALUE", ...existing values], "user_id": "user456"}`,  
**Then** system creates new version with `asset_vsn_no` = 3,  
**And** previous version (vsn_no = 2) remains immutable in database,  
**And** `status` remains "Sandbox",  
**And** `lst_updt_ts` and `lst_updt_user_id` are updated,  
**And** audit log entry created recording version change.

✗ **Sad Path - Reference Data Validation Failure:**

**Given** user attempts to create asset with invalid value "INVALID_INDUSTRY" not in `Industry_Code` reference table,  
**When** API validates values,  
**Then** response returns 400 Bad Request with error:
```json
{
  "error": "Invalid values detected",
  "invalid_values": ["INVALID_INDUSTRY"],
  "message": "Please ensure all values exist in reference data table Industry_Code"
}
```  
**And** no asset is created.

✗ **Sad Path - Duplicate Asset Name:**

**Given** asset named "High_Risk_Industries" already exists,  
**When** backend receives POST with same `name` value,  
**Then** response returns 400 Bad Request with error "Asset name must be unique. 'High_Risk_Industries' already exists",  
**And** no asset is created.

⚠ **Edge Case - Delete Draft Asset:**

**Given** asset with `asset_id` = 789, `status` = "Draft" exists and is NOT used in any rules,  
**When** backend receives DELETE `/api/v1/assets/789`,  
**Then** asset and all related `asset_value` records are permanently deleted,  
**And** response returns 204 No Content.

⚠ **Edge Case - Delete Sandbox Asset Blocked:**

**Given** asset with `status` = "Sandbox" is referenced by at least one rule,  
**When** backend receives DELETE request,  
**Then** response returns 400 Bad Request with error "Cannot delete asset. Asset is currently used in rulesets. Remove all rule references before deletion",  
**And** asset remains in database.

🔴 **Error Handling - Database Transaction Failure:**

**Given** asset creation begins and `asset` table insert succeeds but `asset_value` inserts fail,  
**When** transaction error occurs,  
**Then** entire transaction is rolled back (asset record removed),  
**And** response returns 500 Internal Server Error,  
**And** no partial data remains.

---

## STORY 2.2: Asset Creation UI in Sandbox Context

**Story Title:** Build Asset Creation Modal with Reference Data Dropdown and CSV Upload

**Description:**

**As a** CRR Business User,  
**I want to** create new assets within my sandbox by providing a name, selecting a reference data table, and uploading a CSV file of values,  
**so that** I can build reusable risk policy lists that are validated against reference data and immediately available for use in rules.

**Verbatim Requirement from BRD:**

BRD 12.6.3: "System should provide the ability to setup Centralized (notable) lists in a user friendly manner (UI/UX to facilitate the update in an efficient manner). Product consideration - to provide options and elicit business feedback on the same."

**Story Type:** Frontend

**Sprint Assignment:** 26.1.2

**Dependencies:**
- **Blocks:** Story 2.5 (asset editing depends on creation)
- **Blocked By:** Story 2.1 (requires asset APIs), Story 1.4 (sandbox sub-navigation)
- **External:** None

**Rally Metadata:** Team = CRR Rule Configuration, Feature = [User to populate], Iteration = 26.1.2

**Acceptance Criteria:**

✓ **Happy Path - Open Asset Creation Modal:**

**Given** user is inside sandbox (Draft state) and clicks "Assets" sub-nav,  
**When** user clicks [Create Asset] button,  
**Then** "Create Asset" modal opens with form fields:
- Asset Name (text input, required)
- Description (text area, optional)
- List Name (dropdown, required) - populated from available reference data tables
- CSV File Upload (file input, required)
- Buttons: [Cancel] [Save]  
**And** all fields are initially empty/unselected.

✓ **Happy Path - Select Reference Data Table:**

**Given** Create Asset modal is open,  
**When** user clicks "List Name" dropdown,  
**Then** dropdown displays available reference data tables: ["Country_Code", "Industry_Code", "Occupation_Type", "Product_Type", etc.],  
**When** user selects "Industry_Code",  
**Then** dropdown value updates to "Industry_Code",  
**And** tooltip displays "Values in uploaded CSV must match Industry_Code reference data".

✓ **Happy Path - Upload CSV and Create Asset:**

**Given** user entered name "Restricted_Industries", selected "Industry_Code", and uploaded CSV file `industries.csv` containing valid values,  
**When** user clicks [Save],  
**Then** file is read and parsed client-side,  
**And** API call to POST `/api/v1/assets` is made with `name`, `description`, `list_name`, `values` array, and `sandbox_id`,  
**When** API returns 201 Created,  
**Then** success toast displays "Asset 'Restricted_Industries' created successfully",  
**And** modal closes,  
**And** new asset appears in asset list with status "Draft".

✗ **Sad Path - Duplicate Name Validation:**

**Given** asset named "High_Risk_Products" already exists,  
**When** user enters "High_Risk_Products" in name field and clicks [Save],  
**Then** API returns 400 error "Asset name must be unique",  
**And** inline error message displays below Asset Name field: "This name is already in use. Please choose a different name",  
**And** [Save] button remains enabled for user to fix and retry.

✗ **Sad Path - Invalid CSV Values:**

**Given** user uploaded CSV with values ["VALID_CODE", "INVALID_CODE"] and "INVALID_CODE" is not in reference data,  
**When** API returns 400 error with `invalid_values: ["INVALID_CODE"]`,  
**Then** error message displays above CSV upload field: "Invalid values detected: INVALID_CODE. Please ensure all values match reference data table Industry_Code",  
**And** user can download corrected CSV template or edit and re-upload.

⚠ **Edge Case - Empty CSV File:**

**Given** user uploads CSV file with no data rows (only headers or completely empty),  
**When** file is parsed,  
**Then** validation error displays "CSV file is empty. Please upload a file with at least one value",  
**And** [Save] button is disabled until valid file is uploaded.

⚠ **Edge Case - Large CSV File Warning:**

**Given** user uploads CSV with 10,000 values,  
**When** file size exceeds threshold (e.g., 5MB or 10K rows),  
**Then** warning message displays "Large file detected. Validation may take a moment. Please wait",  
**And** spinner shows while file is being processed,  
**And** user cannot click [Save] until processing completes.

🔴 **Error Handling - API Timeout During Creation:**

**Given** user clicks [Save] and API request times out after 30 seconds,  
**When** timeout occurs,  
**Then** error toast displays "Request timeout. Asset creation may have failed. Please refresh the page and check if asset was created",  
**And** modal remains open allowing user to retry,  
**And** if asset was actually created (backend succeeded but response didn't return), duplicate name validation will catch it on retry.

---

## STORY 2.3: Asset Status Transition from Draft to Sandbox on First Use

**Story Title:** Implement Automatic Asset Status Update When Asset is Used in Rule

**Description:**

**As a** Backend Developer,  
**I want to** automatically transition asset status from "Draft" to "Sandbox" when the asset is first selected as a value in any rule,  
**so that** asset usage is tracked and editability rules are properly enforced based on where the asset is being used.

**Verbatim Requirement from BRD:**

BRD 12.8.9: "All reference data sets that are referenced by the CRR module should be available in the Sandbox environment. In particular (and as example) - Notable Lists, Centralized List/Fundamental Assessments"

**Story Type:** Backend

**Sprint Assignment:** 26.1.2

**Dependencies:**
- **Blocks:** Story 2.5 (editability rules depend on status), Story 2.7 (versioning depends on status)
- **Blocked By:** Story 2.1 (requires asset data model)
- **External:** Rule configuration service must trigger status update when rule references asset

**Rally Metadata:** Team = CRR Rule Configuration, Feature = [User to populate], Iteration = 26.1.2

**Acceptance Criteria:**

✓ **Happy Path - First Rule Reference Triggers Status Change:**

**Given** asset with `asset_id` = 123, `status` = "Draft" exists,  
**When** user configures rule R-500 and selects asset 123 from value dropdown,  
**Then** rule configuration service calls PATCH `/api/v1/assets/123/usage` with payload:
```json
{
  "rule_id": 500,
  "ruleset_id": 200,
  "risk_elem_id": 10,
  "iso_alpha2_ctry_cd": "IN"
}
```  
**And** asset `status` is updated from "Draft" to "Sandbox",  
**And** new record created in `asset_usage` table linking:
- `asset_id` = 123
- `rule_id` = 500
- `ruleset_id` = 200
- `risk_elem_id` = 10
- `iso_alpha2_ctry_cd` = "IN"
- `usage_start_ts` = current timestamp  
**And** `lst_updt_ts` is updated on asset,  
**And** response returns 200 OK.

✓ **Happy Path - Subsequent Rule References Do Not Change Status:**

**Given** asset with `status` = "Sandbox" is already used in rule R-500,  
**When** user configures another rule R-600 and selects same asset,  
**Then** new usage record is created in `asset_usage` table for R-600,  
**And** asset `status` remains "Sandbox" (no change),  
**And** usage metadata now shows 2 rulesets referencing the asset.

✓ **Happy Path - Retrieve Usage Metadata:**

**Given** asset 123 is used in 3 rules across 2 rulesets in India market,  
**When** backend receives GET `/api/v1/assets/123/usage`,  
**Then** response returns array:
```json
[
  {
    "iso_alpha2_ctry_cd": "IN",
    "risk_elem_id": 10,
    "risk_elem_nm": "Product Type",
    "ruleset_id": 200,
    "ruleset_ds": "High-risk product screening",
    "rule_id": 500,
    "rule_logic_tx": "Product IN High_Risk_Industries"
  }
  // ... additional entries
]
```  
**And** response includes count of total usages.

✗ **Sad Path - Invalid Rule Reference (Rule Does Not Exist):**

**Given** usage update request references `rule_id` = 999 which doesn't exist in `risk_rule` table,  
**When** API validates the request,  
**Then** response returns 400 Bad Request with error "Invalid rule_id. Rule 999 does not exist",  
**And** no usage record is created,  
**And** asset status remains unchanged.

⚠ **Edge Case - Remove Last Rule Reference (Status Remains Sandbox):**

**Given** asset is used in only one rule R-500 (status "Sandbox"),  
**When** user deletes rule R-500,  
**Then** usage record for R-500 is deleted from `asset_usage` table,  
**And** asset `status` remains "Sandbox" (does NOT revert to "Draft"),  
**And** asset can still be edited following sandbox editability rules.

⚠ **Edge Case - Cross-Market Usage Tracking:**

**Given** asset is used in India (IN) and France (FR) markets,  
**When** usage metadata is queried,  
**Then** response shows separate entries for each market with distinct `iso_alpha2_ctry_cd` values,  
**And** shared asset detection logic identifies asset as "shared" based on multiple market codes in usage table.

🔴 **Error Handling - Concurrent Status Update:**

**Given** two users simultaneously configure rules that reference same Draft asset,  
**When** both trigger status update requests concurrently,  
**Then** database locking ensures only one update succeeds,  
**And** both usage records are created (one per rule),  
**And** asset status transitions to "Sandbox" exactly once,  
**And** no race condition or data corruption occurs.

---

## STORY 2.4: Asset Visibility - All Assets Visible Everywhere with Indicators

**Story Title:** Build Asset List View Showing All Assets with Visual Indicators for Shared Status

**Description:**

**As a** CRR Business User,  
**I want to** see all assets in the system regardless of status or usage scope, with visual indicators (color accents) showing which assets are shared across multiple markets,  
**so that** I understand the full asset inventory and can identify which assets require special handling (copy-on-write) when editing.

**Verbatim Requirement from BRD:**

BRD 12.6.1: "System must have the capability to setup/update these reference lists at the below levels: > Enterprise > Center/Market specific > Legal Entity > Product"

**Story Type:** Frontend

**Sprint Assignment:** 26.1.3

**Dependencies:**
- **Blocks:** Story 2.5 (editing depends on visibility), Story 2.6 (copy workflow depends on shared detection)
- **Blocked By:** Story 2.1 (requires asset APIs), Story 2.3 (usage tracking enables shared detection)
- **External:** None

**Rally Metadata:** Team = CRR Rule Configuration, Feature = [User to populate], Iteration = 26.1.3

**Acceptance Criteria:**

✓ **Happy Path - All Assets Visible in Enterprise Sandbox:**

**Given** user opens Enterprise sandbox and navigates to Assets sub-nav,  
**When** asset list loads via API call GET `/api/v1/assets?sandbox_id={id}`,  
**Then** all assets are displayed in table with columns:
- Asset Name
- Description
- List Name (reference data table)
- Status (Draft / Sandbox / Production)
- Last Updated
- Actions ([View] [Edit] [Export])  
**And** assets with status "Draft" are shown with no special indicator,  
**And** assets with status "Sandbox" or "Production" used in multiple markets have colored border or background (e.g., light yellow accent) as visual indicator of "shared" status,  
**And** no text labels like "Shared Asset" are displayed (indicator is purely visual).

✓ **Happy Path - All Assets Visible in Market Sandbox:**

**Given** user opens India Market sandbox and navigates to Assets,  
**When** asset list loads,  
**Then** all assets in system are displayed (same as Enterprise view),  
**And** shared assets (used in markets other than India OR used in Enterprise) have visual color indicator,  
**And** local assets (used ONLY in India market) have no special indicator,  
**And** tooltip on shared asset row displays on hover: "This asset is used in multiple markets: [India, France, Spain]".

✓ **Happy Path - Shared Asset Detection Logic:**

**Given** asset "APAC_Countries" has usage records in `asset_usage` table with `iso_alpha2_ctry_cd` = ["IN", "SG", "FR"],  
**When** frontend receives asset data with usage metadata,  
**Then** frontend logic detects `usage_metadata.length > 1` OR presence of 'XX' (Enterprise) in market codes,  
**And** applies "shared" visual styling (colored border/background),  
**And** tooltip text is generated listing distinct markets from usage metadata.

✓ **Happy Path - Draft Assets Have No Indicator:**

**Given** asset "New_Test_Asset" has `status` = "Draft" and is not used in any rules,  
**When** asset appears in list,  
**Then** no color indicator is shown (standard row styling),  
**And** tooltip displays "Draft asset - not yet used in any rules".

✗ **Sad Path - API Failure Loading Assets:**

**Given** user opens Assets tab in sandbox,  
**When** API call to GET `/api/v1/assets` fails with 500 error,  
**Then** error message displays "Failed to load assets. Please retry",  
**And** empty state with [Retry] button is shown,  
**When** user clicks [Retry],  
**Then** API call is attempted again.

⚠ **Edge Case - Asset List Pagination for Large Inventories:**

**Given** system contains 500+ assets,  
**When** asset list loads,  
**Then** pagination controls display at bottom showing "Page 1 of 10 (50 assets per page)",  
**And** user can navigate pages without losing filter/sort settings,  
**And** shared asset indicators are correctly displayed on all pages.

⚠ **Edge Case - Search/Filter Assets by Name:**

**Given** user enters "Risk" in search box above asset list,  
**When** search is triggered,  
**Then** asset list filters to show only assets with names containing "Risk" (e.g., "High_Risk_Products", "Risk_Countries"),  
**And** shared indicators remain visible on filtered results,  
**And** count displays "Showing 15 of 120 assets".

🔴 **Error Handling - Usage Metadata Missing:**

**Given** asset has `status` = "Sandbox" but usage metadata API call fails,  
**When** shared detection logic runs,  
**Then** asset is displayed with warning icon and tooltip "Unable to determine usage scope. Assume shared for safety",  
**And** asset is treated as shared (edit triggers copy-on-write) to prevent accidental cross-market impact.

---

## STORY 2.5: Asset Editability Rules - Draft, Local, and Shared

**Story Title:** Implement Asset Edit Permission Logic Based on Status and Usage Scope

**Description:**

**As a** Backend Developer,  
**I want to** enforce editability rules that allow Draft assets to be edited anywhere, local Sandbox assets to be edited in their market, and shared Sandbox assets to trigger copy-on-write workflow,  
**so that** users cannot accidentally modify assets used in other markets and production integrity is maintained.

**Verbatim Requirement from BRD:**

BRD 12.6.4: "Access to setup a new list and/or update the lists will be controlled by User Access Permissions (should be configurable)."

**Story Type:** Backend

**Sprint Assignment:** 26.1.3

**Dependencies:**
- **Blocks:** Story 2.6 (copy-on-write depends on editability check)
- **Blocked By:** Story 2.3 (requires usage tracking), Story 2.4 (shared detection)
- **External:** None

**Rally Metadata:** Team = CRR Rule Configuration, Feature = [User to populate], Iteration = 26.1.3

**Acceptance Criteria:**

✓ **Happy Path - Draft Asset Editable in Any Sandbox:**

**Given** asset with `asset_id` = 100, `status` = "Draft" exists,  
**When** backend receives GET `/api/v1/assets/100/editability?sandbox_id=200&sandbox_scope=India` (from India Market sandbox),  
**Then** response returns:
```json
{
  "editable": true,
  "edit_mode": "direct",
  "reason": "Draft assets are globally editable"
}
```  
**And** frontend allows direct editing without copy prompt.

✓ **Happy Path - Local Sandbox Asset Editable in Home Market:**

**Given** asset with `status` = "Sandbox" is used ONLY in India market (`iso_alpha2_ctry_cd` = "IN" in all usage records),  
**When** backend receives editability check from India Market sandbox,  
**Then** response returns:
```json
{
  "editable": true,
  "edit_mode": "version",
  "reason": "Asset is local to this market"
}
```  
**And** editing creates new version (backend handles versioning on save).

✗ **Sad Path - Shared Sandbox Asset Not Editable in Market:**

**Given** asset is used in India (IN) and France (FR) markets (shared),  
**When** backend receives editability check from India Market sandbox,  
**Then** response returns:
```json
{
  "editable": false,
  "edit_mode": "copy_required",
  "reason": "Asset is shared across multiple markets: [IN, FR]",
  "shared_markets": ["India", "France"]
}
```  
**And** frontend triggers copy-on-write workflow instead of direct edit.

✓ **Happy Path - All Assets Editable in Enterprise Sandbox:**

**Given** any asset (Draft, Sandbox, or Production status),  
**When** backend receives editability check from Enterprise sandbox,  
**Then** response returns:
```json
{
  "editable": true,
  "edit_mode": "version",
  "reason": "Enterprise sandbox can edit all assets"
}
```  
**And** editing creates new version that propagates to all markets on promotion.

✗ **Sad Path - Production Asset Not Editable Outside Sandbox:**

**Given** asset with `status` = "Production",  
**When** backend receives editability check with `sandbox_id` = null (request from standalone Asset Manager view),  
**Then** response returns:
```json
{
  "editable": false,
  "edit_mode": "none",
  "reason": "Production assets can only be edited within a sandbox"
}
```  
**And** frontend disables/hides edit button in standalone view.

⚠ **Edge Case - Enterprise-Only Asset Editable in Enterprise Sandbox:**

**Given** asset is used ONLY in Enterprise rulesets (`iso_alpha2_ctry_cd` = "XX"),  
**When** editability is checked from Enterprise sandbox,  
**Then** response returns `editable: true, edit_mode: "version"`,  
**When** editability is checked from any Market sandbox,  
**Then** response returns `editable: false, edit_mode: "copy_required"` (even though not used in other markets, Enterprise assets require Enterprise sandbox for editing).

⚠ **Edge Case - Sandbox Non-Editable State Blocks All Edits:**

**Given** sandbox is in "Testing Completed" state (not "Draft"),  
**When** editability check includes sandbox status,  
**Then** response returns:
```json
{
  "editable": false,
  "edit_mode": "none",
  "reason": "Sandbox is not in editable state"
}
```  
**And** all asset edit actions are blocked regardless of asset status.

🔴 **Error Handling - Usage Metadata Unavailable:**

**Given** editability check is requested but usage metadata API call fails,  
**When** backend cannot determine if asset is shared,  
**Then** response returns:
```json
{
  "editable": false,
  "edit_mode": "error",
  "reason": "Unable to determine asset usage. Contact support."
}
```  
**And** editing is blocked to prevent accidental cross-market impact.

---

## STORY 2.6: Copy-on-Write Workflow with Duplicate Name Validation

**Story Title:** Build Shared Asset Copy UI with Real-Time Duplicate Validation

**Description:**

**As a** CRR Business User,  
**I want to** be prompted to create a copy when I attempt to edit a shared asset from a Market sandbox, with automatic duplicate name detection and validation,  
**so that** I can safely customize shared assets for my market without impacting other markets, and avoid naming conflicts.

**Verbatim Requirement from BRD:**

BRD 12.6.1: "System must have the capability to setup/update these reference lists at the below levels: > Enterprise > Center/Market specific > Legal Entity > Product"

**Story Type:** Full-Stack

**Sprint Assignment:** 26.1.4

**Dependencies:**
- **Blocks:** None
- **Blocked By:** Story 2.5 (requires editability check), Story 2.4 (shared detection)
- **External:** None

**Rally Metadata:** Team = CRR Rule Configuration, Feature = [User to populate], Iteration = 26.1.4

**Acceptance Criteria:**

✓ **Happy Path - Shared Asset Edit Triggers Copy Prompt:**

**Given** user in India Market sandbox clicks [Edit] on shared asset "APAC_Countries" (used in IN, SG, FR),  
**When** editability API returns `edit_mode: "copy_required"`,  
**Then** confirmation modal appears with message:
```
This asset has been used across multiple markets:
• India
• Singapore  
• France

Would you like to create a copy and customize?
```  
**And** buttons: [Create a Copy] [Cancel].

✓ **Happy Path - Copy Modal Opens with Pre-Filled Fields:**

**Given** user clicked [Create a Copy],  
**When** Edit Asset modal opens,  
**Then** form fields are pre-populated:
- Asset Name = "APAC_Countries_copy" (with real-time duplicate validation active)
- Description = copied from original "APAC country list for geographic risk"
- List Name = "Country_Code" (disabled, grayed out, cannot be changed)
- CSV file = original values pre-loaded (user can download or replace)  
**And** [Save] button is initially ENABLED if "APAC_Countries_copy" is unique.

✓ **Happy Path - Real-Time Duplicate Validation:**

**Given** Edit Asset modal is open with default name "APAC_Countries_copy" but this name already exists,  
**When** modal loads and API call to GET `/api/v1/assets/validate-name?name=APAC_Countries_copy` returns `{exists: true}`,  
**Then** inline error message appears below Asset Name field: "Asset with this name already exists. Please choose a different name",  
**And** [Save] button is DISABLED,  
**When** user changes name to "APAC_Countries_India",  
**Then** validation API is called again returning `{exists: false}`,  
**And** error message disappears,  
**And** [Save] button becomes ENABLED.

✓ **Happy Path - Save Copy Creates New Asset:**

**Given** user modified name to "APAC_Countries_India" (unique), description, and uploaded new CSV,  
**When** user clicks [Save],  
**Then** API call to POST `/api/v1/assets` is made with:
```json
{
  "name": "APAC_Countries_India",
  "description": "India-specific APAC country list",
  "list_name": "Country_Code",
  "values": [...new values from CSV],
  "creat_user_id": "user123",
  "sandbox_id": 200,
  "copied_from_asset_id": 456
}
```  
**And** new asset is created with new `asset_id`, `status` = "Draft",  
**And** modal closes,  
**And** success toast displays "Copy created: APAC_Countries_India",  
**And** new asset appears in asset list.

✗ **Sad Path - User Cancels Copy Workflow:**

**Given** confirmation modal "Would you like to create a copy?" is displayed,  
**When** user clicks [Cancel],  
**Then** modal closes,  
**And** no copy is created,  
**And** no API calls are made,  
**And** user returns to asset list (original shared asset remains unmodified).

✗ **Sad Path - Save Fails Due to Invalid CSV Values:**

**Given** user uploaded CSV with invalid values during copy creation,  
**When** API validates and finds errors,  
**Then** response returns 400 Bad Request with `invalid_values: ["BAD_VALUE"]`,  
**And** error message displays "Invalid values detected: BAD_VALUE. Please correct and retry",  
**And** modal remains open for user to fix CSV and re-save.

⚠ **Edge Case - Duplicate Validation on Modal Open:**

**Given** default copy name "Asset_Name_copy" already exists in system,  
**When** Edit Asset modal opens,  
**Then** validation runs immediately (on modal load) before user interacts,  
**And** error appears right away,  
**And** [Save] button is disabled,  
**And** user must rename before saving.

⚠ **Edge Case - User Keeps Original Values:**

**Given** copy modal is open with original CSV pre-loaded,  
**When** user changes only the name to "APAC_Countries_India" but does NOT upload new CSV,  
**Then** [Save] creates copy with same values as original,  
**And** copy is valid (duplicate values are allowed, only names must be unique).

🔴 **Error Handling - Validation API Timeout:**

**Given** user types new name and validation API times out,  
**When** 10 seconds elapse without response,  
**Then** warning message displays "Unable to validate name. Please retry",  
**And** [Save] button remains disabled until validation succeeds or user clicks [Retry Validation] button.

---

## STORY 2.7: Enterprise Asset Versioning and Automatic Market Propagation

**Story Title:** Implement Enterprise Asset Version Creation with Auto-Propagation to Markets

**Description:**

**As a** Backend Developer,  
**I want to** create new asset versions when edited in Enterprise sandbox and automatically propagate those versions to all markets using the asset upon promotion,  
**so that** enterprise-wide asset changes are consistently applied across all markets and version history is maintained for audit.

**Verbatim Requirement from BRD:**

BRD 12.7.2: "Version history of the CRR module (enterprise level, market/center level and legal entity) must be maintained with a log of all the changes made to the underlying components (Lists/ Risk Element / Risk Category - weight and multiplier) along with user/implementation date details"

**Story Type:** Backend

**Sprint Assignment:** 26.1.4

**Dependencies:**
- **Blocks:** None (final promotion logic)
- **Blocked By:** Story 1.9 (atomic promotion), Story 2.5 (editability rules)
- **External:** None

**Rally Metadata:** Team = CRR Rule Execution, Feature = [User to populate], Iteration = 26.1.4

**Acceptance Criteria:**

✓ **Happy Path - Enterprise Sandbox Asset Edit Creates New Version:**

**Given** Enterprise sandbox in Draft state contains asset "Global_Products" with `asset_id` = 100, `asset_vsn_no` = 2,  
**When** user edits asset (adds 3 values) and saves,  
**Then** new version record created with `asset_vsn_no` = 3,  
**And** `asset` table updated:
- `asset_vsn_no` = 3
- `lst_updt_ts` = current timestamp
- `lst_updt_user_id` = editing user  
**And** v2 remains immutable (archived in version history),  
**And** sandbox now references v3 in `sandbox_asset_snapshot` table,  
**And** response returns 200 OK with updated asset object.

✓ **Happy Path - Version Captured in Sandbox Snapshot:**

**Given** Enterprise sandbox contains "Global_Products" v3 after editing,  
**When** user clicks Submit for Simulation,  
**Then** sandbox version snapshot links `sandbox_version_id` to `asset_id` = 100 with `asset_vsn_no` = 3,  
**And** simulation uses v3 for risk calculations,  
**And** version lineage is established: Sandbox Version 1 → Global_Products v3.

✓ **Happy Path - Promotion Propagates Asset Version to All Markets:**

**Given** Enterprise sandbox is promoted containing "Global_Products" v3,  
**And** India Market production uses v2, France Market production uses v2,  
**When** atomic promotion succeeds,  
**Then** production `risk_rule` records in India and France are updated:
- India Rule R-200: `asset_id` = 100, references now point to `asset_vsn_no` = 3
- France Rule R-400: `asset_id` = 100, references now point to `asset_vsn_no` = 3  
**And** v2 status changes to "Archived",  
**And** v3 status changes to "Production",  
**And** audit log entries created:
```
Asset Global_Products upgraded from v2 to v3 in markets: [India, France]
User: system, Timestamp: 2025-01-15T10:00:00Z
Triggered by Enterprise Sandbox Implementation: sandbox_id=500
```

✓ **Happy Path - Retrieve Asset Version History:**

**Given** asset "Global_Products" has versions v1, v2, v3,  
**When** backend receives GET `/api/v1/assets/100/versions`,  
**Then** response returns array:
```json
[
  {
    "asset_vsn_no": 3,
    "creat_ts": "2025-01-15T10:00:00Z",
    "creat_user_id": "user123",
    "status": "Production",
    "value_count": 25,
    "sandbox_id": 500
  },
  {
    "asset_vsn_no": 2,
    "creat_ts": "2025-01-10T14:00:00Z",
    "creat_user_id": "user456",
    "status": "Archived",
    "value_count": 22,
    "sandbox_id": 400
  },
  // ... v1
]
```

✗ **Sad Path - Promotion Fails, Version Not Propagated:**

**Given** Enterprise sandbox promotion encounters error during asset propagation,  
**When** transaction rolls back (per Story 1.9),  
**Then** India and France markets continue using v2 in production,  
**And** v3 remains in sandbox (not promoted),  
**And** audit log shows failed promotion attempt with error details.

⚠ **Edge Case - Market Has Stopped Using Enterprise Asset:**

**Given** India Market previously used "Global_Products" v2 but later switched to custom asset "India_Products",  
**When** Enterprise promotes "Global_Products" v3,  
**Then** India rules are NOT updated (they reference different asset),  
**And** only France (still using Global_Products) gets v3,  
**And** audit log notes: "Global_Products v3 applied to: [France]. Skipped: [India - using different asset]".

⚠ **Edge Case - Version History Preserves Old Sandbox Links:**

**Given** v2 was created in Sandbox 400, v3 in Sandbox 500,  
**When** version history is queried,  
**Then** each version record includes `sandbox_id` showing which sandbox created it,  
**And** audit trail can reconstruct "v2 came from Sandbox 400 implemented on 2025-01-10".

🔴 **Error Handling - Concurrent Version Creation:**

**Given** two users in same Enterprise sandbox attempt to edit same asset simultaneously,  
**When** both save requests arrive concurrently,  
**Then** database locking ensures sequential processing,  
**And** first save creates v3, second save creates v4,  
**And** no version numbers are skipped or duplicated,  
**And** both edits are preserved in version history.

---

## STORY 2.8: Asset Export with Two-Sheet Workbook Format

**Story Title:** Build Asset Export Functionality Generating Excel with Values and References Sheets

**Description:**

**As a** CRR Business User,  
**I want to** export any asset to an Excel file containing a "Values" sheet with all asset values and a "References" sheet showing where the asset is used,  
**so that** I can share asset documentation with auditors, analyze usage patterns, and maintain offline records of risk policy lists.

**Verbatim Requirement from BRD:**

BRD 12.13.2: "System should have the ability to generate a report with all the Fundamental Assessments / Centralized Lists / Notable Lists - This should be available at the following levels - > Enterprise > Center/Market specific > Product > Legal Entity"

**Story Type:** Full-Stack

**Sprint Assignment:** 26.1.5

**Dependencies:**
- **Blocks:** None
- **Blocked By:** Story 2.3 (usage metadata required for References sheet)
- **External:** Excel generation library (e.g., ExcelJS or similar)

**Rally Metadata:** Team = CRR Rule Configuration, Feature = [User to populate], Iteration = 26.1.5

**Acceptance Criteria:**

✓ **Happy Path - Export Asset with Usage:**

**Given** asset "High_Risk_Products" with `asset_id` = 100, `asset_vsn_no` = 2 is used in 3 rulesets,  
**When** user clicks [Export] button on asset detail page,  
**Then** API call to GET `/api/v1/assets/100/export` is made,  
**And** backend generates Excel workbook with:

**Sheet 1: "Values"**
| Value |
|-------|
| CASINO |
| ARMS_DEALER |
| CRYPTO_EXCHANGE |
| ... |

**Sheet 2: "References"**
| Scope | Status | Risk Category | Risk Element | Ruleset | Rule |
|-------|--------|---------------|--------------|---------|------|
| India Market | Production | Product Risk | Product Type | High-risk product screening rules | Product IN High_Risk_Products |
| India Market | Production | Product Risk | Product Combination | Combined risk assessment | Product IN High_Risk_Products AND Jurisdiction = 'India' |
| France Market | Production | Product Risk | Product Type | Produits à risque élevé | Product IN High_Risk_Products |

**And** file downloads with name `High_Risk_Products_v2.xlsx`.

✓ **Happy Path - Values Sheet Formatting:**

**Given** asset has 150 values,  
**When** workbook is generated,  
**Then** Values sheet contains:
- Header row: "Value" (bold, background color)
- Data rows: one value per row
- Auto-fit column width
- No row limits (all values included)  
**And** values are sorted alphabetically (optional enhancement).

✓ **Happy Path - References Sheet Column Details:**

**Given** References sheet is populated,  
**Then** columns contain:
- **Scope**: "Enterprise" OR "{Market Name} Market" (e.g., "India Market", not "IN")
- **Status**: "Draft" OR "Sandbox" OR "Production" (never "Archived")
- **Risk Category**: Human-readable category name (e.g., "Product Risk")
- **Risk Element**: Human-readable element name (e.g., "Product Type")
- **Ruleset**: Ruleset description text (not ruleset_id)
- **Rule**: Rule logic text (e.g., "Product IN High_Risk_Products", not rule_id)  
**And** all column headers are bold with background color.

✗ **Sad Path - Asset Has No Usage (Empty References Sheet):**

**Given** asset "Draft_Test_Asset" is in Draft status and not used in any rules,  
**When** export is triggered,  
**Then** Values sheet contains all asset values,  
**And** References sheet exists but contains only header row with message in cell A2: "This asset is not currently used in any rules",  
**And** export completes successfully.

✗ **Sad Path - Export API Fails:**

**Given** user clicks [Export],  
**When** API returns 500 error due to database timeout,  
**Then** error toast displays "Failed to generate export. Please try again",  
**And** no partial file is downloaded,  
**And** user can retry export action.

⚠ **Edge Case - Large Asset with 5000 Values:**

**Given** asset has 5000 values and 50 ruleset references,  
**When** export is generated,  
**Then** progress indicator displays "Generating export... this may take a moment",  
**And** workbook is created with all 5000 rows in Values sheet and 50 rows in References sheet,  
**And** file size is acceptable (< 10MB),  
**And** download completes successfully within 30 seconds.

⚠ **Edge Case - Asset Name with Special Characters:**

**Given** asset name is "High-Risk/Restricted_Products (2025)",  
**When** filename is generated,  
**Then** special characters are sanitized: `High-Risk_Restricted_Products_2025_v1.xlsx`,  
**And** file downloads without OS errors.

🔴 **Error Handling - Incomplete Usage Metadata:**

**Given** usage metadata API returns partial data (some rulesets missing due to data inconsistency),  
**When** export is generated,  
**Then** References sheet includes available data,  
**And** warning note added to sheet footer: "Note: Some usage references may be missing due to data inconsistency. Contact support if complete data is required",  
**And** export completes (does not fail completely).

---

## STORY 2.9: Standalone Asset Manager Read-Only View

**Story Title:** Build Standalone Asset Manager View Filtered by Market Scope (Read-Only)

**Description:**

**As a** Market Compliance Officer,  
**I want to** view production assets used in my market from the standalone Asset Manager tab without editing capabilities,  
**so that** I can understand what risk policy lists are currently active in my market for reference and documentation purposes.

**Verbatim Requirement from BRD:**

BRD 12.6.4: "Access to setup a new list and/or update the lists will be controlled by User Access Permissions (should be configurable)."

**Story Type:** Frontend

**Sprint Assignment:** 26.1.5

**Dependencies:**
- **Blocks:** None
- **Blocked By:** Story 2.3 (usage tracking for filtering)
- **External:** None

**Rally Metadata:** Team = CRR Rule Configuration, Feature = [User to populate], Iteration = 26.1.5

**Acceptance Criteria:**

✓ **Happy Path - Market Dropdown Filters Production Assets:**

**Given** user navigates to standalone Asset Manager tab (outside sandbox),  
**When** page loads,  
**Then** market dropdown displays at top with options: ["India", "France", "Spain", "Belgium", etc.],  
**When** user selects "Belgium",  
**Then** API call to GET `/api/v1/assets?scope=production&market=BE` is made,  
**And** asset list displays only assets currently used in Belgium's production rulesets,  
**And** table shows columns: Asset Name, Description, List Name, Last Updated, Actions ([Export] only - no Edit or Delete).

✓ **Happy Path - Only Production Assets Displayed:**

**Given** system contains assets with statuses: Draft (5), Sandbox (10), Production (30), Archived (20),  
**When** standalone view loads for any market,  
**Then** only 30 Production assets are displayed,  
**And** Draft, Sandbox, and Archived assets are filtered out (not visible).

✓ **Happy Path - No Edit or Delete Buttons:**

**Given** user views asset list in standalone mode,  
**When** user hovers over any asset row,  
**Then** only [Export] action button is displayed,  
**And** [Edit] and [Delete] buttons are hidden/removed,  
**And** clicking on asset row opens detail view (read-only) showing values and metadata but no edit form.

✗ **Sad Path - Market Has No Production Assets:**

**Given** user selects "New_Market" which has no production rulesets yet,  
**When** asset list loads,  
**Then** empty state displays with message "No production assets found for New_Market. Assets will appear here once rulesets are deployed to production",  
**And** no assets are shown in table.

⚠ **Edge Case - User Changes Market Selection:**

**Given** user is viewing Belgium assets,  
**When** user changes dropdown to "India",  
**Then** asset list refreshes to show India's production assets,  
**And** previous Belgium assets are replaced (not appended),  
**And** no loading state flicker if cached data available.

⚠ **Edge Case - Asset Detail View Read-Only:**

**Given** user clicks on asset "High_Risk_Industries" in standalone view,  
**When** detail modal/page opens,  
**Then** all fields are read-only (no text inputs, no edit buttons),  
**And** values are displayed as static list,  
**And** usage metadata shows where asset is used (References section),  
**And** only action available is [Export].

🔴 **Error Handling - API Timeout Loading Assets:**

**Given** user selects market and API call times out after 30 seconds,  
**When** timeout occurs,  
**Then** error message displays "Unable to load assets. Please try again",  
**And** [Retry] button is shown,  
**When** user clicks [Retry],  
**Then** API call is re-attempted.

---

**Total Stories for Feature 2: 9 stories**  
**Estimated Total Points: ~35 points**

---

# SPRINT ASSIGNMENT SUMMARY

## Sprint 26.1.1 (Capacity: 35 points)
**Focus: Backend Foundations**
- Story 1.1: Sandbox Data Model and APIs (5 points)
- Story 2.1: Asset Data Model and APIs (5 points)
- Story 1.2: Sandbox Creation UI (3 points)
**Total: 13 points**

## Sprint 26.1.2 (Capacity: 35 points)
**Focus: Lifecycle and Basic Editing**
- Story 1.3: Sandbox Lifecycle State Management (5 points)
- Story 1.4: Sandbox Detail View with Sub-Nav (4 points)
- Story 2.2: Asset Creation UI (4 points)
- Story 2.3: Asset Status Transitions (5 points)
**Total: 18 points**

## Sprint 26.1.3 (Capacity: 35 points)
**Focus: Versioning and Simulation**
- Story 1.5: Sandbox Versioning Backend (5 points)
- Story 1.6: Submit for Simulation Workflow (5 points)
- Story 1.7: Simulation Progress Tracking (4 points)
- Story 2.4: Asset Visibility with Indicators (4 points)
- Story 2.5: Asset Editability Rules (5 points)
**Total: 23 points**

## Sprint 26.1.4 (Capacity: 35 points)
**Focus: Approval and Promotion**
- Story 1.8: Two-Step Approval Workflow (5 points)
- Story 1.9: Atomic Promotion Logic (5 points)
- Story 2.6: Copy-on-Write Workflow (5 points)
- Story 2.7: Enterprise Asset Propagation (5 points)
**Total: 20 points**

## Sprint 26.1.5 (Capacity: ~17 points - finishes mid-sprint)
**Focus: Rollback, Audit, Export**
- Story 1.10: Rollback Functionality (5 points)
- Story 1.11: Audit Trail Export (4 points)
- Story 2.8: Asset Export (4 points)
- Story 2.9: Standalone Read-Only View (3 points)
**Total: 16 points**

---

**GRAND TOTAL: 90 points across 20 user stories**  
**Target: Complete by mid-Sprint 26.1.5**

All stories are sequenced to minimize dependencies and ensure smooth delivery. Backend foundations are built first, followed by UI and integration work, with polish and audit features at the end.

**Ready for next step: User Journey Tree Diagrams?**