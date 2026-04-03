# Agents: Ansible Developer Environment Repository

This repository manages developer environment installations and configurations across macOS and Linux systems using Ansible.

## Playbook Purposes

| Playbook | Purpose |
|----------|---------|
| `mise.yml` | Install mise version manager binary and its configuration |
| `devbox.yml` | Install devbox nix package manager |
| `homebrew.yml` | Install Homebrew and manage packages via Brewfile |
| `nonroot.yml` | Install packages without root privileges (Linux) |
| `dotfiles.yml` | Deploy configuration files for all CLI tools |
| `apps.yml` | Install GUI applications |
| `kde.yml` | Configure KDE desktop environment |
| `niri.yml` | Configure Niri Wayland compositor |
| `ollama.yml` | Install Ollama for local LLMs |
| `distrobox.yml` | Configure distrobox containers |
| `playbook.yml` | Main entry point (imports others) |
| `requirements.yml` | Ansible collection dependencies |

## Role Categories

### Package Manager Installation Roles
These roles install package managers and their packages. They focus on **binaries and software installation**:

- `mise/` — Installs mise binary; manages `mise.toml` tool definitions
- `devbox/` — Installs devbox nix package manager; manages `devbox.json`
- `homebrew/` — Installs Homebrew; generates and manages `Brewfile`
- `nonroot/` — Installs packages in user-space without root
- `apps/` — Installs GUI applications (Flatpak, AppImage, etc.)
- `distrobox/` — Installs and configures distrobox containers
- `kde/` — KDE desktop environment packages and configs
- `niri/` — Niri compositor installation
- `ollama/` — Ollama LLM runtime installation
- `node/` — Node.js/npm ecosystem installation

### Configuration Role (Dotfiles)
This role manages **configuration files** for CLI tools. It does NOT install the tools themselves:

- `dotfiles/` — Deploys config files for: neovim, helix, zellij, tmux, yazi,
  broot, navi, zsh, bash, nushell, direnv, ranger, pi, opencode, claude,
  cline, codex, sidecar, joplin, bookmarks, and more

**Key Principle**: The `dotfiles` role assumes tools are already installed by one of the package manager roles. It only manages configuration deployment.

## Key Structure

- `roles/` — Role definitions (see categories above)
- `group_vars/` — Inventory-scoped variables (e.g., `all.yml` with `dev_packages`, `flatpak_apps_bundle_map`)
- `host_vars/` — Host-specific variables
- `inventory/` — Inventory definitions
- `vars/` — Shared vars (note: `vars/local.yml` is skip-worktree via `just setup`)
- `files/` — Static files for deployment

## Task Runners (just)

The `justfile` imports modular justfiles from `scripts/just/`:

| Module | Path | Purpose |
|--------|------|---------|
| `apps` | `scripts/just/apps.just` | App installation tasks |
| `dev` | `scripts/just/dev.just` | Development workflow tasks |
| `dotfiles` | `scripts/just/dotfiles.just` | Dotfiles deployment tasks |
| `distrobox` | `scripts/just/distrobox.just` | Container management |
| `kde` | `scripts/just/kde.just` | KDE-specific tasks |
| `mdbook` | `scripts/just/mdbook.just` | Documentation build/serve |
| `niri` | `scripts/just/niri.just` | Niri compositor tasks |
| `node` | `scripts/just/node.just` | Node.js tasks |
| `ucore` | `scripts/just/ucore.just` | Universal Core (Fedora) tasks |

Common entry points:
- `just` — Interactive task selector
- `just install-apps` — Run apps.yml playbook

## Documentation

Comprehensive documentation lives in `markdownbook/` (mdBook format):

- `markdownbook/installation.md` — Installation guides for package managers
  - `dev-tools.md` — mise, devbox, homebrew, nonroot
  - `gui.md` — KDE, workstation GUI setup
  - `apps.md` — Application installation
  - `optional.md` — Optional components
- `markdownbook/configuration.md` — Post-install configuration
  - `dotfiles.md` — Dotfiles role documentation
  - `gui.md` — GUI configuration
  - `examples.md` — Usage examples
- `markdownbook/distrobox.md` — Container workflow documentation

Build/serve docs: `just mdbook-serve` (or see `scripts/just/mdbook.just`)

## Ansible Authoring Guidelines

- Prefer `ansible.builtin` modules and idempotent patterns
- Avoid `shell`/`command` unless necessary; if used, set `changed_when` and `failed_when`
- Structure roles: `defaults/main.yml`, `tasks/main.yml`, `handlers/main.yml`
- Keep YAML concise, consistent, and check-mode friendly
- Respect existing playbook entrypoints and `just` tasks

## Terminal-First Workflow

This repo assumes a terminal-centric workflow using: `zellij`, `neovim`, `fzf`, `nushell`, `sidecar`. Provide CLI-friendly steps and composable commands suitable for running in panes. Avoid GUI-only instructions. When suggesting navigation or search, prefer `rg`, `fd`, and `fzf`-style patterns.
