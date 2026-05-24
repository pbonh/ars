---
title: "Rust"
type: entity
tags: [entity, programming-language, systems-programming, mozilla]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Overview

Rust is a systems programming language sponsored by the Rust Foundation and originally created at Mozilla Research. It emphasizes memory safety, zero-cost abstractions, and fearless concurrency without requiring a garbage collector.

## Characteristics

- **Memory safety through ownership**: Compile-time rules prevent use-after-free, double-free, and data races.
- **Zero-cost abstractions**: High-level features (generics, traits, iterators) compile down to code as efficient as hand-written C/C++.
- **Type inference**: Local variable types are inferred where possible, reducing boilerplate.
- **Pattern matching**: Exhaustive `match` expressions replace many control-flow constructs.
- **Cargo ecosystem**: Built-in package manager, test runner, formatter (`rustfmt`), and language server (`rust-analyzer`).
- **FFI**: Seamless interoperability with C via `extern` blocks and raw pointers.
- **Editions**: The language evolves through opt-in editions (2015, 2018, 2021, 2024) that preserve backward compatibility.

## Common Strategies

- Use `Option` and `Result` instead of null pointers or exceptions.
- Leverage the borrow checker to enforce API contracts without runtime checks.
- Write safe wrappers around small `unsafe` blocks for low-level operations.
- Use `cargo` workspaces to split large applications into cohesive crates.
- Prefer iterators over explicit indexing loops for clarity and optimizer friendliness.

## Related Entities

- [[entities/cargo]] — Rust’s build tool and package manager
- [[entities/crates-io]] — the official Rust package registry
- [[entities/nushell]] — a modern shell written in Rust
- [[entities/zellij]] — a terminal multiplexer written in Rust
- [[entities/television]] — a fuzzy finder written in Rust

## Sources

- *The Rust Programming Language* — official book (raw/rust-book-book/)
