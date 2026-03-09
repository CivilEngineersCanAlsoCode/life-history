# life_brain

Personal AI second brain — capture, search, and converse with your life knowledge.

Store career history, project experiences, and personal knowledge in a semantic vector database (ChromaDB). Get grounded, citation-backed answers from your own data.

## How It Works

life_brain runs through [Claude Code](https://claude.ai/code) as the conversational interface. The agent workflow handles:

1. **Mode gate** — detects if you want casual chat or guided knowledge capture
2. **Intent matching** — maps your request to 40+ guided conversation flows
3. **Expert personas** — adapts conversation style to the domain
4. **Structured Q&A** — captures knowledge using a 15-question template
5. **Ingestion** — stores everything in ChromaDB with rich metadata for semantic search

## Quick Start

```bash
git clone <repo> && cd Career-context
pip install -r life_brain/requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY, OPENAI_API_KEY
```

Then open the project in Claude Code and start talking. The agent reads `.agents/workflows/sync-life.md` to know how to run sessions.

## Run Tests

```bash
pytest life_brain/tests/ -q
```

## Project Structure

| Directory | Purpose |
|-----------|---------|
| `life_brain/core/` | ChromaDB initialization, document ingestion, batch processing |
| `life_brain/conversation/` | Mode gate, intent detection, expert routing, Q&A flows |
| `life_brain/truth/` | Groundedness checking, conflict detection, hallucination prevention |
| `life_brain/retrieval/` | Semantic search, alternative question retrieval, source attribution |
| `life_brain/session/` | Session state, multi-turn continuity, cross-session context |
| `life_brain/tests/` | Full test suite |

## Docs

- [Getting Started](docs/noob-onboarding.md)
- [Configuration Guide](docs/configuration-guide.md)
- [Troubleshooting](docs/troubleshooting-guide.md)
- [15Q Knowledge Template](docs/project-template-15q.md)
- [Organization Guide](docs/organization-guide.md)
