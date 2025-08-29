import 'scripts/just/apps.just'
import 'scripts/just/dotfiles.just'
import 'scripts/just/distrobox.just'
import 'scripts/just/kde.just'
import 'scripts/just/mdbook.just'

set dotenv-load := true
set shell := ["/bin/bash", "-cu"]

task_prelude := env_var_or_default('DOTFILES_TASK_PRELUDE', '')
playbook_selection := if os() == "macos" { ".macos" } else { ".nix" }

default:
  @just --choose
