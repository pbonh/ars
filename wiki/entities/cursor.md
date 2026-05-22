---
title: "Cursor"
type: entity
tags: [entity, tool, ai-editor, coding-agent, agent-skills]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/agentskills-io-home.md"]
confidence: high
---

## Overview

Cursor is an AI-native code editor and coding agent that integrates deeply with a developer's codebase. It supports Agent Skills, allowing users to extend Cursor's capabilities with custom workflows, review procedures, and specialized knowledge packaged as standard skill folders.

## Characteristics

- **Type**: Desktop IDE ( fork of VS Code ) with built-in AI agent features.
- **Agent capabilities**: Code understanding, planning, building, bug fixing, change review, and tool integration.
- **Skills support**: Loads and activates Agent Skills according to the agentskills.io specification.
- **Model support**: Multiple LLM providers behind the scenes; exact set varies by subscription tier.

## Common Strategies

- Write a Cursor-specific skill for onboarding new engineers to your codebase ( e.g., "how we add a new API endpoint" ).
- Share skills across a team by committing them to the repo's `.cursor/skills/` directory or a shared GitHub tap.
- Combine Cursor's native context awareness with custom skills for domain-specific tasks like security audits or compliance checks.

## Sources

- [agentskills.io home page](raw/agentskills-io-home.md)
- https://cursor.com/
- https://cursor.com/docs/context/skills
