---
title: "Architectural Knowledge Management"
type: concept
tags: [concept, architecture, knowledge-management]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/adr-github-home.html"]
confidence: high
---

## Definition

**Architectural Knowledge Management (AKM)** is the discipline of capturing, organizing, and sharing the knowledge embedded in a system's architecture. It encompasses rationale, design patterns, constraints, and the evolution of structural decisions over time.

## How It Works

AKM practices include maintaining a [[concepts/decision-log|decision log]] of [[concepts/architectural-decision-record|ADRs]], recording design patterns and their contexts, and creating living documentation that stays synchronized with code. The goal is to reduce the "tribal knowledge" risk—where critical reasoning exists only in the heads of individual engineers—and to make architectural rationale an explicit, reusable asset.

## Key Parameters

- **Explicitness**: Knowledge must be written down, not implied by code or inferred from commit history.
- **Accessibility**: Stored where developers already work (e.g., alongside code in version control).
- **Liveness**: Updated as the architecture changes; outdated knowledge is worse than no knowledge.

## When To Use

- In growing teams where the original architects may not be available to answer questions.
- When onboarding new engineers who need to understand *why* things are built a certain way.
- During due diligence, audits, or handoffs where architectural reasoning must be demonstrable.

## Risks & Pitfalls

- **Overhead**: Excessive ceremony around knowledge capture can stall development.
- **Shelfware**: Documentation that is written once and never read consumes effort without delivering value.
- **Inconsistency**: Multiple, uncoordinated knowledge stores (wikis, Confluence, READMEs, ADRs) create fragmentation.

## Related Concepts

- [[concepts/architectural-decision-record]] — the primary concrete artifact in AKM.
- [[concepts/decision-log]] — the organized collection of ADRs.
- [[concepts/architectural-decision]] — the knowledge unit each record preserves.

## Sources

- [adr.github.io](https://adr.github.io) — Motivation and Definitions section.
- [OST — Architectural Knowledge Management (AKM)](https://www.ost.ch/en/research-and-consulting-services/computer-science/ifs-institute-for-software-new/cloud-application-lab/architectural-knowledge-management-akm)
