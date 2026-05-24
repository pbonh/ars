---
title: "openspec-schemas"
type: entity
tags: [entity, repository, openspec, schema]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/openspec-schemas/"]
confidence: medium
---

## Overview

**openspec-schemas** is a public, MIT-licensed GitHub repository
(`intent-driven-dev/openspec-schemas`) maintained by
[[entities/intent-driven-dev|Intent-Driven Dev]]. It is a catalog of
[[concepts/custom-workflow-schema|custom workflow schemas]] for
[[entities/openspec|OpenSpec]] — each one a drop-in alternative to OpenSpec's
built-in default `spec-driven` schema, adapting the artifact set, templates, and
dependency graph to a particular work style.

## Characteristics

| Attribute | Detail |
|-----------|--------|
| Full name | `intent-driven-dev/openspec-schemas` |
| License | MIT |
| Visibility | Public |
| Layout | Schemas under `openspec/schemas/<name>/` (each with `schema.yaml`, `README.md`, `templates/`) |
| Schemas | `minimalist`, `event-driven`, `behaviour-driven`, `intent-driven`, `linearized`, `spec-driven-with-adr` |
| Install | copy schema folder → activate in `openspec/config.yaml` → `openspec schema validate` |
| Prerequisite | OpenSpec ≥ 1.0.0 |

## Common Strategies

- **Pick a schema by work style.** `minimalist` for a fast spec→execution path,
  `event-driven` for Event-Storming/AsyncAPI systems, `behaviour-driven` for
  Gherkin GIVEN/WHEN/THEN, `intent-driven` for the full
  proposal→specs→design→adr→tasks flow, `linearized` for Linear-tracker
  integration, and [[concepts/spec-driven-with-adr-schema|`spec-driven-with-adr`]]
  to add durable ADRs to the standard flow.
- **Copy and activate, don't vendor the whole repo.** Teams lift the single
  schema folder they want into their project and pin it.
- **Validate after install.** `openspec schema validate` catches a malformed or
  cyclic artifact graph before the schema is used.

## Sources

- [openspec-schemas directory](https://github.com/intent-driven-dev/openspec-schemas/tree/main/openspec/schemas) (`raw/openspec-schemas/index.md`)
- [spec-driven-with-adr schema](https://github.com/intent-driven-dev/openspec-schemas/tree/main/openspec/schemas/spec-driven-with-adr) (`raw/openspec-schemas/spec-driven-with-adr.md`)
