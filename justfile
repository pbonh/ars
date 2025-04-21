set dotenv-load := true
set shell := ["/bin/bash", "-cu"]

task_prelude := env_var_or_default('DOTFILES_TASK_PRELUDE', '')
playbook_selection := if os() == "macos" { ".macos" } else { ".nix" }

default:
  @just --choose

install-requirements:
  {{ task_prelude }} ansible-galaxy install -r requirements.yml
  {{ task_prelude }} ansible-galaxy collection install -r requirements.yml

setup: install-requirements
  git update-index --skip-worktree vars/local.yml 

dotfiles tag='devbox':
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "{{ tag }}"

devbox:
  {{ task_prelude }} ansible-playbook devbox.yml

homebrew:
  {{ task_prelude }} ansible-playbook homebrew.yml

nonroot:
  {{ task_prelude }} ansible-playbook nonroot.yml

dot tag='env':
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "{{ tag }}" --skip-tags "install"

shell:
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "env,scripts" --skip-tags "install"

bash:
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "bash" --skip-tags "install"

zsh:
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "zsh" --skip-tags "install"

tcsh:
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "tcsh" --skip-tags "install"

neovim:
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "neovim-config" --skip-tags "install"

zellij:
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "zellij" --skip-tags "install"

navi:
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "navi" --skip-tags "install"

ollama:
  {{ task_prelude }} ansible-playbook --ask-become-pass ollama.yml

code2prompt:
  {{ task_prelude }} ansible-playbook ollama.yml --tags "code2prompt" --skip-tags "install"
