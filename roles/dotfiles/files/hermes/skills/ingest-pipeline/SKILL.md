---
name: ingest-pipeline
description: Drive any PDF/markdown directory to a buildable mdBook — handles single PDFs, pre-split markdown, partial mdBooks; idempotent and resumable. Calls pdf-to-mdbook as a Hermes subagent for PDF inputs. Use when the user asks to "ingest", "process a textbook", "build an mdBook from a directory", or "resume a partially processed book".
compatibility: Requires poppler (pdfinfo, pdftotext), mdbook, jq, plus the toolchain pdf-to-mdbook itself depends on (tesseract for OCR, Python with pdfplumber/PyPDF2). Composes the pdf-to-mdbook skill via Hermes subagent delegation.
---

# Ingest Pipeline

Drive any of the following inputs forward to a buildable mdBook:

- A single PDF (text-based or scanned).
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
command -v pdfinfo pdftotext mdbook jq
```

If any are missing, print install hints and abort:
- macOS: `brew install poppler mdbook jq`
- Linux/devbox: `devbox add poppler mdbook jq`

`pdf-to-mdbook` performs its own deeper Step 0 check for tesseract and Python
deps when it's dispatched; we don't repeat that here.

## Step 1 — Resolve `book_root`, `input_target`, and `working_dir`

Resolve the user-provided target to an absolute path. Determine `book_root`:
- If target is a `.pdf` file → `book_root = dirname(target)`.
- If target is a directory → `book_root = target`.

Determine `working_dir`:
- If `<book_root>/pipeline.json` exists and has `working_dir` set, load it.
- Otherwise `working_dir = book_root` (initial state).

Record `input_target`, `book_root`, and `working_dir` for the manifest. The
`pipeline.json` file always lives at `book_root`; `working_dir` may equal
`book_root` (initial) or the mdbook subdirectory produced by `pdf-to-mdbook`
(after S1 advances the pipeline).

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
  - `book_root`, `input_target`, `working_dir`, `initial_state`, `current_state`
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

### S1 — Single PDF

Update `pipeline.json`:
- Append phase entry: `{ name: "mdbook", skill: "pdf-to-mdbook", status: "pending", started_at: now }`
- Set top-level `status: "in_progress"`.

Invoke `pdf-to-mdbook` via **subagent delegation** with:
- Restricted toolset: `terminal`, `file`, `image` (for the vision pass).
- Single argument: `<book_root>/<pdf-filename>` (the input PDF — `pdf-to-mdbook`
  resolves its own work directory and mdbook output directory alongside it).
- Flags: `--vision <user's choice or auto>`. If `--force` was passed at the
  pipeline level, also pass `--force` to the subagent.

When the subagent returns:
- On success → phase `status: "complete"`, `manifest:
  "<mdbook_dir>/manifest.json"` (relative to `book_root` — read `mdbook_dir`
  from the sub-skill's own manifest). `completed_at: now`,
  `subagent_invocation_id: <returned id>`. **Update `pipeline.json`
  `working_dir` to `<book_root>/<mdbook_dir>/`** so the next phase's
  classifier finds `book.toml` and `src/SUMMARY.md` directly. Reclassify
  (loop to Step 2). New state should be S4.
- On failure → phase `status: "failed"`, copy the sub-skill's
  `manifest.json` `error_message` into the pipeline-level `error_message`,
  set `failed_phase: "mdbook"`, set top-level `status: "failed"`, stop.

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

1. The mdBook root is `working_dir` itself. By the time S4 fires, prior
   phases have advanced `working_dir` to point at the directory containing
   `book.toml` and `src/SUMMARY.md` (either via S1's `pdf-to-mdbook` output
   or S3's inline scaffold). If the user entered directly at S4 (a
   partial mdBook), `working_dir == book_root` and the user-supplied target
   was already that directory. Confirm `<working_dir>/book.toml` and
   `<working_dir>/src/SUMMARY.md` exist; if not, set `failed_phase: "build"`,
   error_message: "S4 entered but working_dir does not contain a valid
   mdbook layout".
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
4. On non-zero exit, capture stderr. Try **exactly one** auto-fix round:
   - Broken table syntax → reformat as fenced code block.
   - Missing `README.md` → write a one-line stub.
   - Then rerun `mdbook build` exactly once. If this rerun also fails, do
     NOT attempt further fixes — proceed directly to the failure branch
     (step 6).
5. On success → phase `status: "complete"`. **Update top-level `pipeline.json`
   `status: "complete"` and `current_state: "S5"` BEFORE reclassifying.** This
   prevents a reclassification race where the classifier's S5 trigger
   (`pipeline.json status: complete`) would otherwise see `in_progress` and
   fall back through to S4 again. Then reclassify (loop to Step 2); the
   classifier returns S5 deterministically.
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

The pattern matches `pdf-to-mdbook`: every failure is recorded; never abort
an enclosing batch; user retries with the same command.

| Failure | Where | Behavior |
|---------|-------|----------|
| Required tool missing | Step 0 | Print install hints; abort. No `pipeline.json` written. |
| State classifier returns S0 | Step 2 | Abort with diagnostic. No `pipeline.json` written. |
| `pdf-to-mdbook` subagent fails | S1 phase | Phase failed, `failed_phase: "mdbook"`. Stop. |
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
- For very large books, expect the S1 phase (`pdf-to-mdbook`'s vision pass on every page) to dominate runtime. Use `--vision never` if you have clean text layers and want a faster run.
