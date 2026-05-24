---
title: "Cargo Registry"
type: concept
tags: [concept, rust, packaging, release-engineering]
created: 2026-05-21
updated: 2026-05-23
sources: ["raw/zellij-repo/docs/RELEASE.md", "raw/rust-book-book/"]
confidence: high
---

## Definition

A Cargo registry is a package index and artifact store for Rust crates. Zellij uses both the official crates.io registry and private registries (via [[entities/ktra|ktra]]) for release testing.

## How It Works

A registry consists of:
- An **index**: a Git repository containing metadata JSON for each crate version
- A **download endpoint**: an HTTP server serving `.crate` tarball files
- An **API endpoint**: for publishing, yanking, and authentication

Cargo resolves dependencies from the index, downloads tarballs, and verifies checksums. The official registry for the Rust ecosystem is [[entities/crates-io|crates.io]], which hosts open-source crates alongside documentation on docs.rs. Private registries follow the same index-plus-tarball protocol and are used by organizations that need internal artifact distribution.

## Key Parameters

- Index URL: Git repository with `config.json` at root
- `dl` and `api` endpoints in `config.json`
- Registry token: used by `cargo login` and `cargo publish`

## When To Use

Relevant when:
- Publishing a Rust workspace to crates.io
- Setting up a private registry for internal or test packages
- Simulating a release before going public

## Risks & Pitfalls

- Published versions are immutable; there is no "undo" for a bad release.
- Private registry tokens must be rotated regularly.
- Workspace publishes must respect dependency ordering.

## Related Concepts

- [[concepts/release-simulation]]
- [[concepts/rust-cargo-workspaces]]
- [[entities/ktra]]
- [[entities/crates-io]]

## Sources

- [Zellij Release Process](raw/zellij-repo/docs/RELEASE.md)