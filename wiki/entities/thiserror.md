---
title: "thiserror"
type: entity
tags: [entity, rust-crate, error-handling]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/ERROR_HANDLING.md"]
confidence: high
---

## Overview

`thiserror` is a Rust derive macro library that reduces boilerplate when defining custom error types. Zellij uses it to define the `ZellijError` enum in `zellij_utils::errors`, allowing structured error variants that can be recovered downstream with `anyhow::Error::downcast_ref`.

## Characteristics

- `#[derive(Error)]` generates `std::error::Error` implementations
- `#[error("...")]` attributes define display messages
- Supports named fields in variants for structured error data
- Compatible with `anyhow` via `anyhow!(ZellijError::Variant { ... })`

## Common Strategies

- Define a central error enum for domain-specific failures
- Attach data to variants (e.g., `CommandNotFound { terminal_id: u32 }`)
- Create errors with `anyhow!(variant)` and recover with `downcast_ref`
- Extend the enum with new variants as the domain grows

## Sources

- [Zellij Error Handling](raw/zellij-repo/docs/ERROR_HANDLING.md)