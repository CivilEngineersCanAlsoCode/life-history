---
description: Task Management and Memory Management expert called Beads, to be used before execution of any plan with more than 3 steps
---

# Agent Instructions

This project uses **bd** (beads Go v0.59.0+) for ALL issue tracking. Run `bd quickstart` to get started.

> **IMPORTANT**: Do NOT use `br` (beads_rust). It lacks memory features (remember/memories/prime).
> Install bd (Go) via: `npm install -g @beads/bd`

## Quick Reference

```bash
bd ready              # Find available work (unblocked issues)
bd show <id>          # View issue details
bd update <id> --claim  # Claim work atomically
bd close <id>         # Complete work
bd sync               # Sync with git
bd dolt pull          # Pull beads updates from remote
bd prime              # Load session context (auto-runs on session start)
```

## Non-Interactive Shell Commands

**ALWAYS use non-interactive flags** to avoid hanging on confirmation prompts.

```bash
cp -f source dest           # NOT: cp source dest
mv -f source dest           # NOT: mv source dest
rm -f file                  # NOT: rm file
rm -rf directory            # NOT: rm -r directory
```

Other commands: `scp -o BatchMode=yes` | `ssh -o BatchMode=yes` | `apt-get -y` | `HOMEBREW_NO_AUTO_UPDATE=1 brew`

## Issue Tracking with bd (beads)

### Why bd?

- Dependency-aware: Track blockers and relationships
- Version-controlled: Built on Dolt with cell-level merge + memory system
- Agent-optimized: JSON output, ready work detection, remember/memories/prime
- Single source of truth: No markdown TODOs, no external trackers

### Issue Hierarchy

When planning work, use this hierarchy (top-down):

```
Epic (E)           → High-level goal (numbered: E1, E2...)
  Feature (F)      → Capability within epic (F1.1, F1.2...)
    User Story (US)→ User-facing requirement (US1, US2...)
      Task (T)     → Atomic work item
        Subtask    → Sub-step if task is complex
```

Create with:
```bash
bd create --type=epic --title="E1: <goal>" -p <0-4>
bd create --type=feature --parent=<epic-id> --title="F1.1: <capability>" -p <0-4>
bd create --type=task --parent=<feature-id> --title="US1: <requirement>" -p <0-4>
bd create --type=task --parent=<story-id> --title="<atomic-work>" -p <0-4>
```

Wire dependencies: `bd dep <blocker-id> --blocks <blocked-id>`
View tree: `bd dep tree <epic-id>`

### Issue Types

| Type    | Use For                              |
|---------|--------------------------------------|
| epic    | Large feature with subtasks          |
| feature | New functionality                    |
| task    | Work item (tests, docs, refactoring) |
| bug     | Something broken                     |
| chore   | Maintenance (deps, tooling)          |

### Priorities

| Priority | Level    | Use When                             |
|----------|----------|--------------------------------------|
| 0        | Critical | Security, data loss, broken builds   |
| 1        | High     | Major features, important bugs       |
| 2        | Medium   | Default, nice-to-have                |
| 3        | Low      | Polish, optimization                 |
| 4        | Backlog  | Future ideas                         |

### Agent Workflow

1. **Find work**: `bd ready` → shows unblocked issues
2. **Claim**: `bd update <id> --claim`
3. **Work**: Implement, test, verify
4. **Discover new work?** Create linked: `bd create "Found bug" -p 1 --deps discovered-from:<parent-id>`
5. **Complete**: `bd close <id>`
6. **Auto-commit**: Every 5th close → auto-commit checkpoint

### Auto-Sync

bd auto-syncs with git:
- Exports to `.beads/issues.jsonl` after changes (5s debounce)
- Imports from JSONL when newer (e.g., after `git pull`)

### Rules

- Use bd for ALL task tracking
- Use `--json` flag for programmatic use
- Link discovered work with `discovered-from` dependencies
- Check `bd ready` before asking "what should I work on?"
- Do NOT create markdown TODO lists
- Do NOT use external issue trackers
- Do NOT use `bd edit` (opens $EDITOR, blocks agents)

## Session Protocol

### Starting

```bash
bd prime              # Auto-runs via hook, loads context
bd dolt pull          # Pull latest beads
bd ready              # Find available work
```

### Closing (MANDATORY)

1. File issues for remaining work
2. Run quality gates (if code changed)
3. Update issue status
4. Push to remote:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status          # MUST show "up to date with origin"
   ```
5. Verify all changes committed AND pushed

**CRITICAL**: Work is NOT complete until `git push` succeeds. NEVER stop before pushing.
