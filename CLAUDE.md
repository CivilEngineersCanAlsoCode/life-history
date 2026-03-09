# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


# Life Brain — AI Second Brain

## What This Is

An AI-powered personal knowledge base. Store life experiences, career history, and knowledge in ChromaDB. Search semantically. Get grounded, citation-backed answers from your own data.

## How It Works

The system runs through Claude Code using `.agents/workflows/sync-life.md` as the conversation protocol:
1. Mode gate detects intent (small talk vs guided knowledge capture)
2. Use case selector matches your intent to 40+ guided flows
3. Expert introduction sets the conversation persona
4. One-by-one Q&A captures knowledge with 15-question templates
5. Data ingests into ChromaDB with rich metadata

## Repository Structure

```
Career-context/
├── .agents/workflows/sync-life.md   # Conversation protocol (THE user interface)
├── .env.example                     # API key template
├── life_brain/
│   ├── config.py                    # System configuration
│   ├── core/                        # ChromaDB, ingestion, batch processing
│   ├── conversation/                # Intent, mode gate, experts, Q&A flows
│   ├── truth/                       # Groundedness, conflict detection
│   ├── retrieval/                   # Semantic search, QA generation
│   ├── session/                     # Multi-turn session management
│   └── tests/                       # Test suite (3000+ tests)
├── docs/                            # Configuration, onboarding, troubleshooting
└── context/                         # Templates for knowledge capture
```

## Key Conventions

- **Language**: Communicate in Romanized Hindi (Hinglish) unless user switches to English.
- **Knowledge template**: 15 standardized questions per project for consistent capture.
- **Metadata**: company, project, category, role, date range, type, confidence, source.

---

# Development Guidelines

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.

## Workflow

- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately
- Never mark a task complete without proving it works (run tests, demonstrate correctness)
- For non-trivial changes: pause and ask "is there a more elegant way?"

## Critical Rules

- **Stop and pivot**: If you get stuck and fail repeatedly (2-3 attempts), stop. Explain what's failing and suggest an alternative.
- **Context directory**: `context/` is READ-ONLY. Never modify files inside it.
- **Archive directory**: `archive/` contains local-only files (personal data, dev artifacts). Not tracked by git.
