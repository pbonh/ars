---
title: "Rust Modules"
type: concept
tags: [concept, rust, code-organization, namespaces]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Definition

Rust organizes code into a hierarchy of packages, crates, and modules. A *package* contains one or more crates; a *crate* is a binary or library; *modules* partition code within a crate and control visibility.

## How It Works

- **Package**: defined by a `Cargo.toml`. Can contain multiple binary crates (`src/bin/`) and at most one library crate (`src/lib.rs`).
- **Crate**: the smallest unit compiled by `rustc`. Binary crates have a `main` function; library crates expose a public API.
- **Module**: declared with `mod` and can be inline or in a separate file (`mod garden;` reads `src/garden.rs` or `src/garden/mod.rs`).
- **Path**: items are referenced by path (`crate::front_of_house::hosting::add_to_waitlist`). The `crate` keyword starts at the root; `super` refers to the parent module.
- **Visibility**: `pub` makes an item public. Visibility is private by default. `pub(crate)`, `pub(super)`, and `pub(in path)` provide more granular control.
- **`use`**: brings items into scope, creating shortcuts. Re-exports with `pub use` expose an item through a different module path.

The module tree is rooted at `src/lib.rs` (for libraries) or `src/main.rs` (for binaries). Modules can be nested arbitrarily.

## Key Parameters

- `mod`: declare a module.
- `pub`: make an item public.
- `use`: import a path into local scope.
- `pub use`: re-export for API ergonomics.
- `crate`, `super`, `self`: path qualifiers.

## When To Use

Use modules when:
- A crate grows large enough to need logical partitioning.
- You want to hide implementation details and expose a clean public API.
- Re-exports are needed to flatten deep module trees for consumers.

## Risks & Pitfalls

- **Path confusion**: `mod` declares; `use` imports. Declaring a module twice is an error.
- **Visibility leaks**: Forgetting `pub` on re-exports makes items inaccessible to downstream crates even if the underlying type is public.
- **File layout**: The 2018 edition module system uses `foo.rs` + `foo/bar.rs` rather than `foo/mod.rs` + `foo/bar.rs`.

## Related Concepts

- [[concepts/rust-cargo-workspaces]] — workspaces contain multiple crates
- [[concepts/rust-struct]] — structs and traits live inside modules

## Sources

- *The Rust Programming Language*, Chapter 7 — Managing Growing Projects with Packages, Crates, and Modules
