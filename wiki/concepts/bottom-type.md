---
title: "Bottom Type"
type: concept
tags: [concept, type-system, functional-programming, control-flow]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Definition

The bottom type is a type that has no values. It represents unreachable code, impossible states, or functions that never return (e.g., because they throw an exception or enter an infinite loop). In TypeScript it is `never`; in other languages it may be called `Nothing`, `Void` (in some functional languages), or `⊥` (bottom).

## How It Works

- A function with return type `never` promises it will not return normally. It might throw, loop forever, or terminate the process.
- The bottom type is the identity for sum types: `T + ⊥ = T` (adding zero alternatives does not change the type).
- Because there are no values of the bottom type, a variable of type `never` can be assigned to any variable of any type without risk—there is no value to go wrong. This makes bottom the subtype of every type.
- The bottom type appears in exhaustive type narrowing: when a switch or if-else chain has handled all cases, the remaining inferred type is `never`.

## Key Parameters

- **Exhaustiveness checking**: Compilers use `never` to verify that a union type is fully covered by case handling.
- **Throwing functions**: A function that always throws can be typed as returning `never`, signaling to callers that normal continuation is impossible.
- **Empty type confusion**: In some contexts, the "empty type" (a type with no constructors) is synonymous with bottom; in others, it is a distinct concept.

## When To Use

Use the bottom type when:
- You want to signal that a function never returns (e.g., `panic`, `exit`, `throw`).
- You are performing exhaustiveness checks on sum types or unions.
- You need a type-safe `assertNever` helper to catch unhandled cases at compile time.

## Risks & Pitfalls

- **Run-time vs. compile-time**: A function declared `never` could accidentally return in some code paths if the type checker is not strict enough.
- **Misuse for errors**: Bottom is not the same as an error result type. Use `Result<T, E>` or `Either` when you want to represent recoverable errors, and reserve bottom for unrecoverable cases.
- **Implicit conversions**: Because bottom is a subtype of all types, accidentally creating a bottom-typed expression can silently satisfy any type requirement, masking bugs.

## Related Concepts

- [[concepts/top-type]] — the supertype of all types (dual of bottom)
- [[concepts/algebraic-data-types]] — bottom is the identity for sum types
- [[concepts/type-safety]] — bottom enables safe exhaustiveness checking

## Sources

- *Programming with Types*, Chapter 7 — Subtyping (section 7.2)
