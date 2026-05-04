install-requirements:
  {{ task_prelude }} ansible-galaxy install -r requirements.yml
  {{ task_prelude }} ansible-galaxy collection install -r requirements.yml

setup: install-requirements
  git update-index --skip-worktree vars/local.yml 

dotfiles:
  {{ task_prelude }} ansible-playbook ars.yml --skip-tags "install"

mise:
  {{ task_prelude }} ansible-playbook mise.yml

install-mise-gpg:
  {{ task_prelude }} ansible-playbook mise.yml --tags "gpg"

config-mise:
  {{ task_prelude }} ansible-playbook mise.yml --tags "config" --skip-tags "install"

devbox:
  {{ task_prelude }} ansible-playbook devbox.yml

install-homebrew:
  {{ task_prelude }} ansible-playbook homebrew.yml --tags "install"

homebrew:
  {{ task_prelude }} ansible-playbook homebrew.yml --tags "config" --skip-tags "install"

nonroot:
  {{ task_prelude }} ansible-playbook nonroot.yml

dot tag='env':
  {{ task_prelude }} ansible-playbook ars.yml --tags "{{ tag }}" --skip-tags "install"

pick:
  #!/usr/bin/env bash
  set -euo pipefail
  picker=""
  if command -v tv >/dev/null 2>&1; then
    picker="tv"
  elif command -v fzf >/dev/null 2>&1; then
    picker="fzf --multi --prompt=ansible-tag:❯ --height=40% --reverse --border"
  else
    echo "pick: requires fzf or tv on PATH" >&2
    exit 1
  fi
  tags=$({{ task_prelude }} ansible-playbook ars.yml --list-tags 2>/dev/null \
    | awk -F'[][]' '/TASK TAGS:/ {print $2}' \
    | tr ',' '\n' \
    | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' \
    | grep -v '^$' \
    | grep -vE '^(install|always)$' \
    | sort -u)
  if [ -z "$tags" ]; then
    echo "pick: no tags discovered from ars.yml" >&2
    exit 1
  fi
  chosen=$(printf '%s\n' "$tags" | $picker) || exit 0
  [ -z "$chosen" ] && exit 0
  joined=$(printf '%s\n' "$chosen" | paste -sd, -)
  echo ">> ansible-playbook ars.yml --tags \"$joined\" --skip-tags install"
  {{ task_prelude }} ansible-playbook ars.yml --tags "$joined" --skip-tags install

shell:
  {{ task_prelude }} ansible-playbook ars.yml --tags "env,scripts" --skip-tags "install"

nushell:
  {{ task_prelude }} ansible-playbook ars.yml --tags "nushell" --skip-tags "install"

scripts:
  {{ task_prelude }} ansible-playbook ars.yml --tags "scripts" --skip-tags "install"

bash:
  {{ task_prelude }} ansible-playbook ars.yml --tags "bash" --skip-tags "install"

zsh:
  {{ task_prelude }} ansible-playbook ars.yml --tags "zsh" --skip-tags "install"

tcsh:
  {{ task_prelude }} ansible-playbook ars.yml --tags "tcsh" --skip-tags "install"

neovim:
  {{ task_prelude }} ansible-playbook ars.yml --tags "neovim-config" --skip-tags "install"

rebuild-neovim:
  {{ task_prelude }} ansible-playbook ars.yml --tags "neovim-config-clean" --skip-tags "install"

zellij:
  {{ task_prelude }} ansible-playbook ars.yml --tags "zellij" --skip-tags "install"

yazi:
  {{ task_prelude }} ansible-playbook ars.yml --tags "yazi" --skip-tags "install"

navi:
  {{ task_prelude }} ansible-playbook ars.yml --tags "navi" --skip-tags "install"

ai:
  {{ task_prelude }} ansible-playbook ars.yml --tags "ai" --skip-tags "install"

ollama:
  {{ task_prelude }} ansible-playbook --ask-become-pass ollama.yml

code2prompt:
  {{ task_prelude }} ansible-playbook ollama.yml --tags "code2prompt" --skip-tags "install"
