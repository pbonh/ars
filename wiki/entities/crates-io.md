---
title: "crates.io"
type: entity
tags: [entity, registry, rust, package-distribution]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Overview

crates.io is the official package registry for the Rust programming language. It hosts open-source libraries (crates) that can be consumed by Cargo, Rust’s build tool and package manager.

## Characteristics

- **Index-based resolution**: Cargo reads a Git repository index containing metadata JSON for each crate version, then downloads `.crate` tarball files over HTTP.
- **Immutable publishes**: Once a version is published, it cannot be removed or altered (though it can be yanked, preventing new dependency resolution while keeping existing downloads working).
- **Documentation hosting**: crates.io links to docs.rs, which automatically builds and hosts documentation for every published crate.
- **Authentication**: Publishing requires an API token generated via crates.io and used with `cargo login`.
- **Metadata requirements**: Published crates must declare a license, version, description, and valid manifest fields.

## Common Strategies

- Search crates.io for existing solutions before reimplementing common functionality.
- Use semantic versioning ranges in `Cargo.toml` for libraries; commit `Cargo.lock` for binaries.
- Yank broken versions rather than deleting them, to avoid breaking downstream builds.
- Mirror crates.io or run a private registry (e.g., [[entities/ktra|ktra]]) for internal or proprietary crates.

## Related Entities

- [[entities/cargo]] — the tool that consumes crates.io
- [[entities/rust]] — the language ecosystem the registry serves
- [[entities/ktra]] — private registry implementation

## Sources

- *The Rust Programming Language*, Chapter 14.2 — Publishing a Crate to Crates.io
