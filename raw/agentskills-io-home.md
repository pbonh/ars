# Agent Skills Overview

A standardized way to give AI agents new capabilities and expertise.

## What are Agent Skills?

Agent Skills are a lightweight, open format for extending AI agent capabilities with specialized knowledge and workflows.

At its core, a skill is a folder containing a `SKILL.md` file. This file includes metadata (`name` and `description`, at minimum) and instructions that tell an agent how to perform a specific task. Skills can also bundle scripts, reference materials, templates, and other resources.

```
my-skill/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── assets/           # Optional: templates, resources
└── ...               # Any additional files or directories
```

## Why Agent Skills?

Agents are increasingly capable, but often don't have the context they need to do real work reliably. Skills solve this by packaging procedural knowledge and company-, team-, and user-specific context into portable, version-controlled folders that agents load on demand. This gives agents:

- **Domain expertise**: Capture specialized knowledge — from legal review processes to data analysis pipelines to presentation formatting — as reusable instructions and resources.
- **Repeatable workflows**: Turn multi-step tasks into consistent, auditable procedures.
- **Cross-product reuse**: Build a skill once and use it across any skills-compatible agent.

## How do Agent Skills work?

Agents load skills through **progressive disclosure**, in three stages:

1. **Discovery**: At startup, agents load only the name and description of each available skill, just enough to know when it might be relevant.
2. **Activation**: When a task matches a skill's description, the agent reads the full `SKILL.md` instructions into context.
3. **Execution**: The agent follows the instructions, optionally executing bundled code or loading referenced files as needed.

Full instructions load only when a task calls for them, so agents can keep many skills on hand with only a small context footprint.

## Where can I use Agent Skills?

Agent Skills are supported by a large number of AI tools and agentic clients. The following clients are listed on the agentskills.io website:

- **OpenCode** — Open source coding assistant. https://github.com/sst/opencode
- **OpenHands** — Open platform for cloud coding agents. https://openhands.dev/
- **Mux** — Run parallel coding agents with isolated workspaces. https://mux.coder.com/
- **Cursor** — AI editor and coding agent. https://cursor.com/
- **Amp** — Frontier coding agent. https://ampcode.com/
- **Letta** — Platform for building stateful agents with advanced memory. https://www.letta.com/
- **Firebender** — Android-native coding agent. https://firebender.com/
- **Goose** — Open source, extensible AI agent by Block. https://block.github.io/goose/
- **GitHub Copilot** — AI pair programmer in your editor. https://github.com/
- **VS Code** — Visual Studio Code with Copilot agent skills. https://code.visualstudio.com/
- **Claude Code** — Agentic coding tool by Anthropic. https://claude.ai/code
- **Claude** — Anthropic's AI platform. https://claude.ai/
- **OpenAI Codex** — OpenAI's coding agent. https://developers.openai.com/codex
- **Piebald** — Desktop & web app for agentic development. https://piebald.ai
- **Factory** — AI-native software development platform. https://factory.ai/
- **pi** — Minimal terminal coding harness. https://shittycodingagent.ai/
- **Databricks Genie Code** — Autonomous AI partner for data work. https://databricks.com/
- **Agentman** — Agentic healthcare platform. https://agentman.ai/
- **TRAE** — Adaptive AI IDE by ByteDance. https://trae.ai/
- **Spring AI** — Spring framework for AI functionality. https://docs.spring.io/spring-ai/reference
- **Roo Code** — Open source AI dev team in your editor. https://roocode.com
- **Mistral AI Vibe** — Command-line coding assistant by Mistral. https://github.com/mistralai/mistral-vibe
- **Command Code** — Coding agent with taste learning. https://commandcode.ai/
- **Ona** — Platform for background agents in the cloud. https://ona.com
- **VT Code** — Open-source coding agent with LLM-native understanding. https://github.com/vinhnx/vtcode
- **Qodo** — Agentic code integrity platform. https://www.qodo.ai/
- **Laravel Boost** — AI-assisted Laravel development guidelines. https://github.com/laravel/boost
- **Emdash** — Provider-agnostic desktop app for parallel agents. https://emdash.sh
- **Snowflake Cortex Code** — AI-driven agent for Snowflake. https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code
- **Kiro** — Spec-driven AI coding. https://kiro.dev/
- **Workshop** — Cross-platform AI coding agent. https://workshop.ai/
- **Google AI Edge Gallery** — Run open-source LLMs on mobile. https://github.com/google-ai-edge/gallery
- **nanobot** — Ultra-lightweight personal AI agent. https://nanobot.wiki/
- **fast-agent** — Simple, extendable LLM interaction. https://fast-agent.ai/
- **bub** — Lightweight Python framework for channel-native agents. https://bub.build/
- **Tabnine** — AI engineering platform with agentic workflows. https://www.tabnine.com/
- **Vita** — Autonomous digital workers with virtual desktops. https://www.vita-ai.net
- **Superconductor** — Multiplayer workspace for teams and coding agents. https://superconductor.com/

## Open development

The Agent Skills format was originally developed by Anthropic, released as an open standard, and has been adopted by a growing number of agent products. The standard is open to contributions from the broader ecosystem.

Discussion happens on GitHub (https://github.com/agentskills/agentskills) and Discord (https://discord.gg/MKPE9g8aUy).

## Get started with Agent Skills

- **Quickstart**: Create your first Agent Skill and see it in action. https://agentskills.io/skill-creation/quickstart
- **Specification**: The complete format specification for Agent Skills. https://agentskills.io/specification
