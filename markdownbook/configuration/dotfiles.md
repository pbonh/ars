# Dotfiles

This will apply settings(dotfiles) for a large variety of programs. There are filters in place to
selectivly apply them. Users are strongly encouraged to set their own project, layouts, aliases,
etc.

The bare minimum would be:

Base Example:
```yaml
# devbox.yml
---
tool_provider: "devbox"
projects:
  ars:
    name: "pbonh/ars"
    url: "https://github.com/pbonh/ars.git"
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

Optional Git-Enabled Example:

```yaml
# devbox-git.yml
---
tool_provider: "devbox"
dev_machine: true
git_name: "Your Name"
git_email: "your_name@address.com"
github_username: "username"
projects:
  ars:
    name: "pbonh/ars"
    url: "{{ github_ssh_url }}:pbonh/ars.git"
    path: "{{ code_checkout_path_github }}/pbonh/ars"
```

Optional SSH Overlay (YubiKey/FIDO2 defaults):

```yaml
# devbox-git-yubikey.yml
---
dev_machine: true
git_name: "Your Name"
git_email: "your_name@address.com"
github_username: "username"
projects:
  ars:
    url: "{{ github_ssh_url }}:pbonh/ars.git"

# Uses role defaults:
# bash_ssh_fido2_enabled: true
# zsh_ssh_fido2_enabled: true
# dev_ssh_manage_fido2_stanza: true
```

Optional SSH Overlay (plain ssh-agent config):

```yaml
# devbox-git-plain-ssh.yml
---
dev_machine: true
git_name: "Your Name"
git_email: "your_name@address.com"
github_username: "username"
projects:
  ars:
    url: "{{ github_ssh_url }}:pbonh/ars.git"

bash_ssh_fido2_enabled: false
zsh_ssh_fido2_enabled: false
dev_ssh_manage_fido2_stanza: false
```

The above settings can be applied by running:

```bash
ansible-pull -U https://github.com/pbonh/ars.git ars.yml --skip-tags "install" -e "@devbox.yml"
```

Apply optional Git/SSH + Git tooling config:

```bash
ansible-pull -U https://github.com/pbonh/ars.git dev.yml -e "@devbox-git.yml"
ansible-pull -U https://github.com/pbonh/ars.git dev.yml -e "@devbox-git-yubikey.yml"
ansible-pull -U https://github.com/pbonh/ars.git dev.yml -e "@devbox-git-plain-ssh.yml"
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

## Available Tags

The dotfiles role supports selective application via tags. Use `--tags` to apply specific configurations or `--skip-tags` to exclude them.

### Tool-Specific Tags

| Tag | Description | Just Task |
|-----|-------------|-----------|
| `env` | Environment setup (shell configs, directories) | `just dot` (default), `just shell` |
| `bash` | Bash configuration | `just bash` |
| `zsh` | Zsh configuration | `just zsh` |
| `tcsh` | Tcsh configuration | `just tcsh` |
| `nushell` | Nushell configuration | `just nushell` |
| `scripts` | Shell scripts and aliases | `just scripts` |

### Editor Tags

| Tag | Description | Just Task |
|-----|-------------|-----------|
| `neovim-config` | Neovim configuration | `just neovim` |
| `neovim-config-clean` | Clean and rebuild Neovim config | `just rebuild-neovim` |
| `helix-config` | Helix editor configuration | - |
| `editor` | All editor configurations | - |

### Terminal Multiplexer Tags

| Tag | Description | Just Task |
|-----|-------------|-----------|
| `zellij` | Zellij configuration | `just zellij` |
| `tmux` | Tmux configuration | - |
| `session` | All session managers | - |

### File Manager Tags

| Tag | Description | Just Task |
|-----|-------------|-----------|
| `yazi` | Yazi file manager config | `just yazi` |
| `navi` | Navi cheatsheet tool | `just navi` |
| `broot` | Broot file manager | - |
| `ranger` | Ranger file manager | - |

### AI Tool Tags

| Tag | Description | Just Task |
|-----|-------------|-----------|
| `ai` | All AI tools configuration | `just ai` |
| `pi` | Pi coding agent config | - |
| `opencode` | OpenCode configuration | - |
| `claude` | Claude Code configuration | - |
| `codex` | Codex CLI configuration | - |
| `sidecar` | Sidecar configuration | - |
| `superpowers` | Superpowers skills | - |

### Other Tags

| Tag | Description | Just Task |
|-----|-------------|-----------|
| `direnv` | Direnv configuration | - |
| `joplin` | Joplin notes configuration | - |
| `bookmarks` | Bookmarks configuration | - |
| `setup` | Directory and environment setup | - |

### Common Usage Patterns

Apply only shell configurations:
```bash
ansible-playbook ars.yml --tags "env" --skip-tags "install"
```

Apply only AI tool configurations:
```bash
ansible-playbook ars.yml --tags "ai" --skip-tags "install"
```

Apply only editor configurations:
```bash
ansible-playbook ars.yml --tags "editor" --skip-tags "install"
```

Exclude specific tools:
```bash
ansible-playbook ars.yml --skip-tags "install,neovim-config"
```

## Hermes Skills

The dotfiles role deploys [Hermes](https://hermes.sh) skill files to
`~/.hermes/skills/`. Skills are conversational programs invoked from a
Hermes session.

### Ingest pipeline

The `ingest-pipeline` skill ties `split-textbooks` and `pdf-to-mdbook`
together into an end-to-end orchestrator. It accepts any of:

- A single large PDF.
- A directory of pre-split chapter PDFs.
- A directory of pre-split markdown documents.
- A partial mdBook directory (interrupted prior run).

…and drives it forward to a buildable mdBook. State is persisted in
`pipeline.json` per book; reruns resume from where the previous run
stopped.

Two skills ship together:

- `ingest-pipeline` — per-book engine.
- `ingest-pipeline-batch` — library sweep; runs `ingest-pipeline` over
  every book directory under a library root. Also maintains a
  `library.json` summary at the library root tracking each book's
  status across runs.

Both skills are invoked from a Hermes session like other skills. The
terminal state is `mdbook build` succeeding; wiki ingestion remains a
separate, manual `wiki-ingest` step.

Tests live under `roles/dotfiles/tests/hermes/`. Run them with:

    just test-hermes
    just test-hermes-integration   # requires hermes CLI on PATH
    just regenerate-hermes-fixtures # rebuilds synthetic PDFs
