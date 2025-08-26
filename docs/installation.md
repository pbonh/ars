# Installation

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
Checkout repository and create `.envrc` File(Example)
```bash
touch .envrc
ln -s .envrc .env
cat << EOF >> .envrc
DOTFILES_TASK_PRELUDE=python
DOTFILES_BOOTSTRAP_GIT_NAME="Your Name"
DOTFILES_BOOTSTRAP_GIT_EMAIL="your_name@address.com"
DOTFILES_BOOTSTRAP_GITHUB_USERNAME="username"
OPENAI_API_KEY="MY_OPENAI_API_KEY"
ANTHROPIC_API_KEY="MY_ANTHROPIC_API_KEY"
EOF
```
OR
Ansible Pull
```bash
# (Non-Root, Shell Tools Only)
ansible-pull -U https://github.com/pbonh/ars.git playbook.yml --tags "env" -e "{tool_provider: \"nonroot\"}"

# (Install Non-Root, Shell Tools Only)
ansible-pull -U https://github.com/pbonh/ars.git playbook.yml --tags "install,env" -e "{tool_provider: \"nonroot\"}"
```
