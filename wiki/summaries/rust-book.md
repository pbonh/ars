---
title: "The Rust Programming Language"
type: summary
tags: [summary, rust, programming-language, systems-programming]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Overview

*The Rust Programming Language* is the official introductory book for Rust, written by Steve Klabnik and Carol Nichols with community contributions. It teaches Rust 1.65+ and covers the language from first principles through advanced topics. The book is published by No Starch Press and is also available free online at https://doc.rust-lang.org/stable/book/. An interactive edition with quizzes and visualizations is maintained by Brown University at https://rustbook.cs.brown.edu.

The book positions Rust as a systems programming language that delivers both low-level control and high-level ergonomics. Its central thesis is that Rust’s ownership model eliminates entire categories of memory-safety and concurrency bugs at compile time, without requiring a garbage collector. The text is example-driven, progressing from a guessing-game tutorial through ownership, types, generics, error handling, collections, functional features, smart pointers, concurrency, and finally a multithreaded web server project.

## Key Claims

- [[concepts/rust-ownership|Ownership]] is Rust’s defining feature: memory is managed through compile-time-enforced rules rather than garbage collection or manual allocation/free pairs.
- [[concepts/rust-borrowing|Borrowing]] and [[concepts/rust-lifetimes|lifetimes]] let code access data by reference without taking ownership, while the borrow checker prevents dangling pointers and data races.
- [[concepts/rust-error-handling|Error handling]] splits into unrecoverable errors (`panic!`) and recoverable errors (`Result<T, E>`), with the `?` operator streamlining propagation.
- [[concepts/rust-traits|Traits]] provide shared behavior across types; combined with [[concepts/rust-generics|generics]] they enable zero-cost abstractions through monomorphization.
- [[concepts/rust-concurrency|Fearless concurrency]] leverages the same ownership and type-system rules to turn many concurrency bugs into compile-time errors.
- [[concepts/rust-unsafe|Unsafe Rust]] is a contained escape hatch for five specific operations (raw pointers, unsafe functions, mutable statics, unsafe traits, unions); safe abstractions can wrap it.
- [[entities/cargo|Cargo]] is the unified build tool, dependency manager, test runner, and documentation generator; [[entities/crates-io|crates.io]] is the official package registry.

## Source Metadata

- **Type**: HTML book (mdBook output)
- **Authors**: Steve Klabnik, Carol Nichols, and the Rust Community
- **Publisher**: No Starch Press (print/ebook); online edition via rust-lang.org
- **URL**: https://doc.rust-lang.org/stable/book/
- **License**: dual MIT / Apache-2.0 (for the book text)
- **Ingested on**: 2026-05-23
- **Assumed Rust version**: 1.65 (released 2022-11-03) or later

## Relevant Concepts

- [[concepts/rust-ownership]] — memory management without GC
- [[concepts/rust-borrowing]] — references and the borrow checker
- [[concepts/rust-slice-type]] — views into contiguous data
- [[concepts/rust-struct]] — custom compound types
- [[concepts/rust-enum]] — sum types, Option, Result
- [[concepts/rust-pattern-matching]] — match, exhaustiveness, if let
- [[concepts/rust-generics]] — parametric polymorphism
- [[concepts/rust-traits]] — interfaces/shared behavior
- [[concepts/rust-lifetimes]] — reference validity scopes
- [[concepts/rust-error-handling]] — panic! and Result
- [[concepts/rust-closure]] — anonymous functions that capture environment
- [[concepts/rust-iterator]] — lazy, composable sequences
- [[concepts/rust-concurrency]] — threads, channels, shared state
- [[concepts/rust-unsafe]] — opting out of safety checks
- [[concepts/rust-macros]] — metaprogramming
- [[concepts/rust-smart-pointers]] — Box, Rc, RefCell
- [[concepts/rust-cargo-workspaces]] — multi-crate projects
- [[concepts/rust-modules]] — packages, crates, modules, paths

## Relevant Entities

- [[entities/rust]] — the programming language
- [[entities/cargo]] — build tool and package manager
- [[entities/crates-io]] — official package registry
