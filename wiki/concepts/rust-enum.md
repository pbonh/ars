---
title: "Rust Enum"
type: concept
tags: [concept, rust, algebraic-data-types, type-system]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Definition

An enum (enumeration) in Rust is a type that can be one of several named variants. Unlike simple C-style enums, each variant can carry associated data of different types, making Rust enums a full *sum type* (algebraic data type).

## How It Works

Variants are namespaced under the enum identifier using `::`:

```rust
enum IpAddr {
    V4(String),
    V6(String),
}
```

Each variant can hold zero, one, or many fields. This eliminates the need for separate structs plus a tag field; the variant itself is the tag.

The standard library defines two ubiquitous enums:

- `Option<T>`: `Some(T)` or `None` — replaces null pointers.
- `Result<T, E>`: `Ok(T)` or `Err(E)` — replaces exception-based error handling.

Methods and traits can be implemented on enums via `impl` blocks, just like structs. The `Option` and `Result` types have extensive method suites (`.map`, `.unwrap_or`, `.and_then`, etc.) that allow fluent manipulation without explicit `match`.

## Key Parameters

- Variant payloads: `V4(String)`, `V4(u8, u8, u8, u8)`, or `V4 { octets: [u8; 4] }`.
- `Option<T>`: `Some(T)` / `None`.
- `Result<T, E>`: `Ok(T)` / `Err(E)`.
- `#[derive(Debug)]` and other derives work on enums.

## When To Use

Use enums when:
- A value can be exactly one of a fixed set of alternatives.
- Different alternatives need to carry different data.
- Modeling state machines, message types, or AST nodes.

## Risks & Pitfalls

- **Exhaustiveness**: The compiler requires every `match` on an enum to handle all variants; this is usually a feature, but adding a new variant can break existing matches.
- **Variant size**: An enum’s size is the size of its largest variant plus a discriminant; large variants can waste memory for other variants.
- **Null-free**: Using `Option` everywhere can feel verbose at first, but it eliminates null-dereference bugs.

## Related Concepts

- [[concepts/rust-pattern-matching]] — the primary way to interact with enums
- [[concepts/rust-struct]] — structs group fields; enums choose alternatives
- [[concepts/rust-error-handling]] — built on `Result` and `Option`
- [[concepts/algebraic-data-types]] — the type-theory foundation

## Sources

- *The Rust Programming Language*, Chapter 6 — Enums and Pattern Matching
