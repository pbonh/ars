---
title: "Custom Error Types"
type: concept
tags: [concept, zellij, rust, error-handling]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/ERROR_HANDLING.md"]
confidence: high
---

## Definition

Custom error types in Zellij are domain-specific error variants defined in `zellij_utils::errors::ZellijError` using the [[entities/thiserror|thiserror]] crate, allowing downstream code to match on specific failures.

## How It Works

1. Define a new variant in `ZellijError` (e.g., `CommandNotFound { terminal_id: u32 }`).
2. Create the error with `anyhow!(ZellijError::CommandNotFound { ... })`.
3. Propagate it through the `anyhow` chain.
4. Recover it downstream with `err.downcast_ref::<ZellijError>()`.

This bridges `thiserror`'s structured variants with `anyhow`'s ergonomic propagation.

## Key Parameters

- `ZellijError` enum in `zellij_utils::errors`
- `thiserror` derive macros for boilerplate reduction
- `anyhow::Error::downcast_ref` for recovery

## When To Use

Create a custom variant when:
- A specific error requires special recovery logic (e.g., "command not found" → show UI message)
- The error carries data that downstream code needs (e.g., `terminal_id`)

## Risks & Pitfalls

- Every new variant is a public API commitment; prefer `anyhow` context for one-off errors.
- `downcast_ref` only works if the error was created with the exact `ZellijError` type, not just wrapped.

## Related Concepts

- [[concepts/error-propagation]]
- [[concepts/panic-handling]]

## Sources

- [Zellij Error Handling](raw/zellij-repo/docs/ERROR_HANDLING.md)