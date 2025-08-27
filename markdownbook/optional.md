# Optional Tools

Ansible is also setup to install Ollama as a system package. This will require root access and does
not use the same devbox/homebrew/nonroot scripting.

Ollama(w/ ROCM)
```bash
ansible-pull -U https://github.com/pbonh/ars.git --ask-become-pass ollama.yml -e "{rocm_support: true}"
```
