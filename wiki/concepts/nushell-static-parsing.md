---
title: "Nushell Static Parsing"
type: concept
tags: [concept, shell, compiler, static-analysis]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nushell-book/book"]
confidence: high
---

## Definition

Nushell evaluates code in two strictly separated stages: a **Parsing** stage that processes the entire source code, followed by an **Evaluation** stage that executes it. This static-parsing model is closer to compiled languages (Rust, C++) than to dynamic shells (Bash, Python). All source files, modules, and constants must be known and resolvable at parse time.

## How It Works

1. **Stage 1 (Parser):** The entire expression or file is parsed. Parser keywords such as `source`, `use`, `overlay use`, and `hide` resolve their targets immediately. Types are checked. Completions and syntax highlighting are generated from this stage.
2. **Stage 2 (Engine):** The parsed code is evaluated. Variables are bound, pipelines run, and side effects occur.

Because parsing precedes evaluation, any construct that tries to generate or locate source code dynamically will fail. For example:

```nu
("print Hello" | save output.nu; source output.nu)  # Error: file not found at parse time
```

Similarly, variables cannot be used as arguments to parser keywords:

```nu
let my_path = "~/nushell-files"
source $"($my_path)/common.nu"  # Error: not a parse-time constant
```

Constants (`const`) are the exception: they are resolved during parsing, so they can be used with parser keywords.

## Key Parameters

- `source`, `use`, `overlay use`, `hide`, `source-env` — parser keywords that require their targets to exist and be readable during Stage 1.
- `const` — defines a parse-time constant that can be used in parser keyword arguments.
- `def` — a parser keyword; command names must be literals, not variables.

## When To Use

- Leverage static parsing for IDE integration, real-time error detection, and reliable refactoring.
- Use `const` for paths and values that need to be available to `source` or `use`.
- Structure your code so that all modules and source files are statically discoverable; avoid runtime code generation.

## Risks & Pitfalls

- Users coming from Bash or Python often expect `eval`-like behavior or dynamic `source` paths. These patterns are fundamentally incompatible with Nushell's architecture.
- Typing multiple lines in the REPL works because each line is parsed and evaluated independently. The limitation only appears when multiple dependent lines are parsed as a single expression (e.g., inside a script or block).
- Attempting to `cd` and then `source` a relative file in the same block fails because `cd` happens during evaluation, while `source` resolves during parsing.

## Related Concepts

- [[concepts/nushell-module-system]] — modules are resolved statically at parse time
- [[concepts/nushell-custom-command]] — `def` is a parser keyword; command names and signatures are fixed at parse time

## Sources

- Nushell Book: [Thinking in Nu — Think of Nushell as a Compiled Language](raw/nushell-book/book/thinking_in_nu.md)
- Nushell Book: [How Nushell Code Gets Run](raw/nushell-book/book/how_nushell_code_gets_run.md)
