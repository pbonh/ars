set dotenv-load := true
set shell := ["/bin/bash", "-cu"]

task_prelude := env_var_or_default('DOTFILES_TASK_PRELUDE', '')
playbook_selection := if os() == "macos" { ".macos" } else { ".nix" }

default:
  @just --choose

install-requirements:
  {{ task_prelude }} ansible-galaxy install -r requirements.yml
  {{ task_prelude }} ansible-galaxy collection install -r requirements.yml

