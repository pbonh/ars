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
2. Dispatch a per-book subagent for each entry. The exact
   `delegate_task` kwargs come from `sweep.py dispatch` (Step 3) —
   the orchestrator forwards the JSON verbatim and never constructs,
   augments, or omits keys. Do not vary the parameters per book. Do
   not redesign the strategy mid-sweep.
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

## Configuration prerequisites

Hermes' iteration budget and spawn depth are **global config**, not
per-call kwargs. Before this skill can run end-to-end, `~/.hermes/config.yaml`
must contain:

```yaml
delegation:
  max_iterations: 150
  max_spawn_depth: 2
```

Why these values:
- `max_iterations: 150` — the wiki-chain path (Step 3b) regularly burns
  80–120 iterations (ingest-pipeline ≈ 5, wiki-ingest ≈ 20–40 chapters,
  wiki-lint ≈ 30–60 page audit). Hermes' built-in default of 50 caps
  the per-book agent before `wiki-lint` even starts. The mdBook-only
  path (Step 3a) needs only ~80 but the cap is global, so 150 covers both.
- `max_spawn_depth: 2` — the per-book agent (depth 1) must delegate
  `pdf-to-mdbook` (depth 2). The default of 1 makes children leaves and
  blocks that nested delegation outright.

If you see per-book agents capping at ~45 iterations, or `pdf-to-mdbook`
delegations failing with "Delegation depth limit reached", the config
is missing or stale. Apply via the dotfiles role
(`roles/dotfiles/defaults/main/hermes.yml` → `hermes_config.delegation`)
and re-run the playbook, or hand-edit `~/.hermes/config.yaml`.

The `delegate_task` schema itself does **not** accept `max_iterations`,
`max_spawn_depth`, or `skills` as kwargs (verified against
`tools/delegate_tool.py:DELEGATE_TASK_SCHEMA`). Anything passed in
those keys is silently dropped or rejected. The only per-call levers
this skill uses are `goal`, `context`, `toolsets`, and
`role: "orchestrator"` (set by `sweep.py dispatch`).

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
true` and is persisted with the same flag in `library.json`. The Step 3
`dispatch` command reads that flag and renders the Step 3b context with
`Wiki-pending only: true`, telling the per-book subagent to skip
ingest-pipeline and start at wiki-ingest.

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

## Step 3 — Dispatch the per-book subagent (kwargs from `sweep.py dispatch`)

For each entry in the working set, get the exact `delegate_task` kwargs
from `sweep.py dispatch` and forward them verbatim to `delegate_task`.
Do not transcribe, edit, augment, or drop keys — the script owns the
template. It picks Step 3a (no `--wiki-root`) vs Step 3b (with
`--wiki-root`) automatically and reads `wiki_pending` from `library.json`
(persisted by `sweep.py scan`).

```bash
python "$SKILL_DIR/scripts/sweep.py" dispatch <abs_library_root> \
    --root <book_root_basename> \
    [--wiki-root <abs_wiki_root>] \
    [--vision <auto|never|always>] [--force]
```

Output is a JSON object whose keys are exactly the kwargs to forward:

```json
{
  "goal": "...",
  "context": "...",
  "toolsets": ["terminal", "file", "vision"],
  "role": "orchestrator"
}
```

The two paths differ only in `goal` and `context`; `toolsets` and
`role` are identical. The orchestrator role is required so the
per-book agent retains `delegate_task` for the nested `pdf-to-mdbook`
dispatch — it is **not** a license to redesign anything mid-flight.

**Forbidden parameters** — do not pass `acp_command`, `acp_args`,
`provider`, `model`, `max_iterations`, `max_spawn_depth`, or `skills`.
The first four are not used by this skill. The last three are
**not real `delegate_task` kwargs** in Hermes v0.12+ — `max_iterations`
is silently dropped (config-authoritative), `max_spawn_depth` is
config-only, and `skills` was never a parameter. They live in
`~/.hermes/config.yaml` (see Configuration prerequisites). If you find
yourself reasoning about delegation parameters, stop — the script owns
the per-call surface and config owns the rest.

**Why `dispatch` instead of an inline template:** a prior incident saw
the orchestrator skim past the inline template, build the `delegate_task`
call from memory, and silently include phantom kwargs. The per-book
subagent ran under Hermes' defaults (~50 iter / leaf mode), capped
before reaching `wiki-lint`, and burned a book. The deeper bug — the
template documented kwargs that don't exist in the schema — was masked
because Hermes ignores unknown keys. Sourcing the call from a script
removes both transcription drift and the phantom-kwarg trap: the JSON
matches the public schema exactly.

For `--parallel N > 1`, call `dispatch` once per book and pass the
list of payloads to a single `delegate_task` invocation (Hermes
accepts a list) or spawn multiple back-to-back; cap concurrency at N.
`delegate_task` is **synchronous** — if the orchestrator turn is
interrupted, all in-flight children are cancelled and their work is
lost. The per-book script writes `pipeline.json` atomically so
cancelled work resumes cleanly on next sweep.

`--parallel > 1` is **rejected** when `--wiki-root` is set. Concurrent
per-book agents would race on `wiki/index.md`, `wiki/log.md`, and the
dashboard/analytics files; wiki-lint also reads the whole wiki tree and
its auto-fixes are not safe to interleave. If the user passes both,
refuse with: "wiki-root chain requires --parallel 1; rerun without
--parallel or with --parallel 1."

## Step 4 — Per-book status update after return

When each subagent returns, read the relevant on-disk truth files to
determine final status, then mark accordingly. Which file you read
depends on whether `--wiki-root` was set. **First** run the Step 4.0
sanity check below to detect the default-cap trap before treating any
return as authoritative.

### Step 4.0 — Sanity-check the subagent return

Before reading on-disk truth files, inspect the `delegate_task` return:

- **Iteration cap below configured budget** — if `exit_reason ==
  "max_iterations"` AND `iterations_used` is around 50 (well below the
  expected `delegation.max_iterations: 150` from
  Configuration prerequisites), the runtime is enforcing Hermes' built-in
  default of 50, not the configured value. Either `~/.hermes/config.yaml`
  is missing the `delegation` block or the running Hermes process has a
  stale config snapshot.

  Recovery: stop the sweep and surface the misconfiguration to the user.
  Do not retry the book — additional retries will hit the same wall.
  Suggested message: "per-book subagent capped at ~50 iterations; set
  `delegation.max_iterations: 150` in `~/.hermes/config.yaml` (or apply
  the dotfiles role) and rerun."

- **Depth-limit error** — if the subagent's summary mentions
  "Delegation depth limit reached" or `pipeline.json` reports
  `failed_phase: pdf-to-mdbook` with an error citing depth, the
  per-book agent could not delegate `pdf-to-mdbook`. Same root cause
  bucket: surface the `delegation.max_spawn_depth: 2` requirement and
  stop.

- **Cap reached at the configured budget** — if `iterations_used` is at
  or near 150, the book genuinely needed more than the budget allows;
  treat it as a real cap-hit and proceed to Step 4a/4b (the third case
  there marks `in_progress` so the next sweep resumes).

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
| Cap hit at ~50 iterations (config not applied)| Step 4.0 | `delegation.max_iterations` missing from `~/.hermes/config.yaml`. Stop the sweep, surface the misconfiguration, do not retry. |
| `pdf-to-mdbook` delegation rejected by depth | Step 4.0 | `delegation.max_spawn_depth` not set to ≥ 2. Stop the sweep, surface the misconfiguration. |
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
