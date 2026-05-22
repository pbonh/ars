---
title: "Fatal Error Handling"
type: concept
tags: [concept, zellij, rust, error-handling]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/ERROR_HANDLING.md"]
confidence: high
---

## Definition

Fatal error handling is the pattern of logging the full error chain and then terminating the application, used when recovery is impossible or the program state is corrupted.

## How It Works

Zellij provides a `.fatal()` method on `Result` types. When called on an `Err`:
1. The error chain (including all context messages) is logged.
2. The thread panics, crashing the application.

Typical usage is at thread-root boundaries where `Result` can no longer be propagated (e.g., `screen_thread_main(...).fatal()`).

## Key Parameters

- `.fatal()`: terminates execution after logging
- Use only at the top of spawned threads or main entry points

## When To Use

Use fatal handling when:
- An internal invariant is violated and continuing would risk data loss
- The error occurs in a spawned thread with no parent to receive the `Result`
- All reasonable recovery attempts have failed

## Risks & Pitfalls

- Crashing a terminal multiplexer loses the user's session state.
- Prefer recovery or `non_fatal()` logging when the error is transient.

## Related Concepts

- [[concepts/non-fatal-error-handling]]
- [[concepts/error-propagation]]
- [[concepts/panic-handling]]

## Sources

- [Zellij Error Handling](raw/zellij-repo/docs/ERROR_HANDLING.md)