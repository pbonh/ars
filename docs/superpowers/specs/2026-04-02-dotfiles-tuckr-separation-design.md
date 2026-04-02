# Dotfiles Deployment Separation: Ansible Render + Tuckr Deploy

**Date:** 2026-04-02
**Status:** Approved

## Problem

The dotfiles role currently handles both config file content generation (Jinja2 rendering) and deployment to final locations (`$HOME`). This couples content management to deployment, embeds secrets and absolute paths in the deployment step, and makes config changes hard to review before they land on the system.

## Solution

Separate config content management from deployment:

1. **Ansible** renders templates, creates directories, clones plugins, and downloads extras — all into a git-tracked `predeploy/` directory with portable paths and placeholder secrets. Third-party content (cloned repos, downloaded plugins) is `.gitignore`'d.
2. **Tuckr** symlinks the fully-assembled `predeploy/` tree to `$HOME`, and runs hooks for the small number of groups that need secret injection.

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
│   └── cline/
│       └── post.sh        (inject secrets from secrets file)
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

2. **Non-render tasks retargeted.** Directory creation, git clones, and file downloads stay in Ansible but target the `predeploy/` tree instead of `$HOME`. Cloned repos and downloaded plugins land inside the appropriate group's directory structure (e.g., `predeploy/Configs/bash/.bashrc.d/fzf-tab-completion/`). These are `.gitignore`'d by the user since they're third-party content.

3. **Hook generation added.** Ansible renders secret-injection hook scripts from `.j2` templates into `predeploy/Hooks/<group>/`. Hooks are only needed for groups with secrets.

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

Hooks are **only** needed for groups containing secrets. All other deployment (directory creation, git clones, plugin downloads) is handled by Ansible writing into the `predeploy/` tree, and tuckr symlinking the result to `$HOME`.

**Secret injection hooks** are post-hooks. They read templates from `predeploy/Templates/<group>/`, substitute placeholders using values from the secrets file, and write the final file directly to the target location (bypassing symlinks since the file contains secrets that must not be git-tracked).

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

**Ansible generates hook scripts** from `.j2` templates into `predeploy/Hooks/`, since secret variable names and tool paths come from Ansible vars.

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

## Git Management

The `predeploy/` directory is git-tracked, but third-party content (cloned plugins, downloaded files) should be `.gitignore`'d. The user manages the `.gitignore` entries for these. Example:

```gitignore
# Third-party plugins cloned by Ansible
predeploy/Configs/bash/.bashrc.d/fzf-tab-completion/
predeploy/Configs/bash/.bashrc.d/git-fuzzy/
predeploy/Configs/zellij/.config/zellij/plugins/
predeploy/Configs/yazi/.config/yazi/flavors/
predeploy/Configs/yazi/.config/yazi/plugins/
```

## Migration Path

1. Create `predeploy/` structure with `Configs/`, `Hooks/`, `Templates/` directories.
2. Add new default variables (`predeploy_root`, etc.).
3. Refactor task files one group at a time, starting with simpler groups (e.g., `bash` first).
4. For each group:
   - Change `dest:` to target `predeploy_configs`
   - Retarget git clones, downloads, directory creation to predeploy tree
   - Replace `dotfiles_user_home` with `$HOME`/`~` in template content
   - Replace secret values with `__PLACEHOLDER__` tokens
   - Add platform-conditional directories where applicable
   - Add `.gitignore` entries for third-party content
5. For secret-containing groups only: create hook templates.
6. Test each group: `ansible-playbook dotfiles.yml --tags bash`, then `tuckr set bash`.
7. Once all groups are migrated, remove old direct-deploy paths.
8. Set up the secrets file.
9. Update justfile with new recipes.

## Scope Estimate

- ~15 task files to refactor (`dest:` changes + retargeting non-render tasks to predeploy)
- ~2–3 hook script templates to create (secret-containing groups only)
- ~2–3 secret-bearing templates to move to `Templates/`
- New defaults for predeploy path variables
- `.gitignore` additions for third-party content in predeploy
- Justfile recipe additions
- No symlink setup needed — `TUCKR_HOME` is set in justfile recipes
