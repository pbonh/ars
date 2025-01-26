Role Name
=========

My Developer Dotfiles, powered by Ansible.

Installation Examples
------------

Install Ansible
```bash
wget -O - https://raw.githubusercontent.com/pbonh/ars/main/scripts/bootstrap_ansible.sh | bash
```

Configure Git/SSH
```bash
wget -O - https://raw.githubusercontent.com/pbonh/ars/main/scripts/bootstrap_gitssh.sh | bash
```

Install Devbox
```bash
wget -O - https://raw.githubusercontent.com/pbonh/ars/main/scripts/bootstrap_devbox.sh | bash
```

Install Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

EITHER
Checkout repository and create `.envrc` File(Example)
```bash
touch .envrc
ln -s .envrc .env
cat << EOF >> .envrc
DOTFILES_TASK_PRELUDE=python
DOTFILES_BOOTSTRAP_GIT_NAME="Your Name"
DOTFILES_BOOTSTRAP_GIT_EMAIL="your_name@address.com"
DOTFILES_BOOTSTRAP_GITHUB_USERNAME="username"
OPENAI_API_KEY="MY_OPENAI_API_KEY"
ANTHROPIC_API_KEY="MY_ANTHROPIC_API_KEY"
EOF
```
OR
Ansible Pull
```bash
# (Non-Root, Shell Tools Only)
ansible-pull -U https://github.com/pbonh/ars.git playbook.yml --tags "env" -e "{tool_provider: \"nonroot\"}"

# (Install Non-Root, Shell Tools Only)
ansible-pull -U https://github.com/pbonh/ars.git playbook.yml --tags "install,env" -e "{tool_provider: \"nonroot\"}"
```

Optional Installations
------------
Ollama(w/ ROCM)
```bash
ansible-pull -U https://github.com/pbonh/ars.git --ask-become-pass ollama.yml -e "{rocm_support: true}"
```

Configuration
-------

EITHER
Create a file to specify your configuration.

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
nushell_config_dir: "{{ macos_config_dir }}/nushell"
xdg_config_dir_navi: "{{ macos_config_dir }}/navi"
```

Run playbook with configuration file:
```bash
ansible-pull -U https://github.com/pbonh/ars.git playbook.yml --tags "install,env" -e "@macos.yml"
```

OR
Checkout repository, create `vars/local.yml`, and add configuration there, no `-e` option necessary.
```bash
ansible-playbook playbook.yml --tags "install,env"
```

License
-------

Apache 2.0

Author Information
------------------

Phillip Bonhomme
