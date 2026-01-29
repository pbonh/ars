# Installation

There are different starting points for installing `pbonh/ars` on your system, and they will depend
on your OS. If you are on Linux, pick a `bootstrap_*` script that closely matches the system. There
is also a portable version of ansible available(`scripts/bootstrap_ansible`).

## Bootstrap Examples
- Install Ansible(Portable)
```bash
wget -O - https://raw.githubusercontent.com/pbonh/ars/main/scripts/bootstrap_ansible.sh | bash
```

- Bootstrap Bluefin
```bash
wget -O - https://raw.githubusercontent.com/pbonh/ars/main/scripts/bootstrap_bluefin.sh | bash
```

- Bootstrap Ubuntu
```bash
wget -O - https://raw.githubusercontent.com/pbonh/ars/main/scripts/bootstrap_ubuntu.sh | bash
```

- Bootstrap Fedora
```bash
wget -O - https://raw.githubusercontent.com/pbonh/ars/main/scripts/bootstrap_fedora.sh | bash
```

## Git/SSH(Optional)
Optionally, `git` & `ssh` can be configured via a prompt:

- Configure Git/SSH
```bash
wget -O - https://raw.githubusercontent.com/pbonh/ars/main/scripts/bootstrap_gitssh.sh | bash
```

## Workstation GUI

If GUI support is desired, the following desktop environments are available:

- KDE

## Developer Tools

There are 4 installation options to choose from for the developer tools (homebrew is the default):

1. Homebrew (default)
2. Mise
3. Devbox
4. Non-Root

Homebrew is the default tool manager for the developer toolset. Mise provides a curated toolchain,
and Devbox uses `nix` with support for custom shell environments. Non-Root is useful when you don't
have root permissions, but still need to install the developer tools. All 4 are compatible with
Linux & macOS.

EITHER
Checkout repository and create `.envrc` File(Example)
```bash
touch .envrc
ln -s .envrc .env
cat << EOF >> .envrc
DOTFILES_TASK_PRELUDE=python
DOTFILES_BOOTSTRAP_GIT_NAME="Your Name"
DOTFILES_BOOTSTRAP_GIT_EMAIL="your_name@address.com"
DOTFILES_BOOTSTRAP_GITHUB_USERNAME="username"
OPENAI_API_KEY="MY_OPENAI_API_KEY"
ANTHROPIC_API_KEY="MY_ANTHROPIC_API_KEY"
EOF
```
OR
Ansible Pull
```bash
# (Non-Root, Shell Tools Only)
ansible-pull -U https://github.com/pbonh/ars.git dotfiles.yml --tags "env" -e "{tool_provider: \"nonroot\"}"

# (Install Non-Root, Shell Tools Only)
ansible-pull -U https://github.com/pbonh/ars.git dotfiles.yml --tags "install,env" -e "{tool_provider: \"nonroot\"}"
```
