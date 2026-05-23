---
title: "Visitor Pattern"
type: concept
tags: [concept, design-pattern, algebraic-data-types, functional-programming]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Definition

The visitor pattern is a design pattern that separates an operation from the object structure it traverses. It allows adding new operations to a family of types without modifying the types themselves, and it provides a type-safe way to handle each variant of a sum type.

## How It Works

- **Classical OOP implementation**: Each element in the hierarchy declares an `accept(visitor)` method. Concrete visitors implement an operation for each concrete element type. Double dispatch routes the call to the correct visitor method.
- **Variant-based implementation**: In languages with sum types (variants), the variant itself provides a `visit()` function that applies one of several handler functions depending on which alternative is currently stored. Domain objects do not need an `accept()` method.
- Both approaches avoid scattering type-switching logic across the codebase, concentrating the error-prone dispatch in a single, reusable component.

## Key Parameters

- **Tight coupling in classical form**: The element hierarchy must know about the visitor interface, creating a dependency from domain objects to operations.
- **Open/closed trade-off**: Visitors make it easy to add new operations but hard to add new element types (all visitors must be updated).
- **Exhaustiveness**: Variant-based visitors can leverage the type checker to ensure every case is handled.

## When To Use

Use the visitor pattern when:
- You have a stable set of types but expect to add many new operations over time.
- You want to keep domain objects free of operational concerns (e.g., rendering, serialization).
- You are working with a sum type and need to apply different logic for each alternative.

## Risks & Pitfalls

- **Indirection cost**: Double dispatch adds method-call overhead and cognitive indirection.
- **Hierarchy bloat**: In the classical form, every new operation requires a new visitor class, which can proliferate classes.
- **Maintenance burden**: Adding a new type to the hierarchy breaks all existing visitors unless the language supports partial handling.

## Related Concepts

- [[concepts/algebraic-data-types]] — sum types are the natural structure for visitor-based dispatch
- [[concepts/strategy-pattern]] — both parameterize behavior, but visitor is focused on heterogeneous structures
- [[concepts/encapsulation]] — variant-based visitors achieve better encapsulation by removing accept() from domain objects

## Sources

- *Programming with Types*, Chapter 3 — Composition (section 3.3)
