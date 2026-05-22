---
title: "Hermes Agent Documentation"
type: summary
tags: [summary, ai-agent, autonomous-agent, nous-research]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-agent-docs/website/docs"]
confidence: high
---

## Overview

Hermes Agent is an autonomous AI agent built by [[entities/nous-research]]. Unlike IDE-tethered copilots or single-API chatbots, Hermes is designed as a self-improving agent that lives wherever you deploy it — a $5 VPS, a GPU cluster, or serverless infrastructure. It supports 20+ messaging platforms (Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Email, SMS, Teams, and more) and can be interacted with from any of them while it works on remote infrastructure.

The architecture is built around a synchronous [[concepts/hermes-agent-loop]] (`AIAgent` in `run_agent.py`) that handles prompt assembly, provider selection, tool execution, retries, fallback, and persistence. The agent supports three API modes: OpenAI-compatible `chat_completions`, OpenAI Codex `codex_responses`, and native Anthropic `anthropic_messages`.

Hermes distinguishes itself through a built-in learning loop: it creates [[concepts/hermes-skills-system]] from experience, improves them during use, nudges itself to persist knowledge, and builds a deepening model of the user across sessions via bounded [[concepts/hermes-persistent-memory]] (MEMORY.md / USER.md) and optional external memory providers.

## Key Claims

- Hermes is the only agent with a **closed learning loop** — agent-curated memory, autonomous skill creation, skill self-improvement during use, and FTS5 cross-session recall with LLM summarization.
- It runs on **6 terminal backends**: local, Docker, SSH, Daytona, Singularity, and Modal — with serverless persistence on Daytona/Modal.
- It supports **20+ messaging platforms** from a single [[concepts/hermes-gateway]], making it platform-agnostic at the core.
- The **[[concepts/hermes-kanban-board]]** provides durable SQLite-backed multi-agent coordination across named profiles, surviving restarts and supporting human-in-the-loop workflows.
- **[[concepts/hermes-subagent-delegation]]** spawns isolated child agents with independent contexts, toolsets, and iteration budgets.
- **[[concepts/hermes-cron-scheduler]]** supports first-class agent tasks (not just shell tasks) with skill-backed jobs and multi-platform delivery.
- **[[concepts/hermes-mcp-integration]]** connects to external tool servers (stdio and HTTP) with per-server tool filtering and dynamic discovery.
- The **[[concepts/hermes-plugin-system]]** supports three discovery sources (`~/.hermes/plugins/`, `.hermes/plugins/`, pip entry points) with specialized memory provider and context engine plugin types.
- **[[concepts/hermes-profile-isolation]]** gives each profile (`hermes -p <name>`) its own `HERMES_HOME`, config, memory, sessions, and gateway PID.

## Source Metadata

| Field | Value |
|-------|-------|
| Type | GitHub repository documentation (Docusaurus site) |
| Owner | Nous Research |
| URL | https://github.com/NousResearch/hermes-agent/tree/main/website/docs |
| License | Repository license (see GitHub) |
| Ingested on | 2026-05-21 |

## Relevant Concepts

- [[concepts/hermes-agent-loop]]
- [[concepts/hermes-skills-system]]
- [[concepts/hermes-persistent-memory]]
- [[concepts/hermes-subagent-delegation]]
- [[concepts/hermes-kanban-board]]
- [[concepts/hermes-cron-scheduler]]
- [[concepts/hermes-mcp-integration]]
- [[concepts/hermes-gateway]]
- [[concepts/hermes-provider-resolution]]
- [[concepts/hermes-context-compression]]
- [[concepts/hermes-session-storage]]
- [[concepts/hermes-plugin-system]]
- [[concepts/hermes-profile-isolation]]
