# Mise

Mise is a package manager for the developer tools in this repo. The role installs the mise binary
and applies the tool configuration for you.

To install the Mise-managed packages, ensure `ansible` is installed and create a file to apply your
customizations. The variable `tool_provider` MUST be specified as `mise`.

Base Example Yaml Config(mise.yml):
```yaml
---
tool_provider: "mise"
```

Now use `ansible-pull` to install the Mise packages:

```bash
ansible-pull -U https://github.com/pbonh/ars.git ars.yml --tags "install" -e "@mise.yml"
```

Optional Git-Enabled Example Yaml Config(mise-git.yml):
```yaml
---
tool_provider: "mise"
dev_machine: true
git_name: "Your Name"
git_email: "your_name@address.com"
github_username: "username"
```

Apply optional Git/SSH + Git tooling config:

```bash
ansible-pull -U https://github.com/pbonh/ars.git dev.yml -e "@mise-git.yml"
```
