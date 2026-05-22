---
title: "skills-ref"
type: entity
tags: [entity, tool, cli, agent-skills, validation]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/agentskills-io-specification.md"]
confidence: high
---

## Overview

`skills-ref` is the reference validation CLI for the Agent Skills standard, maintained in the agentskills/agentskills GitHub repository. It checks that a skill folder follows the specification: valid `SKILL.md` frontmatter, correct naming conventions, and proper directory layout.

## Characteristics

- **Type**: Command-line tool (reference implementation)
- **Repository**: https://github.com/agentskills/agentskills/tree/main/skills-ref
- **Scope**: Static validation of frontmatter YAML and directory structure
- **Limitations**: Does not execute or lint scripts; does not verify semantic correctness of skill instructions

## Common Strategies

- Run `skills-ref validate ./my-skill` before committing or publishing.
- Integrate into CI pipelines to reject PRs with malformed skills.
- Use in pre-commit hooks to catch frontmatter typos immediately.
- Pair with manual script review and sandbox testing for executable skills.

## Sources

- [Agent Skills Specification](raw/agentskills-io-specification.md)
- https://github.com/agentskills/agentskills/tree/main/skills-ref
