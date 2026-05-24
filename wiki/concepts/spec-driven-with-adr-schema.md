---
title: "spec-driven-with-adr Schema"
type: concept
tags: [concept, openspec, adr, schema, workflow]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/spec-driven-development-with-adr.md", "raw/openspec-schemas/"]
confidence: medium
---

## Definition

`spec-driven-with-adr` is a [[concepts/custom-workflow-schema|custom OpenSpec
workflow schema]] that takes the standard proposal-to-tasks flow and inserts a
dedicated **Architecture Decision Record** stage whose output is *durable* — it
persists outside the change folder rather than being archived with it. Its
distinguishing property, in the author's words, is that "ADRs live outside the
change, outside the `openspec/` folder."

## How It Works

The schema defines a five-artifact dependency graph:

```text
proposal ──► specs ──► design ──► adr ──► tasks
```

The first four behave like the default `spec-driven` schema, but `design` now
feeds an `adr` stage that distills the design's significant decisions into one or
more [[concepts/architectural-decision-record|ADRs]]. Crucially:

- **ADR storage:** ADR files are written to the **target repository's top-level
  `adr/` folder**, not inside the `openspec/changes/<id>/` change folder. When the
  change is archived, the ADRs stay where they are.
- **Immutability & supersession:** "Accepted ADRs are immutable. If a future
  decision changes a prior ADR, create a new ADR that supersedes the old one and
  leave the original file unchanged." This is the same supersession discipline
  used across the existing [[concepts/decision-log|decision log]] practice.
- **Template delegation:** the schema does not embed an ADR template; it defers to
  external ADR skills (the `intent-driven-template` repo's
  `.agents/skills/architectural-decision-records` folder) for the format.

The payoff is the [[concepts/spec-adr-dual-representation|dual representation]]:
after a change ships, `specs/` says *what the system does today* and the `adr/`
folder says *how and why it got that way*. A future proposal can read the ADRs and
reuse a prior decision instead of rediscovering or contradicting it.

## Key Parameters

| Field | Value |
|-------|-------|
| Artifacts | `proposal → specs → design → adr → tasks` |
| Durable outputs | `specs.md` (into `openspec/specs/`) and ADRs (into top-level `adr/`) |
| Scaffolding outputs | `proposal.md`, `design.md`, `tasks.md` (archived) |
| ADR location | repository root `adr/`, outside `openspec/` |
| ADR lifecycle | immutable once accepted; superseded, never edited |
| Distribution | the [[entities/openspec-schemas]] repo (MIT) |

## When To Use

- When a change involves an [[concepts/architecturally-significant-requirement|
  architecturally significant decision]] whose rationale future teams will need
  (storage engine, framework choice, protocol, security boundary).
- When you already use OpenSpec's default `spec-driven` schema and find the
  archived `design.md` reasoning keeps getting lost.
- When you want decision history to be discoverable from the codebase root rather
  than mined out of archived change folders.

Avoid (or downgrade) when the change is trivial, fully reversible, or has no real
alternatives worth recording — adding an ADR stage to throwaway work is friction,
the same over-formatting pitfall noted on
[[concepts/architectural-decision-record]].

## Risks & Pitfalls

- **Single-witness provenance:** this schema is documented by one blog post and
  one repository README (both fetched via summarizer); field names and exact
  behavior should be confirmed against the live `schema.yaml`.
- **Two sources of truth to keep in sync:** specs and ADRs can drift if a later
  change updates behavior but skips writing the superseding ADR.
- **Top-level `adr/` collisions:** repositories that already keep ADRs elsewhere
  (e.g. `docs/adr/`) must reconcile locations or risk a split decision log.
- **External template dependency:** because the ADR template lives in a separate
  skills repo, the schema's output format depends on a pinned external version.

## Related Concepts

- [[concepts/custom-workflow-schema]] — the OpenSpec mechanism this is built on
- [[concepts/durable-artifacts-vs-scaffolding]] — the lifecycle principle it encodes
- [[concepts/spec-adr-dual-representation]] — what specs vs ADRs each capture
- [[concepts/architectural-decision-record]] — the durable artifact it produces
- [[concepts/decision-log]] — the aggregate the `adr/` folder becomes
- [[concepts/opsx-workflow]] — the workflow engine that runs the schema
- [[concepts/delta-spec]] — the spec representation it preserves

## Sources

- [Architectural Decision Records with Spec-Driven Development using OpenSpec](https://intent-driven.dev/blog/2026/04/29/spec-driven-development-with-adr/) — Hari Krishnan (2026-04-29) (`raw/spec-driven-development-with-adr.md`)
- [openspec-schemas / spec-driven-with-adr](https://github.com/intent-driven-dev/openspec-schemas/tree/main/openspec/schemas/spec-driven-with-adr) (`raw/openspec-schemas/spec-driven-with-adr.md`)
