# Hermes Ingest Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tie the existing Hermes skills (`split-textbooks`, `pdf-to-mdbook`) into a single end-to-end ingestion orchestrator that drives any of [large PDF / pre-split PDFs / pre-split markdown / partial mdBook] forward to a buildable mdBook, idempotent and resumable across runs.

**Architecture:** Two new Hermes skills — `ingest-pipeline` (per-book engine) and `ingest-pipeline-batch` (library sweep) — plus a slice-directory addendum to the existing `pdf-to-mdbook` skill. The orchestrator classifies the input directory into one of six states (S0–S5) and dispatches to existing skills as Hermes subagents. State is persisted in a new `pipeline.json` per book and `library.json` per library; reruns reconcile by treating filesystem as truth and the manifest as belief.

**Tech Stack:** Ansible (`dotfiles` role deployment), Markdown SKILL.md files (LLM-instruction), Hermes Subagent Delegation + Event Hooks + Persistent Memory, Bash test harness, `just` task runner, Python 3 with `reportlab` for fixture-PDF generation (or `pandoc` fallback).

**Reference spec:** `docs/superpowers/specs/2026-05-04-hermes-ingest-pipeline-design.md`

---

## File Structure

**New files:**

- `roles/dotfiles/files/hermes/skills/ingest-pipeline/SKILL.md` — per-book engine (entrypoint).
- `roles/dotfiles/files/hermes/skills/ingest-pipeline/references/state-detection.md` — six-state classifier algorithm.
- `roles/dotfiles/files/hermes/skills/ingest-pipeline/references/manifest-schema.md` — `pipeline.json` schema doc.
- `roles/dotfiles/files/hermes/skills/ingest-pipeline-batch/SKILL.md` — library sweep skill.
- `roles/dotfiles/tests/hermes/run-tests.sh` — test harness driving fixtures + optional Hermes invocation.
- `roles/dotfiles/tests/hermes/make-fixtures.sh` — regenerates synthetic-PDF fixtures.
- `roles/dotfiles/tests/hermes/fixtures/README.md` — fixture catalog.
- `roles/dotfiles/tests/hermes/fixtures/s0-empty/.gitkeep` — S0: empty unrelated dir.
- `roles/dotfiles/tests/hermes/fixtures/s1-single-pdf/book.pdf` — S1 input.
- `roles/dotfiles/tests/hermes/fixtures/s2-pre-split-pdfs/01-intro.pdf` — S2 input slice 1.
- `roles/dotfiles/tests/hermes/fixtures/s2-pre-split-pdfs/02-body.pdf` — S2 input slice 2.
- `roles/dotfiles/tests/hermes/fixtures/s2-pre-split-pdfs/manifest.json` — split-textbooks manifest for the slice dir.
- `roles/dotfiles/tests/hermes/fixtures/s3-pre-split-md/01-intro.md` — S3 input markdown 1.
- `roles/dotfiles/tests/hermes/fixtures/s3-pre-split-md/02-body.md` — S3 input markdown 2.
- `roles/dotfiles/tests/hermes/fixtures/s4-partial-mdbook/book.toml` — S4 partial mdBook config.
- `roles/dotfiles/tests/hermes/fixtures/s4-partial-mdbook/src/SUMMARY.md` — S4 summary.
- `roles/dotfiles/tests/hermes/fixtures/s4-partial-mdbook/src/README.md` — S4 README.
- `roles/dotfiles/tests/hermes/fixtures/s4-partial-mdbook/src/01-intro.md` — S4 chapter.
- `roles/dotfiles/tests/hermes/fixtures/s5-complete/pipeline.json` — S5 marker file.
- `roles/dotfiles/tests/hermes/fixtures/s5-complete/book.pdf` — S5 source PDF (referenced by pipeline.json).
- `roles/dotfiles/tests/hermes/fixtures/s5-complete/book-mdbook/book.toml` — S5 mdBook output stub.
- `roles/dotfiles/tests/hermes/fixtures/stale-pipeline-json/pipeline.json` — fixture: complete marker but missing mdbook dir.
- `roles/dotfiles/tests/hermes/fixtures/stale-pipeline-json/book.pdf` — fixture: input PDF still present.
- `roles/dotfiles/tests/hermes/fixtures/library/calculus/book.pdf` — batch fixture: fresh book.
- `roles/dotfiles/tests/hermes/fixtures/library/probability/pipeline.json` — batch fixture: complete book.
- `roles/dotfiles/tests/hermes/fixtures/library/probability/book.pdf` — batch fixture: complete book input.
- `roles/dotfiles/tests/hermes/fixtures/library/probability/probability-mdbook/book.toml` — batch fixture: complete book output.
- `roles/dotfiles/tests/hermes/fixtures/library/discrete-math/book.pdf` — batch fixture: book that fails (corrupt).
- `scripts/just/hermes.just` — `just` module with the `test-hermes` task.

**Modified files:**

- `roles/dotfiles/files/hermes/skills/pdf-to-mdbook/SKILL.md` — add Step 0.5 for slice-directory input; bump manifest schema_version to 2; add `slice_mode`, `source_dir`, `slice_filename` fields.
- `roles/dotfiles/defaults/main/hermes.yml` — register `ingest-pipeline` and `ingest-pipeline-batch`; update `pdf-to-mdbook` description to mention slice-directory input.
- `justfile` — add `import 'scripts/just/hermes.just'`.
- `markdownbook/configuration/dotfiles.md` — add an entry covering the new skills.

**Unchanged but referenced:**

- `roles/dotfiles/tasks/configure_hermes.yml` — already templates SKILL.md files and copies skill subtree assets recursively (via `src: "hermes/skills/{{ item.name }}/"`); the new `references/` subdirectories deploy automatically.
- `roles/dotfiles/templates/hermes/SKILL.md.j2` — existing template; falls through to `lookup('file', ...)` when `content_file` is set, which is the case for every new skill here.

---

## Notes on the codebase that the engineer will need

- **Skill deployment is recursive.** `configure_hermes.yml` line `src: "hermes/skills/{{ item.name }}/"` copies the entire skill directory into `~/.hermes/skills/<name>/`. Subdirectories like `references/` deploy automatically — no extra Ansible task needed.
- **Skill registration uses `content_file`.** Each entry in `hermes_skills` (in `defaults/main/hermes.yml`) points at `hermes/skills/<name>/SKILL.md`; the `SKILL.md.j2` template falls through to `lookup('file', role_path ~ '/files/' ~ skill.content_file)` for these.
- **Hermes is invoked via `hermes` CLI.** The actual binary location and exact prompt format vary by user setup; the test harness does not invoke real Hermes by default — it gates the live invocation behind `HERMES_TEST=1` so the "fixture validity" checks always run cheaply.
- **Existing skills follow a pattern.** Frontmatter has `name`, `description`, optional `compatibility`. Body has numbered Steps, tables for decisions, a "Failure handling" section, and (for the more complex ones) a `references/` subdirectory holding implementation details that bloat the SKILL.md too much. Mirror that pattern.
- **The existing `pdf-to-mdbook` SKILL.md is 416 lines.** Its Step 1 resolves canonical PDF, Step 2 detects structure, Step 3 scaffolds, Step 4 extracts content per section, Step 5 writes SUMMARY.md, Step 6 writes manifest, Step 7 validates the build. The extension (Task 7 of this plan) inserts a Step 0.5 immediately after Step 0 (env self-check) so the rest of the steps still run unchanged when input is a single PDF.
- **`just` modules are auto-imported in the top-level `justfile`.** Adding a new module is two steps: create `scripts/just/hermes.just`, and add `import 'scripts/just/hermes.just'` to `justfile`.
- **No Molecule, no pytest.** The repo does not have a Hermes-skill test framework. The harness is shell + `jq`. Hermes-CLI invocation is opt-in.
- **Fixtures are binary PDFs.** They must be valid PDFs because the orchestrator calls `pdfinfo` on them. We generate them once with Python `reportlab` (or `pandoc` fallback), then commit the binaries so the harness doesn't require the generator on every machine.

---

## Task 1: Scaffold skill directories and stub SKILL.md files

**Purpose:** Get the Ansible registration in place before any content is written. This lets us run `ansible-playbook --syntax-check` immediately and confirms the deployment path works end-to-end before we sink time into the actual skill content.

**Files:**
- Create: `roles/dotfiles/files/hermes/skills/ingest-pipeline/SKILL.md`
- Create: `roles/dotfiles/files/hermes/skills/ingest-pipeline/references/.gitkeep`
- Create: `roles/dotfiles/files/hermes/skills/ingest-pipeline-batch/SKILL.md`
- Modify: `roles/dotfiles/defaults/main/hermes.yml` (append two `hermes_skills` entries)

- [ ] **Step 1: Create the per-book skill directory tree**

```bash
mkdir -p roles/dotfiles/files/hermes/skills/ingest-pipeline/references
touch roles/dotfiles/files/hermes/skills/ingest-pipeline/references/.gitkeep
```

- [ ] **Step 2: Create the per-book SKILL.md stub**

Write `roles/dotfiles/files/hermes/skills/ingest-pipeline/SKILL.md`:

```markdown
---
name: ingest-pipeline
description: Drive a directory containing a large PDF, pre-split PDFs, pre-split markdown, or a partial mdBook to a buildable mdBook. Idempotent and resumable.
---

# Ingest Pipeline

Stub — full content lands in Task 8.
```

- [ ] **Step 3: Create the batch skill directory and SKILL.md stub**

```bash
mkdir -p roles/dotfiles/files/hermes/skills/ingest-pipeline-batch
```

Write `roles/dotfiles/files/hermes/skills/ingest-pipeline-batch/SKILL.md`:

```markdown
---
name: ingest-pipeline-batch
description: Sweep a library directory and run ingest-pipeline on every book root that is not already complete.
---

# Ingest Pipeline — Batch

Stub — full content lands in Task 9.
```

- [ ] **Step 4: Register both skills in hermes.yml**

Open `roles/dotfiles/defaults/main/hermes.yml`. Find the existing `pdf-to-mdbook` entry at the end of `hermes_skills` (lines around 83–85). Append the two new entries directly after it.

Edit `roles/dotfiles/defaults/main/hermes.yml` — replace:

```yaml
  - name: "pdf-to-mdbook"
    description: "Convert PDF research papers and textbooks into fully structured mdBooks — handles scanned and text-layered PDFs, reconstructs TOC and indices, converts tables to markdown, extracts images, and uses vision-capable LLM for complex pages"
    content_file: "hermes/skills/pdf-to-mdbook/SKILL.md"
```

with:

```yaml
  - name: "pdf-to-mdbook"
    description: "Convert PDF research papers and textbooks into fully structured mdBooks — handles scanned and text-layered PDFs, reconstructs TOC and indices, converts tables to markdown, extracts images, and uses vision-capable LLM for complex pages"
    content_file: "hermes/skills/pdf-to-mdbook/SKILL.md"
  - name: "ingest-pipeline"
    description: "Drive any PDF/markdown directory to a buildable mdBook — handles large PDFs, pre-split PDFs, pre-split markdown, partial mdBooks; idempotent and resumable. Calls split-textbooks and pdf-to-mdbook as Hermes subagents."
    content_file: "hermes/skills/ingest-pipeline/SKILL.md"
  - name: "ingest-pipeline-batch"
    description: "Sweep a library directory and run ingest-pipeline on every book root that is not already complete."
    content_file: "hermes/skills/ingest-pipeline-batch/SKILL.md"
```

(The pdf-to-mdbook description gets a more comprehensive update in Task 7 — for now leave it unchanged.)

- [ ] **Step 5: Run Ansible syntax check**

Run: `ansible-playbook --syntax-check ars.yml`

Expected: exits 0; output ends with `playbook: ars.yml`.

If you get a YAML parse error on `hermes.yml`, double-check indentation matches the existing entries (two-space indent, list item starts with `- name:`).

- [ ] **Step 6: Run Ansible check-mode against the dotfiles role**

Run: `ansible-playbook --check --diff ars.yml --tags hermes 2>&1 | head -200`

Expected: shows planned creation of `~/.hermes/skills/ingest-pipeline/SKILL.md` and `~/.hermes/skills/ingest-pipeline-batch/SKILL.md`. Exits 0.

If the `hermes` tag is not bound, fall back to `--start-at-task 'Hermes | Create per-skill directories'` to trigger the relevant block.

- [ ] **Step 7: Commit**

```bash
git add roles/dotfiles/files/hermes/skills/ingest-pipeline \
        roles/dotfiles/files/hermes/skills/ingest-pipeline-batch \
        roles/dotfiles/defaults/main/hermes.yml
git commit -m "$(cat <<'EOF'
hermes: scaffold ingest-pipeline and ingest-pipeline-batch skills

Stub SKILL.md files registered in hermes_skills so the deployment path is
verified before the real content lands. References dir created with
.gitkeep for the per-book skill.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Write `references/manifest-schema.md`

**Purpose:** Lift the `pipeline.json` schema out of the SKILL.md into a reference doc the engine reads on demand. Keeps the SKILL.md focused on flow; lets the agent re-load the schema only when it needs to write a manifest.

**Files:**
- Create: `roles/dotfiles/files/hermes/skills/ingest-pipeline/references/manifest-schema.md`

- [ ] **Step 1: Write the manifest schema reference**

Write `roles/dotfiles/files/hermes/skills/ingest-pipeline/references/manifest-schema.md`:

````markdown
# `pipeline.json` Schema

`pipeline.json` is the orchestrator's manifest, written at the book root by
`ingest-pipeline`. It is layered on top of (never replaces) the per-skill
manifests written by `split-textbooks` and `pdf-to-mdbook`.

## Schema (schema_version: 1)

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

## Field semantics

| Field | Type | Meaning |
|-------|------|---------|
| `schema_version` | int | Always `1` for this recipe. |
| `skill` | string | Always `"ingest-pipeline"`. |
| `book_root` | string (abs path) | Directory holding the book; never moves on rerun. |
| `input_target` | string (abs path) | What the user invoked the engine with. May be a file (single PDF) or `book_root` itself. |
| `initial_state` | enum `S0`–`S5` | State on first invocation; **never overwritten** on rerun. |
| `current_state` | enum `S0`–`S5` | State on most recent invocation. Updated each run. |
| `status` | enum `pending` \| `in_progress` \| `complete` \| `failed` | The marker `--force`-less reruns check. |
| `started_at` / `updated_at` | ISO 8601 UTC | Clock from the host. |
| `phases` | array | **Append-only** log of work done. Reruns append; do not overwrite prior entries. |
| `phases[].name` | enum `split` \| `mdbook` \| `scaffold` \| `build` | Which logical phase this entry represents. |
| `phases[].skill` | string \| `null` | Name of the sub-skill invoked, or `null` for in-orchestrator inline work. |
| `phases[].status` | enum `pending` \| `in_progress` \| `complete` \| `failed` | Phase-local status. |
| `phases[].manifest` | string (relative path) | Path to the sub-skill's `manifest.json` (relative to `book_root`). |
| `phases[].subagent_invocation_id` | string | Opaque ID returned by Hermes' subagent delegation. Retained for log retracing. |
| `failed_phase` | enum \| `null` | When `status: failed`, which phase tipped over. |
| `error_message` | string \| `null` | Free-form error from the failed phase. |
| `notes` | array of strings | Free-form reconciliations (e.g., `"filesystem reclassified to S2 from S5; user deleted mdbook dir"`). |

## Crash safety

Before invoking each subagent: write `pipeline.json` with `status: in_progress` and the new phase as `pending`. After the subagent returns: update the phase entry to `complete` or `failed`. If the run is interrupted mid-phase, the next run reads partial `pipeline.json`, reconciles with filesystem state, and resumes.

## Filesystem-truth rule

If `pipeline.json` claims `status: complete` but the corresponding output
directory (`<stem>-mdbook/` or referenced files) is missing, **trust the
filesystem**. Reclassify state via the algorithm in `state-detection.md`,
append a `notes` entry recording the reconciliation, and reset `status` to
`in_progress`. Do not error.

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
````

- [ ] **Step 2: Verify the file is well-formed**

Run: `head -10 roles/dotfiles/files/hermes/skills/ingest-pipeline/references/manifest-schema.md`

Expected: starts with `# \`pipeline.json\` Schema`.

Run: `wc -l roles/dotfiles/files/hermes/skills/ingest-pipeline/references/manifest-schema.md`

Expected: between 70 and 110 lines.

- [ ] **Step 3: Commit**

```bash
git add roles/dotfiles/files/hermes/skills/ingest-pipeline/references/manifest-schema.md
git commit -m "$(cat <<'EOF'
hermes(ingest-pipeline): add manifest-schema.md reference

Documents the pipeline.json schema, field semantics, crash-safety rules,
filesystem-truth reconciliation, and the library.json schema for the
batch wrapper.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Write `references/state-detection.md`

**Purpose:** Lift the six-state classifier algorithm out of the SKILL.md into a reference doc. The classifier runs on every invocation and after every phase, so isolating it lets the agent re-load only this when reclassifying.

**Files:**
- Create: `roles/dotfiles/files/hermes/skills/ingest-pipeline/references/state-detection.md`

- [ ] **Step 1: Write the state detection reference**

Write `roles/dotfiles/files/hermes/skills/ingest-pipeline/references/state-detection.md`:

````markdown
# State Detection Algorithm

`ingest-pipeline` classifies an input target into one of six states, then
drives it forward to S5 by dispatching to existing skills.

## States

| #   | State              | Detection                                                                                                                             | Next action                                                                              |
|-----|--------------------|---------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| S0  | Empty / unrelated  | Target absent, OR directory has no `*.pdf`, no `*.md`, and no manifest                                                                | Abort with diagnostic; no partial work.                                                  |
| S1  | Single large PDF   | Target is a `.pdf` file, OR directory contains exactly one `.pdf` and zero `.md`                                                      | Run `split-textbooks` subagent → produces sliced PDFs + `manifest.json`. Reclassify (becomes S2). |
| S2  | Pre-split PDFs     | Directory contains ≥2 `.pdf` files matching `^\d{2}-[a-z0-9-]+\.pdf$`, OR a `split-textbooks` `manifest.json` with `status: complete` | Run `pdf-to-mdbook` subagent (slice-dir mode). Reclassify (becomes S4).                  |
| S3  | Pre-split markdown | Directory contains ≥2 `.md` and zero `book.toml`, OR `split-textbooks` `manifest.json` with `markdown_generated: true`                | Scaffold an mdBook directly (inline; no subagent): write `book.toml`, `src/SUMMARY.md`, copy files into `src/`. |
| S4  | Partial mdBook     | Directory contains both `book.toml` AND `src/SUMMARY.md` AND no `pipeline.json` with `status: complete`                               | Diagnose missing referenced files, fill stubs if needed, run `mdbook build`. On success → S5. |
| S5  | Complete           | `pipeline.json` exists with `status: complete` AND mdBook builds cleanly                                                              | No-op unless `--force`. Print "already complete" and stop.                               |

## Algorithm

Run on every invocation, including reruns:

1. Resolve the target to an absolute path. Identify whether it's a file or
   directory.
2. Determine `book_root`:
   - If target is a file: `book_root = dirname(target)`.
   - If target is a directory: `book_root = target`.
3. If `book_root/pipeline.json` exists with `status: complete` AND `--force`
   was not passed → **return S5**.
4. Else if `book_root/book.toml` AND `book_root/src/SUMMARY.md` both exist →
   **return S4**.
5. Else if `book_root/manifest.json` exists (the `split-textbooks` manifest):
   - If `markdown_generated: true` → **return S3**.
   - Else if `status: complete` → **return S2**.
   - Else if `status: failed` → respect `failed_step`; resume there. Reclassify
     based on what files are actually present (fall through to step 6).
6. Else count files at the top level of `book_root`:
   - ≥2 `.md` and 0 `.pdf` → **return S3**.
   - ≥2 `.pdf` matching `^\d{2}-[a-z0-9-]+\.pdf$` → **return S2**.
   - exactly one `.pdf` (or the original target itself was a `.pdf`) →
     **return S1**.
7. **Return S0** otherwise.

## Filesystem-truth rule

Always inspect the filesystem before trusting `pipeline.json`. If the manifest
disagrees with what's actually on disk, trust the filesystem and reclassify.
Append a `notes` entry recording the reconciliation. Never error on
disagreement.

Examples:

| `pipeline.json` says | Filesystem shows                              | Resolution                                         |
|----------------------|-----------------------------------------------|----------------------------------------------------|
| `status: complete`   | `<stem>-mdbook/` directory missing            | Reclassify (probably S2 or S4). Reset to in_progress. |
| `current_state: S2`  | `book.toml` present                           | Reclassify S4. Update `current_state` on next write. |
| `status: in_progress`, last phase `split` `complete` | Slice files all present, no mdbook dir | S2 — resume at the mdbook phase.                  |

## State transitions

The classifier re-runs after every phase, giving "drive forward to S5" semantics:

```
S1 ──split-textbooks──▶ S2 ──pdf-to-mdbook──▶ S4 ──mdbook build──▶ S5
S3 ──scaffold inline───▶ S4 ──mdbook build──▶ S5
S4 ──mdbook build──────▶ S5
S0 ──abort
```

If any phase fails, the orchestrator sets `pipeline.json` `status: failed`,
populates `failed_phase` and `error_message`, and stops. Rerun resumes by
reclassifying from the current filesystem state.
````

- [ ] **Step 2: Verify the file is well-formed**

Run: `head -10 roles/dotfiles/files/hermes/skills/ingest-pipeline/references/state-detection.md`

Expected: starts with `# State Detection Algorithm`.

Run: `wc -l roles/dotfiles/files/hermes/skills/ingest-pipeline/references/state-detection.md`

Expected: between 60 and 100 lines.

- [ ] **Step 3: Remove the .gitkeep placeholder**

```bash
rm -f roles/dotfiles/files/hermes/skills/ingest-pipeline/references/.gitkeep
```

- [ ] **Step 4: Commit**

```bash
git add roles/dotfiles/files/hermes/skills/ingest-pipeline/references/state-detection.md \
        roles/dotfiles/files/hermes/skills/ingest-pipeline/references/.gitkeep
git commit -m "$(cat <<'EOF'
hermes(ingest-pipeline): add state-detection.md reference

Documents the six-state classifier (S0 empty → S5 complete), the detection
algorithm step-by-step, the filesystem-truth reconciliation rule, and
state-transition semantics.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Build test fixtures (S0–S5 + library + edge cases)

**Purpose:** Concrete fixture directories the harness can verify against. The fixtures are also documentation: an engineer reading them sees exactly what each input state looks like. Synthetic PDFs are tiny (≤4 pages each), generated by `make-fixtures.sh`, then committed as binaries so subsequent test runs do not require the generator.

**Files:**
- Create: `roles/dotfiles/tests/hermes/make-fixtures.sh`
- Create: `roles/dotfiles/tests/hermes/fixtures/README.md`
- Create: `roles/dotfiles/tests/hermes/fixtures/s0-empty/.gitkeep`
- Create: `roles/dotfiles/tests/hermes/fixtures/s1-single-pdf/book.pdf`
- Create: `roles/dotfiles/tests/hermes/fixtures/s2-pre-split-pdfs/01-intro.pdf`
- Create: `roles/dotfiles/tests/hermes/fixtures/s2-pre-split-pdfs/02-body.pdf`
- Create: `roles/dotfiles/tests/hermes/fixtures/s2-pre-split-pdfs/manifest.json`
- Create: `roles/dotfiles/tests/hermes/fixtures/s3-pre-split-md/01-intro.md`
- Create: `roles/dotfiles/tests/hermes/fixtures/s3-pre-split-md/02-body.md`
- Create: `roles/dotfiles/tests/hermes/fixtures/s4-partial-mdbook/book.toml`
- Create: `roles/dotfiles/tests/hermes/fixtures/s4-partial-mdbook/src/SUMMARY.md`
- Create: `roles/dotfiles/tests/hermes/fixtures/s4-partial-mdbook/src/README.md`
- Create: `roles/dotfiles/tests/hermes/fixtures/s4-partial-mdbook/src/01-intro.md`
- Create: `roles/dotfiles/tests/hermes/fixtures/s5-complete/book.pdf`
- Create: `roles/dotfiles/tests/hermes/fixtures/s5-complete/pipeline.json`
- Create: `roles/dotfiles/tests/hermes/fixtures/s5-complete/book-mdbook/book.toml`
- Create: `roles/dotfiles/tests/hermes/fixtures/stale-pipeline-json/book.pdf`
- Create: `roles/dotfiles/tests/hermes/fixtures/stale-pipeline-json/pipeline.json`
- Create: `roles/dotfiles/tests/hermes/fixtures/library/calculus/book.pdf`
- Create: `roles/dotfiles/tests/hermes/fixtures/library/probability/book.pdf`
- Create: `roles/dotfiles/tests/hermes/fixtures/library/probability/pipeline.json`
- Create: `roles/dotfiles/tests/hermes/fixtures/library/probability/probability-mdbook/book.toml`
- Create: `roles/dotfiles/tests/hermes/fixtures/library/discrete-math/book.pdf`

- [ ] **Step 1: Create the directory tree**

```bash
mkdir -p roles/dotfiles/tests/hermes/fixtures/{s0-empty,s1-single-pdf,s2-pre-split-pdfs,s3-pre-split-md,s4-partial-mdbook/src,s5-complete/book-mdbook,stale-pipeline-json}
mkdir -p roles/dotfiles/tests/hermes/fixtures/library/{calculus,probability/probability-mdbook,discrete-math}
touch roles/dotfiles/tests/hermes/fixtures/s0-empty/.gitkeep
```

- [ ] **Step 2: Write the fixture-generator script**

Write `roles/dotfiles/tests/hermes/make-fixtures.sh`:

```bash
#!/usr/bin/env bash
# Regenerate the synthetic-PDF fixtures used by the ingest-pipeline test harness.
# Usage: ./make-fixtures.sh
# Requires: python3 with reportlab installed (pip install reportlab) OR pandoc.
set -euo pipefail

FIX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/fixtures"

generate_pdf() {
  local out_path="$1" title="$2"
  if python3 -c 'import reportlab' 2>/dev/null; then
    python3 - "$out_path" "$title" <<'PY'
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

out_path, title = sys.argv[1], sys.argv[2]
c = canvas.Canvas(out_path, pagesize=letter)
for i in range(1, 5):
    c.setFont("Helvetica-Bold", 18)
    c.drawString(72, 720, f"{title} — Page {i}")
    c.setFont("Helvetica", 12)
    c.drawString(72, 690, f"This is synthetic page {i} of {title}.")
    c.drawString(72, 670, "Generated for ingest-pipeline test fixtures.")
    c.showPage()
c.save()
PY
  elif command -v pandoc >/dev/null 2>&1; then
    local tmp
    tmp="$(mktemp -t fixmd.XXXXXX.md)"
    {
      echo "# $title"
      for i in 1 2 3 4; do
        echo
        echo "## Page $i"
        echo
        echo "This is synthetic page $i of $title."
      done
    } > "$tmp"
    pandoc -o "$out_path" "$tmp"
    rm -f "$tmp"
  else
    echo "make-fixtures: need python3+reportlab or pandoc on PATH" >&2
    exit 1
  fi
}

# Single-PDF fixtures
generate_pdf "$FIX_DIR/s1-single-pdf/book.pdf" "Single Large PDF"
generate_pdf "$FIX_DIR/s5-complete/book.pdf" "Complete Book"
generate_pdf "$FIX_DIR/stale-pipeline-json/book.pdf" "Stale Pipeline JSON"

# Slice fixtures (S2)
generate_pdf "$FIX_DIR/s2-pre-split-pdfs/01-intro.pdf" "Chapter 1 — Introduction"
generate_pdf "$FIX_DIR/s2-pre-split-pdfs/02-body.pdf" "Chapter 2 — Body"

# Library fixtures
generate_pdf "$FIX_DIR/library/calculus/book.pdf" "Calculus"
generate_pdf "$FIX_DIR/library/probability/book.pdf" "Probability"

# Library — discrete-math is intentionally a corrupt PDF (zero-byte)
: > "$FIX_DIR/library/discrete-math/book.pdf"

echo "Fixtures regenerated under $FIX_DIR"
```

Make it executable:

```bash
chmod +x roles/dotfiles/tests/hermes/make-fixtures.sh
```

- [ ] **Step 3: Run the generator**

Run: `roles/dotfiles/tests/hermes/make-fixtures.sh`

Expected stdout: `Fixtures regenerated under <abs path>`. Exit 0.

If the script reports "need python3+reportlab or pandoc", install one — `pip install reportlab` is the lightest option.

Verify PDFs exist and are valid:

```bash
for f in roles/dotfiles/tests/hermes/fixtures/s1-single-pdf/book.pdf \
         roles/dotfiles/tests/hermes/fixtures/s2-pre-split-pdfs/01-intro.pdf \
         roles/dotfiles/tests/hermes/fixtures/s2-pre-split-pdfs/02-body.pdf \
         roles/dotfiles/tests/hermes/fixtures/s5-complete/book.pdf; do
  pdfinfo "$f" >/dev/null && echo "OK $f"
done
```

Expected: four `OK ...` lines.

For `library/discrete-math/book.pdf` (zero-byte intentionally corrupt), `pdfinfo` should fail — verify with: `pdfinfo roles/dotfiles/tests/hermes/fixtures/library/discrete-math/book.pdf 2>&1 | head -1` — expect `Syntax Error: ...`.

- [ ] **Step 4: Write the S2 manifest.json**

Write `roles/dotfiles/tests/hermes/fixtures/s2-pre-split-pdfs/manifest.json`:

```json
{
  "schema_version": 2,
  "source_pdf": "book.pdf",
  "canonical_pdf": "book.pdf",
  "is_scanned": false,
  "page_count": 8,
  "page_offset": 0,
  "detection_method": "bookmarks",
  "markdown_generated": false,
  "cleanup_method": "none",
  "cleanup_fallbacks": [],
  "status": "complete",
  "generated_at": "2026-05-04T10:00:00Z",
  "tool_versions": {
    "pdftotext": "24.08.0",
    "qpdf": "11.9.0"
  },
  "sections": [
    {
      "index": 1,
      "kind": "chapter",
      "title": "Chapter 1 — Introduction",
      "slug": "chapter-1-introduction",
      "filename": "01-intro",
      "start_page": 1,
      "end_page": 4
    },
    {
      "index": 2,
      "kind": "chapter",
      "title": "Chapter 2 — Body",
      "slug": "chapter-2-body",
      "filename": "02-body",
      "start_page": 5,
      "end_page": 8
    }
  ],
  "failed_step": null,
  "error_message": null
}
```

- [ ] **Step 5: Write the S3 markdown fixtures**

Write `roles/dotfiles/tests/hermes/fixtures/s3-pre-split-md/01-intro.md`:

```markdown
# Chapter 1 — Introduction

This is the introduction chapter as already-extracted markdown.
```

Write `roles/dotfiles/tests/hermes/fixtures/s3-pre-split-md/02-body.md`:

```markdown
# Chapter 2 — Body

This is the body chapter as already-extracted markdown.
```

- [ ] **Step 6: Write the S4 partial mdBook fixtures**

Write `roles/dotfiles/tests/hermes/fixtures/s4-partial-mdbook/book.toml`:

```toml
[book]
title = "Partial mdBook"
authors = ["Test"]
language = "en"
multilingual = false
src = "src"

[build]
build-dir = "book"
create-missing = false
```

Write `roles/dotfiles/tests/hermes/fixtures/s4-partial-mdbook/src/SUMMARY.md`:

```markdown
# Summary

[Introduction](README.md)

- [Chapter 1: Intro](01-intro.md)
```

Write `roles/dotfiles/tests/hermes/fixtures/s4-partial-mdbook/src/README.md`:

```markdown
# Partial mdBook

A test fixture exercising the S4 → S5 transition.
```

Write `roles/dotfiles/tests/hermes/fixtures/s4-partial-mdbook/src/01-intro.md`:

```markdown
# Chapter 1 — Intro

S4 fixture body content.
```

- [ ] **Step 7: Write the S5 complete fixture**

Write `roles/dotfiles/tests/hermes/fixtures/s5-complete/pipeline.json`:

```json
{
  "schema_version": 1,
  "skill": "ingest-pipeline",
  "book_root": "FIXTURE",
  "input_target": "FIXTURE/book.pdf",
  "initial_state": "S1",
  "current_state": "S5",
  "status": "complete",
  "started_at": "2026-05-04T09:00:00Z",
  "updated_at": "2026-05-04T09:30:00Z",
  "phases": [
    { "name": "split", "skill": "split-textbooks", "status": "complete", "manifest": "manifest.json", "started_at": "2026-05-04T09:00:00Z", "completed_at": "2026-05-04T09:10:00Z", "subagent_invocation_id": "sa-test-split" },
    { "name": "mdbook", "skill": "pdf-to-mdbook", "status": "complete", "manifest": "book-mdbook/manifest.json", "started_at": "2026-05-04T09:10:00Z", "completed_at": "2026-05-04T09:29:00Z", "subagent_invocation_id": "sa-test-mdbook" },
    { "name": "build", "skill": null, "status": "complete", "started_at": "2026-05-04T09:29:00Z", "completed_at": "2026-05-04T09:30:00Z" }
  ],
  "failed_phase": null,
  "error_message": null,
  "notes": []
}
```

Note: `book_root` and `input_target` are `FIXTURE` placeholders — the harness substitutes the real absolute path at test-time so tests are portable across machines.

Write `roles/dotfiles/tests/hermes/fixtures/s5-complete/book-mdbook/book.toml`:

```toml
[book]
title = "Complete Book"
authors = ["Test"]
language = "en"
multilingual = false
src = "src"
```

- [ ] **Step 8: Write the stale-pipeline-json fixture**

This is the fixture that proves filesystem-truth reconciliation. `pipeline.json`
claims `status: complete`, but `<stem>-mdbook/` is missing.

Write `roles/dotfiles/tests/hermes/fixtures/stale-pipeline-json/pipeline.json`:

```json
{
  "schema_version": 1,
  "skill": "ingest-pipeline",
  "book_root": "FIXTURE",
  "input_target": "FIXTURE/book.pdf",
  "initial_state": "S1",
  "current_state": "S5",
  "status": "complete",
  "started_at": "2026-05-04T08:00:00Z",
  "updated_at": "2026-05-04T08:30:00Z",
  "phases": [
    { "name": "split", "skill": "split-textbooks", "status": "complete", "manifest": "manifest.json", "started_at": "2026-05-04T08:00:00Z", "completed_at": "2026-05-04T08:10:00Z", "subagent_invocation_id": "sa-stale-split" },
    { "name": "mdbook", "skill": "pdf-to-mdbook", "status": "complete", "manifest": "book-mdbook/manifest.json", "started_at": "2026-05-04T08:10:00Z", "completed_at": "2026-05-04T08:29:00Z", "subagent_invocation_id": "sa-stale-mdbook" },
    { "name": "build", "skill": null, "status": "complete", "started_at": "2026-05-04T08:29:00Z", "completed_at": "2026-05-04T08:30:00Z" }
  ],
  "failed_phase": null,
  "error_message": null,
  "notes": []
}
```

There is **no `book-mdbook/` directory** here. The classifier should reclassify
to S1 (single PDF present). This fixture exercises the filesystem-truth rule.

- [ ] **Step 9: Write the library fixtures**

Library: three books at three different states.

Write `roles/dotfiles/tests/hermes/fixtures/library/probability/pipeline.json`:

```json
{
  "schema_version": 1,
  "skill": "ingest-pipeline",
  "book_root": "FIXTURE/library/probability",
  "input_target": "FIXTURE/library/probability/book.pdf",
  "initial_state": "S1",
  "current_state": "S5",
  "status": "complete",
  "started_at": "2026-05-04T07:00:00Z",
  "updated_at": "2026-05-04T07:30:00Z",
  "phases": [
    { "name": "split", "skill": "split-textbooks", "status": "complete", "manifest": "manifest.json", "started_at": "2026-05-04T07:00:00Z", "completed_at": "2026-05-04T07:10:00Z", "subagent_invocation_id": "sa-prob-split" },
    { "name": "mdbook", "skill": "pdf-to-mdbook", "status": "complete", "manifest": "probability-mdbook/manifest.json", "started_at": "2026-05-04T07:10:00Z", "completed_at": "2026-05-04T07:29:00Z", "subagent_invocation_id": "sa-prob-mdbook" },
    { "name": "build", "skill": null, "status": "complete", "started_at": "2026-05-04T07:29:00Z", "completed_at": "2026-05-04T07:30:00Z" }
  ],
  "failed_phase": null,
  "error_message": null,
  "notes": []
}
```

Write `roles/dotfiles/tests/hermes/fixtures/library/probability/probability-mdbook/book.toml`:

```toml
[book]
title = "Probability"
authors = ["Test"]
language = "en"
multilingual = false
src = "src"
```

(`calculus` and `discrete-math` already have just `book.pdf` from Step 3 — that's correct: `calculus` is fresh-S1, `discrete-math` is corrupt-S1-that-fails.)

- [ ] **Step 10: Write the fixtures README**

Write `roles/dotfiles/tests/hermes/fixtures/README.md`:

```markdown
# Ingest Pipeline Test Fixtures

Each subdirectory is a fixture exercising a specific state or behavior of
`ingest-pipeline`.

| Fixture | State | Purpose |
|---------|-------|---------|
| `s0-empty/` | S0 | Empty directory; classifier must abort. |
| `s1-single-pdf/` | S1 | Single large PDF; classifier dispatches to `split-textbooks`. |
| `s2-pre-split-pdfs/` | S2 | Pre-split chapter PDFs + `manifest.json`; classifier dispatches to `pdf-to-mdbook` (slice-dir mode). |
| `s3-pre-split-md/` | S3 | Pre-split markdown; classifier scaffolds an mdBook inline. |
| `s4-partial-mdbook/` | S4 | `book.toml` and `src/SUMMARY.md` already present; classifier runs `mdbook build`. |
| `s5-complete/` | S5 | `pipeline.json` `status: complete` and `book-mdbook/` present; classifier returns "already complete". |
| `stale-pipeline-json/` | S1 | `pipeline.json` claims complete but no `book-mdbook/`; filesystem-truth rule reclassifies to S1. |
| `library/` | mixed | Three books for `ingest-pipeline-batch` — calculus (fresh), probability (complete), discrete-math (corrupt). |

`pipeline.json` files contain `FIXTURE` placeholders for `book_root` and
`input_target`; the harness substitutes the real absolute path at test time so
fixtures are portable across machines.

## Regenerating PDFs

If you change a fixture spec or add a new one, regenerate the PDFs with:

```bash
./make-fixtures.sh
```

Requires `python3` with `reportlab` (`pip install reportlab`) or `pandoc`.

PDFs are committed as binaries so `run-tests.sh` does not require the
generator on every machine.
```

- [ ] **Step 11: Verify all fixture files exist**

Run:

```bash
find roles/dotfiles/tests/hermes/fixtures -type f | sort
```

Expected output:

```
roles/dotfiles/tests/hermes/fixtures/README.md
roles/dotfiles/tests/hermes/fixtures/library/calculus/book.pdf
roles/dotfiles/tests/hermes/fixtures/library/discrete-math/book.pdf
roles/dotfiles/tests/hermes/fixtures/library/probability/book.pdf
roles/dotfiles/tests/hermes/fixtures/library/probability/pipeline.json
roles/dotfiles/tests/hermes/fixtures/library/probability/probability-mdbook/book.toml
roles/dotfiles/tests/hermes/fixtures/s0-empty/.gitkeep
roles/dotfiles/tests/hermes/fixtures/s1-single-pdf/book.pdf
roles/dotfiles/tests/hermes/fixtures/s2-pre-split-pdfs/01-intro.pdf
roles/dotfiles/tests/hermes/fixtures/s2-pre-split-pdfs/02-body.pdf
roles/dotfiles/tests/hermes/fixtures/s2-pre-split-pdfs/manifest.json
roles/dotfiles/tests/hermes/fixtures/s3-pre-split-md/01-intro.md
roles/dotfiles/tests/hermes/fixtures/s3-pre-split-md/02-body.md
roles/dotfiles/tests/hermes/fixtures/s4-partial-mdbook/book.toml
roles/dotfiles/tests/hermes/fixtures/s4-partial-mdbook/src/01-intro.md
roles/dotfiles/tests/hermes/fixtures/s4-partial-mdbook/src/README.md
roles/dotfiles/tests/hermes/fixtures/s4-partial-mdbook/src/SUMMARY.md
roles/dotfiles/tests/hermes/fixtures/s5-complete/book-mdbook/book.toml
roles/dotfiles/tests/hermes/fixtures/s5-complete/book.pdf
roles/dotfiles/tests/hermes/fixtures/s5-complete/pipeline.json
roles/dotfiles/tests/hermes/fixtures/stale-pipeline-json/book.pdf
roles/dotfiles/tests/hermes/fixtures/stale-pipeline-json/pipeline.json
```

- [ ] **Step 12: Validate JSON syntax**

Run:

```bash
for f in $(find roles/dotfiles/tests/hermes/fixtures -name '*.json'); do
  jq empty "$f" && echo "OK $f"
done
```

Expected: every JSON file emits `OK <path>`. No parse errors.

- [ ] **Step 13: Commit**

```bash
git add roles/dotfiles/tests/hermes
git commit -m "$(cat <<'EOF'
hermes(ingest-pipeline): add test fixtures and PDF generator

Six per-state fixtures (s0-empty through s5-complete), a stale-pipeline-json
fixture for the filesystem-truth reconciliation rule, and a three-book
library fixture for the batch wrapper. Synthetic PDFs are generated by
make-fixtures.sh (python3+reportlab or pandoc) and committed as binaries
so the harness does not require the generator on every machine.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Write the test harness `run-tests.sh`

**Purpose:** A shell harness that asserts on fixture validity (always) and optionally invokes Hermes (gated on `HERMES_TEST=1`). The fixture-validity checks alone are useful: they catch malformed JSON, missing files, and PDF corruption regressions whenever fixtures are touched.

**Files:**
- Create: `roles/dotfiles/tests/hermes/run-tests.sh`

- [ ] **Step 1: Write the harness**

Write `roles/dotfiles/tests/hermes/run-tests.sh`:

```bash
#!/usr/bin/env bash
# Test harness for the ingest-pipeline Hermes skill.
#
# By default: runs cheap fixture-validity checks (no Hermes invocation).
# With HERMES_TEST=1 in env: also invokes `hermes` to drive each fixture and
# asserts on the resulting pipeline.json.
#
# Exit 0 on all-pass; non-zero on first failure.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIX="$SCRIPT_DIR/fixtures"

PASS=0
FAIL=0

pass() { printf '\033[0;32mPASS\033[0m %s\n' "$1"; PASS=$((PASS+1)); }
fail() { printf '\033[0;31mFAIL\033[0m %s\n' "$1"; FAIL=$((FAIL+1)); }

require_tools() {
  for tool in jq pdfinfo; do
    if ! command -v "$tool" >/dev/null 2>&1; then
      echo "run-tests: missing required tool: $tool" >&2
      exit 2
    fi
  done
}

# ── Fixture-validity checks (always run) ──────────────────────────────────

check_pdf_valid() {
  local label="$1" path="$2"
  if pdfinfo "$path" >/dev/null 2>&1; then
    pass "PDF valid: $label"
  else
    fail "PDF invalid: $label ($path)"
  fi
}

check_pdf_corrupt() {
  local label="$1" path="$2"
  if pdfinfo "$path" >/dev/null 2>&1; then
    fail "PDF should be corrupt but parses cleanly: $label"
  else
    pass "PDF is intentionally corrupt: $label"
  fi
}

check_json_valid() {
  local label="$1" path="$2"
  if jq empty "$path" >/dev/null 2>&1; then
    pass "JSON valid: $label"
  else
    fail "JSON invalid: $label ($path)"
  fi
}

check_file_exists() {
  local label="$1" path="$2"
  if [ -e "$path" ]; then
    pass "File exists: $label"
  else
    fail "File missing: $label ($path)"
  fi
}

run_fixture_checks() {
  echo "── Fixture validity ──"

  # PDFs that must be valid
  check_pdf_valid "s1-single-pdf/book.pdf"            "$FIX/s1-single-pdf/book.pdf"
  check_pdf_valid "s2 slice 1"                         "$FIX/s2-pre-split-pdfs/01-intro.pdf"
  check_pdf_valid "s2 slice 2"                         "$FIX/s2-pre-split-pdfs/02-body.pdf"
  check_pdf_valid "s5-complete/book.pdf"               "$FIX/s5-complete/book.pdf"
  check_pdf_valid "stale-pipeline-json/book.pdf"       "$FIX/stale-pipeline-json/book.pdf"
  check_pdf_valid "library/calculus/book.pdf"          "$FIX/library/calculus/book.pdf"
  check_pdf_valid "library/probability/book.pdf"       "$FIX/library/probability/book.pdf"

  # PDF that must be intentionally corrupt
  check_pdf_corrupt "library/discrete-math/book.pdf"   "$FIX/library/discrete-math/book.pdf"

  # JSON files that must parse
  check_json_valid "s2 manifest.json"                  "$FIX/s2-pre-split-pdfs/manifest.json"
  check_json_valid "s5 pipeline.json"                  "$FIX/s5-complete/pipeline.json"
  check_json_valid "stale-pipeline-json"               "$FIX/stale-pipeline-json/pipeline.json"
  check_json_valid "library/probability pipeline.json" "$FIX/library/probability/pipeline.json"

  # Markdown / TOML existence
  check_file_exists "s3 markdown 1"                    "$FIX/s3-pre-split-md/01-intro.md"
  check_file_exists "s3 markdown 2"                    "$FIX/s3-pre-split-md/02-body.md"
  check_file_exists "s4 book.toml"                     "$FIX/s4-partial-mdbook/book.toml"
  check_file_exists "s4 SUMMARY.md"                    "$FIX/s4-partial-mdbook/src/SUMMARY.md"
  check_file_exists "s5 book-mdbook/book.toml"         "$FIX/s5-complete/book-mdbook/book.toml"

  # S0 must be empty (only .gitkeep)
  if [ "$(find "$FIX/s0-empty" -type f ! -name '.gitkeep' | wc -l)" = "0" ]; then
    pass "s0-empty contains only .gitkeep"
  else
    fail "s0-empty should be empty (no PDFs / markdown)"
  fi

  # S2 manifest must say status: complete
  if [ "$(jq -r '.status' "$FIX/s2-pre-split-pdfs/manifest.json")" = "complete" ]; then
    pass "s2 manifest.json status == complete"
  else
    fail "s2 manifest.json status should be 'complete'"
  fi

  # S5 pipeline.json must say status: complete
  if [ "$(jq -r '.status' "$FIX/s5-complete/pipeline.json")" = "complete" ]; then
    pass "s5 pipeline.json status == complete"
  else
    fail "s5 pipeline.json status should be 'complete'"
  fi

  # Stale fixture: pipeline.json says complete but no book-mdbook dir
  if [ ! -d "$FIX/stale-pipeline-json/book-mdbook" ]; then
    pass "stale-pipeline-json has no book-mdbook dir (intentional)"
  else
    fail "stale-pipeline-json should NOT have a book-mdbook dir"
  fi
}

# ── Hermes invocation (opt-in via HERMES_TEST=1) ──────────────────────────

run_hermes_invocation() {
  echo "── Hermes integration (HERMES_TEST=1) ──"

  if ! command -v hermes >/dev/null 2>&1; then
    echo "HERMES_TEST=1 set but \`hermes\` not on PATH; skipping integration tests" >&2
    return 0
  fi

  # Prepare a working-copy of the s1 fixture (do not mutate the committed one).
  local work
  work="$(mktemp -d -t ingest-pipeline.XXXXXX)"
  cp -a "$FIX/s1-single-pdf/." "$work/"

  echo "running ingest-pipeline against $work …"
  if hermes -p "Run the ingest-pipeline skill on the directory $work. Use --vision never. Do not invoke any other skills beyond what the orchestrator dispatches." >/tmp/ingest-pipeline-test.log 2>&1; then
    if [ -f "$work/pipeline.json" ] && [ "$(jq -r '.status' "$work/pipeline.json")" = "complete" ]; then
      pass "Hermes drove s1 fixture to status: complete"
    else
      fail "Hermes ran but pipeline.json missing or status != complete; see /tmp/ingest-pipeline-test.log"
    fi
  else
    fail "Hermes invocation failed; see /tmp/ingest-pipeline-test.log"
  fi

  rm -rf "$work"
}

# ── Main ──────────────────────────────────────────────────────────────────

main() {
  require_tools
  run_fixture_checks
  if [ "${HERMES_TEST:-0}" = "1" ]; then
    run_hermes_invocation
  fi

  echo
  echo "──────────────"
  echo "$PASS passed, $FAIL failed"
  if [ "$FAIL" -gt 0 ]; then
    exit 1
  fi
}

main "$@"
```

Make it executable:

```bash
chmod +x roles/dotfiles/tests/hermes/run-tests.sh
```

- [ ] **Step 2: Run the harness in fixture-only mode**

Run: `roles/dotfiles/tests/hermes/run-tests.sh`

Expected output (color codes elided): something like

```
── Fixture validity ──
PASS PDF valid: s1-single-pdf/book.pdf
PASS PDF valid: s2 slice 1
PASS PDF valid: s2 slice 2
PASS PDF valid: s5-complete/book.pdf
PASS PDF valid: stale-pipeline-json/book.pdf
PASS PDF valid: library/calculus/book.pdf
PASS PDF valid: library/probability/book.pdf
PASS PDF is intentionally corrupt: library/discrete-math/book.pdf
PASS JSON valid: s2 manifest.json
PASS JSON valid: s5 pipeline.json
PASS JSON valid: stale-pipeline-json
PASS JSON valid: library/probability pipeline.json
PASS File exists: s3 markdown 1
PASS File exists: s3 markdown 2
PASS File exists: s4 book.toml
PASS File exists: s4 SUMMARY.md
PASS File exists: s5 book-mdbook/book.toml
PASS s0-empty contains only .gitkeep
PASS s2 manifest.json status == complete
PASS s5 pipeline.json status == complete
PASS stale-pipeline-json has no book-mdbook dir (intentional)

──────────────
21 passed, 0 failed
```

Exit code 0. If any check fails, fix the relevant fixture and rerun.

- [ ] **Step 3: Commit**

```bash
git add roles/dotfiles/tests/hermes/run-tests.sh
git commit -m "$(cat <<'EOF'
hermes(ingest-pipeline): add run-tests.sh harness

Always-run fixture-validity checks (PDF parse, JSON parse, expected file
existence, expected file absence). Opt-in Hermes invocation gated on
HERMES_TEST=1, copies the s1 fixture to a tempdir and asserts the resulting
pipeline.json reaches status: complete.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Add `just test-hermes` task

**Purpose:** Wire the harness into the existing `just` command surface so the engineer can run `just test-hermes` from the repo root without remembering the path.

**Files:**
- Create: `scripts/just/hermes.just`
- Modify: `justfile` (add one import line)

- [ ] **Step 1: Read the top-level `justfile` to confirm current imports**

Run: `cat justfile`

Expected (lines 1–9 are the import block):

```
import 'scripts/just/apps.just'
import 'scripts/just/dev.just'
import 'scripts/just/dotfiles.just'
import 'scripts/just/distrobox.just'
import 'scripts/just/kde.just'
import 'scripts/just/mdbook.just'
import 'scripts/just/niri.just'
import 'scripts/just/node.just'
import 'scripts/just/ucore.just'
```

- [ ] **Step 2: Create the `hermes.just` module**

Write `scripts/just/hermes.just`:

```
test-hermes:
  ./roles/dotfiles/tests/hermes/run-tests.sh

test-hermes-integration:
  HERMES_TEST=1 ./roles/dotfiles/tests/hermes/run-tests.sh

regenerate-hermes-fixtures:
  ./roles/dotfiles/tests/hermes/make-fixtures.sh
```

- [ ] **Step 3: Add the import to the top-level `justfile`**

Edit `justfile`. Insert the new import alphabetically (between `dotfiles.just` and `distrobox.just` would be wrong because `distrobox` comes first in the existing block, which is *not* sorted strictly — match the existing partial-alphabetical order: insert before `kde.just`).

Replace:

```
import 'scripts/just/distrobox.just'
import 'scripts/just/kde.just'
```

with:

```
import 'scripts/just/distrobox.just'
import 'scripts/just/hermes.just'
import 'scripts/just/kde.just'
```

- [ ] **Step 4: Verify just discovers the new commands**

Run: `just --list 2>&1 | grep -E '^\s*test-hermes|regenerate-hermes-fixtures'`

Expected:

```
    test-hermes
    test-hermes-integration
    regenerate-hermes-fixtures
```

(`just --list` prefixes each with two spaces; the grep regex tolerates that.)

- [ ] **Step 5: Run the just task**

Run: `just test-hermes`

Expected: same output as Task 5 Step 2 (`21 passed, 0 failed`). Exit 0.

- [ ] **Step 6: Commit**

```bash
git add justfile scripts/just/hermes.just
git commit -m "$(cat <<'EOF'
just: add hermes test tasks

just test-hermes runs the fixture-validity harness; just
test-hermes-integration adds the HERMES_TEST=1 live-Hermes path; just
regenerate-hermes-fixtures rebuilds synthetic PDFs.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Extend `pdf-to-mdbook` for slice-directory input (Step 0.5)

**Purpose:** Teach `pdf-to-mdbook` to accept a directory of pre-split PDF slices in addition to a single PDF, so the orchestrator can hand off the S2 state without merging slices back together. Bumps the manifest schema to v2.

**Files:**
- Modify: `roles/dotfiles/files/hermes/skills/pdf-to-mdbook/SKILL.md` (insert Step 0.5; update inputs section, manifest schema, and tools)
- Modify: `roles/dotfiles/defaults/main/hermes.yml` (update pdf-to-mdbook description)

- [ ] **Step 1: Update the Inputs section (top of SKILL.md)**

Edit `roles/dotfiles/files/hermes/skills/pdf-to-mdbook/SKILL.md`. Find:

```
## Inputs

The user provides:
- Absolute path to the PDF file.
- `--output-dir <path>` (optional) — mdBook root directory. Default: `<pdf-dir>/<stem>-mdbook/`.
- `--vision <mode>` (optional) — `auto` (default), `always`, or `never`. Controls when the vision LLM pass runs.
- `--force` (optional) — Overwrite existing output directory.
```

Replace with:

```
## Inputs

The user provides one of:
- **A single PDF file** — absolute path. Existing path: Steps 1–7 below.
- **A directory of pre-split PDF slices** (from `split-textbooks`) —
  absolute path. New path: Step 0.5 detects this and skips Steps 1–2.

Optional flags:
- `--output-dir <path>` — mdBook root directory.
  - For PDF input, default: `<pdf-dir>/<stem>-mdbook/`.
  - For directory input, default: `<dir>/<dirname>-mdbook/`.
- `--vision <mode>` — `auto` (default), `always`, or `never`. Controls when the vision LLM pass runs.
- `--force` — Overwrite existing output directory.
```

- [ ] **Step 2: Insert Step 0.5 after Step 0**

In the same file, find the heading line `## Step 1 — Resolve canonical PDF (scanned vs. text-layered)`.

Insert this Step 0.5 block immediately before that heading:

````markdown
## Step 0.5 — Detect input shape (single PDF vs. slice directory)

If the input path is a `.pdf` file, set `slice_mode: false` and proceed to
Step 1 unchanged.

If the input path is a **directory**, set `slice_mode: true` and:

1. **If `<dir>/manifest.json` exists with `schema_version: 2`** (a
   `split-textbooks` manifest), read its `sections` array and use it as the
   canonical section list for this run. Each entry yields:

   ```
   {
     index:           <from manifest>,
     title:           <from manifest>,
     slug:            <from manifest>,
     kind:            <from manifest>,
     start_page:      1,                                       # always 1 (the slice itself)
     end_page:        pdfinfo on <dir>/<filename>.pdf → "Pages"
     slice_filename:  "<filename>.pdf"                          # NEW field for slice mode
   }
   ```

   Skip Steps 1 (canonical resolution) and 2 (outline detection) — the
   slicing already did that work. Set `detection_method: "slice_manifest"`,
   `is_scanned`: copy from the slicing manifest's `is_scanned` field,
   `scan_type`: copy `is_scanned ? "ocr_overlay" : "native"`.

2. **Else if the directory contains slice PDFs** matching
   `^\d{2}-[a-z0-9-]+\.pdf$`, derive the section list from filenames:

   ```
   index           = <NN as int>
   slug            = <slug part>
   title           = title-case of slug with hyphens → spaces
   kind            = applied via the same regex used in Step 2's section-kind
                     classification (case-insensitive match on title)
   start_page      = 1
   end_page        = pdfinfo <slice>.pdf → "Pages"
   slice_filename  = "<NN-slug>.pdf"
   ```

   Set `detection_method: "slice_filenames"`. Run Step 1's scanned-PDF
   detection on the **first** slice as a representative; record `is_scanned`
   and `scan_type` once for the run.

3. **Else** the directory is unrecognized → write `manifest.json` with
   `failed_step: "detect_slices"` and stop.

When `slice_mode: true`, skip Step 1 and Step 2 entirely. Step 3 (scaffold)
proceeds normally; Step 4's per-section extraction loop runs over slices —
read `<dir>/<slice_filename>` instead of `pdftotext -f <start> -l <end>
<canonical>`. Use `pdftotext -layout <dir>/<slice_filename> -` (whole slice
at once) and `pdftoppm -png -r 200 <dir>/<slice_filename> <out>/src/assets/
images/<slug>/page` (every page of the slice). All other extraction logic is
unchanged.

````

- [ ] **Step 3: Update Step 7 (validate build) — no change needed, but verify**

Read `roles/dotfiles/files/hermes/skills/pdf-to-mdbook/SKILL.md` from line `## Step 7 — Validate build` to its end. Confirm that this section does NOT reference `<canonical>` or single-PDF assumptions; it only runs `mdbook build` and reports. (No edit needed — flagging this so the engineer doesn't add unnecessary changes.)

- [ ] **Step 4: Bump the manifest schema and add slice-mode fields**

In `roles/dotfiles/files/hermes/skills/pdf-to-mdbook/SKILL.md`, find Step 6's
manifest example. Replace the JSON block:

```json
{
  "schema_version": 1,
  "source_pdf": "book.pdf",
  ...
}
```

(the entire example block, currently around lines 314–361) with:

```json
{
  "schema_version": 2,
  "slice_mode": false,
  "source_pdf": "book.pdf",
  "source_dir": null,
  "canonical_pdf": "book.ocr.pdf",
  "is_scanned": true,
  "scan_type": "no_text",
  "page_count": 612,
  "page_offset": 12,
  "detection_method": "bookmarks",
  "vision_mode": "auto",
  "mdbook_dir": "book-mdbook",
  "status": "complete",
  "generated_at": "2026-04-29T14:33:00Z",
  "tool_versions": {
    "ocrmypdf": "16.10.4",
    "qpdf": "11.9.0",
    "pdftotext": "24.08.0",
    "mdbook": "0.4.40"
  },
  "sections": [
    {
      "index": 0,
      "kind": "front_matter",
      "title": "Table of Contents",
      "slug": "toc",
      "filename": "toc.md",
      "start_page": 5,
      "end_page": 11,
      "slice_filename": null,
      "strategy": "text"
    },
    {
      "index": 1,
      "kind": "chapter",
      "title": "Chapter 1: Limits",
      "slug": "chapter-01-limits",
      "filename": "01-chapter-01-limits.md",
      "start_page": 19,
      "end_page": 56,
      "slice_filename": null,
      "strategy": "vision"
    }
  ],
  "failed_step": null,
  "error_message": null
}
```

Below the JSON, find the **Field notes** subsection. Replace its current
content with:

```
Field notes:
- `schema_version`: `2` for runs that follow this recipe (slice-mode aware). Manifests at `1` predate slice support.
- `slice_mode`: `true` when input was a directory of slices; `false` when input was a single PDF.
- `source_pdf`: present when `slice_mode: false`. Set to the input PDF filename.
- `source_dir`: present when `slice_mode: true`. Set to the input directory path.
- `canonical_pdf`: present when `slice_mode: false`. Same as `source_pdf` when not scanned.
- `scan_type`: `"no_text"` (no OCR layer, ocrmypdf was run), `"ocr_overlay"` (scanned images with invisible OCR text layer, vision pass required), or `"native"` (digitally-born PDF with reliable text layer).
- `detection_method`: `bookmarks` | `toc_parse` | `llm` | `slice_manifest` | `slice_filenames`.
- `strategy` per section: `"text"`, `"vision"`, or `"mixed"`.
- `vision_mode`: the effective mode used (`auto`/`always`/`never`).
- `slice_filename` per section: relative filename inside `source_dir` when `slice_mode: true`; `null` otherwise.
- `failed_step`: `ocr`, `detect_outline`, `detect_llm`, `detect_slices`, `scaffold`, `extract`, `build`.
```

- [ ] **Step 5: Update the failure-handling table**

Find the **Failure handling** table near the bottom of the SKILL.md. Add one
row to it (between the `Required tool missing` row and the `Source PDF
corrupt` row):

```
| Slice directory unrecognized | Step 0.5 | `failed_step: detect_slices`. No partial work. |
```

- [ ] **Step 6: Update the description in `defaults/main/hermes.yml`**

Edit `roles/dotfiles/defaults/main/hermes.yml`. Find the `pdf-to-mdbook`
entry's description. Replace:

```yaml
    description: "Convert PDF research papers and textbooks into fully structured mdBooks — handles scanned and text-layered PDFs, reconstructs TOC and indices, converts tables to markdown, extracts images, and uses vision-capable LLM for complex pages"
```

with:

```yaml
    description: "Convert a PDF or a directory of pre-split PDF slices into a fully structured mdBook — handles scanned and text-layered PDFs, reconstructs TOC and indices, converts tables to markdown, extracts images, and uses vision-capable LLM for complex pages"
```

- [ ] **Step 7: Verify the SKILL.md still parses cleanly**

Run:

```bash
head -8 roles/dotfiles/files/hermes/skills/pdf-to-mdbook/SKILL.md
```

Expected first line: `---`. Frontmatter intact.

Run:

```bash
grep -nE '^## Step' roles/dotfiles/files/hermes/skills/pdf-to-mdbook/SKILL.md
```

Expected: a section list including `## Step 0.5 — Detect input shape (single PDF vs. slice directory)` between Step 0 and Step 1.

Run: `ansible-playbook --syntax-check ars.yml`

Expected: exits 0.

- [ ] **Step 8: Commit**

```bash
git add roles/dotfiles/files/hermes/skills/pdf-to-mdbook/SKILL.md \
        roles/dotfiles/defaults/main/hermes.yml
git commit -m "$(cat <<'EOF'
hermes(pdf-to-mdbook): accept slice-directory input (schema v2)

New Step 0.5 detects whether the input is a single PDF or a directory of
pre-split slices (from split-textbooks). Slice mode skips Step 1 (canonical
resolution) and Step 2 (outline detection) — the slicing already did that
work — and runs Step 4 extraction per slice instead of per page range.
Manifest schema bumps to 2 with slice_mode, source_dir, and per-section
slice_filename fields. New failed_step: detect_slices.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Write `ingest-pipeline/SKILL.md` (per-book engine)

**Purpose:** The main per-book orchestrator. Classifies the input, dispatches to subagents, manages `pipeline.json`, drives the loop until S5 or failure.

**Files:**
- Modify: `roles/dotfiles/files/hermes/skills/ingest-pipeline/SKILL.md` (replace stub with full content)

- [ ] **Step 1: Replace the stub SKILL.md**

Overwrite `roles/dotfiles/files/hermes/skills/ingest-pipeline/SKILL.md` with:

````markdown
---
name: ingest-pipeline
description: Drive a directory containing a large PDF, pre-split PDFs, pre-split markdown, or a partial mdBook to a buildable mdBook. Idempotent and resumable. Use when the user asks to "ingest", "process a textbook", "build an mdBook from a directory", or "resume a partially processed book".
compatibility: Requires poppler (pdfinfo, pdftotext), qpdf, ocrmypdf, mdbook, jq. Composes existing split-textbooks and pdf-to-mdbook skills via Hermes subagent delegation.
---

# Ingest Pipeline

Drive any of the following inputs forward to a buildable mdBook:

- A single large PDF.
- A directory of already-split chapter PDFs.
- A directory of already-split markdown documents.
- A partially-built mdBook directory (interrupted prior run).

The skill is **idempotent**: rerun on a partial directory resumes from where
the prior run left off. Terminal state is `mdbook build` succeeded; wiki
ingestion is a separate, manual follow-up.

**Required references:**
- `references/state-detection.md` — six-state classifier algorithm.
- `references/manifest-schema.md` — `pipeline.json` schema.

## Inputs

The user provides:
- **Absolute path** to a `.pdf` file OR a directory.
- `--force` (optional) — Re-run from scratch even if `pipeline.json` says `status: complete`.
- `--vision <mode>` (optional) — Forwarded to `pdf-to-mdbook`; default `auto`.

## Step 0 — Environment self-check

Run:

```bash
command -v pdfinfo pdftotext qpdf ocrmypdf mdbook jq
```

If any are missing, print install hints and abort:
- macOS: `brew install poppler qpdf ocrmypdf mdbook jq`
- Linux/devbox: `devbox add poppler qpdf ocrmypdf mdbook jq`

## Step 1 — Resolve `book_root` and `input_target`

Resolve the user-provided target to an absolute path. Determine `book_root`:
- If target is a `.pdf` file → `book_root = dirname(target)`.
- If target is a directory → `book_root = target`.

Record both as `input_target` and `book_root` for the manifest.

## Step 2 — Classify state

Apply the algorithm in `references/state-detection.md`. The algorithm is the
single source of truth — re-read it whenever you reclassify.

The result is one of `S0` (empty/unrelated) through `S5` (complete). On the
**first** classification of a run, record this as `initial_state`. On every
classification, record this as `current_state`.

## Step 3 — Open or create `pipeline.json`

Path: `<book_root>/pipeline.json`.

- If the file exists, load it. Apply the **filesystem-truth rule** from
  `references/manifest-schema.md`: if the manifest claims complete state but
  the filesystem disagrees, append a `notes` entry, reclassify, and reset
  `status: in_progress`.
- If the file does not exist, create it with:
  - `schema_version: 1`
  - `skill: "ingest-pipeline"`
  - `book_root`, `input_target`, `initial_state`, `current_state`
  - `status: "pending"`
  - `started_at`, `updated_at` from the current UTC time
  - `phases: []`
  - `failed_phase: null`, `error_message: null`, `notes: []`

## Step 4 — Dispatch by state

Run the action for the current state. Each action either advances state (and
loops back to Step 2) or terminates the run.

### S0 — Empty / unrelated

Abort with a diagnostic listing what was checked and what was found:

```
ingest-pipeline: <book_root> contains no PDFs, no markdown, and no
manifest. Nothing to ingest. (Add a PDF or markdown file and rerun.)
```

Do **not** write `pipeline.json` — the directory is not "managed" yet.

### S1 — Single large PDF

Update `pipeline.json`:
- Append a phase entry: `{ name: "split", skill: "split-textbooks", status: "pending", started_at: now }`
- Set top-level `status: "in_progress"`.

Invoke the `split-textbooks` skill via **subagent delegation** with:
- Restricted toolset: `terminal`, `file`.
- Single argument: `<book_root>/<pdf-filename>`.
- Flags: `markdown: false` (we don't want markdown sidecars at this stage —
  `pdf-to-mdbook` will produce its own).

When the subagent returns:
- On success → set the phase entry's `status: "complete"`, `completed_at: now`,
  `manifest: "manifest.json"`, `subagent_invocation_id: <returned id>`.
  Reclassify (loop to Step 2). New state should be S2.
- On failure → set the phase entry's `status: "failed"`, copy the
  sub-skill's `manifest.json` `error_message` into the pipeline-level
  `error_message`, set `failed_phase: "split"`, set top-level `status: "failed"`,
  stop.

### S2 — Pre-split PDFs

Update `pipeline.json`:
- Append phase entry: `{ name: "mdbook", skill: "pdf-to-mdbook", status: "pending", started_at: now }`
- Top-level `status: "in_progress"` (no change if already).

Invoke `pdf-to-mdbook` via subagent delegation with:
- Restricted toolset: `terminal`, `file`, `image` (for the vision pass).
- Single argument: `<book_root>` (the directory).
- Flags: `--vision <user's choice or auto>`. If `--force` was passed at the
  pipeline level, also pass `--force` to the subagent.

`pdf-to-mdbook` Step 0.5 will detect slice-directory input automatically.

When the subagent returns:
- On success → phase `status: "complete"`, `manifest: "<stem>-mdbook/manifest.json"`,
  `completed_at: now`. Reclassify (loop to Step 2). New state should be S4.
- On failure → phase `status: "failed"`, `failed_phase: "mdbook"`, top-level
  `status: "failed"`, populate `error_message`, stop.

### S3 — Pre-split markdown (inline scaffold)

Update `pipeline.json`:
- Append phase entry: `{ name: "scaffold", skill: null, status: "pending", started_at: now }`

Inline (no subagent — this is small):

1. Compute `<stem>` from `book_root`'s basename.
2. Compute output dir: `<book_root>/<stem>-mdbook/`.
3. If output dir exists and `--force` not passed → abort with phase
   `status: "failed"`, `failed_phase: "scaffold"`, message `"output dir exists; pass --force to overwrite"`.
4. Otherwise create output dir tree:
   ```
   mkdir -p <out>/src/assets/images
   ```
5. Write `<out>/book.toml`:
   ```toml
   [book]
   title = "<title-case of stem>"
   authors = ["Unknown"]
   language = "en"
   multilingual = false
   src = "src"

   [build]
   build-dir = "book"
   create-missing = false
   ```
6. List the `.md` files at the top level of `<book_root>` (not recursive),
   sort lexicographically.
7. Copy each into `<out>/src/`. Preserve filenames.
8. Write `<out>/src/SUMMARY.md`:
   ```markdown
   # Summary

   [Introduction](README.md)

   - [<title from filename 1>](<filename 1>)
   - [<title from filename 2>](<filename 2>)
   ...
   ```
   For the title, strip the leading `NN-` if present and Title-Case the slug
   (replace hyphens with spaces).
9. Write `<out>/src/README.md` (one-line description if missing):
   ```markdown
   # <Title>

   Generated from pre-split markdown by ingest-pipeline.
   ```

Set the phase's `status: "complete"`, `completed_at: now`. Reclassify (loop
to Step 2). New state should be S4.

### S4 — Partial mdBook (inline build)

Update `pipeline.json`:
- Append phase entry: `{ name: "build", skill: null, status: "pending", started_at: now }`

Inline:

1. Find the mdBook root: a directory under `book_root` containing both
   `book.toml` and `src/SUMMARY.md`.
2. Diagnose missing files referenced by `src/SUMMARY.md`:
   ```bash
   grep -oE '\[.*\]\([^)]+\.md\)' <out>/src/SUMMARY.md | sed -E 's/.*\(([^)]+)\).*/\1/'
   ```
   For each referenced filename, if it does not exist under `<out>/src/`,
   create a stub file with content:
   ```markdown
   # <Title from SUMMARY.md link>

   <!-- TODO: content -->
   ```
3. Run `mdbook build` from inside the mdBook root:
   ```bash
   cd <out> && mdbook build
   ```
4. On non-zero exit, capture stderr. Try one auto-fix round:
   - Broken table syntax → reformat as fenced code block.
   - Missing `README.md` → write a one-line stub.
   - Then rerun `mdbook build`.
5. On success → phase `status: "complete"`. Reclassify (loop to Step 2). New
   state should be S5.
6. On failure → phase `status: "failed"`, `failed_phase: "build"`,
   `error_message: <stderr first 500 chars>`, top-level `status: "failed"`, stop.

### S5 — Complete

Set top-level `status: "complete"`. Update `updated_at`. Print:

```
ingest-pipeline: <book_root> is complete.
- mdBook: <out>
- pipeline.json: <book_root>/pipeline.json

To preview: mdbook serve <out>
To re-run anyway: pass --force
```

Stop.

## Step 5 — Reclassify and loop

After every successful phase except S5, return to Step 2. The classifier may
return the same state (idempotent) or advance to the next state. Stop only
on S5 or on `status: failed`.

## Step 6 — Finalize `pipeline.json`

Whenever exiting (S5 success, S0 abort, or any phase failure):
- Set `updated_at: now`.
- For S5: `status: "complete"`.
- For abort/failure: `status: "failed"`, `failed_phase` and `error_message` populated.
- Write the file with pretty JSON (`jq .` formatting).

## Failure handling

The pattern matches `split-textbooks` and `pdf-to-mdbook`: every failure is
recorded; never abort an enclosing batch; user retries with the same command.

| Failure | Where | Behavior |
|---------|-------|----------|
| Required tool missing | Step 0 | Print install hints; abort. No `pipeline.json` written. |
| State classifier returns S0 | Step 2 | Abort with diagnostic. No `pipeline.json` written. |
| `split-textbooks` subagent fails | S1 phase | Phase failed, `failed_phase: "split"`. Stop. |
| `pdf-to-mdbook` subagent fails | S2 phase | Phase failed, `failed_phase: "mdbook"`. Stop. |
| S3 scaffold error | S3 phase | `failed_phase: "scaffold"`. Stop. |
| `mdbook build` fails after auto-fix | S4 phase | `failed_phase: "build"`. Stop. |
| Filesystem inconsistent (book.toml without src/) | Step 2 reclassify | Treat as S4 with damage; record in `notes`; attempt repair. |
| Subagent invocation timeout | Anywhere | Phase failed, `error_message: "subagent invocation failed: <details>"`. Stop. |
| User Ctrl-C | Anywhere | `pipeline.json` left at `status: "in_progress"`. Rerun reconciles via filesystem-truth. |

## Hooks (optional)

If event hooks are configured, the orchestrator emits:
- `pre_phase`: `{ phase, book_root, attempt }` before each subagent invocation or inline phase start.
- `post_phase`: `{ phase, book_root, status, duration_ms, manifest? }` after each phase.
- `pre_destructive`: `{ book_root, reason }` before any phase that would overwrite `status: complete` output (i.e., `--force` on a complete book). Refusing this hook aborts the run.

## Notes

- The orchestrator does **not** call `wiki-ingest`. Hand-off to a wiki is a separate, explicit user action.
- The orchestrator does **not** modify the input PDFs or markdown. All output goes under `book_root`.
- For very large books, expect the S2 phase (vision pass on every page) to dominate runtime. Use `--vision never` if you have clean text layers and want a faster run.
````

- [ ] **Step 2: Verify the file is well-formed**

Run: `head -6 roles/dotfiles/files/hermes/skills/ingest-pipeline/SKILL.md`

Expected: starts with `---` then `name: ingest-pipeline`.

Run: `grep -c '^## Step' roles/dotfiles/files/hermes/skills/ingest-pipeline/SKILL.md`

Expected: `7` (Step 0, Step 1, Step 2, Step 3, Step 4, Step 5, Step 6).

Run: `wc -l roles/dotfiles/files/hermes/skills/ingest-pipeline/SKILL.md`

Expected: 200–280 lines.

- [ ] **Step 3: Confirm Ansible templating still works**

Run: `ansible-playbook --syntax-check ars.yml`

Expected: exits 0.

- [ ] **Step 4: Re-run the harness to confirm fixtures still pass**

Run: `just test-hermes`

Expected: `21 passed, 0 failed`.

- [ ] **Step 5: Commit**

```bash
git add roles/dotfiles/files/hermes/skills/ingest-pipeline/SKILL.md
git commit -m "$(cat <<'EOF'
hermes(ingest-pipeline): write per-book engine SKILL.md

Six-state classifier (S0 empty → S5 complete) dispatching to
split-textbooks and pdf-to-mdbook as Hermes subagents. Inline scaffold for
S3 (pre-split markdown) and inline mdbook build for S4. pipeline.json
written incrementally with crash-safe append-only phases array. Filesystem
is the source of truth on rerun; pipeline.json is the orchestrator's
belief.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: Write `ingest-pipeline-batch/SKILL.md` (library sweep)

**Purpose:** Thin wrapper that walks a library root, identifies book roots, and dispatches `ingest-pipeline` per book. Sequential by default; `--parallel N` for opt-in concurrency.

**Files:**
- Modify: `roles/dotfiles/files/hermes/skills/ingest-pipeline-batch/SKILL.md` (replace stub with full content)

- [ ] **Step 1: Replace the stub SKILL.md**

Overwrite `roles/dotfiles/files/hermes/skills/ingest-pipeline-batch/SKILL.md` with:

````markdown
---
name: ingest-pipeline-batch
description: Sweep a library directory and run ingest-pipeline on every book root that is not already complete. Use when the user asks to "process all books in <dir>", "ingest the library", or "batch convert PDFs to mdBooks".
compatibility: Same as ingest-pipeline (poppler, qpdf, ocrmypdf, mdbook, jq) — invokes ingest-pipeline as a Hermes subagent per book.
---

# Ingest Pipeline — Batch

Walk a library root, identify each book directory, and run `ingest-pipeline`
on the ones that are not already complete. Idempotent across the whole
library: complete books are skipped; failed books retry; in-progress books
resume.

Sequential by default. `--parallel N` opt-in for users who want concurrency
and have the token budget for it.

## Inputs

- **Absolute path** to a library root directory.
- `--force` (optional) — Reprocess every book, even ones marked complete.
- `--parallel <N>` (optional) — Up to N concurrent `ingest-pipeline`
  subagents. Default: `1`.
- `--vision <mode>` (optional) — Forwarded to each per-book `ingest-pipeline`
  invocation; default `auto`.

## Step 0 — Environment self-check

Run:

```bash
command -v pdfinfo pdftotext qpdf ocrmypdf mdbook jq
```

If any are missing, print install hints (same as `ingest-pipeline`) and
abort. The per-book engine will check again, but failing fast at the batch
level avoids spawning N subagents that all immediately abort.

## Step 1 — Load or create `library.json`

Path: `<library_root>/library.json`.

- If exists, load. Use it as the prior-run cache.
- If missing, initialize:
  ```json
  {
    "schema_version": 1,
    "library_root": "<abs path>",
    "last_swept_at": null,
    "books": []
  }
  ```

## Step 2 — Walk the library tree, identify book roots

For every immediate subdirectory of `<library_root>`:

A directory is a "book root" if **any** of the following are true:
- It contains exactly one `.pdf` file at its top level.
- It contains a `pipeline.json` file (already managed).
- It contains a `manifest.json` from `split-textbooks` (mid-process).
- It contains both `book.toml` and `src/SUMMARY.md` (mid-process or done).

Skip directories that match none of the above (likely user-managed
non-book content).

Build the working set: an array of `{ root, abs_path }` entries.

## Step 3 — Filter complete books

For each candidate book root, read `<root>/pipeline.json` if present:
- If `status: "complete"` AND `--force` not passed → drop from working set
  (will be reflected as `complete` in `library.json`).
- Otherwise → keep in working set.

Books with `status: "failed"` are retained — failure was logged, the user
inspected, the rerun is the explicit "try again" signal.

## Step 4 — Dispatch per-book engine

Default sequential (`--parallel 1`):

For each book in the working set, in lexicographic order by root name:

1. Append a stub entry to `library.json` `books`: `{ root, status: "in_progress", pipeline_json: "<root>/pipeline.json" }`.
2. Write `library.json` (so observers see progress).
3. Invoke the `ingest-pipeline` skill via **subagent delegation** with:
   - Restricted toolset: `terminal`, `file`, `image`.
   - Argument: `<abs_path>`.
   - Flags: `--vision <mode>`. If `--force` was passed at the batch level,
     also pass `--force`.
4. When the subagent returns, read `<root>/pipeline.json`:
   - `status: "complete"` → update `library.json` book entry to
     `status: "complete"`.
   - `status: "failed"` → update to
     `status: "failed", failed_phase: <from per-book>`. Continue with
     the next book.
   - any other state → update to `status: "in_progress"` (likely a
     subagent crash mid-phase). Continue.

`--parallel N > 1`:

- Spawn up to N subagents concurrently, drawing from the working set as a
  queue. Cap concurrency at N.
- Use a small write-coalescing window for `library.json` updates: when
  multiple subagents finish at once, batch the writes. Write at least every
  5 seconds and on every state transition.

## Step 5 — Finalize `library.json`

Set `last_swept_at: now`. Sort `books` lexicographically by `root` for
deterministic output. Write the file.

Print a summary:

```
ingest-pipeline-batch: swept <library_root>
- Total books: <N>
- Complete: <X>
- Failed: <Y> (see <library_root>/library.json for details)
- Skipped (already complete): <Z>

Failed books:
- <root>: <failed_phase> — <error_message>
- ...
```

## Failure handling

Batch-level errors **never abort the whole sweep**. Per-book failures are
isolated: one failed book gets its `library.json` entry marked `failed`, and
the next book proceeds.

| Failure | Where | Behavior |
|---------|-------|----------|
| Required tool missing | Step 0 | Print install hints; abort. No `library.json` written if it didn't exist. |
| `library_root` does not exist or is not a directory | Step 1 | Abort with diagnostic. |
| No book roots found (Step 2 returns empty) | Step 2 | Print "no books found in <library_root>" and exit 0 (not an error — just nothing to do). |
| `ingest-pipeline` subagent fails for a book | Step 4 | Mark that book `status: "failed"` in `library.json`. Continue to next book. |
| Subagent invocation infrastructure failure | Step 4 | Mark book `status: "failed"`, `error_message: "subagent invocation failed: <details>"`. Continue. |
| User Ctrl-C | Anywhere | Books marked `in_progress` in `library.json` will be reconciled by the per-book engine on next sweep (filesystem-truth rule). |

## Hooks (optional)

If event hooks are configured:
- `pre_book`: `{ root, abs_path }` before each `ingest-pipeline` invocation.
- `post_book`: `{ root, abs_path, status, duration_ms }` after each.
- `pre_sweep` / `post_sweep`: at the start and end of the whole batch.

## Notes

- The batch wrapper does **not** know how to ingest individual books — it
  only dispatches. All real work happens inside `ingest-pipeline`.
- `library.json` is a *summary* — it is regenerated each sweep from per-book
  `pipeline.json` files. Do not rely on it as a primary store.
- For very large libraries (50+ books), default `--parallel 1` may be slow
  but predictable. Bump cautiously: vision-heavy scanned books burn tokens
  fast.
````

- [ ] **Step 2: Verify the file is well-formed**

Run: `head -6 roles/dotfiles/files/hermes/skills/ingest-pipeline-batch/SKILL.md`

Expected: starts with `---` then `name: ingest-pipeline-batch`.

Run: `grep -c '^## Step' roles/dotfiles/files/hermes/skills/ingest-pipeline-batch/SKILL.md`

Expected: `6` (Step 0 through Step 5).

Run: `wc -l roles/dotfiles/files/hermes/skills/ingest-pipeline-batch/SKILL.md`

Expected: 110–160 lines.

- [ ] **Step 3: Confirm Ansible templating still works**

Run: `ansible-playbook --syntax-check ars.yml`

Expected: exits 0.

- [ ] **Step 4: Run the harness one more time**

Run: `just test-hermes`

Expected: `21 passed, 0 failed`.

- [ ] **Step 5: Commit**

```bash
git add roles/dotfiles/files/hermes/skills/ingest-pipeline-batch/SKILL.md
git commit -m "$(cat <<'EOF'
hermes(ingest-pipeline-batch): write library-sweep SKILL.md

Walks a library root, identifies book directories by their content
shape, filters out complete books unless --force, dispatches
ingest-pipeline per book. Sequential default; --parallel N caps
concurrent subagents. library.json is a summary regenerated each sweep
from per-book pipeline.json. Per-book failures isolated; batch-level
sweep never aborts on a single failed book.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: Update mdBook documentation and verify end-to-end deployment

**Purpose:** User-facing documentation in `markdownbook/configuration/dotfiles.md` so the new skills are discoverable from the existing handbook. Final ansible deployment dry-run to confirm the skill files are recognized and would deploy under `~/.hermes/skills/`.

**Files:**
- Modify: `markdownbook/configuration/dotfiles.md`

- [ ] **Step 1: Read current dotfiles.md to find the right insertion point**

Run: `grep -n -E '^#|^##|hermes' markdownbook/configuration/dotfiles.md`

Expected: an outline of the existing doc. Look for an "Hermes skills" or
similar section. If one already exists, append to it. If not, append at the
end of the file.

- [ ] **Step 2: Append the new section**

If `markdownbook/configuration/dotfiles.md` already has an "Hermes skills" section, append the following at its end. If not, append the entire block at the end of the file:

```markdown
### Ingest pipeline

The `ingest-pipeline` skill ties `split-textbooks` and `pdf-to-mdbook`
together into an end-to-end orchestrator. It accepts any of:

- A single large PDF.
- A directory of pre-split chapter PDFs.
- A directory of pre-split markdown documents.
- A partial mdBook directory (interrupted prior run).

…and drives it forward to a buildable mdBook. State is persisted in
`pipeline.json` per book; reruns resume from where the previous run
stopped.

Two skills ship together:

- `ingest-pipeline` — per-book engine.
- `ingest-pipeline-batch` — library sweep; runs `ingest-pipeline` over
  every book directory under a library root.

Both skills are invoked from a Hermes session like other skills. The
terminal state is `mdbook build` succeeding; wiki ingestion remains a
separate, manual `wiki-ingest` step.

Tests live under `roles/dotfiles/tests/hermes/`. Run them with:

```
just test-hermes
just test-hermes-integration   # requires hermes CLI on PATH
just regenerate-hermes-fixtures # rebuilds synthetic PDFs
```
```

- [ ] **Step 3: Verify the markdownbook still builds**

Run: `just mdbook-build 2>&1 | tail -20`

Expected: `mdbook build` exits 0; output ends with no warnings about
broken links or missing files. (If there's a SUMMARY.md gating which files
appear in the book, you may need to add the new section there as well.
Check `markdownbook/SUMMARY.md` to confirm `dotfiles.md` is already listed —
if so, the appended section flows into the existing chapter automatically.)

- [ ] **Step 4: Run the full Ansible deploy in check mode**

Run: `ansible-playbook --check --diff ars.yml --tags hermes 2>&1 | tail -80`

Expected output should include planned creations of:
- `~/.hermes/skills/ingest-pipeline/SKILL.md`
- `~/.hermes/skills/ingest-pipeline/references/state-detection.md`
- `~/.hermes/skills/ingest-pipeline/references/manifest-schema.md`
- `~/.hermes/skills/ingest-pipeline-batch/SKILL.md`

…and modifications to `~/.hermes/skills/pdf-to-mdbook/SKILL.md` (slice-mode
section added).

If the `hermes` tag is not bound in the role's task tags, run with
`--start-at-task 'Hermes | Ensure home directory exists'` instead.

- [ ] **Step 5: Run the harness one final time**

Run: `just test-hermes`

Expected: `21 passed, 0 failed`.

- [ ] **Step 6: Commit**

```bash
git add markdownbook/configuration/dotfiles.md
git commit -m "$(cat <<'EOF'
docs: cover ingest-pipeline and ingest-pipeline-batch skills

Adds an "Ingest pipeline" subsection under the dotfiles configuration
chapter describing what the new skills accept, the per-book vs
library-sweep split, the pipeline.json resume model, and the test
commands.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Self-Review

(Run by the plan author after writing the plan; fix any issues inline.)

### 1. Spec coverage

| Spec section / requirement                                        | Implementing task |
|-------------------------------------------------------------------|-------------------|
| Two new skills (`ingest-pipeline`, `ingest-pipeline-batch`)       | Tasks 1, 8, 9     |
| Reference docs (state-detection.md, manifest-schema.md)           | Tasks 2, 3        |
| `pdf-to-mdbook` slice-directory extension                         | Task 7            |
| Ansible registration in `defaults/main/hermes.yml`                | Tasks 1, 7        |
| Test fixtures (S0–S5, library, stale-pipeline-json)               | Task 4            |
| Test harness wired into `just`                                    | Tasks 5, 6        |
| Documentation in markdownbook                                     | Task 10           |
| Six-state classifier (S0–S5)                                      | Tasks 3, 8        |
| Filesystem-truth reconciliation rule                              | Tasks 2, 3, 8     |
| `pipeline.json` schema                                            | Tasks 2, 8        |
| `library.json` schema                                             | Tasks 2, 9        |
| Subagent delegation usage                                         | Tasks 8, 9        |
| Sequential-by-default with `--parallel N` opt-in                  | Task 9            |
| Hooks (pre_phase, post_phase, pre_destructive)                    | Tasks 8, 9        |
| Hermes feature touchpoints (memory, hooks, checkpoints, code exec) | Tasks 8, 9 (documented in skill bodies) |
| Crash safety / resume semantics                                   | Tasks 2, 3, 8     |
| Failure handling tables                                           | Tasks 8, 9        |

No coverage gaps.

### 2. Placeholder scan

- No "TBD", "TODO" outside of intentional content (e.g., `<!-- TODO: content -->` is the *literal* stub the orchestrator writes in S4 — that's a real string, not a plan placeholder).
- No "Add appropriate error handling" without showing it — every failure path is enumerated in the tables in Tasks 8 and 9.
- No "Similar to Task N" — every code block and command appears in full.
- All file paths absolute and exact.

### 3. Type / name consistency

- `pipeline.json` schema: `schema_version`, `skill`, `book_root`, `input_target`, `initial_state`, `current_state`, `status`, `phases[].name|skill|status|manifest|started_at|completed_at|subagent_invocation_id`, `failed_phase`, `error_message`, `notes` — these names appear identically across Tasks 2, 4, 8.
- `pdf-to-mdbook` schema v2 fields: `slice_mode`, `source_dir`, `slice_filename` — used identically in Task 7's manifest example, Step 0.5 narrative, and field-notes block.
- `library.json` schema: `library_root`, `last_swept_at`, `books[].root|status|pipeline_json|failed_phase` — consistent across Tasks 2, 4, 9.
- State enum values `S0`, `S1`, `S2`, `S3`, `S4`, `S5` consistent across all tasks.
- Phase names (`split`, `mdbook`, `scaffold`, `build`) consistent.
- Skill names (`ingest-pipeline`, `ingest-pipeline-batch`) consistent across SKILL.md files and Ansible registration.

No naming drift.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-04-hermes-ingest-pipeline.md`. Two execution options:

**1. Subagent-Driven (recommended)** — Dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.

Which approach?
