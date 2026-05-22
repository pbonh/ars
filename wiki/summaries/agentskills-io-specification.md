---
title: "Agent Skills Specification"
type: summary
tags: [summary, agent-skills, specification]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/agentskills-io-specification.md"]
confidence: high
---

## Overview

The Agent Skills Specification is the formal definition of the folder-based format that agents use to discover, load, and execute specialized skills. It lives in the agentskills/agentskills GitHub repository and covers the complete contract: directory layout, `SKILL.md` frontmatter schema with per-field constraints, body-content guidelines, optional subdirectories (`scripts/`, `references/`, `assets/`), progressive-disclosure token budgets, file-reference conventions, and a validation CLI.

The specification is normative: any agent or tool that claims compatibility must honor the frontmatter rules, the directory structure, and the progressive-disclosure loading model. Optional fields (license, compatibility, metadata, allowed-tools) give authors room for extension without breaking interoperability.

## Key Claims

- The [[concepts/agent-skills-format|Agent Skills format]] mandates a directory named after the skill, containing at minimum a `SKILL.md` file, plus optional `scripts/`, `references/`, and `assets/` subdirectories.
- The `SKILL.md` frontmatter defines six fields: `name` (required, 1–64 lowercase alphanumerics + hyphens, must match directory name), `description` (required, 1–1024 chars), `license` (optional), `compatibility` (optional, 1–500 chars), `metadata` (optional key-value map), and `allowed-tools` (optional, experimental, space-separated).
- The Markdown body has no format restrictions; recommended content includes step-by-step instructions, input/output examples, and edge cases.
- [[concepts/progressive-disclosure|Progressive disclosure]] follows concrete token budgets: metadata is ~100 tokens, the full `SKILL.md` body should stay under 5000 tokens (~500 lines), and resource files load only when referenced.
- File references must use relative paths from the skill root and stay one level deep; deeply nested reference chains are discouraged.
- [[concepts/skill-validation|Skill validation]] is supported by the [[entities/skills-ref|skills-ref]] CLI, which checks frontmatter validity and naming conventions.

## Source Metadata

- **Type**: Formal specification document (Markdown/MDX)
- **Owner**: agentskills/agentskills open-source project
- **URL**: https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx
- **License**: Same as the agentskills/agentskills repository
- **Ingested on**: 2026-05-21

## Relevant Concepts

- [[concepts/agent-skills-format]] — extended with frontmatter schema and directory details
- [[concepts/progressive-disclosure]] — extended with token budgets and file-size guidance
- [[concepts/skill-validation]] — new concept for validation tooling
- [[concepts/pi-skill]] — Pi's implementation of the standard
- [[concepts/hermes-skills-system]] — Hermes Agent's implementation

## Relevant Entities

- [[entities/skills-ref]] — CLI validation tool for Agent Skills
- [[entities/agentskills-io]] — the standard body and website
