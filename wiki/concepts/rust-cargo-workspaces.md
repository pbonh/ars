---
title: "Rust Cargo Workspaces"
type: concept
tags: [concept, rust, build-tool, project-management]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Definition

A Cargo workspace is a collection of related packages that share a single `Cargo.lock` file and output directory, managed by a root `Cargo.toml`.

## How It Works

A workspace root declares member crates:

```toml
[workspace]
members = ["adder", "add-one"]
```

Each member has its own `Cargo.toml` and can depend on other workspace members via path dependencies. Workspace members share a single `target` directory and a unified lockfile, ensuring consistent dependency versions across the project.

Cargo also supports:

- **Release profiles**: `dev` (default) and `release` optimize levels, debug assertions, LTO, and panic behavior can be customized per profile.
- **Publishing**: `cargo publish` uploads a crate to [[entities/crates-io|crates.io]] after validating metadata, license, and README.
- **cargo install**: installs binary crates from crates.io into `~/.cargo/bin`.
- **Custom commands**: binaries named `cargo-<something>` on `PATH` are invocable as `cargo something`.

## Key Parameters

- `members`: list of paths to workspace crates.
- `resolver`: dependency resolution algorithm version.
- `[profile.release]` / `[profile.dev]`: optimization and codegen settings.
- `workspace.dependencies`: centralize common dependency versions.

## When To Use

Use workspaces when:
- A project grows beyond a single crate (e.g., library + CLI + test utilities).
- Multiple crates must stay on compatible dependency versions.
- You want faster incremental builds via a shared target directory.

## Risks & Pitfalls

- **Version coordination**: Publishing a workspace requires careful ordering because crates.io enforces that all dependencies exist before a dependent crate is published.
- **Feature unification**: Features are unified across the workspace; enabling a feature in one member can affect others.
- **Root-only metadata**: Some settings must be declared at the workspace root and cannot be overridden per member.

## Related Concepts

- [[concepts/cargo-registry]] — registries are the source of external dependencies
- [[concepts/rust-modules]] — modules organize code within a crate

## Sources

- *The Rust Programming Language*, Chapter 14 — More About Cargo and Crates.io
