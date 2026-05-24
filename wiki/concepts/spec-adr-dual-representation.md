---
title: "Spec/ADR Dual Representation of Architecture"
type: concept
tags: [concept, architecture, documentation, adr]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/spec-driven-development-with-adr.md"]
confidence: medium
---

## Definition

**Spec/ADR dual representation** is the idea that a system's living documentation
needs two complementary artifacts that answer different questions:

- **Specs** capture *what the system does today* — observable behavior, the
  current contract.
- **ADRs** capture *how and why the system is built that way* — the decisions and
  rationale behind that behavior.

Neither subsumes the other: a spec without its ADRs tells you the rules but not
why they hold; ADRs without specs tell you the reasoning but not the present
state.

## How It Works

A spec is a present-tense behavior contract (see [[concepts/delta-spec]] for how
OpenSpec represents one). It deliberately omits rationale — it says PostgreSQL is
the store, not why PostgreSQL was chosen over DynamoDB. The "why" is the job of an
[[concepts/architectural-decision-record|ADR]].

When both are kept durable (see
[[concepts/durable-artifacts-vs-scaffolding]]), a future contributor reading the
codebase gets a complete picture: the specs say what must be true now, and the
ADRs explain the forces that made it so. This is what lets a later proposal *build
on* a decision — e.g. seeing the PostgreSQL ADR and reaching for `pg_trgm`/
`tsvector` for full-text search — rather than re-debating or contradicting it.

The [[concepts/spec-driven-with-adr-schema|`spec-driven-with-adr` schema]]
operationalizes this duality by producing both as persistent outputs.

## Key Parameters

| Artifact | Question answered | Tense | Changes when |
|----------|-------------------|-------|--------------|
| Spec | What does it do? | present | behavior changes |
| ADR | How & why is it built this way? | historical / append-only | a new decision supersedes an old one |

## When To Use

- When deciding what documentation a change must leave behind: ensure *both* the
  "what" and the "why" are written down, in the right artifact.
- When onboarding or auditing: read specs for current behavior, ADRs for the
  reasoning, and treat a gap in either as a documentation defect.

## Risks & Pitfalls

- **Conflating the two:** stuffing rationale into specs makes them brittle and
  noisy; stuffing current-state facts into ADRs makes the decision log a
  moving target instead of an append-only history.
- **Drift between them:** if behavior changes but no superseding ADR is written,
  the "why" silently goes stale even though the spec is up to date.

## Related Concepts

- [[concepts/spec-driven-with-adr-schema]] — the schema that produces both durably
- [[concepts/durable-artifacts-vs-scaffolding]] — why both must persist
- [[concepts/architectural-decision-record]] — the "why/how" artifact
- [[concepts/delta-spec]] — the "what" artifact in OpenSpec
- [[concepts/decision-log]] — the accumulated ADR history
- [[concepts/architectural-knowledge-management]] — the broader discipline

## Sources

- [Architectural Decision Records with Spec-Driven Development using OpenSpec](https://intent-driven.dev/blog/2026/04/29/spec-driven-development-with-adr/) — Hari Krishnan (2026-04-29) (`raw/spec-driven-development-with-adr.md`)
