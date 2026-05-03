# Zellij + Television: unified command surface

**Date:** 2026-05-02
**Scope:** `roles/dotfiles/defaults/main/zellij.yml`, `roles/dotfiles/defaults/main/television.yml` (new), `roles/dotfiles/tasks/television.yml` (new), `roles/dotfiles/templates/television/` (new), `roles/dotfiles/templates/zellij/config.kdl.j2`
**Branch:** `main` (no PR, no branch)

## Goal

Expose the breadth of Zellij actions (layouts, sessions, panes, plugins, AI agents, common actions, git worktrees) through Television's fuzzy picker, so the user doesn't need to memorize zellij CLI flags or scattered keybindings.

The picker is launched as a Zellij floating pane that inherits `$ZELLIJ` / `$ZELLIJ_SESSION_NAME`; on selection, the picker fires `zellij action ...` against the parent session and exits, and the floating pane closes.

Two reinforcing wins:

1. **DRY against existing Ansible vars.** Television cable channels are Jinja-templated from the same `zellij_kdl_layouts`, `zellij_ai_agents`, and `zellij_plugins` declarations that already drive Zellij. Adding a new project layout or AI agent automatically flows into the picker.
2. **Reuses existing autolock plumbing.** Adding `tv` to the autolock `triggers` list cleanly hands keyboard focus to TV while it runs and returns it to Zellij when TV exits.

## Non-goals

- Replacing existing zellij plugins beyond `forgot` (which the master picker absorbs).
- Refactoring `zellij_kdl_layouts_from_projects_json` or `zellij_kdl_layouts_extra`.
- Building a wasm Zellij plugin. Television runs as a regular floating pane; no wasm.
- Theming Television. Default theme stays; theme work is its own task if ever wanted.
- Building a wrapper binary (`zlt`-style shim). Channels handle dynamic state via `source.command` shell-outs directly.
- Cleaning up the user's current `~/.config/television/config.toml` and `~/.config/television/cable/` content. The dotfiles role takes ownership going forward; pre-existing files will be overwritten by the deploy.

## Design

### Component overview

```
┌─ Zellij session (parent) ─────────────────────────────────────┐
│                                                               │
│  Ctrl+k          → tv --select-channel  (master picker)       │
│  Alt+l           → tv zellij-layouts    (direct: layouts)     │
│  Alt+a           → tv zellij-ai-agents  (direct: AI agents)   │
│                                                               │
│  All three: floating=true, close_on_exit=true                 │
│             autolock triggers on `tv` → Zellij locked         │
│                                                               │
│  ┌─ floating pane ─────────────────────────────────────────┐  │
│  │  $ tv <channel>                                         │  │
│  │  source: static-templated   |   shell command           │  │
│  │  preview: optional shell command per entry              │  │
│  │  actions: Enter / Ctrl+s / Ctrl+a → `zellij action ...` │  │
│  │           inherits $ZELLIJ → targets parent session     │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  TV exits → pane closes → autolock unlocks (≤ reaction_secs)  │
└───────────────────────────────────────────────────────────────┘
```

### Channel taxonomy

| Channel name           | Source kind            | Source                                                       | Default action (Enter)                                                |
|------------------------|------------------------|--------------------------------------------------------------|-----------------------------------------------------------------------|
| `zellij-layouts`       | static (templated)     | keys of `zellij_kdl_layouts`                                 | `zellij action new-tab --layout={selected}`                           |
| `zellij-ai-agents`     | static (templated)     | keys of `zellij_ai_agents`                                   | `zellij action new-pane --floating --name "<pane_name>" -- <command>` |
| `zellij-actions`       | static (templated)     | curated catalog (NewPane, NewTab, FullScreen, ToggleSync, ToggleFloating, MoveTab L/R, RenameSession, RenameTab, etc.) | runs the bound `zellij action ...`                                    |
| `zellij-plugins`       | static (templated)     | keys of `zellij_plugins` that have `launch_keybinding`       | `zellij action launch-or-focus-plugin file:{path}` (forgot replacement) |
| `zellij-sessions`      | dynamic (shell)        | `zellij list-sessions -s`                                    | `zellij action switch-session {selected}`                             |
| `zellij-panes`         | dynamic (shell)        | `zellij action query-tab-names` + tab-name mapping           | `zellij action go-to-tab-name {selected}`                             |
| `zellij-worktrees`     | dynamic (shell)        | `git worktree list --porcelain` parsed for paths             | `zellij action new-tab --cwd={selected}`                              |

The **master picker** is Television's built-in remote-control / channel-picker view, opened by launching `tv --select-channel`. The naming convention `zellij-*` keeps the Zellij-related channels grouped for visual scanning. (Other unrelated channels users may have continue to coexist; nothing filters them out.)

### Alternate actions

Each channel may expose alternate actions via TV's per-channel `[[keybindings]]` array (see the rendered example below). Spec'd defaults:

- `zellij-layouts`:
  - `Enter` → `zellij action new-tab --layout={selected}` (current session)
  - `Ctrl+s` → `zellij --layout={selected}` (new detached session)
- `zellij-ai-agents`:
  - `Enter` → floating pane (`zellij action new-pane --floating -- <command>`)
  - `Ctrl+t` → new tab with the command (`zellij action new-tab --name "<pane_name>" -- <command>`)
- `zellij-sessions`:
  - `Enter` → `zellij action switch-session {selected}` (when inside zellij)
  - `Ctrl+a` → `zellij attach {selected}` (when invoked outside zellij)

Actions in TV cable channel TOML are written as exec commands; the dotfiles template wires `{selected}` placeholders to TV's `{}` substitution syntax.

### Out-of-Zellij behavior

Channels run fine outside Zellij (the user can `tv zellij-layouts` from a plain shell). The Enter action checks `[ -n "$ZELLIJ" ]` and falls back appropriately:

- Inside Zellij → `zellij action ...` against the current session.
- Outside Zellij → `zellij --layout=...` (new session) or `zellij attach ...` (sessions channel).

This is implemented in the action template, not in a wrapper script.

### Zellij keybinding changes

In `roles/dotfiles/defaults/main/zellij.yml`:

1. **Remove** the `forgot` entry from `zellij_plugins`. This drops the wasm download and the `Ctrl k` keybinding the schema currently emits.
2. **Add** three TV-launching bindings. These are Run-style bindings (not plugin launches), so they don't fit the `zellij_plugins` schema — they belong as a new top-level structured key `zellij_television_keybindings`, consumed by `templates/zellij/config.kdl.j2`:

   ```yaml
   zellij_television_keybindings:
     master:
       key: "Ctrl k"
       channel: null            # null → tv --select-channel
     layouts:
       key: "Alt l"
       channel: "zellij-layouts"
     ai_agents:
       key: "Alt a"
       channel: "zellij-ai-agents"
   ```

3. **Append** `tv` to the autolock plugin's `triggers` string:

   ```yaml
   autolock:
     url: "https://github.com/fresh2dev/zellij-autolock/releases/latest/download/zellij-autolock.wasm"
     load_on_startup:
       args:
         triggers: "nvim|hx|fzf|yazi|btm|less|man|lazygit|atuin|zoxide|tv"
         reaction_seconds: "1.0"
   ```

The KDL template emits each TV keybinding under `shared_except "locked"`:

```kdl
bind "Ctrl k" {
    Run "tv" "--select-channel" {
        floating true
        close_on_exit true
    }
    SwitchToMode "Normal"
}
```

(With the channel name argument omitted when `channel: null`.)

### Ansible role structure

**New files:**

- `roles/dotfiles/defaults/main/television.yml`

  Vars:
  - `television_config_dir: "{{ xdg_config_dir }}/television"`
  - `television_cable_dir: "{{ television_config_dir }}/cable"`
  - `television_default_channel: "files"` (preserves TV's stock default)
  - `television_theme: "default"`
  - `television_global_settings` — dict mapping to `[ui]`, `[ui.input_bar]`, etc. blocks in `config.toml`. Lifted from the user's existing config so behavior is preserved.
  - `television_channels` — dict; each value has `source.command`, `preview.command` (optional), `actions` (dict of keybinding → exec template). Computed from `zellij_kdl_layouts`, `zellij_ai_agents`, `zellij_plugins`, plus a curated `zellij_actions` catalog.

- `roles/dotfiles/tasks/television.yml`

  Tasks:
  1. Ensure `television_config_dir` and `television_cable_dir` exist.
  2. Template `config.toml.j2` → `{{ television_config_dir }}/config.toml`.
  3. Loop `television_channels` and template `_channel.toml.j2` → `{{ television_cable_dir }}/{{ item.key }}.toml`.
  4. Cleanup task to remove `{{ zellij_plugin_dir }}/zellij_forgot.wasm` if present (file module, `state: absent`).

- `roles/dotfiles/templates/television/config.toml.j2` — global TV config.
- `roles/dotfiles/templates/television/cable/_channel.toml.j2` — single parameterized template producing each cable file.

**Modified files:**

- `roles/dotfiles/defaults/main/zellij.yml`:
  - Remove `forgot` plugin block.
  - Add `tv` to the `autolock.load_on_startup.args.triggers` string.
  - Add `zellij_television_keybindings` block.
- `roles/dotfiles/templates/zellij/config.kdl.j2`:
  - Emit a `shared_except "locked" { ... }` block that loops `zellij_television_keybindings`.
- The dotfiles entrypoint task list — import `tasks/television.yml` (mirroring how `tasks/zellij.yml` is imported today).

The pattern intentionally mirrors `tasks/zellij.yml` + `tasks/zellij_plugins.yml` — no new role, no new playbook entry.

### Channel TOML output (illustrative)

The rendered cable file for layouts looks like:

```toml
[metadata]
name = "zellij-layouts"
description = "Pick a Zellij layout — Enter for new tab, Ctrl+s for new session"

[source]
command = "printf '%s\n' homelab dev1 example"

[preview]
command = "echo 'Layout: {}'"

[ui]
preview_panel = { size = 30 }

[[keybindings]]
shortcut = "enter"
description = "New tab in current session"
action = """
if [ -n "$ZELLIJ" ]; then
  zellij action new-tab --layout={}
else
  zellij --layout={}
fi
"""

[[keybindings]]
shortcut = "ctrl-s"
description = "New session with this layout"
action = "zellij --layout={}"
```

Substitutions are TV's literal `{}` placeholder; the `printf` source lists are produced by Jinja from the relevant Ansible var.

### Removal: `forgot` plugin

- `forgot` entry deleted from `zellij_plugins`.
- `Ctrl k` is now the master TV picker.
- An Ansible task removes `zellij_forgot.wasm` from `zellij_plugin_dir` (idempotent `file: state=absent`).
- The `zellij-plugins` TV channel takes over the discoverability role: it lists every plugin with a `launch_keybinding`, with the keybinding shown in the entry text and Enter firing `launch-or-focus-plugin`. The `forgot` plugin's actual function (showing zellij's built-in keybindings) is not replicated; that's tracked separately if it turns out to be missed.

### Edge cases

- **Outside Zellij:** Channels work; actions branch on `$ZELLIJ` as described above.
- **No sessions running:** `zellij-sessions` source returns empty → TV shows empty state. No special handling.
- **Lock mode active:** TV launch keybindings live under `shared_except "locked"`, so pressing Ctrl+k while already locked is inert — no nested launches, no fight with TV.
- **Autolock latency:** With `reaction_seconds: 1.0`, there is up to a one-second window after TV exits where Zellij is still locked. This matches the existing nvim/yazi/lazygit experience and is acceptable.
- **Re-launching a picker over a running picker:** Cannot happen (autolock has Zellij locked while TV is running).
- **Multiple TV instances:** If the user runs `tv` outside the picker keybindings (e.g., from a shell), autolock will lock Zellij for that too. This is existing autolock behavior, not new — flagged for awareness.
- **Pre-existing user config at `~/.config/television/`:** The deploy overwrites `config.toml` and `cable/zellij-*.toml`. Other cable files (non-`zellij-*`) are untouched. Documented in non-goals.

## Testing

- `ansible-playbook playbook.yml --check --diff --tags dotfiles` — verify expected changes (no surprise deletions).
- Apply, then in Zellij:
  - Press **Ctrl k** → floating pane opens with TV remote control listing channels including `zellij-*`. Pick `zellij-layouts` → pick a project → new tab opens; pane closes.
  - Press **Alt l** → floating pane opens directly to `zellij-layouts`. Same selection flow.
  - Press **Alt a** → floating pane opens to `zellij-ai-agents`. Pick `claude` → floating pane opens running `claude`.
  - Verify autolock: while TV is open, press Ctrl+k — should be inert (locked); press Ctrl+t inside TV — should switch channels (TV consumes it).
- Outside Zellij: `tv zellij-layouts` → pick a layout → new zellij session starts.
- Verify `~/.zellij-plugins/zellij_forgot.wasm` is absent after deploy.
- `ansible-lint` clean.

## Open implementation details (resolved during plan, not design)

These are decisions for the writing-plans step, not unresolved spec questions:

- Exact name of the dotfiles task-list entrypoint that imports `tasks/television.yml` (depends on current import structure in the dotfiles role).
- Whether `_channel.toml.j2` parameterizes shortcut→action mapping via a list of dicts or a flat dict (Jinja syntax detail).
- Concrete `zellij-actions` catalog contents (the curated list of common zellij actions) — initial set: NewPane, NewPane (Right), NewPane (Down), NewTab, ToggleFullscreen, ToggleSync, ToggleFloating, MoveTab Left, MoveTab Right, RenameSession, RenameTab, CloseTab, CloseFocus. Refinable later.
- Whether `zellij-panes` uses `query-tab-names` (which lists tabs, not panes) or a richer `dump-screen`-derived list. Defaulting to tab-name go-to in v1; pane-level navigation deferred unless `query-tab-names` proves insufficient.
- Exact TV CLI flag for the channel-picker / remote-control launch (the spec uses `tv --select-channel` illustratively; the implementer will confirm the flag name against the installed TV version and adjust the master keybinding accordingly).
