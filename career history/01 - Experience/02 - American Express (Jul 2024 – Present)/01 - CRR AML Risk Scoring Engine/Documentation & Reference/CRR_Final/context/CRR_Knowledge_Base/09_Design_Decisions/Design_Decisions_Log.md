# Design Decisions Log

## Purpose

This document records all finalized design decisions for CRR 2.0. Each decision includes context, options considered, final choice, and rationale.

---

## Decision 1: Enterprise-Only Asset Creation

### Context
Assets are reusable lists used across rules. The question was: Should markets be able to create their own assets?

### Options Considered
| Option | Description |
|--------|-------------|
| A | Markets can create and own assets |
| B | Enterprise-only asset creation |
| C | Hybrid: Markets can create but Enterprise approves |

### Final Decision
> **Option B: Enterprise-Only Asset Creation**

### Rationale
1. **Single source of truth** - One place to manage all assets
2. **Prevents duplicates** - No "High Risk Countries" in India and "Risky Countries" in China
3. **Cross-market consistency** - Same values across all markets
4. **Simpler governance** - One team manages asset lifecycle
5. **Audit simplicity** - Clear ownership and versioning

### Implication
- Markets can USE production assets but cannot CREATE new ones
- Markets can EDIT assets that are exclusively used by their market only
- Enterprise sandbox required for new asset creation

---

## Decision 2: Sandbox Coexistence

### Context
Can Enterprise and Market sandboxes exist at the same time?

### Options Considered
| Option | Description |
|--------|-------------|
| A | Mutual exclusion (only one type at a time) |
| B | Full coexistence |

### Final Decision
> **Option B: Enterprise and Market sandboxes CAN coexist**

### Rationale
1. **Parallel work** - Enterprise and markets can work simultaneously
2. **No blocking** - Markets not blocked waiting for Enterprise
3. **Different scopes** - Enterprise changes don't conflict with market-specific rules
4. **Flexibility** - Supports real-world team structures

### Implication
- Multiple market sandboxes can exist concurrently
- One Enterprise sandbox can exist alongside market sandboxes
- Asset editing rules prevent conflicts (Enterprise owns shared assets)

---

## Decision 3: Asset Versioning on First Edit

### Context
When does a new asset version get created?

### Options Considered
| Option | Description |
|--------|-------------|
| A | New version on every save |
| B | New version only when sandbox is submitted |
| C | Inline edit until submit, then freeze |

### Final Decision
> **Option C: Inline edit until submit, then new version on further edits**

### Rationale
1. **Reduces version explosion** - Don't create V2, V3, V4 for 3 typo fixes
2. **Clear snapshot** - Version represents "submitted state"
3. **Audit alignment** - Version maps to specific approval cycle

### Behavior
```
DRAFT asset → V1
Link to sandbox → V1 (SANDBOX state)
Edit before submit → V1 updated inline
Submit sandbox → V1 frozen
Edit after submit → V2 created
```

---

## Decision 4: Cross-Market Asset Update Ownership

### Context
If an asset is used by multiple markets, who can edit it?

### Options Considered
| Option | Description |
|--------|-------------|
| A | Any market can edit (with conflict resolution) |
| B | Last user wins |
| C | Enterprise ownership for shared assets |

### Final Decision
> **Option C: Enterprise ownership for shared assets**

### Rationale
1. **No conflicts** - One owner, one version
2. **Coordinated testing** - All affected markets tested together
3. **Clear accountability** - Enterprise team responsible

### Behavior
```
Asset used by 1 market only → That market can edit
Asset used by 2+ markets → Enterprise sandbox required
```

---

## Decision 5: Simulation Skip for FA-Only Changes

### Context
Can simulation be skipped if only FA scores change (no rule logic changes)?

### Options Considered
| Option | Description |
|--------|-------------|
| A | Always require simulation |
| B | Skip simulation for FA-only changes |

### Final Decision
> **Option B: Simulation can be skipped for FA-only changes**

### Rationale
1. **FA score changes are pre-validated** - Based on 10-question assessment
2. **No rule logic change** - Same rules, different multiplier values
3. **Time savings** - Skip lengthy simulation for minor FA updates

### Implication
- Approval still required
- Two-person rule still applies

---

## Decision 6: Two User Types Only

### Context
How many user roles should the system have?

### Options Considered
| Option | Description |
|--------|-------------|
| A | Multiple granular roles (Viewer, Editor, Approver, Admin) |
| B | Two simple roles (Viewer, Editor) |

### Final Decision
> **Option B: Two simple roles**

### Rationale
1. **Simplicity** - Easier to manage and explain
2. **Sufficient granularity** - Two-person rule handles approval separation
3. **RBAC not needed** - Small user base, enterprise context

### User Types
- **Viewer**: Market Compliance Officer (read-only)
- **Editor**: CRR Business User (full edit)

---

## Decision 7: Asset Status States

### Context
What lifecycle states should assets have?

### Final Decision
> **5 states: DRAFT, SANDBOX, PRODUCTION, ARCHIVE, DELETE**

### State Definitions
| State | Meaning |
|-------|---------|
| DRAFT | Created, not linked anywhere |
| SANDBOX | Linked to rule in sandbox |
| PRODUCTION | Live in production |
| ARCHIVE | Replaced by newer version |
| DELETE | Soft-deleted |

---

## Decision 8: Prohibited Score (10)

### Context
What does a score of 10 mean?

### Final Decision
> **Score 10 = Prohibited = Cannot onboard customer**

### Behavior
- Customer with score 10 is flagged as prohibited
- Business rules prevent account opening
- Separate workflow for exceptions (out of CRR scope)

---

*Update this document when new design decisions are finalized.*
