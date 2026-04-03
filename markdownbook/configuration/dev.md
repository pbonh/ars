# Developer Configuration

The `dev` role configures Git identity, SSH settings, and developer-specific tooling.

## Just Tasks

| Task | Description |
|------|-------------|
| `just configure-git` | Configure Git user name, email, and GitHub settings |
| `just configure-ssh` | Configure SSH keys and agent (depends on configure-git) |

## Configuration

Set these variables in `vars/local.yml` or via `-e` flag:

```yaml
---
dev_machine: true
git_name: "Your Name"
git_email: "your_name@address.com"
github_username: "username"
```

## Ansible-Pull

Apply developer configuration via ansible-pull:

```bash
ansible-pull -U https://github.com/pbonh/ars.git dev.yml -e "{dev_machine: true, git_name: 'Your Name', git_email: 'email@example.com', github_username: 'username'}"
```

Or with a vars file:

```bash
ansible-pull -U https://github.com/pbonh/ars.git dev.yml -e "@dev-config.yml"
```
