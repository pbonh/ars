---
title: "Rust Lifetimes"
type: concept
tags: [concept, rust, memory-management, type-system]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Definition

A lifetime is the scope for which a reference is valid. Lifetimes are another kind of generic parameter; rather than ensuring a type has certain behavior, they ensure that references do not outlive the data they point to.

## How It Works

Every reference in Rust has a lifetime, but in most cases the compiler infers them automatically (lifetime elision). Explicit lifetime annotations are required when the compiler cannot determine the relationship between multiple references.

Lifetime annotations use apostrophes: `&'a str` means a string slice that lives at least as long as lifetime `'a`.

The borrow checker compares scopes to determine whether all borrows are valid. If a reference could outlive its referent, compilation fails with an error like "borrowed value does not live long enough."

Common lifetime elision rules (applied automatically to function signatures):
1. Each parameter that is a reference gets its own lifetime parameter.
2. If there is exactly one input lifetime, it is assigned to all output lifetimes.
3. If there are multiple input lifetimes but one is `&self` or `&mut self`, the lifetime of `self` is assigned to all output lifetimes.

The special `'static` lifetime denotes data that lives for the entire program duration (e.g., string literals).

## Key Parameters

- `'a`, `'b`, etc.: named lifetime parameters.
- `&'a T`: reference valid for at least `'a`.
- `'static`: lifetime of the entire program.
- Lifetime bounds: `'a: 'b` means `'a` outlives `'b`.
- Structs with references: `struct Foo<'a> { part: &'a str }`.

## When To Use

You need explicit lifetimes when:
- A function returns a reference and the compiler cannot infer which input lifetime it relates to.
- A struct holds a reference; the struct must carry the lifetime parameter.
- Writing complex generic APIs with multiple references.

## Risks & Pitfalls

- **Dangling references**: The borrow checker rejects code where a reference outlives its data; this is usually correct but can frustrate beginners.
- **Lifetime proliferation**: Structs with many references accumulate many lifetime parameters, complicating signatures.
- **Self-referential structs**: Rust cannot express safe self-referential structs without indirection (e.g., indices, `Pin`).

## Related Concepts

- [[concepts/rust-borrowing]] — lifetimes formalize reference validity
- [[concepts/rust-ownership]] — lifetimes track how long borrowed data stays alive
- [[concepts/rust-generics]] — lifetime parameters are a kind of generic

## Sources

- *The Rust Programming Language*, Chapter 10.3 — Validating References with Lifetimes
