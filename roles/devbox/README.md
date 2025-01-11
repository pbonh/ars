Shell
=========

Devbox Configuration

Requirements
------------

EITHER
Install via Bootstrap Script
```bash
wget -O - https://raw.githubusercontent.com/pbonh/ars/main/scripts/bootstrap_devbox.sh | bash
```
OR
Install Nix & Devbox Manually
```bash
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | \
  sh -s -- install
curl -fsSL https://get.jetify.com/devbox | bash
```

Role Variables
--------------

Global Package Configuration for Devbox Install

Dependencies
------------

- Devbox

Example Playbook
----------------

```yaml
- name: Install Global Devbox Tools
  import_role:
    name: devbox
```

License
-------

Apache 2.0

Author Information
------------------

Phillip Bonhomme
