workstation-kde:
  ansible-playbook --ask-become-pass kde.yml

backup-kde-config:
  konsave --save current_profile --force && konsave --export-profile current_profile && mv ~/current_profile.knsv roles/workstation-kde/files

restore-kde-config:
  konsave --import-profile roles/workstation-kde/files/current_profile.knsv

