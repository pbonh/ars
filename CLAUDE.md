# Claude Code agent instructions (AGENTS.md)

> **Important (Claude Code):** Claude Code automatically loads **`CLAUDE.md`** at session start for persistent project instructions. If you want these rules to apply by default, copy this file’s contents into `CLAUDE.md` (or make `CLAUDE.md` include/link to this file).

## Session + context hygiene (Claude Code)

- Use **separate named sessions** for distinct workstreams (e.g., “auth-refactor”, “serde-migration”). In Claude Code: `/rename <name>`; later: `/resume <name>` or `claude --resume <name>`; or `claude --continue` to pick up the most recent session in this directory.
- If an experiment goes sideways, use **`/rewind`** (or `Esc` `Esc`) to restore **code**, **conversation**, or both, or to “Summarize from here” to free context.

## Required handoff

Before ending a task (or when you’re about to run out of context), include this **Handoff** block in your final response:

**Handoff**
- **Done:** …
- **Remaining:** …
- **Decisions:** …
- **Uncertain / needs confirmation:** …
- **Commands run (exact):** …

