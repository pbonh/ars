---
title: "Zellij Release Process"
type: summary
tags: [summary, zellij, release-engineering, cargo]
created: 2026-05-21
sources: ["raw/zellij-repo/docs/RELEASE.md"]
updated: 2026-05-21
confidence: high
---

## Overview

The Zellij release process is based on `cargo x publish`, which publishes all workspace crates in dependency order. Before a real release, maintainers are expected to perform a simulated release using a private [[entities/ktra|ktra]] registry to validate the pipeline end-to-end. The document describes both the dry-run simulation and the real release checklist.

## Key Claims

- Simulation requires a private cargo index (Git repo), a local ktra server, and temporary registry redirects in all Cargo.toml files.
- Safety measures include removing upstream remotes and disabling crates.io credentials during simulation.
- After a successful simulation, the real release uses the same `cargo x publish` command against crates.io.
- Cleanup after simulation is manual: reset commits, delete tags, restore remotes.

## Source Metadata

- **Type**: Markdown documentation
- **Owner**: Zellij Contributors
- **URL**: https://github.com/zellij-org/zellij/tree/main/docs/RELEASE.md
- **License**: MIT
- **Ingested on**: 2026-05-21

## Relevant Concepts

- [[concepts/cargo-registry]]
- [[concepts/release-simulation]]

## Relevant Entities

- [[entities/ktra]]
- [[entities/zellij]]