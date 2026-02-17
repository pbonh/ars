## Project Layout Snapshot (Keep In Sync)

Justfile entrypoints:
- Root `justfile` imports `scripts/just/*.just` and uses `just --choose` by default.
- `scripts/just/apps.just`: `install-apps`
- `scripts/just/distrobox.just`: `distrobox`, `distrobox-ubuntu`, `pull-ars`
- `scripts/just/dotfiles.just`: `install-requirements`, `setup`, `dotfiles`, `mise`, `install-mise-gpg`, `config-mise`, `devbox`, `install-homebrew`, `homebrew`, `nonroot`, `dot`, `shell`, `nushell`, `scripts`, `bash`, `zsh`, `tcsh`, `neovim`, `rebuild-neovim`, `zellij`, `yazi`, `navi`, `ai`, `ollama`, `code2prompt`
- `scripts/just/kde.just`: `workstation-kde`, `backup-kde-config`, `restore-kde-config`, `generate-uuid`
- `scripts/just/mdbook.just`: `mdbook-build`, `mdbook-serve`, `mdbook-serve-all`, `mdbook-push`, `mdbook-rsync`, `mdbook-gh-pages`
- `scripts/just/niri.just`: `workstation-niri`
- `scripts/just/ucore.just`: `regenerate-ignition-file`
