#!/usr/bin/env bash

# Download Ansible Modules
wget https://github.com/ownport/portable-ansible/releases/download/v0.5.0/portable-ansible-v0.5.0-py3.tar.bz2 -O ansible.tar.bz2

# Unpack Files
tar -xjf ansible.tar.bz2

# Test Ansible Python Modules
python ansible localhost -m ping

# Create Symlinks for Ansible Commands
if [[ ! -d "ansible" ]]; then
    for l in config console doc galaxy inventory playbook pull vault;do
      ln -s ansible ansible-$l
    done
fi

# Example Usage
# python ansible-galaxy install -r requirements.yml
# python ansible-galaxy collection install -r requirements.yml
# python ansible-pull -U https://github.com/pbonh/ars.git -i "$(hostname --short),"
