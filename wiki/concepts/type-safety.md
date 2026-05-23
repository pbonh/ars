---
title: "Type Safety"
type: concept
tags: [concept, type-system, software-correctness, software-design]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Definition

Type safety is the property of a programming language or program that prevents operations from being applied to values of inappropriate types. A type-safe system guarantees that type errors are caught before they can cause run-time misbehavior, ideally at compile time.

## How It Works

- The **type checker** verifies that every operation receives arguments of the expected type and that every expression produces a value of the declared type.
- **Strong typing** rejects most implicit conversions, while **weak typing** allows more coercions at the risk of subtle bugs.
- **Static typing** catches mismatches at compile time; **dynamic typing** defers checks to run time.
- Type safety can be increased by adding more information to the type system: units of measure, value constraints, nullability, and ownership.

## Key Parameters

- **Soundness**: A sound type system guarantees that well-typed programs cannot go wrong (no type-related crashes).
- **Completeness**: A complete type system accepts every program that would not crash; most practical systems sacrifice completeness for soundness.
- **Gradual typing**: Systems like TypeScript or Python type hints allow mixing typed and untyped code, trading some safety for interoperability.

## When To Use

Maximize type safety when:
- Correctness is critical (financial, medical, aerospace software).
- The system is large enough that informal understanding of data shapes cannot be trusted.
- Refactoring is frequent; a strong type system acts as a safety net.

## Risks & Pitfalls

- **Type casting and assertions**: Manually overriding the type checker (`as`, `any`, `unknown` downcasts) moves responsibility back to the developer and can reintroduce run-time errors.
- **Overly complex types**: Encoding every invariant in the type system can lead to types that are harder to read than the code they describe.
- **False negatives**: No type system catches all bugs; logic errors and performance issues remain outside its scope.

## Related Concepts

- [[concepts/primitive-obsession]] — a common failure mode that undermines type safety
- [[concepts/static-typing-in-typescript]] — one approach to compile-time type checking
- [[concepts/encapsulation]] — hides implementation so consumers depend on stable types

## Sources

- *Programming with Types*, Chapters 1 and 4 — Introduction to typing and Type safety
