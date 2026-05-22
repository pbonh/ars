---
title: "Delta Spec"
type: concept
tags: [concept, specification, brownfield, versioning]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/openspec-docs"]
confidence: high
---

## Definition

A delta spec is a specification that describes changes relative to an existing baseline spec rather than restating the entire specification. It uses explicit sections—ADDED, MODIFIED, REMOVED—to declare what behavior is new, altered, or deprecated.

## How It Works

Delta specs live inside a change folder (e.g., `openspec/changes/add-2fa/specs/auth/spec.md`) and are merged into the main spec directory during archive. The format uses top-level section headers to categorize each change:

```markdown
# Delta for Auth

## ADDED Requirements
### Requirement: Two-Factor Authentication
The system MUST support TOTP-based 2FA.

## MODIFIED Requirements
### Requirement: Session Expiration
The system MUST expire sessions after 15 minutes.
(Previously: 30 minutes)

## REMOVED Requirements
### Requirement: Remember Me
(Deprecated in favor of 2FA.)
```

On archive, the archive engine:
1. Appends ADDED requirements to the target spec
2. Replaces MODIFIED requirements in place
3. Deletes REMOVED requirements
4. Preserves untouched requirements

## Key Parameters

| Parameter | Effect |
|-----------|--------|
| ADDED | New behavior appended to the main spec |
| MODIFIED | Existing requirement replaced; previous text should be noted inline |
| REMOVED | Existing requirement deleted from the main spec |

## When To Use

Use delta specs when:
- Specifying changes to an existing system (brownfield work)
- Multiple parallel changes touch the same domain but different requirements
- Reviewers need to see only what changed, not the full spec
- Archiving should merge cleanly without manual diffing

Avoid delta specs when:
- The project has no existing specs yet (create a full spec instead)
- A change is so sweeping that the delta is larger than the original spec

## Risks & Pitfalls

- **Merge conflicts:** If two parallel changes modify the same requirement, the second archive may overwrite the first. OpenSpec resolves this by checking what is actually implemented in the codebase.
- **Drift from baseline:** Long-running changes can diverge from the main spec if it is updated by other archived changes in the meantime. Periodic sync (`/opsx:sync`) mitigates this.
- **Incomplete REMOVED context:** A removed requirement should explain *why* it is deprecated so future readers understand the decision.

## Related Concepts

- spec-driven development — The broader methodology
- [[concepts/brownfield-first]] — The philosophy that makes deltas necessary
- [[concepts/fluid-workflow]] — Updating artifacts during implementation

## Sources

- OpenSpec Concepts Guide (`raw/openspec-docs/concepts.md`)
- OpenSpec Getting Started Guide (`raw/openspec-docs/getting-started.md`)
