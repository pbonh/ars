---
name: ingest-pipeline-batch
description: Sweep a library directory and run ingest-pipeline on every book root that is not already complete. Use when the user asks to "process all books in <dir>", "ingest the library", or "batch convert PDFs to mdBooks". Pass `--wiki-root <abs_path>` to chain `wiki-ingest` and `wiki-lint` after each book so the wiki stays well-formed across the sweep.
compatibility: Same as ingest-pipeline (poppler, mdbook, jq, plus pdf-to-mdbook's tesseract/Python deps) — invokes ingest-pipeline as a Hermes subagent per book. With `--wiki-root`, the per-book subagent additionally runs `wiki-ingest` and `wiki-lint` inline (no extra deps).
---

# Ingest Pipeline — Batch

Walk a library root, identify each book directory, and run `ingest-pipeline`
on the ones not already complete. Idempotent across the whole library:
complete books are skipped, failed books retry, in-progress books resume.

## Architecture: prescriptive dispatcher

Like `ingest-pipeline` itself, this skill keeps the LLM out of the
bookkeeping path. The deterministic library walk and `library.json`
management run in `scripts/sweep.py`. The LLM agent's only jobs are:

1. Run `sweep.py scan` to get the working set (forward `--wiki-root` if
   given so books needing only the wiki side re-enter the working set).
2. Dispatch a per-book subagent for each entry, using the **fixed
   parameter template in Step 3** — Step 3a without `--wiki-root`,
   Step 3b with it. Do not vary the parameters per book. Do not redesign
   the strategy mid-sweep.
3. Run `sweep.py mark` after each subagent returns. With `--wiki-root`,
   read `wiki.json` (Step 4b) before marking; without it, read
   `pipeline.json` (Step 4a).
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
- `--wiki-root <abs_path>` (optional) — Wiki root (parent of `raw/` and
  `wiki/`). When set, each book's per-book subagent runs the full chain
  `ingest-pipeline → wiki-ingest → wiki-lint`, keeping the wiki
  well-formed across the sweep instead of only at the end. Forces
  `--parallel 1`: wiki writes serialize on `wiki/index.md`, `wiki/log.md`,
  `wiki/dashboard.md`, and `wiki/analytics.md`, so concurrent per-book
  agents would race on those files. If the user passes `--parallel >1`
  alongside `--wiki-root`, refuse before calling `sweep.py`.

## Step 1 — Scan the library

```bash
python "$SKILL_DIR/scripts/sweep.py" scan <abs_library_root> [--force] [--wiki-root <abs_wiki_root>]
```

The script verifies the path is a directory, walks it, identifies book
roots (rule: contains exactly one `.pdf`, OR a `pipeline.json`, OR both
`book.toml` and `src/SUMMARY.md`), refreshes `library.json`, and prints
the working set as JSON. If the directory has no book roots, `working_set`
is empty — print "no books found" and stop.

When `--wiki-root` is forwarded, sweep.py also re-checks each book's
per-book `wiki.json` sentinel: a book with `pipeline.json:complete` but
no `wiki.json:complete` re-enters the working set with `wiki_pending:
true`. The orchestrator uses that flag to skip the ingest-pipeline phase
in the per-book dispatch and start at wiki-ingest.

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

Two templates: pick by whether `--wiki-root` was provided.

### Step 3a — Without `--wiki-root` (mdBook-only path)

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

### Step 3b — With `--wiki-root` (chained path)

```
delegate_task(
    goal      = "Drive <root> through ingest-pipeline → wiki-ingest → wiki-lint.",
    context   = """
                Book directory (absolute): <abs_path>
                Wiki root (absolute):      <abs_wiki_root>
                Force flag:                <true|false>           # forward as --force if true
                Vision mode:               <auto|never|always>    # forward as --vision <mode>
                Wiki-pending only:         <true|false>           # from working_set entry

                Run the chain in order:

                1. ingest-pipeline against the book directory.
                   - Skip if `Wiki-pending only` is true (pipeline.json already
                     reports complete). Otherwise follow ingest-pipeline's Step 0
                     / Step 1 loop exactly: invoke run_pipeline.py, read the JSON
                     action signal, dispatch pdf-to-mdbook on S1, record-phase
                     on return, repair build errors when surfaced. Stop on `done`
                     or any `failed` record-phase.
                   - On `failed`: write <book_dir>/wiki.json with
                     {"status": "failed", "failed_phase": "ingest-pipeline",
                      "error_message": "<message>"} and return — do NOT proceed.

                2. wiki-ingest against <abs_wiki_root>.
                   - Run the skill's Step 0 triage. wiki-ingest naturally skips
                     sources whose wiki/summaries/<slug>.md already exists, so
                     only the freshly-completed source (or any unprocessed
                     siblings sharing this wiki root) will be ingested. Process
                     to completion.
                   - On any failure: write <book_dir>/wiki.json with
                     {"status": "failed", "failed_phase": "wiki-ingest",
                      "error_message": "<message>"} and return.

                3. wiki-lint against <abs_wiki_root>.
                   - Run the full lint workflow (read pages → run checks →
                     auto-fix → update statistics → update dashboard/analytics
                     → append to log → report).
                   - On any failure: write <book_dir>/wiki.json with
                     {"status": "failed", "failed_phase": "wiki-lint",
                      "error_message": "<message>"} and return.

                4. On success of all three, write <book_dir>/wiki.json with
                   {"status": "complete",
                    "summary_path": "<abs_wiki_root>/wiki/summaries/<slug>.md",
                    "linted_at": "<iso8601 utc>"}.

                Return a one-line summary of which phase finished last.
                """,
    toolsets  = ["terminal", "file", "vision"],
    skills    = ["ingest-pipeline", "pdf-to-mdbook", "wiki-ingest", "wiki-lint"],
    max_iterations  = 150,
    max_spawn_depth = 2,
)
```

Notes on each parameter:

- `toolsets` — `vision` (not `image` — `image` is text-to-image generation,
  the wrong toolset). The `vision` toolset is what `pdf-to-mdbook` needs
  for its TOC structure-detection review.
- `skills` — Preload all skills the per-book agent will use so it does
  not pay `skill_view` round-trips in its iteration budget. The
  `pdf-to-mdbook` preload is critical: when the per-book agent itself
  delegates `pdf-to-mdbook` (as a depth-2 subagent), Hermes' delegation
  system benefits from already having the skill loaded. In Step 3b the
  preload extends to `wiki-ingest` and `wiki-lint`, both of which the
  per-book agent invokes inline (not via further delegation).
- `max_iterations` — `80` for Step 3a; `150` for Step 3b. A typical book
  needs ~3–5 LLM iterations on the per-book side; 80 leaves margin for
  build-fix loops on books with difficult mdbook errors. The Step 3b
  bump covers wiki-ingest's chapter-at-a-time read pass plus wiki-lint's
  page-by-page audit, which together can run another 30–60 iterations on
  a populated wiki. Default 50 is too tight in either case.
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

`--parallel > 1` is **rejected** when `--wiki-root` is set. Concurrent
per-book agents would race on `wiki/index.md`, `wiki/log.md`, and the
dashboard/analytics files; wiki-lint also reads the whole wiki tree and
its auto-fixes are not safe to interleave. If the user passes both,
refuse with: "wiki-root chain requires --parallel 1; rerun without
--parallel or with --parallel 1."

## Step 4 — Per-book status update after return

When each subagent returns, read the relevant on-disk truth files to
determine final status, then mark accordingly. Which file you read
depends on whether `--wiki-root` was set.

### Step 4a — Without `--wiki-root` (read `pipeline.json`)

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

### Step 4b — With `--wiki-root` (read `wiki.json`, fall back to `pipeline.json`)

The per-book agent's chain writes `<root>/wiki.json` as the terminal
status sentinel (see Step 3b). Read it first; only fall back to
`pipeline.json` if the chain failed before wiki-ingest started.

```bash
# wiki.json reports status:complete → chain finished cleanly.
python "$SKILL_DIR/scripts/sweep.py" mark <library_root> --root <root> --status complete

# wiki.json reports status:failed → mark with the phase from wiki.json.
python "$SKILL_DIR/scripts/sweep.py" mark <library_root> --root <root> \
    --status failed --failed-phase <wiki-ingest|wiki-lint|ingest-pipeline> \
    --error "<message from wiki.json>"

# wiki.json missing AND pipeline.json reports status:failed → ingest-pipeline
# died before the chain could write wiki.json. Mark with the pipeline phase.
python "$SKILL_DIR/scripts/sweep.py" mark <library_root> --root <root> \
    --status failed --failed-phase <pipeline phase> \
    --error "<message from pipeline.json>"

# wiki.json missing AND pipeline.json reports status:complete → chain
# stopped between phases (iteration cap, subagent crash). Mark failed
# with a synthetic phase so the next sweep retries the wiki side.
python "$SKILL_DIR/scripts/sweep.py" mark <library_root> --root <root> \
    --status failed --failed-phase wiki-chain-incomplete \
    --error "subagent returned without writing wiki.json"

# wiki.json missing AND pipeline.json still in_progress → same as 4a's
# third case; leave in_progress and let the next sweep resume.
python "$SKILL_DIR/scripts/sweep.py" mark <library_root> --root <root> --status in_progress
```

A book marked `failed` with `failed_phase: wiki-chain-incomplete` (or
any of the wiki phases) is automatically re-dispatched on the next sweep
because sweep.py's `--wiki-root` mode treats `pipeline.json:complete`
without `wiki.json:complete` as still-pending. The per-book agent's
Step 3b instructions skip already-done phases on the retry.

## Step 5 — Finalize

After the working set is exhausted:

```bash
python "$SKILL_DIR/scripts/sweep.py" finalize <abs_library_root>
```

This sets `last_swept_at`, sorts books deterministically, and prints a
summary. Print the summary to the user as-is.

## Resume semantics

`library.json` is a *summary*; the per-book `pipeline.json` (and, when
`--wiki-root` is set, `wiki.json`) files are the source of truth. A
re-invocation of this skill against the same library root re-scans and:

- Skips books with `pipeline.json` `status: complete` (unless `--force`).
  When `--wiki-root` is set, also requires `wiki.json` `status: complete`
  before skipping.
- Re-dispatches books with `status: failed` (the rerun is the explicit
  retry signal).
- Re-dispatches books with `status: in_progress` — `ingest-pipeline`'s
  filesystem-truth rule reconciles the partial state cleanly. The
  per-book agent in Step 3b additionally skips wiki-ingest if
  `wiki/summaries/<slug>.md` already exists, so re-runs of a chain that
  failed only at wiki-lint cost only the lint pass.

You do not need to reason about which case applies — `sweep.py scan`
(with the right `--wiki-root` flag) returns the correct working set.

## Failure handling

Batch-level errors **never abort the sweep**. Per-book failures are
isolated.

| Failure                                       | Where         | Behavior                                                                                  |
|-----------------------------------------------|---------------|-------------------------------------------------------------------------------------------|
| `library_root` not a directory                | `scan`        | Script exits 2 with diagnostic; stop.                                                     |
| No book roots found                           | `scan`        | Working set empty; print "no books found" and exit 0.                                     |
| `ingest-pipeline` subagent fails for a book   | Step 4 mark   | Mark `failed` with phase + message; continue.                                             |
| `wiki-ingest` fails for a book (Step 3b)      | Step 4b mark  | Mark `failed` with `failed_phase: wiki-ingest` from `wiki.json`; continue.                |
| `wiki-lint` fails for a book (Step 3b)        | Step 4b mark  | Mark `failed` with `failed_phase: wiki-lint` from `wiki.json`; continue.                  |
| Chain returns without `wiki.json` (Step 3b)   | Step 4b mark  | Mark `failed` with `failed_phase: wiki-chain-incomplete`; next sweep retries.             |
| Subagent infrastructure failure / timeout     | Step 4 mark   | Mark `failed` with `error_message: "subagent invocation failed: <details>"`; continue.    |
| Subagent hits iteration cap                   | Step 4 mark   | Mark `in_progress`; user reruns to resume.                                                |
| User Ctrl-C during sweep                      | anywhere      | All in-flight subagents are cancelled. Per-book `pipeline.json` files are consistent on disk; next sweep resumes. |

## Notes

- The batch wrapper does **not** know how to ingest individual books — it
  only dispatches. All real work happens inside `ingest-pipeline`, which
  in turn dispatches `pdf-to-mdbook` for the structure-bearing PDF work.
  When `--wiki-root` is set, `wiki-ingest` and `wiki-lint` also run
  inline inside the per-book subagent.
- For very large libraries (50+ books), default `--parallel 1` is slow
  but predictable. Bump cautiously — and not at all when `--wiki-root`
  is set, since wiki writes serialize.
- A typical successful sweep dispatches one orchestrator-side LLM
  iteration per book (one `delegate_task`, one `mark`), plus the per-book
  subagent's own iterations (3–8 typical without `--wiki-root`, 8–20
  with it; wiki-lint dominates the second-half cost on populated wikis).
  The orchestrator does not burn iterations on bookkeeping.
