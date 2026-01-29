# Mise

Mise is a package manager for the developer tools in this repo. The role installs the mise binary
and applies the tool configuration for you.

To install the Mise-managed packages, ensure `ansible` is installed and create a file to apply your
customizations. The variable `tool_provider` MUST be specified as `mise`. The remaining variables are
optional, but keep in mind that they will overwrite any customizations that you have made to git,
ssh, neovim, tmux, etc.

Example Yaml Config(mise.yml):
```yaml
---
tool_provider: "mise"
git_name: "Your Name"
git_email: "your_name@address.com"
github_username: "username"
anthropic_api_key: "MY_ANTHROPIC_API_KEY"
openai_api_key: "MY_OPENAI_API_KEY"
```

Now use `ansible-pull` to install the Mise packages:

```bash
ansible-pull -U https://github.com/pbonh/ars.git dotfiles.yml --tags "install" -e "@mise.yml"
```
