distrobox:
  ansible-playbook distrobox.yml

distrobox-rebuild:
  ansible-playbook distrobox.yml --tags all,rebuild

distrobox-ubuntu name:
  distrobox create --pull --image ubuntu:latest --init --home ~/distrobox/$USER --name {{ name }} --additional-packages "ansible git build-essential"

pull-ars:
  ansible-pull -U https://github.com/pbonh/ars.git playbook.yml
