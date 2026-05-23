---
title: "Functor"
type: concept
tags: [concept, type-system, functional-programming, category-theory]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Definition

A functor is a generic type `H<T>` together with a `map` operation that applies a function `T -> U` to the value(s) inside `H<T>` and returns an `H<U>`, preserving the structure of the container. Arrays, optional types, promises, and many other generic types are functors.

## How It Works

- For any functor `H`, `map` has the signature: `(H<T>, (T -> U)) -> H<U>`.
- The `map` operation does not alter the shape or context of `H`; it only transforms the contained values. For example, mapping over an array keeps the array length the same but changes the element type.
- Two laws govern functors:
  1. **Identity**: `map(identity, H<T>) == H<T>` (mapping the identity function does nothing).
  2. **Composition**: `map(f . g, H<T>) == map(f, map(g, H<T>))` (mapping a composed function is the same as mapping twice).
- Functors allow uniform handling of many generic types: instead of learning separate APIs for arrays, options, and results, you learn `map` once.

## Key Parameters

- **Context preservation**: A functor preserves the computational context (emptiness, asynchrony, error state) while transforming the success value.
- **Higher-kinded types**: To express a functor as an interface generic over `H<T>`, a language needs higher-kinded type support (e.g., Haskell, Idris). Most mainstream languages (TypeScript, Java, C#) cannot express this abstraction directly in the type system.
- **Pattern vs. formal type**: In languages without higher-kinded types, "functor" is used as a design pattern rather than a compiler-checked contract.

## When To Use

Think in terms of functors when:
- You want to apply a pure transformation inside a generic container without unwrapping it.
- You are building generic pipelines (e.g., `optional.map(f).map(g)`) and want consistent semantics.
- You are moving toward monadic patterns, because every monad is also a functor.

## Risks & Pitfalls

- **Breaking the laws**: A hand-rolled `map` that drops elements, reorders them, or changes the context violates functor laws and composes unpredictably.
- **Over-abstraction**: Introducing functor terminology in a codebase that does not use functional patterns can confuse teammates.
- **Type system limits**: Without higher-kinded types, you cannot write a single generic `mapAll` that accepts any functor, leading to duplicated boilerplate.

## Related Concepts

- [[concepts/monad]] — a monad is a functor with additional `bind`/`flatMap` capability
- [[concepts/higher-kinded-types]] — the missing type-system feature needed to abstract over functors
- [[concepts/map-filter-reduce]] — `map` is the functor operation

## Sources

- *Programming with Types*, Chapter 11 — Higher kinded types and beyond (section 11.1)
