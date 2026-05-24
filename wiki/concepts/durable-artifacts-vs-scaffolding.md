---
title: "Durable Artifacts vs. Scaffolding"
type: concept
tags: [concept, architecture, documentation, openspec, lifecycle]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/spec-driven-development-with-adr.md"]
confidence: medium
---

## Definition

**Durable artifacts vs. scaffolding** is a lifecycle distinction for the documents
a spec-driven change produces. *Durable* artifacts describe the system's current
state and are meant to persist indefinitely; *scaffolding* artifacts exist only to
get a change shipped and are archived (or discarded) once it has. The distinction
decides which documents future contributors can still read after a change closes.

## How It Works

In [[entities/openspec|OpenSpec]]'s default `spec-driven` schema a change emits
four documents:

- `specs.md` — **durable.** Merged into `openspec/specs/`; the standing
  description of behavior.
- `proposal.md`, `design.md`, `tasks.md` — **scaffolding.** Archived with the
  change folder once it ships.

The problem this concept names is that `design.md` — which holds the *rationale*
(alternatives, trade-offs, consequences) — is scaffolding, so the "why" is lost at
archival. The [[concepts/spec-driven-with-adr-schema|`spec-driven-with-adr`
schema]] fixes this by promoting that rationale into a durable artifact: an
[[concepts/architectural-decision-record|ADR]] stored outside the change folder.

The general rule: **rationale that future proposals will need must be captured in
a durable artifact, not left in scaffolding.** Specs and ADRs are durable;
proposals, designs, and task lists are scaffolding.

## Key Parameters

| Class | Examples | Fate after a change ships |
|-------|----------|---------------------------|
| Durable | specs, ADRs | persist as current state / decision history |
| Scaffolding | proposal, design, tasks | archived or discarded |

## When To Use

- When designing or choosing a [[concepts/custom-workflow-schema|workflow schema]]:
  classify each artifact as durable or scaffolding and verify every piece of
  must-keep knowledge lands in a durable one.
- When auditing why institutional knowledge keeps evaporating — usually it was
  recorded only in scaffolding that got archived.

## Risks & Pitfalls

- **Misclassification:** treating rationale-bearing design notes as scaffolding is
  exactly the failure mode that motivates this concept.
- **Durable bloat:** promoting *everything* to durable status produces an
  unmaintainable record; only current-state facts and significant decisions belong
  there.
- **Archival ≠ deletion, but it is invisibility:** archived scaffolding still
  exists, yet it no longer surfaces to future proposals, which is functionally the
  same as losing it.

## Related Concepts

- [[concepts/spec-driven-with-adr-schema]] — applies this distinction concretely
- [[concepts/spec-adr-dual-representation]] — what the two durable artifacts capture
- [[concepts/architectural-decision-record]] — the durable rationale artifact
- [[concepts/decision-log]] — the durable aggregate of ADRs
- [[concepts/architectural-knowledge-management]] — the discipline this serves
- [[concepts/delta-spec]] — the durable spec representation

## Sources

- [Architectural Decision Records with Spec-Driven Development using OpenSpec](https://intent-driven.dev/blog/2026/04/29/spec-driven-development-with-adr/) — Hari Krishnan (2026-04-29) (`raw/spec-driven-development-with-adr.md`)
