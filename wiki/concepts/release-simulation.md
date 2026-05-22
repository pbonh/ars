---
title: "Release Simulation"
type: concept
tags: [concept, zellij, release-engineering, testing]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/RELEASE.md"]
confidence: high
---

## Definition

Release simulation is the practice of performing a dry-run of the full publish pipeline (version bump, tag, crate upload, install test) against a private registry before executing the real release to crates.io.

## How It Works

The Zellij release simulation involves:
1. Creating a private Git-based cargo index
2. Running a local [[entities/ktra|ktra]] registry server
3. Temporarily redirecting all internal `zellij-*` crate dependencies to the private registry
4. Executing `cargo x publish` against the private registry
5. Installing the resulting binary and verifying it runs
6. Cleaning up: resetting commits, deleting tags, restoring remotes

## Key Parameters

- Private index repo (HTTPS, not SSH)
- Registry token for ktra
- Fork of the Zellij repo (to avoid accidental real pushes)
- Commented-out crates.io credentials

## When To Use

Perform a simulated release when:
- Preparing a new version for the first time
- Changing the workspace structure or publish tooling
- Validating CI changes that affect the release pipeline

## Risks & Pitfalls

- Forgetting to clean up the fork and private registry leaves stale tags/commits.
- Accidentally using real remotes or credentials during simulation can publish prematurely.
- ktra server state is local; team-wide simulation requires shared infrastructure.

## Related Concepts

- [[concepts/cargo-registry]]
- [[entities/ktra]]

## Sources

- [Zellij Release Process](raw/zellij-repo/docs/RELEASE.md)