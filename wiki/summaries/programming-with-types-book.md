---
title: "Programming with Types"
type: summary
tags: [summary, typescript, type-system, software-design, programming-language]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Overview

*Programming with Types* by Vlad Riscutia is a practical walk-through of type system features, from basic primitives to higher-kinded types such as functors and monads. Published by Manning Publications, the book uses TypeScript as its example language because its syntax is accessible while its type system is powerful enough to demonstrate advanced features. The author’s goal is to bridge the gap between dense theoretical texts and day-to-day software engineering, showing how each type system feature addresses real-world problems.

The book progresses through four major arcs:
1. **Basic types and composition** — primitive types, compound types, enumerations, optional and result types, algebraic data types, and the visitor pattern.
2. **Type safety** — avoiding primitive obsession, enforcing constraints at construction, type casting, and serialization.
3. **Function types and subtyping** — first-class functions, closures, strategy and decorator patterns, state machines, map/filter/reduce, promises, async/await, structural vs. nominal subtyping, variance, top and bottom types.
4. **Generics and higher-kinded types** — generic data structures, iterators, generic algorithms, type constraints, functors, monads, and pointers to dependent and linear types.

Throughout, the book emphasizes that type-checker guarantees eliminate whole classes of errors that testing alone cannot catch, and that encoding meaning and constraints directly into types makes code both safer and more readable.

## Key Claims

- **[[concepts/type-safety|Type safety]]** is not merely about catching bugs; it is about encoding meaning and guarantees into the type system so that invalid states become unrepresentable.
- The **[[concepts/primitive-obsession|primitive obsession]]** antipattern—using raw numbers and strings for domain concepts—leaves room for catastrophic misinterpretation (exemplified by the Mars Climate Orbiter failure).
- **[[concepts/algebraic-data-types|Algebraic data types]]** (product types and sum types) are the fundamental building blocks for composing richer types from primitives.
- **[[concepts/first-class-functions|First-class functions]]** unlock strategy patterns, state machines, lazy evaluation, and higher-order algorithms such as **[[concepts/map-filter-reduce|map, filter, and reduce]]**.
- **[[concepts/structural-typing|Structural subtyping]]** (used by TypeScript) enables flexible reuse across library boundaries, while **[[concepts/nominal-subtyping|nominal subtyping]]** prevents accidental substitution of similar-looking types.
- **[[concepts/variance|Variance]]** (covariance, contravariance, bivariance, invariance) governs whether collections and functions can be safely substituted based on their type parameters.
- **[[concepts/functor|Functors]]** generalize `map()` beyond collections to any generic type, and **[[concepts/monad|monads]]** generalize sequential composition with error propagation and side-effect management.
- **[[concepts/higher-kinded-types|Higher-kinded types]]** are the type-system feature needed to express functors and monads abstractly, but most mainstream languages lack direct support.

## Source Metadata

- **Type**: Technical book (mdBook source Markdown)
- **Author**: Vlad Riscutia
- **Publisher**: Manning Publications
- **Language**: TypeScript (with appendix cheat sheet)
- **Ingested**: 2026-05-23
- **License**: Proprietary (licensed copy)

## Relevant Concepts

- [[concepts/algebraic-data-types]]
- [[concepts/primitive-obsession]]
- [[concepts/type-safety]]
- [[concepts/first-class-functions]]
- [[concepts/closure]]
- [[concepts/strategy-pattern]]
- [[concepts/decorator-pattern]]
- [[concepts/state-machine]]
- [[concepts/map-filter-reduce]]
- [[concepts/iterator-pattern]]
- [[concepts/promises]]
- [[concepts/async-await]]
- [[concepts/short-circuit-evaluation]]
- [[concepts/unit-type]]
- [[concepts/bottom-type]]
- [[concepts/top-type]]
- [[concepts/nominal-subtyping]]
- [[concepts/variance]]
- [[concepts/functor]]
- [[concepts/monad]]
- [[concepts/higher-kinded-types]]
- [[concepts/visitor-pattern]]
- [[concepts/immutability]]
- [[concepts/composability]]
