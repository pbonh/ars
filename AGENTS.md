## MANDATORY: Use td for Task Management

Run td usage --new-session at conversation start (or after /clear). This tells you what to work on next.

When presenting changes, include the usual summary and file list, then prompt the user to update td state when appropriate. Follow the td state diagram rules:
- `open` → `in_progress` via `td start <id>`
- `in_progress` → `in_review` via `td review <id>`
- `in_review` → `closed` via `td approve <id>` (must be a different session)
- `in_review` → `blocked` via `td reject <id> --reason "..."`
- `in_progress` → `blocked` when work cannot proceed (log a blocker with `td log --blocker "..."`)

If unsure which state applies, ask and provide the exact td command(s) to run.

## Project Layout Snapshot (Keep In Sync)

Top-level playbooks in this repo:
- `apps.yml`
- `devbox.yml`
- `distrobox.yml`
- `dotfiles.yml`
- `homebrew.yml`
- `kde.yml`
- `mise.yml`
- `niri.yml`
- `nonroot.yml`
- `ollama.yml`
- `playbook.yml`
- `requirements.yml`

Justfile entrypoints:
- Root `justfile` imports `scripts/just/*.just` and uses `just --choose` by default.
- `scripts/just/apps.just`: `install-apps`
- `scripts/just/distrobox.just`: `distrobox`, `distrobox-ubuntu`, `pull-ars`
- `scripts/just/dotfiles.just`: `install-requirements`, `setup`, `dotfiles`, `mise`, `install-mise-gpg`, `config-mise`, `devbox`, `install-homebrew`, `homebrew`, `nonroot`, `dot`, `shell`, `nushell`, `scripts`, `bash`, `zsh`, `tcsh`, `neovim`, `rebuild-neovim`, `zellij`, `yazi`, `navi`, `ai`, `ollama`, `code2prompt`
- `scripts/just/kde.just`: `workstation-kde`, `backup-kde-config`, `restore-kde-config`, `generate-uuid`
- `scripts/just/mdbook.just`: `mdbook-build`, `mdbook-serve`, `mdbook-serve-all`, `mdbook-push`, `mdbook-rsync`, `mdbook-gh-pages`
- `scripts/just/niri.just`: `workstation-niri`
- `scripts/just/ucore.just`: `regenerate-ignition-file`

Key structure:
- `roles/` for role definitions
- `group_vars/` and `host_vars/` for inventory-scoped variables
- `inventory/` for inventory definitions
- `vars/` for shared vars (note `vars/local.yml` is skip-worktree via `just setup`)
- `files/` for static files

## Specialization: Ansible Authoring

Primary focus is writing Ansible modules/tasks/roles/variables for this repo.
- Prefer `ansible.builtin` modules and idempotent patterns.
- Avoid `shell`/`command` unless necessary; if used, set `changed_when` and `failed_when`.
- Structure roles as: `defaults/main.yml` for defaults, `tasks/main.yml` for tasks, `handlers/main.yml` for handlers, and use `notify` where appropriate.
- Keep YAML concise, consistent, and check-mode friendly.
- Respect existing playbook entrypoints and `just` tasks; avoid inventing new flows unless needed.

## Terminal-Centric Developer Flow

Assume a terminal-first workflow using `zellij`, `neovim`, `fzf`, `nushell`, and `sidecar`.
- Provide CLI-friendly steps and short, composable commands suitable for running in panes.
- Avoid GUI-only instructions.
- For search/navigation, prefer `rg`, `fd`, and `fzf` patterns.

## Specialization: Ansible Authoring

Focus on writing Ansible modules/tasks/roles/variables. Prefer `ansible.builtin` modules, idempotent patterns, and check-mode friendly logic. Avoid `shell`/`command` unless necessary; if used, set `changed_when`/`failed_when`. Use clear variable naming, defaults in role `defaults/main.yml`, role tasks in `tasks/main.yml`, handlers in `handlers/main.yml`, and `notify` where appropriate. Keep YAML concise and consistent.

## Terminal-Centric Developer Flow

Assume a terminal-first workflow with `zellij`, `neovim`, `fzf`, `nushell`, and `sidecar`. Provide CLI-friendly steps and short, composable commands suitable for running in panes. Avoid GUI-only instructions. When suggesting navigation or search, prefer `rg`, `fd`, and `fzf`-style patterns.
