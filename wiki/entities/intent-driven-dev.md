---
title: "Intent-Driven Dev"
type: entity
tags: [entity, organization, openspec, adr]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/spec-driven-development-with-adr.md", "raw/openspec-schemas/"]
confidence: medium
---

## Overview

**Intent-Driven Dev** is the project/organization behind the
[intent-driven.dev](https://intent-driven.dev) website and the matching
`intent-driven-dev` GitHub organization. It promotes "intent-driven development" —
the practice of keeping the reasoning behind code close to the code so future
contributors can read the *why*. In practice it publishes writing (a blog,
including [[entities/hari-krishnan|Hari Krishnan]]'s post on spec-driven
development with ADRs) and tooling that extends [[entities/openspec|OpenSpec]],
most notably the [[entities/openspec-schemas|openspec-schemas]] repository.

## Characteristics

| Attribute | Detail |
|-----------|--------|
| Website | https://intent-driven.dev |
| GitHub org | https://github.com/intent-driven-dev |
| Flagship repo | `openspec-schemas` (MIT-licensed custom OpenSpec schemas) |
| Related repo | `intent-driven-template` (ships ADR authoring skills) |
| Stance | Vendor-adjacent to OpenSpec/Fission AI; customizes rather than forks |

## Common Strategies

- **Customize, don't fork OpenSpec.** Ships its ideas as drop-in
  [[concepts/custom-workflow-schema|custom workflow schemas]] (e.g.
  [[concepts/spec-driven-with-adr-schema]]) rather than maintaining a competing
  framework.
- **Pair writing with tooling.** A blog post explains the motivation
  (durable ADRs) and a repository provides the runnable schema that implements it.
- **Externalize ADR templates into skills.** Keeps the ADR format in a separate
  `intent-driven-template` skills repo so multiple schemas can share it.

## Sources

- [intent-driven.dev blog](https://intent-driven.dev/blog/2026/04/29/spec-driven-development-with-adr/) (`raw/spec-driven-development-with-adr.md`)
- [github.com/intent-driven-dev/openspec-schemas](https://github.com/intent-driven-dev/openspec-schemas) (`raw/openspec-schemas/`)
