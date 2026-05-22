---
title: "OpenAI Codex"
type: entity
tags: [entity, tool, coding-agent, openai, agent-skills]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/agentskills-io-home.md"]
confidence: high
---

## Overview

OpenAI Codex is OpenAI's dedicated coding agent for software development. It supports Agent Skills, allowing developers to extend Codex with custom workflows, domain-specific procedures, and reusable task definitions packaged as standard skill folders.

## Characteristics

- **Type**: Cloud-based coding agent from OpenAI.
- **Integration**: Works within the OpenAI developer platform and associated tooling.
- **Skills support**: Implements the Agent Skills standard for on-demand skill loading.
- **Open source**: The Codex CLI and agent components are available on GitHub.

## Common Strategies

- Write a Codex skill for your team's deployment playbook so every engineer can trigger staging releases via natural language.
- Share Codex skills across projects by hosting them in a central GitHub repository and referencing them by URL.
- Combine Codex with OpenAI's function-calling infrastructure for skills that need to query live APIs during execution.

## Sources

- [agentskills.io home page](raw/agentskills-io-home.md)
- https://developers.openai.com/codex
- https://github.com/openai/codex
