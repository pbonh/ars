---
title: "Rust Ownership"
type: concept
tags: [concept, rust, memory-management, systems-programming]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Definition

Ownership is Rust’s compile-time memory-management discipline. Every value has a single *owner*; when the owner goes out of scope the value is *dropped* (its memory is freed). No garbage collector or manual `free` is required.

## How It Works

Rust’s ownership system rests on three rules enforced by the compiler:

1. Each value has exactly one owner at a time.
2. Ownership can be *moved* to another binding or into a function.
3. When the owner leaves scope, the value is automatically cleaned up via the `drop` function (analogous to C++ RAII).

Values with a fixed, known size (e.g., integers, booleans) implement the `Copy` trait and are copied rather than moved. Values with heap-allocated or variable-size data (e.g., `String`, `Vec<T>`) are moved by default: after `let s2 = s1;`, `s1` is no longer valid.

The stack/heap distinction matters because ownership’s primary purpose is managing heap data. The stack is LIFO and fast; the heap is dynamic and slower. A `String` stores its metadata (pointer, length, capacity) on the stack and its contents on the heap. Ownership tracks the heap allocation and frees it when the stack metadata is dropped.

## Key Parameters

- `Copy` trait: enables bitwise copy instead of move for simple types.
- `Clone` trait: explicit deep-copy for types that are not `Copy`.
- `Drop` trait: custom cleanup logic executed on scope exit.
- Move semantics: assignment and function calls transfer ownership.

## When To Use

Ownership is the default in every Rust program. You must work with it when:
- Passing heap-allocated data into or out of functions.
- Returning multiple values from a function (previously you might have used output parameters in C).
- Designing data structures that own their contents.

## Risks & Pitfalls

- **Use-after-move**: Accessing a variable after its value has been moved produces a compile-time error, which can surprise newcomers.
- **Deep copies by accident**: Calling `.clone()` everywhere to avoid move errors can hurt performance; prefer borrowing when possible.
- **Partial moves**: Moving individual fields out of a struct can make the parent struct partially invalid.

## Related Concepts

- [[concepts/rust-borrowing]] — accessing data without taking ownership
- [[concepts/rust-slice-type]] — borrowed views into collections
- [[concepts/rust-smart-pointers]] — types like `Box<T>` that own heap data
- [[concepts/rust-lifetimes]] — how long references remain valid

## Sources

- *The Rust Programming Language*, Chapter 4 — Understanding Ownership
