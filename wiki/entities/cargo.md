---
title: "Cargo"
type: entity
tags: [entity, build-tool, package-manager, rust]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Overview

Cargo is Rust’s official build system, dependency manager, test runner, and documentation generator. It ships with every Rust installation via `rustup` and is the standard entry point for Rust development.

## Characteristics

- **Project scaffolding**: `cargo new` and `cargo init` create binary or library projects with standard layouts.
- **Dependency resolution**: Downloads and compiles crates from [[entities/crates-io|crates.io]] or alternative registries, producing a reproducible `Cargo.lock`.
- **Build profiles**: `dev` and `release` profiles control optimization level, debug info, LTO, and panic behavior.
- **Workspaces**: Multi-crate projects share a single lockfile and target directory.
- **Testing**: `cargo test` discovers and runs unit, integration, and documentation tests.
- **Documentation**: `cargo doc` generates HTML docs from doc comments; `cargo publish` uploads to crates.io.
- **Extensibility**: Custom commands named `cargo-<name>` on `PATH` are automatically available as `cargo name`.

## Common Strategies

- Pin dependencies with `Cargo.lock` in applications; allow flexibility with version ranges in libraries.
- Use workspaces to separate a public library from internal binaries and test helpers.
- Define `[profile.release]` overrides for size-critical or performance-critical builds.
- Run `cargo clippy` and `cargo fmt` in CI to enforce style and catch common mistakes.

## Related Entities

- [[entities/rust]] — the language Cargo builds
- [[entities/crates-io]] — the default registry Cargo resolves against
- [[entities/ktra]] — a private registry implementation used by projects like Zellij

## Sources

- *The Rust Programming Language*, Chapter 1.3 — Hello, Cargo!, and Chapter 14 — More About Cargo and Crates.io
