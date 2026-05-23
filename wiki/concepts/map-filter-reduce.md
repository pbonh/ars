---
title: "Map, Filter, and Reduce"
type: concept
tags: [concept, functional-programming, data-processing, algorithms]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Definition

Map, filter, and reduce are three fundamental higher-order functions for processing collections. They abstract common looping patterns into reusable, composable operations:
- **map** transforms every element of a collection.
- **filter** selects a subset of elements matching a predicate.
- **reduce** aggregates all elements into a single value.

## How It Works

- **map** applies a function `f: T -> U` to each element of a `T[]` and produces a `U[]` of the same length.
- **filter** applies a predicate `p: T -> boolean` and returns a new collection containing only elements for which `p` is true.
- **reduce** takes an accumulator of type `U`, a combining function `(U, T) -> U`, and folds the collection into a single `U`.
- Together they form a fluent pipeline: `range.filter(p).map(f).reduce(g, init)`.

## Key Parameters

- **Purity**: All three functions assume the passed functions are pure (no side effects) so that order and parallelism can be reasoned about safely.
- **Laziness vs. eagerness**: Some implementations process elements eagerly (arrays), others lazily (iterators/generators), which affects memory usage and infinite-stream support.
- **Identity and associativity**: For parallel reduce, the combining function should be associative; for sequential reduce, associativity is not required.

## When To Use

Use map, filter, and reduce when:
- You are transforming or aggregating data in a collection.
- You want to replace imperative loops with declarative, composable pipelines.
- You need uniform operations that work across arrays, lists, trees, and streams (via iterators).

## Risks & Pitfalls

- **Readability**: Overly complex reduce functions can be harder to read than a simple loop with early exits.
- **Performance**: Chaining multiple eager map/filter calls creates intermediate arrays. Use lazy iterators or transducers when performance matters.
- **Empty collections**: reduce on an empty collection requires an initial value or throws an error, depending on the language.

## Related Concepts

- [[concepts/first-class-functions]] — these algorithms are higher-order functions
- [[concepts/iterator-pattern]] — generic versions of map/filter/reduce operate on iterators rather than arrays
- [[concepts/functor]] — map is the defining operation of a functor

## Sources

- *Programming with Types*, Chapters 5 and 10 — Function types and Generic algorithms and iterators (sections 5.4, 10.1, 10.2)
