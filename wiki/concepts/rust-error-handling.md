---
title: "Rust Error Handling"
type: concept
tags: [concept, rust, error-handling, reliability]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Definition

Rust groups errors into two categories: *recoverable* errors, modeled with `Result<T, E>`, and *unrecoverable* errors, modeled with `panic!`. There is no exception-throwing mechanism; all error handling is explicit and type-safe.

## How It Works

**Unrecoverable errors**: `panic!` immediately unwinds the stack (or aborts, depending on configuration) and prints an error message. Use `panic!` for bugs, contract violations, or states that should be impossible.

**Recoverable errors**: `Result<T, E>` is an enum with `Ok(T)` for success and `Err(E)` for failure. The standard library offers many methods:
- `.unwrap()` and `.expect(msg)`: return `T` or panic on `Err`.
- `.unwrap_or(default)`: return `T` or a default value.
- `.map`, `.and_then`, `.or_else`: functional combinators for chaining.
- `?` operator: early-return `Err` or unwrap `Ok` in functions returning `Result` or `Option`.

The `?` operator propagates errors concisely:

```rust
fn read_username_from_file() -> Result<String, io::Error> {
    let mut file = File::open("hello.txt")?;
    let mut username = String::new();
    file.read_to_string(&mut username)?;
    Ok(username)
}
```

Custom error types implement `std::error::Error` and `Display`. The `From` trait allows automatic conversion of error types via `?`.

## Key Parameters

- `Result<T, E>`: recoverable operation outcome.
- `Option<T>`: optional value (`Some` / `None`), a subset of error-handling patterns.
- `panic!`: unrecoverable failure.
- `?` operator: ergonomic error propagation.
- `unwrap` / `expect`: convenience with panic-on-failure tradeoff.

## When To Use

- Use `Result` for expected failures (file not found, network timeout).
- Use `panic!` for programmer errors (index out of bounds, assertion failure).
- Use `Option` for values that may be absent.

## Risks & Pitfalls

- **Overusing unwrap**: Libraries should avoid `.unwrap()` on user-provided data; applications may use it for prototyping.
- **Error type explosion**: Every library defining its own error type can make integration noisy; the ecosystem converges on crates like `anyhow` and `thiserror`.
- **Panic in async**: Panics in async contexts may be caught by the runtime or task, but behavior depends on the executor.

## Related Concepts

- [[concepts/rust-enum]] — `Result` and `Option` are enums
- [[concepts/rust-pattern-matching]] — matching `Result`/`Option` is idiomatic
- [[concepts/panic-handling]] — custom panic hooks and behavior
- [[concepts/error-propagation]] — patterns for passing errors upward

## Sources

- *The Rust Programming Language*, Chapter 9 — Error Handling
