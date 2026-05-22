---
title: "Architecturally Significant Requirement"
type: concept
tags: [concept, architecture, requirements, adr]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/adr-github-home.html"]
confidence: high
---

## Definition

An **Architecturally Significant Requirement (ASR)** is a requirement that has a measurable effect on the architecture and quality of a software or hardware system. It is the trigger that justifies the creation of an [[concepts/architectural-decision|Architectural Decision]] and its accompanying record.

## How It Works

ASRs emerge from business goals, quality-attribute scenarios, constraints, or stakeholder concerns. They are distinguished from ordinary functional requirements by their impact on structural or cross-cutting system qualities. For example, a requirement to support 10,000 concurrent users is an ASR because it drives choices around concurrency models, caching, and scaling strategy. Each ASR that cannot be satisfied by off-the-shelf defaults should be linked to one or more explicit architectural decisions.

## Key Parameters

- **Measurability**: An ASR should be expressed in a way that can be tested or verified (e.g., latency SLAs, throughput targets, security compliance levels).
- **Cross-cutting impact**: It affects multiple components, layers, or interfaces.
- **Stability**: ASRs tend to change more slowly than implementation details, making them a durable anchor for decision rationale.

## When To Use

- At the start of a project or major iteration, when eliciting and prioritizing requirements.
- During architecture reviews, to filter which requirements deserve explicit decision documentation.
- When tracing decisions back to business or technical drivers during audits or onboarding.

## Risks & Pitfalls

- **Treating all requirements as ASRs**: Over-documenting trivial choices dilutes the decision log and creates maintenance burden.
- **Vague phrasing**: An ASR like "the system should be fast" provides no objective basis for decision evaluation.
- **Decoupling from decisions**: ASRs tracked separately from ADRs decay into orphan statements with no actionable history.

## Related Concepts

- [[concepts/architectural-decision]] — the design choice that addresses an ASR.
- [[concepts/architectural-decision-record]] — where the linkage between ASR and decision is documented.
- [[concepts/decision-log]] — the searchable history that connects requirements to outcomes.

## Sources

- [adr.github.io](https://adr.github.io) — Motivation and Definitions section.
- [Wikipedia — Architecturally significant requirements](https://en.wikipedia.org/wiki/Architecturally_significant_requirements)
