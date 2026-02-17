# AGENTS.md

This repo uses **td** as the canonical task backlog + session handoff log. If `td` disagrees with chat history, **trust `td`**.

## Quick start (mandatory)

At the **start of every session**:

1. Inspect current work + start a fresh session context:
   - `td usage --new-session`
2. Pick an issue to work on:
   - `td next` (recommended), or `td ready`, or `td list`
3. Begin + focus the work:
   - `td start <issue-id>`
   - `td focus <issue-id>`

While working:

- Log meaningful progress (keep it short and factual):
  - `td log "…"`
  - `td log --decision "…"`
  - `td log --blocker "…"`
- Link files you touch so reviewers can jump straight to diffs:
  - `td link <issue-id> path/to/file1 path/to/file2`

Before you stop (end of context window, switching tasks, or pausing):

- **Always** write a structured handoff:
  - `td handoff <issue-id> --done "…" --remaining "…" --decision "…" --uncertain "…"`

## Review workflow (mandatory separation)

When implementation is ready for review:

- Submit:
  - `td review <issue-id>`

For review (must be a **different session** than the implementer):

- List reviewable work:
  - `td reviewable`
- Read full context + handoff:
  - `td context <issue-id>`
- Inspect changed files:
  - `td files <issue-id>`
- Decide:
  - `td approve <issue-id>`
  - `td reject <issue-id> --reason "…"` (be specific about what must change)

## Creating tasks (when new work arrives)

If the user request isn’t already tracked in `td`, create an issue first so work stays resumable:

- Create:
  - `td create "<short title>" --type feature|bug|chore|docs|refactor|test --priority P0|P1|P2|P3`
- If needed, model larger efforts:
  - `td epic create "<epic title>" --priority P0|P1|P2|P3`
  - `td create "<child task>" --parent <epic-id>`
- If work depends on other work:
  - `td dep add <issue-id> <depends-on-issue-id>`
  - `td critical-path`

## Querying / finding context

Use these instead of “guessing what’s in progress”:

- `td show <issue-id>` (full details)
- `td search "<text>"` (full-text search)
- `td query "<expression>"` (advanced filtering)
- `td blocked` (find blockers)

## Installing / initializing td (one-time per dev environment)

If `td` is not available:

- Install:
  - `go install github.com/marcus/td@latest`
- Initialize in the repo root:
  - `td init`

> Note: `td init` creates a local database under `.todos/` (keep it untracked).

## Definition of done (for agents)

Only mark work “done” in a handoff when:

- The change is implemented and locally validated (tests/lint/typecheck as appropriate for the repo).
- The handoff’s `--remaining` section is either empty or contains concrete, actionable follow-ups.
- Any non-obvious choices are captured under `--decision`.
- Any open questions are captured under `--uncertain`.

## Project Layout Snapshot (Keep In Sync)

Top-level playbooks in this repo:
- `apps.yml`
- `devbox.yml`
- `distrobox.yml`
- `ars.yml`
- `dotfiles.yml`
- `homebrew.yml`
- `kde.yml`
- `mise.yml`
- `niri.yml`
- `nonroot.yml`
- `ollama.yml`
- `playbook.yml`
- `requirements.yml`

Key structure:
- `roles/` for role definitions
- `group_vars/` and `host_vars/` for inventory-scoped variables
- `inventory/` for inventory definitions
- `vars/` for shared vars (note `vars/local.yml` is skip-worktree via `just setup`)
- `files/` for static files

