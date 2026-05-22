---
title: "Nushell Immutable Variables"
type: concept
tags: [concept, shell, functional-programming, immutability]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nushell-book/book"]
confidence: high
---

## Definition

Nushell variables are **immutable by default**. Once a value is bound to a name with `let`, it cannot be reassigned. Mutable variables are available via `mut` when truly needed, but the language and standard library are designed around functional, immutable data-transformation patterns.

## How It Works

Immutability means that instead of mutating a variable in place, you create a new value from the old one:

```nu
let data = [1 2 3]
let data = ($data | append 4)  # shadowing, not mutation
```

For cases where mutation is required (e.g., performance-critical loops or accumulating state), `mut` provides explicit mutability:

```nu
mut count = 0
for x in 1..100 {
    $count = $count + $x
}
```

Immutability is a prerequisite for parallel execution commands such as `par-each`, which operates safely on immutable data across threads.

## Key Parameters

- `let` — binds an immutable variable.
- `mut` — binds a mutable variable.

## When To Use

- Prefer `let` and pipeline transformations (`each`, `update`, `where`, `reduce`) over mutable accumulators.
- Use `mut` only when mutation significantly simplifies the algorithm or improves performance.

## Risks & Pitfalls

- Users coming from imperative languages often reach for `mut` out of habit. Learning Nushell's filter commands (`each`, `reduce`, `group-by`, etc.) leads to more idiomatic and often faster code.
- Attempting to reassign a `let` variable produces an error; use variable shadowing (re-binding with `let`) or switch to `mut`.

## Related Concepts

- [[concepts/nushell-structured-pipeline]] — pipelines transform data without mutation
- [[concepts/nushell-static-parsing]] — static analysis benefits from immutable bindings

## Sources

- Nushell Book: [Thinking in Nu — Variables are Immutable by Default](raw/nushell-book/book/thinking_in_nu.md)
- Nushell Book: [Variables](raw/nushell-book/book/variables.md)
