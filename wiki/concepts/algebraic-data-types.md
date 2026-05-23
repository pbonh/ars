---
title: "Algebraic Data Types"
type: concept
tags: [concept, type-system, functional-programming, software-design]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Definition

Algebraic data types (ADTs) are composite types formed by combining other types through two fundamental operations: product types (AND) and sum types (OR). They are called "algebraic" because the number of possible values of a composite type can be computed algebraically from the number of values of its component types.

## How It Works

- **Product types** combine multiple values at once. A tuple `(T, U)` or a struct/record with fields of type `T` and `U` is a product type. The total number of values is the product of the cardinalities of `T` and `U`.
- **Sum types** (also called tagged unions or variants) hold a value of one of several types. An `Either<T, U>` or a variant that is either a `T` or a `U` is a sum type. The total number of values is the sum of the cardinalities of `T` and `U`.
- Together, product and sum types form a closed algebra for building any complex type from primitives.

## Key Parameters

- **Exhaustiveness checking**: In languages with native ADT support, the compiler can verify that all cases of a sum type are handled.
- **Tagged vs. untagged**: A sum type must carry a tag (discriminant) so the type checker knows which variant is present. Untagged unions risk type confusion.
- **Nesting**: ADTs compose recursively—e.g., a binary tree node is a product of a value and a sum of left/right subtrees or a leaf.

## When To Use

Use algebraic data types when:
- You need to model data that is either one of several alternatives (sum type).
- You need to group multiple fields into a single value (product type).
- You want the compiler to enforce that every case is handled, eliminating null-pointer or missing-case bugs.

## Risks & Pitfalls

- **Untagged unions** in weakly typed languages allow values to be misinterpreted if the tag is lost or incorrect.
- **Deep nesting** of sum types can lead to verbose code if the language lacks pattern matching.
- **Encoding domain constraints** in ADTs alone may not be enough; you may still need run-time validation (e.g., a sum type can represent "positive integer" structurally, but the compiler won’t enforce positivity).

## Related Concepts

- [[concepts/visitor-pattern]] — a way to operate on sum types without scattering switches throughout the codebase
- [[concepts/encapsulation]] — product types naturally encapsulate related fields
- [[concepts/type-safety]] — ADTs increase safety by making invalid states unrepresentable

## Sources

- *Programming with Types*, Chapter 3 — Composition (sections 3.1–3.4)
