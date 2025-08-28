# Homebrew

The following command will install homebrew for Linux or macOS systems:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

To install the Homebrew packages, ensure `ansible` is installed and create a file to apply your
customizations. The variable `tool_provider` MUST be specified as `homebrew`. The remaining variables
are optional, but keep in mind that they will overwrite any customizations that you have made to
git, ssh, neovim, tmux, etc.

Example Yaml Config(brew.yml):
```yaml
---
tool_provider: "homebrew"
git_name: "Your Name"
git_email: "your_name@address.com"
github_username: "username"
anthropic_api_key: "MY_ANTHROPIC_API_KEY"
openai_api_key: "MY_OPENAI_API_KEY"
```

Now use `ansible-pull` to install the Homebrew packages:

```bash
ansible-pull -U https://github.com/pbonh/ars.git dotfiles.yml --tags "install" -e "@brew.yml"
```
