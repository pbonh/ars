---
title: "Y-Statement Format"
type: concept
tags: [concept, architecture, documentation, adr]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/adr-github-home.html"]
confidence: medium
---

## Definition

The **Y-statement format** is a concise, structured template for documenting architectural decisions. It organizes the essential elements of a decision into a single sentence or short paragraph that reads like a natural-language argument.

## How It Works

The Y-statement captures the decision in the form:

> In the context of `<forces>`, facing `<concern>`, we decided for `<option>` and against `<alternatives>` to achieve `<benefits>`, accepting `<drawbacks>`.

This format forces the author to articulate forces, chosen option, rejected alternatives, expected benefits, and accepted trade-offs in one cohesive statement. It is one of several templates recommended by the adr.github.io community, derived from the *Sustainable Architectural Decisions* guidelines by Zdun et al.

## Key Parameters

- **Forces**: The constraints, requirements, or pressures that shape the decision space.
- **Concern**: The specific problem or quality attribute being addressed.
- **Option / Alternatives**: The chosen path and at least one credible rejected alternative.
- **Benefits / Drawbacks**: The positive outcomes sought and the negative consequences accepted.

## When To Use

- When teams want a lightweight, low-friction ADR format that can be read in seconds.
- In agile or iterative environments where heavy templates slow down decision capture.
- As the opening paragraph of a longer ADR, providing an executive summary before deeper analysis.

## Risks & Pitfalls

- **Oversimplification**: Complex decisions with many stakeholders may not fit neatly into a single Y-statement.
- **Vague forces**: Using hand-wavy force descriptions ("performance concerns") weakens the rationale.
- **Missing evidence**: The format encourages brevity, which can lead to skipping supporting data or measurements.

## Related Concepts

- [[concepts/architectural-decision-record]] — the document type that often contains a Y-statement.
- [[concepts/architectural-decision]] — the reasoning the Y-statement captures.

## Sources

- [adr.github.io](https://adr.github.io) — Background Information section.
- [Sustainable Architectural Decisions](https://www.infoq.com/articles/sustainable-architectural-design-decisions) — Zdun et al., InfoQ
