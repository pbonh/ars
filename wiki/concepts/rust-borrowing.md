---
title: "Rust Borrowing"
type: concept
tags: [concept, rust, memory-management, references]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Definition

Borrowing is the mechanism by which Rust code accesses a value via a reference without taking ownership of it. References are guaranteed to point to valid data for a specific lifetime, enforced by the borrow checker.

## How It Works

A reference is created with `&` and has type `&T` for an immutable reference or `&mut T` for a mutable reference.

The borrowing rules (enforced at compile time) are:

1. At any given time, you can have **either** one mutable reference **or** any number of immutable references.
2. References must always be valid (no dangling references allowed).

Because a borrowed value is not dropped when the reference goes out of scope, the original owner can continue using it after the borrow ends. Mutable references allow in-place modification without transferring ownership.

## Key Parameters

- `&T`: immutable reference; read-only, can coexist with other immutable references.
- `&mut T`: mutable reference; exclusive, allows mutation, cannot coexist with any other reference.
- Dereference operator `*`: accesses the value behind a reference.
- Lifetime elision: the compiler infers lifetimes in common patterns so annotations are not always required.

## When To Use

Borrow whenever you want to:
- Pass a large value to a function without copying or moving it.
- Read data from multiple places simultaneously.
- Mutate data in place without the caller giving up ownership.

## Risks & Pitfalls

- **Data races prevented**: The exclusive-mutable-or-multiple-immutable rule eliminates data races at compile time.
- **Dangling references**: Returning a reference to a local variable will not compile.
- **Overlapping mutable borrows**: Splitting a collection into mutable slices is safe, but two mutable references to the same element are not.

## Related Concepts

- [[concepts/rust-ownership]] — the foundation that makes borrowing safe
- [[concepts/rust-lifetimes]] — formalizes how long a borrow remains valid
- [[concepts/rust-slice-type]] — a kind of reference to a contiguous sequence

## Sources

- *The Rust Programming Language*, Chapter 4.2 — References and Borrowing
