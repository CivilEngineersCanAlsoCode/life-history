# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
