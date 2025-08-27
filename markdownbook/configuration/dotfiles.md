# Dotfiles

This will apply settings(dotfiles) for a large variety of programs. There are filters in place to
selectivly apply them. Users are strongly encouraged to set their own project, layouts, aliases,
etc.

The bare minimum would be:

Example:
```yaml
# example.yml
---
tool_provider: "devbox"
projects:
  ars:
    name: "pbonh/ars"
    url: "{{ github_ssh_url }}:pbonh/ars.git"
    path: "{{ code_checkout_path_github }}/pbonh/ars"
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
nushell_extra_aliases: |
  alias zdot = {{ zellij_exe }} --layout dotfiles
bash_extra_aliases: |
  alias zdot='{{ zellij_exe }} --layout dotfiles'
extra_zsh_aliases: |
  alias zdot='{{ zellij_exe }} --layout dotfiles'
```

The above settings can be applied by running:

```bash
ansible-pull -U https://github.com/pbonh/ars.git dotfiles.yml --skip-tags "install" -e "@example.yml"
```

If checking out the `ars` repo directly, then create `vars/local.yml`, and add configuration there, no `-e` option necessary.

```bash
ansible-playbook playbook.yml --skip-tags "install"
```
