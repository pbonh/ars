---
title: "Rust Slice Type"
type: concept
tags: [concept, rust, collections, references]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Definition

A slice is a reference to a contiguous sequence of elements in a collection rather than the whole collection. It does not have ownership; it borrows part of the underlying data.

## How It Works

Slices are written as `&[T]` for arrays/vectors or `&str` for string slices. They consist of a pointer to the starting element and a length. Because the length is encoded in the slice type, out-of-bounds access is impossible at runtime (bounds checks are performed on indexing).

String slices (`&str`) solve the problem of referring to a substring without copying data or tracking separate byte indices that can become invalid when the original string is modified. Array/vector slices allow functions to operate on any contiguous subsequence without caring whether it is an entire vector or just a portion.

## Key Parameters

- `&str`: immutable string slice; the most common string type in Rust APIs.
- `&[T]`: slice of any type.
- Range syntax: `&s[0..5]` creates a slice from index 0 (inclusive) to 5 (exclusive).
- `.as_bytes()`, `.as_mut_slice()`: conversion methods on standard collections.

## When To Use

Use slices when:
- Writing a function that should accept either a full vector/array or just part of one.
- Returning a substring without allocating a new `String`.
- Iterating over a contiguous portion of a collection.

## Risks & Pitfalls

- **UTF-8 boundaries**: Slicing a `String` at an invalid UTF-8 boundary will panic at runtime; slice at character boundaries only.
- **Lifetime tied to source**: A slice cannot outlive the collection it borrows from.
- **Mutable slices**: `&mut [T]` enforces the same exclusivity rule as other mutable references.

## Related Concepts

- [[concepts/rust-borrowing]] — slices are a form of reference
- [[concepts/rust-ownership]] — slices do not own the data they point to
- [[concepts/rust-struct]] — structs can hold slices with explicit lifetime annotations

## Sources

- *The Rust Programming Language*, Chapter 4.3 — The Slice Type
