Shell
=========

Homebrew Configuration

Requirements
------------

Install Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Role Variables
--------------

Global Package Configuration for Homebrew Install

Dependencies
------------

- Homebrew

Example Playbook
----------------

```yaml
- name: Install Homebrew Tools
  import_role:
    name: homebrew
```

License
-------

Apache 2.0

Author Information
------------------

Phillip Bonhomme
