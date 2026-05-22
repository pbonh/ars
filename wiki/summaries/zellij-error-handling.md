---
title: "Zellij Error Handling"
type: summary
tags: [summary, zellij, rust, error-handling]
created: 2026-05-21
sources: ["raw/zellij-repo/docs/ERROR_HANDLING.md"]
updated: 2026-05-21
confidence: high
---

## Overview

Zellij uses a layered error-handling strategy built on three Rust crates: [[entities/anyhow|anyhow]] for propagation, [[entities/miette|miette]] for panic formatting, and [[entities/thiserror|thiserror]] for custom error variants. The goal is to eliminate bare `unwrap()` calls so that errors carry context up the call stack, giving callers the choice to recover, log, or terminate.

## Key Claims

- `unwrap()` is acceptable only at thread-root boundaries where propagation is impossible.
- `anyhow::Context` (`.context()` and `.with_context()`) attaches location-specific messages without repeating library error text.
- `fatal()` panics the application after logging the full error chain; `non_fatal()` logs and continues.
- Custom error types live in `zellij_utils::errors::ZellijError` and can be recovered downstream with `downcast_ref`.
- Converting a function to `Result<T>` is the primary refactoring pattern for removing `unwrap()`.

## Source Metadata

- **Type**: Markdown documentation
- **Owner**: Zellij Contributors
- **URL**: https://github.com/zellij-org/zellij/tree/main/docs/ERROR_HANDLING.md
- **License**: MIT
- **Ingested on**: 2026-05-21

## Relevant Concepts

- [[concepts/error-propagation]]
- [[concepts/error-context]]
- [[concepts/fatal-error-handling]]
- [[concepts/non-fatal-error-handling]]
- [[concepts/panic-handling]]
- [[concepts/custom-error-types]]