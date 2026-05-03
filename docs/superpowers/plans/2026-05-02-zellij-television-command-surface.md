# Zellij + Television Unified Command Surface — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire Television (`tv`) into Zellij as a fuzzy command surface so the user can launch zellij actions (layouts, AI agents, sessions, panes, plugins, common actions, git worktrees) by name from a floating picker — without memorizing CLI flags.

**Architecture:** Television cable channels are templated by Ansible from the same vars that already drive Zellij (`zellij_kdl_layouts`, `zellij_ai_agents`, `zellij_plugins`). Each channel's `actions` execute `zellij action ...` commands; the floating pane inherits `$ZELLIJ` so commands target the parent session. Three new Zellij keybindings (`Ctrl k`, `Alt l`, `Alt a`) launch `tv` with `floating true` + `close_on_exit true`. The autolock plugin's `triggers` list gains `tv` so Zellij auto-locks while TV is active. The existing `forgot` plugin is removed; the master picker (`tv --show-remote`) absorbs the channel-discovery role.

**Tech Stack:** Ansible (template, file modules), Jinja2 (TOML/KDL templates), Television 0.15.x cable schema (`[metadata]` + `[source]` + `[preview]` + `[keybindings]` + `[actions.NAME]`), Zellij KDL config (`Run` keybindings under `shared_except "locked"`).

**Spec:** `docs/superpowers/specs/2026-05-02-zellij-television-command-surface-design.md`

---

## File Structure

**New files:**

| Path | Responsibility |
|------|----------------|
| `roles/dotfiles/defaults/main/television.yml` | All TV vars: paths, theme, global TOML settings, `television_channels` dict (one entry per channel; rendered into a cable file). |
| `roles/dotfiles/tasks/television.yml` | Ensure dirs, deploy `config.toml`, loop `television_channels` and deploy each cable file, remove orphaned `zellij_forgot.wasm`. |
| `roles/dotfiles/templates/television/config.toml.j2` | Global TV config (UI, keybindings, shell integration). |
| `roles/dotfiles/templates/television/cable/_channel.toml.j2` | Single parameterized template rendered once per channel. |

**Modified files:**

| Path | Change |
|------|--------|
| `roles/dotfiles/defaults/main/zellij.yml` | Remove `forgot` plugin entry; add `tv` to autolock triggers; add `zellij_television_keybindings` block. |
| `roles/dotfiles/templates/zellij/config.kdl.j2` | Emit `Run`-style bindings for each entry in `zellij_television_keybindings` inside the existing `shared_except "locked"` block. |
| `roles/dotfiles/tasks/main.yml` | Add `Television Config` import after `Zellij Plugins` (~line 122). |

---

## Conventions used in this plan

- **"Verify"** for Ansible tasks means: `ansible-playbook playbook.yml --check --diff --tags <tag>` followed by inspection of the rendered file in the destination path. Idempotency check is a re-run with the expectation of zero changed tasks.
- All commits follow the existing style: `[Component] Imperative verb phrase.` (e.g., `[Television] Add cable channel scaffolding.`).
- The plan assumes execution on `main` (no PR per spec); commits land directly.
- Each task's first step is a short context refresher; the engineer may be reading tasks out of order.

---

### Task 1: Television role scaffolding (defaults + global config + task wiring)

**Files:**
- Create: `roles/dotfiles/defaults/main/television.yml`
- Create: `roles/dotfiles/tasks/television.yml`
- Create: `roles/dotfiles/templates/television/config.toml.j2`
- Modify: `roles/dotfiles/tasks/main.yml` (insert one block ~line 122)

- [ ] **Step 1: Create `roles/dotfiles/defaults/main/television.yml`**

```yaml
---
television_config_dir: "{{ xdg_config_dir }}/television"
television_cable_dir: "{{ television_config_dir }}/cable"

# Global config.toml settings — preserved from the user's prior config so
# behavior (history, prompt, keybindings, shell integration) is unchanged.
television_tick_rate: 50
television_default_channel: "files"
television_history_size: 200
television_global_history: false

television_ui_scale: 100
television_ui_orientation: "landscape"
television_theme: "default"

television_input_bar_position: "top"
television_input_bar_prompt: ">"
television_input_bar_border: "rounded"

television_results_panel_border: "rounded"
television_preview_panel_size: 50
television_preview_panel_border: "rounded"
television_help_panel_show_categories: true
television_help_panel_hidden: true
television_remote_show_descriptions: true
television_remote_sort_alphabetically: true

# Channels — populated in Tasks 2-4.
television_channels: {}
```

- [ ] **Step 2: Create `roles/dotfiles/templates/television/config.toml.j2`**

Render only the keys the role owns; do not attempt to reproduce TV's verbose comment-doc. The rendered file is the canonical config from now on.

```jinja
# Managed by Ansible: roles/dotfiles/templates/television/config.toml.j2
# Edit roles/dotfiles/defaults/main/television.yml and re-run the role.

tick_rate = {{ television_tick_rate }}
default_channel = "{{ television_default_channel }}"
history_size = {{ television_history_size }}
global_history = {{ television_global_history | string | lower }}

[ui]
ui_scale = {{ television_ui_scale }}
orientation = "{{ television_ui_orientation }}"
theme = "{{ television_theme }}"

[ui.input_bar]
position = "{{ television_input_bar_position }}"
prompt = "{{ television_input_bar_prompt }}"
border_type = "{{ television_input_bar_border }}"

[ui.status_bar]
separator_open = ""
separator_close = ""
hidden = false

[ui.results_panel]
border_type = "{{ television_results_panel_border }}"

[ui.preview_panel]
size = {{ television_preview_panel_size }}
scrollbar = true
border_type = "{{ television_preview_panel_border }}"
hidden = false

[ui.help_panel]
show_categories = {{ television_help_panel_show_categories | string | lower }}
hidden = {{ television_help_panel_hidden | string | lower }}

[ui.remote_control]
show_channel_descriptions = {{ television_remote_show_descriptions | string | lower }}
sort_alphabetically = {{ television_remote_sort_alphabetically | string | lower }}

[keybindings]
esc = "quit"
ctrl-c = "quit"
down = "select_next_entry"
ctrl-n = "select_next_entry"
ctrl-j = "select_next_entry"
up = "select_prev_entry"
ctrl-p = "select_prev_entry"
ctrl-up = "select_prev_history"
ctrl-down = "select_next_history"
tab = "toggle_selection_down"
backtab = "toggle_selection_up"
enter = "confirm_selection"
pagedown = "scroll_preview_half_page_down"
pageup = "scroll_preview_half_page_up"
ctrl-f = "cycle_previews"
ctrl-y = "copy_entry_to_clipboard"
ctrl-r = "reload_source"
ctrl-s = "cycle_sources"
ctrl-t = "toggle_remote_control"
ctrl-x = "toggle_action_picker"
ctrl-o = "toggle_preview"
ctrl-h = "toggle_help"
f12 = "toggle_status_bar"
ctrl-l = "toggle_layout"
backspace = "delete_prev_char"
ctrl-w = "delete_prev_word"
ctrl-u = "delete_line"
delete = "delete_next_char"
left = "go_to_prev_char"
right = "go_to_next_char"
home = "go_to_input_start"
ctrl-a = "go_to_input_start"
end = "go_to_input_end"
ctrl-e = "go_to_input_end"

[shell_integration]
fallback_channel = "files"

[shell_integration.channel_triggers]
"alias" = ["alias", "unalias"]
"env" = ["export", "unset"]
"dirs" = ["cd", "ls", "rmdir", "z"]
"files" = ["cat", "less", "head", "tail", "vim", "nano", "bat", "cp", "mv", "rm", "touch", "chmod", "chown", "ln", "tar", "zip", "unzip", "gzip", "gunzip", "xz"]
"git-diff" = ["git add", "git restore"]
"git-branch" = ["git checkout", "git branch", "git merge", "git rebase", "git pull", "git push"]
"git-log" = ["git log", "git show"]
"docker-images" = ["docker run"]
"git-repos" = ["nvim", "code", "hx", "git clone"]

[shell_integration.keybindings]
"smart_autocomplete" = "ctrl-t"
"command_history" = "ctrl-r"
```

> **Note** — `ctrl-k` is intentionally NOT bound to `select_prev_entry` here even though TV's stock config includes it. Reason: leaving Ctrl+k unbound inside TV preserves it for the engineer's terminal-level expectations and avoids surprise. `ctrl-p` already covers prev-entry. (If a future need arises, add `ctrl-k = "select_prev_entry"` back.)

- [ ] **Step 3: Create `roles/dotfiles/tasks/television.yml`**

```yaml
---
- name: Television | Setup Television Config Directory | file
  file:
    path: "{{ television_config_dir }}"
    state: directory
    mode: '0755'

- name: Television | Setup Television Cable Directory | file
  file:
    path: "{{ television_cable_dir }}"
    state: directory
    mode: '0755'

- name: Television | Deploy Global Config | template
  template:
    src: television/config.toml.j2
    dest: "{{ television_config_dir }}/config.toml"
    mode: '0644'
```

- [ ] **Step 4: Wire `tasks/television.yml` into `tasks/main.yml`**

Open `roles/dotfiles/tasks/main.yml`. Find the `Zellij Plugins` block (currently lines 118-122):

```yaml
- name: Zellij Plugins
  import_tasks: tasks/zellij_plugins.yml
  tags:
    - zellij
    - session
```

Insert the new block immediately after it:

```yaml
- name: Television Config
  import_tasks: tasks/television.yml
  tags:
    - television
    - session
```

- [ ] **Step 5: Render with `--check --diff` and inspect**

```bash
ansible-playbook playbook.yml --check --diff --tags television
```

Expected: shows `~/.config/television/config.toml` would be modified (because the templated content differs from the user's existing 254-line stock config). Directory creates are idempotent no-ops.

- [ ] **Step 6: Apply and verify the rendered config.toml**

```bash
ansible-playbook playbook.yml --tags television
cat ~/.config/television/config.toml | head -20
tv list-channels
```

Expected: file starts with `# Managed by Ansible:` header. `tv list-channels` still works (existing builtin channels remain in `~/.config/television/cable/`).

- [ ] **Step 7: Idempotency check**

```bash
ansible-playbook playbook.yml --tags television
```

Expected: `changed=0` for the television tasks.

- [ ] **Step 8: Commit**

```bash
git add roles/dotfiles/defaults/main/television.yml \
        roles/dotfiles/templates/television/config.toml.j2 \
        roles/dotfiles/tasks/television.yml \
        roles/dotfiles/tasks/main.yml
git commit -m "[Television] Add role scaffolding and global config template."
```

---

### Task 2: Cable channel template + first templated channel (`zellij-layouts`)

**Files:**
- Create: `roles/dotfiles/templates/television/cable/_channel.toml.j2`
- Modify: `roles/dotfiles/defaults/main/television.yml` (add the layouts entry to `television_channels`)
- Modify: `roles/dotfiles/tasks/television.yml` (add the deployment loop)

- [ ] **Step 1: Create `_channel.toml.j2`**

This template is rendered once per entry in `television_channels`. The rendering loop will set `tv_channel_name` and `tv_channel` (the inner dict) before include. Schema mirrors the inspected `git-branch.toml`.

```jinja
# Managed by Ansible: roles/dotfiles/templates/television/cable/_channel.toml.j2
# Edit roles/dotfiles/defaults/main/television.yml -> television_channels[{{ tv_channel_name }}]

[metadata]
name = "{{ tv_channel_name }}"
description = "{{ tv_channel.description }}"
{% if tv_channel.requirements is defined %}
requirements = {{ tv_channel.requirements | to_json }}
{% endif %}

[source]
command = {{ tv_channel.source.command | to_json }}
{% if tv_channel.source.output is defined %}
output = {{ tv_channel.source.output | to_json }}
{% endif %}
{% if tv_channel.source.entry_delimiter is defined %}
entry_delimiter = {{ tv_channel.source.entry_delimiter | to_json }}
{% endif %}

{% if tv_channel.preview is defined %}
[preview]
command = {{ tv_channel.preview.command | to_json }}
{% endif %}

[keybindings]
{% for shortcut, action_name in tv_channel.keybindings.items() %}
{{ shortcut }} = "actions:{{ action_name }}"
{% endfor %}

{% for action_name, action in tv_channel.actions.items() %}
[actions.{{ action_name }}]
description = {{ action.description | to_json }}
command = {{ action.command | to_json }}
mode = "{{ action.mode | default('execute') }}"

{% endfor %}
```

- [ ] **Step 2: Add `zellij-layouts` to `television_channels`**

Replace the `television_channels: {}` line in `roles/dotfiles/defaults/main/television.yml` with:

```yaml
television_channels:
  zellij-layouts:
    description: "Pick a Zellij layout — Enter for new tab, Alt+s for new session"
    source:
      # Each layout key on its own line. Generated from zellij_kdl_layouts at template time.
      command: >-
        printf '%s\n' {{ (zellij_kdl_layouts | default({})).keys() | map('quote') | join(' ') }}
    preview:
      command: "echo 'Layout: {0}'"
    keybindings:
      enter: "new_tab_or_session"
      alt-s: "new_session"
    actions:
      new_tab_or_session:
        description: "New tab in current zellij session (or new session if outside zellij)"
        command: |
          if [ -n "$ZELLIJ" ]; then
            zellij action new-tab --layout '{0}'
          else
            zellij --layout '{0}'
          fi
        mode: "execute"
      new_session:
        description: "Start a new zellij session with this layout"
        command: "zellij --layout '{0}'"
        mode: "execute"
```

- [ ] **Step 3: Add the cable deployment loop to `tasks/television.yml`**

Append after the existing `Deploy Global Config` task:

```yaml
- name: Television | Deploy Cable Channels | template
  vars:
    tv_channel_name: "{{ item.key }}"
    tv_channel: "{{ item.value }}"
  template:
    src: television/cable/_channel.toml.j2
    dest: "{{ television_cable_dir }}/{{ item.key }}.toml"
    mode: '0644'
  loop: "{{ television_channels | dict2items }}"
  loop_control:
    label: "{{ item.key }}"
```

- [ ] **Step 4: Render with `--check --diff`**

```bash
ansible-playbook playbook.yml --check --diff --tags television
```

Expected: shows `~/.config/television/cable/zellij-layouts.toml` would be created. No other cable files affected.

- [ ] **Step 5: Apply and inspect the rendered cable file**

```bash
ansible-playbook playbook.yml --tags television
cat ~/.config/television/cable/zellij-layouts.toml
```

Expected output (assuming `zellij_kdl_layouts` resolves to keys `homelab`, `dev1`, `example` based on current `group_vars`):

```toml
[metadata]
name = "zellij-layouts"
description = "Pick a Zellij layout — Enter for new tab, Alt+s for new session"

[source]
command = "printf '%s\\n' 'homelab' 'dev1' 'example'"

[preview]
command = "echo 'Layout: {0}'"

[keybindings]
enter = "actions:new_tab_or_session"
alt-s = "actions:new_session"

[actions.new_tab_or_session]
description = "New tab in current zellij session (or new session if outside zellij)"
command = "if [ -n \"$ZELLIJ\" ]; then\n  zellij action new-tab --layout '{0}'\nelse\n  zellij --layout '{0}'\nfi\n"
mode = "execute"

[actions.new_session]
description = "Start a new zellij session with this layout"
command = "zellij --layout '{0}'"
mode = "execute"
```

- [ ] **Step 6: Smoke-test the channel from the shell**

```bash
tv list-channels | grep zellij-layouts
tv zellij-layouts --no-preview --input '' --hide-status-bar 2>&1 | head -3 || true
```

Expected: first command shows `zellij-layouts`. Second command may not be straightforwardly inspectable from a non-interactive shell; the real test is interactive in Task 8.

A cheaper non-interactive sanity check:

```bash
# Run the source command from the channel and confirm it lists keys
sh -c "$(grep '^command' ~/.config/television/cable/zellij-layouts.toml | head -1 | sed 's/^command = //; s/^"//; s/"$//; s/\\\\n/\\n/g')"
```

Expected: prints each layout key on its own line.

- [ ] **Step 7: Idempotency check**

```bash
ansible-playbook playbook.yml --tags television
```

Expected: `changed=0`.

- [ ] **Step 8: Commit**

```bash
git add roles/dotfiles/templates/television/cable/_channel.toml.j2 \
        roles/dotfiles/defaults/main/television.yml \
        roles/dotfiles/tasks/television.yml
git commit -m "[Television] Add zellij-layouts cable channel and channel template."
```

---

### Task 3: Static channels — `zellij-ai-agents`, `zellij-plugins`, `zellij-actions`

**Files:**
- Modify: `roles/dotfiles/defaults/main/television.yml` (extend `television_channels`)

The deployment loop from Task 2 picks up new entries automatically; no task-list changes.

- [ ] **Step 1: Add `zellij_actions_catalog` var**

This new var declares the curated catalog used by the `zellij-actions` channel. Insert near the top of `roles/dotfiles/defaults/main/television.yml`, above `television_channels`:

```yaml
# Curated catalog for the zellij-actions cable channel. Each entry maps a
# human-readable label to the `zellij action` subcommand that runs.
zellij_actions_catalog:
  "New Pane": "new-pane"
  "New Pane (Right)": "new-pane --direction right"
  "New Pane (Down)": "new-pane --direction down"
  "New Floating Pane": "new-pane --floating"
  "New Tab": "new-tab"
  "Toggle Fullscreen": "toggle-fullscreen"
  "Toggle Floating": "toggle-floating-panes"
  "Toggle Sync": "toggle-pane-sync-tab"
  "Move Tab Left": "move-tab left"
  "Move Tab Right": "move-tab right"
  "Rename Session": "rename-session"
  "Rename Tab": "rename-tab"
  "Close Pane": "close-pane"
  "Close Tab": "close-tab"
```

- [ ] **Step 2: Extend `television_channels` with three more entries**

Append to the existing `television_channels` mapping in `roles/dotfiles/defaults/main/television.yml`:

```yaml
  zellij-ai-agents:
    description: "Launch an AI agent — Enter floats, Alt+t opens in new tab"
    source:
      command: >-
        printf '%s\n' {{ (zellij_ai_agents | default({})).keys() | map('quote') | join(' ') }}
    preview:
      command: >-
        printf 'Agent: %s\nCommand: %s\n' '{0}' "$(echo '{ {%- for k, v in (zellij_ai_agents | default({})).items() %}\"{{ k }}\":\"{{ v.command }}\"{% if not loop.last %},{% endif %}{%- endfor %} }' | jq -r '.[\"{0}\"]')"
    keybindings:
      enter: "open_floating"
      alt-t: "open_in_tab"
    actions:
      open_floating:
        description: "Open AI agent in a floating pane"
        command: |
          {%- set agents = zellij_ai_agents | default({}) %}
          case '{0}' in
          {%- for k, v in agents.items() %}
            {{ k }}) zellij action new-pane --floating --name "{{ v.pane_name }}" -- {{ v.command }} ;;
          {%- endfor %}
          esac
        mode: "execute"
      open_in_tab:
        description: "Open AI agent in a new tab"
        command: |
          {%- set agents = zellij_ai_agents | default({}) %}
          case '{0}' in
          {%- for k, v in agents.items() %}
            {{ k }}) zellij action new-tab --name "{{ v.pane_name }}" -- {{ v.command }} ;;
          {%- endfor %}
          esac
        mode: "execute"

  zellij-plugins:
    description: "Launch a Zellij plugin — Enter focuses or launches the plugin"
    source:
      # Only plugins with a launch_keybinding are listed; load_on_startup-only
      # plugins (autolock, zjstatus) are background-only and not user-launchable.
      command: >-
        printf '%s\n' {{
          (zellij_plugins | default({}))
          | dict2items
          | selectattr('value.launch_keybinding', 'defined')
          | map(attribute='key')
          | map('quote')
          | join(' ')
        }}
    preview:
      command: >-
        printf 'Plugin: %s\nKey: %s\n' '{0}' "$(echo '{ {%- for k, v in (zellij_plugins | default({})).items() if v.launch_keybinding is defined %}\"{{ k }}\":\"{{ v.launch_keybinding.key }}\"{% if not loop.last %},{% endif %}{%- endfor %} }' | jq -r '.[\"{0}\"]')"
    keybindings:
      enter: "launch_plugin"
    actions:
      launch_plugin:
        description: "LaunchOrFocus the selected plugin"
        command: |
          {%- set plugins = zellij_plugins | default({}) %}
          case '{0}' in
          {%- for k, v in plugins.items() if v.launch_keybinding is defined %}
            {{ k }}) zellij action launch-or-focus-plugin "file:{{ zellij_plugin_dir }}/{{ v.url | basename }}" ;;
          {%- endfor %}
          esac
        mode: "execute"

  zellij-actions:
    description: "Run a common Zellij action against the current session"
    source:
      command: >-
        printf '%s\n' {{ (zellij_actions_catalog | default({})).keys() | map('quote') | join(' ') }}
    keybindings:
      enter: "run_action"
    actions:
      run_action:
        description: "Run the selected zellij action"
        command: |
          {%- set catalog = zellij_actions_catalog | default({}) %}
          case '{0}' in
          {%- for label, sub in catalog.items() %}
            {{ label | to_json }}) zellij action {{ sub }} ;;
          {%- endfor %}
          esac
        mode: "execute"
```

> **Why `case ... esac` blocks instead of pure substitution:** TV's `{0}` substitution drops the entry's text into the command at runtime. We need the *associated value* (e.g., agent's `command`, plugin's `url`, action's `zellij action` subcommand). Resolving it via a Jinja-rendered `case` statement at template time is the simplest mechanism that doesn't require a wrapper script. The rendered command sees the entry as the literal text and dispatches.

- [ ] **Step 3: Render with `--check --diff`**

```bash
ansible-playbook playbook.yml --check --diff --tags television
```

Expected: three new cable files would be created (`zellij-ai-agents.toml`, `zellij-plugins.toml`, `zellij-actions.toml`). The existing `zellij-layouts.toml` shows `ok` (unchanged).

- [ ] **Step 4: Apply and inspect each cable file**

```bash
ansible-playbook playbook.yml --tags television
ls ~/.config/television/cable/zellij-*.toml
cat ~/.config/television/cable/zellij-ai-agents.toml
cat ~/.config/television/cable/zellij-plugins.toml
cat ~/.config/television/cable/zellij-actions.toml
```

Expected:
- `zellij-ai-agents.toml` `[actions.open_floating]` contains a `case` block listing `claude`, `codex`, `opencode`, `pi` with their respective commands and pane names from `zellij_ai_agents`.
- `zellij-plugins.toml` `[actions.launch_plugin]` lists every plugin in `zellij_plugins` that has a `launch_keybinding` defined (so: `forgot`, `room`, `harpoon`, `worktree` at this point — `forgot` will be removed in Task 7) with absolute file:// paths.
- `zellij-actions.toml` `[source]` lists every label from `zellij_actions_catalog`.

- [ ] **Step 5: Verify channel listings**

```bash
tv list-channels | grep ^zellij-
```

Expected: four lines — `zellij-actions`, `zellij-ai-agents`, `zellij-layouts`, `zellij-plugins`.

- [ ] **Step 6: Idempotency check**

```bash
ansible-playbook playbook.yml --tags television
```

Expected: `changed=0`.

- [ ] **Step 7: Commit**

```bash
git add roles/dotfiles/defaults/main/television.yml
git commit -m "[Television] Add zellij-ai-agents, zellij-plugins, zellij-actions channels."
```

---

### Task 4: Dynamic channels — `zellij-sessions`, `zellij-panes`, `zellij-worktrees`

**Files:**
- Modify: `roles/dotfiles/defaults/main/television.yml` (extend `television_channels`)

- [ ] **Step 1: Append three dynamic channel entries to `television_channels`**

In `roles/dotfiles/defaults/main/television.yml`:

```yaml
  zellij-sessions:
    description: "Switch to a running Zellij session — Enter switches or attaches"
    requirements: ["zellij"]
    source:
      command: "zellij list-sessions -s"
    keybindings:
      enter: "switch_or_attach"
    actions:
      switch_or_attach:
        description: "Switch to the session (when inside zellij) or attach (when outside)"
        command: |
          if [ -n "$ZELLIJ" ]; then
            zellij action switch-session '{0}'
          else
            zellij attach '{0}'
          fi
        mode: "execute"

  zellij-panes:
    description: "Jump to a tab in the current Zellij session"
    requirements: ["zellij"]
    source:
      # query-tab-names emits one tab name per line.
      command: "zellij action query-tab-names"
    keybindings:
      enter: "go_to_tab"
    actions:
      go_to_tab:
        description: "Switch focus to the selected tab"
        command: "zellij action go-to-tab-name '{0}'"
        mode: "execute"

  zellij-worktrees:
    description: "Open a git worktree in a new Zellij tab"
    requirements: ["git", "zellij"]
    source:
      # Output absolute paths only (one per line).
      command: "git worktree list --porcelain | awk '/^worktree /{print $2}'"
    preview:
      command: "git -C '{0}' log --oneline -5 2>/dev/null"
    keybindings:
      enter: "open_in_tab"
    actions:
      open_in_tab:
        description: "Open a new tab with the worktree as cwd"
        command: |
          if [ -n "$ZELLIJ" ]; then
            zellij action new-tab --cwd '{0}'
          else
            (cd '{0}' && zellij)
          fi
        mode: "execute"
```

- [ ] **Step 2: Render with `--check --diff`**

```bash
ansible-playbook playbook.yml --check --diff --tags television
```

Expected: three new cable files created. Other files unchanged.

- [ ] **Step 3: Apply and inspect each cable file**

```bash
ansible-playbook playbook.yml --tags television
cat ~/.config/television/cable/zellij-sessions.toml
cat ~/.config/television/cable/zellij-panes.toml
cat ~/.config/television/cable/zellij-worktrees.toml
```

Expected: each file has `[source.command]` calling the live shell command (no Jinja `case` blocks here — these are runtime queries).

- [ ] **Step 4: Smoke-test the source commands**

```bash
zellij list-sessions -s 2>&1 | head -3
git worktree list --porcelain | awk '/^worktree /{print $2}' | head -3
```

Expected: sessions list (or empty if no sessions running). Worktree paths print one per line. The `query-tab-names` command must run from inside a zellij session — it'll fail outside, which is the channel's `requirements: ["zellij"]` justification.

- [ ] **Step 5: Verify channel listings**

```bash
tv list-channels | grep ^zellij-
```

Expected: seven lines — actions, ai-agents, layouts, panes, plugins, sessions, worktrees.

- [ ] **Step 6: Idempotency check**

```bash
ansible-playbook playbook.yml --tags television
```

Expected: `changed=0`.

- [ ] **Step 7: Commit**

```bash
git add roles/dotfiles/defaults/main/television.yml
git commit -m "[Television] Add zellij-sessions, zellij-panes, zellij-worktrees channels."
```

---

### Task 5: Zellij keybindings — three TV-launching `Run` bindings

**Files:**
- Modify: `roles/dotfiles/defaults/main/zellij.yml` (add `zellij_television_keybindings` block)
- Modify: `roles/dotfiles/templates/zellij/config.kdl.j2` (emit Run bindings)

- [ ] **Step 1: Add `zellij_television_keybindings` to defaults**

In `roles/dotfiles/defaults/main/zellij.yml`, insert this block after the `zellij_plugins:` mapping ends (currently ends near line 61, after the `zjstatus` entry — place it before the `# monocle:` commented block to keep semantically related vars adjacent):

```yaml
zellij_television_keybindings:
  master:
    key: "Ctrl k"
    args: ["--show-remote"]      # null-channel: launch remote-control browser
  layouts:
    key: "Alt l"
    args: ["zellij-layouts"]
  ai_agents:
    key: "Alt a"
    args: ["zellij-ai-agents"]
```

> **Why a list of args:** the KDL `Run "tv" "ARG1" "ARG2"` form takes positional strings; keeping `args` as a YAML list lets the template emit zero-or-more arg strings naturally.

- [ ] **Step 2: Modify `templates/zellij/config.kdl.j2` to emit Run bindings**

The current `shared_except "locked"` block (lines 3-13) only emits LaunchOrFocusPlugin bindings. Extend it to also emit Run bindings for `zellij_television_keybindings`. Replace lines 1-14:

```jinja
// Default Keybinding Preset + Plugin Section
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
        {% for name, kb in (zellij_television_keybindings | default({})).items() %}
        bind "{{ kb.key }}" {
            Run "tv"{% for arg in (kb.args | default([])) %} "{{ arg }}"{% endfor %} {
                floating true
                close_on_exit true
            }
            SwitchToMode "Normal"
        }
        {% endfor %}
    }
}
```

- [ ] **Step 3: Render with `--check --diff`**

```bash
ansible-playbook playbook.yml --check --diff --tags zellij
```

Expected: `~/.config/zellij/config.kdl` would be modified — diff shows three new `bind` blocks calling `Run "tv" ...` inside `shared_except "locked"`.

- [ ] **Step 4: Apply and inspect the rendered KDL**

```bash
ansible-playbook playbook.yml --tags zellij
sed -n '/shared_except "locked"/,/^    }/p' ~/.config/zellij/config.kdl
```

Expected (excerpt):

```kdl
    shared_except "locked" {
        bind "Ctrl k" {
            LaunchOrFocusPlugin "file:.../zellij_forgot.wasm" {
                ...
            }
        }
        ...   // other plugin bindings (room/harpoon/worktree)
        bind "Ctrl k" {
            Run "tv" "--show-remote" {
                floating true
                close_on_exit true
            }
            SwitchToMode "Normal"
        }
        bind "Alt l" {
            Run "tv" "zellij-layouts" {
                floating true
                close_on_exit true
            }
            SwitchToMode "Normal"
        }
        bind "Alt a" {
            Run "tv" "zellij-ai-agents" {
                floating true
                close_on_exit true
            }
            SwitchToMode "Normal"
        }
    }
```

> **Note** — at this point both `forgot`'s Ctrl+k binding AND the master TV Ctrl+k binding exist, which is a Zellij KDL conflict. This is intentional and **temporary** — Task 7 removes the `forgot` plugin, eliminating the duplicate. Don't restart zellij yet; see Task 8.

- [ ] **Step 5: Idempotency check**

```bash
ansible-playbook playbook.yml --tags zellij
```

Expected: `changed=0`.

- [ ] **Step 6: Commit**

```bash
git add roles/dotfiles/defaults/main/zellij.yml \
        roles/dotfiles/templates/zellij/config.kdl.j2
git commit -m "[Zellij] Add Run keybindings to launch Television floating picker."
```

---

### Task 6: Add `tv` to autolock triggers

**Files:**
- Modify: `roles/dotfiles/defaults/main/zellij.yml` (one-string change)

- [ ] **Step 1: Append `|tv` to the triggers string**

In `roles/dotfiles/defaults/main/zellij.yml`, find the autolock entry (currently around lines 54-59):

```yaml
  autolock:
    url: "https://github.com/fresh2dev/zellij-autolock/releases/latest/download/zellij-autolock.wasm"
    load_on_startup:
      args:
        triggers: "nvim|hx|fzf|yazi|btm|less|man|lazygit|atuin|zoxide"
        reaction_seconds: "1.0"
```

Change the `triggers` line to:

```yaml
        triggers: "nvim|hx|fzf|yazi|btm|less|man|lazygit|atuin|zoxide|tv"
```

- [ ] **Step 2: Render with `--check --diff`**

```bash
ansible-playbook playbook.yml --check --diff --tags zellij
```

Expected: `config.kdl` diff shows the `triggers` arg inside the `load_plugins` block updated to include `|tv`.

- [ ] **Step 3: Apply and verify the rendered KDL**

```bash
ansible-playbook playbook.yml --tags zellij
grep -A2 'autolock' ~/.config/zellij/config.kdl
```

Expected: shows `"triggers" "nvim|hx|fzf|yazi|btm|less|man|lazygit|atuin|zoxide|tv"`.

- [ ] **Step 4: Idempotency check**

```bash
ansible-playbook playbook.yml --tags zellij
```

Expected: `changed=0`.

- [ ] **Step 5: Commit**

```bash
git add roles/dotfiles/defaults/main/zellij.yml
git commit -m "[Zellij] Add tv to autolock triggers list."
```

---

### Task 7: Remove `forgot` plugin and clean up orphan wasm

**Files:**
- Modify: `roles/dotfiles/defaults/main/zellij.yml` (delete `forgot` entry)
- Modify: `roles/dotfiles/tasks/television.yml` (add cleanup task)

- [ ] **Step 1: Delete the `forgot` plugin entry**

In `roles/dotfiles/defaults/main/zellij.yml`, delete lines 26-32:

```yaml
  forgot:
    url: "https://github.com/karimould/zellij-forgot/releases/download/0.3.0/zellij_forgot.wasm"
    launch_keybinding:
      key: "Ctrl k"
      args:
        LOAD_ZELLIJ_BINDINGS: "true"
        floating: true
```

After this edit, the `zellij_plugins` mapping should start with `mini_ci:` and proceed directly to `room:`.

- [ ] **Step 2: Add cleanup task for orphan wasm**

Append to `roles/dotfiles/tasks/television.yml` (this task lives here rather than in `zellij_plugins.yml` to keep the forgot→TV migration self-contained):

```yaml
- name: Television | Remove orphaned forgot plugin wasm | file
  file:
    path: "{{ zellij_plugin_dir }}/zellij_forgot.wasm"
    state: absent
```

- [ ] **Step 3: Render with `--check --diff` for both tags**

```bash
ansible-playbook playbook.yml --check --diff --tags zellij
ansible-playbook playbook.yml --check --diff --tags television
```

Expected:
- zellij: `config.kdl` no longer emits a `bind "Ctrl k"` for forgot (only the TV master picker remains). The `zellij-plugins` cable also re-renders without the forgot entry (changed task is the cable, not the global config).
- television: shows `zellij_forgot.wasm` would be deleted.

- [ ] **Step 4: Apply both**

```bash
ansible-playbook playbook.yml --tags zellij,television
ls -la ~/.zellij-plugins/zellij_forgot.wasm 2>&1 || echo "absent (expected)"
grep -c '"Ctrl k"' ~/.config/zellij/config.kdl
```

Expected:
- The wasm file is `absent (expected)`.
- The `grep -c '"Ctrl k"'` count is exactly **1** (only the TV master picker; the forgot binding is gone).

- [ ] **Step 5: Confirm zellij-plugins channel no longer lists forgot**

```bash
grep -A1 '\[source\]' ~/.config/television/cable/zellij-plugins.toml
```

Expected: source command's printf list contains `room`, `harpoon`, `worktree` but NOT `forgot`.

- [ ] **Step 6: Idempotency check**

```bash
ansible-playbook playbook.yml --tags zellij,television
```

Expected: `changed=0`.

- [ ] **Step 7: Commit**

```bash
git add roles/dotfiles/defaults/main/zellij.yml \
        roles/dotfiles/tasks/television.yml
git commit -m "[Zellij] Remove forgot plugin; Television master picker absorbs its role."
```

---

### Task 8: End-to-end verification in a real Zellij session

This task is purely manual — no code changes. It is required because the previous tasks only verify file rendering and idempotency. The actual user-visible behavior (autolock locking on `tv`, keybindings firing, actions executing against the parent session) must be exercised interactively.

- [ ] **Step 1: Restart Zellij to pick up new config**

If a zellij session is currently attached, detach (Ctrl+o then Ctrl+d in default keybindings) and kill it:

```bash
zellij kill-all-sessions --yes
zellij delete-all-sessions --yes
```

Then start a fresh session:

```bash
zellij
```

Expected: a new session attaches with the updated config; autolock loads on startup.

- [ ] **Step 2: Verify master picker (Ctrl+k)**

In the zellij session, press `Ctrl+k`.

Expected: a floating pane opens running `tv --show-remote`. The remote-control panel shows the channel list including `zellij-actions`, `zellij-ai-agents`, `zellij-layouts`, `zellij-panes`, `zellij-plugins`, `zellij-sessions`, `zellij-worktrees`. While TV is open, the zellij status bar shows mode `LOCKED` (autolock fired on `tv`).

- [ ] **Step 3: Verify layouts picker (Alt+l)**

Press `Esc` to exit TV. Press `Alt+l`.

Expected: floating pane opens directly to `zellij-layouts`. Type a partial layout name; press `Enter`. The pane closes and a new tab is created in the current session running the selected layout.

- [ ] **Step 4: Verify AI agents picker (Alt+a)**

Press `Alt+a`. Type `claude` (or pick interactively); press `Enter`.

Expected: floating pane appears running `claude`. Press Esc/exit to dismiss; the pane closes.

- [ ] **Step 5: Verify alt-action — new session from layouts**

Press `Alt+l`. Pick a layout; press `Alt+s`.

Expected: a *new* zellij session starts with that layout (visible via `zellij list-sessions -s` from outside). May require detaching from current session first depending on TV/zellij interaction; alternatively, run from the master picker outside the session: in a non-zellij terminal, `tv zellij-layouts` → Alt+s on a layout → new session created.

- [ ] **Step 6: Verify sessions channel**

Detach from one session (`Ctrl+o`, `d`), open a new terminal, run `tv zellij-sessions`. Pick a session and press Enter.

Expected: the terminal attaches to the selected session.

- [ ] **Step 7: Verify autolock latency**

Inside zellij, press `Ctrl+k` to open TV. Inside TV, press `Ctrl+t`.

Expected: TV consumes Ctrl+t (toggles its remote-control panel); zellij does NOT intercept it (autolock has zellij locked).

- [ ] **Step 8: Verify forgot binding is gone**

Inside zellij, press `Ctrl+k` and confirm only TV opens (no forgot fallback).

```bash
ls ~/.zellij-plugins/zellij_forgot.wasm 2>&1
```

Expected: `No such file or directory`.

- [ ] **Step 9: ansible-lint clean**

```bash
ansible-lint roles/dotfiles/
```

Expected: no new errors introduced by these changes. (Pre-existing lint warnings are out of scope.)

- [ ] **Step 10: No commit needed**

This task is verification only.

---

## Self-Review Notes

**Spec coverage check:**

| Spec section | Implementing task(s) |
|--------------|----------------------|
| Component overview (floating pane mechanics) | Tasks 5, 8 |
| Channel taxonomy: zellij-layouts | Task 2 |
| Channel taxonomy: zellij-ai-agents | Task 3 |
| Channel taxonomy: zellij-actions | Task 3 |
| Channel taxonomy: zellij-plugins | Task 3 |
| Channel taxonomy: zellij-sessions | Task 4 |
| Channel taxonomy: zellij-panes | Task 4 |
| Channel taxonomy: zellij-worktrees | Task 4 |
| Master picker (`tv --show-remote`) | Task 5 |
| Alternate actions (alt-s for new session, alt-t for new tab) | Tasks 2, 3 |
| Out-of-Zellij behavior (`$ZELLIJ` branching) | Tasks 2, 4 (sessions/worktrees) |
| Zellij keybinding changes (Ctrl+k, Alt+l, Alt+a) | Task 5 |
| Autolock triggers update (`+tv`) | Task 6 |
| Ansible role structure (defaults, tasks, templates) | Task 1 (skeleton), Tasks 2-7 (content) |
| Channel TOML output (illustrative) | Task 2 (Step 5 verifies the rendered output) |
| Removal: forgot plugin + wasm cleanup | Task 7 |
| Edge cases (lock mode, no sessions, autolock latency) | Tasks 5, 8 |
| Testing (ansible-lint, --check, manual) | Tasks 1-7 (per-task verification), Task 8 (manual e2e) |

All spec requirements have a concrete task. The "open implementation details" listed in the spec (TV CLI flag, channel keybinding format) are resolved inline: `--show-remote` confirmed via `tv --help`; `[keybindings] + [actions.NAME]` confirmed via inspection of installed `git-branch.toml`.

**Type/name consistency check:** Channel names are `zellij-layouts`, `zellij-ai-agents`, `zellij-actions`, `zellij-plugins`, `zellij-sessions`, `zellij-panes`, `zellij-worktrees` consistently across tasks. Action names within each channel (`new_tab_or_session`, `new_session`, `open_floating`, `open_in_tab`, `launch_plugin`, `run_action`, `switch_or_attach`, `go_to_tab`) are referenced identically in `[keybindings]` mappings and `[actions.NAME]` blocks. Var names (`television_channels`, `television_cable_dir`, `zellij_television_keybindings`, `zellij_actions_catalog`) are consistent.

**Placeholder scan:** No TBD/TODO/"appropriate"/"similar to" placeholders — all code blocks contain literal content the engineer can paste.

**Scope check:** Single coherent feature, single role, ~7 implementation tasks plus one verification task. Fits one plan.
