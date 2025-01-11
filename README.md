Role Name
=========

My Developer Dotfiles, powered by Ansible.

Installation
------------

Configure Git/SSH
```bash
wget -O - https://raw.githubusercontent.com/pbonh/ars/main/scripts/bootstrap_gitssh.sh | bash
```

Install Devbox
```bash
wget -O - https://raw.githubusercontent.com/pbonh/ars/main/scripts/bootstrap_devbox.sh | bash
```

Install Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

EITHER
Checkout Reop & Setup `.envrc` File(Example)
```bash
touch .envrc
ln -s .envrc .env
echo "DOTFILES_TASK_PRELUDE=python" > .envrc
```
OR
Ansible Pull
```bash
ansible-pull -U https://github.com/pbonh/ars.git -i "$(hostname --short),"
```

License
-------

Apache 2.0

Author Information
------------------

Phillip Bonhomme
