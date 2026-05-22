---
title: "miette"
type: entity
tags: [entity, rust-crate, diagnostics]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/ERROR_HANDLING.md"]
confidence: high
---

## Overview

`miette` is a Rust diagnostics library that produces styled, human-friendly error reports. Zellij uses it via `handle_panic` to format panic messages so that users see a clean diagnostic instead of a raw stack trace.

## Characteristics

- Fancy error formatting with source snippets and labels
- Panic hook integration: `handle_panic` wraps panic payloads in `miette` diagnostics
- Optional graphical report rendering in supported terminals

## Common Strategies

- Register `handle_panic` as the process panic hook
- Wrap panic payloads in `miette`-compatible error types
- Use for user-facing diagnostics where readability matters more than machine parsing

## Sources

- [Zellij Error Handling](raw/zellij-repo/docs/ERROR_HANDLING.md)