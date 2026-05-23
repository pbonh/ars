---
title: "First-Class Functions"
type: concept
tags: [concept, functional-programming, type-system, software-design]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Definition

First-class functions are functions that can be treated like any other value: assigned to variables, stored in data structures, passed as arguments to other functions, and returned as results. A language with first-class functions allows function types to appear anywhere value types can.

## How It Works

- **Function types** are declared explicitly (e.g., `(arg: T) => U`), enabling the type checker to verify that a function passed as an argument matches the expected signature.
- **Higher-order functions** take functions as arguments or return them (e.g., `map`, `filter`, `reduce`).
- **Lambdas/anonymous functions** provide lightweight syntax for creating function values inline without a named declaration.
- Because functions are values, they can be composed, partially applied, and stored in collections just like numbers or strings.

## Key Parameters

- **Type inference for functions**: Languages with type inference can often deduce the parameter and return types of lambdas from context, reducing boilerplate.
- **Arity and overloads**: Function types fix the number and types of arguments; overloads or variadic functions require additional type system support.
- **Purity**: A first-class function may capture mutable state; whether it is pure (no side effects) is a separate concern from being first-class.

## When To Use

Use first-class functions when:
- You want to parameterize behavior (strategy pattern, callbacks, comparators).
- You are building data-processing pipelines (map, filter, reduce).
- You need deferred or repeated execution (event handlers, thunks, decorators).

## Risks & Pitfalls

- **Callback hell**: Deeply nested callbacks (before promises/async-await) become hard to read and reason about.
- **Type erasure**: In some languages, generic function types lose information at run time, making certain reflective operations impossible.
- **Scope confusion**: Capturing variables in closures can lead to unexpected shared state if mutability is not carefully controlled.

## Related Concepts

- [[concepts/closure]] — first-class functions that capture their environment
- [[concepts/map-filter-reduce]] — canonical higher-order functions enabled by first-class functions
- [[concepts/strategy-pattern]] — parameterizing behavior via function arguments

## Sources

- *Programming with Types*, Chapter 5 — Function types (section 5.1)
