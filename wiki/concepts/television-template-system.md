---
title: "Television Template System"
type: concept
tags: [concept, fuzzy-finder, templating, string-processing]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/television-repo/docs"]
confidence: high
---

## Definition

Television's **template system** is a mini language based on the Rust [`string-pipeline`](https://docs.rs/string_pipeline) crate. It is used to dynamically format entries for display, build preview commands, construct output strings, and parameterize custom actions.

## How It Works

Templates are strings embedded in channel TOML files. They are evaluated against the currently selected entry at runtime. Operations can be chained with `|` into pipelines.

### Basic Placeholders

- `{}` — the entire raw entry.
- `{0}`, `{1}`, ... — positional fields using the default delimiter (`:` for entries, space otherwise).

### Core Operations

| Operation | Syntax | Description |
|-----------|--------|-------------|
| Split | `{split:DELIM:INDEX}` or `{split:DELIM:RANGE}` | Split on a delimiter and extract an index or slice. |
| Strip ANSI | `{strip_ansi}` | Remove color codes and other escape sequences. |
| Trim | `{trim}`, `{trim_start}`, `{trim_end}` | Remove whitespace. |
| Case | `{upper}`, `{lower}`, `{capitalize}` | Change case. |
| Pad | `{pad:WIDTH:CHAR:DIRECTION}` | Pad to a target width (`left`, `right`, `center`). |
| Prefix/Suffix | `{prepend:TEXT}`, `{append:TEXT}` | Add text around the value. |
| Regex Extract | `{regex_extract:PATTERN}` or `{regex_extract:PATTERN:GROUP}` | Extract matching text. |
| Regex Replace | `{regex_replace:PATTERN:REPLACEMENT}` | Replace matches. |
| Collection Map | `{map:{...}}` | Apply a sub-template to each element. |
| Collection Filter | `{filter:PATTERN}` | Keep elements matching a regex. |
| Collection Sort | `{sort}` or `{sort:desc}` | Sort elements. |
| Collection Join | `{join:DELIM}` | Join elements with a delimiter. |

### Pipeline Example

```toml
[source]
command = "git log --oneline --color=always"
output = "{strip_ansi|split: :0}"  # Extract commit hash only
```

## Key Parameters

- Delimiters can be escaped with double backslashes (`\\:` for literal `:`).
- Special characters: `\t` (tab), `\n` (newline).
- `display` and `ansi = true` are mutually exclusive.

## When To Use

Use templates whenever the raw entry needs to be transformed before display, preview, or output. Common scenarios: extracting a file path from a ripgrep hit (`file:line:content`), building a preview command that jumps to a specific line, formatting multi-select output as a bullet list, or filtering a subset of fields.

## Risks & Pitfalls

- Template errors surface at runtime; there is no static validation when authoring a channel.
- Complex nested pipelines can be hard to debug. The docs recommend starting with `{}` and adding one operation at a time.
- When using `{0}`, `{1}`, etc., remember the default delimiter is `:` for entries produced by the source command, but this can be overridden with `entry_delimiter`.

## Related Concepts

- [[concepts/television-channel]]
- [[entities/string-pipeline]]

## Sources

- Television docs: Template system guide and channel specification reference.
