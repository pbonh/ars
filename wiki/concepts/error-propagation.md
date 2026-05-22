---
title: "Error Propagation"
type: concept
tags: [concept, zellij, rust, error-handling]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/ERROR_HANDLING.md"]
confidence: high
---

## Definition

Error propagation in Zellij is the practice of passing errors up the call stack via `Result<T>` rather than terminating with `unwrap()`, so that callers can decide whether to recover, log, or abort.

## How It Works

Zellij uses the [[entities/anyhow|anyhow]] crate to wrap arbitrary errors into a single `anyhow::Error` type. Functions return `Result<T>` and callers use the `?` operator to propagate. The `Context` trait adds human-readable messages at each level.

Example pattern:
```rust
fn do_work() -> Result<()> {
    fallible_op().context("failed to do work")?;
    Ok(())
}
```

## Key Parameters

- `Result<T>`: the return type of fallible functions
- `?` operator: automatic early-return on `Err`
- `anyhow::Context`: trait providing `.context()` and `.with_context()`

## When To Use

Apply this pattern whenever:
- A function currently calls `unwrap()` or `expect()`
- The caller may want to handle the error differently
- You need to attach location-specific context to a library error

## Risks & Pitfalls

- Propagating too far without attaching context produces opaque error chains.
- `?` in closures or async blocks can sometimes require explicit type annotations.

## Related Concepts

- [[concepts/error-context]]
- [[concepts/fatal-error-handling]]
- [[concepts/non-fatal-error-handling]]

## Sources

- [Zellij Error Handling](raw/zellij-repo/docs/ERROR_HANDLING.md)