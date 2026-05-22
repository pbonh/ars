---
title: "VS Code"
type: entity
tags: [entity, tool, code-editor, ide, agent-skills, microsoft]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/agentskills-io-home.md"]
confidence: high
---

## Overview

Visual Studio Code ( VS Code ) is Microsoft's lightweight, extensible code editor. Through its GitHub Copilot integration and native agent-skills support, VS Code can load and execute Agent Skills, turning natural-language requests into multi-step editing and debugging workflows.

## Characteristics

- **Type**: Cross-platform desktop code editor.
- **Extensibility**: Rich extension marketplace; Copilot extension adds AI agent capabilities.
- **Skills support**: Agent Skills can be discovered and activated within the Copilot chat panel.
- **Languages & debuggers**: Broad ecosystem for virtually every programming language and runtime.

## Common Strategies

- Store project-specific Agent Skills in `.vscode/skills/` so teammates automatically get guided workflows when they open the repo.
- Use VS Code Copilot skills to generate boilerplate, run tests, and explain errors without leaving the editor.
- Combine VS Code tasks ( `.vscode/tasks.json` ) with Agent Skills for hybrid automation that mixes native editor commands with LLM-driven reasoning.

## Sources

- [agentskills.io home page](raw/agentskills-io-home.md)
- https://code.visualstudio.com/
- https://code.visualstudio.com/docs/copilot/customization/agent-skills
