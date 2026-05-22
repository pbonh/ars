---
title: "Agent Skills Format"
type: concept
tags: [concept, agent-skills, specification, ai-tools]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/agentskills-io-home.md"]
confidence: high
---

## Definition

The Agent Skills Format is a lightweight, file-based specification for packaging specialized knowledge and workflows so that AI agents can discover, load, and execute them on demand. A skill is a folder containing a mandatory `SKILL.md` file plus optional scripts, references, and assets.

## How It Works

A skill folder follows this layout:

```
my-skill/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── assets/           # Optional: templates, resources
└── ...               # Any additional files or directories
```

The `SKILL.md` file must include at minimum:
- `name` — a short identifier for the skill
- `description` — a concise explanation of what the skill does

Additional instructions in the file tell the agent how to perform the specific task. The agent reads the full file only when the skill is activated, keeping the permanent context footprint small.

## Key Parameters

- **Required file**: `SKILL.md` with `name` and `description`
- **Optional folders**: `scripts/`, `references/`, `assets/`, or any other files
- **Versioning**: Skills are plain folders, so they can be tracked in Git or distributed as archives
- **Portability**: Any agent that implements the standard can consume the same skill folder

## When To Use

Use the Agent Skills format when:
- You have a repeatable, specialized workflow you want an agent to perform consistently.
- You need to share agent capabilities across projects, teams, or even different agent products.
- You want version-controlled, auditable procedures rather than ad-hoc prompts.

## Risks & Pitfalls

- Skills can instruct the model to perform any action and may include executable code; review before use.
- Because the format is open and folder-based, there is no built-in sandboxing — the agent's execution environment determines safety.
- Name collisions can occur when multiple skill sources are merged; agents typically keep the first discovered skill and warn.

## Related Concepts

- [[concepts/progressive-disclosure]] — how agents load skills without keeping full instructions in context at all times
- [[concepts/pi-skill]] — Pi's implementation and discovery-path conventions
- [[concepts/hermes-skills-system]] — Hermes Agent's skill installation and tap system

## Sources

- [agentskills.io home page](raw/agentskills-io-home.md)
- [Agent Skills Specification](https://agentskills.io/specification)
