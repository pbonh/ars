---
title: "Rust Unsafe"
type: concept
tags: [concept, rust, systems-programming, memory-safety]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Definition

Unsafe Rust is a mode that opts out of specific compile-time safety checks. It is not a separate language; `unsafe` grants access to five operations that the compiler cannot verify for memory safety.

## How It Works

The `unsafe` keyword introduces a block or function where the following are permitted:

1. Dereference a raw pointer (`*const T`, `*mut T`).
2. Call an `unsafe` function or method.
3. Access or modify a mutable static variable.
4. Implement an `unsafe` trait.
5. Access fields of a `union`.

`unsafe` does **not** disable the borrow checker, type checking, or pattern matching. References used inside an `unsafe` block are still checked. The keyword only opens the door to the five capabilities above.

Raw pointers are like C pointers: they can be null, dangling, or alias mutably. They are allowed only inside `unsafe` blocks. Creating raw pointers is safe; dereferencing them is unsafe.

The standard library wraps unsafe code in safe abstractions (e.g., `Vec`, `String`, `Rc`, `Arc`, `Mutex`). Users of these abstractions do not need `unsafe`.

## Key Parameters

- `unsafe { ... }`: unsafe block.
- `unsafe fn ...`: unsafe function (callers must wrap the call in `unsafe`).
- `unsafe trait ...`: unsafe trait (implementors promise invariants manually).
- `*const T` / `*mut T`: raw pointers.
- `extern` functions: FFI calls are unsafe because the compiler cannot check foreign code.

## When To Use

Use unsafe when:
- Interfacing with C code via FFI.
- Implementing fundamental data structures that the borrow checker cannot express (e.g., self-referential structs, intrusive linked lists).
- Optimizing hot paths where proven-safe invariants cannot be encoded in the type system.

## Risks & Pitfalls

- **Undefined behavior**: Dereferencing dangling raw pointers, violating aliasing rules, or causing data races in unsafe code leads to UB, just as in C/C++.
- **Safe abstraction leaks**: If a safe wrapper has a bug, users of the safe API can trigger UB without writing `unsafe`.
- **Scope creep**: Keep `unsafe` blocks as small as possible; audit them rigorously.

## Related Concepts

- [[concepts/rust-ownership]] — unsafe opts out of ownership checks for raw pointers
- [[concepts/rust-borrowing]] — references in unsafe blocks are still checked
- [[concepts/rust-smart-pointers]] — many smart pointers use unsafe internally

## Sources

- *The Rust Programming Language*, Chapter 19.1 — Unsafe Rust
