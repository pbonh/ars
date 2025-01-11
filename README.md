Role Name
=========

My Developer Dotfiles, powered by Ansible.

Installation
------------

Configure Git/SSH
```bash
wget -O - https://raw.githubusercontent.com/pbonh/ars/main/scripts/bootstrap_gitssh.sh | bash
```

Setup `.envrc` File(Example)
```bash
touch .envrc
ln -s .envrc .env
echo "DOTFILES_TASK_PRELUDE=python" > .envrc
```

License
-------

Apache 2.0

Author Information
------------------

Phillip Bonhomme
