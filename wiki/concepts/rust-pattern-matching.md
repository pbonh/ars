---
title: "Rust Pattern Matching"
type: concept
tags: [concept, rust, control-flow, algebraic-data-types]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Definition

Pattern matching is the primary control-flow mechanism for deconstructing values in Rust. The `match` expression compares a value against a series of *patterns* and executes the code associated with the first matching pattern. The compiler confirms that all possible cases are handled.

## How It Works

A `match` expression has *arms*, each consisting of a pattern and an expression separated by `=>`:

```rust
match coin {
    Coin::Penny => 1,
    Coin::Nickel => 5,
    Coin::Dime => 10,
    Coin::Quarter => 25,
}
```

Patterns can be:
- Literal values
- Named enum variants (with or without nested destructuring)
- Variables that bind to parts of the matched value
- Wildcards `_` that match anything
- Ranges, multiple patterns (`|`), and more (see Chapter 18)

`if let` provides a concise alternative when only one pattern matters:

```rust
if let Some(3) = some_value {
    println!("three");
}
```

`while let` loops as long as a pattern continues to match. `let` itself is a form of pattern binding (e.g., `let (x, y) = point;`).

Refutability is the property of whether a pattern can fail to match. `let x = 5;` uses an *irrefutable* pattern (always matches). `if let Some(x) = option` uses a *refutable* pattern (might not match).

## Key Parameters

- Exhaustiveness: `match` must cover every variant; missing arms are compile-time errors.
- Pattern bindings: `Coin::Quarter(state)` binds `state` to the inner data.
- `@` bindings: `id @ 3..=7` binds the matched value to `id` while also matching a range.
- `..` rest patterns: ignore remaining fields in a struct or variant.

## When To Use

Use pattern matching when:
- Working with enums (`Option`, `Result`, custom enums).
- Destructuring tuples, structs, or slices.
- Replacing deeply nested `if/else` chains with explicit, exhaustive branches.

## Risks & Pitfalls

- **Non-exhaustive match**: Adding a new enum variant breaks all non-wildcard `match` expressions; this is by design (compile-time safety).
- **Variable shadowing**: A pattern-binding variable can shadow an outer variable with the same name.
- **Match arm comma**: Trailing commas are optional, but omitting commas between arms is a syntax error.

## Related Concepts

- [[concepts/rust-enum]] — the primary type matched against
- [[concepts/rust-struct]] — fields can be destructured in patterns
- [[concepts/rust-closure]] — closures are often used inside match arms

## Sources

- *The Rust Programming Language*, Chapter 6.2 — The match Control Flow Construct
- *The Rust Programming Language*, Chapter 18 — Patterns and Matching
