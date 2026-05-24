---
title: "Closure"
type: concept
tags: [concept, functional-programming, type-system, scope]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/", "raw/rust-book-book/"]
confidence: high
---

## Definition

A closure is a function bundled together with the lexical environment in which it was created. The closure "captures" variables from its enclosing scope, allowing the function to access and modify those variables even after the outer function has returned.

## How It Works

- When a lambda or nested function references a variable from an outer scope, the language runtime stores a reference to that variable inside the closure.
- The captured variable outlives the function invocation that created it, enabling stateful behavior without objects or global variables.
- In type systems that support first-class functions, a closure has the same function type as a pure function; the captured state is an implementation detail hidden from the type signature.
- In Rust, closures are anonymous functions that capture their environment. The compiler infers parameter and return types when not annotated. Rust closures implement one of three traits depending on how they capture variables: `Fn` (by immutable reference), `FnMut` (by mutable reference), or `FnOnce` (by value). A `move` closure forces all captures to be by value, transferring ownership into the closure.

## Key Parameters

- **Capture by reference vs. by value**: Some languages capture by reference (sharing mutable state), others capture by value (copying at closure creation time).
- **Mutable captures**: If the captured variable is mutable, the closure can modify it, effectively creating shared state across multiple invocations.
- **Garbage collection**: Captured variables are kept alive as long as any closure referencing them is alive.
- **Rust capture semantics**: Rust closures are structs under the hood; the compiler chooses the least restrictive capture mode possible. `move` closures are required when passing a closure to a new thread or when the original scope will end before the closure is called.

## When To Use

Use closures when:
- You need to maintain state between calls without introducing a class or global variable (e.g., a counter, a singleton decorator).
- You want to create factory functions that pre-configure behavior with some fixed arguments.
- You are implementing callbacks that need access to context from the calling scope.

## Risks & Pitfalls

- **Unexpected mutation**: Multiple closures capturing the same mutable variable can interfere with each other in surprising ways.
- **Memory leaks**: Long-lived closures holding large captured objects can prevent garbage collection.
- **Loop capture bugs**: Capturing a loop variable by reference in a language that does not create a new binding per iteration causes all closures to see the final value.
- **Trait bound confusion**: In Rust, generic functions that accept closures must declare the correct `Fn*` trait bound. `Fn` is the most common and most restrictive; choosing `FnMut` or `FnOnce` only when mutation or single-call semantics are required prevents unnecessary constraints.

## Related Concepts

- [[concepts/first-class-functions]] — closures require the language to treat functions as values
- [[concepts/lazy-evaluation]] — thunks and deferred computations are often implemented as closures
- [[concepts/encapsulation]] — closures encapsulate state with behavior, similar to objects
- [[concepts/rust-closure]] — Rust-specific closure mechanics and trait bounds

## Sources

- *Programming with Types*, Chapter 6 — Advanced applications of function types (section 6.1)
