---
title: "Hermes Agent"
type: entity
tags: [entity, tool, ai-agent, autonomous-agent, nous-research]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-agent-docs/website/docs"]
confidence: high
---

## Overview

Hermes Agent is an autonomous AI agent built by Nous Research. It is designed as a self-improving agent with a built-in learning loop that creates skills from experience, improves them during use, and builds a persistent model of the user across sessions. It is not tied to a specific IDE or laptop — it runs on VPS, GPU clusters, or serverless infrastructure and can be interacted with from 20+ messaging platforms.

## Characteristics

- **Closed learning loop**: Agent-curated memory, autonomous skill creation, skill self-improvement, FTS5 cross-session recall, and optional Honcho dialectic user modeling.
- **Multi-platform gateway**: CLI, Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Mattermost, Email, SMS, Teams, Google Chat, and more — all from one gateway instance.
- **70+ built-in tools**: Terminal (7 backends), browser (5 backends), web search, file operations, code execution, delegation, MCP, cron, kanban, and more.
- **Three API modes**: OpenAI-compatible, OpenAI Codex Responses, and native Anthropic Messages — with automatic fallback on provider failure.
- **Plugin architecture**: Memory providers, context engines, custom tools, hooks, and CLI commands via three discovery sources.
- **Durable multi-agent coordination**: SQLite-backed Kanban board for cross-profile collaboration.
- **Scheduled automation**: Built-in cron with skill-backed jobs and multi-platform delivery.

## Common Strategies

- **Remote agent on VPS**: Install on a cheap cloud VM, interact via Telegram, never SSH in.
- **Serverless with Modal/Daytona**: Hibernates when idle, costs nearly nothing.
- **Profile specialization**: Create named profiles (`coder`, `writer`, `ops`) with distinct toolsets and memory for Kanban workflows.
- **Skill accumulation**: Let the agent build skills from complex tasks over time, then share via taps or the Skills Hub.
- **MCP bridge**: Connect to existing tool ecosystems (GitHub, databases, internal APIs) without writing custom Hermes tools.

## Sources

- `index.md`
- `developer-guide/architecture.md`
- `reference/faq.md`
