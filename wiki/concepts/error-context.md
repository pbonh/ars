---
title: "Error Context"
type: concept
tags: [concept, zellij, rust, error-handling]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/ERROR_HANDLING.md"]
confidence: high
---

## Definition

Error context is the human-readable description of what the program was trying to do when an error occurred, attached to the error chain via the `anyhow::Context` trait.

## How It Works

`anyhow` provides two methods:
- `.context("static message")` — for fixed strings
- `.with_context(|| format!("dynamic: {}", value))` — for formatted strings

The rule of thumb: describe what the current function was attempting, not what the underlying library error says. For example, use `"failed to render screen"` rather than `"failed to send message to server"`.

## Key Parameters

- Context message: what the caller was trying to achieve
- Library error: what the underlying operation reported

## When To Use

Add context before every `?` when:
- The underlying error message is generic (e.g., "NotFound")
- Multiple code paths call the same low-level function
- The error will eventually be shown to a user or logged

## Risks & Pitfalls

- Repeating the library error text adds noise, not value.
- Overly verbose context strings bloat log output.

## Related Concepts

- [[concepts/error-propagation]]
- [[concepts/panic-handling]]

## Sources

- [Zellij Error Handling](raw/zellij-repo/docs/ERROR_HANDLING.md)