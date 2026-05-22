---
title: "Architectural Decision Records (ADRs)"
type: summary
tags: [summary, architecture, documentation, adr]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/adr-github-home.html"]
confidence: high
---

## Overview

The [adr.github.io](https://adr.github.io) website is the homepage of the GitHub ADR organization, a community hub dedicated to Architectural Decision Records (ADRs). Its purpose is to motivate the practice of capturing architectural decisions, establish a shared vocabulary, strengthen tooling around ADRs, and curate public knowledge in the domain of Architectural Knowledge Management (AKM).

The site defines the core terms and their relationships: an [[concepts/architectural-decision|Architectural Decision (AD)]] addresses an [[concepts/architecturally-significant-requirement|Architecturally Significant Requirement (ASR)]]; an [[concepts/architectural-decision-record|Architectural Decision Record (ADR)]] captures a single decision and its rationale; and the collection of ADRs maintained in a project forms its [[concepts/decision-log|decision log]]. The site also links to templates, tools, and media coverage that demonstrate growing industry adoption.

## Key Claims

- ADRs help teams understand the *reasons* for a chosen architectural decision, along with its trade-offs and consequences.
- The practice sits within [[concepts/architectural-knowledge-management|Architectural Knowledge Management (AKM)]], but can be extended to any kind of design or project decision.
- The [[concepts/y-statement-format|Y-statement format]], suggested by Zdun et al., is a recommended lightweight template for recording decisions.
- Major industry frameworks—Azure Well-Architected, AWS Prescriptive Guidance, and the Open Practice Library—now recommend or feature ADRs.
- Michael Nygard’s 2011 blog post "Documenting Architecture Decisions" is widely credited with popularizing the ADR concept.

## Source Metadata

| Field | Value |
|-------|-------|
| Type | Website (Jekyll) |
| Owner | GitHub ADR organization |
| URL | https://adr.github.io/ |
| License | CC BY 4.0 (blog posts); theme under MIT-like terms |
| Ingested | 2026-05-21 |

## Relevant Concepts

- [[concepts/architectural-decision]]
- [[concepts/architecturally-significant-requirement]]
- [[concepts/architectural-decision-record]]
- [[concepts/decision-log]]
- [[concepts/architectural-knowledge-management]]
- [[concepts/y-statement-format]]
