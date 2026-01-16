Niri
====

Render a user-scoped niri configuration to `~/.config/niri/local.kdl` using a KDL template.

Requirements
------------

None.

Role Variables
--------------

- `niri_config_dir`: Target configuration directory. Default: `{{ ansible_env.HOME }}/.config/niri`.
- `niri_config_filename`: Target configuration filename. Default: `local.kdl`.
- `niri_local_kdl_content`: Raw KDL content to render. Default contains the provided layout override, named workspaces, and window rules.
- `niri_named_workspaces`: Map of named workspaces (lowercase, hyphen-friendly keys). Each entry may define `name` (label, defaults to key), optional `open_on_output`, and optional `layout` overrides.
- `niri_window_rules`: Map of window rules keyed by identifier. Each entry may define `workspace` (required), `app_id` regex string, `at_startup` (default: false), and optional `extra_match` tokens appended to `match`.

Example Playbook
----------------

```yaml
- hosts: all
  roles:
    - role: niri
      vars:
        # Optional: override per-workspace labels and settings.
        niri_named_workspaces:
          browse:
            name: "browse"
          obsidian:
            name: "obsidian"
            layout: |
              gaps 32
              border { on width 4 }

        # Optional: place apps onto workspaces at startup.
        niri_window_rules:
          brave:
            workspace: "browse"
            app_id: '^Brave-browser$'
            at_startup: true
          obsidian:
            workspace: "obsidian"
            app_id: '^obsidian$'
            at_startup: true

        # Optional: override the rendered content entirely.
        # niri_local_kdl_content: |
        #   {{ niri_global_layout_options }}
        #   workspace "custom" {
        #     open-on-output "DP-2"
        #   }
        #   window-rule {
        #     match at-startup=true app-id=r#"^my\.app$"#
        #     open-on-workspace "custom"
        #   }
```

License
-------

MIT-0
