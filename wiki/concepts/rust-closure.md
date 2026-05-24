---
title: "Rust Closure"
type: concept
tags: [concept, rust, functional-programming, first-class-functions]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Definition

A closure in Rust is an anonymous function that can capture values from the environment in which it is defined. Closures are first-class values: they can be stored in variables, passed as arguments, and returned from functions.

## How It Works

Closure syntax uses vertical bars for parameters:

```rust
let expensive_closure = |num| {
    println!("calculating slowly...");
    num
};
```

Rust infers parameter and return types from usage when they are not annotated.

Closures capture their environment in one of three ways, which map to three traits:

1. `Fn`: captures by immutable reference (`&T`) — the closure can be called multiple times without mutating captures.
2. `FnMut`: captures by mutable reference (`&mut T`) — the closure can mutate its captures and must be called mutably.
3. `FnOnce`: captures by value (moves ownership into the closure) — the closure can only be called once because it consumes its captures.

The compiler automatically implements the most permissive trait possible. `move` closures force all captures to be by value: `let c = move || ...;`.

Closures are used extensively in iterator adaptors (`map`, `filter`, `fold`) and in APIs like `thread::spawn` and `unwrap_or_else`.

## Key Parameters

- `||`: parameter list (empty, single, or multiple).
- `move` keyword: forces ownership capture.
- `Fn`, `FnMut`, `FnOnce`: trait bounds describing capture semantics.
- Type inference: parameter and return types are usually inferred.

## When To Use

Use closures when:
- You need a short, throwaway function (e.g., a comparator, a callback).
- You want to capture local state without explicit struct fields.
- Working with iterator chains or higher-order functions.

## Risks & Pitfalls

- **Move closures and lifetimes**: A `move` closure may try to move a reference out of scope; the borrow checker catches this.
- **Closure size**: Closures are structs under the hood; large captures increase closure size.
- **Trait bound confusion**: `Fn` is the most restrictive but most common bound; choose `FnMut` or `FnOnce` only when mutation or single call is required.

## Related Concepts

- [[concepts/closure]] — the general concept across languages
- [[concepts/rust-iterator]] — closures power iterator adaptors
- [[concepts/rust-traits]] — `Fn*` are traits
- [[concepts/rust-ownership]] — `move` closures transfer ownership

## Sources

- *The Rust Programming Language*, Chapter 13.1 — Closures: Anonymous Functions that Capture Their Environment
