# Non-Root

To install the Non-Root packages, ensure `ansible` is installed and create a file to apply your
customizations. The variable `tool_provider` MUST be specified as `nonroot`.

Base Example Yaml Config(nonroot.yml):
```yaml
---
tool_provider: "nonroot"
```

Now use `ansible-pull` to install the Non-Root packages:

```bash
ansible-pull -U https://github.com/pbonh/ars.git ars.yml --tags "install" -e "@nonroot.yml"
```

Optional Git-Enabled Example Yaml Config(nonroot-git.yml):
```yaml
---
tool_provider: "nonroot"
dev_machine: true
git_name: "Your Name"
git_email: "your_name@address.com"
github_username: "username"
```

Apply optional Git/SSH + Git tooling config:

```bash
ansible-pull -U https://github.com/pbonh/ars.git dev.yml -e "@nonroot-git.yml"
```
