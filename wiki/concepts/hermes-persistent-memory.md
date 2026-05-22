---
title: "Hermes Persistent Memory"
type: concept
tags: [concept, ai-agent, memory, sqlite, context-window]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-agent-docs/website/docs"]
confidence: high
---

## Definition

Hermes Persistent Memory is a bounded, curated memory system that persists across sessions. It consists of two character-limited text files injected into the system prompt as a frozen snapshot at session start, plus an FTS5-backed session search for recalling past conversations.

## How It Works

### Memory Files

| File | Purpose | Char Limit | Typical Tokens |
|------|---------|------------|----------------|
| **MEMORY.md** | Agent's personal notes — environment facts, conventions, lessons learned | 2,200 chars | ~800 tokens |
| **USER.md** | User profile — preferences, communication style, expectations | 1,375 chars | ~500 tokens |

Both live in `~/.hermes/memories/`. The agent manages them via the `memory` tool (`add`, `replace`, `remove` actions).

### Frozen Snapshot Pattern

Memory content is captured once at session start and never changes mid-conversation. This preserves the LLM's prefix cache for performance. Changes during a session are persisted to disk immediately but only appear in the system prompt on the next session start. Tool responses always show the live state.

### System Prompt Rendering

```
══════════════════════════════════════════════
MEMORY (your personal notes) [67% — 1,474/2,200 chars]
══════════════════════════════════════════════
User's project is a Rust web service at ~/code/myapi using Axum + SQLx
§
This machine runs Ubuntu 22.04, has Docker and Podman installed
§
User prefers concise responses, dislikes verbose explanations
```

Entries are separated by `§` (section sign) delimiters. The header shows usage percentage and character counts so the agent knows capacity.

### Session Search

All CLI and messaging sessions are stored in SQLite (`~/.hermes/state.db`) with FTS5 full-text search. The `session_search` tool queries actual messages from the DB — no LLM summarization, no truncation. Returns in ~20ms.

| Feature | Persistent Memory | Session Search |
|---------|------------------|----------------|
| Capacity | ~1,300 tokens total | Unlimited |
| Speed | Instant (in system prompt) | ~20ms FTS5 query |
| Cost | Token cost in every prompt | Free — no LLM calls |
| Management | Agent-curated | Automatic |

### External Memory Providers

8 plugins provide deeper memory: Honcho, OpenViking, Mem0, Hindsight, Holographic, RetainDB, ByteRover, Supermemory. They run alongside built-in memory (never replacing it), adding knowledge graphs, semantic search, automatic fact extraction, and cross-session user modeling.

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `memory.memory_enabled` | `true` | Enable MEMORY.md |
| `memory.user_profile_enabled` | `true` | Enable USER.md |
| `memory.memory_char_limit` | 2200 | MEMORY.md character limit |
| `memory.user_char_limit` | 1375 | USER.md character limit |

## When To Use

- **Critical facts that should always be in context**: project structure, conventions, environment setup → save to `memory`.
- **User identity and style**: name, role, communication preferences → save to `user`.
- **Finding specifics from past conversations**: "did we discuss X last week?" → use `session_search`.

## Risks & Pitfalls

- **Capacity exhaustion**: At 80%+ capacity, consolidate entries before adding new ones. Merge related entries into shorter, denser versions.
- **Frozen snapshot lag**: Memory changes during a session don't appear in the system prompt until the next session. The agent must rely on tool results for live state.
- **Over-saving**: Trivial or easily re-discovered facts waste capacity. Don't save raw data dumps or session-specific ephemeral paths.
- **Security scanning**: Memory entries are scanned for prompt injection and exfiltration patterns. Invisible Unicode characters are blocked.

## Related Concepts

- [[concepts/hermes-session-storage]]
- [[concepts/hermes-skills-system]]
- [[concepts/hermes-agent-loop]]

## Sources

- `user-guide/features/memory.md`
