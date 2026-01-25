install-requirements:
  {{ task_prelude }} ansible-galaxy install -r requirements.yml
  {{ task_prelude }} ansible-galaxy collection install -r requirements.yml

setup: install-requirements
  git update-index --skip-worktree vars/local.yml 

dotfiles tag='devbox':
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "{{ tag }}"

mise:
  {{ task_prelude }} ansible-playbook mise.yml

devbox:
  {{ task_prelude }} ansible-playbook devbox.yml

homebrew:
  {{ task_prelude }} ansible-playbook homebrew.yml

nonroot:
  {{ task_prelude }} ansible-playbook nonroot.yml

dot tag='env':
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "{{ tag }}" --skip-tags "install"

shell:
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "env,scripts" --skip-tags "install"

nushell:
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "nushell" --skip-tags "install"

scripts:
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "scripts" --skip-tags "install"

bash:
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "bash" --skip-tags "install"

zsh:
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "zsh" --skip-tags "install"

tcsh:
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "tcsh" --skip-tags "install"

neovim:
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "neovim-config" --skip-tags "install"

rebuild-neovim:
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "neovim-config-clean" --skip-tags "install"

zellij:
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "zellij" --skip-tags "install"

yazi:
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "yazi" --skip-tags "install"

navi:
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "navi" --skip-tags "install"

ai:
  {{ task_prelude }} ansible-playbook dotfiles.yml --tags "ai" --skip-tags "install"

ollama:
  {{ task_prelude }} ansible-playbook --ask-become-pass ollama.yml

code2prompt:
  {{ task_prelude }} ansible-playbook ollama.yml --tags "code2prompt" --skip-tags "install"
