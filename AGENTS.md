# ars.scientia_rewrite — Agent Operating Guide

<!-- Emitted by scientia-wiki-init on 2026-05-23 (bundle 0.1.0). -->
<!-- This file is regenerated only if absent; hand-edits are preserved on upgrade. -->

## Purpose

This repository is managed by **scientia**, a closed-loop software R&D delivery
pipeline. Knowledge flows in one direction and back:

```
raw/ ──► wiki/ ──► development/manifests/ ──► openspec/changes/ ──► kanban tasks ──► ingest ──► wiki/
        (wiki)        (intent)                  (kanban)             (ingest)
```

Every durable artifact in this repo — wiki pages, manifests, OpenSpec proposals,
specs, designs, ADRs, task lists, kanban rows — is **produced by a scientia
skill, not hand-authored.** Your job as an agent is to detect where a change is
in the pipeline and invoke the correct skill, never to write these artifacts
free-hand. This file is the front door; the authoritative, full detail for each
step lives in that step's `SKILL.md`.

**Concurrency law:** one in-flight change per bounded-context **tenant**;
different tenants run fully in parallel.

## Repository Layout

```
ars.scientia_rewrite/
├── AGENTS.md                # this file — how agents operate here
├── raw/                     # immutable source documents — NEVER modify
├── wiki/                    # the knowledge graph (the source of truth)
│   ├── index.md             # master catalog — every page must appear here
│   ├── log.md               # append-only activity log
│   ├── concepts/            # concept / strategy / framework pages
│   ├── entities/            # tools, services, libraries, people
│   ├── summaries/           # one summary per raw/ source
│   ├── syntheses/           # cross-change syntheses; ingest writes PROPOSED edits here
│   ├── contexts/            # one bounded-context page per tenant
│   ├── context-maps/        # context maps across bounded contexts
│   ├── decisions/           # ADR mirrors (living documentation)
│   └── specs/               # spec mirrors (living documentation)
├── development/             # scientia's own metadata layer
│   ├── config.yaml          # per-repo scientia configuration
│   ├── log.md               # orchestrator audit trail (append-only)
│   ├── manifests/<tenant>/<change-id>/   # the knowledge pinned into each change
│   └── tasks/<tenant>/<change-id>/       # per-task kanban index
└── openspec/                # the intent-driven change lifecycle
    ├── config.yaml          # OpenSpec config (binds each stage to its scientia skill)
    ├── schemas/intent-driven/
    ├── changes/<tenant>-<change-id>/     # one in-flight change per dir
    └── archive/             # archived changes
```

## The Pipeline (four phases)

| Phase | Skills (in order) | Owns / produces |
|-------|-------------------|-----------------|
| **wiki** | `wiki-init` → `wiki-ingest` → `wiki-strategy` → `wiki-grill` → `wiki-lint` → `wiki-bind` | `raw/`, `wiki/`; ends by writing `development/manifests/<tenant>/<change-id>/core.md` |
| **intent** | `intent-proposal` → `intent-spec` → `intent-design` → `intent-adr` → `intent-tasks` → `intent-verify` | `openspec/changes/<tenant>-<change-id>/` + design/tasks manifest extensions |
| **kanban** | `kanban-init` (once/host) → `kanban-emit` → workers (`kanban-worker`) → `kanban-status` → `kanban-archive` | durable rows on the Hermes board |
| **ingest** | `ingest-evidence` → `ingest-synthesize` → `ingest-archive` | round-trips results back into `wiki/`, then archives all three stores |

(Skill names above are prefixed `scientia-` — e.g. `scientia-wiki-bind`.)

## Skill Map — detected state → next action

**Always start with the `scientia` orchestrator skill.** It runs state detection
and routes you; do not guess the stage by hand.

| When you observe… | Invoke |
|-------------------|--------|
| No `wiki/` | `scientia-wiki-init` |
| Wiki exists, a new raw/ source landed | `scientia-wiki-ingest` |
| Wiki exists, contexts not yet mapped | `scientia-wiki-strategy` |
| User names a new change | `scientia-wiki-grill` → `scientia-wiki-lint` → `scientia-wiki-bind` |
| Manifest `core.md` bound, no proposal | `scientia-intent-proposal` |
| Proposal on trunk | `scientia-intent-spec` |
| Specs on trunk | `scientia-intent-design` |
| Design exists | `scientia-intent-adr` |
| ADRs accepted | `scientia-intent-tasks` |
| `tasks.md` exists | `scientia-intent-verify` |
| Verified, findings below `verify.block_on_severity` | `scientia-kanban-emit` |
| Tasks running | `scientia-kanban-status` (poll) or wait |
| All tasks done | `scientia-ingest-evidence` → `scientia-ingest-synthesize` → `scientia-ingest-archive` |
| User says "status?" | `scientia-kanban-status` |
| User says "grill me" / "interview me" | `scientia-grill` |
| User says "verify" | `scripts/verify_all.py` |

## Naming Conventions

- **tenant** — a bounded-context slug. It is simultaneously the OpenSpec
  spec-slug and the Hermes `--tenant` value. Example: `billing`.
- **change-id** — `<YYYY-MM-DD>-<short-slug>`. Example: `2026-05-19-add-refunds`.
- **full change identifier** — `<tenant>/<change-id>`, e.g.
  `billing/2026-05-19-add-refunds`. (OpenSpec dirs join with a hyphen:
  `billing-2026-05-19-add-refunds`.)
- **file slugs** — all lowercase, hyphen-separated, no spaces/uppercase; the
  slug matches the page title.
- **ADR files** — `NNNN-<kebab-title>.md`, zero-padded sequence (`0001-…`).
- **dates** — ISO 8601 (`YYYY-MM-DD`); timestamps `YYYY-MM-DDTHH:MM:SSZ` (UTC).

## Artifact Formats

Full schemas live in each owning skill; these are reminders so you recognize a
well-formed artifact.

### Wiki pages

Every page carries this frontmatter:

```yaml
---
title: "Page Title"
type: concept | entity | summary | synthesis | context
tags: [tag1, tag2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: ["raw/filename.txt"]
confidence: high | medium | low
---
```

Required sections by page type:
- **summary** — `## Key Points`, `## Relevant Concepts`, `## Source Metadata`.
- **concept** — `## Definition`, `## How It Works`, `## Key Parameters`,
  `## When To Use`, `## Risks & Pitfalls`, `## Related Concepts`, `## Sources`.
- **entity** — `## Overview`, `## Characteristics`, `## Common Strategies`,
  `## Related Entities`.
- **synthesis** — `## Comparison`, `## Analysis`, `## Recommendations`,
  `## Pages Compared`.
- **context** (`wiki/contexts/<tenant>.md`) — the bounded context's boundary,
  subdomains (core/supporting/generic), and **ubiquitous language** glossary.

`wiki/decisions/` and `wiki/specs/` hold living-documentation mirrors of accepted
ADRs and specs; they are written by the ingest/intent skills, not by hand.

### Manifest `core.md` (10 slices)

The single artifact that carries wiki knowledge into a change, pinned at the
wiki's git rev. Slices fill in across stages:
1–4 + 7 (domain framing, concepts, entities, ubiquitous language, prior work) at
**bind**; 5, 6, 8 (in-force ADRs, ASRs/QAS, pitfalls) at **design**; 9
(tradeoffs) at **tasks**; 10 (addenda) lazily.

### OpenSpec change tree

```
openspec/changes/<tenant>-<change-id>/
├── proposal.md                  # why + what-changes
├── specs/<capability>/spec.md   # Gherkin scenarios (one When per scenario)
├── design.md                    # C4 diagrams + explicit treatment of each in-force ADR
├── adr/NNNN-<kebab-title>.md     # immutable Y-statement ADRs
├── tasks.md                     # INVEST checkbox items; (depends on #N) edges
└── verify-<timestamp>.md        # Completeness / Correctness / Coherence report
```

### ADR — Y-statement (immutable)

> In the context of **X**, facing **Y**, we decided for **Z** and against **A**,
> to achieve **B**, accepting **C**.

Carries an Architecturally Significant Requirement (ASR). **Never edit an
accepted ADR — write a new one that `Supersedes` it.**

### Kanban task body

`scientia-kanban-emit` writes each task body in this fixed order; workers read it
top to bottom:

```
# @wiki-spec: <spec-slug>
## Goal                      (verbatim from spec — your contract)
## Acceptance Criteria       (verbatim from spec)
## Scenario                  (the Gherkin block — the executable spec)
## Glossary                  (ubiquitous language — use terms EXACTLY)
## Governing ADRs            (in-force decisions you must honor)
## Implementation Checklist  (advisory, scoped from tasks.md)
## Required Handoff          (fill on completion — see below)
```

**Required Handoff** fields (all required; `none`/`none known`/`""` are the
sentinels for absence): `summary`, `verification` (exact command + outcome),
`changed_files` (YAML list), `dependencies`, `blocked_reason`, `retry_notes`,
`residual_risk`, `branch_head` (commit SHA), `wiki_spec`, `wiki_adr_ids`.

## Linking Conventions

- Obsidian-style wiki links: `[[concepts/concept-name]]`, relative to wiki root.
- Every page links to at least one other (no orphans).
- When you mention a concept that has a page, link it.

## Confidence Levels

- **high** — well-established, multiple corroborating sources, concrete examples.
- **medium** — supported but limited examples or single-source.
- **low** — single mention, anecdotal, or speculative. When in doubt, use `low`
  and note the uncertainty.

## Workflows

### Ingest knowledge
A new document in `raw/` → invoke `scientia-wiki-ingest`: it writes the summary,
creates/updates concept and entity pages, cross-links them, updates `wiki/index.md`,
and appends to `wiki/log.md`. Flag contradictions with existing pages.

### Run a change (the closed loop)
1. `scientia-wiki-grill` → `scientia-wiki-lint` → `scientia-wiki-bind` (bind `core.md`).
2. `scientia-intent-proposal` → `-spec` → `-design` → `-adr` → `-tasks` → `-verify`.
3. `scientia-kanban-emit` (once verify is clean) → workers run → `scientia-kanban-status` to poll.
4. `scientia-ingest-evidence` (per task) → `scientia-ingest-synthesize` (per change) →
   user applies the proposed wiki edits → `scientia-ingest-archive`.

### Check status
`scientia-kanban-status`, or run `scientia/scripts/state_detect.py --pretty`.

### Verify / lint
`scientia-wiki-lint` (wiki integrity), `scientia-intent-verify` (per-change C/C/C
scoring), and `scientia/scripts/verify_all.py` as the CI entry point across all
in-flight changes.

## Rules (load-bearing invariants)

Breaking any of these stalls the board or corrupts artifacts.

1. **Delegate, don't hand-author.** Never write `proposal.md`, `spec.md`,
   `design.md`, ADRs, `tasks.md`, kanban rows, or `wiki/concepts|entities` pages
   by hand — invoke the owning skill.
2. **Never modify `raw/`.** Sources are immutable.
3. **Append logs via shell redirection**, never edit-anchors —
   `development/log.md` and `wiki/log.md` grow between turns, so anchored edits
   race:
   ```bash
   printf '%s\n' "- $(date -u +%Y-%m-%dT%H:%M:%SZ) — <skill> — <event> — <tenant>/<change-id> — <details>" >> development/log.md
   ```
4. **ADRs are immutable** once accepted — supersede, never edit.
5. **One in-flight change per tenant.** Refuse to start a second.
6. **The manifest pins the wiki rev.** If a change's `wiki_snapshot` no longer
   resolves, stop and re-bind — never proceed on drift.
7. **Gates block advance:** `scientia-wiki-lint` CRITICAL findings, verify
   findings ≥ `verify.block_on_severity`, `git:spec-on-trunk` failing before
   emit, multiple in-flight changes per tenant, or a `scientia_schema_version`
   newer than the installed bundle.
8. **Headless worker discipline** (Hermes-spawned workers): never ask clarifying
   questions (no human is listening); every turn ends with a tool call until you
   call `hermes kanban complete` or `hermes kanban block`; on ambiguity, **block
   with a precise handoff — do not guess**; never archive yourself; never create
   a child task of yourself.
9. **Git:** each pipeline stage runs in its own worktree; the implementer commits
   to the worker branch and only the **integrator** merges to trunk; commit
   messages reference the kanban task id and the `@wiki-spec` tag; never
   force-push trunk; unblock only through `scientia/scripts/unblock_gate.py`.
10. **Synthesis proposes, humans apply.** `scientia-ingest-synthesize` writes
    proposed edits to `wiki/syntheses/` only; it never writes `wiki/concepts/` or
    `wiki/entities/` directly. The user reviews and applies.

## Where to go deeper

- The `scientia` orchestrator skill, plus its `references/PIPELINE.md` and
  `references/SKILL_MAP.md`.
- Each phase skill's own `SKILL.md` for the full procedure and schema.
- `development/config.yaml` for this repo's emit/verify/ingest policy and tenant
  overrides.
