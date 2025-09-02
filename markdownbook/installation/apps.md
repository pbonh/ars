# Apps

Application install support includes the ProtonMail Bridge and Flatpak

## ProtonMail Bridge

Use this script to install the ProtonMail Bridge *.rpm(Fedora/Bluefin only):

```bash
wget -O - https://raw.githubusercontent.com/pbonh/ars/main/scripts/install_protonmail_bridge.sh | bash
```

## Flatpak

This role will install Desktop applications via [flathub](https://flathub.org).

```bash
ansible-pull -U https://github.com/pbonh/ars.git apps.yml
```
