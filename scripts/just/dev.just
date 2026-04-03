configure-git:
  {{ task_prelude }} ansible-playbook dev.yml

configure-ssh: configure-git
