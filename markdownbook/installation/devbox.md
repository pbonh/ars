# Devbox

Run the bootstrap script, which will install:

1. Nix(via Determinate Systems)
2. Devbox
3. Bootstrap `.bashrc` Config

```bash
wget -O - https://raw.githubusercontent.com/pbonh/ars/main/scripts/bootstrap_devbox.sh | bash
```

To install the Devbox packages, ensure `ansible` is installed and create a file to apply your
customizations. The variable `tool_provider` MUST be specified as `devbox`.

Base Example Yaml Config(devbox.yml):
```yaml
---
tool_provider: "devbox"
```

Now use `ansible-pull` to install the Devbox packages:

```bash
ansible-pull -U https://github.com/pbonh/ars.git ars.yml --tags "install" -e "@devbox.yml"
```

Optional Git-Enabled Example Yaml Config(devbox-git.yml):
```yaml
---
tool_provider: "devbox"
dev_machine: true
git_name: "Your Name"
git_email: "your_name@address.com"
github_username: "username"
```

Apply optional Git/SSH + Git tooling config:

```bash
ansible-pull -U https://github.com/pbonh/ars.git dev.yml -e "@devbox-git.yml"
```
