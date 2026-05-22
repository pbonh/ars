---
title: "Pi Skill"
type: concept
tags: [concept, pi, agent-skills, workflow]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/pi-repo/packages/coding-agent/docs/skills.md", "raw/agentskills-io-home.md"]
confidence: high
---

## Definition

A Pi skill is a self-contained capability package that the agent loads on-demand. It provides specialized workflows, setup instructions, helper scripts, and reference documentation for specific tasks, following the Agent Skills standard.

## How It Works

1. At startup, Pi scans skill locations and extracts names and descriptions.
2. The system prompt includes available skills in XML format per the specification.
3. When a task matches a skill description, the agent uses `read` to load the full `SKILL.md`.
4. The agent follows the instructions, using relative paths to reference scripts and assets.

This is progressive disclosure: only descriptions are always in context; full instructions load on demand.

## Key Parameters

- Discovery paths: `~/.pi/agent/skills/`, `~/.agents/skills/`, `.pi/skills/`, `.agents/skills/`
- Required file: `SKILL.md` with frontmatter `name` and `description`
- Name rules: 1–64 chars, lowercase a-z, 0-9, hyphens only
- Description max: 1024 characters
- Command invocation: `/skill:name` with optional arguments

## When To Use

Create a skill when:
- You have a repeatable, specialized workflow (e.g., PDF processing, web search, code review).
- You want to share agent capabilities across projects or teams.
- You need the agent to follow a specific procedure without re-prompting every time.

## Risks & Pitfalls

- Skills can instruct the model to perform any action and may include executable code; review before use.
- Name collisions from different locations warn and keep the first found skill.
- Skills missing a description are not loaded.
- Descriptions must be specific; vague descriptions lead to missed skill loading.

## Related Concepts

- [[concepts/pi-extension]]
- [[concepts/pi-package]]
- [[concepts/agent-skills-format]] — the broader folder and file specification Pi implements
- [[concepts/progressive-disclosure]] — the three-stage loading mechanism Pi uses
- [[entities/agentskills-io]]

## Sources

- [Pi Skills Documentation](raw/pi-repo/packages/coding-agent/docs/skills.md)
