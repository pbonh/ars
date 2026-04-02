# Dotfiles Deployment Separation: Ansible Render + Tuckr Deploy

**Date:** 2026-04-02
**Status:** Approved

## Problem

The dotfiles role currently handles both config file content generation (Jinja2 rendering) and deployment to final locations (`$HOME`). This couples content management to deployment, embeds secrets and absolute paths in the deployment step, and makes config changes hard to review before they land on the system.

## Solution

Separate config rendering from deployment:

1. **Ansible** renders templates into a git-tracked `predeploy/` directory with portable paths and placeholder secrets.
2. **Tuckr** symlinks the rendered configs to `$HOME`, runs hooks for secret injection and post-install tasks (git clones, plugin downloads).

## Predeploy Directory Structure

```
predeploy/
├── Configs/
│   ├── bash/
│   │   ├── .bashrc
│   │   └── .bashrc.d/
│   │       └── (plugin source files)
│   ├── bash_macos/
│   │   └── .bashrc.d/homebrew
│   ├── bash_linux/
│   │   └── .bashrc.d/devbox
│   ├── zsh/
│   │   └── .zshrc
│   ├── nushell/
│   │   └── .config/nushell/
│   │       ├── config.nu
│   │       └── env.nu
│   ├── neovim/
│   │   └── .config/<appname>-modular/
│   │       ├── init.lua
│   │       └── lua/...
│   ├── zellij/
│   │   └── .config/zellij/
│   │       ├── config.kdl
│   │       ├── layouts/
│   │       └── themes/
│   ├── tmux/
│   │   └── .config/tmux/...
│   ├── yazi/
│   │   └── .config/yazi/...
│   ├── claude/
│   │   └── .config/claude/
│   │       └── agent.md
│   ├── opencode/
│   ├── codex/
│   ├── scripts/
│   │   └── .local/bin/...
│   └── ... (one group per current task file)
├── Hooks/
│   ├── claude/
│   │   └── post.sh        (inject secrets from secrets file)
│   ├── bash/
│   │   └── post.sh        (git clone fzf-tab, git-fuzzy)
│   ├── zellij/
│   │   └── post.sh        (plugin clones)
│   └── yazi/
│       └── post.sh        (flavor/plugin downloads, git clones)
└── Templates/
    ├── claude/
    │   └── api-key-helper.sh  (contains __ANTHROPIC_API_KEY__ placeholder)
    └── cline/
        └── secrets.json      (contains __CLINE_SECRETS__ placeholder)
```

### Group naming

Group names match the current task file names: `bash`, `zsh`, `nushell`, `neovim`, `zellij`, `tmux`, `yazi`, `claude`, `opencode`, `codex`, `scripts`, `direnv`, `broot`, `navi`, `bookmarks`, `joplin`, `helix`, `tcsh`, `ranger`, `superpowers`, `sidecar`.

### Conditional deployment

Platform-specific configs go in suffixed directories per tuckr convention:

- `<group>/` — cross-platform configs, always deployed
- `<group>_linux/` — Linux-only configs
- `<group>_macos/` — macOS-only configs

Tuckr automatically deploys the correct platform group alongside the base group. Ansible decides which conditional directory to render into based on existing `when:` conditions in tasks.

## Ansible Changes

### New default variables

```yaml
predeploy_root: "{{ playbook_dir }}/predeploy"
predeploy_configs: "{{ predeploy_root }}/Configs"
predeploy_hooks: "{{ predeploy_root }}/Hooks"
predeploy_templates: "{{ predeploy_root }}/Templates"
```

### Task file changes

Each task file in `roles/dotfiles/tasks/` changes in three ways:

1. **`dest:` targets predeploy tree.** Example:
   ```yaml
   # Before
   dest: "{{ dotfiles_user_home }}/.bashrc"
   # After
   dest: "{{ predeploy_configs }}/bash/.bashrc"

   # Platform-specific
   dest: "{{ predeploy_configs }}/bash_linux/.bashrc.d/devbox"
   dest: "{{ predeploy_configs }}/bash_macos/.bashrc.d/homebrew"
   ```

2. **Non-render tasks removed.** Git clones, directory creation, file downloads are extracted from Ansible tasks and moved to tuckr hook scripts.

3. **Hook generation added.** Ansible renders hook scripts from `.j2` templates into `predeploy/Hooks/<group>/`.

### Template variable substitutions

| Current variable | New value in template content |
|---|---|
| `{{ dotfiles_user_home }}` | `$HOME` (shell contexts) or `~` (tilde expansion contexts) |
| `{{ ansible_env.HOME }}` | Same treatment as above |
| `{{ claude_anthropic_api_key }}` | `__ANTHROPIC_API_KEY__` |
| `{{ cline_secrets \| to_nice_json }}` | Entire file written by hook from secrets file (JSON blob, not simple sed substitution) |
| Tool paths (`{{ fzf_exe }}`, etc.) | Still resolved by Ansible (machine-specific, not secrets) |

### What stays unchanged

- All non-dotfiles roles (homebrew, mise, devbox, apps, etc.)
- `group_vars/`, `host_vars/`, `vars/` structure
- Inventory and playbook structure
- Template content logic (Jinja2 loops, conditionals for plugin lists, etc.)
- `.j2` template files remain in `roles/dotfiles/templates/`

## Tuckr Integration

### Dotfiles path

Tuckr expects its directory at `~/.config/dotfiles` or `~/.dotfiles`. A symlink connects it:

```sh
ln -s /path/to/ars/predeploy ~/.config/dotfiles
```

This is set up once, either manually or via a justfile `setup` recipe.

### Secrets file

`~/.config/ars-secrets` — non-git-tracked, simple key=value format:

```sh
ANTHROPIC_API_KEY=sk-ant-...
CLINE_SECRETS='{"key": "value"}'
```

### Hook design

**Pre-hooks** are not used. All hooks are **post-hooks** to run after tuckr symlinks configs.

**Secret injection hooks** read templates from `predeploy/Templates/<group>/`, substitute placeholders using values from the secrets file, and write the final file directly to the target location (bypassing symlinks since the file contains secrets that must not be git-tracked).

Example — `Hooks/claude/post.sh`:

```sh
#!/bin/sh
SECRETS_FILE="${HOME}/.config/ars-secrets"
[ -f "$SECRETS_FILE" ] && . "$SECRETS_FILE"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE_DIR="${SCRIPT_DIR}/../../Templates/claude"
TARGET_DIR="${HOME}/.config/claude"

mkdir -p "$TARGET_DIR"
sed "s|__ANTHROPIC_API_KEY__|${ANTHROPIC_API_KEY}|g" \
    "$TEMPLATE_DIR/api-key-helper.sh" > "$TARGET_DIR/api-key-helper.sh"
chmod +x "$TARGET_DIR/api-key-helper.sh"
```

**Post-install hooks** handle git clones and plugin downloads.

Example — `Hooks/bash/post.sh`:

```sh
#!/bin/sh
BASHRC_D="${HOME}/.bashrc.d"
mkdir -p "$BASHRC_D"

[ -d "$BASHRC_D/fzf-tab-completion" ] || \
    git clone https://github.com/lincheney/fzf-tab-completion "$BASHRC_D/fzf-tab-completion"

[ -d "$BASHRC_D/git-fuzzy" ] || \
    git clone https://github.com/bigH/git-fuzzy "$BASHRC_D/git-fuzzy"
```

**Ansible generates hook scripts** from `.j2` templates into `predeploy/Hooks/`, since repo URLs, plugin lists, and tool paths come from Ansible vars.

## Workflow

### Commands

```sh
# Step 1: Render configs into predeploy tree
ansible-playbook dotfiles.yml

# Step 2: Deploy to system
tuckr set \*
```

### Justfile recipes

```just
# Render configs only
render:
    ansible-playbook dotfiles.yml

# Deploy rendered configs via tuckr
deploy:
    tuckr set \*

# Full flow: render then deploy
sync: render deploy

# Remove all deployed symlinks
undeploy:
    tuckr unset \*

# Check deployment status
status:
    tuckr status
```

### Reviewing changes

After rendering, `git diff predeploy/` shows exactly what changed in configs before deploying. This enables a review step between render and deploy.

## Migration Path

1. Create `predeploy/` structure with `Configs/`, `Hooks/`, `Templates/` directories.
2. Add new default variables (`predeploy_root`, etc.).
3. Refactor task files one group at a time, starting with simpler groups (e.g., `bash` first).
4. For each group:
   - Change `dest:` to target `predeploy_configs`
   - Replace `dotfiles_user_home` with `$HOME`/`~` in template content
   - Replace secret values with `__PLACEHOLDER__` tokens
   - Extract git clones, downloads, directory creation to hook templates
   - Add platform-conditional directories where applicable
5. Test each group: `ansible-playbook dotfiles.yml --tags bash`, then `tuckr set bash`.
6. Once all groups are migrated, remove old direct-deploy paths.
7. Set up the tuckr dotfiles symlink and secrets file.
8. Update justfile with new recipes.

## Scope Estimate

- ~15 task files to refactor (`dest:` changes + extracting non-render tasks)
- ~5–10 hook script templates to create
- ~2–3 secret-bearing templates to move to `Templates/`
- New defaults for predeploy path variables
- Justfile recipe additions
- One-time tuckr symlink setup
