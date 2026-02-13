# Dotfiles

This will apply settings(dotfiles) for a large variety of programs. There are filters in place to
selectivly apply them. Users are strongly encouraged to set their own project, layouts, aliases,
etc.

The bare minimum would be:

Example:
```yaml
# devbox.yml
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
```

The above settings can be applied by running:

```bash
ansible-pull -U https://github.com/pbonh/ars.git dotfiles.yml --skip-tags "install" -e "@devbox.yml"
```

If checking out the `ars` repo directly, then create `vars/local.yml`, and add configuration there, no `-e` option necessary.

```bash
ansible-playbook playbook.yml --skip-tags "install"
```

## Bitwarden CLI + wl-clipboard (Flatpak)

This is a quick way to copy passwords to the Wayland clipboard using the Flatpak Bitwarden CLI.

Set a Flatpak wrapper alias and unlock once per shell session:

```bash
alias bw='flatpak run --command=bw com.bitwarden.desktop'
export BW_SESSION="$(bw unlock --raw)"
```

Copy by exact item name:

```bash
bw get password "Item Name" | wl-copy
```

Search and pick an item ID (requires `jq`):

```bash
bw list items --search "query" | jq -r '.[] | "\(.id)\t\(.name)"'
bw get password <id> | wl-copy
```

### Bashrc helpers

```bash
# ~/.bashrc
alias bw='flatpak run --command=bw com.bitwarden.desktop'

bw_unlock() {
  export BW_SESSION="$(bw unlock --raw)"
}

bw_copy_name() {
  bw get password "$1" | wl-copy
}

bw_search() {
  bw list items --search "$1" | jq -r '.[] | "\(.id)\t\(.name)"'
}

bw_copy_id() {
  bw get password "$1" | wl-copy
}

bw_pick_copy() {
  local selection
  selection="$(bw list items --search "$1" | jq -r '.[] | "\(.id)\t\(.name)"' | fzf)"
  [ -n "$selection" ] || return 1
  bw get password "${selection%%$'\t'*}" | wl-copy
}
```

Clipboard auto-clear (optional): check `wl-copy --help` for a `--clear` flag; if available, you can clear after a delay.

```bash
bw_copy_name_clear() {
  bw get password "$1" | wl-copy
  (sleep 20; wl-copy --clear) &
}
```
