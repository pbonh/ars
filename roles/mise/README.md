Role Name
=========

Manage installation of the mise binary and configure mise config files (`mise.toml`, `mise.local.toml`, `~/.config/mise/config.toml`, `conf.d` fragments).

Requirements
------------

None beyond Ansible built-ins.

Role Variables
--------------

Core config variables (templated into `mise-config.toml.j2` by default):

- `mise_env`: mapping for `[env]` section.
- `mise_tools`: mapping for `[tools]` section. Each entry accepts an object with `name` (required, string for the actual package) and optional `version` (defaults to `latest`); legacy string values are still accepted and treated as the version for that key.
- `mise_tasks`: mapping for `[tasks.*]` entries; each task is a mapping of keys (e.g., `run`, `depends`, `dir`).
- `mise_settings`: mapping for `[settings]` section.
- `mise_plugins`: mapping for `[plugins]` section.
- `mise_tool_alias`: mapping for `[tool_alias.<tool>.versions]`.
- `mise_shell_alias`: mapping for `[shell_alias]`.
- `mise_min_version_hard` / `mise_min_version_soft`: strings to set `min_version` (hard/soft).
- `mise_experimental_monorepo_root`: bool to set `experimental_monorepo_root`.
- `mise_config_raw`: raw TOML appended at end of template.
- `mise_schema_url`: schema URL hint (default `https://mise.jdx.dev/schema/mise.json`).
- `mise_task_schema_url`: schema URL hint for task fragments (default `https://mise.jdx.dev/schema/mise-task.json`).

Config file management:

- `mise_config_files`: list of files to manage (e.g., `mise.toml`, `mise.local.toml`, `~/.config/mise/config.toml`). Each item supports:
  - `path` (required)
  - `state` (`present`|`absent`, default `present`)
  - `mode` (default `0644`)
  - `owner`, `group` (optional)
  - `dir_mode` (default `0755` for created parents)
  - `content` (raw text; bypasses templating)
  - `template` (default `mise-config.toml.j2`)
  - `schema_url` (override schema hint)
  - `vars` (dict to override template context per-file: any of the core config vars above)

- `mise_conf_d_fragments`: list of additional fragments for `conf.d` directories; same schema as `mise_config_files`. Example: `path: ~/.config/mise/conf.d/10-tasks.toml`.

Tool name reuse:

- When `mise_settings.enable_tools` is not provided, the role now derives it from the `name` fields in `mise_tools` (falling back to legacy keys when `name` is absent).

Binary install control:

- `mise_install_binary` (bool, default true): toggle downloading/installing mise. When false, only config management runs.
- Existing install vars remain supported (`mise_version`, `mise_install_path`, etc.).

Dependencies
------------

None.

Example Playbook
----------------

```yaml
- hosts: all
  roles:
    - role: mise
      vars:
        mise_install_help: true
        mise_config_files:
          - path: "{{ ansible_env.HOME }}/work/mise.toml"
            vars:
              mise_env:
                NODE_ENV: production
              mise_tools:
                node:
                  name: node
                  version: "22"
                python:
                  name: python
                  version: "3.12"
              mise_tasks:
                build:
                  run: "npm run build"
              mise_settings:
                jobs: 6
        mise_conf_d_fragments:
          - path: "{{ ansible_env.HOME }}/.config/mise/conf.d/10-local-env.toml"
            vars:
              mise_env:
                API_URL: "http://localhost:3000"
```

License
-------

MIT-0

Author Information
------------------

pbonh
