# Devbox

Run the bootstrap script, which will install:

1. Nix(via Determinate Systems)
2. Devbox
3. Bootstrap `.bashrc` Config

```bash
wget -O - https://raw.githubusercontent.com/pbonh/ars/main/scripts/bootstrap_devbox.sh | bash
```

To install the Devbox packages, ensure `ansible` is installed and create a file to apply your
customizations. The variable `tool_provider` MUST be specified as `devbox`. The remaining variables
are optional, but keep in mind that they will overwrite any customizations that you have made to
git, ssh, neovim, tmux, etc.

Example Yaml Config(devbox.yml):
```yaml
---
tool_provider: "devbox"
git_name: "Your Name"
git_email: "your_name@address.com"
github_username: "username"
anthropic_api_key: "MY_ANTHROPIC_API_KEY"
openai_api_key: "MY_OPENAI_API_KEY"
```

Now use `ansible-pull` to install the Devbox packages:

```bash
ansible-pull -U https://github.com/pbonh/ars.git dotfiles.yml --tags "install" -e "@devbox.yml"
```
