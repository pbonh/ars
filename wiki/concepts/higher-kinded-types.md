---
title: "Higher-Kinded Types"
type: concept
tags: [concept, type-system, functional-programming, generics]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Definition

Higher-kinded types (HKTs) are type constructors that take other type constructors as arguments. Just as higher-order functions take functions as arguments, higher-kinded types abstract over generic types themselves (e.g., `List`, `Optional`, `Promise`) rather than over the values they contain.

## How It Works

- A **kind** is the type of a type. `number` has kind `*` (a concrete type). `Array<T>` has kind `* -> *` (a type constructor that takes a concrete type and produces a concrete type).
- A **higher-kinded type** has a kind like `(* -> *) -> *`: it takes a type constructor (e.g., `Array`) and produces a concrete type.
- HKTs enable defining interfaces such as `Functor<F>` or `Monad<M>` where `F` and `M` are generic type constructors, not concrete types. This allows writing generic code that works for any functor or monad without knowing which one.
- Most mainstream languages (TypeScript, Java, C#, C++, Rust) lack direct HKT support. Developers use patterns, code generation, or language extensions to approximate the abstraction.

## Key Parameters

- **Type constructor as argument**: The critical distinction is passing `Array` (the constructor) rather than `Array<number>` (the constructed type).
- **Simulation techniques**: In languages without HKTs, developers use lightweight higher-rank polymorphism, type classes, traits with associated types, or simply document the pattern and rely on convention.
- **Expressiveness trade-off**: Adding HKTs increases type system complexity and error-message opacity, which is why many language designers have been cautious about including them.

## When To Use

You need higher-kinded types when:
- You want to write generic libraries that abstract over `map`, `bind`, `traverse`, etc., for any container or effect type.
- You are implementing advanced functional patterns (free monads, finally-tagless embeddings, lens libraries) that require generic type constructors.
- You are working in a language that supports HKTs (Haskell, Scala, Idris, PureScript) and want to maximize code reuse.

## Risks & Pitfalls

- **Type system ceiling**: In languages without HKTs, you cannot enforce functor/monad laws at the type level; you must rely on documentation and testing.
- **Complexity**: HKTs introduce an additional layer of abstraction that can make types harder to read and errors harder to debug.
- **Partial support**: Some languages provide features that look like HKTs but have restrictions (e.g., Java’s wildcards, Rust’s higher-ranked trait bounds) that may not cover all use cases.

## Related Concepts

- [[concepts/functor]] — the canonical example of an abstraction that requires HKTs to express generically
- [[concepts/monad]] — another abstraction that needs HKTs for a fully generic definition
- [[concepts/typescript-generics]] — TypeScript generics are first-order (no HKTs)

## Sources

- *Programming with Types*, Chapter 11 — Higher kinded types and beyond (section 11.1)
