import 'scripts/just/dotfiles.just'
import 'scripts/just/distrobox.just'
import 'scripts/just/kde.just'

set dotenv-load := true
set shell := ["/bin/bash", "-cu"]

task_prelude := env_var_or_default('DOTFILES_TASK_PRELUDE', '')
playbook_selection := if os() == "macos" { ".macos" } else { ".nix" }

default:
  @just --choose
