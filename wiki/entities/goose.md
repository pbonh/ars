---
title: "Goose"
type: entity
tags: [entity, tool, coding-agent, open-source, agent-skills]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/agentskills-io-home.md"]
confidence: high
---

## Overview

Goose is an open-source, extensible AI agent created by Block ( formerly Square ). It goes beyond code suggestions to install dependencies, execute commands, edit files, and run tests — all with any LLM. Goose supports Agent Skills, making it easy to add reusable workflows and domain expertise.

## Characteristics

- **Type**: Open-source extensible AI agent.
- **Owner**: Block ( public company, financial services and creator tools ).
- **Flexibility**: Works with any LLM provider; not tied to a single model or API.
- **Skills support**: Implements the Agent Skills standard for portable capability extensions.
- **Extensibility**: Plugin-like architecture beyond skills for custom tool integrations.

## Common Strategies

- Write a Goose skill for your team's onboarding checklist so new developers can say "set up my dev environment" and Goose runs the exact sequence.
- Distribute Goose skills via GitHub so external contributors get the same automation your internal team uses.
- Pair Goose with local or self-hosted models for air-gapped environments that still benefit from structured skill workflows.

## Sources

- [agentskills.io home page](raw/agentskills-io-home.md)
- https://block.github.io/goose/
- https://block.github.io/goose/docs/guides/context-engineering/using-skills/
- https://github.com/block/goose
