---
title: "Hermes Session Storage"
type: concept
tags: [concept, ai-agent, sqlite, fts5, persistence]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-agent-docs/website/docs"]
confidence: high
---

## Definition

Hermes Session Storage is a SQLite-based persistence layer for conversation history, state, and full-text search. It uses FTS5 for fast cross-session recall, supports session lineage tracking (parent/child across compressions), per-platform isolation, and atomic writes with contention handling.

## How It Works

### Database Schema

The session store (`~/.hermes/state.db`) persists:
- Messages per session (OpenAI-format role/content/tool_calls).
- Session metadata (platform, chat_id, timestamps).
- Session lineage (parent → child relationships created during compression).
- FTS5 full-text index over all message content.

### Session Key Format

```
agent:main:{platform}:{chat_type}:{chat_id}
```

Example: `agent:main:telegram:private:123456789`. Thread-aware platforms append thread IDs.

### Persistence Lifecycle

After each agent turn:
- Messages saved to session store.
- Memory changes flushed to `MEMORY.md` / `USER.md`.
- Session can be resumed later via `/resume` or `hermes chat --resume`.

### FTS5 Search

All CLI and messaging sessions are indexed. The `session_search` tool returns actual messages from the DB in ~20ms — no LLM summarization, no truncation. Three calling shapes:
- **Discovery**: pass `query` to find sessions.
- **Scroll**: pass `session_id` + `around_message_id` to browse within a session.
- **Browse**: no args to list recent sessions.

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| Atomic writes | Prevents partially written state on crashes |
| Contention handling | Multiple writers (gateway + CLI) coordinate via SQLite locking |
| Session expiry | Abandoned sessions cleaned up after timeout |

## When To Use

- **Resume long conversations**: Pick up where you left off after restart.
- **Cross-session recall**: "What did we decide about X last Tuesday?" — answered via FTS5 without LLM cost.
- **Audit**: Review past agent behavior, tool calls, and outputs.

## Risks & Pitfalls

- **Schema instability**: `~/.hermes/state.db` is an internal schema that changes between releases. Do not query it directly from external scripts — use `session_search` or the CLI surface.
- **Compression lineage gaps**: After compression, early conversation turns are summarized. The raw messages are still in the DB, but the active session only sees the summary.
- **Platform isolation edge cases**: Sessions from gateway and CLI for the same chat may diverge if both are active simultaneously.

## Related Concepts

- [[concepts/hermes-persistent-memory]]
- [[concepts/hermes-context-compression]]
- [[concepts/hermes-gateway]]

## Sources

- `developer-guide/session-storage.md`
- `developer-guide/gateway-internals.md`
