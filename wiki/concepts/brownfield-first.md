---
title: "Brownfield-First"
type: concept
tags: [concept, software-development, legacy-code, specification]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/openspec-docs"]
confidence: high
---

## Definition

Brownfield-first is a software-planning philosophy that prioritizes tools and practices for evolving existing codebases over describing greenfield systems from scratch. It acknowledges that most professional software work modifies existing behavior rather than creating entirely new systems.

## How It Works

OpenSpec implements brownfield-first through several design choices:

1. **Delta specs as first-class citizens.** Changes are expressed as ADDED, MODIFIED, and REMOVED requirements relative to the current spec baseline, not as full rewritten specifications.
2. **Archive merges cleanly.** When a change is archived, its deltas are merged into the main specs, building up the specification organically over time.
3. **Parallel changes without conflict.** Multiple changes can touch the same spec domain simultaneously because each change only describes its own delta.
4. **Existing specs are the source of truth.** The `openspec/specs/` directory always reflects the currently agreed-upon behavior, making it a living document.

## Key Parameters

| Aspect | Greenfield-First | Brownfield-First |
|--------|----------------|------------------|
| Default spec format | Full specification | Delta relative to baseline |
| Parallel work | Independent specs per feature | Deltas against shared baseline |
| Historical context | Minimal (everything is new) | Preserved in archive + spec evolution |
| Onboarding new devs | Read full spec | Read current specs + recent archives |

## When To Use

A brownfield-first approach is appropriate when:
- The team maintains an existing product with users and production data
- Most changes are enhancements, fixes, or refactors rather than new modules
- Specifications need to stay current with a living codebase
- Audit history of *why* each change was made is valuable

Greenfield-first may still be preferable when:
- Building a new product or service from scratch
- The project has no existing behavior to preserve or modify
- A full up-front specification is required by contract or regulation

## Risks & Pitfalls

- **Baseline drift:** If the main specs are not kept current, deltas become harder to write and archive. The archive step is the critical hygiene practice.
- **Over-reliance on deltas:** For a massive rewrite where nearly every requirement changes, a delta spec may be larger and more confusing than a fresh full spec. In that case, starting a new spec domain or a comprehensive replacement change is acceptable.
- **Archive ordering:** When multiple changes modify the same requirement, archiving in the wrong order can create logical inconsistencies. OpenSpec's bulk-archive command resolves this by checking the codebase.

## Related Concepts

- [[concepts/delta-spec]] — The mechanism that makes brownfield-first practical
- spec-driven development — The discipline of keeping specs current
- [[concepts/fluid-workflow]] — Iteration fits brownfield reality better than phases

## Sources

- OpenSpec Concepts Guide (`raw/openspec-docs/concepts.md`)
