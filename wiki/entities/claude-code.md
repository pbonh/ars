---
title: "Claude Code"
type: entity
tags: [entity, tool, coding-agent, terminal, agent-skills]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/agentskills-io-home.md"]
confidence: high
---

## Overview

Claude Code is Anthropic's agentic coding tool that reads codebases, edits files, runs commands, and integrates with development workflows. It is available in the terminal, IDE, desktop app, and browser. Claude Code supports Agent Skills, enabling users to define reusable procedures that the agent can invoke on demand.

## Characteristics

- **Type**: Agentic coding assistant by Anthropic.
- **Access modes**: Terminal, IDE extension, desktop application, and web browser.
- **Skills support**: Implements the Agent Skills standard for loading specialized knowledge and workflows.
- **Integration**: Connects to existing developer tools and can run shell commands within the project environment.

## Common Strategies

- Create a skill for repetitive refactoring patterns ( e.g., "migrate all React class components to hooks" ) and invoke it across multiple files.
- Use Claude Code skills to enforce team conventions — coding style, test patterns, or documentation requirements — without writing custom linters.
- Combine Claude Code with the Claude API for headless or CI-driven automation using the same skill definitions.

## Sources

- [agentskills.io home page](raw/agentskills-io-home.md)
- https://claude.ai/code
- https://code.claude.com/docs/en/skills
