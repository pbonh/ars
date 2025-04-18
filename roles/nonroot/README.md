Code
=========

Install Tools without Root Privileges

Requirements
------------

None

Role Variables
--------------

Installation settings for Local Installation

Dependencies
------------

None

Example Playbook
----------------

```yaml
- name: Install Local Tools(Non-Root)
  import_role:
    name: nonroot
```

Example Configuration
----------------

Example w/ custom install path for tool downloads/libraries/executables.
```yaml
# nonroot_config.yml
---
tool_provider: "nonroot"
tool_install_dir: "/path/to/disk/.local"
cargo_home: "/path/to/disk/.cargo"
ars_name: "pbonh/ars"
term_dev_name: "pbonh/term-dev.nix"
projects:
  ars:
    name: "{{ ars_name }}"
    url: "{{ github_ssh_url }}:{{ ars_name }}.git"
    path: "{{ code_checkout_path_github }}/{{ ars_name }}"
  term_dev:
    name: "{{ term_dev_name }}"
    url: "{{ github_ssh_url }}:{{ term_dev_name }}.git"
    path: "{{ code_checkout_path_github }}/{{ term_dev_name }}"
nushell_extra_aliases: |
  alias zdot = {{ zellij_exe }} --layout dotfiles
bash_extra_aliases: |
  alias zdot='{{ zellij_exe }} --layout dotfiles'
extra_zsh_aliases: |
  alias zdot='{{ zellij_exe }} --layout dotfiles'
zellij_kdl_layouts:
  dotfiles:
    name: dotfiles
    cwd: "{{ ansible_env.HOME }}"
    template_info: "{{ zellij_kdl_template_info_default }}"
    layout_info: |
      tab name="Ars" split_direction="vertical" cwd="{{ projects['ars']['path'] }}" focus=true {
          pane {
              command "{{ nvim_exe }}"
              args "README.md"
              start_suspended true
          }
      }
      tab name="Dotfiles" split_direction="vertical" cwd="{{ dotfiles_checkout_dir }}" {
          pane {
              command "env"
              args {% set bash_arg_list = nvim_exe_bone_bash_cmd %}
                   {% set bash_arg_string = bash_arg_list | map('string') | map('regex_replace', '^(.*)$', '"\\1"') | join(' ') %}
                   {{ bash_arg_string }}
              start_suspended true
          }
      }
      tab name="Devbox Project Example" split_direction="vertical" cwd="/path/to/devbox_project" {
          pane {
              command "env"
              args "NVIM_APPNAME=nvim-chatgpt-modular" "bash" "-c" "devbox run -- {{ nvim_exe }} README.md"
              start_suspended true
          }
      }
```

Run playbook with configuration file:
```bash
ansible-pull -U https://github.com/pbonh/ars.git playbook.yml --tags "install" -e "@nonroot_config.yml"
```

Run incremental updates with configuration file:
```bash
ansible-pull -U https://github.com/pbonh/ars.git playbook.yml --skip-tags "install" -e "@nonroot_config.yml"
```

License
-------

Apache 2.0

Author Information
------------------

Phillip Bonhomme
