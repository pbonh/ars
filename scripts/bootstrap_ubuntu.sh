#!/usr/bin/env bash

wget -qO - 'https://proget.makedeb.org/debian-feeds/prebuilt-mpr.pub' | gpg --dearmor | sudo tee /usr/share/keyrings/prebuilt-mpr-archive-keyring.gpg 1> /dev/null
echo "deb [arch=all,$(dpkg --print-architecture) signed-by=/usr/share/keyrings/prebuilt-mpr-archive-keyring.gpg] https://proget.makedeb.org prebuilt-mpr $(lsb_release -cs)" | sudo tee /etc/apt/sources.list.d/prebuilt-mpr.list
sudo apt update -y
sudo apt upgrade -y
sudo apt install -y ansible make python3-psutil just zsh build-essential

if ! [ -x "$(command -v ansible)" ]; then
  echo 'Error: ansible is not installed.' >&2
  exit 1
fi
if ! [ -x "$(command -v ansible-galaxy)" ]; then
  echo 'Error: ansible galaxy is not installed.' >&2
  exit 1
fi

ansible-galaxy install -r requirements.yml
