---
title: "GitHub Copilot"
type: entity
tags: [entity, tool, ai-pair-programmer, agent-skills, microsoft]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/agentskills-io-home.md"]
confidence: high
---

## Overview

GitHub Copilot is Microsoft's AI pair programmer that works directly inside editors such as VS Code, JetBrains IDEs, and Neovim. In addition to inline completions, Copilot supports agentic features and Agent Skills, allowing it to perform multi-step coding tasks guided by custom skill documents.

## Characteristics

- **Type**: AI coding assistant integrated into mainstream editors.
- **Completion model**: Suggests whole lines or functions based on surrounding context.
- **Agent mode**: Can execute multi-step tasks using Agent Skills when enabled.
- **Skills support**: Follows the agentskills.io specification for skill discovery and activation.
- **Enterprise features**: Organization-wide policy controls, audit logs, and private model instances.

## Common Strategies

- Publish an organization-level Copilot skill for internal libraries so all developers get consistent usage patterns and examples.
- Use Copilot skills in pull-request reviews to auto-suggest fixes for common issues.
- Combine Copilot chat with skills for natural-language-driven codebase exploration ( e.g., "find all places that call the legacy auth helper and propose migrations" ).

## Sources

- [agentskills.io home page](raw/agentskills-io-home.md)
- https://github.com/
- https://docs.github.com/en/copilot/concepts/agents/about-agent-skills
