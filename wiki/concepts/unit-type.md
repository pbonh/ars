---
title: "Unit Type"
type: concept
tags: [concept, type-system, functional-programming]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Definition

The unit type is a type that has exactly one inhabitant (one possible value). In TypeScript it is `void` (in the sense of functions returning no meaningful value); in many functional languages it is explicitly called `unit` or `()`. Functions that are executed only for side effects return the unit type to signal that their purpose is not to produce a result.

## How It Works

- A function declared as returning `void` in TypeScript conceptually returns the unit type: the caller knows there is no usable return value.
- The unit type is the identity for product types: pairing any type `T` with unit yields `T` (up to isomorphism).
- In type algebra, unit corresponds to the number 1: `T × 1 = T`.
- Distinguishing unit from the bottom type (which has zero values) is important: a function returning unit always succeeds in returning its one value, whereas a function returning bottom can never return.

## Key Parameters

- **Language representation**: `void` in C-family languages, `()` in Haskell and ML, `Unit` in Scala, `undefined` in some JavaScript contexts.
- **Discarding results**: Some languages warn when a non-unit expression’s result is unused; unit-typed expressions are expected to be used only for effects.
- **Arity**: A nullary function (taking no arguments) is equivalent to a value of its return type; a function returning unit is equivalent to a statement.

## When To Use

Use or declare the unit type when:
- A function exists only for side effects (logging, mutation, I/O).
- You need a placeholder type in a generic position where no meaningful data exists (e.g., `Promise<void>`).
- You are modeling type algebra and need the multiplicative identity.

## Risks & Pitfalls

- **Confusion with undefined**: In TypeScript, `void` is not exactly the same as `undefined`, though a `void`-returning function may actually return `undefined` at run time.
- **Overuse in generics**: Using unit as a generic parameter to ignore data can make APIs less self-documenting than using a more descriptive type.
- **JavaScript truthiness**: `undefined` is falsy, which can lead to unexpected behavior if a unit value is accidentally used in a Boolean context.

## Related Concepts

- [[concepts/bottom-type]] — the type with zero values, distinct from unit
- [[concepts/algebraic-data-types]] — unit is the identity element for product types

## Sources

- *Programming with Types*, Chapter 2 — Basic types (section 2.1)
