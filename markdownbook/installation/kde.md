# KDE

This will install KDE tools necessary for managing a KDE config, and enables config backup & restore
functionality.

```bash
ansible-pull -U https://github.com/pbonh/ars.git kde.yml --tags "install" --skip-tags "kwin"
```
