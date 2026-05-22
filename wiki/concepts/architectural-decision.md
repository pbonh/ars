---
title: "Architectural Decision"
type: concept
tags: [concept, architecture, documentation, adr]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/adr-github-home.html"]
confidence: high
---

## Definition

An **Architectural Decision (AD)** is a justified design choice that addresses a functional or non-functional requirement that is architecturally significant. It is the atomic unit of reasoning behind why a system is built one way rather than another.

## How It Works

When a team faces a choice between competing design options—database selection, communication protocol, deployment topology, API style—they evaluate the options against the system's requirements and constraints. The chosen option, together with the reasoning that led to it, constitutes the architectural decision. An AD is typically recorded in an [[concepts/architectural-decision-record|Architectural Decision Record (ADR)]].

## Key Parameters

- **Scope**: A single AD addresses one specific concern; it does not bundle unrelated choices.
- **Justification**: Must include the rationale, trade-offs, and consequences.
- **ASR linkage**: The decision should explicitly reference the [[concepts/architecturally-significant-requirement|Architecturally Significant Requirement(s)]] it satisfies.

## When To Use

- During the initial design phase of a system or component.
- When evaluating technology alternatives (e.g., message broker, cloud provider, persistence layer).
- Whenever a change could measurably affect quality attributes such as performance, security, maintainability, or scalability.

## Risks & Pitfalls

- **Bundling**: Combining multiple unrelated decisions into one record makes the rationale hard to follow and harder to reverse.
- **Missing context**: Recording the *what* without the *why* leaves future maintainers guessing.
- **Stale records**: Decisions evolve; without a living [[concepts/decision-log|decision log]], records become misinformation.

## Related Concepts

- [[concepts/architecturally-significant-requirement]] — the requirements that motivate ADs.
- [[concepts/architectural-decision-record]] — the document that captures an AD.
- [[concepts/decision-log]] — the aggregated collection of ADRs for a project.
- [[concepts/architectural-knowledge-management]] — the broader discipline.

## Sources

- [adr.github.io](https://adr.github.io) — Motivation and Definitions section.
- [Wikipedia — Architectural decision](https://en.wikipedia.org/wiki/Architectural_decision)
