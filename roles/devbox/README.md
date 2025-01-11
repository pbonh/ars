Shell
=========

Devbox Configuration

Requirements
------------

Install Devbox
```bash
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
