# Zellij Plugins (autolock + worktree) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `zellij-worktree` (Ctrl a) and `zellij-autolock` plugins to the `dotfiles` role, and migrate `forgot`/`room`/`harpoon` from raw-KDL keybindings to a structured schema in the same change.

**Architecture:** Extend `zellij_plugins` entries with two optional structured fields — `launch_keybinding` (for on-demand plugins) and `load_on_startup` (for background plugins). Replace the raw-KDL `keybindings.shared_except_locked` field. The Jinja2 template (`config.kdl.j2`) renders each field through a generic loop that emits KDL child nodes as `"<key>" <value|to_json>`.

**Tech Stack:** Ansible (dotfiles role), Jinja2 templates, KDL config format, zellij terminal multiplexer.

**Reference spec:** `docs/superpowers/specs/2026-04-23-zellij-plugins-autolock-worktree-design.md`

---

## File Structure

**Modified files (two, changed atomically):**

- `roles/dotfiles/defaults/main/zellij.yml` — update `zellij_plugins` dict: migrate three entries, add two new entries. Remove `keybindings.shared_except_locked` field everywhere it appears.
- `roles/dotfiles/templates/zellij/config.kdl.j2` — replace the keybindings loop inside `keybinds { shared_except "locked" { … } }`, and replace the empty `load_plugins { }` block with a populated loop.

**Unchanged:**

- `roles/dotfiles/tasks/zellij.yml` — no changes (template copy is generic).
- `roles/dotfiles/tasks/zellij_plugins.yml` — no changes (download loop is generic over `zellij_plugins | dict2items`).

---

## Task 1: Capture baseline rendered config.kdl

**Purpose:** Before changing anything, render the current template so we have a reference point to compare the new output against. This is our "test baseline."

**Files:**
- Read: `~/.config/zellij/config.kdl` (the installed rendered config) — if the role has been applied before.
- Alternative: run the role once to write a fresh baseline.

- [ ] **Step 1: Locate the current rendered config**

Run: `ls -la "${XDG_CONFIG_HOME:-$HOME/.config}/zellij/config.kdl"`

Expected: file exists and has non-zero size. If it does not exist (role not yet applied), skip to Step 2.

- [ ] **Step 2: Render current state by running the zellij role once**

Run: `just zellij`

Expected: playbook runs to completion, `config.kdl` is written to `$XDG_CONFIG_HOME/zellij/config.kdl`. Changes may be zero if role already up to date.

- [ ] **Step 3: Save baseline for diffing**

Run:

```bash
cp "${XDG_CONFIG_HOME:-$HOME/.config}/zellij/config.kdl" /tmp/zellij-config.kdl.baseline
```

Expected: file copied with no error.

- [ ] **Step 4: Inspect baseline's keybinds and load_plugins sections**

Run:

```bash
sed -n '/^keybinds {/,/^}/p' /tmp/zellij-config.kdl.baseline
sed -n '/^load_plugins {/,/^}/p' /tmp/zellij-config.kdl.baseline
```

Expected output (roughly):

```
keybinds {
    shared_except "locked" {
        bind "Ctrl k" {
            LaunchOrFocusPlugin "file:<plugin_dir>/zellij_forgot.wasm" {
                "LOAD_ZELLIJ_BINDINGS" "true"
                floating true
            }
        }
        bind "Ctrl y" {
           LaunchOrFocusPlugin "file:<plugin_dir>/room.wasm" {
                floating true
                ignore_case true
            }
        }
        bind "Ctrl z" {
            LaunchOrFocusPlugin "file:<plugin_dir>/harpoon.wasm" {
                floating true; move_to_focused_tab true;
            }
        }
    }
}
...
load_plugins {
}
```

Note the exact formatting — we'll compare against this after the change. Record the plugin_dir path shown.

---

## Task 2: Update defaults schema (migrate + add)

**Files:**
- Modify: `roles/dotfiles/defaults/main/zellij.yml:23-56` (the `zellij_plugins:` dict).

- [ ] **Step 1: Replace the entire `zellij_plugins:` block**

Open `roles/dotfiles/defaults/main/zellij.yml`. Replace lines 23–56 (the `zellij_plugins:` dict, from the line `zellij_plugins:` through the `zjstatus:` entry's URL line — stop before the commented-out `monocle` block starting at line 57).

**Before (lines 23–56):**

```yaml
zellij_plugins:
  mini_ci:
    url: "https://github.com/imsnif/multitask/releases/download/0.38.2v2/multitask.wasm"
  forgot:
    url: "https://github.com/karimould/zellij-forgot/releases/download/0.3.0/zellij_forgot.wasm"
    keybindings:
      shared_except_locked: |
        bind "Ctrl k" {
            LaunchOrFocusPlugin "file:{{ zellij_plugin_dir }}/zellij_forgot.wasm" {
                "LOAD_ZELLIJ_BINDINGS" "true"
                floating true
            }
        }
  room:
    url: "https://github.com/rvcas/room/releases/latest/download/room.wasm"
    keybindings:
      shared_except_locked: |
        bind "Ctrl y" {
           LaunchOrFocusPlugin "file:{{ zellij_plugin_dir }}/room.wasm" {
                floating true
                ignore_case true
            }
        }
  harpoon:
    url: "https://github.com/Nacho114/harpoon/releases/download/v0.1.0/harpoon.wasm"
    keybindings:
      shared_except_locked: |
        bind "Ctrl z" {
            LaunchOrFocusPlugin "file:{{ zellij_plugin_dir }}/harpoon.wasm" {
                floating true; move_to_focused_tab true;
            }
        }
  zjstatus:
    url: "https://github.com/dj95/zjstatus/releases/download/v0.13.1/zjstatus.wasm"
```

**After:**

```yaml
zellij_plugins:
  mini_ci:
    url: "https://github.com/imsnif/multitask/releases/download/0.38.2v2/multitask.wasm"
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
  zjstatus:
    url: "https://github.com/dj95/zjstatus/releases/download/v0.13.1/zjstatus.wasm"
```

Do NOT touch the commented-out `monocle` block that follows. Leave it verbatim.

- [ ] **Step 2: Verify YAML syntax**

Run: `python3 -c "import yaml; yaml.safe_load(open('roles/dotfiles/defaults/main/zellij.yml'))" && echo OK`

Expected: `OK`. If a `yaml.YAMLError` is raised, fix the indentation/syntax and re-run.

- [ ] **Step 3: Verify the schema round-trips the expected keys**

Run:

```bash
python3 -c "
import yaml
d = yaml.safe_load(open('roles/dotfiles/defaults/main/zellij.yml'))
plugins = d['zellij_plugins']
assert set(plugins.keys()) == {'mini_ci','forgot','room','harpoon','worktree','autolock','zjstatus'}, plugins.keys()
assert plugins['forgot']['launch_keybinding']['key'] == 'Ctrl k'
assert plugins['autolock']['load_on_startup']['args']['reaction_seconds'] == '0.3'
assert plugins['worktree']['launch_keybinding']['args']['floating'] is True
assert 'keybindings' not in plugins['forgot']
print('OK')
"
```

Expected: `OK`. If any assertion fails, fix the defaults file.

Do NOT commit yet — the template still references the removed `keybindings.shared_except_locked` field, so the tree is in a broken intermediate state until Task 3 is done.

---

## Task 3: Update the Jinja2 template

**Files:**
- Modify: `roles/dotfiles/templates/zellij/config.kdl.j2:1-8` (the `keybinds { }` block).
- Modify: `roles/dotfiles/templates/zellij/config.kdl.j2:60-61` (the empty `load_plugins { }` block).

- [ ] **Step 1: Replace the `keybinds { }` block**

In `roles/dotfiles/templates/zellij/config.kdl.j2`, replace lines 1–8:

**Before:**

```jinja
// Default Keybinding Preset + Plugin Section
keybinds {
    shared_except "locked" {
        {% for zellij_plugin in zellij_plugins -%}
        {{ zellij_plugins[zellij_plugin]['keybindings']['shared_except_locked']  | default('') }}
        {% endfor %}
    }
}
```

**After:**

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
    }
}
```

- [ ] **Step 2: Replace the empty `load_plugins { }` block**

Find the block at lines 60–61:

**Before:**

```jinja
load_plugins {
}
```

**After:**

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

Do NOT touch any other part of `config.kdl.j2` (themes, plugin aliases, options, env block).

- [ ] **Step 3: Verify the template renders without Jinja2 errors**

Run the playbook in check mode (does not write files, but catches template errors):

```bash
ANSIBLE_STDOUT_CALLBACK=debug ansible-playbook -i inventory ars.yml --tags zellij --skip-tags install --check --diff
```

Expected: the task `Zellij | Copies Zellij Config(KDL) | template` runs and reports a diff (or no change). No Jinja2 syntax errors. If you see `UndefinedError` or `TemplateSyntaxError`, review Steps 1–2 for typos.

---

## Task 4: Render config.kdl and validate output

**Files:**
- Read: `~/.config/zellij/config.kdl` (rendered output).
- Compare: `/tmp/zellij-config.kdl.baseline`.

- [ ] **Step 1: Actually render the config (no --check)**

Run: `just zellij`

Expected: playbook runs, downloads `zellij-worktree.wasm` and `zellij-autolock.wasm` via `get_url`, renders `config.kdl`. "changed" status on the template task and the plugin download task.

- [ ] **Step 2: Inspect the rendered `keybinds` block**

Run:

```bash
sed -n '/^keybinds {/,/^}/p' "${XDG_CONFIG_HOME:-$HOME/.config}/zellij/config.kdl"
```

Expected output (ignoring whitespace variations from Jinja2 line stripping):

```
keybinds {
    shared_except "locked" {
        bind "Ctrl k" {
            LaunchOrFocusPlugin "file:<plugin_dir>/zellij_forgot.wasm" {
                "LOAD_ZELLIJ_BINDINGS" "true"
                "floating" true
            }
        }
        bind "Ctrl y" {
            LaunchOrFocusPlugin "file:<plugin_dir>/room.wasm" {
                "floating" true
                "ignore_case" true
            }
        }
        bind "Ctrl z" {
            LaunchOrFocusPlugin "file:<plugin_dir>/harpoon.wasm" {
                "floating" true
                "move_to_focused_tab" true
            }
        }
        bind "Ctrl a" {
            LaunchOrFocusPlugin "file:<plugin_dir>/zellij-worktree.wasm" {
                "floating" true
                "move_to_focused_tab" true
            }
        }
    }
}
```

Verify:
- Four `bind` entries present (Ctrl k, Ctrl y, Ctrl z, Ctrl a).
- `LOAD_ZELLIJ_BINDINGS` renders as `"LOAD_ZELLIJ_BINDINGS" "true"` (quoted key + quoted string value, because the YAML value is the string `"true"` not the bool `true`).
- Bool args render as `"<key>" true` (quoted key + bare bool).
- wasm filenames match the URL basenames (`zellij_forgot.wasm`, `room.wasm`, `harpoon.wasm`, `zellij-worktree.wasm`).

If anything is missing or malformed, revisit Task 2/3 and fix.

- [ ] **Step 3: Inspect the rendered `load_plugins` block**

Run:

```bash
sed -n '/^load_plugins {/,/^}/p' "${XDG_CONFIG_HOME:-$HOME/.config}/zellij/config.kdl"
```

Expected output:

```
load_plugins {
    "file:<plugin_dir>/zellij-autolock.wasm" {
        "triggers" "nvim|hx|fzf|yazi|btm|less|man|lazygit|atuin|zoxide"
        "reaction_seconds" "0.3"
    }
}
```

Verify:
- Exactly one entry (autolock).
- `triggers` value is the full pipe-separated string, quoted.
- `reaction_seconds` is quoted (`"0.3"`) because the YAML value is a string.

- [ ] **Step 4: Verify the wasm files were downloaded**

Run:

```bash
ls -la "$(ansible -i inventory localhost -m debug -a 'var=zellij_plugin_dir' 2>/dev/null | grep -oE '"[^"]+"' | tail -1 | tr -d '"')" 2>/dev/null || \
ls -la "$HOME"/.local/share/tools/.zellij-plugins/ 2>/dev/null || \
find "$HOME" -maxdepth 5 -name 'zellij-autolock.wasm' 2>/dev/null
```

Expected: `zellij-autolock.wasm` and `zellij-worktree.wasm` are present alongside the existing `zellij_forgot.wasm`, `room.wasm`, `harpoon.wasm`, `zjstatus.wasm`, `multitask.wasm`. If the paths don't resolve, check `tool_install_dir` in `group_vars/all.yml` or `host_vars/` to locate the actual `zellij_plugin_dir`.

- [ ] **Step 5: Diff against baseline to catch unintended changes elsewhere**

Run:

```bash
diff /tmp/zellij-config.kdl.baseline "${XDG_CONFIG_HOME:-$HOME/.config}/zellij/config.kdl" | head -120
```

Expected: the only diffs should be (a) inside the `keybinds` block — old raw-KDL replaced by the structured-loop output, (b) inside the `load_plugins` block — new autolock entry. No drift in themes, options, env, or plugin aliases.

If you see unrelated diffs, the template was touched by mistake — revert the extraneous change.

---

## Task 5: Commit the change

**Files:**
- Modified: `roles/dotfiles/defaults/main/zellij.yml`
- Modified: `roles/dotfiles/templates/zellij/config.kdl.j2`

- [ ] **Step 1: Stage only the two changed files**

Run:

```bash
git add roles/dotfiles/defaults/main/zellij.yml roles/dotfiles/templates/zellij/config.kdl.j2
git status
```

Expected: exactly two files staged. Do not add any untracked files (`.harness/`, `.pi/`, `.superpowers/`).

- [ ] **Step 2: Show the staged diff for a final eyeball**

Run: `git diff --cached`

Expected: the diff shows the schema migration + new entries in the defaults, and the two loop replacements in the template. No other changes.

- [ ] **Step 3: Commit**

Run:

```bash
git commit -m "$(cat <<'EOF'
[Zellij] Add autolock + worktree plugins, structured plugin schema

Replaces raw-KDL keybindings.shared_except_locked with structured
launch_keybinding / load_on_startup fields. Migrates forgot, room,
harpoon to the new schema and adds zellij-worktree (Ctrl a) and
zellij-autolock (background, triggers on nvim|hx|fzf|yazi|...).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected: commit succeeds on `main`. Capture the commit SHA.

---

## Task 6: Live smoke test

**Files:**
- Live zellij session.

- [ ] **Step 1: Start a fresh zellij session**

Outside any existing zellij session (detach first if attached), run: `zellij --session smoke-test-autolock-worktree`

Expected: new session attaches with no errors. The session should feel indistinguishable from normal.

- [ ] **Step 2: Test worktree keybinding**

Press `Ctrl a`.

Expected: a floating pane opens showing the `zellij-worktree` picker UI (list of git worktrees, or a "no worktrees" message if you're not inside a git repo with worktrees). Press `Esc` or `Ctrl a` again to dismiss.

If nothing happens: check that `zellij-worktree.wasm` is in `zellij_plugin_dir`, check `~/.config/zellij/config.kdl` shows the correct `bind "Ctrl a"` entry, and check zellij's log (`~/.cache/zellij/<session>/zellij-log/zellij.log`) for plugin load errors.

- [ ] **Step 3: Test autolock trigger**

In any pane, run: `nvim /tmp/autolock-test.txt`

Expected: within ~0.3s of nvim starting, the zellij mode indicator in the status bar changes to `locked` (or `LOCK`). All zellij keybindings (including Ctrl-anything in the `shared_except "locked"` block) are passed through to nvim.

Quit nvim (`:q`). Expected: mode returns to `normal` within ~0.3s.

If autolock doesn't trigger: check `load_plugins { }` in the rendered config, check that `zellij-autolock.wasm` is in `zellij_plugin_dir`, and check the zellij log for plugin load errors. Verify `reaction_seconds` is present.

- [ ] **Step 4: Regression check on existing keybindings**

Press `Ctrl k` → expect `zellij-forgot` floating pane.
Press `Ctrl y` → expect `room` floating pane (outside a yazelix layout).
Press `Ctrl z` → expect `harpoon` floating pane.

All three should launch their respective plugins as they did before the change.

- [ ] **Step 5: Detach and clean up the smoke-test session**

Run: `zellij kill-session smoke-test-autolock-worktree` (from outside the session).

Expected: session is gone.

---

## Rollback

If any of the above fails in a way that can't be fixed forward:

```bash
git revert <commit-sha-from-task-5>
just zellij
```

This restores the prior schema and template atomically. The two new wasm files will remain downloaded but unused.
