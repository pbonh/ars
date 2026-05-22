---
title: "Skill Validation"
type: concept
tags: [concept, agent-skills, validation, tooling, quality]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/agentskills-io-specification.md"]
confidence: high
---

## Definition

Skill validation is the process of checking that an Agent Skills folder conforms to the formal specification: correct directory layout, valid `SKILL.md` frontmatter, naming-convention compliance, and sensible file references. Validation catches structural errors before an agent attempts to load or execute a skill.

## How It Works

The agentskills/agentskills project distributes a reference validation library called `skills-ref`. Running it against a skill directory performs static checks:

```bash
skills-ref validate ./my-skill
```

Checks typically include:
- Presence and readability of `SKILL.md`
- Frontmatter YAML syntax
- `name` field constraints (length, character set, no leading/trailing/consecutive hyphens, match with directory name)
- `description` field constraints (non-empty, max 1024 characters)
- Optional field constraints (`compatibility` max 500 chars, etc.)

## Key Parameters

- **Tool**: `skills-ref` CLI from the agentskills/agentskills repository
- **Scope**: Static analysis of folder structure and frontmatter; does not execute scripts
- **Integration point**: CI pipelines, pre-commit hooks, and skill publishing workflows

## When To Use

Validate a skill:
- Before committing it to version control.
- Before publishing to a shared tap or registry.
- After editing frontmatter or renaming a skill directory.
- In CI to prevent broken skills from reaching production agents.

## Risks & Pitfalls

- `skills-ref` checks structure, not semantics: a valid frontmatter does not guarantee the skill instructions are correct or safe.
- The `allowed-tools` field is experimental and may not be validated uniformly across implementations.
- Validation does not sandbox or lint executable scripts; always review `scripts/` contents independently.

## Related Concepts

- [[concepts/agent-skills-format]] — the specification that defines what validation checks
- [[concepts/progressive-disclosure]] — loading model that depends on correct file layout

## Sources

- [Agent Skills Specification](raw/agentskills-io-specification.md)
- https://github.com/agentskills/agentskills/tree/main/skills-ref
