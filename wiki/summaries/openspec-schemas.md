---
title: "OpenSpec Schemas Repository"
type: summary
tags: [summary, openspec, schema, workflow]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/openspec-schemas/"]
confidence: medium
---

## Overview

`intent-driven-dev/openspec-schemas` is a public, MIT-licensed GitHub repository
maintained by the [[entities/intent-driven-dev|intent-driven-dev]] organization.
It is a collection of [[concepts/custom-workflow-schema|custom workflow schemas]]
that extend [[entities/openspec|OpenSpec]] beyond its built-in default
`spec-driven` schema. Each schema adapts OpenSpec's artifact set, templates, and
dependency graph to a different work style or delivery context.

A schema is installed by copying its folder out of `openspec/schemas/` into a
project-local or user-level schemas directory, activating it in
`openspec/config.yaml`, and running `openspec schema validate`. The repository's
guidance tells AI agents to confirm OpenSpec (version ≥ 1.0.0) is installed before
proceeding.

The directory currently ships six schemas. The one this knowledge base ingested
in detail is [[concepts/spec-driven-with-adr-schema|`spec-driven-with-adr`]],
which adds a durable Architecture Decision Record stage to the standard
proposal-to-tasks flow. The remaining five (`minimalist`, `event-driven`,
`behaviour-driven`, `intent-driven`, `linearized`) are catalogued at entity level
but not yet given full concept pages, because the fetched source provided only
one-line purposes for each.

## Key Claims

- **OpenSpec is customizable via swappable schemas.** A schema is a versioned,
  shareable definition of the artifact DAG and templates — see
  [[concepts/custom-workflow-schema]] and [[concepts/opsx-workflow]].
- **One schema per work style.** The repo packages six: a fast `minimalist`
  path, `event-driven` (Event Storming / AsyncAPI), `behaviour-driven`
  (GIVEN/WHEN/THEN), `intent-driven` (full proposal→specs→design→adr→tasks),
  `linearized` (Linear-tracker integration), and
  [[concepts/spec-driven-with-adr-schema|`spec-driven-with-adr`]].
- **Schemas are distributed, not built into OpenSpec.** They live in a separate
  community repo with its own MIT license and release cadence, which is the
  schema-drift trade-off already noted on [[concepts/custom-workflow-schema]].

## Source Metadata

| Field | Value |
|-------|-------|
| Type | GitHub repository (fetched directory + README extraction) |
| Owner | intent-driven-dev |
| URL | https://github.com/intent-driven-dev/openspec-schemas/tree/main/openspec/schemas |
| License | MIT |
| Ingested | 2026-05-23 |

## Relevant Concepts

- [[concepts/spec-driven-with-adr-schema]] — the schema ingested in full
- [[concepts/custom-workflow-schema]] — the OpenSpec feature these populate
- [[concepts/opsx-workflow]] — the engine that consumes schemas
- [[concepts/durable-artifacts-vs-scaffolding]] — the principle behind the ADR schema

## Relevant Entities

- [[entities/openspec-schemas]] — the repository itself
- [[entities/intent-driven-dev]] — maintaining organization
- [[entities/openspec]] — the framework extended
