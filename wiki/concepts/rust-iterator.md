---
title: "Rust Iterator"
type: concept
tags: [concept, rust, functional-programming, performance]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Definition

An iterator is a value that produces a sequence of items, one at a time. In Rust, iterators are *lazy*: they have no effect until a consuming method drives them to completion.

## How It Works

All iterators implement the `Iterator` trait, which requires a single method:

```rust
pub trait Iterator {
    type Item;
    fn next(&mut self) -> Option<Self::Item>;
}
```

Calling `.next()` advances the iterator and returns `Some(item)` or `None` when exhausted. A `for` loop desugars into creating an iterator and repeatedly calling `next`.

Iterator methods fall into two groups:

- **Adaptor methods** (lazy): `map`, `filter`, `enumerate`, `zip`, `take`, `skip`, `flat_map`, etc. They return a new iterator describing a transformed sequence.
- **Consuming methods** (eager): `collect`, `sum`, `fold`, `for_each`, `count`, `any`, `all`, etc. They drive the iterator to completion and return a non-iterator result.

Because iterators are lazy, chains of adaptors fuse into a single loop with no intermediate allocations. Benchmarks in the book show that iterator-based code is often faster than equivalent hand-written loops because the optimizer can vectorize and inline across the chain.

## Key Parameters

- `iter()`: immutable references.
- `iter_mut()`: mutable references.
- `into_iter()`: owned values (moves items out of the collection).
- `collect::<Vec<_>>()`: gather results into a collection.
- `Iterator::Item`: associated type defining the yielded element type.

## When To Use

Use iterators when:
- Transforming or filtering collections declaratively.
- Chaining multiple operations without intermediate data structures.
- Implementing custom sequences (e.g., ranges, parsers, generators).

## Risks & Pitfalls

- **Laziness trap**: A chain of adaptors without a consumer does nothing.
- **Ownership and `into_iter`**: Consuming a collection via `into_iter` moves its elements; the original collection becomes unusable for most purposes.
- **Iterator invalidation**: Rust’s borrow checker prevents the classic C++ iterator-invalidation bugs because mutable aliasing is already disallowed.

## Related Concepts

- [[concepts/iterator-pattern]] — the general design pattern
- [[concepts/rust-closure]] — closures drive iterator transformations
- [[concepts/rust-traits]] — `Iterator` is a trait with associated types

## Sources

- *The Rust Programming Language*, Chapter 13.2 — Processing a Series of Items with Iterators
