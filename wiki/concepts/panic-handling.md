---
title: "Panic Handling"
type: concept
tags: [concept, zellij, rust, error-handling]
created: 2026-05-21
updated: 2026-05-23
sources: ["raw/zellij-repo/docs/ERROR_HANDLING.md", "raw/rust-book-book/"]
confidence: high
---

## Definition

Panic handling is the discipline for managing unrecoverable errors in Rust. In the broader language, `panic!` immediately unwinds the stack (or aborts, depending on configuration) when a program enters an unrecoverable state. In Zellij, panic handling specifically refers to catching and formatting unexpected crashes using the [[entities/miette|miette]] crate, producing user-friendly diagnostic output instead of raw stack traces.

## How It Works

In general Rust, panics are triggered by bugs or contract violations (e.g., index out of bounds, failed assertions, or explicit `panic!` calls). By default, the standard library prints a message and unwinds the stack, calling destructors for local variables. Programs can register a custom panic hook to change this behavior (e.g., logging to a file or showing a dialog).

In Zellij specifically, the application registers a custom panic hook via `handle_panic`. When a thread panics:
1. The `Panic` error type wraps the panic payload.
2. `miette` renders a styled, contextual diagnostic message.
3. The session terminates (since panics are considered unrecoverable).

## Key Parameters

- `panic!`: macro for unrecoverable failures in Rust.
- Panic hook: global callback registered via `std::panic::set_hook`.
- `Panic` error type in `zellij_utils::errors`
- `handle_panic` function as the panic hook
- `miette` for fancy formatting

## When To Use

Relevant when:
- Writing Rust code that must abort on invariant violations (`assert!`, `unreachable!`).
- Deciding between `panic!` and `Result` for a given failure mode.
- Investigating why Zellij crashed unexpectedly.
- Adding custom panic hooks for plugins or child processes.

## Risks & Pitfalls

- Panics should be the last resort; prefer `Result`-based propagation for expected failures.
- In long-running sessions, even a single panic is catastrophic because it kills the server thread.

## Related Concepts

- [[concepts/fatal-error-handling]]
- [[concepts/custom-error-types]]
- [[concepts/rust-error-handling]]
- [[concepts/rust-ownership]]

## Sources

- [Zellij Error Handling](raw/zellij-repo/docs/ERROR_HANDLING.md)