# Homebrew

The following command will install homebrew for Linux or macOS systems:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

To install the Homebrew packages, ensure `ansible` is installed and create a file to apply your
customizations. Homebrew is the default tool provider.

Base Example Yaml Config(brew.yml):
```yaml
---
tool_provider: "homebrew"
```

Now use `ansible-pull` to install the Homebrew packages:

```bash
ansible-pull -U https://github.com/pbonh/ars.git ars.yml --tags "install" -e "@brew.yml"
```

Optional Git-Enabled Example Yaml Config(brew-git.yml):
```yaml
---
tool_provider: "homebrew"
dev_machine: true
git_name: "Your Name"
git_email: "your_name@address.com"
github_username: "username"
```

Apply optional Git/SSH + Git tooling config:

```bash
ansible-pull -U https://github.com/pbonh/ars.git dev.yml -e "@brew-git.yml"
```
