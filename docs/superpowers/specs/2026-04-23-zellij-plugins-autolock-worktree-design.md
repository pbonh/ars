# Zellij Plugins: autolock + worktree (structured plugin schema)

**Date:** 2026-04-23
**Scope:** `roles/dotfiles/defaults/main/zellij.yml`, `roles/dotfiles/templates/zellij/config.kdl.j2`
**Branch:** `main` (no PR, no branch)

## Goal

Add two zellij plugins to the `dotfiles` role:

1. **zellij-worktree** (`sharph/zellij-worktree`) — on-demand git worktree switcher launched via `Ctrl a`.
2. **zellij-autolock** (`fresh2dev/zellij-autolock`) — background plugin that auto-locks zellij when configured commands are active.

Autolock requires a capability the current schema does not support: loading a plugin at session start with config args. Rather than special-casing it, replace the existing raw-KDL `keybindings.shared_except_locked` field with a structured schema that handles both on-demand and startup-loaded plugins uniformly. Migrate `forgot`, `room`, and `harpoon` to the new shape in the same change.

## Non-goals

- Refactoring layout KDL (`zellij_kdl_layouts_from_projects_json`, `zellij_kdl_layouts_extra`).
- Refactoring yazelix mode keybindings (`yazelix_keybindings_default`).
- Refactoring zjstatus format strings.
- Moving inline themes (`dracula`, `gruvbox-dark`) out of `config.kdl.j2`.
- Changing `mini_ci`, `zjstatus`, or the commented-out `monocle` entries (beyond what falls out of the schema change — they have no keybindings and keep just `url`).

These are tracked as future refactors but out of scope here.

## Design

### Schema: `zellij_plugins` entries

Each entry keeps required `url` and gains two optional structured fields:

- `launch_keybinding` — on-demand plugin launched via a keybinding in `shared_except "locked"` mode.
- `load_on_startup` — plugin loaded at session start via zellij's `load_plugins { }` block.

An entry may have zero or one of these (having both is unusual but not forbidden; the template renders both independently).

```yaml
zellij_plugins:
  worktree:
    url: "https://github.com/sharph/zellij-worktree/releases/latest/download/zellij-worktree.wasm"
    launch_keybinding:
      key: "Ctrl a"
      args:
        floating: true
        move_to_focused_tab: true

  autolock:
    url: "https://github.com/fresh2dev/zellij-autolock/releases/latest/download/zellij-autolock.wasm"
    load_on_startup:
      args:
        triggers: "nvim|hx|fzf|yazi|btm|less|man|lazygit|atuin|zoxide"
        reaction_seconds: "0.3"
```

#### Rendering rules

- `args` is a dict. Each entry renders as one KDL child node: `{{ key | to_json }} {{ value | to_json }}`.
  - Keys render quoted: `"triggers" "…"`, `"floating" true`. KDL treats quoted and bare property identifiers identically, so this is equivalent to the existing mix of bare and quoted keys (`floating true`, `"LOAD_ZELLIJ_BINDINGS" "true"`). Quoting both sides removes the ambiguity.
  - String values render quoted: `"triggers" "nvim|hx"`.
  - Bool values render bare: `"floating" true`.
- `launch_keybinding.key` is the zellij keybinding string (e.g., `"Ctrl a"`), rendered as-is inside `bind "…" { … }`.
- The plugin wasm filename is derived from `url | basename`. No explicit `wasm_name` field.

#### Removed field

- `keybindings.shared_except_locked` (raw-KDL) is removed. All existing plugins using it are migrated to `launch_keybinding`.

### Template: `config.kdl.j2`

Two generic loops replace current logic.

**Keybindings block** (replaces current raw-KDL dump inside `shared_except "locked"`):

```jinja
keybinds {
    shared_except "locked" {
        {% for name, plugin in zellij_plugins.items() if plugin.launch_keybinding is defined %}
        bind "{{ plugin.launch_keybinding.key }}" {
            LaunchOrFocusPlugin "file:{{ zellij_plugin_dir }}/{{ plugin.url | basename }}" {
                {% for k, v in (plugin.launch_keybinding.args | default({})).items() %}
                {{ k | to_json }} {{ v | to_json }}
                {% endfor %}
            }
        }
        {% endfor %}
    }
}
```

**`load_plugins` block** (replaces the empty `load_plugins { }`):

```jinja
load_plugins {
    {% for name, plugin in zellij_plugins.items() if plugin.load_on_startup is defined %}
    "file:{{ zellij_plugin_dir }}/{{ plugin.url | basename }}" {
        {% for k, v in (plugin.load_on_startup.args | default({})).items() %}
        {{ k | to_json }} {{ v | to_json }}
        {% endfor %}
    }
    {% endfor %}
}
```

No other changes to `config.kdl.j2`. The plugin-aliases block, themes, env vars, and general options are untouched.

### Tasks: `tasks/zellij_plugins.yml`

No changes. The existing `get_url` loop already iterates every `zellij_plugins` entry by `url`, so new entries are picked up automatically.

### Concrete plugin entries

**New:**

```yaml
worktree:
  url: "https://github.com/sharph/zellij-worktree/releases/latest/download/zellij-worktree.wasm"
  launch_keybinding:
    key: "Ctrl a"
    args:
      floating: true
      move_to_focused_tab: true

autolock:
  url: "https://github.com/fresh2dev/zellij-autolock/releases/latest/download/zellij-autolock.wasm"
  load_on_startup:
    args:
      triggers: "nvim|hx|fzf|yazi|btm|less|man|lazygit|atuin|zoxide"
      reaction_seconds: "0.3"
```

Release URLs use `/releases/latest/download/…` (same pattern as the existing `room` entry). No version pinning.

**Migrated:**

```yaml
forgot:
  url: "https://github.com/karimould/zellij-forgot/releases/download/0.3.0/zellij_forgot.wasm"
  launch_keybinding:
    key: "Ctrl k"
    args:
      LOAD_ZELLIJ_BINDINGS: "true"
      floating: true

room:
  url: "https://github.com/rvcas/room/releases/latest/download/room.wasm"
  launch_keybinding:
    key: "Ctrl y"
    args:
      floating: true
      ignore_case: true

harpoon:
  url: "https://github.com/Nacho114/harpoon/releases/download/v0.1.0/harpoon.wasm"
  launch_keybinding:
    key: "Ctrl z"
    args:
      floating: true
      move_to_focused_tab: true
```

**Unchanged:** `mini_ci`, `zjstatus` (neither has a keybinding nor startup load — both retain only `url`). The commented-out `monocle` block is left as-is.

## Validation

- `ansible-playbook dotfiles.yml --check --diff` on the zellij role should show a diff for `config.kdl` and no other churn.
- Render `config.kdl` locally and verify:
  - `keybinds { shared_except "locked" { … } }` contains `bind` entries for `Ctrl k` (forgot), `Ctrl y` (room), `Ctrl z` (harpoon), `Ctrl a` (worktree) — no stale raw-KDL fragments.
  - `load_plugins { }` contains one entry for autolock with `"triggers"` and `"reaction_seconds"` child nodes.
  - `"LOAD_ZELLIJ_BINDINGS" "true"` still renders correctly for `forgot` (quoted key + quoted string value).
- Start a new zellij session and confirm:
  - `Ctrl a` launches the worktree picker (floating).
  - Running `nvim` in a pane triggers autolock within ~0.3s; exiting nvim unlocks.
  - `Ctrl k`, `Ctrl y`, `Ctrl z` still launch `forgot`/`room`/`harpoon` as before.

## Risks / open questions

- **Ctrl y collision** with yazelix scroll-mode binding. Acknowledged; they coexist by layout scoping — no change.
- **`/releases/latest/`** means a bad upstream release could break downloads until reverted. Accepted (matches existing `room` choice).
- **autolock trigger scope** — the trigger regex matches process names in a pane. If the user adds new interactive tools later (e.g., k9s, btop replacement), the trigger list needs updating. Accepted; trivial one-line edit.
