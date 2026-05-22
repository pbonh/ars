---
title: "Decision Log"
type: concept
tags: [concept, architecture, documentation, adr]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/adr-github-home.html"]
confidence: high
---

## Definition

A **Decision Log** is the complete collection of [[concepts/architectural-decision-record|Architectural Decision Records (ADRs)]] created and maintained for a project. It serves as the persistent, searchable history of why the system looks and behaves the way it does.

## How It Works

Each time the team makes an architecturally significant choice, it records an ADR and appends it to the log. The log grows monotonically: new decisions are added, and obsolete decisions are *superseded* rather than deleted. This preserves the full evolutionary narrative of the architecture, allowing newcomers and auditors to trace the lineage of any design element.

In practice, a decision log is often a directory of Markdown files in version control (e.g., `docs/adr/NNNN-title.md`), with an index or README that lists entries by number, status, and date.

## Key Parameters

- **Monotonic growth**: Entries are never removed; status changes to "superseded" when replaced.
- **Chronological numbering**: Sequential numbering (e.g., `0001`, `0002`) preserves temporal order.
- **Linking**: Each entry should cross-reference related ADRs, requirements, and design documents.

## When To Use

- From the first week of a greenfield project, to capture foundational choices.
- During brownfield modernization, to document why legacy patterns are being replaced.
- In compliance-heavy domains where regulators or security auditors require decision traceability.

## Risks & Pitfalls

- **Log rot**: If the log is not kept current, it becomes a graveyard of outdated assumptions.
- **Poor discoverability**: A flat list of files with opaque titles makes the log hard to search.
- **Scope creep**: Mixing technical ADRs with product or business decisions can blur accountability.

## Related Concepts

- [[concepts/architectural-decision-record]] — the atomic unit of the log.
- [[concepts/architectural-decision]] — the decision each record captures.
- [[concepts/architectural-knowledge-management]] — the discipline that treats decision logs as first-class artifacts.

## Sources

- [adr.github.io](https://adr.github.io) — Motivation and Definitions section.
