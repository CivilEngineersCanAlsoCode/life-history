# Meta-Prompt: Asset Manager System Design Analysis
## For Solution Architect / Product Manager / Tech Lead

---

## Context

You are a world-class Solution Architect tasked with designing an **Asset Manager** system for a Customer Risk Rating (CRR) platform used by American Express. This system must handle:
- Enterprise-level and Market-level configurations
- Sandbox-based testing workflows
- Asset versioning and lifecycle management
- Cross-scope asset sharing and copy-on-write mechanisms
- Complex approval and promotion workflows

Your goal: Design a system that is **maximally flexible** for users while avoiding **complicated edge cases** or **hard-coded workarounds**.

---

## Your Task: Systematic Design Analysis

Please conduct a **structured, step-by-step analysis** of the Asset Manager system design. For each section below, think deeply, identify constraints, propose solutions, and validate against edge cases.

---

## SECTION 1: Core Requirements Analysis

### 1.1 User Personas & Needs
**Question:** Who are the users and what do they need?

Analyze:
- CRR Business User (full permissions)
- Market Compliance Officer (view-only, market-restricted)
- What workflows must each persona complete?
- What frustrations must we eliminate from the current system?

### 1.2 System Scope & Boundaries
**Question:** What is IN scope vs OUT of scope?

Define:
- What entities does Asset Manager manage? (Assets, Versions, Sandbox references)
- What does it NOT manage? (Rules, FA configurations, customer data)
- Integration points with other systems?

### 1.3 Success Metrics
**Question:** How do we measure if this design is successful?

Define:
- User productivity metrics (time to create/test/promote)
- System reliability metrics (conflict resolution success rate)
- Flexibility metrics (can we add new asset types without code changes?)

---

## SECTION 2: State Machine Design

### 2.1 Asset Lifecycle States
**Question:** What are ALL possible states an asset can be in?

For each state, define:
- **Entry condition:** How does an asset enter this state?
- **Exit condition:** What triggers transition to next state?
- **Allowed operations:** What can users do in this state?
- **Forbidden operations:** What is NOT allowed and why?

States to analyze:
1. DRAFT
2. SANDBOX
3. PRODUCTION
4. ARCHIVED
5. (Any others?)

### 2.2 State Transition Rules
**Question:** What are the valid transitions between states?

For each transition, document:
- Trigger event (e.g., "link to rule", "promote sandbox", "newer version promoted")
- Pre-conditions that must be true
- Post-conditions that are guaranteed
- Can this transition FAIL? Under what conditions?

### 2.3 Invalid State Scenarios
**Question:** What states are IMPOSSIBLE and why?

Examples:
- Can an asset be PRODUCTION and DRAFT simultaneously? (NO - why?)
- Can two versions both be PRODUCTION? (NO - why?)
- Can ARCHIVED assets be unarchived? (Design decision needed)

---

## SECTION 3: Versioning Strategy

### 3.1 Version Creation Logic
**Question:** When is a new version created?

Analyze:
- User explicitly edits existing version
- Copy-on-write scenario
- System-triggered version creation?
- Versioning granularity (per asset or per change?)

### 3.2 Version Identification
**Question:** How do we uniquely identify versions?

Options to evaluate:
- Sequential numbers (V1, V2, V3...)
- Timestamps
- Hash-based (git-style)
- Composite (AssetID + VersionNo)

For chosen approach, validate:
- Can users understand it?
- Is it globally unique?
- Does it support rollback?

### 3.3 Version Limits
**Question:** Should there be limits on version count?

Analyze:
- Performance implications of unlimited versions
- UI/UX complexity with 100+ versions
- Storage costs
- Auditability requirements (must keep all versions forever?)

### 3.4 Active Version Logic
**Question:** How do we determine which version is "active"?

**Critical Rule (from context):** Only ONE version can be PRODUCTION at a time.

Validate:
- When V2 is promoted, does V1 automatically get ARCHIVED?
- Do ALL scopes (Enterprise + all markets) use the same PRODUCTION version?
- What happens to rules referencing V1 when V2 becomes PRODUCTION?
- Is there ANY scenario where split-version is valid? (Answer: NO)

---

## SECTION 4: Sandbox Interaction Model

### 4.1 Sandbox-Asset Relationship
**Question:** What is the cardinality and ownership model?

Define:
- Can one sandbox reference multiple assets? (YES)
- Can one asset be referenced by multiple sandboxes? (Design decision)
- Does sandbox "own" assets or "reference" them?
- What happens to assets when sandbox is promoted/rejected/archived?

### 4.2 Snapshot Mechanism
**Question:** When and how are asset versions "frozen" for simulation?

Analyze:
- At what point is snapshot taken? (Submit time? Simulation start time?)
- What data is captured in snapshot?
- Can asset be edited while simulation is running?
- What if referenced asset is deleted during simulation queue time?

### 4.3 Mutual Exclusion Rule
**Question:** Why can't Enterprise sandbox and Market sandbox coexist?

Document:
- Root cause of the constraint (staleness problem)
- Alternative designs that could avoid this constraint
- Trade-offs of chosen approach
- User education required

---

## SECTION 5: Cross-Scope Sharing & Copy-on-Write

### 5.1 Global Visibility
**Question:** When is an asset visible to other scopes?

Define:
- Are DRAFT assets visible globally? (Design decision)
- Are SANDBOX assets visible to other markets?
- Can a Market create an asset and "hide" it from Enterprise?
- Privacy/security implications?

### 5.2 Copy-on-Write Trigger
**Question:** When does system force user to create a copy?

Analyze scenarios:
- Market tries to edit Enterprise PRODUCTION asset
- Market tries to edit another Market's SANDBOX asset
- Enterprise tries to edit Market's PRODUCTION asset
- User tries to edit asset while simulation is running

For each, define:
- Block edit (force copy) OR
- Allow edit (create new version) OR
- Warn and let user choose

### 5.3 Copy Naming Convention
**Question:** How are copied assets named?

Options:
- Auto-suffix: "High_Risk_Countries_IN"
- User-provided name during copy
- Keep same name but different asset ID (confusing?)

Validate:
- No name collisions
- User can trace lineage (which asset was copied from where)

### 5.4 Copy Independence
**Question:** After copy, are the two assets truly independent?

Clarify:
- If Enterprise updates original, does copy get updated? (NO)
- Can user "sync" copy with original later? (Design decision)
- How to show divergence in UI?

---

## SECTION 6: Conflict Resolution Framework

### 6.1 Concurrent Edit Detection
**Question:** How do we detect when two users edit same asset?

Analyze:
- Optimistic locking (version_no column)
- Pessimistic locking (row-level locks)
- Last-write-wins (dangerous!)
- Chosen approach and trade-offs?

### 6.2 Conflict Types
**Question:** What types of conflicts can occur?

Enumerate:
- **Edit-Edit:** Two users edit same asset version
- **Edit-Delete:** User A edits, User B deletes
- **Edit-Promote:** User A editing V1 while User B promotes V2
- **Delete-Reference:** Asset deleted while referenced in active sandbox
- (Others?)

### 6.3 Conflict Resolution UI
**Question:** How does user resolve conflicts?

For each conflict type, design:
- How is conflict presented to user?
- What options do they have? (Merge, Overwrite, Reload, Cancel)
- Can system auto-resolve some conflicts?
- What if user chooses wrong option? (Undo mechanism?)

---

## SECTION 7: Deletion & Archival Strategy

### 7.1 Soft Delete vs Hard Delete
**Question:** When user "deletes" an asset, what really happens?

Options:
- Soft delete (mark as deleted, keep in DB)
- Hard delete (remove from DB)
- Move to ARCHIVED state
- Prevent deletion if referenced anywhere

Validate:
- Auditability requirements (compliance, regulatory)
- Can deleted assets be recovered?
- Performance impact of soft deletes

### 7.2 Orphaned Assets
**Question:** What happens to assets not used anywhere?

Define:
- How do we detect orphaned assets?
- Auto-archive after N days?
- Manual cleanup workflow?
- Do we warn user before auto-cleanup?

### 7.3 ARCHIVED State Behavior
**Question:** What can users do with ARCHIVED assets?

Clarify:
- Can they view ARCHIVED assets?
- Can they restore ARCHIVED assets to PRODUCTION?
- Can they delete ARCHIVED assets permanently?
- How long do we keep ARCHIVED versions?

---

## SECTION 8: Edge Case Enumeration

### 8.1 Systematic Edge Case Discovery
**Question:** How do we ensure we've found ALL edge cases?

**Method:** For each pair of entities/operations, ask "What if...?"

Matrix to complete:

| Entity 1 | Operation 1 | Entity 2 | Operation 2 | What Happens? | Handled? |
|----------|-------------|----------|-------------|---------------|----------|
| Asset V1 | In PRODUCTION | User | Edits V1 | Create V2 | ✅ |
| Asset A1 | Referenced in Sandbox | User | Deletes A1 | ? | ? |
| Sandbox | In simulation | Referenced Asset | Gets edited | ? | ? |
| Asset V2 | Just promoted | Rule | Still uses V1 | Auto-switch to V2 | ✅ |
| ... | ... | ... | ... | ... | ... |

(Complete this matrix for ALL combinations)

### 8.2 Extreme Scenarios
**Question:** What happens in extreme cases?

Test:
- 1000+ versions of same asset
- 100+ sandboxes referencing same asset
- Asset with 1M+ values
- Simultaneous promotion of 10 sandboxes
- Network partition during promotion
- Database failure mid-transaction

### 8.3 User Error Scenarios
**Question:** What can users do wrong and how do we protect them?

Analyze:
- Upload invalid values (misspelled country names)
- Delete asset still in use
- Promote conflicting changes
- Rollback to very old version
- Rapid submit-cancel-submit cycles

For each, design:
- Validation (prevent error)
- Error message (guide user to fix)
- Recovery flow (undo/rollback)

---

## SECTION 9: Performance & Scalability

### 9.1 Query Performance
**Question:** What are the most frequent queries?

Identify:
- "Get latest PRODUCTION version of asset"
- "List all assets used in sandbox"
- "Check if asset is referenced anywhere"
- "Get full version history"

For each, ensure:
- Proper database indexes
- Query response time < X ms
- No N+1 query problems

### 9.2 Transaction Boundaries
**Question:** What operations must be atomic?

Define:
- Sandbox promotion (rules + assets + FA all-or-nothing)
- Asset version creation
- Copy-on-write operation
- Status transitions

For each:
- ACID properties maintained?
- Rollback strategy on failure?
- Idempotency (can retry safely)?

### 9.3 Concurrency Limits
**Question:** How many concurrent operations can system handle?

Test:
- 100 users creating sandboxes simultaneously
- 50 sandboxes in simulation queue
- 10 promotions to production at once
- Peak load vs steady state

---

## SECTION 10: Data Model Validation

### 10.1 Entity Relationship Diagram
**Question:** Are all relationships properly modeled?

Validate:
- Asset ↔ Asset_Version (1:N)
- Asset_Version ↔ Sandbox (M:N via reference table)
- Asset_Version ↔ Asset_Value (1:N)
- Rule ↔ Asset_Version (M:N)

For each relationship:
- Cardinality correct?
- Cascading deletes safe?
- Referential integrity enforced?

### 10.2 Immutability Guarantees
**Question:** What data must NEVER change?

Define:
- Once simulation snapshot is taken, configuration is immutable
- Once promoted to production, that version is immutable
- Audit logs are append-only

Enforce:
- Database constraints
- Application-level checks
- Code reviews

---

## SECTION 11: User Experience Design Principles

### 11.1 Principle: Least Surprise
**Question:** Does the system behave as users expect?

Validate:
- When they edit an asset, do they get a new version or modify existing?
- When they delete, is it reversible?
- When they promote, do all changes go live or just selected ones?

### 11.2 Principle: Progressive Disclosure
**Question:** Do we show right level of detail at right time?

Design:
- Summary view: Show latest version only
- Detail view: Show last 10 versions
- Full history: Show all versions (paginated)

### 11.3 Principle: Clear Consequences
**Question:** Do users understand impact before taking action?

For critical actions, show:
- "This will affect 5 markets and 20 rules"
- "This will archive V1 and make V2 active everywhere"
- "This cannot be undone"

---

## SECTION 12: Testing Strategy

### 12.1 Unit Test Coverage
**Question:** What units need testing?

List:
- Asset version creation logic
- State transition validations
- Copy-on-write trigger conditions
- Conflict detection algorithm

### 12.2 Integration Test Scenarios
**Question:** What workflows need end-to-end testing?

Cover:
- Full sandbox lifecycle (create → edit → simulate → approve → promote)
- Asset copy-on-write flow
- Concurrent edit conflict resolution
- Rollback to previous version

### 12.3 Negative Test Cases
**Question:** What should FAIL gracefully?

Test:
- Promote sandbox with deleted asset
- Edit asset during simulation
- Delete asset referenced in 10 sandboxes
- Upload 1GB file as asset values

---

## SECTION 13: Migration & Backward Compatibility

### 13.1 Legacy System Migration
**Question:** How do we migrate from old system?

Plan:
- Export existing asset values
- Import into new version-controlled system
- Set initial version as V1, status as PRODUCTION
- Preserve audit history

### 13.2 Breaking Changes
**Question:** What if we need to change asset structure later?

Examples:
- Add new status type
- Change versioning scheme
- Modify copy-on-write rules

For each:
- Backward compatibility strategy
- Migration script
- Communication plan

---

## SECTION 14: Observability & Debugging

### 14.1 Audit Logging
**Question:** What events must be logged?

Track:
- Asset created/edited/deleted (who, when, what changed)
- Version promoted/archived
- Copy-on-write triggered
- Conflict occurred and how resolved

### 14.2 Debugging Tools
**Question:** How do we troubleshoot issues?

Provide:
- Asset version history viewer
- "Who references this asset" query
- Simulation snapshot inspector
- Conflict resolution history

---

## SECTION 15: Final Validation Checklist

### 15.1 Design Completeness
**Did we answer:**
- [ ] All state transitions defined?
- [ ] All edge cases identified and handled?
- [ ] All conflict types resolved?
- [ ] All deletion scenarios covered?
- [ ] All performance bottlenecks addressed?

### 15.2 Design Quality
**Does the design have:**
- [ ] No hard-coded exceptions?
- [ ] No "if (specialCase)" logic?
- [ ] Clear, consistent rules?
- [ ] Understandable by non-technical PMs?
- [ ] Implementable by development team?

### 15.3 User Flexibility
**Can users:**
- [ ] Create assets freely?
- [ ] Version assets as needed?
- [ ] Share assets across scopes?
- [ ] Customize per market?
- [ ] Rollback when needed?
- [ ] Understand what system will do before acting?

---

## OUTPUT FORMAT

For each section above, provide:

1. **Analysis:** Thoughtful examination of the question
2. **Design Decision:** Clear choice with rationale
3. **Trade-offs:** What we gain vs what we lose
4. **Edge Cases:** Specific scenarios to validate
5. **Implementation Notes:** Guidance for developers
6. **User Impact:** How this affects PM/business users

---

## Success Criteria

Your design is successful if:

✅ **No edge case is unhandled** - Every "what if" has an answer
✅ **No hard-coded special cases** - Rules are consistent and general
✅ **Maximum user flexibility** - Users can accomplish tasks without workarounds  
✅ **System is debuggable** - When issues occur, we can trace root cause
✅ **Design is explainable** - A PM can understand the logic without engineering background

---

**Now, begin your systematic analysis using this framework.**
