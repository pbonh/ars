---
title: "Immutability"
type: concept
tags: [concept, functional-programming, type-system, software-design]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Definition

Immutability is the property of a data structure or variable whose value cannot be modified after creation. In a type system, immutability is often enforced via read-only types, `const` declarations, or persistent data structures that return new copies on change rather than mutating in place.

## How It Works

- A type checker can mark variables, fields, or collections as read-only, rejecting any code that attempts to mutate them.
- Immutable collections (e.g., persistent vectors, maps) use structural sharing to make copy-on-write efficient, so immutability does not necessarily mean poor performance.
- Functions that operate on immutable data are naturally referentially transparent: the same inputs always yield the same outputs, with no hidden side effects.
- Immutability pairs well with first-class functions and closures because shared state cannot be accidentally modified by a callback or concurrent thread.

## Key Parameters

- **Shallow vs. deep**: A shallow immutable reference prevents reassignment but does not protect the contents of a referenced mutable object. Deep immutability requires recursive read-only constraints.
- **Language support**: Some languages default to immutability (Haskell, Rust by default for bindings); others require explicit opt-in (TypeScript `readonly`, C# `readonly`, Java `final`).
- **Performance cost**: Naïve copy-on-write can be expensive; persistent data structures mitigate this with structural sharing and tree-based representations.

## When To Use

Use immutability when:
- You want to prevent a whole class of bugs caused by unexpected mutation (aliasing bugs, stale state, race conditions).
- You need to reason about code locally, without tracing every possible mutation path.
- You are building concurrent or distributed systems where shared mutable state is a primary source of complexity.

## Risks & Pitfalls

- **Performance misconceptions**: Developers sometimes avoid immutability assuming it is always slow. Modern persistent collections and compiler optimizations often make the cost negligible.
- **Interoperability**: Integrating immutable code with libraries that require mutation (e.g., DOM APIs, graphics buffers) requires deliberate boundary handling.
- **Partial adoption**: A codebase that is half-immutable and half-mutable is often harder to reason about than one that commits to either extreme.

## Related Concepts

- [[concepts/encapsulation]] — immutability is a strong form of encapsulation that prevents internal change
- [[concepts/closure]] — closures capturing mutable state undermine immutability guarantees
- [[concepts/composability]] — immutable data composes more reliably because pieces cannot interfere with each other

## Sources

- *Programming with Types*, Chapter 1 — Introduction to typing (section 1.3)
