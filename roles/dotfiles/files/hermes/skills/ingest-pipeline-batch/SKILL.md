---
name: ingest-pipeline-batch
description: Sweep a library directory and run ingest-pipeline on every book root that is not already complete. Use when the user asks to "process all books in <dir>", "ingest the library", or "batch convert PDFs to mdBooks".
compatibility: Same as ingest-pipeline (poppler, mdbook, jq, plus pdf-to-mdbook's tesseract/Python deps) — invokes ingest-pipeline as a Hermes subagent per book.
---

# Ingest Pipeline — Batch

Walk a library root, identify each book directory, and run `ingest-pipeline`
on the ones not already complete. Idempotent across the whole library:
complete books are skipped, failed books retry, in-progress books resume.

## Architecture: prescriptive dispatcher

Like `ingest-pipeline` itself, this skill keeps the LLM out of the
bookkeeping path. The deterministic library walk and `library.json`
management run in `scripts/sweep.py`. The LLM agent's only jobs are:

1. Run `sweep.py scan` to get the working set.
2. Dispatch a per-book `ingest-pipeline` subagent for each entry, using
   the **fixed parameter template in Step 3**. Do not vary the parameters
   per book. Do not redesign the strategy mid-sweep.
3. Run `sweep.py mark` after each subagent returns.
4. Run `sweep.py finalize` at the end and print the summary.

If the agent finds itself reasoning about token budgets, concurrency
tuning, retry policies, or whether to bypass subagents and run scripts
directly — that is the wrong mode. The dispatch loop below is fixed.

**Required reference (read on demand):**
- `../ingest-pipeline/references/manifest-schema.md` — defines both the
  per-book `pipeline.json` and the `library.json` schemas.

## Inputs

- **Absolute path** to a library root directory.
- `--force` (optional) — Reprocess every book, even ones marked complete.
- `--parallel <N>` (optional) — Up to N concurrent `ingest-pipeline`
  subagents. Default: `1`. Recommend `1`–`3`; vision-heavy scanned books
  burn tokens fast.
- `--vision <mode>` (optional) — Forwarded to each per-book
  `ingest-pipeline` invocation; default `auto`.

## Step 1 — Scan the library

```bash
python "$SKILL_DIR/scripts/sweep.py" scan <abs_library_root> [--force]
```

The script verifies the path is a directory, walks it, identifies book
roots (rule: contains exactly one `.pdf`, OR a `pipeline.json`, OR both
`book.toml` and `src/SUMMARY.md`), refreshes `library.json`, and prints
the working set as JSON. If the directory has no book roots, `working_set`
is empty — print "no books found" and stop.

The script does **not** include directories that only contain pre-split
markdown without a manifest. If users have such directories, they should
invoke `ingest-pipeline` on each individually; the batch wrapper is for
PDF and pre-managed libraries.

## Step 2 — Per-book status update before dispatch

For every entry in `working_set`, immediately mark it `in_progress`:

```bash
python "$SKILL_DIR/scripts/sweep.py" mark <library_root> --root <root> --status in_progress
```

This makes progress visible to anyone reading `library.json` mid-sweep.

## Step 3 — Dispatch the per-book subagent (fixed template)

For each entry in the working set (sequentially if `--parallel 1`,
otherwise up to N at a time), invoke `delegate_task` with **exactly**
these parameters. Do not add others. Do not omit any.

```
delegate_task(
    goal      = "Drive <root> to a complete mdBook using the ingest-pipeline skill.",
    context   = """
                Book directory (absolute): <abs_path>
                Force flag: <true|false>           # forward as --force if true
                Vision mode: <auto|never|always>   # forward as --vision <mode>

                Run the ingest-pipeline skill against this directory. Follow the
                skill's Step 0 / Step 1 loop exactly: invoke run_pipeline.py,
                read the JSON action signal, dispatch pdf-to-mdbook on S1,
                record-phase on return, repair build errors when surfaced.
                Stop on `done` or any `failed` record-phase.
                """,
    toolsets  = ["terminal", "file", "vision"],
    skills    = ["ingest-pipeline", "pdf-to-mdbook"],
    max_iterations  = 80,
    max_spawn_depth = 2,
)
```

Notes on each parameter:

- `toolsets` — `vision` (not `image` — `image` is text-to-image generation,
  the wrong toolset). The `vision` toolset is what `pdf-to-mdbook` needs
  for its TOC structure-detection review.
- `skills` — Preload both skills so the per-book subagent does not pay
  a `skill_view` round-trip in its iteration budget. The `pdf-to-mdbook`
  preload is critical: when the per-book agent itself delegates
  `pdf-to-mdbook` (as a depth-2 subagent), Hermes' delegation system
  benefits from already having the skill loaded.
- `max_iterations: 80` — A typical book needs ~3–5 LLM iterations on the
  per-book side; 80 leaves margin for build-fix loops on books with
  difficult mdbook errors. Default 50 is too tight when a book triggers
  a vision-review cycle plus a build repair.
- `max_spawn_depth: 2` — Per-book subagent (depth 1) needs to itself
  delegate `pdf-to-mdbook` (depth 2). Without this raise, the per-book
  subagent runs in leaf mode and cannot delegate. (Hermes doc reference:
  `developer-guide/agent-loop.md`, `guides/delegation-patterns.md`.)
- **Forbidden parameters**: do not pass `acp_command`, `provider`, `model`,
  or any other parameter not listed above. Earlier versions of this skill
  invited the agent to reason about these — every such reasoning step is
  wasted iterations. The defaults Hermes selects are correct.

For `--parallel N > 1`, dispatch up to N entries in a single `delegate_task`
call (Hermes accepts a list) or spawn multiple back-to-back; cap concurrency
at N. `delegate_task` is **synchronous** — if the orchestrator turn is
interrupted, all in-flight children are cancelled and their work is lost.
The per-book script writes `pipeline.json` atomically so cancelled work
resumes cleanly on next sweep.

## Step 4 — Per-book status update after return

When each subagent returns, read the corresponding `pipeline.json` to
determine final status, then mark accordingly:

```bash
# On success:
python "$SKILL_DIR/scripts/sweep.py" mark <library_root> --root <root> --status complete

# On failure (read failed_phase + error_message from <root>/pipeline.json):
python "$SKILL_DIR/scripts/sweep.py" mark <library_root> --root <root> \
    --status failed --failed-phase <phase> --error "<message>"

# Subagent crashed before pipeline.json reached a terminal state:
python "$SKILL_DIR/scripts/sweep.py" mark <library_root> --root <root> --status in_progress
```

The third case is the iteration-cap-reached scenario: the subagent
returned a summary, but `pipeline.json` is still `in_progress`. Leave it
that way. The next sweep will resume from the consistent on-disk state.

## Step 5 — Finalize

After the working set is exhausted:

```bash
python "$SKILL_DIR/scripts/sweep.py" finalize <abs_library_root>
```

This sets `last_swept_at`, sorts books deterministically, and prints a
summary. Print the summary to the user as-is.

## Resume semantics

`library.json` is a *summary*; the per-book `pipeline.json` files are the
source of truth. A re-invocation of this skill against the same library
root re-scans and:

- Skips books with `pipeline.json` `status: complete` (unless `--force`).
- Re-dispatches books with `status: failed` (the rerun is the explicit
  retry signal).
- Re-dispatches books with `status: in_progress` — `ingest-pipeline`'s
  filesystem-truth rule reconciles the partial state cleanly.

You do not need to reason about which case applies — `sweep.py scan`
returns the correct working set.

## Failure handling

Batch-level errors **never abort the sweep**. Per-book failures are
isolated.

| Failure                                       | Where         | Behavior                                                                                  |
|-----------------------------------------------|---------------|-------------------------------------------------------------------------------------------|
| `library_root` not a directory                | `scan`        | Script exits 2 with diagnostic; stop.                                                     |
| No book roots found                           | `scan`        | Working set empty; print "no books found" and exit 0.                                     |
| `ingest-pipeline` subagent fails for a book   | Step 4 mark   | Mark `failed` with phase + message; continue.                                             |
| Subagent infrastructure failure / timeout     | Step 4 mark   | Mark `failed` with `error_message: "subagent invocation failed: <details>"`; continue.    |
| Subagent hits iteration cap                   | Step 4 mark   | Mark `in_progress`; user reruns to resume.                                                |
| User Ctrl-C during sweep                      | anywhere      | All in-flight subagents are cancelled. Per-book `pipeline.json` files are consistent on disk; next sweep resumes. |

## Notes

- The batch wrapper does **not** know how to ingest individual books — it
  only dispatches. All real work happens inside `ingest-pipeline`, which
  in turn dispatches `pdf-to-mdbook` for the structure-bearing PDF work.
- For very large libraries (50+ books), default `--parallel 1` is slow
  but predictable. Bump cautiously.
- A typical successful sweep dispatches one orchestrator-side LLM
  iteration per book (one `delegate_task`, one `mark`), plus the per-book
  subagent's own iterations (3–8 typical). The orchestrator does not
  burn iterations on bookkeeping.
