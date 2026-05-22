---
title: "Pi RPC Mode"
type: concept
tags: [concept, pi, rpc, jsonl, headless, integration]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/pi-repo/packages/coding-agent/docs/rpc.md", "raw/pi-repo/packages/coding-agent/docs/json.md"]
confidence: high
---

## Definition

Pi RPC mode is a headless operational mode that exposes the coding agent's capabilities via a JSONL protocol over stdin/stdout. It enables embedding Pi in other applications, IDEs, and custom UIs without the interactive TUI.

## How It Works

1. Start Pi with `pi --mode rpc [options]`.
2. The client sends JSON command objects to stdin, one per line.
3. Pi responds with JSON `response` objects and streams asynchronous `event` objects to stdout.
4. All commands support an optional `id` field for request/response correlation.
5. Framing uses strict JSONL with LF (`\n`) only as the record delimiter.

Commands include: `prompt`, `compact`, `clear`, `get_entries`, `get_context`, `execute_tool`, `set_settings`, `get_settings`, `get_models`, and lifecycle commands.

## Key Parameters

- Entry point: `pi --mode rpc`
- Protocol: JSONL over stdin/stdout
- Delimiter: `\n` only (Node `readline` is non-compliant due to Unicode separator splitting)
- Correlation: optional `id` field on commands

## When To Use

Use RPC mode when:
- You are building an IDE plugin or external UI that needs to drive Pi programmatically.
- You want headless agent execution in CI/CD or automated pipelines.
- You are integrating Pi into a non-terminal environment (web app, desktop app).
- For Node.js/TypeScript integrations, prefer the [[concepts/pi-sdk|SDK]] over spawning a subprocess.

## Risks & Pitfalls

- JSONL parsers must split on `\n` only; generic line readers may corrupt JSON strings containing `U+2028` or `U+2029`.
- Events stream asynchronously; clients must handle out-of-order responses relative to commands.
- Session state is still persisted to disk unless `--no-session` is used.
- Streaming behavior must be specified when prompting during an active stream (`steer`, `queue`, or `cancel`).

## Related Concepts

- [[concepts/pi-sdk]]
- [[concepts/pi-session-format]]
- [[concepts/pi-extension]]

## Sources

- [Pi RPC Mode Documentation](raw/pi-repo/packages/coding-agent/docs/rpc.md)
- [Pi JSON Event Stream Documentation](raw/pi-repo/packages/coding-agent/docs/json.md)
