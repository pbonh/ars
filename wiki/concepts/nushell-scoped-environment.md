---
title: "Nushell Scoped Environment"
type: concept
tags: [concept, shell, environment-variables, scope]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nushell-book/book"]
confidence: high
---

## Definition

In Nushell, changes to environment variables are scoped to the block in which they occur. When a block ends, any environment mutations made inside it are reverted. This design eliminates global mutable state and makes scripts more predictable and easier to reason about.

## How It Works

Environment variables are modified using commands like `load-env` or direct assignment (`$env.VAR = "value"`). These changes persist only for the duration of the current block. For example:

```nu
ls | each { |row|
    cd $row.name
    make
}
```

Each iteration of `each` runs in its own block. The `cd` command changes `$env.PWD`, but that change is undone when the iteration ends, so the next iteration starts from the original directory.

To propagate environment changes to the caller, define the command with `def --env` or `export def --env`:

```nu
def --env go-home [] {
    cd ~
}
```

## Key Parameters

- `def --env` / `export def --env` — defines a command that preserves environment changes in its caller's scope.
- `load-env` — atomically updates multiple environment variables within the current block.

## When To Use

- Rely on scoped environment by default to avoid unintended side effects in loops, custom commands, and scripts.
- Use `def --env` only when a command's purpose is to change the caller's environment (e.g., a `cd` wrapper or environment setup script).

## Risks & Pitfalls

- Forgetting that `cd` inside a custom command is scoped can lead to confusion when the caller's directory does not change.
- Global environment mutation is not possible in standard blocks; if you need persistent changes, they must be written to configuration files and reloaded.

## Related Concepts

- [[concepts/nushell-custom-command]] — commands defined with `--env` escape the default scoping rule
- [[concepts/nushell-immutable-variables]] — Nushell avoids global mutable state in both variables and environment

## Sources

- Nushell Book: [Thinking in Nu — Nushell's Environment is Scoped](raw/nushell-book/book/thinking_in_nu.md)
- Nushell Book: [Environment](raw/nushell-book/book/environment.md)
