---
name: ingest-pipeline
description: Drive any PDF/markdown directory to a buildable mdBook — handles large PDFs, pre-split PDFs, pre-split markdown, partial mdBooks; idempotent and resumable. Calls split-textbooks and pdf-to-mdbook as Hermes subagents. Use when the user asks to "ingest", "process a textbook", "build an mdBook from a directory", or "resume a partially processed book".
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
