---
title: "Agent Skills Format"
type: concept
tags: [concept, agent-skills, specification, ai-tools]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/agentskills-io-home.md", "raw/agentskills-io-specification.md"]
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

The `SKILL.md` file must contain YAML frontmatter followed by Markdown content. The frontmatter fields are:

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | 1–64 chars; lowercase `a-z`, `0-9`, hyphens only; no leading, trailing, or consecutive hyphens; must match the parent directory name |
| `description` | Yes | 1–1024 chars; describes what the skill does and when to use it |
| `license` | No | Short license name or bundled file reference |
| `compatibility` | No | 1–500 chars; environment requirements (product, packages, network) |
| `metadata` | No | Arbitrary string-key-to-string-value map for client extensions |
| `allowed-tools` | No | Space-separated pre-approved tool list (experimental) |

The Markdown body after the frontmatter contains the skill instructions. There are no format restrictions; recommended content includes step-by-step instructions, input/output examples, and common edge cases. The agent loads the full body only when the skill is activated, keeping the permanent context footprint small.

## Key Parameters

- **Required file**: `SKILL.md` with valid frontmatter (`name` and `description` are mandatory)
- **Optional folders**:
  - `scripts/` — executable code (self-contained or clearly documented; Python, Bash, JavaScript common)
  - `references/` — on-demand docs (`REFERENCE.md`, `FORMS.md`, domain-specific files)
  - `assets/` — static resources (templates, images, data files)
- **File references**: Use relative paths from the skill root; keep references one level deep; avoid deeply nested chains
- **Line budget**: Keep `SKILL.md` under ~500 lines; move detailed reference material to `references/`
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
- The `allowed-tools` field is experimental and not uniformly supported across implementations.
- Frontmatter YAML errors or constraint violations can prevent a skill from loading at all; validate with [[entities/skills-ref|skills-ref]] before publishing.

## Related Concepts

- [[concepts/progressive-disclosure]] — how agents load skills without keeping full instructions in context at all times
- [[concepts/skill-validation]] — validation process and tooling
- [[concepts/pi-skill]] — Pi's implementation and discovery-path conventions
- [[concepts/hermes-skills-system]] — Hermes Agent's skill installation and tap system

## Sources

- [agentskills.io home page](raw/agentskills-io-home.md)
- [Agent Skills Specification](raw/agentskills-io-specification.md)
- https://agentskills.io/specification
