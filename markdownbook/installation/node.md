# Node.js Packages

This role installs Node.js packages via npm/pnpm as configured in your vars file.

## Prerequisites

Ensure you have a tool provider installed (homebrew, mise, devbox, or nonroot) that provides Node.js.

## Installation

```bash
ansible-pull -U https://github.com/pbonh/ars.git node.yml --tags "install"
```

## Just Task

```bash
just install-node-packages
```

## Configuration

Add Node packages to your `vars/local.yml`:

```yaml
---
npm_packages:
  - name: "typescript"
    global: true
  - name: "@angular/cli"
    global: true
```
