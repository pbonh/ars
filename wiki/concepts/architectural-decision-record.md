---
title: "Architectural Decision Record"
type: concept
tags: [concept, architecture, documentation, adr]
created: 2026-05-21
updated: 2026-05-23
sources: ["raw/adr-github-home.html", "raw/spec-driven-development-with-adr.md"]
confidence: high
---

## Definition

An **Architectural Decision Record (ADR)** is a document that captures a single [[concepts/architectural-decision|Architectural Decision]] and its rationale. It explains the reasons for a chosen design path, the trade-offs considered, and the consequences accepted. The collection of ADRs maintained in a project constitutes its [[concepts/decision-log|decision log]].

## How It Works

When a team makes a design choice that addresses an [[concepts/architecturally-significant-requirement|Architecturally Significant Requirement]], they write an ADR. The record typically includes the context (forces and constraints), the decision (chosen option), the rationale (why this option over alternatives), and the consequences (both positive and negative). ADRs are stored in version control, often in a dedicated directory, and are assigned sequential identifiers for stable referencing.

**Where ADRs live matters.** In spec-driven workflows the storage location
decides whether an ADR is a [[concepts/durable-artifacts-vs-scaffolding|durable
artifact or scaffolding]]. The [[concepts/spec-driven-with-adr-schema|
`spec-driven-with-adr`]] OpenSpec schema makes this explicit: ADRs are written to
the repository's top-level `adr/` folder, *outside* the per-change `openspec/`
folder, so they survive when the change is archived. Kept durable alongside the
specs, they give a [[concepts/spec-adr-dual-representation|dual representation]]
of the system — specs say what it does now, ADRs say how and why — letting a
future proposal reuse a decision instead of rediscovering it.

## Key Parameters

- **One decision per record**: Each ADR addresses exactly one architectural choice; bundling unrelated decisions is discouraged.
- **Immutable history**: Once accepted, an ADR is not edited in place; it is superseded by a newer ADR if the decision changes.
- **Status lifecycle**: Common statuses include *proposed*, *accepted*, *deprecated*, *superseded*.
- **Lightweight format**: Many teams use Markdown with a simple template (e.g., the [[concepts/y-statement-format|Y-statement format]]).

## When To Use

- Whenever a design choice has long-term structural implications for the system.
- When multiple viable alternatives exist and the team must explain why one was selected.
- During handoffs, onboarding, or audits where the "why" behind the architecture must be discoverable.

## Risks & Pitfalls

- **Writing too late**: Decisions captured from memory are often incomplete or rationalized post-hoc.
- **Over-formatting**: Elaborate templates can create friction and cause teams to abandon the practice.
- **Orphan records**: ADRs that are not linked to requirements, code, or other ADRs become hard to discover and trust.

## Related Concepts

- [[concepts/architectural-decision]] — the decision an ADR captures.
- [[concepts/architecturally-significant-requirement]] — the requirement motivating the decision.
- [[concepts/decision-log]] — the aggregate collection of ADRs.
- [[concepts/architectural-knowledge-management]] — the discipline that treats ADRs as first-class artifacts.
- [[concepts/y-statement-format]] — a concise template for expressing decision rationale.
- [[concepts/spec-driven-with-adr-schema]] — an OpenSpec schema that produces durable ADRs outside the change folder.
- [[concepts/durable-artifacts-vs-scaffolding]] — why ADR storage location determines its longevity.
- [[concepts/spec-adr-dual-representation]] — how ADRs and specs together describe a system.

## Sources

- [adr.github.io](https://adr.github.io) — Motivation and Definitions section.
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions.html) — Michael Nygard (2011)
- [Architectural Decision Records with Spec-Driven Development using OpenSpec](https://intent-driven.dev/blog/2026/04/29/spec-driven-development-with-adr/) — Hari Krishnan (2026-04-29) (`raw/spec-driven-development-with-adr.md`)
