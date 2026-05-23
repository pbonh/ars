---
title: "pi-prompt-template-model"
type: entity
tags: [entity, tool, pi-extension, prompt-template]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/pi-subagents-readme.md"]
confidence: medium
---

## Overview

`pi-prompt-template-model` is a [[entities/pi|Pi]]
[[concepts/pi-extension|extension]] (github.com/nicobailon/pi-prompt-template-model)
that lets users wrap subagent delegation in their own reusable
[[concepts/pi-prompt-template|prompt templates]]. It is optional;
[[entities/pi-subagents]] already works through natural language, the
`subagent` tool, slash commands, and packaged shortcuts.

## Characteristics

- A prompt template's frontmatter can set `model`, `subagent`, and `cwd`; the
  command body becomes the delegated task.
- Runtime overrides such as `--cwd=<path>` and `--subagent=<name>` are
  supported.
- Enables additional reusable workflows on top of subagents, including
  `/chain-prompts` and compare-style prompts such as `/best-of-n` (copy the
  examples into `~/.pi/agent/prompts/`).

## Common Strategies

- Define a template like `/take-screenshot` that pins a model, delegates to a
  named subagent (`browser-screenshoter`), sets `cwd`, runs against the
  argument, and restores the prior model when done — e.g.
  `/take-screenshot https://example.com`.

## Sources

- [pi-subagents README](raw/pi-subagents-readme.md)
</content>
