---
title: "Nushell Implicit Return"
type: concept
tags: [concept, shell, programming-language, control-flow]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nushell-book/book"]
confidence: high
---

## Definition

In Nushell, every expression and command returns a value. The value of the **last** expression in a block, custom command, or script becomes the implicit return value of that scope. There is no syntactic distinction between "statements" and "expressions" because every command produces a value.

## How It Works

When Nushell evaluates a block, it evaluates each expression in order. The return value of each expression except the last is discarded (unless assigned to a variable or explicitly printed). The final expression's value is returned to the caller or displayed in interactive mode.

For example:

```nu
def latest-file [] {
    ls | sort-by modified | last
}
```

The pipeline `ls | sort-by modified | last` is the only expression, so its output (a file record) is the return value of `latest-file`.

In a multi-expression block, only the last value is returned:

```nu
def eight [] {
    1 + 1   # evaluated but discarded
    2 + 2   # evaluated but discarded
    4 + 4   # returned: 8
}
```

The `echo` command in Nushell returns a value; it does **not** write to stdout like in Bash. To force display, use `print`.

## Key Parameters

- `return` — can be used for early exit from a custom command, but is rarely needed.
- `ignore` — suppresses the return value of a pipeline when you do not want it propagated.
- `print` — displays its argument to stdout but itself returns `null`.

## When To Use

- Rely on implicit return in custom commands and closures to keep code concise and pipeline-friendly.
- Use `print` for debugging or user-facing output that should not become the return value.
- Use `return` only when you need early termination based on a condition.

## Risks & Pitfalls

- A common mistake is placing `echo "debug message"` before the real return expression inside a custom command. Because `echo` returns a value, that debug string becomes the return value and the subsequent expression is discarded.
- Loops like `for` do not return a value; using `for` as the last expression of a command yields `null`. Use filters like `each` or `reduce` instead when you need to return transformed data.
- Because everything returns a value, accidental side-effect-only commands (e.g., `ls` inside a `do` block) silently return `null` or their data rather than producing display output unless explicitly piped to `print` or `table`.

## Related Concepts

- [[concepts/nushell-custom-command]] — defining commands whose last expression is their return value
- [[concepts/nushell-structured-pipeline]] — pipeline values are the implicit returns of their constituent commands

## Sources

- Nushell Book: [Thinking in Nu — Implicit Return](raw/nushell-book/book/thinking_in_nu.md)
- Nushell Book: [Custom Commands — Returning Values](raw/nushell-book/book/custom_commands.md)
