---
title: "Nushell Custom Command"
type: concept
tags: [concept, shell, functions, extensibility]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nushell-book/book"]
confidence: high
---

## Definition

A custom command in Nushell is a user-defined command created with the `def` keyword. Custom commands are first-class citizens: they participate in the help system, can accept pipeline input, declare typed input/output signatures, support named flags and rest parameters, and can carry documentation attributes.

## How It Works

Define a command with `def`, parameters in brackets, and a block body:

```nu
def greet [name: string] {
    $"Hello, ($name)!"
}
```

### Parameter Forms

- **Required positional** — `def greet [name]`
- **Optional positional** — `def greet [name?: string]`
- **Default value** — `def greet [name = "World"]`
- **Flags** — `def greet [name: string --age (-a): int]`
- **Rest parameters** — `def greet [...names: string]`
- **Wrapped external** — `def --wrapped ezal [...rest]` forwards unknown flags/args to an external command.

### Pipeline Signatures

Commands can declare which types they accept and emit:

```nu
def "str stats" []: string -> record { }
```

This enables static checking: piping a `string` into `str stats` is valid; piping an `int` is a parse-time error.

### Attributes

As of 0.103.0, commands can be annotated with attributes prefixed by `@`:

- `@example "desc" {command} --result "..."` — adds examples to help output.
- `@deprecated ["replacement"]` — emits a warning when the command is used.
- `@category "label"` — groups the command in help listings.

## Key Parameters

- `def` / `def --env` / `def --wrapped` / `export def` — keywords for defining custom commands.
- Input/output signature syntax: `input_type -> output_type` or `[list -> string, string -> string]`.

## When To Use

- Encapsulate reusable pipelines as named commands.
- Use typed parameters and signatures to catch caller mistakes early.
- Use `def --env` when a command must change the caller's environment (e.g., changing directories).

## Risks & Pitfalls

- Command names must be literal strings at parse time; dynamic command names are not allowed.
- A boolean flag cannot be typed as `bool`; it is a switch that evaluates to `true` when present and `false` when absent.
- Without an explicit `ignore` or `null` final expression, a custom command returns the last pipeline's value, which may be surprising if the command was intended to be side-effect-only.

## Related Concepts

- [[concepts/nushell-implicit-return]] — custom commands implicitly return their last expression
- [[concepts/nushell-module-system]] — custom commands can be exported from modules
- [[concepts/nushell-static-parsing]] — `def` is a parser keyword; signatures are resolved at parse time

## Sources

- Nushell Book: [Custom Commands](raw/nushell-book/book/custom_commands.md)
