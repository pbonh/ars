---
title: "Agent Skills Standard"
type: entity
tags: [entity, standard, specification, agent-skills]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/pi-repo/packages/coding-agent/docs/skills.md"]
confidence: high
---

## Overview

Agent Skills (agentskills.io) is an open specification for packaging reusable agent capabilities. It defines a directory structure, required `SKILL.md` frontmatter, and XML-based integration into system prompts. Pi implements this standard, remaining lenient about minor violations such as skill names not matching parent directories.

## Characteristics

- **Specification**: https://agentskills.io/specification
- **Required file**: `SKILL.md` with `name` and `description` frontmatter
- **Integration**: Skills are advertised to models via XML in the system prompt
- **Discovery**: Recursive directory scanning for `SKILL.md` files
- **Ecosystem**: Shared skill repositories exist for Claude Code, OpenAI Codex, and Pi

## Common Strategies

- Write skills with specific descriptions so the model knows when to load them
- Store shared skills in `~/.agents/skills/` for cross-tool compatibility
- Reference the specification when building skills intended for multiple agent harnesses
- Use relative paths inside skill directories for scripts and assets

## Sources

- [Pi Skills Documentation](raw/pi-repo/packages/coding-agent/docs/skills.md)
- [Agent Skills Specification](https://agentskills.io/specification)
