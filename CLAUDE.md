# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


# Workflow Orchestration
## 1. Plan Mode Default

- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately — don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity
- Use beads for task tracking and memory management by reading file - `.agents/workflows/sync-beads.md`

## 2. Subagent Strategy

- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution

## 3. Self-Improvement Loop

- After ANY correction from the user: update tasks/lessons.md with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

## 4. Verification Before Done

- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

## 5. Demand Elegance (Balanced)

- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes — don't over-engineer
- Challenge your own work before presenting it

## 6. Autonomous Bug Fixing

- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests — then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

---

## Task Management

1. **Plan First**: Write plan to tasks/todo.md with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review section to tasks/todo.md
6. **Capture Lessons**: Update tasks/lessons.md after corrections

---

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.

---

## Critical Rules

- **Language**: Communicate with user in Romanized Hindi (Hinglish) unless they switch to English.
- **Stop and pivot**: If you get stuck on an operation and fail repeatedly (2-3 attempts), do NOT push through or brute-force it. Stop immediately, explain what's failing and why, and suggest an alternative approach. Ask the user before continuing.
- **Context directory**: `context/` is READ-ONLY. Never modify files inside it.


# Project Context


## Repository Purpose

Personal career knowledge base and "second brain" for Satvik Jain. Contains career history, project documentation, interview prep, STAR stories, and reference materials. The long-term goal is to build a comprehensive AI-searchable life history stored in a vector database (ChromaDB).

## Repository Structure

```
career history/
├── 00 - Identity & Resume/     # Resume, portfolio, performance reviews, interview prep
│   ├── Interview Prep/         # STAR stories, resume brain index
│   ├── Resume & Portfolio/     # PDF resume, HTML portfolio
│   └── performance-review/     # Year-end reviews
├── 01 - Experience/
│   ├── 01 - Sprinklr (Apr 2022 – Jul 2024)/
│   │   ├── CGB (Citizen Governance Bot)/
│   │   ├── Use Case Hub/
│   │   └── Walmart Spark Driver Support/
│   └── 02 - American Express (Jul 2024 – Present)/
│       └── 01 - CRR AML Risk Scoring Engine/  # Primary active project
└── 02 - Resources & Learning/
```

Each project folder typically contains:
- A 15-question interview template with detailed answers (problem definition, personas, discovery, architecture, metrics, AI/ML, scalability, monetization, stakeholders, execution, competition, UX, failure modes, strategy, ownership)
- Brain dump / resume brain docs
- Documentation & reference materials (PDFs, confluence exports)

## Key Conventions

- **Language**: Content and conversations are in Hinglish (Hindi-English mix). Respond in the same style when working with content.
- **Interview template**: 15 standardized questions per project for consistent knowledge capture.
- **File naming**: Numbered prefixes for ordering (01, 02, ...). Projects organized by company with date ranges.
- **Content types**: MD files for editable content, PDFs for reference docs and exports.

## Issue Tracking

Uses `bd` (beads) for issue tracking. See system prompt for full command reference.

## Vector DB Strategy (Planned)

Target: ChromaDB with rich metadata tagging per document chunk:
- company, project, category, subcategory, role, date range, type, confidence, source
- Designed for filtered semantic search across career and life history
- Atomic knowledge units (Q&A pairs, facts, metrics, STAR stories)
