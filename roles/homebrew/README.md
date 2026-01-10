Homebrew
========

Installs taps, formulae, casks, and flatpaks via `brew bundle` using a generated Brewfile at `~/.Brewfile`. Cleanup runs by default.

Requirements
------------
- Homebrew installed and accessible as `brew`.

Role Variables
--------------
- `homebrew_brewfile_path`: path for the Brewfile (default `~/.Brewfile`).
- `homebrew_bundle_no_lock`: skip `Brewfile.lock.json` generation (default `true`).
- `homebrew_bundle_check`: run `brew bundle check` before install (default `true`).
- `homebrew_bundle_cleanup`: run `brew bundle cleanup --force` after install (default `true`).
- `homebrew_bundle_bin_dir_default`, `homebrew_brew_bin_default`: OS-detected defaults (Darwin uses `homebrew_path_macos`, others use `homebrew_path`).
- `homebrew_bundle_env_path`: default PATH seed; tasks recompute an OS-appropriate PATH (`homebrew_bundle_env_path_resolved`) using detected Homebrew bin dir + `ansible_env.PATH`.
- `homebrew_brewfile_extra_taps`, `homebrew_brewfile_extra_formulae`, `homebrew_brewfile_extra_casks`: lists appended to the generated Brewfile.
- `homebrew_cask_packages`, `homebrew_formula_packages_extra`, `homebrew_flatpak_packages`: derived from `flatpak_apps_bundle_map` in `group_vars/all.yml`.
- `dev_packages.*.brew`: formulae included in the Brewfile.

How it works
------------
1. Resolve Homebrew paths per OS (Darwin vs others) using `ansible_facts.system`, then template `roles/homebrew/templates/Brewfile.j2` to `{{ homebrew_brewfile_path }}` from taps, dev package brew entries, flatpak-to-cask/formula mapping, flatpak entries (with optional `remote`/`url`), and extra lists.
2. Run `brew bundle check --file … --no-lock` (if enabled) then `brew bundle install --file … --no-lock` with the resolved PATH.
3. Run `brew bundle cleanup --force --file … --no-lock` when cleanup is enabled.

Adding packages
---------------
- CLI tools: add to `dev_packages.<name>.brew` in `group_vars/all.yml`.
- GUI apps: set `flatpak_apps_bundle_map.<app>.cask` (or `.formula`), or use `flatpak` (with optional `remote`/`url`) in `group_vars/all.yml`.
- Extra taps/formulae/casks: use `homebrew_brewfile_extra_*` variables.

Manual commands
---------------
- Check: `brew bundle check --file ~/.Brewfile --no-lock`
- Install: `brew bundle install --file ~/.Brewfile --no-lock`
- Cleanup: `brew bundle cleanup --file ~/.Brewfile --force --no-lock`

Note
----
`Brewfile.lock.json` is intentionally skipped per Homebrew Bundle guidance.
