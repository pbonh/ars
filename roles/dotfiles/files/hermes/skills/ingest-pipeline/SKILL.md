---
name: ingest-pipeline
description: Drive any PDF/markdown directory to a buildable mdBook — handles single PDFs, pre-split markdown, partial mdBooks; idempotent and resumable. Calls pdf-to-mdbook as a Hermes subagent for PDF inputs. Use when the user asks to "ingest", "process a textbook", "build an mdBook from a directory", or "resume a partially processed book".
compatibility: Requires poppler (pdfinfo, pdftotext), mdbook, jq, plus the toolchain pdf-to-mdbook itself depends on (tesseract for OCR, Python with pdfplumber/PyPDF2). Composes the pdf-to-mdbook skill via Hermes subagent delegation.
---

# Ingest Pipeline

Drive any of these inputs forward to a buildable mdBook:

- A single PDF (text-based or scanned).
- A directory of already-split markdown documents.
- A partially-built mdBook directory (interrupted prior run).

The skill is **idempotent and resumable**: rerun on a partial directory
resumes from where the prior run left off. Terminal state is `mdbook build`
succeeded; wiki ingestion is a separate, manual follow-up.

## Architecture: thin LLM, fat script

This skill keeps the LLM **decisive for judgment, supervisory for bookkeeping**.

The deterministic state machine — path resolution, state classification,
`pipeline.json` reads/writes, S3 inline scaffold, S4 mdbook build with one
auto-fix round, S5 finalize — runs entirely in `scripts/run_pipeline.py`.
That script never invokes a subagent and writes the manifest atomically
after every state transition.

The LLM agent's job is exactly two things:

1. **Dispatch the `pdf-to-mdbook` subagent** when the script signals S1.
   `pdf-to-mdbook` is where structure detection (TOC parse, font analysis,
   vision review of rasterized TOC images) and any judgment-bearing PDF
   work happens. That judgment is preserved in full.
2. **Repair `mdbook build` errors** the deterministic auto-fix could not
   handle. The script surfaces the captured stderr; the agent edits files
   and re-runs the script.

Everything else is one shell call followed by reading the JSON it printed.

If the agent finds itself reasoning about file paths, manifest fields, or
state classification rules, it is in the wrong mode — the script owns those.

**Required references (read on demand, not preloaded):**
- `references/state-detection.md` — the spec `run_pipeline.py` implements.
- `references/manifest-schema.md` — the `pipeline.json` schema the script writes.

## Inputs

The user provides:
- **Absolute path** to a `.pdf` file OR a directory.
- `--force` (optional) — Re-run from scratch even if `pipeline.json` says
  `status: complete`.
- `--vision <mode>` (optional) — Forwarded to `pdf-to-mdbook`; default `auto`.

## Step 0 — Run the state machine

```bash
python "$SKILL_DIR/scripts/run_pipeline.py" <abs_target> [--force] [--vision auto|never|always]
```

The script does the environment self-check (`pdfinfo`, `pdftotext`,
`mdbook`, `jq`) and aborts with install hints if anything is missing — do
not duplicate that check here.

It prints **exactly one** JSON object on stdout. Read it; that object
tells you what to do next.

## Step 1 — Dispatch on the action signal

The JSON's `action` field selects the next step. Treat anything not listed
here as a script bug — do not improvise.

### `action: "done"`

Pipeline reached S5. Print the script's `message` to the user and stop.
Nothing else to do.

### `action: "advanced"`

A deterministic phase (S3 scaffold or S4 build) succeeded. Re-run the
script (Step 0). The classifier will pick up the next state.

### `action: "delegate_pdf_to_mdbook"`

The script identified an S1 (single PDF) input and is asking you to
dispatch the `pdf-to-mdbook` subagent. The fields you receive:

- `pdf` — absolute path to the PDF
- `book_root` — absolute path the manifest lives at
- `force` — boolean, forward as `--force` if true
- `vision` — `auto` / `never` / `always`, forward as `--vision <value>`
- `phase_index` — pass to `record-phase` so the right phase entry is updated

Invoke `delegate_task` with **exactly these parameters** (no others —
do not add `acp_command`, `acp_args`, `role`, `provider`, `model`,
`max_iterations`, `max_spawn_depth`, or `skills`):

- `goal` — `"Convert <pdf> into an mdBook using the pdf-to-mdbook skill."`
- `context` — Pass the absolute `pdf` path, `book_root`, `force` flag,
  and `vision` mode. The subagent has no conversation history.
- `toolsets` — `["terminal", "file", "vision"]`

Notes:
- The Hermes v0.12+ `delegate_task` schema does not accept `skills`,
  `max_iterations`, or `max_spawn_depth`. They are not real per-call
  kwargs — `max_iterations` is silently dropped (config-authoritative),
  `max_spawn_depth` is config-only, and `skills` was never a parameter.
  Iteration budget lives in `~/.hermes/config.yaml` as
  `delegation.max_iterations` (the dotfiles role sets this to 150).
- `role` is omitted (defaults to `leaf`) because `pdf-to-mdbook` does
  not delegate further. If this skill is invoked from inside another
  delegated agent (e.g. `ingest-pipeline-batch`'s per-book subagent),
  the parent must have been dispatched with `role: "orchestrator"` and
  `delegation.max_spawn_depth >= 2` for this nested call to land at
  all — otherwise it returns "Delegation depth limit reached".

When the subagent returns:

1. If it succeeded, read its `manifest.json` to find the mdbook output
   directory (`<book_root>/<mdbook_dir>/`). Then call:

   ```bash
   python "$SKILL_DIR/scripts/run_pipeline.py" record-phase <book_root> \
       --phase mdbook --phase-index <idx> --status complete \
       --manifest <mdbook_dir>/manifest.json \
       --invocation-id <returned subagent id> \
       --working-dir <abs path to mdbook output dir>
   ```

2. If it failed, call:

   ```bash
   python "$SKILL_DIR/scripts/run_pipeline.py" record-phase <book_root> \
       --phase mdbook --phase-index <idx> --status failed \
       --error "<short error message from subagent>"
   ```

   Then stop — `pipeline.json` `status` is now `failed` and the user must
   inspect.

3. After a successful `record-phase complete`, return to Step 0 (re-run
   the script). The classifier will return S4 and the script will run
   `mdbook build`.

### `action: "need_judgment_build_fix"`

`mdbook build` failed and the deterministic auto-fix did not repair it.
Apply LLM judgment:

- Read the `stderr` field (last 2000 chars of mdbook output).
- Inspect files under `working_dir`. Common causes: a Markdown file
  generates ill-formed HTML, a `[link](missing.md)` references a file
  that wasn't stubbed, an unsupported `book.toml` field.
- Edit the offending file(s) under `working_dir` to fix the root cause.
  Do not delete content.
- Re-run Step 0. If the script signals `need_judgment_build_fix` again,
  iterate — but if you have not made meaningful progress in two attempts,
  call `record-phase --phase build --status failed` and stop.

## Step 2 — Loop

After every action except `done` and `failed` `record-phase`, return to
Step 0. The script enforces forward progress; it will not loop on the
same state without producing a different action.

## Resume semantics

The script writes `pipeline.json` atomically after every transition. If
this skill (or its parent batch sweep) is interrupted — Ctrl-C, iteration
cap, subagent crash — the on-disk state is consistent. Re-running the
skill on the same target will:

- See the prior `pipeline.json`, apply the filesystem-truth rule (see
  `references/manifest-schema.md`), and reclassify.
- Skip work that is already complete.
- Re-emit a `delegate_pdf_to_mdbook` signal if the mdbook phase did not
  finish, or proceed to S4 if it did.

You do **not** need to reason about "is this resume or rerun?" — the
script's classification handles both.

## Failure handling

Per-phase failures are isolated. The script writes `status: failed`,
`failed_phase`, and `error_message` into `pipeline.json` and exits via
the appropriate action signal. The batch wrapper (`ingest-pipeline-batch`)
treats any non-complete result as "failed for this book; continue" and
will not abort the sweep.

| Failure                                | Source              | What you do                                                         |
|----------------------------------------|---------------------|---------------------------------------------------------------------|
| Required tool missing                  | Step 0 stderr       | Print install hints from script stderr; stop.                       |
| `S0` (empty/unrelated dir)             | Step 0 exit 2       | Forward the script's diagnostic and stop.                           |
| `pdf-to-mdbook` subagent failed        | Step 1 delegate     | `record-phase --status failed`; stop.                               |
| `mdbook build` failed after LLM repair | Step 1 build_fix    | After 2 failed repair attempts, `record-phase --status failed`; stop. |
| Subagent invocation timed out          | Step 1 delegate     | `record-phase --status failed --error "subagent timeout"`; stop.    |

## Notes

- The skill does **not** call `wiki-ingest`. Hand-off to a wiki is a
  separate, explicit user action.
- The skill does **not** modify input PDFs or markdown. All output goes
  under `book_root`.
- For very large books, expect `pdf-to-mdbook`'s vision pass over TOC
  rasters to dominate runtime. Use `--vision never` if you have clean
  text layers and want a faster run.
- A typical successful run is 3–5 LLM iterations: dispatch script,
  delegate pdf-to-mdbook, record-phase, dispatch script, done.
