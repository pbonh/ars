---
title: "Ansible Galaxy"
type: entity
tags: [entity, tool, hub, registry, community]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/ansible-user-guide.md"]
confidence: high
---

## Overview

Ansible Galaxy is the community hub and CLI tool for discovering, sharing, and reusing Ansible content. The public website (https://galaxy.ansible.com) hosts thousands of roles and collections contributed by the community. The `ansible-galaxy` command-line utility ships with `ansible-core` and can install content from the public Galaxy, private Galaxy servers, Automation Hub, Git repositories, or local tarballs.

## Characteristics

- **Dual role.** Galaxy is both a web registry and a CLI client (`ansible-galaxy`). The client can install roles (`ansible-galaxy role install`) and collections (`ansible-galaxy collection install`).
- **Namespace versioning.** Collections are named `namespace.collection` and carry semantic versions. The CLI respects version constraints and can upgrade or pin.
- **Offline support.** The `download` subcommand fetches collections and their dependencies for air-gapped environments, producing a `requirements.yml` that can be used later for offline installation.

## Common Strategies

- **Dependency management.** Projects declare required collections and roles in a `requirements.yml` file; CI pipelines run `ansible-galaxy collection install -r requirements.yml` before playbook execution.
- **Private content hubs.** Organizations run a private Galaxy server or Red Hat Automation Hub to distribute internally certified collections while still using the standard `ansible-galaxy` CLI.
- **Role bootstrapping.** Operators search Galaxy for pre-built roles (e.g., `geerlingguy.nginx`) to avoid writing common tasks from scratch.

## Sources

- Ansible User Guide — https://docs.ansible.com/projects/ansible/latest/user_guide/index.html
