---
title: "Nushell Module System"
type: concept
tags: [concept, shell, modularity, code-organization]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nushell-book/book"]
confidence: high
---

## Definition

Nushell modules are containers that group related definitions — custom commands, aliases, constants, external commands, environment variables, and even submodules — into reusable, importable units. Modules provide namespacing and allow selective exporting and importing.

## How It Works

A module is typically a file (or directory with a `mod.nu` entry point) that contains definitions prefixed with `export`:

```nu
# spam/mod.nu
export def hello [] { "hello" }
export alias h = hello
export const MAGIC = 42
```

Consumers import the module with `use`:

```nu
use spam *
hello  # => hello
```

Or import selectively:

```nu
use spam [hello]
```

Modules can also be created inline with the `module` keyword, though file-based modules are more common for reusable code.

## Key Parameters

- `export def`, `export def --env`, `export alias`, `export const`, `export use`, `export extern` — export items from a module.
- `use` — imports a module or specific items from it.
- `overlay use` — imports a module as an overlay, allowing its definitions to be added and later removed as a group.
- `hide` — hides imported definitions, useful for shadowing or cleanup.

## When To Use

- Organize large scripts into logical modules (e.g., `git`, `utils`, `format`).
- Share reusable command libraries via files or packages.
- Use `overlay use` when you need to temporarily import a set of commands and then revert them cleanly.

## Risks & Pitfalls

- Modules are resolved at parse time; dynamic module paths are not supported.
- Recursive or circular module dependencies can lead to confusing parse errors.
- Forgetting `export` makes a definition private to the module file, which is a common source of "not found" errors for consumers.

## Related Concepts

- [[concepts/nushell-static-parsing]] — modules are parsed and resolved before evaluation
- [[concepts/nushell-custom-command]] — custom commands are the primary exportable unit of modules

## Sources

- Nushell Book: [Modules](raw/nushell-book/book/modules.md)
- Nushell Book: [Creating Modules](raw/nushell-book/book/modules/creating_modules.md)
- Nushell Book: [Using Modules](raw/nushell-book/book/modules/using_modules.md)
