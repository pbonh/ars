---
title: "Variance"
type: concept
tags: [concept, type-system, generics, subtyping]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Definition

Variance describes how the subtyping relationship between two types carries over to composite types built from them—such as arrays, functions, or generic containers. It answers the question: if `Triangle` is a subtype of `Shape`, is `Array<Triangle>` a subtype of `Array<Shape>`?

## How It Works

- **Covariance** preserves the subtyping relationship. If `B` extends `A`, then `Container<B>` is a subtype of `Container<A>`. Most languages make read-only collections covariant.
- **Contravariance** reverses the subtyping relationship. If `B` extends `A`, then `Container<A>` is a subtype of `Container<B>`. Function argument types are typically contravariant: a function that accepts `Shape` can safely accept `Triangle`, so `(arg: Shape) => void` is a subtype of `(arg: Triangle) => void`.
- **Invariance** ignores the subtyping relationship. `Container<B>` and `Container<A>` are not subtypes of each other unless `B` and `A` are the same type. Mutable collections are usually invariant to prevent unsafe writes.
- **Bivariance** allows subtyping in both directions. TypeScript’s function arguments are bivariant for backward compatibility with JavaScript patterns: `(arg: Shape) => void` and `(arg: Triangle) => void` are subtypes of each other.

## Key Parameters

- **Position rule**: In a type definition, type parameters occurring in "output" positions (return types) tend to be covariant, while those in "input" positions (argument types) tend to be contravariant.
- **Mutable state**: Invariance is the safe default for mutable generics because allowing covariance would permit inserting a supertype value into a subtype collection.
- **Language defaults**: Different languages choose different defaults (e.g., Java arrays are covariant but invariant for generics; C# supports explicit `in` and `out` variance annotations).

## When To Use

Understand variance when:
- You are designing generic collections or interfaces and need to decide whether subtyping should be preserved, reversed, or forbidden.
- You are passing generic functions or collections across API boundaries and need to know what substitutions are safe.
- You are working in a language with explicit variance annotations (e.g., C# `IEnumerable<out T>`).

## Risks & Pitfalls

- **Array covariance bug**: In Java, `String[]` is a subtype of `Object[]`, allowing an `Object` to be stored into a `String[]`, which throws `ArrayStoreException` at run time.
- **Bivariant unsoundness**: TypeScript’s bivariant function arguments can mask type errors that would be caught under strict contravariance.
- **Overly restrictive invariance**: Requiring invariance everywhere limits code reuse; prefer covariance for read-only views and contravariance for callbacks.

## Related Concepts

- [[concepts/nominal-subtyping]] and [[concepts/structural-typing]] — variance applies to both
- [[concepts/typescript-generics]] — generic type parameters determine variance positions
- [[concepts/liskov-substitution-principle]] — variance rules formalize safe substitution

## Sources

- *Programming with Types*, Chapter 7 — Subtyping (section 7.3)
