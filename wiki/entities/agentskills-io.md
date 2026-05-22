---
title: "agentskills.io"
type: entity
tags: [entity, standard, specification, ai-skills]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-agent-docs/website/docs"]
confidence: high
---

## Overview

agentskills.io is an open standard for AI agent skills. Hermes Agent is compatible with this specification, making its skills portable, shareable, and interoperable with other agents that support the standard.

## Characteristics

- **Open standard**: Published specification for skill documents.
- **Hermes compatibility**: Hermes skills follow the agentskills.io format with additional Hermes-specific metadata extensions.
- **Skills Hub integration**: Hermes can install skills from multiple sources including skills.sh (Vercel's public skills directory), well-known endpoints, GitHub repos, and direct URLs.
- **Portable**: Skills written for Hermes can theoretically be used by other agentskills.io-compatible agents.

## Common Strategies

- **Publishing skills**: Write skills following the standard SKILL.md format and publish to GitHub or well-known endpoints.
- **Team taps**: Create a GitHub tap (repo of skills) that team members subscribe to with `hermes skills tap add`.
- **Cross-agent reuse**: Use skills across different agent platforms that support agentskills.io.

## Sources

- `user-guide/features/skills.md`
