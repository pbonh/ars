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
