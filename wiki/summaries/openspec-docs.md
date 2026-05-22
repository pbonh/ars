---
title: "OpenSpec Documentation"
type: summary
tags: [summary, specification, ai-assisted-development, workflow]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/openspec-docs"]
confidence: high
---

## Overview

OpenSpec is a specification and planning framework for AI-assisted software development created by [[entities/fission-ai]]. It structures work into **specs** (the current source of truth) and **changes** (proposed modifications packaged as self-contained folders). The framework is designed around a [[concepts/fluid-workflow]] philosophy—actions, not rigid phases—so teams can iterate naturally rather than being locked into waterfall-style planning → implementation → archive gates.

The core innovation is the [[concepts/delta-spec]]: instead of rewriting full specifications for every change, OpenSpec describes modifications as ADDED, MODIFIED, or REMOVED requirements relative to existing specs. This makes the framework natively [[concepts/brownfield-first]]—it excels at evolving existing systems rather than only describing greenfield builds.

OpenSpec provides both a CLI (`openspec`) and AI-agent slash commands (`/opsx:*`) that work across 25+ coding assistants (Claude Code, Cursor, GitHub Copilot, Windsurf, Pi, and others). The newer [[concepts/opsx-workflow]] replaces a legacy phase-locked workflow with an [[concepts/artifact-dependency-graph]] model where artifacts (proposal, specs, design, tasks) form a DAG and dependencies are enablers rather than gates.

## Key Claims

- **Specs are behavior contracts, not implementation plans.** Good specs describe observable behavior, inputs, outputs, and error conditions. They avoid internal class names, library choices, or step-by-step execution details.
- **Delta specs make brownfield work first-class.** By expressing changes as deltas (ADDED/MODIFIED/REMOVED), multiple parallel changes can touch the same spec domain without conflicting, and reviewers see only what changed.
- **Schemas define customizable artifact workflows.** Teams can fork the default `spec-driven` schema (proposal → specs → design → tasks) or create entirely custom schemas with their own artifact types, templates, and dependency graphs.
- **Project context is actively injected.** The `openspec/config.yaml` file stores tech stack, conventions, and per-artifact rules that are prepended to every AI planning request—more reliable than passive documentation.
- **Workspaces enable cross-repo planning.** A coordination workspace links multiple repos or monorepo folders under stable names, letting a single planning surface span disparate codebases (currently in beta).
- **Progressive rigor avoids bureaucracy.** OpenSpec encourages "lite" specs (short behavior-first requirements, clear scope, a few acceptance checks) by default, escalating to "full" specs only for cross-team changes, API migrations, or security-sensitive work.

## Source Metadata

| Field | Value |
|-------|-------|
| Type | Open-source documentation (markdown) |
| Owner | Fission AI |
| URL | https://github.com/Fission-AI/OpenSpec/tree/main/docs |
| License | Not specified in docs (repository license applies) |
| Ingested | 2026-05-21 |

## Relevant Concepts

- [[concepts/delta-spec]] — Brownfield change representation
- [[concepts/fluid-workflow]] — Actions-not-phases philosophy
- [[concepts/artifact-dependency-graph]] — DAG-based artifact model
- [[concepts/progressive-rigor]] — Lite vs. full spec discipline
- [[concepts/opsx-workflow]] — OpenSpec's modern workflow brand
- [[concepts/coordination-workspace]] — Cross-repo planning
- [[concepts/custom-workflow-schema]] — User-defined artifact schemas
- [[concepts/brownfield-first]] — Existing-codebase-first approach

## Relevant Entities

- [[entities/openspec]] — The specification framework
- [[entities/fission-ai]] — Creator organization
