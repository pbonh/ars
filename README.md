Role Name
=========

My Developer Dotfiles, powered by Ansible.

Installation
------------

Install Ansible
```bash
wget -O - https://raw.githubusercontent.com/pbonh/ars/main/scripts/bootstrap_ansible.sh | bash
```

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
echo "TOOL_PROVIDER=\"homebrew\"" > .envrc
```
OR
Ansible Pull
```bash
# (Non-Root, Shell Tools Only)
ansible-pull -U https://github.com/pbonh/ars.git playbook.yml --tags "env" -e "{tool_provider: \"nonroot\"}"
# (Install Non-Root, Shell Tools Only)
ansible-pull -U https://github.com/pbonh/ars.git playbook.yml --tags "install,env" -e "{tool_provider: \"nonroot\"}"
```

License
-------

Apache 2.0

Author Information
------------------

Phillip Bonhomme
