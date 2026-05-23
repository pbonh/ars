---
title: "Iterator Pattern"
type: concept
tags: [concept, design-pattern, data-structures, generic-programming]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Definition

The iterator pattern provides a standard interface for traversing a data structure without exposing its internal representation. It decouples algorithms from the shapes of the data structures they operate on, enabling the same algorithm to work across arrays, lists, trees, and streams.

## How It Works

- An **iterator** is an object that implements a minimal contract—typically a `next()` method that returns the next value and a flag indicating whether traversal is complete.
- The data structure implements a factory method (e.g., `Symbol.iterator` in JavaScript/TypeScript) that returns a fresh iterator positioned at the beginning of the structure.
- Algorithms are written against the iterator interface, not the concrete data structure. A `print()` or `contains()` function works with any structure that can produce an iterator.
- **Generators** (resumable functions) provide a concise way to implement iterators by yielding values one at a time, automatically preserving traversal state between calls.

## Key Parameters

- **Iterator categories**: Forward, bidirectional, random-access, and input iterators differ in what operations they support (e.g., going backward, jumping ahead).
- **Invalidation**: Modifying a data structure while iterating may invalidate the iterator, leading to run-time errors or skipped elements.
- **Laziness**: An iterator can represent an infinite or lazily computed sequence, because values are produced on demand rather than stored upfront.

## When To Use

Use the iterator pattern when:
- You want to write generic algorithms that work across multiple data structures.
- You need to hide the internal layout (array, linked list, tree) from consumers.
- You are processing large or infinite streams and want to avoid materializing the entire sequence.

## Risks & Pitfalls

- **Concurrent modification**: Iterators often fail if the underlying collection is modified during traversal.
- **Single-pass exhaustion**: Some iterators can be traversed only once; reusing them requires creating a new instance.
- **Performance overhead**: Iterator abstraction can add indirection compared to direct index access in tight loops.

## Related Concepts

- [[concepts/map-filter-reduce]] — generic versions operate on iterators rather than concrete collections
- [[concepts/lazy-evaluation]] — iterators enable lazy traversal
- [[concepts/closure]] — generator-based iterators use closures to maintain traversal state

## Sources

- *Programming with Types*, Chapters 9 and 10 — Generic data structures and Generic algorithms and iterators (sections 9.3, 9.4, 10.4)
