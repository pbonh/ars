---
title: "Panic Handling"
type: concept
tags: [concept, zellij, rust, error-handling]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/ERROR_HANDLING.md"]
confidence: high
---

## Definition

Panic handling in Zellij is the mechanism for catching and formatting unexpected crashes using the [[entities/miette|miette]] crate, producing user-friendly diagnostic output instead of raw stack traces.

## How It Works

Zellij registers a custom panic hook via `handle_panic`. When a thread panics:
1. The `Panic` error type wraps the panic payload.
2. `miette` renders a styled, contextual diagnostic message.
3. The session terminates (since panics are considered unrecoverable).

## Key Parameters

- `Panic` error type in `zellij_utils::errors`
- `handle_panic` function as the panic hook
- `miette` for fancy formatting

## When To Use

Relevant when:
- Investigating why Zellij crashed unexpectedly
- Adding custom panic hooks for plugins or child processes

## Risks & Pitfalls

- Panics should be the last resort; prefer `Result`-based propagation for expected failures.
- In long-running sessions, even a single panic is catastrophic because it kills the server thread.

## Related Concepts

- [[concepts/fatal-error-handling]]
- [[concepts/custom-error-types]]

## Sources

- [Zellij Error Handling](raw/zellij-repo/docs/ERROR_HANDLING.md)