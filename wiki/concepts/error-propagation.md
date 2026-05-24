---
title: "Error Propagation"
type: concept
tags: [concept, zellij, rust, error-handling]
created: 2026-05-21
updated: 2026-05-23
sources: ["raw/zellij-repo/docs/ERROR_HANDLING.md", "raw/rust-book-book/"]
confidence: high
---

## Definition

Error propagation is the practice of passing recoverable failures up the call stack via `Result<T, E>` rather than terminating with `unwrap()`. In Rust, this is an idiomatic, type-safe alternative to exceptions. Zellij applies this pattern using the [[entities/anyhow|anyhow]] crate to wrap arbitrary errors into a single `anyhow::Error` type, so that callers can decide whether to recover, log, or abort.

## How It Works

In general Rust, functions return `Result<T, E>` and callers use the `?` operator to propagate errors concisely. The `?` returns early on `Err` or unwraps the `Ok` value. The `From` trait enables automatic conversion between error types, so a function can declare a single error type while internal calls produce diverse errors.

Zellij uses the [[entities/anyhow|anyhow]] crate to wrap arbitrary errors into a single `anyhow::Error` type. Functions return `Result<T>` and callers use `?` to propagate. The `Context` trait adds human-readable messages at each level.

Example pattern in Zellij:
```rust
fn do_work() -> Result<()> {
    fallible_op().context("failed to do work")?;
    Ok(())
}
```

General Rust pattern:
```rust
fn read_username_from_file() -> Result<String, io::Error> {
    let mut file = File::open("hello.txt")?;
    let mut username = String::new();
    file.read_to_string(&mut username)?;
    Ok(username)
}
```

## Key Parameters

- `Result<T, E>`: the return type of fallible functions.
- `?` operator: automatic early-return on `Err` or unwrap on `Ok`.
- `From` trait: enables `?` to convert error types automatically.
- `anyhow::Context`: trait providing `.context()` and `.with_context()` (Zellij-specific convenience).

## When To Use

Apply this pattern whenever:
- A function currently calls `unwrap()` or `expect()` on operations that can legitimately fail.
- The caller may want to handle the error differently (e.g., retry, fallback, or log).
- You need to attach location-specific context to a library error.
- Writing library code where consumers should decide failure handling.

## Risks & Pitfalls

- Propagating too far without attaching context produces opaque error chains.
- `?` in closures or async blocks can sometimes require explicit type annotations.

## Related Concepts

- [[concepts/error-context]]
- [[concepts/fatal-error-handling]]
- [[concepts/non-fatal-error-handling]]
- [[concepts/rust-error-handling]]
- [[concepts/rust-enum]]

## Sources

- [Zellij Error Handling](raw/zellij-repo/docs/ERROR_HANDLING.md)