---
title: "OpenSpec"
type: entity
tags: [entity, tool, specification, ai-assisted-development, opensource]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/openspec-docs"]
confidence: high
---

## Overview

OpenSpec is an open-source specification and planning framework for AI-assisted software development. Created by [[entities/fission-ai]], it provides a CLI (`openspec`) and AI-agent slash commands (`/opsx:*`) that structure work into **specs** (behavior contracts describing current system state) and **changes** (proposed modifications expressed as delta specs).

OpenSpec is distributed via npm as `@fission-ai/openspec` and requires Node.js 20.19.0 or higher. It is also available via Nix (`nix run github:Fission-AI/OpenSpec`).

## Characteristics

| Attribute | Detail |
|-----------|--------|
| License | Open source (repository on GitHub) |
| Runtime | Node.js ≥ 20.19.0 |
| Package managers | npm, pnpm, yarn, bun, Nix |
| AI tool support | 25+ tools including Claude Code, Cursor, GitHub Copilot, Windsurf, Pi, Kimi, Trae, Continue, Gemini, RooCode, and others |
| Default schema | `spec-driven` (proposal → specs → design → tasks) |
| Workspace support | Beta (cross-repo planning) |

## Common Strategies

1. **Initialize in an existing repo:** `openspec init` scaffolds `openspec/specs/`, `openspec/changes/`, and `openspec/config.yaml`, plus AI-tool skill files.
2. **Propose a change:** `/opsx:propose add-feature` creates a change folder with proposal, delta specs, design, and tasks.
3. **Apply tasks:** `/opsx:apply` works through `tasks.md` checkboxes, writing code and marking completion.
4. **Archive when done:** `/opsx:archive` merges delta specs into main specs and moves the change to `openspec/changes/archive/`.
5. **Customize via schemas:** Teams fork `spec-driven` or create new schemas to match their own artifact workflows.
6. **Inject project context:** `openspec/config.yaml` stores tech stack and per-artifact rules that are prepended to every AI planning request.

## Sources

- OpenSpec Documentation (`raw/openspec-docs/`)
- GitHub repository: https://github.com/Fission-AI/OpenSpec
