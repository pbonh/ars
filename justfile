set dotenv-load := true
set shell := ["/bin/bash", "-cu"]

task_prelude := env_var_or_default('DOTFILES_TASK_PRELUDE', '')
playbook_selection := if os() == "macos" { ".macos" } else { ".nix" }

default:
  @just --choose

install-requirements:
  {{ task_prelude }} ansible-galaxy install -r requirements.yml
  {{ task_prelude }} ansible-galaxy collection install -r requirements.yml

shell tag='devbox':
  {{ task_prelude }} ansible-playbook shell.yml --tags "{{ tag }}"

code tag='devbox':
  {{ task_prelude }} ansible-playbook code.yml --tags "{{ tag }}"

devbox:
  {{ task_prelude }} ansible-playbook devbox.yml

homebrew:
  {{ task_prelude }} ansible-playbook homebrew.yml

nonroot:
  {{ task_prelude }} ansible-playbook nonroot.yml
