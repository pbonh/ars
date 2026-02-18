# Agents: Mandatory: use td usage --new-session to see open work.

# Agents: Before context ends, ALWAYS run:
```sh
td handoff <issue-id> --done "..." --remaining "..." --decision "..." --uncertain "..."
```

# Agents: Project Layout Snapshot (Keep In Sync)

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

