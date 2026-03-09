# life_brain

Personal AI second brain — semantic search across career history, life experiences, and knowledge.

## Quick Start

```bash
git clone <repo> && cd Career-context
pip install -r life_brain/requirements.txt
cp .env.example .env   # fill in API keys
```

## Run Tests

```bash
pytest life_brain/tests/ -q
```

## Project Structure

| Directory | Purpose |
|-----------|---------|
| `life_brain/core/` | Database (ChromaDB), ingestion, batch metrics, validation |
| `life_brain/conversation/` | Conversation flows, intent detection, expert routing, emotional tracking |
| `life_brain/truth/` | Conflict detection, groundedness, hallucination prevention |
| `life_brain/retrieval/` | Semantic search, QA generation, source attribution |
| `life_brain/session/` | Session state, continuity, multi-turn context |
| `life_brain/testing/` | Load tests, latency benchmarks, resilience tests |
| `life_brain/tests/` | Full test suite (3156 tests) |

## Docs

- [Architecture](docs/architecture.md)
- [Configuration Guide](docs/configuration-guide.md)
- [Getting Started](docs/noob-onboarding.md)
- [Troubleshooting](docs/troubleshooting-guide.md)
