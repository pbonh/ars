# Examples

Example(MacOS):
```yaml
# macos.yml
---
tool_provider: "devbox"
homebrew_path: "{{ homebrew_path_macos }}"
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
other_projects: "{{ projects | dict2items | 
             map(attribute='key', 
                 attribute2='value', 
                 transform=lambda k, v: [k, {'name': v.name, 'path': v.path}]) | 
             items2dict }}"
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
      tab name="Devbox Project" split_direction="vertical" cwd="/path/to/devbox_project" {
          pane {
              command "env"
              args "NVIM_APPNAME=nvim-chatgpt-modular" "bash" "-c" "devbox run -- {{ nvim_exe }} README.md"
              start_suspended true
          }
      }
nushell_config_dir: "{{ macos_config_dir }}/nushell"
xdg_config_dir_navi: "{{ macos_config_dir }}/navi"
```

Example(Devbox,AMD-ROCM):
```yaml
---
tool_provider: "devbox"
rocm_support: true
ars_name: "pbonh/ars"
projects:
  ars:
    name: "{{ ars_name }}"
    url: "{{ github_ssh_url }}/{{ ars_name }}.git"
    path: "{{ code_checkout_path_github }}/{{ ars_name }}"
other_projects: "{{ projects | dict2items | 
             map(attribute='key', 
                 attribute2='value', 
                 transform=lambda k, v: [k, {'name': v.name, 'path': v.path}]) | 
             items2dict }}"
# {{
#   {
#     key: {
#       'name': value.name,
#       'path': value.path
#     }
#     for key, value in projects.items()
#   }
# }}
codelldb_install_path: "{{ codelldb_install_devbox_path }}"
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
      tab name="Neovim(Ollama): Lazy-Config" split_direction="vertical" cwd="{{ nvim_config_dir }}-lazy-modular" {
          pane {
              command "env"
              args {% set bash_arg_list = nvim_exe_ollama_bash_cmd %}
                   {% set bash_arg_string = bash_arg_list | map('string') | map('regex_replace', '^(.*)$', '"\\1"') | join(' ') %}
                   {{ bash_arg_string }}
              start_suspended true
          }
      }
      tab name="CPU/MEM" split_direction="vertical" {
          pane {
              command "btm"
              start_suspended true
          }
      }
