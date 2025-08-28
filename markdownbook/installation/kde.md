# KDE

This will install KDE tools necessary for managing a KDE config, and enables config backup & restore
functionality. Make sure to specify your chosen `tool_provider`(`devbox` in this example).

```bash
ansible-pull -U https://github.com/pbonh/ars.git kde.yml --tags "install" --skip-tags "kwin" -e "{tool_provider: \"devbox\"}"
```
