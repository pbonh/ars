---
title: "Pi Worktree Isolation"
type: concept
tags: [concept, pi, subagent, git, isolation]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/pi-subagents-readme.md"]
confidence: high
---

## Definition

Pi worktree isolation (`worktree: true`) gives each parallel
[[concepts/pi-subagent|subagent]] its own git worktree branched from `HEAD`, so
concurrent children editing the same repository cannot clobber each other's
working tree.

## How It Works

- Setting `worktree: true` on a parallel `tasks` array or a chain `parallel:`
  group creates an isolated worktree per child.
- Requirements:
  - run inside a git repo
  - the working tree must be clean
  - `node_modules/` is symlinked into each worktree when present
  - task-level `cwd` overrides must be omitted or match the shared cwd
  - a configured `worktreeSetupHook` must return valid JSON before timeout
- After a worktree parallel step completes, per-agent diff stats are appended to
  the output and full patch files are written to artifacts. Worktrees and temp
  branches are cleaned up in `finally` blocks.

### Setup hook

`worktreeSetupHook` runs once per created worktree. Its path must be absolute,
`~/...`, or repo-relative (bare command names are rejected). stdin is a JSON
object (`repoRoot`, `worktreePath`, `agentCwd`, `branch`, `index`, `runId`,
`baseCommit`); stdout must be one JSON object, e.g.
`{ "syntheticPaths": [".venv", ".env.local"] }`. `syntheticPaths` are relative
to the worktree root and are removed before diff capture so helper files do not
pollute patches. Tracked files can never be excluded — marking a tracked path as
synthetic fails setup. Default timeout is `30000` ms
(`worktreeSetupHookTimeoutMs`).

## Key Parameters

- `worktree: true` (default `false`) on parallel tasks or a parallel chain group.
- `worktreeSetupHook` / `worktreeSetupHookTimeoutMs` in config.

## When To Use

- Running multiple `worker` agents in parallel that each edit files, where they
  would otherwise collide in a single checkout.
- Any fan-out implementation step where you want clean, independently-diffable
  patches per child.

## Risks & Pitfalls

- A dirty working tree blocks worktree creation — commit or stash first.
- Per-task `cwd` overrides conflicting with the shared cwd fail the run.
- The setup hook must emit a single valid JSON object before the timeout, or
  setup fails; environments needing untracked helper files (`.venv`, `.env`)
  must declare them as `syntheticPaths`.

## Related Concepts

- [[concepts/pi-subagent-chain]]
- [[concepts/pi-subagent-execution-mode]]
- [[concepts/pi-subagent]]

## Sources

- [pi-subagents README](raw/pi-subagents-readme.md)
</content>
