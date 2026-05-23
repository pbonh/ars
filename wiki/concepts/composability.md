---
title: "Composability"
type: concept
tags: [concept, software-design, functional-programming, type-system]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Definition

Composability is the degree to which software components can be combined to build larger systems without modifying the components themselves. Strong type systems enhance composability by ensuring that the interfaces of components are explicit, predictable, and mechanically checked.

## How It Works

- **Explicit contracts**: Type signatures act as machine-checked contracts. A function with type `(T) => U` can be composed with a function `(U) => V` to yield a function `(T) => V`, and the type checker verifies the connection.
- **Algebraic composition**: Product types compose as AND (both pieces must be present); sum types compose as OR (one of several alternatives). Function types compose via substitution and higher-order functions.
- **Purity and immutability**: Pure functions and immutable data make composition order-independent and free from hidden interactions.
- **Generic abstractions**: Generic types and higher-order functions (map, bind) provide uniform composition mechanisms across many concrete types.

## Key Parameters

- **Interface stability**: Composability degrades when interfaces change frequently. Versioned, typed APIs help maintain stable contracts.
- **Granularity**: Very fine-grained components may compose flexibly but create boilerplate; very coarse components may not fit together without adaptation.
- **Effect encapsulation**: Components with uncontrolled side effects (global state, I/O) compose unpredictably. Encapsulating effects in monads or explicit contexts restores composability.

## When To Use

Design for composability when:
- You are building libraries, frameworks, or platforms intended for reuse.
- You expect requirements to change and want to swap algorithms, data sources, or UI layers without rewrites.
- You are constructing data-processing pipelines, UI component trees, or service architectures.

## Risks & Pitfalls

- **Over-abstraction**: Premature genericization can produce interfaces so abstract that they obscure intent.
- **Leaky abstractions**: A component that exposes internal state or depends on global context cannot be composed in new environments.
- **Composition overhead**: Deeply nested generic wrappers (e.g., `Promise<Optional<Result<T, E>>>`) can make types noisy. Use type aliases and clear naming to manage this.

## Related Concepts

- [[concepts/algebraic-data-types]] — the fundamental building blocks for typed composition
- [[concepts/first-class-functions]] — higher-order functions are the primary mechanism for composing behavior
- [[concepts/encapsulation]] — encapsulation hides internals so only the stable interface participates in composition
- [[concepts/lazy-evaluation]] — lazy components compose without executing until needed

## Sources

- *Programming with Types*, Chapter 1 — Introduction to typing (section 1.3)
