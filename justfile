set dotenv-load := true
set shell := ["/bin/bash", "-cu"]

task_prelude := env_var_or_default('DOTFILES_TASK_PRELUDE', '')
playbook_selection := if os() == "macos" { ".macos" } else { ".nix" }

default:
  @just --choose

install-requirements:
  {{ task_prelude }} ansible-galaxy install -r requirements.yml
  {{ task_prelude }} ansible-galaxy collection install -r requirements.yml

dotfiles tag='devbox':
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "{{ tag }}"

devbox:
  {{ task_prelude }} ansible-playbook devbox.yml

homebrew:
  {{ task_prelude }} ansible-playbook homebrew.yml

nonroot:
  {{ task_prelude }} ansible-playbook nonroot.yml

neovim:
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "neovim-config" --skip-tags "install"
