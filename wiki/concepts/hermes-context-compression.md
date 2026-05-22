---
title: "Hermes Context Compression"
type: concept
tags: [concept, ai-agent, context-window, prompt-caching, compression]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-agent-docs/website/docs"]
confidence: high
---

## Definition

Hermes Context Compression is the subsystem that keeps conversations within model context windows by summarizing middle conversation turns, applying Anthropic prompt caching breakpoints, and tracking token budgets. It prevents context-overflow errors while preserving recent message integrity.

## How It Works

### Compression Triggers

- **Preflight** (before API call): If conversation exceeds 50% of model's context window.
- **Gateway auto-compression**: If conversation exceeds 85% (more aggressive, runs between turns).

### Compression Process

1. **Memory is flushed to disk first** — prevents data loss.
2. **Middle conversation turns are summarized** into a compact summary by the default `context_compressor.py` engine (lossy summarization).
3. **Last N messages preserved intact** (`compression.protect_last_n`, default: 20).
4. **Tool call/result pairs kept together** — never split across the summary boundary.
5. **New session lineage ID generated** — compression creates a "child" session for tracking.

### Prompt Caching

For Anthropic models, `prompt_caching.py` applies cache breakpoints to enable prefix caching:
- System prompt cached as a stable prefix.
- No cache-breaking mutations mid-conversation except explicit user actions (`/model`).

### Context Engine Plugin

The context engine is pluggable via `agent/context_engine.py`. The default implementation is `context_compressor.py` (lossy summarization). Users can install custom context engines as plugins under `plugins/context_engine/`.

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `compression.protect_last_n` | 20 | Messages preserved intact during compression |
| `compression.threshold` | 50% | Preflight compression trigger (% of context window) |
| `gateway.compression_threshold` | 85% | Gateway auto-compression trigger |

## When To Use

- **Long conversations**: Multi-hour sessions with dozens of tool calls will inevitably hit context limits.
- **Large codebases**: Refactoring tasks that read many files need compression to keep tool schemas and recent context visible.
- **Cost-sensitive runs**: Compression reduces token usage by collapsing early conversation history.

## Risks & Pitfalls

- **Lossy summarization**: Middle turns lose detail. Critical instructions given early may be summarized away. Repeat important constraints in the protected last N messages if needed.
- **Cache invalidation**: Changing the system prompt mid-conversation breaks Anthropic prefix cache. Hermes avoids this by freezing the system prompt snapshot.
- **Gateway vs CLI divergence**: Gateway uses 85% threshold; CLI uses 50%. Long gateway conversations may compress more aggressively than expected.
- **Tool pair splitting**: Although tool call/result pairs are kept together, if a pair straddles the protect_last_n boundary, the older portion may be summarized, losing intermediate reasoning.

## Related Concepts

- [[concepts/hermes-agent-loop]]
- [[concepts/hermes-session-storage]]
- [[concepts/hermes-persistent-memory]]

## Sources

- `developer-guide/context-compression-and-caching.md`
- `developer-guide/architecture.md`
