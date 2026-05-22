---
title: "Pi"
type: entity
tags: [entity, tool, coding-agent, terminal, ai]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/pi-repo/packages/coding-agent/docs"]
confidence: high
---

## Overview

Pi is a minimal terminal-based coding agent harness created by [[entities/earendil-works]]. It provides an interactive TUI for conversing with LLMs, executing shell commands, editing files, and managing codebases. Pi is designed to be extended rather than bloated: its core is small, and most additional behavior comes from user-provided [[concepts/pi-extension|extensions]], [[concepts/pi-skill|skills]], [[concepts/pi-theme|themes]], and [[concepts/pi-prompt-template|prompt templates]].

## Characteristics

- **Runtime**: Node.js/TypeScript, distributed via npm as `@earendil-works/pi-coding-agent`
- **Interface**: Interactive terminal UI (TUI) with slash commands and autocomplete
- **Extensibility**: TypeScript extensions, Agent Skills, themes, prompt templates, packages
- **Providers**: Anthropic, OpenAI, Google, DeepSeek, Groq, Cerebras, Mistral, Azure, Cloudflare
- **Session model**: Tree-structured JSONL sessions with in-place branching
- **Headless modes**: SDK (Node.js API) and RPC (stdin/stdout JSONL)

## Common Strategies

- Install globally with `npm install -g --ignore-scripts @earendil-works/pi-coding-agent`
- Authenticate via `/login` for subscriptions or set `ANTHROPIC_API_KEY` etc.
- Place extensions in `~/.pi/agent/extensions/` for auto-discovery and hot-reload
- Share reusable capabilities via [[concepts/pi-package|pi packages]] published to npm or git
- Use `/compact` to manually summarize conversation history when context runs low

## Sources

- [Pi Documentation](raw/pi-repo/packages/coding-agent/docs/index.md)
