---
title: Hermes Ingest Pipeline — Design
date: 2026-05-04
status: draft
---

# Hermes Ingest Pipeline — Design

## Goal

Tie the existing per-task Hermes skills (`split-textbooks`, `pdf-to-mdbook`,
`wiki-*`) into an end-to-end ingestion flow that drives any of these inputs to
a buildable mdBook:

1. A single large PDF.
2. A directory of already-split chapter PDFs.
3. A directory of already-split markdown documents.
4. A partially-built mdBook directory (interrupted prior run).

The pipeline must be **idempotent**: rerun on a partial directory resumes from
where the prior run left off. The pipeline ends at `mdbook build` succeeding;
wiki ingestion (`wiki-ingest`) remains a separate, manual follow-up step.

## Scope

In scope:

- A new per-book orchestrator skill, `ingest-pipeline`, that classifies an
  input directory and drives it forward to a buildable mdBook by invoking
  existing skills as Hermes subagents.
- A new library batch wrapper, `ingest-pipeline-batch`, that walks a library
  root, identifies book directories, and dispatches the per-book engine.
- An addendum to the existing `pdf-to-mdbook` skill so it accepts a directory
  of pre-split PDF slices in addition to a single PDF (auto-detecting the
  input shape).
- Ansible registration (`defaults/main/hermes.yml`) so the new skills deploy
  through the existing `configure_hermes.yml` task.
- Test fixtures and a test harness wired into `just`.

Out of scope:

- Any changes to wiki skills.
- Modifying `split-textbooks` (used as-is via subagent).
- New Hermes plugins or MCP servers.
- Wiki-side coupling: the orchestrator does not call `wiki-ingest`.

## Hermes features used

| Feature                  | Where                                                       | Purpose                                                              |
|--------------------------|-------------------------------------------------------------|----------------------------------------------------------------------|
| Subagent Delegation      | Engine S1/S2 phases; batch per-book dispatch                | Context isolation so vision-pass output doesn't pollute orchestrator |
| Persistent Memory        | Batch reads `library.json` and prior failure history        | Cross-session continuity                                             |
| Event Hooks              | `pre_phase`, `post_phase`, `pre_destructive`                | Observability; refusal to clobber complete books without `--force`   |
| Checkpoints              | All file edits (already-on default behavior)                | Free rollback safety; no new wiring                                  |
| Code Execution (Python)  | Filesystem walks and JSON manifest reads                    | Cleaner than `jq` chains for nested cases                            |
| Scheduled Tasks (Cron)   | Documented as user-side recipe in skill README              | Optional; not encoded in SKILL.md                                    |

## Architecture

Two new skills live alongside the existing Hermes skill set:

```
hermes/skills/
├── ingest-pipeline/             (per-book engine — NEW)
│   ├── SKILL.md
│   └── references/
│       ├── state-detection.md
│       └── manifest-schema.md
├── ingest-pipeline-batch/       (library sweep — NEW)
│   └── SKILL.md
├── split-textbooks/             (existing — invoked as subagent)
├── pdf-to-mdbook/               (existing — extended for slice-dir input)
└── wiki-*/                      (untouched)
```

Both new skills are registered in `roles/dotfiles/defaults/main/hermes.yml`
under `hermes_skills`, deployed by `roles/dotfiles/tasks/configure_hermes.yml`.

## State model

The per-book engine classifies the target into one of six states.

| #   | State              | Detection                                                                                                                                     | Next action                                                                                          |
|-----|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| S0  | Empty / unrelated  | Target absent, or directory has no PDFs, no `*.md`, and no manifest                                                                           | Abort with diagnostic; no partial work                                                               |
| S1  | Single large PDF   | Target is `.pdf` file, OR directory contains exactly one `.pdf` and nothing else relevant                                                     | Run `split-textbooks` → produces sliced PDFs + `manifest.json` (schema 2). Reclassify (becomes S2).  |
| S2  | Pre-split PDFs     | Directory contains ≥2 `.pdf` matching `NN-<slug>.pdf` OR a `split-textbooks` `manifest.json` with `status: complete`                          | Run `pdf-to-mdbook` (slice-dir mode). Reclassify (becomes S4).                                       |
| S3  | Pre-split markdown | Directory contains ≥2 `.md` and no `book.toml`, OR `split-textbooks` manifest with `markdown_generated: true`                                 | Scaffold an mdBook directly (inline; no subagent): write `book.toml`, `src/SUMMARY.md`, copy files.  |
| S4  | Partial mdBook     | Directory contains `book.toml` AND `src/SUMMARY.md` AND no `pipeline.json` with `status: complete`                                            | Diagnose missing referenced files, fill stubs if needed, run `mdbook build`. On success → S5.        |
| S5  | Complete           | `pipeline.json` exists with `status: complete` AND mdBook builds cleanly                                                                      | No-op unless `--force`.                                                                              |

### Detection algorithm

Run on every invocation:

1. Resolve target to absolute path; identify file vs directory.
2. If `pipeline.json` at candidate book root has `status: complete` and
   `--force` not set → S5.
3. Else if `book.toml` and `src/SUMMARY.md` exist → S4.
4. Else if `split-textbooks` `manifest.json` exists:
   - `markdown_generated: true` → S3
   - `status: complete` (PDFs present) → S2
   - `status: failed` → respect `failed_step`; resume there
5. Else count files in the directory:
   - ≥2 `.md` and 0 `.pdf` → S3
   - ≥2 `.pdf` matching slice pattern → S2
   - exactly one `.pdf` (or target itself is a `.pdf`) → S1
6. Anything else → S0.

The algorithm is **filesystem-truth, manifest-belief**: if `pipeline.json` and
the filesystem disagree (user manually deleted output), the filesystem wins.
The orchestrator reclassifies and appends new phase entries; never errors on
disagreement.

## `pdf-to-mdbook` extension (slice-directory input)

Add a Step 0.5 to the existing `pdf-to-mdbook` SKILL.md, before the
canonical-PDF resolution step:

- If input is a `.pdf` file → existing path (Steps 1–7 unchanged).
- If input is a directory:
  - If `split-textbooks` `manifest.json` (schema 2) is present → use its
    `sections` array directly. Each slice becomes one chapter; `start_page`
    and `end_page` reduce to the slice's own page range. Skip Steps 1–2.
  - Else if directory contains `NN-<slug>.pdf` files → derive section list
    from filenames: `index = NN`, `slug = <slug>`, `kind` classified by the
    same regex used in Step 2's section-kind classification, page ranges from
    `pdfinfo` per slice.
  - In both directory cases, Step 4's per-section extraction loop runs over
    slices instead of page ranges of a single canonical PDF
    (`pdftotext` / `pdftoppm` operate on `<slice>.pdf` directly with
    `-f 1 -l <pagecount>`).

Manifest gains two fields: `slice_mode: bool` and `source_dir: <path>` (set
when `slice_mode: true`). `source_pdf` becomes optional in slice mode. The
manifest `schema_version` for `pdf-to-mdbook` bumps to `2`.

The vision pass and text-rules pass are untouched — they don't care whether
their input is "page 19–56 of canonical.pdf" or "all of slice.pdf".

## `pipeline.json` schema

Each book root gets one `pipeline.json` written by the orchestrator alongside
(not replacing) the existing per-skill manifests.

```json
{
  "schema_version": 1,
  "skill": "ingest-pipeline",
  "book_root": "/abs/path/to/book-root",
  "input_target": "/abs/path/to/book.pdf",
  "initial_state": "S1",
  "current_state": "S5",
  "status": "complete",
  "started_at": "2026-05-04T10:00:00Z",
  "updated_at": "2026-05-04T10:47:33Z",
  "phases": [
    {
      "name": "split",
      "skill": "split-textbooks",
      "status": "complete",
      "manifest": "manifest.json",
      "started_at": "2026-05-04T10:00:00Z",
      "completed_at": "2026-05-04T10:18:02Z",
      "subagent_invocation_id": "sa-7f3a"
    },
    {
      "name": "mdbook",
      "skill": "pdf-to-mdbook",
      "status": "complete",
      "manifest": "calculus-mdbook/manifest.json",
      "started_at": "2026-05-04T10:18:05Z",
      "completed_at": "2026-05-04T10:47:30Z",
      "subagent_invocation_id": "sa-9c12"
    },
    {
      "name": "build",
      "skill": null,
      "status": "complete",
      "started_at": "2026-05-04T10:47:30Z",
      "completed_at": "2026-05-04T10:47:33Z"
    }
  ],
  "failed_phase": null,
  "error_message": null,
  "notes": []
}
```

### Field semantics

- `initial_state` — captured on first invocation; never overwritten.
- `current_state` — updated each invocation.
- `status` — `pending` | `in_progress` | `complete` | `failed`.
- `phases` — append-only log. Reruns append; do not overwrite prior entries.
- `phases[].skill: null` — in-orchestrator inline work (S3 scaffold, final
  `mdbook build`).
- `subagent_invocation_id` — opaque ID returned by Hermes' subagent
  delegation, retained for log retracing.
- `notes` — free-form strings recording reconciliations (e.g., "filesystem
  reclassified to S2 from S5; user deleted mdbook dir").

### Crash safety

Before invoking each subagent: write `pipeline.json` with `status:
in_progress` and the new phase as `pending`. After the subagent returns:
update the phase entry to `complete` or `failed`. If Hermes is interrupted
mid-phase, rerun reads partial `pipeline.json`, reconciles with filesystem
state, and resumes.

## `library.json` schema (batch)

Single file at the library root, written by `ingest-pipeline-batch`.

```json
{
  "schema_version": 1,
  "library_root": "/abs/path/to/library",
  "last_swept_at": "2026-05-04T10:47:33Z",
  "books": [
    { "root": "calculus", "status": "complete", "pipeline_json": "calculus/pipeline.json" },
    { "root": "probability", "status": "in_progress", "pipeline_json": "probability/pipeline.json" },
    { "root": "discrete-math", "status": "failed", "failed_phase": "split", "pipeline_json": "discrete-math/pipeline.json" }
  ]
}
```

A book with `status: complete` is skipped on rerun unless `--force`. A book
with `status: failed` retries automatically — failure was logged, the user
inspected, the rerun is the explicit "try again" signal.

## Data flow

### Per-book engine

```
ingest-pipeline <target> [--force] [--vision auto|always|never]
  Step 0  env self-check (poppler, qpdf, ocrmypdf, mdbook, jq)
  Step 1  resolve book root
  Step 2  classify state (S0–S5)
  Step 3  write/update pipeline.json (status: in_progress, append phase)
  Step 4  dispatch by state:
            S0 → abort
            S1 → split-textbooks subagent → S2
            S2 → pdf-to-mdbook subagent  → S4
            S3 → scaffold mdbook inline   → S4
            S4 → mdbook build inline      → S5
  Step 5  reclassify; loop until S5 or failure
  Step 6  finalize pipeline.json (status: complete | failed)
```

Sequencing rules:

- Phases within a book run sequentially. Concurrent phases on the same book
  would compete for tool I/O and would not save real time.
- Subagent invocations carry a restricted toolset: `terminal`, `file`, plus
  `image` for the vision pass. Subagent response is `{status, manifest_path,
  error?}` — a pointer, not the content.
- The classifier re-runs after every phase, giving "drive forward to S5"
  semantics.
- Inline work (S3 scaffold, final `mdbook build`) runs in the orchestrator's
  context — these steps are small (file templating; one shell command) and
  don't justify subagent overhead.

### Library batch

```
ingest-pipeline-batch <library_root> [--force] [--parallel N]
  Step 0  env self-check
  Step 1  load library.json (initialize empty if missing)
  Step 2  walk library tree, identify book roots:
            - dir contains exactly one PDF, OR
            - dir contains pipeline.json, OR
            - dir contains split-textbooks manifest.json, OR
            - dir contains book.toml + src/SUMMARY.md
  Step 3  filter: skip status: complete unless --force
  Step 4  dispatch per-book engine: sequential by default, --parallel N caps
          concurrent ingest-pipeline subagents at N
  Step 5  collect results, write library.json
```

`--parallel` defaults to 1. Vision-heavy scanned books should stay sequential
to keep token cost predictable; small clean books are safe at 2–4.

## Error handling

| Failure                                              | Detected at         | Behavior                                                                                                       |
|------------------------------------------------------|---------------------|----------------------------------------------------------------------------------------------------------------|
| Required tool missing                                | Step 0              | Print install hints; abort. No partial pipeline.json written.                                                  |
| State classifier returns S0                          | Step 2              | Abort with diagnostic ("no PDFs, markdown, or book.toml found in <dir>"). No pipeline.json written.            |
| `split-textbooks` subagent fails                     | Step 4              | Phase status `failed`; populate `failed_phase: split` and `error_message` from the sub-skill manifest. Stop.   |
| `pdf-to-mdbook` subagent fails                       | Step 4              | Phase status `failed`; `failed_phase: mdbook`. Stop.                                                           |
| S3 scaffold error                                    | Step 4              | `failed_phase: scaffold`. Stop.                                                                                |
| `mdbook build` fails after auto-fix attempt          | Step 4              | `failed_phase: build`. (`pdf-to-mdbook` already attempts one auto-fix; orchestrator does not add another.)     |
| Filesystem inconsistent (e.g., book.toml without src/) | Step 2 reclassify | Treat as S4 with damage; record in `notes`; attempt repair by re-running prior phase.                          |
| Subagent invocation timeout / Hermes error           | Anywhere            | Phase status `failed`, `error_message: "subagent invocation failed: <details>"`. Stop.                         |
| User-aborted run (Ctrl-C)                            | Anywhere            | `pipeline.json` left at `status: in_progress`. Rerun reconciles via filesystem-truth rule.                     |

Batch-level errors never abort the whole sweep — one failed book gets its
`library.json` entry marked `failed` and the next book proceeds. The user
inspects `library.json` and reruns either the batch (retries failed books) or
the per-book engine (debug one book interactively).

### Hooks for safety

- `pre_destructive` hook fires before any phase that would overwrite a
  `status: complete` directory; refuses unless `--force` is passed. Backstop
  against accidental data loss.
- `pre_phase` and `post_phase` hooks emit JSON log lines:
  `{phase, book_root, status, duration_ms}` — usable by users who pipe to
  `jq` or set up notifications.

## Testing

Tests live under `roles/dotfiles/tests/hermes/ingest-pipeline/` and
`roles/dotfiles/tests/hermes/ingest-pipeline-batch/`. Test fixtures are tiny
synthetic PDFs (a 4-page text PDF, a 4-page scanned PDF) checked into a
fixtures directory under the same path.

### Unit (state classifier)

- Each of S0–S5 has a fixture directory; the classifier returns the expected
  state. Pure function, fast, no subprocess calls.
- Idempotency: classifying the same fixture twice returns the same state.
- Filesystem-truth rule: a fixture with stale `pipeline.json` (claims
  complete) but missing `<stem>-mdbook/` reclassifies correctly.

### Integration (per-book engine)

- Run engine end-to-end on a 4-page synthetic PDF. Verify `pipeline.json`
  reaches `status: complete` and `mdbook build` produces output.
- Crash-resume: kill engine after `split-textbooks` completes, rerun, verify
  it resumes at S2 and reaches S5 without re-running the split.
- `--force` re-run: verify it re-does all phases and overwrites prior output.
- S3 path: feed a directory of pre-split markdown, verify scaffold + build.

### Integration (batch)

- Library with three books: one fresh PDF, one already-complete, one partial.
  Verify only the fresh and partial get worked on, complete is skipped.
- Failure isolation: one book is corrupted. Verify other books in the batch
  still complete; `library.json` reflects per-book status.

### Test runner

Add `roles/dotfiles/tests/hermes/run-tests.sh` shell harness driving the
engine via the Hermes CLI, asserting on `pipeline.json` contents with `jq`,
wired into `just test-hermes`.

## Observability

- `pipeline.json` is the durable record per book. Documented `jq` queries in
  the skill README:
  - `jq '.status' pipeline.json` — quick status
  - `jq '.phases[] | select(.status=="failed")' pipeline.json` — what broke
  - `jq -r '.phases | map(select(.status=="complete")) | .[] | "\(.name): \(.completed_at)"' pipeline.json`
- `library.json` is the durable record per library.
- Hermes hooks can pipe phase events to syslog or a file; documented as
  optional in the skill README, not enforced.

## Ansible deployment

Add to `roles/dotfiles/defaults/main/hermes.yml`:

```yaml
hermes_skills:
  # ... existing entries unchanged ...
  - name: "ingest-pipeline"
    description: "Drive any PDF/markdown input directory to a buildable mdBook — handles large PDFs, pre-split PDFs, pre-split markdown, partial mdBooks; idempotent and resumable"
    content_file: "hermes/skills/ingest-pipeline/SKILL.md"
  - name: "ingest-pipeline-batch"
    description: "Sweep a library directory and run ingest-pipeline on every book root that isn't already complete"
    content_file: "hermes/skills/ingest-pipeline-batch/SKILL.md"
```

The existing `configure_hermes.yml` task copies skill directories under
`hermes/skills/<name>/` into `~/.hermes/skills/<name>/` and templates the
`SKILL.md`. No task changes required.

The `pdf-to-mdbook` SKILL.md content is updated in-place (Step 0.5 added,
manifest schema bumped). Description in `hermes_skills` updates to mention
slice-directory input.

## Open questions

None at design close.

## Out of scope follow-ups

- A `wiki-bridge` skill that copies completed mdBook chapter files into a
  wiki's `raw/` so `wiki-ingest` can pick them up. Mentioned for context;
  intentionally separate.
- Cron recipe in user-facing docs ("nightly library sweep").
- Hermes plugin to expose phase events via Prometheus exporter.
