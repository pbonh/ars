---
title: "Pi Prompt Template"
type: concept
tags: [concept, pi, prompt, slash-command]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/pi-repo/packages/coding-agent/docs/prompt-templates.md"]
confidence: high
---

## Definition

A Pi prompt template is a Markdown snippet that expands into a full prompt when invoked via a slash command (`/name`) in the interactive editor.

## How It Works

1. The user creates a `.md` file in a prompts directory (`~/.pi/agent/prompts/`, `.pi/prompts/`, or via packages).
2. The filename (without `.md`) becomes the command name.
3. Optional YAML frontmatter can include `description` and `argument-hint`.
4. Typing `/name` in the editor expands the template content into the current message.
5. Prompts are auto-completed in the TUI with descriptions and argument hints.

## Key Parameters

- Discovery paths: `~/.pi/agent/prompts/*.md`, `.pi/prompts/*.md`
- Frontmatter: `description` (optional), `argument-hint` (optional)
- Command naming: filename without extension
- Disable discovery: `--no-prompt-templates`

## When To Use

Create a prompt template when:
- You have a reusable prompt pattern (e.g., code review, refactoring, test generation).
- You want quick access to complex instructions without retyping.
- You are distributing a Pi package that includes standardized workflows.

## Risks & Pitfalls

- Prompt templates execute as user messages; they do not have special system-level privileges.
- Overly generic templates may not trigger the desired agent behavior without additional context.
- Name collisions are resolved by discovery order; local prompts override packaged ones.

## Related Concepts

- [[concepts/pi-package]]
- [[concepts/pi-skill]]

## Sources

- [Pi Prompt Templates Documentation](raw/pi-repo/packages/coding-agent/docs/prompt-templates.md)
