---
title: "Progressive Rigor"
type: concept
tags: [concept, specification, risk-management, documentation]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/openspec-docs"]
confidence: high
---

## Definition

Progressive rigor is a documentation discipline in which the depth and formality of specifications scale with the risk, scope, and cross-team impact of a change, rather than enforcing a single heavyweight template for all work.

## How It Works

OpenSpec defines two default levels:

**Lite spec (default):**
- Short behavior-first requirements
- Clear scope and explicit non-goals
- A few concrete acceptance checks (scenarios)
- Minimal ceremony; can be drafted in minutes

**Full spec (for higher risk):**
- Cross-team or cross-repo changes
- API/contract changes, migrations, security or privacy concerns
- Changes where ambiguity is likely to cause expensive rework
- Edge cases, error conditions, and compatibility notes explicitly covered

The decision is made per-change. A team might use lite specs for routine UI tweaks and full specs for authentication overhauls. The schema and artifact templates remain the same; only the content depth varies.

## Key Parameters

| Rigor Driver | Lite | Full |
|--------------|------|------|
| Team surface | Single team | Multiple teams or repos |
| Contract impact | Internal only | Public API, database schema, protocol |
| Risk domain | Low sensitivity | Security, privacy, compliance, payments |
| Ambiguity cost | Cheap to fix later | Expensive to fix later |
| Scenarios | 2–4 happy-path + key edge cases | Exhaustive happy, error, and edge cases |

## When To Use

Apply progressive rigor when:
- A specification framework is being adopted and the team fears bureaucratic overhead
- Different changes genuinely need different levels of detail
- The goal is to keep specs lightweight enough that they stay maintained

Avoid the lite-default approach if:
- Regulatory or contractual requirements mandate exhaustive documentation for everything
- The team has a history of under-specifying and paying rework costs

## Risks & Pitfalls

- **Inconsistent quality:** Without clear criteria, "lite" can become a euphemism for "vague." Teams should publish their own heuristics for when to escalate.
- **Pressure to stay lite:** Engineers may resist writing fuller specs even when risk warrants them. A designated reviewer or checklist can enforce escalation.
- **Lite specs aging badly:** A spec that was sufficient for a small change may become insufficient after the feature grows. Periodic spec review (e.g., during archive) catches this.

## Related Concepts

- [[concepts/delta-spec]] — The format in which rigor is expressed
- spec-driven development — The methodology that requires rigor
- [[concepts/fluid-workflow]] — Iterative refinement lets lite specs grow organically

## Sources

- OpenSpec Concepts Guide (`raw/openspec-docs/concepts.md`)
