---
title: "Lazy Evaluation"
type: concept
tags: [concept, performance, memory, python, generators]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/practices-of-the-python-pro-book/"]
confidence: high
---

## Definition

Lazy evaluation is the strategy of producing values only when explicitly requested, rather than computing and storing all values up front. It is "lazy" because it does as little work as possible, and only once asked. In Python, generators are the primary mechanism for lazy evaluation.

## How It Works

A generator produces a single value at a time, pausing until the next value is requested. This avoids storing all produced values in memory at once. The `yield` keyword is central: after producing a value, it yields execution back to the caller. The generator's internal state is preserved, so it can resume where it left off.

The standard pattern for writing a generator:
1. Perform main setup required for producing all values.
2. Create a loop.
3. `yield` a value on each iteration.
4. Update state for the next iteration.

Python's built-in `range` is a familiar example of lazy evaluation. `range(100_000_000)` does not allocate 100 million integers; it stores only the bounds and produces values on demand.

Generators can be chained. For example, `squares(range(100_000_000))` stores only one item from `range` and one squared result at a time, even though the conceptual pipeline is enormous.

## Key Parameters

- **`yield` vs. `return`**: `return` exits permanently; `yield` pauses and can be resumed.
- **Space complexity**: Lazy evaluation can turn an O(n) space operation into O(1).
- **Termination**: The consuming code may not need all values, so the generator may never finish its full sequence.

## When To Use

Use lazy evaluation when:
- You are iterating over a large (or infinite) sequence and don't need all values simultaneously.
- You are building a data-processing pipeline where intermediate stages can stream values.
- Memory is constrained and materializing full collections would be prohibitive.
- You want to represent an infinite or unbounded sequence (e.g., Fibonacci numbers).

## Risks & Pitfalls

- **Need for random access**: If you need to index into the middle of a sequence repeatedly, a list may be more appropriate than a generator.
- **Multiple iteration**: Generators are exhausted after a single pass. If you need to iterate multiple times, you may need to recreate the generator or materialize a list.
- **Debugging**: Paused generator state can be harder to inspect than a concrete list.

## Related Concepts

- [[concepts/big-o-notation]] — space complexity is the primary metric improved by lazy evaluation

## Sources

- *Practices of the Python Pro*, Chapter 4 — Designing for high performance
