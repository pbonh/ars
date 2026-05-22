---
title: "agentskills.io"
type: entity
tags: [entity, standard, specification, ai-skills]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-agent-docs/website/docs", "raw/agentskills-io-home.md"]
confidence: high
---

## Overview

agentskills.io is the website and community hub for the Agent Skills open standard — a lightweight, folder-based format for extending AI agents with specialized knowledge and workflows. The standard was originally developed by Anthropic and released as an open specification. It is now adopted by a growing ecosystem of AI coding agents, IDEs, and agent platforms (over 38 listed clients as of 2026-05-21), including Hermes Agent, Pi, Cursor, Claude Code, VS Code, GitHub Copilot, and many others.

## Characteristics

- **Open standard**: Published specification for skill documents; governed openly on GitHub with community contributions.
- **Origin**: Originally authored by Anthropic and released as an open standard.
- **Ecosystem**: Supported by a large and growing list of agent products, editors, and frameworks.
- **Hermes compatibility**: Hermes skills follow the agentskills.io format with additional Hermes-specific metadata extensions.
- **Skills Hub integration**: Hermes can install skills from multiple sources including skills.sh (Vercel's public skills directory), well-known endpoints, GitHub repos, and direct URLs.
- **Portable**: Skills written for one compatible agent can be reused by any other agentskills.io-compatible agent.

## Common Strategies

- **Publishing skills**: Write skills following the standard SKILL.md format and publish to GitHub or well-known endpoints.
- **Team taps**: Create a GitHub tap (repo of skills) that team members subscribe to with `hermes skills tap add`.
- **Cross-agent reuse**: Use skills across different agent platforms that support agentskills.io.
- **Client-specific directories**: Many editors (e.g., Cursor, VS Code) look for skills in project-local or user-global paths; consult your client's documentation.
- **Community contribution**: Propose specification improvements or new examples via the agentskills.io GitHub repository.

## Sources

- [Hermes Agent Skills Documentation](raw/hermes-agent-docs/website/docs/user-guide/features/skills.md)
- [agentskills.io home page](raw/agentskills-io-home.md)
