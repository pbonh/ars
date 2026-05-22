---
title: "Non-Fatal Error Handling"
type: concept
tags: [concept, zellij, rust, error-handling]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/ERROR_HANDLING.md"]
confidence: high
---

## Definition

Non-fatal error handling is the pattern of logging an error and continuing execution, used when the failure is transient or does not compromise program state.

## How It Works

Zellij provides a `.non_fatal()` method on `Result<(), E>` (and `Err` wrappers). It writes the error chain to the application log and returns `()`, allowing execution to proceed.

Example:
```rust
fs::create_dir_all(&dir)
    .context("failed to create plugin asset directory")
    .non_fatal();
```

## Key Parameters

- `.non_fatal()`: logs and swallows the error
- Only valid on `Result<(), _>` because a typed `Ok` value is presumed needed downstream

## When To Use

Use non-fatal handling when:
- The error is cosmetic (e.g., failed to write a cache file)
- A fallback default can safely be used
- The error is worth investigating but not worth crashing the session

## Risks & Pitfalls

- Overuse hides systemic problems.
- `.non_fatal()` returns `()`, so you cannot use the `Ok` value; rewrite to `match` if you need both branches.

## Related Concepts

- [[concepts/fatal-error-handling]]
- [[concepts/error-propagation]]

## Sources

- [Zellij Error Handling](raw/zellij-repo/docs/ERROR_HANDLING.md)