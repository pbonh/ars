---
title: "TypeScript Generics"
type: concept
tags: [concept, typescript, type-system, polymorphism]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/", "raw/programming-with-types-book/"]
confidence: high
---

## Definition

Generics in TypeScript are type parameters that act as placeholders for concrete types. They allow classes, interfaces, and functions to operate on a range of types while preserving compile-time type safety, rather than falling back to `any` or `unknown`.

## How It Works

A generic is declared with angle brackets (`<T>`) and instantiated with a concrete type argument when used:

```typescript
class DataStore<T> {
    private data: T[] = [];
    add(item: T) { this.data.push(item); }
    getAll(): T[] { return this.data; }
}

let store = new DataStore<number>();
store.add(10); // OK
store.add("x"); // Error
```

Type inference often supplies the type argument automatically from the constructor arguments or function parameters, so explicit type arguments are not always required.

**Generic algorithms and iterators**
Beyond collections, generics enable reusable algorithms that work across data structures. By parameterizing over an iterator type rather than a concrete array or list, a single `map`, `filter`, or `reduce` implementation can operate on arrays, linked lists, binary trees, and streams. Type constraints (`T extends Comparable`) ensure the generic algorithm only accepts types that provide the required operations, turning compile-time contracts into reusable library code.

## Key Parameters

- Type parameters can be constrained with `extends` to require certain properties or methods.
- Multiple type parameters are supported: `<K, V>`.
- Generic interfaces and type aliases can describe reusable shapes without committing to a specific type.

## When To Use

- Use generics for collection classes, utility functions, and APIs that need to work with multiple types while preserving type information.
- Use constraints (`T extends Comparable`) when the generic code relies on members that not all types possess.

## Risks & Pitfalls

- **Over-generalization**: Adding generics where a concrete type or union would suffice increases complexity and error-message verbosity.
- **Variance pitfalls**: TypeScript's structural typing means generic types are compared structurally; developers expecting strict nominal variance may be surprised by assignability rules.
- **Iterator abstraction cost**: Writing fully generic algorithms over iterators requires understanding iterator categories (forward, random-access) and may introduce indirection that direct indexing avoids.

## Related Concepts

- [[concepts/generic-constraints]]
- [[concepts/conditional-types]]
- [[concepts/type-inference]]
- [[concepts/iterator-pattern]] — generic algorithms decouple from concrete data structures via iterators
- [[concepts/map-filter-reduce]] — canonical generic algorithms
- [[concepts/variance]] — governs substitution of generic types based on their parameters

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapters 12, 13
- *Programming with Types*, Chapters 9 and 10 — Generic data structures and Generic algorithms and iterators
