---
title: "Architectural Decision Records with Spec-Driven Development using OpenSpec"
type: summary
tags: [summary, architecture, adr, openspec, spec-driven-development]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/spec-driven-development-with-adr.md"]
confidence: medium
---

## Overview

This blog post by [[entities/hari-krishnan|Hari Krishnan]], published on the
[[entities/intent-driven-dev|intent-driven.dev]] site, argues that
[[entities/openspec|OpenSpec]]'s default `spec-driven` schema loses architectural
rationale over time. That schema produces four artifacts per change —
`proposal.md`, `specs.md`, `design.md`, and `tasks.md` — but only `specs.md`
survives in `openspec/specs/` after a change is archived. The reasoning captured
in `design.md` (alternatives, trade-offs, consequences) is buried in the archive,
so future teams must *rediscover* why a decision was made instead of building on
it.

The proposed fix is a custom OpenSpec schema, the
[[concepts/spec-driven-with-adr-schema|`spec-driven-with-adr`]] schema, whose
defining property is that **ADRs live outside the change folder and outside the
`openspec/` directory entirely** — at the repository's top-level `adr/` folder.
Because they sit outside the archived change, they remain permanently visible and
queryable by future proposals.

The post frames two conceptual distinctions to justify this. First,
[[concepts/durable-artifacts-vs-scaffolding|durable artifacts vs. scaffolding]]:
specs and ADRs represent current state and persist, while proposals, designs, and
tasks are temporary scaffolding archived after shipping. Second,
[[concepts/spec-adr-dual-representation|the spec/ADR dual representation]]: specs
capture *what the system does today*, ADRs capture *how and why it is built that
way*.

A storage example anchors the argument: an early choice of PostgreSQL over
DynamoDB. Under the default schema that rationale vanishes after archival; under
`spec-driven-with-adr`, a later full-text-search proposal immediately surfaces the
PostgreSQL foundation, prompting the team to evaluate native options (`pg_trgm`,
`tsvector`) rather than re-litigating storage or bolting on contradictory
infrastructure. The piece closes on intent-driven development's guiding
principle: "keep the reasoning close to the code so future contributors can read
the why."

## Key Claims

- **Archived design reasoning is effectively lost.** Only `specs.md` persists
  after archival; `design.md` rationale becomes inaccessible to future
  proposals. See [[concepts/durable-artifacts-vs-scaffolding]].
- **ADRs should outlive the change that produced them.** The
  [[concepts/spec-driven-with-adr-schema]] stores ADRs in a top-level `adr/`
  folder outside `openspec/`, so they persist as durable architecture knowledge.
- **Specs and ADRs answer different questions.** Specs describe current behavior
  ("what"); ADRs describe rationale ("how and why"). Together they give a
  [[concepts/spec-adr-dual-representation|dual representation]] of the
  architecture. This complements existing
  [[concepts/architectural-decision-record|ADR]] and
  [[concepts/decision-log|decision-log]] practice.
- **Persisting rationale prevents costly rediscovery.** The PostgreSQL/DynamoDB
  example shows future proposals reusing an accepted decision instead of
  re-debating or contradicting it — a concrete instance of
  [[concepts/architectural-knowledge-management|architectural knowledge
  management]].
- **This is a customization of OpenSpec, not a fork.** `spec-driven-with-adr` is
  one [[concepts/custom-workflow-schema|custom workflow schema]] among several in
  the [[entities/openspec-schemas|openspec-schemas]] repository.

## Source Metadata

| Field | Value |
|-------|-------|
| Type | Blog post (HTML; fetched markdown extraction) |
| Author | Hari Krishnan |
| Owner | intent-driven.dev / intent-driven-dev |
| URL | https://intent-driven.dev/blog/2026/04/29/spec-driven-development-with-adr/ |
| Published | 2026-04-29 |
| License | Not stated |
| Ingested | 2026-05-23 |

## Relevant Concepts

- [[concepts/spec-driven-with-adr-schema]] — the schema the post introduces
- [[concepts/durable-artifacts-vs-scaffolding]] — persistence distinction
- [[concepts/spec-adr-dual-representation]] — what-vs-why division of labor
- [[concepts/custom-workflow-schema]] — the OpenSpec mechanism this builds on
- [[concepts/architectural-decision-record]] — the artifact made durable
- [[concepts/decision-log]] — the aggregate the durable ADRs form
- [[concepts/architectural-knowledge-management]] — the discipline served

## Relevant Entities

- [[entities/hari-krishnan]] — author
- [[entities/intent-driven-dev]] — publisher / project
- [[entities/openspec-schemas]] — repository hosting the schema
- [[entities/openspec]] — the framework being extended
